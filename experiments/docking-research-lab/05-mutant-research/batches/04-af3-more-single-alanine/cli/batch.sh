#!/usr/bin/env bash
set -euo pipefail
ROOT="${DOCKING_PROJECT_ROOT:-/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab}"
CLI="$ROOT/outputs/batches/04-af3-round2/cli"
PY="${DOCKING_PYTHON:-/Users/yangruoxi/miniconda3/envs/docking/bin/python}"
OUT="${ROUND2_AF3_OUT:-$ROOT/outputs/batches/04-af3-round2/run-01}"
stage="${1:-help}"
case "$stage" in
  unpack|compare) bash "$CLI/commands.sh" "$stage" ;;
  convert|align|prepare|config|dock|top1)
    groups=$("$PY" "$CLI/helpers.py" groups)
    while IFS= read -r group; do
      echo "[$stage] $group"
      if [[ "$stage" == top1 ]]; then
        for ligand in ascr3 ascr18; do
          "$PY" "$ROOT/outputs/batches/03-af3-single-alanine/cli/top1_contacts.py" --run-dir "$OUT/$group/$ligand"
        done
      else
        bash "$CLI/commands.sh" "$stage" "$group"
      fi
    done <<< "$groups"
    ;;
  *) echo 'Usage: bash batch.sh unpack|convert|align|prepare|config|dock|compare|top1' >&2; exit 2 ;;
esac
