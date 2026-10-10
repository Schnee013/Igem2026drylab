load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/L27A/prepared.pdb", L27A_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/L27A/ascr18/top1_contacts/top1.sdf", L27A_ascr18_top1
hide everything, L27A_ascr18_receptor or L27A_ascr18_top1
show cartoon, L27A_ascr18_receptor
color gray70, L27A_ascr18_receptor
show sticks, L27A_ascr18_top1
color cyan, L27A_ascr18_top1
select L27A_ascr18_contacts, L27A_ascr18_receptor and chain A and resi 31+77+80+81+84+110+181+189+338+364+367
show sticks, L27A_ascr18_contacts
color yellow, L27A_ascr18_contacts and elem C
label L27A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (L27A_ascr18_receptor or L27A_ascr18_top1) and hydro
zoom L27A_ascr18_top1, 8
