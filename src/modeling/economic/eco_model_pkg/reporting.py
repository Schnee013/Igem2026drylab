"""Create audience-friendly TXT, JSON, and HTML economic-benefit reports."""

from __future__ import annotations

import html
import json
import math
import webbrowser
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

from .break_even import break_even_analysis
from .config import Model, Treatment
from .economics import Result, choose_treatment, evaluate
from .loss import relative_yield_fraction


REFERENCES = (
    {
        "citation": (
            "EXPÓSITO A, PUJOLÀ M, ACHAERANDIO I, et al. Tomato and Melon "
            "Meloidogyne Resistant Rootstocks Improve Crop Yield but Melon Fruit Quality "
            "Is Influenced by the Cropping Season[J]. Frontiers in Plant Science, 2020, "
            "11: 560024. DOI: 10.3389/fpls.2020.560024."
        ),
        "url": "https://doi.org/10.3389/fpls.2020.560024",
    },
    {
        "citation": (
            "TALAVERA-RUBIA M, VELA-DELGADO M D, VERDEJO-LUCAS S. A Cost-Benefit "
            "Analysis of Soil Disinfestation Methods against Root-Knot Nematodes in "
            "Mediterranean Intensive Horticulture[J]. Plants, 2022, 11(20): 2774. "
            "DOI: 10.3390/plants11202774."
        ),
        "url": "https://doi.org/10.3390/plants11202774",
    },
    {
        "citation": (
            "TALAVERA M, SAYADI S, CHIROSA-RÍOS M, et al. Perception of the Impact "
            "of Root-Knot Nematode-Induced Diseases in Horticultural Protected Crops "
            "of South-Eastern Spain[J]. Nematology, 2012, 14: 517–527. "
            "DOI: 10.1163/156854112X635850."
        ),
        "url": "https://doi.org/10.1163/156854112X635850",
    },
    {
        "citation": (
            "TALAVERA M, VELA M D, ARRIAZA M. Experts’ Opinion on the Sustainable "
            "Use of Nematicides in Mediterranean Intensive Horticulture[J]. Spanish "
            "Journal of Agricultural Research, 2024, 22(1): e1001. "
            "DOI: 10.5424/sjar/2024221-20568."
        ),
        "url": "https://doi.org/10.5424/sjar/2024221-20568",
    },
    {
        "citation": (
            "MINISTERIO DE AGRICULTURA, PESCA Y ALIMENTACIÓN. Guía de Gestión "
            "Integrada de Plagas: Solanáceas[M/OL]. Madrid: MAPA, 2021."
        ),
        "url": (
            "https://www.mapa.gob.es/dam/mapa/contenido/agricultura/temas/"
            "medios-de-produccion/productos-fitosanitarios/uso-sostenible-de-productos-"
            "fitosanitarios/guias-de-gestion-integrada-de-plagas/"
            "solanaceas_web_metadatos_v03_protegida.pdf"
        ),
    },
    {
        "citation": (
            "MINISTERIO DE AGRICULTURA, PESCA Y ALIMENTACIÓN. Registro de Productos "
            "Fitosanitarios[DB/OL]. Madrid: MAPA."
        ),
        "url": "https://servicio.mapa.gob.es/regfiweb",
    },
    {
        "citation": (
            "SHAO H, ZHANG P, PENG D, et al. Current Advances in the Identification "
            "of Plant Nematode Diseases: From Lab Assays to In-Field Diagnostics[J]. "
            "Frontiers in Plant Science, 2023, 14: 1106784. "
            "DOI: 10.3389/fpls.2023.1106784."
        ),
        "url": "https://doi.org/10.3389/fpls.2023.1106784",
    },
    {
        "citation": (
            "GENERALITAT DE CATALUNYA. Service Analysis of Plant Diseases[EB/OL]. "
            "Barcelona: Canal Empresa, updated 2026-07-23."
        ),
        "url": (
            "https://canalempresa.gencat.cat/en/integraciodepartamentaltramit/"
            "tramit/PerTemes/7630_Servei-danalisis-dafeccions-vegetals"
        ),
    },
    {
        "citation": (
            "ILVO DIAGNOSTIC CENTRE FOR PLANTS. Price List for General Diagnostic "
            "Procedures[EB/OL]. Merelbeke: ILVO, valid from 2026-09-01."
        ),
        "url": (
            "https://www.ilvodiagnosecentrumvoorplanten.be/en/"
            "price-list-for-general-diagnostic-procedures"
        ),
    },
)


ZH_UI = {
    "eyebrow": "经济效益示例",
    "example_scenario": "示例场景",
    "detected_density": "检测出的线虫密度",
    "untreated_yield_loss": "如不采取防治手段，预计产量损失",
    "treatment_recommendation": "预设风险等级",
    "profit_change": "检测分级的条件增量价值",
    "section_profit": "两种收益比较",
    "without_test": "未使用试纸",
    "with_test": "使用试纸并按建议处理",
    "season_profit": "预计单季利润",
    "remaining_loss": "预计剩余产量损失",
    "treatment_cost": "处理成本",
    "test_cost": "试纸成本",
    "program_benefit": "整套检测与防治项目净收益",
    "detection_value": "检测信息与分级决策的条件增量价值",
    "incremental_cost": "增量成本",
    "roi": "ROI",
    "roi_not_applicable": "不适用（增量成本不为正）",
    "detection_costs": "常用线虫检测方法成本对比",
    "section_loss": "净收益、盈亏平衡与敏感性",
    "legend_low": "低等级",
    "legend_middle": "中等级",
    "legend_high": "高等级",
    "current_input": "本次输入",
    "section_plans": "预设分级与经济比较",
    "current_density": "当前密度",
    "avoided_loss": "预计避免作物损失",
    "preset_strategy": "预设演示策略",
    "economic_best": "当前参数下经济净收入最高",
    "option_profit": "检测后预计利润",
    "difference_from_preset": "相对预设方案",
    "effect_scope": "效果适用性",
    "sensitivity": "关键参数单因素敏感性",
    "section_execution": "执行建议",
    "implementation": "实施内容",
    "precautions": "注意事项",
    "section_references": "参考文献",
}


EN_UI = {
    "eyebrow": "ECONOMIC BENEFIT EXAMPLE",
    "example_scenario": "Example scenario",
    "detected_density": "Detected density",
    "untreated_yield_loss": "Yield loss without control",
    "treatment_recommendation": "Preset risk tier",
    "profit_change": "Conditional value of density-guided testing",
    "section_profit": "Two benefit comparisons",
    "without_test": "Without test strip",
    "with_test": "With test strip and recommended treatment",
    "season_profit": "Estimated profit per season",
    "remaining_loss": "Remaining crop loss",
    "treatment_cost": "Treatment cost",
    "test_cost": "Test-strip cost",
    "program_benefit": "Net benefit of the combined testing-and-control program",
    "detection_value": "Conditional incremental value of testing and tiered decisions",
    "incremental_cost": "Incremental cost",
    "roi": "ROI",
    "roi_not_applicable": "Not applicable (incremental cost is not positive)",
    "detection_costs": "Detection-method cost comparison",
    "section_loss": "Net benefit, break-even, and sensitivity",
    "legend_low": "Low tier",
    "legend_middle": "Medium tier",
    "legend_high": "High tier",
    "current_input": "Current input",
    "section_plans": "Preset tiers and economic comparison",
    "current_density": "Current density",
    "avoided_loss": "Estimated crop loss avoided",
    "preset_strategy": "Preset demonstration strategy",
    "economic_best": "Highest net income under current parameters",
    "option_profit": "Expected profit after testing",
    "difference_from_preset": "Versus preset strategy",
    "effect_scope": "Effect applicability",
    "sensitivity": "One-way sensitivity of key parameters",
    "section_execution": "Implementation guidance",
    "implementation": "Implementation steps",
    "precautions": "Precautions",
    "section_references": "References",
}


def _money(value: float, report: dict[str, Any]) -> str:
    scenario = report["scenario"]
    return f"{value:,.2f} {scenario['currency']}/{scenario['area_unit']}"


def _signed_money(value: float, report: dict[str, Any]) -> str:
    scenario = report["scenario"]
    return (
        f"{value:+,.2f} {scenario['currency']}/{scenario['area_unit']}"
        if value != 0
        else f"0.00 {scenario['currency']}/{scenario['area_unit']}"
    )


def _format_roi(value: float | None) -> str:
    return "不适用" if value is None else f"{value:.2%}"


def _format_roots(roots: list[float]) -> str:
    if not roots:
        return "文献密度范围内无严格零点；方案切换处另有收益跳变"
    return "、".join(f"{value:.2f} J2/100 cm³" for value in roots)


def _display_unit(text: str) -> str:
    """Use typographic superscripts in user-facing report text."""

    return text.replace("cm^3", "cm³")


