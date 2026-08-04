"""Contract tests for the ODE Phase 2A sensitivity and experiment interface."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "experiments/ode-model/configs"
CONTRACT_PATH = CONFIG_DIR / "phase2a_analysis_contract.json"

EXPECTED_PARAMETER_PATHS = {
    "receptor.basal_activity",
    "receptor.efficacy",
    "receptor.half_activation_normalized",
    "receptor.hill_coefficient",
    "g_protein.coupling_rate_per_hour",
    "g_protein.deactivation_rate_per_hour",
    "mapk.activation_rate_per_hour",
    "mapk.deactivation_rate_per_hour",
    "transcription.basal_activity",
    "transcription.efficacy",
    "transcription.half_activation",
    "transcription.hill_coefficient",
    "gal_output.copy_number",
    "gal_output.leak_rate",
    "gal_output.gain_rate",
    "gal_output.half_activation",
    "color.production_rate_per_hour",
    "color.loss_rate_per_hour",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _get_dotted(config: dict, dotted_path: str):
    value = config
    for part in dotted_path.split("."):
        value = value[part]
    return value


class Phase2AContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        files = cls.contract["contract_files"]
        cls.parameter_rows = _read_csv(ROOT / files["parameter_space"])
        cls.output_rows = _read_csv(ROOT / files["output_metrics"])
        cls.experiment_rows = _read_csv(ROOT / files["experiment_matrix"])
        cls.baseline = json.loads(
            (ROOT / cls.contract["source_baseline"]["baseline_config"]).read_text(
                encoding="utf-8"
            )
        )

    def test_contract_references_existing_sources_and_artifacts(self) -> None:
        self.assertEqual(
            self.contract["source_base_commit"],
            "36599402fd091f616520e9b7415d3b30aefd5781",
        )
        for path in self.contract["source_baseline"].values():
            self.assertTrue((ROOT / path).is_file(), path)
        for path in self.contract["contract_files"].values():
            self.assertTrue((ROOT / path).is_file(), path)

    def test_parameter_space_matches_all_18_baseline_fields(self) -> None:
        counts = self.contract["parameter_counts"]
        self.assertEqual(counts["internal_config_fields"], 18)
        self.assertEqual(len(self.parameter_rows), 18)
        self.assertEqual(
            {row["config_path"] for row in self.parameter_rows},
            EXPECTED_PARAMETER_PATHS,
        )
        self.assertEqual(len({row["parameter_id"] for row in self.parameter_rows}), 18)

        continuous = [
            row for row in self.parameter_rows if row["analysis_role"] == "uncertain_continuous"
        ]
        discrete = [
            row for row in self.parameter_rows if row["analysis_role"] == "design_stratum"
        ]
        self.assertEqual(len(continuous), counts["continuous_uncertainty_fields"])
        self.assertEqual(len(discrete), counts["discrete_design_fields"])

        for row in self.parameter_rows:
            baseline = float(_get_dotted(self.baseline, row["config_path"]))
            self.assertAlmostEqual(baseline, float(row["baseline_value"]))
            if row["analysis_role"] == "uncertain_continuous":
                self.assertLessEqual(float(row["lower_bound"]), baseline)
                self.assertGreaterEqual(float(row["upper_bound"]), baseline)
            else:
                levels = {int(value) for value in row["discrete_levels"].split("|")}
                self.assertIn(int(baseline), levels)

    def test_design_contexts_preserve_phase1_copy_strata_and_controls(self) -> None:
        contexts = self.contract["design_contexts"]
        self.assertEqual(contexts["copy_number_strata"], [1, 2, 4])
        self.assertEqual(contexts["ligand_normalized"]["no_ligand"], 0.0)
        self.assertEqual(
            contexts["ligand_context_sets"]["primary"],
            ["no_ligand", "transition_reference", "high_input"],
        )
        self.assertEqual(
            contexts["ligand_context_sets"]["transition_diagnostic"],
            ["transition_low_diagnostic", "transition_high_diagnostic"],
        )
        classified = {
            context_id
            for context_ids in contexts["ligand_context_sets"].values()
            for context_id in context_ids
        }
        self.assertEqual(classified, set(contexts["ligand_normalized"]))
        self.assertIn("only input.ligand_normalized", contexts["matched_control_rule"])

    def test_nr_diagnostic_contexts_flank_baseline_kr_for_analysis_only(self) -> None:
        contexts = self.contract["design_contexts"]
        ligand = contexts["ligand_normalized"]
        basis = contexts["transition_diagnostic_basis"]
        baseline_kr = float(
            _get_dotted(self.baseline, "receptor.half_activation_normalized")
        )

        self.assertEqual(basis["target_parameter"], "n_R")
        self.assertEqual(float(basis["baseline_K_R"]), baseline_kr)
        self.assertEqual(basis["scope"], "analysis_only")
        self.assertFalse(basis["wet_lab_requirement"])
        self.assertEqual(ligand["transition_low_diagnostic"], 0.3)
        self.assertEqual(ligand["transition_high_diagnostic"], 3.0)
        self.assertLess(ligand["transition_low_diagnostic"], baseline_kr)
        self.assertEqual(ligand["transition_reference"], baseline_kr)
        self.assertGreater(ligand["transition_high_diagnostic"], baseline_kr)
        self.assertLess(
            ligand["transition_high_diagnostic"],
            ligand["high_input"],
        )

    def test_output_metrics_have_unique_ids_and_explicit_activation_state(self) -> None:
        ids = [row["metric_id"] for row in self.output_rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(row["status"] for row in self.output_rows))
        threshold = next(
            row for row in self.output_rows if row["metric_id"] == "time_to_readout_threshold"
        )
        self.assertEqual(threshold["status"], "inactive_pending_threshold")
        self.assertIn("wet-lab threshold", threshold["required_data"])

    def test_guarded_ratio_metric_has_machine_readable_policy(self) -> None:
        guarded_metrics = [
            row["metric_id"]
            for row in self.output_rows
            if row["status"] == "active_with_denominator_guard"
        ]
        self.assertEqual(guarded_metrics, ["ratio_color_8h"])

        policies = self.contract["metric_guard_policies"]
        policy = policies["ratio_color_8h"]
        self.assertEqual(policy["status"], "active")
        self.assertEqual(policy["applies_to_metric_id"], "ratio_color_8h")
        self.assertEqual(policy["numerator_metric_id"], "color_8h")
        self.assertEqual(policy["denominator_metric_id"], "matched_control_color_8h")
        self.assertGreater(float(policy["denominator_min_positive_value"]), 0.0)
        self.assertEqual(policy["invalid_result"], "NaN")
        self.assertEqual(
            policy["validity_flag_column"],
            "final_color_ratio_vs_no_ligand_valid",
        )
        self.assertEqual(
            policy["invalid_reason_column"],
            "final_color_ratio_vs_no_ligand_invalid_reason",
        )
        self.assertIn("delta_color_8h", policy["interpretation"])

    def test_experiment_matrix_covers_each_parameter_exactly_once(self) -> None:
        parameter_ids = {row["parameter_id"] for row in self.parameter_rows}
        experiment_ids = [row["parameter_id"] for row in self.experiment_rows]
        self.assertEqual(len(experiment_ids), 18)
        self.assertEqual(set(experiment_ids), parameter_ids)
        self.assertEqual(len(experiment_ids), len(set(experiment_ids)))
        self.assertTrue(all(row["replacement_gate"] for row in self.experiment_rows))


if __name__ == "__main__":
    unittest.main()
