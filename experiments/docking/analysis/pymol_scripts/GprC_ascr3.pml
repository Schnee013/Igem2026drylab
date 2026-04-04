# PyMOL 可视化脚本: GprC_ascr3
# 生成自 P0 分子对接 Pipeline

# 加载结构
load /Users/roy/Documents/drylab/experiments/docking/receptors/GprC_A0A437AGY2.pdb, receptor
load /Users/roy/Documents/drylab/experiments/docking/results/interactions/GprC_ascr3_pose0.pdb, ligand

# 外观设置
bg_color white
hide everything
show cartoon, receptor
show sticks, ligand
color slate, receptor
color yellow, ligand

# pLDDT 着色（AlphaFold B-factor）
spectrum b, blue_white_red, receptor, minimum=50, maximum=90

# 显示结合残基
select binding_site, receptor and resi 185+189+42+377+378+109+108+381
show sticks, binding_site
color orange, binding_site

# 标注关键残基
label binding_site and name CA, "%s-%s" % (oneletter, resi)

# 视角设置
orient ligand
zoom ligand, 8

# 显示蛋白表面（半透明）
show surface, receptor
set transparency, 0.7, receptor

# 保存
# save /Users/roy/Documents/drylab/experiments/docking/analysis/pymol_scripts/GprC_ascr3.pse
ray 1200, 900
png /Users/roy/Documents/drylab/experiments/docking/analysis/pymol_scripts/GprC_ascr3.png, dpi=150
