"""Focused tests for Phase-2B local time-dependent ODE sensitivity."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import tempfile
import unittest

from src.modeling.ode.local_sensitivity import (
    compute_parameter_context_rows,
    load_analysis_inputs,
    run_local_sensitivity,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "experiments/ode-model/configs/phase2b_local_sensitivity.json"


class LocalSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.analysis,
            _,
            cls.baseline,
            cls.parameters,
            cls.contexts,
            _,
            _,
        ) = load_analysis_inputs(CONFIG_PATH)

    def parameter(self, parameter_id: str) -> dict[str, str]:
        return next(row for row in self.parameters if row["parameter_id"] == parameter_id)

    def context(self, context_id: str) -> tuple[str, str, float]:
        return next(context for context in self.contexts if context[1] == context_id)

    def test_contract_drives_all_continuous_parameters_and_ligand_contexts(self) -> None:
        self.assertEqual(len(self.parameters), 17)
        self.assertEqual(
            [context_id for _, context_id, _ in self.contexts],
            [
                "no_ligand",
                "transition_reference",
                "high_input",
                "transition_low_diagnostic",
                "transition_high_diagnostic",
            ],
        )

    def test_nr_reference_is_zero_while_diagnostic_contexts_have_opposite_signs(self) -> None:
        parameter = self.parameter("n_R")
        reference = compute_parameter_context_rows(
            self.analysis,
            self.baseline,
            parameter,
            self.context("transition_reference"),
        )[-1]
        low = compute_parameter_context_rows(
            self.analysis,
            self.baseline,
            parameter,
            self.context("transition_low_diagnostic"),
        )[-1]
        high = compute_parameter_context_rows(
            self.analysis,
            self.baseline,
            parameter,
            self.context("transition_high_diagnostic"),
        )[-1]

        self.assertAlmostEqual(reference["color_signal_scaled_sensitivity"], 0.0, places=12)
        self.assertLess(low["color_signal_scaled_sensitivity"], 0.0)
        self.assertGreater(high["color_signal_scaled_sensitivity"], 0.0)

    def test_upper_bound_parameter_uses_backward_difference(self) -> None:
        rows = compute_parameter_context_rows(
            self.analysis,
            self.baseline,
            self.parameter("k_couple"),
            self.context("transition_reference"),
        )
        self.assertEqual({row["finite_difference_scheme"] for row in rows}, {"backward"})
        self.assertLess(
            max(row["color_signal_step_halving_relative_difference"] for row in rows),
            0.01,
        )

    def test_selected_slice_writes_reproducible_shape_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "slice" / "sensitivities.csv"
            metadata = run_local_sensitivity(
                CONFIG_PATH,
                output,
                parameter_ids=["n_R"],
                ligand_context_ids=[
                    "transition_reference",
                    "transition_low_diagnostic",
                    "transition_high_diagnostic",
                ],
            )
            with output.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(metadata["parameter_count"], 1)
            self.assertEqual(metadata["ligand_context_count"], 3)
            self.assertEqual(metadata["row_count"], 3 * 161)
            self.assertEqual(len(rows), 3 * 161)
            self.assertNotIn(b"\r\n", output.read_bytes())
            self.assertTrue(output.with_name("run_metadata.json").is_file())
            self.assertEqual(
                metadata["output"]["sha256"],
                hashlib.sha256(output.read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
