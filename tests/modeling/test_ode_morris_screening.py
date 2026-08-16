"""Focused tests for the Phase-2B Morris screening slice."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from src.modeling.ode.morris_screening import (
    build_morris_trajectories,
    load_morris_inputs,
    morris_delta,
    normalized_to_physical,
    run_morris_screening,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "experiments/ode-model/configs/phase2b_morris_screening.json"


class MorrisScreeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.analysis,
            _,
            _,
            cls.parameters,
            cls.contexts,
            cls.copy_numbers,
            cls.metric_rows,
            _,
            _,
            _,
        ) = load_morris_inputs(CONFIG_PATH)

    def parameter(self, parameter_id: str) -> dict[str, str]:
        return next(row for row in self.parameters if row["parameter_id"] == parameter_id)

    def test_contract_drives_screening_dimensions(self) -> None:
        self.assertEqual(len(self.parameters), 17)
        self.assertEqual(len(self.contexts), 5)
        self.assertEqual(self.copy_numbers, [1, 2, 4])
        self.assertEqual(len(self.analysis["metric_ids"]), 12)
        self.assertNotIn(
            "time_to_readout_threshold",
            {row["metric_id"] for row in self.metric_rows},
        )

    def test_trajectories_are_reproducible_one_at_a_time(self) -> None:
        first = build_morris_trajectories(
            3, num_levels=4, trajectory_count=4, random_seed=20260807
        )
        second = build_morris_trajectories(
            3, num_levels=4, trajectory_count=4, random_seed=20260807
        )
        delta = morris_delta(4)
        self.assertEqual(delta, 2.0 / 3.0)
        for left, right in zip(first, second, strict=True):
            np.testing.assert_allclose(left.points, right.points)
            self.assertEqual(left.parameter_order, right.parameter_order)
            self.assertEqual(left.points.shape, (4, 3))
            self.assertTrue(np.all((left.points >= 0) & (left.points <= 1)))
            differences = np.diff(left.points, axis=0)
            self.assertTrue(np.all(np.count_nonzero(np.abs(differences) > 1e-12, axis=1) == 1))
            np.testing.assert_allclose(np.max(np.abs(differences), axis=1), delta)
            self.assertEqual(set(left.parameter_order), {0, 1, 2})

    def test_distribution_mapping_respects_uniform_and_loguniform_ranges(self) -> None:
        uniform = self.parameter("n_R")
        loguniform = self.parameter("K_R")
        self.assertAlmostEqual(normalized_to_physical(uniform, 0.0), 0.5)
        self.assertAlmostEqual(normalized_to_physical(uniform, 1.0), 3.0)
        self.assertAlmostEqual(normalized_to_physical(loguniform, 0.0), 0.01)
        self.assertAlmostEqual(normalized_to_physical(loguniform, 1.0), 100.0)
        self.assertAlmostEqual(normalized_to_physical(loguniform, 0.5), 1.0)

    def test_minimal_slice_writes_reproducible_effects_and_summary(self) -> None:
        kwargs = {
            "parameter_ids": ["K_R", "n_R", "k_couple"],
            "ligand_context_ids": ["transition_low_diagnostic"],
            "copy_numbers": [1],
            "metric_ids": ["color_8h"],
            "trajectory_count": 4,
        }
        with tempfile.TemporaryDirectory() as directory:
            first_dir = Path(directory) / "first"
            second_dir = Path(directory) / "second"
            first = run_morris_screening(CONFIG_PATH, first_dir, **kwargs)
            second = run_morris_screening(CONFIG_PATH, second_dir, **kwargs)
            self.assertEqual(first["elementary_effect_row_count"], 12)
            self.assertEqual(first["summary_row_count"], 3)
            self.assertEqual(first["model_solve_count"], 16)
            self.assertEqual(first["outputs"], second["outputs"])
            self.assertEqual(
                (first_dir / "elementary_effects.csv").read_bytes(),
                (second_dir / "elementary_effects.csv").read_bytes(),
            )
            self.assertEqual(
                (first_dir / "morris_summary.csv").read_bytes(),
                (second_dir / "morris_summary.csv").read_bytes(),
            )
            with (first_dir / "elementary_effects.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                effects = list(csv.DictReader(handle))
            with (first_dir / "morris_summary.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                summary = list(csv.DictReader(handle))
            self.assertEqual({row["parameter_id"] for row in effects}, set(kwargs["parameter_ids"]))
            self.assertEqual({int(row["valid_effect_count"]) for row in summary}, {4})
            self.assertTrue(all(math.isfinite(float(row["mu_star"])) for row in summary))
            self.assertTrue(all(float(row["mu_star"]) >= abs(float(row["mu"])) for row in summary))
            self.assertEqual(
                first["outputs"]["summary"]["sha256"],
                hashlib.sha256((first_dir / "morris_summary.csv").read_bytes()).hexdigest(),
            )
            metadata = json.loads((first_dir / "run_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["random_seed"], 20260807)
            self.assertEqual(metadata["normalized_delta"], 2.0 / 3.0)

    def test_positive_context_control_metric_uses_matched_no_ligand_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metadata = run_morris_screening(
                CONFIG_PATH,
                Path(directory),
                parameter_ids=["leak_out"],
                ligand_context_ids=["transition_reference"],
                copy_numbers=[1],
                metric_ids=["delta_color_8h"],
                trajectory_count=2,
            )
            self.assertEqual(metadata["elementary_effect_row_count"], 2)
            self.assertEqual(metadata["summary_row_count"], 1)
            self.assertEqual(metadata["model_solve_count"], 6)
            self.assertEqual(metadata["matched_control_unique_solve_count"], 2)
            self.assertEqual(metadata["matched_control_cache_hit_count"], 2)
            with (Path(directory) / "elementary_effects.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual({row["metric_id"] for row in rows}, {"delta_color_8h"})
            self.assertEqual({row["elementary_effect_valid"] for row in rows}, {"true"})

    def test_positive_contexts_reuse_parameter_matched_no_ligand_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metadata = run_morris_screening(
                CONFIG_PATH,
                Path(directory),
                parameter_ids=["leak_out"],
                ligand_context_ids=[
                    "transition_low_diagnostic",
                    "transition_high_diagnostic",
                ],
                copy_numbers=[1],
                metric_ids=[
                    "matched_control_color_8h",
                    "delta_color_8h",
                    "ratio_color_8h",
                ],
                trajectory_count=2,
            )
            self.assertEqual(metadata["model_solve_count"], 10)
            self.assertEqual(metadata["matched_control_unique_solve_count"], 2)
            self.assertEqual(metadata["matched_control_cache_hit_count"], 6)
            with (Path(directory) / "elementary_effects.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            matched = [
                row for row in rows if row["metric_id"] == "matched_control_color_8h"
            ]
            effects_by_context = {
                context: [
                    float(row["elementary_effect"])
                    for row in matched
                    if row["ligand_context"] == context
                ]
                for context in (
                    "transition_low_diagnostic",
                    "transition_high_diagnostic",
                )
            }
            self.assertEqual(
                effects_by_context["transition_low_diagnostic"],
                effects_by_context["transition_high_diagnostic"],
            )


if __name__ == "__main__":
    unittest.main()
