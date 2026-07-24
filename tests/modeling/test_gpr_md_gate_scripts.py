"""Regression tests for the remote GPR production launch-package gate."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_GATE = (
    ROOT
    / "experiments/md-simulation/scripts/prepare_gpr_md_production_gate.sh"
)
PREPRODUCTION_DRIVER = (
    ROOT / "experiments/md-simulation/scripts/run_gpr_md_preproduction.sh"
)
HEARTBEAT_RUNNER = (
    ROOT
    / "experiments/md-simulation/scripts/run_gpr_md_production_heartbeat.sh"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GprMdProductionGateTests(unittest.TestCase):
    def test_expected_initial_geometry_failure_bypasses_err_trap(self) -> None:
        driver = PREPRODUCTION_DRIVER.read_text(encoding="utf-8")
        guarded_validator = re.compile(
            r'if python3 "\$VALIDATOR" geometry \\\n'
            r'.+?initial_geometry_rc=0\n'
            r'  else\n'
            r'    initial_geometry_rc=\$\?\n'
            r'  fi\n'
            r'  \[\[ "\$initial_geometry_rc" -ne 0 \]\]',
            re.DOTALL,
        )
        self.assertRegex(driver, guarded_validator)
        self.assertNotIn(
            'set +e\n  python3 "$VALIDATOR" geometry',
            driver,
        )

    def test_resume_gate_accepts_existing_empty_issue_scans(self) -> None:
        driver = PREPRODUCTION_DRIVER.read_text(encoding="utf-8")
        resume_required_files = (
            driver.split("resume_benchmark() {", 1)[1]
            .split("  done", 1)[0]
        )
        self.assertNotIn(
            '"$LOG_DIR/em_issue_scan.log"',
            resume_required_files,
        )
        self.assertIn(
            'for issue_log in "$LOG_DIR"/em_issue_scan.log '
            '"$LOG_DIR"/step6.*_issue_scan.log',
            driver,
        )

    def write_executable(self, path: Path, body: str) -> None:
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    def make_stub_commands(self, temporary: Path) -> tuple[Path, Path]:
        stub_bin = temporary / "stub-bin"
        stub_bin.mkdir()
        invocation_log = temporary / "gmx_invocations.log"
        self.write_executable(
            stub_bin / "gmx_mpi",
            """#!/usr/bin/env bash
set -Eeuo pipefail
printf '%s\n' "$*" >> "$GMX_STUB_LOG"
case "${1:-}" in
  --version)
    printf 'GROMACS version:     2025.4\n'
    ;;
  grompp)
    shift
    while [[ "$#" -gt 0 ]]; do
      case "$1" in
        -o|-po)
          printf 'stub %s\n' "$1" > "$2"
          shift 2
          ;;
        *)
          shift
          ;;
      esac
    done
    ;;
  check)
    printf 'stub check PASS\n'
    ;;
  dump)
    printf '   integrator                     = md\n'
    printf '   dt                             = 0.002\n'
    printf '   nsteps                         = 100000000\n'
    printf '   init-step                      = 0\n'
    printf '   continuation                   = true\n'
    printf '   nstxout-compressed             = 5000\n'
    ;;
  mdrun)
    printf 'unexpected mdrun invocation\n' >&2
    exit 99
    ;;
  *)
    printf 'unexpected gmx command: %s\n' "${1:-missing}" >&2
    exit 98
    ;;
esac
""",
        )
        self.write_executable(
            stub_bin / "nvidia-smi",
            """#!/usr/bin/env bash
set -Eeuo pipefail
case "$*" in
  *--query-compute-apps=*)
    exit 0
    ;;
  *--query-gpu=utilization.gpu,memory.used*)
    printf '0, 0\n'
    ;;
  *-L*)
    printf 'GPU 0: NVIDIA GeForce RTX 5090 (UUID: GPU-STUB)\n'
    ;;
  *)
    printf 'stub nvidia-smi\n'
    ;;
