load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/R181A/prepared.pdb", R181A_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/R181A/ascr3/top1_contacts/top1.sdf", R181A_ascr3_top1
hide everything, R181A_ascr3_receptor or R181A_ascr3_top1
show cartoon, R181A_ascr3_receptor
color gray70, R181A_ascr3_receptor
show sticks, R181A_ascr3_top1
color cyan, R181A_ascr3_top1
select R181A_ascr3_contacts, R181A_ascr3_receptor and chain A and resi 31+77+80+81+110+185+189+338+345+364+367+368
show sticks, R181A_ascr3_contacts
color yellow, R181A_ascr3_contacts and elem C
label R181A_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (R181A_ascr3_receptor or R181A_ascr3_top1) and hydro
zoom R181A_ascr3_top1, 8
