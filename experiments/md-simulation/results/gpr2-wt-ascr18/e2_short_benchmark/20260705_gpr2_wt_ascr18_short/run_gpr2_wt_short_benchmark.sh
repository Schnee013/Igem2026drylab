#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_short_benchmark_20260705"
INPUT_DIR="$RUN_ROOT/input/gromacs"
LOG_DIR="$RUN_ROOT/logs"
PROD_DIR="$RUN_ROOT/production_smoke"
SANITY_DIR="$RUN_ROOT/sanity"
GMX_CMD="/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi"
PREFIX="gpr2_wt_ascr18_short"
NTHREADS=24
GROMPP_MAXWARN=11

mkdir -p "$LOG_DIR" "$PROD_DIR" "$SANITY_DIR"
cd "$RUN_ROOT"

date --iso-8601=seconds > "$LOG_DIR/run_start_time.txt"
hostname > "$LOG_DIR/hostname.txt"
whoami > "$LOG_DIR/whoami.txt"
nvidia-smi > "$LOG_DIR/nvidia_smi_before.log"
"$GMX_CMD" --version > "$LOG_DIR/gmx_version.log" 2>&1

for required in \
  "$INPUT_DIR/step6.6.gro" \
  "$INPUT_DIR/topol_phase3.top" \
  "$INPUT_DIR/index.ndx" \
  "$INPUT_DIR/step7_production.mdp" \
  "$INPUT_DIR/ASCR18.itp" \
  "$INPUT_DIR/posre_ASCR18.itp" \
  "$INPUT_DIR/toppar/forcefield.itp" \
  "$INPUT_DIR/toppar/cgenff_ASCR18.itp" \
  "$INPUT_DIR/toppar/PROA.itp" \
  "$INPUT_DIR/toppar/POPC.itp" \
  "$INPUT_DIR/toppar/POT.itp" \
  "$INPUT_DIR/toppar/CLA.itp" \
  "$INPUT_DIR/toppar/TIP3.itp"; do
  test -s "$required"
done

python3 - <<'PY'
from pathlib import Path

input_mdp = Path("input/gromacs/step7_production.mdp")
output_mdp = Path("production_smoke/gpr2_wt_ascr18_short.mdp")
lines = input_mdp.read_text().splitlines()
seen = set()
out = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith("nsteps"):
        out.append("nsteps                  = 50000")
        seen.add("nsteps")
    elif stripped.startswith("continuation"):
        out.append("continuation            = no")
        seen.add("continuation")
    elif stripped.startswith("gen-vel") or stripped.startswith("gen_vel"):
        out.append("gen-vel                 = yes")
        seen.add("gen-vel")
    elif stripped.startswith("gen-temp") or stripped.startswith("gen_temp"):
        out.append("gen-temp                = 303.15")
        seen.add("gen-temp")
    elif stripped.startswith("gen-seed") or stripped.startswith("gen_seed"):
        out.append("gen-seed                = 20260705")
        seen.add("gen-seed")
    else:
        out.append(line)
if "gen-vel" not in seen:
    out.append("gen-vel                 = yes")
if "gen-temp" not in seen:
    out.append("gen-temp                = 303.15")
if "gen-seed" not in seen:
    out.append("gen-seed                = 20260705")
output_mdp.write_text("\n".join(out) + "\n")
PY

(
  cd "$INPUT_DIR"
  "$GMX_CMD" grompp \
    -f "$PROD_DIR/${PREFIX}.mdp" \
    -o "$PROD_DIR/${PREFIX}.tpr" \
    -c "$INPUT_DIR/step6.6.gro" \
    -p "$INPUT_DIR/topol_phase3.top" \
    -n "$INPUT_DIR/index.ndx" \
    -po "$PROD_DIR/${PREFIX}_out.mdp" \
    -maxwarn "$GROMPP_MAXWARN"
) > "$LOG_DIR/grompp_${PREFIX}.log" 2>&1

python3 - <<'PY'
from pathlib import Path
import sys

expected = 11
log_path = Path("logs/grompp_gpr2_wt_ascr18_short.log")
log = log_path.read_text(errors="replace")
if "Fatal error" in log:
    sys.exit("grompp fatal error after maxwarn")

lines = log.splitlines()
warning_lines = [i for i, line in enumerate(lines) if line.startswith("WARNING ")]
if len(warning_lines) != expected:
    sys.exit(f"unexpected grompp warning count: {len(warning_lines)}")

for i in warning_lines:
    header = lines[i]
    body = "\n".join(lines[i:i + 6])
    if "[file cgenff_ASCR18.itp," not in header:
        sys.exit(f"unexpected warning source: {header}")
    if "Encountered a second line of parameters for dihedral type 9" not in body:
        sys.exit(f"unexpected warning body: {header}")

Path("logs/grompp_warning_gate.txt").write_text(
    "status\taccepted\n"
    "warning_count\t11\n"
    "warning_source\tcgenff_ASCR18.itp duplicate type-9 dihedral parameters\n"
)
PY

