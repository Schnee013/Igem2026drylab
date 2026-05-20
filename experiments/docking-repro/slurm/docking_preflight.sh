#!/bin/bash
# Slurm preflight for docking-repro supplemental refresh.

#SBATCH --job-name=dock_preflight
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=docking_preflight_%j.log
#SBATCH --error=docking_preflight_%j.err

set -euo pipefail

cd /home/guest/drylab-docking
export PATH="/home/guest/bin:${PATH}"
export PYTHONPATH="/home/guest/drylab-docking/src/modeling/docking-repro:${PYTHONPATH:-}"
if [[ -f experiments/docking-repro/slurm/adfr_env.sh ]]; then
  source experiments/docking-repro/slurm/adfr_env.sh
fi

echo "== Host =="
hostname
date

echo "== Vina =="
/home/guest/bin/vina --version

echo "== ADFR prepare_receptor =="
if command -v prepare_receptor >/dev/null 2>&1; then
  command -v prepare_receptor
elif command -v prepare_receptor4.py >/dev/null 2>&1; then
  command -v prepare_receptor4.py
else
  echo "ERROR: prepare_receptor not found in PATH. Set ADFR_BIN or install ADFR Suite before ADFR prep." >&2
  exit 2
fi

echo "== Python imports =="
python3 - <<'PY'
import importlib

for name in ["yaml", "numpy", "dock", "mutagenesis", "run_adfr_mutants"]:
    importlib.import_module(name)
    print(f"OK {name}")
PY

echo "== Expected project files =="
test -f src/modeling/docking-repro/run_mutagenesis_saturation.py
test -f src/modeling/docking-repro/run_adfr_mutants.py
test -f experiments/docking-repro/prepared/ligands/ascr18_optimized.pdbqt
test -f experiments/docking-repro/prepared/ligands/ascr3_optimized.pdbqt
test -f experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdb
test -f experiments/docking-repro/results/wt_singlestage/docking_results.json
test -f experiments/docking-repro/results/wt_singlestage_gpr3_f_test/docking_results.json
test -f experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_01.json
test -f experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_02.json
test -f experiments/docking-repro/mutagenesis/af3_structures/Gpr3/D100C_tm.pdb

echo "Preflight PASS"
