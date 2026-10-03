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
class Treatment:
    """A fixed demo treatment; effect is the fraction of yield loss avoided."""

    name: str
    cost_per_ha: float
    avoided_loss_fraction: float
    evidence_class: str
    evidence_note: str
    plan_overview: str
    recommended_actions: tuple[str, ...]
    precautions: tuple[str, ...]


@dataclass(frozen=True)
class Model:
    crop: str
    country: str
    nematode: str
    detection_timing: str
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
    source_note: str
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


def _fraction(value: object, label: str) -> float:
    result = _number(value, label)
    if not 0 <= result <= 1:
        raise ValueError(f"{label} 必须处于 0 到 1 之间")
    return result


def _treatment(value: object, label: str) -> Treatment:
    data = _object(value, label)
    return Treatment(
        name=_text(data.get("name"), f"{label}.name"),
        cost_per_ha=_number(data.get("cost_per_ha"), f"{label}.cost_per_ha", minimum=0),
        avoided_loss_fraction=_fraction(
            data.get("avoided_loss_fraction"), f"{label}.avoided_loss_fraction"
        ),
        evidence_class=_text(data.get("evidence_class"), f"{label}.evidence_class"),
        evidence_note=_text(data.get("evidence_note"), f"{label}.evidence_note"),
        plan_overview=_text(data.get("plan_overview"), f"{label}.plan_overview", allow_empty=True),
        recommended_actions=_text_list(data.get("recommended_actions"), f"{label}.recommended_actions"),
        precautions=_text_list(data.get("precautions"), f"{label}.precautions"),
    )


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
    for plan in (model.without_test, model.low, model.middle, model.high):
        if plan.cost_per_ha < 0 or not 0 <= plan.avoided_loss_fraction <= 1:
            raise ValueError(f"方案 {plan.name} 的成本或避免损失比例无效")
    if model.low.cost_per_ha != 0 or model.low.avoided_loss_fraction != 0:
        raise ValueError("低等级必须是不增加专项成本且不计避免损失的无专项防治方案")
    if (
        model.without_test.cost_per_ha != model.middle.cost_per_ha
        or model.without_test.avoided_loss_fraction
        != model.middle.avoided_loss_fraction
    ):
        raise ValueError("常规统一处理必须与中等级氟吡菌酰胺代表方案使用同一成本和效果")


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
        evidence_items.append(
            Evidence(
                parameter=_text(item.get("parameter"), f"evidence[{index}].parameter"),
                classification=_text(
                    item.get("classification"), f"evidence[{index}].classification"
                ),
                value_note=_text(item.get("value_note"), f"evidence[{index}].value_note"),
                source=_text(item.get("source"), f"evidence[{index}].source"),
            )
        )

    model = Model(
        crop=_text(scenario.get("crop"), "scenario.crop"),
        country=_text(scenario.get("country"), "scenario.country"),
        nematode=_text(scenario.get("nematode"), "scenario.nematode"),
        detection_timing=_text(scenario.get("detection_timing"), "scenario.detection_timing"),
        density_unit=_text(scenario.get("density_unit"), "scenario.density_unit"),
        area_unit=_text(scenario.get("area_unit"), "scenario.area_unit"),
        currency=_text(scenario.get("currency"), "scenario.currency"),
        baseline_yield_kg_per_ha=_number(
            economics.get("baseline_yield_kg_per_ha"),
            "economics.baseline_yield_kg_per_ha",
            minimum=0,
        ),
        price_per_kg=_number(economics.get("price_per_kg"), "economics.price_per_kg", minimum=0),
        baseline_production_cost_per_ha=_number(
            economics.get("baseline_production_cost_per_ha"),
            "economics.baseline_production_cost_per_ha",
            minimum=0,
        ),
        test_cost_per_ha=_number(
            economics.get("test_cost_per_ha"), "economics.test_cost_per_ha", minimum=0
        ),
        test_cost_status=_text(economics.get("test_cost_status"), "economics.test_cost_status"),
        tolerance_density=_number(
            loss.get("tolerance_density"), "loss_function.tolerance_density", minimum=0
        ),
        minimum_relative_yield=_fraction(
            loss.get("minimum_relative_yield"), "loss_function.minimum_relative_yield"
        ),
        seinhorst_z=_fraction(loss.get("z"), "loss_function.z"),
        max_density=_number(loss.get("max_density"), "loss_function.max_density", minimum=0),
        middle_from_density=_number(
            thresholds.get("middle_from_density"),
            "grade_thresholds.middle_from_density",
            minimum=0,
        ),
        high_from_density=_number(
            thresholds.get("high_from_density"),
            "grade_thresholds.high_from_density",
            minimum=0,
        ),
        without_test=_treatment(data.get("without_test"), "without_test"),
        low=_treatment(data.get("low"), "low"),
        middle=_treatment(data.get("middle"), "middle"),
        high=_treatment(data.get("high"), "high"),
        source_note=_text(data.get("source_note"), "source_note"),
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
