"""Command-line interface for the fixed Spain protected-tomato demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .break_even import break_even_analysis
from .config import Model, load_density, load_model
from .economics import evaluate
from .reporting import (
    build_diagnostic_report,
    open_report_in_browser,
    write_diagnostic_report,
    write_english_html_report,
)


PROJECT_DIR = Path(__file__).resolve().parents[4]
CONFIG_DIR = PROJECT_DIR / "experiments" / "economic" / "configs"
DEFAULT_REPORT_DIR = (
    PROJECT_DIR / "experiments" / "economic" / "results" / "eco_model"
)


def _money(value: float, model: Model) -> str:
    return f"{value:,.2f} {model.currency}/{model.area_unit}"


def _density_unit_label(model: Model) -> str:
    return model.density_unit.replace("cm^3", "cm³")


def print_report(model: Model, density: float | None) -> None:
    program_roots, program_jumps = break_even_analysis(model, baseline="no_control")
    detection_roots, detection_jumps = break_even_analysis(
        model, baseline="uniform_control"
    )
    print(
        f"场景：{model.country}；{model.crop}；{model.nematode}；"
        f"{model.detection_timing}检测"
    )
    print(
        f"单位：密度={_density_unit_label(model)}；面积={model.area_unit}；"
        f"货币={model.currency}"
    )
    print(
        "损失公式：d<=T 时 y=1；否则 "
        "y=m+(1-m)*z^(d/T-1)，损失=1-y"
    )
    print(
        f"参数：T={model.tolerance_density:g}, "
        f"m={model.minimum_relative_yield:g}, z={model.seinhorst_z:g}"
    )
    print("\n整套检测与防治项目相对未采取防治的严格零收益密度：")
    if program_roots:
        for root in program_roots:
            benefit = evaluate(root, model).program_net_benefit_vs_no_control
            print(
                f"  {root:.4f} {_density_unit_label(model)}；"
                f"增量净收益={_money(benefit, model)}"
            )
    else:
        print("  在文献试验密度范围内不存在严格零收益密度。")
    for threshold, left, right in program_jumps:
        print(
            f"  分级阈值 {threshold:g}：左极限 {_money(left, model)} → "
            f"阈值处 {_money(right, model)}（方案切换造成跳变）"
        )
    print("\n检测分级相对未检测统一处理的严格零收益密度：")
    if detection_roots:
        for root in detection_roots:
            benefit = evaluate(root, model).detection_net_benefit_vs_uniform
            print(
                f"  {root:.4f} {_density_unit_label(model)}；"
                f"条件增量价值={_money(benefit, model)}"
            )
    else:
        print("  在文献试验密度范围内不存在严格零收益密度。")
    for threshold, left, right in detection_jumps:
        print(
            f"  分级阈值 {threshold:g}：左极限 {_money(left, model)} → "
            f"阈值处 {_money(right, model)}（方案切换造成跳变）"
        )
    if density is None:
        return

    result = evaluate(density, model)
    print(
        f"\n输入密度：{density:g} {_density_unit_label(model)}；"
        f"分级：{result.band}；方案：{result.treatment.name}"
    )
    print(
        f"正常产量保留：{result.relative_yield_fraction:.2%}；"
        f"无防治产量损失：{result.yield_loss_fraction:.2%}"
    )
    print(f"无防治毛损失：{_money(result.gross_loss, model)}")
    print(
        "未检测且未采取防治手段的净收入："
        f"{_money(result.net_income_without_test, model)}"
    )
    print(
        f"未检测采用{model.without_test.name}的净收入："
        f"{_money(result.net_income_without_test_uniform, model)}"
    )
    print(f"检测后分级处理的净收入：{_money(result.net_income_with_test, model)}")
    print("整套检测与防治项目净收益（基线：未采取防治）："
          f"{_money(result.program_net_benefit_vs_no_control, model)}")
    print("检测信息与分级决策的条件增量价值（基线：未检测统一处理）："
          f"{_money(result.detection_net_benefit_vs_uniform, model)}")
    print(
        f"预设策略：{result.treatment.name}；"
        f"当前参数下经济净收入最高：{result.economic_best_treatment.name}"
    )
    print(
        f"注意：试纸成本 {model.test_cost_per_ha:g} "
        f"{model.currency}/{model.area_unit} 为团队定价假设；"
        "本简化模型把输入密度视为已知且准确。"
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="西班牙设施番茄—南方根结线虫演示经济模型"
    )
    parser.add_argument(
        "density",
        nargs="?",
        type=float,
        help=f"可选密度位置参数，覆盖输入 JSON",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_DIR / "eco_model_example_model.json",
        help="模型参数 JSON 文件",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=CONFIG_DIR / "eco_model_example_input.json",
        help="待计算密度 JSON 文件",
    )
    parser.add_argument("--break-even-only", action="store_true", help="只输出零收益密度")
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help="诊断报告输出目录",
    )
    parser.add_argument("--no-report", action="store_true", help="不写入诊断报告")
    parser.add_argument(
        "--open",
        action="store_true",
        help="生成报告后打开中文网页（默认不自动打开）",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    try:
        model = load_model(args.config)
        density = (
            None
            if args.break_even_only
            else args.density
            if args.density is not None
            else load_density(args.input)
        )
        print_report(model, density)
        if density is not None and not args.no_report:
            report = build_diagnostic_report(model, evaluate(density, model))
            text_path, json_path, html_path = write_diagnostic_report(
                report, args.report_dir
            )
            english_html_path = write_english_html_report(report, args.report_dir)
            print(
                "\n诊断报告已保存："
                f"\n  {text_path}\n  {json_path}\n  {html_path}\n  {english_html_path}"
            )
            if args.open and not args.no_open and not open_report_in_browser(html_path):
                print("未能自动打开浏览器，请手动打开 HTML 文件。")
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
