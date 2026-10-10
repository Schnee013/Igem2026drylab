load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/V110A/prepared.pdb", V110A_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/V110A/ascr18/top1_contacts/top1.sdf", V110A_ascr18_top1
hide everything, V110A_ascr18_receptor or V110A_ascr18_top1
show cartoon, V110A_ascr18_receptor
color gray70, V110A_ascr18_receptor
show sticks, V110A_ascr18_top1
color cyan, V110A_ascr18_top1
select V110A_ascr18_contacts, V110A_ascr18_receptor and chain A and resi 28+31+77+80+81+90+181+345+364+367+368
show sticks, V110A_ascr18_contacts
color yellow, V110A_ascr18_contacts and elem C
label V110A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (V110A_ascr18_receptor or V110A_ascr18_top1) and hydro
zoom V110A_ascr18_top1, 8
