"""Finalize an incomplete/failed frame-repair smoke without running more jobs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from docking_manifest import (  # noqa: E402
    load_json,
    parse_vina_pose_models,
    sha256_file,
    verify_environment_manifest,
    verify_frame_run_manifest,
    verify_job_manifest,
)
from frame_alignment import canonical_json_bytes, write_canonical_json  # noqa: E402
from run_frame_repair_docking import build_subject_matrix  # noqa: E402
from utils import load_config  # noqa: E402


SCHEMA = "docking-frame-repair-smoke-terminal-v2"


def _file_record(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256_file(path)}


def _attempt_evidence(
    attempt_dir: Path, requested_max_modes: int
) -> dict[str, Any]:
    status_path = attempt_dir / "attempt_status.json"
    status = load_json(status_path)
    evidence: dict[str, Any] = {
        "attempt": attempt_dir.name,
        "status": status,
        "status_file": _file_record(status_path),
    }
    pose_files = sorted(attempt_dir.glob("*_poses.pdbqt"))
    if len(pose_files) > 1:
        raise ValueError(f"failed attempt has multiple pose bodies: {attempt_dir}")
    if pose_files:
        pose_path = pose_files[0]
        models = parse_vina_pose_models(pose_path)
        evidence["pose_file"] = {
            **_file_record(pose_path),
            "requested_max_model_count": requested_max_modes,
            "actual_model_count": len(models),
            "model_body_sha256": [model.body_sha256 for model in models],
        }
    command_files = sorted(attempt_dir.glob("*.vina.command.json"))
    stdout_files = sorted(attempt_dir.glob("*.vina.stdout.txt"))
    stderr_files = sorted(attempt_dir.glob("*.vina.stderr.txt"))
    for label, files in (
        ("command", command_files),
        ("stdout", stdout_files),
        ("stderr", stderr_files),
    ):
        if len(files) > 1:
            raise ValueError(f"failed attempt has multiple {label} files: {attempt_dir}")
        if files:
            evidence[label] = _file_record(files[0])
    return evidence


def write_terminal_state(
    frame_run_root: Path,
    *,
    terminal_path: Path,
    detail: dict[str, Any],
    observed_at: str,
) -> tuple[Path, Path]:
    events_path = frame_run_root / "run_state_events.tsv"
    snapshot_path = frame_run_root / "terminal_status.tsv"
    if events_path.exists() or snapshot_path.exists():
        raise FileExistsError("run state authority already exists; refusing overwrite")
    source = str(terminal_path.resolve())
    detail_text = json.dumps(detail, ensure_ascii=False, sort_keys=True)
    header = ["observed_at", "state", "source", "detail"]
    row = [observed_at, "TERMINAL_ABNORMAL", source, detail_text]
    for path in (events_path, snapshot_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            writer.writerow(header)
            writer.writerow(row)
    return events_path, snapshot_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--frame-run-root", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    frame_run_root = Path(args.frame_run_root).resolve()
    run_manifest_path = frame_run_root / "run_manifest.json"
    run_manifest = verify_frame_run_manifest(run_manifest_path, verify_records=True)
    environment_path = frame_run_root / "environment_manifest.json"
    environment = verify_environment_manifest(
        environment_path,
        expected_frame_run_root=frame_run_root,
        require_production_ready=True,
    )
    config_sha256 = sha256_file(config_path)
    if (
        run_manifest["inputs"]["config"]["sha256"] != config_sha256
        or environment["configuration"]["sha256"] != config_sha256
    ):
        raise ValueError("failed-smoke finalizer config/run/environment mismatch")

    technical_completion = frame_run_root / "docking/smoke_technical_completion.json"
    full_plan = frame_run_root / "docking/full_job_plan.json"
    full_completion = frame_run_root / "docking/full_technical_completion.json"
    if technical_completion.exists():
        raise ValueError("smoke technical completion exists; failure finalizer is invalid")
    if full_plan.exists() or full_completion.exists():
        raise ValueError("full-run artifact exists after failed smoke")

    terminal_path = frame_run_root / "terminal/smoke_terminal.json"
    if terminal_path.exists():
        raise FileExistsError(f"refusing to overwrite smoke terminal: {terminal_path}")

    requested_max_modes = int(
        config["frame_repair"]["requested_max_modes_per_job"]
    )
    completed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    unattempted: list[dict[str, str]] = []
    matrix = build_subject_matrix(run_manifest, run_mode="smoke")
    for receptor, mutation, ligand in matrix:
        key = {
            "receptor": receptor,
            "mutation": mutation,
            "ligand": ligand,
        }
        job_root = frame_run_root / "docking/jobs" / receptor / mutation / ligand
        job_manifest_path = job_root / "job_manifest.json"
        attempt_dirs = sorted(
            path
            for path in (job_root / "attempts").glob("attempt-*")
            if path.is_dir()
        )
        if job_manifest_path.exists():
            job = verify_job_manifest(
                job_manifest_path,
                requested_max_modes=requested_max_modes,
            )
            if not attempt_dirs:
                raise ValueError(f"completed job has no attempt evidence: {job_root}")
            record = {
                **key,
                "job_identity": job["job_identity"],
                "job_manifest": {
                    **_file_record(job_manifest_path),
                    "manifest_identity": job["manifest_identity"],
                },
                "pose_file": job["outputs"]["poses"],
                "pose_population": job["outputs"]["pose_population"],
                "model1_affinity": job["outputs"]["score"]["model1_affinity"],
                "attempt": _attempt_evidence(
                    attempt_dirs[-1], requested_max_modes
                ),
            }
            if job["outputs"]["pose_population"]["comparable"]:
                completed.append(record)
            else:
                failed.append(
                    {
                        **record,
                        "failure_type": "non_comparable_pose_population",
                    }
                )
            continue
        if attempt_dirs:
            attempts = [
                _attempt_evidence(attempt_dir, requested_max_modes)
                for attempt_dir in attempt_dirs
            ]
            if not any(
                attempt["status"].get("status")
                in {
                    "technical_failure",
                    "non_comparable_pose_population",
                }
                for attempt in attempts
            ):
                raise ValueError(f"incomplete job lacks technical failure: {job_root}")
            failed.append({**key, "attempts": attempts})
        else:
            unattempted.append(key)

    if not failed:
        raise ValueError("failure finalizer requires at least one failed smoke job")
    if len(completed) + len(failed) + len(unattempted) != len(matrix):
        raise ValueError("failed smoke accounting mismatch")

    observed_at = datetime.now(timezone.utc).isoformat()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "fail_stop_before_full",
        "observed_at_utc": observed_at,
        "stop_reason": "technical_or_pose_population_gate_failed",
        "requested_max_modes_per_job": requested_max_modes,
        "scope": {
            "planned_jobs": len(matrix),
            "completed_jobs": len(completed),
            "failed_jobs": len(failed),
            "unattempted_jobs": len(unattempted),
        },
        "frame_run": {
            **_file_record(run_manifest_path),
            "run_identity": run_manifest["run_identity"],
        },
        "environment": {
            **_file_record(environment_path),
            "manifest_identity": environment["manifest_identity"],
        },
        "configuration": _file_record(config_path),
        "finalizer": _file_record(Path(__file__).resolve()),
        "completed": completed,
        "failed": failed,
        "unattempted": unattempted,
        "full_run_authorized": False,
        "full_run_started": False,
    }
    payload["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    write_canonical_json(terminal_path, payload)
    events_path, snapshot_path = write_terminal_state(
        frame_run_root,
        terminal_path=terminal_path,
        detail={
            "stop_reason": payload["stop_reason"],
            **payload["scope"],
            "terminal_manifest_identity": payload["manifest_identity"],
        },
        observed_at=observed_at,
    )
    print(
        json.dumps(
            {
                "terminal": str(terminal_path),
                "terminal_manifest_identity": payload["manifest_identity"],
                "scope": payload["scope"],
                "run_state_events": str(events_path),
                "terminal_status": str(snapshot_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
