#!/bin/bash
# Full Gpr3 scheme F supplemental docking for D100/R164/R167.

#SBATCH --job-name=gpr3_supp_dock
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --output=gpr3_supplemental_docking_%j.log
#SBATCH --error=gpr3_supplemental_docking_%j.err

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
  --residues Gpr3:100,164,167 \
  --cpu "$VINA_CPU" \
  --out-json 'mutagenesis_results_gpr3_supplemental_f_{run_id}.json' \
  --report-md 'mutagenesis_report_gpr3_supplemental_f_{run_id}.md'
