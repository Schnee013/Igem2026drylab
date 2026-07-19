#!/usr/bin/env bash
set -Eeuo pipefail

REMOTE=${REMOTE:-nkuliulab-e2}
RUN_ROOT=${RUN_ROOT:-/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716}
GMX_CMD=${GMX_CMD:-/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi}
PS_CMD=${PS_CMD:-ps}
NTHREADS=${NTHREADS:-24}
MAXWARN=${MAXWARN:-11}
NSTEPS=${NSTEPS:-100000000}
PREFIX=${PREFIX:-gpr2_r59c_ascr18_rep1_200ns}
SESSION=${SESSION:-gpr2_r59c_prod_rep1_20260716}
HEARTBEAT_INTERVAL_SECONDS=${HEARTBEAT_INTERVAL_SECONDS:-1800}
HEARTBEAT_INITIAL_DELAY_SECONDS=${HEARTBEAT_INITIAL_DELAY_SECONDS:-60}
HEARTBEAT_RETRY_SECONDS=${HEARTBEAT_RETRY_SECONDS:-300}
HEARTBEAT_MAX_PROGRESS_AGE_SECONDS=${HEARTBEAT_MAX_PROGRESS_AGE_SECONDS:-900}
HEARTBEAT_MAX_CHECKPOINT_AGE_SECONDS=${HEARTBEAT_MAX_CHECKPOINT_AGE_SECONDS:-3600}
HEARTBEAT_CHECKPOINT_GRACE_SECONDS=${HEARTBEAT_CHECKPOINT_GRACE_SECONDS:-2700}

PREPROD_DIR="$RUN_ROOT/preproduction/gromacs"
PREPROD_LOG="$RUN_ROOT/logs/preproduction"
PROD_DIR="$RUN_ROOT/production"
LOG_DIR="$RUN_ROOT/logs/production"
SANITY_DIR="$RUN_ROOT/sanity/production"
STATE_EVENTS="$LOG_DIR/run_state_events.tsv"
STATE_LOCK="$LOG_DIR/run_state.lock"
MD_RUN_PROCESS="$LOG_DIR/mdrun_process.tsv"

current_timestamp() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

file_mtime_epoch() {
  local path=$1
  if stat -c %Y "$path" >/dev/null 2>&1; then
    stat -c %Y "$path"
  else
    stat -f %m "$path"
  fi
}

