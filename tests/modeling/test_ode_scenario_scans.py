"""Contract tests for the Phase-1 ODE scenario-prior scan suite."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil
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
        scenario_ids = [record.config["scenario_id"] for record in records]
        self.assertEqual(len(scenario_ids), len(set(scenario_ids)))

        ligand_records = [record for record in records if record.scenario_role == "ligand"]
        control_records = [
            record for record in records if record.scenario_role == "no_ligand_control"
        ]
        self.assertEqual(len(ligand_records), 74)
        self.assertEqual(len(control_records), 69)
        ligand_ids = {record.config["scenario_id"] for record in ligand_records}
        paired_ids = [record.control_for_scenario_id for record in control_records]
        self.assertEqual(len(paired_ids), len(set(paired_ids)))
        self.assertTrue(set(paired_ids).issubset(ligand_ids))
        self.assertTrue(
            all(record.config["input"]["ligand_normalized"] == 0.0 for record in control_records)
        )
        self.assertTrue(
            all(
                record.effective_axis_values["input.ligand_normalized"] == 0.0
                for record in control_records
            )
        )
        self.assertTrue(
            all(
                record.requested_axis_values["input.ligand_normalized"] > 0.0
                for record in control_records
            )
        )
        copy_numbers = {
            record.config["gal_output"]["copy_number"]
            for record in records
            if record.scan_id == "copy_gain_by_time_window"
        }
        self.assertEqual(copy_numbers, {1, 2, 4})

    def test_suite_run_writes_compact_results_and_external_payload_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "stage1"
            timecourse_path = Path(temporary_directory) / "payload" / "timecourses.csv"
            summary = run_scan_suite(
                SUITE_CONFIG,
                output_dir,
                timecourse_output_path=timecourse_path,
            )
            self.assertEqual(
                summary,
                {
                    "scenario_count": 143,
                    "timecourse_row_count": 23023,
                    "control_count": 69,
                },
            )
            self.assertTrue(timecourse_path.is_file())
            self.assertFalse((output_dir / "timecourses.csv").exists())
            for csv_path in (
                output_dir / "scenario_manifest.csv",
                output_dir / "final_metrics.csv",
                output_dir / "payload_manifest.tsv",
                timecourse_path,
            ):
                self.assertNotIn(b"\r\n", csv_path.read_bytes())

            with (output_dir / "final_metrics.csv").open(encoding="utf-8", newline="") as handle:
                metrics = list(csv.DictReader(handle))
            with (output_dir / "scenario_manifest.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            with timecourse_path.open(encoding="utf-8", newline="") as handle:
                timecourses = list(csv.DictReader(handle))
            self.assertEqual(len(metrics), 143)
            self.assertTrue(all(row["evidence_status"] == "scenario_prior" for row in metrics))
            self.assertIn("final_color_delta_vs_no_ligand_arbitrary_units", metrics[0])
            scenario_set = {row["scenario_id"] for row in manifest}
            self.assertEqual(scenario_set, {row["scenario_id"] for row in metrics})
            self.assertEqual(scenario_set, {row["scenario_id"] for row in timecourses})
            controls = [
                row for row in manifest if row["scenario_role"] == "no_ligand_control"
            ]
            self.assertEqual(len(controls), 69)
            self.assertTrue(all(row["control_for_scenario_id"] for row in controls))
            self.assertTrue(
                all(
                    json.loads(row["effective_axis_values_json"])[
                        "input.ligand_normalized"
                    ]
                    == 0.0
                    for row in controls
                )
            )

            metadata = json.loads((output_dir / "run_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["scenario_count"], 143)
            self.assertEqual(metadata["control_count"], 69)
            self.assertIn("not calibrated", metadata["result_boundary"])
            self.assertEqual(
                metadata["external_timecourse_payload"]["sha256"],
                hashlib.sha256(timecourse_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                json.loads(
                    (output_dir / "scan_suite_config_snapshot.json").read_text(
                        encoding="utf-8"
                    )
                )["base_config"],
                "base_config_snapshot.json",
            )
            self.assertTrue((output_dir / "base_config_snapshot.json").is_file())

            with (output_dir / "payload_manifest.tsv").open(
                encoding="utf-8", newline=""
            ) as handle:
                payload_rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(len(payload_rows), 1)
            self.assertEqual(payload_rows[0]["tracked_policy"], "external")
            self.assertEqual(
                payload_rows[0]["sha256"],
                hashlib.sha256(timecourse_path.read_bytes()).hexdigest(),
            )

            figure_path = output_dir / "summary.png"
            plot_metrics(load_metrics(output_dir / "final_metrics.csv"), figure_path)
            self.assertGreater(figure_path.stat().st_size, 0)

    def test_copied_config_snapshots_replay_without_source_config_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            original_output = temporary_root / "original"
            original_timecourses = temporary_root / "payload" / "original.csv"
            run_scan_suite(
                SUITE_CONFIG,
                original_output,
                timecourse_output_path=original_timecourses,
            )

            copied_package = temporary_root / "copied_package"
            shutil.copytree(original_output, copied_package)
            replay_output = temporary_root / "replay"
            replay_timecourses = temporary_root / "payload" / "replay.csv"
            replay_summary = run_scan_suite(
                copied_package / "scan_suite_config_snapshot.json",
                replay_output,
                timecourse_output_path=replay_timecourses,
            )

            self.assertEqual(
                replay_summary,
                {
                    "scenario_count": 143,
                    "timecourse_row_count": 23023,
                    "control_count": 69,
                },
            )
            self.assertEqual(
                (original_output / "scenario_manifest.csv").read_bytes(),
                (replay_output / "scenario_manifest.csv").read_bytes(),
            )
            self.assertEqual(
                (original_output / "final_metrics.csv").read_bytes(),
                (replay_output / "final_metrics.csv").read_bytes(),
            )
            self.assertEqual(original_timecourses.read_bytes(), replay_timecourses.read_bytes())

    def test_suite_rejects_non_scenario_prior_label(self) -> None:
        suite = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
        suite["evidence_status"] = "literature_prior"
        with tempfile.TemporaryDirectory() as temporary_directory:
            invalid_path = Path(temporary_directory) / "invalid_suite.json"
            invalid_path.write_text(json.dumps(suite), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "scenario_prior"):
                load_scan_suite(invalid_path)

    def test_suite_rejects_unknown_fields_non_finite_values_and_fractional_copy_number(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            base_config = ROOT / "experiments/ode-model/configs/minimal_normalized_scenario.json"
            shutil.copyfile(base_config, temporary_root / base_config.name)

            suite = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
            suite["unknown"] = True
            invalid_path = temporary_root / "unknown.json"
            invalid_path.write_text(json.dumps(suite), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown fields"):
                load_scan_suite(invalid_path)

            suite = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
            suite["scans"][0]["axes"]["input.ligand_normalized"] = [float("nan")]
            invalid_path = temporary_root / "nan.json"
            invalid_path.write_text(json.dumps(suite), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "finite"):
                load_scan_suite(invalid_path)

            suite = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
            suite["scans"][2]["axes"]["gal_output.copy_number"] = [1, 2.5]
            invalid_path = temporary_root / "fractional-copy.json"
            invalid_path.write_text(json.dumps(suite), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integer"):
                load_scan_suite(invalid_path)


if __name__ == "__main__":
    unittest.main()
