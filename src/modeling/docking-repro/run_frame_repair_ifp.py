"""Generate per-MODEL ProLIF evidence for one verified frame-repair job."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from rdkit import Chem

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from docking_manifest import (
    load_json,
    parse_vina_pose_models,
    sha256_file,
    verify_environment_manifest,
    verify_job_manifest,
)
from frame_alignment import (
    canonical_json_bytes,
    parse_atom_lines,
    sha256_file as frame_sha256_file,
    write_canonical_json,
)
from run_ifp_analysis import (
    ALL_INTERACTION_TYPES,
    analyze_pair,
)
from utils import load_config


IFP_REPORT_SCHEMA = "docking-run-local-ifp-v2"
SDF_VINA_RESULT_RE = re.compile(
    r"VINA RESULT:\s+([-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?)"
)


def run_checked(command: list[str], *, label: str) -> dict[str, Any]:
    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"{label} failed ({result.returncode}): {result.stderr.strip()}"
        )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def verify_sdf_pose_binding(
    pose_pdbqt: Path,
    pose_sdf: Path,
    *,
    actual_modes: int,
    coordinate_tolerance_angstrom: float = 0.0011,
) -> list[dict[str, Any]]:
    """Bind each OpenBabel SDF record to the source PDBQT MODEL in order."""
    pdbqt_models = parse_vina_pose_models(pose_pdbqt)
    if len(pdbqt_models) != actual_modes:
        raise ValueError(
            f"PDBQT MODEL completeness failed: "
            f"job={actual_modes}, converted={len(pdbqt_models)}"
        )
    supplier = Chem.SDMolSupplier(
        str(pose_sdf),
        removeHs=False,
        sanitize=False,
        strictParsing=True,
    )
    sdf_molecules = list(supplier)
    if len(sdf_molecules) != actual_modes or any(
        molecule is None for molecule in sdf_molecules
    ):
        raise ValueError(
            f"SDF record completeness failed: "
            f"job={actual_modes}, converted={len(sdf_molecules)}"
        )

    evidence: list[dict[str, Any]] = []
    for index, (pdbqt_model, molecule) in enumerate(
        zip(pdbqt_models, sdf_molecules, strict=True),
        start=1,
    ):
        assert molecule is not None
        if not molecule.HasProp("MODEL") or not molecule.HasProp("REMARK"):
            raise ValueError(f"SDF record {index} 缺少 MODEL/REMARK provenance")
        try:
            sdf_model_number = int(molecule.GetProp("MODEL").strip())
        except ValueError as exc:
            raise ValueError(f"SDF record {index} MODEL 非整数") from exc
        if sdf_model_number != index or pdbqt_model.model_number != index:
            raise ValueError(
                f"SDF/PDBQT MODEL order mismatch: "
                f"record={index}, sdf={sdf_model_number}, "
                f"pdbqt={pdbqt_model.model_number}"
            )
        affinity_match = SDF_VINA_RESULT_RE.search(molecule.GetProp("REMARK"))
        if affinity_match is None:
            raise ValueError(f"SDF record {index} REMARK 缺少 VINA RESULT")
        sdf_affinity = float(affinity_match.group(1))
        if abs(sdf_affinity - pdbqt_model.affinity) > 1e-9:
            raise ValueError(
                f"SDF/PDBQT affinity mismatch for MODEL {index}: "
                f"{sdf_affinity} != {pdbqt_model.affinity}"
            )

        pdbqt_atoms = parse_atom_lines(
            pdbqt_model.body.splitlines(),
            source=f"{pose_pdbqt}#MODEL{index}",
            first_model_only=False,
        )
        if molecule.GetNumAtoms() != len(pdbqt_atoms):
            raise ValueError(
                f"SDF/PDBQT atom count mismatch for MODEL {index}: "
                f"{molecule.GetNumAtoms()} != {len(pdbqt_atoms)}"
            )
        sdf_elements = [atom.GetSymbol().upper() for atom in molecule.GetAtoms()]
        pdbqt_elements = [
            (atom.element or atom.atom_name[:1]).upper() for atom in pdbqt_atoms
        ]
        if sdf_elements != pdbqt_elements:
            raise ValueError(
                f"SDF/PDBQT element order mismatch for MODEL {index}"
            )
        conformer = molecule.GetConformer()
        sdf_coordinates = np.asarray(
            [
                list(conformer.GetAtomPosition(atom_index))
                for atom_index in range(molecule.GetNumAtoms())
            ],
            dtype=float,
        )
        pdbqt_coordinates = np.vstack([atom.coord for atom in pdbqt_atoms])
        coordinate_delta = np.linalg.norm(
            sdf_coordinates - pdbqt_coordinates,
            axis=1,
        )
        maximum_delta = float(coordinate_delta.max())
        if maximum_delta > coordinate_tolerance_angstrom:
            raise ValueError(
                f"SDF/PDBQT coordinate mismatch for MODEL {index}: "
                f"max_delta={maximum_delta:.6f} Å"
            )
        evidence.append(
            {
                "model_number": index,
                "affinity": pdbqt_model.affinity,
                "pose_body_sha256": pdbqt_model.body_sha256,
                "atom_count": len(pdbqt_atoms),
                "element_order_sha256": hashlib.sha256(
                    "\n".join(pdbqt_elements).encode("utf-8")
                ).hexdigest(),
                "max_coordinate_delta_angstrom": maximum_delta,
                "coordinate_tolerance_angstrom": coordinate_tolerance_angstrom,
            }
        )
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--job-manifest", required=True)
    parser.add_argument(
        "--output",
        default=None,
        help="默认写入 job manifest 同目录的 ifp/ifp_report.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    job_manifest_path = Path(args.job_manifest).resolve()
    job = verify_job_manifest(job_manifest_path)
    inputs = job["inputs"]
    environment_path = Path(inputs["environment"]["path"])
    environment = verify_environment_manifest(environment_path)
    config_path = Path(args.config).resolve()
    environment_config = environment["configuration"]
    if (
        Path(environment_config["path"]).resolve() != config_path
        or environment_config["sha256"] != frame_sha256_file(config_path)
    ):
        raise ValueError("IFP config 与 docking environment manifest 不同源")
    obabel = environment["executables"]["openbabel"]
    if not obabel.get("path"):
        raise ValueError("environment manifest 未绑定 OpenBabel executable")

    receptor_manifest = load_json(
        Path(inputs["receptor_pdbqt"]["manifest"]["path"])
    )
    receptor_pdb = Path(receptor_manifest["aligned_pdb"]["path"])
    pose_pdbqt = Path(job["outputs"]["poses"]["path"])
    output_path = (
        Path(args.output).resolve()
        if args.output
        else job_manifest_path.parent / "ifp" / "ifp_report.json"
    )
    output_dir = output_path.parent
    if output_path.exists():
        raise FileExistsError(f"拒绝覆盖既有 IFP report: {output_path}")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"拒绝复用非空 IFP 中间目录: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    receptor_with_h = output_dir / "receptor_with_h.pdb"
    pose_sdf = output_dir / "poses.sdf"
    for intermediate in (receptor_with_h, pose_sdf):
        if intermediate.exists():
            raise FileExistsError(f"拒绝覆盖既有 IFP 中间体: {intermediate}")

    add_h = run_checked(
        [
            obabel["path"],
            str(receptor_pdb),
            "-O",
            str(receptor_with_h),
            "-h",
        ],
        label="OpenBabel receptor hydrogenation",
    )
    convert = run_checked(
        [
            obabel["path"],
            str(pose_pdbqt),
            "-O",
            str(pose_sdf),
        ],
        label="OpenBabel PDBQT to SDF",
    )
    requested_max_modes = config["frame_repair"][
        "requested_max_modes_per_job"
    ]
    actual_modes = int(job["outputs"]["poses"]["model_count"])
    if (
        requested_max_modes != job["inputs"]["vina"]["requested_max_modes"]
        or not 1 <= actual_modes <= requested_max_modes
    ):
        raise ValueError("IFP job pose count 与 requested maximum 合同不一致")
    if not job["outputs"]["pose_population"]["comparable"]:
        raise ValueError("IFP 拒绝 non_comparable_pose_population job")
    sdf_pose_binding = verify_sdf_pose_binding(
        pose_pdbqt,
        pose_sdf,
        actual_modes=actual_modes,
    )

    ligand_cfg = config["ligands"][inputs["ligand"]]
    dataframe, molecule_count = analyze_pair(
        receptor_with_h,
        pose_sdf,
        top_n=actual_modes,
        template_smiles=ligand_cfg["smiles_pH74"],
        pocket_mode="all_pose_heavy_atom_union",
    )
    if molecule_count != actual_modes or len(dataframe) != actual_modes:
        raise ValueError(
            f"IFP molecule completeness failed: "
            f"job={actual_modes}, molecules={molecule_count}, rows={len(dataframe)}"
        )

    pose_models = job["outputs"]["poses"]["models"]
    model_records: list[dict[str, Any]] = []
    for index in range(actual_modes):
        row = dataframe.iloc[index]
        interactions = []
        for column in dataframe.columns:
            if bool(row[column]):
                interactions.append(
                    {
                        "ligand_residue": str(column[0]),
                        "protein_residue": str(column[1]),
                        "interaction": str(column[2]),
                    }
                )
        model = pose_models[index]
        if model["model_number"] != index + 1:
            raise ValueError("job pose MODEL order is not canonical")
        model_records.append(
            {
                "model_number": model["model_number"],
                "pose_body_sha256": model["body_sha256"],
                "affinity": model["affinity"],
                "has_standard_prolif_contact": bool(interactions),
                "interaction_count": len(interactions),
                "interactions": interactions,
            }
        )

    payload: dict[str, Any] = {
        "schema": IFP_REPORT_SCHEMA,
        "status": "complete",
        "job": {
            "manifest_path": str(job_manifest_path),
            "manifest_sha256": sha256_file(job_manifest_path),
            "job_identity": job["job_identity"],
            "manifest_identity": job["manifest_identity"],
        },
        "configuration": {
            "path": str(config_path),
            "sha256": frame_sha256_file(config_path),
        },
        "pose_file": {
            "path": str(pose_pdbqt),
            "sha256": sha256_file(pose_pdbqt),
            "requested_max_modes": requested_max_modes,
            "model_count": actual_modes,
        },
        "receptor_input": {
            "path": str(receptor_pdb),
            "sha256": sha256_file(receptor_pdb),
        },
        "conversion": {
            "openbabel": {
                "path": obabel["path"],
                "sha256": obabel["sha256"],
                "version": environment["observed_versions"][
                    "openbabel_conda_package"
                ],
            },
            "receptor_hydrogenation": add_h,
            "pose_conversion": convert,
            "receptor_with_h": {
                "path": str(receptor_with_h),
                "sha256": sha256_file(receptor_with_h),
            },
            "pose_sdf": {
                "path": str(pose_sdf),
                "sha256": sha256_file(pose_sdf),
            },
            "sdf_pose_binding": sdf_pose_binding,
        },
        "prolif": {
            "version": environment["analysis_packages"]["prolif"],
            "interaction_types": ALL_INTERACTION_TYPES,
            "template_smiles_pH74": ligand_cfg["smiles_pH74"],
        },
        "models": model_records,
        "all_models_have_standard_prolif_contact": all(
            record["has_standard_prolif_contact"] for record in model_records
        ),
    }
    payload["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    write_canonical_json(output_path, payload)
    print(output_path)


if __name__ == "__main__":
    main()
