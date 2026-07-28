"""Run the Phase-1 scenario-prior scan suite for the P0 ODE model.

The suite deliberately separates a reusable single-scenario solver from a
small, explicit set of engineering scenarios.  It does not fit parameters,
turn docking scores into affinities, or produce a detection-limit estimate.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.metadata
import itertools
import json
from dataclasses import dataclass
import math
from numbers import Integral, Real
from pathlib import Path
import platform
import shutil
import sys
from typing import Any, Iterable, Mapping

import numpy as np

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.modeling.ode.minimal_solver import (
        SimulationResult,
        solve_normalized_scenario,
        validate_config,
    )
else:
    from .minimal_solver import SimulationResult, solve_normalized_scenario, validate_config


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUITE_CONFIG = ROOT / "experiments/ode-model/configs/stage1_scenario_scan.json"
DEFAULT_OUTPUT_DIR = ROOT / "experiments/ode-model/results/stage1_scenario_scan"
REQUIRED_SUITE_FIELDS = {"suite_id", "evidence_status", "model_scope", "base_config", "scans"}
OPTIONAL_SUITE_FIELDS = {"parameter_basis"}
REQUIRED_SCAN_FIELDS = {"scan_id", "purpose", "axes"}
OPTIONAL_SCAN_FIELDS = {"fixed_overrides", "include_no_ligand_control"}
PAYLOAD_MANIFEST_FIELDS = (
    "path",
    "role",
    "owner",
    "tracked_policy",
    "bytes",
    "sha256",
    "storage_location",
    "producer",
    "source",
    "consumer",
    "stage",
    "required_for",
    "recovery_pointer",
    "validator_result",
    "notes",
)


@dataclass(frozen=True)
class ScenarioRecord:
    """One generated scenario plus the metadata required to interpret it."""

    config: dict[str, Any]
    suite_id: str
    scan_id: str
    scenario_role: str
    requested_axis_values: dict[str, int | float]
    effective_axis_values: dict[str, int | float]
    control_for_scenario_id: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Phase-1 P0 ODE scenario-prior scan suite."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_SUITE_CONFIG,
        help="Readable Stage-1 scan-suite JSON configuration.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for compact CSV/JSON scan outputs.",
    )
    parser.add_argument(
        "--timecourses-out",
        type=Path,
        required=True,
        help="External path for the full time-course CSV payload.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def _validate_fields(
    mapping: Mapping[str, Any],
    label: str,
    required: set[str],
    optional: set[str],
) -> None:
    missing = required.difference(mapping)
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
    unknown = set(mapping).difference(required | optional)
    if unknown:
        raise ValueError(f"{label} has unknown fields: {', '.join(sorted(unknown))}")


def _require_non_empty_string(mapping: Mapping[str, Any], field: str, label: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.{field} must be a non-empty string")
    return value


def _finite_number(value: Any, label: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return int(value) if isinstance(value, Integral) else numeric


def _set_dotted_value(config: dict[str, Any], dotted_path: str, value: Any) -> None:
    """Set one existing numeric configuration field by a dotted path."""

    parts = dotted_path.split(".")
    if not dotted_path or any(not part for part in parts):
        raise ValueError(f"invalid dotted configuration path: {dotted_path!r}")
    current: dict[str, Any] = config
    for part in parts[:-1]:
        nested = current.get(part)
        if not isinstance(nested, dict):
            raise ValueError(f"configuration path does not exist: {dotted_path!r}")
        current = nested
    if parts[-1] not in current:
        raise ValueError(f"configuration path does not exist: {dotted_path!r}")
    existing = current[parts[-1]]
    if isinstance(existing, (dict, list, str, bool)) or not isinstance(existing, Real):
        raise ValueError(f"scan target must be numeric: {dotted_path!r}")
    numeric = _finite_number(value, f"value for {dotted_path!r}")
    if isinstance(existing, Integral):
        if not isinstance(numeric, int):
            raise ValueError(f"scan target requires an integer value: {dotted_path!r}")
        current[parts[-1]] = numeric
    else:
        current[parts[-1]] = float(numeric)


def _flatten_numeric_values(mapping: Mapping[str, Any], prefix: str = "") -> dict[str, float]:
    """Return numeric model settings as stable, CSV-safe parameter columns."""

    flattened: dict[str, float] = {}
    for key, value in mapping.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, Mapping):
            flattened.update(_flatten_numeric_values(value, path))
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            flattened[f"parameter__{path.replace('.', '__')}"] = float(value)
    return flattened


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write an empty CSV: {path}")
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "unavailable"


def _write_payload_manifest(
    path: Path,
    timecourse_path: Path,
    *,
    scenario_count: int,
    row_count: int,
) -> None:
    row = {
        "path": "timecourses.csv",
        "role": "full_timecourse_payload",
        "owner": "src/modeling/ode/run_scenario_scans.py",
        "tracked_policy": "external",
        "bytes": timecourse_path.stat().st_size,
        "sha256": _sha256(timecourse_path),
        "storage_location": str(timecourse_path.resolve()),
        "producer": "python -m src.modeling.ode.run_scenario_scans",
        "source": "scan_suite_config_snapshot.json + base_config_snapshot.json",
        "consumer": "Phase-1 ODE reproduction and downstream analysis",
        "stage": "phase1_scenario_scan",
        "required_for": "full numerical time-course authority",
        "recovery_pointer": (
            "Rerun the tracked config snapshots with an explicit external "
            "--timecourses-out path."
        ),
        "validator_result": "PASS",
        "notes": f"{scenario_count} scenarios; {row_count} data rows",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=PAYLOAD_MANIFEST_FIELDS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(row)


def load_scan_suite(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and validate the suite plus its Phase-0 base configuration."""

    suite = _load_json(path)
    _validate_fields(suite, "scan suite", REQUIRED_SUITE_FIELDS, OPTIONAL_SUITE_FIELDS)
    _require_non_empty_string(suite, "suite_id", "scan suite")
    _require_non_empty_string(suite, "model_scope", "scan suite")
    if suite["evidence_status"] != "scenario_prior":
        raise ValueError("Stage-1 scan suite must be labelled evidence_status='scenario_prior'")
    if not isinstance(suite["scans"], list) or not suite["scans"]:
        raise ValueError("scan suite must contain at least one scan")
    if "parameter_basis" in suite:
        parameter_basis = suite["parameter_basis"]
        if not isinstance(parameter_basis, Mapping) or not parameter_basis:
            raise ValueError("scan suite parameter_basis must be a non-empty object")
        for key, value in parameter_basis.items():
            if not isinstance(key, str) or not key or not isinstance(value, str) or not value:
                raise ValueError("scan suite parameter_basis keys and values must be non-empty strings")

    base_config_name = _require_non_empty_string(suite, "base_config", "scan suite")
    if Path(base_config_name).name != base_config_name:
        raise ValueError("scan suite base_config must name a colocated file")
    base_config_path = path.parent / base_config_name
    if not base_config_path.is_file():
        raise ValueError(f"base configuration does not exist: {base_config_path}")
    base_config = _load_json(base_config_path)
    validate_config(base_config)

    scan_ids: set[str] = set()
    for scan in suite["scans"]:
        if not isinstance(scan, Mapping):
            raise ValueError("each scan must be an object")
        _validate_fields(scan, "scan", REQUIRED_SCAN_FIELDS, OPTIONAL_SCAN_FIELDS)
        scan_id = _require_non_empty_string(scan, "scan_id", "scan")
        _require_non_empty_string(scan, "purpose", f"scan {scan_id!r}")
        if scan_id in scan_ids:
            raise ValueError(f"duplicate scan_id: {scan_id}")
        scan_ids.add(scan_id)
        axes = scan.get("axes")
        if not isinstance(axes, Mapping) or not axes:
            raise ValueError(f"scan {scan_id!r} needs at least one axis")
        for dotted_path, values in axes.items():
            if not isinstance(dotted_path, str) or not isinstance(values, list) or not values:
                raise ValueError(f"scan {scan_id!r} has an invalid axis")
            for value in values:
                trial = copy.deepcopy(base_config)
                _set_dotted_value(trial, dotted_path, value)
        fixed_overrides = scan.get("fixed_overrides", {})
        if not isinstance(fixed_overrides, Mapping):
            raise ValueError(f"scan {scan_id!r} fixed_overrides must be an object")
        if set(axes).intersection(fixed_overrides):
            raise ValueError(f"scan {scan_id!r} cannot fix and scan the same field")
        for dotted_path, value in fixed_overrides.items():
            if not isinstance(dotted_path, str):
                raise ValueError(f"scan {scan_id!r} has an invalid fixed override")
            trial = copy.deepcopy(base_config)
            _set_dotted_value(trial, dotted_path, value)
        if not isinstance(scan.get("include_no_ligand_control", False), bool):
            raise ValueError(f"scan {scan_id!r} include_no_ligand_control must be boolean")
    return suite, base_config


