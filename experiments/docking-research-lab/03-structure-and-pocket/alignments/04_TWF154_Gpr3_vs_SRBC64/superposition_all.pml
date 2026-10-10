#!/usr/bin/env pymol
load /Users/yangruoxi/Projects/Docking-Research-Lab/alignment/alignments/04_TWF154_Gpr3_vs_SRBC64/superposition_all, format=pdb
hide all
show stick
color blue, chain A
color red, chain B
set ray_shadow, 0
set stick_radius, 0.3
set sphere_scale, 0.25
show stick, not polymer
show sphere, not polymer
bg_color white
set transparency=0.2
zoom polymer

