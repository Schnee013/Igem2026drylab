#!/usr/bin/env bash
set -Eeuo pipefail

# Run-local production heartbeat and optional mdrun supervisor.
#
# Required environment:
#   RUN_ROOT, GMX_CMD, PREFIX
#
# Normal future launch:
#   ... run_gpr_md_production_heartbeat.sh --supervise launch -- \
#     "$GMX_CMD" mdrun ...
#
# Additive monitoring of an already-running mdrun:
#   ... run_gpr_md_production_heartbeat.sh --monitor-existing <gmx_mpi-pid>

: "${RUN_ROOT:?set RUN_ROOT to the remote run root}"
: "${GMX_CMD:?set GMX_CMD to the accepted gmx_mpi executable}"
: "${PREFIX:?set PREFIX to the production deffnm basename}"

PROD_DIR=${PROD_DIR:-"$RUN_ROOT/production/rep1"}
LOG_DIR=${LOG_DIR:-"$RUN_ROOT/logs/production/rep1"}
SESSION=${SESSION:-}
ATTEMPT_ID=${ATTEMPT_ID:-production_heartbeat_$(date -u '+%Y%m%dT%H%M%SZ')}
GATE_ID=${GATE_ID:-unknown}
PS_CMD=${PS_CMD:-ps}
REQUIRE_TMUX=${REQUIRE_TMUX:-1}
SAMPLER_ENABLED=${SAMPLER_ENABLED:-1}
SAMPLER_INTERVAL_SECONDS=${SAMPLER_INTERVAL_SECONDS:-30}
HEARTBEAT_INITIAL_DELAY_SECONDS=${HEARTBEAT_INITIAL_DELAY_SECONDS:-60}
HEARTBEAT_INTERVAL_SECONDS=${HEARTBEAT_INTERVAL_SECONDS:-1800}
HEARTBEAT_RETRY_SECONDS=${HEARTBEAT_RETRY_SECONDS:-300}
HEARTBEAT_MAX_PROGRESS_AGE_SECONDS=${HEARTBEAT_MAX_PROGRESS_AGE_SECONDS:-900}
HEARTBEAT_MAX_OUTPUT_AGE_SECONDS=${HEARTBEAT_MAX_OUTPUT_AGE_SECONDS:-900}
HEARTBEAT_MAX_CHECKPOINT_AGE_SECONDS=${HEARTBEAT_MAX_CHECKPOINT_AGE_SECONDS:-3600}
HEARTBEAT_CHECKPOINT_GRACE_SECONDS=${HEARTBEAT_CHECKPOINT_GRACE_SECONDS:-2700}
RUNNING_TERMINAL_STATUS=${RUNNING_TERMINAL_STATUS:-RUNNING_EARLY_GATE_PASS}
IDENTITY_MANIFEST=${IDENTITY_MANIFEST:-"$PROD_DIR/production_launch_package.sha256"}
SOURCE_IDENTITY_MANIFEST=${SOURCE_IDENTITY_MANIFEST:-"$PROD_DIR/production_source_inputs.sha256"}

STATE_EVENTS="$LOG_DIR/run_state_events.tsv"
STATE_LOCK="$LOG_DIR/run_state.lock"
STATUS="$LOG_DIR/terminal_status.tsv"
PROCESS_IDENTITY="$LOG_DIR/heartbeat_mdrun_process.tsv"
HEARTBEAT_STATE="$LOG_DIR/heartbeat_latest.tsv"
HEARTBEAT_RUNNER_PID="$LOG_DIR/heartbeat_runner.pid"
SAMPLER="$LOG_DIR/nvidia_smi_mdrun_sampler.csv"
PROGRESS_LOG="$PROD_DIR/$PREFIX.log"
TPR="$PROD_DIR/$PREFIX.tpr"
CPT="$PROD_DIR/$PREFIX.cpt"
EDR="$PROD_DIR/$PREFIX.edr"
XTC="$PROD_DIR/$PREFIX.xtc"

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

process_start_identity() {
  local pid=$1
  if [[ -r "/proc/$pid/stat" ]]; then
    awk '{print $22}' "/proc/$pid/stat"
  else
    "$PS_CMD" -p "$pid" -o lstart= | tr -s ' ' | sed 's/^ //;s/ $//'
  fi
}

