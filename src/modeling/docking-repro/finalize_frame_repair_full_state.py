"""Append a verified 328-job full-run terminal event to run-state authority."""

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
    sha256_file,
    verify_environment_manifest,
    verify_frame_run_manifest,
)
from frame_alignment import canonical_json_bytes  # noqa: E402
from utils import load_config  # noqa: E402


def verify_full_terminal(
    *,
    config_path: Path,
    frame_run_root: Path,
) -> dict[str, Any]:
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
    terminal_path = frame_run_root / "terminal/terminal_manifest.json"
    terminal = load_json(terminal_path)
    body = dict(terminal)
    expected_identity = body.pop("manifest_identity", None)
    actual_identity = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    if (
        terminal.get("schema") != "docking-frame-repair-terminal-matrix-v1"
        or terminal.get("status") != "complete"
        or not expected_identity
        or expected_identity != actual_identity
    ):
        raise ValueError("full terminal manifest schema/status/identity failure")
    scope = terminal.get("scope", {})
    if (
        scope.get("job_count") != 328
        or scope.get("mutant_count") != 162
        or scope.get("mutant_counts") != {"Gpr2": 46, "Gpr3": 116}
    ):
        raise ValueError("full terminal manifest matrix is incomplete")
    if (
        terminal.get("frame_run", {}).get("run_identity")
        != run_manifest["run_identity"]
        or terminal.get("environment", {}).get("manifest_identity")
        != environment["manifest_identity"]
        or terminal.get("configuration", {}).get("sha256") != config_sha256
        or Path(run_manifest["inputs"]["config"]["path"]).resolve()
        != config_path
        or run_manifest["inputs"]["config"]["sha256"] != config_sha256
    ):
        raise ValueError("full terminal 与 run/config/environment 不同源")
    for key in ("terminal_matrix", "terminal_jobs"):
        record = terminal["outputs"][key]
        path = Path(record["path"]).resolve()
        if not path.is_file() or sha256_file(path) != record["sha256"]:
            raise ValueError(f"full terminal linked output drift: {key}")
    return {
        "terminal_path": terminal_path,
        "terminal_sha256": sha256_file(terminal_path),
        "terminal_manifest_identity": terminal["manifest_identity"],
        "run_identity": run_manifest["run_identity"],
        "environment_manifest_identity": environment["manifest_identity"],
        "scope": scope,
    }


def append_full_terminal_state(
    frame_run_root: Path,
    *,
    evidence: dict[str, Any],
    observed_at: str,
) -> tuple[Path, Path]:
    events_path = frame_run_root / "run_state_events.tsv"
    snapshot_path = frame_run_root / "terminal_status.tsv"
    if not events_path.is_file() or not snapshot_path.is_file():
        raise FileNotFoundError(
            "full finalization requires the passing smoke run-state authority"
        )
    with events_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or rows[-1]["state"] != "TERMINAL_NORMAL":
        raise ValueError("full finalization requires a normal smoke terminal")
    source = str(evidence["terminal_path"].resolve())
    if any(row["source"] == source for row in rows):
        raise FileExistsError("full terminal event already exists")
    detail = json.dumps(
        {
            "full_status": "complete",
            **{
                key: value
                for key, value in evidence.items()
                if key != "terminal_path"
            },
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    row = [observed_at, "TERMINAL_NORMAL", source, detail]
    with events_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(row)

    temporary = snapshot_path.with_suffix(".tsv.tmp")
    if temporary.exists():
        raise FileExistsError(f"refusing existing snapshot temp file: {temporary}")
    with temporary.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["observed_at", "state", "source", "detail"])
        writer.writerow(row)
    temporary.replace(snapshot_path)
    return events_path, snapshot_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--frame-run-root", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame_run_root = Path(args.frame_run_root).resolve()
    evidence = verify_full_terminal(
        config_path=Path(args.config),
        frame_run_root=frame_run_root,
    )
    events, snapshot = append_full_terminal_state(
        frame_run_root,
        evidence=evidence,
        observed_at=datetime.now(timezone.utc).isoformat(),
    )
    print(
        json.dumps(
            {
                "status": "TERMINAL_NORMAL",
                "full_terminal_manifest_identity": evidence[
                    "terminal_manifest_identity"
                ],
                "run_state_events": str(events),
                "terminal_snapshot": str(snapshot),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
