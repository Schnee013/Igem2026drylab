"""Deterministic cost-accounting helpers for P2 early-detection economics.

The MVP intentionally separates evidence-backed loss rules from HP/wet-lab
unknowns such as sensor unit cost, deployment density, and field performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LossEstimate:
    """Yield-loss estimate for a single density input."""

    loss_fraction: float | None
    normal_yield_percent: float | None
    note: str


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def interpolate_piecewise(points: list[list[float]], x: float) -> float:
    """Linearly interpolate y from sorted ``[x, y]`` points.

    Values outside the table are clamped to the nearest endpoint rather than
    extrapolated. That keeps extension-table examples conservative.
    """

    if not points:
        raise ValueError("piecewise rule requires at least one point")

    sorted_points = sorted((float(px), float(py)) for px, py in points)
    if x <= sorted_points[0][0]:
        return sorted_points[0][1]
    if x >= sorted_points[-1][0]:
        return sorted_points[-1][1]

    for (x0, y0), (x1, y1) in zip(sorted_points, sorted_points[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            weight = (x - x0) / (x1 - x0)
            return y0 + weight * (y1 - y0)

    raise RuntimeError("failed to interpolate piecewise rule")


def estimate_loss(rule: dict[str, Any], density: float, baseline_yield_per_area: float | None) -> LossEstimate:
    """Estimate yield loss from one configured rule.

    Supported rule types:
    - ``piecewise_percent_normal_yield``: points map density to percent normal yield.
    - ``linear_loss_per_density_increment``: loss in yield units per density increment.
    - ``threshold_only``: no numeric revenue-loss estimate; use for decision trees.
    """

    rule_type = rule.get("type")

    if rule_type == "piecewise_percent_normal_yield":
        normal_pct = interpolate_piecewise(rule["points"], density)
        loss_fraction = clamp(1.0 - normal_pct / 100.0, 0.0, 1.0)
        return LossEstimate(loss_fraction, normal_pct, "piecewise table")

    if rule_type == "linear_loss_per_density_increment":
        if baseline_yield_per_area is None:
            return LossEstimate(None, None, "missing baseline yield")
        increment = float(rule["density_increment"])
        loss_per_increment = float(rule["yield_loss_per_increment"])
        cap = float(rule.get("max_loss_fraction", 1.0))
        if increment <= 0:
            raise ValueError("density_increment must be positive")
        raw_loss_yield = max(0.0, density / increment) * loss_per_increment
        loss_fraction = clamp(raw_loss_yield / baseline_yield_per_area, 0.0, cap)
        return LossEstimate(loss_fraction, 100.0 * (1.0 - loss_fraction), "linear density-loss approximation")

    if rule_type == "threshold_only":
        return LossEstimate(None, None, "threshold-only rule; no yield-loss function yet")

    raise ValueError(f"unsupported yield loss rule type: {rule_type}")


def evaluate_scenario(scenario: dict[str, Any], intervention_effects: list[float]) -> list[dict[str, Any]]:
    """Evaluate one scenario over an intervention-effect sweep.

    ``intervention_effect`` means the fraction of late-scenario revenue loss
    avoided by early detection plus timely intervention.
    """

    density = float(scenario["density_input"]["value"])
    baseline_yield = scenario.get("baseline_yield_per_area")
    baseline_yield = None if baseline_yield is None else float(baseline_yield)
    price = scenario.get("crop_price_per_yield_unit")
    price = None if price is None else float(price)

    loss = estimate_loss(scenario["yield_loss_rule"], density, baseline_yield)
    can_monetize = loss.loss_fraction is not None and baseline_yield is not None and price is not None
    gross_loss = baseline_yield * price * loss.loss_fraction if can_monetize else None

    early_costs = scenario.get("early_program_costs_per_area", [])
    if not early_costs:
        early_costs = [None]

    rows = []
    for effect in intervention_effects:
        effect = clamp(float(effect), 0.0, 1.0)
        residual_loss = gross_loss * (1.0 - effect) if gross_loss is not None else None
        break_even = gross_loss - residual_loss if gross_loss is not None else None

        for early_cost in early_costs:
            early_cost_value = None if early_cost is None else float(early_cost)
            net_benefit = None
            roi = None
            if break_even is not None and early_cost_value is not None:
                net_benefit = break_even - early_cost_value
                roi = net_benefit / early_cost_value if early_cost_value > 0 else None

            rows.append({
                "scenario_id": scenario["scenario_id"],
                "crop": scenario.get("crop", ""),
                "nematode": scenario.get("nematode", ""),
                "area_unit": scenario.get("area_unit", ""),
                "yield_unit": scenario.get("yield_unit", ""),
                "currency": scenario.get("currency", "USD"),
                "density_value": density,
                "density_unit": scenario["density_input"].get("unit", ""),
                "loss_rule_type": scenario["yield_loss_rule"].get("type", ""),
                "normal_yield_percent": loss.normal_yield_percent,
                "yield_loss_fraction": loss.loss_fraction,
                "gross_loss_per_area": gross_loss,
                "intervention_effect": effect,
                "residual_loss_per_area": residual_loss,
                "break_even_early_program_cost_per_area": break_even,
                "early_program_cost_per_area": early_cost_value,
                "net_benefit_per_area": net_benefit,
                "roi": roi,
                "evidence_status": scenario.get("evidence_status", ""),
                "hp_status": scenario.get("hp_status", ""),
                "notes": "; ".join([scenario.get("notes", ""), loss.note]).strip("; "),
            })

    return rows


def evaluate_config(config: dict[str, Any]) -> list[dict[str, Any]]:
    effects = [float(x) for x in config.get("intervention_effect_sweep", [0.25, 0.5, 0.75])]
    rows: list[dict[str, Any]] = []
    for scenario in config["scenarios"]:
        if not scenario.get("enabled", True):
            continue
        rows.extend(evaluate_scenario(scenario, effects))
    return rows