record_state() {
  local legacy_status=$1 canonical_state=$2 source=$3 allowed_use=$4 detail=$5
  local finished_at=${6:-}
  local lock_attempt=0 lock_mode= observed_at snapshot_tmp state_lock_fd
  observed_at=$(current_timestamp)
  source=${source//$'\t'/ }
  source=${source//$'\n'/ }
  detail=${detail//$'\t'/ }
  detail=${detail//$'\n'/ }
  mkdir -p "$LOG_DIR"
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
    "$observed_at" "$canonical_state" "$source" "$detail" >> "$STATE_EVENTS"
  snapshot_tmp=$(mktemp "$LOG_DIR/.terminal_status.tsv.XXXXXX")
  if [[ $legacy_status == finished ]]; then
    printf 'status\tfinished\nfinished\t%s\nstate\t%s\nsource\t%s\nas_of\t%s\nallowed_use\t%s\nupdate_trigger\tnew_run_state_event\ndetail\t%s\n' \
      "${finished_at:-$observed_at}" "$canonical_state" run_state_events.tsv \
      "$observed_at" "$allowed_use" "$detail" > "$snapshot_tmp"
  else
    printf 'status\t%s\nstate\t%s\nsource\t%s\nas_of\t%s\nallowed_use\t%s\nupdate_trigger\tnew_run_state_event\ndetail\t%s\n' \
      "$legacy_status" "$canonical_state" run_state_events.tsv "$observed_at" \
      "$allowed_use" "$detail" > "$snapshot_tmp"
  fi
  mv -f "$snapshot_tmp" "$LOG_DIR/terminal_status.tsv"
  if [[ $lock_mode == flock ]]; then
    flock -u "$state_lock_fd"
    exec {state_lock_fd}>&-
  else
    rmdir "${STATE_LOCK}.d"
  fi
}

write_mdrun_process() {
  local state=$1 pid=$2 exit_code=${3:-}
  local process_tmp
  process_tmp=$(mktemp "$LOG_DIR/.mdrun_process.tsv.XXXXXX")
  printf 'field\tvalue\nstate\t%s\npid\t%s\nupdated_at\t%s\n' \
    "$state" "$pid" "$(current_timestamp)" > "$process_tmp"
  if [[ -n $exit_code ]]; then
    printf 'exit_code\t%s\n' "$exit_code" >> "$process_tmp"
  fi
  mv -f "$process_tmp" "$MD_RUN_PROCESS"
}

warning_gate() {
  local log_path=$1
  python3 - "$log_path" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(errors="replace")
if "Fatal error" in text:
    raise SystemExit(f"fatal grompp error in {path}")
lines = text.splitlines()
warnings = [index for index, line in enumerate(lines) if line.startswith("WARNING ")]
if len(warnings) != 11:
    raise SystemExit(f"unexpected warning count in {path}: {len(warnings)}")
for index in warnings:
    header = lines[index]
    body = "\n".join(lines[index:index + 6])
    if "[file cgenff_ASCR18.itp," not in header:
        raise SystemExit(f"unexpected warning source: {header}")
    if "Encountered a second line of parameters for dihedral type 9" not in body:
        raise SystemExit(f"unexpected warning body: {header}")
Path(str(path) + ".warning_gate.tsv").write_text(
    "field\tvalue\n"
    "status\taccepted\n"
    "duplicate_type9_warning_count\t11\n"
)
PY
}

gpu_idle_gate() {
  local sample=0 active_apps util mem streak=0
  : > "$LOG_DIR/gpu_gate_samples.tsv"
  printf 'sample\ttimestamp\tapps\tutilization_gpu\tmemory_used_mib\n' \
    >> "$LOG_DIR/gpu_gate_samples.tsv"
  while IFS=, read -r util mem; do
    sample=$((sample + 1))
    active_apps=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory \
      --format=csv,noheader,nounits 2>/dev/null || true)
    util=${util//[[:space:]]/}
    mem=${mem//[[:space:]]/}
    printf '%s\t%s\t%s\t%s\t%s\n' "$sample" "$(date -Is)" \
      "${active_apps:-none}" "${util:-NA}" "${mem:-NA}" \
      >> "$LOG_DIR/gpu_gate_samples.tsv"
    if [[ -z "$active_apps" && "$util" == "0" && "$mem" == "0" ]]; then
      streak=$((streak + 1))
    else
      streak=0
    fi
    [[ $streak -lt 5 ]] || return 0
    [[ $sample -lt 8 ]] || break
  done < <(
    timeout 12 nvidia-smi \
      --query-gpu=utilization.gpu,memory.used \
      --format=csv,noheader,nounits \
      -l 1 2>/dev/null
  )
  return 1
}

make_production_input() {
  python3 - "$PREPROD_DIR/step7_production.mdp" "$PROD_DIR/${PREFIX}.mdp" "$NSTEPS" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
nsteps = sys.argv[3]
values = {
    "nsteps": nsteps,
    "continuation": "yes",
    "gen-vel": "no",
}
drop = {"gen-temp", "gen-seed"}
seen = set()
out = []
for raw in source.read_text().splitlines():
    stripped = raw.strip()
    key = stripped.split("=", 1)[0].strip().replace("_", "-") if "=" in stripped else ""
    if key in values:
        out.append(f"{key:<24s}= {values[key]}")
        seen.add(key)
    elif key not in drop:
        out.append(raw)
for key, value in values.items():
    if key not in seen:
        out.append(f"{key:<24s}= {value}")
target.write_text("\n".join(out) + "\n")
PY

  (
    cd "$PREPROD_DIR"
    "$GMX_CMD" grompp \
      -f "$PROD_DIR/${PREFIX}.mdp" \
      -c step6.6.gro \
      -p topol_phase3.top \
      -n index.fixed.ndx \
      -o "$PROD_DIR/${PREFIX}.tpr" \
      -po "$PROD_DIR/${PREFIX}_out.mdp" \
      -maxwarn "$MAXWARN"
  ) > "$LOG_DIR/grompp_${PREFIX}.log" 2>&1
  warning_gate "$LOG_DIR/grompp_${PREFIX}.log"
}

final_sanity() {
  "$GMX_CMD" check -f "$PROD_DIR/${PREFIX}.xtc" \
    > "$LOG_DIR/gmx_check_production_xtc.log" 2>&1
  "$GMX_CMD" check -e "$PROD_DIR/${PREFIX}.edr" \
    > "$LOG_DIR/gmx_check_production_edr.log" 2>&1
  printf 'Temperature\nPressure\nDensity\nPotential\n0\n' | "$GMX_CMD" energy \
    -f "$PROD_DIR/${PREFIX}.edr" \
    -o "$SANITY_DIR/${PREFIX}_energy.xvg" \
    > "$LOG_DIR/gmx_energy_production.log" 2>&1

  if grep -Ein \
      'Fatal error|LINCS WARNING|Segmentation fault|non-finite|(^|[^A-Za-z])nan([^A-Za-z]|$)|Out of memory|Killed' \
      "$LOG_DIR/mdrun_${PREFIX}.log" "$PROD_DIR/${PREFIX}.log" \
      > "$LOG_DIR/mdrun_issue_scan.log"; then
    return 1
  fi

  python3 - "$LOG_DIR/gmx_check_production_xtc.log" \
    "$LOG_DIR/gmx_check_production_edr.log" \
    "$LOG_DIR/mdrun_${PREFIX}.log" \
    "$PROD_DIR/${PREFIX}.log" <<'PY'
from pathlib import Path
import re
import sys

xtc = Path(sys.argv[1]).read_text(errors="replace").replace("\r", "\n")
edr = Path(sys.argv[2]).read_text(errors="replace").replace("\r", "\n")
mdrun = Path(sys.argv[3]).read_text(errors="replace")
production_log = Path(sys.argv[4]).read_text(errors="replace")
completion_text = (mdrun + "\n" + production_log).replace("\r", "\n")
atoms = re.search(r"# Atoms\s+(\d+)", xtc)
xtc_last = re.findall(r"Last frame\s+\d+\s+time\s+([0-9.]+)", xtc)
edr_last = re.findall(r"Last energy frame read\s+\d+\s+time\s+([0-9.]+)", edr)
completion = re.findall(r"^Finished mdrun on rank 0\s+.+$", completion_text, re.MULTILINE)
performance = re.findall(
    r"^Performance:\s+([0-9.]+)\s+([0-9.]+)\s*$",
    completion_text,
    re.MULTILINE,
)
if not atoms or int(atoms.group(1)) != 130638:
    raise SystemExit(f"unexpected production XTC atom count: {atoms.group(1) if atoms else 'missing'}")
if not xtc_last or abs(float(xtc_last[-1]) - 200000.0) > 0.01:
    raise SystemExit(f"unexpected final XTC time: {xtc_last[-1] if xtc_last else 'missing'}")
if not edr_last or abs(float(edr_last[-1]) - 200000.0) > 0.01:
    raise SystemExit(f"unexpected final EDR time: {edr_last[-1] if edr_last else 'missing'}")
if not completion or not performance:
    raise SystemExit("normal mdrun completion markers missing")
PY
}

write_summary() {
  python3 - "$LOG_DIR/mdrun_${PREFIX}.log" "$PROD_DIR/${PREFIX}.log" \
    "$LOG_DIR/nvidia_smi_mdrun_sampler.csv" <<'PY'
from pathlib import Path
import csv
import re
import sys

log = (
    Path(sys.argv[1]).read_text(errors="replace")
    + "\n"
    + Path(sys.argv[2]).read_text(errors="replace")
).replace("\r", "\n")
performance_rows = re.findall(
    r"^Performance:\s+([0-9.]+)\s+([0-9.]+)", log, re.MULTILINE
)
perf = performance_rows[-1] if performance_rows else None
samples = []
for row in csv.reader(Path(sys.argv[3]).open()):
    if len(row) < 6:
        continue
    try:
        samples.append(tuple(float(value.strip()) for value in row[1:6]))
    except ValueError:
        continue
util = [row[0] for row in samples]
nonzero = [value for value in util if value > 0]
mem = [row[1] for row in samples]
power = [row[3] for row in samples]
temp = [row[4] for row in samples]
rows = [
    ("status", "finished"),
    ("system", "Gpr2_R59C_ASCR18"),
    ("nsteps", "100000000"),
    ("nominal_ns", "200"),
    ("atoms", "130638"),
    ("performance_ns_per_day", perf[0] if perf else ""),
    ("performance_hour_per_ns", perf[1] if perf else ""),
    ("gpu_samples", str(len(samples))),
    ("gpu_utilization_avg_percent", f"{sum(util)/len(util):.2f}" if util else ""),
    ("gpu_utilization_nonzero_avg_percent", f"{sum(nonzero)/len(nonzero):.2f}" if nonzero else ""),
    ("gpu_utilization_max_percent", f"{max(util):.0f}" if util else ""),
    ("gpu_memory_max_mib", f"{max(mem):.0f}" if mem else ""),
    ("gpu_power_avg_w", f"{sum(power)/len(power):.2f}" if power else ""),
    ("gpu_temperature_max_c", f"{max(temp):.0f}" if temp else ""),
]
Path("logs/production/production_rep1_summary.tsv").write_text(
    "key\tvalue\n" + "\n".join(f"{key}\t{value}" for key, value in rows) + "\n"
)
PY
}

archive_and_promote() {
  local archive_manifest_sha
  write_summary
  find production logs/production sanity/production \
    -type f \
    ! -path 'logs/production/terminal_status.tsv' \
    ! -path 'logs/production/run_state_events.tsv' \
    ! -path 'logs/production/run_state.lock' \
    -print0 \
    | sort -z | xargs -0 sha256sum > "$RUN_ROOT/production_archive.sha256"
  archive_manifest_sha=$(sha256sum "$RUN_ROOT/production_archive.sha256" | awk '{print $1}')
  record_state \
    finished \
    TERMINAL_NORMAL \
    final_sanity_and_archive \
    terminal_gate \
    "archive_manifest_sha256=$archive_manifest_sha"
}

finalize_completed() {
  local stage=preflight required
  local attempt_status="$LOG_DIR/finalization_attempt_status.tsv"
  mkdir -p "$PROD_DIR" "$LOG_DIR" "$SANITY_DIR"
  cd "$RUN_ROOT"
  trap 'rc=$?; record_state unresolved UNRESOLVED finalizer no_action_authority "finalizer failed; stage=$stage;exit_code=$rc"; printf "status\tfailed\nstage\t%s\nexit_code\t%s\nfailed\t%s\n" "$stage" "$rc" "$(date -Is)" > "$attempt_status"' ERR
  printf 'status\trunning\nmode\tfinalize_completed\nstarted\t%s\n' "$(date -Is)" \
    > "$attempt_status"

  if pgrep -ax gmx_mpi > "$LOG_DIR/finalization_process_check.tsv"; then
    record_state \
      unresolved \
      UNRESOLVED \
      finalizer_process_gate \
      no_action_authority \
      "active gmx_mpi detected; terminal validation refused"
    trap - ERR
    printf 'status\trefuse_active_gmx_mpi\nchecked\t%s\n' "$(date -Is)" \
      > "$attempt_status"
    return 75
  fi

  for required in \
    "$PROD_DIR/${PREFIX}.tpr" \
    "$PROD_DIR/${PREFIX}.cpt" \
    "$PROD_DIR/${PREFIX}.gro" \
    "$PROD_DIR/${PREFIX}.xtc" \
    "$PROD_DIR/${PREFIX}.edr" \
    "$PROD_DIR/${PREFIX}.log" \
    "$LOG_DIR/mdrun_${PREFIX}.log" \
    "$LOG_DIR/nvidia_smi_mdrun_sampler.csv"; do
    if [[ ! -s "$required" ]]; then
      record_state \
        unresolved \
        UNRESOLVED \
        finalizer_required_input_gate \
        no_action_authority \
        "missing_or_empty=$required"
      trap - ERR
      printf 'status\tmissing_required_completed_run_input\npath\t%s\nchecked\t%s\n' \
        "$required" "$(date -Is)" > "$attempt_status"
      return 66
    fi
  done

  stage=final_sanity
  final_sanity
  stage=archive_and_promote
  printf 'status\tfinished\nmode\tfinalize_completed\nfinished\t%s\n' "$(date -Is)" \
    > "$attempt_status"
  archive_and_promote
  trap - ERR
}

record_heartbeat() {
  local process_snapshot="$LOG_DIR/heartbeat_process_snapshot.tsv"
  local checkpoint_dump="$LOG_DIR/heartbeat_checkpoint_dump.txt"
  local checkpoint_sha=not_available checkpoint_age=not_available
  local command_line detail now_epoch process_age process_state progress_age
  local mdrun_pid
  mkdir -p "$PROD_DIR" "$LOG_DIR" "$SANITY_DIR"
  cd "$RUN_ROOT"

  if [[ ! -s "$MD_RUN_PROCESS" ]]; then
    record_state unresolved UNRESOLVED heartbeat_process_identity \
      no_action_authority "missing=$MD_RUN_PROCESS"
    return 75
  fi
  process_state=$(awk -F '\t' '$1 == "state" { print $2; exit }' "$MD_RUN_PROCESS")
  mdrun_pid=$(awk -F '\t' '$1 == "pid" { print $2; exit }' "$MD_RUN_PROCESS")
  if [[ $process_state != running || ! $mdrun_pid =~ ^[0-9]+$ ]] \
      || ! kill -0 "$mdrun_pid" 2>/dev/null; then
    record_state unresolved UNRESOLVED heartbeat_process_identity \
      no_action_authority \
      "process_state=${process_state:-missing};pid=${mdrun_pid:-missing};active=false"
    return 75
  fi
  if ! command_line=$("$PS_CMD" -p "$mdrun_pid" -o args=) \
      || [[ -z $command_line ]]; then
    record_state unresolved UNRESOLVED heartbeat_process_identity \
      no_action_authority "pid=$mdrun_pid;process_command_unavailable=true"
    return 75
  fi
  printf 'field\tvalue\npid\t%s\ncommand\t%s\nobserved_at\t%s\n' \
    "$mdrun_pid" "$command_line" "$(current_timestamp)" > "$process_snapshot"
  if [[ $command_line != *"$GMX_CMD mdrun"* ]] \
      || [[ $command_line != *"$PROD_DIR/$PREFIX"* ]]; then
    record_state unresolved UNRESOLVED heartbeat_process_identity \
      no_action_authority \
      "pid=$mdrun_pid;command_identity_mismatch=true"
    return 75
  fi
  for required in \
    "$PROD_DIR/${PREFIX}.tpr" \
    "$PROD_DIR/${PREFIX}.log"; do
    if [[ ! -s "$required" ]]; then
      record_state unresolved UNRESOLVED heartbeat_required_output \
        no_action_authority "missing_or_empty=$required"
      return 75
    fi
  done

  now_epoch=$(date +%s)
  process_age=$((now_epoch - $(file_mtime_epoch "$MD_RUN_PROCESS")))
  progress_age=$((now_epoch - $(file_mtime_epoch "$PROD_DIR/${PREFIX}.log")))
  if (( progress_age > HEARTBEAT_MAX_PROGRESS_AGE_SECONDS )); then
    record_state unresolved UNRESOLVED heartbeat_progress_freshness \
      no_action_authority \
      "pid=$mdrun_pid;progress_log_age_seconds=$progress_age"
    return 75
  fi

  if [[ -s "$PROD_DIR/${PREFIX}.cpt" ]]; then
    checkpoint_age=$((now_epoch - $(file_mtime_epoch "$PROD_DIR/${PREFIX}.cpt")))
    if (( checkpoint_age > HEARTBEAT_MAX_CHECKPOINT_AGE_SECONDS )); then
      record_state unresolved UNRESOLVED heartbeat_checkpoint_freshness \
        no_action_authority \
        "pid=$mdrun_pid;checkpoint_age_seconds=$checkpoint_age"
      return 75
    fi
    if ! "$GMX_CMD" dump -cp "$PROD_DIR/${PREFIX}.cpt" \
        > "$checkpoint_dump" 2>&1; then
      record_state unresolved UNRESOLVED heartbeat_checkpoint_parse \
        no_action_authority "pid=$mdrun_pid;checkpoint_parse_failed=true"
      return 75
    fi
    if ! checkpoint_sha=$(sha256sum "$PROD_DIR/${PREFIX}.cpt" | awk '{print $1}'); then
      record_state unresolved UNRESOLVED heartbeat_checkpoint_identity \
        no_action_authority "pid=$mdrun_pid;checkpoint_sha256_failed=true"
      return 75
    fi
  elif (( process_age > HEARTBEAT_CHECKPOINT_GRACE_SECONDS )); then
    record_state unresolved UNRESOLVED heartbeat_checkpoint_missing \
      no_action_authority \
      "pid=$mdrun_pid;process_age_seconds=$process_age"
    return 75
  fi

  detail="pid=$mdrun_pid;prefix=$PREFIX;progress_log_age_seconds=$progress_age"
  detail+=";checkpoint_age_seconds=$checkpoint_age;checkpoint_sha256=$checkpoint_sha"
  record_state running RUNNING_VERIFIED live_process_and_run_outputs \
    current_view_for_6h "$detail"
}

heartbeat_loop() {
  local delay=$HEARTBEAT_INITIAL_DELAY_SECONDS mdrun_pid=$1
  while kill -0 "$mdrun_pid" 2>/dev/null; do
    sleep "$delay"
    kill -0 "$mdrun_pid" 2>/dev/null || break
    if record_heartbeat; then
      delay=$HEARTBEAT_INTERVAL_SECONDS
    else
      delay=$HEARTBEAT_RETRY_SECONDS
    fi
  done
}

migrate_completed_terminal_event() {
  local archive_manifest_sha expected_manifest_sha finished_at latest_detail latest_state
  mkdir -p "$LOG_DIR"
  cd "$RUN_ROOT"
  grep -Fxq $'status\tfinished' "$LOG_DIR/terminal_status.tsv"
  grep -Fxq $'exit_code\t0' "$LOG_DIR/finalizer_exit_code.tsv"
  [[ -s "$RUN_ROOT/production_archive.sha256" ]]
  archive_manifest_sha=$(sha256sum "$RUN_ROOT/production_archive.sha256" | awk '{print $1}')
  if [[ -s "$STATE_EVENTS" ]]; then
    latest_state=$(awk -F '\t' 'NR > 1 && NF >= 4 { state=$2 } END { print state }' \
      "$STATE_EVENTS")
    if [[ $latest_state == TERMINAL_NORMAL ]]; then
      latest_detail=$(awk -F '\t' 'NR > 1 && NF >= 4 { detail=$4 } END { print detail }' \
        "$STATE_EVENTS")
      expected_manifest_sha=$(awk -v RS=';' -F= \
        '$1 == "archive_manifest_sha256" { print $2; exit }' <<< "$latest_detail")
      if [[ $expected_manifest_sha == "$archive_manifest_sha" ]]; then
        return 0
      fi
      record_state unresolved UNRESOLVED terminal_identity_migration \
        no_action_authority \
        "event_archive_manifest_sha256=${expected_manifest_sha:-missing};current_archive_manifest_sha256=$archive_manifest_sha"
      return 66
    fi
  fi
  finished_at=$(awk -F '\t' '$1 == "finished" { print $2; exit }' \
    "$LOG_DIR/terminal_status.tsv")
  [[ -n $finished_at ]]
  record_state finished TERMINAL_NORMAL existing_finalizer_evidence_migration \
    terminal_gate \
    "terminal_finished_at=$finished_at;archive_manifest_sha256=$archive_manifest_sha;backfilled_from_legacy_terminal=true" \
    "$finished_at"
}

cleanup_runner_processes() {
  local pid
  for pid in "${heartbeat_pid:-}" "${sampler_pid:-}" "${mdrun_pid:-}"; do
    [[ -z $pid ]] || kill "$pid" 2>/dev/null || true
  done
  for pid in "${heartbeat_pid:-}" "${sampler_pid:-}" "${mdrun_pid:-}"; do
    [[ -z $pid ]] || wait "$pid" 2>/dev/null || true
  done
}

remote_run() {
  local run_mode=${1:-launch} stage
  local sampler_pid= heartbeat_pid= mdrun_pid= mdrun_status termination_signal=
  mkdir -p "$PROD_DIR" "$LOG_DIR" "$SANITY_DIR"
  cd "$RUN_ROOT"

  if ! grep -Fxq $'status\tfinished' "$PREPROD_LOG/preproduction_benchmark_summary.tsv"; then
    record_state unresolved UNRESOLVED preproduction_benchmark_gate \
      no_action_authority "preproduction_benchmark_not_finished=true"
    exit 66
  fi
  for required in \
    "$PREPROD_DIR/step6.6.gro" \
    "$PREPROD_DIR/topol_phase3.top" \
    "$PREPROD_DIR/index.fixed.ndx" \
    "$PREPROD_DIR/step7_production.mdp" \
    "$PREPROD_DIR/ASCR18.itp" \
    "$PREPROD_DIR/toppar/cgenff_ASCR18.itp"; do
    [[ -s "$required" ]]
  done
  if [[ $run_mode == launch ]]; then
    for output in \
      "$PROD_DIR/${PREFIX}.xtc" \
      "$PROD_DIR/${PREFIX}.edr" \
      "$PROD_DIR/${PREFIX}.cpt" \
      "$PROD_DIR/${PREFIX}.gro" \
      "$PROD_DIR/${PREFIX}.log"; do
      if [[ -e "$output" ]]; then
        record_state unresolved UNRESOLVED launch_existing_output_gate \
          no_action_authority "refuse_existing_mdrun_output=$output"
        exit 66
      fi
    done
  elif [[ $run_mode == resume ]]; then
    [[ -s "$PROD_DIR/${PREFIX}.tpr" && -s "$PROD_DIR/${PREFIX}.cpt" ]]
    if [[ -s "$PROD_DIR/${PREFIX}.gro" ]] \
        || grep -q 'Finished mdrun on rank 0' "$PROD_DIR/${PREFIX}.log" 2>/dev/null; then
      record_state unresolved UNRESOLVED resume_completed_output_gate \
        no_action_authority "refuse_resume_completed_mdrun=true"
      exit 66
    fi
    if pgrep -ax gmx_mpi > "$LOG_DIR/resume_process_check.tsv"; then
      record_state unresolved UNRESOLVED resume_active_process_gate \
        no_action_authority "refuse_resume_active_process=true"
      exit 66
    fi
  else
    echo "ERROR: unsupported run mode $run_mode" >&2
    exit 64
  fi

  if [[ $run_mode == launch ]]; then
    date -Is > "$LOG_DIR/run_start_time.txt"
  else
    date -Is > "$LOG_DIR/run_resume_time.txt"
  fi
  hostname > "$LOG_DIR/hostname.txt"
  whoami > "$LOG_DIR/whoami.txt"
  nvidia-smi > "$LOG_DIR/nvidia_smi_before.log"
  "$GMX_CMD" --version > "$LOG_DIR/gmx_version.log" 2>&1
  if [[ $run_mode == launch ]]; then
    make_production_input
  fi

  if ! gpu_idle_gate; then
    record_state unresolved UNRESOLVED gpu_idle_gate \
      no_action_authority "gpu_busy_before_production=true"
    exit 75
  fi

  record_state running UNRESOLVED launch_or_resume_attempt \
    launch_confirmation_only \
    "mode=$run_mode; live heartbeat required for RUNNING_VERIFIED"
  if [[ $run_mode == launch ]]; then
    date -Is > "$LOG_DIR/mdrun_start_time.txt"
  else
    date -Is > "$LOG_DIR/mdrun_resume_time.txt"
  fi
  printf '%s\t%s\n' "$run_mode" "$(date -Is)" >> "$LOG_DIR/mdrun_attempts.tsv"
  if [[ $run_mode == launch ]]; then
    : > "$LOG_DIR/nvidia_smi_mdrun_sampler.csv"
  fi
  (
    while true; do
      nvidia-smi \
        --query-gpu=timestamp,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu \
        --format=csv,noheader,nounits
      sleep 60
    done
  ) >> "$LOG_DIR/nvidia_smi_mdrun_sampler.csv" &
  sampler_pid=$!
  trap cleanup_runner_processes EXIT
  trap 'termination_signal=TERM; [[ -z ${mdrun_pid:-} ]] || kill -TERM "$mdrun_pid" 2>/dev/null || true' TERM
  trap 'termination_signal=INT; [[ -z ${mdrun_pid:-} ]] || kill -INT "$mdrun_pid" 2>/dev/null || true' INT

  set +e
  if [[ $run_mode == resume ]]; then
    OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
      -v \
      -s "$PROD_DIR/${PREFIX}.tpr" \
      -deffnm "$PROD_DIR/$PREFIX" \
      -cpi "$PROD_DIR/${PREFIX}.cpt" \
      -append \
      -ntomp "$NTHREADS" \
      -pin on \
      -nb gpu \
      -pme gpu \
      -bonded gpu \
      -cpt 30 \
      >> "$LOG_DIR/mdrun_${PREFIX}.log" 2>&1 &
  else
    OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
      -v \
      -deffnm "$PROD_DIR/$PREFIX" \
      -ntomp "$NTHREADS" \
      -pin on \
      -nb gpu \
      -pme gpu \
      -bonded gpu \
      -cpt 30 \
      > "$LOG_DIR/mdrun_${PREFIX}.log" 2>&1 &
  fi
  mdrun_pid=$!
  write_mdrun_process running "$mdrun_pid"
  heartbeat_loop "$mdrun_pid" >> "$LOG_DIR/heartbeat_loop.log" 2>&1 &
  heartbeat_pid=$!
  wait "$mdrun_pid"
  mdrun_status=$?
  if [[ -n $termination_signal ]] && kill -0 "$mdrun_pid" 2>/dev/null; then
    wait "$mdrun_pid"
    mdrun_status=$?
  fi
  set -e

  kill "$heartbeat_pid" "$sampler_pid" 2>/dev/null || true
  wait "$heartbeat_pid" "$sampler_pid" 2>/dev/null || true
  heartbeat_pid=
  sampler_pid=
  write_mdrun_process exited "$mdrun_pid" "$mdrun_status"
  trap - EXIT TERM INT
  date -Is > "$LOG_DIR/mdrun_end_time.txt"
  nvidia-smi > "$LOG_DIR/nvidia_smi_after.log"

  if [[ $mdrun_status -ne 0 ]]; then
    record_state mdrun_failed TERMINAL_ABNORMAL mdrun_exit \
      terminal_gate \
      "exit_code=$mdrun_status"
    exit "$mdrun_status"
  fi

  stage=final_sanity
  trap 'rc=$?; record_state validation_failed UNRESOLVED "$stage" no_action_authority "$stage failed; exit_code=$rc"; exit "$rc"' ERR
  final_sanity
  stage=archive_and_promote
  archive_and_promote
  trap - ERR
}

local_launch() {
  local run_mode=${1:-launch}
  local remote_flag=--remote-run
  [[ $run_mode != resume ]] || remote_flag=--remote-resume
  rsync -a "$0" "$REMOTE:$RUN_ROOT/e2_run_gpr2_r59c_ascr18_production.sh"
  ssh "$REMOTE" "mkdir -p '$RUN_ROOT/logs/production'"
  if ssh "$REMOTE" "tmux has-session -t '$SESSION' 2>/dev/null"; then
    echo "ERROR: tmux session already exists: $SESSION" >&2
    exit 66
  fi
  ssh "$REMOTE" \
    "tmux new-session -d -s '$SESSION' 'RUN_ROOT=$RUN_ROOT GMX_CMD=$GMX_CMD NTHREADS=$NTHREADS MAXWARN=$MAXWARN NSTEPS=$NSTEPS PREFIX=$PREFIX bash $RUN_ROOT/e2_run_gpr2_r59c_ascr18_production.sh $remote_flag >> $RUN_ROOT/logs/production/launcher.log 2>&1'"
  printf 'launched_session\t%s\nrun_root\t%s\n' "$SESSION" "$RUN_ROOT"
}

local_finalize_completed() {
  local remote_script="$RUN_ROOT/e2_run_gpr2_r59c_ascr18_production.sh"
  local command_file="$RUN_ROOT/logs/production/finalizer_command.txt"
  local stdout_file="$RUN_ROOT/logs/production/finalizer_stdout.log"
  local stderr_file="$RUN_ROOT/logs/production/finalizer_stderr.log"
  local exit_file="$RUN_ROOT/logs/production/finalizer_exit_code.tsv"
  local remote_command
  remote_command="RUN_ROOT=$RUN_ROOT GMX_CMD=$GMX_CMD PREFIX=$PREFIX bash $remote_script --remote-finalize-completed"
  rsync -a "$0" "$REMOTE:$remote_script"
  ssh "$REMOTE" "mkdir -p '$RUN_ROOT/logs/production'"
  ssh "$REMOTE" "set +e; printf '%s\\n' '$remote_command' > '$command_file'; $remote_command > '$stdout_file' 2> '$stderr_file'; rc=\$?; printf 'exit_code\\t%s\\nfinished\\t%s\\n' \"\$rc\" \"\$(date -Is)\" > '$exit_file'; exit \"\$rc\""
}

local_heartbeat() {
  ssh "$REMOTE" \
    "RUN_ROOT=$RUN_ROOT GMX_CMD=$GMX_CMD PREFIX=$PREFIX bash '$RUN_ROOT/e2_run_gpr2_r59c_ascr18_production.sh' --remote-heartbeat"
}

local_migrate_completed_terminal_event() {
  local remote_script="$RUN_ROOT/e2_run_gpr2_r59c_ascr18_production.sh"
  rsync -a "$0" "$REMOTE:$remote_script"
  ssh "$REMOTE" "mkdir -p '$RUN_ROOT/logs/production'"
  ssh "$REMOTE" \
    "RUN_ROOT=$RUN_ROOT GMX_CMD=$GMX_CMD PREFIX=$PREFIX bash '$remote_script' --remote-migrate-completed-terminal-event"
}

case ${1:-} in
  --remote-run) remote_run launch ;;
  --remote-resume) remote_run resume ;;
  --remote-finalize-completed) finalize_completed ;;
  --remote-heartbeat) record_heartbeat ;;
  --remote-migrate-completed-terminal-event) migrate_completed_terminal_event ;;
  --finalize-completed) local_finalize_completed ;;
  --heartbeat) local_heartbeat ;;
  --migrate-completed-terminal-event) local_migrate_completed_terminal_event ;;
  --resume) local_launch resume ;;
  "") local_launch launch ;;
  *) echo "ERROR: unsupported argument $1" >&2; exit 64 ;;
esac
