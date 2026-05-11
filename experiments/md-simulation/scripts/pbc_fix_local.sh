#!/usr/bin/env bash
set -euo pipefail

SYS=${SYS:-chimeric-ste2-gpa1-wt}
BASE=${BASE:-experiments/md-simulation/results/$SYS}
RAW=${RAW:-$BASE/raw}
PROCESSED=${PROCESSED:-$BASE/processed}
GMX=${GMX:-gmx}

mkdir -p "$PROCESSED"

make_protein_ref() {
  local in_pdb="$1"
  local out_pdb="$2"
  python - "$in_pdb" "$out_pdb" <<'PY'
import sys
src, dst = sys.argv[1:3]
serial = 1
with open(src) as f, open(dst, 'w') as out:
    for line in f:
        if line.startswith(('ATOM', 'HETATM')) and line[72:76].strip() in {'PROA', 'PROB'}:
            out.write(f"{line[:6]}{serial:5d}{line[11:]}")
            serial += 1
    out.write('END\n')
PY
}

for rep in 1 2 3; do
  in="$RAW/rep${rep}"
  out="$PROCESSED/rep${rep}"
  mkdir -p "$out"
  echo "[pbc] rep${rep}"

  test -s "$in/prod.tpr"
  test -s "$in/prod.xtc"

  # Production XTC was written with compressed-x-grps = SOLU/Protein, so it
  # contains protein atoms only. Always output Protein; selecting System would
  # mismatch the 263,906-atom TPR against the 14,365-atom trajectory.
  printf "Protein\n" | "$GMX" trjconv -s "$in/prod.tpr" -f "$in/prod.xtc" -o "$out/prod_whole.xtc" -pbc whole
  printf "Protein\nProtein\n" | "$GMX" trjconv -s "$in/prod.tpr" -f "$out/prod_whole.xtc" -o "$out/prod_center.xtc" -center -pbc mol -ur compact
  printf "Backbone\nProtein\n" | "$GMX" trjconv -s "$in/prod.tpr" -f "$out/prod_center.xtc" -o "$out/prod_protein.xtc" -fit rot+trans
  printf "Protein\n" | "$GMX" trjconv -s "$in/prod.tpr" -f "$out/prod_protein.xtc" -o "$out/prod_protein_frame0.pdb" -dump 0

  make_protein_ref "$RAW/shared/step5_input.pdb" "$out/protein_ref.pdb"
  "$GMX" check -f "$out/prod_protein.xtc" > "$out/gmx_check_protein.txt" 2>&1 || {
    cat "$out/gmx_check_protein.txt"
    exit 1
  }
done

echo "[pbc] done: $PROCESSED"
