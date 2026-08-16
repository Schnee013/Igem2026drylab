"""Run deterministic Morris screening for the normalized Phase-2B ODE model.

The implementation uses one-at-a-time trajectories in a normalized unit cube,
then maps each coordinate through the uniform or log-uniform range registered
by the Phase-2A contract.  It deliberately reports elementary effects by
metric, ligand context, and copy-number stratum instead of pooling conditions.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import numpy as np

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.modeling.ode.minimal_solver import SimulationResult, solve_normalized_scenario
else:
    from .minimal_solver import SimulationResult, solve_normalized_scenario


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "experiments/ode-model/configs/phase2b_morris_screening.json"
DEFAULT_OUTPUT_DIR = ROOT / "experiments/ode-model/results/phase2b_morris_screening"
REQUIRED_ANALYSIS_FIELDS = {
    "analysis_id",
    "evidence_status",
    "analysis_contract",
    "num_levels",
    "trajectory_count",
    "random_seed",
    "metric_ids",
    "result_boundary",
}
CONTROL_METRICS = {
    "matched_control_color_8h",
    "delta_color_8h",
    "ratio_color_8h",
}


@dataclass(frozen=True)
class MorrisTrajectory:
    """One normalized OAT trajectory and its parameter-change order."""

    trajectory_id: int
    points: np.ndarray
    parameter_order: tuple[int, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Phase-2B Morris screening for the normalized ODE."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--parameter-id", action="append")
    parser.add_argument("--ligand-context", action="append")
    parser.add_argument("--copy-number", action="append", type=int)
    parser.add_argument("--metric-id", action="append")
    parser.add_argument("--trajectory-count", type=int)
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Morris export cannot be empty: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _get_dotted(mapping: Mapping[str, Any], dotted_path: str) -> Any:
    value: Any = mapping
    for part in dotted_path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            raise ValueError(f"configuration path does not exist: {dotted_path!r}")
        value = value[part]
    return value


def _set_dotted(mapping: dict[str, Any], dotted_path: str, value: float) -> None:
    parts = dotted_path.split(".")
    current = mapping
    for part in parts[:-1]:
        nested = current.get(part)
        if not isinstance(nested, dict):
            raise ValueError(f"configuration path does not exist: {dotted_path!r}")
        current = nested
    if parts[-1] not in current:
        raise ValueError(f"configuration path does not exist: {dotted_path!r}")
    current[parts[-1]] = float(value)


def _positive_integer(value: Any, label: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def _unique_selection(
    requested: Sequence[Any] | None,
    available: Sequence[Any],
    label: str,
) -> list[Any]:
    if requested is None:
        return list(available)
    selected = list(requested)
    if not selected or len(selected) != len(set(selected)):
        raise ValueError(f"{label} selection must be non-empty and unique")
    unknown = set(selected).difference(available)
    if unknown:
        raise ValueError(f"unknown {label}: {', '.join(map(str, sorted(unknown)))}")
    return selected


def load_morris_inputs(
    config_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, str]],
    list[tuple[str, str, float]],
    list[int],
    list[dict[str, str]],
    Path,
    Path,
    Path,
]:
    """Load and cross-check the Morris config against the Phase-2A contract."""

    config_path = config_path.resolve()
    analysis = _load_json(config_path)
    missing = REQUIRED_ANALYSIS_FIELDS.difference(analysis)
    unknown = set(analysis).difference(REQUIRED_ANALYSIS_FIELDS)
    if missing:
        raise ValueError(f"Morris config is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"Morris config has unknown fields: {', '.join(sorted(unknown))}")
    if analysis["evidence_status"] != "scenario_prior":
        raise ValueError("Morris screening accepts only evidence_status='scenario_prior'")
    for field in ("analysis_id", "analysis_contract", "result_boundary"):
        if not isinstance(analysis[field], str) or not analysis[field].strip():
            raise ValueError(f"Morris config field {field!r} must be a non-empty string")

    levels = _positive_integer(analysis["num_levels"], "num_levels", minimum=4)
    if levels % 2:
        raise ValueError("num_levels must be even")
    _positive_integer(analysis["trajectory_count"], "trajectory_count", minimum=2)
    if isinstance(analysis["random_seed"], bool) or not isinstance(
        analysis["random_seed"], int
    ):
        raise ValueError("random_seed must be an integer")

    metric_ids = analysis["metric_ids"]
    if (
        not isinstance(metric_ids, list)
        or not metric_ids
        or any(not isinstance(metric_id, str) or not metric_id for metric_id in metric_ids)
        or len(metric_ids) != len(set(metric_ids))
    ):
        raise ValueError("metric_ids must be a non-empty list of unique strings")

    contract_path = (ROOT / analysis["analysis_contract"]).resolve()
    contract = _load_json(contract_path)
    if contract.get("status") != "active_contract":
        raise ValueError("Phase-2A analysis contract must be active")
    stages = [row["stage"] for row in contract["analysis_sequence"]]
    if "morris_screening" not in stages:
        raise ValueError("Phase-2A analysis sequence must include morris_screening")

    baseline_path = (ROOT / contract["source_baseline"]["baseline_config"]).resolve()
    baseline = _load_json(baseline_path)
    parameter_path = (ROOT / contract["contract_files"]["parameter_space"]).resolve()
    parameter_rows = [
        row
        for row in _read_csv(parameter_path)
        if row["analysis_role"] == "uncertain_continuous"
    ]
    if len(parameter_rows) != int(contract["parameter_counts"]["continuous_uncertainty_fields"]):
        raise ValueError("continuous parameter count does not match the Phase-2A contract")
    for row in parameter_rows:
        distribution = row["sampling_distribution"]
        if distribution not in {"uniform", "loguniform"}:
            raise ValueError(f"unsupported sampling distribution: {distribution!r}")
        lower = float(row["lower_bound"])
        upper = float(row["upper_bound"])
        if not math.isfinite(lower) or not math.isfinite(upper) or lower >= upper:
            raise ValueError(f"invalid parameter bounds: {row['parameter_id']}")
        if distribution == "loguniform" and lower <= 0:
            raise ValueError(f"loguniform lower bound must be positive: {row['parameter_id']}")
        baseline_value = float(_get_dotted(baseline, row["config_path"]))
        if not lower <= baseline_value <= upper:
            raise ValueError(f"parameter baseline is outside bounds: {row['parameter_id']}")

    output_path = (ROOT / contract["contract_files"]["output_metrics"]).resolve()
    metric_rows = [
        row
        for row in _read_csv(output_path)
        if row["status"] in {"active", "active_with_denominator_guard"}
    ]
    active_metric_ids = {row["metric_id"] for row in metric_rows}
    unknown_metrics = set(metric_ids).difference(active_metric_ids)
    if unknown_metrics:
        raise ValueError(
            f"Morris config references inactive or unknown metrics: {', '.join(sorted(unknown_metrics))}"
        )

    design = contract["design_contexts"]
    contexts: list[tuple[str, str, float]] = []
    for context_set, context_ids in design["ligand_context_sets"].items():
        for context_id in context_ids:
            contexts.append(
                (context_set, context_id, float(design["ligand_normalized"][context_id]))
            )
    copy_numbers = [int(value) for value in design["copy_number_strata"]]
    return (
        analysis,
        contract,
        baseline,
        parameter_rows,
        contexts,
        copy_numbers,
        metric_rows,
        contract_path,
        parameter_path,
        output_path,
    )


def morris_delta(num_levels: int) -> float:
    """Return the standard Morris normalized step for an even level count."""

    levels = _positive_integer(num_levels, "num_levels", minimum=4)
    if levels % 2:
        raise ValueError("num_levels must be even")
    return levels / (2.0 * (levels - 1.0))


def build_morris_trajectories(
    parameter_count: int,
    *,
    num_levels: int,
    trajectory_count: int,
    random_seed: int,
) -> list[MorrisTrajectory]:
    """Build reproducible OAT trajectories inside the normalized unit cube."""

    parameter_count = _positive_integer(parameter_count, "parameter_count")
    trajectory_count = _positive_integer(
        trajectory_count, "trajectory_count", minimum=2
    )
    delta = morris_delta(num_levels)
    grid = np.linspace(0.0, 1.0, num_levels)
    rng = np.random.default_rng(random_seed)
    trajectories: list[MorrisTrajectory] = []

    for trajectory_id in range(1, trajectory_count + 1):
        directions = rng.choice(np.array([-1.0, 1.0]), size=parameter_count)
        start = np.empty(parameter_count, dtype=float)
        for index, direction in enumerate(directions):
            allowed = grid[grid <= 1.0 - delta + 1e-12]
            if direction < 0:
                allowed = grid[grid >= delta - 1e-12]
            start[index] = float(rng.choice(allowed))
        order = tuple(int(index) for index in rng.permutation(parameter_count))
        points = [start.copy()]
        current = start.copy()
        for parameter_index in order:
            current = current.copy()
            current[parameter_index] += directions[parameter_index] * delta
            if current[parameter_index] < -1e-12 or current[parameter_index] > 1.0 + 1e-12:
                raise RuntimeError("generated Morris point is outside the unit cube")
            current[parameter_index] = min(max(current[parameter_index], 0.0), 1.0)
            points.append(current)
        trajectories.append(
            MorrisTrajectory(
                trajectory_id=trajectory_id,
                points=np.asarray(points, dtype=float),
                parameter_order=order,
            )
        )
    return trajectories


def normalized_to_physical(row: Mapping[str, str], coordinate: float) -> float:
    """Map one unit-cube coordinate through its registered distribution."""

    if not math.isfinite(coordinate) or not 0.0 <= coordinate <= 1.0:
        raise ValueError("normalized coordinate must lie in [0, 1]")
    lower = float(row["lower_bound"])
    upper = float(row["upper_bound"])
    if row["sampling_distribution"] == "uniform":
        return lower + coordinate * (upper - lower)
    if row["sampling_distribution"] == "loguniform":
        return math.exp(math.log(lower) + coordinate * (math.log(upper) - math.log(lower)))
    raise ValueError(f"unsupported sampling distribution: {row['sampling_distribution']!r}")


def _value_at_time(time: np.ndarray, values: np.ndarray, target: float) -> float:
    if target < float(time[0]) or target > float(time[-1]):
        raise ValueError(f"metric time {target} h is outside the simulated interval")
    return float(np.interp(target, time, values))


def _trapezoid(values: np.ndarray, time: np.ndarray) -> float:
    integrate = getattr(np, "trapezoid", None)
    if integrate is None:
        integrate = np.trapz
    return float(integrate(values, time))


def _time_to_half_final(result: SimulationResult) -> float:
    final_signal = float(result.color_signal[-1])
    if final_signal <= 0:
        return float("nan")
    indices = np.flatnonzero(result.color_signal >= final_signal * 0.5)
    return float(result.time_hours[int(indices[0])]) if len(indices) else float("nan")


def _direct_metrics(result: SimulationResult) -> dict[str, float]:
    time = np.asarray(result.time_hours, dtype=float)
    color = np.asarray(result.color_signal, dtype=float)
    return {
        "color_2h": _value_at_time(time, color, 2.0),
        "color_4h": _value_at_time(time, color, 4.0),
        "color_8h": _value_at_time(time, color, 8.0),
        "color_auc_0_8h": _trapezoid(color, time),
        "time_to_half_final_color": _time_to_half_final(result),
        "g_on_1h": _value_at_time(time, np.asarray(result.g_on, dtype=float), 1.0),
        "mapk_active_1h": _value_at_time(
            time, np.asarray(result.mapk_active, dtype=float), 1.0
        ),
        "stf_activity_1h": _value_at_time(
            time, np.asarray(result.stf_activity, dtype=float), 1.0
        ),
        "gal_product_rate_1h": _value_at_time(
            time, np.asarray(result.gal_product_rate, dtype=float), 1.0
        ),
    }


def _evaluate_metrics(
    config: dict[str, Any],
    metric_ids: Sequence[str],
    ratio_policy: Mapping[str, Any],
    matched_control_cache: dict[str, float] | None = None,
) -> tuple[dict[str, float], int, bool]:
    result = solve_normalized_scenario(config)
    solve_count = 1
    control_cache_hit = False
    metrics = _direct_metrics(result)
    requested_control = bool(set(metric_ids).intersection(CONTROL_METRICS))
    ligand = float(config["input"]["ligand_normalized"])
    if requested_control and ligand > 0:
        control_config = copy.deepcopy(config)
        control_config["scenario_id"] = f"{config['scenario_id']}__matched_no_ligand"
        control_config["input"]["ligand_normalized"] = 0.0
        control_identity = json.dumps(
            {
                key: control_config[key]
                for key in (
                    "time",
                    "receptor",
                    "g_protein",
                    "mapk",
                    "transcription",
                    "gal_output",
                    "color",
                )
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        if matched_control_cache is not None and control_identity in matched_control_cache:
            control_final = matched_control_cache[control_identity]
            control_cache_hit = True
        else:
            control_final = float(solve_normalized_scenario(control_config).color_signal[-1])
            solve_count += 1
            if matched_control_cache is not None:
                matched_control_cache[control_identity] = control_final
        final = metrics["color_8h"]
        metrics["matched_control_color_8h"] = control_final
        metrics["delta_color_8h"] = final - control_final
        minimum = float(ratio_policy["denominator_min_positive_value"])
        metrics["ratio_color_8h"] = (
            final / control_final if control_final > minimum else float("nan")
        )
    selected = {
        metric_id: metrics[metric_id] for metric_id in metric_ids if metric_id in metrics
    }
    return selected, solve_count, control_cache_hit


def _configured_point(
    baseline: dict[str, Any],
    parameters: Sequence[Mapping[str, str]],
    point: np.ndarray,
    *,
    ligand: float,
    copy_number: int,
    scenario_id: str,
) -> dict[str, Any]:
    config = copy.deepcopy(baseline)
    config["scenario_id"] = scenario_id
    config["evidence_status"] = "scenario_prior"
    config["input"]["ligand_normalized"] = ligand
    config["gal_output"]["copy_number"] = copy_number
    for row, coordinate in zip(parameters, point, strict=True):
        _set_dotted(config, row["config_path"], normalized_to_physical(row, float(coordinate)))
    return config


def run_morris_screening(
    config_path: Path,
    output_dir: Path,
    *,
    parameter_ids: Sequence[str] | None = None,
    ligand_context_ids: Sequence[str] | None = None,
    copy_numbers: Sequence[int] | None = None,
    metric_ids: Sequence[str] | None = None,
    trajectory_count: int | None = None,
) -> dict[str, Any]:
    """Run a selected Morris slice and write effects, summaries, and metadata."""

    (
        analysis,
        contract,
        baseline,
        all_parameters,
        all_contexts,
        all_copy_numbers,
        all_metric_rows,
        contract_path,
        parameter_path,
        output_metric_path,
    ) = load_morris_inputs(config_path)

    selected_parameter_ids = _unique_selection(
        parameter_ids,
        [row["parameter_id"] for row in all_parameters],
        "parameter_id",
    )
    parameter_lookup = {row["parameter_id"]: row for row in all_parameters}
    parameters = [parameter_lookup[parameter_id] for parameter_id in selected_parameter_ids]
    selected_context_ids = _unique_selection(
        ligand_context_ids,
        [context_id for _, context_id, _ in all_contexts],
        "ligand_context",
    )
    context_lookup = {row[1]: row for row in all_contexts}
    contexts = [context_lookup[context_id] for context_id in selected_context_ids]
    selected_copy_numbers = _unique_selection(
        copy_numbers, all_copy_numbers, "copy_number"
    )
    configured_metric_ids = list(analysis["metric_ids"])
    selected_metric_ids = _unique_selection(
        metric_ids, configured_metric_ids, "metric_id"
    )
    metric_lookup = {row["metric_id"]: row for row in all_metric_rows}
    selected_metric_rows = [metric_lookup[metric_id] for metric_id in selected_metric_ids]
    trajectories_requested = (
        analysis["trajectory_count"] if trajectory_count is None else trajectory_count
    )
    trajectories_requested = _positive_integer(
        trajectories_requested, "trajectory_count", minimum=2
    )
    delta = morris_delta(int(analysis["num_levels"]))
    trajectories = build_morris_trajectories(
        len(parameters),
        num_levels=int(analysis["num_levels"]),
        trajectory_count=trajectories_requested,
        random_seed=int(analysis["random_seed"]),
    )
    ratio_policy = contract["metric_guard_policies"]["ratio_color_8h"]

    effect_rows: list[dict[str, Any]] = []
    solve_count = 0
    matched_control_cache: dict[str, float] = {}
    matched_control_cache_hit_count = 0
    for context_set, context_id, ligand in contexts:
        applicable_metric_ids = [
            row["metric_id"]
            for row in selected_metric_rows
            if ligand > 0 or row["metric_id"] not in CONTROL_METRICS
        ]
        if not applicable_metric_ids:
            continue
        for copy_number in selected_copy_numbers:
            for trajectory in trajectories:
                point_metrics: list[dict[str, float]] = []
                for point_index, point in enumerate(trajectory.points):
                    scenario_id = (
                        f"{analysis['analysis_id']}__{context_id}__N{copy_number}__"
                        f"T{trajectory.trajectory_id:03d}__P{point_index:02d}"
                    )
                    configured = _configured_point(
                        baseline,
                        parameters,
                        point,
                        ligand=ligand,
                        copy_number=copy_number,
                        scenario_id=scenario_id,
                    )
                    metrics, point_solve_count, control_cache_hit = _evaluate_metrics(
                        configured,
                        applicable_metric_ids,
                        ratio_policy,
                        matched_control_cache,
                    )
                    point_metrics.append(metrics)
                    solve_count += point_solve_count
                    matched_control_cache_hit_count += int(control_cache_hit)

                for step_index, parameter_index in enumerate(trajectory.parameter_order):
                    row = parameters[parameter_index]
                    before_coordinate = float(trajectory.points[step_index, parameter_index])
                    after_coordinate = float(
                        trajectory.points[step_index + 1, parameter_index]
                    )
                    signed_step = after_coordinate - before_coordinate
                    if not math.isclose(abs(signed_step), delta, rel_tol=0.0, abs_tol=1e-12):
                        raise RuntimeError("Morris trajectory step does not match delta")
                    before_value = normalized_to_physical(row, before_coordinate)
                    after_value = normalized_to_physical(row, after_coordinate)
                    for metric_id in applicable_metric_ids:
                        output_before = float(point_metrics[step_index][metric_id])
                        output_after = float(point_metrics[step_index + 1][metric_id])
                        valid = math.isfinite(output_before) and math.isfinite(output_after)
                        effect_rows.append(
                            {
                                "analysis_id": analysis["analysis_id"],
                                "evidence_status": analysis["evidence_status"],
                                "context_set": context_set,
                                "ligand_context": context_id,
                                "ligand_normalized": ligand,
                                "copy_number": copy_number,
                                "metric_id": metric_id,
                                "trajectory_id": trajectory.trajectory_id,
                                "step_index": step_index + 1,
                                "parameter_id": row["parameter_id"],
                                "module": row["module"],
                                "config_path": row["config_path"],
                                "sampling_distribution": row["sampling_distribution"],
                                "normalized_before": before_coordinate,
                                "normalized_after": after_coordinate,
                                "normalized_step": signed_step,
                                "physical_before": before_value,
                                "physical_after": after_value,
                                "output_before": output_before,
                                "output_after": output_after,
                                "elementary_effect": (
                                    (output_after - output_before) / signed_step if valid else ""
                                ),
                                "elementary_effect_valid": "true" if valid else "false",
                            }
                        )

    summary_rows: list[dict[str, Any]] = []
    groups: dict[tuple[str, str, float, int, str, str], list[float]] = {}
    for row in effect_rows:
        if row["elementary_effect_valid"] != "true":
            continue
        key = (
            str(row["context_set"]),
            str(row["ligand_context"]),
            float(row["ligand_normalized"]),
            int(row["copy_number"]),
            str(row["metric_id"]),
            str(row["parameter_id"]),
        )
        groups.setdefault(key, []).append(float(row["elementary_effect"]))

    for key, effects in groups.items():
        context_set, context_id, ligand, copy_number, metric_id, parameter_id = key
        parameter = parameter_lookup[parameter_id]
        values = np.asarray(effects, dtype=float)
        summary_rows.append(
            {
                "analysis_id": analysis["analysis_id"],
                "evidence_status": analysis["evidence_status"],
                "context_set": context_set,
                "ligand_context": context_id,
                "ligand_normalized": ligand,
                "copy_number": copy_number,
                "metric_id": metric_id,
                "metric_role": metric_lookup[metric_id]["role"],
                "parameter_id": parameter_id,
                "module": parameter["module"],
                "sampling_distribution": parameter["sampling_distribution"],
                "lower_bound": float(parameter["lower_bound"]),
                "upper_bound": float(parameter["upper_bound"]),
                "num_levels": int(analysis["num_levels"]),
                "normalized_delta": delta,
                "trajectories_requested": trajectories_requested,
                "valid_effect_count": len(effects),
                "mu": float(np.mean(values)),
                "mu_star": float(np.mean(np.abs(values))),
                "sigma": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
            }
        )

    summary_rows.sort(
        key=lambda row: (
            selected_context_ids.index(str(row["ligand_context"])),
            selected_copy_numbers.index(int(row["copy_number"])),
            selected_metric_ids.index(str(row["metric_id"])),
            -float(row["mu_star"]),
            selected_parameter_ids.index(str(row["parameter_id"])),
        )
    )
    output_dir = output_dir.resolve()
    effects_path = output_dir / "elementary_effects.csv"
    summary_path = output_dir / "morris_summary.csv"
    _write_csv(effects_path, effect_rows)
    _write_csv(summary_path, summary_rows)
    metadata = {
        "schema_version": "ode_phase2b_morris_v1",
        "analysis_id": analysis["analysis_id"],
        "evidence_status": analysis["evidence_status"],
        "parameter_ids": selected_parameter_ids,
        "ligand_context_ids": selected_context_ids,
        "copy_numbers": selected_copy_numbers,
        "metric_ids": selected_metric_ids,
        "num_levels": int(analysis["num_levels"]),
        "normalized_delta": delta,
        "trajectory_count": trajectories_requested,
        "random_seed": int(analysis["random_seed"]),
        "model_solve_count": solve_count,
        "matched_control_unique_solve_count": len(matched_control_cache),
        "matched_control_cache_hit_count": matched_control_cache_hit_count,
        "elementary_effect_row_count": len(effect_rows),
        "summary_row_count": len(summary_rows),
        "source_provenance": {
            "analysis_config": str(Path(config_path).resolve()),
            "analysis_config_sha256": _sha256(Path(config_path).resolve()),
            "phase2a_contract": str(contract_path),
            "phase2a_contract_sha256": _sha256(contract_path),
            "parameter_space": str(parameter_path),
            "parameter_space_sha256": _sha256(parameter_path),
            "output_metrics": str(output_metric_path),
            "output_metrics_sha256": _sha256(output_metric_path),
        },
        "runner_identity": {
            "runner_file": "src/modeling/ode/morris_screening.py",
            "runner_sha256": _sha256(Path(__file__)),
            "solver_file": "src/modeling/ode/minimal_solver.py",
            "solver_sha256": _sha256(Path(__file__).with_name("minimal_solver.py")),
        },
        "outputs": {
            "elementary_effects": {
                "file": effects_path.name,
                "sha256": _sha256(effects_path),
            },
            "summary": {
                "file": summary_path.name,
                "sha256": _sha256(summary_path),
            },
        },
        "result_boundary": analysis["result_boundary"],
    }
    metadata_path = output_dir / "run_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> None:
    args = parse_args()
    metadata = run_morris_screening(
        args.config,
        args.out_dir,
        parameter_ids=args.parameter_id,
        ligand_context_ids=args.ligand_context,
        copy_numbers=args.copy_number,
        metric_ids=args.metric_id,
        trajectory_count=args.trajectory_count,
    )
    print(
        "Wrote {elementary_effect_row_count} elementary effects and "
        "{summary_row_count} Morris summary rows to {output_dir}".format(
            output_dir=Path(args.out_dir).resolve(), **metadata
        )
    )


if __name__ == "__main__":
    main()
