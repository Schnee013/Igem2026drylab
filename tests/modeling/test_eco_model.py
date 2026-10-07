from __future__ import annotations

import io
import json
import math
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from src.modeling.economic.eco_model_pkg import (
    break_even_analysis,
    build_diagnostic_report,
    evaluate,
    load_density,
    load_model,
    relative_yield_fraction,
    yield_loss_fraction,
)
from src.modeling.economic.eco_model_pkg.reporting import (
    format_html_report,
    format_html_report_en,
    format_text_report,
    write_diagnostic_report,
    write_english_html_report,
)
from src.modeling.economic.eco_model_pkg.cli import main as cli_main


ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = (
    ROOT / "experiments" / "economic" / "configs" / "eco_model_example_model.json"
)
INPUT_PATH = (
    ROOT / "experiments" / "economic" / "configs" / "eco_model_example_input.json"
)


class SpainTomatoDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = load_model(MODEL_PATH)

    def test_fixed_scenario_and_units(self) -> None:
        model = self.model
        self.assertEqual(model.country, "西班牙")
        self.assertIn("设施番茄", model.crop)
        self.assertIn("Meloidogyne incognita", model.nematode)
        self.assertEqual(model.density_unit, "J2/100 cm^3 soil")
        self.assertEqual(model.area_unit, "ha")
        self.assertEqual(model.currency, "EUR")
        self.assertAlmostEqual(model.max_density, 869.6)

    def test_seinhorst_formula_is_used_directly(self) -> None:
        model = self.model
        for density in (0.0, 6.0):
            self.assertEqual(relative_yield_fraction(density, model), 1.0)
            self.assertEqual(yield_loss_fraction(density, model), 0.0)
        for density in (10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 800.0):
            expected = 0.34 + 0.66 * 0.95 ** (density / 6.0 - 1.0)
            self.assertAlmostEqual(relative_yield_fraction(density, model), expected, places=12)
        self.assertAlmostEqual(relative_yield_fraction(100.0, model), 0.6354929237, places=9)

    def test_density_outside_literature_range_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            yield_loss_fraction(-0.01, self.model)
        with self.assertRaises(ValueError):
            yield_loss_fraction(869.6001, self.model)

    def test_grade_boundaries_and_economic_baseline(self) -> None:
        low = evaluate(9.999999, self.model)
        middle = evaluate(10.0, self.model)
        high = evaluate(80.0, self.model)
        self.assertEqual(low.band, "低")
        self.assertEqual(middle.band, "中")
        self.assertEqual(high.band, "高")
        self.assertAlmostEqual(self.model.without_test.cost_per_ha, 220.0)
        self.assertAlmostEqual(self.model.without_test.avoided_loss_fraction, 0.586805)
        self.assertEqual(
            self.model.without_test.name,
            "常规统一处理（氟吡菌酰胺方案）",
        )
        self.assertEqual(self.model.low.cost_per_ha, 0.0)
        self.assertEqual(self.model.low.avoided_loss_fraction, 0.0)
        self.assertAlmostEqual(self.model.test_cost_per_ha, 5.0)
        self.assertAlmostEqual(self.model.middle_from_density, 10.0)
        self.assertAlmostEqual(self.model.high_from_density, 80.0)
        self.assertAlmostEqual(high.baseline_production_cost, 51600.0)
        self.assertAlmostEqual(
            high.net_income_with_test - high.net_income_without_test,
            high.incremental_net_benefit,
        )
        self.assertGreater(
            high.net_income_without_test_uniform,
            high.net_income_without_test,
        )
        at_100 = evaluate(100.0, self.model)
        self.assertAlmostEqual(at_100.program_net_benefit_vs_no_control, 17028.4824857)
        self.assertAlmostEqual(at_100.detection_net_benefit_vs_uniform, 496.2593745)
        self.assertAlmostEqual(at_100.detection_incremental_cost_vs_uniform, 2485.0)
        self.assertAlmostEqual(at_100.program_roi_vs_no_control, 6.2951876)
        self.assertAlmostEqual(at_100.detection_roi_vs_uniform, 0.1997020)

    def test_fixed_effects_match_reference_density_derivation(self) -> None:
        model = self.model
        untreated_loss = yield_loss_fraction(100.0, model)
        fluopyram_loss = yield_loss_fraction(100.0 * (1.0 - 0.6370), model)
        biosolarization_loss = yield_loss_fraction(100.0 * (1.0 - 0.7213), model)
        self.assertAlmostEqual(
            (untreated_loss - fluopyram_loss) / untreated_loss,
            model.middle.avoided_loss_fraction,
            places=5,
        )
        self.assertEqual(
            model.middle.effect_model,
            "fixed_avoided_loss_fraction_at_reference_density",
        )
        self.assertEqual(model.middle.effect_reference_density, 100.0)
        self.assertEqual(model.middle.study_density_min, 50.0)
        self.assertIn("不代表所有初始密度", model.middle.effect_basis_note)
        self.assertAlmostEqual(
            (untreated_loss - biosolarization_loss) / untreated_loss,
            model.high.avoided_loss_fraction,
            places=5,
        )

    def test_break_even_roots_are_true_zeros(self) -> None:
        program_roots, program_jumps = break_even_analysis(
            self.model, baseline="no_control"
        )
        detection_roots, detection_jumps = break_even_analysis(
            self.model, baseline="uniform_control"
        )
        self.assertEqual(program_roots, [])
        self.assertEqual(len(program_jumps), 2)
        self.assertAlmostEqual(detection_roots[0], 6.8320749, places=6)
        self.assertEqual(len(detection_jumps), 2)
        self.assertAlmostEqual(detection_jumps[1][0], 80.0)
        self.assertLess(detection_jumps[1][1], 0)
        self.assertGreater(detection_jumps[1][2], 0)

    def test_report_is_plain_language_and_uses_new_structure(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(100.0, self.model))
        self.assertEqual(report["scenario"]["currency"], "EUR")
        self.assertEqual(report["thresholds"]["expected_loss_begins_near"], 6.0)
        self.assertEqual(report["thresholds"]["action_from_density"], 10.0)
        self.assertEqual(report["thresholds"]["high_from_density"], 80.0)
        self.assertEqual(len(report["treatment_options"]), 3)
        self.assertGreaterEqual(len(report["references"]), 9)
        text = format_text_report(report)
        html = format_html_report(report)
        self.assertIn("J2/100 cm³ soil", text)
        self.assertNotIn("cm^3", text)
        self.assertIn("EUR/ha", text)
        self.assertNotIn("USD/mu", text)
        self.assertNotIn("J2/kg", text)
        self.assertIn("线虫检测试纸经济效益模拟报告", html)
        self.assertIn("西班牙", html)
        self.assertIn("设施番茄", html)
        self.assertIn("Meloidogyne incognita", html)
        self.assertIn("鸡粪生物太阳能消毒", html)
        self.assertIn("两种收益比较", html)
        self.assertIn("未采取防治手段", html)
        self.assertIn("<h3>未采取防治手段</h3>", html)
        self.assertIn("<h3>常规统一处理（氟吡菌酰胺方案）</h3>", html)
        self.assertEqual(html.count('<article class="strategy-group">'), 2)
        self.assertEqual(html.count('<div class="strategy sub-strategy">'), 3)
        self.assertEqual(html.count('<article class="strategy">'), 0)
        self.assertEqual(html.count('<div class="no-test-grid with-test-grid">'), 1)
        self.assertEqual(html.count('<div class="summary-content">'), 4)
        self.assertEqual(html.count('<div class="summary-notes">'), 4)
        summary_markup = html.split('<div class="summary-grid">', 1)[1].split(
            "\n\n  <section>", 1
        )[0]
        self.assertNotIn("20,000 kg/ha", summary_markup)
        self.assertNotIn("0.375 L/ha", summary_markup)
        self.assertIn("J2/100 cm³ soil", html)
        self.assertNotIn("cm^3", html)
        self.assertEqual(html.count('class="muted profit-caption">预计单季利润'), 3)
        self.assertIn("如不采取防治手段，预计产量损失", html)
        self.assertIn("常用线虫检测方法成本对比", html)
        self.assertIn("5.00 EUR/ha", html)
        self.assertIn("31.55 EUR/ha", html)
        self.assertIn("15.80 EUR/ha", html)
        self.assertIn("152.14 EUR/ha", html)
        self.assertNotIn("团队定价，EUR/ha", html)
        self.assertNotIn("首项判定/样", html)
        self.assertNotIn("ILVO 公开价", html)
        self.assertIn("净收益、盈亏平衡与敏感性", html)
        self.assertIn("扣除成本后的净收益（EUR/ha）", html)
        self.assertIn("整套检测与防治项目净收益", html)
        self.assertIn("检测信息与分级决策的条件增量价值", html)
        self.assertIn("+17,028.48 EUR/ha", html)
        self.assertIn("+496.26 EUR/ha", html)
        self.assertIn("629.52%", html)
        self.assertIn("19.97%", html)
        self.assertIn("本团队试纸成本比所列实验室公开收费低约68%–97%，且操作更为简便。", html)
        self.assertIn('<div class="cost-footnote">实验室费用按每公顷提交1份代表性样品换算；未计采样、寄送、税费或额外前处理。</div>', html)
        self.assertNotIn('<p class="section-kicker">', html)
        self.assertEqual(html.count("<circle "), 2)
        self.assertIn("预计避免作物损失", html)
        self.assertNotIn("预计避免损失", html)
        self.assertEqual(html.count('<article class="execution-card">'), 1)
        self.assertIn("横轴显示至500", html)
        self.assertIn("参考文献", html)
        self.assertIn("预设演示策略", html)
        self.assertIn("当前参数下经济净收入最高", html)
        self.assertIn("固定69.1234%避免损失比例", html)
        self.assertIn("每公顷提交1份代表性样品", html)
        self.assertNotIn("损失公式", html)
        self.assertNotIn("Seinhorst", html)
        self.assertNotIn("核算边界", html)
        self.assertNotIn('<span class="section-no">06</span>', html)
        self.assertNotIn('<span class="section-no">07</span>', html)
        self.assertNotIn('href="尚需', html)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_diagnostic_report(report, directory)
            self.assertTrue(all(path.exists() for path in paths))
            payload = json.loads(paths[1].read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 9)
            self.assertIn("program_vs_no_control", payload["break_even"])
            self.assertIn("detection_vs_uniform", payload["break_even"])

    def test_high_density_report_has_support_warning(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(800.0, self.model))
        self.assertTrue(report["diagnosis"]["above_biosolarization_support"])
        html = format_html_report(report)
        self.assertIn("高密度提示", html)
        self.assertIn("超过横轴显示范围", html)
        self.assertEqual(html.count("<circle "), 0)

    def test_low_density_efficacy_extrapolation_is_flagged(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(20.0, self.model))
        self.assertTrue(report["diagnosis"]["effect_scope_warning"])
        self.assertEqual(len(report["diagnosis"]["effect_scope_warnings"]), 2)
        self.assertIn(
            "共享", report["diagnosis"]["effect_scope_warnings"][0]["role"]
        )
        html = format_html_report(report)
        english = format_html_report_en(report)
        self.assertIn("防效外推提示", html)
        self.assertIn("Effect extrapolation", english)

    def test_low_density_sensitivity_includes_uniform_control_baseline(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(6.8, self.model))
        self.assertAlmostEqual(
            report["diagnosis"]["detection_net_benefit_vs_uniform"],
            8.2595281,
            places=6,
        )
        baseline_effect = next(
            row
            for row in report["sensitivity_analysis"]
            if row["parameter"] == "固定避免损失比例"
            and row["change"] == "×1.2"
            and row["scope"].startswith("未检测统一处理基线")
        )
        self.assertAlmostEqual(
            baseline_effect["detection_net_benefit_vs_uniform"],
            -33.0885663,
            places=6,
        )
        self.assertFalse(baseline_effect["detection_worthwhile"])
        warnings = report["diagnosis"]["effect_scope_warnings"]
        self.assertEqual(len(warnings), 2)
        self.assertIn("未检测统一处理基线", warnings[0]["role"])
        html = format_html_report(report)
        english = format_html_report_en(report)
        self.assertIn("作用方案", html)
        self.assertIn("未检测统一处理基线（共享）：40%氟吡菌酰胺制剂", html)
        self.assertIn("-33.09 EUR/ha", html)
        self.assertIn("Applies to", english)
        self.assertIn("Uniform-control baseline", english)

    def test_text_report_includes_sensitivity_reversal_and_scope_warnings(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(6.8, self.model))
        text = format_text_report(report)
        self.assertIn("+8.26 EUR/ha", text)
        self.assertIn("-33.09 EUR/ha；检测是否增益：否", text)
        self.assertIn("单因素敏感性", text)
        self.assertIn("不是置信区间", text)
        for row in report["sensitivity_analysis"]:
            self.assertIn(f"{row['parameter']} {row['change']}；作用方案：{row['scope']}", text)
        self.assertIn("防效外推提示", text)
        for warning in report["diagnosis"]["effect_scope_warnings"]:
            self.assertIn(f"{warning['role']}：{warning['treatment']}", text)
        high_text = format_text_report(
            build_diagnostic_report(self.model, evaluate(800.0, self.model))
        )
        self.assertIn("高密度提示：本次输入超过约759", high_text)

    def test_unselected_high_option_has_warning_in_all_report_formats(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(20.0, self.model))
        warnings = report["diagnosis"]["effect_scope_warnings"]
        high_warning = next(w for w in warnings if w["treatment"] == self.model.high.name)
        self.assertEqual(high_warning["role"], "经济比较备选方案")
        for rendered in (format_text_report(report), format_html_report(report)):
            self.assertIn("经济比较备选方案：鸡粪生物太阳能消毒", rendered)
            self.assertIn("约50 J2/100 cm³及以上", rendered)
        english = format_html_report_en(report)
        self.assertIn("Alternative in economic comparison: Chicken-manure biosolarization", english)
        self.assertNotRegex(english, r"[\u4e00-\u9fff]")
        in_range = build_diagnostic_report(self.model, evaluate(100.0, self.model))
        self.assertEqual(in_range["diagnosis"]["effect_scope_warnings"], [])

    def test_uniform_control_with_distinct_support_is_checked_separately(self) -> None:
        model = replace(
            self.model,
            without_test=replace(self.model.without_test, study_density_max=90.0),
        )
        report = build_diagnostic_report(model, evaluate(100.0, model))
        warnings = report["diagnosis"]["effect_scope_warnings"]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["role"], "未检测统一处理基线")
        self.assertIn("约50–90 J2/100 cm³", format_text_report(report))
        self.assertIn("approximately 50–90 J2/100 cm³", format_html_report_en(report))

    def test_shared_middle_treatment_sensitivity_changes_both_sides(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(20.0, self.model))
        shared_effect_rows = [
            row
            for row in report["sensitivity_analysis"]
            if row["parameter"] == "固定避免损失比例"
        ]
        self.assertEqual(len(shared_effect_rows), 2)
        self.assertTrue(all("共享参数" in row["scope"] for row in shared_effect_rows))
        self.assertTrue(
            all(
                abs(row["detection_net_benefit_vs_uniform"] + 5.0) < 1e-8
                for row in shared_effect_rows
            )
        )

    def test_english_web_report_matches_chinese_structure_and_values(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(100.0, self.model))
        chinese = format_html_report(report)
        english = format_html_report_en(report)
        self.assertIn('<html lang="zh-CN">', chinese)
        self.assertIn('<html lang="en">', english)
        self.assertIn("Nematode Test-Strip Economic Benefit Simulation", english)
        self.assertIn("Protected tomato", english)
        self.assertIn("Southern root-knot nematode", english)
        self.assertIn("Chicken-manure biosolarization", english)
        self.assertIn("+17,028.48 EUR/ha", english)
        self.assertIn("+496.26 EUR/ha", english)
        self.assertIn("36.45%", english)
        self.assertIn("Yield loss without control", english)
        self.assertIn("With test strip and recommended treatment", english)
        self.assertIn(".summary-card .value{left:16px;right:16px;", english)
        self.assertIn("white-space:nowrap", english)
        self.assertIn(".sub-strategy h3{min-height:2.15em", english)
        self.assertIn(".sub-strategy .income{margin-top:.1rem}", english)
        self.assertNotIn("Expected yield loss without control", english)
        self.assertNotIn(
            "Test strip used and recommended treatment applied", english
        )
        self.assertNotRegex(english, r"[\u4e00-\u9fff]")
        profit_section = english.split('<span class="section-no">01</span>', 1)[1].split(
            '<span class="section-no">02</span>', 1
        )[0]
        self.assertIn("<h3>Chicken-manure biosolarization</h3>", profit_section)
        self.assertNotIn("20,000 kg/ha", profit_section)
        plans_section = english.split('<span class="section-no">03</span>', 1)[1].split(
            '<span class="section-no">04</span>', 1
        )[0]
        self.assertIn(
            '<h3>40% fluopyram formulation<span class="plan-dose">0.375 L/ha</span></h3>',
            plans_section,
        )
        self.assertIn(
            '<h3>Chicken-manure biosolarization<span class="plan-dose">20,000 kg/ha</span></h3>',
            plans_section,
        )
        self.assertIn(
            '<h3>鸡粪生物太阳能消毒<span class="plan-dose">20,000 kg/ha</span></h3>',
            chinese,
        )
        for marker in (
            '<span class="section-no">',
            '<div class="summary-card">',
            '<article class="strategy-group">',
            '<article class="plan-card ',
            '<article class="execution-card">',
        ):
            self.assertEqual(english.count(marker), chinese.count(marker))
        english_summary = english.split('<div class="summary-grid">', 1)[1].split(
            "\n\n  <section>", 1
        )[0]
        self.assertNotIn("20,000 kg/ha", english_summary)
        self.assertNotIn("0.375 L/ha", english_summary)
        with tempfile.TemporaryDirectory() as directory:
            path = write_english_html_report(report, directory)
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "diagnostic_report_en.html")
            self.assertEqual(path.read_text(encoding="utf-8"), english)

    def test_config_changes_flow_to_both_reports_without_hardcoded_overrides(self) -> None:
        payload = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
        payload["economics"]["test_cost_per_ha"] = 12.0
        payload["high"]["name"] = "配置中的高等级方案"
        payload["high"]["name_en"] = "Configured high-tier plan"
        payload["high"]["application_rate"] = "配置剂量"
        payload["high"]["application_rate_en"] = "configured dose"
        payload["high"]["plan_overview_en"] = "Configured English instructions."
        payload["detection_cost_comparison"]["samples_per_ha"] = 2.0
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            model = load_model(path)
            report = build_diagnostic_report(model, evaluate(100.0, model))
            text = format_text_report(report)
            chinese = format_html_report(report)
            english = format_html_report_en(report)
        self.assertIn("配置中的高等级方案", chinese)
        self.assertIn("配置剂量", chinese)
        self.assertIn("Configured high-tier plan", english)
        self.assertIn("configured dose", english)
        self.assertIn("Configured English instructions.", english)
        self.assertIn("12.00 EUR/ha", english)
        self.assertIn("63.10 EUR/ha", english)
        self.assertIn("2 representative samples", english)
        self.assertIn("每公顷2份代表性样品", text)
        self.assertIn("approximately 62%–96% less", english)

    def test_preset_tier_is_distinct_from_economic_best_option(self) -> None:
        expensive_high = replace(self.model.high, cost_per_ha=20000.0)
        scenario = replace(self.model, high=expensive_high)
        result = evaluate(100.0, scenario)
        self.assertEqual(result.treatment_key, "high")
        self.assertEqual(result.economic_best_key, "middle")
        self.assertGreater(result.preset_opportunity_cost, 0)
        report = build_diagnostic_report(scenario, result)
        high = next(item for item in report["treatment_options"] if item["key"] == "high")
        middle = next(item for item in report["treatment_options"] if item["key"] == "middle")
        self.assertTrue(high["is_preset"])
        self.assertTrue(middle["is_economic_best"])

    def test_cli_does_not_open_browser_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            argv = ["eco_model", "100", "--report-dir", directory]
            with patch("sys.argv", argv), patch(
                "src.modeling.economic.eco_model_pkg.cli.open_report_in_browser"
            ) as opener, redirect_stdout(io.StringIO()):
                cli_main()
            opener.assert_not_called()
            self.assertTrue((Path(directory) / "diagnostic_report.html").exists())
            self.assertTrue((Path(directory) / "diagnostic_report_en.html").exists())

    def test_low_density_plan_and_current_execution_only(self) -> None:
        report = build_diagnostic_report(self.model, evaluate(5.0, self.model))
        html = format_html_report(report)
        text = format_text_report(report)
        self.assertEqual(report["diagnosis"]["treatment"], "不进行专项防治")
        self.assertIn("不额外施用杀线虫剂", html)
        self.assertEqual(html.count('<article class="execution-card">'), 1)
        self.assertNotIn("40%氟吡菌酰胺0.375 L/ha作为中等级代表方案", html)
        self.assertIn("低等级｜不进行专项防治", text)

    def test_input_schema(self) -> None:
        input_payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(load_density(INPUT_PATH), float(input_payload["density"]))
        with tempfile.TemporaryDirectory() as directory:
            old_input = Path(directory) / "old.json"
            old_input.write_text('{"density_j2_per_kg": 100}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_density(old_input)
            wrong_unit = Path(directory) / "wrong-unit.json"
            wrong_unit.write_text(
                '{"density": 100, "density_unit": "J2/kg soil"}',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_density(wrong_unit)


if __name__ == "__main__":
    unittest.main()