def build_scenarios(suite: Mapping[str, Any], base_config: Mapping[str, Any]) -> list[ScenarioRecord]:
    """Expand a small named scan suite into solver-ready scenario configurations."""

    records: list[ScenarioRecord] = []
    for scan in suite["scans"]:
        scan_id = str(scan["scan_id"])
        axes = dict(scan["axes"])
        axis_paths = list(axes)
        for index, values in enumerate(itertools.product(*(axes[path] for path in axis_paths)), start=1):
            config = copy.deepcopy(base_config)
            requested_axis_values: dict[str, int | float] = {}
            for dotted_path, value in scan.get("fixed_overrides", {}).items():
                _set_dotted_value(config, dotted_path, value)
                requested_axis_values[dotted_path] = _finite_number(
                    value, f"value for {dotted_path!r}"
                )
            for dotted_path, value in zip(axis_paths, values, strict=True):
                _set_dotted_value(config, dotted_path, value)
                requested_axis_values[dotted_path] = _finite_number(
                    value, f"value for {dotted_path!r}"
                )
            config["scenario_id"] = f"{suite['suite_id']}__{scan_id}__{index:03d}"
            config["evidence_status"] = "scenario_prior"
            validate_config(config)
            effective_axis_values = dict(requested_axis_values)
            effective_axis_values["input.ligand_normalized"] = float(
                config["input"]["ligand_normalized"]
            )
            records.append(
                ScenarioRecord(
                    config=config,
                    suite_id=str(suite["suite_id"]),
                    scan_id=scan_id,
                    scenario_role="ligand",
                    requested_axis_values=requested_axis_values,
                    effective_axis_values=effective_axis_values,
                    control_for_scenario_id=None,
                )
            )

            ligand = float(config["input"]["ligand_normalized"])
            if scan.get("include_no_ligand_control", False) and ligand != 0.0:
                control_config = copy.deepcopy(config)
                control_config["scenario_id"] = f"{config['scenario_id']}__no_ligand_control"
                control_config["input"]["ligand_normalized"] = 0.0
                validate_config(control_config)
                control_effective_axis_values = dict(requested_axis_values)
                control_effective_axis_values["input.ligand_normalized"] = 0.0
                records.append(
                    ScenarioRecord(
                        config=control_config,
                        suite_id=str(suite["suite_id"]),
                        scan_id=scan_id,
                        scenario_role="no_ligand_control",
                        requested_axis_values=dict(requested_axis_values),
                        effective_axis_values=control_effective_axis_values,
                        control_for_scenario_id=config["scenario_id"],
                    )
                )
    scenario_ids = [str(record.config["scenario_id"]) for record in records]
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("generated scenario IDs must be unique")
    return records


