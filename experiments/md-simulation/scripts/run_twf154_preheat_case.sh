#!/usr/bin/env bash
# One isolated diagnostic: solvation, neutralization, EM, 50 ps ramp + 75 ps hold.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
MODE=${3:-cpu}
GMX=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
HELPER="$ROOT/scripts/twf154_preheat_support_v2.py"
export OMP_NUM_THREADS=16
export OPENBLAS_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES=0
mkdir -p "$ROOT/runs"
if [[ "$MODE" != heat_gpu && "$MODE" != heat_cpu ]]; then
test ! -e "$ROOT/runs/$CASE"
cp -a "$ROOT/inputs/membrane05/$CASE" "$ROOT/runs/$CASE"
ln -sfn ../inputs/membrane05/ff "$ROOT/runs/ff"
cd "$ROOT/runs/$CASE"
exec > runner.log 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Failed at line $LINENO; inspect runner.log and stage logs"' ERR
python3 "$HELPER" setup
python3 "$HELPER" event RUNNING_VERIFIED "Input preparation started; CPU threads 16"
sha256sum dry.gro topol.top toppar/*.itp > run_input.sha256
if [[ ! -s solvated.gro ]]; then
  "$GMX" solvate -cp dry.gro -cs spc216.gro -o solvated.gro -p topol.top > solvate.log 2>&1
fi
if "$GMX" grompp -f genion.mdp -c solvated.gro -p topol.top -o genion.tpr > genion.grompp.log 2>&1; then
  status=0
else
  status=$?
fi
if (( status != 0 )); then
  python3 "$HELPER" warning_gate
  "$GMX" grompp -f genion.mdp -c solvated.gro -p topol.top -o genion.tpr -maxwarn 1 > genion.accepted.log 2>&1
fi
read -r NP NN < <(python3 "$HELPER" ions)
printf 'SOL\n' | "$GMX" genion -s genion.tpr -o ionized.gro -p topol.top -pname POT -nname CLA -np "$NP" -nn "$NN" -seed 8428368 > genion.log 2>&1
python3 "$HELPER" index
"$GMX" grompp -f em.mdp -c ionized.gro -r ionized.gro -p topol.top -n index.ndx -o em.tpr -pp em.processed.top > em.grompp.log 2>&1
python3 "$HELPER" event RUNNING_VERIFIED "Neutral topology compiled without warning override; minimization starts"
"$GMX" mdrun -deffnm em -ntomp 16 -nb cpu -pme cpu -pin off > em.mdrun.log 2>&1
python3 "$HELPER" em_gate
python3 "$HELPER" event RUNNING_VERIFIED "Minimization passed force and final-water geometry checks"
else
  cd "$ROOT/runs/$CASE"
  exec >> runner.log 2>&1
  trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Failed in resumed heating at line $LINENO"' ERR
  python3 "$HELPER" em_gate
  test ! -e heat.tpr
fi
if [[ "$MODE" == em_only ]]; then
  python3 "$HELPER" event UNRESOLVED "Minimization completed and passed; queued for heating after first-system runtime validation"
  exit 0
fi
RUN_ARGS=(-ntomp 16 -pin off -nb cpu -pme cpu)
if [[ "$MODE" == gpu || "$MODE" == heat_gpu ]]; then
  exec 199>"$ROOT/gpu_preheat.lock"
  flock 199
  FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
  if (( FREE >= 4096 )); then
    RUN_ARGS=(-ntomp 16 -pin off -nb gpu -pme gpu -bonded cpu -update cpu)
  fi
fi
printf '%s\n' "${RUN_ARGS[*]}" > execution_backend.txt
"$GMX" grompp -f heat.mdp -c em.gro -r ionized.gro -p topol.top -n index.ndx -o heat.tpr > heat.grompp.log 2>&1
"$GMX" mdrun -deffnm heat "${RUN_ARGS[@]}" > heat.mdrun.log 2>&1
python3 "$HELPER" event RUNNING_VERIFIED "50 ps temperature ramp completed; 75 ps hold starts"
"$GMX" grompp -f hold.mdp -c heat.gro -t heat.cpt -r ionized.gro -p topol.top -n index.ndx -o hold.tpr > hold.grompp.log 2>&1
"$GMX" mdrun -deffnm hold "${RUN_ARGS[@]}" > hold.mdrun.log 2>&1
"$GMX" check -f hold.xtc > hold.check.log 2>&1
printf 'Temperature\nPotential\n0\n' | "$GMX" energy -f hold.edr -b 105 -o final20ps_energy.xvg > final20ps_energy.log 2>&1
sha256sum em.gro heat.gro hold.gro hold.cpt hold.xtc hold.edr > output.sha256
python3 "$HELPER" event TERMINAL_NORMAL "EM plus 125 ps NVT heating completed; structural/temperature audit still required; not production-ready"
