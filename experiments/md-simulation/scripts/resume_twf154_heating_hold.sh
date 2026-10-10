#!/usr/bin/env bash
# Continue a completed 50 ps ramp when its supervising session disappeared.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
GMX=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
QC="$ROOT/scripts/check_twf154_snapshot_v5.py"
HELPER="$ROOT/scripts/twf154_preheat_support_v3.py"
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=0
cd "$ROOT/runs/$CASE"
exec 199>heating_dispatch.lock
flock -n 199
OUT="$PWD/heating_v4"
test -d "$OUT"
test ! -e "$OUT/hold.tpr"
exec >> "$OUT/runner.log" 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Hold recovery failed at line $LINENO; see heating_v4/runner.log"' ERR
sha256sum -c "$OUT/input.sha256"
"$GMX" dump -cp "$OUT/heat.cpt" > "$OUT/heat_checkpoint_recovery.txt" 2>&1
python3 - "$OUT" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);s=(p/'heat.log').read_text()
assert 'Finished mdrun' in s
assert re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+([\d.]+)',s)[-1]==('50000','50.00000')
assert not re.search(r'LINCS WARNING|cannot be settled|Fatal error',s)
c=(p/'heat_checkpoint_recovery.txt').read_text()
assert re.search(r'^\s*step\s*=\s*50000\s*$',c,re.M)
assert float(re.search(r'^\s*t\s*=\s*([\d.eE+-]+)',c,re.M)[1])==50
PY
python3 "$QC" "$PWD" "$OUT/heat.gro" "$ROOT/inputs/ligand_geometry_contract_v2.json" "$OUT/heat_snapshot_qc.json"
FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
test "$FREE" -ge 2048
sha256sum "$0" "$OUT/heat.gro" "$OUT/heat.cpt" > "$OUT/recovery_input.sha256"
python3 "$HELPER" event RUNNING_VERIFIED "Recovered after supervising sessions disappeared: verified completed 50 ps ramp/checkpoint; original 75 ps hold starts without repeating ramp"
ARGS=(-ntomp 8 -pin off -nb gpu -pme gpu -bonded cpu -update cpu)
"$GMX" grompp -f hold.mdp -c "$OUT/heat.gro" -t "$OUT/heat.cpt" -r ionized.gro -p topol.top -n index.ndx -o "$OUT/hold.tpr" -po "$OUT/hold_mdout.mdp" > "$OUT/hold.grompp.log" 2>&1
"$GMX" mdrun -deffnm "$OUT/hold" "${ARGS[@]}" > "$OUT/hold.mdrun.log" 2>&1
"$GMX" check -f "$OUT/hold.xtc" > "$OUT/hold.check.log" 2>&1
printf 'Temperature\nPotential\nT-SOLU\nT-MEMB\nT-SOLV\n0\n' | "$GMX" energy -f "$OUT/hold.edr" -b 105 -o "$OUT/final20ps_energy.xvg" > "$OUT/final20ps_energy.log" 2>&1
python3 "$QC" "$PWD" "$OUT/hold.gro" "$ROOT/inputs/ligand_geometry_contract_v2.json" "$OUT/hold_snapshot_qc.json"
sha256sum "$OUT/heat.gro" "$OUT/hold.gro" "$OUT/hold.cpt" "$OUT/hold.xtc" "$OUT/hold.edr" > "$OUT/output.sha256"
python3 "$HELPER" event TERMINAL_NORMAL "heating_v4 completed 125 ps after hold recovery; final snapshot geometry passed; final temperature/log audit pending"
