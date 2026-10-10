# ATCC r3 full-length WT pose review; pearl style adapted from the user reference.
reinitialize
set auto_zoom, off
load receptor/Gpr2_WT_full_length_prepared.pdbqt, receptor_full_length_prepared
hide everything, all
remove solvent
set all_state, 1
bg_color white
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
set_color pearl_grey, [0.85, 0.86, 0.88]
set_color aura_blue, [0.65, 0.85, 0.95]
set_color neon_magenta, [0.95, 0.15, 0.55]
select protein_sele, receptor_full_length_prepared and polymer.protein
show cartoon, protein_sele
color pearl_grey, protein_sele
set cartoon_smooth_loops, 1
set cartoon_fancy_helices, 1
set cartoon_flat_sheets, 0
create protein_cloud, protein_sele
hide everything, protein_cloud
show surface, protein_cloud
color aura_blue, protein_cloud
set transparency, 0.82, protein_cloud
set ray_transparency_contrast, 1.5
set ray_transparency_shadows, 0
select seven_tm, receptor_full_length_prepared and chain A and resi 30-50+62-82+108-128+144-164+186-206+327-347+357-377
show cartoon, seven_tm
color marine, seven_tm
run fixed_search_box.py
pseudoatom fixed_box_center, pos=[-1.589167400,2.409682562,-11.638445843]
hide everything, fixed_box_center
select target_pocket_review_hint, byres (receptor_full_length_prepared within 10.0 of fixed_box_center)
show sticks, target_pocket_review_hint
color wheat, target_pocket_review_hint
load poses/ATCCFLR3-GPR2-ASCR3-P001.pdbqt, ATCCFLR3_GPR2_ASCR3_P001
show sticks, ATCCFLR3_GPR2_ASCR3_P001
show spheres, ATCCFLR3_GPR2_ASCR3_P001
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P001
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P001
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P001
color white, elem O and ATCCFLR3_GPR2_ASCR3_P001
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P001
hide (elem H and ATCCFLR3_GPR2_ASCR3_P001)
disable ATCCFLR3_GPR2_ASCR3_P001
load poses/ATCCFLR3-GPR2-ASCR3-P002.pdbqt, ATCCFLR3_GPR2_ASCR3_P002
show sticks, ATCCFLR3_GPR2_ASCR3_P002
show spheres, ATCCFLR3_GPR2_ASCR3_P002
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P002
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P002
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P002
color white, elem O and ATCCFLR3_GPR2_ASCR3_P002
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P002
hide (elem H and ATCCFLR3_GPR2_ASCR3_P002)
disable ATCCFLR3_GPR2_ASCR3_P002
load poses/ATCCFLR3-GPR2-ASCR3-P003.pdbqt, ATCCFLR3_GPR2_ASCR3_P003
show sticks, ATCCFLR3_GPR2_ASCR3_P003
show spheres, ATCCFLR3_GPR2_ASCR3_P003
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P003
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P003
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P003
color white, elem O and ATCCFLR3_GPR2_ASCR3_P003
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P003
hide (elem H and ATCCFLR3_GPR2_ASCR3_P003)
disable ATCCFLR3_GPR2_ASCR3_P003
load poses/ATCCFLR3-GPR2-ASCR3-P004.pdbqt, ATCCFLR3_GPR2_ASCR3_P004
show sticks, ATCCFLR3_GPR2_ASCR3_P004
show spheres, ATCCFLR3_GPR2_ASCR3_P004
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P004
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P004
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P004
color white, elem O and ATCCFLR3_GPR2_ASCR3_P004
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P004
hide (elem H and ATCCFLR3_GPR2_ASCR3_P004)
disable ATCCFLR3_GPR2_ASCR3_P004
load poses/ATCCFLR3-GPR2-ASCR3-P005.pdbqt, ATCCFLR3_GPR2_ASCR3_P005
show sticks, ATCCFLR3_GPR2_ASCR3_P005
show spheres, ATCCFLR3_GPR2_ASCR3_P005
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P005
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P005
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P005
color white, elem O and ATCCFLR3_GPR2_ASCR3_P005
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P005
hide (elem H and ATCCFLR3_GPR2_ASCR3_P005)
disable ATCCFLR3_GPR2_ASCR3_P005
load poses/ATCCFLR3-GPR2-ASCR3-P006.pdbqt, ATCCFLR3_GPR2_ASCR3_P006
show sticks, ATCCFLR3_GPR2_ASCR3_P006
show spheres, ATCCFLR3_GPR2_ASCR3_P006
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P006
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P006
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P006
color white, elem O and ATCCFLR3_GPR2_ASCR3_P006
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P006
hide (elem H and ATCCFLR3_GPR2_ASCR3_P006)
disable ATCCFLR3_GPR2_ASCR3_P006
load poses/ATCCFLR3-GPR2-ASCR3-P007.pdbqt, ATCCFLR3_GPR2_ASCR3_P007
show sticks, ATCCFLR3_GPR2_ASCR3_P007
show spheres, ATCCFLR3_GPR2_ASCR3_P007
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P007
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P007
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P007
color white, elem O and ATCCFLR3_GPR2_ASCR3_P007
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P007
hide (elem H and ATCCFLR3_GPR2_ASCR3_P007)
disable ATCCFLR3_GPR2_ASCR3_P007
load poses/ATCCFLR3-GPR2-ASCR3-P008.pdbqt, ATCCFLR3_GPR2_ASCR3_P008
show sticks, ATCCFLR3_GPR2_ASCR3_P008
show spheres, ATCCFLR3_GPR2_ASCR3_P008
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P008
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P008
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P008
color white, elem O and ATCCFLR3_GPR2_ASCR3_P008
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P008
hide (elem H and ATCCFLR3_GPR2_ASCR3_P008)
disable ATCCFLR3_GPR2_ASCR3_P008
load poses/ATCCFLR3-GPR2-ASCR3-P009.pdbqt, ATCCFLR3_GPR2_ASCR3_P009
show sticks, ATCCFLR3_GPR2_ASCR3_P009
show spheres, ATCCFLR3_GPR2_ASCR3_P009
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P009
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P009
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P009
color white, elem O and ATCCFLR3_GPR2_ASCR3_P009
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P009
hide (elem H and ATCCFLR3_GPR2_ASCR3_P009)
disable ATCCFLR3_GPR2_ASCR3_P009
load poses/ATCCFLR3-GPR2-ASCR3-P010.pdbqt, ATCCFLR3_GPR2_ASCR3_P010
show sticks, ATCCFLR3_GPR2_ASCR3_P010
show spheres, ATCCFLR3_GPR2_ASCR3_P010
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P010
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P010
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P010
color white, elem O and ATCCFLR3_GPR2_ASCR3_P010
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P010
hide (elem H and ATCCFLR3_GPR2_ASCR3_P010)
disable ATCCFLR3_GPR2_ASCR3_P010
load poses/ATCCFLR3-GPR2-ASCR3-P011.pdbqt, ATCCFLR3_GPR2_ASCR3_P011
show sticks, ATCCFLR3_GPR2_ASCR3_P011
show spheres, ATCCFLR3_GPR2_ASCR3_P011
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P011
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P011
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P011
color white, elem O and ATCCFLR3_GPR2_ASCR3_P011
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P011
hide (elem H and ATCCFLR3_GPR2_ASCR3_P011)
disable ATCCFLR3_GPR2_ASCR3_P011
load poses/ATCCFLR3-GPR2-ASCR3-P012.pdbqt, ATCCFLR3_GPR2_ASCR3_P012
show sticks, ATCCFLR3_GPR2_ASCR3_P012
show spheres, ATCCFLR3_GPR2_ASCR3_P012
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P012
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P012
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P012
color white, elem O and ATCCFLR3_GPR2_ASCR3_P012
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P012
hide (elem H and ATCCFLR3_GPR2_ASCR3_P012)
disable ATCCFLR3_GPR2_ASCR3_P012
load poses/ATCCFLR3-GPR2-ASCR3-P013.pdbqt, ATCCFLR3_GPR2_ASCR3_P013
show sticks, ATCCFLR3_GPR2_ASCR3_P013
show spheres, ATCCFLR3_GPR2_ASCR3_P013
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P013
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P013
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P013
color white, elem O and ATCCFLR3_GPR2_ASCR3_P013
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P013
hide (elem H and ATCCFLR3_GPR2_ASCR3_P013)
disable ATCCFLR3_GPR2_ASCR3_P013
load poses/ATCCFLR3-GPR2-ASCR3-P014.pdbqt, ATCCFLR3_GPR2_ASCR3_P014
show sticks, ATCCFLR3_GPR2_ASCR3_P014
show spheres, ATCCFLR3_GPR2_ASCR3_P014
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P014
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P014
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P014
color white, elem O and ATCCFLR3_GPR2_ASCR3_P014
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P014
hide (elem H and ATCCFLR3_GPR2_ASCR3_P014)
disable ATCCFLR3_GPR2_ASCR3_P014
load poses/ATCCFLR3-GPR2-ASCR3-P015.pdbqt, ATCCFLR3_GPR2_ASCR3_P015
show sticks, ATCCFLR3_GPR2_ASCR3_P015
show spheres, ATCCFLR3_GPR2_ASCR3_P015
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P015
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P015
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P015
color white, elem O and ATCCFLR3_GPR2_ASCR3_P015
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P015
hide (elem H and ATCCFLR3_GPR2_ASCR3_P015)
disable ATCCFLR3_GPR2_ASCR3_P015
load poses/ATCCFLR3-GPR2-ASCR3-P016.pdbqt, ATCCFLR3_GPR2_ASCR3_P016
show sticks, ATCCFLR3_GPR2_ASCR3_P016
show spheres, ATCCFLR3_GPR2_ASCR3_P016
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P016
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P016
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P016
color white, elem O and ATCCFLR3_GPR2_ASCR3_P016
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P016
hide (elem H and ATCCFLR3_GPR2_ASCR3_P016)
disable ATCCFLR3_GPR2_ASCR3_P016
load poses/ATCCFLR3-GPR2-ASCR3-P017.pdbqt, ATCCFLR3_GPR2_ASCR3_P017
show sticks, ATCCFLR3_GPR2_ASCR3_P017
show spheres, ATCCFLR3_GPR2_ASCR3_P017
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P017
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P017
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P017
color white, elem O and ATCCFLR3_GPR2_ASCR3_P017
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P017
hide (elem H and ATCCFLR3_GPR2_ASCR3_P017)
disable ATCCFLR3_GPR2_ASCR3_P017
load poses/ATCCFLR3-GPR2-ASCR3-P018.pdbqt, ATCCFLR3_GPR2_ASCR3_P018
show sticks, ATCCFLR3_GPR2_ASCR3_P018
show spheres, ATCCFLR3_GPR2_ASCR3_P018
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P018
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P018
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P018
color white, elem O and ATCCFLR3_GPR2_ASCR3_P018
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P018
hide (elem H and ATCCFLR3_GPR2_ASCR3_P018)
disable ATCCFLR3_GPR2_ASCR3_P018
load poses/ATCCFLR3-GPR2-ASCR3-P019.pdbqt, ATCCFLR3_GPR2_ASCR3_P019
show sticks, ATCCFLR3_GPR2_ASCR3_P019
show spheres, ATCCFLR3_GPR2_ASCR3_P019
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P019
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P019
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P019
color white, elem O and ATCCFLR3_GPR2_ASCR3_P019
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P019
hide (elem H and ATCCFLR3_GPR2_ASCR3_P019)
disable ATCCFLR3_GPR2_ASCR3_P019
load poses/ATCCFLR3-GPR2-ASCR3-P020.pdbqt, ATCCFLR3_GPR2_ASCR3_P020
show sticks, ATCCFLR3_GPR2_ASCR3_P020
show spheres, ATCCFLR3_GPR2_ASCR3_P020
set stick_radius, 0.15, ATCCFLR3_GPR2_ASCR3_P020
set sphere_scale, 0.32, ATCCFLR3_GPR2_ASCR3_P020
color neon_magenta, elem C and ATCCFLR3_GPR2_ASCR3_P020
color white, elem O and ATCCFLR3_GPR2_ASCR3_P020
color deepblue, elem N and ATCCFLR3_GPR2_ASCR3_P020
hide (elem H and ATCCFLR3_GPR2_ASCR3_P020)
disable ATCCFLR3_GPR2_ASCR3_P020
set stick_quality, 100
set sphere_quality, 4
enable ATCCFLR3_GPR2_ASCR3_P001
zoom seven_tm or ATCCFLR3_GPR2_ASCR3_P001, 8
orient seven_tm
print 'Loaded Gpr2_ascr3: full-length prepared receptor and 20 r3 poses.'
print 'Enable one ATCCFLR3_* pose object at a time and report the stable ID.'
