"""Find break-even densities on the nonlinear yield-loss curve."""

from __future__ import annotations

from .config import Model, Treatment
from .economics import evaluate, incremental_benefit_for_plan


def _bisect(
    model: Model,
    plan: Treatment,
    left: float,
    right: float,
    tolerance: float = 1e-10,
) -> float | None:
    f_left = incremental_benefit_for_plan(left, model, plan)
    f_right = incremental_benefit_for_plan(right, model, plan)
    if abs(f_left) <= tolerance:
        return left
    if abs(f_right) <= tolerance:
        return right
    if f_left * f_right > 0:
        return None
    for _ in range(100):
        midpoint = (left + right) / 2.0
        f_mid = incremental_benefit_for_plan(midpoint, model, plan)
        if abs(f_mid) <= tolerance or right - left <= tolerance:
            return midpoint
        if f_left * f_mid <= 0:
            right = midpoint
        else:
            left = midpoint
            f_left = f_mid
    return (left + right) / 2.0


def break_even_analysis(model: Model) -> tuple[list[float], list[tuple[float, float, float]]]:
    """Return strict roots and benefit jumps at grade thresholds."""

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
        actual = evaluate(root, model).incremental_net_benefit
        if abs(actual) <= root_tolerance and not any(
            abs(root - old) <= root_tolerance for old in roots
        ):
            roots.append(root)

    for left, right, plan in segments:
        add_if_actual(_bisect(model, plan, left, right))

    for threshold, left_plan in (
        (model.middle_from_density, model.low),
        (model.high_from_density, model.middle),
    ):
        left_value = incremental_benefit_for_plan(threshold, model, left_plan)
        right_value = evaluate(threshold, model).incremental_net_benefit
        if abs(left_value - right_value) > jump_tolerance:
            jumps.append((threshold, left_value, right_value))

    return sorted(roots), jumps
