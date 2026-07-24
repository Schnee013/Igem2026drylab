#!/usr/bin/env bash
set -Eeuo pipefail

# Validate an already-stopped GPR production run and promote its terminal state.
# This script never launches or resumes mdrun.

: "${RUN_ROOT:?set RUN_ROOT}"
: "${GMX_CMD:?set GMX_CMD}"
: "${PREFIX:?set PREFIX}"

PROD_DIR=${PROD_DIR:-"$RUN_ROOT/production/rep1"}
LOG_DIR=${LOG_DIR:-"$RUN_ROOT/logs/production/rep1"}
SANITY_DIR=${SANITY_DIR:-"$RUN_ROOT/sanity/production/rep1"}
PYTHON_CMD=${PYTHON_CMD:-"$(dirname "$GMX_CMD")/python3"}
EXPECTED_XTC_ATOMS=${EXPECTED_XTC_ATOMS:?set EXPECTED_XTC_ATOMS}
EXPECTED_FRAMES=${EXPECTED_FRAMES:-2001}
EXPECTED_FINAL_STEP=${EXPECTED_FINAL_STEP:-100000000}
EXPECTED_FINAL_TIME_PS=${EXPECTED_FINAL_TIME_PS:-200000}
EXPECTED_DT_PS=${EXPECTED_DT_PS:-0.002}
EXPECTED_TPR_SHA256=${EXPECTED_TPR_SHA256:?set EXPECTED_TPR_SHA256}
IDENTITY_MANIFEST=${IDENTITY_MANIFEST:-"$PROD_DIR/production_launch_package.sha256"}
SOURCE_IDENTITY_MANIFEST=${SOURCE_IDENTITY_MANIFEST:-"$PROD_DIR/production_source_inputs.sha256"}
ATTEMPT_ID=${ATTEMPT_ID:-"completion_attempt3_$(date -u '+%Y%m%dT%H%M%SZ')"}

STATE_EVENTS="$LOG_DIR/run_state_events.tsv"
STATE_LOCK="$LOG_DIR/run_state.lock"
STATUS="$LOG_DIR/terminal_status.tsv"
ATTEMPT_DIR="$LOG_DIR/$ATTEMPT_ID"
ATTEMPT_STATUS="$ATTEMPT_DIR/completion_status.tsv"
TPR="$PROD_DIR/$PREFIX.tpr"
CPT="$PROD_DIR/$PREFIX.cpt"
GRO="$PROD_DIR/$PREFIX.gro"
XTC="$PROD_DIR/$PREFIX.xtc"
EDR="$PROD_DIR/$PREFIX.edr"
MDLOG="$PROD_DIR/$PREFIX.log"
MDRUN_CAPTURE="$LOG_DIR/mdrun_${PREFIX}.stdout_stderr.log"
SAMPLER="$LOG_DIR/nvidia_smi_mdrun_sampler.csv"
CURRENT_STAGE=preflight

current_timestamp() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

