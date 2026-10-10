load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_t106s/prepared.pdb", 06_t106s_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_t106s/ascr18/top1_contacts/top1.sdf", 06_t106s_ascr18_top1
hide everything, 06_t106s_ascr18_receptor or 06_t106s_ascr18_top1
show cartoon, 06_t106s_ascr18_receptor
color gray70, 06_t106s_ascr18_receptor
show sticks, 06_t106s_ascr18_top1
color cyan, 06_t106s_ascr18_top1
select 06_t106s_ascr18_contacts, 06_t106s_ascr18_receptor and chain A and resi 27+28+31+77+84+110+189+338+364+367
show sticks, 06_t106s_ascr18_contacts
color yellow, 06_t106s_ascr18_contacts and elem C
label 06_t106s_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (06_t106s_ascr18_receptor or 06_t106s_ascr18_top1) and hydro
zoom 06_t106s_ascr18_top1, 8
