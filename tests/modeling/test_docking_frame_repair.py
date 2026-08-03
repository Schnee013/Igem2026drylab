from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "src/modeling/docking-repro"
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from docking_manifest import compare_pdb_pdbqt_frame, verify_frame_manifest
from frame_alignment import (
    RigidTransform,
    align_mutant_to_wt,
    kabsch_transform,
    rmsd,
)
from geometry_gate import split_pdbqt_models


def load_prepare_module():
    path = MODULE_DIR / "prepare_frame_corrected_mutants.py"
    spec = importlib.util.spec_from_file_location("prepare_frame_corrected_mutants", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pdb_atom_line(
    serial: int,
    atom: str,
    resname: str,
    chain: str,
    resseq: int,
    xyz: tuple[float, float, float],
    element: str,
) -> str:
    return (
        f"ATOM  {serial:5d} {atom:^4s} {resname:>3s} {chain}{resseq:4d}    "
        f"{xyz[0]:8.3f}{xyz[1]:8.3f}{xyz[2]:8.3f}"
        f"  1.00 90.00          {element:>2s}\n"
    )


def test_kabsch_and_inverse_round_trip():
    source = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]]
    )
    angle = np.deg2rad(37.0)
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0.0],
            [np.sin(angle), np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    expected = RigidTransform(rotation, np.array([4.0, -3.0, 2.0]))
    target = expected.apply(source)
    fitted = kabsch_transform(source, target)
    assert rmsd(fitted.apply(source), target) < 1e-12
    assert np.linalg.det(fitted.rotation) == pytest.approx(1.0, abs=1e-12)
    assert np.max(np.abs(fitted.inverse().apply(target) - source)) < 1e-12


def test_mutation_inventory_counts_are_frozen():
    module = load_prepare_module()
    inventory = module.enumerate_mutants(
        ROOT
        / "experiments/docking-repro/mutagenesis/"
        "mutagenesis_results_merged_gpr3_f_full_20260520_0854.json"
    )
    assert {key: len(value) for key, value in inventory.items()} == {
        "Gpr2": 46,
        "Gpr3": 116,
    }
    assert sum(map(len, inventory.values())) == 162


@pytest.mark.parametrize(
    ("receptor", "mutation", "expected_center", "expected_rmsd"),
    [
        ("Gpr2", "R59C", 9.61, 0.269),
        ("Gpr2", "R59F", 19.02, 0.332),
        ("Gpr2", "R59T", 9.41, 0.453),
        ("Gpr2", "M327A", 12.56, 0.658),
        ("Gpr3", "R167Y", 10.93, 0.494),
        ("Gpr3", "V138M", 10.99, 0.517),
        ("Gpr3", "R167P", 11.10, 0.394),
        ("Gpr3", "R167C", 11.59, 0.373),
    ],
)
def test_real_mutant_alignment_regression(
    tmp_path: Path,
    receptor: str,
    mutation: str,
    expected_center: float,
    expected_rmsd: float,
):
    config = yaml.safe_load((MODULE_DIR / "config.yaml").read_text())
    receptor_cfg = config["receptors"][receptor]
    wt_full = ROOT / config["paths"]["receptor_dir"] / receptor_cfg["pdb_file"]
    wt_tm = (
        ROOT
        / config["paths"]["prepared_dir"]
        / "receptors"
        / f"{Path(receptor_cfg['pdb_file']).stem}_tm.pdb"
    )
    source = (
        ROOT
        / config["paths"]["mutagenesis_dir"]
        / "af3_structures"
        / receptor
    )
    helices = [
        config["tm_topology"][receptor]["helices"][key]
        for key in sorted(config["tm_topology"][receptor]["helices"])
    ]
    aligned_full = tmp_path / f"{mutation}.aligned.pdb"
    aligned_tm = tmp_path / f"{mutation}_tm.aligned.pdb"
    manifest_path = tmp_path / "frame_manifest.json"
    manifest = align_mutant_to_wt(
        receptor=receptor,
        mutation=mutation,
        wt_full_pdb=wt_full,
        wt_tm_pdb=wt_tm,
        mutant_full_pdb=source / f"{mutation}.pdb",
        mutant_tm_pdb=source / f"{mutation}_tm.pdb",
        aligned_full_pdb=aligned_full,
        aligned_tm_pdb=aligned_tm,
        manifest_path=manifest_path,
        helices=helices,
    )
    assert manifest["alignment_selection"]["ca_count"] == 147
    assert manifest["metrics_angstrom"]["pre_alignment_center_distance"] == pytest.approx(
        expected_center, abs=0.02
    )
    assert manifest["metrics_angstrom"]["post_alignment_rmsd"] == pytest.approx(
        expected_rmsd, abs=0.002
    )
    assert manifest["transform"]["determinant"] == pytest.approx(1.0, abs=1e-8)
    verify_frame_manifest(
        manifest_path,
        aligned_pdb=aligned_full,
        aligned_tm_pdb=aligned_tm,
        expected_receptor=receptor,
        expected_mutation=mutation,
    )


def test_frame_manifest_fails_closed_after_body_change(tmp_path: Path):
    config = yaml.safe_load((MODULE_DIR / "config.yaml").read_text())
    receptor = "Gpr2"
    mutation = "R59C"
    receptor_cfg = config["receptors"][receptor]
    source = (
        ROOT
        / config["paths"]["mutagenesis_dir"]
        / "af3_structures"
        / receptor
    )
    helices = [
        config["tm_topology"][receptor]["helices"][key]
        for key in sorted(config["tm_topology"][receptor]["helices"])
    ]
    aligned_full = tmp_path / "aligned.pdb"
    aligned_tm = tmp_path / "aligned_tm.pdb"
    manifest = tmp_path / "frame_manifest.json"
    align_mutant_to_wt(
        receptor=receptor,
        mutation=mutation,
        wt_full_pdb=ROOT / config["paths"]["receptor_dir"] / receptor_cfg["pdb_file"],
        wt_tm_pdb=ROOT
        / config["paths"]["prepared_dir"]
        / "receptors"
        / f"{Path(receptor_cfg['pdb_file']).stem}_tm.pdb",
        mutant_full_pdb=source / f"{mutation}.pdb",
        mutant_tm_pdb=source / f"{mutation}_tm.pdb",
        aligned_full_pdb=aligned_full,
        aligned_tm_pdb=aligned_tm,
        manifest_path=manifest,
        helices=helices,
    )
    aligned_tm.write_text(aligned_tm.read_text() + "REMARK tampered\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_frame_manifest(manifest, aligned_tm_pdb=aligned_tm)


def test_pdb_pdbqt_frame_check_and_pose_count(tmp_path: Path):
    atoms = [
        pdb_atom_line(1, "CA", "ALA", "A", 1, (1.0, 2.0, 3.0), "C"),
        pdb_atom_line(2, "CB", "ALA", "A", 1, (2.0, 2.0, 3.0), "C"),
    ]
    pdb = tmp_path / "receptor.pdb"
    pdbqt = tmp_path / "receptor.pdbqt"
    pdb.write_text("".join(atoms) + "END\n")
    pdbqt.write_text("".join(atoms) + "END\n")
    report = compare_pdb_pdbqt_frame(pdb, pdbqt)
    assert report["common_heavy_atom_count"] == 2
    assert report["max_coordinate_delta_angstrom"] == 0.0

    shifted = atoms.copy()
    shifted[1] = pdb_atom_line(2, "CB", "ALA", "A", 1, (2.1, 2.0, 3.0), "C")
    pdbqt.write_text("".join(shifted) + "END\n")
    with pytest.raises(ValueError, match="改变 receptor frame"):
        compare_pdb_pdbqt_frame(pdb, pdbqt)

    poses = tmp_path / "poses.pdbqt"
    poses.write_text(
        "".join(
            f"MODEL {model}\n"
            + f"REMARK VINA RESULT: {-5.0 - model / 100:.3f} 0.000 0.000\n"
            + pdb_atom_line(model, "C1", "LIG", "X", 901, (model, 0.0, 0.0), "C")
            + "ENDMDL\n"
            for model in range(1, 21)
        )
    )
    assert len(split_pdbqt_models(poses)) == 20
    poses.write_text(poses.read_text().replace("MODEL 20\n", "").replace("ENDMDL\n", "", 1))
    with pytest.raises(ValueError):
        split_pdbqt_models(poses)


def test_frame_manifest_content_identity_is_canonical(tmp_path: Path):
    payload = {
        "schema": "docking-frame-alignment-v2",
        "status": "frame_aligned",
        "alignment_selection": {"ca_count": 147},
        "files": {},
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="manifest_identity"):
        verify_frame_manifest(path)
