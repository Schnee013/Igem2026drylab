reinitialize
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/projects-done/inputs&outputs-deltaNlid/inputs/receptors/af3/pdb/gpr2_twf154_wt/deltaN_aligned/gpr2_twf154_wt_model_0_deltaN1-21_deltaN164-178_aligned.pdb", reference
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/05-af3-saturation-combinations/run-01/05_n84q/input.pdb", current
hide everything
show cartoon, reference or current
color gray70, reference
color cyan, current
select target_sites, current and chain A and resi 84+110+368
show sticks, target_sites
color yellow, target_sites
label target_sites and name CA, "%s%s" % (resn,resi)
set cartoon_transparency, 0.45, reference
zoom current
