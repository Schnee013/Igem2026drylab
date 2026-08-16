"""Run Phase-2B local time-dependent sensitivity for the normalized ODE.

The analysis is driven by the Phase-2A machine contract and leaves the
accepted M0 equations unchanged.  It reports scaled local sensitivities
``d(output) / d(log(parameter))`` and repeats each estimate at a halved step
to expose finite-difference instability.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
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
DEFAULT_CONFIG = ROOT / "experiments/ode-model/configs/phase2b_local_sensitivity.json"
DEFAULT_OUTPUT = (
    ROOT
    / "experiments/ode-model/results/phase2b_local_sensitivity/time_dependent_sensitivities.csv"
)
REQUIRED_ANALYSIS_FIELDS = {
    "analysis_id",
    "evidence_status",
    "analysis_contract",
    "relative_step",
    "stability_step_factor",
    "numerical_zero_floor_relative_to_output_scale",
    "copy_number",
    "outputs",
    "result_boundary",
}
RESULT_OUTPUTS = {
    "receptor_active",
    "g_on",
    "mapk_active",
    "stf_activity",
    "gal_product_rate",
    "color_signal",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Phase-2B local time-dependent sensitivity analysis."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--parameter-id",
        action="append",
        help="Restrict the run to one parameter ID; repeat for multiple IDs.",
    )
    parser.add_argument(
        "--ligand-context",
        action="append",
        help="Restrict the run to one ligand context; repeat for multiple contexts.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("local-sensitivity export cannot be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _finite_float(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{label} must be finite")
    return numeric


def _get_dotted(config: Mapping[str, Any], dotted_path: str) -> Any:
    value: Any = config
    for part in dotted_path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            raise ValueError(f"configuration path does not exist: {dotted_path!r}")
        value = value[part]
    return value


def _set_dotted(config: dict[str, Any], dotted_path: str, value: float) -> None:
    parts = dotted_path.split(".")
    current: dict[str, Any] = config
    for part in parts[:-1]:
        nested = current.get(part)
        if not isinstance(nested, dict):
            raise ValueError(f"configuration path does not exist: {dotted_path!r}")
        current = nested
    if parts[-1] not in current:
        raise ValueError(f"configuration path does not exist: {dotted_path!r}")
    current[parts[-1]] = value


def _result_series(result: SimulationResult, output: str) -> np.ndarray:
    if output not in RESULT_OUTPUTS:
        raise ValueError(f"unsupported sensitivity output: {output!r}")
    return np.asarray(getattr(result, output), dtype=float)


def load_analysis_inputs(
    config_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, str]],
    list[tuple[str, str, float]],
    Path,
    Path,
]:
    """Load and cross-check the Phase-2B config, Phase-2A contract, and baseline."""

    config_path = config_path.resolve()
    analysis = _load_json(config_path)
    missing = REQUIRED_ANALYSIS_FIELDS.difference(analysis)
    unknown = set(analysis).difference(REQUIRED_ANALYSIS_FIELDS)
    if missing:
        raise ValueError(f"analysis config is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"analysis config has unknown fields: {', '.join(sorted(unknown))}")
    if analysis["evidence_status"] != "scenario_prior":
        raise ValueError("local sensitivity accepts only evidence_status='scenario_prior'")
    for field in ("analysis_id", "analysis_contract", "result_boundary"):
        if not isinstance(analysis[field], str) or not analysis[field].strip():
            raise ValueError(f"analysis config field {field!r} must be a non-empty string")

    relative_step = _finite_float(analysis["relative_step"], "relative_step")
    step_factor = _finite_float(
        analysis["stability_step_factor"], "stability_step_factor"
    )
    numerical_zero_floor = _finite_float(
        analysis["numerical_zero_floor_relative_to_output_scale"],
        "numerical_zero_floor_relative_to_output_scale",
    )
    if not 0 < relative_step < 0.25:
        raise ValueError("relative_step must be between 0 and 0.25")
    if not 0 < step_factor < 1:
        raise ValueError("stability_step_factor must be between 0 and 1")
    if not 0 < numerical_zero_floor < 1:
        raise ValueError(
            "numerical_zero_floor_relative_to_output_scale must be between 0 and 1"
        )
    if isinstance(analysis["copy_number"], bool) or not isinstance(
        analysis["copy_number"], int
    ):
        raise ValueError("copy_number must be an integer")
    outputs = analysis["outputs"]
    if (
        not isinstance(outputs, list)
        or not outputs
        or any(not isinstance(output, str) for output in outputs)
        or len(outputs) != len(set(outputs))
    ):
        raise ValueError("outputs must be a non-empty list of unique strings")
    unsupported = set(outputs).difference(RESULT_OUTPUTS)
    if unsupported:
        raise ValueError(f"unsupported sensitivity outputs: {', '.join(sorted(unsupported))}")

    contract_path = (ROOT / analysis["analysis_contract"]).resolve()
    contract = _load_json(contract_path)
    if contract.get("status") != "active_contract":
        raise ValueError("Phase-2A analysis contract must be active")
    design = contract["design_contexts"]
    if analysis["copy_number"] not in design["copy_number_strata"]:
        raise ValueError("copy_number must be one of the Phase-2A design strata")

    baseline_path = (ROOT / contract["source_baseline"]["baseline_config"]).resolve()
    baseline = _load_json(baseline_path)
    if float(baseline["time"]["duration_hours"]) != float(design["duration_hours"]):
        raise ValueError("baseline duration does not match the Phase-2A contract")
    if int(baseline["time"]["output_points"]) != int(design["output_points"]):
        raise ValueError("baseline output_points does not match the Phase-2A contract")

    parameter_path = (ROOT / contract["contract_files"]["parameter_space"]).resolve()
    parameter_rows = [
        row
        for row in _read_csv(parameter_path)
        if row["analysis_role"] == "uncertain_continuous"
    ]
    if len(parameter_rows) != int(contract["parameter_counts"]["continuous_uncertainty_fields"]):
        raise ValueError("continuous parameter count does not match the Phase-2A contract")
    for row in parameter_rows:
        baseline_value = _finite_float(
            _get_dotted(baseline, row["config_path"]), row["config_path"]
        )
        if baseline_value <= 0:
            raise ValueError(
                f"relative local sensitivity requires a positive baseline: {row['parameter_id']}"
            )
        if not math.isclose(baseline_value, float(row["baseline_value"]), rel_tol=1e-12):
            raise ValueError(f"parameter baseline mismatch: {row['parameter_id']}")

    contexts: list[tuple[str, str, float]] = []
    for context_set, context_ids in design["ligand_context_sets"].items():
        for context_id in context_ids:
            contexts.append(
                (context_set, context_id, float(design["ligand_normalized"][context_id]))
            )
    if len(contexts) != len(design["ligand_normalized"]):
        raise ValueError("ligand contexts must be classified exactly once")
    return (
        analysis,
        contract,
        baseline,
        parameter_rows,
        contexts,
        contract_path,
        parameter_path,
    )


def _difference_scheme(
    baseline: float,
    lower_bound: float,
    upper_bound: float,
    relative_step: float,
) -> str:
    delta = baseline * relative_step
    if baseline - delta >= lower_bound and baseline + delta <= upper_bound:
        return "central"
    if baseline + delta <= upper_bound:
        return "forward"
    if baseline - delta >= lower_bound:
        return "backward"
    raise ValueError("finite-difference step does not fit within the parameter bounds")


def _solve_at_parameter(
    base_config: dict[str, Any],
    config_path: str,
    parameter_value: float,
) -> SimulationResult:
    config = copy.deepcopy(base_config)
    _set_dotted(config, config_path, parameter_value)
    return solve_normalized_scenario(config)


def _scaled_derivative(
    base_config: dict[str, Any],
    parameter_path: str,
    baseline_value: float,
    baseline_result: SimulationResult,
    outputs: Sequence[str],
    relative_step: float,
    scheme: str,
) -> dict[str, np.ndarray]:
    lower_value = baseline_value * (1.0 - relative_step)
    upper_value = baseline_value * (1.0 + relative_step)
    if scheme == "central":
        lower = _solve_at_parameter(base_config, parameter_path, lower_value)
        upper = _solve_at_parameter(base_config, parameter_path, upper_value)
        return {
            output: (_result_series(upper, output) - _result_series(lower, output))
            / (2.0 * relative_step)
            for output in outputs
        }
    if scheme == "forward":
        upper = _solve_at_parameter(base_config, parameter_path, upper_value)
        return {
            output: (_result_series(upper, output) - _result_series(baseline_result, output))
            / relative_step
            for output in outputs
        }
    if scheme == "backward":
        lower = _solve_at_parameter(base_config, parameter_path, lower_value)
        return {
            output: (_result_series(baseline_result, output) - _result_series(lower, output))
            / relative_step
            for output in outputs
        }
    raise ValueError(f"unsupported finite-difference scheme: {scheme}")


def compute_parameter_context_rows(
    analysis: Mapping[str, Any],
    baseline: dict[str, Any],
    parameter: Mapping[str, str],
    context: tuple[str, str, float],
) -> list[dict[str, Any]]:
    """Compute one parameter/context trace with a step-halving stability check."""

    context_set, context_id, ligand = context
    configured = copy.deepcopy(baseline)
    configured["scenario_id"] = f"{analysis['analysis_id']}__{parameter['parameter_id']}__{context_id}"
    configured["input"]["ligand_normalized"] = ligand
    configured["gal_output"]["copy_number"] = analysis["copy_number"]

    baseline_value = _finite_float(
        _get_dotted(configured, parameter["config_path"]), parameter["config_path"]
    )
    lower_bound = float(parameter["lower_bound"])
    upper_bound = float(parameter["upper_bound"])
    coarse_step = float(analysis["relative_step"])
    fine_step = coarse_step * float(analysis["stability_step_factor"])
    scheme = _difference_scheme(baseline_value, lower_bound, upper_bound, coarse_step)
    baseline_result = solve_normalized_scenario(configured)
    outputs = list(analysis["outputs"])
    coarse = _scaled_derivative(
        configured,
        parameter["config_path"],
        baseline_value,
        baseline_result,
        outputs,
        coarse_step,
        scheme,
    )
    fine = _scaled_derivative(
        configured,
        parameter["config_path"],
        baseline_value,
        baseline_result,
        outputs,
        fine_step,
        scheme,
    )

    rows: list[dict[str, Any]] = []
    output_scales = {
        output: max(float(np.max(np.abs(_result_series(baseline_result, output)))), 1.0)
        for output in outputs
    }
    for index, time_hours in enumerate(baseline_result.time_hours):
        row: dict[str, Any] = {
            "analysis_id": analysis["analysis_id"],
            "evidence_status": analysis["evidence_status"],
            "parameter_id": parameter["parameter_id"],
            "config_path": parameter["config_path"],
            "ligand_context_set": context_set,
            "ligand_context": context_id,
            "ligand_normalized": ligand,
            "copy_number": analysis["copy_number"],
            "baseline_parameter_value": baseline_value,
            "finite_difference_scheme": scheme,
            "relative_step": fine_step,
            "time_hours": float(time_hours),
        }
        for output in outputs:
            baseline_output = float(_result_series(baseline_result, output)[index])
            sensitivity = float(fine[output][index])
            elasticity_floor = output_scales[output] * 1e-10
            stability_floor = output_scales[output] * float(
                analysis["numerical_zero_floor_relative_to_output_scale"]
            )
            difference = abs(sensitivity - float(coarse[output][index]))
            sensitivity_scale = max(abs(sensitivity), abs(float(coarse[output][index])))
            step_difference = (
                0.0 if sensitivity_scale <= stability_floor else difference / sensitivity_scale
            )
            row[f"{output}_baseline"] = baseline_output
            row[f"{output}_scaled_sensitivity"] = sensitivity
            row[f"{output}_elasticity"] = (
                sensitivity / baseline_output
                if abs(baseline_output) > elasticity_floor
                else ""
            )
            row[f"{output}_step_halving_relative_difference"] = step_difference
        rows.append(row)
    return rows


def run_local_sensitivity(
    config_path: Path,
    output_path: Path,
    *,
    parameter_ids: Sequence[str] | None = None,
    ligand_context_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run the selected contract slice and write CSV plus provenance metadata."""

    (
        analysis,
        contract,
        baseline,
        parameters,
        contexts,
        contract_path,
        parameter_path,
    ) = load_analysis_inputs(config_path)
    available_parameters = {row["parameter_id"] for row in parameters}
    available_contexts = {context_id for _, context_id, _ in contexts}
    selected_parameter_ids = set(parameter_ids or available_parameters)
    selected_context_ids = set(ligand_context_ids or available_contexts)
    unknown_parameters = selected_parameter_ids.difference(available_parameters)
    unknown_contexts = selected_context_ids.difference(available_contexts)
    if unknown_parameters:
        raise ValueError(f"unknown parameter IDs: {', '.join(sorted(unknown_parameters))}")
    if unknown_contexts:
        raise ValueError(f"unknown ligand contexts: {', '.join(sorted(unknown_contexts))}")
    parameters = [row for row in parameters if row["parameter_id"] in selected_parameter_ids]
    contexts = [context for context in contexts if context[1] in selected_context_ids]

    rows: list[dict[str, Any]] = []
    for parameter in parameters:
        for context in contexts:
            rows.extend(compute_parameter_context_rows(analysis, baseline, parameter, context))
    output_path = output_path.resolve()
    _write_csv(output_path, rows)
    baseline_path = (
        ROOT / contract["source_baseline"]["baseline_config"]
    ).resolve()
    runner_path = Path(__file__).resolve()
    solver_path = runner_path.with_name("minimal_solver.py")

    metadata = {
        "schema_version": "ode_phase2b_local_sensitivity_v1",
        "analysis_id": analysis["analysis_id"],
        "evidence_status": analysis["evidence_status"],
        "parameter_count": len(parameters),
        "ligand_context_count": len(contexts),
        "time_point_count": int(contract["design_contexts"]["output_points"]),
        "row_count": len(rows),
        "finite_difference": {
            "reported_quantity": "d(output)/d(log(parameter))",
            "relative_step": analysis["relative_step"],
            "stability_step_factor": analysis["stability_step_factor"],
            "numerical_zero_floor_relative_to_output_scale": analysis[
                "numerical_zero_floor_relative_to_output_scale"
            ],
            "boundary_rule": "central when both perturbations fit; otherwise one-sided within registered bounds",
        },
        "source_provenance": {
            "analysis_config": str(config_path.resolve()),
            "analysis_config_sha256": _sha256(config_path.resolve()),
            "phase2a_contract": str(contract_path),
            "phase2a_contract_sha256": _sha256(contract_path),
            "parameter_space": str(parameter_path),
            "parameter_space_sha256": _sha256(parameter_path),
            "baseline_config": str(baseline_path),
            "baseline_config_sha256": _sha256(baseline_path),
        },
        "runner_identity": {
            "runner_file": str(runner_path.relative_to(ROOT)),
            "runner_sha256": _sha256(runner_path),
            "solver_file": str(solver_path.relative_to(ROOT)),
            "solver_sha256": _sha256(solver_path),
        },
        "output": {
            "csv_file": output_path.name,
            "bytes": output_path.stat().st_size,
            "sha256": _sha256(output_path),
        },
        "result_boundary": analysis["result_boundary"],
    }
    metadata_path = output_path.with_name("run_metadata.json")
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    args = parse_args()
    metadata = run_local_sensitivity(
        args.config,
        args.out,
        parameter_ids=args.parameter_id,
        ligand_context_ids=args.ligand_context,
    )
    print(
        f"Wrote {metadata['row_count']} local-sensitivity rows for "
        f"{metadata['parameter_count']} parameters and "
        f"{metadata['ligand_context_count']} ligand contexts to {args.out}"
    )


if __name__ == "__main__":
    main()
