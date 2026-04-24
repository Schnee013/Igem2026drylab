#!/usr/bin/env python
"""Analyze all 20 Gpr2 docking poses (3D offset rerun) across 4 ligands.

依赖：
- membrane system: experiments/md-simulation/systems/Gpr2_WT/gromacs/step5_input.pdb
- docking receptor: experiments/docking-repro/prepared/receptors/Gpr2_G1X9E2_tm.pdbqt
- poses: experiments/docking-repro/results/wt_singlestage_gpr2_3d_offset/wt_singlestage/poses/Gpr2_ascr{1,3,7,18}/

调用方式：
    conda activate docking
    python experiments/md-simulation/scripts/analyze_all_gpr2_poses_3doffset.py

产出基线指标（写入 stdout 与同目录 .log，本 plan Phase 0-B 使用）。
"""

from pathlib import Path
import sys

import numpy as np
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

LIGANDS = ("ascr1", "ascr3", "ascr7", "ascr18")
MEMB_PDB = "experiments/md-simulation/systems/Gpr2_WT/gromacs/step5_input.pdb"
DOCK_REC = "experiments/docking-repro/prepared/receptors/Gpr2_G1X9E2_tm.pdbqt"
POSE_TPL = "experiments/docking-repro/results/wt_singlestage_gpr2_3d_offset/wt_singlestage/poses/Gpr2_{lig}/Gpr2_{lig}_poses.pdbqt"


def build_alignment(memb_pdb: str, dock_rec: str):
    """Compute R, t that map docking-receptor frame → membrane-system frame."""
    u_memb = mda.Universe(memb_pdb)
    dock_u = mda.Universe(dock_rec)
    ca_dock = dock_u.select_atoms("name CA")
    ca_memb = u_memb.select_atoms("name CA")
    common = np.intersect1d(ca_dock.resids, ca_memb.resids)
    sel = "resid " + " ".join(str(r) for r in common)
    pd_ = ca_dock.select_atoms(sel).positions.copy()
    pm_ = ca_memb.select_atoms(sel).positions.copy()
    cd, cm = pd_.mean(axis=0), pm_.mean(axis=0)
    H = (pd_ - cd).T @ (pm_ - cm)
    U, S, Vt = np.linalg.svd(H)
    d = np.linalg.det(Vt.T @ U.T)
    R = Vt.T @ np.diag([1, 1, np.sign(d)]) @ U.T
    t = cm - R @ cd
    return u_memb, R, t


def tm_geometry(u_memb):
    """Return (tm_center_xy, lower_z, upper_z)."""
    popc_p = u_memb.select_atoms("resname POPC and name P")
    pz = popc_p.positions[:, 2]
    upper_z = np.median(pz[pz > np.median(pz)])
    lower_z = np.median(pz[pz < np.median(pz)])
    tm_ca = u_memb.select_atoms(
        "protein and name CA and prop z > {} and prop z < {}".format(lower_z, upper_z)
    )
    return tm_ca.positions[:, :2].mean(axis=0), lower_z, upper_z


