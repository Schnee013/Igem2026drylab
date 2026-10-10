load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84Q/prepared.pdb", N84Q_ascr3_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/N84Q/ascr3/top1_contacts/top1.sdf", N84Q_ascr3_top1
hide everything, N84Q_ascr3_receptor or N84Q_ascr3_top1
show cartoon, N84Q_ascr3_receptor
color gray70, N84Q_ascr3_receptor
show sticks, N84Q_ascr3_top1
color cyan, N84Q_ascr3_top1
select N84Q_ascr3_contacts, N84Q_ascr3_receptor and chain A and resi 31+77+80+81+106+107+110+181+364+367+368
show sticks, N84Q_ascr3_contacts
color yellow, N84Q_ascr3_contacts and elem C
label N84Q_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (N84Q_ascr3_receptor or N84Q_ascr3_top1) and hydro
zoom N84Q_ascr3_top1, 8
