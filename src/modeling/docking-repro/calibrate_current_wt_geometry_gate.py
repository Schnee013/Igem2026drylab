"""Freeze a portable geometry gate from two current-toolchain WT runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from docking_manifest import sha256_file
from frame_alignment import canonical_json_bytes, write_canonical_json
from geometry_calibration import (
    CURRENT_GATE_ARTIFACT_SCHEMA,
    derive_current_toolchain_gate,
)


METHOD = {
    "name": "two_seed_current_toolchain_wt_dominant_protein_cluster_v1",
    "calibration_seeds": [42, 43],
    "requested_max_modes": 20,
    "height_margin_angstrom": 0.25,
    "radial_margin_angstrom": 0.25,
    "protein_closer_fraction": 0.8,
    "passing_mode_margin": 2,
    "definitions": {
        "calibration_positive_pose": (
            "inside the shared docking box, has a standard ProLIF contact, "
            "and belongs to the unique modal protein-closer atom-count group "
            "for the receptor/ligand across both WT seeds"
        ),
        "height_window": (
            "receptor-level minimum/maximum calibration-positive absolute "
            "membrane height, expanded by the frozen numeric margin"
        ),
        "radial_limit": (
            "receptor-level maximum calibration-positive radial distance, "
            "expanded by the frozen numeric margin; evaluated strictly less than"
        ),
        "protein_limit": (
            "ceiling of the frozen fraction times the ligand-specific modal "
            "protein-closer atom count"
        ),
        "pose_population_limit": (
            "minimum passing count across the two WT seeds minus the frozen "
            "absolute passing-mode margin"
        ),
    },
}


def _verify_content_identity(
    payload: dict[str, Any],
    *,
    identity_key: str,
    label: str,
) -> None:
    body = dict(payload)
    expected = body.pop(identity_key, None)
    actual = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    if not isinstance(expected, str) or expected != actual:
        raise ValueError(f"{label} content identity mismatch")


def _portable_path(path: Path, *, project_root: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _source_arm(
    *,
    run_root: Path,
    seed: int,
    receptor: str,
    ligand: str,
    project_root: Path,
) -> dict[str, Any]:
    report_path = (
        run_root
        / "docking"
        / "jobs"
        / receptor
        / "WT"
        / ligand
        / "geometry"
        / "geometry_report.json"
    )
    job_manifest_path = report_path.parents[1] / "job_manifest.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    _verify_content_identity(
        report,
        identity_key="manifest_identity",
        label=f"{seed}/{receptor}/{ligand} geometry report",
    )
    job = json.loads(job_manifest_path.read_text(encoding="utf-8"))
    _verify_content_identity(
        job,
        identity_key="manifest_identity",
        label=f"{seed}/{receptor}/{ligand} job manifest",
    )
    if (
        job.get("schema") != "docking-job-v3"
        or job.get("status") != "technical_complete"
        or job.get("inputs", {}).get("receptor") != receptor
        or job.get("inputs", {}).get("mutation") != "WT"
        or job.get("inputs", {}).get("ligand") != ligand
        or int(job.get("outputs", {}).get("poses", {}).get("model_count", -1))
        != METHOD["requested_max_modes"]
        or int(
            job.get("outputs", {})
            .get("poses", {})
            .get("requested_max_modes", -1)
        )
        != METHOD["requested_max_modes"]
    ):
        raise ValueError(f"calibration job contract mismatch: {receptor}/{ligand}")
    if int(job["inputs"]["seed"]) != seed:
        raise ValueError(f"calibration seed mismatch: {receptor}/{ligand}")
    if (
        report.get("job", {}).get("job_identity") != job["job_identity"]
        or report.get("job", {}).get("manifest_identity")
        != job["manifest_identity"]
        or report.get("pose_file", {}).get("sha256")
        != job["outputs"]["poses"]["sha256"]
    ):
        raise ValueError(f"geometry/job identity mismatch: {receptor}/{ligand}")
    poses = []
    for pose in report.get("poses", []):
        poses.append(
            {
                "model": int(pose["model"]),
                "pose_body_sha256": pose["pose_body_sha256"],
                "affinity": float(pose["affinity"]),
                "radial_to_tm_axis_angstrom": float(
                    pose["radial_to_tm_axis_angstrom"]
                ),
                "membrane_absolute_height_angstrom": float(
                    pose["membrane_absolute_height_angstrom"]
                ),
                "protein_closer_atom_count": int(
                    pose["protein_vs_membrane"][
                        "protein_closer_atom_count"
                    ]
                ),
                "inside_shared_box": bool(
                    pose["checks"]["inside_shared_box"]
                ),
                "standard_prolif_contact": bool(
                    pose["checks"]["prolif_contact"]
                ),
            }
        )
    return {
        "seed": seed,
        "receptor": receptor,
        "ligand": ligand,
        "mutation": "WT",
        "actual_modes": int(report["actual_modes"]),
        "source": {
            "run_root": _portable_path(run_root, project_root=project_root),
            "geometry_report": {
                "path": _portable_path(
                    report_path,
                    project_root=project_root,
                ),
                "sha256": sha256_file(report_path),
                "manifest_identity": report["manifest_identity"],
            },
            "job_manifest": {
                "path": _portable_path(
                    job_manifest_path,
                    project_root=project_root,
                ),
                "sha256": sha256_file(job_manifest_path),
                "job_identity": job["job_identity"],
                "manifest_identity": job["manifest_identity"],
            },
            "pose_file_sha256": job["outputs"]["poses"]["sha256"],
            "environment_manifest_identity": job["inputs"]["environment"][
                "manifest_identity"
            ],
        },
        "poses": poses,
    }


def build_artifact(
    *,
    seed42_root: Path,
    seed43_root: Path,
    project_root: Path,
) -> dict[str, Any]:
    roots = {
        42: seed42_root.resolve(),
        43: seed43_root.resolve(),
    }
    source_arms = [
        _source_arm(
            run_root=roots[seed],
            seed=seed,
            receptor=receptor,
            ligand=ligand,
            project_root=project_root,
        )
        for seed in METHOD["calibration_seeds"]
        for receptor in ("Gpr2", "Gpr3")
        for ligand in ("ascr18", "ascr3")
    ]
    artifact: dict[str, Any] = {
        "schema": CURRENT_GATE_ARTIFACT_SCHEMA,
        "status": "frozen_before_holdout_and_mutant_results",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "allowed_use": (
            "freeze geometry thresholds for an independent-seed holdout and, "
            "only after that holdout passes, the bound full docking matrix"
        ),
        "forbidden_use": (
            "threshold fitting from holdout/mutant results or biological "
            "ranking from these WT calibration poses"
        ),
        "method": METHOD,
        "source_arms": source_arms,
    }
    artifact["derived_gate"] = derive_current_toolchain_gate(
        source_arms,
        method=METHOD,
    )
    artifact["gate_identity"] = hashlib.sha256(
        canonical_json_bytes(artifact)
    ).hexdigest()
    return artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed42-run-root", required=True)
    parser.add_argument("--seed43-run-root", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--confirm-freeze",
        action="store_true",
        help="required after explicit authorization to freeze the gate",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.confirm_freeze:
        raise PermissionError("geometry gate freeze authorization not confirmed")
    output = Path(args.output).resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite frozen gate: {output}")
    artifact = build_artifact(
        seed42_root=Path(args.seed42_run_root),
        seed43_root=Path(args.seed43_run_root),
        project_root=Path(args.project_root).resolve(),
    )
    write_canonical_json(output, artifact)
    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": sha256_file(output),
                "gate_identity": artifact["gate_identity"],
                "derived_gate": artifact["derived_gate"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
