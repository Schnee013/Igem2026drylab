load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_t106v/prepared.pdb", 06_t106v_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/06-af3-supplement-singles/run-01/06_t106v/ascr18/top1_contacts/top1.sdf", 06_t106v_ascr18_top1
hide everything, 06_t106v_ascr18_receptor or 06_t106v_ascr18_top1
show cartoon, 06_t106v_ascr18_receptor
color gray70, 06_t106v_ascr18_receptor
show sticks, 06_t106v_ascr18_top1
color cyan, 06_t106v_ascr18_top1
select 06_t106v_ascr18_contacts, 06_t106v_ascr18_receptor and chain A and resi 31+77+80+81+84+106+107+110+181+185+364+367
show sticks, 06_t106v_ascr18_contacts
color yellow, 06_t106v_ascr18_contacts and elem C
label 06_t106v_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (06_t106v_ascr18_receptor or 06_t106v_ascr18_top1) and hydro
zoom 06_t106v_ascr18_top1, 8
