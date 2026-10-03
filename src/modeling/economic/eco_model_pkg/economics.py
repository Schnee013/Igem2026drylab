"""Compare test-guided treatment with no-control and uniform-control scenarios."""

from __future__ import annotations

from dataclasses import dataclass

from .config import Model, Treatment
from .loss import relative_yield_fraction, yield_loss_fraction


@dataclass(frozen=True)
class Result:
    density: float
    band: str
    treatment: Treatment
    relative_yield_fraction: float
    yield_loss_fraction: float
    potential_revenue: float
    gross_loss: float
    baseline_production_cost: float
    net_income_without_test: float
    net_income_without_test_uniform: float
    net_income_with_test: float
    incremental_cost: float
    incremental_net_benefit: float
    incremental_roi: float | None


def choose_treatment(density: float, model: Model) -> tuple[str, Treatment]:
    """Assign the lower boundary to the newly entered band."""

    if density < model.middle_from_density:
        return "低", model.low
    if density < model.high_from_density:
        return "中", model.middle
    return "高", model.high


def net_income(
    gross_loss: float,
    potential_revenue: float,
    baseline_production_cost: float,
    plan: Treatment,
    extra_cost: float = 0.0,
) -> float:
    """Net income after production, yield-loss, treatment, and test costs."""

    residual_loss = gross_loss * (1.0 - plan.avoided_loss_fraction)
    return (
        potential_revenue
        - baseline_production_cost
        - residual_loss
        - plan.cost_per_ha
        - extra_cost
    )


def evaluate(density: float, model: Model) -> Result:
    loss_fraction = yield_loss_fraction(density, model)
    relative_yield = relative_yield_fraction(density, model)
    potential_revenue = model.baseline_yield_kg_per_ha * model.price_per_kg
    gross_loss = potential_revenue * loss_fraction
    band, plan = choose_treatment(density, model)
    no_control = model.low
    no_test = net_income(
        gross_loss,
        potential_revenue,
        model.baseline_production_cost_per_ha,
        no_control,
    )
    no_test_uniform = net_income(
        gross_loss,
        potential_revenue,
        model.baseline_production_cost_per_ha,
        model.without_test,
    )
    with_test = net_income(
        gross_loss,
        potential_revenue,
        model.baseline_production_cost_per_ha,
        plan,
        model.test_cost_per_ha,
    )
    incremental_cost = model.test_cost_per_ha + plan.cost_per_ha
    benefit = with_test - no_test
    roi = benefit / incremental_cost if incremental_cost > 0 else None
    return Result(
        density=density,
        band=band,
        treatment=plan,
        relative_yield_fraction=relative_yield,
        yield_loss_fraction=loss_fraction,
        potential_revenue=potential_revenue,
        gross_loss=gross_loss,
        baseline_production_cost=model.baseline_production_cost_per_ha,
        net_income_without_test=no_test,
        net_income_without_test_uniform=no_test_uniform,
        net_income_with_test=with_test,
        incremental_cost=incremental_cost,
        incremental_net_benefit=benefit,
        incremental_roi=roi,
    )


def incremental_benefit_for_plan(
    density: float, model: Model, plan: Treatment
) -> float:
    """Evaluate incremental benefit while holding the treatment plan fixed."""

    gross_loss = (
        model.baseline_yield_kg_per_ha
        * model.price_per_kg
        * yield_loss_fraction(density, model)
    )
    added_avoided_loss = gross_loss * plan.avoided_loss_fraction
    added_cost = model.test_cost_per_ha + plan.cost_per_ha
    return added_avoided_loss - added_cost
