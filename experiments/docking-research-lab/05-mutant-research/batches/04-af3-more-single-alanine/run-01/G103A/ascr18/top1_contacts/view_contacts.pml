load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/G103A/prepared.pdb", G103A_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/G103A/ascr18/top1_contacts/top1.sdf", G103A_ascr18_top1
hide everything, G103A_ascr18_receptor or G103A_ascr18_top1
show cartoon, G103A_ascr18_receptor
color gray70, G103A_ascr18_receptor
show sticks, G103A_ascr18_top1
color cyan, G103A_ascr18_top1
select G103A_ascr18_contacts, G103A_ascr18_receptor and chain A and resi 27+28+31+77+80+90+110+364+367
show sticks, G103A_ascr18_contacts
color yellow, G103A_ascr18_contacts and elem C
label G103A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (G103A_ascr18_receptor or G103A_ascr18_top1) and hydro
zoom G103A_ascr18_top1, 8