read_key() {
  local path=$1 key=$2
  awk -F '\t' -v wanted="$key" '$1 == wanted { print $2; exit }' "$path"
}

record_state() {
  local state=$1 source=$2 allowed_use=$3 detail=$4
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
    "$observed_at" "$state" "$source" "$detail" >> "$STATE_EVENTS"

  snapshot_tmp=$(mktemp "$LOG_DIR/.terminal_status.tsv.XXXXXX")
  {
    printf 'key\tvalue\n'
    case "$state" in
      RUNNING_VERIFIED)
        printf 'terminal_status\t%s\n' "$RUNNING_TERMINAL_STATUS"
        printf 'mdrun_started\tYES\n'
        printf 'production_completed\tNO\n'
        ;;
      TERMINAL_ABNORMAL)
        printf 'terminal_status\tHOLD\n'
        printf 'mdrun_started\tYES\n'
        printf 'production_completed\tNO\n'
        ;;
      *)
        printf 'terminal_status\tUNRESOLVED\n'
        printf 'mdrun_started\tYES\n'
        printf 'production_completed\tNO\n'
        ;;
    esac
    printf 'run_state\t%s\n' "$state"
    printf 'attempt_id\t%s\n' "$ATTEMPT_ID"
    printf 'gate_id\t%s\n' "$GATE_ID"
    printf 'session\t%s\n' "${SESSION:-none}"
    printf 'stage\tperiodic_heartbeat\n'
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

record_unresolved() {
  local source=$1 detail=$2
  record_state UNRESOLVED "$source" no_action_authority "$detail"
  return 75
}

validate_command_identity() {
  local command_line=$1
  local gmx_basename
  gmx_basename=$(basename "$GMX_CMD")
  [[ " $command_line " == *" mdrun "* ]]
  [[ "$command_line" == *"$gmx_basename"* ]]
  [[ "$command_line" == *"-s $TPR"* ]]
  [[ "$command_line" == *"-deffnm $PROD_DIR/$PREFIX"* ]]
}

write_process_identity() {
  local pid=$1 command_line process_start tpr_sha process_tmp
  kill -0 "$pid" 2>/dev/null || return 1
  command_line=$("$PS_CMD" -p "$pid" -o args=) || return 1
  [[ -n "$command_line" ]] || return 1
  validate_command_identity "$command_line" || return 1
  process_start=$(process_start_identity "$pid") || return 1
  [[ -n "$process_start" ]] || return 1
  [[ -s "$TPR" ]] || return 1
  tpr_sha=$(sha256sum "$TPR" | awk '{print $1}') || return 1
  process_tmp=$(mktemp "$LOG_DIR/.heartbeat_mdrun_process.tsv.XXXXXX")
  {
    printf 'key\tvalue\n'
    printf 'state\trunning\n'
    printf 'pid\t%s\n' "$pid"
    printf 'process_start_identity\t%s\n' "$process_start"
    printf 'command\t%s\n' "${command_line//$'\t'/ }"
    printf 'tpr_sha256\t%s\n' "$tpr_sha"
    printf 'bound_at\t%s\n' "$(current_timestamp)"
    printf 'bound_at_epoch\t%s\n' "$(date +%s)"
  } > "$process_tmp"
  mv -f "$process_tmp" "$PROCESS_IDENTITY"
}

validate_bound_process() {
  local expected_pid=$1 command_line current_start recorded_pid recorded_start
  [[ -s "$PROCESS_IDENTITY" ]]
  recorded_pid=$(read_key "$PROCESS_IDENTITY" pid)
  recorded_start=$(read_key "$PROCESS_IDENTITY" process_start_identity)
  [[ "$recorded_pid" == "$expected_pid" ]]
  [[ "$recorded_pid" =~ ^[0-9]+$ ]]
  kill -0 "$recorded_pid" 2>/dev/null
  current_start=$(process_start_identity "$recorded_pid")
  [[ -n "$current_start" && "$current_start" == "$recorded_start" ]]
  command_line=$("$PS_CMD" -p "$recorded_pid" -o args=)
  [[ -n "$command_line" ]]
  validate_command_identity "$command_line"
}

