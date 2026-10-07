"""Find break-even densities on the nonlinear yield-loss curve."""

from __future__ import annotations

from .config import Model, Treatment
from .economics import evaluate, incremental_benefit_for_plan


def _bisect(
    model: Model,
    plan: Treatment,
    left: float,
    right: float,
    baseline: str,
    tolerance: float = 1e-10,
) -> float | None:
    f_left = incremental_benefit_for_plan(left, model, plan, baseline=baseline)
    f_right = incremental_benefit_for_plan(right, model, plan, baseline=baseline)
    if abs(f_left) <= tolerance:
        return left
    if abs(f_right) <= tolerance:
        return right
    if f_left * f_right > 0:
        return None
    for _ in range(100):
        midpoint = (left + right) / 2.0
        f_mid = incremental_benefit_for_plan(
            midpoint, model, plan, baseline=baseline
        )
        if abs(f_mid) <= tolerance or right - left <= tolerance:
            return midpoint
        if f_left * f_mid <= 0:
            right = midpoint
        else:
            left = midpoint
            f_left = f_mid
    return (left + right) / 2.0


def break_even_analysis(
    model: Model, *, baseline: str = "no_control"
) -> tuple[list[float], list[tuple[float, float, float]]]:
    """Return roots and threshold jumps for one explicit comparison baseline."""

    if baseline not in {"no_control", "uniform_control"}:
        raise ValueError("baseline 必须是 no_control 或 uniform_control")

    segments = (
        (0.0, model.middle_from_density, model.low),
        (model.middle_from_density, model.high_from_density, model.middle),
        (model.high_from_density, model.max_density, model.high),
    )
    roots: list[float] = []
    jumps: list[tuple[float, float, float]] = []
    root_tolerance = 1e-7
    jump_tolerance = 1e-2

    def add_if_actual(root: float | None) -> None:
        if root is None:
            return
        result = evaluate(root, model)
        actual = (
            result.program_net_benefit_vs_no_control
            if baseline == "no_control"
            else result.detection_net_benefit_vs_uniform
        )
        if abs(actual) <= root_tolerance and not any(
            abs(root - old) <= root_tolerance for old in roots
        ):
            roots.append(root)

    for left, right, plan in segments:
        add_if_actual(_bisect(model, plan, left, right, baseline))

    for threshold, left_plan in (
        (model.middle_from_density, model.low),
        (model.high_from_density, model.middle),
    ):
        left_value = incremental_benefit_for_plan(
            threshold, model, left_plan, baseline=baseline
        )
        result = evaluate(threshold, model)
        right_value = (
            result.program_net_benefit_vs_no_control
            if baseline == "no_control"
            else result.detection_net_benefit_vs_uniform
        )
        if abs(left_value - right_value) > jump_tolerance:
            jumps.append((threshold, left_value, right_value))

    return sorted(roots), jumps
