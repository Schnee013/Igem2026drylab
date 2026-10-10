#!/usr/bin/env bash
# Compare one unchanged minimized snapshot across the two actual binaries.
set -euo pipefail
ROOT=$(cd "$1" && pwd)
OUT="$ROOT/benchmarks/precision_smoke"
mkdir -p "$OUT"
cd "$ROOT/runs/rebuilt_n84v_ascr18"
awk '!/^(integrator|emtol|emstep|nsteps|nstenergy|nstlog)/' em.mdp > "$OUT/point.mdp"
printf 'integrator = md\nnsteps = 0\ndt = 0.001\ncontinuation = yes\nnstenergy = 1\n' >> "$OUT/point.mdp"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for precision in mixed double; do
  if [[ "$precision" == mixed ]]; then
    GMX=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
    MPIARGS=()
  else
    GMX="$ROOT/software/gromacs_double/install/bin/gmx_d"
    MPIARGS=(-ntmpi 1)
  fi
  "$GMX" grompp -f "$OUT/point.mdp" -c em.gro -r ionized.gro -p topol.top -n index.ndx \
    -o "$OUT/$precision.tpr" -po "$OUT/${precision}_mdout.mdp" > "$OUT/${precision}_grompp.log" 2>&1
  "$GMX" mdrun -s "$OUT/$precision.tpr" -rerun em.gro -deffnm "$OUT/$precision" \
    -ntomp 1 "${MPIARGS[@]}" -nb cpu -pme cpu -pin off > "$OUT/${precision}_mdrun.log" 2>&1
  printf 'Potential\n0\n' | "$GMX" energy -f "$OUT/$precision.edr" -o "$OUT/$precision.xvg" > "$OUT/${precision}_energy.log" 2>&1
done
python3 - "$OUT" <<'PY'
import json,sys,math
from pathlib import Path
p=Path(sys.argv[1]);values={}
for precision in ['mixed','double']:
 rows=[l.split() for l in (p/(precision+'.xvg')).read_text().splitlines() if l and not l.startswith(('#','@'))]
 values[precision]=float(rows[-1][1]);assert math.isfinite(values[precision])
relative=abs(values['double']-values['mixed'])/max(1,abs(values['double']))
report={'potential_kj_mol':values,'relative_difference':relative,'pass':relative<1e-5,
        'scope':'single-snapshot numerical compatibility on the actual full topology; not a full GROMACS regression suite'}
(p/'comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert report['pass']
PY