check_manifest() {
  local manifest=$1 output=$2
  [[ -n "$manifest" && -s "$manifest" ]]
  (
    cd "$(dirname "$manifest")"
    sha256sum -c "$(basename "$manifest")"
  ) > "$output" 2>&1
}

write_heartbeat_state() {
  local observed_at=$1 live_step=$2 live_time_ps=$3 checkpoint_step=$4
  local checkpoint_time_ps=$5 state_tmp
  state_tmp=$(mktemp "$LOG_DIR/.heartbeat_latest.tsv.XXXXXX")
  {
    printf 'key\tvalue\n'
    printf 'observed_at\t%s\n' "$observed_at"
    printf 'live_step\t%s\n' "$live_step"
    printf 'live_time_ps\t%s\n' "$live_time_ps"
    printf 'checkpoint_step\t%s\n' "$checkpoint_step"
    printf 'checkpoint_time_ps\t%s\n' "$checkpoint_time_ps"
  } > "$state_tmp"
  mv -f "$state_tmp" "$HEARTBEAT_STATE"
}

record_heartbeat() {
  local pid=$1
  local bound_epoch checkpoint_age=not_available checkpoint_sha=not_available
  local checkpoint_step=not_available checkpoint_time_ps=not_available
  local detail edr_age issue_count live_step live_time_ps log_age
  local now_epoch previous_step progress_line process_age tpr_sha xtc_age
  local checkpoint_tmp issue_tmp observed_at

  if ! validate_bound_process "$pid"; then
    record_unresolved heartbeat_process_identity \
      "pid=$pid;active_or_command_identity=false"
    return 75
  fi
  if [[ "$REQUIRE_TMUX" == 1 && -n "$SESSION" ]] \
      && ! tmux has-session -t "$SESSION" 2>/dev/null; then
    record_unresolved heartbeat_tmux_identity \
      "pid=$pid;session=$SESSION;session_active=false"
    return 75
  fi
  if ! check_manifest "$IDENTITY_MANIFEST" \
      "$LOG_DIR/heartbeat_launch_identity_check.log"; then
    record_unresolved heartbeat_launch_identity \
      "pid=$pid;manifest=${IDENTITY_MANIFEST:-missing};identity_pass=false"
    return 75
  fi
  if [[ -n "$SOURCE_IDENTITY_MANIFEST" ]] \
      && ! check_manifest "$SOURCE_IDENTITY_MANIFEST" \
        "$LOG_DIR/heartbeat_source_identity_check.log"; then
    record_unresolved heartbeat_source_identity \
      "pid=$pid;manifest=$SOURCE_IDENTITY_MANIFEST;identity_pass=false"
    return 75
  fi

  for required in "$TPR" "$PROGRESS_LOG" "$EDR" "$XTC"; do
    if [[ ! -s "$required" ]]; then
      record_unresolved heartbeat_required_output \
        "pid=$pid;missing_or_empty=$required"
      return 75
    fi
  done

  now_epoch=$(date +%s)
  bound_epoch=$(read_key "$PROCESS_IDENTITY" bound_at_epoch)
  [[ "$bound_epoch" =~ ^[0-9]+$ ]]
  process_age=$((now_epoch - bound_epoch))
  log_age=$((now_epoch - $(file_mtime_epoch "$PROGRESS_LOG")))
  edr_age=$((now_epoch - $(file_mtime_epoch "$EDR")))
  xtc_age=$((now_epoch - $(file_mtime_epoch "$XTC")))
  if (( log_age > HEARTBEAT_MAX_PROGRESS_AGE_SECONDS )); then
    record_unresolved heartbeat_progress_freshness \
      "pid=$pid;progress_log_age_seconds=$log_age"
    return 75
  fi
  if (( edr_age > HEARTBEAT_MAX_OUTPUT_AGE_SECONDS \
      || xtc_age > HEARTBEAT_MAX_OUTPUT_AGE_SECONDS )); then
    record_unresolved heartbeat_output_freshness \
      "pid=$pid;edr_age_seconds=$edr_age;xtc_age_seconds=$xtc_age"
    return 75
  fi

  progress_line=$(awk '
    /^[[:space:]]*[0-9]+[[:space:]]+[0-9]+([.]?[0-9]*)[[:space:]]*$/ {
      line=$0
    }
    END { print line }
  ' "$PROGRESS_LOG")
  read -r live_step live_time_ps <<< "$progress_line"
  if [[ ! "$live_step" =~ ^[0-9]+$ || ! "$live_time_ps" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    record_unresolved heartbeat_progress_parse \
      "pid=$pid;latest_progress_unparseable=true"
    return 75
  fi
  if [[ -s "$HEARTBEAT_STATE" ]]; then
    previous_step=$(read_key "$HEARTBEAT_STATE" live_step)
    if [[ "$previous_step" =~ ^[0-9]+$ ]] && (( live_step <= previous_step )); then
      record_unresolved heartbeat_progress_advance \
        "pid=$pid;previous_step=$previous_step;live_step=$live_step"
      return 75
    fi
  fi

  if [[ -s "$CPT" ]]; then
    checkpoint_age=$((now_epoch - $(file_mtime_epoch "$CPT")))
    if (( checkpoint_age > HEARTBEAT_MAX_CHECKPOINT_AGE_SECONDS )); then
      record_unresolved heartbeat_checkpoint_freshness \
        "pid=$pid;checkpoint_age_seconds=$checkpoint_age"
      return 75
    fi
    checkpoint_tmp=$(mktemp "$LOG_DIR/.heartbeat_checkpoint_dump.txt.XXXXXX")
    if ! "$GMX_CMD" dump -cp "$CPT" > "$checkpoint_tmp" 2>&1; then
      rm -f "$checkpoint_tmp"
      record_unresolved heartbeat_checkpoint_parse \
        "pid=$pid;checkpoint_parse_failed=true"
      return 75
    fi
    checkpoint_step=$(awk -F= '/^step =/ {gsub(/[[:space:]]/, "", $2); print $2; exit}' \
      "$checkpoint_tmp")
    checkpoint_time_ps=$(awk -F= '/^t =/ {gsub(/[[:space:]]/, "", $2); print $2; exit}' \
      "$checkpoint_tmp")
    if [[ ! "$checkpoint_step" =~ ^[0-9]+$ \
        || ! "$checkpoint_time_ps" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
      rm -f "$checkpoint_tmp"
      record_unresolved heartbeat_checkpoint_parse \
        "pid=$pid;checkpoint_fields_unparseable=true"
      return 75
    fi
    mv -f "$checkpoint_tmp" "$LOG_DIR/heartbeat_checkpoint_dump.txt"
    checkpoint_sha=$(sha256sum "$CPT" | awk '{print $1}')
  elif (( process_age > HEARTBEAT_CHECKPOINT_GRACE_SECONDS )); then
    record_unresolved heartbeat_checkpoint_missing \
      "pid=$pid;process_age_seconds=$process_age"
    return 75
  fi

  issue_tmp=$(mktemp "$LOG_DIR/.heartbeat_issue_scan.log.XXXXXX")
  grep -Ein \
    'Fatal error|LINCS WARNING|(^|[^[:alpha:]])NaN([^[:alpha:]]|$)|out of memory|cudaError|invalid[[:space:]_-]*ptx|PTX.*(error|fail)|CUDA.*(error|fail)|segmentation fault|segfault|(^|[^[:alpha:]])Killed([^[:alpha:]]|$)' \
    "$PROGRESS_LOG" > "$issue_tmp" || true
  issue_count=$(wc -l < "$issue_tmp" | tr -d ' ')
  mv -f "$issue_tmp" "$LOG_DIR/heartbeat_issue_scan.log"
  if [[ "$issue_count" != 0 ]]; then
    record_unresolved heartbeat_issue_scan \
      "pid=$pid;issue_count=$issue_count"
    return 75
  fi

  tpr_sha=$(sha256sum "$TPR" | awk '{print $1}')
  observed_at=$(current_timestamp)
  detail="pid=$pid;prefix=$PREFIX;live_step=$live_step;live_time_ps=$live_time_ps"
  detail+=";checkpoint_step=$checkpoint_step;checkpoint_time_ps=$checkpoint_time_ps"
  detail+=";checkpoint_age_seconds=$checkpoint_age;checkpoint_sha256=$checkpoint_sha"
  detail+=";log_age_seconds=$log_age;edr_age_seconds=$edr_age;xtc_age_seconds=$xtc_age"
  detail+=";issue_count=0;tpr_sha256=$tpr_sha"
  record_state RUNNING_VERIFIED periodic_live_process_and_run_outputs \
    current_view_for_6h "$detail"
  write_heartbeat_state \
    "$observed_at" "$live_step" "$live_time_ps" \
    "$checkpoint_step" "$checkpoint_time_ps"
}

heartbeat_loop() {
  local pid=$1 delay rc
  delay=$HEARTBEAT_INITIAL_DELAY_SECONDS
  while kill -0 "$pid" 2>/dev/null; do
    if [[ "$delay" != 0 ]]; then
      sleep "$delay"
    fi
    kill -0 "$pid" 2>/dev/null || break
    set +e
    record_heartbeat "$pid"
    rc=$?
    set -e
    if [[ "$rc" -eq 0 ]]; then
      delay=$HEARTBEAT_INTERVAL_SECONDS
    else
      delay=$HEARTBEAT_RETRY_SECONDS
    fi
  done
}

sampler_loop() {
  while true; do
    nvidia-smi \
      --query-gpu=timestamp,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu \
      --format=csv,noheader,nounits
    sleep "$SAMPLER_INTERVAL_SECONDS"
  done
}

write_runner_pid() {
  local pid_tmp
  pid_tmp=$(mktemp "$LOG_DIR/.heartbeat_runner.pid.XXXXXX")
  printf '%s\n' "$$" > "$pid_tmp"
  mv -f "$pid_tmp" "$HEARTBEAT_RUNNER_PID"
}

cleanup_runner_pid() {
  if [[ -s "$HEARTBEAT_RUNNER_PID" ]] \
      && [[ "$(cat "$HEARTBEAT_RUNNER_PID")" == "$$" ]]; then
    rm -f "$HEARTBEAT_RUNNER_PID"
  fi
}

cleanup_supervised_processes() {
  local pid
  for pid in "${heartbeat_pid:-}" "${sampler_pid:-}" "${mdrun_pid:-}"; do
    [[ -z "$pid" ]] || kill "$pid" 2>/dev/null || true
  done
  for pid in "${heartbeat_pid:-}" "${sampler_pid:-}" "${mdrun_pid:-}"; do
    [[ -z "$pid" ]] || wait "$pid" 2>/dev/null || true
  done
  cleanup_runner_pid
}

monitor_existing() {
  local pid=$1
  mkdir -p "$LOG_DIR"
  if ! write_process_identity "$pid"; then
    record_unresolved heartbeat_process_identity \
      "pid=$pid;bind_failed=true"
    return 75
  fi
  write_runner_pid
  trap cleanup_runner_pid EXIT
  heartbeat_loop "$pid"
  record_unresolved monitored_mdrun_exit \
    "pid=$pid;process_inactive=true;completion_gate_required=true"
}

supervise_mdrun() {
  local mode=$1
  shift
  [[ "${1:-}" == "--" ]]
  shift
  [[ "$#" -gt 0 ]]
  local bind_attempt bound=0 heartbeat_pid= mdrun_pid= sampler_pid= rc
  local termination_signal=

  mkdir -p "$LOG_DIR"
  if pgrep -x gmx_mpi >/dev/null 2>&1; then
    record_unresolved prestart_active_process \
      "mode=$mode;active_gmx_mpi=true"
    return 75
  fi
  case "$mode" in
    launch)
      for output in "$PROGRESS_LOG" "$CPT" "$EDR" "$XTC" "$PROD_DIR/$PREFIX.gro"; do
        if [[ -e "$output" ]]; then
          record_unresolved launch_existing_output \
            "mode=launch;refuse_existing_output=$output"
          return 66
        fi
      done
      ;;
    resume)
      [[ -s "$TPR" && -s "$CPT" ]]
      if [[ -s "$PROD_DIR/$PREFIX.gro" ]] \
          || grep -q 'Finished mdrun on rank 0' "$PROGRESS_LOG" 2>/dev/null; then
        record_unresolved resume_completed_output \
          "mode=resume;refuse_completed_output=true"
        return 66
      fi
      ;;
    *)
      echo "ERROR: unsupported supervise mode: $mode" >&2
      return 64
      ;;
  esac

  record_state UNRESOLVED launch_or_resume_attempt \
    launch_confirmation_only \
    "mode=$mode;live heartbeat required for RUNNING_VERIFIED"
  trap cleanup_supervised_processes EXIT
  trap 'termination_signal=TERM; [[ -z ${mdrun_pid:-} ]] || kill -TERM "$mdrun_pid" 2>/dev/null || true' TERM
  trap 'termination_signal=INT; [[ -z ${mdrun_pid:-} ]] || kill -INT "$mdrun_pid" 2>/dev/null || true' INT
  if [[ "$SAMPLER_ENABLED" == 1 ]]; then
    if [[ ! -e "$SAMPLER" ]]; then
      printf 'timestamp,utilization_gpu_percent,memory_used_mib,memory_total_mib,power_draw_w,temperature_gpu_c\n' \
        > "$SAMPLER"
    fi
    sampler_loop >> "$SAMPLER" 2>&1 &
    sampler_pid=$!
  fi

  "$@" >> "$LOG_DIR/mdrun_${PREFIX}.stdout_stderr.log" 2>&1 &
  mdrun_pid=$!
  for ((bind_attempt = 1; bind_attempt <= 50; bind_attempt++)); do
    if write_process_identity "$mdrun_pid"; then
      bound=1
      break
    fi
    sleep 0.1
  done
  if [[ "$bound" != 1 ]]; then
    kill -TERM "$mdrun_pid" 2>/dev/null || true
    wait "$mdrun_pid" 2>/dev/null || true
    kill "$sampler_pid" 2>/dev/null || true
    wait "$sampler_pid" 2>/dev/null || true
    record_unresolved heartbeat_process_identity \
      "mode=$mode;pid=$mdrun_pid;bind_failed=true;mdrun_stopped=true"
    return 75
  fi
  write_runner_pid
  record_state UNRESOLVED mdrun_invoked \
    launch_confirmation_only \
    "mode=$mode;pid=$mdrun_pid;live heartbeat pending"
  heartbeat_loop "$mdrun_pid" >> "$LOG_DIR/heartbeat_runner.log" 2>&1 &
  heartbeat_pid=$!

  set +e
  wait "$mdrun_pid"
  rc=$?
  if [[ -n "$termination_signal" ]] && kill -0 "$mdrun_pid" 2>/dev/null; then
    wait "$mdrun_pid"
    rc=$?
  fi
  set -e
  kill "$heartbeat_pid" "$sampler_pid" 2>/dev/null || true
  wait "$heartbeat_pid" "$sampler_pid" 2>/dev/null || true
  heartbeat_pid=
  sampler_pid=
  cleanup_runner_pid
  trap - EXIT TERM INT

  if [[ "$rc" -eq 0 ]]; then
    record_state UNRESOLVED mdrun_exit \
      completion_gate_required \
      "mode=$mode;pid=$mdrun_pid;exit_code=0;awaiting_completion_gate=true"
  else
    record_state TERMINAL_ABNORMAL mdrun_exit \
      terminal_gate \
      "mode=$mode;pid=$mdrun_pid;exit_code=$rc"
  fi
  return "$rc"
}

case ${1:-} in
  --monitor-existing)
    [[ "${2:-}" =~ ^[0-9]+$ ]]
    monitor_existing "$2"
    ;;
  --once)
    [[ "${2:-}" =~ ^[0-9]+$ ]]
    mkdir -p "$LOG_DIR"
    if [[ ! -s "$PROCESS_IDENTITY" ]] \
        || [[ "$(read_key "$PROCESS_IDENTITY" pid)" != "$2" ]]; then
      if ! write_process_identity "$2"; then
        record_unresolved heartbeat_process_identity \
          "pid=$2;bind_failed=true"
        exit 75
      fi
    fi
    record_heartbeat "$2"
    ;;
  --supervise)
    [[ -n "${2:-}" ]]
    mode=$2
    shift 2
    supervise_mdrun "$mode" "$@"
    ;;
  *)
    echo "ERROR: expected --monitor-existing PID, --once PID, or --supervise MODE -- COMMAND" >&2
    exit 64
    ;;
esac
