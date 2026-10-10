#!/usr/bin/env bash
# Geometry-preserving diagnostic retry; release temporary constraints before heat.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
GMX="$ROOT/software/gromacs_double/install/bin/gmx_d"
HELPER="$ROOT/scripts/twf154_preheat_support_v3.py"
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=1
cd "$ROOT/runs/$CASE"
mkdir attempt3_constrained
cd attempt3_constrained
exec > runner.log 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Constrained EM attempt failed at line $LINENO"' ERR
ln -s ../toppar toppar
ln -s ../ionized.gro ionized.gro
sed 's@../ff/@../../ff/@g' ../topol.top > topol.top
sed -e 's/emstep = 0.001/emstep = 0.0001/' -e 's/constraints = none/constraints = all-bonds/' ../em.mdp > constrained.mdp
printf 'constraint_algorithm = LINCS\nlincs_order = 8\nlincs_iter = 4\n' >> constrained.mdp
sed 's/emstep = 0.001/emstep = 0.0001/' ../em.mdp > em.mdp
cp ../input_contract.json .
sha256sum ../ionized.gro ../em.mdp constrained.mdp em.mdp topol.top "$0" > input.sha256
python3 "$HELPER" event RUNNING_VERIFIED "Same original ionized coordinates; temporary all-bond constraints during double-precision clash relief, then unconstrained-bond EM with original force field"
"$GMX" grompp -f constrained.mdp -c ../ionized.gro -r ../ionized.gro -p topol.top -n ../index.ndx -o constrained.tpr > constrained.grompp.log 2>&1
"$GMX" mdrun -deffnm constrained -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > constrained.mdrun.log 2>&1
python3 "$ROOT/scripts/check_twf154_snapshot_v2.py" .. constrained.gro "$ROOT/inputs/ligand_geometry_contract.json" constrained_snapshot_qc.json
python3 "$HELPER" event RUNNING_VERIFIED "Constrained clash relief produced an intact snapshot; original unconstrained-bond minimization resumes"
"$GMX" grompp -f em.mdp -c constrained.gro -r ../ionized.gro -p topol.top -n ../index.ndx -o em.tpr > em.grompp.log 2>&1
"$GMX" mdrun -deffnm em -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > em.mdrun.log 2>&1
python3 "$HELPER" em_gate
python3 "$ROOT/scripts/check_twf154_snapshot_v2.py" .. em.gro "$ROOT/inputs/ligand_geometry_contract.json" em_snapshot_qc_v2.json
sha256sum constrained.gro em.gro em.tpr em.edr > output.sha256
python3 "$HELPER" event TERMINAL_NORMAL "Temporary all-bond constraints removed; final original-force-field EM and snapshot checks passed; awaiting heating"