esac
""",
        )
        self.write_executable(stub_bin / "pgrep", "#!/usr/bin/env bash\nexit 1\n")
        self.write_executable(stub_bin / "sleep", "#!/usr/bin/env bash\nexit 0\n")
        self.write_executable(
            stub_bin / "date",
            "#!/usr/bin/env bash\nprintf '2026-07-17T12:00:00+08:00\\n'\n",
        )
        return stub_bin, invocation_log

    def make_run_root(self, temporary: Path) -> dict[str, Path]:
        run_root = temporary / "run"
        contract_dir = run_root / "input/contracts"
        manifest_dir = run_root / "manifests"
        preprod = run_root / "preproduction/attempts/accepted/gromacs"
        benchmark = run_root / "benchmark_100ps/attempts/accepted"
        preprod_log = run_root / "logs/preproduction/accepted"
        for directory in (
            contract_dir,
            manifest_dir,
            preprod,
            benchmark,
            preprod_log,
        ):
            directory.mkdir(parents=True)

        contract = {
            "contract_id": "synthetic-production-gate",
            "system_id": "Gpr3_R167Y_ASCR3",
            "system_slug": "gpr3_r167y_ascr3",
            "expected_atoms": 139708,
            "expected_gromacs_version": "2025.4",
            "expected_gromacs_command": "gmx_mpi",
            "step6_warning_contract": {
                "warning_count": 0,
                "source_basename": "cgenff_ASCR3.itp",
                "source_lines": [],
                "required_text": "reviewed warning",
            },
            "production_gate": {
                "nsteps": 100000000,
                "nominal_ns": 200,
                "warning_count": 0,
            },
        }
        contract_path = contract_dir / "autodl_preproduction_contract.json"
        contract_path.write_text(
            json.dumps(contract, indent=2) + "\n", encoding="utf-8"
        )

        inputs = {
            "step6.6.gro": "synthetic accepted equilibration\n139708\n",
            "topol.top": "synthetic topology\n",
            "index_final.ndx": "[ SYSTEM ]\n1\n",
            "step7_production.mdp": "dt = 0.002\nnsteps = 50000\n",
            "ASCR3.itp": "synthetic ligand\n",
            "toppar/cgenff_ASCR3.itp": "synthetic ligand atom types\n",
        }
        for relative, body in inputs.items():
            path = preprod / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")

        (preprod_log / "terminal_status.tsv").write_text(
            "key\tvalue\nstatus\tPASS\n", encoding="utf-8"
        )
        (preprod_log / "benchmark_summary.tsv").write_text(
            "key\tvalue\nstatus\tPASS\n", encoding="utf-8"
        )

        input_manifest = manifest_dir / "input_manifest.sha256"
        input_manifest.write_text(
            f"{sha256(contract_path)}  "
            "input/contracts/autodl_preproduction_contract.json\n",
            encoding="utf-8",
        )
        attempt_manifest = manifest_dir / "preproduction_accepted.sha256"
        step6_path = preprod / "step6.6.gro"
        attempt_manifest.write_text(
            f"{sha256(step6_path)}  "
            "preproduction/attempts/accepted/gromacs/step6.6.gro\n",
            encoding="utf-8",
        )
        accepted_pointer = run_root / "preproduction/accepted_attempt.tsv"
        accepted_pointer.write_text(
            "\n".join(
                [
                    "key\tvalue",
                    "status\tPASS",
                    "attempt_id\taccepted",
                    f"work_dir\t{preprod}",
                    f"benchmark_dir\t{benchmark}",
                    f"log_dir\t{preprod_log}",
                    f"attempt_manifest\t{attempt_manifest}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "run_root": run_root,
            "contract": contract_path,
            "input_manifest": input_manifest,
            "accepted_pointer": accepted_pointer,
        }

    def gate_environment(
        self,
        fixture: dict[str, Path],
        stub_bin: Path,
        invocation_log: Path,
        gate_id: str,
    ) -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{stub_bin}:{environment['PATH']}",
                "RUN_ROOT": str(fixture["run_root"]),
                "GMX_CMD": str(stub_bin / "gmx_mpi"),
                "INPUT_MANIFEST": str(fixture["input_manifest"]),
                "GATE_ID": gate_id,
                "SESSION": "synthetic_autodl_rep1",
                "NTHREADS": "24",
                "GMX_STUB_LOG": str(invocation_log),
            }
        )
        return environment

    def test_gate_atomically_promotes_without_starting_mdrun(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            fixture = self.make_run_root(temporary)
            stub_bin, invocation_log = self.make_stub_commands(temporary)
            completed = subprocess.run(
                ["bash", str(PRODUCTION_GATE)],
                cwd=ROOT,
                env=self.gate_environment(
                    fixture, stub_bin, invocation_log, "gate-pass"
                ),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )

            production = fixture["run_root"] / "production/rep1"
            self.assertTrue(
                (production / "gpr3_r167y_ascr3_rep1_200ns.tpr").is_file()
            )
            self.assertFalse(
                (
                    fixture["run_root"]
                    / "production/gates/gate-pass/staging_rep1"
                ).exists()
            )
            self.assertIn(
                "mdrun_started\tNO",
                (
                    fixture["run_root"] / "production/launch_gate.tsv"
                ).read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (
                    production / "run_gpr_md_production_heartbeat.sh"
                ).is_file()
            )
            launch_command = (production / "launch_command.sh").read_text(
                encoding="utf-8"
            )
            resume_command = (production / "resume_command.sh").read_text(
                encoding="utf-8"
            )
            self.assertIn("--supervise launch --", launch_command)
            self.assertIn("--supervise resume --", resume_command)
            launch_manifest = (
                production / "production_launch_package.sha256"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "run_gpr_md_production_heartbeat.sh", launch_manifest
            )
            gate_summary = (
                fixture["run_root"]
                / "logs/production_gate/gate-pass/"
                "production_launch_gate_summary.tsv"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "heartbeat_auto_started_by_launch_command\tYES",
                gate_summary,
            )
            invocations = invocation_log.read_text(encoding="utf-8")
            self.assertIn("grompp", invocations)
            self.assertIn("dump", invocations)
            self.assertNotIn("mdrun", invocations)

    def test_supervised_launch_automatically_records_verified_heartbeat(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            run_root = temporary / "run"
            production = run_root / "production/rep1"
            logs = run_root / "logs/production/rep1"
            production.mkdir(parents=True)
            logs.mkdir(parents=True)
            prefix = "synthetic_rep1_200ns"
            tpr = production / f"{prefix}.tpr"
            tpr.write_text("synthetic tpr\n", encoding="utf-8")
            launch_manifest = production / "production_launch_package.sha256"
            launch_manifest.write_text(
                f"{sha256(tpr)}  {tpr.name}\n",
                encoding="utf-8",
            )

            fake_gmx = temporary / "gmx_mpi"
            self.write_executable(
                fake_gmx,
                """#!/usr/bin/env bash
