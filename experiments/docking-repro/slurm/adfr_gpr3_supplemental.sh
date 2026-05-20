#!/bin/bash
# Prepare Gpr3 supplemental AF3 TM PDB files with ADFR prepare_receptor.

#SBATCH --job-name=adfr_gpr3_supp
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=adfr_gpr3_supplemental_%j.log
#SBATCH --error=adfr_gpr3_supplemental_%j.err

set -euo pipefail

cd /home/guest/drylab-docking
export PATH="/home/guest/bin:${PATH}"
export PYTHONPATH="/home/guest/drylab-docking/src/modeling/docking-repro:${PYTHONPATH:-}"
if [[ -f experiments/docking-repro/slurm/adfr_env.sh ]]; then
  source experiments/docking-repro/slurm/adfr_env.sh
fi

ADFR_ARGS=()
if [[ -n "${ADFR_BIN:-}" ]]; then
  ADFR_ARGS=(--adfr-bin "$ADFR_BIN")
fi

python3 src/modeling/docking-repro/run_adfr_mutants.py \
  --project-root /home/guest/drylab-docking \
  --job-names-file \
    experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_01.json \
    experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_02.json \
  "${ADFR_ARGS[@]}"
