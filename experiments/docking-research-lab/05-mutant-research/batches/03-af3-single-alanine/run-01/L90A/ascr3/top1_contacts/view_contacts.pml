load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/L90A/prepared.pdb", L90A_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-single-af3-run01/L90A/ascr3/top1_contacts/top1.sdf", L90A_ascr3_top1
hide everything, L90A_ascr3_receptor or L90A_ascr3_top1
show cartoon, L90A_ascr3_receptor
color gray70, L90A_ascr3_receptor
show sticks, L90A_ascr3_top1
color cyan, L90A_ascr3_top1
select L90A_ascr3_contacts, L90A_ascr3_receptor and chain A and resi 31+77+80+102+106+181+345+364+367+368
show sticks, L90A_ascr3_contacts
color yellow, L90A_ascr3_contacts and elem C
label L90A_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (L90A_ascr3_receptor or L90A_ascr3_top1) and hydro
zoom L90A_ascr3_top1, 8
