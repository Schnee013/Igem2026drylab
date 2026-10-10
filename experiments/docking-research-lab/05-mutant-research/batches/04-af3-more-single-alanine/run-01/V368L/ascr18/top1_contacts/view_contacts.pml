load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V368L/prepared.pdb", V368L_ascr18_receptor
load "/Users/yangruoxi/Projects/Docking-Research-Lab/outputs/gpr2-round2-af3-run01/V368L/ascr18/top1_contacts/top1.sdf", V368L_ascr18_top1
hide everything, V368L_ascr18_receptor or V368L_ascr18_top1
show cartoon, V368L_ascr18_receptor
color gray70, V368L_ascr18_receptor
show sticks, V368L_ascr18_top1
color cyan, V368L_ascr18_top1
select V368L_ascr18_contacts, V368L_ascr18_receptor and chain A and resi 31+77+80+102+106+110+189+338+364+367+368
show sticks, V368L_ascr18_contacts
color yellow, V368L_ascr18_contacts and elem C
label V368L_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (V368L_ascr18_receptor or V368L_ascr18_top1) and hydro
zoom V368L_ascr18_top1, 8
