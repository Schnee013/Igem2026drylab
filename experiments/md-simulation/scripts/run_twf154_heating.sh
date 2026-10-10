#!/usr/bin/env bash
# Promote an audited EM branch into its own heating directory; never production.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
EMREL=${3:-em.gro}
GMX=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
QC="$ROOT/scripts/check_twf154_snapshot_v5.py"
HELPER="$ROOT/scripts/twf154_preheat_support_v3.py"
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=0
cd "$ROOT/runs/$CASE"
exec 199>heating_dispatch.lock
flock -n 199
test ! -e heat.tpr
test ! -e heating_v4
python3 "$QC" "$PWD" "$PWD/$EMREL" "$ROOT/inputs/ligand_geometry_contract_v2.json" em_promotion_qc.json
FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
test "$FREE" -ge 2048
mkdir heating_v4
OUT="$PWD/heating_v4"
exec > "$OUT/runner.log" 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Heating v4 failed at line $LINENO; see heating_v4/runner.log"' ERR
sha256sum "$EMREL" ionized.gro heat.mdp hold.mdp topol.top "$QC" "$0" > "$OUT/input.sha256"
printf '%s\n' "$EMREL" > "$OUT/em_source.txt"
python3 "$HELPER" event RUNNING_VERIFIED "Audited EM branch $EMREL promoted to heating_v4: GPU, 8 CPU threads, 50 ps ramp plus 75 ps hold"
ARGS=(-ntomp 8 -pin off -nb gpu -pme gpu -bonded cpu -update cpu)
"$GMX" grompp -f heat.mdp -c "$EMREL" -r ionized.gro -p topol.top -n index.ndx -o "$OUT/heat.tpr" -po "$OUT/heat_mdout.mdp" > "$OUT/heat.grompp.log" 2>&1
"$GMX" mdrun -deffnm "$OUT/heat" "${ARGS[@]}" > "$OUT/heat.mdrun.log" 2>&1
python3 "$HELPER" event RUNNING_VERIFIED "heating_v4 temperature ramp finished; 75 ps hold starts"
"$GMX" grompp -f hold.mdp -c "$OUT/heat.gro" -t "$OUT/heat.cpt" -r ionized.gro -p topol.top -n index.ndx -o "$OUT/hold.tpr" -po "$OUT/hold_mdout.mdp" > "$OUT/hold.grompp.log" 2>&1
"$GMX" mdrun -deffnm "$OUT/hold" "${ARGS[@]}" > "$OUT/hold.mdrun.log" 2>&1
"$GMX" check -f "$OUT/hold.xtc" > "$OUT/hold.check.log" 2>&1
printf 'Temperature\nPotential\nT-SOLU\nT-MEMB\nT-SOLV\n0\n' | "$GMX" energy -f "$OUT/hold.edr" -b 105 -o "$OUT/final20ps_energy.xvg" > "$OUT/final20ps_energy.log" 2>&1
python3 "$QC" "$PWD" "$OUT/hold.gro" "$ROOT/inputs/ligand_geometry_contract_v2.json" "$OUT/hold_snapshot_qc.json"
sha256sum "$OUT/heat.gro" "$OUT/hold.gro" "$OUT/hold.cpt" "$OUT/hold.xtc" "$OUT/hold.edr" > "$OUT/output.sha256"
python3 "$HELPER" event TERMINAL_NORMAL "heating_v4 completed 125 ps and final snapshot geometry passed; final temperature/log audit pending; not production-ready"
