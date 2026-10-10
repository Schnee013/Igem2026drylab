# ASCR18 / TM6 tryptophan contact scenes
#
# Scene switching in PyMOL:
#   scene Gpr2_W338_ASCR18
#   scene Gpr3_W306_ASCR18
#   scene GprC_W388_ASCR18
# or use Scene > Next / Previous.
#
# Dashed lines are representative atom-to-atom distances in contact-positive
# docking poses. They are geometric contact guides, not calculated force vectors.

reinitialize
set retain_order, 1
set auto_zoom, off
bg_color white
set orthoscopic, on
set depth_cue, 0
set fog, 0
set antialias, 2
set cartoon_fancy_helices, 1
set cartoon_smooth_loops, 1
set stick_radius, 0.22
set sphere_scale, 0.24
set dash_width, 3.0
set dash_gap, 0.25
set dash_length, 0.18
set label_size, 18
set label_color, black
set label_outline_color, white
set scene_animation_duration, 0.5

# -----------------------------------------------------------------------------
# Load receptors and the selected ASCR18 pose from each multi-pose SDF.
# PyMOL state 1/3/2 corresponds to ProLIF pose index 0/2/1, respectively.
# -----------------------------------------------------------------------------

load experiments/docking-repro/prepared/final-docking/receptors/af3/pdb/gpr2_twf154_wt/deltaN_aligned/gpr2_twf154_wt_model_2_deltaN1-21_deltaN164-178_aligned.pdb, gpr2
load experiments/docking-repro/results/final-docking/prolif/af3/gpr2_twf154_wt/deltaN_aligned/gpr2_twf154_wt_model_2_deltaN1-21_deltaN164-178_aligned/ligands/ascr18_deprotonated/run_20260823_223248_3240812/poses.sdf, _gpr2_ascr18_all
create gpr2_ascr18, _gpr2_ascr18_all, 1, 1
delete _gpr2_ascr18_all

load experiments/docking-repro/prepared/final-docking/receptors/af3/pdb/gpr3_twf154_wt/deltaN_aligned/gpr3_twf154_wt_model_1_deltaN1-7_deltaN150-163_aligned.pdb, gpr3
load experiments/docking-repro/results/final-docking/prolif/af3/gpr3_twf154_wt/deltaN_aligned/gpr3_twf154_wt_model_1_deltaN1-7_deltaN150-163_aligned/ligands/ascr18_deprotonated/run_20260823_223248_3240812/poses.sdf, _gpr3_ascr18_all
create gpr3_ascr18, _gpr3_ascr18_all, 3, 1
delete _gpr3_ascr18_all

load experiments/docking-repro/prepared/final-docking/receptors/af3/pdb/gprc_wt/wt_aligned/gprc_wt_model_1_aligned.pdb, gprc
load experiments/docking-repro/results/final-docking/prolif/af3/gprc_wt/wt_aligned/gprc_wt_model_1_aligned/ligands/ascr18_deprotonated/run_20260823_223248_3240812/poses.sdf, _gprc_ascr18_all
create gprc_ascr18, _gprc_ascr18_all, 2, 1
delete _gprc_ascr18_all

# Target residues and local pockets.
select gpr2_w338, gpr2 and chain A and resi 338 and resn TRP
select gpr3_w306, gpr3 and chain A and resi 306 and resn TRP
select gprc_w388, gprc and chain A and resi 388 and resn TRP
select gpr2_pocket, byres (gpr2 within 5.0 of gpr2_ascr18)
select gpr3_pocket, byres (gpr3 within 5.0 of gpr3_ascr18)
select gprc_pocket, byres (gprc within 5.0 of gprc_ascr18)

# Representative shortest contact pairs from the ProLIF-positive poses.
# Orange: carbon-carbon contact illustrating the Hydrophobic assignment.
distance gpr2_hydrophobic, (gpr2_w338 and name CZ3), (gpr2_ascr18 and id 10), 5.0, mode=0
distance gpr3_hydrophobic, (gpr3_w306 and name CH2), (gpr3_ascr18 and id 10), 5.0, mode=0
distance gprc_hydrophobic, (gprc_w388 and name CH2), (gprc_ascr18 and id 11), 5.0, mode=0

# Cyan: a short W388-to-ligand oxygen distance illustrating the additional
# ProLIF VdWContact assignment in the selected GprC pose.
distance gprc_vdw_close, (gprc_w388 and name CH2), (gprc_ascr18 and id 12), 5.0, mode=0

