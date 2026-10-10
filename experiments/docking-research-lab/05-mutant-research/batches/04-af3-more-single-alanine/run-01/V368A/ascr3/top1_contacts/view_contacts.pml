load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V368A/prepared.pdb", V368A_ascr3_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V368A/ascr3/top1_contacts/top1.sdf", V368A_ascr3_top1
hide everything, V368A_ascr3_receptor or V368A_ascr3_top1
show cartoon, V368A_ascr3_receptor
color gray70, V368A_ascr3_receptor
show sticks, V368A_ascr3_top1
color cyan, V368A_ascr3_top1
select V368A_ascr3_contacts, V368A_ascr3_receptor and chain A and resi 31+77+80+106+107+110+181+364+367
show sticks, V368A_ascr3_contacts
color yellow, V368A_ascr3_contacts and elem C
label V368A_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (V368A_ascr3_receptor or V368A_ascr3_top1) and hydro
zoom V368A_ascr3_top1, 8