def analyze_ligand(lig: str, u_memb, R, t, tm_center_xy, radius_75: float):
    prot = u_memb.select_atoms("protein")
    popc_all = u_memb.select_atoms("resname POPC")

    pose_file = POSE_TPL.format(lig=lig)
    if not Path(pose_file).exists():
        print(f"[WARN] missing pose file: {pose_file}")
        return None

    text = Path(pose_file).read_text()
    models = text.split("MODEL ")

    header = "{:>5} {:>7} {:>10} {:>12} {:>9} {:>7} {}".format(
        "Model", "dG", "Dist_axis", "Closer_prot", "Min_POPC", "Z_cent", "Location"
    )
    print(f"\n=== Gpr2_{lig} (3D offset) ===")
    print(header)
    print("-" * 75)

    dist_list = []
    closer_frac = []  # per-model: (closer_prot / n_atoms)
    dg_list = []

    for block in models[1:]:
        lines = block.strip().split("\n")
        model_num = int(lines[0].strip())
        energy_line = [l for l in lines if "VINA RESULT" in l][0]
        dg = float(energy_line.split(":")[1].split()[0])
        atom_lines = [l for l in lines if l.startswith(("ATOM", "HETATM"))]
        coords = []
        for l in atom_lines:
            x, y, z = float(l[30:38]), float(l[38:46]), float(l[46:54])
            pos = R @ np.array([x, y, z]) + t
            coords.append(pos)
        coords = np.array(coords)

        centroid = coords.mean(axis=0)
        dist_axis = float(np.sqrt(np.sum((centroid[:2] - tm_center_xy) ** 2)))
        d_prot = distance_array(coords, prot.positions).min(axis=1)
        d_popc = distance_array(coords, popc_all.positions).min(axis=1)
        closer_prot = int((d_prot < d_popc).sum())
        min_popc = float(d_popc.min())

        if dist_axis < 8:
            loc = "** DEEP **"
        elif dist_axis < radius_75:
            loc = "inside"
        elif dist_axis < radius_75 + 5:
            loc = "peripheral"
        else:
            loc = "OUTSIDE"

        print("{:>5} {:>7.3f} {:>10.1f} {:>8}/{:<3} {:>9.1f} {:>7.1f} {}".format(
            model_num, dg, dist_axis, closer_prot, len(coords), min_popc, centroid[2], loc
        ))
        dist_list.append(dist_axis)
        closer_frac.append(closer_prot / len(coords))
        dg_list.append(dg)

    dist_arr = np.array(dist_list)
    cf_arr = np.array(closer_frac)
    print(f"\nSummary Gpr2_{lig}:")
    print(f"  dist_axis: median={np.median(dist_arr):.2f}  min={dist_arr.min():.2f}  max={dist_arr.max():.2f}")
    print(f"  closer_prot_frac: median={np.median(cf_arr):.2%}  min={cf_arr.min():.2%}  max={cf_arr.max():.2%}")
    print(f"  best_dG: {min(dg_list):.3f}")
    return {
        "ligand": lig,
        "dist_median": float(np.median(dist_arr)),
        "dist_min": float(dist_arr.min()),
        "dist_max": float(dist_arr.max()),
        "closer_median": float(np.median(cf_arr)),
        "closer_min": float(cf_arr.min()),
        "best_dg": float(min(dg_list)),
    }


def main():
    u_memb, R, t = build_alignment(MEMB_PDB, DOCK_REC)
    tm_center_xy, lz, uz = tm_geometry(u_memb)
    tm_ca = u_memb.select_atoms(
        "protein and name CA and prop z > {} and prop z < {}".format(lz, uz)
    )
    radii = np.sqrt(((tm_ca.positions[:, :2] - tm_center_xy) ** 2).sum(axis=1))
    radius_75 = float(np.percentile(radii, 75))

    print(f"TM bundle center XY: ({tm_center_xy[0]:.1f}, {tm_center_xy[1]:.1f})")
    print(f"Bilayer: lower P={lz:.1f}, upper P={uz:.1f}")
    print(f"TM bundle 75th-percentile radius: {radius_75:.2f} Å")

    results = []
    for lig in LIGANDS:
        r = analyze_ligand(lig, u_memb, R, t, tm_center_xy, radius_75)
        if r:
            results.append(r)

    print("\n" + "=" * 80)
    print("Baseline summary (Gpr2 3D offset, used as Phase 0-B reference):")
    print("=" * 80)
    print(f"{'lig':<8} {'dist_med':>10} {'dist_min':>10} {'dist_max':>10} {'closer_med':>12} {'best_dG':>10}")
    for r in results:
        print(f"{r['ligand']:<8} {r['dist_median']:>10.2f} {r['dist_min']:>10.2f} {r['dist_max']:>10.2f} "
              f"{r['closer_median']:>12.2%} {r['best_dg']:>10.3f}")

    all_dist = np.array([r["dist_median"] for r in results])
    all_closer = np.array([r["closer_median"] for r in results])
    print(f"\nOverall (median-of-median): dist={np.median(all_dist):.2f} Å, closer_frac={np.median(all_closer):.2%}")
    print(f"TM 75th-percentile radius for reference: {radius_75:.2f} Å")


if __name__ == "__main__":
    main()
