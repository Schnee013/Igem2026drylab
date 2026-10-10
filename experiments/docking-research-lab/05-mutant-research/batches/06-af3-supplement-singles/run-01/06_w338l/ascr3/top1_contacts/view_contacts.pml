load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_w338l/prepared.pdb", 06_w338l_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_w338l/ascr3/top1_contacts/top1.sdf", 06_w338l_ascr3_top1
hide everything, 06_w338l_ascr3_receptor or 06_w338l_ascr3_top1
show cartoon, 06_w338l_ascr3_receptor
color gray70, 06_w338l_ascr3_receptor
show sticks, 06_w338l_ascr3_top1
color cyan, 06_w338l_ascr3_top1
select 06_w338l_ascr3_contacts, 06_w338l_ascr3_receptor and chain A and resi 77+80+106+107+110+181+364+367
show sticks, 06_w338l_ascr3_contacts
color yellow, 06_w338l_ascr3_contacts and elem C
label 06_w338l_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (06_w338l_ascr3_receptor or 06_w338l_ascr3_top1) and hydro
zoom 06_w338l_ascr3_top1, 8
