"""Create audience-friendly TXT, JSON, and HTML economic-benefit reports."""

from __future__ import annotations

import html
import json
import math
import webbrowser
from copy import deepcopy
from pathlib import Path
from typing import Any

from .config import Model, Treatment
from .economics import Result, choose_treatment
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


DETECTION_COST_COMPARISON = (
    {
        "method": "本项目试纸",
        "cost_per_ha": 5.0,
        "basis": "团队定价，EUR/ha",
        "featured": True,
    },
    {
        "method": "提取后显微/形态学鉴定",
        "cost_per_ha": 31.55,
        "basis": "西班牙官方实验室，首项判定/样",
        "featured": False,
    },
    {
        "method": "PCR 分子鉴定",
        "cost_per_ha": 15.80,
        "basis": "西班牙官方实验室，首项判定/样",
        "featured": False,
    },
    {
        "method": "PCR / 实时 PCR 实验室分析",
        "cost_per_ha": 152.14,
        "basis": "ILVO 公开价，单项分析/样，未含税",
        "featured": False,
    },
)


ENGLISH_PLAN_TEXT = {
    "low": {
        "label": "Low",
        "name": "No dedicated nematode control",
        "overview": (
            "Do not apply a nematicide or soil disinfestation treatment specifically "
            "for root-knot nematodes this season; maintain routine crop management, "
            "field hygiene, and regular scouting."
        ),
        "actions": [
            "Do not add a nematicide or schedule a dedicated soil disinfestation treatment.",
            "Use healthy seedlings without obvious root-galling symptoms, remove soil-bearing root residues, and avoid moving infested soil with tools or irrigation runoff.",
            "Keep the pre-plant density record and reassess nematodes if uneven growth, wilting, or root galls appear during the crop cycle.",
        ],
        "precautions": [
            "Loss may begin above a density of about 6. The no-dedicated-control decision below 10 is a simplified demonstration rule and does not mean that risk is absent.",
            "A treatment cost of 0 EUR/ha means no additional nematode-specific control cost; routine cultivation, hygiene, and scouting remain part of normal production.",
        ],
    },
    "middle": {
        "label": "Medium",
        "name": "40% fluopyram formulation 0.375 L/ha",
        "overview": (
            "Use the 40% fluopyram formulation at 0.375 L/ha from the source study "
            "as the representative medium-tier treatment."
        ),
        "actions": [
            "In the source trial, the chemical treatment was applied through drip irrigation before planting.",
            "Before use, verify the specific product, tomato use, dose, application timing, and protection requirements in Spain’s live plant-protection product register.",
        ],
        "precautions": [
            "The efficacy study included only fields with an initial density above 50 J2/100 cm³ soil; the estimated effect from 10 to 50 is therefore a simplified extrapolation.",
        ],
    },
    "high": {
        "label": "High",
        "name": "Chicken-manure biosolarization 20,000 kg/ha",
        "overview": (
            "Use the chicken-manure biosolarization treatment from the Spanish study: "
            "incorporate 20,000 kg/ha of chicken manure in summer, irrigate, and cover "
            "the soil with transparent film for about six weeks."
        ),
        "actions": [
            "In summer, distribute the chicken manure evenly, incorporate it into approximately 20 cm of topsoil, and irrigate to field capacity.",
            "Cover the soil with approximately 0.03 mm transparent low-density polyethylene film for about six weeks, then remove the film and prepare the soil for planting.",
            "Combine the treatment with resistant rootstocks, crop rotation, and field hygiene in an integrated management plan.",
        ],
        "precautions": [
            "Verify the manure source, sanitary quality, salinity, and local organic-fertilizer requirements before treatment.",
            "At nematode densities above about 759 J2/100 cm³ soil, assess resistant rootstocks, crop rotation, or a change of crop.",
        ],
    },
}


