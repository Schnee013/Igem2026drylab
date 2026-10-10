load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/05-af3-saturation-combinations/run-01/05_n84a/prepared.pdb", 05_n84a_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/05-af3-saturation-combinations/run-01/05_n84a/ascr3/top1_contacts/top1.sdf", 05_n84a_ascr3_top1
hide everything, 05_n84a_ascr3_receptor or 05_n84a_ascr3_top1
show cartoon, 05_n84a_ascr3_receptor
color gray70, 05_n84a_ascr3_receptor
show sticks, 05_n84a_ascr3_top1
color cyan, 05_n84a_ascr3_top1
select 05_n84a_ascr3_contacts, 05_n84a_ascr3_receptor and chain A and resi 28+31+77+80+181+345+364+367
show sticks, 05_n84a_ascr3_contacts
color yellow, 05_n84a_ascr3_contacts and elem C
label 05_n84a_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (05_n84a_ascr3_receptor or 05_n84a_ascr3_top1) and hydro
zoom 05_n84a_ascr3_top1, 8
