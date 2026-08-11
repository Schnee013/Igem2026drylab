"""Run and render one registered Phase-2B two-parameter response surface."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from .minimal_solver import solve_normalized_scenario, validate_config
except ImportError:  # pragma: no cover - direct script execution fallback
    from minimal_solver import solve_normalized_scenario, validate_config


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = (
    ROOT
    / "experiments/ode-model/configs/phase2b_focused_two_parameter_surface.json"
)
DEFAULT_OUTPUT_DIR = (
    ROOT / "experiments/ode-model/results/phase2b_focused_two_parameter_surface"
)
REQUIRED_CONFIG_FIELDS = {
    "analysis_id",
    "evidence_status",
    "analysis_contract",
    "baseline_config",
    "parameter_ids",
    "ligand_context_id",
    "copy_number",
    "metric_id",
    "grid_points_each",
    "grid_coordinate_rule",
    "result_boundary",
}
REQUIRED_PARAMETER_FIELDS = {
    "parameter_id",
    "config_path",
    "baseline_value",
    "analysis_role",
    "sampling_distribution",
    "lower_bound",
    "upper_bound",
}
OUTPUT_FIELDS = [
    "analysis_id",
    "evidence_status",
    "ligand_context",
    "ligand_normalized",
    "copy_number",
    "metric_id",
    "gain_out_grid_index",
    "K_out_grid_index",
    "u_gain_out",
    "gain_out",
    "u_K_out",
    "K_out",
    "color_8h",
    "additive_interaction_residual",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate or run a registered Phase-2B two-parameter surface."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--execute-ode",
        action="store_true",
        help="Run the 49-point ODE grid; default behavior validates only.",
    )
    return parser.parse_args()


def _load_json(file_path: Path) -> dict[str, Any]:
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {file_path}")
    return payload


def _sha256(file_path: Path) -> str:
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def _read_csv(file_path: Path) -> list[dict[str, str]]:
    with file_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError(f"CSV cannot be empty: {file_path}")
    return rows


def _positive_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _finite(value: str | float | int, label: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be numeric") from error
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return numeric


def _set_dotted(config: dict[str, Any], dotted_path: str, value: float) -> None:
    parts = dotted_path.split(".")
    if len(parts) != 2 or parts[0] not in config:
        raise ValueError(f"unsupported config_path: {dotted_path}")
    section = config[parts[0]]
    if not isinstance(section, dict) or parts[1] not in section:
        raise ValueError(f"config_path is absent from baseline: {dotted_path}")
    section[parts[1]] = value


def _physical_from_unit(parameter: Mapping[str, str], coordinate: float) -> float:
    lower = _finite(parameter["lower_bound"], "lower_bound")
    upper = _finite(parameter["upper_bound"], "upper_bound")
    if not 0.0 <= coordinate <= 1.0 or not lower < upper:
        raise ValueError("unit coordinate and registered bounds are inconsistent")
    distribution = parameter["sampling_distribution"]
    if distribution == "uniform":
        return lower + coordinate * (upper - lower)
    if distribution == "loguniform":
        if lower <= 0:
            raise ValueError("loguniform lower_bound must be positive")
        return lower * (upper / lower) ** coordinate
    raise ValueError(f"unsupported sampling_distribution: {distribution}")


def load_surface_inputs(
    config_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, str]],
    float,
    Path,
    Path,
    Path,
]:
    """Load and validate the fixed two-parameter surface contract."""

    config_path = Path(config_path).resolve()
    analysis = _load_json(config_path)
    missing = REQUIRED_CONFIG_FIELDS.difference(analysis)
    unknown = set(analysis).difference(REQUIRED_CONFIG_FIELDS)
    if missing:
        raise ValueError(
            f"surface config is missing fields: {', '.join(sorted(missing))}"
        )
    if unknown:
        raise ValueError(
            f"surface config has unknown fields: {', '.join(sorted(unknown))}"
        )
    if analysis["evidence_status"] != "scenario_prior":
        raise ValueError("surface config requires evidence_status='scenario_prior'")
    if analysis["parameter_ids"] != ["gain_out", "K_out"]:
        raise ValueError("surface parameter_ids must be ['gain_out', 'K_out']")
    if analysis["metric_id"] != "color_8h":
        raise ValueError("focused surface metric_id must be 'color_8h'")
    if analysis["grid_coordinate_rule"] != "linear_in_registered_unit_interval":
        raise ValueError("surface grid_coordinate_rule is unsupported")
    grid_points = _positive_integer(
        analysis["grid_points_each"], "grid_points_each"
    )
    if grid_points < 3:
        raise ValueError("grid_points_each must be at least 3")
    copy_number = _positive_integer(analysis["copy_number"], "copy_number")

    contract_path = (ROOT / analysis["analysis_contract"]).resolve()
    baseline_path = (ROOT / analysis["baseline_config"]).resolve()
    contract = _load_json(contract_path)
    baseline = _load_json(baseline_path)
    validate_config(baseline)
    if float(baseline["time"]["duration_hours"]) < 8.0:
        raise ValueError("baseline duration must cover color_8h")

    stages = [row["stage"] for row in contract["analysis_sequence"]]
    if "focused_two_parameter_surfaces" not in stages:
        raise ValueError("analysis sequence is missing focused_two_parameter_surfaces")
    contexts = contract["design_contexts"]["ligand_normalized"]
    context_id = analysis["ligand_context_id"]
    if context_id not in contexts:
        raise ValueError(f"unknown ligand_context_id: {context_id}")
    if copy_number not in contract["design_contexts"]["copy_number_strata"]:
        raise ValueError("copy_number is outside the registered design strata")

    parameter_path = (
        ROOT / contract["contract_files"]["parameter_space"]
    ).resolve()
    output_metric_path = (
        ROOT / contract["contract_files"]["output_metrics"]
    ).resolve()
    parameter_rows = _read_csv(parameter_path)
    parameter_lookup = {row["parameter_id"]: row for row in parameter_rows}
    selected: list[dict[str, str]] = []
    for parameter_id in analysis["parameter_ids"]:
        if parameter_id not in parameter_lookup:
            raise ValueError(f"unknown surface parameter: {parameter_id}")
        row = parameter_lookup[parameter_id]
        missing_fields = REQUIRED_PARAMETER_FIELDS.difference(row)
        if missing_fields:
            raise ValueError(
                f"parameter {parameter_id} is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )
        if row["analysis_role"] != "uncertain_continuous":
            raise ValueError(
                f"surface parameter is not continuously sampled: {parameter_id}"
            )
        selected.append(row)

    metric_rows = _read_csv(output_metric_path)
    metric_lookup = {row["metric_id"]: row for row in metric_rows}
    metric = metric_lookup.get(analysis["metric_id"])
    if metric is None or metric["status"] != "active":
        raise ValueError("surface metric is inactive or unknown")

    return (
        analysis,
        contract,
        baseline,
        selected,
        float(contexts[context_id]),
        contract_path,
        parameter_path,
        output_metric_path,
    )


def build_surface_grid(
    parameters: Sequence[Mapping[str, str]], grid_points_each: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return unit and physical axes for the registered pair."""

    if len(parameters) != 2:
        raise ValueError("focused surface requires exactly two parameters")
    count = _positive_integer(grid_points_each, "grid_points_each")
    unit_gain = np.linspace(0.0, 1.0, count)
    unit_half = np.linspace(0.0, 1.0, count)
    gain = np.asarray(
        [_physical_from_unit(parameters[0], float(value)) for value in unit_gain]
    )
    half = np.asarray(
        [_physical_from_unit(parameters[1], float(value)) for value in unit_half]
    )
    return unit_gain, gain, unit_half, half


