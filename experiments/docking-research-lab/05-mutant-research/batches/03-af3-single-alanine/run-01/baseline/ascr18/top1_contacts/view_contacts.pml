load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-single-af3-run01/baseline/prepared.pdb", baseline_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-single-af3-run01/baseline/ascr18/top1_contacts/top1.sdf", baseline_ascr18_top1
hide everything, baseline_ascr18_receptor or baseline_ascr18_top1
show cartoon, baseline_ascr18_receptor
color gray70, baseline_ascr18_receptor
show sticks, baseline_ascr18_top1
color cyan, baseline_ascr18_top1
select baseline_ascr18_contacts, baseline_ascr18_receptor and chain A and resi 27+28+31+77+110+181+338+364+367
show sticks, baseline_ascr18_contacts
color yellow, baseline_ascr18_contacts and elem C
label baseline_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (baseline_ascr18_receptor or baseline_ascr18_top1) and hydro
zoom baseline_ascr18_top1, 8
