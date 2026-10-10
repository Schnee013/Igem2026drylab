load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N28A/prepared.pdb", N28A_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N28A/ascr18/top1_contacts/top1.sdf", N28A_ascr18_top1
hide everything, N28A_ascr18_receptor or N28A_ascr18_top1
show cartoon, N28A_ascr18_receptor
color gray70, N28A_ascr18_receptor
show sticks, N28A_ascr18_top1
color cyan, N28A_ascr18_top1
select N28A_ascr18_contacts, N28A_ascr18_receptor and chain A and resi 31+77+80+84+106+107+110+181+185+186+364+367+368
show sticks, N28A_ascr18_contacts
color yellow, N28A_ascr18_contacts and elem C
label N28A_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (N28A_ascr18_receptor or N28A_ascr18_top1) and hydro
zoom N28A_ascr18_top1, 8