set dash_color, orange, gpr2_hydrophobic
set dash_color, orange, gpr3_hydrophobic
set dash_color, orange, gprc_hydrophobic
set dash_color, cyan, gprc_vdw_close

# Scene annotations sit at the ligand centroid.
pseudoatom gpr2_note, selection=gpr2_ascr18, label='ASCR18 | ProLIF Hydrophobic | model 2 pose 0'
pseudoatom gpr3_note, selection=gpr3_ascr18, label='ASCR18 | ProLIF Hydrophobic | model 1 pose 2'
pseudoatom gprc_note, selection=gprc_ascr18, label='ASCR18 | ProLIF Hydrophobic + VdWContact | model 1 pose 1'
set label_position, [0.0, 0.0, 3.0], gpr2_note
set label_position, [0.0, 0.0, 3.0], gpr3_note
set label_position, [0.0, 0.0, 3.0], gprc_note

label (gpr2_w338 and name CA), 'Gpr2 W338'
label (gpr3_w306 and name CA), 'Gpr3 W306'
label (gprc_w388 and name CA), 'GprC W388'

# -----------------------------------------------------------------------------
# Scene 1: Gpr2 W338 / ASCR18
# -----------------------------------------------------------------------------
disable all
enable gpr2
enable gpr2_ascr18
enable gpr2_hydrophobic
enable gpr2_note
hide everything, all
show cartoon, gpr2
show sticks, gpr2_pocket
show sticks, gpr2_w338
show spheres, gpr2_w338 and sidechain
show sticks, gpr2_ascr18
show dashes, gpr2_hydrophobic
show labels, gpr2_note or (gpr2_w338 and name CA)
color gray80, gpr2
color lightblue, gpr2_pocket and not gpr2_w338
color yellow, gpr2_w338
color blue, gpr2_w338 and elem N
color hotpink, gpr2_ascr18 and elem C
color red, gpr2_ascr18 and elem O
color white, gpr2_ascr18 and elem H
orient gpr2_pocket or gpr2_ascr18
zoom gpr2_w338 or gpr2_ascr18, 7.0
scene Gpr2_W338_ASCR18, store

# -----------------------------------------------------------------------------
# Scene 2: Gpr3 W306 / ASCR18
# -----------------------------------------------------------------------------
disable all
enable gpr3
enable gpr3_ascr18
enable gpr3_hydrophobic
enable gpr3_note
hide everything, all
show cartoon, gpr3
show sticks, gpr3_pocket
show sticks, gpr3_w306
show spheres, gpr3_w306 and sidechain
show sticks, gpr3_ascr18
show dashes, gpr3_hydrophobic
show labels, gpr3_note or (gpr3_w306 and name CA)
color gray80, gpr3
color palegreen, gpr3_pocket and not gpr3_w306
color yellow, gpr3_w306
color blue, gpr3_w306 and elem N
color hotpink, gpr3_ascr18 and elem C
color red, gpr3_ascr18 and elem O
color white, gpr3_ascr18 and elem H
orient gpr3_pocket or gpr3_ascr18
zoom gpr3_w306 or gpr3_ascr18, 7.0
scene Gpr3_W306_ASCR18, store

# -----------------------------------------------------------------------------
# Scene 3: GprC W388 / ASCR18
# -----------------------------------------------------------------------------
disable all
enable gprc
enable gprc_ascr18
enable gprc_hydrophobic
enable gprc_vdw_close
enable gprc_note
hide everything, all
show cartoon, gprc
show sticks, gprc_pocket
show sticks, gprc_w388
show spheres, gprc_w388 and sidechain
show sticks, gprc_ascr18
show dashes, gprc_hydrophobic
show dashes, gprc_vdw_close
show labels, gprc_note or (gprc_w388 and name CA)
color gray80, gprc
color wheat, gprc_pocket and not gprc_w388
color yellow, gprc_w388
color blue, gprc_w388 and elem N
color hotpink, gprc_ascr18 and elem C
color red, gprc_ascr18 and elem O
color white, gprc_ascr18 and elem H
orient gprc_pocket or gprc_ascr18
zoom gprc_w388 or gprc_ascr18, 7.0
scene GprC_W388_ASCR18, store

# Start on Gpr2. Use Scene > Next / Previous to compare all three.
scene Gpr2_W338_ASCR18, recall
