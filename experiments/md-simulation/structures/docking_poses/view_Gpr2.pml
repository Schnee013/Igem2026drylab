# PyMOL: Gpr2_WT membrane + 3D-offset redocked poses (4 ligands)
# Usage: cd experiments/md-simulation/structures/docking_poses && pymol view_Gpr2.pml
#
# 2026-04-16: 3D offset redock [6.17, 0.65, -7.85] (Slurm job 6535)
# Kabsch verification: 76/80 poses extracellular (Z~106, bilayer center~87.3)
# Previous Z-only offset was incorrect (dock Z opposes membrane normal, R[2,2]=-0.785)
# -> docs/logs/2026-04-16.md §Gpr2 Docking Pose 朝向验证

# === Load membrane system ===
load ../../systems/Gpr2_WT/gromacs/step5_input.pdb, membrane

# === Load 3D-offset aligned poses (MODEL 1) ===
load Gpr2_ascr18_3doffset_model1_aligned.pdb, ascr18_3d
load Gpr2_ascr3_3doffset_model1_aligned.pdb, ascr3_3d
load Gpr2_ascr7_3doffset_model1_aligned.pdb, ascr7_3d
load Gpr2_ascr1_3doffset_model1_aligned.pdb, ascr1_3d

# Hide everything first
hide everything

# Protein cartoon (lightblue)
show cartoon, membrane and polymer
color lightblue, membrane and polymer

# ascr18 ligand sticks (orange) — dG = -5.811
show sticks, ascr18_3d
color orange, ascr18_3d
set stick_radius, 0.25, ascr18_3d

# ascr3 ligand sticks (cyan) — dG = -5.601
show sticks, ascr3_3d
color cyan, ascr3_3d
set stick_radius, 0.25, ascr3_3d

# ascr7 ligand sticks (green) — dG = -5.515
show sticks, ascr7_3d
color green, ascr7_3d
set stick_radius, 0.25, ascr7_3d

# ascr1 ligand sticks (yellow) — dG = -5.821
show sticks, ascr1_3d
color yellow, ascr1_3d
set stick_radius, 0.25, ascr1_3d

# Key mutation residues: MET327, ARG59, HIS60
select mut_sites, membrane and polymer and (resi 327 or resi 59 or resi 60)
show sticks, mut_sites
color magenta, mut_sites
label mut_sites and name CA, "%s%s" % (resn, resi)

# POPC as semi-transparent lines
show lines, membrane and resname POPC
color gray80, membrane and resname POPC
set transparency, 0.7, membrane and resname POPC

# Hide water/ions
hide everything, membrane and (resname TIP3 or resname SOD or resname CLA or resname POT)

# Settings
bg_color white
set ray_shadow, 0

# Center on ascr18 ligand
center ascr18_3d
zoom ascr18_3d, 20

# === Reference geometry ===
# Lower leaflet P ~ 69.0 A
# Bilayer center  ~ 87.3 A
# Upper leaflet P ~ 105.7 A
# Ligand centroids (Kabsch-aligned, 3D offset):
#   ascr18: Z = 106.1 (EXTRACELL, +18.8 above bilayer center)
#   ascr3:  Z = 106.3 (EXTRACELL, +19.0)
#   ascr7:  Z = 105.7 (EXTRACELL, +18.4)
#   ascr1:  Z = 105.9 (EXTRACELL, +18.5)
# All 4 best poses in upper leaflet region — offset fix confirmed
