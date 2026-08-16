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

    def test_near_zero_signal_boundary_preserves_bounded_solver_states(self) -> None:
        config = load_config()
        config["input"]["ligand_normalized"] = 0.3
        config["receptor"].update(
            basal_activity=0.0,
            efficacy=0.9,
            half_activation_normalized=100.0,
            hill_coefficient=2.1666666666666665,
        )
        config["g_protein"].update(
            coupling_rate_per_hour=0.05,
            deactivation_rate_per_hour=0.9694956105143481,
        )
        config["mapk"].update(
            activation_rate_per_hour=0.46415888336127786,
            deactivation_rate_per_hour=0.6463304070095649,
        )
        config["transcription"].update(
            basal_activity=0.0,
            efficacy=0.1,
            half_activation=0.1160397208403195,
            hill_coefficient=1.3333333333333335,
        )
        config["gal_output"].update(
            leak_rate=0.0,
            gain_rate=0.4641588833612779,
            half_activation=2.5000000000000013,
        )
        config["color"].update(
            production_rate_per_hour=0.4641588833612779,
            loss_rate_per_hour=0.258532162803826,
        )

        result = solve_normalized_scenario(config)

        self.assertTrue(np.all((0.0 <= result.g_on) & (result.g_on <= 1.0)))
        self.assertTrue(np.all((0.0 <= result.mapk_active) & (result.mapk_active <= 1.0)))
        self.assertTrue(np.all(np.isfinite(result.color_signal)))

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
            self.assertNotIn(b"\r\n", output_path.read_bytes())
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

    def test_config_validation_rejects_non_finite_fractional_and_boolean_values(self) -> None:
        invalid_cases = (
            (("time", "output_points"), 2.9, "integer"),
            (("time", "output_points"), True, "integer"),
            (("input", "ligand_normalized"), float("nan"), "finite"),
            (("receptor", "efficacy"), float("inf"), "finite"),
            (("g_protein", "coupling_rate_per_hour"), "1.2", "finite number"),
            (("gal_output", "copy_number"), 1.5, "integer"),
            (("gal_output", "copy_number"), False, "integer"),
        )
        for path, value, message in invalid_cases:
            with self.subTest(path=path, value=value):
                config = load_config()
                config[path[0]][path[1]] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_config(config)

    def test_config_validation_rejects_unknown_and_missing_fields(self) -> None:
        config = load_config()
        config["unexpected"] = 1
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            validate_config(config)

        config = load_config()
        config["receptor"]["unexpected"] = 1
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            validate_config(config)

        config = load_config()
        del config["g_protein"]["coupling_rate_per_hour"]
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            validate_config(config)


if __name__ == "__main__":
    unittest.main()
