# Gpr3 F 方案 pose 定性复查（Phase 1.5，第 2 次目视）
# 方案 F：manual ECL2 center + box=20
# 目的：确认新 pose 深入 ECL2 胞外口袋而非某一侧面
#
# 使用方式（Mac 本地）：
#   cd /Users/roy/Documents/drylab
#   conda activate docking
#   pymol experiments/docking-repro/analysis/pymol_gpr3_review/load_gpr3_f_poses.pml
#
# 可选：File → Save Session 保存到
#   experiments/docking-repro/analysis/pymol_gpr3_review/gpr3_f_poses.pse

reinitialize

# 受体 TM-only
load experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdb, Gpr3_WT

# 4 配体 × 20 pose（F 方案产出，位置在 ECL2 区胞外侧）
load experiments/docking-repro/results/wt_singlestage_gpr3_f_test/poses/Gpr3_ascr18/Gpr3_ascr18_poses.pdbqt, ascr18_F
load experiments/docking-repro/results/wt_singlestage_gpr3_f_test/poses/Gpr3_ascr1/Gpr3_ascr1_poses.pdbqt, ascr1_F
load experiments/docking-repro/results/wt_singlestage_gpr3_f_test/poses/Gpr3_ascr3/Gpr3_ascr3_poses.pdbqt, ascr3_F
load experiments/docking-repro/results/wt_singlestage_gpr3_f_test/poses/Gpr3_ascr7/Gpr3_ascr7_poses.pdbqt, ascr7_F

# 同时加载旧 groove pose 作对比（box=40 旧数据）
load experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr18/Gpr3_ascr18_poses.pdbqt, ascr18_OLD
load experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr3/Gpr3_ascr3_poses.pdbqt, ascr3_OLD

# 受体白色半透明 cartoon
hide everything
show cartoon, Gpr3_WT
color grey80, Gpr3_WT
set cartoon_transparency, 0.3, Gpr3_WT

# ECL2 (150-175) 高亮为橙色 — 这是 F 方案 box center 所在区
select ecl2, Gpr3_WT and resi 150-175
show cartoon, ecl2
color orange, ecl2

# IFP 高频残基（原 scan_residues）高亮为黄色 sticks
select scan_res, Gpr3_WT and resi 93+100+138+141+170+171+175+178
show sticks, scan_res and not name C+N+O
color yellow, scan_res

# F pose 用 cyan sticks
show sticks, ascr18_F or ascr1_F or ascr3_F or ascr7_F
color cyan, ascr18_F or ascr1_F or ascr3_F or ascr7_F

# 旧 groove pose 用 magenta lines（对比用）
show lines, ascr18_OLD or ascr3_OLD
color magenta, ascr18_OLD or ascr3_OLD

set all_states, 1

# 视角：从膜侧面看，容易观察 Z 方向分布
orient Gpr3_WT
rotate x, 90
zoom Gpr3_WT, 5

bg_color white
set ray_opaque_background, 0

# 提示：
# - cyan pose 应聚集在 ECL2（橙色区）附近胞外侧
# - magenta 旧 pose 应在 TM 束外侧/膜内（对比）
# - 用 `set state, N` 逐一看单 pose，`set all_states, 1` 看总分布
