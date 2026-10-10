reinitialize
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84A_V110A_V368A/prepared.pdb", receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84A_V110A_V368A/ascr3/poses.pdbqt", ascr3
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84A_V110A_V368A/ascr18/poses.pdbqt", ascr18
hide everything
show cartoon, receptor
color gray70, receptor
show sticks, ascr3 or ascr18
color cyan, ascr3
color orange, ascr18
select sites, receptor and chain A and resi 27+28+80+81+84+102+103+106+110+181+338+368
show sticks, sites
hide everything, hydro
set all_states, off
frame 1
zoom ascr3 or ascr18, 8
