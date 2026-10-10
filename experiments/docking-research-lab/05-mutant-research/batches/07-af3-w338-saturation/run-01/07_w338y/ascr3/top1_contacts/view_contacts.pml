load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/07-af3-w338-saturation/run-01/07_w338y/prepared.pdb", 07_w338y_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/07-af3-w338-saturation/run-01/07_w338y/ascr3/top1_contacts/top1.sdf", 07_w338y_ascr3_top1
hide everything, 07_w338y_ascr3_receptor or 07_w338y_ascr3_top1
show cartoon, 07_w338y_ascr3_receptor
color gray70, 07_w338y_ascr3_receptor
show sticks, 07_w338y_ascr3_top1
color cyan, 07_w338y_ascr3_top1
select 07_w338y_ascr3_contacts, 07_w338y_ascr3_receptor and chain A and resi 31+77+106+107+181+185+364+367
show sticks, 07_w338y_ascr3_contacts
color yellow, 07_w338y_ascr3_contacts and elem C
label 07_w338y_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (07_w338y_ascr3_receptor or 07_w338y_ascr3_top1) and hydro
zoom 07_w338y_ascr3_top1, 8
