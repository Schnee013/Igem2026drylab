#!/usr/bin/env bash
set -Eeuo pipefail

# Remote-only, site-parameterized GPR preproduction and 100 ps benchmark driver.
# It never starts a production mdrun. A fresh ATTEMPT_ID preserves prior
# evidence; --resume is limited to an incomplete benchmark with a valid CPT.

: "${RUN_ROOT:?set RUN_ROOT to the remote run root}"
: "${GMX_CMD:?set GMX_CMD to the accepted gmx_mpi executable}"
: "${INPUT_MANIFEST:?set INPUT_MANIFEST to the frozen combined input manifest}"
: "${ATTEMPT_ID:?set ATTEMPT_ID to a new audit-safe attempt id}"
: "${HOURLY_PRICE_CNY:?set HOURLY_PRICE_CNY to the live instance price}"

NTHREADS=${NTHREADS:-24}
BENCHMARK_FIRST_ATTEMPT_MAXH=${BENCHMARK_FIRST_ATTEMPT_MAXH:-0.001}
MODE=${1:---launch}

if [[ ! "$ATTEMPT_ID" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "ERROR: unsafe ATTEMPT_ID: $ATTEMPT_ID" >&2
  exit 64
fi
if [[ "$MODE" != "--launch" && "$MODE" != "--resume" ]]; then
  echo "ERROR: expected --launch or --resume" >&2
  exit 64
fi

INPUT_DIR="$RUN_ROOT/input/gromacs"
CONTRACT_DIR="$RUN_ROOT/input/contracts"
SCRIPT_DIR="$RUN_ROOT/input/scripts"
RUN_CONTRACT=${RUN_CONTRACT:-"$CONTRACT_DIR/autodl_preproduction_contract.json"}
VALIDATOR="$SCRIPT_DIR/validate_md_run_contract.py"
WORK_DIR="$RUN_ROOT/preproduction/attempts/$ATTEMPT_ID/gromacs"
BENCH_DIR="$RUN_ROOT/benchmark_100ps/attempts/$ATTEMPT_ID"
LOG_DIR="$RUN_ROOT/logs/preproduction/$ATTEMPT_ID"
STATUS="$LOG_DIR/terminal_status.tsv"
ACCEPTED_POINTER="$RUN_ROOT/preproduction/accepted_attempt.tsv"
PREFIX=
sampler_pid=
stage=initialization

json_scalar() {
  local dotted_key=$1
  python3 - "$RUN_CONTRACT" "$dotted_key" <<'PY'
import json
from pathlib import Path
import sys

value = json.loads(Path(sys.argv[1]).read_text())
for part in sys.argv[2].split("."):
    value = value[part]
if isinstance(value, bool):
    print("true" if value else "false")
elif value is None or isinstance(value, (dict, list)):
    raise SystemExit(f"expected scalar at {sys.argv[2]}")
else:
    print(value)
PY
}

SYSTEM_ID=$(json_scalar system_id)
SYSTEM_SLUG=$(json_scalar system_slug)
EXPECTED_ATOMS=$(json_scalar expected_atoms)
EXPECTED_GMX_VERSION=$(json_scalar expected_gromacs_version)
EXPECTED_GMX_COMMAND=$(json_scalar expected_gromacs_command)
REPAIR_MDP_NAME=$(json_scalar geometry_repair_mdp)
REPAIR_CONTRACT_NAME=$(json_scalar geometry_repair_contract)
POST_EM_CONTRACT_NAME=$(json_scalar geometry_post_em_contract)
STANDARD_EM_MDP=$(json_scalar standard_em_mdp)
EM_MAX_FORCE=$(json_scalar standard_em_maximum_force_kj_mol_nm)
STEP6_WARNING_COUNT=$(json_scalar step6_warning_contract.warning_count)
BENCHMARK_NSTEPS=$(json_scalar benchmark.nsteps)
BENCHMARK_PS=$(json_scalar benchmark.nominal_ps)
BENCHMARK_TEMP=$(json_scalar benchmark.gen_temp_k)
BENCHMARK_SEED=$(json_scalar benchmark.gen_seed)
BENCHMARK_WARNING_COUNT=$(json_scalar benchmark.warning_count)
BENCHMARK_CPT_MINUTES=$(json_scalar benchmark.checkpoint_minutes)
PREFIX="${SYSTEM_SLUG}_rep1_100ps"

[[ "$BENCHMARK_WARNING_COUNT" == "$STEP6_WARNING_COUNT" ]]

stop_sampler() {
  if [[ -n "${sampler_pid:-}" ]]; then
    kill "$sampler_pid" 2>/dev/null || true
    wait "$sampler_pid" 2>/dev/null || true
    sampler_pid=
  fi
}

write_status() {
  local status_value=$1
  local detail=${2:-}
  mkdir -p "$LOG_DIR"
  {
    printf 'key\tvalue\n'
    printf 'status\t%s\n' "$status_value"
    printf 'stage\t%s\n' "$stage"
    printf 'attempt_id\t%s\n' "$ATTEMPT_ID"
    printf 'mode\t%s\n' "$MODE"
    printf 'timestamp\t%s\n' "$(date -Is)"
    [[ -z "$detail" ]] || printf 'detail\t%s\n' "$detail"
  } > "$STATUS"
}

on_error() {
  local rc=$?
  trap - ERR
  set +e
  stop_sampler
  write_status failed "exit_code=$rc"
  exit "$rc"
}
trap on_error ERR
trap stop_sampler EXIT

start_sampler() {
  local output=$1
  printf 'timestamp,gpu_name,gpu_uuid,utilization_gpu_percent,memory_used_mib,memory_total_mib,power_draw_w,temperature_c\n' \
    > "$output"
  (
    while true; do
      nvidia-smi \
        --query-gpu=timestamp,name,uuid,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu \
        --format=csv,noheader,nounits
      sleep 5
    done
  ) >> "$output" 2>&1 &
  sampler_pid=$!
}

gpu_idle_gate() {
  local sample active_apps util mem streak=0
  printf 'sample\ttimestamp\tapps\tutilization_gpu_percent\tmemory_used_mib\n' \
    > "$LOG_DIR/gpu_gate_samples.tsv"
  for sample in 1 2 3 4 5 6 7 8; do
    active_apps=$(nvidia-smi \
      --query-compute-apps=pid,process_name,used_memory \
      --format=csv,noheader,nounits 2>/dev/null || true)
    IFS=, read -r util mem < <(
      nvidia-smi \
        --query-gpu=utilization.gpu,memory.used \
        --format=csv,noheader,nounits
    )
    util=${util//[[:space:]]/}
    mem=${mem//[[:space:]]/}
    printf '%s\t%s\t%s\t%s\t%s\n' \
      "$sample" "$(date -Is)" "${active_apps:-none}" "$util" "$mem" \
      >> "$LOG_DIR/gpu_gate_samples.tsv"
    if [[ -z "$active_apps" && "$util" =~ ^[0-9]+$ && "$util" -le 5 ]]; then
      streak=$((streak + 1))
    else
      streak=0
    fi
    [[ "$streak" -lt 5 ]] || return 0
    sleep 1
  done
  return 1
}

warning_gate_zero() {
  local log_path=$1
  python3 - "$log_path" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(errors="replace")
if re.search(r"Fatal error", text, re.IGNORECASE):
    raise SystemExit(f"fatal grompp error in {path}")
warnings = [line for line in text.splitlines() if line.startswith("WARNING ")]
if warnings:
    raise SystemExit(f"expected zero warnings in {path}, found {len(warnings)}")
PY
}

warning_gate_step6() {
  local log_path=$1
  python3 - "$log_path" "$RUN_CONTRACT" <<'PY'
from pathlib import Path
import json
import re
import sys

log_path = Path(sys.argv[1])
contract = json.loads(Path(sys.argv[2]).read_text())
expected = contract["step6_warning_contract"]
text = log_path.read_text(errors="replace")
if re.search(r"Fatal error", text, re.IGNORECASE):
    raise SystemExit(f"fatal grompp error in {log_path}")
lines = text.splitlines()
header = re.compile(r"^WARNING \d+ \[file (.+), line (\d+)\]:$")
observed = []
for index, line in enumerate(lines):
    match = header.match(line)
    if not match:
        continue
    body = " ".join(value.strip() for value in lines[index + 1:index + 7])
    observed.append(
        (
            Path(match.group(1)).name,
            int(match.group(2)),
            expected["required_text"] in body,
        )
    )
wanted = [
    (expected["source_basename"], int(line), True)
    for line in expected["source_lines"]
]
if len(observed) != int(expected["warning_count"]) or observed != wanted:
    raise SystemExit(
        f"step6 warning contract mismatch in {log_path}: "
        f"observed={observed}, expected={wanted}"
    )
PY
}

issue_gate() {
  local output=$1
  shift
  grep -Ein \
    'Fatal error|LINCS WARNING|(^|[^[:alpha:]])NaN([^[:alpha:]]|$)|non-finite|Out of memory|cudaError|Invalid PTX|invalid ptx|segmentation fault|Killed' \
    "$@" > "$output" || true
  [[ ! -s "$output" ]]
}

require_atom_count() {
  local coordinate=$1
  local observed
  observed=$(sed -n '2p' "$coordinate" | tr -d ' ')
  [[ "$observed" == "$EXPECTED_ATOMS" ]]
}

compact_checkpoint_dump() {
  local checkpoint=$1
  local output=$2
  local temporary_dump="$LOG_DIR/.checkpoint_dump_${RANDOM}_$$.tmp"
  "$GMX_CMD" dump -cp "$checkpoint" > "$temporary_dump" 2>&1
  grep -E '^(checkpoint file version|generating host|#atoms|simulation part #|step|t) = ' \
    "$temporary_dump" > "$output"
  rm -f "$temporary_dump"
}

build_benchmark_mdp() {
  python3 - "$WORK_DIR/step7_production.mdp" "$BENCH_DIR/$PREFIX.mdp" \
    "$BENCHMARK_NSTEPS" "$BENCHMARK_TEMP" "$BENCHMARK_SEED" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
values = {
    "nsteps": sys.argv[3],
    "continuation": "no",
    "gen-vel": "yes",
    "gen-temp": sys.argv[4],
    "gen-seed": sys.argv[5],
}
seen = set()
output = []
for raw in source.read_text().splitlines():
    stripped = raw.strip()
    key = (
        stripped.split("=", 1)[0].strip().replace("_", "-")
        if "=" in stripped
        else ""
    )
    if key in values:
        output.append(f"{key:<24s}= {values[key]}")
        seen.add(key)
    else:
        output.append(raw)
for key, value in values.items():
    if key not in seen:
        output.append(f"{key:<24s}= {value}")
target.write_text("\n".join(output) + "\n")
PY
}

resume_benchmark() {
  stage=benchmark_resume_gate
  for required in \
    "$WORK_DIR/step6.6.gro" \
    "$LOG_DIR/step6.6_normal_completion.txt" \
    "$LOG_DIR/equilibration_steps.tsv" \
    "$LOG_DIR/geometry_repair/geometry_summary.tsv" \
    "$LOG_DIR/geometry_post_em/geometry_summary.tsv" \
    "$LOG_DIR/em_force_gate.tsv" \
    "$BENCH_DIR/$PREFIX.tpr" \
    "$BENCH_DIR/$PREFIX.cpt" \
    "$LOG_DIR/benchmark_checkpoint_before_resume.txt" \
    "$LOG_DIR/mdrun_attempts.tsv"; do
    [[ -s "$required" ]]
  done
  require_atom_count "$WORK_DIR/step6.6.gro"
  grep -F $'status\tPASS' \
    "$LOG_DIR/geometry_repair/geometry_summary.tsv" \
    > "$LOG_DIR/benchmark_resume_geometry_repair_gate.txt"
  grep -F $'status\tPASS' \
    "$LOG_DIR/geometry_post_em/geometry_summary.tsv" \
    > "$LOG_DIR/benchmark_resume_geometry_post_em_gate.txt"
  grep -F $'status\tPASS' "$LOG_DIR/em_force_gate.tsv" \
    > "$LOG_DIR/benchmark_resume_em_force_gate.txt"
  grep -F $'step6.6\t' "$LOG_DIR/equilibration_steps.tsv" \
    > "$LOG_DIR/benchmark_resume_step6.6_gate.txt"
  for issue_log in "$LOG_DIR"/em_issue_scan.log "$LOG_DIR"/step6.*_issue_scan.log; do
    [[ -f "$issue_log" && ! -s "$issue_log" ]]
  done
  "$GMX_CMD" --version > "$LOG_DIR/gmx_version_resume.log" 2>&1
  [[ "$(basename "$GMX_CMD")" == "$EXPECTED_GMX_COMMAND" ]]
  grep -F "GROMACS version:     $EXPECTED_GMX_VERSION" \
    "$LOG_DIR/gmx_version_resume.log" \
    > "$LOG_DIR/gmx_version_resume_gate.txt"
  (
    cd "$RUN_ROOT"
    sha256sum -c "$INPUT_MANIFEST"
  ) > "$LOG_DIR/input_manifest_resume_check.log"
  local checkpoint_step
  checkpoint_step=$(awk -F' = ' '$1 == "step" {print $2}' \
    "$LOG_DIR/benchmark_checkpoint_before_resume.txt")
  [[ "$checkpoint_step" =~ ^[0-9]+$ ]]
  [[ "$checkpoint_step" -gt 0 && "$checkpoint_step" -lt "$BENCHMARK_NSTEPS" ]]
  if pgrep -x gmx_mpi > "$LOG_DIR/benchmark_resume_active_process.txt"; then
    echo "ERROR: active gmx_mpi blocks benchmark resume" >&2
    return 75
  fi
  if ! gpu_idle_gate; then
    echo "ERROR: GPU is not idle before benchmark resume" >&2
    return 75
  fi

  start_sampler "$LOG_DIR/nvidia_smi_benchmark_resume.csv"
  stage=mdrun_benchmark_resume
  local start end rc
  start=$(date -Is)
  set +e
  OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
    -deffnm "$BENCH_DIR/$PREFIX" \
    -cpi "$BENCH_DIR/$PREFIX.cpt" \
    -append \
    -ntomp "$NTHREADS" \
    -pin on \
    -nb gpu \
    -pme gpu \
    -bonded gpu \
    -cpt "$BENCHMARK_CPT_MINUTES" \
    > "$LOG_DIR/mdrun_benchmark_attempt2_resume.log" 2>&1
  rc=$?
  set -e
  end=$(date -Is)
  printf '2\tresume_append\t%s\t%s\t%s\n' "$start" "$end" "$rc" \
    >> "$LOG_DIR/mdrun_attempts.tsv"
  stop_sampler
  [[ "$rc" -eq 0 ]]
  compact_checkpoint_dump \
    "$BENCH_DIR/$PREFIX.cpt" \
    "$LOG_DIR/benchmark_checkpoint_after_resume.txt"
  local final_checkpoint_step
  final_checkpoint_step=$(awk -F' = ' '$1 == "step" {print $2}' \
    "$LOG_DIR/benchmark_checkpoint_after_resume.txt")
  [[ "$final_checkpoint_step" == "$BENCHMARK_NSTEPS" ]]
}

if [[ "$MODE" == "--launch" ]]; then
  if [[ -e "$WORK_DIR" || -e "$BENCH_DIR" || -e "$LOG_DIR" ]]; then
    echo "ERROR: refusing to overwrite attempt $ATTEMPT_ID" >&2
    exit 66
  fi
  mkdir -p "$WORK_DIR" "$BENCH_DIR" "$LOG_DIR"
else
  [[ -d "$WORK_DIR" && -d "$BENCH_DIR" && -d "$LOG_DIR" ]]
fi

stage=static_input_gate
for required in \
  "$RUN_CONTRACT" \
  "$VALIDATOR" \
  "$INPUT_MANIFEST" \
  "$INPUT_DIR/step5_complex_ion.gro" \
  "$INPUT_DIR/topol.top" \
  "$INPUT_DIR/index_final.ndx" \
  "$INPUT_DIR/$REPAIR_MDP_NAME" \
  "$INPUT_DIR/$STANDARD_EM_MDP" \
  "$INPUT_DIR/step7_production.mdp" \
  "$CONTRACT_DIR/$REPAIR_CONTRACT_NAME" \
  "$CONTRACT_DIR/$POST_EM_CONTRACT_NAME"; do
  [[ -s "$required" ]] || {
    echo "ERROR: required input missing: $required" >&2
    exit 66
  }
done
if [[ -e "$ACCEPTED_POINTER" ]]; then
  echo "ERROR: an accepted preproduction attempt already exists" >&2
  exit 66
fi

write_status running
if [[ "$MODE" == "--resume" ]]; then
  resume_benchmark
else
  stage=provenance_snapshot
  date -Is > "$LOG_DIR/run_start_time.txt"
  hostname > "$LOG_DIR/hostname.txt"
  id > "$LOG_DIR/id.txt"
  pwd > "$LOG_DIR/launch_pwd.txt"
  nvidia-smi > "$LOG_DIR/nvidia_smi_before.log"
  nvidia-smi -L >> "$LOG_DIR/nvidia_smi_before.log"
  "$GMX_CMD" --version > "$LOG_DIR/gmx_version.log" 2>&1
  [[ "$(basename "$GMX_CMD")" == "$EXPECTED_GMX_COMMAND" ]]
  grep -F "GROMACS version:     $EXPECTED_GMX_VERSION" \
    "$LOG_DIR/gmx_version.log" > "$LOG_DIR/gmx_version_gate.txt"
  (
    cd "$RUN_ROOT"
    sha256sum -c "$INPUT_MANIFEST"
  ) > "$LOG_DIR/input_manifest_check.log"
  if pgrep -x gmx_mpi > "$LOG_DIR/active_gmx_mpi_before_launch.txt"; then
    echo "ERROR: active gmx_mpi blocks preproduction" >&2
    exit 75
  fi
  if ! gpu_idle_gate; then
    echo "ERROR: GPU is not idle before preproduction" >&2
    exit 75
  fi

  stage=copy_frozen_input
  rmdir "$WORK_DIR"
  cp -a "$INPUT_DIR" "$WORK_DIR"
  require_atom_count "$WORK_DIR/step5_complex_ion.gro"
  cd "$WORK_DIR"

  stage=initial_geometry_characterization
  if python3 "$VALIDATOR" geometry \
      --contract "$CONTRACT_DIR/$REPAIR_CONTRACT_NAME" \
      --coordinate-override "$WORK_DIR/step5_complex_ion.gro" \
      --output-dir "$LOG_DIR/geometry_initial" \
      > "$LOG_DIR/geometry_initial_validator.log" 2>&1; then
    initial_geometry_rc=0
  else
    initial_geometry_rc=$?
  fi
  [[ "$initial_geometry_rc" -ne 0 ]]
  grep -F $'status\tBLOCKED' "$LOG_DIR/geometry_initial/geometry_summary.tsv"

  stage=grompp_geometry_repair
  "$GMX_CMD" grompp \
    -f "$REPAIR_MDP_NAME" \
    -c step5_complex_ion.gro \
    -r step5_complex_ion.gro \
    -p topol.top \
    -n index_final.ndx \
    -o geometry_repair.tpr \
    -po geometry_repair_out.mdp \
    -maxwarn "$STEP6_WARNING_COUNT" \
    > "$LOG_DIR/grompp_geometry_repair.log" 2>&1
  warning_gate_step6 "$LOG_DIR/grompp_geometry_repair.log"

  stage=mdrun_geometry_repair
  OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
    -deffnm geometry_repair \
    -ntomp "$NTHREADS" \
    -pin on \
    -nb cpu \
    -pme cpu \
    -bonded cpu \
    > "$LOG_DIR/mdrun_geometry_repair.log" 2>&1
  require_atom_count geometry_repair.gro
  issue_gate "$LOG_DIR/geometry_repair_issue_scan.log" \
    "$LOG_DIR/mdrun_geometry_repair.log" geometry_repair.log

  stage=geometry_repair_gate
  python3 "$VALIDATOR" geometry \
    --contract "$CONTRACT_DIR/$REPAIR_CONTRACT_NAME" \
    --coordinate-override "$WORK_DIR/geometry_repair.gro" \
    --output-dir "$LOG_DIR/geometry_repair" \
    > "$LOG_DIR/geometry_repair_validator.log" 2>&1

  stage=grompp_standard_em
  "$GMX_CMD" grompp \
    -f "$STANDARD_EM_MDP" \
    -c geometry_repair.gro \
    -r step5_complex_ion.gro \
    -p topol.top \
    -n index_final.ndx \
    -o em.tpr \
    -po em_out.mdp \
    -maxwarn "$STEP6_WARNING_COUNT" \
    > "$LOG_DIR/grompp_em.log" 2>&1
  warning_gate_step6 "$LOG_DIR/grompp_em.log"

  stage=mdrun_standard_em
  OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
    -deffnm em \
    -ntomp "$NTHREADS" \
    -pin on \
    -nb cpu \
    -pme cpu \
    -bonded cpu \
    > "$LOG_DIR/mdrun_em.log" 2>&1
  require_atom_count em.gro
  grep -F 'converged to Fmax <' em.log > "$LOG_DIR/em_convergence_marker.txt"
  maximum_force=$(awk '/Maximum force/{value=$4} END {print value}' em.log)
  [[ "$maximum_force" =~ ^[0-9.eE+-]+$ ]]
  awk -v observed="$maximum_force" -v maximum="$EM_MAX_FORCE" \
    'BEGIN {exit !(observed < maximum)}'
  printf 'key\tvalue\nmaximum_force_kj_mol_nm\t%s\nrequired_below\t%s\nstatus\tPASS\n' \
    "$maximum_force" "$EM_MAX_FORCE" > "$LOG_DIR/em_force_gate.tsv"
  issue_gate "$LOG_DIR/em_issue_scan.log" \
    "$LOG_DIR/mdrun_em.log" em.log

  stage=post_em_geometry_gate
  python3 "$VALIDATOR" geometry \
    --contract "$CONTRACT_DIR/$POST_EM_CONTRACT_NAME" \
    --coordinate-override "$WORK_DIR/em.gro" \
    --output-dir "$LOG_DIR/geometry_post_em" \
    > "$LOG_DIR/geometry_post_em_validator.log" 2>&1

  stage=equilibration
  start_sampler "$LOG_DIR/nvidia_smi_equilibration.csv"
  prev_gro=em.gro
  ref_gro=em.gro
  printf 'step\tcompleted\tcoordinate_sha256\n' \
    > "$LOG_DIR/equilibration_steps.tsv"
  for step_number in 1 2 3 4 5 6; do
    stage="grompp_step6.${step_number}"
    "$GMX_CMD" grompp \
      -f "step6.${step_number}_equilibration.mdp" \
      -c "$prev_gro" \
      -r "$ref_gro" \
      -p topol.top \
      -n index_final.ndx \
      -o "step6.${step_number}.tpr" \
      -po "step6.${step_number}_out.mdp" \
      -maxwarn "$STEP6_WARNING_COUNT" \
      > "$LOG_DIR/grompp_step6.${step_number}.log" 2>&1
    warning_gate_step6 "$LOG_DIR/grompp_step6.${step_number}.log"

    stage="mdrun_step6.${step_number}"
    OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
      -deffnm "step6.${step_number}" \
      -ntomp "$NTHREADS" \
      -pin on \
      -nb gpu \
      -pme gpu \
      -bonded gpu \
      -cpt 1 \
      > "$LOG_DIR/mdrun_step6.${step_number}.log" 2>&1
    grep -F 'Finished mdrun' "step6.${step_number}.log" \
      > "$LOG_DIR/step6.${step_number}_normal_completion.txt"
    require_atom_count "step6.${step_number}.gro"
    issue_gate "$LOG_DIR/step6.${step_number}_issue_scan.log" \
      "$LOG_DIR/mdrun_step6.${step_number}.log" "step6.${step_number}.log"
    prev_gro="step6.${step_number}.gro"
    printf 'step6.%s\t%s\t%s\n' \
      "$step_number" "$(date -Is)" "$(sha256sum "$prev_gro" | awk '{print $1}')" \
      >> "$LOG_DIR/equilibration_steps.tsv"
  done
  stop_sampler

  stage=build_benchmark
  build_benchmark_mdp
  "$GMX_CMD" grompp \
    -f "$BENCH_DIR/$PREFIX.mdp" \
    -c step6.6.gro \
    -p topol.top \
    -n index_final.ndx \
    -o "$BENCH_DIR/$PREFIX.tpr" \
    -po "$BENCH_DIR/${PREFIX}_out.mdp" \
    -maxwarn "$BENCHMARK_WARNING_COUNT" \
    > "$LOG_DIR/grompp_benchmark_100ps.log" 2>&1
  warning_gate_step6 "$LOG_DIR/grompp_benchmark_100ps.log"

  stage=mdrun_benchmark_checkpoint_attempt
  printf 'attempt\tmode\tstart\tend\texit_code\n' \
    > "$LOG_DIR/mdrun_attempts.tsv"
  start_sampler "$LOG_DIR/nvidia_smi_benchmark_attempt1.csv"
  benchmark_start=$(date -Is)
  set +e
  OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
    -deffnm "$BENCH_DIR/$PREFIX" \
    -ntomp "$NTHREADS" \
    -pin on \
    -nb gpu \
    -pme gpu \
    -bonded gpu \
    -cpt "$BENCHMARK_CPT_MINUTES" \
    -maxh "$BENCHMARK_FIRST_ATTEMPT_MAXH" \
    > "$LOG_DIR/mdrun_benchmark_attempt1_checkpoint.log" 2>&1
  benchmark_rc=$?
  set -e
  benchmark_end=$(date -Is)
  printf '1\tfresh_maxh_checkpoint\t%s\t%s\t%s\n' \
    "$benchmark_start" "$benchmark_end" "$benchmark_rc" \
    >> "$LOG_DIR/mdrun_attempts.tsv"
  stop_sampler
  [[ "$benchmark_rc" -eq 0 && -s "$BENCH_DIR/$PREFIX.cpt" ]]
  compact_checkpoint_dump \
    "$BENCH_DIR/$PREFIX.cpt" \
    "$LOG_DIR/benchmark_checkpoint_before_resume.txt"
  resume_benchmark
fi

stage=benchmark_completion_gate
for required_extension in tpr log edr xtc cpt gro; do
  [[ -s "$BENCH_DIR/$PREFIX.$required_extension" ]]
done
grep -F 'Finished mdrun' "$BENCH_DIR/$PREFIX.log" \
  > "$LOG_DIR/benchmark_normal_completion.txt"
grep -F 'Performance:' "$LOG_DIR/mdrun_benchmark_attempt2_resume.log" \
  > "$LOG_DIR/benchmark_performance.txt"
"$GMX_CMD" check -f "$BENCH_DIR/$PREFIX.xtc" \
  > "$LOG_DIR/gmx_check_benchmark_xtc.log" 2>&1
"$GMX_CMD" check -e "$BENCH_DIR/$PREFIX.edr" \
  > "$LOG_DIR/gmx_check_benchmark_edr.log" 2>&1
"$GMX_CMD" check -s1 "$BENCH_DIR/$PREFIX.tpr" \
  > "$LOG_DIR/gmx_check_benchmark_tpr.log" 2>&1
printf 'Potential\nTemperature\nPressure\nDensity\n0\n' |
  "$GMX_CMD" energy \
    -f "$BENCH_DIR/$PREFIX.edr" \
    -o "$LOG_DIR/benchmark_energy_sanity.xvg" \
    > "$LOG_DIR/benchmark_energy_sanity.log" 2>&1
awk '
  !/^[@#]/ {
    rows++
    for (i = 2; i <= NF; i++) {
      value = tolower($i)
      if ($i != $i || value ~ /nan|inf/) bad = 1
    }
  }
  END { if (rows < 2 || bad) exit 1 }
' "$LOG_DIR/benchmark_energy_sanity.xvg"
issue_gate "$LOG_DIR/benchmark_issue_scan.log" \
  "$LOG_DIR/mdrun_benchmark_attempt1_checkpoint.log" \
  "$LOG_DIR/mdrun_benchmark_attempt2_resume.log" \
  "$BENCH_DIR/$PREFIX.log"

stage=benchmark_summary
performance=$(awk '/^Performance:/ {value=$2} END {print value}' \
  "$LOG_DIR/mdrun_benchmark_attempt2_resume.log")
[[ "$performance" =~ ^[0-9.]+$ ]]
maximum_force=${maximum_force:-$(awk -F'\t' \
  '$1 == "maximum_force_kj_mol_nm" {print $2}' \
  "$LOG_DIR/em_force_gate.tsv")}
[[ "$maximum_force" =~ ^[0-9.eE+-]+$ ]]
gpu_name=$(nvidia-smi --query-gpu=name --format=csv,noheader | sed -n '1p')
gpu_uuid=$(nvidia-smi --query-gpu=uuid --format=csv,noheader | sed -n '1p')
hour_per_ns=$(awk -v value="$performance" 'BEGIN {printf "%.8f", 24/value}')
cost_per_ns=$(awk -v price="$HOURLY_PRICE_CNY" -v hours="$hour_per_ns" \
  'BEGIN {printf "%.8f", price*hours}')
estimated_200ns_hours=$(awk -v hours="$hour_per_ns" \
  'BEGIN {printf "%.4f", 200*hours}')
estimated_200ns_cost=$(awk -v price="$HOURLY_PRICE_CNY" \
  -v hours="$estimated_200ns_hours" 'BEGIN {printf "%.2f", price*hours}')
repair_outliers=$(awk -F'\t' '$1 == "outlier_bonds" {print $2}' \
  "$LOG_DIR/geometry_repair/geometry_summary.tsv")
post_em_outliers=$(awk -F'\t' '$1 == "outlier_bonds" {print $2}' \
  "$LOG_DIR/geometry_post_em/geometry_summary.tsv")
checkpoint_before=$(awk -F' = ' '$1 == "step" {print $2}' \
  "$LOG_DIR/benchmark_checkpoint_before_resume.txt")
{
  printf 'key\tvalue\n'
  printf 'status\tPASS\n'
  printf 'contract_id\t%s\n' "$(json_scalar contract_id)"
  printf 'system\t%s\n' "$SYSTEM_ID"
  printf 'site\tAutoDL\n'
  printf 'attempt_id\t%s\n' "$ATTEMPT_ID"
  printf 'atoms\t%s\n' "$EXPECTED_ATOMS"
  printf 'gpu_name\t%s\n' "$gpu_name"
  printf 'gpu_uuid\t%s\n' "$gpu_uuid"
  printf 'threads\t%s\n' "$NTHREADS"
  printf 'geometry_repair_outlier_bonds\t%s\n' "$repair_outliers"
  printf 'post_standard_em_outlier_bonds\t%s\n' "$post_em_outliers"
  printf 'standard_em_maximum_force_kj_mol_nm\t%s\n' "$maximum_force"
  printf 'step6_warning_count\t%s\n' "$STEP6_WARNING_COUNT"
  printf 'benchmark_grompp_warning_count_raw\t%s\n' "$BENCHMARK_WARNING_COUNT"
  printf 'benchmark_grompp_unexpected_warning_count\t0\n'
  printf 'benchmark_ps\t%s\n' "$BENCHMARK_PS"
  printf 'benchmark_checkpoint_before_resume_step\t%s\n' "$checkpoint_before"
  printf 'benchmark_checkpoint_after_resume_step\t%s\n' "$BENCHMARK_NSTEPS"
  printf 'benchmark_resume_mode\t-cpi -append\n'
  printf 'performance_ns_per_day\t%s\n' "$performance"
  printf 'hour_per_ns\t%s\n' "$hour_per_ns"
  printf 'hourly_price_cny\t%s\n' "$HOURLY_PRICE_CNY"
  printf 'cost_per_ns_cny\t%s\n' "$cost_per_ns"
  printf 'estimated_200ns_hours\t%s\n' "$estimated_200ns_hours"
  printf 'estimated_200ns_cost_cny\t%s\n' "$estimated_200ns_cost"
  printf 'finished\t%s\n' "$(date -Is)"
} > "$LOG_DIR/benchmark_summary.tsv"

stage=archive_and_accept
ATTEMPT_MANIFEST="$RUN_ROOT/manifests/preproduction_${ATTEMPT_ID}.sha256"
mkdir -p "$RUN_ROOT/manifests"
(
  cd "$RUN_ROOT"
  find \
    "preproduction/attempts/$ATTEMPT_ID" \
    "benchmark_100ps/attempts/$ATTEMPT_ID" \
    "logs/preproduction/$ATTEMPT_ID" \
    -type f \
    ! -path "logs/preproduction/$ATTEMPT_ID/terminal_status.tsv" \
    -print0 |
    LC_ALL=C sort -z |
    xargs -0 sha256sum
) > "$ATTEMPT_MANIFEST"
(
  cd "$RUN_ROOT"
  sha256sum -c "$ATTEMPT_MANIFEST"
) > "$LOG_DIR/preproduction_archive_check.log"
pointer_tmp="$RUN_ROOT/preproduction/.accepted_attempt_${ATTEMPT_ID}.tmp"
{
  printf 'key\tvalue\n'
  printf 'status\tPASS\n'
  printf 'attempt_id\t%s\n' "$ATTEMPT_ID"
  printf 'work_dir\t%s\n' "$WORK_DIR"
  printf 'benchmark_dir\t%s\n' "$BENCH_DIR"
  printf 'log_dir\t%s\n' "$LOG_DIR"
  printf 'attempt_manifest\t%s\n' "$ATTEMPT_MANIFEST"
  printf 'accepted\t%s\n' "$(date -Is)"
} > "$pointer_tmp"
[[ ! -e "$ACCEPTED_POINTER" ]]
mv "$pointer_tmp" "$ACCEPTED_POINTER"

trap - ERR
trap - EXIT
stop_sampler
stage=preproduction_benchmark_complete
write_status PASS