def _english_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return the config-backed English view without changing numeric values."""

    localized = deepcopy(report)
    translations = localized.pop("translations")
    localized["report_title"] = "Nematode Test-Strip Economic Benefit Simulation"
    localized["report_note"] = (
        "This example reports both the combined value of testing plus treatment "
        "against no control and the conditional value of density-guided decisions "
        "against uniform control."
    )
    localized["scenario"].update(translations["scenario"])
    localized["scenario"]["scenario_status"] = "Example scenario"
    localized["thresholds"]["plain_language_note"] = translations["threshold_note"]
    localized["economics"]["without_test_no_control"]["name"] = "No control treatment"
    localized["economics"]["without_test_uniform_control"].update(
        translations["uniform_control"]
    )
    localized["diagnosis"].update(translations["diagnosis"])
    for plan in localized["treatment_options"]:
        plan.update(plan.pop("en"))
    for item in localized["detection_cost_comparison"]["items"]:
        item["method"] = item.pop("method_en")
        item["basis"] = item.pop("basis_en")
    localized["detection_cost_comparison"]["price_summary"] = localized[
        "detection_cost_comparison"
    ].pop("price_summary_en")
    localized["detection_cost_comparison"]["comparison_basis"] = localized[
        "detection_cost_comparison"
    ].pop("comparison_basis_en")
    for row in localized["sensitivity_analysis"]:
        row["parameter"] = row.pop("parameter_en")
        row["scope"] = row.pop("scope_en")
        row["change"] = row.pop("change_en")
    for warning in localized["diagnosis"]["effect_scope_warnings"]:
        warning["role"] = warning.pop("role_en")
        warning["treatment"] = warning.pop("treatment_en")
    localized["assumptions"] = translations["assumptions"]
    localized["source_note"] = translations["source_note"]
    return localized


def _plan_payload(
    key: str,
    label: str,
    label_en: str,
    plan: Treatment,
    density_range: str,
    outcome: Any,
    result: Result,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "density_range": density_range,
        "name": plan.name,
        "application_rate": plan.application_rate,
        "cost_per_ha": plan.cost_per_ha,
        "expected_avoided_loss_fraction": plan.avoided_loss_fraction,
        "effect_model": plan.effect_model,
        "effect_reference_density": plan.effect_reference_density,
        "population_reduction_fraction": plan.population_reduction_fraction,
        "study_density_min": plan.study_density_min,
        "study_density_max": plan.study_density_max,
        "management_support_max": plan.management_support_max,
        "effect_basis_note": _display_unit(plan.effect_basis_note),
        "overview": _display_unit(plan.plan_overview),
        "actions": [_display_unit(item) for item in plan.recommended_actions],
        "precautions": [_display_unit(item) for item in plan.precautions],
        "net_income_with_test_per_ha": outcome.net_income_with_test,
        "difference_from_preset_per_ha": outcome.difference_from_preset,
        "is_preset": key == result.treatment_key,
        "is_economic_best": key == result.economic_best_key,
        "en": {
            "label": label_en,
            "name": plan.name_en,
            "application_rate": plan.application_rate_en,
            "effect_basis_note": _display_unit(plan.effect_basis_note_en),
            "overview": _display_unit(plan.plan_overview_en),
            "actions": [_display_unit(item) for item in plan.recommended_actions_en],
            "precautions": [_display_unit(item) for item in plan.precautions_en],
        },
    }


def _loss_reduction_at_density(density: float, model: Model) -> float:
    """Value of untreated crop loss avoided by the test-guided treatment."""

    _, guided_plan = choose_treatment(density, model)
    gross_loss = (
        model.baseline_yield_kg_per_ha
        * model.price_per_kg
        * (1.0 - relative_yield_fraction(density, model))
    )
    return gross_loss * guided_plan.avoided_loss_fraction


def _discount_summary(test_cost: float, laboratory_costs: list[float]) -> tuple[str, str]:
    discounts = [1.0 - test_cost / cost for cost in laboratory_costs if cost > 0]
    if discounts and min(discounts) >= 0:
        low = round(min(discounts) * 100)
        high = round(max(discounts) * 100)
        return (
            f"本团队试纸成本比所列实验室公开收费低约{low}%–{high}%，且操作更为简便。",
            f"Our team's test strip costs approximately {low}%–{high}% less than the listed public laboratory fees and is simpler to operate.",
        )
    return (
        "当前试纸成本并非低于所有列示实验室收费，请逐项比较。",
        "The current test-strip cost is not lower than every listed laboratory fee; compare the entries individually.",
    )


def _detection_cost_payload(model: Model) -> dict[str, Any]:
    settings = model.detection_cost_comparison
    laboratory_costs = [
        method.fee_per_sample_eur * settings.samples_per_ha
        for method in settings.methods
    ]
    summary, summary_en = _discount_summary(model.test_cost_per_ha, laboratory_costs)
    items = [
        {
            "method": settings.project_method_name,
            "method_en": settings.project_method_name_en,
            "cost_per_ha": model.test_cost_per_ha,
            "basis": "团队定价，EUR/ha",
            "basis_en": "Team pricing assumption, EUR/ha",
            "featured": True,
        }
    ]
    for method, cost in zip(settings.methods, laboratory_costs):
        items.append(
            {
                "method": method.name,
                "method_en": method.name_en,
                "cost_per_ha": cost,
                "basis": method.basis,
                "basis_en": method.basis_en,
                "featured": False,
            }
        )
    sample_text = f"{settings.samples_per_ha:g}份代表性样品"
    sample_text_en = (
        f"{settings.samples_per_ha:g} representative sample"
        + ("" if settings.samples_per_ha == 1 else "s")
    )
    return {
        "items": items,
        "samples_per_ha": settings.samples_per_ha,
        "price_summary": summary,
        "price_summary_en": summary_en,
        "comparison_basis": f"实验室费用按每公顷提交{sample_text}换算；{settings.excluded_costs}",
        "comparison_basis_en": f"Laboratory fees assume {sample_text_en} submitted per hectare; {settings.excluded_costs_en}",
    }


def _replace_selected_treatment(
    model: Model, key: str, treatment: Treatment
) -> Model:
    changes = {key: treatment}
    if key == "middle":
        changes["without_test"] = replace(
            model.without_test,
            cost_per_ha=treatment.cost_per_ha,
            avoided_loss_fraction=treatment.avoided_loss_fraction,
            population_reduction_fraction=treatment.population_reduction_fraction,
            effect_reference_density=treatment.effect_reference_density,
        )
    return replace(model, **changes)


def _replace_uniform_control(model: Model, treatment: Treatment) -> Model:
    """Change the comparator while keeping its shared medium-tier inputs aligned."""

    middle = replace(
        model.middle,
        cost_per_ha=treatment.cost_per_ha,
        avoided_loss_fraction=treatment.avoided_loss_fraction,
        population_reduction_fraction=treatment.population_reduction_fraction,
        effect_reference_density=treatment.effect_reference_density,
    )
    return replace(model, without_test=treatment, middle=middle)


def _sensitivity_payload(model: Model, result: Result) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(
        parameter: str,
        parameter_en: str,
        scope: str,
        scope_en: str,
        change: str,
        change_en: str,
        scenario: Model,
    ) -> None:
        scenario_result = evaluate(result.density, scenario)
        rows.append(
            {
                "parameter": parameter,
                "parameter_en": parameter_en,
                "scope": scope,
                "scope_en": scope_en,
                "change": change,
                "change_en": change_en,
                "program_net_benefit_vs_no_control": scenario_result.program_net_benefit_vs_no_control,
                "detection_net_benefit_vs_uniform": scenario_result.detection_net_benefit_vs_uniform,
                "detection_worthwhile": scenario_result.detection_net_benefit_vs_uniform > 0,
            }
        )

    for multiplier in model.sensitivity.test_cost_multipliers:
        add(
            "试纸成本",
            "Test-strip cost",
            "检测后预设策略",
            "Preset strategy after testing",
            f"×{multiplier:g}",
            f"×{multiplier:g}",
            replace(model, test_cost_per_ha=model.test_cost_per_ha * multiplier),
        )
    for multiplier in model.sensitivity.treatment_cost_multipliers:
        selected = replace(
            result.treatment,
            cost_per_ha=result.treatment.cost_per_ha * multiplier,
        )
        if result.treatment_key == "middle":
            add(
                "处理成本",
                "Treatment cost",
                "检测后中等级方案与未检测统一处理基线（共享参数）",
                "Guided medium-tier plan and uniform-control baseline (shared parameter)",
                f"×{multiplier:g}",
                f"×{multiplier:g}",
                _replace_selected_treatment(model, result.treatment_key, selected),
            )
        else:
            add(
                "处理成本",
                "Treatment cost",
                f"检测后预设方案：{result.treatment.name}",
                f"Preset guided plan: {result.treatment.name_en}",
                f"×{multiplier:g}",
                f"×{multiplier:g}",
                _replace_selected_treatment(model, result.treatment_key, selected),
            )
            uniform = replace(
                model.without_test,
                cost_per_ha=model.without_test.cost_per_ha * multiplier,
            )
            add(
                "处理成本",
                "Treatment cost",
                f"未检测统一处理基线：{model.without_test.name}",
                f"Uniform-control baseline: {model.without_test.name_en}",
                f"×{multiplier:g}",
                f"×{multiplier:g}",
                _replace_uniform_control(model, uniform),
            )
    for multiplier in model.sensitivity.efficacy_multipliers:
        selected_effect = min(
            1.0, result.treatment.avoided_loss_fraction * multiplier
        )
        selected = replace(
            result.treatment,
            avoided_loss_fraction=selected_effect,
            population_reduction_fraction=None,
            effect_reference_density=None,
        )
        if result.treatment_key == "middle":
            add(
                "固定避免损失比例",
                "Fixed loss-avoidance fraction",
                "检测后中等级方案与未检测统一处理基线（共享参数）",
                "Guided medium-tier plan and uniform-control baseline (shared parameter)",
                f"×{multiplier:g}",
                f"×{multiplier:g}",
                _replace_selected_treatment(model, result.treatment_key, selected),
            )
        else:
            add(
                "固定避免损失比例",
                "Fixed loss-avoidance fraction",
                f"检测后预设方案：{result.treatment.name}",
                f"Preset guided plan: {result.treatment.name_en}",
                f"×{multiplier:g}",
                f"×{multiplier:g}",
                _replace_selected_treatment(model, result.treatment_key, selected),
            )
            uniform_effect = min(
                1.0, model.without_test.avoided_loss_fraction * multiplier
            )
            uniform = replace(
                model.without_test,
                avoided_loss_fraction=uniform_effect,
                population_reduction_fraction=None,
                effect_reference_density=None,
            )
            add(
                "固定避免损失比例",
                "Fixed loss-avoidance fraction",
                f"未检测统一处理基线：{model.without_test.name}",
                f"Uniform-control baseline: {model.without_test.name_en}",
                f"×{multiplier:g}",
                f"×{multiplier:g}",
                _replace_uniform_control(model, uniform),
            )
    for multiplier in model.sensitivity.crop_price_multipliers:
        add(
            "番茄价格",
            "Tomato price",
            "所有比较方案",
            "All compared strategies",
            f"×{multiplier:g}",
            f"×{multiplier:g}",
            replace(model, price_per_kg=model.price_per_kg * multiplier),
        )
    return rows


def _outside_study_density(treatment: Treatment, density: float) -> bool:
    return (
        treatment.study_density_min is not None
        and density < treatment.study_density_min
    ) or (
        treatment.study_density_max is not None
        and density > treatment.study_density_max
    )


def _effect_scope_warnings(model: Model, result: Result) -> list[dict[str, Any]]:
    participants = []
    shared_scope = (
        model.middle.study_density_min == model.without_test.study_density_min
        and model.middle.study_density_max == model.without_test.study_density_max
    )
    for outcome in result.plan_outcomes:
        role = "经济比较备选方案"
        role_en = "Alternative in economic comparison"
        if outcome.key == result.treatment_key:
            role = "检测后预设方案"
            role_en = "Preset guided plan"
        if outcome.key == "middle" and shared_scope:
            role += "与未检测统一处理基线（共享）"
            role_en += " and uniform-control baseline (shared)"
        participants.append((role, role_en, outcome.treatment))
    if not shared_scope:
        participants.append(
            ("未检测统一处理基线", "Uniform-control baseline", model.without_test)
        )
    return [
        {
            "role": role,
            "role_en": role_en,
            "treatment": treatment.name,
            "treatment_en": treatment.name_en,
            "study_density_min": treatment.study_density_min,
            "study_density_max": treatment.study_density_max,
        }
        for role, role_en, treatment in participants
        if _outside_study_density(treatment, result.density)
    ]


def _support_range_text(warning: dict[str, Any], *, english: bool = False) -> str:
    minimum = warning["study_density_min"]
    maximum = warning["study_density_max"]
    if minimum is not None and maximum is not None:
        return (
            f"approximately {minimum:g}–{maximum:g} J2/100 cm³"
            if english
            else f"约{minimum:g}–{maximum:g} J2/100 cm³"
        )
    if minimum is not None:
        return (
            f"approximately {minimum:g} J2/100 cm³ and above"
            if english
            else f"约{minimum:g} J2/100 cm³及以上"
        )
    return (
        f"approximately {maximum:g} J2/100 cm³ and below"
        if english
        else f"约{maximum:g} J2/100 cm³及以下"
    )


def _comparison_effect_assumption(
    model: Model, result: Result, *, english: bool = False
) -> str:
    if result.treatment_key == "middle":
        prefix = (
            "Guided medium-tier plan and uniform-control baseline share: "
            if english
            else "检测后中等级方案与未检测统一处理基线共享："
        )
        note = (
            model.middle.effect_basis_note_en
            if english
            else model.middle.effect_basis_note
        )
        return _display_unit(prefix + note)
    guided_prefix = "Preset guided plan: " if english else "检测后预设方案："
    uniform_prefix = (
        "Uniform-control baseline: " if english else "未检测统一处理基线："
    )
    guided_note = (
        result.treatment.effect_basis_note_en
        if english
        else result.treatment.effect_basis_note
    )
    uniform_note = (
        model.without_test.effect_basis_note_en
        if english
        else model.without_test.effect_basis_note
    )
    return _display_unit(
        f"{guided_prefix}{guided_note} {uniform_prefix}{uniform_note}"
    )


def build_diagnostic_report(model: Model, result: Result) -> dict[str, Any]:
    potential_revenue = model.baseline_yield_kg_per_ha * model.price_per_kg
    without_test_no_control_residual_loss = result.gross_loss
    without_test_uniform_residual_loss = result.gross_loss * (
        1.0 - model.without_test.avoided_loss_fraction
    )
    with_test_residual_loss = result.gross_loss * (
        1.0 - result.treatment.avoided_loss_fraction
    )
    sampled_densities = {model.max_density * index / 200.0 for index in range(201)}
    sampled_densities.update(
        {
            model.tolerance_density,
            model.middle_from_density - 1e-6,
            model.middle_from_density,
            model.high_from_density - 1e-6,
            model.high_from_density,
            500.0,
            model.high.management_support_max or model.max_density,
        }
    )
    curve_points = []
    for density in sorted(
        value for value in sampled_densities if 0.0 <= value <= model.max_density
    ):
        curve_points.append(
            {
                "density": density,
                "expected_reduced_loss_per_ha": _loss_reduction_at_density(density, model),
                "program_net_benefit_vs_no_control": evaluate(
                    density, model
                ).program_net_benefit_vs_no_control,
                "detection_net_benefit_vs_uniform": evaluate(
                    density, model
                ).detection_net_benefit_vs_uniform,
            }
        )
    no_control_roots, no_control_jumps = break_even_analysis(
        model, baseline="no_control"
    )
    uniform_roots, uniform_jumps = break_even_analysis(
        model, baseline="uniform_control"
    )
    outcome_by_key = {item.key: item for item in result.plan_outcomes}
    plan_payloads = [
        _plan_payload(
            "low",
            "低",
            "Low",
            model.low,
            f"d < {model.middle_from_density:g}",
            outcome_by_key["low"],
            result,
        ),
        _plan_payload(
            "middle",
            "中",
            "Medium",
            model.middle,
            f"{model.middle_from_density:g} ≤ d < {model.high_from_density:g}",
            outcome_by_key["middle"],
            result,
        ),
        _plan_payload(
            "high",
            "高",
            "High",
            model.high,
            f"{model.high_from_density:g} ≤ d ≤ {model.max_density:g}",
            outcome_by_key["high"],
            result,
        ),
    ]
    effect_scope_warnings = _effect_scope_warnings(model, result)
    management_max = model.high.management_support_max
    return {
        "schema_version": 9,
        "report_title": "线虫检测试纸经济效益模拟报告",
        "report_note": (
            "模拟用户在种植前使用试纸获得线虫密度，并根据试纸给出的分级防治建议采取相应措施后，"
            "分别比较整套检测与防治项目相对无防治的收益，以及检测分级相对统一处理的条件增量价值。"
        ),
        "scenario": {
            "crop": model.crop,
            "country": model.country,
            "nematode": model.nematode,
            "detection_timing": model.detection_timing,
            "density_unit": _display_unit(model.density_unit),
            "area_unit": model.area_unit,
            "currency": model.currency,
            "scenario_status": "示例场景",
        },
        "translations": {
            "scenario": {
                "crop": model.crop_en,
                "country": model.country_en,
                "nematode": model.nematode_en,
                "detection_timing": model.detection_timing_en,
            },
            "threshold_note": (
                f"Yield loss may begin above approximately {model.tolerance_density:g} J2/100 cm³ soil. "
                f"The fixed {model.middle_from_density:g}/{model.high_from_density:g} thresholds form a preset demonstration policy, not an economic optimiser."
            ),
            "uniform_control": {
                "name": model.without_test.name_en,
                "note": _display_unit(model.without_test.evidence_note_en),
            },
            "diagnosis": {
                "band": {"低": "Low", "中": "Medium", "高": "High"}[result.band],
                "treatment": result.treatment.name_en,
                "treatment_title": result.treatment.name_en,
                "treatment_dose": result.treatment.application_rate_en,
                "economic_best_treatment": result.economic_best_treatment.name_en,
            },
            "assumptions": {
                "test_cost": "Test-strip cost is a team pricing assumption, not an observed market price.",
                "known_density": "Input density is treated as known and accurate; detection limit, sensitivity, specificity, sampling error, and misclassification are not modelled.",
                "fixed_effect": _comparison_effect_assumption(
                    model, result, english=True
                ),
                "cross_study": _display_unit(model.source_note_en),
                "conditional_value": "The comparison with uniform control is conditional on the current density. Without a prior density distribution and test error, it is not an ex-ante expected value of information.",
            },
            "source_note": _display_unit(model.source_note_en),
        },
        "input": {
            "density": result.density,
            "within_literature_density_range": result.density <= model.max_density,
        },
        "thresholds": {
            "expected_loss_begins_near": model.tolerance_density,
            "action_from_density": model.middle_from_density,
            "high_from_density": model.high_from_density,
            "biosolarization_supported_to": management_max,
            "maximum_supported_density": model.max_density,
            "plain_language_note": (
                f"约{model.tolerance_density:g} J2/100 cm³以上可能开始出现损失；"
                f"本示例考虑文献不确定性后，从{model.middle_from_density:g}开始给出"
                f"专项处理建议，并在{model.high_from_density:g}以上切换到高等级方案。"
                "这些阈值是预设演示策略，不会随成本或防效自动优化。"
            ),
        },
        "economics": {
            "baseline_yield_kg_per_ha": model.baseline_yield_kg_per_ha,
            "price_per_kg": model.price_per_kg,
            "potential_revenue_per_ha": potential_revenue,
            "baseline_production_cost_per_ha": model.baseline_production_cost_per_ha,
            "test_cost_per_ha": model.test_cost_per_ha,
            "test_cost_status": model.test_cost_status,
            "without_test_no_control": {
                "name": "未采取防治手段",
                "cost_per_ha": 0.0,
                "expected_avoided_loss_fraction": 0.0,
            },
            "without_test_uniform_control": {
                "name": model.without_test.name,
                "cost_per_ha": model.without_test.cost_per_ha,
                "expected_avoided_loss_fraction": model.without_test.avoided_loss_fraction,
                "note": _display_unit(model.without_test.evidence_note),
            },
        },
        "diagnosis": {
            "band": result.band,
            "treatment": result.treatment.name,
            "treatment_title": result.treatment.name,
            "treatment_dose": result.treatment.application_rate,
            "treatment_cost_per_ha": result.treatment.cost_per_ha,
            "expected_avoided_loss_fraction": result.treatment.avoided_loss_fraction,
            "relative_yield_fraction": result.relative_yield_fraction,
            "yield_loss_fraction": result.yield_loss_fraction,
            "gross_loss_per_ha": result.gross_loss,
            "without_test_no_control_residual_loss_per_ha": (
                without_test_no_control_residual_loss
            ),
            "without_test_uniform_residual_loss_per_ha": (
                without_test_uniform_residual_loss
            ),
            "with_test_residual_loss_per_ha": with_test_residual_loss,
            "without_test_uniform_treatment_cost_per_ha": model.without_test.cost_per_ha,
            "test_cost_per_ha": model.test_cost_per_ha,
            "net_income_without_test_no_control_per_ha": result.net_income_without_test,
            "net_income_without_test_uniform_per_ha": (
                result.net_income_without_test_uniform
            ),
            "net_income_with_test_per_ha": result.net_income_with_test,
            "profit_change_per_ha": result.detection_net_benefit_vs_uniform,
            "program_incremental_cost_vs_no_control": result.program_incremental_cost_vs_no_control,
            "program_net_benefit_vs_no_control": result.program_net_benefit_vs_no_control,
            "program_roi_vs_no_control": result.program_roi_vs_no_control,
            "detection_incremental_cost_vs_uniform": result.detection_incremental_cost_vs_uniform,
            "detection_net_benefit_vs_uniform": result.detection_net_benefit_vs_uniform,
            "detection_roi_vs_uniform": result.detection_roi_vs_uniform,
            "economic_best_key": result.economic_best_key,
            "economic_best_treatment": result.economic_best_treatment.name,
            "economic_best_net_income_per_ha": result.economic_best_net_income,
            "preset_opportunity_cost_per_ha": result.preset_opportunity_cost,
            "expected_reduced_loss_per_ha": (
                without_test_no_control_residual_loss - with_test_residual_loss
            ),
            "expected_reduced_loss_fraction": result.treatment.avoided_loss_fraction,
            "effect_scope_warning": bool(effect_scope_warnings),
            "effect_scope_warnings": effect_scope_warnings,
            "above_biosolarization_support": bool(
                management_max is not None and result.density > management_max
            ),
        },
        "net_benefit_curve": {
            "comparison_no_control": "检测并按预设策略处理 vs 未采取防治",
            "comparison_uniform": "检测并按预设策略处理 vs 未检测统一处理",
            "value_definition": "扣除检测与处理成本后的净收益",
            "points": curve_points,
        },
        "break_even": {
            "program_vs_no_control": {
                "baseline": "未采取防治",
                "roots": no_control_roots,
                "threshold_jumps": no_control_jumps,
            },
            "detection_vs_uniform": {
                "baseline": "未检测统一处理",
                "roots": uniform_roots,
                "threshold_jumps": uniform_jumps,
            },
        },
        "detection_cost_comparison": _detection_cost_payload(model),
        "sensitivity_analysis": _sensitivity_payload(model, result),
        "treatment_options": plan_payloads,
        "assumptions": {
            "test_cost": "试纸成本为团队定价，不是公开市场实测售价。",
            "known_density": "输入线虫密度被视为已知且准确；本模型未计检出限、灵敏度、特异性、采样误差和误分级。",
            "fixed_effect": _comparison_effect_assumption(model, result),
            "cross_study": _display_unit(model.source_note),
            "conditional_value": "相对统一处理的结果是给定当前密度后的条件增量价值；没有密度先验分布和检测误差时，不能解释为种植前的期望信息价值。",
        },
        "references": list(REFERENCES),
        "source_note": _display_unit(model.source_note),
    }


def format_text_report(report: dict[str, Any]) -> str:
    s = report["scenario"]
    d = report["diagnosis"]
    e = report["economics"]
    t = report["thresholds"]
    lines = [
        report["report_title"],
        "=" * 48,
        report["report_note"],
        f"标签：示例场景；{s['country']}；{s['crop']}；{s['nematode']}；{s['currency']}/{s['area_unit']}",
        "",
        "一、两种收益比较",
        f"  检测密度：{report['input']['density']:g} {s['density_unit']}",
        f"  如不采取防治手段，预计产量损失：{d['yield_loss_fraction']:.2%}",
        f"  处理建议：{d['band']}等级；{d['treatment']}",
        f"  未检测且未采取防治手段的预计利润：{_money(d['net_income_without_test_no_control_per_ha'], report)}",
        f"  未检测但采用统一处理的预计利润：{_money(d['net_income_without_test_uniform_per_ha'], report)}",
        f"  使用试纸后的预计利润：{_money(d['net_income_with_test_per_ha'], report)}",
        f"  整套检测与防治项目净收益（相对未采取防治）：{_signed_money(d['program_net_benefit_vs_no_control'], report)}",
        f"    增量成本：{_signed_money(d['program_incremental_cost_vs_no_control'], report)}；ROI：{_format_roi(d['program_roi_vs_no_control'])}",
        f"  检测信息与分级决策的条件增量价值（相对未检测统一处理）：{_signed_money(d['detection_net_benefit_vs_uniform'], report)}",
        f"    增量成本：{_signed_money(d['detection_incremental_cost_vs_uniform'], report)}；ROI：{_format_roi(d['detection_roi_vs_uniform'])}",
        "",
        f"  检测成本对比（每公顷{report['detection_cost_comparison']['samples_per_ha']:g}份代表性样品）",
        *(
            f"  - {item['method']}：{item['cost_per_ha']:.2f} EUR/ha（{item['basis']}）"
            for item in report["detection_cost_comparison"]["items"]
        ),
        f"  {report['detection_cost_comparison']['comparison_basis']}",
        "",
        "二、净收益、盈亏平衡与敏感性",
        f"  {t['plain_language_note']}",
        "  整套项目收益不能全部归因于检测；检测的条件增量价值使用统一处理作为基线。",
        f"  相对无防治的严格盈亏平衡密度：{_format_roots(report['break_even']['program_vs_no_control']['roots'])}",
        "  相对无防治的分级阈值收益跳变："
        + "; ".join(
            f"{threshold:g} J2/100 cm³：{_signed_money(left, report)} → {_signed_money(right, report)}"
            for threshold, left, right in report["break_even"]["program_vs_no_control"]["threshold_jumps"]
        ),
        f"  相对统一处理的严格盈亏平衡密度：{_format_roots(report['break_even']['detection_vs_uniform']['roots'])}",
        "  相对统一处理的分级阈值收益跳变："
        + "; ".join(
            f"{threshold:g} J2/100 cm³：{_signed_money(left, report)} → {_signed_money(right, report)}"
            for threshold, left, right in report["break_even"]["detection_vs_uniform"]["threshold_jumps"]
        ),
        "",
        "  单因素敏感性（其余参数保持不变；不是置信区间）",
    ]
    for row in report["sensitivity_analysis"]:
        lines.append(
            f"  - {row['parameter']} {row['change']}；作用方案：{row['scope']}；"
            f"整套项目净收益（相对无防治）={_signed_money(row['program_net_benefit_vs_no_control'], report)}；"
            f"检测条件增量价值（相对统一处理）={_signed_money(row['detection_net_benefit_vs_uniform'], report)}；"
            f"检测是否增益：{'是' if row['detection_worthwhile'] else '否'}"
        )
    if d["effect_scope_warnings"]:
        lines.extend(["", "  防效外推提示：以下参与经济比较的方案超出来源研究密度支持范围；固定防效仅作为演示假设。"])
        for warning in d["effect_scope_warnings"]:
            lines.append(
                f"  - {warning['role']}：{warning['treatment']}；"
                f"研究密度支持为{_support_range_text(warning)}；"
                f"本次输入为{report['input']['density']:g} J2/100 cm³。"
            )
    if d["above_biosolarization_support"]:
        lines.append(
            f"  高密度提示：本次输入超过约{t['biosolarization_supported_to']:g} J2/100 cm³，"
            "高等级方案超出来源文献估算的番茄经济管理范围；应另行评估抗性砧木、轮作或调整作物。"
        )
    lines.extend(["", "三、预设分级与经济比较"])
    for plan in report["treatment_options"]:
        selected = "【当前密度】" if plan["label"] == d["band"] else ""
        lines.append(
            f"  {plan['label']}等级 {selected} {plan['density_range']}：{plan['name']}；"
            f"成本={_money(plan['cost_per_ha'], report)}；"
            f"预计避免作物损失={plan['expected_avoided_loss_fraction']:.2%}；"
            f"检测后预计利润={_money(plan['net_income_with_test_per_ha'], report)}；"
            f"相对预设方案={_signed_money(plan['difference_from_preset_per_ha'], report)}"
        )
    lines.extend(["", "四、执行建议"])
    selected_plan = next(
        plan for plan in report["treatment_options"] if plan["label"] == d["band"]
    )
    lines.append(f"  {selected_plan['label']}等级｜{selected_plan['name']}")
    lines.append(f"    {selected_plan['overview']}")
    lines.extend(f"    - {item}" for item in selected_plan["actions"])
    lines.extend(f"    - 注意：{item}" for item in selected_plan["precautions"])
    lines.append(f"    - 效果换算：{selected_plan['effect_basis_note']}")
    lines.extend(["", "  关键假设"])
    lines.extend(f"    - {value}" for value in report["assumptions"].values())
    lines.extend(["", "五、参考文献"])
    for index, item in enumerate(report["references"], 1):
        lines.append(f"  [{index}] {item['citation']} {item['url']}")
    return "\n".join(lines) + "\n"


def _net_benefit_curve_svg(
    report: dict[str, Any], *, language: str = "zh-CN"
) -> str:
    points = [
        point
        for point in report["net_benefit_curve"]["points"]
        if point["density"] <= 500.0
    ]
    input_density = report["input"]["density"]
    diagnosis = report["diagnosis"]
    width, height = 900.0, 330.0
    left, right, top, bottom = 82.0, 24.0, 20.0, 50.0
    plot_w, plot_h = width - left - right, height - top - bottom
    values = [
        value
        for point in points
        for value in (
            point["program_net_benefit_vs_no_control"],
            point["detection_net_benefit_vs_uniform"],
        )
    ]
    max_abs = max([abs(value) for value in values] + [1.0])
    raw_step = max_abs / 2.0
    magnitude = 10.0 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude
    step = magnitude if normalized <= 1 else 2 * magnitude if normalized <= 2 else 5 * magnitude if normalized <= 5 else 10 * magnitude
    axis_max = step * 2.0
    axis_min = -axis_max

    def sx(value: float) -> float:
        return left + plot_w * value / 500.0

    def sy(value: float) -> float:
        return top + plot_h * (axis_max - value) / (axis_max - axis_min)

    grid = []
    for value in (axis_min, -axis_max / 2, 0.0, axis_max / 2, axis_max):
        y = sy(value)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" stroke="#dbe4de" stroke-width="1" />'
            f'<text x="{left-10}" y="{y+4:.2f}" text-anchor="end">{value:,.0f}</text>'
        )
    x_ticks = []
    for tick in (0.0, 10.0, 50.0, 80.0, 150.0, 300.0, 500.0):
        x_ticks.append(
            f'<text x="{sx(tick):.2f}" y="{height-bottom+22}" text-anchor="middle">{tick:g}</text>'
        )
    thresholds = report["thresholds"]
    zones = (
        (0.0, thresholds["action_from_density"], "#e8f5ed"),
        (thresholds["action_from_density"], thresholds["high_from_density"], "#fff4d6"),
        (thresholds["high_from_density"], 500.0, "#fbe9e5"),
    )
    zone_markup = "".join(
        f'<rect x="{sx(start):.2f}" y="{top:.2f}" width="{sx(end)-sx(start):.2f}" height="{plot_h:.2f}" fill="{colour}" />'
        for start, end, colour in zones
    )

    def polyline(field: str, colour: str) -> str:
        bands = (
            [p for p in points if p["density"] < thresholds["action_from_density"]],
            [p for p in points if thresholds["action_from_density"] <= p["density"] < thresholds["high_from_density"]],
            [p for p in points if p["density"] >= thresholds["high_from_density"]],
        )
        parts = []
        for band in bands:
            if len(band) < 2:
                continue
            coordinates = " ".join(
                f"{sx(point['density']):.2f},{sy(point[field]):.2f}"
                for point in band
            )
            parts.append(
                f'<polyline points="{coordinates}" fill="none" stroke="{colour}" '
                'stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round" />'
            )
        return "".join(parts)

    markers = ""
    if input_density <= 500.0:
        x = sx(input_density)
        for value, colour in (
            (diagnosis["program_net_benefit_vs_no_control"], "#176744"),
            (diagnosis["detection_net_benefit_vs_uniform"], "#b76518"),
        ):
            markers += f'<circle cx="{x:.2f}" cy="{sy(value):.2f}" r="4.5" fill="#fff" stroke="{colour}" stroke-width="2.5" />'
    if language == "en":
        aria = "Net benefit of test-guided treatment against two baselines"
        x_label = "Nematode density (J2/100 cm³ soil)"
        y_label = "Net benefit after costs (EUR/ha)"
    else:
        aria = "检测后预设分级处理相对两种基线的净收益"
        x_label = "线虫密度（J2/100 cm³ soil）"
        y_label = "扣除成本后的净收益（EUR/ha）"
    return f"""
