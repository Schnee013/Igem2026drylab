"""Run conditional Sobol analysis for the Morris-selected Phase-2B subset.

The module builds deterministic scrambled-Sobol A/B designs, maps unit-cube
coordinates through the Phase-2A uniform or log-uniform parameter ranges, and
estimates first-, total-, and optional second-order variance contributions.
The command line validates the design by default; ODE execution requires the
explicit ``--execute-ode`` gate.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, Sequence

import numpy as np
from scipy.stats import qmc

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.modeling.ode.morris_screening import (
        CONTROL_METRICS,
        _configured_point,
        _evaluate_metrics,
        normalized_to_physical,
    )
else:
    from .morris_screening import (
        CONTROL_METRICS,
        _configured_point,
        _evaluate_metrics,
        normalized_to_physical,
    )


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "experiments/ode-model/configs/phase2b_sobol_sensitivity.json"
DEFAULT_OUTPUT_DIR = ROOT / "experiments/ode-model/results/phase2b_sobol_sensitivity"
REQUIRED_CONFIG_FIELDS = {
    "analysis_id",
    "evidence_status",
    "analysis_contract",
    "parameter_ids",
    "ligand_context_ids",
    "copy_numbers",
    "metric_ids",
    "random_seed",
    "pilot_base_sample_size",
    "second_order_base_sample_size",
    "bootstrap_replicates",
    "confidence_level",
    "result_boundary",
}

MetricEvaluator = Callable[
    [dict[str, Any], Sequence[str], Mapping[str, Any], dict[str, float]],
    tuple[dict[str, float], int, bool],
]


@dataclass(frozen=True)
class SobolDesign:
    """Saltelli A/B matrices and one-column swap matrices."""

    unit_a: np.ndarray
    unit_b: np.ndarray
    unit_ab: tuple[np.ndarray, ...]
    unit_ba: tuple[np.ndarray, ...] | None

    @property
    def base_sample_size(self) -> int:
        return int(self.unit_a.shape[0])

    @property
    def dimension(self) -> int:
        return int(self.unit_a.shape[1])

    @property
    def design_row_count(self) -> int:
        multiplier = 2 * self.dimension + 2 if self.unit_ba is not None else self.dimension + 2
        return self.base_sample_size * multiplier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate or run Phase-2B conditional Sobol sensitivity analysis."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--base-sample-size", type=int)
    parser.add_argument("--second-order", action="store_true")
    parser.add_argument(
        "--execute-ode",
        action="store_true",
        help="Run the registered ODE design after the validation gate is approved.",
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


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Sobol export cannot be empty: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _power_of_two(value: Any, label: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 2
        or value & (value - 1)
    ):
        raise ValueError(f"{label} must be a power-of-two integer >= 2")
    return value


def _unique_strings(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"{label} must be a non-empty list of unique strings")
    return list(value)


def _unique_integers(value: Any, label: str) -> list[int]:
    if (
        not isinstance(value, list)
        or not value
        or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"{label} must be a non-empty list of unique integers")
    return list(value)


def load_sobol_inputs(
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
    """Load and validate the conditional Sobol configuration and sources."""

    config_path = config_path.resolve()
    analysis = _load_json(config_path)
    missing = REQUIRED_CONFIG_FIELDS.difference(analysis)
    unknown = set(analysis).difference(REQUIRED_CONFIG_FIELDS)
    if missing:
        raise ValueError(f"Sobol config is missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"Sobol config has unknown fields: {', '.join(sorted(unknown))}")
    if analysis["evidence_status"] != "scenario_prior":
        raise ValueError("Sobol analysis accepts only evidence_status='scenario_prior'")
    for field in ("analysis_id", "analysis_contract", "result_boundary"):
        if not isinstance(analysis[field], str) or not analysis[field].strip():
            raise ValueError(f"Sobol config field {field!r} must be a non-empty string")

    parameter_ids = _unique_strings(analysis["parameter_ids"], "parameter_ids")
    context_ids = _unique_strings(
        analysis["ligand_context_ids"], "ligand_context_ids"
    )
    copy_numbers = _unique_integers(analysis["copy_numbers"], "copy_numbers")
    metric_ids = _unique_strings(analysis["metric_ids"], "metric_ids")
    _power_of_two(analysis["pilot_base_sample_size"], "pilot_base_sample_size")
    _power_of_two(
        analysis["second_order_base_sample_size"], "second_order_base_sample_size"
    )
    if isinstance(analysis["random_seed"], bool) or not isinstance(
        analysis["random_seed"], int
    ):
        raise ValueError("random_seed must be an integer")
    if (
        isinstance(analysis["bootstrap_replicates"], bool)
        or not isinstance(analysis["bootstrap_replicates"], int)
        or analysis["bootstrap_replicates"] < 2
    ):
        raise ValueError("bootstrap_replicates must be an integer >= 2")
    confidence = analysis["confidence_level"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("confidence_level must be numeric")
    if not 0.0 < float(confidence) < 1.0:
        raise ValueError("confidence_level must lie in (0, 1)")

    contract_path = (ROOT / analysis["analysis_contract"]).resolve()
    contract = _load_json(contract_path)
    if contract.get("status") != "active_contract":
        raise ValueError("Phase-2A analysis contract must be active")
    stages = [row["stage"] for row in contract["analysis_sequence"]]
    if "conditional_subset_sobol" not in stages:
        raise ValueError("analysis sequence must include conditional_subset_sobol")
    if stages.index("conditional_subset_sobol") > stages.index(
        "focused_two_parameter_surfaces"
    ):
        raise ValueError("conditional_subset_sobol must precede focused surfaces")

    baseline_path = (ROOT / contract["source_baseline"]["baseline_config"]).resolve()
    baseline = _load_json(baseline_path)
    parameter_path = (ROOT / contract["contract_files"]["parameter_space"]).resolve()
    all_parameters = [
        row
        for row in _read_csv(parameter_path)
        if row["analysis_role"] == "uncertain_continuous"
    ]
    parameter_lookup = {row["parameter_id"]: row for row in all_parameters}
    unknown_parameters = set(parameter_ids).difference(parameter_lookup)
    if unknown_parameters:
        raise ValueError(
            f"unknown Sobol parameters: {', '.join(sorted(unknown_parameters))}"
        )
    parameters = [parameter_lookup[parameter_id] for parameter_id in parameter_ids]
    for row in parameters:
        lower = float(row["lower_bound"])
        upper = float(row["upper_bound"])
        if not math.isfinite(lower) or not math.isfinite(upper) or lower >= upper:
            raise ValueError(f"invalid parameter bounds: {row['parameter_id']}")
        if row["sampling_distribution"] == "loguniform" and lower <= 0:
            raise ValueError(
                f"loguniform lower bound must be positive: {row['parameter_id']}"
            )
        if row["sampling_distribution"] not in {"uniform", "loguniform"}:
            raise ValueError(
                f"unsupported sampling distribution: {row['sampling_distribution']!r}"
            )

    design = contract["design_contexts"]
    context_lookup: dict[str, tuple[str, str, float]] = {}
    for context_set, registered_ids in design["ligand_context_sets"].items():
        for context_id in registered_ids:
            context_lookup[context_id] = (
                context_set,
                context_id,
                float(design["ligand_normalized"][context_id]),
            )
    unknown_contexts = set(context_ids).difference(context_lookup)
    if unknown_contexts:
        raise ValueError(f"unknown ligand contexts: {', '.join(sorted(unknown_contexts))}")
    contexts = [context_lookup[context_id] for context_id in context_ids]
    unknown_copies = set(copy_numbers).difference(design["copy_number_strata"])
    if unknown_copies:
        raise ValueError(f"unknown copy numbers: {', '.join(map(str, sorted(unknown_copies)))}")

    output_path = (ROOT / contract["contract_files"]["output_metrics"]).resolve()
    active_metrics = [
        row
        for row in _read_csv(output_path)
        if row["status"] in {"active", "active_with_denominator_guard"}
    ]
    metric_lookup = {row["metric_id"]: row for row in active_metrics}
    unknown_metrics = set(metric_ids).difference(metric_lookup)
    if unknown_metrics:
        raise ValueError(f"inactive or unknown metrics: {', '.join(sorted(unknown_metrics))}")
    metric_rows = [metric_lookup[metric_id] for metric_id in metric_ids]

    if "b_TF" in parameter_ids:
        b_tf = parameter_lookup["b_TF"]
        e_tf_baseline = float(baseline["transcription"]["efficacy"])
        if float(b_tf["upper_bound"]) + e_tf_baseline > 1.0 + 1e-12:
            raise ValueError("selected b_TF range violates b_TF + fixed E_TF <= 1")

    return (
        analysis,
        contract,
        baseline,
        parameters,
        contexts,
        copy_numbers,
        metric_rows,
        contract_path,
        parameter_path,
        output_path,
    )


def build_saltelli_design(
    dimension: int,
    *,
    base_sample_size: int,
    random_seed: int,
    second_order: bool = False,
) -> SobolDesign:
    """Build a deterministic scrambled-Sobol Saltelli design."""

    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError("dimension must be an integer >= 1")
    size = _power_of_two(base_sample_size, "base_sample_size")
    if isinstance(random_seed, bool) or not isinstance(random_seed, int):
        raise ValueError("random_seed must be an integer")
    exponent = int(math.log2(size))
    raw = qmc.Sobol(d=2 * dimension, scramble=True, seed=random_seed).random_base2(
        exponent
    )
    unit_a = np.asarray(raw[:, :dimension], dtype=float)
    unit_b = np.asarray(raw[:, dimension:], dtype=float)
    unit_ab: list[np.ndarray] = []
    unit_ba: list[np.ndarray] = []
    for index in range(dimension):
        ab = unit_a.copy()
        ab[:, index] = unit_b[:, index]
        unit_ab.append(ab)
        if second_order:
            ba = unit_b.copy()
            ba[:, index] = unit_a[:, index]
            unit_ba.append(ba)
    return SobolDesign(
        unit_a=unit_a,
        unit_b=unit_b,
        unit_ab=tuple(unit_ab),
        unit_ba=tuple(unit_ba) if second_order else None,
    )


def transform_unit_samples(
    unit_samples: np.ndarray,
    parameters: Sequence[Mapping[str, str]],
) -> np.ndarray:
    """Map a unit-cube matrix through registered marginal distributions."""

    samples = np.asarray(unit_samples, dtype=float)
    if samples.ndim != 2 or samples.shape[1] != len(parameters):
        raise ValueError("unit sample matrix width must match parameter count")
    if not np.all(np.isfinite(samples)) or np.any(samples < 0.0) or np.any(samples > 1.0):
        raise ValueError("unit samples must be finite and lie in [0, 1]")
    physical = np.empty_like(samples)
    for column, row in enumerate(parameters):
        physical[:, column] = [
            normalized_to_physical(row, float(value)) for value in samples[:, column]
        ]
    return physical


def iter_design_blocks(
    design: SobolDesign,
    parameter_ids: Sequence[str],
) -> list[tuple[str, str, np.ndarray]]:
    """Return design blocks in stable manifest and evaluation order."""

    if len(parameter_ids) != design.dimension:
        raise ValueError("parameter_ids length must match Sobol design dimension")
    blocks: list[tuple[str, str, np.ndarray]] = [
        ("A", "", design.unit_a),
        ("B", "", design.unit_b),
    ]
    blocks.extend(
        (f"AB_{parameter_id}", parameter_id, design.unit_ab[index])
        for index, parameter_id in enumerate(parameter_ids)
    )
    if design.unit_ba is not None:
        blocks.extend(
            (f"BA_{parameter_id}", parameter_id, design.unit_ba[index])
            for index, parameter_id in enumerate(parameter_ids)
        )
    return blocks


def build_sample_manifest(
    design: SobolDesign,
    parameters: Sequence[Mapping[str, str]],
) -> list[dict[str, Any]]:
    """Build a row-level manifest containing unit and physical coordinates."""

    parameter_ids = [row["parameter_id"] for row in parameters]
    rows: list[dict[str, Any]] = []
    design_row = 0
    for block_id, swapped_parameter, unit in iter_design_blocks(design, parameter_ids):
        physical = transform_unit_samples(unit, parameters)
        for sample_index in range(design.base_sample_size):
            design_row += 1
            row: dict[str, Any] = {
                "design_row": design_row,
                "base_sample_index": sample_index,
                "matrix_id": block_id,
                "swapped_parameter_id": swapped_parameter,
            }
            for column, parameter_id in enumerate(parameter_ids):
                row[f"u_{parameter_id}"] = float(unit[sample_index, column])
                row[parameter_id] = float(physical[sample_index, column])
            rows.append(row)
    return rows


def evaluate_design(
    design: SobolDesign,
    parameter_ids: Sequence[str],
    evaluator: Callable[[np.ndarray], float],
) -> dict[str, np.ndarray]:
    """Evaluate a scalar callable over every design block."""

    output: dict[str, np.ndarray] = {}
    for block_id, _, matrix in iter_design_blocks(design, parameter_ids):
        output[block_id] = np.asarray([evaluator(row) for row in matrix], dtype=float)
    return output


def _validate_outputs(
    design: SobolDesign,
    parameter_ids: Sequence[str],
    outputs: Mapping[str, np.ndarray],
) -> None:
    for block_id, _, _ in iter_design_blocks(design, parameter_ids):
        if block_id not in outputs:
            raise ValueError(f"missing Sobol output block: {block_id}")
        values = np.asarray(outputs[block_id], dtype=float)
        if values.shape != (design.base_sample_size,):
            raise ValueError(f"Sobol output block has wrong shape: {block_id}")
        invalid = np.flatnonzero(~np.isfinite(values))
        if len(invalid):
            raise ValueError(
                f"non-finite Sobol output in block {block_id} at base sample "
                f"{int(invalid[0])}"
            )


def estimate_sobol_indices(
    design: SobolDesign,
    parameter_ids: Sequence[str],
    outputs: Mapping[str, np.ndarray],
) -> dict[str, list[dict[str, Any]]]:
    """Estimate Saltelli S1, Jansen ST, and optional second-order S2."""

    _validate_outputs(design, parameter_ids, outputs)
    raw_a = np.asarray(outputs["A"], dtype=float)
    raw_b = np.asarray(outputs["B"], dtype=float)
    center = float(np.mean(np.concatenate([raw_a, raw_b])))
    y_a = raw_a - center
    y_b = raw_b - center
    variance = float(np.var(np.concatenate([y_a, y_b]), ddof=0))
    if not math.isfinite(variance) or variance <= 0.0:
        raise ValueError("Sobol output variance must be finite and positive")

    parameter_rows: list[dict[str, Any]] = []
    s1_values: list[float] = []
    for parameter_id in parameter_ids:
        y_ab = np.asarray(outputs[f"AB_{parameter_id}"], dtype=float) - center
        s1 = float(np.mean(y_b * (y_ab - y_a)) / variance)
        st = float(0.5 * np.mean(np.square(y_a - y_ab)) / variance)
        s1_values.append(s1)
        parameter_rows.append(
            {
                "parameter_id": parameter_id,
                "S1": s1,
                "ST": st,
                "ST_minus_S1": st - s1,
            }
        )

    pair_rows: list[dict[str, Any]] = []
    if design.unit_ba is not None:
        for left in range(design.dimension):
            for right in range(left + 1, design.dimension):
                left_id = parameter_ids[left]
                right_id = parameter_ids[right]
                y_ba_left = np.asarray(outputs[f"BA_{left_id}"], dtype=float) - center
                y_ab_right = np.asarray(outputs[f"AB_{right_id}"], dtype=float) - center
                closed_pair = float(np.mean(y_ba_left * y_ab_right - y_a * y_b) / variance)
                pair_rows.append(
                    {
                        "parameter_i": left_id,
                        "parameter_j": right_id,
                        "S2": closed_pair - s1_values[left] - s1_values[right],
                    }
                )
    return {"parameters": parameter_rows, "pairs": pair_rows}


def bootstrap_sobol_indices(
    design: SobolDesign,
    parameter_ids: Sequence[str],
    outputs: Mapping[str, np.ndarray],
    *,
    replicates: int,
    confidence_level: float,
    random_seed: int,
) -> dict[str, list[dict[str, Any]]]:
    """Return percentile intervals using base-row bootstrap resampling."""

    if isinstance(replicates, bool) or not isinstance(replicates, int) or replicates < 2:
        raise ValueError("replicates must be an integer >= 2")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must lie in (0, 1)")
    _validate_outputs(design, parameter_ids, outputs)
    rng = np.random.default_rng(random_seed)
    parameter_samples = {
        parameter_id: {"S1": [], "ST": []} for parameter_id in parameter_ids
    }
    pair_ids = [
        (parameter_ids[left], parameter_ids[right])
        for left in range(design.dimension)
        for right in range(left + 1, design.dimension)
    ] if design.unit_ba is not None else []
    pair_samples = {pair: [] for pair in pair_ids}
    block_ids = [block_id for block_id, _, _ in iter_design_blocks(design, parameter_ids)]

    accepted = 0
    attempts = 0
    while accepted < replicates:
        attempts += 1
        if attempts > replicates * 10:
            raise ValueError("too many zero-variance bootstrap resamples")
        indices = rng.integers(0, design.base_sample_size, size=design.base_sample_size)
        sampled = {block_id: np.asarray(outputs[block_id])[indices] for block_id in block_ids}
        try:
            estimate = estimate_sobol_indices(design, parameter_ids, sampled)
        except ValueError as error:
            if "variance" in str(error):
                continue
            raise
        accepted += 1
        for row in estimate["parameters"]:
            target = parameter_samples[str(row["parameter_id"])]
            target["S1"].append(float(row["S1"]))
            target["ST"].append(float(row["ST"]))
        for row in estimate["pairs"]:
            pair = (str(row["parameter_i"]), str(row["parameter_j"]))
            pair_samples[pair].append(float(row["S2"]))

    alpha = (1.0 - confidence_level) / 2.0
    parameter_rows = []
    for parameter_id in parameter_ids:
        samples = parameter_samples[parameter_id]
        parameter_rows.append(
            {
                "parameter_id": parameter_id,
                "S1_ci_low": float(np.quantile(samples["S1"], alpha)),
                "S1_ci_high": float(np.quantile(samples["S1"], 1.0 - alpha)),
                "ST_ci_low": float(np.quantile(samples["ST"], alpha)),
                "ST_ci_high": float(np.quantile(samples["ST"], 1.0 - alpha)),
            }
        )
    pair_rows = [
        {
            "parameter_i": pair[0],
            "parameter_j": pair[1],
            "S2_ci_low": float(np.quantile(samples, alpha)),
            "S2_ci_high": float(np.quantile(samples, 1.0 - alpha)),
        }
        for pair, samples in pair_samples.items()
    ]
    return {"parameters": parameter_rows, "pairs": pair_rows}


def ishigami(unit_point: np.ndarray, *, a: float = 7.0, b: float = 0.1) -> float:
    """Evaluate the three-input Ishigami benchmark from a unit-cube point."""

    point = np.asarray(unit_point, dtype=float)
    if point.shape != (3,):
        raise ValueError("Ishigami benchmark requires exactly three inputs")
    x1, x2, x3 = -math.pi + 2.0 * math.pi * point
    return float(math.sin(x1) + a * math.sin(x2) ** 2 + b * x3**4 * math.sin(x1))


def _default_metric_evaluator(
    config: dict[str, Any],
    metric_ids: Sequence[str],
    ratio_policy: Mapping[str, Any],
    matched_control_cache: dict[str, float],
) -> tuple[dict[str, float], int, bool]:
    return _evaluate_metrics(config, metric_ids, ratio_policy, matched_control_cache)


def run_sobol_analysis(
    config_path: Path,
    output_dir: Path,
    *,
    base_sample_size: int | None = None,
    second_order: bool = False,
    bootstrap_replicates: int | None = None,
    metric_evaluator: MetricEvaluator | None = None,
) -> dict[str, Any]:
    """Run the registered conditional Sobol design and write auditable outputs."""

    (
        analysis,
        contract,
        baseline,
        parameters,
        contexts,
        copy_numbers,
        metric_rows,
        contract_path,
        parameter_path,
        output_metric_path,
    ) = load_sobol_inputs(config_path)
    parameter_ids = [row["parameter_id"] for row in parameters]
    configured_size = (
        analysis["second_order_base_sample_size"]
        if second_order
        else analysis["pilot_base_sample_size"]
    )
    size = configured_size if base_sample_size is None else base_sample_size
    size = _power_of_two(size, "base_sample_size")
    bootstrap_count = (
        analysis["bootstrap_replicates"]
        if bootstrap_replicates is None
        else bootstrap_replicates
    )
    if isinstance(bootstrap_count, bool) or not isinstance(bootstrap_count, int) or bootstrap_count < 2:
        raise ValueError("bootstrap_replicates must be an integer >= 2")
    design = build_saltelli_design(
        len(parameters),
        base_sample_size=size,
        random_seed=int(analysis["random_seed"]),
        second_order=second_order,
    )
    manifest_rows = build_sample_manifest(design, parameters)
    metric_ids = [row["metric_id"] for row in metric_rows]
    metric_lookup = {row["metric_id"]: row for row in metric_rows}
    ratio_policy = contract["metric_guard_policies"]["ratio_color_8h"]
    evaluator = metric_evaluator or _default_metric_evaluator
    matched_control_cache: dict[str, float] = {}
    matched_control_cache_hit_count = 0
    solve_count = 0
    group_outputs: dict[
        tuple[str, str, float, int, str], dict[str, np.ndarray]
    ] = {}
    blocks = iter_design_blocks(design, parameter_ids)
    for context_set, context_id, ligand in contexts:
        applicable_metrics = [
            metric_id
            for metric_id in metric_ids
            if ligand > 0 or metric_id not in CONTROL_METRICS
        ]
        for copy_number in copy_numbers:
            for metric_id in applicable_metrics:
                group_outputs[(context_set, context_id, ligand, copy_number, metric_id)] = {
                    block_id: np.empty(size, dtype=float) for block_id, _, _ in blocks
                }

    for block_id, _, matrix in blocks:
        for sample_index, point in enumerate(matrix):
            for context_set, context_id, ligand in contexts:
                applicable_metrics = [
                    metric_id
                    for metric_id in metric_ids
                    if ligand > 0 or metric_id not in CONTROL_METRICS
                ]
                for copy_number in copy_numbers:
                    scenario_id = (
                        f"{analysis['analysis_id']}__{context_id}__N{copy_number}__"
                        f"{block_id}__S{sample_index:05d}"
                    )
                    configured = _configured_point(
                        baseline,
                        parameters,
                        point,
                        ligand=ligand,
                        copy_number=copy_number,
                        scenario_id=scenario_id,
                    )
                    metrics, point_solve_count, cache_hit = evaluator(
                        configured,
                        applicable_metrics,
                        ratio_policy,
                        matched_control_cache,
                    )
                    solve_count += point_solve_count
                    matched_control_cache_hit_count += int(cache_hit)
                    for metric_id in applicable_metrics:
                        value = float(metrics[metric_id])
                        if not math.isfinite(value):
                            raise ValueError(
                                "non-finite model output for "
                                f"context={context_id}, copy={copy_number}, "
                                f"metric={metric_id}, matrix={block_id}, "
                                f"base_sample={sample_index}"
                            )
                        key = (context_set, context_id, ligand, copy_number, metric_id)
                        group_outputs[key][block_id][sample_index] = value

    index_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    for group_index, (key, outputs) in enumerate(group_outputs.items()):
        context_set, context_id, ligand, copy_number, metric_id = key
        estimate = estimate_sobol_indices(design, parameter_ids, outputs)
        intervals = bootstrap_sobol_indices(
            design,
            parameter_ids,
            outputs,
            replicates=bootstrap_count,
            confidence_level=float(analysis["confidence_level"]),
            random_seed=int(analysis["random_seed"]) + 100000 + group_index,
        )
        parameter_ci = {row["parameter_id"]: row for row in intervals["parameters"]}
        for row in estimate["parameters"]:
            parameter_id = str(row["parameter_id"])
            index_rows.append(
                {
                    "analysis_id": analysis["analysis_id"],
                    "evidence_status": analysis["evidence_status"],
                    "context_set": context_set,
                    "ligand_context": context_id,
                    "ligand_normalized": ligand,
                    "copy_number": copy_number,
                    "metric_id": metric_id,
                    "metric_role": metric_lookup[metric_id]["role"],
                    **row,
                    **parameter_ci[parameter_id],
                }
            )
        pair_ci = {
            (row["parameter_i"], row["parameter_j"]): row
            for row in intervals["pairs"]
        }
        for row in estimate["pairs"]:
            pair = (str(row["parameter_i"]), str(row["parameter_j"]))
            pair_rows.append(
                {
                    "analysis_id": analysis["analysis_id"],
                    "evidence_status": analysis["evidence_status"],
                    "context_set": context_set,
                    "ligand_context": context_id,
                    "ligand_normalized": ligand,
                    "copy_number": copy_number,
                    "metric_id": metric_id,
                    "metric_role": metric_lookup[metric_id]["role"],
                    **row,
                    **pair_ci[pair],
                }
            )

    output_dir = output_dir.resolve()
    manifest_path = output_dir / "sample_manifest.csv"
    index_path = output_dir / "sobol_indices.csv"
    _write_csv(manifest_path, manifest_rows)
    _write_csv(index_path, index_rows)
    pair_path: Path | None = None
    if pair_rows:
        pair_path = output_dir / "sobol_second_order.csv"
        _write_csv(pair_path, pair_rows)
    metadata = {
        "schema_version": "ode_phase2b_conditional_sobol_v1",
        "analysis_id": analysis["analysis_id"],
        "evidence_status": analysis["evidence_status"],
        "parameter_ids": parameter_ids,
        "ligand_context_ids": [row[1] for row in contexts],
        "copy_numbers": copy_numbers,
        "metric_ids": metric_ids,
        "random_seed": int(analysis["random_seed"]),
        "base_sample_size": size,
        "second_order": second_order,
        "design_row_count": design.design_row_count,
        "bootstrap_replicates": bootstrap_count,
        "confidence_level": float(analysis["confidence_level"]),
        "model_solve_count": solve_count,
        "matched_control_unique_solve_count": len(matched_control_cache),
        "matched_control_cache_hit_count": matched_control_cache_hit_count,
        "index_row_count": len(index_rows),
        "second_order_row_count": len(pair_rows),
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
            "runner_file": "src/modeling/ode/sobol_sensitivity.py",
            "runner_sha256": _sha256(Path(__file__)),
            "solver_file": "src/modeling/ode/minimal_solver.py",
            "solver_sha256": _sha256(Path(__file__).with_name("minimal_solver.py")),
        },
        "outputs": {
            "sample_manifest": {
                "file": manifest_path.name,
                "sha256": _sha256(manifest_path),
            },
            "indices": {"file": index_path.name, "sha256": _sha256(index_path)},
        },
        "result_boundary": analysis["result_boundary"],
    }
    if pair_path is not None:
        metadata["outputs"]["second_order"] = {
            "file": pair_path.name,
            "sha256": _sha256(pair_path),
        }
    metadata_path = output_dir / "run_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> None:
    args = parse_args()
    if not args.execute_ode:
        analysis, _, _, parameters, contexts, copies, metrics, *_ = load_sobol_inputs(
            args.config
        )
        second_order = bool(args.second_order)
        configured_size = (
            analysis["second_order_base_sample_size"]
            if second_order
            else analysis["pilot_base_sample_size"]
        )
        size = configured_size if args.base_sample_size is None else args.base_sample_size
        design = build_saltelli_design(
            len(parameters),
            base_sample_size=size,
            random_seed=int(analysis["random_seed"]),
            second_order=second_order,
        )
        print(
            "Validated conditional Sobol design: "
            f"{len(parameters)} parameters, {len(contexts) * len(copies)} design cells, "
            f"{len(metrics)} configured metrics, {design.design_row_count} rows per cell. "
            "ODE execution requires --execute-ode."
        )
        return
    metadata = run_sobol_analysis(
        args.config,
        args.out_dir,
        base_sample_size=args.base_sample_size,
        second_order=args.second_order,
    )
    print(
        "Wrote {index_row_count} Sobol index rows from {design_row_count} design rows "
        "per cell to {output_dir}".format(
            output_dir=Path(args.out_dir).resolve(), **metadata
        )
    )


if __name__ == "__main__":
    main()
