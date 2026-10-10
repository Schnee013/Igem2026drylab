load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N102A/prepared.pdb", N102A_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N102A/ascr18/top1_contacts/top1.sdf", N102A_ascr18_top1
hide everything, N102A_ascr18_receptor or N102A_ascr18_top1
show cartoon, N102A_ascr18_receptor
color gray70, N102A_ascr18_receptor
show sticks, N102A_ascr18_top1
color cyan, N102A_ascr18_top1
select N102A_ascr18_contacts, N102A_ascr18_receptor and chain A and resi 77+80+106+181+364+367+368
show sticks, N102A_ascr18_contacts
color yellow, N102A_ascr18_contacts and elem C
label N102A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (N102A_ascr18_receptor or N102A_ascr18_top1) and hydro
zoom N102A_ascr18_top1, 8
