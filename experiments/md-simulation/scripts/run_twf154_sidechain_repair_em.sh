#!/usr/bin/env bash
# Minimize a documented side-chain-only repair with the unchanged force field.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
SEED=$(realpath "$3")
GMX="$ROOT/software/gromacs_double/install/bin/gmx_d"
HELPER="$ROOT/scripts/twf154_preheat_support_v3.py"
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=1
cd "$ROOT/runs/$CASE"
mkdir attempt6_trp174_orientation
cd attempt6_trp174_orientation
exec > runner.log 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Trp174 orientation preparation failed at line $LINENO"' ERR
ln -s ../toppar toppar
ln -s ../ionized.gro ionized.gro
cp ../input_contract.json .
cp "$SEED" sidechain_repaired.gro
sed 's@../ff/@../../ff/@g' ../topol.top > topol.top
cp ../em.mdp em.mdp
sha256sum sidechain_repaired.gro ../ionized.gro em.mdp topol.top "$0" > input.sha256
python3 "$HELPER" event RUNNING_VERIFIED "Only Trp174 input side-chain torsions changed; original backbone/ligand preserved; unchanged original force-field EM with no temporary bond/freeze changes"
"$GMX" grompp -f em.mdp -c sidechain_repaired.gro -r ../ionized.gro -p topol.top -n ../index.ndx -o em.tpr > em.grompp.log 2>&1
"$GMX" mdrun -deffnm em -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > em.mdrun.log 2>&1
python3 "$HELPER" em_gate
python3 "$ROOT/scripts/check_twf154_snapshot_v5.py" .. em.gro "$ROOT/inputs/ligand_geometry_contract_v2.json" em_snapshot_qc_v5.json > em_snapshot_qc_v5.log 2>&1
sha256sum em.gro em.tpr em.edr > output.sha256
python3 "$HELPER" event TERMINAL_NORMAL "Original-force-field EM finished with full covalent/ring geometry checks; ready for heating promotion"
