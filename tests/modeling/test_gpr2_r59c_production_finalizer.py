from __future__ import annotations

import os
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_production.sh"
)
POSTPROCESS_SCRIPT = (
    REPO_ROOT
    / "experiments/md-simulation/scripts/e2_postprocess_gpr2_r59c_ascr18_rep1.sh"
)
PREFIX = "gpr2_r59c_ascr18_rep1_200ns"


def _write_fake_gmx(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
command=${1:-}
shift || true
case "$command" in
  check)
    if [[ " ${*} " == *" -f "* ]]; then
      printf '# Atoms  130638\\nLast frame       2000 time 200000.000\\n'
    elif [[ " ${*} " == *" -e "* ]]; then
      printf 'Last energy frame read 100000 time 200000.000\\n'
    else
      exit 64
    fi
    ;;
  energy)
    output=
    while [[ $# -gt 0 ]]; do
      if [[ $1 == -o ]]; then
        output=$2
        shift 2
      else
        shift
      fi
    done
    printf '# fake energy output\\n' > "$output"
    ;;
  dump)
    printf 'checkpoint dump ok\\n'
    ;;
  mdrun)
    printf 'mdrun must not be called\\n' > "${FORBIDDEN_MDRUN_MARKER:?}"
    exit 99
    ;;
  *)
    exit 64
    ;;
esac
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _completed_run(tmp_path: Path, *, include_main_completion: bool = True) -> tuple[Path, Path]:
    run_root = tmp_path / "run"
    production = run_root / "production"
    logs = run_root / "logs/production"
    production.mkdir(parents=True)
    logs.mkdir(parents=True)
    (run_root / "sanity/production").mkdir(parents=True)

    for suffix in ("tpr", "cpt", "gro", "xtc", "edr"):
        (production / f"{PREFIX}.{suffix}").write_text(
            f"fake {suffix} body\n", encoding="utf-8"
        )
    main_lines = ["Performance:       67.635        0.355"]
    if include_main_completion:
        main_lines.append("Finished mdrun on rank 0 Sun Jul 19 14:46:34 2026")
    (production / f"{PREFIX}.log").write_text(
        "\n".join(main_lines) + "\n", encoding="utf-8"
    )
    (logs / f"mdrun_{PREFIX}.log").write_text(
        "Performance:       67.635        0.355\n", encoding="utf-8"
    )
    (logs / "nvidia_smi_mdrun_sampler.csv").write_text(
        "2026/07/16 15:48:20, 75, 1234, 81920, 250, 55\n",
        encoding="utf-8",
    )
    (logs / "terminal_status.tsv").write_text(
        "status\trunning\n", encoding="utf-8"
    )
    fake_gmx = tmp_path / "fake_gmx"
    _write_fake_gmx(fake_gmx)
    return run_root, fake_gmx


