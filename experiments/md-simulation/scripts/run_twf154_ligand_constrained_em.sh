#!/usr/bin/env bash
# Protect ligand heavy-atom bonds only during a bounded initial clash-relief EM.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
CASE=$2
GMX="$ROOT/software/gromacs_double/install/bin/gmx_d"
HELPER="$ROOT/scripts/twf154_preheat_support_v3.py"
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=1
cd "$ROOT/runs/$CASE"
mkdir attempt4_ligand_constraints
cd attempt4_ligand_constraints
exec > runner.log 2>&1
trap 'python3 "$HELPER" event TERMINAL_ABNORMAL "Ligand-constrained EM failed at line $LINENO"' ERR
ln -s ../ionized.gro ionized.gro
cp ../input_contract.json .
sed -e 's@../ff/@../../ff/@g' -e 's@"toppar/@"../toppar/@g' ../topol.top > topol.top
python3 - <<'PY'
import json
from pathlib import Path
info=json.loads(Path('input_contract.json').read_text());name=info['ligand'].upper();src=Path('../toppar')/(name+'.itp')
types={};mass={};parameters={};section=''
for l in Path('../toppar/cgenff.itp').read_text().splitlines():
 t=l.split(';')[0].strip()
 if t.startswith('['):section=t.strip('[] ')
 elif t and not t.startswith('#') and section=='bondtypes':
  f=t.split();parameters[tuple(sorted(f[:2]))]=float(f[3])
out=[];constraints=[];section=''
for l in src.read_text().splitlines():
 t=l.split(';')[0].strip()
 if t.startswith('['):section=t.strip('[] ')
 elif t and not t.startswith('#'):
  f=t.split()
  if section=='atoms':types[int(f[0])]=f[1];mass[int(f[0])]=float(f[7])
  elif section=='bonds':
   i,j=map(int,f[:2])
   if mass[i]>2 and mass[j]>2:
    assert f[2]=='1';length=parameters[tuple(sorted([types[i],types[j]]))];constraints.append([i,j,length]);continue
 out.append(l)
assert constraints
out+=['','[ constraints ]','; Temporary heavy-bond geometry protection; original topology restored for final EM']
out += [f'{i} {j} 1 {length:.9f}' for i,j,length in constraints]
Path('ligand_constrained.itp').write_text('\n'.join(out)+'\n')
Path('constrained.top').write_text(Path('topol.top').read_text().replace(f'"../toppar/{name}.itp"','"ligand_constrained.itp"'))
Path('constraint_contract.json').write_text(json.dumps({'ligand':name,'constraints':constraints,'source':str(src),'length_source':'existing CGenFF equilibrium bond lengths','final_topology':'original unchanged ligand bonds'},indent=2))
PY
sed -e 's/emstep = 0.001/emstep = 0.0001/' -e 's/nsteps = 100000/nsteps = 10000/' ../em.mdp > constrained.mdp
printf 'constraint_algorithm = LINCS\nlincs_order = 8\nlincs_iter = 4\n' >> constrained.mdp
sed 's/emstep = 0.001/emstep = 0.0001/' ../em.mdp > em.mdp
sha256sum ../ionized.gro constrained.mdp em.mdp topol.top constrained.top ligand_constrained.itp "$0" > input.sha256
python3 "$HELPER" event RUNNING_VERIFIED "Original ionized coordinates; only ligand heavy bonds constrained at CGenFF equilibrium lengths during bounded clash-relief EM; original topology restored before final EM"
"$GMX" grompp -f constrained.mdp -c ../ionized.gro -r ../ionized.gro -p constrained.top -n ../index.ndx -o constrained.tpr > constrained.grompp.log 2>&1
"$GMX" mdrun -deffnm constrained -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > constrained.mdrun.log 2>&1
python3 "$ROOT/scripts/check_twf154_snapshot_v2.py" .. constrained.gro "$ROOT/inputs/ligand_geometry_contract.json" constrained_snapshot_qc.json
python3 "$HELPER" event RUNNING_VERIFIED "Ligand-constrained clash relief passed geometry; original unconstrained ligand topology restored"
"$GMX" grompp -f em.mdp -c constrained.gro -r ../ionized.gro -p topol.top -n ../index.ndx -o em.tpr > em.grompp.log 2>&1
"$GMX" mdrun -deffnm em -ntmpi 1 -ntomp 16 -nb cpu -pme cpu -pin off > em.mdrun.log 2>&1
python3 "$HELPER" em_gate
python3 "$ROOT/scripts/check_twf154_snapshot_v2.py" .. em.gro "$ROOT/inputs/ligand_geometry_contract.json" em_snapshot_qc_v2.json
sha256sum constrained.gro em.gro em.tpr em.edr > output.sha256
python3 "$HELPER" event TERMINAL_NORMAL "Final EM with original ligand topology passed force and full snapshot checks; eligible for heating"
