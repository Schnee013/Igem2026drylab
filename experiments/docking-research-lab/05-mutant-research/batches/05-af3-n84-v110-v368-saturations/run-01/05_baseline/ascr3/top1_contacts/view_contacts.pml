load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/05-af3-saturation-combinations/run-01/05_baseline/prepared.pdb", 05_baseline_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/05-af3-saturation-combinations/run-01/05_baseline/ascr3/top1_contacts/top1.sdf", 05_baseline_ascr3_top1
hide everything, 05_baseline_ascr3_receptor or 05_baseline_ascr3_top1
show cartoon, 05_baseline_ascr3_receptor
color gray70, 05_baseline_ascr3_receptor
show sticks, 05_baseline_ascr3_top1
color cyan, 05_baseline_ascr3_top1
select 05_baseline_ascr3_contacts, 05_baseline_ascr3_receptor and chain A and resi 77+80+106+107+110+181+364+367
show sticks, 05_baseline_ascr3_contacts
color yellow, 05_baseline_ascr3_contacts and elem C
label 05_baseline_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (05_baseline_ascr3_receptor or 05_baseline_ascr3_top1) and hydro
zoom 05_baseline_ascr3_top1, 8
