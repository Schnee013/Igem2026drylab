#!/bin/bash
#SBATCH --job-name=gpr2_sat_rerun
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --output=gpr2_sat_rerun_%j.log
#SBATCH --error=gpr2_sat_rerun_%j.err

# Gpr2 Saturation Scan 重跑 — 用 3D box offset [6.17, 0.65, -7.85]
# M327 × 18 AA + R59 × 18 AA = 36 突变体 × 2 配体 = 72 次对接
# → 设计与执行记录: docs/logs/2026-04-23.md

cd ~/drylab-docking

export PYTHONPATH=~/drylab-docking/src/modeling/docking-repro:${PYTHONPATH:-}
export PATH=~/bin:${PATH}

python3 src/modeling/docking-repro/run_mutagenesis_saturation.py \
    --project-root ~/drylab-docking \
    --receptors Gpr2
