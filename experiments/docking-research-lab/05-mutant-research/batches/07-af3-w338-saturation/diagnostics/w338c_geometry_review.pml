reinitialize
load "/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab/outputs/batches/07-af3-w338-saturation/run-01/07_w338c/input.pdb", w338c
hide everything
show cartoon, w338c
color gray70, w338c
select clash_pair, w338c and chain A and resi 181+345
show sticks, clash_pair
color cyan, clash_pair and elem C
color blue, clash_pair and elem N
distance suspect_contact, w338c and chain A and resi 181 and name NH1, w338c and chain A and resi 345 and name NH1
label clash_pair and name CA, "%s%s" % (resn,resi)
zoom clash_pair, 6
deselect
