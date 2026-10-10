load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_n84y_v368q/prepared.pdb", 08_n84y_v368q_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_n84y_v368q/ascr18/top1_contacts/top1.sdf", 08_n84y_v368q_ascr18_top1
hide everything, 08_n84y_v368q_ascr18_receptor or 08_n84y_v368q_ascr18_top1
show cartoon, 08_n84y_v368q_ascr18_receptor
color gray70, 08_n84y_v368q_ascr18_receptor
show sticks, 08_n84y_v368q_ascr18_top1
color cyan, 08_n84y_v368q_ascr18_top1
select 08_n84y_v368q_ascr18_contacts, 08_n84y_v368q_ascr18_receptor and chain A and resi 28+31+77+110+189+338+364+367+368
show sticks, 08_n84y_v368q_ascr18_contacts
color yellow, 08_n84y_v368q_ascr18_contacts and elem C
label 08_n84y_v368q_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (08_n84y_v368q_ascr18_receptor or 08_n84y_v368q_ascr18_top1) and hydro
zoom 08_n84y_v368q_ascr18_top1, 8
