#!/usr/bin/env bash
set -Eeuo pipefail

REMOTE=${REMOTE:-nkuliulab-e2}
RUN_ROOT=${RUN_ROOT:-/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716}
GMX_CMD=${GMX_CMD:-/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi}
NTHREADS=${NTHREADS:-24}
MAXWARN=${MAXWARN:-11}
REMOVE_POPC=${REMOVE_POPC:-410}
BENCHMARK_NSTEPS=${BENCHMARK_NSTEPS:-50000}
BENCHMARK_SEED=${BENCHMARK_SEED:-20260716}
SESSION=${SESSION:-gpr2_r59c_preprod_20260716}

ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
SYSTEM_DIR="$ROOT/experiments/md-simulation/systems/gpr2-R59C-ascr18"
RETURN_GMX="$SYSTEM_DIR/gromacs/charmm_gui_returned/charmm-gui-8417129094/gromacs"
LIGAND_DIR="$SYSTEM_DIR/gromacs/ascr18_receptor_frame"

warning_gate() {
  local log_path=$1
  local allow_net_charge=${2:-0}
  python3 - "$log_path" "$allow_net_charge" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
allow_net_charge = bool(int(sys.argv[2]))
text = path.read_text(errors="replace")
if "Fatal error" in text:
    raise SystemExit(f"fatal grompp error in {path}")
lines = text.splitlines()
warnings = [index for index, line in enumerate(lines) if line.startswith("WARNING ")]
duplicate_count = 0
net_charge_count = 0
for index in warnings:
    header = lines[index]
    body = "\n".join(lines[index:index + 6])
    if (
        "[file cgenff_ASCR18.itp," in header
        and "Encountered a second line of parameters for dihedral type 9" in body
    ):
        duplicate_count += 1
    elif (
        allow_net_charge
        and "[file topol.top," in header
        and "You are using Ewald electrostatics in a system with net charge" in body
    ):
        net_charge_count += 1
    else:
        raise SystemExit(f"unexpected warning: {header}")
expected_net_charge = 1 if allow_net_charge else 0
if duplicate_count != 11 or net_charge_count != expected_net_charge:
    raise SystemExit(
        f"warning contract mismatch in {path}: "
        f"duplicate_type9={duplicate_count}, net_charge={net_charge_count}"
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
    if [[ $streak -ge 5 ]]; then
      return 0
    fi
    [[ $sample -lt 8 ]] || break
  done < <(
    timeout 12 nvidia-smi \
      --query-gpu=utilization.gpu,memory.used \
      --format=csv,noheader,nounits \
      -l 1 2>/dev/null
  )
  return 1
}

validate_molecules() {
  local top=$1 expected_popc=$2 expected_pot=$3 expected_tip3=$4
  python3 - "$top" "$expected_popc" "$expected_pot" "$expected_tip3" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
expected = {
    "PROA": 1,
    "ASCR18": 1,
    "POPC": int(sys.argv[2]),
    "POT": int(sys.argv[3]),
    "CLA": 100,
    "TIP3": int(sys.argv[4]),
}
rows = {}
inside = False
for raw in path.read_text().splitlines():
    line = raw.split(";", 1)[0].strip()
    if line == "[ molecules ]":
        inside = True
        continue
    if inside and line.startswith("["):
        break
    if inside and line:
        parts = line.split()
        if len(parts) == 2 and parts[1].isdigit():
            rows[parts[0]] = rows.get(parts[0], 0) + int(parts[1])
if rows != expected:
    raise SystemExit(f"molecule table mismatch: observed={rows} expected={expected}")
print("molecule_table_pass", rows)
PY
}

remote_run() {
  INPUT_DIR="$RUN_ROOT/input/gromacs"
  WORK_DIR="$RUN_ROOT/preproduction/gromacs"
  LOG_DIR="$RUN_ROOT/logs/preproduction"
  BENCH_DIR="$RUN_ROOT/benchmark_100ps"
  mkdir -p "$LOG_DIR" "$BENCH_DIR"

  if [[ -e "$WORK_DIR/step6.6.gro" || -e "$BENCH_DIR/gpr2_r59c_ascr18_100ps.xtc" ]]; then
    echo "ERROR: refusing to overwrite completed preproduction/benchmark outputs" >&2
    exit 66
  fi
  if [[ ! -d "$WORK_DIR" ]]; then
    mkdir -p "$RUN_ROOT/preproduction"
    cp -a "$INPUT_DIR" "$WORK_DIR"
  fi

  cd "$WORK_DIR"
  date -Is > "$LOG_DIR/run_start_time.txt"
  hostname > "$LOG_DIR/hostname.txt"
  whoami > "$LOG_DIR/whoami.txt"
  pwd > "$LOG_DIR/pwd.txt"
  nvidia-smi > "$LOG_DIR/nvidia_smi_before.log"
  "$GMX_CMD" --version > "$LOG_DIR/gmx_version.log" 2>&1

  if ! gpu_idle_gate; then
    printf 'status\tgpu_busy_before_preproduction\n' > "$LOG_DIR/terminal_status.tsv"
    exit 75
  fi

  stage=assembly
  trap 'rc=$?; printf "status\tfailed\nstage\t%s\nexit_code\t%s\nfailed\t%s\n" "$stage" "$rc" "$(date -Is)" > "$LOG_DIR/terminal_status.tsv"' ERR
  printf 'status\trunning\nstarted\t%s\n' "$(date -Is)" > "$LOG_DIR/terminal_status.tsv"

  python3 assemble_complex.py \
    --system Gpr2_R59C \
    --work-dir . \
    --ligand ligand.gro \
    --remove-popc "$REMOVE_POPC" \
    > "$LOG_DIR/assembly.log" 2>&1
  [[ $(sed -n '2p' step5_complex.gro | tr -d ' ') == 130640 ]]
  validate_molecules topol.top 200 87 32405 > "$LOG_DIR/molecule_gate_pre_genion.log"

  stage=grompp_genion
  "$GMX_CMD" grompp \
    -f step6.0_minimization.mdp \
    -c step5_complex.gro \
    -r step5_complex.gro \
    -p topol.top \
    -n index.ndx \
    -o genion.tpr \
    -po genion_out.mdp \
    -maxwarn "$((MAXWARN + 1))" \
    > "$LOG_DIR/grompp_genion.log" 2>&1
  warning_gate "$LOG_DIR/grompp_genion.log" 1

  stage=genion
  printf 'TIP3\n' | "$GMX_CMD" genion \
    -s genion.tpr \
    -p topol.top \
    -n index.ndx \
    -o step5_complex_ion.gro \
    -pname POT \
    -np 1 \
    -seed "$BENCHMARK_SEED" \
    > "$LOG_DIR/genion.log" 2>&1
  stage=rebuild_index
  python3 assemble_complex.py --rebuild-index step5_complex_ion.gro \
    > "$LOG_DIR/rebuild_index.log" 2>&1
  [[ $(sed -n '2p' step5_complex_ion.gro | tr -d ' ') == 130638 ]]
  validate_molecules topol.top 200 88 32404 > "$LOG_DIR/molecule_gate_post_genion.log"

  cp topol.top topol_phase3.top
  cp index.ndx index.fixed.ndx

  stage=grompp_em
  "$GMX_CMD" grompp \
    -f step6.0_minimization.mdp \
    -c step5_complex_ion.gro \
    -r step5_complex_ion.gro \
    -p topol_phase3.top \
    -n index.fixed.ndx \
    -o em.tpr \
    -po em_out.mdp \
    -maxwarn "$MAXWARN" \
    > "$LOG_DIR/grompp_em.log" 2>&1
  warning_gate "$LOG_DIR/grompp_em.log"
  stage=mdrun_em
  OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
    -deffnm em \
    -ntomp "$NTHREADS" \
    -pin on \
    -nb cpu \
    -pme cpu \
    -bonded cpu \
    > "$LOG_DIR/mdrun_em.log" 2>&1
  grep 'Maximum force' em.log | tail -n 1 > "$LOG_DIR/em_maximum_force.txt"

  (
    while true; do
      nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu \
        --format=csv,noheader,nounits
      sleep 5
    done
  ) > "$LOG_DIR/nvidia_smi_equilibration.csv" &
  sampler_pid=$!
  trap 'kill "$sampler_pid" 2>/dev/null || true' EXIT

  prev_gro=em.gro
  ref_gro=em.gro
  for step in 1 2 3 4 5 6; do
    stage="grompp_step6.${step}"
    "$GMX_CMD" grompp \
      -f "step6.${step}_equilibration.mdp" \
      -c "$prev_gro" \
      -r "$ref_gro" \
      -p topol_phase3.top \
      -n index.fixed.ndx \
      -o "step6.${step}.tpr" \
      -po "step6.${step}_out.mdp" \
      -maxwarn "$MAXWARN" \
      > "$LOG_DIR/grompp_step6.${step}.log" 2>&1
    warning_gate "$LOG_DIR/grompp_step6.${step}.log"
    stage="mdrun_step6.${step}"
    OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
      -deffnm "step6.${step}" \
      -ntomp "$NTHREADS" \
      -pin on \
      -nb gpu \
      -pme gpu \
      -bonded gpu \
      > "$LOG_DIR/mdrun_step6.${step}.log" 2>&1
    prev_gro="step6.${step}.gro"
    printf 'step6.%s\t%s\n' "$step" "$(date -Is)" >> "$LOG_DIR/equilibration_steps.tsv"
  done

  kill "$sampler_pid" 2>/dev/null || true
  wait "$sampler_pid" 2>/dev/null || true
  trap - EXIT
  [[ -s step6.6.gro && $(sed -n '2p' step6.6.gro | tr -d ' ') == 130638 ]]

  python3 - "$WORK_DIR/step7_production.mdp" "$BENCH_DIR/gpr2_r59c_ascr18_100ps.mdp" <<PY
from pathlib import Path
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
values = {
    "nsteps": "$BENCHMARK_NSTEPS",
    "continuation": "no",
    "gen-vel": "yes",
    "gen-temp": "303.15",
    "gen-seed": "$BENCHMARK_SEED",
}
seen = set()
out = []
for raw in source.read_text().splitlines():
    stripped = raw.strip()
    key = stripped.split("=", 1)[0].strip().replace("_", "-") if "=" in stripped else ""
    if key in values:
        out.append(f"{key:<24s}= {values[key]}")
        seen.add(key)
    else:
        out.append(raw)
for key, value in values.items():
    if key not in seen:
        out.append(f"{key:<24s}= {value}")
target.write_text("\n".join(out) + "\n")
PY

  stage=grompp_benchmark_100ps
  "$GMX_CMD" grompp \
    -f "$BENCH_DIR/gpr2_r59c_ascr18_100ps.mdp" \
    -c step6.6.gro \
    -p topol_phase3.top \
    -n index.fixed.ndx \
    -o "$BENCH_DIR/gpr2_r59c_ascr18_100ps.tpr" \
    -po "$BENCH_DIR/gpr2_r59c_ascr18_100ps_out.mdp" \
    -maxwarn "$MAXWARN" \
    > "$LOG_DIR/grompp_benchmark_100ps.log" 2>&1
  warning_gate "$LOG_DIR/grompp_benchmark_100ps.log"

  (
    while true; do
      nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu \
        --format=csv,noheader,nounits
      sleep 5
    done
  ) > "$LOG_DIR/nvidia_smi_benchmark_100ps.csv" &
  sampler_pid=$!
  trap 'kill "$sampler_pid" 2>/dev/null || true' EXIT
  stage=mdrun_benchmark_100ps
  OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
    -deffnm "$BENCH_DIR/gpr2_r59c_ascr18_100ps" \
    -ntomp "$NTHREADS" \
    -pin on \
    -nb gpu \
    -pme gpu \
    -bonded gpu \
    > "$LOG_DIR/mdrun_benchmark_100ps.log" 2>&1
  kill "$sampler_pid" 2>/dev/null || true
  wait "$sampler_pid" 2>/dev/null || true
  trap - EXIT

  "$GMX_CMD" check -f "$BENCH_DIR/gpr2_r59c_ascr18_100ps.xtc" \
    > "$LOG_DIR/gmx_check_benchmark_xtc.log" 2>&1
  "$GMX_CMD" check -e "$BENCH_DIR/gpr2_r59c_ascr18_100ps.edr" \
    > "$LOG_DIR/gmx_check_benchmark_edr.log" 2>&1
  stage=mdrun_issue_scan
  if grep -Ein 'Fatal error|LINCS WARNING|Segmentation fault|non-finite|(^|[^A-Za-z])nan([^A-Za-z]|$)' \
      "$LOG_DIR"/mdrun_*.log > "$LOG_DIR/mdrun_issue_scan.log"; then
    printf 'status\tmdrun_issue_scan_failed\n' > "$LOG_DIR/terminal_status.tsv"
    exit 1
  fi

  performance=$(grep '^Performance:' "$LOG_DIR/mdrun_benchmark_100ps.log" | tail -n 1 | awk '{print $2}')
  {
    printf 'key\tvalue\n'
    printf 'status\tfinished\n'
    printf 'system\tGpr2_R59C_ASCR18\n'
    printf 'final_atoms\t130638\n'
    printf 'popc\t200\n'
    printf 'pot\t88\n'
    printf 'cla\t100\n'
    printf 'tip3\t32404\n'
    printf 'removed_popc_resid\t410\n'
    printf 'benchmark_ps\t100\n'
    printf 'performance_ns_per_day\t%s\n' "$performance"
    printf 'finished\t%s\n' "$(date -Is)"
  } > "$LOG_DIR/preproduction_benchmark_summary.tsv"
  find "$RUN_ROOT/input" "$RUN_ROOT/preproduction" "$RUN_ROOT/benchmark_100ps" "$RUN_ROOT/logs/preproduction" \
    -type f ! -path "$LOG_DIR/terminal_status.tsv" -print0 \
    | sort -z | xargs -0 sha256sum > "$RUN_ROOT/preproduction_benchmark_archive.sha256"
  trap - ERR
  printf 'status\tfinished\n' > "$LOG_DIR/terminal_status.tsv"
}

local_sync_and_launch() {
  required=(
    "$RETURN_GMX/step5_input.gro"
    "$RETURN_GMX/step5_input.pdb"
    "$RETURN_GMX/topol.top"
    "$RETURN_GMX/index.ndx"
    "$RETURN_GMX/step7_production.mdp"
    "$LIGAND_DIR/ASCR18_receptor_frame.gro"
    "$SYSTEM_DIR/gromacs/ASCR18.itp"
    "$SYSTEM_DIR/gromacs/posre_ASCR18.itp"
    "$SYSTEM_DIR/gromacs/toppar/cgenff_ASCR18.itp"
    "$ROOT/experiments/md-simulation/scripts/assemble_complex.py"
  )
  for path in "${required[@]}"; do
    [[ -s "$path" ]] || { echo "ERROR: missing input $path" >&2; exit 1; }
  done

  ssh "$REMOTE" "mkdir -p '$RUN_ROOT/input/gromacs' '$RUN_ROOT/logs/preproduction'"
  rsync -a --delete "$RETURN_GMX/" "$REMOTE:$RUN_ROOT/input/gromacs/"
  rsync -a \
    "$LIGAND_DIR/ASCR18_receptor_frame.gro" \
    "$REMOTE:$RUN_ROOT/input/gromacs/ligand.gro"
  rsync -a \
    "$SYSTEM_DIR/gromacs/ASCR18.itp" \
    "$SYSTEM_DIR/gromacs/posre_ASCR18.itp" \
    "$ROOT/experiments/md-simulation/scripts/assemble_complex.py" \
    "$REMOTE:$RUN_ROOT/input/gromacs/"
  rsync -a "$SYSTEM_DIR/gromacs/toppar/cgenff_ASCR18.itp" \
    "$REMOTE:$RUN_ROOT/input/gromacs/toppar/cgenff_ASCR18.itp"
  rsync -a "$0" "$REMOTE:$RUN_ROOT/e2_run_gpr2_r59c_ascr18_preproduction.sh"
  ssh "$REMOTE" "cd '$RUN_ROOT/input/gromacs' && find . -type f -print0 | sort -z | xargs -0 sha256sum > '$RUN_ROOT/input_manifest.sha256'"

  if ssh "$REMOTE" "tmux has-session -t '$SESSION' 2>/dev/null"; then
    echo "ERROR: tmux session already exists: $SESSION" >&2
    exit 66
  fi
  ssh "$REMOTE" \
    "tmux new-session -d -s '$SESSION' 'RUN_ROOT=$RUN_ROOT GMX_CMD=$GMX_CMD NTHREADS=$NTHREADS MAXWARN=$MAXWARN REMOVE_POPC=$REMOVE_POPC BENCHMARK_NSTEPS=$BENCHMARK_NSTEPS BENCHMARK_SEED=$BENCHMARK_SEED bash $RUN_ROOT/e2_run_gpr2_r59c_ascr18_preproduction.sh --remote-run >> $RUN_ROOT/logs/preproduction/launcher.log 2>&1'"
  printf 'launched_session\t%s\nrun_root\t%s\n' "$SESSION" "$RUN_ROOT"
}

if [[ ${1:-} == "--remote-run" ]]; then
  remote_run
else
  local_sync_and_launch
fi
