"""Focused tests for the Phase-2B two-parameter surface runner."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from src.modeling.ode.focused_two_parameter_surface import (
    _default_evaluator,
    additive_interaction_residuals,
    build_surface_grid,
    load_surface_inputs,
    load_surface_points,
    run_focused_surface,
    summarize_surface,
)
from src.modeling.ode.minimal_solver import solve_normalized_scenario


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = (
    ROOT
    / "experiments/ode-model/configs/phase2b_focused_two_parameter_surface.json"
)


class FocusedTwoParameterSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.analysis,
            cls.contract,
            cls.baseline,
            cls.parameters,
            cls.ligand,
            *_rest,
        ) = load_surface_inputs(CONFIG_PATH)

    def test_contract_fixes_pair_condition_metric_and_registered_ranges(self) -> None:
        self.assertEqual(self.analysis["parameter_ids"], ["gain_out", "K_out"])
        self.assertEqual(
            self.analysis["ligand_context_id"], "transition_reference"
        )
        self.assertEqual(self.ligand, 1.0)
        self.assertEqual(self.analysis["copy_number"], 1)
        self.assertEqual(self.analysis["metric_id"], "color_8h")
        stages = [row["stage"] for row in self.contract["analysis_sequence"]]
        self.assertIn("focused_two_parameter_surfaces", stages)
        unit_gain, gain, unit_half, half = build_surface_grid(self.parameters, 7)
        np.testing.assert_allclose(unit_gain, np.linspace(0.0, 1.0, 7))
        np.testing.assert_allclose(unit_half, np.linspace(0.0, 1.0, 7))
        self.assertAlmostEqual(float(gain[0]), 0.1)
        self.assertAlmostEqual(float(gain[-1]), 1.0)
        self.assertAlmostEqual(float(half[0]), 0.025)
        self.assertAlmostEqual(float(half[-1]), 2.5)

    def test_default_evaluator_uses_eight_hour_endpoint_for_longer_run(self) -> None:
        config = copy.deepcopy(self.baseline)
        config["time"]["duration_hours"] = 10.0
        config["time"]["output_points"] = 201

        long_run = solve_normalized_scenario(config)
        eight_hour_index = int(np.flatnonzero(long_run.time_hours == 8.0)[0])
        evaluated = _default_evaluator(config)

        self.assertAlmostEqual(
            evaluated,
            float(long_run.color_signal[eight_hour_index]),
            places=8,
        )
        self.assertNotAlmostEqual(
            evaluated,
            float(long_run.color_signal[-1]),
            places=6,
        )

    def test_additive_surface_has_zero_interaction_residual(self) -> None:
        row_effect = np.asarray([1.0, 2.0, 4.0])[:, None]
        column_effect = np.asarray([0.5, 1.5, 3.5, 7.5])[None, :]
        values = row_effect + column_effect
        residual = additive_interaction_residuals(values)
        np.testing.assert_allclose(residual, 0.0, atol=1e-12)
        summary = summarize_surface(values)
        self.assertAlmostEqual(
            float(summary["interaction_residual_max_abs"]), 0.0
        )

    def test_stubbed_runner_writes_reproducible_complete_grid_and_plot(
        self,
    ) -> None:
        def evaluator(config):
            gain = float(config["gal_output"]["gain_rate"])
            half = float(config["gal_output"]["half_activation"])
            return gain / (gain + half)

        with tempfile.TemporaryDirectory() as directory:
            first_dir = Path(directory) / "first"
            second_dir = Path(directory) / "second"
            first = run_focused_surface(
                CONFIG_PATH, first_dir, metric_evaluator=evaluator
            )
            second = run_focused_surface(
                CONFIG_PATH, second_dir, metric_evaluator=evaluator
            )
            self.assertEqual(first["surface_point_count"], 49)
            self.assertEqual(first["model_solve_count"], 49)
            self.assertEqual(
                first["outputs"]["surface_points"],
                second["outputs"]["surface_points"],
            )
            self.assertEqual(
                (first_dir / "surface_points.csv").read_bytes(),
                (second_dir / "surface_points.csv").read_bytes(),
            )
            rows = load_surface_points(first_dir / "surface_points.csv")
            self.assertEqual(len(rows), 49)
            plot_path = first_dir / "gain_out_by_K_out_surface.png"
            self.assertTrue(plot_path.is_file())
            self.assertGreater(plot_path.stat().st_size, 10_000)
            metadata = json.loads(
                (first_dir / "run_metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["grid_points_each"], 7)
            self.assertTrue(
                all(math.isfinite(float(row["color_8h"])) for row in rows)
            )

    def test_non_finite_surface_output_identifies_grid_point(self) -> None:
        def evaluator(config):
            if float(config["gal_output"]["gain_rate"]) > 0.5:
                return float("nan")
            return 1.0

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                ValueError, "non-finite surface output at gain index"
            ):
                run_focused_surface(
                    CONFIG_PATH,
                    Path(directory),
                    metric_evaluator=evaluator,
                )


if __name__ == "__main__":
    unittest.main()
