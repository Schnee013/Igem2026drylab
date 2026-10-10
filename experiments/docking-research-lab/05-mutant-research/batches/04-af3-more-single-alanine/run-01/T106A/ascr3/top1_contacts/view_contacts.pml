load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/T106A/prepared.pdb", T106A_ascr3_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/T106A/ascr3/top1_contacts/top1.sdf", T106A_ascr3_top1
hide everything, T106A_ascr3_receptor or T106A_ascr3_top1
show cartoon, T106A_ascr3_receptor
color gray70, T106A_ascr3_receptor
show sticks, T106A_ascr3_top1
color cyan, T106A_ascr3_top1
select T106A_ascr3_contacts, T106A_ascr3_receptor and chain A and resi 77+80+81+107+110+181+364+367+368
show sticks, T106A_ascr3_contacts
color yellow, T106A_ascr3_contacts and elem C
label T106A_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (T106A_ascr3_receptor or T106A_ascr3_top1) and hydro
zoom T106A_ascr3_top1, 8
