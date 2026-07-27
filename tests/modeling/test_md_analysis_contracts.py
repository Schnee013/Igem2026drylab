"""Regression tests for config-driven MD analysis output contracts."""

from __future__ import annotations

import importlib.util
import json
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

from common import analysis_context, configured_replicate_numbers


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
    WT_GPR2_CONFIG = (
        ROOT
        / "experiments/md-simulation/results/gpr2-wt-ascr18/chimeric_systems.gpr2_wt_ascr18_rep1.json"
    )
    R59C_GPR2_CONFIG = (
        ROOT
        / "experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json"
    )

    def test_external_payload_root_keeps_analysis_outputs_in_repo_tree(self) -> None:
        config = {
            "default": "test-system",
            "systems": {
                "test-system": {
                    "label": "test",
                    "result_dir": "experiments/md-simulation/results/test-system",
                    "receptor": {
                        "name": "receptor",
                        "selection": "segid A",
                        "interface_selection": "segid A",
                    },
                    "galpha": {
                        "name": "partner",
                        "selection": "segid B",
                        "alpha5_selection": "segid B",
                        "ect_selection": "segid B",
                        "core_backbone_selection": "segid B",
                    },
                }
            },
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            config_path = temporary / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            payload_root = temporary / "payloads"
            with patch.dict(
                os.environ,
                {
                    "DRYLAB_PAYLOAD_ROOT": str(payload_root),
                    "CHIMERIC_MD_REPS": "1",
                },
                clear=False,
            ):
                context = analysis_context(config_path=config_path)

            self.assertEqual(
                context.analysis_base,
                Path("experiments/md-simulation/results/test-system/analysis"),
            )
            self.assertEqual(
                context.payload_base,
                payload_root / "experiments/md-simulation/results/test-system",
            )
            self.assertEqual(
                context.replicates()[0].trajectory,
                payload_root
                / "experiments/md-simulation/results/test-system/processed/rep1/prod_protein.xtc",
            )

    def test_direct_payload_root_overrides_shared_payload_root(self) -> None:
        direct = Path("/external/package")
        with patch.dict(
            os.environ,
            {
                "CHIMERIC_MD_PAYLOAD_ROOT": str(direct),
                "DRYLAB_PAYLOAD_ROOT": "/external/shared",
                "CHIMERIC_MD_REPS": "1",
            },
            clear=False,
        ):
            context = analysis_context(
                "gpr2-wt-ascr18-rep1",
                config_path=ROOT
                / "experiments/md-simulation/results/gpr2-wt-ascr18/chimeric_systems.gpr2_wt_ascr18_rep1.json",
            )

        self.assertEqual(context.payload_base, direct)
        self.assertEqual(
            context.replicates()[0].topology,
            direct / "processed/rep1/protein_ref.pdb",
        )

    def test_gpr2_r59c_config_matches_wt_metric_contract(self) -> None:
        wt_root = json.loads(self.WT_GPR2_CONFIG.read_text(encoding="utf-8"))
        r59c_root = json.loads(self.R59C_GPR2_CONFIG.read_text(encoding="utf-8"))
        wt = wt_root["systems"][wt_root["default"]]
        r59c = r59c_root["systems"][r59c_root["default"]]

        shared_fields = (
            "selection_rmsd_label",
            "selection_rmsd_selection_label",
            "selection_rmsd_selection",
            "interaction_partner_role",
            "com_target_label",
            "plot_segids",
            "galpha",
            "junction_rmsf_regions",
        )
        for field in shared_fields:
            self.assertEqual(r59c[field], wt[field], field)
        self.assertEqual(r59c["receptor"]["selection"], wt["receptor"]["selection"])
        self.assertEqual(
            r59c["receptor"]["interface_selection"],
            wt["receptor"]["interface_selection"],
        )
        self.assertEqual(
            r59c["receptor"]["interface_clusters"],
            wt["receptor"]["interface_clusters"],
        )
        for heuristic in (
            "selection_rmsd_mean_heuristic",
            "bsa_mean_fraction_heuristic",
            "contact_mean_fraction_heuristic",
            "hbond_occupancy_reporting_heuristic",
        ):
            self.assertNotIn(heuristic, wt)
            self.assertNotIn(heuristic, r59c)

    def test_gpr2_r59c_config_resolves_single_rep_external_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            payload_root = Path(temporary_directory) / "gpr2-r59c-ascr18"
            with patch.dict(
                os.environ,
                {
                    "CHIMERIC_MD_PAYLOAD_ROOT": str(payload_root),
                    "CHIMERIC_MD_REPS": "1",
                },
                clear=False,
            ):
                context = analysis_context(config_path=self.R59C_GPR2_CONFIG)
                replicates = context.replicates()

        self.assertEqual(context.system, "gpr2-r59c-ascr18-rep1")
        self.assertEqual(context.interaction_partner_role, "ligand")
        self.assertEqual(context.selection_rmsd_mean_heuristic, None)
        self.assertEqual(len(replicates), 1)
        self.assertEqual(
            replicates[0].topology,
            payload_root / "processed/rep1/protein_ref.pdb",
        )
        self.assertEqual(
            replicates[0].trajectory,
            payload_root / "processed/rep1/prod_protein.xtc",
        )

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
