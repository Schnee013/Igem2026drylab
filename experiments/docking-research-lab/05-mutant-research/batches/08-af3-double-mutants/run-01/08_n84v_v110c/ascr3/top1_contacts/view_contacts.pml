load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_n84v_v110c/prepared.pdb", 08_n84v_v110c_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_n84v_v110c/ascr3/top1_contacts/top1.sdf", 08_n84v_v110c_ascr3_top1
hide everything, 08_n84v_v110c_ascr3_receptor or 08_n84v_v110c_ascr3_top1
show cartoon, 08_n84v_v110c_ascr3_receptor
color gray70, 08_n84v_v110c_ascr3_receptor
show sticks, 08_n84v_v110c_ascr3_top1
color cyan, 08_n84v_v110c_ascr3_top1
select 08_n84v_v110c_ascr3_contacts, 08_n84v_v110c_ascr3_receptor and chain A and resi 31+77+80+81+106+110+181+186+189+338+364+367+368
show sticks, 08_n84v_v110c_ascr3_contacts
color yellow, 08_n84v_v110c_ascr3_contacts and elem C
label 08_n84v_v110c_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (08_n84v_v110c_ascr3_receptor or 08_n84v_v110c_ascr3_top1) and hydro
zoom 08_n84v_v110c_ascr3_top1, 8
