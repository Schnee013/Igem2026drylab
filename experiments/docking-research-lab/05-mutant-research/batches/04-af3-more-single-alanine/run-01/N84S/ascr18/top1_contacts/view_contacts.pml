load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84S/prepared.pdb", N84S_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84S/ascr18/top1_contacts/top1.sdf", N84S_ascr18_top1
hide everything, N84S_ascr18_receptor or N84S_ascr18_top1
show cartoon, N84S_ascr18_receptor
color gray70, N84S_ascr18_receptor
show sticks, N84S_ascr18_top1
color cyan, N84S_ascr18_top1
select N84S_ascr18_contacts, N84S_ascr18_receptor and chain A and resi 31+77+81+106+181+186+364+367+368
show sticks, N84S_ascr18_contacts
color yellow, N84S_ascr18_contacts and elem C
label N84S_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (N84S_ascr18_receptor or N84S_ascr18_top1) and hydro
zoom N84S_ascr18_top1, 8
