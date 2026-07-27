"""Regression tests for generic GPR MD completion and postprocess gates."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
FINALIZER = (
    ROOT
    / "experiments/md-simulation/scripts/finalize_gpr_md_production.sh"
)
POSTPROCESS = (
    ROOT
    / "experiments/md-simulation/scripts/postprocess_gpr_md_rep.sh"
)
PREFIX = "synthetic_gpr_rep1_200ns"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GprMdCompletionContractTests(unittest.TestCase):
    def write_executable(self, path: Path, body: str) -> None:
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    def make_finalizer_fixture(
        self,
        temporary: Path,
        *,
        include_completion_marker: bool,
    ) -> tuple[dict[str, Path], dict[str, str]]:
        run_root = temporary / "run"
        production = run_root / "production/rep1"
        logs = run_root / "logs/production/rep1"
        production.mkdir(parents=True)
        logs.mkdir(parents=True)

        tpr = production / f"{PREFIX}.tpr"
        cpt = production / f"{PREFIX}.cpt"
        gro = production / f"{PREFIX}.gro"
        xtc = production / f"{PREFIX}.xtc"
        edr = production / f"{PREFIX}.edr"
        mdlog = production / f"{PREFIX}.log"
        for path in (tpr, cpt, xtc, edr):
            path.write_text(f"synthetic {path.suffix}\n", encoding="utf-8")
        gro.write_text(
            "synthetic final structure\n"
            "2\n"
            "    1PROA    CA    1   0.000   0.000   0.000\n"
            "    1PROA    CB    2   0.100   0.100   0.100\n"
            "   1.00000   1.00000   1.00000\n",
            encoding="utf-8",
        )
        log_lines = [
            "  100000000  200000.000",
            "Performance:       67.635        0.355",
        ]
        if include_completion_marker:
            log_lines.append(
                "Finished mdrun on rank 0 Sun Jul 19 14:46:34 2026"
            )
        mdlog.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
        (logs / f"mdrun_{PREFIX}.stdout_stderr.log").write_text(
            "synthetic clean capture\n",
            encoding="utf-8",
        )
        (logs / "nvidia_smi_mdrun_sampler.csv").write_text(
            "2026/07/19 14:46:00, 75, 1234, 81920, 250, 55\n",
            encoding="utf-8",
        )

        launch_manifest = production / "production_launch_package.sha256"
        launch_manifest.write_text(
            f"{sha256(tpr)}  {tpr.name}\n",
            encoding="utf-8",
        )
        source_manifest = production / "production_source_inputs.sha256"
        source_manifest.write_text(
            f"{sha256(tpr)}  {tpr}\n",
            encoding="utf-8",
        )

        stub_bin = temporary / "stub-bin"
        stub_bin.mkdir()
        forbidden_mdrun = temporary / "mdrun_was_called"
        self.write_executable(
            stub_bin / "pgrep",
            "#!/usr/bin/env bash\nexit 1\n",
        )
        self.write_executable(
            stub_bin / "gmx_mpi",
            """#!/usr/bin/env bash
set -Eeuo pipefail
command=${1:-}
shift || true
case "$command" in
  check)
    if [[ " ${*} " == *" -f "* ]]; then
      printf '# Atoms  2\nLast frame       2000 time 200000.000\n'
    elif [[ " ${*} " == *" -e "* ]]; then
      printf 'Last energy frame read 100000 time 200000.000\n'
    else
      exit 64
    fi
    ;;
  dump)
    if [[ " ${*} " == *" -cp "* ]]; then
      printf 'step = 100000000\nt = 200000.000\n'
    elif [[ " ${*} " == *" -s "* ]]; then
      printf 'nsteps = 100000000\ndt = 0.002\n'
    else
      exit 64
    fi
    ;;
  energy)
    output=
    while [[ "$#" -gt 0 ]]; do
      if [[ $1 == -o ]]; then
        output=$2
        shift 2
      else
        shift
      fi
    done
    printf '# synthetic energy output\n' > "$output"
    ;;
  mdrun)
    printf 'called\n' > "${FORBIDDEN_MDRUN_MARKER:?}"
    exit 99
    ;;
  *)
    exit 64
    ;;