record_state() {
  local state=$1 source=$2 allowed_use=$3 detail=$4
  local lock_mode= lock_attempt=0 observed_at snapshot_tmp state_lock_fd
  observed_at=$(current_timestamp)
  detail=${detail//$'\t'/ }
  detail=${detail//$'\n'/ }
  source=${source//$'\t'/ }
  source=${source//$'\n'/ }

  if command -v flock >/dev/null 2>&1; then
    exec {state_lock_fd}> "$STATE_LOCK"
    flock -x "$state_lock_fd"
    lock_mode=flock
  else
    while ! mkdir "${STATE_LOCK}.d" 2>/dev/null; do
      lock_attempt=$((lock_attempt + 1))
      (( lock_attempt < 100 )) || return 75
      sleep 0.1
    done
    lock_mode=mkdir
  fi

  if [[ ! -s "$STATE_EVENTS" ]]; then
    printf 'observed_at\tstate\tsource\tdetail\n' > "$STATE_EVENTS"
  elif ! awk -F '\t' '
      NR == 1 && $0 != "observed_at\tstate\tsource\tdetail" { exit 1 }
      NR > 1 && NF != 4 { exit 1 }
    ' "$STATE_EVENTS"; then
    if [[ $lock_mode == flock ]]; then
      flock -u "$state_lock_fd"
      exec {state_lock_fd}>&-
    else
      rmdir "${STATE_LOCK}.d"
    fi
    return 75
  fi

  printf '%s\t%s\t%s\t%s\n' \
    "$observed_at" "$state" "$source" "$detail" >> "$STATE_EVENTS"

  snapshot_tmp=$(mktemp "$LOG_DIR/.terminal_status.tsv.XXXXXX")
  {
    printf 'key\tvalue\n'
    if [[ $state == TERMINAL_NORMAL ]]; then
      printf 'terminal_status\tPRODUCTION_COMPLETE\n'
      printf 'mdrun_started\tYES\n'
      printf 'production_completed\tYES\n'
    else
      printf 'terminal_status\tHOLD\n'
      printf 'mdrun_started\tYES\n'
      printf 'production_completed\tNO\n'
    fi
    printf 'run_state\t%s\n' "$state"
    printf 'attempt_id\t%s\n' "$ATTEMPT_ID"
    printf 'stage\tproduction_completion_gate\n'
    printf 'observed_at\t%s\n' "$observed_at"
    printf 'source\trun_state_events.tsv\n'
    printf 'allowed_use\t%s\n' "$allowed_use"
    printf 'update_trigger\tnew_run_state_event\n'
    printf 'detail\t%s\n' "$detail"
  } > "$snapshot_tmp"
  mv -f "$snapshot_tmp" "$STATUS"

  if [[ $lock_mode == flock ]]; then
    flock -u "$state_lock_fd"
    exec {state_lock_fd}>&-
  else
    rmdir "${STATE_LOCK}.d"
  fi
}

on_error() {
  local rc=$?
  trap - ERR
  set +e
  {
    printf 'key\tvalue\n'
    printf 'status\tHOLD\n'
    printf 'stage\t%s\n' "$CURRENT_STAGE"
    printf 'exit_code\t%s\n' "$rc"
    printf 'observed_at\t%s\n' "$(current_timestamp)"
  } > "$ATTEMPT_STATUS"
  record_state UNRESOLVED completion_gate no_action_authority \
    "attempt_id=$ATTEMPT_ID;stage=$CURRENT_STAGE;exit_code=$rc;evidence_dir=$ATTEMPT_DIR"
  exit "$rc"
}

mkdir -p "$ATTEMPT_DIR" "$SANITY_DIR"
trap on_error ERR
{
  printf 'key\tvalue\n'
  printf 'status\tRUNNING\n'
  printf 'stage\tpreflight\n'
  printf 'started_at\t%s\n' "$(current_timestamp)"
} > "$ATTEMPT_STATUS"

CURRENT_STAGE=active_process_gate
if pgrep -x gmx_mpi > "$ATTEMPT_DIR/active_gmx_mpi.tsv"; then
  echo "ERROR: active gmx_mpi detected; completion validation refused" >&2
  exit 75
fi
record_state UNRESOLVED completion_gate_started completion_gate_required \
  "attempt_id=$ATTEMPT_ID;active_gmx_mpi=false;evidence_dir=$ATTEMPT_DIR"

CURRENT_STAGE=required_files
for required in \
  "$TPR" "$CPT" "$GRO" "$XTC" "$EDR" "$MDLOG" \
  "$MDRUN_CAPTURE" "$SAMPLER" "$IDENTITY_MANIFEST" \
  "$SOURCE_IDENTITY_MANIFEST" "$PYTHON_CMD"; do
  if [[ ! -s "$required" ]]; then
    printf '%s\n' "$required" > "$ATTEMPT_DIR/missing_required_file.txt"
    echo "ERROR: missing or empty required file: $required" >&2
    exit 66
  fi
done

CURRENT_STAGE=identity_gate
(
  cd "$PROD_DIR"
  sha256sum -c "$(basename "$IDENTITY_MANIFEST")"
) > "$ATTEMPT_DIR/launch_identity_check.log" 2>&1
sha256sum -c "$SOURCE_IDENTITY_MANIFEST" \
  > "$ATTEMPT_DIR/source_identity_check.log" 2>&1
actual_tpr_sha=$(sha256sum "$TPR" | awk '{print $1}')
printf 'key\tactual\texpected\tstatus\n' > "$ATTEMPT_DIR/tpr_identity.tsv"
printf 'tpr_sha256\t%s\t%s\t%s\n' \
  "$actual_tpr_sha" "$EXPECTED_TPR_SHA256" \
  "$([[ $actual_tpr_sha == "$EXPECTED_TPR_SHA256" ]] && printf PASS || printf FAIL)" \
  >> "$ATTEMPT_DIR/tpr_identity.tsv"
[[ $actual_tpr_sha == "$EXPECTED_TPR_SHA256" ]]

CURRENT_STAGE=gromacs_sanity
"$GMX_CMD" check -f "$XTC" > "$ATTEMPT_DIR/gmx_check_xtc.log" 2>&1
"$GMX_CMD" check -e "$EDR" > "$ATTEMPT_DIR/gmx_check_edr.log" 2>&1
"$GMX_CMD" dump -cp "$CPT" > "$ATTEMPT_DIR/checkpoint_dump.log" 2>&1
"$GMX_CMD" dump -s "$TPR" > "$ATTEMPT_DIR/tpr_dump.log" 2>&1
printf 'Temperature\nPressure\nDensity\nPotential\n0\n' | \
  "$GMX_CMD" energy -f "$EDR" -o "$SANITY_DIR/${PREFIX}_energy.xvg" \
  > "$ATTEMPT_DIR/gmx_energy.log" 2>&1

CURRENT_STAGE=issue_scan
if grep -Ein \
    'Fatal error|LINCS WARNING|Segmentation fault|segfault|non-finite|(^|[^A-Za-z])nan([^A-Za-z]|$)|Out of memory|(^|[^A-Za-z])OOM([^A-Za-z]|$)|CUDA error|cudaError|invalid PTX|Killed' \
    "$MDLOG" "$MDRUN_CAPTURE" > "$ATTEMPT_DIR/issue_scan.log"; then
  echo "ERROR: production issue scan is not empty" >&2
  exit 1
fi

CURRENT_STAGE=semantic_gate
"$PYTHON_CMD" - \
  "$ATTEMPT_DIR/gmx_check_xtc.log" \
  "$ATTEMPT_DIR/gmx_check_edr.log" \
  "$ATTEMPT_DIR/checkpoint_dump.log" \
  "$ATTEMPT_DIR/tpr_dump.log" \
  "$MDLOG" "$GRO" "$SAMPLER" \
  "$EXPECTED_XTC_ATOMS" "$EXPECTED_FRAMES" \
  "$EXPECTED_FINAL_STEP" "$EXPECTED_FINAL_TIME_PS" "$EXPECTED_DT_PS" \
  > "$ATTEMPT_DIR/completion_summary.tsv" <<'PY'
from pathlib import Path
import csv
import re
import sys

(
    xtc_path,
    edr_path,
    checkpoint_path,
    tpr_path,
    log_path,
    gro_path,
    sampler_path,
    expected_atoms,
    expected_frames,
    expected_step,
    expected_time,
    expected_dt,
) = sys.argv[1:]
expected_atoms = int(expected_atoms)
expected_frames = int(expected_frames)
expected_step = int(expected_step)
expected_time = float(expected_time)
expected_dt = float(expected_dt)

xtc = Path(xtc_path).read_text(errors="replace").replace("\r", "\n")
edr = Path(edr_path).read_text(errors="replace").replace("\r", "\n")
checkpoint = Path(checkpoint_path).read_text(errors="replace")
tpr = Path(tpr_path).read_text(errors="replace")
log = Path(log_path).read_text(errors="replace").replace("\r", "\n")

atoms_match = re.search(r"# Atoms\s+(\d+)", xtc)
xtc_last = re.findall(r"Last frame\s+(\d+)\s+time\s+([0-9.]+)", xtc)
edr_last = re.findall(r"Last energy frame read\s+\d+\s+time\s+([0-9.]+)", edr)
checkpoint_step = re.search(r"^step\s*=\s*(\d+)\s*$", checkpoint, re.MULTILINE)
checkpoint_time = re.search(r"^t\s*=\s*([0-9.]+)\s*$", checkpoint, re.MULTILINE)
tpr_nsteps = re.search(r"^\s*nsteps\s*=\s*(\d+)\s*$", tpr, re.MULTILINE)
tpr_dt = re.search(r"^\s*dt\s*=\s*([0-9.eE+-]+)\s*$", tpr, re.MULTILINE)
progress = re.findall(r"^\s*(\d+)\s+([0-9.]+)\s*$", log, re.MULTILINE)
completion = re.findall(r"^Finished mdrun on rank 0\s+.+$", log, re.MULTILINE)
performance = re.findall(
    r"^Performance:\s+([0-9.]+)\s+([0-9.]+)", log, re.MULTILINE
)

if not atoms_match or int(atoms_match.group(1)) != expected_atoms:
    raise SystemExit("unexpected production XTC atom count")
if not xtc_last:
    raise SystemExit("missing production XTC final frame")
last_frame_index, xtc_time = int(xtc_last[-1][0]), float(xtc_last[-1][1])
if last_frame_index + 1 != expected_frames or abs(xtc_time - expected_time) > 0.01:
    raise SystemExit("unexpected production XTC frame count or final time")
if not edr_last or abs(float(edr_last[-1]) - expected_time) > 0.01:
    raise SystemExit("unexpected production EDR final time")
if (
    not checkpoint_step
    or int(checkpoint_step.group(1)) <= 0
    or int(checkpoint_step.group(1)) > expected_step
):
    raise SystemExit("invalid final checkpoint step")
if (
    not checkpoint_time
    or float(checkpoint_time.group(1)) <= 0
    or float(checkpoint_time.group(1)) > expected_time + 0.01
):
    raise SystemExit("invalid final checkpoint time")
if not tpr_nsteps or int(tpr_nsteps.group(1)) != expected_step:
    raise SystemExit("unexpected TPR nsteps")
if not tpr_dt or abs(float(tpr_dt.group(1)) - expected_dt) > 1e-12:
    raise SystemExit("unexpected TPR dt")
if not progress or int(progress[-1][0]) != expected_step:
    raise SystemExit("unexpected final log step")
if abs(float(progress[-1][1]) - expected_time) > 0.01:
    raise SystemExit("unexpected final log time")
if not completion or not performance:
    raise SystemExit("normal mdrun completion markers missing")

gro_lines = Path(gro_path).read_text(errors="replace").splitlines()
if len(gro_lines) < 3 or int(gro_lines[1].strip()) != expected_atoms:
    raise SystemExit("unexpected final GRO atom count")

samples = []
for row in csv.reader(Path(sampler_path).open(errors="replace")):
    if len(row) < 6:
        continue
    try:
        samples.append(tuple(float(value.strip()) for value in row[1:6]))
    except ValueError:
        continue

perf = performance[-1]
rows = [
    ("status", "PASS"),
    ("xtc_atoms", str(expected_atoms)),
    ("xtc_frames", str(expected_frames)),
    ("final_step", str(expected_step)),
    ("final_time_ps", f"{expected_time:.3f}"),
    ("checkpoint_step", checkpoint_step.group(1)),
    ("checkpoint_time_ps", checkpoint_time.group(1)),
    ("tpr_nsteps", tpr_nsteps.group(1)),
    ("tpr_dt_ps", tpr_dt.group(1)),
    ("performance_ns_per_day", perf[0]),
    ("performance_hour_per_ns", perf[1]),
    ("gpu_samples", str(len(samples))),
    ("gpu_utilization_avg_percent", f"{sum(row[0] for row in samples) / len(samples):.2f}" if samples else ""),
]
print("key\tvalue")
for key, value in rows:
    print(f"{key}\t{value}")
PY

CURRENT_STAGE=archive
archive_manifest="$ATTEMPT_DIR/production_archive.sha256"
attempt_rel=${ATTEMPT_DIR#"$RUN_ROOT/"}
(
  cd "$RUN_ROOT"
  find production/rep1 logs/production/rep1 sanity/production/rep1 \
    -type f \
    ! -path "$attempt_rel/*" \
    ! -path 'logs/production/rep1/terminal_status.tsv' \
    ! -path 'logs/production/rep1/run_state_events.tsv' \
    ! -path 'logs/production/rep1/run_state.lock' \
    -print0 \
    | sort -z | xargs -0 sha256sum > "$archive_manifest"
  sha256sum -c "$archive_manifest" > "$ATTEMPT_DIR/production_archive_check.log"
)
archive_manifest_sha=$(sha256sum "$archive_manifest" | awk '{print $1}')

find "$ATTEMPT_DIR" -maxdepth 1 -type f \
  ! -name 'completion_evidence.sha256' \
  ! -name 'completion_status.tsv' \
  -print0 | sort -z | xargs -0 sha256sum \
  > "$ATTEMPT_DIR/completion_evidence.sha256"

CURRENT_STAGE=terminal_promotion
{
  printf 'key\tvalue\n'
  printf 'status\tPASS\n'
  printf 'stage\tproduction_completion_gate\n'
  printf 'completed_at\t%s\n' "$(current_timestamp)"
  printf 'archive_manifest\t%s\n' "$archive_manifest"
  printf 'archive_manifest_sha256\t%s\n' "$archive_manifest_sha"
} > "$ATTEMPT_STATUS"
record_state TERMINAL_NORMAL completion_gate terminal_gate \
  "attempt_id=$ATTEMPT_ID;evidence_dir=$ATTEMPT_DIR;archive_manifest=$archive_manifest;archive_manifest_sha256=$archive_manifest_sha;tpr_sha256=$actual_tpr_sha;final_step=$EXPECTED_FINAL_STEP;final_time_ps=$EXPECTED_FINAL_TIME_PS"
trap - ERR
printf 'status\tPASS\nattempt_id\t%s\nevidence_dir\t%s\n' "$ATTEMPT_ID" "$ATTEMPT_DIR"
