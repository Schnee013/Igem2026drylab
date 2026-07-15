"""Regression tests for keeping E2 payload bodies outside the Git worktree."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "experiments/md-simulation/scripts"


class MdPayloadRoutingTests(unittest.TestCase):
    def run_script(self, name: str, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPTS / name), *args],
            cwd=ROOT,
            env={**os.environ, **env},
            text=True,
            capture_output=True,
            check=False,
        )

    def test_input_sync_audit_reads_canonical_and_payload_roots_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            canonical = temporary / "canonical"
            payload = temporary / "payload"
            canonical_gmx = canonical / "demo/gromacs"
            payload_gmx = payload / "demo/gromacs"
            (canonical_gmx / "toppar").mkdir(parents=True)
            payload_gmx.mkdir(parents=True)

            (canonical_gmx / "topol.top").write_text("canonical topology\n")
            (canonical_gmx / "step7_production.mdp").write_text("nsteps = 1\n")
            (canonical_gmx / "toppar/forcefield.itp").write_text("canonical forcefield\n")
            (canonical_gmx / "index.ndx").write_text(
                "[ SOLU ]\n1\n"
                "[ SOLU_MEMB ]\n1\n"
                "[ SOLV ]\n2\n"
                "[ MEMB ]\n2\n"
                "[ SYSTEM ]\n1 2\n"
            )
            (payload_gmx / "step6.6.gro").write_text("external final coordinates\n")
            (payload_gmx / "step6.6.cpt").write_text("external checkpoint\n")
            (payload_gmx / "phase3_test.log").write_text("Phase C3 complete\n")

            result = self.run_script(
                "e2_sync_chimeric_inputs.sh",
                "--audit-only",
                "demo",
                env={
                    "SYSTEM_ROOT": str(canonical),
                    "SYSTEM_PAYLOAD_ROOT": str(payload),
                    "RUN_ID": "test",
                },
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("audit-only passed: demo", result.stdout)

    def test_sync_scripts_reject_payload_roots_inside_repo(self) -> None:
        cases = [
            (
                "e2_sync_chimeric_inputs.sh",
                ("--audit-only", "demo"),
                {"SYSTEM_PAYLOAD_ROOT": str(ROOT / "experiments")},
                "SYSTEM_PAYLOAD_ROOT must be outside",
            ),
            (
                "e2_sync_chimeric_phase3_outputs.sh",
                ("run", "demo"),
                {"SYSTEM_PAYLOAD_ROOT": str(ROOT / "experiments")},
                "SYSTEM_PAYLOAD_ROOT must be outside",
            ),
            (
                "e2_sync_chimeric_results.sh",
                ("demo",),
                {"RESULT_PAYLOAD_ROOT": str(ROOT / "experiments")},
                "RESULT_PAYLOAD_ROOT must be outside",
            ),
        ]
        for script, args, env, expected in cases:
            with self.subTest(script=script):
                result = self.run_script(script, *args, env=env)
                self.assertEqual(result.returncode, 2)
                self.assertIn(expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
