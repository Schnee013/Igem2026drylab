# Gpr3 旧 pose 定性复查（Phase 0-A，第 1 次目视）
# 目的：视觉确认 Gpr3 WT 20 pose 贴在 TM 束外侧 groove（与 2026-04-16 量化诊断对应）
#
# 使用方式（Mac 本地）：
#   cd /Users/roy/Documents/drylab
#   conda activate docking        # 或任何含 pymol 的环境
#   pymol experiments/docking-repro/analysis/pymol_gpr3_review/load_gpr3_old_poses.pml
#
# 可选：结束后手动 File → Save Session 到
#   experiments/docking-repro/analysis/pymol_gpr3_review/gpr3_old_poses.pse

reinitialize

# 受体（TM-only，ADFR 准备后的 PDB 形式）
load experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdb, Gpr3_WT

# 四个配体，全部 20 pose
load experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr18/Gpr3_ascr18_poses.pdbqt, ascr18
load experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr1/Gpr3_ascr1_poses.pdbqt, ascr1
load experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr3/Gpr3_ascr3_poses.pdbqt, ascr3
load experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr7/Gpr3_ascr7_poses.pdbqt, ascr7

# 视觉：受体白色半透明卡通；所有 pose 线条，rank 1 单独高亮
hide everything
show cartoon, Gpr3_WT
color grey80, Gpr3_WT
set cartoon_transparency, 0.3, Gpr3_WT

# 所有 pose 作为 lines
show sticks, ascr18 or ascr1 or ascr3 or ascr7
color cyan, ascr18
color magenta, ascr1
color yellow, ascr3
color salmon, ascr7

# rank 1（state 1）更显眼
set all_states, 1
frame 1
set cartoon_side_chain_helper, 0

# 视角：从膜侧面看，能同时看到 TM 束和 pose 偏离方向
orient Gpr3_WT
rotate x, 90
zoom Gpr3_WT, 5

bg_color white
set ray_opaque_background, 0

# 提示：
# - 在 PyMOL 命令栏输入  set state, N  （N=1..20）逐帧检查单个 pose
# - 用  set all_states, 1  显示全部 20 个 pose 的重叠分布
set all_states, 1
