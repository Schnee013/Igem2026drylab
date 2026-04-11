# -*- coding: utf-8 -*-
# =========================================================================
#  style_overview.pml  —  Top 6 对接结果·全览版样式脚本
# -------------------------------------------------------------------------
#  风格参考：PANGOLINNN《流光珍珠_全览图》（小红书 / bilibili 同名）
#  用途：蛋白整体 + 配体位置的全景图（适合做 banner / 封面）
# -------------------------------------------------------------------------
#  用法：
#    1) 在 PyMOL 里手动 load 受体 + 配体（同 style_detail.pml）
#    2) @style_overview.pml
#    3) 旋到合适角度后 `ray 1600 1200`
# =========================================================================

remove solvent
set all_state, 1
bg_color white

# === 1. 电影级光影 ===
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

# === 2. 配色 ===
set_color pearl_grey,   [0.85, 0.86, 0.88]
set_color aura_blue,    [0.65, 0.85, 0.95]
set_color neon_magenta, [0.95, 0.15, 0.55]

# === 3. 选择集（跨对象通用）===
select protein_sele, polymer.protein
select ligand_sele, organic

# === 4. 蛋白主体：流线珍珠 cartoon ===
hide everything, protein_sele
show cartoon, protein_sele
color pearl_grey, protein_sele

set cartoon_smooth_loops, 1
set cartoon_fancy_helices, 1
set cartoon_flat_sheets, 0

# === 5. 配体：霓虹宝石 ===
hide everything, ligand_sele
show sticks, ligand_sele
show spheres, ligand_sele
set stick_radius, 0.15, ligand_sele
set sphere_scale, 0.32, ligand_sele
set stick_quality, 100
set sphere_quality, 100

color neon_magenta, elem C and ligand_sele
color white,        elem O and ligand_sele
color deepblue,     elem N and ligand_sele
hide (elem H and ligand_sele)

# === 6. 极光水膜云朵 surface ===
# 为每个受体对象创建透明表面副本 {obj}_cloud
python
for obj in cmd.get_object_list("polymer.protein"):
    cloud = obj + "_cloud"
    if cloud in cmd.get_object_list():
        cmd.delete(cloud)
    cmd.create(cloud, obj)
    cmd.hide("everything", cloud)
    cmd.show("surface", cloud)
    cmd.color("aura_blue", cloud)
    cmd.set("transparency", 0.82, cloud)
python end

set ray_transparency_contrast, 1.5
set ray_transparency_shadows,  0

# 自动寻找最佳宏观视角
zoom all, buffer=2.5
orient all

print ""
print "==== style_overview.pml loaded ==========================="
print " · 每个受体对象生成 {obj}_cloud 透明 surface 副本"
print " · `ray 1600 1200` 出图"
print "==========================================================="
