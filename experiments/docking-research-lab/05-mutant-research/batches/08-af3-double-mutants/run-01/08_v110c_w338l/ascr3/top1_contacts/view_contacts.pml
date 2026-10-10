load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_v110c_w338l/prepared.pdb", 08_v110c_w338l_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_v110c_w338l/ascr3/top1_contacts/top1.sdf", 08_v110c_w338l_ascr3_top1
hide everything, 08_v110c_w338l_ascr3_receptor or 08_v110c_w338l_ascr3_top1
show cartoon, 08_v110c_w338l_ascr3_receptor
color gray70, 08_v110c_w338l_ascr3_receptor
show sticks, 08_v110c_w338l_ascr3_top1
color cyan, 08_v110c_w338l_ascr3_top1
select 08_v110c_w338l_ascr3_contacts, 08_v110c_w338l_ascr3_receptor and chain A and resi 27+28+31+77+80+81+84+90+181+345+364+367+368
show sticks, 08_v110c_w338l_ascr3_contacts
color yellow, 08_v110c_w338l_ascr3_contacts and elem C
label 08_v110c_w338l_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (08_v110c_w338l_ascr3_receptor or 08_v110c_w338l_ascr3_top1) and hydro
zoom 08_v110c_w338l_ascr3_top1, 8
