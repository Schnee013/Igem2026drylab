#!/bin/bash
# One-mutant smoke test for Gpr3 scheme F supplemental docking.

#SBATCH --job-name=gpr3_supp_smoke
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=gpr3_supplemental_smoke_%j.log
#SBATCH --error=gpr3_supplemental_smoke_%j.err

set -euo pipefail

cd /home/guest/drylab-docking
export PATH="/home/guest/bin:${PATH}"
export PYTHONPATH="/home/guest/drylab-docking/src/modeling/docking-repro:${PYTHONPATH:-}"
export VINA_CPU="${SLURM_CPUS_PER_TASK:-8}"

python3 src/modeling/docking-repro/run_mutagenesis_saturation.py \
  --project-root /home/guest/drylab-docking \
  --vina-bin /home/guest/bin/vina \
  --wt-baseline-subdir wt_singlestage_gpr3_f_test \
  --receptors Gpr3 \
  --mutations Gpr3:D100C \
  --cpu "$VINA_CPU" \
  --out-json 'mutagenesis_results_gpr3_supplemental_smoke_{run_id}.json' \
  --report-md 'mutagenesis_report_gpr3_supplemental_smoke_{run_id}.md'
