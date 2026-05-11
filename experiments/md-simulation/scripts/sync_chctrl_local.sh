#!/usr/bin/env bash
set -euo pipefail

REMOTE=${REMOTE:-guest@10.40.4.5}
REMOTE_BASE=${REMOTE_BASE:-/home/guest/md-simulation/chimeric-ste2-gpa1-wt/gromacs}
OUT=${OUT:-experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw}

mkdir -p "$OUT"/rep{1,2,3} "$OUT/shared"

for rep in 1 2 3; do
  src="$REMOTE:$REMOTE_BASE/prod_rep${rep}"
  dst="$OUT/rep${rep}"
  echo "[sync] rep${rep} -> $dst"
  scp "$src/prod.xtc" "$src/prod.gro" "$src/prod.tpr" "$src/prod.log" "$dst/"
done

echo "[sync] shared topology/input files"
scp "$REMOTE:$REMOTE_BASE/step5_input.gro" \
    "$REMOTE:$REMOTE_BASE/topol.top" \
    "$REMOTE:$REMOTE_BASE/index.ndx" \
    "$OUT/shared/"
if scp "$REMOTE:$REMOTE_BASE/step5_input.pdb" "$OUT/shared/"; then
  :
else
  echo "[sync] remote step5_input.pdb absent; using local CHARMM-GUI copy"
  cp experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step5_input.pdb "$OUT/shared/"
fi
scp -r "$REMOTE:$REMOTE_BASE/toppar" "$OUT/shared/"

echo "[sync] done: $(du -sh "$OUT" | awk '{print $1}') in $OUT"
