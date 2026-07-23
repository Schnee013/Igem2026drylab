"""Contract tests for the Phase-1 ODE scenario-prior scan suite."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
import unittest

from src.modeling.ode.plot_scenario_scan import load_metrics, plot_metrics
from src.modeling.ode.run_scenario_scans import build_scenarios, load_scan_suite, run_scan_suite


ROOT = Path(__file__).resolve().parents[2]
SUITE_CONFIG = ROOT / "experiments/ode-model/configs/stage1_scenario_scan.json"


class ScenarioScanTests(unittest.TestCase):
    def test_readable_suite_expands_to_expected_scenario_prior_controls(self) -> None:
        suite, base_config = load_scan_suite(SUITE_CONFIG)
        records = build_scenarios(suite, base_config)

        self.assertEqual(suite["evidence_status"], "scenario_prior")
        self.assertEqual(len(records), 143)
        self.assertTrue(all(record.config["evidence_status"] == "scenario_prior" for record in records))
        self.assertTrue(any(record.scenario_role == "no_ligand_control" for record in records))
        copy_numbers = {
            record.config["gal_output"]["copy_number"]
            for record in records
            if record.scan_id == "copy_gain_by_time_window"
        }
        self.assertEqual(copy_numbers, {1.0, 2.0, 4.0})

    def test_suite_run_writes_self_describing_compact_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "stage1"
            summary = run_scan_suite(SUITE_CONFIG, output_dir)
            self.assertEqual(summary, {"scenario_count": 143, "timecourse_row_count": 23023})

            with (output_dir / "final_metrics.csv").open(encoding="utf-8", newline="") as handle:
                metrics = list(csv.DictReader(handle))
            self.assertEqual(len(metrics), 143)
            self.assertTrue(all(row["evidence_status"] == "scenario_prior" for row in metrics))
            self.assertIn("final_color_delta_vs_no_ligand_arbitrary_units", metrics[0])
            self.assertTrue(
                any(row["scenario_role"] == "no_ligand_control" for row in metrics)
            )

            metadata = json.loads((output_dir / "run_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["scenario_count"], 143)
            self.assertIn("not calibrated", metadata["result_boundary"])

            figure_path = output_dir / "summary.png"
            plot_metrics(load_metrics(output_dir / "final_metrics.csv"), figure_path)
            self.assertGreater(figure_path.stat().st_size, 0)

    def test_suite_rejects_non_scenario_prior_label(self) -> None:
        suite = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
        suite["evidence_status"] = "literature_prior"
        with tempfile.TemporaryDirectory() as temporary_directory:
            invalid_path = Path(temporary_directory) / "invalid_suite.json"
            invalid_path.write_text(json.dumps(suite), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "scenario_prior"):
                load_scan_suite(invalid_path)


if __name__ == "__main__":
    unittest.main()
