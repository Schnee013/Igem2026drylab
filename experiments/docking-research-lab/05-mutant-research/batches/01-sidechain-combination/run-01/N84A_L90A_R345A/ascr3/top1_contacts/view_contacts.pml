load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-combination-run01/N84A_L90A_R345A/prepared.pdb", N84A_L90A_R345A_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-combination-run01/N84A_L90A_R345A/ascr3/top1_contacts/top1.sdf", N84A_L90A_R345A_ascr3_top1
hide everything, N84A_L90A_R345A_ascr3_receptor or N84A_L90A_R345A_ascr3_top1
show cartoon, N84A_L90A_R345A_ascr3_receptor
color gray70, N84A_L90A_R345A_ascr3_receptor
show sticks, N84A_L90A_R345A_ascr3_top1
color cyan, N84A_L90A_R345A_ascr3_top1
select N84A_L90A_R345A_ascr3_contacts, N84A_L90A_R345A_ascr3_receptor and chain A and resi 28+31+77+80+81+364+367
show sticks, N84A_L90A_R345A_ascr3_contacts
color yellow, N84A_L90A_R345A_ascr3_contacts and elem C
label N84A_L90A_R345A_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (N84A_L90A_R345A_ascr3_receptor or N84A_L90A_R345A_ascr3_top1) and hydro
zoom N84A_L90A_R345A_ascr3_top1, 8
