#!/usr/bin/env python3
"""Run AutoDock Vina once and preserve a compact reproducibility record."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def resolve_input(value: str, cwd: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else cwd / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vina-executable", default="vina")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-pdbqt", required=True, type=Path)
    parser.add_argument("--stdout-log", required=True, type=Path)
    parser.add_argument("--stderr-log", required=True, type=Path)
    parser.add_argument("--report-json", required=True, type=Path)
    parser.add_argument("--cpu", type=int, default=4)
    parser.add_argument("--spacing", type=float, default=0.1)
    parser.add_argument("--min-rmsd", type=float, default=1.0)
    parser.add_argument("--max-evals", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    executable = shutil.which(args.vina_executable)
    if executable is None:
        parser.error(f"Vina executable not found: {args.vina_executable}")
    if not args.config.is_file():
        parser.error(f"Config not found: {args.config}")
    outputs = [args.output_pdbqt, args.stdout_log, args.stderr_log, args.report_json]
    existing = [str(path) for path in outputs if path.exists()]
    if existing and not args.overwrite:
        parser.error("Refusing to overwrite: " + ", ".join(existing))
    if args.cpu < 1 or args.spacing <= 0 or args.min_rmsd <= 0 or args.max_evals < 0:
        parser.error("Invalid numeric run parameter")
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)

    cwd = Path.cwd()
    config_values = parse_config(args.config)
    input_records = {}
    for key in ("receptor", "ligand"):
        if key not in config_values:
            parser.error(f"Config is missing {key}")
        path = resolve_input(config_values[key], cwd).resolve()
        if not path.is_file():
            parser.error(f"Config {key} not found: {path}")
        input_records[key] = {"path": str(path), "sha256": sha256(path)}

    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{args.output_pdbqt.name}.", suffix=".tmp", dir=args.output_pdbqt.parent
    )
    os.close(descriptor)
    temp_output = Path(temp_name)
    temp_output.unlink()
    command = [
        executable,
        "--config",
        str(args.config),
        "--out",
        str(temp_output),
        "--cpu",
        str(args.cpu),
        "--spacing",
        str(args.spacing),
        "--min_rmsd",
        str(args.min_rmsd),
        "--max_evals",
        str(args.max_evals),
    ]
    version = subprocess.run(
        [executable, "--version"], text=True, capture_output=True, check=False
    )
    started = time.time()
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    elapsed = time.time() - started
    args.stdout_log.write_text(completed.stdout)
    args.stderr_log.write_text(completed.stderr)

    report = {
        "command": command,
        "cwd": str(cwd),
        "vina_version": (version.stdout or version.stderr).strip(),
        "return_code": completed.returncode,
        "elapsed_seconds": elapsed,
        "config": {
            "path": str(args.config.resolve()),
            "sha256": sha256(args.config),
            "values": config_values,
        },
        "inputs": input_records,
        "runtime_overrides": {
            "cpu": args.cpu,
            "spacing": args.spacing,
            "min_rmsd": args.min_rmsd,
            "max_evals": args.max_evals,
        },
    }
    if completed.returncode == 0 and temp_output.is_file():
        os.replace(temp_output, args.output_pdbqt)
        report["output"] = {
            "path": str(args.output_pdbqt.resolve()),
            "sha256": sha256(args.output_pdbqt),
        }
    else:
        temp_output.unlink(missing_ok=True)
        report["output"] = None
    args.report_json.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
