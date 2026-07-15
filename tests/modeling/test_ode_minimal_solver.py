"""Smoke and boundary tests for the P0 Phase-0 ODE minimum solver."""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from src.modeling.ode.minimal_solver import solve_normalized_scenario, validate_config
from src.modeling.ode.run_minimal_solver import write_csv


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "experiments/ode-model/configs/minimal_normalized_scenario.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


class MinimumSolverTests(unittest.TestCase):
    def test_default_scenario_produces_one_complete_time_course(self) -> None:
        config = load_config()
        result = solve_normalized_scenario(config)

        self.assertEqual(len(result.time_hours), 161)
        self.assertEqual(result.time_hours[0], 0.0)
        self.assertEqual(result.time_hours[-1], 8.0)
        self.assertTrue(np.allclose(result.g_on[0], 0.0))
        self.assertTrue(np.allclose(result.mapk_active[0], 0.0))
        self.assertTrue(np.allclose(result.color_signal[0], 0.0))
        self.assertTrue(np.all((0.0 <= result.receptor_active) & (result.receptor_active <= 1.0)))
        self.assertTrue(np.all((0.0 <= result.g_on) & (result.g_on <= 1.0)))
        self.assertTrue(np.all((0.0 <= result.mapk_active) & (result.mapk_active <= 1.0)))
        self.assertGreater(result.color_signal[-1], 0.0)

    def test_solver_is_deterministic_and_has_an_upstream_signal_effect(self) -> None:
        config = load_config()
        first = solve_normalized_scenario(config)
        second = solve_normalized_scenario(config)
        self.assertTrue(np.allclose(first.color_signal, second.color_signal))

        no_receptor_signal = copy.deepcopy(config)
        no_receptor_signal["receptor"]["basal_activity"] = 0.0
        no_receptor_signal["receptor"]["efficacy"] = 0.0
        baseline = solve_normalized_scenario(no_receptor_signal)
        self.assertGreater(first.color_signal[-1], baseline.color_signal[-1])

    def test_rows_are_self_describing_and_writable(self) -> None:
        config = load_config()
        result = solve_normalized_scenario(config)
        rows = result.as_rows(config["scenario_id"], config["evidence_status"])
        self.assertEqual(rows[0]["scenario_id"], "phase0_normalized_single_input")
        self.assertEqual(rows[0]["evidence_status"], "scenario_prior")
        self.assertIn("gal_product_rate", rows[0])

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "timecourse.csv"
            write_csv(output_path, rows)
            with output_path.open(encoding="utf-8", newline="") as handle:
                exported = list(csv.DictReader(handle))
        self.assertEqual(len(exported), 161)
        self.assertEqual(exported[-1]["evidence_status"], "scenario_prior")

    def test_calibrated_label_and_invalid_time_grid_are_rejected(self) -> None:
        config = load_config()
        config["evidence_status"] = "calibrated"
        with self.assertRaisesRegex(ValueError, "scenario_prior"):
            validate_config(config)

        config = load_config()
        config["time"]["output_points"] = 1
        with self.assertRaisesRegex(ValueError, "at least 2"):
            validate_config(config)


if __name__ == "__main__":
    unittest.main()
