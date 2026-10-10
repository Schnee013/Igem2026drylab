load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-single-af3-run01/baseline/prepared.pdb", baseline_ascr3_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-single-af3-run01/baseline/ascr3/top1_contacts/top1.sdf", baseline_ascr3_top1
hide everything, baseline_ascr3_receptor or baseline_ascr3_top1
show cartoon, baseline_ascr3_receptor
color gray70, baseline_ascr3_receptor
show sticks, baseline_ascr3_top1
color cyan, baseline_ascr3_top1
select baseline_ascr3_contacts, baseline_ascr3_receptor and chain A and resi 31+77+80+81+102+103+106+364+367+368
show sticks, baseline_ascr3_contacts
color yellow, baseline_ascr3_contacts and elem C
label baseline_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (baseline_ascr3_receptor or baseline_ascr3_top1) and hydro
zoom baseline_ascr3_top1, 8
