reinitialize
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-single-af3-run01/R345A/prepared.pdb", receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-single-af3-run01/R345A/ascr3/poses.pdbqt", ascr3
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-single-af3-run01/R345A/ascr18/poses.pdbqt", ascr18
hide everything
show cartoon, receptor
color gray70, receptor
show sticks, ascr3 or ascr18
color cyan, ascr3
color orange, ascr18
select sites, receptor and chain A and resi 84+90+110+181+338+345+368
show sticks, sites
hide everything, hydro
set all_states, off
frame 1
zoom ascr3 or ascr18, 8