def additive_interaction_residuals(values: np.ndarray) -> np.ndarray:
    """Return the residual after balanced-grid row and column main effects."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or min(array.shape) < 2 or not np.all(np.isfinite(array)):
        raise ValueError("surface values must be a finite two-dimensional grid")
    return (
        array
        - array.mean(axis=1, keepdims=True)
        - array.mean(axis=0, keepdims=True)
        + array.mean()
    )


def summarize_surface(values: np.ndarray) -> dict[str, float | int | bool]:
    """Summarize monotonicity and non-additive structure on the sampled grid."""

    array = np.asarray(values, dtype=float)
    residual = additive_interaction_residuals(array)
    gain_differences = np.diff(array, axis=0)
    half_differences = np.diff(array, axis=1)
    response_min = float(array.min())
    response_max = float(array.max())
    response_range = response_max - response_min
    maximum_residual = float(np.max(np.abs(residual)))
    return {
        "response_min": response_min,
        "response_max": response_max,
        "response_range": response_range,
        "gain_out_nondecreasing_comparisons": int(
            np.count_nonzero(gain_differences >= 0)
        ),
        "gain_out_comparison_count": int(gain_differences.size),
        "K_out_nonincreasing_comparisons": int(
            np.count_nonzero(half_differences <= 0)
        ),
        "K_out_comparison_count": int(half_differences.size),
        "monotonic_in_expected_directions": bool(
            np.all(gain_differences >= 0) and np.all(half_differences <= 0)
        ),
        "interaction_residual_rms": float(np.sqrt(np.mean(np.square(residual)))),
        "interaction_residual_max_abs": maximum_residual,
        "interaction_residual_max_abs_fraction_of_response_range": (
            maximum_residual / response_range if response_range > 0 else 0.0
        ),
    }


def _default_evaluator(config: dict[str, Any]) -> float:
    result = solve_normalized_scenario(config)
    return float(result.color_signal[-1])


def _write_csv(file_path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with file_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_surface_points(file_path: Path) -> list[dict[str, str]]:
    """Read and validate a complete focused-surface CSV for plotting."""

    with Path(file_path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(OUTPUT_FIELDS).difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"surface CSV is missing columns: {', '.join(sorted(missing))}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError("surface CSV cannot be empty")
    if {row["evidence_status"] for row in rows} != {"scenario_prior"}:
        raise ValueError("surface plot requires exclusively scenario_prior rows")
    numeric_fields = set(OUTPUT_FIELDS).difference(
        {"analysis_id", "evidence_status", "ligand_context", "metric_id"}
    )
    for row in rows:
        for field in numeric_fields:
            _finite(row[field], field)
    gain_indices = sorted(
        {int(row["gain_out_grid_index"]) for row in rows}
    )
    half_indices = sorted({int(row["K_out_grid_index"]) for row in rows})
    expected = {
        (gain_index, half_index)
        for gain_index in gain_indices
        for half_index in half_indices
    }
    observed = {
        (int(row["gain_out_grid_index"]), int(row["K_out_grid_index"]))
        for row in rows
    }
    if observed != expected or len(rows) != len(expected):
        raise ValueError("surface CSV does not contain one complete rectangular grid")
    return rows


def plot_surface(rows: Sequence[Mapping[str, str]], output_path: Path) -> None:
    """Render response and balanced-grid interaction-residual heatmaps."""

    gain_values = sorted({_finite(row["gain_out"], "gain_out") for row in rows})
    half_values = sorted({_finite(row["K_out"], "K_out") for row in rows})
    gain_lookup = {value: index for index, value in enumerate(gain_values)}
    half_lookup = {value: index for index, value in enumerate(half_values)}
    response = np.empty((len(gain_values), len(half_values)), dtype=float)
    residual = np.empty_like(response)
    for row in rows:
        i = gain_lookup[_finite(row["gain_out"], "gain_out")]
        j = half_lookup[_finite(row["K_out"], "K_out")]
        response[i, j] = _finite(row["color_8h"], "color_8h")
        residual[i, j] = _finite(
            row["additive_interaction_residual"],
            "additive_interaction_residual",
        )

    half_mesh, gain_mesh = np.meshgrid(half_values, gain_values)
    figure, axes = plt.subplots(
        1, 2, figsize=(11.5, 4.8), constrained_layout=True
    )
    response_mesh = axes[0].pcolormesh(
        half_mesh, gain_mesh, response, shading="nearest", cmap="viridis"
    )
    if float(response.max()) > float(response.min()):
        contours = axes[0].contour(
            half_mesh,
            gain_mesh,
            response,
            levels=6,
            colors="white",
            linewidths=0.7,
            alpha=0.8,
        )
        axes[0].clabel(contours, inline=True, fontsize=7, fmt="%.2g")
    axes[0].scatter(half_mesh, gain_mesh, s=10, color="black", alpha=0.55)
    axes[0].set_title("color_8h response")
    response_bar = figure.colorbar(response_mesh, ax=axes[0])
    response_bar.set_label("color_8h (arbitrary color units)")

    residual_limit = float(np.max(np.abs(residual)))
    if residual_limit == 0:
        residual_limit = 1.0
    residual_mesh = axes[1].pcolormesh(
        half_mesh,
        gain_mesh,
        residual,
        shading="nearest",
        cmap="coolwarm",
        vmin=-residual_limit,
        vmax=residual_limit,
    )
    axes[1].scatter(half_mesh, gain_mesh, s=10, color="black", alpha=0.55)
    axes[1].set_title("non-additive residual")
    residual_bar = figure.colorbar(residual_mesh, ax=axes[1])
    residual_bar.set_label("observed - additive main effects")

    for axis in axes:
        axis.set_xscale("log")
        axis.set_yscale("log")
        axis.set_xlabel("K_out (normalized sTF half-activation)")
        axis.set_ylabel("gain_out (effective production rate)")
        axis.grid(alpha=0.15)
    figure.suptitle(
        "Phase 2B focused surface: gain_out x K_out\n"
        "transition_reference, N=1, color_8h, scenario_prior",
        fontsize=12,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def run_focused_surface(
    config_path: Path,
    output_dir: Path,
    *,
    metric_evaluator: Callable[[dict[str, Any]], float] = _default_evaluator,
) -> dict[str, Any]:
    """Run, summarize, render, and identify the registered 49-point surface."""

    (
        analysis,
        _contract,
        baseline,
        parameters,
        ligand,
        contract_path,
        parameter_path,
        output_metric_path,
    ) = load_surface_inputs(config_path)
    unit_gain, gain_values, unit_half, half_values = build_surface_grid(
        parameters, analysis["grid_points_each"]
    )
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    values = np.empty((len(gain_values), len(half_values)), dtype=float)
    raw_rows: list[dict[str, Any]] = []
    for gain_index, (u_gain, gain) in enumerate(
        zip(unit_gain, gain_values, strict=True)
    ):
        for half_index, (u_half, half) in enumerate(
            zip(unit_half, half_values, strict=True)
        ):
            point = copy.deepcopy(baseline)
            point["scenario_id"] = (
                f"{analysis['analysis_id']}__gain_{gain_index:02d}__K_{half_index:02d}"
            )
            point["evidence_status"] = "scenario_prior"
            point["input"]["ligand_normalized"] = ligand
            point["gal_output"]["copy_number"] = analysis["copy_number"]
            _set_dotted(point, parameters[0]["config_path"], float(gain))
            _set_dotted(point, parameters[1]["config_path"], float(half))
            value = float(metric_evaluator(point))
            if not math.isfinite(value):
                raise ValueError(
                    f"non-finite surface output at gain index {gain_index}, "
                    f"K_out index {half_index}"
                )
            values[gain_index, half_index] = value
            raw_rows.append(
                {
                    "analysis_id": analysis["analysis_id"],
                    "evidence_status": analysis["evidence_status"],
                    "ligand_context": analysis["ligand_context_id"],
                    "ligand_normalized": ligand,
                    "copy_number": analysis["copy_number"],
                    "metric_id": analysis["metric_id"],
                    "gain_out_grid_index": gain_index,
                    "K_out_grid_index": half_index,
                    "u_gain_out": float(u_gain),
                    "gain_out": float(gain),
                    "u_K_out": float(u_half),
                    "K_out": float(half),
                    "color_8h": value,
                }
            )

    residual = additive_interaction_residuals(values)
    for row in raw_rows:
        row["additive_interaction_residual"] = float(
            residual[
                int(row["gain_out_grid_index"]), int(row["K_out_grid_index"])
            ]
        )

    csv_path = output_dir / "surface_points.csv"
    plot_path = output_dir / "gain_out_by_K_out_surface.png"
    _write_csv(csv_path, raw_rows)
    validated_rows = load_surface_points(csv_path)
    plot_surface(validated_rows, plot_path)
    metadata = {
        "schema_version": "ode_phase2b_focused_two_parameter_surface_v1",
        "analysis_id": analysis["analysis_id"],
        "evidence_status": analysis["evidence_status"],
        "parameter_ids": analysis["parameter_ids"],
        "ligand_context_id": analysis["ligand_context_id"],
        "ligand_normalized": ligand,
        "copy_number": analysis["copy_number"],
        "metric_id": analysis["metric_id"],
        "grid_points_each": analysis["grid_points_each"],
        "grid_coordinate_rule": analysis["grid_coordinate_rule"],
        "surface_point_count": len(raw_rows),
        "model_solve_count": len(raw_rows),
        "surface_summary": summarize_surface(values),
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
            "runner_file": "src/modeling/ode/focused_two_parameter_surface.py",
            "runner_sha256": _sha256(Path(__file__)),
            "solver_file": "src/modeling/ode/minimal_solver.py",
            "solver_sha256": _sha256(
                Path(__file__).with_name("minimal_solver.py")
            ),
        },
        "outputs": {
            "surface_points": {
                "file": csv_path.name,
                "sha256": _sha256(csv_path),
            },
            "surface_plot": {
                "file": plot_path.name,
                "sha256": _sha256(plot_path),
            },
        },
        "result_boundary": analysis["result_boundary"],
    }
    metadata_path = output_dir / "run_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    args = parse_args()
    if not args.execute_ode:
        analysis, _, _, parameters, ligand, *_ = load_surface_inputs(args.config)
        _, gain_values, _, half_values = build_surface_grid(
            parameters, analysis["grid_points_each"]
        )
        print(
            "Validated focused two-parameter surface: "
            f"{len(gain_values)} gain_out values x {len(half_values)} K_out values "
            f"= {len(gain_values) * len(half_values)} ODE points; "
            f"ligand={ligand:g}, copy={analysis['copy_number']}, "
            f"metric={analysis['metric_id']}."
        )
        return
    metadata = run_focused_surface(args.config, args.out_dir)
    print(
        "Wrote {surface_point_count} focused-surface rows and plot to "
        "{output_dir}".format(
            output_dir=Path(args.out_dir).resolve(), **metadata
        )
    )


if __name__ == "__main__":
    main()
