"""Focused contract tests for the four-job WT calibration runner."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCKING_SRC = REPO_ROOT / "src" / "modeling" / "docking-repro"
sys.path.insert(0, str(DOCKING_SRC))

from run_frame_repair_wt_calibration import (  # noqa: E402
    build_wt_calibration_matrix,
    validate_calibration_seed,
)


class WTCalibrationContractTests(unittest.TestCase):
    def test_matrix_is_exactly_four_wt_jobs(self) -> None:
        self.assertEqual(
            build_wt_calibration_matrix(),
            [
                ("Gpr2", "WT", "ascr18"),
                ("Gpr2", "WT", "ascr3"),
                ("Gpr3", "WT", "ascr18"),
                ("Gpr3", "WT", "ascr3"),
            ],
        )

    def test_seed_must_be_new_and_nonnegative(self) -> None:
        self.assertEqual(validate_calibration_seed(43, source_seed=42), 43)
        with self.assertRaisesRegex(ValueError, "不同"):
            validate_calibration_seed(42, source_seed=42)
        with self.assertRaisesRegex(ValueError, "非负"):
            validate_calibration_seed(-1, source_seed=42)


if __name__ == "__main__":
    unittest.main()
