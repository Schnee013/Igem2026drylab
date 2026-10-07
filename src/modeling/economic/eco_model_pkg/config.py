"""Load and validate the source-labelled Spain protected-tomato demo model."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Evidence:
    parameter: str
    classification: str
    value_note: str
    source: str


@dataclass(frozen=True)
class DetectionMethod:
    name: str
    name_en: str
    fee_per_sample_eur: float
    basis: str
    basis_en: str


@dataclass(frozen=True)
class DetectionCostComparison:
    project_method_name: str
    project_method_name_en: str
    samples_per_ha: float
    excluded_costs: str
    excluded_costs_en: str
    methods: tuple[DetectionMethod, ...]


@dataclass(frozen=True)
class SensitivitySettings:
    test_cost_multipliers: tuple[float, ...]
    treatment_cost_multipliers: tuple[float, ...]
    efficacy_multipliers: tuple[float, ...]
    crop_price_multipliers: tuple[float, ...]


@dataclass(frozen=True)
class Treatment:
    """A fixed demo treatment; effect is the fraction of yield loss avoided."""

    name: str
    name_en: str
    application_rate: str
    application_rate_en: str
    cost_per_ha: float
    avoided_loss_fraction: float
    population_reduction_fraction: float | None
    effect_reference_density: float | None
    study_density_min: float | None
    study_density_max: float | None
    management_support_max: float | None
    effect_model: str
    effect_basis_note: str
    effect_basis_note_en: str
    evidence_class: str
    evidence_note: str
    evidence_note_en: str
    plan_overview: str
    plan_overview_en: str
    recommended_actions: tuple[str, ...]
    recommended_actions_en: tuple[str, ...]
    precautions: tuple[str, ...]
    precautions_en: tuple[str, ...]


@dataclass(frozen=True)
class Model:
    crop: str
    crop_en: str
    country: str
    country_en: str
    nematode: str
    nematode_en: str
    detection_timing: str
    detection_timing_en: str
    density_unit: str
    area_unit: str
    currency: str
    baseline_yield_kg_per_ha: float
    price_per_kg: float
    baseline_production_cost_per_ha: float
    test_cost_per_ha: float
    test_cost_status: str
    tolerance_density: float
    minimum_relative_yield: float
    seinhorst_z: float
    max_density: float
    middle_from_density: float
    high_from_density: float
    without_test: Treatment
    low: Treatment
    middle: Treatment
    high: Treatment
    detection_cost_comparison: DetectionCostComparison
    sensitivity: SensitivitySettings
    source_note: str
    source_note_en: str
    evidence: tuple[Evidence, ...]


def _number(value: object, label: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} 必须是 JSON 数字")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} 必须是有限数")
    if minimum is not None and result < minimum:
        raise ValueError(f"{label} 不能小于 {minimum}")
    return result


def _optional_number(
    value: object, label: str, *, minimum: float | None = None
) -> float | None:
    if value is None:
        return None
    return _number(value, label, minimum=minimum)


def _object(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} 必须是 JSON 对象")
    return value


def _text(value: object, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{label} 必须是{'字符串' if allow_empty else '非空字符串'}")
    return value.strip()


def _text_list(value: object, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{label} 必须是字符串数组")
    return tuple(_text(item, f"{label}[{index}]") for index, item in enumerate(value))


def _number_list(value: object, label: str) -> tuple[float, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} 必须是非空数字数组")
    return tuple(
        _number(item, f"{label}[{index}]", minimum=0)
        for index, item in enumerate(value)
    )


def _fraction(value: object, label: str) -> float:
    result = _number(value, label)
    if not 0 <= result <= 1:
        raise ValueError(f"{label} 必须处于 0 到 1 之间")
    return result


def _optional_fraction(value: object, label: str) -> float | None:
    if value is None:
        return None
    return _fraction(value, label)


def _treatment(value: object, label: str) -> Treatment:
    data = _object(value, label)
    effect = _object(data.get("effect"), f"{label}.effect")
    return Treatment(
        name=_text(data.get("name"), f"{label}.name"),
        name_en=_text(data.get("name_en"), f"{label}.name_en"),
        application_rate=_text(data.get("application_rate", ""), f"{label}.application_rate", allow_empty=True),
        application_rate_en=_text(data.get("application_rate_en", ""), f"{label}.application_rate_en", allow_empty=True),
        cost_per_ha=_number(data.get("cost_per_ha"), f"{label}.cost_per_ha", minimum=0),
        avoided_loss_fraction=_fraction(effect.get("avoided_loss_fraction"), f"{label}.effect.avoided_loss_fraction"),
        population_reduction_fraction=_optional_fraction(effect.get("population_reduction_fraction"), f"{label}.effect.population_reduction_fraction"),
        effect_reference_density=_optional_number(effect.get("reference_density"), f"{label}.effect.reference_density", minimum=0),
        study_density_min=_optional_number(effect.get("study_density_min"), f"{label}.effect.study_density_min", minimum=0),
        study_density_max=_optional_number(effect.get("study_density_max"), f"{label}.effect.study_density_max", minimum=0),
        management_support_max=_optional_number(effect.get("management_support_max"), f"{label}.effect.management_support_max", minimum=0),
        effect_model=_text(effect.get("model"), f"{label}.effect.model"),
        effect_basis_note=_text(effect.get("basis_note"), f"{label}.effect.basis_note"),
        effect_basis_note_en=_text(effect.get("basis_note_en"), f"{label}.effect.basis_note_en"),
        evidence_class=_text(data.get("evidence_class"), f"{label}.evidence_class"),
        evidence_note=_text(data.get("evidence_note"), f"{label}.evidence_note"),
        evidence_note_en=_text(data.get("evidence_note_en"), f"{label}.evidence_note_en"),
        plan_overview=_text(data.get("plan_overview"), f"{label}.plan_overview", allow_empty=True),
        plan_overview_en=_text(data.get("plan_overview_en"), f"{label}.plan_overview_en", allow_empty=True),
        recommended_actions=_text_list(data.get("recommended_actions"), f"{label}.recommended_actions"),
        recommended_actions_en=_text_list(data.get("recommended_actions_en"), f"{label}.recommended_actions_en"),
        precautions=_text_list(data.get("precautions"), f"{label}.precautions"),
        precautions_en=_text_list(data.get("precautions_en"), f"{label}.precautions_en"),
    )


def _detection_cost_comparison(value: object) -> DetectionCostComparison:
    data = _object(value, "detection_cost_comparison")
    raw_methods = data.get("laboratory_methods")
    if not isinstance(raw_methods, list) or not raw_methods:
        raise ValueError("detection_cost_comparison.laboratory_methods 必须是非空数组")
    methods: list[DetectionMethod] = []
    for index, raw_method in enumerate(raw_methods):
        label = f"detection_cost_comparison.laboratory_methods[{index}]"
        method = _object(raw_method, label)
        methods.append(
            DetectionMethod(
                name=_text(method.get("name"), f"{label}.name"),
                name_en=_text(method.get("name_en"), f"{label}.name_en"),
                fee_per_sample_eur=_number(method.get("fee_per_sample_eur"), f"{label}.fee_per_sample_eur", minimum=0),
                basis=_text(method.get("basis"), f"{label}.basis"),
                basis_en=_text(method.get("basis_en"), f"{label}.basis_en"),
            )
        )
    return DetectionCostComparison(
        project_method_name=_text(data.get("project_method_name"), "detection_cost_comparison.project_method_name"),
        project_method_name_en=_text(data.get("project_method_name_en"), "detection_cost_comparison.project_method_name_en"),
        samples_per_ha=_number(data.get("samples_per_ha"), "detection_cost_comparison.samples_per_ha", minimum=0),
        excluded_costs=_text(data.get("excluded_costs"), "detection_cost_comparison.excluded_costs"),
        excluded_costs_en=_text(data.get("excluded_costs_en"), "detection_cost_comparison.excluded_costs_en"),
        methods=tuple(methods),
    )


def _sensitivity(value: object) -> SensitivitySettings:
    data = _object(value, "sensitivity_analysis")
    return SensitivitySettings(
        test_cost_multipliers=_number_list(data.get("test_cost_multipliers"), "sensitivity_analysis.test_cost_multipliers"),
        treatment_cost_multipliers=_number_list(data.get("treatment_cost_multipliers"), "sensitivity_analysis.treatment_cost_multipliers"),
        efficacy_multipliers=_number_list(data.get("efficacy_multipliers"), "sensitivity_analysis.efficacy_multipliers"),
        crop_price_multipliers=_number_list(data.get("crop_price_multipliers"), "sensitivity_analysis.crop_price_multipliers"),
    )


def _loss_fraction_at_density(density: float, model: Model) -> float:
    if density <= model.tolerance_density:
        return 0.0
    relative_yield = model.minimum_relative_yield + (1.0 - model.minimum_relative_yield) * model.seinhorst_z ** (density / model.tolerance_density - 1.0)
    return 1.0 - relative_yield


def validate_model(model: Model) -> None:
    if model.density_unit != "J2/100 cm^3 soil":
        raise ValueError("当前演示仅接受密度单位 J2/100 cm^3 soil")
    if model.area_unit != "ha" or model.currency != "EUR":
        raise ValueError("当前演示仅接受面积单位 ha 和货币 EUR")
    if model.baseline_yield_kg_per_ha <= 0 or model.price_per_kg <= 0:
        raise ValueError("基准产量与作物价格必须大于 0")
    if model.baseline_production_cost_per_ha < 0 or model.test_cost_per_ha < 0:
        raise ValueError("生产成本与检测成本不能为负")
    if not 0 <= model.minimum_relative_yield <= 1:
        raise ValueError("minimum_relative_yield 必须处于 0 到 1 之间")
    if not 0 < model.seinhorst_z < 1:
        raise ValueError("Seinhorst 参数 z 必须处于 0 到 1 之间")
    if not 0 < model.tolerance_density <= model.middle_from_density:
        raise ValueError("耐受阈值与中等级起点无效")
    if not model.middle_from_density < model.high_from_density <= model.max_density:
        raise ValueError("分级阈值必须递增且不超过文献试验密度范围")
    if model.detection_cost_comparison.samples_per_ha <= 0:
        raise ValueError("每公顷代表性样品数必须大于 0")
    for plan in (model.without_test, model.low, model.middle, model.high):
        if plan.cost_per_ha < 0 or not 0 <= plan.avoided_loss_fraction <= 1:
            raise ValueError(f"方案 {plan.name} 的成本或避免损失比例无效")
        if plan.study_density_min is not None and plan.study_density_max is not None and plan.study_density_min > plan.study_density_max:
            raise ValueError(f"方案 {plan.name} 的研究密度范围无效")
        if plan.population_reduction_fraction is not None:
            if plan.effect_reference_density is None:
                raise ValueError(f"方案 {plan.name} 缺少效果换算参考密度")
            untreated_loss = _loss_fraction_at_density(plan.effect_reference_density, model)
            treated_density = plan.effect_reference_density * (1.0 - plan.population_reduction_fraction)
            treated_loss = _loss_fraction_at_density(treated_density, model)
            if untreated_loss <= 0:
                raise ValueError(f"方案 {plan.name} 的参考密度不能换算避免损失比例")
            derived = (untreated_loss - treated_loss) / untreated_loss
            if abs(derived - plan.avoided_loss_fraction) > 5e-5:
                raise ValueError(f"方案 {plan.name} 的固定避免损失比例与参考密度换算不一致：配置={plan.avoided_loss_fraction:.6f}，换算={derived:.6f}")
    if model.low.cost_per_ha != 0 or model.low.avoided_loss_fraction != 0:
        raise ValueError("低等级必须是不增加专项成本且不计避免损失的无专项防治方案")
    if model.without_test.cost_per_ha != model.middle.cost_per_ha or model.without_test.avoided_loss_fraction != model.middle.avoided_loss_fraction:
        raise ValueError("常规统一处理必须与中等级代表方案使用同一成本和效果")


def load_model(path: str | Path) -> Model:
    source = Path(path)
    try:
        root = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取模型 JSON {source}: {exc}") from exc
    data = _object(root, "模型根对象")
    scenario = _object(data.get("scenario"), "scenario")
    loss = _object(data.get("loss_function"), "loss_function")
    economics = _object(data.get("economics"), "economics")
    thresholds = _object(data.get("grade_thresholds"), "grade_thresholds")
    if _text(loss.get("type"), "loss_function.type").lower() != "seinhorst":
        raise ValueError("loss_function.type 必须是 seinhorst")

    raw_evidence = data.get("evidence", [])
    if not isinstance(raw_evidence, list):
        raise ValueError("evidence 必须是数组")
    evidence_items: list[Evidence] = []
    for index, raw_item in enumerate(raw_evidence):
        item = _object(raw_item, f"evidence[{index}]")
        evidence_items.append(Evidence(
            parameter=_text(item.get("parameter"), f"evidence[{index}].parameter"),
            classification=_text(item.get("classification"), f"evidence[{index}].classification"),
            value_note=_text(item.get("value_note"), f"evidence[{index}].value_note"),
            source=_text(item.get("source"), f"evidence[{index}].source"),
        ))

    model = Model(
        crop=_text(scenario.get("crop"), "scenario.crop"),
        crop_en=_text(scenario.get("crop_en"), "scenario.crop_en"),
        country=_text(scenario.get("country"), "scenario.country"),
        country_en=_text(scenario.get("country_en"), "scenario.country_en"),
        nematode=_text(scenario.get("nematode"), "scenario.nematode"),
        nematode_en=_text(scenario.get("nematode_en"), "scenario.nematode_en"),
        detection_timing=_text(scenario.get("detection_timing"), "scenario.detection_timing"),
        detection_timing_en=_text(scenario.get("detection_timing_en"), "scenario.detection_timing_en"),
        density_unit=_text(scenario.get("density_unit"), "scenario.density_unit"),
        area_unit=_text(scenario.get("area_unit"), "scenario.area_unit"),
        currency=_text(scenario.get("currency"), "scenario.currency"),
        baseline_yield_kg_per_ha=_number(economics.get("baseline_yield_kg_per_ha"), "economics.baseline_yield_kg_per_ha", minimum=0),
        price_per_kg=_number(economics.get("price_per_kg"), "economics.price_per_kg", minimum=0),
        baseline_production_cost_per_ha=_number(economics.get("baseline_production_cost_per_ha"), "economics.baseline_production_cost_per_ha", minimum=0),
        test_cost_per_ha=_number(economics.get("test_cost_per_ha"), "economics.test_cost_per_ha", minimum=0),
        test_cost_status=_text(economics.get("test_cost_status"), "economics.test_cost_status"),
        tolerance_density=_number(loss.get("tolerance_density"), "loss_function.tolerance_density", minimum=0),
        minimum_relative_yield=_fraction(loss.get("minimum_relative_yield"), "loss_function.minimum_relative_yield"),
        seinhorst_z=_fraction(loss.get("z"), "loss_function.z"),
        max_density=_number(loss.get("max_density"), "loss_function.max_density", minimum=0),
        middle_from_density=_number(thresholds.get("middle_from_density"), "grade_thresholds.middle_from_density", minimum=0),
        high_from_density=_number(thresholds.get("high_from_density"), "grade_thresholds.high_from_density", minimum=0),
        without_test=_treatment(data.get("without_test"), "without_test"),
        low=_treatment(data.get("low"), "low"),
        middle=_treatment(data.get("middle"), "middle"),
        high=_treatment(data.get("high"), "high"),
        detection_cost_comparison=_detection_cost_comparison(data.get("detection_cost_comparison")),
        sensitivity=_sensitivity(data.get("sensitivity_analysis")),
        source_note=_text(data.get("source_note"), "source_note"),
        source_note_en=_text(data.get("source_note_en"), "source_note_en"),
        evidence=tuple(evidence_items),
    )
    validate_model(model)
    return model


def load_density(path: str | Path) -> float:
    source = Path(path)
    try:
        root = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取密度输入 JSON {source}: {exc}") from exc
    data = _object(root, "输入根对象")
    unit = _text(data.get("density_unit"), "density_unit")
    if unit != "J2/100 cm^3 soil":
        raise ValueError("输入密度单位必须是 J2/100 cm^3 soil")
    return _number(data.get("density"), "density", minimum=0)
