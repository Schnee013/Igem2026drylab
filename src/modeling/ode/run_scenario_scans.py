"""Run the Phase-1 scenario-prior scan suite for the P0 ODE model.

The suite deliberately separates a reusable single-scenario solver from a
small, explicit set of engineering scenarios.  It does not fit parameters,
turn docking scores into affinities, or produce a detection-limit estimate.
"""

from __future__ import annotations

import argparse
import copy
import csv
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
import shutil
import sys
from typing import Any, Iterable, Mapping

import numpy as np

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.modeling.ode.minimal_solver import SimulationResult, solve_normalized_scenario
else:
    from .minimal_solver import SimulationResult, solve_normalized_scenario


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUITE_CONFIG = ROOT / "experiments/ode-model/configs/stage1_scenario_scan.json"
DEFAULT_OUTPUT_DIR = ROOT / "experiments/ode-model/results/stage1_scenario_scan"
REQUIRED_SUITE_FIELDS = {"suite_id", "evidence_status", "model_scope", "base_config", "scans"}


@dataclass(frozen=True)
class ScenarioRecord:
    """One generated scenario plus the metadata required to interpret it."""

    config: dict[str, Any]
    suite_id: str
    scan_id: str
    scenario_role: str
    axis_values: dict[str, float]


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
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _set_dotted_value(config: dict[str, Any], dotted_path: str, value: float) -> None:
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
    if isinstance(current[parts[-1]], (dict, list, str, bool)):
        raise ValueError(f"scan target must be numeric: {dotted_path!r}")
    current[parts[-1]] = float(value)


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


