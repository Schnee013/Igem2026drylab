"""Validation tests for the P2 economic-benefit MVP.

These tests validate arithmetic and evidence plumbing only. They do not claim
local ROI calibration because sensor cost, deployment density, and local market
inputs are still HP/wet-lab variables.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import unittest

from src.modeling.economic.economic_model import (
    estimate_loss,
    evaluate_config,
    evaluate_scenario,
    interpolate_piecewise,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "experiments/economic/configs/public_mvp_framework.json"


def load_public_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


class EconomicModelValidationTests(unittest.TestCase):
    def test_piecewise_table_reproduces_ucipm_points(self) -> None:
        config = load_public_config()
        tomato = next(s for s in config["scenarios"] if s["scenario_id"] == "tomato_rkn_ucipm_500j2_public_example")
        points = tomato["yield_loss_rule"]["points"]

        expected_points = {
            0: 100,
            25: 100,
            50: 98,
            200: 88,
            500: 72,
            1000: 53,
        }
        for density, expected_normal_yield in expected_points.items():
            with self.subTest(density=density):
                self.assertEqual(interpolate_piecewise(points, density), expected_normal_yield)

    def test_piecewise_table_interpolates_between_points(self) -> None:
        config = load_public_config()
        tomato = next(s for s in config["scenarios"] if s["scenario_id"] == "tomato_rkn_ucipm_500j2_public_example")
        points = tomato["yield_loss_rule"]["points"]

        self.assertAlmostEqual(interpolate_piecewise(points, 75), 96.5)
        self.assertAlmostEqual(interpolate_piecewise(points, 225), 86.5)
        self.assertAlmostEqual(interpolate_piecewise(points, 525), 70.5)

    def test_piecewise_table_clamps_outside_ucipm_range(self) -> None:
        config = load_public_config()
        tomato = next(s for s in config["scenarios"] if s["scenario_id"] == "tomato_rkn_ucipm_500j2_public_example")
        points = tomato["yield_loss_rule"]["points"]

        self.assertEqual(interpolate_piecewise(points, -1), 100)
        self.assertEqual(interpolate_piecewise(points, 5000), 53)

    def test_empty_piecewise_table_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "piecewise rule requires at least one point"):
            interpolate_piecewise([], 100)

    def test_ucipm_200j2_golden_baseline(self) -> None:
        """UC IPM arithmetic: 30 tons/ac x $54/ton x 12% loss = $194.40/ac."""

        config = load_public_config()
        tomato = next(s for s in config["scenarios"] if s["scenario_id"] == "tomato_rkn_ucipm_500j2_public_example")
        scenario = {
            **tomato,
            "scenario_id": "tomato_rkn_ucipm_200j2_golden_baseline",
            "density_input": {"value": 200, "unit": "spring J2/kg soil"},
            "early_program_costs_per_area": [100],
        }

        row = evaluate_scenario(scenario, [0.5])[0]
        self.assertEqual(row["normal_yield_percent"], 88)
        self.assertAlmostEqual(row["yield_loss_fraction"], 0.12)
        self.assertAlmostEqual(row["gross_loss_per_area"], 194.4)
        self.assertAlmostEqual(row["break_even_early_program_cost_per_area"], 97.2)
        self.assertAlmostEqual(row["net_benefit_per_area"], -2.8)
        self.assertAlmostEqual(row["roi"], -0.028)

    def test_current_tomato_500j2_public_example(self) -> None:
        """Current public example: 30 tons/ac x $54/ton x 28% loss = $453.60/ac."""

        config = load_public_config()
        tomato = next(s for s in config["scenarios"] if s["scenario_id"] == "tomato_rkn_ucipm_500j2_public_example")

        rows = evaluate_scenario(tomato, [0.25, 0.5, 0.75])
        first_effect_rows = [r for r in rows if math.isclose(r["intervention_effect"], 0.25)]
        self.assertEqual(first_effect_rows[0]["normal_yield_percent"], 72)
        self.assertAlmostEqual(first_effect_rows[0]["yield_loss_fraction"], 0.28)
        self.assertAlmostEqual(first_effect_rows[0]["gross_loss_per_area"], 453.6)

        by_effect = {
            row["intervention_effect"]: row["break_even_early_program_cost_per_area"]
            for row in rows
            if row["early_program_cost_per_area"] == 50.0
        }
        self.assertAlmostEqual(by_effect[0.25], 113.4)
        self.assertAlmostEqual(by_effect[0.5], 226.8)
        self.assertAlmostEqual(by_effect[0.75], 340.2)

    def test_cost_accounting_identities_hold_for_monetized_rows(self) -> None:
        config = load_public_config()
        rows = evaluate_config(config)

        monetized_rows = [row for row in rows if row["gross_loss_per_area"] is not None]
        self.assertGreater(len(monetized_rows), 0)

        for row in monetized_rows:
            with self.subTest(row=row["scenario_id"], effect=row["intervention_effect"], cost=row["early_program_cost_per_area"]):
                gross_loss = row["gross_loss_per_area"]
                effect = row["intervention_effect"]
                early_cost = row["early_program_cost_per_area"]
                residual_loss = row["residual_loss_per_area"]
                break_even = row["break_even_early_program_cost_per_area"]
                net_benefit = row["net_benefit_per_area"]
                roi = row["roi"]

                self.assertAlmostEqual(residual_loss, gross_loss * (1.0 - effect))
                self.assertAlmostEqual(break_even, gross_loss - residual_loss)
                self.assertAlmostEqual(net_benefit, break_even - early_cost)
                self.assertAlmostEqual(roi, net_benefit / early_cost)

    def test_intervention_effects_are_clamped_to_probability_range(self) -> None:
        config = load_public_config()
        tomato = next(s for s in config["scenarios"] if s["scenario_id"] == "tomato_rkn_ucipm_500j2_public_example")
        scenario = {**tomato, "early_program_costs_per_area": [100]}

        rows = evaluate_scenario(scenario, [-1, 2])
        by_effect = {row["intervention_effect"]: row for row in rows}

        self.assertEqual(set(by_effect), {0.0, 1.0})
        self.assertAlmostEqual(by_effect[0.0]["break_even_early_program_cost_per_area"], 0.0)
        self.assertAlmostEqual(by_effect[1.0]["break_even_early_program_cost_per_area"], 453.6)

    def test_zero_early_cost_does_not_emit_roi(self) -> None:
        config = load_public_config()
        tomato = next(s for s in config["scenarios"] if s["scenario_id"] == "tomato_rkn_ucipm_500j2_public_example")
        scenario = {**tomato, "early_program_costs_per_area": [0]}

        row = evaluate_scenario(scenario, [0.5])[0]
        self.assertAlmostEqual(row["net_benefit_per_area"], 226.8)
        self.assertIsNone(row["roi"])

    def test_pcn_normalized_linear_rule_matches_configured_slope(self) -> None:
        config = load_public_config()
        pcn = next(s for s in config["scenarios"] if s["scenario_id"] == "potato_pcn_eppo_20egg_normalized")

        loss = estimate_loss(pcn["yield_loss_rule"], pcn["density_input"]["value"], pcn["baseline_yield_per_area"])
        self.assertAlmostEqual(loss.loss_fraction, 0.0444444444)
        self.assertAlmostEqual(loss.normal_yield_percent, 95.55555556)

    def test_linear_rule_respects_max_loss_cap(self) -> None:
        rule = {
            "type": "linear_loss_per_density_increment",
            "density_increment": 20,
            "yield_loss_per_increment": 0.2,
            "max_loss_fraction": 0.8,
        }

        loss = estimate_loss(rule, density=1000, baseline_yield_per_area=1.0)
        self.assertAlmostEqual(loss.loss_fraction, 0.8)
        self.assertAlmostEqual(loss.normal_yield_percent, 20.0)

    def test_invalid_linear_density_increment_is_rejected(self) -> None:
        rule = {
            "type": "linear_loss_per_density_increment",
            "density_increment": 0,
            "yield_loss_per_increment": 0.2,
        }

        with self.assertRaisesRegex(ValueError, "density_increment must be positive"):
            estimate_loss(rule, density=20, baseline_yield_per_area=1.0)

    def test_threshold_only_scn_does_not_emit_monetary_claims(self) -> None:
        config = load_public_config()
        rows = evaluate_config(config)
        scn_rows = [row for row in rows if row["scenario_id"] == "soybean_scn_threshold_skeleton"]

        self.assertEqual(len(scn_rows), 3)
        for row in scn_rows:
            with self.subTest(effect=row["intervention_effect"]):
                self.assertIsNone(row["normal_yield_percent"])
                self.assertIsNone(row["yield_loss_fraction"])
                self.assertIsNone(row["gross_loss_per_area"])
                self.assertIsNone(row["net_benefit_per_area"])
                self.assertIsNone(row["roi"])

    def test_public_config_row_count_and_scenario_coverage(self) -> None:
        config = load_public_config()
        rows = evaluate_config(config)

        self.assertEqual(len(rows), 21)
        self.assertEqual(
            {row["scenario_id"] for row in rows},
            {
                "tomato_rkn_ucipm_500j2_public_example",
                "potato_pcn_eppo_20egg_normalized",
                "soybean_scn_threshold_skeleton",
            },
        )


if __name__ == "__main__":
    unittest.main()
