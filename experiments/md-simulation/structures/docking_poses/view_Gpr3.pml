# PyMOL: Gpr3_WT membrane + ascr18 docking pose
# Usage: pymol view_Gpr3.pml

# Load
load ../../systems/Gpr3_WT/gromacs/step5_input.pdb, membrane
load Gpr3_ascr18_model1_aligned.pdb, ascr18

# Hide everything first
hide everything

# Protein cartoon (palegreen)
show cartoon, membrane and polymer
color palegreen, membrane and polymer

# Ligand sticks (yellow)
show sticks, ascr18
color yellow, ascr18
set stick_radius, 0.25, ascr18

# Key mutation residues: VAL138, PHE170, ILE141
select mut_sites, membrane and polymer and (resi 138 or resi 170 or resi 141)
show sticks, mut_sites
color magenta, mut_sites
label mut_sites and name CA, "%s%s" % (resn, resi)

# Clashing POPC resid 113 (red, must delete in Phase 3)
select clash_popc, membrane and resname POPC and resi 113
show sticks, clash_popc
color red, clash_popc

# Other POPC as semi-transparent lines
show lines, membrane and resname POPC and not clash_popc
color gray80, membrane and resname POPC and not clash_popc
set transparency, 0.7, membrane and resname POPC and not clash_popc

# Settings
bg_color white
set ray_shadow, 0

# Center on ligand
center ascr18
zoom ascr18, 15

# NOTE: Red POPC 113 clashes with ligand (0.18 A) — must be deleted before MD
# Ligand centroid Z~95, bilayer center~92 — extracellular half of TM bundle (expected)
