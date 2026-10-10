load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/W338A/prepared.pdb", W338A_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/W338A/ascr18/top1_contacts/top1.sdf", W338A_ascr18_top1
hide everything, W338A_ascr18_receptor or W338A_ascr18_top1
show cartoon, W338A_ascr18_receptor
color gray70, W338A_ascr18_receptor
show sticks, W338A_ascr18_top1
color cyan, W338A_ascr18_top1
select W338A_ascr18_contacts, W338A_ascr18_receptor and chain A and resi 24+27+28+31+77+80+81+84+90+181+345+364+367
show sticks, W338A_ascr18_contacts
color yellow, W338A_ascr18_contacts and elem C
label W338A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (W338A_ascr18_receptor or W338A_ascr18_top1) and hydro
zoom W338A_ascr18_top1, 8
