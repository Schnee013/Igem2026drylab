load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_v110m_w338q/prepared.pdb", 08_v110m_w338q_ascr18_receptor
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/08-af3-double-mutants/run-01/08_v110m_w338q/ascr18/top1_contacts/top1.sdf", 08_v110m_w338q_ascr18_top1
hide everything, 08_v110m_w338q_ascr18_receptor or 08_v110m_w338q_ascr18_top1
show cartoon, 08_v110m_w338q_ascr18_receptor
color gray70, 08_v110m_w338q_ascr18_receptor
show sticks, 08_v110m_w338q_ascr18_top1
color cyan, 08_v110m_w338q_ascr18_top1
select 08_v110m_w338q_ascr18_contacts, 08_v110m_w338q_ascr18_receptor and chain A and resi 27+28+31+77+80+81+84+110+181+345+364+367+368
show sticks, 08_v110m_w338q_ascr18_contacts
color yellow, 08_v110m_w338q_ascr18_contacts and elem C
label 08_v110m_w338q_ascr18_contacts and name CA, "%s%s" % (resn, resi)
hide everything, (08_v110m_w338q_ascr18_receptor or 08_v110m_w338q_ascr18_top1) and hydro
zoom 08_v110m_w338q_ascr18_top1, 8
