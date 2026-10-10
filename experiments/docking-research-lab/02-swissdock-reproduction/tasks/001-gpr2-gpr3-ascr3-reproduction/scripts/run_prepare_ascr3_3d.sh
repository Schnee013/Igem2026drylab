#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
task_dir=$(dirname "$script_dir")
input_mol="$task_dir/inputs/ligand/ascr3_ChemSpider_17226059_2D.mol"
output_dir="$task_dir/inputs/ligand"
venv_dir="${TMPDIR:-/private/tmp}/ascr3-rdkit-py312"

if command -v python3.12 >/dev/null 2>&1; then
    python312=$(command -v python3.12)
elif [ -x /Users/yangruoxi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 ]; then
    python312=/Users/yangruoxi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
else
    echo "ERROR: Python 3.12 was not found. Run this preparation in Google Colab instead." >&2
    exit 1
fi

if [ ! -x "$venv_dir/bin/python" ]; then
    "$python312" -m venv "$venv_dir"
fi

if ! "$venv_dir/bin/python" -c 'import rdkit' >/dev/null 2>&1; then
    "$venv_dir/bin/python" -m pip install --no-cache-dir rdkit==2026.3.5
fi

"$venv_dir/bin/python" "$script_dir/prepare_ascr3_3d.py" "$input_mol" "$output_dir"
