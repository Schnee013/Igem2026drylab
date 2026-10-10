#!/usr/bin/env bash
# Run one explicitly selected stage. No default docking action.
set -euo pipefail
ROOT="${DOCKING_PROJECT_ROOT:-/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab}"
SRC="$ROOT/vina/src"
HELPER="$ROOT/outputs/batches/01-sidechain-combination/cli/helpers.py"
DATA="$ROOT/projects-done/inputs&outputs-deltaNlid"
NAME=gpr2_twf154_wt_model_0_deltaN1-21_deltaN164-178_aligned
BASE="$DATA/inputs/receptors/af3/pdb/gpr2_twf154_wt/deltaN_aligned/$NAME.pdb"
OUT="${GPR2_OUT:-$ROOT/outputs/batches/01-sidechain-combination/run-01}"
PY="${DOCKING_PYTHON:-/Users/yangruoxi/miniconda3/envs/docking/bin/python}"
VINA="${VINA_EXE:-/Users/yangruoxi/miniconda3/envs/docking/bin/vina}"
GROUPS_LIST=(baseline N84A_L90A_R345A V110A_R181A_W338A_V368A)
cd "$ROOT"
case "${1:-help}" in
  prepare)
    "$PY" "$HELPER" build "$BASE" "$OUT"
    for group in "${GROUPS_LIST[@]}"; do
      d="$OUT/$group"
      "$PY" "$SRC/prepare_receptor_pdbqt.py" \
        --receptor-pdb "$d/input.pdb" --output-pdbqt "$d/receptor.pdbqt" \
        --meeko-executable "$PY" --charge-model gasteiger \
        --meeko-arg=-j --meeko-arg="$d/receptor.json" \
        --meeko-arg=--write_pdb --meeko-arg="$d/prepared.pdb" \
        > "$d/preparation.log" 2>&1
      "$PY" "$HELPER" validate "$BASE" "$d/receptor.pdbqt" "$group"
      "$PY" "$HELPER" validate "$BASE" "$d/prepared.pdb" "$group"
      for ligand in ascr3 ascr18; do
        mkdir -p "$d/$ligand"
        "$PY" "$SRC/define_vina_box.py" \
          --receptor "$d/receptor.pdbqt" \
          --ligand "$DATA/inputs/ligands/deprotonated-minus1/pdbqt/${ligand}_deprotonated.pdbqt" \
          --center-x 20 --center-y -20 --center-z 5 \
          --size-x 26 --size-y 26 --size-z 26 \
          --exhaustiveness 8 --num-modes 9 --energy-range 3 --seed 1919 \
          --output "$d/$ligand/vina.conf"
      done
    done
    ;;
  dock)
    "$VINA" --version
    for group in "${GROUPS_LIST[@]}"; do
      "$PY" "$HELPER" validate "$BASE" "$OUT/$group/receptor.pdbqt" "$group"
      for ligand in ascr3 ascr18; do
        d="$OUT/$group/$ligand"
        "$PY" "$SRC/run_vina.py" --vina-executable "$VINA" \
          --config "$d/vina.conf" --output-pdbqt "$d/poses.pdbqt" \
          --stdout-log "$d/vina.stdout.txt" --stderr-log "$d/vina.stderr.txt" \
          --report-json "$d/run.json" --cpu 16 --spacing 0.375 \
          --min-rmsd 1 --max-evals 0
        "$PY" "$SRC/summarize_vina_results.py" \
          --log "$d/vina.stdout.txt" --pose "$d/poses.pdbqt" --output "$d/summary.json"
      done
    done
    "$PY" "$HELPER" compare "$OUT"
    ;;
  contacts)
    for group in "${GROUPS_LIST[@]}"; do
      for ligand in ascr3 ascr18; do
        d="$OUT/$group/$ligand"
        "$PY" "$SRC/export_ligand_pdbqt_to_sdf.py" \
          --input "$d/poses.pdbqt" --output "$d/poses.sdf" --meeko-python "$PY"
        "$PY" "$HELPER" contacts "$OUT/$group/receptor.json" "$d/poses.sdf" "$d/ifp"
      done
    done
    "$PY" "$HELPER" compare_contacts "$OUT"
    ;;
  *)
    echo 'Usage: bash commands.sh prepare|dock|contacts'
    echo 'prepare builds fixed-coordinate alanine variants and prepares all three receptors.'
    echo 'dock explicitly runs six Vina jobs. contacts analyzes their poses.'
    ;;
esac
