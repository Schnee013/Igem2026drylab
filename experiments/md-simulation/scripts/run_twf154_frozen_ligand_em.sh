#!/usr/bin/env bash
# Independent rescue diagnostic: hold the exact ligand pose during initial EM.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
GMX="$ROOT/software/gromacs_double/install/bin/gmx_d"
HELPER="$ROOT/scripts/twf154_preheat_support_v3.py"
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=1
cd "$ROOT/runs/$CASE"
mkdir attempt5_frozen_ligand
cd attempt5_frozen_ligand
exec > runner.log 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Frozen-ligand diagnostic failed at line $LINENO"' ERR
ln -s ../toppar toppar
ln -s ../ionized.gro ionized.gro
cp ../input_contract.json .
cp ../index.ndx frozen.ndx
sed 's@../ff/@../../ff/@g' ../topol.top > topol.top
python3 - <<'PY'
import json
from pathlib import Path
j=json.loads(Path('input_contract.json').read_text());n=j['atoms']
cfg=json.loads(Path('../../inputs/ligand_geometry_contract_v2.json').read_text()) if Path('../../inputs/ligand_geometry_contract_v2.json').exists() else json.loads(Path('../../../inputs/ligand_geometry_contract_v2.json').read_text())
nl=len(cfg[j['pose_mapping']]['atom_names'])
with Path('frozen.ndx').open('a') as h:h.write('\n[ FROZEN_LIG ]\n'+' '.join(map(str,range(n+1,n+nl+1)))+'\n')
PY
sed -e 's/emstep = 0.001/emstep = 0.0001/' -e 's/nsteps = 100000/nsteps = 10000/' ../em.mdp > frozen.mdp
printf 'freezegrps = FROZEN_LIG\nfreezedim = Y Y Y\n' >> frozen.mdp
sed 's/emstep = 0.001/emstep = 0.0001/' ../em.mdp > em.mdp
sha256sum ../ionized.gro frozen.mdp em.mdp topol.top frozen.ndx "$0" > input.sha256
python3 "$HELPER" event RUNNING_VERIFIED "Independent original-input retry: exact entire ligand pose frozen for initial EM while lid remains free; frozen group removed before final EM"
"$GMX" grompp -f frozen.mdp -c ../ionized.gro -r ../ionized.gro -p topol.top -n frozen.ndx -o frozen.tpr > frozen.grompp.log 2>&1
"$GMX" mdrun -deffnm frozen -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > frozen.mdrun.log 2>&1
# This bounded intermediate may still have strained receptor bonds. Record the
# geometry without promoting it; only the final original-force-field EM can pass.
python3 "$ROOT/scripts/check_twf154_snapshot_v5.py" .. frozen.gro "$ROOT/inputs/ligand_geometry_contract_v2.json" frozen_snapshot_qc.json > frozen_snapshot_qc.log 2>&1 || true
python3 "$HELPER" event RUNNING_VERIFIED "Frozen-pose intermediate recorded, not accepted as a simulation endpoint; freeze removed for original-force-field EM"
"$GMX" grompp -f em.mdp -c frozen.gro -r ../ionized.gro -p topol.top -n ../index.ndx -o em.tpr > em.grompp.log 2>&1
"$GMX" mdrun -deffnm em -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > em.mdrun.log 2>&1
python3 "$HELPER" em_gate
python3 "$ROOT/scripts/check_twf154_snapshot_v5.py" .. em.gro "$ROOT/inputs/ligand_geometry_contract_v2.json" em_snapshot_qc_v5.json > em_snapshot_qc_v5.log 2>&1
sha256sum frozen.gro em.gro em.tpr em.edr > output.sha256
python3 "$HELPER" event TERMINAL_NORMAL "Ligand freeze removed; final original-force-field EM passed force and geometry; eligible for heating"
