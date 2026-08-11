"""Focused non-ODE tests for the Phase-2B conditional Sobol runner."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from src.modeling.ode.sobol_sensitivity import (
    build_saltelli_design,
    build_sample_manifest,
    estimate_sobol_indices,
    evaluate_design,
    ishigami,
    load_sobol_inputs,
    run_sobol_analysis,
    transform_unit_samples,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "experiments/ode-model/configs/phase2b_sobol_sensitivity.json"


class SobolSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.analysis,
            cls.contract,
            _,
            cls.parameters,
            cls.contexts,
            cls.copy_numbers,
            cls.metric_rows,
            _,
            _,
            _,
        ) = load_sobol_inputs(CONFIG_PATH)

    def parameter(self, parameter_id: str) -> dict[str, str]:
        return next(row for row in self.parameters if row["parameter_id"] == parameter_id)

    def test_contract_fixes_preflight_dimensions_and_sequence(self) -> None:
        self.assertEqual(
            [row["parameter_id"] for row in self.parameters],
            [
                "b_TF",
                "k_color_loss",
                "gain_out",
                "K_out",
                "k_color_prod",
                "K_TF",
                "k_mapk_on",
                "k_couple",
            ],
        )
        self.assertEqual([row[1] for row in self.contexts], self.analysis["ligand_context_ids"])
        self.assertEqual(self.copy_numbers, [1, 4])
        self.assertEqual(len(self.metric_rows), 4)
        stages = [row["stage"] for row in self.contract["analysis_sequence"]]
        self.assertLess(
            stages.index("conditional_subset_sobol"),
            stages.index("focused_two_parameter_surfaces"),
        )

    def test_scrambled_sobol_design_is_reproducible_and_manifested(self) -> None:
        first = build_saltelli_design(
            3, base_sample_size=8, random_seed=20260809, second_order=False
        )
        second = build_saltelli_design(
            3, base_sample_size=8, random_seed=20260809, second_order=False
        )
        np.testing.assert_array_equal(first.unit_a, second.unit_a)
        np.testing.assert_array_equal(first.unit_b, second.unit_b)
        self.assertEqual(first.design_row_count, 8 * (3 + 2))
        self.assertTrue(np.all((first.unit_a >= 0.0) & (first.unit_a <= 1.0)))
        parameters = self.parameters[:3]
        manifest = build_sample_manifest(first, parameters)
        self.assertEqual(len(manifest), first.design_row_count)
        self.assertEqual(manifest[0]["matrix_id"], "A")
        self.assertEqual(manifest[8]["matrix_id"], "B")
        self.assertEqual(manifest[16]["matrix_id"], f"AB_{parameters[0]['parameter_id']}")
        self.assertEqual(
            [row["design_row"] for row in manifest],
            list(range(1, first.design_row_count + 1)),
        )

    def test_second_order_design_has_registered_sample_count(self) -> None:
        design = build_saltelli_design(
            3, base_sample_size=8, random_seed=20260809, second_order=True
        )
        self.assertEqual(design.design_row_count, 8 * (2 * 3 + 2))
        self.assertIsNotNone(design.unit_ba)
        self.assertEqual(len(design.unit_ab), 3)
        self.assertEqual(len(design.unit_ba or ()), 3)

    def test_distribution_mapping_respects_bounds_and_midpoints(self) -> None:
        parameters = [self.parameter("b_TF"), self.parameter("K_out")]
        physical = transform_unit_samples(
            np.asarray([[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]]), parameters
        )
        np.testing.assert_allclose(physical[:, 0], [0.0, 0.05, 0.1])
        np.testing.assert_allclose(physical[:, 1], [0.025, 0.25, 2.5])

    def test_ishigami_matches_analytic_first_total_and_pair_indices(self) -> None:
        parameter_ids = ["x1", "x2", "x3"]
        design = build_saltelli_design(
            3, base_sample_size=4096, random_seed=20260809, second_order=True
        )
        outputs = evaluate_design(design, parameter_ids, ishigami)
        estimates = estimate_sobol_indices(design, parameter_ids, outputs)
        shifted = {block: values + 1000.0 for block, values in outputs.items()}
        shifted_estimates = estimate_sobol_indices(design, parameter_ids, shifted)
        by_parameter = {row["parameter_id"]: row for row in estimates["parameters"]}
        shifted_by_parameter = {
            row["parameter_id"]: row for row in shifted_estimates["parameters"]
        }
        expected = {
            "x1": (0.3139, 0.5576),
            "x2": (0.4424, 0.4424),
            "x3": (0.0, 0.2437),
        }
        for parameter_id, (s1, st) in expected.items():
            self.assertAlmostEqual(by_parameter[parameter_id]["S1"], s1, delta=0.015)
            self.assertAlmostEqual(by_parameter[parameter_id]["ST"], st, delta=0.015)
            self.assertAlmostEqual(
                shifted_by_parameter[parameter_id]["S1"],
                by_parameter[parameter_id]["S1"],
                places=12,
            )
            self.assertAlmostEqual(
                shifted_by_parameter[parameter_id]["ST"],
                by_parameter[parameter_id]["ST"],
                places=12,
            )
        by_pair = {
            (row["parameter_i"], row["parameter_j"]): row["S2"]
            for row in estimates["pairs"]
        }
        self.assertAlmostEqual(by_pair[("x1", "x3")], 0.2437, delta=0.02)
        self.assertAlmostEqual(by_pair[("x1", "x2")], 0.0, delta=0.02)
        self.assertAlmostEqual(by_pair[("x2", "x3")], 0.0, delta=0.02)

    def test_non_finite_output_reports_block_and_sample(self) -> None:
        parameter_ids = ["x1", "x2"]
        design = build_saltelli_design(
            2, base_sample_size=8, random_seed=20260809, second_order=False
        )
        outputs = evaluate_design(design, parameter_ids, lambda point: float(np.sum(point)))
        outputs["AB_x2"][3] = float("nan")
        with self.assertRaisesRegex(
            ValueError, "non-finite Sobol output in block AB_x2 at base sample 3"
        ):
            estimate_sobol_indices(design, parameter_ids, outputs)

    def test_stubbed_runner_writes_reproducible_manifest_and_indices_without_ode(self) -> None:
        def stub_evaluator(config, metric_ids, ratio_policy, matched_control_cache):
            del ratio_policy, matched_control_cache
            value = (
                float(config["transcription"]["basal_activity"])
                + float(config["transcription"]["half_activation"])
                + float(config["gal_output"]["gain_rate"])
                + float(config["gal_output"]["half_activation"])
                + float(config["color"]["production_rate_per_hour"])
                + float(config["color"]["loss_rate_per_hour"])
                + float(config["mapk"]["activation_rate_per_hour"])
                + float(config["g_protein"]["coupling_rate_per_hour"])
            )
            return {metric_id: value for metric_id in metric_ids}, 1, False

        with tempfile.TemporaryDirectory() as directory:
            first_dir = Path(directory) / "first"
            second_dir = Path(directory) / "second"
            first = run_sobol_analysis(
                CONFIG_PATH,
                first_dir,
                base_sample_size=8,
                bootstrap_replicates=16,
                metric_evaluator=stub_evaluator,
            )
            second = run_sobol_analysis(
                CONFIG_PATH,
                second_dir,
                base_sample_size=8,
                bootstrap_replicates=16,
                metric_evaluator=stub_evaluator,
            )
            self.assertEqual(first["design_row_count"], 80)
            self.assertEqual(first["model_solve_count"], 480)
            self.assertEqual(first["index_row_count"], 176)
            self.assertEqual(first["second_order_row_count"], 0)
            self.assertEqual(first["outputs"], second["outputs"])
            self.assertEqual(
                (first_dir / "sample_manifest.csv").read_bytes(),
                (second_dir / "sample_manifest.csv").read_bytes(),
            )
            self.assertEqual(
                (first_dir / "sobol_indices.csv").read_bytes(),
                (second_dir / "sobol_indices.csv").read_bytes(),
            )
            with (first_dir / "sample_manifest.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(len(manifest), 80)
            metadata = json.loads(
                (first_dir / "run_metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["base_sample_size"], 8)
            self.assertFalse(metadata["second_order"])
            with (first_dir / "sobol_indices.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                indices = list(csv.DictReader(handle))
            self.assertTrue(all(math.isfinite(float(row["S1"])) for row in indices))


if __name__ == "__main__":
    unittest.main()