<svg class="loss-chart" viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{aria}">
  {zone_markup}{''.join(grid)}{''.join(x_ticks)}
  <line x1="{left}" y1="{sy(0):.2f}" x2="{width-right}" y2="{sy(0):.2f}" stroke="#617269" stroke-width="1.5" />
  {polyline('program_net_benefit_vs_no_control', '#176744')}
  {polyline('detection_net_benefit_vs_uniform', '#b76518')}
  {markers}
  <text x="{left + plot_w/2:.2f}" y="{height-2}" text-anchor="middle">{x_label}</text>
  <text x="17" y="{top+plot_h/2:.2f}" text-anchor="middle" transform="rotate(-90 17 {top+plot_h/2:.2f})">{y_label}</text>
</svg>"""


def format_html_report(
    report: dict[str, Any], *, language: str = "zh-CN"
) -> str:
    if language not in {"zh-CN", "en"}:
        raise ValueError("language 必须是 zh-CN 或 en")
    english = language == "en"
    if english:
        report = _english_report(report)
    ui = EN_UI if english else ZH_UI
    s = report["scenario"]
    d = report["diagnosis"]
    e = report["economics"]
    t = report["thresholds"]
    colon = ": " if english else "："
    profit_class = "gain" if d["profit_change_per_ha"] >= 0 else "loss"

    def plan_name_markup(plan: dict[str, Any]) -> str:
        rate = plan.get("application_rate", "")
        return html.escape(plan["name"]) + (
            f'<span class="plan-dose">{html.escape(rate)}</span>' if rate else ""
        )

    def roi_text(value: float | None) -> str:
        return ui["roi_not_applicable"] if value is None else f"{value:.2%}"

    treatment_cards = "".join(
        f"""<article class="plan-card {'selected' if plan['is_preset'] else ''}">
          {f'<span class="current-tag">{ui["current_density"]}</span>' if plan['is_preset'] else ''}
          <div class="plan-heading"><span class="grade grade-{plan['key']}">{plan['label']}</span>
          <span class="range">{html.escape(plan['density_range'])}</span></div>
          <h3>{plan_name_markup(plan)}</h3>
          <div class="plan-metrics"><span>{ui['treatment_cost']} <b>{_money(plan['cost_per_ha'], report)}</b></span>
          <span>{ui['avoided_loss']} <b>{plan['expected_avoided_loss_fraction']:.2%}</b></span>
          <span>{ui['option_profit']} <b>{_money(plan['net_income_with_test_per_ha'], report)}</b></span>
          <span>{ui['difference_from_preset']} <b>{_signed_money(plan['difference_from_preset_per_ha'], report)}</b></span></div>
          <div class="plan-flags">{'<span>'+ui['preset_strategy']+'</span>' if plan['is_preset'] else ''}{'<span>'+ui['economic_best']+'</span>' if plan['is_economic_best'] else ''}</div>
        </article>"""
        for plan in report["treatment_options"]
    )
    execution_cards = "".join(
        f"""<article class="execution-card">
          <div class="execution-title"><span class="grade grade-{plan['key']}">{plan['label']}</span>
          <div><h3>{plan_name_markup(plan)}</h3><span>{html.escape(plan['density_range'])}</span></div></div>
          <p>{html.escape(plan['overview'])}</p>
          <div class="expected">{ui['avoided_loss']}: <strong>{plan['expected_avoided_loss_fraction']:.2%}</strong>
          · {ui['treatment_cost']}: <strong>{_money(plan['cost_per_ha'], report)}</strong></div>
          <div class="plain-note"><strong>{ui['effect_scope']}：</strong>{html.escape(plan['effect_basis_note'])}</div>
          <h4>{ui['implementation']}</h4><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in plan['actions'])}</ul>
          <h4>{ui['precautions']}</h4><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in plan['precautions'])}</ul>
        </article>"""
        for plan in report["treatment_options"]
        if plan["is_preset"]
    )
    cost_cards = "".join(
        f"""<article class="cost-card {'featured' if item['featured'] else ''}">
          <div class="cost-method">{html.escape(item['method'])}</div>
          <div class="cost-value">{_money(item['cost_per_ha'], report)}</div>
        </article>"""
        for item in report["detection_cost_comparison"]["items"]
    )
    reference_items = "".join(
        f'<li><a href="{html.escape(item["url"], quote=True)}" target="_blank" '
        f'rel="noopener noreferrer">{html.escape(item["citation"])}</a></li>'
        for item in report["references"]
    )
    sensitivity_rows = "".join(
        f"<tr><td>{html.escape(row['parameter'])}</td><td>{html.escape(row['scope'])}</td>"
        f"<td>{html.escape(row['change'])}</td>"
        f"<td>{_signed_money(row['program_net_benefit_vs_no_control'], report)}</td>"
        f"<td>{_signed_money(row['detection_net_benefit_vs_uniform'], report)}</td>"
        f"<td>{'Yes' if english and row['detection_worthwhile'] else 'No' if english else '是' if row['detection_worthwhile'] else '否'}</td></tr>"
        for row in report["sensitivity_analysis"]
    )
    def root_text(roots: list[float]) -> str:
        if roots:
            return ", ".join(f"{value:.2f} J2/100 cm³" for value in roots)
        return (
            "No strict zero within the literature density range; inspect threshold jumps."
            if english
            else "文献密度范围内无严格零点；需同时查看固定分级切换造成的收益跳变。"
        )

    def jump_text(jumps: list[list[float]] | list[tuple[float, float, float]]) -> str:
        if not jumps:
            return "None" if english else "无"
        return "; ".join(
            f"{threshold:g} J2/100 cm³: {_signed_money(left, report)} → {_signed_money(right, report)}"
            for threshold, left, right in jumps
        )

    program_break_even = root_text(
        report["break_even"]["program_vs_no_control"]["roots"]
    )
    detection_break_even = root_text(
        report["break_even"]["detection_vs_uniform"]["roots"]
    )
    program_jumps = jump_text(
        report["break_even"]["program_vs_no_control"]["threshold_jumps"]
    )
    detection_jumps = jump_text(
        report["break_even"]["detection_vs_uniform"]["threshold_jumps"]
    )

    effect_warning_items = "".join(
        f"<li><strong>{html.escape(warning['role'])}{colon}{html.escape(warning['treatment'])}</strong>"
        + (
            f" — source-study density support is {html.escape(_support_range_text(warning, english=english))}; "
            f"the current input is {report['input']['density']:g} J2/100 cm³."
            if english
            else f"；配置记录的来源研究密度支持为{html.escape(_support_range_text(warning, english=english))}，"
            f"本次输入为{report['input']['density']:g} J2/100 cm³。"
        )
        + "</li>"
        for warning in d["effect_scope_warnings"]
    )
    if english:
        effect_warning = (
            '<div class="alert"><strong>Effect extrapolation:</strong> Every treatment '
            'participating in the comparison is checked. The following fixed '
            f'loss-avoidance value is extrapolated for this input:<ul>{effect_warning_items}</ul>'
            'These values are retained only as demonstration assumptions.</div>'
            if d["effect_scope_warning"]
            else ""
        )
        high_warning = (
            "<div class=\"alert danger\"><strong>High-density note:</strong> "
            f"The current input exceeds approximately {t['biosolarization_supported_to']:g} J2/100 cm³ soil. "
            "The selected high-tier treatment is beyond the tomato economic-management "
            "range estimated in the source study; also assess resistant rootstocks, "
            "crop rotation, or a change of crop.</div>"
            if d["above_biosolarization_support"]
            else ""
        )
        chart_current_note = (
            "The dot marks the current input."
            if report["input"]["density"] <= 500.0
            else "The current input is beyond the displayed x-axis range, so no dot is shown."
        )
        chart_note = (
            "The green curve is the net benefit of the combined testing-and-control program "
            "against no control. The amber curve is the conditional incremental value of "
            "density-guided testing against uniform control. Both deduct test and treatment "
            f"costs. {chart_current_note} The x-axis ends at 500 J2/100 cm³ soil. "
            "The fixed tier changes create discontinuities; they are not automatically "
            "re-optimised when cost or efficacy parameters change."
        )
        language_css = """