def _run_finalizer(tmp_path: Path, *, include_main_completion: bool = True) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    run_root, fake_gmx = _completed_run(
        tmp_path, include_main_completion=include_main_completion
    )
    forbidden_marker = tmp_path / "mdrun_was_called"
    env = os.environ.copy()
    env.update(
        {
            "RUN_ROOT": str(run_root),
            "GMX_CMD": str(fake_gmx),
            "PREFIX": PREFIX,
            "FORBIDDEN_MDRUN_MARKER": str(forbidden_marker),
        }
    )
    completed = subprocess.run(
        ["bash", str(SCRIPT), "--remote-finalize-completed"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed, run_root, forbidden_marker


def test_completed_run_finalizer_accepts_marker_from_main_log_without_mdrun(
    tmp_path: Path,
) -> None:
    completed, run_root, forbidden_marker = _run_finalizer(tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert not forbidden_marker.exists()
    logs = run_root / "logs/production"
    assert (logs / "terminal_status.tsv").read_text(encoding="utf-8").startswith(
        "status\tfinished\nfinished\t"
    )
    assert "status\tfinished" in (
        logs / "finalization_attempt_status.tsv"
    ).read_text(encoding="utf-8")
    state_events = (logs / "run_state_events.tsv").read_text(encoding="utf-8")
    assert state_events.startswith("observed_at\tstate\tsource\tdetail\n")
    assert "\tTERMINAL_NORMAL\tfinal_sanity_and_archive\t" in state_events
    summary = (logs / "production_rep1_summary.tsv").read_text(encoding="utf-8")
    assert "performance_ns_per_day\t67.635" in summary
    assert "performance_hour_per_ns\t0.355" in summary
    archive = run_root / "production_archive.sha256"
    assert archive.is_file()
    assert "terminal_status.tsv" not in archive.read_text(encoding="utf-8")
    assert "run_state_events.tsv" not in archive.read_text(encoding="utf-8")
    archive_check = subprocess.run(
        ["sha256sum", "-c", str(archive)],
        cwd=run_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert archive_check.returncode == 0, archive_check.stderr
    assert (logs / "mdrun_issue_scan.log").read_text(encoding="utf-8") == ""


def test_completed_run_finalizer_rejects_missing_normal_completion_marker(
    tmp_path: Path,
) -> None:
    completed, run_root, forbidden_marker = _run_finalizer(
        tmp_path, include_main_completion=False
    )

    assert completed.returncode != 0
    assert "normal mdrun completion markers missing" in completed.stderr
    assert not forbidden_marker.exists()
    logs = run_root / "logs/production"
    snapshot = (logs / "terminal_status.tsv").read_text(encoding="utf-8")
    assert snapshot.startswith("status\tunresolved\nstate\tUNRESOLVED\n")
    assert "source\trun_state_events.tsv\n" in snapshot
    assert "allowed_use\tno_action_authority\n" in snapshot
    attempt = (logs / "finalization_attempt_status.tsv").read_text(
        encoding="utf-8"
    )
    assert "status\tfailed" in attempt
    assert "stage\tfinal_sanity" in attempt
    state_events = (logs / "run_state_events.tsv").read_text(encoding="utf-8")
    assert (
        "\tUNRESOLVED\tfinalizer\tfinalizer failed; "
        "stage=final_sanity;exit_code=1"
    ) in state_events
    assert not (run_root / "production_archive.sha256").exists()


def test_legacy_completed_run_is_backfilled_without_changing_finished_time(
    tmp_path: Path,
) -> None:
    run_root, fake_gmx = _completed_run(tmp_path)
    logs = run_root / "logs/production"
    finished_at = "2026-07-19T21:39:21+08:00"
    (logs / "terminal_status.tsv").write_text(
        f"status\tfinished\nfinished\t{finished_at}\n", encoding="utf-8"
    )
    (logs / "finalizer_exit_code.tsv").write_text(
        "exit_code\t0\n", encoding="utf-8"
    )
    (run_root / "production_archive.sha256").write_text(
        "legacy validated manifest\n", encoding="utf-8"
    )
    env = os.environ.copy()
    env.update(
        {
            "RUN_ROOT": str(run_root),
            "GMX_CMD": str(fake_gmx),
            "PREFIX": PREFIX,
        }
    )

    completed = subprocess.run(
        ["bash", str(SCRIPT), "--remote-migrate-completed-terminal-event"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    events = (logs / "run_state_events.tsv").read_text(encoding="utf-8")
    assert "\tTERMINAL_NORMAL\texisting_finalizer_evidence_migration\t" in events
    assert "backfilled_from_legacy_terminal=true" in events
    snapshot = (logs / "terminal_status.tsv").read_text(encoding="utf-8")
    assert f"finished\t{finished_at}\n" in snapshot
    assert "state\tTERMINAL_NORMAL\nsource\trun_state_events.tsv\n" in snapshot


def test_heartbeat_requires_run_specific_pid_and_records_fresh_identity(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "run"
    production = run_root / "production"
    logs = run_root / "logs/production"
    production.mkdir(parents=True)
    logs.mkdir(parents=True)
    fake_gmx = tmp_path / "fake_gmx_heartbeat"
    fake_gmx.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == dump ]]; then
  printf 'checkpoint dump ok\\n'
elif [[ ${1:-} == mdrun ]]; then
  sleep 30
else
  exit 64
fi
""",
        encoding="utf-8",
    )
    fake_gmx.chmod(0o755)
    fake_ps = tmp_path / "fake_ps"
    fake_ps.write_text(
        f"""#!/usr/bin/env bash
printf '%s\\n' '{fake_gmx} mdrun -deffnm {production / PREFIX}'
""",
        encoding="utf-8",
    )
    fake_ps.chmod(0o755)
    for suffix in ("tpr", "cpt", "log"):
        (production / f"{PREFIX}.{suffix}").write_text(
            f"fake {suffix}\n", encoding="utf-8"
        )
    process = subprocess.Popen(
        [
            str(fake_gmx),
            "mdrun",
            "-deffnm",
            str(production / PREFIX),
        ],
        cwd=run_root,
    )
    try:
        (logs / "mdrun_process.tsv").write_text(
            f"field\tvalue\nstate\trunning\npid\t{process.pid}\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env.update(
            {
                "RUN_ROOT": str(run_root),
                "GMX_CMD": str(fake_gmx),
                "PS_CMD": str(fake_ps),
                "PREFIX": PREFIX,
            }
        )

        completed = subprocess.run(
            ["bash", str(SCRIPT), "--remote-heartbeat"],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        process.terminate()
        process.wait(timeout=5)

    assert completed.returncode == 0, completed.stderr
    events = (logs / "run_state_events.tsv").read_text(encoding="utf-8")
    assert "\tRUNNING_VERIFIED\tlive_process_and_run_outputs\t" in events
    assert f"pid={process.pid};prefix={PREFIX};" in events
    assert "checkpoint_sha256=" in events
    snapshot = (logs / "terminal_status.tsv").read_text(encoding="utf-8")
    assert snapshot.startswith("status\trunning\nstate\tRUNNING_VERIFIED\n")


def test_postprocess_gate_uses_latest_event_and_archive_identity(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "run"
    logs = run_root / "logs/production"
    logs.mkdir(parents=True)
    archive = run_root / "production_archive.sha256"
    archive.write_text("validated manifest\n", encoding="utf-8")
    archive_sha = subprocess.check_output(
        ["sha256sum", str(archive)], text=True
    ).split()[0]
    events = logs / "run_state_events.tsv"
    events.write_text(
        "observed_at\tstate\tsource\tdetail\n"
        "2026-07-19T13:39:21Z\tTERMINAL_NORMAL\tfinalizer\t"
        f"archive_manifest_sha256={archive_sha}\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update({"RUN_ROOT": str(run_root), "PREFIX": PREFIX})

    accepted = subprocess.run(
        ["bash", str(POSTPROCESS_SCRIPT), "--verify-production-terminal"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert accepted.returncode == 0, accepted.stderr

    archive.write_text("changed manifest\n", encoding="utf-8")
    identity_rejected = subprocess.run(
        ["bash", str(POSTPROCESS_SCRIPT), "--verify-production-terminal"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert identity_rejected.returncode == 66
    assert "archive identity changed" in identity_rejected.stderr
    archive.write_text("validated manifest\n", encoding="utf-8")

    with events.open("a", encoding="utf-8") as handle:
        handle.write(
            "2026-07-19T13:40:21Z\tUNRESOLVED\tidentity_check\t"
            "archive changed\n"
        )
    rejected = subprocess.run(
        ["bash", str(POSTPROCESS_SCRIPT), "--verify-production-terminal"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode == 66
    assert "latest production state is UNRESOLVED" in rejected.stderr
