"""Dependency-light assertion harness for docking frame repair.

Run with the existing docking environment:
  /opt/homebrew/Caskroom/miniforge/base/envs/docking/bin/python -B \
    -m unittest tests/modeling/test_docking_frame_repair_unittest.py -v
"""

from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from rdkit import Chem


ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "src/modeling/docking-repro"
sys.path.insert(0, str(MODULE_DIR))

from aggregate_frame_repair_terminal import (  # noqa: E402
    build_terminal_rows,
    verify_comparable_job_contracts,
)
from docking_manifest import (  # noqa: E402
    build_job_identity,
    compare_pdb_pdbqt_frame,
    parse_vina_pose_models,
    pose_evidence,
    sha256_file,
    verify_vina_attempt,
    verify_frame_manifest,
)
from dock import _run_vina  # noqa: E402
from evaluate_frame_repair_geometry import thresholds_for  # noqa: E402
from frame_alignment import (  # noqa: E402
    RigidTransform,
    align_mutant_to_wt,
    ca_map,
    kabsch_transform,
    materialize_wt_frame_reference,
    parse_atoms,
    rmsd,
    select_tm_ca,
    validate_mutation_identity,
)
from finalize_frame_repair_smoke_failure import write_terminal_state  # noqa: E402
from finalize_frame_repair_full_state import (  # noqa: E402
    append_full_terminal_state,
)
from finalize_frame_repair_terminal_state import (  # noqa: E402
    write_terminal_state as write_existing_terminal_state,
)
from geometry_calibration import verify_frozen_geometry_calibration  # noqa: E402
from geometry_gate import (  # noqa: E402
    evaluate_pose_set,
    write_membrane_transform_manifest,
)
from prepare_frame_corrected_mutants import enumerate_mutants  # noqa: E402
from preflight_docking_environment import extract_adfr_build  # noqa: E402
from ratio_ranking import (  # noqa: E402
    classify,
    load_frozen_policy,
    select_panel,
)
from run_frame_repair_docking import (  # noqa: E402
    _resolve_box,
    assert_run_accepts_docking,
    build_subject_matrix,
    minimum_returned_modes,
    run_bounded_fail_fast,
    should_continue_after_technical_failure,
    validate_max_parallel_jobs,
    validate_max_new_smoke_attempts,
)
from run_frame_repair_ifp import verify_sdf_pose_binding  # noqa: E402
from utils import load_config  # noqa: E402


def pdb_atom_line(
    serial: int,
    atom_name: str,
    resname: str,
    chain: str,
    resseq: int,
    xyz: tuple[float, float, float],
    element: str,
) -> str:
    return (
        f"ATOM  {serial:5d} {atom_name:^4s} {resname:>3s} {chain}{resseq:4d}    "
        f"{xyz[0]:8.3f}{xyz[1]:8.3f}{xyz[2]:8.3f}"
        f"  1.00 90.00          {element:>2s}\n"
    )


def pose_body(model: int, coordinates: list[tuple[float, float, float]]) -> str:
    lines = [
        f"MODEL {model}\n",
        f"REMARK VINA RESULT: {-5.0 - model / 100:.3f} 0.000 0.000\n",
    ]
    for index, (element, coordinate) in enumerate(
        zip(("C", "O"), coordinates, strict=True),
        start=1,
    ):
        lines.append(
            pdb_atom_line(
                index,
                f"{element}{index}",
                "LIG",
                "X",
                901,
                coordinate,
                element,
            )
        )
    lines.append("ENDMDL\n")
    return "".join(lines)


