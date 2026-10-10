load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/S80A/prepared.pdb", S80A_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/S80A/ascr18/top1_contacts/top1.sdf", S80A_ascr18_top1
hide everything, S80A_ascr18_receptor or S80A_ascr18_top1
show cartoon, S80A_ascr18_receptor
color gray70, S80A_ascr18_receptor
show sticks, S80A_ascr18_top1
color cyan, S80A_ascr18_top1
select S80A_ascr18_contacts, S80A_ascr18_receptor and chain A and resi 31+77+80+102+106+110+189+338+364+367
show sticks, S80A_ascr18_contacts
color yellow, S80A_ascr18_contacts and elem C
label S80A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (S80A_ascr18_receptor or S80A_ascr18_top1) and hydro
zoom S80A_ascr18_top1, 8
