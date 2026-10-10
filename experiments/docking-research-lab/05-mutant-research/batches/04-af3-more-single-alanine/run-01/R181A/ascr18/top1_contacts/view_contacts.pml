load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/R181A/prepared.pdb", R181A_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/R181A/ascr18/top1_contacts/top1.sdf", R181A_ascr18_top1
hide everything, R181A_ascr18_receptor or R181A_ascr18_top1
show cartoon, R181A_ascr18_receptor
color gray70, R181A_ascr18_receptor
show sticks, R181A_ascr18_top1
color cyan, R181A_ascr18_top1
select R181A_ascr18_contacts, R181A_ascr18_receptor and chain A and resi 28+31+77+84+90+186+189+338+364+367+368
show sticks, R181A_ascr18_contacts
color yellow, R181A_ascr18_contacts and elem C
label R181A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (R181A_ascr18_receptor or R181A_ascr18_top1) and hydro
zoom R181A_ascr18_top1, 8
