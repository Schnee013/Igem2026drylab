load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_r181q/prepared.pdb", 06_r181q_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_r181q/ascr3/top1_contacts/top1.sdf", 06_r181q_ascr3_top1
hide everything, 06_r181q_ascr3_receptor or 06_r181q_ascr3_top1
show cartoon, 06_r181q_ascr3_receptor
color gray70, 06_r181q_ascr3_receptor
show sticks, 06_r181q_ascr3_top1
color cyan, 06_r181q_ascr3_top1
select 06_r181q_ascr3_contacts, 06_r181q_ascr3_receptor and chain A and resi 24+27+28+31+77+80+81+345+364+367+368
show sticks, 06_r181q_ascr3_contacts
color yellow, 06_r181q_ascr3_contacts and elem C
label 06_r181q_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (06_r181q_ascr3_receptor or 06_r181q_ascr3_top1) and hydro
zoom 06_r181q_ascr3_top1, 8