set -Eeuo pipefail
case "${1:-}" in
  mdrun)
    shift
    deffnm=
    while [[ "$#" -gt 0 ]]; do
      case "$1" in
        -deffnm)
          deffnm=$2
          shift 2
          ;;
        *)
          shift
          ;;
      esac
    done
    printf '       100       0.20000\n' > "${deffnm}.log"
    printf 'synthetic checkpoint\n' > "${deffnm}.cpt"
    printf 'synthetic energy\n' > "${deffnm}.edr"
    printf 'synthetic trajectory\n' > "${deffnm}.xtc"
    sleep 2
    :
    ;;
  dump)
    printf 'step = 100\n'
    printf 't = 0.200000\n'
    ;;
  *)
    exit 64
    ;;
esac
""",
            )
            fake_ps = temporary / "ps"
            self.write_executable(
                fake_ps,
                """#!/usr/bin/env bash
set -Eeuo pipefail
case "$*" in
  *args=*)
    printf '%s\n' "$SYNTHETIC_PS_ARGS"
    ;;
  *lstart=*)
    printf 'Sun Jul 20 12:00:00 2026\n'
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
                    "RUN_ROOT": str(run_root),
                    "GMX_CMD": str(fake_gmx),
                    "PROD_DIR": str(production),
                    "LOG_DIR": str(logs),
                    "PREFIX": prefix,
                    "SESSION": "",
                    "ATTEMPT_ID": "synthetic-heartbeat",
                    "GATE_ID": "synthetic-gate",
                    "REQUIRE_TMUX": "0",
                    "SAMPLER_ENABLED": "0",
                    "HEARTBEAT_INITIAL_DELAY_SECONDS": "0.2",
                    "HEARTBEAT_INTERVAL_SECONDS": "5",
                    "HEARTBEAT_RETRY_SECONDS": "0.1",
                    "IDENTITY_MANIFEST": str(launch_manifest),
                    "SOURCE_IDENTITY_MANIFEST": str(launch_manifest),
                    "PS_CMD": str(fake_ps),
                    "SYNTHETIC_PS_ARGS": (
                        f"{fake_gmx} mdrun -v -s {tpr} "
                        f"-deffnm {production / prefix}"
                    ),
                }
            )
            completed = subprocess.run(
                [
                    "bash",
                    str(HEARTBEAT_RUNNER),
                    "--supervise",
                    "launch",
                    "--",
                    str(fake_gmx),
                    "mdrun",
                    "-v",
                    "-s",
                    str(tpr),
                    "-deffnm",
                    str(production / prefix),
                ],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            events = (logs / "run_state_events.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "\tRUNNING_VERIFIED\t"
                "periodic_live_process_and_run_outputs\t",
                events,
            )
            self.assertIn("live_step=100;live_time_ps=0.20000", events)
            latest = (logs / "heartbeat_latest.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn("live_step\t100\n", latest)
            terminal = (logs / "terminal_status.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn("run_state\tUNRESOLVED\n", terminal)
            self.assertIn("awaiting_completion_gate=true", terminal)

    def test_supervised_runner_forwards_term_and_reaps_mdrun(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            run_root = temporary / "run"
            production = run_root / "production/rep1"
            logs = run_root / "logs/production/rep1"
            production.mkdir(parents=True)
            logs.mkdir(parents=True)
            prefix = "synthetic_rep1_200ns"
            tpr = production / f"{prefix}.tpr"
            tpr.write_text("synthetic tpr\n", encoding="utf-8")
            child_pid_file = temporary / "mdrun.pid"
            terminated_file = temporary / "mdrun.terminated"

            fake_gmx = temporary / "gmx_mpi"
            self.write_executable(
                fake_gmx,
                """#!/usr/bin/env bash
set -Eeuo pipefail
case "${1:-}" in
  mdrun)
    printf '%s\n' "$$" > "$SYNTHETIC_CHILD_PID_FILE"
    trap 'printf "TERM\\n" > "$SYNTHETIC_TERMINATED_FILE"; exit 143' TERM
    while true; do
      sleep 1
    done
    ;;
  *)
    exit 64
    ;;
esac
""",
            )
            fake_ps = temporary / "ps"
            self.write_executable(
                fake_ps,
                """#!/usr/bin/env bash
set -Eeuo pipefail
case "$*" in
  *args=*)
    printf '%s\n' "$SYNTHETIC_PS_ARGS"
    ;;
  *lstart=*)
    printf 'Sun Jul 20 12:00:00 2026\n'
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
                    "RUN_ROOT": str(run_root),
                    "GMX_CMD": str(fake_gmx),
                    "PROD_DIR": str(production),
                    "LOG_DIR": str(logs),
                    "PREFIX": prefix,
                    "SESSION": "",
                    "ATTEMPT_ID": "synthetic-signal-cleanup",
                    "GATE_ID": "synthetic-gate",
                    "REQUIRE_TMUX": "0",
                    "SAMPLER_ENABLED": "0",
                    "HEARTBEAT_INITIAL_DELAY_SECONDS": "30",
                    "PS_CMD": str(fake_ps),
                    "SYNTHETIC_PS_ARGS": (
                        f"{fake_gmx} mdrun -v -s {tpr} "
                        f"-deffnm {production / prefix}"
                    ),
                    "SYNTHETIC_CHILD_PID_FILE": str(child_pid_file),
                    "SYNTHETIC_TERMINATED_FILE": str(terminated_file),
                }
            )
            runner = subprocess.Popen(
                [
                    "bash",
                    str(HEARTBEAT_RUNNER),
                    "--supervise",
                    "launch",
                    "--",
                    str(fake_gmx),
                    "mdrun",
                    "-v",
                    "-s",
                    str(tpr),
                    "-deffnm",
                    str(production / prefix),
                ],
                cwd=ROOT,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            child_pid = None
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline and not child_pid_file.is_file():
                    if runner.poll() is not None:
                        break
                    time.sleep(0.05)
                self.assertTrue(child_pid_file.is_file())
                child_pid = int(child_pid_file.read_text(encoding="utf-8").strip())

                runner.terminate()
                stdout, stderr = runner.communicate(timeout=5)
                self.assertNotEqual(
                    runner.returncode,
                    0,
                    msg=f"stdout:\n{stdout}\nstderr:\n{stderr}",
                )
                self.assertTrue(terminated_file.is_file())
                with self.assertRaises(ProcessLookupError):
                    os.kill(child_pid, 0)
                self.assertFalse((logs / "heartbeat_runner.pid").exists())
                events = (logs / "run_state_events.tsv").read_text(
                    encoding="utf-8"
                )
                self.assertIn("\tTERMINAL_ABNORMAL\tmdrun_exit\t", events)
            finally:
                if runner.poll() is None:
                    runner.kill()
                    runner.wait(timeout=5)
                if child_pid is not None:
                    try:
                        os.kill(child_pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass

    def test_monitor_existing_rejects_wrong_process_without_killing_it(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            run_root = temporary / "run"
            production = run_root / "production/rep1"
            logs = run_root / "logs/production/rep1"
            production.mkdir(parents=True)
            logs.mkdir(parents=True)
            prefix = "synthetic_200ns"
            fake_gmx = temporary / "gmx_mpi"
            self.write_executable(fake_gmx, "#!/usr/bin/env bash\nexit 0\n")
            unrelated = subprocess.Popen(["sleep", "10"])
            try:
                environment = os.environ.copy()
                environment.update(
                    {
                        "RUN_ROOT": str(run_root),
                        "GMX_CMD": str(fake_gmx),
                        "PROD_DIR": str(production),
                        "LOG_DIR": str(logs),
                        "PREFIX": prefix,
                        "REQUIRE_TMUX": "0",
                    }
                )
                completed = subprocess.run(
                    [
                        "bash",
                        str(HEARTBEAT_RUNNER),
                        "--monitor-existing",
                        str(unrelated.pid),
                    ],
                    cwd=ROOT,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=5,
                )
                self.assertEqual(completed.returncode, 75)
                self.assertIsNone(unrelated.poll())
                events = (logs / "run_state_events.tsv").read_text(
                    encoding="utf-8"
                )
                self.assertIn(
                    "\tUNRESOLVED\theartbeat_process_identity\t",
                    events,
                )
                self.assertIn(
                    f"pid={unrelated.pid};bind_failed=true",
                    events,
                )
            finally:
                unrelated.terminate()
                unrelated.wait(timeout=5)

    def test_monitor_existing_records_process_exit_for_completion_gate(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            run_root = temporary / "run"
            production = run_root / "production/rep1"
            logs = run_root / "logs/production/rep1"
            production.mkdir(parents=True)
            logs.mkdir(parents=True)
            prefix = "synthetic_200ns"
            tpr = production / f"{prefix}.tpr"
            tpr.write_text("synthetic tpr\n", encoding="utf-8")
            fake_gmx = temporary / "gmx_mpi"
            self.write_executable(fake_gmx, "#!/usr/bin/env bash\nexit 0\n")
            fake_ps = temporary / "ps"
            self.write_executable(
                fake_ps,
                """#!/usr/bin/env bash
set -Eeuo pipefail
case "$*" in
  *args=*)
    printf '%s\n' "$SYNTHETIC_PS_ARGS"
    ;;
  *lstart=*)
    printf 'Sun Jul 20 12:00:00 2026\n'
    ;;
  *)
    exit 64
    ;;
esac
""",
            )
            short_lived = subprocess.Popen(["sleep", "0.2"])
            environment = os.environ.copy()
            environment.update(
                {
                    "RUN_ROOT": str(run_root),
                    "GMX_CMD": str(fake_gmx),
                    "PROD_DIR": str(production),
                    "LOG_DIR": str(logs),
                    "PREFIX": prefix,
                    "REQUIRE_TMUX": "0",
                    "HEARTBEAT_INITIAL_DELAY_SECONDS": "1",
                    "PS_CMD": str(fake_ps),
                    "SYNTHETIC_PS_ARGS": (
                        f"{fake_gmx} mdrun -s {tpr} "
                        f"-deffnm {production / prefix}"
                    ),
                }
            )
            monitor = subprocess.Popen(
                [
                    "bash",
                    str(HEARTBEAT_RUNNER),
                    "--monitor-existing",
                    str(short_lived.pid),
                ],
                cwd=ROOT,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            short_lived.wait(timeout=5)
            stdout, stderr = monitor.communicate(timeout=5)
            self.assertEqual(
                monitor.returncode,
                75,
                msg=f"stdout:\n{stdout}\nstderr:\n{stderr}",
            )
            events = (logs / "run_state_events.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "\tUNRESOLVED\tmonitored_mdrun_exit\t",
                events,
            )
            self.assertIn(
                "process_inactive=true;completion_gate_required=true",
                events,
            )

    def test_failed_gate_does_not_claim_production_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            fixture = self.make_run_root(temporary)
            fixture["accepted_pointer"].unlink()
            stub_bin, invocation_log = self.make_stub_commands(temporary)
            completed = subprocess.run(
                ["bash", str(PRODUCTION_GATE)],
                cwd=ROOT,
                env=self.gate_environment(
                    fixture, stub_bin, invocation_log, "gate-hold"
                ),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(
                (fixture["run_root"] / "production/rep1").exists()
            )
            status = (
                fixture["run_root"]
                / "logs/production_gate/gate-hold/terminal_status.tsv"
            ).read_text(encoding="utf-8")
            self.assertIn("status\tHOLD", status)


if __name__ == "__main__":
    unittest.main()
