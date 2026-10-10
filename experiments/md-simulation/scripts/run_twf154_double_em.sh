#!/usr/bin/env bash
# Retry the unchanged ionized starting coordinates using double precision.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
GMX="$ROOT/software/gromacs_double/install/bin/gmx_d"
HELPER="$ROOT/scripts/twf154_preheat_support_v2.py"
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=1
cd "$ROOT/runs/$CASE"
mkdir attempt2_double
cd attempt2_double
exec > runner.log 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Double precision EM failed at line $LINENO"' ERR
ln -s ../toppar toppar
sed 's@../ff/@../../ff/@g' ../topol.top > topol.top
sed 's/emstep = 0.001/emstep = 0.0001/' ../em.mdp > em.mdp
cp ../input_contract.json .
"$GMX" --version > binary_identity.txt 2>&1
sha256sum ../ionized.gro ../em.mdp em.mdp topol.top > input.sha256
python3 "$HELPER" event RUNNING_VERIFIED "Double precision EM from original ionized coordinates; same force field, emstep 0.0001 nm"
"$GMX" grompp -f em.mdp -c ../ionized.gro -r ../ionized.gro -p topol.top -n ../index.ndx -o em.tpr > em.grompp.log 2>&1
"$GMX" mdrun -deffnm em -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > em.mdrun.log 2>&1
python3 "$HELPER" em_gate
sha256sum em.gro em.tpr em.edr > output.sha256
python3 "$HELPER" event TERMINAL_NORMAL "Double precision minimization passed; requires geometric review and separate heating promotion"
