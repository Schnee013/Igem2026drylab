# -*- coding: utf-8 -*-
# =========================================================================
#  style_detail.pml  —  Top 6 对接结果·细节版样式脚本
# -------------------------------------------------------------------------
#  风格参考：PANGOLINNN《流光珍珠_细节版》（小红书 / bilibili 同名）
#  用途：蛋白-配体复合物对接位点聚焦图
# -------------------------------------------------------------------------
#  用法：
#    1) 在 PyMOL 里手动 load 需要对比的受体和配体 .pdb（从 receptors/ 和
#       ligands/ 选）。典型：
#         load receptors/Gpr3_WT.pdb,    rec_wt
#         load ligands/Gpr3_WT_ascr18.pdb, lig_wt_18
#         load receptors/Gpr3_V138R.pdb, rec_mut
#         load ligands/Gpr3_V138R_ascr18.pdb, lig_mut_18
#       若做结构叠加：align rec_mut, rec_wt （或 cealign）
#    2) @style_detail.pml
#    3) 用鼠标旋到最佳视角后输入 `ray 1600 1200` 高清出图
# =========================================================================

remove solvent
set all_state, 1
bg_color white

# === 1. 写实光影 ===
set ray_opaque_background, on
set ray_trace_mode, 0
set ray_shadows, on
set depth_cue, on
set fog_start, 0.45

set light_count, 8
set ambient, 0.25
set direct, 0.65
set specular, 0.5
set shininess, 45
set antialias, 2
set orthoscopic, on

# === 2. 配色 ===
set_color pearl_grey,        [0.85, 0.86, 0.88]
set_color neon_magenta,      [0.95, 0.15, 0.55]
set_color cloud_pink,        [1.00, 0.85, 0.88]
set_color muted_amber_grey,  [0.60, 0.50, 0.35]

# === 3. 选择集（基于通用选择子，跨对象生效）===
# polymer.protein 自动匹配所有受体对象；organic 自动匹配所有配体对象。
select protein_sele, polymer.protein
select ligand_sele, organic

# ==================== 主体渲染（珍珠银灰 cartoon）====================
hide everything, protein_sele
show cartoon, protein_sele
color pearl_grey, protein_sele

set cartoon_smooth_loops, 1
set cartoon_fancy_helices, 1
set cartoon_flat_sheets, 0
set cartoon_side_chain_helper, 1

# ==================== 配体渲染（霓虹宝石球棍）====================
hide everything, ligand_sele
show sticks, ligand_sele
show spheres, ligand_sele
set stick_radius, 0.15, ligand_sele
set sphere_scale, 0.26, ligand_sele
set stick_quality, 100
set sphere_quality, 100

color neon_magenta, elem C and ligand_sele
color white,        elem O and ligand_sele
color deepblue,     elem N and ligand_sele
hide (elem H and ligand_sele)

# ==================== 氢键候选残基（4Å 极性原子 byres）====================
select prot_polar,        protein_sele and elem O+N+S
select lig_polar,         ligand_sele  and elem O+N+S
select hb_candidate_atoms, prot_polar within 3.6 of lig_polar
select hbond_residues,    byres hb_candidate_atoms

show sticks, hbond_residues
set stick_radius, 0.10, hbond_residues

color muted_amber_grey, elem C and hbond_residues
color red,              elem O and hbond_residues
color blue,             elem N and hbond_residues
color gold,             elem S and hbond_residues
hide sticks, elem H and hbond_residues

# ==================== 氢键虚线 + 距离 ====================
distance hbonds, ligand_sele, protein_sele, 3.5, mode=2
set dash_color, cyan
set dash_radius, 0.12
set dash_gap, 0.25

show labels, hbonds
set label_color, grey40, hbonds
set label_size, 18, hbonds

# ==================== 残基主标签 ====================
label (hbond_residues and name CA), "%s %s" % (resn, resi)
set label_color,    black, hbond_residues
set label_font_id,  7,     hbond_residues
set label_size,     30,    hbond_residues

set label_connector,        on
set label_connector_color,  grey50
set label_connector_width,  2

# ==================== "云朵" 背景 Surface（整体轮廓提示）====================
# 为每个受体对象创建一份高透明表面。遍历 polymer.protein 所在对象
# 生成 {obj}_cloud 副本以便独立透明度。
python
for obj in cmd.get_object_list("polymer.protein"):
    cloud = obj + "_cloud"
    if cloud in cmd.get_object_list():
        cmd.delete(cloud)
    cmd.create(cloud, obj)
    cmd.hide("everything", cloud)
    cmd.show("surface", cloud)
    cmd.set("transparency", 0.90, cloud)
    cmd.color("cloud_pink", cloud)
python end

set ray_transparency_contrast, 1.5
set ray_transparency_shadows,  0

# === 自动聚焦到结合口袋 ===
zoom hbond_residues, buffer=2.0

print ""
print "==== style_detail.pml loaded ============================="
print " · 选择集 protein_sele / ligand_sele / hbond_residues 已建立"
print " · hbonds 为距离虚线对象，可 `disable hbonds` 隐藏"
print " · 每个受体对象生成 {obj}_cloud 透明表面副本"
print " · 输入 `ray 1600 1200` 出图"
print "==========================================================="
