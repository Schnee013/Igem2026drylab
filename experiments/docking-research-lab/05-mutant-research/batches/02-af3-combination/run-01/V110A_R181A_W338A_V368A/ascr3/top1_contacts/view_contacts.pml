load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-af3-combination-run01/V110A_R181A_W338A_V368A/prepared.pdb", V110A_R181A_W338A_V368A_ascr3_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/gpr2-af3-combination-run01/V110A_R181A_W338A_V368A/ascr3/top1_contacts/top1.sdf", V110A_R181A_W338A_V368A_ascr3_top1
hide everything, V110A_R181A_W338A_V368A_ascr3_receptor or V110A_R181A_W338A_V368A_ascr3_top1
show cartoon, V110A_R181A_W338A_V368A_ascr3_receptor
color gray70, V110A_R181A_W338A_V368A_ascr3_receptor
show sticks, V110A_R181A_W338A_V368A_ascr3_top1
color cyan, V110A_R181A_W338A_V368A_ascr3_top1
select V110A_R181A_W338A_V368A_ascr3_contacts, V110A_R181A_W338A_V368A_ascr3_receptor and chain A and resi 31+77+80+110+185+186+364+367
show sticks, V110A_R181A_W338A_V368A_ascr3_contacts
color yellow, V110A_R181A_W338A_V368A_ascr3_contacts and elem C
label V110A_R181A_W338A_V368A_ascr3_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (V110A_R181A_W338A_V368A_ascr3_receptor or V110A_R181A_W338A_V368A_ascr3_top1) and hydro
zoom V110A_R181A_W338A_V368A_ascr3_top1, 8