ACTIVE_GPU_PROCS="$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits 2>/dev/null || true)"
if [ -n "$ACTIVE_GPU_PROCS" ]; then
  printf '%s\n' "$ACTIVE_GPU_PROCS" > "$LOG_DIR/gpu_busy_before_mdrun.log"
  {
    printf 'key\tvalue\n'
    printf 'status\tgpu_busy_before_mdrun\n'
    printf 'nsteps_override\t50000\n'
    printf 'nominal_ps\t100\n'
  } > "$LOG_DIR/production_short_summary.tsv"
  exit 75
fi

(
  while true; do
    nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu \
      --format=csv,noheader,nounits
    sleep 5
  done
) > "$LOG_DIR/nvidia_smi_production_short.csv" &
SAMPLER_PID=$!

set +e
OMP_NUM_THREADS="$NTHREADS" "$GMX_CMD" mdrun \
  -v \
  -deffnm "$PROD_DIR/$PREFIX" \
  -ntomp "$NTHREADS" \
  -pin on \
  -nb gpu \
  -pme gpu \
  -bonded gpu \
  > "$LOG_DIR/mdrun_${PREFIX}.log" 2>&1
MDRUN_STATUS=$?
set -e

kill "$SAMPLER_PID" 2>/dev/null || true
wait "$SAMPLER_PID" 2>/dev/null || true
nvidia-smi > "$LOG_DIR/nvidia_smi_after.log"

if [ "$MDRUN_STATUS" -ne 0 ]; then
  echo "mdrun_status	$MDRUN_STATUS" > "$LOG_DIR/production_short_summary.tsv"
  exit "$MDRUN_STATUS"
fi

"$GMX_CMD" check -f "$PROD_DIR/${PREFIX}.xtc" > "$LOG_DIR/sanity_short_prod_xtc_check.log" 2>&1
"$GMX_CMD" check -e "$PROD_DIR/${PREFIX}.edr" > "$LOG_DIR/sanity_short_prod_edr_check.log" 2>&1
printf 'Temperature\nPressure\nDensity\n0\n' | "$GMX_CMD" energy \
  -f "$PROD_DIR/${PREFIX}.edr" \
  -o "$SANITY_DIR/${PREFIX}_energy.xvg" \
  > "$LOG_DIR/sanity_short_prod_energy.log" 2>&1

grep -Ein 'fatal|error|lincs|cuda|nan' "$LOG_DIR/mdrun_${PREFIX}.log" > "$LOG_DIR/mdrun_issue_scan.log" || true

python3 - <<'PY'
from pathlib import Path
import csv
import re

log = Path("logs/mdrun_gpr2_wt_ascr18_short.log").read_text(errors="replace")
perf = re.search(r"^Performance:\s+([0-9.]+)\s+([0-9.]+)", log, re.MULTILINE)
samples = []
csv_path = Path("logs/nvidia_smi_production_short.csv")
if csv_path.exists():
    for row in csv.reader(csv_path.open()):
        if len(row) < 6:
            continue
        try:
            util = float(row[1].strip())
            mem = float(row[2].strip())
            total = float(row[3].strip())
            power = float(row[4].strip())
            temp = float(row[5].strip())
        except ValueError:
            continue
        samples.append((util, mem, total, power, temp))

util_values = [s[0] for s in samples]
nonzero = [v for v in util_values if v > 0]
mem_values = [s[1] for s in samples]
power_values = [s[3] for s in samples]
temp_values = [s[4] for s in samples]

lines = [
    ("finished", Path("logs/run_end_time.txt").read_text().strip() if Path("logs/run_end_time.txt").exists() else ""),
    ("nsteps_override", "50000"),
    ("nominal_ps", "100"),
    ("performance_ns_per_day", perf.group(1) if perf else ""),
    ("performance_hour_per_ns", perf.group(2) if perf else ""),
    ("gpu_samples", str(len(samples))),
    ("gpu_utilization_avg_percent", f"{sum(util_values) / len(util_values):.2f}" if util_values else ""),
    ("gpu_utilization_nonzero_avg_percent", f"{sum(nonzero) / len(nonzero):.2f}" if nonzero else ""),
    ("gpu_utilization_max_percent", f"{max(util_values):.0f}" if util_values else ""),
    ("gpu_memory_max_mib", f"{max(mem_values):.0f}" if mem_values else ""),
    ("gpu_memory_total_mib", f"{samples[-1][2]:.0f}" if samples else ""),
    ("gpu_power_avg_w", f"{sum(power_values) / len(power_values):.2f}" if power_values else ""),
    ("gpu_temperature_max_c", f"{max(temp_values):.0f}" if temp_values else ""),
]
Path("logs/production_short_summary.tsv").write_text(
    "key\tvalue\n" + "\n".join(f"{k}\t{v}" for k, v in lines) + "\n"
)
PY

date --iso-8601=seconds > "$LOG_DIR/run_end_time.txt"
python3 - <<'PY'
from pathlib import Path
summary = Path("logs/production_short_summary.tsv")
text = summary.read_text()
end_time = Path("logs/run_end_time.txt").read_text().strip()
text = text.replace("finished\t\n", f"finished\t{end_time}\n")
summary.write_text(text)
PY

find input production_smoke logs sanity \
  -type f \
  ! -path 'logs/manifest_sha256_after_short_benchmark.txt' \
  -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 sha256sum \
  > "$LOG_DIR/manifest_sha256_after_short_benchmark.txt"
