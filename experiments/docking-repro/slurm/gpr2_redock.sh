#!/bin/bash
#SBATCH --job-name=gpr2_redock
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem=16G
#SBATCH --time=2:00:00
#SBATCH --output=gpr2_redock_%j.log
#SBATCH --error=gpr2_redock_%j.err

# Gpr2 WT 重对接 — 3D box offset [6.17, 0.65, -7.85] 修复胞内 pose 问题
# 旧: Z-only +10Å（方向反）→ 新: 10Å × 膜法线在 dock frame [0.617,0.065,-0.785]
# → docs/logs/2026-04-16.md §Gpr2 Docking Pose 朝向验证
# Vina 是 CPU 任务，不需要 GPU；但若只有 gpu 分区可用也可以跑

cd ~/drylab-docking

python3 src/modeling/docking-repro/run_wt_singlestage.py \
    --project-root ~/drylab-docking \
    --vina-bin ~/bin/vina \
    --receptors Gpr2 \
    --ligands ascr18 ascr3 ascr7 ascr1
