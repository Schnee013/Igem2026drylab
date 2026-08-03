"""Validate and summarize IFP/geometry diagnostics for four WT jobs."""

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

from docking_manifest import load_json, sha256_file, verify_job_manifest
from evaluate_frame_repair_geometry import verify_ifp_report
from frame_alignment import canonical_json_bytes, write_canonical_json
from run_frame_repair_wt_calibration import build_wt_calibration_matrix


def _verify_identity(payload: dict[str, Any], *, label: str) -> None:
    body = dict(payload)
    expected = body.pop("manifest_identity", None)
    actual = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    if not isinstance(expected, str) or expected != actual:
        raise ValueError(f"{label} content identity mismatch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration-run-root", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = Path(args.calibration_run_root).resolve()
    technical_path = (
        run_root
        / "docking"
        / "wt_calibration_technical_completion.json"
    )
    technical = load_json(technical_path)
    _verify_identity(technical, label="WT calibration technical completion")
    if (
        technical.get("schema")
        != "docking-frame-repair-wt-calibration-completion-v1"
        or technical.get("job_count") != 4
    ):
        raise ValueError("WT calibration technical completion 不完整")

    expected_matrix = build_wt_calibration_matrix()
    jobs: list[dict[str, Any]] = []
    for receptor, mutation, ligand in expected_matrix:
        job_root = (
            run_root
            / "docking"
            / "jobs"
            / receptor
            / mutation
            / ligand
        )
        job_path = job_root / "job_manifest.json"
        job = verify_job_manifest(
            job_path,
            expected_receptor=receptor,
            expected_mutation="WT",
            expected_ligand=ligand,
            requested_max_modes=20,
        )
        ifp_path = job_root / "ifp" / "ifp_report.json"
        ifp, _contacts = verify_ifp_report(ifp_path, job=job)
        geometry_path = job_root / "geometry" / "geometry_report.json"
        geometry = load_json(geometry_path)
        _verify_identity(geometry, label=f"{receptor}/{ligand} geometry")
        if (
            geometry.get("schema") != "docking-geometry-report-v2"
            or geometry.get("status") != "evaluated"
            or geometry.get("job", {}).get("job_identity")
            != job["job_identity"]
            or geometry.get("pose_file", {}).get("sha256")
            != job["outputs"]["poses"]["sha256"]
            or geometry.get("ifp_report", {}).get("manifest_identity")
            != ifp["manifest_identity"]
        ):
            raise ValueError(f"{receptor}/{ligand} geometry binding mismatch")
        pose_models = job["outputs"]["poses"]["models"]
        actual_modes = int(job["outputs"]["poses"]["model_count"])
        if not 1 <= actual_modes <= 20 or len(pose_models) != actual_modes:
            raise ValueError(f"{receptor}/{ligand} maximum-20 contract failed")
        jobs.append(
            {
                "receptor": receptor,
                "mutation": "WT",
                "ligand": ligand,
                "job_manifest": {
                    "path": str(job_path),
                    "sha256": sha256_file(job_path),
                    "manifest_identity": job["manifest_identity"],
                    "job_identity": job["job_identity"],
                },
                "pose_file": job["outputs"]["poses"],
                "requested_max_modes": 20,
                "actual_modes": actual_modes,
                "best_pose": {
                    "model": pose_models[0]["model_number"],
                    "affinity": pose_models[0]["affinity"],
                    "body_sha256": pose_models[0]["body_sha256"],
                },
                "ifp": {
                    "path": str(ifp_path),
                    "sha256": sha256_file(ifp_path),
                    "manifest_identity": ifp["manifest_identity"],
                    "all_models_have_standard_prolif_contact": ifp[
                        "all_models_have_standard_prolif_contact"
                    ],
                },
                "historical_geometry_gate_audit": {
                    "path": str(geometry_path),
                    "sha256": sha256_file(geometry_path),
                    "manifest_identity": geometry["manifest_identity"],
                    "pass": geometry["pass"],
                    "distribution_pass": geometry["distribution_pass"],
                    "model1_pass": geometry["model1_pass"],
                    "passing_mode_count": geometry["passing_mode_count"],
                },
            }
        )

    summary: dict[str, Any] = {
        "schema": "docking-frame-repair-wt-calibration-postprocess-v1",
        "status": "technical_and_diagnostic_postprocess_complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "job_count": len(jobs),
        "seed": technical["seed"],
        "finalizer": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "returned_mode_contract": (
            "1 <= actual_modes <= requested_max_modes"
        ),
        "gate_status": "not_frozen",
        "allowed_use": (
            "WT-only seed-43 replicate evidence and visual pose review; "
            "historical geometry thresholds are diagnostic only"
        ),
        "forbidden_use": (
            "do not start mutant/full docking, ranking, candidate selection, "
            "or freeze a new geometry gate from this file alone"
        ),
        "technical_completion": {
            "path": str(technical_path),
            "sha256": sha256_file(technical_path),
            "manifest_identity": technical["manifest_identity"],
        },
        "jobs": jobs,
    }
    summary["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(summary)
    ).hexdigest()
    output = (
        run_root
        / "docking"
        / "wt_calibration_postprocess_completion.json"
    )
    if output.exists():
        raise FileExistsError(f"拒绝覆盖既有 postprocess summary: {output}")
    write_canonical_json(output, summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "job_count": len(jobs),
                "actual_modes": [job["actual_modes"] for job in jobs],
                "geometry_pass": [
                    job["historical_geometry_gate_audit"]["pass"]
                    for job in jobs
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
