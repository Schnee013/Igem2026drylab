# PyMOL 总览脚本：三受体 + ascr#18 对比
bg_color white
hide everything
load /Users/roy/Documents/drylab/experiments/docking/receptors/Gpr2_G1X9E2.pdb, Gpr2
show cartoon, Gpr2
color slate, Gpr2
load /Users/roy/Documents/drylab/experiments/docking/results/interactions/Gpr2_ascr18_pose0.pdb, Gpr2_ascr18
show sticks, Gpr2_ascr18
color yellow, Gpr2_ascr18
translate [-60, 0, 0], Gpr2
translate [-60, 0, 0], Gpr2_ascr18
load /Users/roy/Documents/drylab/experiments/docking/receptors/Gpr3_G1XJN1.pdb, Gpr3
show cartoon, Gpr3
color marine, Gpr3
load /Users/roy/Documents/drylab/experiments/docking/results/interactions/Gpr3_ascr18_pose0.pdb, Gpr3_ascr18
show sticks, Gpr3_ascr18
color yellow, Gpr3_ascr18
translate [0, 0, 0], Gpr3
translate [0, 0, 0], Gpr3_ascr18
load /Users/roy/Documents/drylab/experiments/docking/receptors/GprC_A0A437AGY2.pdb, GprC
show cartoon, GprC
color teal, GprC
load /Users/roy/Documents/drylab/experiments/docking/results/interactions/GprC_ascr18_pose0.pdb, GprC_ascr18
show sticks, GprC_ascr18
color yellow, GprC_ascr18
translate [60, 0, 0], GprC
translate [60, 0, 0], GprC_ascr18
orient
ray 1800, 600
png /Users/roy/Documents/drylab/experiments/docking/analysis/pymol_scripts/overview_ascr18.png, dpi=150