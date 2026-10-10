load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V368I/prepared.pdb", V368I_ascr3_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V368I/ascr3/top1_contacts/top1.sdf", V368I_ascr3_top1
hide everything, V368I_ascr3_receptor or V368I_ascr3_top1
show cartoon, V368I_ascr3_receptor
color gray70, V368I_ascr3_receptor
show sticks, V368I_ascr3_top1
color cyan, V368I_ascr3_top1
select V368I_ascr3_contacts, V368I_ascr3_receptor and chain A and resi 77+80+106+107+110+181+185+364+367+368
show sticks, V368I_ascr3_contacts
color yellow, V368I_ascr3_contacts and elem C
label V368I_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (V368I_ascr3_receptor or V368I_ascr3_top1) and hydro
zoom V368I_ascr3_top1, 8