class DockingFrameRepairAssertions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config_path = MODULE_DIR / "config.yaml"
        cls.config = load_config(cls.config_path)
        cls.inventory_path = (
            ROOT
            / cls.config["frame_repair"]["mutation_inventory"]
        )
        cls.inventory = enumerate_mutants(cls.inventory_path)

    def receptor_inputs(
        self, receptor: str
    ) -> tuple[Path, Path, list[list[int]], Path]:
        receptor_cfg = self.config["receptors"][receptor]
        wt_full = (
            ROOT
            / self.config["paths"]["receptor_dir"]
            / receptor_cfg["pdb_file"]
        )
        wt_tm = (
            ROOT
            / self.config["paths"]["prepared_dir"]
            / "receptors"
            / f"{Path(receptor_cfg['pdb_file']).stem}_tm.pdb"
        )
        helices = [
            self.config["tm_topology"][receptor]["helices"][key]
            for key in sorted(self.config["tm_topology"][receptor]["helices"])
        ]
        source = (
            ROOT
            / self.config["paths"]["mutagenesis_dir"]
            / "af3_structures"
            / receptor
        )
        return wt_full, wt_tm, helices, source

    def test_kabsch_inverse_and_proper_rotation(self) -> None:
        source = np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 2.0, 0.0],
                [0.0, 0.0, 3.0],
            ]
        )
        angle = np.deg2rad(37.0)
        rotation = np.asarray(
            [
                [np.cos(angle), -np.sin(angle), 0.0],
                [np.sin(angle), np.cos(angle), 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        expected = RigidTransform(rotation, np.asarray([4.0, -3.0, 2.0]))
        target = expected.apply(source)
        fitted = kabsch_transform(source, target)
        self.assertLess(rmsd(fitted.apply(source), target), 1e-12)
        self.assertAlmostEqual(float(np.linalg.det(fitted.rotation)), 1.0, places=12)
        self.assertLess(
            float(np.max(np.abs(fitted.inverse().apply(target) - source))),
            1e-12,
        )

    def test_all_162_mutants_have_complete_identity_and_alignment(self) -> None:
        self.assertEqual(
            {key: len(value) for key, value in self.inventory.items()},
            {"Gpr2": 46, "Gpr3": 116},
        )
        expected_ranges = {
            "Gpr2": (0.236, 0.675),
            "Gpr3": (0.300, 0.665),
        }
        expected_eight = {
            ("Gpr2", "R59C"): (9.61, 0.269),
            ("Gpr2", "R59F"): (19.02, 0.332),
            ("Gpr2", "R59T"): (9.41, 0.453),
            ("Gpr2", "M327A"): (12.56, 0.658),
            ("Gpr3", "R167Y"): (10.93, 0.494),
            ("Gpr3", "V138M"): (10.99, 0.517),
            ("Gpr3", "R167P"): (11.10, 0.394),
            ("Gpr3", "R167C"): (11.59, 0.373),
        }
        observed: dict[str, list[float]] = {"Gpr2": [], "Gpr3": []}
        for receptor, mutations in self.inventory.items():
            wt_full, wt_tm, helices, source_dir = self.receptor_inputs(receptor)
            wt_full_atoms = parse_atoms(wt_full)
            wt_selected = select_tm_ca(parse_atoms(wt_tm), helices)
            target = np.vstack([atom.coord for atom in wt_selected])
            self.assertEqual(len(wt_selected), 147)
            for mutation in mutations:
                mutant_full_atoms = parse_atoms(source_dir / f"{mutation}.pdb")
                identity = validate_mutation_identity(
                    wt_full_atoms,
                    mutant_full_atoms,
                    mutation,
                )
                self.assertTrue(identity["full_ca_key_sets_equal"])
                self.assertEqual(identity["unexpected_identity_differences"], [])
                mutant_selected = select_tm_ca(
                    parse_atoms(source_dir / f"{mutation}_tm.pdb"),
                    helices,
                )
                self.assertEqual(len(mutant_selected), 147)
                source = np.vstack([atom.coord for atom in mutant_selected])
                transform = kabsch_transform(source, target)
                post_rmsd = rmsd(transform.apply(source), target)
                observed[receptor].append(post_rmsd)
                self.assertAlmostEqual(
                    float(np.linalg.det(transform.rotation)),
                    1.0,
                    places=8,
                )
                if (receptor, mutation) in expected_eight:
                    center, expected_rmsd = expected_eight[(receptor, mutation)]
                    self.assertAlmostEqual(
                        float(np.linalg.norm(source.mean(0) - target.mean(0))),
                        center,
                        delta=0.02,
                    )
                    self.assertAlmostEqual(post_rmsd, expected_rmsd, delta=0.002)
        for receptor, values in observed.items():
            minimum, maximum = expected_ranges[receptor]
            self.assertGreaterEqual(min(values), minimum - 0.002)
            self.assertLessEqual(max(values), maximum + 0.002)

    def test_wt_materialization_manifest_and_tamper(self) -> None:
        wt_full, wt_tm, helices, _ = self.receptor_inputs("Gpr2")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            full_out = root / "WT.aligned.pdb"
            tm_out = root / "WT_tm.aligned.pdb"
            manifest_path = root / "frame_manifest.json"
            materialize_wt_frame_reference(
                receptor="Gpr2",
                wt_full_pdb=wt_full,
                wt_tm_pdb=wt_tm,
                run_full_pdb=full_out,
                run_tm_pdb=tm_out,
                manifest_path=manifest_path,
                helices=helices,
            )
            verify_frame_manifest(
                manifest_path,
                aligned_pdb=full_out,
                aligned_tm_pdb=tm_out,
                expected_receptor="Gpr2",
                expected_mutation="WT",
            )
            tm_out.write_text(tm_out.read_text() + "REMARK tampered\n")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_frame_manifest(manifest_path, aligned_tm_pdb=tm_out)

    def test_existing_legacy_pdbqt_preserves_original_frame_when_present(self) -> None:
        cases = (
            ("Gpr2", "R59C"),
            ("Gpr2", "R59F"),
            ("Gpr2", "R59T"),
            ("Gpr2", "M327A"),
            ("Gpr3", "R167Y"),
            ("Gpr3", "R167P"),
            ("Gpr3", "R167C"),
        )
        for receptor, mutation in cases:
            _, _, _, source_dir = self.receptor_inputs(receptor)
            pdb_atoms = {
                atom.atom_key: atom.coord
                for atom in parse_atoms(source_dir / f"{mutation}_tm.pdb")
                if (atom.element or atom.atom_name[:1]).upper() != "H"
            }
            pdbqt = (
                ROOT
                / self.config["paths"]["mutagenesis_dir"]
                / "af3_prepared"
                / receptor
                / f"{mutation}_tm.pdbqt"
            )
            pdbqt_atoms = {
                atom.atom_key: atom.coord
                for atom in parse_atoms(pdbqt)
                if (atom.element or atom.atom_name[:1]).upper() != "H"
            }
            common = sorted(set(pdb_atoms) & set(pdbqt_atoms))
            self.assertGreater(len(common), 1000)
            maximum = max(
                float(np.linalg.norm(pdb_atoms[key] - pdbqt_atoms[key]))
                for key in common
            )
            self.assertLessEqual(maximum, 0.002)
        missing = (
            ROOT
            / self.config["paths"]["mutagenesis_dir"]
            / "af3_prepared/Gpr3/V138M_tm.pdbqt"
        )
        self.assertFalse(missing.exists())

    def test_pdb_pdbqt_pose_and_sdf_identity_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receptor_pdb = root / "receptor.pdb"
            receptor_pdbqt = root / "receptor.pdbqt"
            atoms = [
                pdb_atom_line(1, "CA", "ALA", "A", 1, (1.0, 2.0, 3.0), "C"),
                pdb_atom_line(2, "CB", "ALA", "A", 1, (2.0, 2.0, 3.0), "C"),
            ]
            receptor_pdb.write_text("".join(atoms) + "END\n")
            receptor_pdbqt.write_text("".join(atoms) + "END\n")
            self.assertEqual(
                compare_pdb_pdbqt_frame(
                    receptor_pdb,
                    receptor_pdbqt,
                )["common_heavy_atom_count"],
                2,
            )

            poses = root / "poses.pdbqt"
            coordinates_by_model = [
                [
                    (float(model), 0.0, 0.0),
                    (float(model), 1.2, 0.0),
                ]
                for model in range(1, 21)
            ]
            poses.write_text(
                "".join(
                    pose_body(model, coordinates_by_model[model - 1])
                    for model in range(1, 21)
                )
            )
            evidence = pose_evidence(
                poses, requested_max_modes=20
            )
            self.assertEqual(evidence["model_count"], 20)
            self.assertEqual(evidence["models"][0]["model_number"], 1)
            poses_18 = root / "poses_18.pdbqt"
            poses_18.write_text(
                "".join(
                    pose_body(model, coordinates_by_model[model - 1])
                    for model in range(1, 19)
                )
            )
            self.assertEqual(
                pose_evidence(
                    poses_18, requested_max_modes=20
                )["model_count"],
                18,
            )
            poses_21 = root / "poses_21.pdbqt"
            poses_21.write_text(
                "".join(
                    pose_body(
                        model,
                        [
                            (float(model), 0.0, 0.0),
                            (float(model), 1.2, 0.0),
                        ],
                    )
                    for model in range(1, 22)
                )
            )
            with self.assertRaisesRegex(ValueError, "requested_max=20"):
                pose_evidence(poses_21, requested_max_modes=20)

            sdf = root / "poses.sdf"
            writer = Chem.SDWriter(str(sdf))
            for model, coordinates in enumerate(coordinates_by_model, start=1):
                molecule = Chem.RWMol()
                carbon = molecule.AddAtom(Chem.Atom("C"))
                oxygen = molecule.AddAtom(Chem.Atom("O"))
                molecule.AddBond(carbon, oxygen, Chem.BondType.SINGLE)
                result = molecule.GetMol()
                conformer = Chem.Conformer(2)
                for atom_index, coordinate in enumerate(coordinates):
                    conformer.SetAtomPosition(atom_index, coordinate)
                result.AddConformer(conformer)
                result.SetProp("MODEL", str(model))
                result.SetProp(
                    "REMARK",
                    f" VINA RESULT: {-5.0 - model / 100:.3f} 0.000 0.000",
                )
                writer.write(result)
            writer.close()
            binding = verify_sdf_pose_binding(
                poses,
                sdf,
                actual_modes=20,
            )
            self.assertEqual(len(binding), 20)
            self.assertLessEqual(
                max(item["max_coordinate_delta_angstrom"] for item in binding),
                0.0011,
            )
            tampered = sdf.read_text().replace(
                "VINA RESULT: -5.010",
                "VINA RESULT: -9.999",
                1,
            )
            sdf.write_text(tampered)
            with self.assertRaisesRegex(ValueError, "affinity mismatch"):
                verify_sdf_pose_binding(poses, sdf, actual_modes=20)

    def test_cpu8_invocation_and_identity_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = root / "poses.pdbqt"
            completed = SimpleNamespace(
                returncode=0,
                stdout=(
                    "    1       -5.010      0.000      0.000\n"
                ),
                stderr="",
            )
            with patch("dock.subprocess.run", return_value=completed):
                affinities = _run_vina(
                    vina_bin="/frozen/vina",
                    receptor=Path("/frozen/receptor.pdbqt"),
                    ligand=Path("/frozen/ligand.pdbqt"),
                    center=(1.0, 2.0, 3.0),
                    box_size=20.0,
                    spacing=0.1,
                    exhaustiveness=200,
                    num_modes=20,
                    energy_range=3.0,
                    min_rmsd=1.0,
                    max_evals=0,
                    cpu=8,
                    seed=42,
                    output=output,
                )
            self.assertEqual(affinities, [-5.01])
            command = json.loads(
                (root / "poses.vina.command.json").read_text()
            )
            argv = command["argv"]
            for flag, value in (
                ("--cpu", "8"),
                ("--num_modes", "20"),
                ("--energy_range", "3.0"),
                ("--min_rmsd", "1.0"),
                ("--max_evals", "0"),
                ("--seed", "42"),
            ):
                self.assertEqual(argv[argv.index(flag) + 1], value)
            self.assertEqual(command["returncode"], 0)
            self.assertGreaterEqual(command["elapsed_sec"], 0.0)
            output.write_text(
                pose_body(1, [(1.0, 0.0, 0.0), (1.0, 1.2, 0.0)])
            )
            attempt_inputs = {
                "receptor_pdbqt": {
                    "path": "/frozen/receptor.pdbqt"
                },
                "ligand_pdbqt": {
                    "path": "/frozen/ligand.pdbqt"
                },
                "box": {
                    "center": [1.0, 2.0, 3.0],
                    "size": [20.0, 20.0, 20.0],
                },
                "vina": {
                    "executable_path": "/frozen/vina",
                    "spacing": 0.1,
                    "exhaustiveness": 200,
                    "requested_max_modes": 20,
                    "energy_range": 3.0,
                    "min_rmsd": 1.0,
                    "max_evals": 0,
                    "cpu": 8,
                },
                "seed": 42,
            }
            file_record = lambda path: {
                "path": str(path.resolve()),
                "sha256": sha256_file(path),
            }
            verified = verify_vina_attempt(
                {
                    "returncode": 0,
                    "elapsed_sec": command["elapsed_sec"],
                    "command": file_record(
                        root / "poses.vina.command.json"
                    ),
                    "stdout": file_record(
                        root / "poses.vina.stdout.txt"
                    ),
                    "stderr": file_record(
                        root / "poses.vina.stderr.txt"
                    ),
                },
                inputs=attempt_inputs,
                poses=pose_evidence(
                    output, requested_max_modes=20
                ),
            )
            self.assertEqual(verified["stdout_affinities"], [-5.01])

        inputs = {
            "receptor": "Gpr3",
            "mutation": "R167Y",
            "ligand": "ascr18",
            "receptor_pdbqt": {
                "sha256": "a" * 64,
                "manifest_identity": "b" * 64,
            },
            "ligand_pdbqt": {"sha256": "c" * 64},
            "box": {"center": [0.42, 7.16, -17.11], "size": [20.0] * 3},
            "vina": {
                "executable_sha256": "d" * 64,
                "version": "1.2.6",
                "package_build": "py311h1ddb823_2",
                "package_build_number": 2,
                "spacing": 0.1,
                "exhaustiveness": 200,
                "requested_max_modes": 20,
                "energy_range": 3.0,
                "min_rmsd": 1.0,
                "max_evals": 0,
                "cpu": 8,
            },
            "seed": 42,
            "environment": {"manifest_identity": "e" * 64},
        }
        baseline = build_job_identity(inputs)
        for field, value in (
            ("cpu", 4),
            ("min_rmsd", 2.0),
            ("max_evals", 100),
            ("package_build", "different-build"),
        ):
            changed = deepcopy(inputs)
            changed["vina"][field] = value
            self.assertNotEqual(build_job_identity(changed), baseline)

    def test_pose_population_minima_reuse_frozen_geometry_counts(self) -> None:
        expected = {
            ("Gpr2", "ascr18"): 17,
            ("Gpr2", "ascr3"): 15,
            ("Gpr3", "ascr18"): 16,
            ("Gpr3", "ascr3"): 18,
        }
        self.assertEqual(
            {
                key: minimum_returned_modes(
                    self.config, receptor=key[0], ligand=key[1]
                )
                for key in expected
            },
            expected,
        )

    def test_frozen_geometry_calibration_and_membrane_baselines(self) -> None:
        calibration = verify_frozen_geometry_calibration(
            self.config,
            root=ROOT,
        )
        self.assertEqual(
            calibration["status"],
            "verified_frozen_before_mutant_results",
        )
        expected = {
            "Gpr2": 0.0542837,
            "Gpr3": 0.0644625,
        }
        for receptor, target in expected.items():
            observed = calibration["receptors"][receptor][
                "membrane_transform"
            ]["metrics_angstrom"]["post_alignment_rmsd"]
            self.assertAlmostEqual(observed, target, delta=1e-6)
        self.assertEqual(calibration["calibration_seeds"], [42, 43])
        self.assertEqual(calibration["production_seed"], 44)

    def test_current_geometry_gate_rejects_config_drift(self) -> None:
        changed = deepcopy(self.config)
        changed["frame_repair"]["geometry_gate"]["Gpr2"]["by_ligand"][
            "ascr18"
        ]["min_passing_modes"] += 1
        with self.assertRaisesRegex(ValueError, "min_passing_modes mismatch"):
            verify_frozen_geometry_calibration(changed, root=ROOT)

        changed = deepcopy(self.config)
        changed["vina"]["seed"] = 42
        with self.assertRaisesRegex(ValueError, "must be independent"):
            verify_frozen_geometry_calibration(changed, root=ROOT)

    def test_current_geometry_gate_rejects_artifact_tamper_and_seed_drift(
        self,
    ) -> None:
        source = (
            ROOT
            / self.config["frame_repair"]["geometry_gate"][
                "calibration_artifact"
            ]["path"]
        )
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "geometry_gate.json"
            artifact = json.loads(source.read_text(encoding="utf-8"))
            artifact["method"]["calibration_seeds"] = [41, 43]
            body = dict(artifact)
            body.pop("gate_identity")
            artifact["gate_identity"] = hashlib.sha256(
                json.dumps(
                    body,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
                + b"\n"
            ).hexdigest()
            artifact_path.write_text(
                json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            changed = deepcopy(self.config)
            record = changed["frame_repair"]["geometry_gate"][
                "calibration_artifact"
            ]
            record["path"] = str(artifact_path)
            record["sha256"] = sha256_file(artifact_path)
            record["gate_identity"] = artifact["gate_identity"]
            with self.assertRaisesRegex(
                ValueError,
                "must be exactly 42 and 43",
            ):
                verify_frozen_geometry_calibration(changed, root=ROOT)

            artifact["status"] = "tampered"
            artifact_path.write_text(
                json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            record["sha256"] = sha256_file(artifact_path)
            with self.assertRaisesRegex(ValueError, "not frozen"):
                verify_frozen_geometry_calibration(changed, root=ROOT)

    def test_smoke_and_full_matrix_are_exact(self) -> None:
        records = [
            {"receptor": receptor, "mutation": mutation}
            for receptor, mutations in self.inventory.items()
            for mutation in mutations
        ]
        run_manifest = {"records": records}
        smoke = build_subject_matrix(run_manifest, run_mode="smoke")
        full = build_subject_matrix(run_manifest, run_mode="full")
        self.assertEqual(len(smoke), 8)
        self.assertEqual(len(full), 328)
        self.assertEqual(len(set(full)), 328)
        self.assertFalse(any(receptor == "GprC" for receptor, _, _ in full))

    def test_continue_after_failure_is_smoke_only(self) -> None:
        self.assertTrue(
            should_continue_after_technical_failure(
                run_mode="smoke",
                continue_smoke_after_technical_failure=True,
            )
        )
        self.assertFalse(
            should_continue_after_technical_failure(
                run_mode="smoke",
                continue_smoke_after_technical_failure=False,
            )
        )
        with self.assertRaisesRegex(ValueError, "仅允许用于 smoke"):
            should_continue_after_technical_failure(
                run_mode="full",
                continue_smoke_after_technical_failure=True,
            )

    def test_max_new_attempt_limit_is_positive_and_smoke_only(self) -> None:
        self.assertIsNone(
            validate_max_new_smoke_attempts(
                run_mode="smoke",
                max_new_smoke_attempts=None,
            )
        )
        self.assertEqual(
            validate_max_new_smoke_attempts(
                run_mode="smoke",
                max_new_smoke_attempts=1,
            ),
            1,
        )
        with self.assertRaisesRegex(ValueError, "正整数"):
            validate_max_new_smoke_attempts(
                run_mode="smoke",
                max_new_smoke_attempts=0,
            )
        with self.assertRaisesRegex(ValueError, "仅允许用于 smoke"):
            validate_max_new_smoke_attempts(
                run_mode="full",
                max_new_smoke_attempts=1,
            )

    def test_parallel_full_runner_is_bounded_and_order_preserving(self) -> None:
        self.assertEqual(
            validate_max_parallel_jobs(
                run_mode="full",
                max_parallel_jobs=12,
                cpu_per_job=8,
            ),
            12,
        )
        with self.assertRaisesRegex(ValueError, "smoke 必须保持"):
            validate_max_parallel_jobs(
                run_mode="smoke",
                max_parallel_jobs=2,
                cpu_per_job=8,
            )
        with self.assertRaisesRegex(ValueError, "128-thread"):
            validate_max_parallel_jobs(
                run_mode="full",
                max_parallel_jobs=17,
                cpu_per_job=8,
            )
        self.assertEqual(
            run_bounded_fail_fast(
                [3, 1, 4, 2],
                lambda value: value * 2,
                max_workers=3,
            ),
            [6, 2, 8, 4],
        )

        def fail_on_three(value: int) -> int:
            if value == 3:
                raise RuntimeError("synthetic docking failure")
            return value

        with self.assertRaisesRegex(RuntimeError, "synthetic docking failure"):
            run_bounded_fail_fast(
                [1, 2, 3, 4],
                fail_on_three,
                max_workers=2,
            )

    def test_terminal_smoke_run_rejects_new_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assert_run_accepts_docking(root, run_mode="smoke")
            assert_run_accepts_docking(root, run_mode="full")
            terminal = root / "terminal/smoke_terminal.json"
            terminal.parent.mkdir(parents=True)
            terminal.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                FileExistsError,
                "拒绝新增 attempt",
            ):
                assert_run_accepts_docking(root, run_mode="smoke")
            assert_run_accepts_docking(root, run_mode="full")

    def test_e2_environment_lock_and_adfr_build_identity(self) -> None:
        lock_path = ROOT / self.config["frame_repair"]["environment_lock"]
        lock = load_config(lock_path)
        packages = lock["resolved"]["packages"]
        canonical = ("\n".join(packages) + "\n").encode()
        import hashlib

        self.assertEqual(len(packages), lock["resolved"]["package_count"])
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            lock["resolved"]["canonical_name_version_build_sha256"],
        )
        self.assertIn("vina=1.2.6=py311h1ddb823_2", packages)
        self.assertIn("openbabel=3.1.1=py311h8b422cb_9", packages)
        self.assertEqual(
            extract_adfr_build("BUILD 100 (Nov_16_21)\n"),
            self.config["frame_repair"]["target_toolchain"]["adfr_build"],
        )

    def test_failed_smoke_terminal_state_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            terminal = root / "terminal/smoke_terminal.json"
            terminal.parent.mkdir(parents=True)
            terminal.write_text("{}\n", encoding="utf-8")
            events, snapshot = write_terminal_state(
                root,
                terminal_path=terminal,
                detail={"stop_reason": "pose_completeness"},
                observed_at="2026-07-30T00:00:00+00:00",
            )
            self.assertEqual(events.read_text(), snapshot.read_text())
            self.assertIn("TERMINAL_ABNORMAL", events.read_text())
            with self.assertRaisesRegex(FileExistsError, "refusing overwrite"):
                write_terminal_state(
                    root,
                    terminal_path=terminal,
                    detail={"stop_reason": "pose_completeness"},
                    observed_at="2026-07-30T00:00:01+00:00",
                )

    def test_existing_smoke_terminal_state_supports_pass_and_fail(self) -> None:
        for terminal_status, expected_state in (
            ("pass", "TERMINAL_NORMAL"),
            ("fail_stop_before_full", "TERMINAL_ABNORMAL"),
        ):
            with self.subTest(terminal_status=terminal_status):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    terminal = root / "terminal/smoke_terminal.json"
                    terminal.parent.mkdir(parents=True)
                    terminal.write_text("{}\n", encoding="utf-8")
                    events, snapshot = write_existing_terminal_state(
                        root,
                        terminal_status=terminal_status,
                        terminal_path=terminal,
                        detail={"smoke_status": terminal_status},
                        observed_at="2026-07-30T00:00:00+00:00",
                    )
                    self.assertEqual(events.read_text(), snapshot.read_text())
                    self.assertIn(expected_state, events.read_text())
                    with self.assertRaisesRegex(
                        FileExistsError,
                        "refusing overwrite",
                    ):
                        write_existing_terminal_state(
                            root,
                            terminal_status=terminal_status,
                            terminal_path=terminal,
                            detail={"smoke_status": terminal_status},
                            observed_at="2026-07-30T00:00:01+00:00",
                        )

    def test_full_terminal_state_appends_after_passing_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            smoke_terminal = root / "terminal/smoke_terminal.json"
            smoke_terminal.parent.mkdir(parents=True)
            smoke_terminal.write_text("{}\n", encoding="utf-8")
            write_existing_terminal_state(
                root,
                terminal_status="pass",
                terminal_path=smoke_terminal,
                detail={"smoke_status": "pass"},
                observed_at="2026-07-31T00:00:00+00:00",
            )
            full_terminal = root / "terminal/terminal_manifest.json"
            full_terminal.write_text("{}\n", encoding="utf-8")
            evidence = {
                "terminal_path": full_terminal,
                "terminal_sha256": "a" * 64,
                "terminal_manifest_identity": "b" * 64,
                "run_identity": "c" * 64,
                "environment_manifest_identity": "d" * 64,
                "scope": {
                    "job_count": 328,
                    "mutant_count": 162,
                    "mutant_counts": {"Gpr2": 46, "Gpr3": 116},
                },
            }
            events, snapshot = append_full_terminal_state(
                root,
                evidence=evidence,
                observed_at="2026-07-31T01:00:00+00:00",
            )
            self.assertEqual(events.read_text().count("TERMINAL_NORMAL"), 2)
            self.assertIn(str(full_terminal.resolve()), snapshot.read_text())
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                append_full_terminal_state(
                    root,
                    evidence=evidence,
                    observed_at="2026-07-31T02:00:00+00:00",
                )

    def test_synthetic_terminal_matrix_and_comparable_contract(self) -> None:
        records = [
            {"receptor": receptor, "mutation": mutation}
            for receptor, mutations in self.inventory.items()
            for mutation in mutations
        ]
        run_manifest = {"records": records}
        jobs = []
        for receptor, mutation, ligand in build_subject_matrix(
            run_manifest,
            run_mode="full",
        ):
            identity = f"{len(jobs) + 1:064x}"
            jobs.append(
                {
                    "receptor": receptor,
                    "mutation": mutation,
                    "ligand": ligand,
                    "job_identity": identity,
                    "pose_sha256": identity,
                    "model1_affinity": -6.0 if ligand == "ascr18" else -5.0,
                    "geometry_pass": True,
                    "model1_geometry_pass": True,
                    "ifp_complete": True,
                    "provenance_pass": True,
                    "technical_pose_pass": True,
                    "pose_population_pass": True,
                    "provenance_status": (
                        "canonical_wt_coordinate"
                        if mutation == "WT"
                        else "af3_request_and_coordinate"
                    ),
                    "provenance_gap": False,
                    "contract": {
                        "box": {
                            "center": [0.0, 0.0, 0.0]
                            if receptor == "Gpr2"
                            else [1.0, 2.0, 3.0],
                            "size": [40.0, 40.0, 40.0]
                            if receptor == "Gpr2"
                            else [20.0, 20.0, 20.0],
                        },
                        "ligand_pdbqt": {
                            "path": f"/frozen/{ligand}.pdbqt",
                            "sha256": "a" * 64 if ligand == "ascr18" else "b" * 64,
                        },
                        "vina": {
                            "version": "1.2.6",
                            "spacing": 0.1,
                            "exhaustiveness": 200,
                            "requested_max_modes": 20,
                            "energy_range": 3.0,
                            "min_rmsd": 1.0,
                            "max_evals": 0,
                            "cpu": 8,
                            "package_build": "py311h1ddb823_2",
                            "package_build_number": 2,
                            "executable_path": "/frozen/vina",
                            "executable_sha256": "c" * 64,
                        },
                        "seed": 20260412,
                        "environment": {
                            "path": "/frozen/environment.json",
                            "sha256": "d" * 64,
                            "manifest_identity": "e" * 64,
                        },
                    },
                }
            )
        contract = verify_comparable_job_contracts(jobs)
        self.assertEqual(contract["status"], "pass")
        rows = build_terminal_rows(run_manifest, jobs)
        self.assertEqual(len(rows), 162)
        self.assertEqual(
            {
                receptor: sum(row["receptor"] == receptor for row in rows)
                for receptor in ("Gpr2", "Gpr3")
            },
            {"Gpr2": 46, "Gpr3": 116},
        )
        jobs[-1]["contract"]["seed"] += 1
        with self.assertRaisesRegex(ValueError, "environment/Vina/seed"):
            verify_comparable_job_contracts(jobs)

    def test_ratio_policy_vectors_and_panel_diversity(self) -> None:
        policy = load_frozen_policy(self.config)
        for vector in policy["test_vectors"]:
            self.assertEqual(
                classify(
                    vector,
                    threshold=float(policy["channel_threshold"]),
                    affinity_floor=float(policy["affinity_floor"]),
                ),
                vector["expected_channel"],
            )
        pairings = []
        for rank in range(1, 10):
            gpr2 = "Gpr2_R59C" if rank <= 7 else f"Gpr2_ALT{rank}"
            pairings.append(
                {
                    "rank": rank,
                    "channel_a": gpr2,
                    "channel_b": f"Gpr3_TEST{rank}",
                    "receptor_a": "Gpr2",
                    "receptor_b": "Gpr3",
                }
            )
        panel = select_panel(
            pairings,
            panel_size=int(policy["panel_size"]),
            min_distinct_gpr2=int(policy["min_distinct_gpr2_mutants"]),
        )
        self.assertEqual(len(panel), 7)
        self.assertGreaterEqual(
            len({item["channel_a"] for item in panel}),
            2,
        )

    def test_legacy_misaligned_pose_is_geometry_negative_control(self) -> None:
        receptor = "Gpr2"
        ligand = "ascr18"
        _, wt_tm, helices, source_dir = self.receptor_inputs(receptor)
        membrane_pdb = (
            ROOT
            / self.config["frame_repair"]["membrane_references"][receptor]
        )
        legacy_pose = (
            ROOT
            / "experiments/docking-repro/results/ifp_analysis_mutants/poses/"
            "Gpr2_R59C_ascr18_poses.pdbqt"
        )
        self.assertEqual(len(parse_vina_pose_models(legacy_pose)), 20)
        with tempfile.TemporaryDirectory() as directory:
            membrane_manifest = Path(directory) / "membrane.json"
            write_membrane_transform_manifest(
                membrane_manifest,
                receptor=receptor,
                wt_docking_pdb=wt_tm,
                membrane_pdb=membrane_pdb,
                helices=helices,
            )
            report = evaluate_pose_set(
                pose_pdbqt=legacy_pose,
                receptor_pdb=source_dir / "R59C_tm.pdb",
                membrane_transform_manifest=membrane_manifest,
                box=_resolve_box(
                    self.config,
                    receptor=receptor,
                    wt_tm_pdb=wt_tm,
                ),
                thresholds=thresholds_for(
                    self.config,
                    receptor=receptor,
                    ligand=ligand,
                ),
                ifp_contact_by_model={model: True for model in range(1, 21)},
            )
        self.assertFalse(report["pass"])
        self.assertLess(
            report["passing_mode_count"],
            report["thresholds"]["min_passing_modes"],
        )


if __name__ == "__main__":
    unittest.main()
