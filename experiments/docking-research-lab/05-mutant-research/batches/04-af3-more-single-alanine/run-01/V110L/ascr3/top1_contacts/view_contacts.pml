load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V110L/prepared.pdb", V110L_ascr3_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V110L/ascr3/top1_contacts/top1.sdf", V110L_ascr3_top1
hide everything, V110L_ascr3_receptor or V110L_ascr3_top1
show cartoon, V110L_ascr3_receptor
color gray70, V110L_ascr3_receptor
show sticks, V110L_ascr3_top1
color cyan, V110L_ascr3_top1
select V110L_ascr3_contacts, V110L_ascr3_receptor and chain A and resi 28+31+77+81+90+364+367
show sticks, V110L_ascr3_contacts
color yellow, V110L_ascr3_contacts and elem C
label V110L_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (V110L_ascr3_receptor or V110L_ascr3_top1) and hydro
zoom V110L_ascr3_top1, 8
