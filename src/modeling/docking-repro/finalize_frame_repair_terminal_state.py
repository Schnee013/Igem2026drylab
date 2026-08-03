"""Finalize an existing frame-repair smoke terminal as run-state authority."""

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
_SOURCE_DIR = (
    _THIS_DIR
    if (_THIS_DIR / "aggregate_frame_repair_terminal.py").is_file()
    else _THIS_DIR.parent / "src/modeling/docking-repro"
)
sys.path.insert(0, str(_SOURCE_DIR))

from aggregate_frame_repair_terminal import (  # noqa: E402
    collect_job,
    verify_comparable_job_contracts,
    verify_technical_completion,
)
from docking_manifest import (  # noqa: E402
    load_json,
    sha256_file,
    verify_environment_manifest,
    verify_frame_run_manifest,
)
from frame_alignment import canonical_json_bytes  # noqa: E402
from run_frame_repair_docking import build_subject_matrix  # noqa: E402
from utils import load_config  # noqa: E402


TERMINAL_SCHEMA = "docking-frame-repair-smoke-terminal-v2"
TERMINAL_STATUSES = {"pass", "fail_stop_before_full"}


def verify_existing_smoke_terminal(
    *,
    config_path: Path,
    frame_run_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify the immutable smoke terminal against all current run evidence."""
    config_path = config_path.resolve()
    frame_run_root = frame_run_root.resolve()
    config = load_config(config_path)
    config_sha256 = sha256_file(config_path)

    run_manifest_path = frame_run_root / "run_manifest.json"
    run_manifest = verify_frame_run_manifest(
        run_manifest_path,
        verify_records=True,
    )
    environment_path = frame_run_root / "environment_manifest.json"
    environment = verify_environment_manifest(
        environment_path,
        expected_frame_run_root=frame_run_root,
        require_production_ready=True,
    )
    if (
        Path(run_manifest["inputs"]["config"]["path"]).resolve() != config_path
        or run_manifest["inputs"]["config"]["sha256"] != config_sha256
        or Path(environment["configuration"]["path"]).resolve() != config_path
        or environment["configuration"]["sha256"] != config_sha256
    ):
        raise ValueError("terminal finalization config/run/environment 不同源")

    terminal_path = frame_run_root / "terminal/smoke_terminal.json"
    terminal = load_json(terminal_path)
    if (
        terminal.get("schema") != TERMINAL_SCHEMA
        or terminal.get("status") not in TERMINAL_STATUSES
        or terminal.get("job_count") != 8
    ):
        raise ValueError("smoke terminal schema、状态或 job 数量不可用")
    terminal_body = dict(terminal)
    expected_identity = terminal_body.pop("manifest_identity", None)
    actual_identity = hashlib.sha256(
        canonical_json_bytes(terminal_body)
    ).hexdigest()
    if not expected_identity or actual_identity != expected_identity:
        raise ValueError("smoke terminal content identity mismatch")
    if (
        terminal.get("frame_run", {}).get("run_identity")
        != run_manifest["run_identity"]
        or terminal.get("frame_run", {}).get("sha256")
        != sha256_file(run_manifest_path)
        or terminal.get("environment", {}).get("manifest_identity")
        != environment["manifest_identity"]
        or terminal.get("environment", {}).get("sha256")
        != sha256_file(environment_path)
        or terminal.get("configuration", {}).get("sha256") != config_sha256
    ):
        raise ValueError("smoke terminal 与 run/config/environment 不同源")

    expected_matrix = build_subject_matrix(run_manifest, run_mode="smoke")
    recorded_by_key = {
        (job["receptor"], job["mutation"], job["ligand"]): job
        for job in terminal.get("jobs", [])
    }
    if (
        len(recorded_by_key) != len(terminal.get("jobs", []))
        or set(recorded_by_key) != set(expected_matrix)
    ):
        raise ValueError("smoke terminal job matrix mismatch")

    requested_max_modes = int(
        config["frame_repair"]["requested_max_modes_per_job"]
    )
    current_jobs: list[dict[str, Any]] = []
    for receptor, mutation, ligand in expected_matrix:
        current = collect_job(
            frame_run_root=frame_run_root,
            receptor=receptor,
            mutation=mutation,
            ligand=ligand,
            requested_max_modes=requested_max_modes,
            expected_environment_identity=environment["manifest_identity"],
            expected_config_sha256=config_sha256,
            expected_run_identity=run_manifest["run_identity"],
        )
        recorded = recorded_by_key[(receptor, mutation, ligand)]
        for field in (
            "job_identity",
            "job_manifest_identity",
            "pose_sha256",
            "ifp_manifest_identity",
            "geometry_manifest_identity",
            "pose_model_count",
            "passing_mode_count",
            "geometry_pass",
            "model1_geometry_pass",
            "ifp_complete",
            "provenance_pass",
            "technical_pose_pass",
            "pose_population_pass",
        ):
            if current[field] != recorded.get(field):
                raise ValueError(f"smoke terminal evidence drift: {field}")
        current_jobs.append(current)

    contract_audit = verify_comparable_job_contracts(current_jobs)
    if terminal.get("contract_audit") != contract_audit:
        raise ValueError("smoke terminal comparable-search contract drift")
    technical_completion_path = (
        frame_run_root / "docking/smoke_technical_completion.json"
    )
    technical_completion = verify_technical_completion(
        technical_completion_path,
        mode="smoke",
        jobs=current_jobs,
        expected_run_identity=run_manifest["run_identity"],
        expected_environment_identity=environment["manifest_identity"],
        expected_config_sha256=config_sha256,
    )

    smoke_pass = all(
        job["geometry_pass"]
        and job["model1_geometry_pass"]
        and job["ifp_complete"]
        and job["provenance_pass"]
        and job["technical_pose_pass"]
        and job["pose_population_pass"]
        for job in current_jobs
    )
    expected_status = "pass" if smoke_pass else "fail_stop_before_full"
    if terminal["status"] != expected_status:
        raise ValueError("smoke terminal status 与逐 job gate 不一致")

    evidence = {
        "terminal_path": terminal_path,
        "terminal_sha256": sha256_file(terminal_path),
        "terminal_manifest_identity": terminal["manifest_identity"],
        "run_identity": run_manifest["run_identity"],
        "environment_manifest_identity": environment["manifest_identity"],
        "technical_completion_manifest_identity": technical_completion[
            "manifest_identity"
        ],
        "failed_jobs": [
            {
                "receptor": job["receptor"],
                "mutation": job["mutation"],
                "ligand": job["ligand"],
                "model1_geometry_pass": job["model1_geometry_pass"],
                "passing_mode_count": job["passing_mode_count"],
            }
            for job in current_jobs
            if not job["geometry_pass"]
        ],
    }
    return terminal, evidence


def write_terminal_state(
    frame_run_root: Path,
    *,
    terminal_status: str,
    terminal_path: Path,
    detail: dict[str, Any],
    observed_at: str,
) -> tuple[Path, Path]:
    """Create the append-only event authority and its initial snapshot."""
    if terminal_status not in TERMINAL_STATUSES:
        raise ValueError(f"unsupported smoke terminal status: {terminal_status}")
    state = (
        "TERMINAL_NORMAL"
        if terminal_status == "pass"
        else "TERMINAL_ABNORMAL"
    )
    events_path = frame_run_root / "run_state_events.tsv"
    snapshot_path = frame_run_root / "terminal_status.tsv"
    if events_path.exists() or snapshot_path.exists():
        raise FileExistsError("run state authority already exists; refusing overwrite")
    source = str(terminal_path.resolve())
    detail_text = json.dumps(detail, ensure_ascii=False, sort_keys=True)
    header = ["observed_at", "state", "source", "detail"]
    row = [observed_at, state, source, detail_text]
    for path in (events_path, snapshot_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            writer.writerow(header)
            writer.writerow(row)
    return events_path, snapshot_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_SOURCE_DIR / "config.yaml"))
    parser.add_argument("--frame-run-root", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    frame_run_root = Path(args.frame_run_root).resolve()
    terminal, evidence = verify_existing_smoke_terminal(
        config_path=config_path,
        frame_run_root=frame_run_root,
    )
    observed_at = datetime.now(timezone.utc).isoformat()
    detail = {
        "smoke_status": terminal["status"],
        "full_run_authorized": terminal["status"] == "pass",
        **{
            key: value
            for key, value in evidence.items()
            if key != "terminal_path"
        },
        "finalizer": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
    }
    events_path, snapshot_path = write_terminal_state(
        frame_run_root,
        terminal_status=terminal["status"],
        terminal_path=evidence["terminal_path"],
        detail=detail,
        observed_at=observed_at,
    )
    print(
        json.dumps(
            {
                "terminal_status": terminal["status"],
                "terminal_manifest_identity": terminal["manifest_identity"],
                "run_state_events": str(events_path),
                "terminal_snapshot": str(snapshot_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
