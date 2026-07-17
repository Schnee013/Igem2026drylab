#!/usr/bin/env bash
set -Eeuo pipefail

REMOTE=${REMOTE:-nkuliulab-e2}
RUN_ROOT=${RUN_ROOT:-/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716}
GMX_CMD=${GMX_CMD:-/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi}
NTHREADS=${NTHREADS:-24}
MAXWARN=${MAXWARN:-11}
NSTEPS=${NSTEPS:-100000000}
PREFIX=${PREFIX:-gpr2_r59c_ascr18_rep1_200ns}
SESSION=${SESSION:-gpr2_r59c_prod_rep1_20260716}

PREPROD_DIR="$RUN_ROOT/preproduction/gromacs"
PREPROD_LOG="$RUN_ROOT/logs/preproduction"
PROD_DIR="$RUN_ROOT/production"
LOG_DIR="$RUN_ROOT/logs/production"
SANITY_DIR="$RUN_ROOT/sanity/production"

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
completion_text = mdrun + "\n" + production_log
atoms = re.search(r"# Atoms\s+(\d+)", xtc)
xtc_last = re.findall(r"Last frame\s+\d+\s+time\s+([0-9.]+)", xtc)
edr_last = re.findall(r"Last energy frame read\s+\d+\s+time\s+([0-9.]+)", edr)
if not atoms or int(atoms.group(1)) != 130638:
    raise SystemExit(f"unexpected production XTC atom count: {atoms.group(1) if atoms else 'missing'}")
if not xtc_last or abs(float(xtc_last[-1]) - 200000.0) > 0.01:
    raise SystemExit(f"unexpected final XTC time: {xtc_last[-1] if xtc_last else 'missing'}")
if not edr_last or abs(float(edr_last[-1]) - 200000.0) > 0.01:
    raise SystemExit(f"unexpected final EDR time: {edr_last[-1] if edr_last else 'missing'}")
if "Finished mdrun on rank 0" not in completion_text or "Performance:" not in completion_text:
    raise SystemExit("normal mdrun completion markers missing")
PY
}

write_summary() {
  python3 - "$LOG_DIR/mdrun_${PREFIX}.log" "$LOG_DIR/nvidia_smi_mdrun_sampler.csv" <<'PY'
from pathlib import Path
import csv
import re
import sys

log = Path(sys.argv[1]).read_text(errors="replace")
performance_rows = re.findall(
    r"^Performance:\s+([0-9.]+)\s+([0-9.]+)", log, re.MULTILINE
)
perf = performance_rows[-1] if performance_rows else None
samples = []
for row in csv.reader(Path(sys.argv[2]).open()):
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

remote_run() {
  local run_mode=${1:-launch}
  mkdir -p "$PROD_DIR" "$LOG_DIR" "$SANITY_DIR"
  cd "$RUN_ROOT"

  if ! grep -Fxq $'status\tfinished' "$PREPROD_LOG/preproduction_benchmark_summary.tsv"; then
    printf 'status\tpreproduction_benchmark_not_finished\n' > "$LOG_DIR/terminal_status.tsv"
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
        printf 'status\trefuse_existing_mdrun_output\npath\t%s\n' "$output" \
          > "$LOG_DIR/terminal_status.tsv"
        exit 66
      fi
    done
  elif [[ $run_mode == resume ]]; then
    [[ -s "$PROD_DIR/${PREFIX}.tpr" && -s "$PROD_DIR/${PREFIX}.cpt" ]]
    if [[ -s "$PROD_DIR/${PREFIX}.gro" ]] \
        || grep -q 'Finished mdrun on rank 0' "$PROD_DIR/${PREFIX}.log" 2>/dev/null; then
      printf 'status\trefuse_resume_completed_mdrun\n' > "$LOG_DIR/terminal_status.tsv"
      exit 66
    fi
    if pgrep -ax gmx_mpi > "$LOG_DIR/resume_process_check.tsv"; then
      printf 'status\trefuse_resume_active_process\n' > "$LOG_DIR/terminal_status.tsv"
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
    printf 'status\tgpu_busy_before_production\n' > "$LOG_DIR/terminal_status.tsv"
    exit 75
  fi

  printf 'status\trunning\nmode\t%s\nstarted\t%s\n' \
    "$run_mode" "$(date -Is)" > "$LOG_DIR/terminal_status.tsv"
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
  trap 'kill "$sampler_pid" 2>/dev/null || true' EXIT

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
      >> "$LOG_DIR/mdrun_${PREFIX}.log" 2>&1
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
      > "$LOG_DIR/mdrun_${PREFIX}.log" 2>&1
  fi
  mdrun_status=$?
  set -e

  kill "$sampler_pid" 2>/dev/null || true
  wait "$sampler_pid" 2>/dev/null || true
  trap - EXIT
  date -Is > "$LOG_DIR/mdrun_end_time.txt"
  nvidia-smi > "$LOG_DIR/nvidia_smi_after.log"

  if [[ $mdrun_status -ne 0 ]]; then
    printf 'status\tmdrun_failed\nexit_code\t%s\n' "$mdrun_status" \
      > "$LOG_DIR/terminal_status.tsv"
    exit "$mdrun_status"
  fi

  final_sanity
  write_summary
  find production logs/production sanity/production \
    -type f ! -path "$LOG_DIR/terminal_status.tsv" -print0 \
    | sort -z | xargs -0 sha256sum > "$RUN_ROOT/production_archive.sha256"
  printf 'status\tfinished\nfinished\t%s\n' "$(date -Is)" \
    > "$LOG_DIR/terminal_status.tsv"
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

case ${1:-} in
  --remote-run) remote_run launch ;;
  --remote-resume) remote_run resume ;;
  --resume) local_launch resume ;;
  "") local_launch launch ;;
  *) echo "ERROR: unsupported argument $1" >&2; exit 64 ;;
esac
