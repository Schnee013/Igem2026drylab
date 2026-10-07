"""Compare the preset test-guided strategy with two explicit baselines."""

from __future__ import annotations

from dataclasses import dataclass

from .config import Model, Treatment
from .loss import relative_yield_fraction, yield_loss_fraction


@dataclass(frozen=True)
class PlanOutcome:
    key: str
    treatment: Treatment
    net_income_with_test: float
    difference_from_preset: float


@dataclass(frozen=True)
class Result:
    density: float
    band: str
    treatment_key: str
    treatment: Treatment
    relative_yield_fraction: float
    yield_loss_fraction: float
    potential_revenue: float
    gross_loss: float
    baseline_production_cost: float
    net_income_without_test: float
    net_income_without_test_uniform: float
    net_income_with_test: float
    program_incremental_cost_vs_no_control: float
    program_net_benefit_vs_no_control: float
    program_roi_vs_no_control: float | None
    detection_incremental_cost_vs_uniform: float
    detection_net_benefit_vs_uniform: float
    detection_roi_vs_uniform: float | None
    economic_best_key: str
    economic_best_treatment: Treatment
    economic_best_net_income: float
    preset_opportunity_cost: float
    plan_outcomes: tuple[PlanOutcome, ...]

    @property
    def incremental_cost(self) -> float:
        """Backward-compatible alias for the no-control comparison cost."""

        return self.program_incremental_cost_vs_no_control

    @property
    def incremental_net_benefit(self) -> float:
        """Backward-compatible alias for the no-control comparison benefit."""

        return self.program_net_benefit_vs_no_control

    @property
    def incremental_roi(self) -> float | None:
        """Backward-compatible alias for the no-control comparison ROI."""

        return self.program_roi_vs_no_control


def treatment_options(model: Model) -> tuple[tuple[str, Treatment], ...]:
    return (("low", model.low), ("middle", model.middle), ("high", model.high))


def choose_treatment(density: float, model: Model) -> tuple[str, Treatment]:
    """Apply the preset demonstration thresholds; this is not an optimiser."""

    if density < model.middle_from_density:
        return "低", model.low
    if density < model.high_from_density:
        return "中", model.middle
    return "高", model.high


def choose_treatment_with_key(
    density: float, model: Model
) -> tuple[str, str, Treatment]:
    band, treatment = choose_treatment(density, model)
    key = {"低": "low", "中": "middle", "高": "high"}[band]
    return band, key, treatment


def net_income(
    gross_loss: float,
    potential_revenue: float,
    baseline_production_cost: float,
    plan: Treatment,
    extra_cost: float = 0.0,
) -> float:
    """Net income after production, residual crop loss, treatment, and test costs."""

    residual_loss = gross_loss * (1.0 - plan.avoided_loss_fraction)
    return potential_revenue - baseline_production_cost - residual_loss - plan.cost_per_ha - extra_cost


def evaluate(density: float, model: Model) -> Result:
    loss_fraction = yield_loss_fraction(density, model)
    relative_yield = relative_yield_fraction(density, model)
    potential_revenue = model.baseline_yield_kg_per_ha * model.price_per_kg
    gross_loss = potential_revenue * loss_fraction
    band, plan_key, plan = choose_treatment_with_key(density, model)

    no_control_income = net_income(
        gross_loss,
        potential_revenue,
        model.baseline_production_cost_per_ha,
        model.low,
    )
    uniform_income = net_income(
        gross_loss,
        potential_revenue,
        model.baseline_production_cost_per_ha,
        model.without_test,
    )
    guided_income = net_income(
        gross_loss,
        potential_revenue,
        model.baseline_production_cost_per_ha,
        plan,
        model.test_cost_per_ha,
    )

    program_incremental_cost = model.test_cost_per_ha + plan.cost_per_ha
    program_benefit = guided_income - no_control_income
    program_roi = (
        program_benefit / program_incremental_cost
        if program_incremental_cost > 0
        else None
    )

    detection_incremental_cost = (
        model.test_cost_per_ha + plan.cost_per_ha - model.without_test.cost_per_ha
    )
    detection_benefit = guided_income - uniform_income
    detection_roi = (
        detection_benefit / detection_incremental_cost
        if detection_incremental_cost > 0
        else None
    )

    raw_outcomes = []
    for key, option in treatment_options(model):
        option_income = net_income(
            gross_loss,
            potential_revenue,
            model.baseline_production_cost_per_ha,
            option,
            model.test_cost_per_ha,
        )
        raw_outcomes.append((key, option, option_income))
    best_key, best_plan, best_income = max(raw_outcomes, key=lambda item: item[2])
    outcomes = tuple(
        PlanOutcome(
            key=key,
            treatment=option,
            net_income_with_test=option_income,
            difference_from_preset=option_income - guided_income,
        )
        for key, option, option_income in raw_outcomes
    )

    return Result(
        density=density,
        band=band,
        treatment_key=plan_key,
        treatment=plan,
        relative_yield_fraction=relative_yield,
        yield_loss_fraction=loss_fraction,
        potential_revenue=potential_revenue,
        gross_loss=gross_loss,
        baseline_production_cost=model.baseline_production_cost_per_ha,
        net_income_without_test=no_control_income,
        net_income_without_test_uniform=uniform_income,
        net_income_with_test=guided_income,
        program_incremental_cost_vs_no_control=program_incremental_cost,
        program_net_benefit_vs_no_control=program_benefit,
        program_roi_vs_no_control=program_roi,
        detection_incremental_cost_vs_uniform=detection_incremental_cost,
        detection_net_benefit_vs_uniform=detection_benefit,
        detection_roi_vs_uniform=detection_roi,
        economic_best_key=best_key,
        economic_best_treatment=best_plan,
        economic_best_net_income=best_income,
        preset_opportunity_cost=best_income - guided_income,
        plan_outcomes=outcomes,
    )


def incremental_benefit_for_plan(
    density: float,
    model: Model,
    plan: Treatment,
    *,
    baseline: str = "no_control",
) -> float:
    """Net benefit for a fixed plan against an explicitly named baseline."""

    gross_loss = model.baseline_yield_kg_per_ha * model.price_per_kg * yield_loss_fraction(density, model)
    guided_income = net_income(
        gross_loss,
        model.baseline_yield_kg_per_ha * model.price_per_kg,
        model.baseline_production_cost_per_ha,
        plan,
        model.test_cost_per_ha,
    )
    if baseline == "no_control":
        baseline_plan = model.low
    elif baseline == "uniform_control":
        baseline_plan = model.without_test
    else:
        raise ValueError("baseline 必须是 no_control 或 uniform_control")
    baseline_income = net_income(
        gross_loss,
        model.baseline_yield_kg_per_ha * model.price_per_kg,
        model.baseline_production_cost_per_ha,
        baseline_plan,
    )
    return guided_income - baseline_income
