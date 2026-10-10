load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V110I/prepared.pdb", V110I_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V110I/ascr18/top1_contacts/top1.sdf", V110I_ascr18_top1
hide everything, V110I_ascr18_receptor or V110I_ascr18_top1
show cartoon, V110I_ascr18_receptor
color gray70, V110I_ascr18_receptor
show sticks, V110I_ascr18_top1
color cyan, V110I_ascr18_top1
select V110I_ascr18_contacts, V110I_ascr18_receptor and chain A and resi 77+80+81+106+107+110+181+364+367+368
show sticks, V110I_ascr18_contacts
color yellow, V110I_ascr18_contacts and elem C
label V110I_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (V110I_ascr18_receptor or V110I_ascr18_top1) and hydro
zoom V110I_ascr18_top1, 8
