"""Regression tests for config-driven MD analysis output contracts."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
COMMON_DIR = ROOT / "src/modeling/md-analysis"
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))

from common import configured_replicate_numbers


def load_hbond_module():
    path = ROOT / "experiments/md-simulation/analysis/chctrl/analyze_hbond.py"
    spec = importlib.util.spec_from_file_location("drylab_analyze_hbond", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HBOND = load_hbond_module()


class MdAnalysisContractTests(unittest.TestCase):
    def test_duplicate_replicate_numbers_are_rejected(self) -> None:
        with patch.dict(os.environ, {"CHIMERIC_MD_REPS": "1,1"}):
            with self.assertRaisesRegex(ValueError, "duplicate replicate numbers: 1"):
                configured_replicate_numbers()

    def test_replicate_selector_accepts_sparse_labels(self) -> None:
        with patch.dict(os.environ, {"CHIMERIC_MD_REPS": "rep1 rep3"}):
            self.assertEqual(configured_replicate_numbers(), [1, 3])

    def test_hbond_aggregate_zero_fills_unobserved_replicates(self) -> None:
        summary = pd.DataFrame(
            [
                {
                    "rep": "rep1",
                    "direction": "receptor_to_partner",
                    "pair": "donor -> acceptor",
                    "events": 3,
                    "mean_distance_A": 2.8,
                    "mean_angle_deg": 160.0,
                    "n_frames": 20,
                    "occupancy": 3 / 20,
                }
            ],
            columns=HBOND.SUMMARY_COLUMNS,
        )

        aggregate = HBOND.aggregate_pair_occupancy(
            summary, ["rep1", "rep2", "rep3"]
        )

        self.assertEqual(len(aggregate), 1)
        self.assertAlmostEqual(float(aggregate.iloc[0].occupancy), 0.05)
        self.assertEqual(int(aggregate.iloc[0].observed_reps), 1)
        self.assertEqual(int(aggregate.iloc[0].configured_reps), 3)

        lines, _ = HBOND.judgement_lines(
            summary,
            ["rep1", "rep2", "rep3"],
            heuristic={"occupancy_above": 0.1},
            step=5,
        )
        self.assertIn("rep2: no detected pairs; top pair occupancy=0.000", lines[1])
        self.assertIn("rep3: no detected pairs; top pair occupancy=0.000", lines[2])

    def test_empty_hbond_run_replaces_tables_and_removes_stale_plot(self) -> None:
        raw, summary = HBOND.summarize_events([], {})
        aggregate = HBOND.aggregate_pair_occupancy(
            summary, ["rep1", "rep2", "rep3"]
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            out = Path(temporary_directory)
            stale_plot = out / "occupancy_top10.png"
            stale_plot.write_bytes(b"stale plot")

            HBOND.write_outputs(
                out,
                raw,
                summary,
                aggregate,
                ["rep1", "rep2", "rep3"],
                "test-system",
                heuristic=None,
                step=5,
            )

            self.assertFalse(stale_plot.exists())
            self.assertEqual(
                list(pd.read_csv(out / "hbond_events.csv").columns),
                HBOND.EVENT_COLUMNS,
            )
            self.assertEqual(
                list(pd.read_csv(out / "hbond_summary.csv").columns),
                HBOND.SUMMARY_COLUMNS,
            )
            self.assertEqual(
                list(pd.read_csv(out / "hbond_pair_mean_occupancy.csv").columns),
                HBOND.AGGREGATE_COLUMNS,
            )
            judgement = (out / "judgement.md").read_text(encoding="utf-8")
            self.assertIn("rep1: no detected pairs; top pair occupancy=0.000", judgement)
            self.assertIn("rep2: no detected pairs; top pair occupancy=0.000", judgement)
            self.assertIn("rep3: no detected pairs; top pair occupancy=0.000", judgement)


if __name__ == "__main__":
    unittest.main()
