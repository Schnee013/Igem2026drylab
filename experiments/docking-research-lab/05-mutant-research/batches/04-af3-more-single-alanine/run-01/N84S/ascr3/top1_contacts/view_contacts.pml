load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84S/prepared.pdb", N84S_ascr3_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84S/ascr3/top1_contacts/top1.sdf", N84S_ascr3_top1
hide everything, N84S_ascr3_receptor or N84S_ascr3_top1
show cartoon, N84S_ascr3_receptor
color gray70, N84S_ascr3_receptor
show sticks, N84S_ascr3_top1
color cyan, N84S_ascr3_top1
select N84S_ascr3_contacts, N84S_ascr3_receptor and chain A and resi 77+80+81+106+107+110+181+185+186+364+367
show sticks, N84S_ascr3_contacts
color yellow, N84S_ascr3_contacts and elem C
label N84S_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (N84S_ascr3_receptor or N84S_ascr3_top1) and hydro
zoom N84S_ascr3_top1, 8
