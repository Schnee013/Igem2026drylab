#!/usr/bin/env bash
# Full-length AF3 prediction, followed by docking-only segment removal.
set -euo pipefail
ROOT="${DOCKING_PROJECT_ROOT:-/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab}"
SRC="$ROOT/vina/src"
HELPER="$ROOT/outputs/batches/04-af3-round2/cli/helpers.py"
TRIM="$ROOT/outputs/batches/02-af3-combination/cli/trim_after_full_length_af3.py"
ARCHIVE="${ROUND2_AF3_ARCHIVE:-$ROOT/vina/inputs/receptors/af3/gpr2_round2_20260911_0054}"
OUT="${ROUND2_AF3_OUT:-$ROOT/outputs/batches/04-af3-round2/run-01}"
PY="${DOCKING_PYTHON:-/Users/yangruoxi/miniconda3/envs/docking/bin/python}"
VINA="${VINA_EXE:-/Users/yangruoxi/miniconda3/envs/docking/bin/vina}"
DATA="$ROOT/projects-done/inputs&outputs-deltaNlid"
REFERENCE="$DATA/inputs/receptors/af3/pdb/gpr2_twf154_wt/deltaN_aligned/gpr2_twf154_wt_model_0_deltaN1-21_deltaN164-178_aligned.pdb"
TM_RANGES=30-50,62-83,101-126,144-163,182-201,326-346,358-380
stage="${1:-help}"
group="${2:-}"
cd "$ROOT"
if [[ "$stage" == unpack ]]; then
  "$PY" "$HELPER" unpack "${ROUND2_AF3_ZIP:-/Users/yangruoxi/Downloads/folds_2026_09_11_00_54.zip}" "$ARCHIVE"
  exit
fi
if [[ "$stage" == compare ]]; then
  "$PY" "$HELPER" compare "$OUT"
  exit
fi
if [[ "$stage" == compare_contacts ]]; then
  "$PY" "$HELPER" compare_contacts "$OUT"
  exit
fi
case "$group" in
  baseline|V110I|V110L|V110T|N84Q|N84S|V368I|V368L|S80A|N102A|G103A|T106A|V368A|L27A|N28A|V110A|R181A|W338A|N84A_V110A_V368A)
    job=$(echo "$group" | tr '[:upper:]' '[:lower:]') ;;
  *) echo 'Usage: bash commands.sh unpack|compare|compare_contacts';
     echo 'Or: bash commands.sh convert|align|prepare|config|dock|contacts GROUP'; exit 2 ;;
esac
d="$OUT/$group"
expected="$ARCHIVE/fasta_full_length/Gpr2_full_length_${group}.fasta"
cif="${ROUND2_AF3_CIF:-$ARCHIVE/original_cif/$job/fold_${job}_model_0.cif}"
request="${ROUND2_AF3_REQUEST:-$ARCHIVE/original_cif/$job/fold_${job}_job_request.json}"
case "$stage" in
  convert)
    mkdir -p "$d"
    "$PY" "$SRC/cif_to_pdb.py" --input-file "$cif" --output-file "$d/raw_model0.pdb"
    "$PY" "$TRIM" --input-pdb "$d/raw_model0.pdb" --expected-fasta "$expected" \
      --job-request "$request" --output-pdb "$d/trimmed.pdb" --report-json "$d/trimming.json"
    ;;
  align)
    "$PY" "$SRC/align_pdb_to_reference.py" \
      --moving-pdb "$d/trimmed.pdb" --reference-pdb "$REFERENCE" \
      --moving-chain A --reference-chain A \
      --moving-ranges "$TM_RANGES" --reference-ranges "$TM_RANGES" \
      --output-pdb "$d/input.pdb" --report-json "$d/alignment.json"
    # Visual overlay for the user; AF3 conformation remains unchanged by rigid alignment.
    printf 'reinitialize\nload "%s", reference\nload "%s", af3\nhide everything\nshow cartoon\ncolor gray70, reference\ncolor cyan, af3\nzoom af3\n' \
      "$REFERENCE" "$d/input.pdb" > "$d/alignment_review.pml"
    ;;
  prepare)
    "$PY" "$SRC/prepare_receptor_pdbqt.py" \
      --receptor-pdb "$d/input.pdb" --output-pdbqt "$d/receptor.pdbqt" \
      --meeko-executable "$PY" --charge-model gasteiger \
      --meeko-arg=-j --meeko-arg="$d/receptor.json" \
      --meeko-arg=--write_pdb --meeko-arg="$d/prepared.pdb" > "$d/preparation.log" 2>&1
    "$PY" "$HELPER" validate "$d/input.pdb" "$d/receptor.pdbqt" "$group"
    "$PY" "$HELPER" validate "$d/input.pdb" "$d/prepared.pdb" "$group"
    ;;
  config)
    for ligand in ascr3 ascr18; do
      mkdir -p "$d/$ligand"
      "$PY" "$SRC/define_vina_box.py" --receptor "$d/receptor.pdbqt" \
        --ligand "$DATA/inputs/ligands/deprotonated-minus1/pdbqt/${ligand}_deprotonated.pdbqt" \
        --center-x 20 --center-y -20 --center-z 5 --size-x 26 --size-y 26 --size-z 26 \
        --exhaustiveness 8 --num-modes 9 --energy-range 3 --seed 1919 --output "$d/$ligand/vina.conf"
    done
    ;;
  dock)
    test -f "$d/trimming.json"
    test -f "$d/alignment.json"
    "$PY" "$HELPER" validate "$d/input.pdb" "$d/receptor.pdbqt" "$group"
    for ligand in ascr3 ascr18; do
      r="$d/$ligand"
      if [[ -e "$r/poses.pdbqt" ]]; then echo "Refusing to overwrite $r/poses.pdbqt" >&2; exit 2; fi
      "$PY" "$SRC/run_vina.py" --vina-executable "$VINA" --config "$r/vina.conf" \
        --output-pdbqt "$r/poses.pdbqt" --stdout-log "$r/vina.stdout.txt" \
        --stderr-log "$r/vina.stderr.txt" --report-json "$r/run.json" \
        --cpu 16 --spacing 0.375 --min-rmsd 1 --max-evals 0
      "$PY" "$SRC/summarize_vina_results.py" --log "$r/vina.stdout.txt" \
        --pose "$r/poses.pdbqt" --output "$r/summary.json"
    done
    printf 'reinitialize\nload "%s", receptor\nload "%s", ascr3\nload "%s", ascr18\nhide everything\nshow cartoon, receptor\nshow sticks, ascr3 or ascr18\ncolor gray70, receptor\ncolor cyan, ascr3\ncolor orange, ascr18\nhide everything, hydro\nset all_states, off\nframe 1\nzoom ascr3 or ascr18, 8\n' \
      "$d/prepared.pdb" "$d/ascr3/poses.pdbqt" "$d/ascr18/poses.pdbqt" > "$d/review.pml"
    ;;
  contacts)
    for ligand in ascr3 ascr18; do
      r="$d/$ligand"
      "$PY" "$SRC/export_ligand_pdbqt_to_sdf.py" --input "$r/poses.pdbqt" \
        --output "$r/poses.sdf" --meeko-python "$PY"
      "$PY" "$HELPER" contacts "$d/receptor.json" "$r/poses.sdf" "$r/ifp"
    done
    ;;
  *) echo "Unknown stage: $stage"; exit 2 ;;
esac