esac
""",
        )

        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{stub_bin}:{environment['PATH']}",
                "RUN_ROOT": str(run_root),
                "GMX_CMD": str(stub_bin / "gmx_mpi"),
                "PYTHON_CMD": sys.executable,
                "PREFIX": PREFIX,
                "EXPECTED_XTC_ATOMS": "2",
                "EXPECTED_TPR_SHA256": sha256(tpr),
                "ATTEMPT_ID": "synthetic-completion",
                "FORBIDDEN_MDRUN_MARKER": str(forbidden_mdrun),
            }
        )
        return (
            {
                "run_root": run_root,
                "logs": logs,
                "forbidden_mdrun": forbidden_mdrun,
            },
            environment,
        )

    def run_finalizer(
        self,
        temporary: Path,
        *,
        include_completion_marker: bool,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Path]]:
        fixture, environment = self.make_finalizer_fixture(
            temporary,
            include_completion_marker=include_completion_marker,
        )
        completed = subprocess.run(
            ["bash", str(FINALIZER)],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed, fixture

    def test_completed_run_finalizer_never_invokes_mdrun(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            completed, fixture = self.run_finalizer(
                Path(directory),
                include_completion_marker=True,
            )

            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            self.assertFalse(fixture["forbidden_mdrun"].exists())
            events = (
                fixture["logs"] / "run_state_events.tsv"
            ).read_text(encoding="utf-8")
            self.assertEqual(
                events.rstrip().splitlines()[-1].split("\t")[1],
                "TERMINAL_NORMAL",
            )
            status = (
                fixture["logs"] / "terminal_status.tsv"
            ).read_text(encoding="utf-8")
            self.assertIn("production_completed\tYES\n", status)
            archive = (
                fixture["logs"]
                / "synthetic-completion/production_archive.sha256"
            )
            self.assertTrue(archive.is_file())
            self.assertIn(
                f"archive_manifest={archive};"
                f"archive_manifest_sha256={sha256(archive)}",
                events,
            )

    def test_missing_normal_completion_marker_stays_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            completed, fixture = self.run_finalizer(
                Path(directory),
                include_completion_marker=False,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(fixture["forbidden_mdrun"].exists())
            events = (
                fixture["logs"] / "run_state_events.tsv"
            ).read_text(encoding="utf-8")
            self.assertEqual(
                events.rstrip().splitlines()[-1].split("\t")[1],
                "UNRESOLVED",
            )
            self.assertNotIn("\tTERMINAL_NORMAL\t", events)
            status = (
                fixture["logs"] / "terminal_status.tsv"
            ).read_text(encoding="utf-8")
            self.assertIn("run_state\tUNRESOLVED\n", status)
            self.assertIn("production_completed\tNO\n", status)
            attempt = (
                fixture["logs"]
                / "synthetic-completion/completion_status.tsv"
            ).read_text(encoding="utf-8")
            self.assertIn("status\tHOLD\n", attempt)
            self.assertIn("stage\tsemantic_gate\n", attempt)

    def make_postprocess_fixture(
        self,
        temporary: Path,
    ) -> tuple[dict[str, Path], dict[str, str]]:
        run_root = temporary / "run"
        production = run_root / "production/rep1"
        logs = run_root / "logs/production/rep1"
        output = run_root / "processed/rep1"
        production.mkdir(parents=True)
        logs.mkdir(parents=True)

        archive_member = production / "archive_member.dat"
        archive_member.write_text(
            "synthetic archived production member\n",
            encoding="utf-8",
        )
        archive = logs / "production_archive.sha256"
        archive.write_text(
            f"{sha256(archive_member)}  production/rep1/"
            "archive_member.dat\n",
            encoding="utf-8",
        )
        source_manifest = production / "production_source_inputs.sha256"
        source_manifest.write_text(
            "synthetic source manifest without an index pointer\n",
            encoding="utf-8",
        )
        status = logs / "terminal_status.tsv"
        status.write_text(
            "key\tvalue\n"
            "terminal_status\tPRODUCTION_COMPLETE\n"
            "production_completed\tYES\n"
            "run_state\tTERMINAL_NORMAL\n",
            encoding="utf-8",
        )

        environment = os.environ.copy()
        environment.update(
            {
                "RUN_ROOT": str(run_root),
                "GMX_CMD": "/usr/bin/false",
                "PYTHON_CMD": sys.executable,
                "PREFIX": PREFIX,
                "OUT_DIR": str(output),
                "EXPECTED_SOLUTION_ATOMS": "2",
                "EXPECTED_FIT_ATOMS": "1",
                "ATTEMPT_ID": "synthetic-postprocess",
            }
        )
        return (
            {
                "archive": archive,
                "events": logs / "run_state_events.tsv",
                "attempt_status": (
                    output
                    / "synthetic-postprocess/postprocess_status.tsv"
                ),
            },
            environment,
        )

    def write_terminal_event(
        self,
        fixture: dict[str, Path],
        *,
        later_state: str | None = None,
    ) -> None:
        archive = fixture["archive"]
        rows = [
            "observed_at\tstate\tsource\tdetail",
            (
                "2026-07-20T00:00:00Z\tTERMINAL_NORMAL\tcompletion_gate\t"
                f"archive_manifest={archive};"
                f"archive_manifest_sha256={sha256(archive)}"
            ),
        ]
        if later_state is not None:
            rows.append(
                "2026-07-20T00:01:00Z\t"
                f"{later_state}\tidentity_check\t"
                "completion authority no longer current"
            )
        fixture["events"].write_text(
            "\n".join(rows) + "\n",
            encoding="utf-8",
        )

    def run_postprocess(
        self,
        environment: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(POSTPROCESS)],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_postprocess_accepts_latest_matching_terminal_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture, environment = self.make_postprocess_fixture(
                Path(directory)
            )
            self.write_terminal_event(fixture)

            completed = self.run_postprocess(environment)

            self.assertNotEqual(completed.returncode, 0)
            attempt = fixture["attempt_status"].read_text(encoding="utf-8")
            self.assertIn("stage\trequired_inputs\n", attempt)
            archive_check = (
                fixture["attempt_status"].parent
                / "production_archive_check.log"
            )
            self.assertTrue(archive_check.is_file())
            self.assertIn(": OK\n", archive_check.read_text(encoding="utf-8"))

    def test_postprocess_rejects_changed_archive_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture, environment = self.make_postprocess_fixture(
                Path(directory)
            )
            self.write_terminal_event(fixture)
            fixture["archive"].write_text(
                "changed archive manifest\n",
                encoding="utf-8",
            )

            completed = self.run_postprocess(environment)

            self.assertNotEqual(completed.returncode, 0)
            attempt = fixture["attempt_status"].read_text(encoding="utf-8")
            self.assertIn("stage\tproduction_terminal_gate\n", attempt)
            self.assertFalse(
                (
                    fixture["attempt_status"].parent
                    / "production_archive_check.log"
                ).exists()
            )

    def test_postprocess_rejects_event_after_terminal_normal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture, environment = self.make_postprocess_fixture(
                Path(directory)
            )
            self.write_terminal_event(
                fixture,
                later_state="UNRESOLVED",
            )

            completed = self.run_postprocess(environment)

            self.assertNotEqual(completed.returncode, 0)
            attempt = fixture["attempt_status"].read_text(encoding="utf-8")
            self.assertIn("stage\tproduction_terminal_gate\n", attempt)
            self.assertFalse(
                (
                    fixture["attempt_status"].parent
                    / "production_archive_check.log"
                ).exists()
            )


if __name__ == "__main__":
    unittest.main()