def _time_to_half_final(result: SimulationResult) -> float:
    final_signal = float(result.color_signal[-1])
    if final_signal <= 0:
        return float("nan")
    first_index = int(np.flatnonzero(result.color_signal >= final_signal * 0.5)[0])
    return float(result.time_hours[first_index])


def run_scan_suite(
    suite_path: Path,
    output_dir: Path,
    *,
    timecourse_output_path: Path,
) -> dict[str, int]:
    """Run all scenarios and write self-describing time-courses and summaries."""

    suite_path = suite_path.resolve()
    output_dir = output_dir.resolve()
    timecourse_output_path = timecourse_output_path.resolve()
    try:
        timecourse_output_path.relative_to(output_dir)
    except ValueError:
        pass
    else:
        raise ValueError("full time-course payload must be outside the compact result directory")

    suite, base_config = load_scan_suite(suite_path)
    base_config_path = suite_path.parent / str(suite["base_config"])
    records = build_scenarios(suite, base_config)
    outputs: list[tuple[ScenarioRecord, SimulationResult]] = []

    for record in records:
        result = solve_normalized_scenario(record.config)
        outputs.append((record, result))

    control_final_color = {
        str(record.control_for_scenario_id): float(result.color_signal[-1])
        for record, result in outputs
        if record.control_for_scenario_id is not None
    }
    if len(control_final_color) != sum(
        record.scenario_role == "no_ligand_control" for record in records
    ):
        raise ValueError("no-ligand controls must pair one-to-one with ligand scenarios")

    manifest_rows: list[dict[str, Any]] = []
    timecourse_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    for record, result in outputs:
        parameter_values = _flatten_numeric_values(record.config)
        common = {
            "suite_id": record.suite_id,
            "scan_id": record.scan_id,
            "scenario_id": record.config["scenario_id"],
            "scenario_role": record.scenario_role,
            "control_for_scenario_id": record.control_for_scenario_id or "",
            "evidence_status": record.config["evidence_status"],
            "requested_axis_values_json": json.dumps(
                record.requested_axis_values, sort_keys=True
            ),
            "effective_axis_values_json": json.dumps(
                record.effective_axis_values, sort_keys=True
            ),
            **parameter_values,
        }
        manifest_rows.append(common)
        for timecourse_row in result.as_rows(record.config["scenario_id"], record.config["evidence_status"]):
            timecourse_rows.append(
                {
                    "suite_id": record.suite_id,
                    "scan_id": record.scan_id,
                    "scenario_role": record.scenario_role,
                    "control_for_scenario_id": record.control_for_scenario_id or "",
                    **timecourse_row,
                }
            )

        final_color = float(result.color_signal[-1])
        if record.scenario_role == "no_ligand_control":
            baseline = final_color
        else:
            baseline = control_final_color.get(str(record.config["scenario_id"]))
        delta = final_color - baseline if baseline is not None else 0.0
        ratio = final_color / baseline if baseline is not None and baseline > 0 else 1.0
        metric_rows.append(
            {
                **common,
                "final_color_signal_arbitrary_units": final_color,
                "area_under_color_curve_arbitrary_units_hours": float(
                    np.trapezoid(result.color_signal, result.time_hours)
                ),
                "time_to_half_final_color_hours": _time_to_half_final(result),
                "matched_no_ligand_final_color_arbitrary_units": baseline,
                "final_color_delta_vs_no_ligand_arbitrary_units": delta,
                "final_color_ratio_vs_no_ligand": ratio,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "scenario_manifest.csv", manifest_rows)
    _write_csv(timecourse_output_path, timecourse_rows)
    _write_csv(output_dir / "final_metrics.csv", metric_rows)
    base_snapshot_path = output_dir / "base_config_snapshot.json"
    shutil.copyfile(base_config_path, base_snapshot_path)
    suite_snapshot = copy.deepcopy(suite)
    suite_snapshot["base_config"] = base_snapshot_path.name
    suite_snapshot_path = output_dir / "scan_suite_config_snapshot.json"
    suite_snapshot_path.write_text(
        json.dumps(suite_snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    control_count = sum(record.scenario_role == "no_ligand_control" for record in records)
    _write_payload_manifest(
        output_dir / "payload_manifest.tsv",
        timecourse_output_path,
        scenario_count=len(records),
        row_count=len(timecourse_rows),
    )
    run_metadata = {
        "schema_version": "ode_phase1_run_metadata_v1",
        "suite_id": suite["suite_id"],
        "evidence_status": "scenario_prior",
        "model_scope": suite["model_scope"],
        "scenario_count": len(records),
        "control_count": control_count,
        "timecourse_row_count": len(timecourse_rows),
        "source_config_provenance": {
            "suite_path": str(suite_path),
            "suite_sha256": _sha256(suite_path),
            "base_config_path": str(base_config_path),
            "base_config_sha256": _sha256(base_config_path),
        },
        "snapshot_config": {
            "suite_file": suite_snapshot_path.name,
            "suite_sha256": _sha256(suite_snapshot_path),
            "base_config_file": base_snapshot_path.name,
            "base_config_sha256": _sha256(base_snapshot_path),
        },
        "runner_identity": {
            "runner_file": "src/modeling/ode/run_scenario_scans.py",
            "runner_sha256": _sha256(Path(__file__)),
            "solver_file": "src/modeling/ode/minimal_solver.py",
            "solver_sha256": _sha256(Path(__file__).with_name("minimal_solver.py")),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": _package_version("scipy"),
            "matplotlib": _package_version("matplotlib"),
        },
        "generation_command": (
            "python -m src.modeling.ode.run_scenario_scans "
            f"--config {suite_path} --out-dir {output_dir} "
            f"--timecourses-out {timecourse_output_path}"
        ),
        "external_timecourse_payload": {
            "path": str(timecourse_output_path),
            "bytes": timecourse_output_path.stat().st_size,
            "sha256": _sha256(timecourse_output_path),
        },
        "result_boundary": (
            "These are normalized scenario simulations. They are not calibrated receptor "
            "affinities, experimental detection limits, or final engineering recommendations."
        ),
    }
    (output_dir / "run_metadata.json").write_text(
        json.dumps(run_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "scenario_count": len(records),
        "timecourse_row_count": len(timecourse_rows),
        "control_count": control_count,
    }


def main() -> None:
    args = parse_args()
    summary = run_scan_suite(
        args.config,
        args.out_dir,
        timecourse_output_path=args.timecourses_out,
    )
    print(
        "Wrote {scenario_count} scenario summaries and {timecourse_row_count} "
        "time-course rows to {output_dir}".format(output_dir=args.out_dir, **summary)
    )


if __name__ == "__main__":
    main()