ZH_UI = {
    "eyebrow": "经济效益示例",
    "example_scenario": "示例场景",
    "detected_density": "检测出的线虫密度",
    "untreated_yield_loss": "如不采取防治手段，预计产量损失",
    "treatment_recommendation": "处理建议",
    "profit_change": "使用试纸后的预计利润变化",
    "section_profit": "使用试纸后的利润变化",
    "without_test": "未使用试纸",
    "with_test": "使用试纸并按建议处理",
    "season_profit": "预计单季利润",
    "remaining_loss": "预计剩余产量损失",
    "treatment_cost": "处理成本",
    "test_cost": "试纸成本",
    "profit_delta": "使用试纸后的预计利润变化（相比未检测且未采取防治手段）",
    "detection_costs": "常用线虫检测方法成本对比",
    "section_loss": "预计减少损失一览",
    "legend_low": "低等级",
    "legend_middle": "中等级",
    "legend_high": "高等级",
    "current_input": "本次输入",
    "section_plans": "三级处理方案",
    "current_density": "当前密度",
    "avoided_loss": "预计避免作物损失",
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
    "treatment_recommendation": "Treatment recommendation",
    "profit_change": "Profit change with test strip",
    "section_profit": "Profit change with test strip",
    "without_test": "Without test strip",
    "with_test": "With test strip and recommended treatment",
    "season_profit": "Estimated profit per season",
    "remaining_loss": "Remaining crop loss",
    "treatment_cost": "Treatment cost",
    "test_cost": "Test-strip cost",
    "profit_delta": "Profit change vs no control",
    "detection_costs": "Detection-method cost comparison",
    "section_loss": "Expected loss reduction",
    "legend_low": "Low tier",
    "legend_middle": "Medium tier",
    "legend_high": "High tier",
    "current_input": "Current input",
    "section_plans": "Three-tier treatment plans",
    "current_density": "Current density",
    "avoided_loss": "Estimated crop loss avoided",
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


def _display_unit(text: str) -> str:
    """Use typographic superscripts in user-facing report text."""

    return text.replace("cm^3", "cm³")


def _english_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return an English presentation view without changing report values."""

    localized = deepcopy(report)
    localized["report_title"] = "Nematode Test-Strip Economic Benefit Simulation"
    localized["report_note"] = (
        "This example simulates a grower using a pre-plant test strip to determine "
        "nematode density, following the tiered treatment recommendation, and then "
        "compares the resulting profit per hectare with the no-testing scenario."
    )
    localized["scenario"].update(
        {
            "crop": "Protected tomato",
            "country": "Spain",
            "nematode": "Southern root-knot nematode (Meloidogyne incognita)",
            "detection_timing": "Pre-plant testing",
            "scenario_status": "Example scenario",
        }
    )
    thresholds = localized["thresholds"]
    thresholds["plain_language_note"] = (
        f"Yield loss may begin above approximately "
        f"{thresholds['expected_loss_begins_near']:g} J2/100 cm³ soil. To reflect "
        f"literature uncertainty, this example begins dedicated treatment at "
        f"{thresholds['action_from_density']:g} and switches to the high-tier plan "
        f"at {thresholds['high_from_density']:g}."
    )
    localized["economics"]["without_test_no_control"]["name"] = "No control treatment"
    localized["economics"]["without_test_uniform_control"].update(
        {
            "name": "Uniform control (fluopyram program)",
            "note": (
                "A uniform-control comparison constructed from the fluopyram cost "
                "and nematode-reduction result reported by Talavera-Rubia et al. "
                "(2022); it is not a survey of the most frequently used product in Spain."
            ),
        }
    )

    band_to_key = {"低": "low", "中": "middle", "高": "high"}
    selected_key = band_to_key[report["diagnosis"]["band"]]
    selected_text = ENGLISH_PLAN_TEXT[selected_key]
    treatment_title, treatment_dose = _split_treatment_name(selected_text["name"])
    localized["diagnosis"].update(
        {
            "band": selected_text["label"],
            "treatment": selected_text["name"],
            "treatment_title": treatment_title,
            "treatment_dose": treatment_dose,
        }
    )
    for plan in localized["treatment_options"]:
        translated = ENGLISH_PLAN_TEXT[plan["key"]]
        plan.update(
            {
                "label": translated["label"],
                "name": translated["name"],
                "overview": translated["overview"],
                "actions": list(translated["actions"]),
                "precautions": list(translated["precautions"]),
            }
        )

    localized["loss_reduction_curve"].update(
        {
            "comparison": "Tiered treatment after testing versus no testing and no control",
            "value_definition": "Expected value of crop loss avoided",
        }
    )
    method_names = (
        "Project test strip",
        "Extraction followed by microscopy / morphological identification",
        "PCR molecular identification",
        "PCR / real-time PCR laboratory analysis",
    )
    for item, name in zip(
        localized["detection_cost_comparison"]["items"], method_names
    ):
        item["method"] = name
    localized["detection_cost_comparison"].update(
        {
            "price_summary": (
                "Our team’s test strip costs approximately 68%–97% less than the "
                "listed public laboratory fees and is simpler to operate."
            ),
            "comparison_basis": (
                "Costs assume one representative sample submitted per hectare and "
                "exclude sampling, shipping, tax, and additional preparation."
            ),
        }
    )
    return localized


def _split_treatment_name(name: str) -> tuple[str, str]:
    for dose in ("20,000 kg/ha", "0.375 L/ha"):
        suffix = f" {dose}"
        if name.endswith(suffix):
            return name[: -len(suffix)], dose
    return name, ""


def _plan_payload(key: str, label: str, plan: Treatment, density_range: str) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "density_range": density_range,
        "name": plan.name,
        "cost_per_ha": plan.cost_per_ha,
        "expected_avoided_loss_fraction": plan.avoided_loss_fraction,
        "overview": _display_unit(plan.plan_overview),
        "actions": [_display_unit(item) for item in plan.recommended_actions],
        "precautions": [_display_unit(item) for item in plan.precautions],
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


def build_diagnostic_report(model: Model, result: Result) -> dict[str, Any]:
    potential_revenue = model.baseline_yield_kg_per_ha * model.price_per_kg
    without_test_no_control_residual_loss = result.gross_loss
    without_test_uniform_residual_loss = result.gross_loss * (
        1.0 - model.without_test.avoided_loss_fraction
    )
    with_test_residual_loss = result.gross_loss * (
        1.0 - result.treatment.avoided_loss_fraction
    )
    sampled_densities = {
        model.max_density * index / 200.0 for index in range(201)
    }
    sampled_densities.update(
        {
            model.tolerance_density,
            model.middle_from_density - 1e-6,
            model.middle_from_density,
            model.high_from_density - 1e-6,
            model.high_from_density,
            500.0,
            759.0,
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
            }
        )

    treatment_title, treatment_dose = _split_treatment_name(result.treatment.name)
    return {
        "schema_version": 7,
        "report_title": "线虫检测试纸经济效益模拟报告",
        "report_note": (
            "模拟用户在种植前使用试纸获得线虫密度，并根据试纸给出的分级防治建议采取相应措施后，"
            "相比未检测情况单位面积利润发生的变化。"
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
        "input": {
            "density": result.density,
            "within_literature_density_range": result.density <= model.max_density,
        },
        "thresholds": {
            "expected_loss_begins_near": model.tolerance_density,
            "action_from_density": model.middle_from_density,
            "high_from_density": model.high_from_density,
            "biosolarization_supported_to": 759.0,
            "maximum_supported_density": model.max_density,
            "plain_language_note": (
                f"约{model.tolerance_density:g} J2/100 cm³以上可能开始出现损失；"
                f"本示例考虑文献不确定性后，从{model.middle_from_density:g}开始给出"
                f"专项处理建议，并在{model.high_from_density:g}以上切换到高等级方案。"
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
            "treatment_title": treatment_title,
            "treatment_dose": treatment_dose,
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
            "profit_change_per_ha": result.incremental_net_benefit,
            "expected_reduced_loss_per_ha": (
                without_test_no_control_residual_loss - with_test_residual_loss
            ),
            "expected_reduced_loss_fraction": result.treatment.avoided_loss_fraction,
            "above_biosolarization_support": result.density > 759.0,
        },
        "loss_reduction_curve": {
            "comparison": "检测分级处理相对于未检测且未采取防治手段",
            "value_definition": "预计减少的作物损失金额",
            "points": curve_points,
        },
        "detection_cost_comparison": {
            "items": [dict(item) for item in DETECTION_COST_COMPARISON],
            "price_summary": (
                "本团队试纸成本比所列实验室公开收费低约68%–97%，且操作更为简便。"
            ),
            "comparison_basis": (
                "成本按每公顷提交1份代表性样品计算，且未计采样、寄送、税费或额外前处理。"
            ),
        },
        "treatment_options": [
            _plan_payload(
                "low", "低", model.low, f"d < {model.middle_from_density:g}"
            ),
            _plan_payload(
                "middle",
                "中",
                model.middle,
                f"{model.middle_from_density:g} ≤ d < {model.high_from_density:g}",
            ),
            _plan_payload(
                "high",
                "高",
                model.high,
                f"{model.high_from_density:g} ≤ d ≤ {model.max_density:g}",
            ),
        ],
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
        "一、使用试纸后的利润变化",
        f"  检测密度：{report['input']['density']:g} {s['density_unit']}",
        f"  如不采取防治手段，预计产量损失：{d['yield_loss_fraction']:.2%}",
        f"  处理建议：{d['band']}等级；{d['treatment']}",
        f"  未检测且未采取防治手段的预计利润：{_money(d['net_income_without_test_no_control_per_ha'], report)}",
        f"  未检测但采用统一处理的预计利润：{_money(d['net_income_without_test_uniform_per_ha'], report)}",
        f"  使用试纸后的预计利润：{_money(d['net_income_with_test_per_ha'], report)}",
        f"  使用试纸后的预计利润变化：{_signed_money(d['profit_change_per_ha'], report)}",
        "",
        "  检测成本对比（按1份代表性样品/ha的演示口径）",
        *(
            f"  - {item['method']}：{item['cost_per_ha']:.2f} EUR/ha（{item['basis']}）"
            for item in report["detection_cost_comparison"]["items"]
        ),
        f"  {report['detection_cost_comparison']['comparison_basis']}",
        "",
        "二、阈值说明",
        f"  {t['plain_language_note']}",
        "  损失的减少来自依据检测结果调整处理方案，不是试纸本身直接防治线虫。",
        "",
        "三、三级处理方案",
    ]
    for plan in report["treatment_options"]:
        selected = "【当前密度】" if plan["label"] == d["band"] else ""
        lines.append(
            f"  {plan['label']}等级 {selected} {plan['density_range']}：{plan['name']}；"
            f"成本={_money(plan['cost_per_ha'], report)}；"
            f"预计避免作物损失={plan['expected_avoided_loss_fraction']:.2%}"
        )
    lines.extend(["", "四、执行建议"])
    selected_plan = next(
        plan for plan in report["treatment_options"] if plan["label"] == d["band"]
    )
    lines.append(f"  {selected_plan['label']}等级｜{selected_plan['name']}")
    lines.append(f"    {selected_plan['overview']}")
    lines.extend(f"    - {item}" for item in selected_plan["actions"])
    lines.extend(f"    - 注意：{item}" for item in selected_plan["precautions"])
    lines.extend(["", "五、参考文献"])
    for index, item in enumerate(report["references"], 1):
        lines.append(f"  [{index}] {item['citation']} {item['url']}")
    return "\n".join(lines) + "\n"


def _loss_reduction_curve_svg(
    report: dict[str, Any], *, language: str = "zh-CN"
) -> str:
    points_data = report["loss_reduction_curve"]["points"]
    thresholds = report["thresholds"]
    diagnosis = report["diagnosis"]
    input_density = report["input"]["density"]
    width, height = 900.0, 310.0
    left, right, top, bottom = 76.0, 24.0, 20.0, 48.0
    plot_w, plot_h = width - left - right, height - top - bottom
    chart_max_density = 500.0
    visible_points = [
        point for point in points_data if point["density"] <= chart_max_density
    ]
    current_is_visible = input_density <= chart_max_density
    current_value = diagnosis["expected_reduced_loss_per_ha"]
    values = [point["expected_reduced_loss_per_ha"] for point in visible_points]
    raw_max = max(values + ([current_value] if current_is_visible else []) + [1.0])
    raw_step = raw_max / 4.0
    magnitude = 10.0 ** math.floor(math.log10(raw_step))
    normalized_step = raw_step / magnitude
    if normalized_step <= 1.0:
        tick_step = magnitude
    elif normalized_step <= 2.0:
        tick_step = 2.0 * magnitude
    elif normalized_step <= 5.0:
        tick_step = 5.0 * magnitude
    else:
        tick_step = 10.0 * magnitude
    y_min, y_max = 0.0, tick_step * 4.0

    def sx(value: float) -> float:
        return left + plot_w * value / chart_max_density

    def sy(value: float) -> float:
        return top + plot_h * (y_max - value) / (y_max - y_min)

    zones = (
        (0.0, thresholds["action_from_density"], "#e8f5ed"),
        (thresholds["action_from_density"], thresholds["high_from_density"], "#fff4d6"),
        (thresholds["high_from_density"], chart_max_density, "#fbe9e5"),
    )
    zone_markup = "".join(
        f'<rect x="{sx(start):.2f}" y="{top:.2f}" width="{sx(end)-sx(start):.2f}" '
        f'height="{plot_h:.2f}" fill="{colour}" />'
        for start, end, colour in zones
    )
    bands = (
        [point for point in visible_points if point["density"] < thresholds["action_from_density"]],
        [
            point
            for point in visible_points
            if thresholds["action_from_density"] <= point["density"] < thresholds["high_from_density"]
        ],
        [point for point in visible_points if point["density"] >= thresholds["high_from_density"]],
    )
    polylines = "".join(
        '<polyline points="{}" fill="none" stroke="#176744" stroke-width="3" '
        'stroke-linejoin="round" stroke-linecap="round" />'.format(
            " ".join(
                f"{sx(point['density']):.2f},{sy(point['expected_reduced_loss_per_ha']):.2f}"
                for point in band
            )
        )
        for band in bands
        if len(band) >= 2
    )
    grid = []
    for index in range(5):
        value = y_min + (y_max - y_min) * index / 4.0
        y = sy(value)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width-right}" y2="{y:.2f}" '
            'stroke="#dbe4de" stroke-width="1" />'
            f'<text x="{left-10}" y="{y+4:.2f}" text-anchor="end">{value:,.0f}</text>'
        )
    x_ticks = []
    for tick in (0.0, 10.0, 50.0, 80.0, 150.0, 300.0, chart_max_density):
        x = sx(tick)
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{height-bottom}" x2="{x:.2f}" y2="{height-bottom+5}" '
            'stroke="#617269" />'
            f'<text x="{x:.2f}" y="{height-bottom+21}" text-anchor="middle">{tick:g}</text>'
        )
    zero_y = sy(0.0)
    marker_x, marker_y = sx(min(input_density, chart_max_density)), sy(current_value)
    marker_markup = (
        f'<circle cx="{marker_x:.2f}" cy="{marker_y:.2f}" r="5" fill="#ffffff" '
        'stroke="#253b33" stroke-width="3" />'
        if current_is_visible
        else ""
    )
    if language == "en":
        aria_label = "Nematode density and expected crop-loss reduction after testing"
        x_axis_label = "Nematode density (J2/100 cm³ soil)"
        y_axis_label = "Expected loss reduction (EUR/ha)"
    else:
        aria_label = "线虫密度与根据检测建议预计减少的损失"
        x_axis_label = "线虫密度（J2/100 cm³ soil）"
        y_axis_label = "预计减少的损失（EUR/ha）"
    return f"""
<svg class="loss-chart" viewBox="0 0 {width:g} {height:g}" role="img"
 aria-label="{aria_label}">
  {zone_markup}
  {''.join(grid)}
  {''.join(x_ticks)}
  <line x1="{left}" y1="{zero_y:.2f}" x2="{width-right}" y2="{zero_y:.2f}"
   stroke="#617269" stroke-width="1.4" />
  {polylines}
  {marker_markup}
  <text x="{left + plot_w/2:.2f}" y="{height-2}" text-anchor="middle">{x_axis_label}</text>
  <text x="17" y="{top+plot_h/2:.2f}" text-anchor="middle"
   transform="rotate(-90 17 {top+plot_h/2:.2f})">{y_axis_label}</text>
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
    profit_class = "gain" if d["profit_change_per_ha"] >= 0 else "loss"

    def plan_name_markup(plan: dict[str, Any]) -> str:
        if english and plan["key"] in {"middle", "high"}:
            title, dose = _split_treatment_name(plan["name"])
            if dose:
                return (
                    f"{html.escape(title)}"
                    f'<span class="plan-dose">{html.escape(dose)}</span>'
                )
        return html.escape(plan["name"])

    treatment_cards = "".join(
        f"""<article class="plan-card {'selected' if plan['label'] == d['band'] else ''}">
          {f'<span class="current-tag">{ui["current_density"]}</span>' if plan['label'] == d['band'] else ''}
          <div class="plan-heading"><span class="grade grade-{plan['key']}">{plan['label']}</span>
          <span class="range">{html.escape(plan['density_range'])}</span></div>
          <h3>{plan_name_markup(plan)}</h3>
          <div class="plan-metrics"><span>{ui['treatment_cost']} <b>{_money(plan['cost_per_ha'], report)}</b></span>
          <span>{ui['avoided_loss']} <b>{plan['expected_avoided_loss_fraction']:.2%}</b></span></div>
        </article>"""
        for plan in report["treatment_options"]
    )
    execution_cards = "".join(
        f"""<article class="execution-card">
          <div class="execution-title"><span class="grade grade-{plan['key']}">{plan['label']}</span>
          <div><h3>{html.escape(plan['name'])}</h3><span>{html.escape(plan['density_range'])}</span></div></div>
          <p>{html.escape(plan['overview'])}</p>
          <div class="expected">{ui['avoided_loss']}: <strong>{plan['expected_avoided_loss_fraction']:.2%}</strong>
          · {ui['treatment_cost']}: <strong>{_money(plan['cost_per_ha'], report)}</strong></div>
          <h4>{ui['implementation']}</h4><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in plan['actions'])}</ul>
          <h4>{ui['precautions']}</h4><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in plan['precautions'])}</ul>
        </article>"""
        for plan in report["treatment_options"]
        if plan["label"] == d["band"]
    )
    cost_cards = "".join(
        f"""<article class="cost-card {'featured' if item['featured'] else ''}">
          <div class="cost-method">{html.escape(item['method'])}</div>
          <div class="cost-value">{item['cost_per_ha']:,.2f} EUR/ha</div>
        </article>"""
        for item in report["detection_cost_comparison"]["items"]
    )
    reference_items = "".join(
        f'<li><a href="{html.escape(item["url"], quote=True)}" target="_blank" '
        f'rel="noopener noreferrer">{html.escape(item["citation"])}</a></li>'
        for item in report["references"]
    )
    if english:
        high_warning = (
            "<div class=\"alert danger\"><strong>High-density note:</strong> "
            "The current input exceeds approximately 759 J2/100 cm³ soil. "
            "Single-treatment biosolarization is beyond the tomato economic-management "
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
            "The curve uses ‘no testing and no control’ as its baseline. The y-axis "
            "shows the monetary value of crop loss expected to be avoided by following "
            f"the test-strip recommendation. The current input is "
            f"{report['input']['density']:g} J2/100 cm³ soil, corresponding to an "
            f"expected crop-loss reduction of {_money(d['expected_reduced_loss_per_ha'], report)}. "
            f"{chart_current_note} To show the low- and medium-density regions clearly, "
            "the x-axis ends at 500 J2/100 cm³ soil. Yield loss may begin above "
            f"approximately {t['expected_loss_begins_near']:g}; this example begins "
            f"dedicated treatment at {t['action_from_density']:g} and switches to the "
            f"high tier at {t['high_from_density']:g}."
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
        high_warning = (
            "<div class=\"alert danger\"><strong>高密度提示：</strong>本次输入超过约759 J2/100 cm³。"
            "单项生物太阳能消毒超出文献估算的番茄经济管理范围，应同时评估抗性砧木、轮作或调整作物。</div>"
            if d["above_biosolarization_support"]
            else ""
        )
        chart_current_note = (
            "图中圆点标记本次输入。"
            if report["input"]["density"] <= 500.0
            else "本次输入超过横轴显示范围，因此图中不标记数据点。"
        )
        chart_note = (
            "曲线以“未检测且未采取防治手段”为比较基线，纵轴表示按试纸建议处理后预计减少的作物损失金额。"
            f"本次输入为{report['input']['density']:g} J2/100 cm³，对应预计减少作物损失"
            f"{_money(d['expected_reduced_loss_per_ha'], report)}。{chart_current_note}"
            "为清楚展示中低密度变化，横轴显示至500 J2/100 cm³。"
            f"约{t['expected_loss_begins_near']:g}以上可能开始出现损失，本示例从"
            f"{t['action_from_density']:g}开始给出专项处理建议，在"
            f"{t['high_from_density']:g}以上切换至高等级方案。"
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
.execution-list{{display:grid;gap:14px}} .execution-card{{border:1px solid var(--line);border-radius:16px;padding:20px;background:#fff}} .execution-title{{display:flex;align-items:flex-start;gap:12px}} .execution-title h3{{margin:0}} .execution-title span:last-child{{font-size:.78rem;line-height:1.5;color:var(--muted)}}
.expected{{padding:10px 12px;background:#f0f6f2;border-radius:9px;margin:12px 0;font-size:.9rem}} ul{{margin:.45rem 0;padding-left:1.3rem}} li{{margin:.45rem 0}}
.alert{{padding:15px 17px;border-left:5px solid var(--amber);background:#fff7e7;border-radius:10px;margin:14px 0}} .alert.danger{{border-color:var(--red);background:#fff0ed}}
.references{{padding-left:1.5rem;font-size:.9rem;line-height:1.75}} .references li{{padding:.55rem 0 .75rem .35rem;border-bottom:1px solid var(--line);overflow-wrap:anywhere}} a{{color:#245d47;text-decoration:none;text-underline-offset:2px}} a:hover{{text-decoration:underline}} .muted{{color:var(--muted)}}
@media(max-width:850px){{.summary-grid{{grid-template-columns:1fr 1fr}}.decision-grid{{grid-template-columns:1fr}}.cost-grid{{grid-template-columns:1fr 1fr}}.plans{{grid-template-columns:1fr;row-gap:28px}}.hero{{padding:34px 26px}}}}
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
    <div class="summary-card"><div class="label">{ui['profit_change']}</div><div class="summary-content"><div class="value {profit_class}">{_signed_money(d['profit_change_per_ha'], report)}</div><div class="summary-notes"></div></div></div>
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
    <div class="delta"><span>{ui['profit_delta']}</span><strong class="{profit_class}">{_signed_money(d['profit_change_per_ha'], report)}</strong></div>
    <h3 class="subsection-title">{ui['detection_costs']}</h3>
    <div class="cost-grid">{cost_cards}</div>
    <div class="plain-note"><div>{html.escape(report['detection_cost_comparison']['price_summary'])}</div><div class="cost-footnote">{html.escape(report['detection_cost_comparison']['comparison_basis'])}</div></div>
  </section>

  <section>
    <div class="section-head"><span class="section-no">02</span><div><h2>{ui['section_loss']}</h2></div></div>
    {_loss_reduction_curve_svg(report, language=language)}
    <div class="legend"><span><i style="background:#e8f5ed"></i>{ui['legend_low']}</span><span><i style="background:#fff4d6"></i>{ui['legend_middle']}</span><span><i style="background:#fbe9e5"></i>{ui['legend_high']}</span><span>● {ui['current_input']}</span></div>
    <div class="plain-note">{chart_note}</div>
  </section>

  <section>
    <div class="section-head"><span class="section-no">03</span><div><h2>{ui['section_plans']}</h2></div></div>
    <div class="plans">{treatment_cards}</div>{high_warning}
  </section>

  <section>
    <div class="section-head"><span class="section-no">04</span><div><h2>{ui['section_execution']}</h2></div></div>
    <div class="execution-list">{execution_cards}</div>
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
