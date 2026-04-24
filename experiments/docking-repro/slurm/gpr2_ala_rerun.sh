#!/bin/bash
#SBATCH --job-name=gpr2_ala_rerun
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem=16G
#SBATCH --time=4:00:00
#SBATCH --output=gpr2_ala_rerun_%j.log
#SBATCH --error=gpr2_ala_rerun_%j.err

# Gpr2 Alanine Scan 重跑 — 用 3D box offset [6.17, 0.65, -7.85]
# 旧 scan 基于胞内污染 box，必须重跑
# 10 残基 × 2 配体（ascr18/3）= 20 次对接
# → ~/.claude/plans/charmmgui-membrane-builder-gpr2-icl-vin-whimsical-ripple.md

cd ~/drylab-docking

# mutagenesis.py + run_mutagenesis_alanine.py 需从 src/modeling/docking-repro 加载
export PYTHONPATH=~/drylab-docking/src/modeling/docking-repro:${PYTHONPATH:-}
export PATH=~/bin:${PATH}

python3 src/modeling/docking-repro/run_mutagenesis_alanine.py \
    --project-root ~/drylab-docking \
    --receptors Gpr2
