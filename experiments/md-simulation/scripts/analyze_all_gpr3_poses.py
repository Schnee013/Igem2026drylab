#!/usr/bin/env python
"""Analyze all 20 Gpr3_ascr18 docking poses for membrane compatibility."""

import numpy as np
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

# Load membrane system
u_memb = mda.Universe("experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.pdb")
prot = u_memb.select_atoms("protein")
popc_all = u_memb.select_atoms("resname POPC")

# TM bundle geometry
popc_p = u_memb.select_atoms("resname POPC and name P")
pz = popc_p.positions[:, 2]
upper_z = np.median(pz[pz > np.median(pz)])
lower_z = np.median(pz[pz < np.median(pz)])
tm_ca = u_memb.select_atoms(
    "protein and name CA and prop z > {} and prop z < {}".format(lower_z, upper_z)
)
tm_center_xy = tm_ca.positions[:, :2].mean(axis=0)
print("TM bundle center XY: ({:.1f}, {:.1f})".format(*tm_center_xy))
print("Bilayer: lower P={:.1f}, center={:.1f}, upper P={:.1f}".format(
    lower_z, (lower_z + upper_z) / 2, upper_z))

# Compute alignment matrix: docking receptor -> membrane system
dock_rec = mda.Universe("experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdbqt")
ca_dock = dock_rec.select_atoms("name CA")
ca_memb = u_memb.select_atoms("name CA")
common_resids = np.intersect1d(ca_dock.resids, ca_memb.resids)
resid_sel = "resid " + " ".join(str(r) for r in common_resids)
sel_d = ca_dock.select_atoms(resid_sel)
sel_m = ca_memb.select_atoms(resid_sel)
pos_d = sel_d.positions.copy()
pos_m = sel_m.positions.copy()
cd = pos_d.mean(axis=0)
cm = pos_m.mean(axis=0)
H = (pos_d - cd).T @ (pos_m - cm)
U, S, Vt = np.linalg.svd(H)
d = np.linalg.det(Vt.T @ U.T)
R = Vt.T @ np.diag([1, 1, np.sign(d)]) @ U.T
t = cm - R @ cd

# Parse all models
pose_file = "experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr18/Gpr3_ascr18_poses.pdbqt"
with open(pose_file) as f:
    text = f.read()

models = text.split("MODEL ")

header = "{:>5} {:>7} {:>10} {:>12} {:>9} {:>7} {}".format(
    "Model", "dG", "Dist_axis", "Closer_prot", "Min_POPC", "Z_cent", "Location"
)
print("\n" + header)
print("-" * 75)

for block in models[1:]:
    lines = block.strip().split("\n")
    model_num = int(lines[0].strip())

    energy_line = [l for l in lines if "VINA RESULT" in l][0]
    dg = float(energy_line.split(":")[1].split()[0])

    atom_lines = [l for l in lines if l.startswith("ATOM") or l.startswith("HETATM")]
    coords = []
    for l in atom_lines:
        x, y, z = float(l[30:38]), float(l[38:46]), float(l[46:54])
        pos = R @ np.array([x, y, z]) + t
        coords.append(pos)
    coords = np.array(coords)

    centroid = coords.mean(axis=0)
    dist_axis = np.sqrt(np.sum((centroid[:2] - tm_center_xy) ** 2))

    d_prot = distance_array(coords, prot.positions).min(axis=1)
    d_popc = distance_array(coords, popc_all.positions).min(axis=1)
    closer_prot = (d_prot < d_popc).sum()
    min_popc = d_popc.min()

    if dist_axis < 8:
        loc = "** DEEP **"
    elif dist_axis < 13.6:
        loc = "inside"
    elif dist_axis < 18.6:
        loc = "peripheral"
    else:
        loc = "OUTSIDE"

    print("{:>5} {:>7.3f} {:>10.1f} {:>8}/{:<3} {:>9.1f} {:>7.1f} {}".format(
        model_num, dg, dist_axis, closer_prot, len(coords), min_popc, centroid[2], loc
    ))
