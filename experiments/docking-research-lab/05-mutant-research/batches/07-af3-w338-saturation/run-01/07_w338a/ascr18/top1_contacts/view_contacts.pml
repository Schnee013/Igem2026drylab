load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/07-af3-w338-saturation/run-01/07_w338a/prepared.pdb", 07_w338a_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/07-af3-w338-saturation/run-01/07_w338a/ascr18/top1_contacts/top1.sdf", 07_w338a_ascr18_top1
hide everything, 07_w338a_ascr18_receptor or 07_w338a_ascr18_top1
show cartoon, 07_w338a_ascr18_receptor
color gray70, 07_w338a_ascr18_receptor
show sticks, 07_w338a_ascr18_top1
color cyan, 07_w338a_ascr18_top1
select 07_w338a_ascr18_contacts, 07_w338a_ascr18_receptor and chain A and resi 31+77+80+81+106+107+110+181+185+364+367+368
show sticks, 07_w338a_ascr18_contacts
color yellow, 07_w338a_ascr18_contacts and elem C
label 07_w338a_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (07_w338a_ascr18_receptor or 07_w338a_ascr18_top1) and hydro
zoom 07_w338a_ascr18_top1, 8