body{font-family:Inter,"Segoe UI",Arial,sans-serif;line-height:1.6}
h1,h2{font-family:"Source Serif 4",Georgia,"Times New Roman",serif}
h1{font-size:clamp(2rem,3.7vw,3.05rem);max-width:930px}
.subtitle{max-width:930px;line-height:1.65}
.summary-card .label{font-size:.74rem;line-height:1.35;letter-spacing:.025em}
.summary-card .value{left:16px;right:16px;font-size:clamp(1.12rem,1.8vw,1.38rem);white-space:nowrap}
.summary-notes{left:16px;right:16px}.summary-notes>.muted{font-size:.78rem;white-space:nowrap}
h2{font-size:1.45rem}h3{font-size:1rem}
.strategy .income{font-size:clamp(1.18rem,2vw,1.58rem)}
.strategy-label{min-height:1.4em;white-space:nowrap;letter-spacing:.025em}
.sub-strategy h3{min-height:2.15em;line-height:1.35;margin-bottom:.15rem}.sub-strategy .income{margin-top:.1rem}.calc-table{font-size:.80rem}.calc-table td:first-child{white-space:nowrap}
.cost-method{min-height:4.5em;line-height:1.4}.cost-value{font-size:1.14rem}
.plan-card h3{min-height:3em}.plan-dose{display:block}.plan-metrics{font-size:.82rem}.plan-metrics span{display:flex;justify-content:space-between;gap:10px}.plan-metrics b{white-space:nowrap}
.plain-note,.references{font-size:.86rem}
@media(min-width:851px){.summary-card .label{white-space:nowrap;font-size:.70rem}}
@media(max-width:850px){.strategy-label{white-space:normal}}
@media(max-width:520px){.summary-card .label,.summary-notes>.muted,.calc-table td:first-child{white-space:normal}.sub-strategy h3,.cost-method,.plan-card h3{min-height:0}}
"""
    else:
        effect_warning = (
            '<div class="alert"><strong>防效外推提示：</strong>已检查参与比较的各方案。'
            f'以下方案的固定避免损失比例在本次密度下属于外推：<ul>{effect_warning_items}</ul>'
            '报告仍保留该数值，仅作为演示假设。</div>'
            if d["effect_scope_warning"]
            else ""
        )
        high_warning = (
            f"<div class=\"alert danger\"><strong>高密度提示：</strong>本次输入超过约{t['biosolarization_supported_to']:g} J2/100 cm³。"
            "当前高等级方案超出文献估算的番茄经济管理范围，应同时评估抗性砧木、轮作或调整作物。</div>"
            if d["above_biosolarization_support"]
            else ""
        )
        chart_current_note = (
            "图中圆点标记本次输入。"
            if report["input"]["density"] <= 500.0
            else "本次输入超过横轴显示范围，因此图中不标记数据点。"
        )
        chart_note = (
            "绿色曲线表示整套检测与防治项目相对无防治的净收益；棕色曲线表示检测分级相对未检测统一处理的条件增量价值。"
            f"两条曲线均已扣除检测和处理成本。{chart_current_note}为清楚展示中低密度变化，横轴显示至500 J2/100 cm³。"
            "固定分级切换会造成曲线跳变；成本或防效变化时，预设阈值不会自动重新优化。"
        )
        language_css = ""
    timing_tag = s["detection_timing"] if english else f"{s['detection_timing']}检测"
    return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(report['report_title'])}</title>
<style>
:root{{--ink:#173129;--muted:#607269;--green:#176744;--cream:#f4f1e8;--paper:#fffdfa;
--line:#dce4de;--amber:#bf7618;--red:#a94432;--shadow:0 12px 34px rgba(20,54,42,.10)}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}}
body{{margin:0;color:var(--ink);background:var(--cream);font-family:"Noto Sans SC","Source Han Sans SC","Microsoft YaHei","PingFang SC",sans-serif;font-size:16px;line-height:1.68;text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}}
.page{{max-width:1180px;margin:0 auto;padding:34px 24px 72px}}
.hero{{position:relative;overflow:hidden;background:linear-gradient(135deg,#123f2f 0%,#176744 58%,#2f7d57 100%);color:#fff;border-radius:28px;padding:46px 48px 40px;box-shadow:var(--shadow)}}
.hero:after{{content:"";position:absolute;width:380px;height:380px;border:78px solid rgba(255,255,255,.07);border-radius:50%;right:-130px;top:-190px}}
.eyebrow{{font-size:.78rem;letter-spacing:.12em;font-weight:700;color:#c9ead8}}
h1,h2{{font-family:"Noto Serif SC","Source Han Serif SC","Songti SC",SimSun,serif}}
h1{{font-size:clamp(2rem,4vw,3.25rem);font-weight:700;letter-spacing:-.02em;line-height:1.18;margin:.5rem 0 1rem;max-width:850px}}
.subtitle{{max-width:850px;font-size:1rem;line-height:1.75;color:#e4f1e9;margin:0 0 1.7rem;position:relative;z-index:1}}
.meta{{display:flex;gap:10px;flex-wrap:wrap;position:relative;z-index:1}} .meta span{{border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.09);padding:7px 11px;border-radius:999px;font-size:.84rem}}
.summary-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:18px 0 26px}}
.summary-card{{min-width:0;min-height:138px;position:relative;background:var(--paper);border:1px solid rgba(23,103,68,.10);border-radius:18px;padding:20px;box-shadow:0 6px 22px rgba(20,54,42,.06)}}
.summary-card .label{{position:relative;z-index:1;font-size:.78rem;line-height:1.45;letter-spacing:.04em;color:var(--muted);font-weight:700}} .summary-content{{position:absolute;inset:0;text-align:center;pointer-events:none}} .summary-card .value{{position:absolute;top:50%;left:20px;right:20px;text-align:center;transform:translateY(-50%);font-size:clamp(1.25rem,2vw,1.45rem);line-height:1.25;font-weight:800;letter-spacing:-.015em;font-variant-numeric:tabular-nums}} .summary-notes{{position:absolute;top:calc(50% + 1rem);left:20px;right:20px;text-align:center}} .summary-notes>.muted{{font-size:.82rem;line-height:1.55;margin-top:2px}}
section{{background:var(--paper);border:1px solid rgba(23,103,68,.10);border-radius:22px;padding:30px;margin:0 0 18px;box-shadow:0 7px 26px rgba(20,54,42,.06)}}
.section-head{{display:flex;align-items:center;gap:12px;margin-bottom:20px}} .section-no{{font-family:"Aptos Display","Segoe UI",Arial,sans-serif;color:var(--green);font-weight:750;font-size:1.28rem;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:.025em}}
h2{{font-size:1.55rem;line-height:1.35;margin:0;color:#163e30}} h3{{font-size:1.02rem;line-height:1.5;margin:.7rem 0 .4rem}} h4{{line-height:1.45;margin:1rem 0 .25rem;color:#315b4b}}
.section-kicker{{margin:2px 0 0;color:var(--muted);font-size:.91rem}}
.decision-grid{{display:grid;grid-template-columns:2fr 1fr;gap:16px;align-items:stretch}} .strategy,.strategy-group{{min-width:0;border:1px solid var(--line);border-radius:16px;padding:20px;background:#fff}}
.no-test-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:stretch;margin-top:10px}} .with-test-grid{{grid-template-columns:1fr}} .sub-strategy{{display:flex;flex-direction:column;padding:16px;background:#fbfdfb}} .sub-strategy h3{{min-height:3.1em}}
.strategy-label{{font-size:.76rem;line-height:1.4;color:var(--muted);font-weight:800;letter-spacing:.05em}} .strategy .income{{font-size:clamp(1.35rem,2.25vw,1.75rem);font-weight:800;letter-spacing:-.02em;line-height:1.3;white-space:nowrap;margin:.35rem 0;font-variant-numeric:tabular-nums}} .profit-caption{{font-size:.72rem;line-height:1.4;letter-spacing:.02em}}
.calc-table{{width:100%;border-collapse:collapse;margin-top:12px;font-size:.86rem;line-height:1.5}} .calc-table td{{vertical-align:top;border-bottom:1px dashed var(--line);padding:7px 0}} .calc-table td:first-child{{padding-right:12px}} .calc-table td:last-child{{text-align:right;white-space:nowrap;font-weight:650;font-variant-numeric:tabular-nums}}
.delta{{margin-top:16px;padding:17px 19px;border-radius:14px;background:#edf7f1;display:flex;justify-content:space-between;gap:18px;align-items:center}}
.delta span{{line-height:1.5}} .delta strong{{font-size:1.35rem;line-height:1.25;white-space:nowrap;font-variant-numeric:tabular-nums}} .gain{{color:var(--green)}} .loss{{color:var(--red)}}
.comparison-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}} .comparison-card{{border:1px solid var(--line);border-radius:14px;padding:16px 18px;background:#f8fbf9}} .comparison-card h3{{margin:0 0 8px}} .comparison-value{{font-size:1.35rem;font-weight:850;font-variant-numeric:tabular-nums}} .comparison-meta{{display:grid;gap:3px;margin-top:8px;color:var(--muted);font-size:.82rem}}
.subsection-title{{margin:24px 0 12px;color:#315b4b}} .cost-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.cost-card{{min-width:0;display:flex;flex-direction:column;border:1px solid var(--line);border-radius:14px;padding:16px;background:#fff}} .cost-card.featured{{border:2px solid var(--green);background:#f2f8f4}}
.cost-method{{min-height:3em;font-weight:800;line-height:1.5}} .cost-value{{font-size:1.25rem;font-weight:800;line-height:1.35;letter-spacing:-.015em;white-space:nowrap;margin:.45rem 0 0;font-variant-numeric:tabular-nums}} .cost-footnote{{margin-top:5px;font-size:.78rem;color:var(--muted)}}
.loss-chart{{display:block;width:100%;height:auto;margin-top:8px}} .loss-chart text{{font-size:12px;fill:#607269;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif}} .loss-chart .chart-callout{{fill:#173129;font-weight:800}}
.legend{{display:flex;align-items:center;gap:10px 18px;flex-wrap:wrap;font-size:.84rem;line-height:1.5;color:var(--muted);margin-top:8px}} .legend span{{display:inline-flex;align-items:center}} .legend i{{width:11px;height:11px;display:inline-block;border-radius:3px;margin-right:5px}}
.plain-note{{padding:15px 17px;border-left:5px solid var(--green);background:#eff7f2;border-radius:10px;margin-top:18px;font-size:.9rem;line-height:1.7}}
.plans{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;align-items:stretch;padding-top:14px}} .plan-card{{min-width:0;position:relative;display:flex;flex-direction:column;border:1px solid var(--line);border-radius:16px;padding:18px;background:#fff}}
.plan-card.selected{{border-color:var(--green);box-shadow:0 0 0 1px var(--green),0 8px 24px rgba(23,103,68,.12)}} .current-tag{{position:absolute;z-index:1;top:-14px;left:22px;right:22px;display:flex;align-items:center;justify-content:center;min-height:24px;background:var(--green);color:#fff;font-size:.7rem;font-weight:800;line-height:1;text-align:center;border-radius:999px;padding:0 10px}}
.plan-heading{{display:flex;align-items:center;justify-content:space-between;gap:8px}} .plan-heading h3{{margin:0}} .grade{{display:grid;place-items:center;min-width:34px;height:34px;padding:0 9px;border-radius:9px;font-weight:900}}
.grade-low{{background:#e1f2e8;color:#176744}} .grade-middle{{background:#fff0c9;color:#966015}} .grade-high{{background:#f8ded8;color:#923d2c}} .range{{font-family:"Cascadia Code",Consolas,monospace;font-size:.78rem;color:var(--muted)}}
.plan-metrics{{display:grid;gap:5px;margin:.8rem 0;color:var(--muted);font-size:.86rem}} .plan-metrics b{{color:var(--ink)}}
.plan-flags{{display:flex;gap:6px;flex-wrap:wrap;margin-top:auto}} .plan-flags span{{font-size:.68rem;font-weight:800;color:var(--green);background:#e8f5ed;border-radius:999px;padding:4px 8px}}
.execution-list{{display:grid;gap:14px}} .execution-card{{border:1px solid var(--line);border-radius:16px;padding:20px;background:#fff}} .execution-title{{display:flex;align-items:flex-start;gap:12px}} .execution-title h3{{margin:0}} .execution-title span:last-child{{font-size:.78rem;line-height:1.5;color:var(--muted)}}
.expected{{padding:10px 12px;background:#f0f6f2;border-radius:9px;margin:12px 0;font-size:.9rem}} ul{{margin:.45rem 0;padding-left:1.3rem}} li{{margin:.45rem 0}}
.alert{{padding:15px 17px;border-left:5px solid var(--amber);background:#fff7e7;border-radius:10px;margin:14px 0}} .alert.danger{{border-color:var(--red);background:#fff0ed}}
.references{{padding-left:1.5rem;font-size:.9rem;line-height:1.75}} .references li{{padding:.55rem 0 .75rem .35rem;border-bottom:1px solid var(--line);overflow-wrap:anywhere}} a{{color:#245d47;text-decoration:none;text-underline-offset:2px}} a:hover{{text-decoration:underline}} .muted{{color:var(--muted)}}
.analysis-grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}} .analysis-card{{border:1px solid var(--line);border-radius:14px;padding:16px;background:#fff}} .analysis-card h3{{margin:0 0 8px}} .analysis-card p{{margin:.35rem 0;color:var(--muted)}} .sensitivity-table{{width:100%;border-collapse:collapse;margin-top:12px;font-size:.78rem}} .sensitivity-table th,.sensitivity-table td{{padding:8px 7px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}} .sensitivity-table th:first-child,.sensitivity-table td:first-child,.sensitivity-table th:nth-child(2),.sensitivity-table td:nth-child(2){{text-align:left}} .sensitivity-table td:nth-child(2){{max-width:270px}} .assumption-list{{font-size:.88rem;line-height:1.65}}
@media(max-width:850px){{.summary-grid{{grid-template-columns:1fr 1fr}}.decision-grid,.comparison-grid,.analysis-grid{{grid-template-columns:1fr}}.cost-grid{{grid-template-columns:1fr 1fr}}.plans{{grid-template-columns:1fr;row-gap:28px}}.hero{{padding:34px 26px}}}}
@media(max-width:520px){{.page{{padding:12px 10px 40px}}.hero{{border-radius:20px}}section{{padding:21px 17px}}.summary-grid,.cost-grid,.no-test-grid{{grid-template-columns:1fr}}.summary-card{{min-height:138px;padding:17px}}.sub-strategy h3,.cost-method{{min-height:0}}.section-head{{gap:10px;margin-bottom:16px}}.section-no{{font-size:1.15rem}}h1{{font-size:2rem}}h2{{font-size:1.35rem}}.delta{{align-items:flex-start;flex-direction:column}}}}
@media print{{body{{background:#fff}}.page{{max-width:none;padding:0}}.hero,section,.summary-card{{box-shadow:none}}section{{break-inside:avoid}}a{{color:inherit}}}}
{language_css}
</style>
</head>
<body>
<main class="page">
  <header class="hero">
    <div class="eyebrow">{ui['eyebrow']}</div>
    <h1>{html.escape(report['report_title'])}</h1>
    <p class="subtitle">{html.escape(report['report_note'])}</p>
    <div class="meta"><span>{ui['example_scenario']}</span><span>{html.escape(s['country'])}</span>
      <span>{html.escape(s['crop'])}</span><span>{html.escape(s['nematode'])}</span>
      <span>{html.escape(timing_tag)}</span><span>{html.escape(s['currency'])}/{html.escape(s['area_unit'])}</span></div>
  </header>

  <div class="summary-grid">
    <div class="summary-card"><div class="label">{ui['detected_density']}</div><div class="summary-content"><div class="value">{report['input']['density']:g}</div><div class="summary-notes"><div class="muted">{html.escape(s['density_unit'])}</div></div></div></div>
    <div class="summary-card"><div class="label">{ui['untreated_yield_loss']}</div><div class="summary-content"><div class="value">{d['yield_loss_fraction']:.2%}</div><div class="summary-notes"></div></div></div>
    <div class="summary-card"><div class="label">{ui['treatment_recommendation']}</div><div class="summary-content"><div class="value">{html.escape(d['band'])}{'' if english else '等级'}</div><div class="summary-notes"><div class="muted">{html.escape(d['treatment_title'])}</div></div></div></div>
    <div class="summary-card"><div class="label">{ui['profit_change']}</div><div class="summary-content"><div class="value {profit_class}">{_signed_money(d['detection_net_benefit_vs_uniform'], report)}</div><div class="summary-notes"><div class="muted">{'vs uniform control' if english else '相对未检测统一处理'}</div></div></div></div>
  </div>

  <section>
    <div class="section-head"><span class="section-no">01</span><div><h2>{ui['section_profit']}</h2></div></div>
    <div class="decision-grid">
      <article class="strategy-group"><div class="strategy-label">{ui['without_test']}</div><div class="no-test-grid">
        <div class="strategy sub-strategy"><h3>{html.escape(e['without_test_no_control']['name'])}</h3>
          <div class="income">{_money(d['net_income_without_test_no_control_per_ha'], report)}</div><div class="muted profit-caption">{ui['season_profit']}</div>
          <table class="calc-table"><tr><td>{ui['remaining_loss']}</td><td>− {_money(d['without_test_no_control_residual_loss_per_ha'], report)}</td></tr><tr><td>{ui['treatment_cost']}</td><td>− {_money(0.0, report)}</td></tr><tr><td>{ui['test_cost']}</td><td>—</td></tr></table>
        </div>
        <div class="strategy sub-strategy"><h3>{html.escape(e['without_test_uniform_control']['name'])}</h3>
          <div class="income">{_money(d['net_income_without_test_uniform_per_ha'], report)}</div><div class="muted profit-caption">{ui['season_profit']}</div>
          <table class="calc-table"><tr><td>{ui['remaining_loss']}</td><td>− {_money(d['without_test_uniform_residual_loss_per_ha'], report)}</td></tr><tr><td>{ui['treatment_cost']}</td><td>− {_money(d['without_test_uniform_treatment_cost_per_ha'], report)}</td></tr><tr><td>{ui['test_cost']}</td><td>—</td></tr></table>
        </div>
      </div>
      </article>
      <article class="strategy-group"><div class="strategy-label">{ui['with_test']}</div><div class="no-test-grid with-test-grid">
        <div class="strategy sub-strategy"><h3>{html.escape(d['treatment_title'] if english else d['treatment'])}</h3>
          <div class="income">{_money(d['net_income_with_test_per_ha'], report)}</div><div class="muted profit-caption">{ui['season_profit']}</div>
          <table class="calc-table"><tr><td>{ui['remaining_loss']}</td><td>− {_money(d['with_test_residual_loss_per_ha'], report)}</td></tr><tr><td>{ui['treatment_cost']}</td><td>− {_money(d['treatment_cost_per_ha'], report)}</td></tr><tr><td>{ui['test_cost']}</td><td>− {_money(d['test_cost_per_ha'], report)}</td></tr></table>
        </div>
      </div></article>
    </div>
    <div class="comparison-grid">
      <article class="comparison-card"><h3>{ui['program_benefit']}</h3><div class="comparison-value {'gain' if d['program_net_benefit_vs_no_control'] >= 0 else 'loss'}">{_signed_money(d['program_net_benefit_vs_no_control'], report)}</div><div class="comparison-meta"><span>{'Baseline: no control' if english else '基线：未采取防治手段'}</span><span>{ui['incremental_cost']}{colon}{_signed_money(d['program_incremental_cost_vs_no_control'], report)}</span><span>{ui['roi']}{colon}{roi_text(d['program_roi_vs_no_control'])}</span></div></article>
      <article class="comparison-card"><h3>{ui['detection_value']}</h3><div class="comparison-value {'gain' if d['detection_net_benefit_vs_uniform'] >= 0 else 'loss'}">{_signed_money(d['detection_net_benefit_vs_uniform'], report)}</div><div class="comparison-meta"><span>{'Baseline: no testing with uniform control' if english else '基线：未检测统一处理'}</span><span>{ui['incremental_cost']}{colon}{_signed_money(d['detection_incremental_cost_vs_uniform'], report)}</span><span>{ui['roi']}{colon}{roi_text(d['detection_roi_vs_uniform'])}</span></div></article>
    </div>
    <h3 class="subsection-title">{ui['detection_costs']}</h3>
    <div class="cost-grid">{cost_cards}</div>
    <div class="plain-note"><div>{html.escape(report['detection_cost_comparison']['price_summary'])}</div><div class="cost-footnote">{html.escape(report['detection_cost_comparison']['comparison_basis'])}</div></div>
  </section>

  <section>
    <div class="section-head"><span class="section-no">02</span><div><h2>{ui['section_loss']}</h2></div></div>
    {_net_benefit_curve_svg(report, language=language)}
    <div class="legend"><span><i style="background:#176744"></i>{ui['program_benefit']}</span><span><i style="background:#b76518"></i>{ui['detection_value']}</span><span>○ {ui['current_input']}</span></div>
    <div class="plain-note">{chart_note}</div>
    <div class="analysis-grid">
      <article class="analysis-card"><h3>{'Break-even density' if english else '密度盈亏平衡'}</h3><p><strong>{ui['program_benefit']}{colon}</strong>{html.escape(program_break_even)}</p><p class="fine-print"><strong>{'Tier-threshold changes' if english else '分级阈值两侧'}{colon}</strong>{html.escape(program_jumps)}</p><p><strong>{ui['detection_value']}{colon}</strong>{html.escape(detection_break_even)}</p><p class="fine-print"><strong>{'Tier-threshold changes' if english else '分级阈值两侧'}{colon}</strong>{html.escape(detection_jumps)}</p><p>{'A preset plan change can cross zero without an exact zero-benefit density, so both strict roots and the values immediately beside each tier threshold are shown.' if english else '预设方案切换可能直接跨过零点而没有严格零收益密度，因此同时展示严格零点和分级阈值两侧的结果。'}</p></article>
      <article class="analysis-card"><h3>{'Interpretation boundary' if english else '解释边界'}</h3><p>{'The first comparison includes control benefits and must not be attributed entirely to detection. The second is a conditional, density-known comparison, not an ex-ante expected value of information.' if english else '第一种比较包含防治本身的收益，不能全部归因于检测；第二种比较是在密度已知条件下的增量价值，不是种植前的期望信息价值。'}</p></article>
    </div>
    <h3 class="subsection-title">{ui['sensitivity']}</h3>
    <table class="sensitivity-table"><thead><tr><th>{'Parameter' if english else '参数'}</th><th>{'Applies to' if english else '作用方案'}</th><th>{'Change' if english else '变化'}</th><th>{'Program net benefit' if english else '整套项目净收益'}</th><th>{'Conditional test value' if english else '检测条件增量价值'}</th><th>{'Worth testing?' if english else '检测是否增益'}</th></tr></thead><tbody>{sensitivity_rows}</tbody></table>
  </section>

  <section>
    <div class="section-head"><span class="section-no">03</span><div><h2>{ui['section_plans']}</h2></div></div>
    <div class="plain-note">{'The density tier selects a preset demonstration strategy. The economic-best badge identifies the option with the highest modelled profit at the current density and parameters; it is not a field prescription.' if english else '密度等级决定预设演示策略；“当前参数下经济净收入最高”标记表示在本次密度和参数下模型利润最高的备选方案，并不构成田间处方。'}</div>
    <div class="plans">{treatment_cards}</div>{effect_warning}{high_warning}
  </section>

  <section>
    <div class="section-head"><span class="section-no">04</span><div><h2>{ui['section_execution']}</h2></div></div>
    <div class="execution-list">{execution_cards}</div>
    <h3 class="subsection-title">{'Key assumptions' if english else '关键假设'}</h3><ul class="assumption-list">{''.join(f'<li>{html.escape(value)}</li>' for value in report['assumptions'].values())}</ul>
  </section>

  <section>
    <div class="section-head"><span class="section-no">05</span><div><h2>{ui['section_references']}</h2></div></div>
    <ol class="references">{reference_items}</ol>
  </section>
</main>
</body>
</html>
"""


def format_html_report_en(report: dict[str, Any]) -> str:
    """Render the English webpage with the same data and structure as Chinese."""

    return format_html_report(report, language="en")


def write_diagnostic_report(
    report: dict[str, Any], output_dir: str | Path
) -> tuple[Path, Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    text_path = directory / "diagnostic_report.txt"
    json_path = directory / "diagnostic_report.json"
    html_path = directory / "diagnostic_report.html"
    text_path.write_text(format_text_report(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    html_path.write_text(format_html_report(report), encoding="utf-8")
    return text_path, json_path, html_path


def write_english_html_report(
    report: dict[str, Any], output_dir: str | Path
) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    html_path = directory / "diagnostic_report_en.html"
    html_path.write_text(format_html_report_en(report), encoding="utf-8")
    return html_path


def open_report_in_browser(path: str | Path) -> bool:
    return webbrowser.open(Path(path).resolve().as_uri())
