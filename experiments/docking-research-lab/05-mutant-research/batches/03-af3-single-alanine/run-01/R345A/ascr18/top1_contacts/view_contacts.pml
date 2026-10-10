load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/R345A/prepared.pdb", R345A_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/R345A/ascr18/top1_contacts/top1.sdf", R345A_ascr18_top1
hide everything, R345A_ascr18_receptor or R345A_ascr18_top1
show cartoon, R345A_ascr18_receptor
color gray70, R345A_ascr18_receptor
show sticks, R345A_ascr18_top1
color cyan, R345A_ascr18_top1
select R345A_ascr18_contacts, R345A_ascr18_receptor and chain A and resi 27+28+77+84+110+189+338+364+367
show sticks, R345A_ascr18_contacts
color yellow, R345A_ascr18_contacts and elem C
label R345A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (R345A_ascr18_receptor or R345A_ascr18_top1) and hydro
zoom R345A_ascr18_top1, 8
