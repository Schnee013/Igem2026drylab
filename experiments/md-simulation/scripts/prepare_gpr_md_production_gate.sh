#!/usr/bin/env bash
set -Eeuo pipefail

# Remote-only production launch-package builder. It freezes the 200 ns MDP,
# TPR, binary identity, launch/resume commands, and checksums, but deliberately
# contains no mdrun invocation.

: "${RUN_ROOT:?set RUN_ROOT to the remote run root}"
: "${GMX_CMD:?set GMX_CMD to the accepted gmx_mpi executable}"
: "${INPUT_MANIFEST:?set INPUT_MANIFEST to the frozen combined input manifest}"
: "${GATE_ID:?set GATE_ID to a new audit-safe production gate id}"

NTHREADS=${NTHREADS:-24}
SESSION=${SESSION:-gpr3_r167y_ascr3_autodl_rep1_20260717}
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HEARTBEAT_RUNNER_SOURCE=${HEARTBEAT_RUNNER_SOURCE:-"$SCRIPT_DIR/run_gpr_md_production_heartbeat.sh"}

if [[ ! "$GATE_ID" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "ERROR: unsafe GATE_ID: $GATE_ID" >&2
  exit 64
fi
if [[ ! "$SESSION" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "ERROR: unsafe SESSION: $SESSION" >&2
  exit 64
fi

CONTRACT_DIR="$RUN_ROOT/input/contracts"
RUN_CONTRACT=${RUN_CONTRACT:-"$CONTRACT_DIR/autodl_preproduction_contract.json"}
ACCEPTED_POINTER="$RUN_ROOT/preproduction/accepted_attempt.tsv"
PROD_DIR="$RUN_ROOT/production/rep1"
GATE_WORK_DIR="$RUN_ROOT/production/gates/$GATE_ID"
PROD_STAGING="$GATE_WORK_DIR/staging_rep1"
LOG_DIR="$RUN_ROOT/logs/production_gate/$GATE_ID"
STATUS="$LOG_DIR/terminal_status.tsv"
GATE_POINTER="$RUN_ROOT/production/launch_gate.tsv"
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
if value is None or isinstance(value, (dict, list)):
    raise SystemExit(f"expected scalar at {sys.argv[2]}")
print(value)
PY
}

SYSTEM_ID=$(json_scalar system_id)
SYSTEM_SLUG=$(json_scalar system_slug)
EXPECTED_ATOMS=$(json_scalar expected_atoms)
EXPECTED_GMX_VERSION=$(json_scalar expected_gromacs_version)
EXPECTED_GMX_COMMAND=$(json_scalar expected_gromacs_command)
PRODUCTION_NSTEPS=$(json_scalar production_gate.nsteps)
PRODUCTION_NS=$(json_scalar production_gate.nominal_ns)
STEP6_WARNING_COUNT=$(json_scalar step6_warning_contract.warning_count)
PRODUCTION_WARNING_COUNT=$(json_scalar production_gate.warning_count)
PREFIX="${SYSTEM_SLUG}_rep1_200ns"

[[ "$PRODUCTION_WARNING_COUNT" == "$STEP6_WARNING_COUNT" ]]

write_status() {
  local status_value=$1
  local detail=${2:-}
  mkdir -p "$LOG_DIR"
  {
    printf 'key\tvalue\n'
    printf 'status\t%s\n' "$status_value"
    printf 'stage\t%s\n' "$stage"
    printf 'gate_id\t%s\n' "$GATE_ID"
    printf 'timestamp\t%s\n' "$(date -Is)"
    [[ -z "$detail" ]] || printf 'detail\t%s\n' "$detail"
  } > "$STATUS"
}

on_error() {
  local rc=$?
  trap - ERR
  set +e
  write_status HOLD "exit_code=$rc"
  exit "$rc"
}
trap on_error ERR

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
        f"production warning contract mismatch in {log_path}: "
        f"observed={observed}, expected={wanted}"
    )
PY
}

build_production_mdp() {
  local source=$1
  local target=$2
  python3 - "$source" "$target" "$PRODUCTION_NSTEPS" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
values = {
    "nsteps": sys.argv[3],
    "continuation": "yes",
    "gen-vel": "no",
}
drop = {"gen-temp", "gen-seed"}
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
    elif key not in drop:
        output.append(raw)
for key, value in values.items():
    if key not in seen:
        output.append(f"{key:<24s}= {value}")
target.write_text("\n".join(output) + "\n")
PY
}

if [[ -e "$PROD_DIR" || -e "$GATE_WORK_DIR" || -e "$LOG_DIR" || -e "$GATE_POINTER" ]]; then
  echo "ERROR: refusing to overwrite production launch-package state" >&2
  exit 66
fi
mkdir -p "$PROD_STAGING" "$LOG_DIR"
write_status running

stage=accepted_preproduction_gate
for required in "$RUN_CONTRACT" "$INPUT_MANIFEST" "$ACCEPTED_POINTER"; do
  [[ -s "$required" ]]
done
accepted_status=$(awk -F'\t' '$1 == "status" {print $2}' "$ACCEPTED_POINTER")
accepted_attempt=$(awk -F'\t' '$1 == "attempt_id" {print $2}' "$ACCEPTED_POINTER")
PREPROD_DIR=$(awk -F'\t' '$1 == "work_dir" {print $2}' "$ACCEPTED_POINTER")
BENCH_DIR=$(awk -F'\t' '$1 == "benchmark_dir" {print $2}' "$ACCEPTED_POINTER")
PREPROD_LOG=$(awk -F'\t' '$1 == "log_dir" {print $2}' "$ACCEPTED_POINTER")
ATTEMPT_MANIFEST=$(awk -F'\t' '$1 == "attempt_manifest" {print $2}' "$ACCEPTED_POINTER")
[[ "$accepted_status" == "PASS" ]]
[[ "$PREPROD_DIR" == "$RUN_ROOT"/preproduction/attempts/*/gromacs ]]
[[ "$BENCH_DIR" == "$RUN_ROOT"/benchmark_100ps/attempts/* ]]
[[ "$PREPROD_LOG" == "$RUN_ROOT"/logs/preproduction/* ]]
[[ "$ATTEMPT_MANIFEST" == "$RUN_ROOT"/manifests/preproduction_*.sha256 ]]
grep -F $'status\tPASS' "$PREPROD_LOG/terminal_status.tsv" \
  > "$LOG_DIR/preproduction_status_gate.txt"
grep -F $'status\tPASS' "$PREPROD_LOG/benchmark_summary.tsv" \
  > "$LOG_DIR/benchmark_status_gate.txt"
(
  cd "$RUN_ROOT"
  sha256sum -c "$INPUT_MANIFEST"
) > "$LOG_DIR/input_manifest_check.log"
(
  cd "$RUN_ROOT"
  sha256sum -c "$ATTEMPT_MANIFEST"
) > "$LOG_DIR/preproduction_manifest_check.log"

stage=resource_and_environment_gate
date -Is > "$LOG_DIR/gate_start_time.txt"
hostname > "$LOG_DIR/hostname.txt"
id > "$LOG_DIR/id.txt"
pwd > "$LOG_DIR/launch_pwd.txt"
nvidia-smi > "$LOG_DIR/nvidia_smi_before.log"
nvidia-smi -L >> "$LOG_DIR/nvidia_smi_before.log"
"$GMX_CMD" --version > "$LOG_DIR/gmx_version.log" 2>&1
[[ "$(basename "$GMX_CMD")" == "$EXPECTED_GMX_COMMAND" ]]
grep -F "GROMACS version:     $EXPECTED_GMX_VERSION" \
  "$LOG_DIR/gmx_version.log" > "$LOG_DIR/gmx_version_gate.txt"
if pgrep -x gmx_mpi > "$LOG_DIR/active_gmx_mpi.txt"; then
  echo "ERROR: active gmx_mpi blocks production gate" >&2
  exit 75
fi
if ! gpu_idle_gate; then
  echo "ERROR: GPU is not idle at production gate" >&2
  exit 75
fi

stage=freeze_production_input
for required in \
  "$PREPROD_DIR/step6.6.gro" \
  "$PREPROD_DIR/topol.top" \
  "$PREPROD_DIR/index_final.ndx" \
  "$PREPROD_DIR/step7_production.mdp" \
  "$PREPROD_DIR/ASCR3.itp" \
  "$PREPROD_DIR/toppar/cgenff_ASCR3.itp"; do
  [[ -s "$required" ]]
done
observed_atoms=$(sed -n '2p' "$PREPROD_DIR/step6.6.gro" | tr -d ' ')
[[ "$observed_atoms" == "$EXPECTED_ATOMS" ]]
build_production_mdp \
  "$PREPROD_DIR/step7_production.mdp" \
  "$PROD_STAGING/$PREFIX.mdp"
(
  cd "$PREPROD_DIR"
  "$GMX_CMD" grompp \
    -f "$PROD_STAGING/$PREFIX.mdp" \
    -c step6.6.gro \
    -p topol.top \
    -n index_final.ndx \
    -o "$PROD_STAGING/$PREFIX.tpr" \
    -po "$PROD_STAGING/${PREFIX}_out.mdp" \
    -maxwarn "$PRODUCTION_WARNING_COUNT"
) > "$LOG_DIR/grompp_${PREFIX}.log" 2>&1
warning_gate_step6 "$LOG_DIR/grompp_${PREFIX}.log"
"$GMX_CMD" check -s1 "$PROD_STAGING/$PREFIX.tpr" \
  > "$LOG_DIR/gmx_check_production_tpr.log" 2>&1

stage=tpr_semantic_gate
temporary_dump="$LOG_DIR/.tpr_dump_${RANDOM}_$$.tmp"
"$GMX_CMD" dump -s "$PROD_STAGING/$PREFIX.tpr" > "$temporary_dump" 2>&1
grep -E '^[[:space:]]*(integrator|dt|nsteps|init-step|continuation|nstxout-compressed)' \
  "$temporary_dump" > "$LOG_DIR/production_tpr_semantics.txt"
rm -f "$temporary_dump"
grep -E "^[[:space:]]*nsteps[[:space:]]*=[[:space:]]*$PRODUCTION_NSTEPS$" \
  "$LOG_DIR/production_tpr_semantics.txt"

stage=freeze_commands_and_checksums
GMX_REAL=$(readlink -f "$GMX_CMD")
[[ -s "$HEARTBEAT_RUNNER_SOURCE" ]]
cp "$HEARTBEAT_RUNNER_SOURCE" \
  "$PROD_STAGING/run_gpr_md_production_heartbeat.sh"
{
  printf '#!/usr/bin/env bash\n'
  printf 'set -Eeuo pipefail\n'
  printf 'export RUN_ROOT=%q\n' "$RUN_ROOT"
  printf 'export GMX_CMD=%q\n' "$GMX_CMD"
  printf 'export PROD_DIR=%q\n' "$PROD_DIR"
  printf 'export LOG_DIR=%q\n' "$RUN_ROOT/logs/production/rep1"
  printf 'export PREFIX=%q\n' "$PREFIX"
  printf 'export SESSION=%q\n' "$SESSION"
  printf 'export GATE_ID=%q\n' "$GATE_ID"
  printf 'export ATTEMPT_ID=${ATTEMPT_ID:-production_launch_%s_$(date -u +%%Y%%m%%dT%%H%%M%%SZ)}\n' \
    "$GATE_ID"
  printf 'export IDENTITY_MANIFEST=%q\n' \
    "$PROD_DIR/production_launch_package.sha256"
  printf 'export SOURCE_IDENTITY_MANIFEST=%q\n' \
    "$PROD_DIR/production_source_inputs.sha256"
  printf 'export OMP_NUM_THREADS=%q\n' "$NTHREADS"
  printf 'exec %q --supervise launch -- \\\n' \
    "$PROD_DIR/run_gpr_md_production_heartbeat.sh"
  printf '  %q mdrun \\\n' "$GMX_CMD"
  printf '  -v \\\n'
  printf '  -s %q \\\n' "$PROD_DIR/$PREFIX.tpr"
  printf '  -deffnm %q \\\n' "$PROD_DIR/$PREFIX"
  printf '  -ntomp %q -pin on -nb gpu -pme gpu -bonded gpu -cpt 30\n' "$NTHREADS"
} > "$PROD_STAGING/launch_command.sh"
{
  printf '#!/usr/bin/env bash\n'
  printf 'set -Eeuo pipefail\n'
  printf 'export RUN_ROOT=%q\n' "$RUN_ROOT"
  printf 'export GMX_CMD=%q\n' "$GMX_CMD"
  printf 'export PROD_DIR=%q\n' "$PROD_DIR"
  printf 'export LOG_DIR=%q\n' "$RUN_ROOT/logs/production/rep1"
  printf 'export PREFIX=%q\n' "$PREFIX"
  printf 'export SESSION=%q\n' "$SESSION"
  printf 'export GATE_ID=%q\n' "$GATE_ID"
  printf 'export ATTEMPT_ID=${ATTEMPT_ID:-production_resume_%s_$(date -u +%%Y%%m%%dT%%H%%M%%SZ)}\n' \
    "$GATE_ID"
  printf 'export IDENTITY_MANIFEST=%q\n' \
    "$PROD_DIR/production_launch_package.sha256"
  printf 'export SOURCE_IDENTITY_MANIFEST=%q\n' \
    "$PROD_DIR/production_source_inputs.sha256"
  printf 'export OMP_NUM_THREADS=%q\n' "$NTHREADS"
  printf 'exec %q --supervise resume -- \\\n' \
    "$PROD_DIR/run_gpr_md_production_heartbeat.sh"
  printf '  %q mdrun \\\n' "$GMX_CMD"
  printf '  -v \\\n'
  printf '  -s %q \\\n' "$PROD_DIR/$PREFIX.tpr"
  printf '  -deffnm %q \\\n' "$PROD_DIR/$PREFIX"
  printf '  -cpi %q -append \\\n' "$PROD_DIR/$PREFIX.cpt"
  printf '  -ntomp %q -pin on -nb gpu -pme gpu -bonded gpu -cpt 30\n' "$NTHREADS"
} > "$PROD_STAGING/resume_command.sh"
chmod 0755 \
  "$PROD_STAGING/launch_command.sh" \
  "$PROD_STAGING/resume_command.sh" \
  "$PROD_STAGING/run_gpr_md_production_heartbeat.sh"
{
  printf 'key\tvalue\n'
  printf 'status\tGO\n'
  printf 'scope\tPRODUCTION_LAUNCH_GATE_ONLY_NO_MDRUN_STARTED\n'
  printf 'contract_id\t%s\n' "$(json_scalar contract_id)"
  printf 'system\t%s\n' "$SYSTEM_ID"
  printf 'site\tAutoDL\n'
  printf 'replicate\t1\n'
  printf 'accepted_preproduction_attempt\t%s\n' "$accepted_attempt"
  printf 'production_prefix\t%s\n' "$PREFIX"
  printf 'production_session\t%s\n' "$SESSION"
  printf 'production_nsteps\t%s\n' "$PRODUCTION_NSTEPS"
  printf 'nominal_ns\t%s\n' "$PRODUCTION_NS"
  printf 'atoms\t%s\n' "$EXPECTED_ATOMS"
  printf 'gmx_command\t%s\n' "$GMX_CMD"
  printf 'gmx_real_binary\t%s\n' "$GMX_REAL"
  printf 'threads\t%s\n' "$NTHREADS"
  printf 'gpu_offload\t-nb gpu -pme gpu -bonded gpu\n'
  printf 'checkpoint_minutes\t30\n'
  printf 'heartbeat_runner\t%s\n' \
    "$PROD_DIR/run_gpr_md_production_heartbeat.sh"
  printf 'heartbeat_interval_seconds\t1800\n'
  printf 'heartbeat_auto_started_by_launch_command\tYES\n'
  printf 'grompp_warning_count_raw\t%s\n' "$PRODUCTION_WARNING_COUNT"
  printf 'grompp_unexpected_warning_count\t0\n'
  printf 'mdrun_started\tNO\n'
  printf 'gate_completed\t%s\n' "$(date -Is)"
} > "$LOG_DIR/production_launch_gate_summary.tsv"
{
  cd "$PROD_STAGING"
  sha256sum \
    "$PREFIX.mdp" \
    "${PREFIX}_out.mdp" \
    "$PREFIX.tpr" \
    launch_command.sh \
    resume_command.sh \
    run_gpr_md_production_heartbeat.sh
} > "$PROD_STAGING/production_launch_package.sha256"
(
  cd "$PROD_STAGING"
  sha256sum -c production_launch_package.sha256
) > "$LOG_DIR/production_launch_package_check.log"
sha256sum \
  "$PREPROD_DIR/step6.6.gro" \
  "$PREPROD_DIR/topol.top" \
  "$PREPROD_DIR/index_final.ndx" \
  "$RUN_CONTRACT" \
  "$GMX_CMD" \
  "$GMX_REAL" \
  > "$PROD_STAGING/production_source_inputs.sha256"
sha256sum -c "$PROD_STAGING/production_source_inputs.sha256" \
  > "$LOG_DIR/production_source_inputs_check.log"

stage=atomic_promote_production_package
[[ ! -e "$PROD_DIR" ]]
mv "$PROD_STAGING" "$PROD_DIR"
[[ -s "$PROD_DIR/$PREFIX.tpr" ]]
[[ -s "$PROD_DIR/production_launch_package.sha256" ]]
[[ -s "$PROD_DIR/production_source_inputs.sha256" ]]
sha256sum -c "$PROD_DIR/production_source_inputs.sha256" \
  > "$LOG_DIR/production_source_inputs_post_promote_check.log"
(
  cd "$PROD_DIR"
  sha256sum -c production_launch_package.sha256
) \
  > "$LOG_DIR/production_launch_package_check.log"

pointer_tmp="$RUN_ROOT/production/.launch_gate_${GATE_ID}.tmp"
{
  printf 'key\tvalue\n'
  printf 'status\tGO\n'
  printf 'gate_id\t%s\n' "$GATE_ID"
  printf 'production_dir\t%s\n' "$PROD_DIR"
  printf 'production_prefix\t%s\n' "$PREFIX"
  printf 'session\t%s\n' "$SESSION"
  printf 'summary\t%s\n' "$LOG_DIR/production_launch_gate_summary.tsv"
  printf 'manifest\t%s\n' "$PROD_DIR/production_launch_package.sha256"
  printf 'mdrun_started\tNO\n'
  printf 'accepted\t%s\n' "$(date -Is)"
} > "$pointer_tmp"
[[ ! -e "$GATE_POINTER" ]]
mv "$pointer_tmp" "$GATE_POINTER"

trap - ERR
stage=production_launch_gate_complete
write_status GO "production mdrun not started"