def _control_key(scan_id: str, config: Mapping[str, Any]) -> str:
    """Return a key for a matched no-ligand control with all other settings fixed."""

    numeric = _flatten_numeric_values(config)
    numeric.pop("parameter__input__ligand_normalized", None)
    return json.dumps({"scan_id": scan_id, "parameters": numeric}, sort_keys=True)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write an empty CSV: {path}")
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_scan_suite(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and validate the suite plus its Phase-0 base configuration."""

    suite = _load_json(path)
    missing = REQUIRED_SUITE_FIELDS.difference(suite)
    if missing:
        raise ValueError(f"scan suite is missing required fields: {', '.join(sorted(missing))}")
    if suite["evidence_status"] != "scenario_prior":
        raise ValueError("Stage-1 scan suite must be labelled evidence_status='scenario_prior'")
    if not isinstance(suite["scans"], list) or not suite["scans"]:
        raise ValueError("scan suite must contain at least one scan")

    base_config_path = (path.parent / suite["base_config"]).resolve()
    if not base_config_path.is_file():
        raise ValueError(f"base configuration does not exist: {base_config_path}")
    base_config = _load_json(base_config_path)

    scan_ids: set[str] = set()
    for scan in suite["scans"]:
        if not isinstance(scan, Mapping):
            raise ValueError("each scan must be an object")
        scan_id = scan.get("scan_id")
        if not isinstance(scan_id, str) or not scan_id:
            raise ValueError("each scan requires a non-empty scan_id")
        if scan_id in scan_ids:
            raise ValueError(f"duplicate scan_id: {scan_id}")
        scan_ids.add(scan_id)
        axes = scan.get("axes")
        if not isinstance(axes, Mapping) or not axes:
            raise ValueError(f"scan {scan_id!r} needs at least one axis")
        for dotted_path, values in axes.items():
            if not isinstance(dotted_path, str) or not isinstance(values, list) or not values:
                raise ValueError(f"scan {scan_id!r} has an invalid axis")
            trial = copy.deepcopy(base_config)
            _set_dotted_value(trial, dotted_path, float(values[0]))
        for dotted_path, value in scan.get("fixed_overrides", {}).items():
            trial = copy.deepcopy(base_config)
            _set_dotted_value(trial, dotted_path, float(value))
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
            for dotted_path, value in scan.get("fixed_overrides", {}).items():
                _set_dotted_value(config, dotted_path, float(value))
            axis_values = {path: float(value) for path, value in zip(axis_paths, values, strict=True)}
            for dotted_path, value in axis_values.items():
                _set_dotted_value(config, dotted_path, value)
            config["scenario_id"] = f"{suite['suite_id']}__{scan_id}__{index:03d}"
            config["evidence_status"] = "scenario_prior"
            records.append(
                ScenarioRecord(
                    config=config,
                    suite_id=str(suite["suite_id"]),
                    scan_id=scan_id,
                    scenario_role="ligand_input",
                    axis_values=axis_values,
                )
            )

            ligand = float(config["input"]["ligand_normalized"])
            if scan.get("include_no_ligand_control", False) and ligand != 0.0:
                control_config = copy.deepcopy(config)
                control_config["scenario_id"] = f"{config['scenario_id']}__no_ligand_control"
                control_config["input"]["ligand_normalized"] = 0.0
                records.append(
                    ScenarioRecord(
                        config=control_config,
                        suite_id=str(suite["suite_id"]),
                        scan_id=scan_id,
                        scenario_role="no_ligand_control",
                        axis_values=axis_values,
                    )
                )
    return records


def _time_to_half_final(result: SimulationResult) -> float:
    final_signal = float(result.color_signal[-1])
    if final_signal <= 0:
        return float("nan")
    first_index = int(np.flatnonzero(result.color_signal >= final_signal * 0.5)[0])
    return float(result.time_hours[first_index])


def run_scan_suite(suite_path: Path, output_dir: Path) -> dict[str, int]:
    """Run all scenarios and write self-describing time-courses and summaries."""

    suite, base_config = load_scan_suite(suite_path)
    records = build_scenarios(suite, base_config)
    outputs: list[tuple[ScenarioRecord, SimulationResult]] = []
    control_final_color: dict[str, float] = {}

    for record in records:
        result = solve_normalized_scenario(record.config)
        outputs.append((record, result))
        if float(record.config["input"]["ligand_normalized"]) == 0.0:
            control_final_color[_control_key(record.scan_id, record.config)] = float(result.color_signal[-1])

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
            "evidence_status": record.config["evidence_status"],
            "axis_values_json": json.dumps(record.axis_values, sort_keys=True),
            **parameter_values,
        }
        manifest_rows.append(common)
        for timecourse_row in result.as_rows(record.config["scenario_id"], record.config["evidence_status"]):
            timecourse_rows.append(
                {
                    "suite_id": record.suite_id,
                    "scan_id": record.scan_id,
                    "scenario_role": record.scenario_role,
                    **timecourse_row,
                }
            )

        final_color = float(result.color_signal[-1])
        baseline = control_final_color.get(_control_key(record.scan_id, record.config))
        delta = final_color - baseline if baseline is not None else float("nan")
        ratio = final_color / baseline if baseline is not None and baseline > 0 else float("nan")
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
    _write_csv(output_dir / "timecourses.csv", timecourse_rows)
    _write_csv(output_dir / "final_metrics.csv", metric_rows)
    shutil.copyfile(suite_path, output_dir / "scan_suite_config_snapshot.json")
    run_metadata = {
        "suite_id": suite["suite_id"],
        "evidence_status": "scenario_prior",
        "model_scope": suite["model_scope"],
        "base_config": suite["base_config"],
        "scenario_count": len(records),
        "timecourse_row_count": len(timecourse_rows),
        "result_boundary": (
            "These are normalized scenario simulations. They are not calibrated receptor "
            "affinities, experimental detection limits, or final engineering recommendations."
        ),
    }
    (output_dir / "run_metadata.json").write_text(
        json.dumps(run_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"scenario_count": len(records), "timecourse_row_count": len(timecourse_rows)}


def main() -> None:
    args = parse_args()
    summary = run_scan_suite(args.config, args.out_dir)
    print(
        "Wrote {scenario_count} scenario summaries and {timecourse_row_count} "
        "time-course rows to {output_dir}".format(output_dir=args.out_dir, **summary)
    )


if __name__ == "__main__":
    main()
