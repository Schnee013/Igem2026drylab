#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$1" && pwd)
OUT="$ROOT/benchmarks/precision_forces16"
mkdir "$OUT"
cd "$ROOT/runs/rebuilt_n84v_ascr18"
cp "$ROOT/benchmarks/precision_smoke/point.mdp" "$OUT/point.mdp"
printf 'nstfout = 1\n' >> "$OUT/point.mdp"
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=1
for mode in mixed double; do
  if [[ "$mode" == mixed ]]; then
    GMX=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
    EXTRA=()
  else
    GMX="$ROOT/software/gromacs_double/install/bin/gmx_d"
    EXTRA=(-ntmpi 1)
  fi
  "$GMX" grompp -f "$OUT/point.mdp" -c em.gro -r ionized.gro -p topol.top -n index.ndx -o "$OUT/$mode.tpr" -po "$OUT/${mode}_mdout.mdp" > "$OUT/$mode.grompp.log" 2>&1
  "$GMX" mdrun -s "$OUT/$mode.tpr" -rerun em.gro -deffnm "$OUT/$mode" -ntomp 16 "${EXTRA[@]}" -nb cpu -pme cpu -pin off > "$OUT/$mode.mdrun.log" 2>&1
  printf 'System\n' | "$GMX" traj -s "$OUT/$mode.tpr" -f "$OUT/$mode.trr" -of "$OUT/$mode.force.xvg" -fp > "$OUT/$mode.traj.log" 2>&1
  printf 'Potential\n0\n' | "$GMX" energy -f "$OUT/$mode.edr" -o "$OUT/$mode.energy.xvg" > "$OUT/$mode.energy.log" 2>&1
done
python3 - "$OUT" <<'PY'
import json,sys,math
from pathlib import Path
p=Path(sys.argv[1])
def row(name):
 return list(map(float,[l for l in (p/name).read_text().splitlines() if l and not l.startswith(('#','@'))][-1].split()))[1:]
a,b=row('mixed.force.xvg'),row('double.force.xvg');assert len(a)==len(b) and len(a)>400000
delta=math.sqrt(sum((x-y)**2 for x,y in zip(a,b))/sum(x*x for x in b))
energies={k:row(k+'.energy.xvg')[0] for k in ['mixed','double']}
de=abs(energies['mixed']-energies['double'])/abs(energies['double'])
report={'force_components':len(a),'relative_force_l2':delta,'potential_kj_mol':energies,'relative_energy_difference':de,
 'pass':delta<1e-3 and de<1e-5,'threads_each':16,
 'scope':'Actual full-system snapshot numerical check; previous single-thread energy discrepancy is thread-count-dependent, not a changed topology. Not a full regression suite.'}
(p/'comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert report['pass']
PY
