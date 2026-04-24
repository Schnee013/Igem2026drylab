#!/usr/bin/env python
"""Analyze Gpr3 D+ poses (box=40 + extracellular_z_offset, 2026-04-23).

判定阈值（plan Phase 1 §4，对照 Phase 0-B Gpr2 3D offset 基线）：
  - ≥ 15/20 pose 的质心到 TM 中轴 XY 距离 < 7.61 Å  (= Gpr2 基线 6.34 × 1.2)
  - ≥ 15/20 pose closer_prot_frac ≥ 14/26 = 53.8%
  - best ΔG vs 旧 ascr18 (-5.755) 不下跌 > 1.0 kcal/mol

Pose 文件：experiments/docking-repro/results/wt_singlestage_gpr3_dplus_test/poses/
"""

from pathlib import Path
import numpy as np
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

LIGANDS = ("ascr1", "ascr3", "ascr7", "ascr18")
MEMB_PDB = "experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.pdb"
DOCK_REC = "experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdbqt"
POSE_TPL = "experiments/docking-repro/results/wt_singlestage_gpr3_dplus_test/poses/Gpr3_{lig}/Gpr3_{lig}_poses.pdbqt"

GPR2_BASELINE_DIST = 6.34
PASS_DIST_THRESHOLD = GPR2_BASELINE_DIST * 1.2
PASS_CLOSER_FRAC = 14 / 26
PASS_N = 15
OLD_ASCR18_BEST_DG = -5.755


def build_alignment(memb_pdb, dock_rec):
    u_m = mda.Universe(memb_pdb)
    u_d = mda.Universe(dock_rec)
    cd = u_d.select_atoms("name CA"); cm = u_m.select_atoms("name CA")
    common = np.intersect1d(cd.resids, cm.resids)
    sel = "resid " + " ".join(str(r) for r in common)
    pd_ = cd.select_atoms(sel).positions.copy(); pm_ = cm.select_atoms(sel).positions.copy()
    cdc, cmc = pd_.mean(axis=0), pm_.mean(axis=0)
    H = (pd_ - cdc).T @ (pm_ - cmc)
    U, S, Vt = np.linalg.svd(H)
    d = np.linalg.det(Vt.T @ U.T)
    R = Vt.T @ np.diag([1, 1, np.sign(d)]) @ U.T
    t = cmc - R @ cdc
    return u_m, R, t


def tm_geometry(u_memb):
    popc_p = u_memb.select_atoms("resname POPC and name P")
    pz = popc_p.positions[:, 2]
    upper_z = np.median(pz[pz > np.median(pz)])
    lower_z = np.median(pz[pz < np.median(pz)])
    tm_ca = u_memb.select_atoms(
        "protein and name CA and prop z > {} and prop z < {}".format(lower_z, upper_z)
    )
    return tm_ca.positions[:, :2].mean(axis=0), lower_z, upper_z


def analyze(lig, u_m, R, t, tm_xy, radius_75):
    prot = u_m.select_atoms("protein")
    popc = u_m.select_atoms("resname POPC")
    pose_file = POSE_TPL.format(lig=lig)
    text = Path(pose_file).read_text()
    models = text.split("MODEL ")

    print(f"\n=== Gpr3_{lig} (D+: box=40 + offset) ===")
    print("{:>5} {:>7} {:>10} {:>12} {:>9} {:>7} {}".format(
        "Model", "dG", "Dist_axis", "Closer_prot", "Min_POPC", "Z_cent", "Location"
    ))
    print("-" * 75)
    dist_list, cf_list, dg_list, z_list = [], [], [], []
    pass_dist = pass_close = 0
    for block in models[1:]:
        lines = block.strip().split("\n")
        model_num = int(lines[0].strip())
        energy_line = [l for l in lines if "VINA RESULT" in l][0]
        dg = float(energy_line.split(":")[1].split()[0])
        atom_lines = [l for l in lines if l.startswith(("ATOM", "HETATM"))]
        coords = []
        for l in atom_lines:
            x, y, z = float(l[30:38]), float(l[38:46]), float(l[46:54])
            coords.append(R @ np.array([x, y, z]) + t)
        coords = np.array(coords)
        centroid = coords.mean(axis=0)
        dist_axis = float(np.sqrt(np.sum((centroid[:2] - tm_xy) ** 2)))
        d_p = distance_array(coords, prot.positions).min(axis=1)
        d_l = distance_array(coords, popc.positions).min(axis=1)
        closer = int((d_p < d_l).sum())
        min_popc = float(d_l.min())
        if dist_axis < 8:
            loc = "** DEEP **"
        elif dist_axis < radius_75:
            loc = "inside"
        elif dist_axis < radius_75 + 5:
            loc = "peripheral"
        else:
            loc = "OUTSIDE"
        print("{:>5} {:>7.3f} {:>10.1f} {:>8}/{:<3} {:>9.1f} {:>7.1f} {}".format(
            model_num, dg, dist_axis, closer, len(coords), min_popc, centroid[2], loc
        ))
        dist_list.append(dist_axis)
        cf_list.append(closer / len(coords))
        dg_list.append(dg)
        z_list.append(centroid[2])
        if dist_axis < PASS_DIST_THRESHOLD:
            pass_dist += 1
        if closer / len(coords) >= PASS_CLOSER_FRAC:
            pass_close += 1
    return {
        "ligand": lig,
        "dist_median": float(np.median(dist_list)),
        "dist_min": float(min(dist_list)),
        "dist_max": float(max(dist_list)),
        "closer_median": float(np.median(cf_list)),
        "z_median": float(np.median(z_list)),
        "best_dg": float(min(dg_list)),
        "pass_dist": pass_dist,
        "pass_close": pass_close,
        "n": len(dist_list),
    }


def main():
    u_m, R, t = build_alignment(MEMB_PDB, DOCK_REC)
    tm_xy, lz, uz = tm_geometry(u_m)
    tm_ca = u_m.select_atoms(
        "protein and name CA and prop z > {} and prop z < {}".format(lz, uz)
    )
    radii = np.sqrt(((tm_ca.positions[:, :2] - tm_xy) ** 2).sum(axis=1))
    radius_75 = float(np.percentile(radii, 75))
    print(f"TM bundle center XY: ({tm_xy[0]:.1f}, {tm_xy[1]:.1f})")
    print(f"Bilayer: lower P={lz:.1f}, upper P={uz:.1f}")
    print(f"TM bundle 75th-percentile radius: {radius_75:.2f} Å")
    print(f"\nPass 阈值: dist < {PASS_DIST_THRESHOLD:.2f} Å, closer_frac ≥ {PASS_CLOSER_FRAC:.2%}, ≥ {PASS_N}/20 pose")

    results = [analyze(l, u_m, R, t, tm_xy, radius_75) for l in LIGANDS]

    print("\n" + "=" * 100)
    print("Phase D+ 判定表：Gpr3 box=40 + offset vs Phase 0-B Gpr2 基线（7.6 Å / 53.8% / 15/20）")
    print("=" * 100)
    print(f"{'lig':<8} {'dist_med':>9} {'dist_max':>9} {'z_med':>7} {'closer_med':>12} "
          f"{'pass_dist':>10} {'pass_close':>11} {'best_dG':>9} {'verdict':>10}")
    all_pass = True
    for r in results:
        verdict = "PASS" if (r["pass_dist"] >= PASS_N and r["pass_close"] >= PASS_N) else "FAIL"
        if verdict == "FAIL":
            all_pass = False
        print(f"{r['ligand']:<8} {r['dist_median']:>9.2f} {r['dist_max']:>9.2f} "
              f"{r['z_median']:>7.1f} {r['closer_median']:>12.2%} "
              f"{r['pass_dist']:>4}/{r['n']:<4} {r['pass_close']:>5}/{r['n']:<4} "
              f"{r['best_dg']:>9.3f} {verdict:>10}")

    ascr18_new = next(r for r in results if r["ligand"] == "ascr18")
    dg_shift = ascr18_new["best_dg"] - OLD_ASCR18_BEST_DG
    dg_ok = dg_shift < 1.0
    print(f"\nascr18 best ΔG: 新 {ascr18_new['best_dg']:.3f} vs 旧 {OLD_ASCR18_BEST_DG:.3f} "
          f"→ Δ={dg_shift:+.3f}  [{'PASS' if dg_ok else 'FAIL'} (阈值 < +1.0)]")

    all_dist = np.array([r["dist_median"] for r in results])
    all_z = np.array([r["z_median"] for r in results])
    print(f"\n汇总（median-of-median）：dist={np.median(all_dist):.2f} Å, Z={np.median(all_z):.1f}")
    print(f"Gpr2 基线对照: dist=6.34 Å, Z=105-106")
    print(f"Gpr3 upper P=110.4  (Z > 110 为胞外水相)")
    print(f"\n整体判定: {'PASS — 进 Phase 1.5 PyMOL' if (all_pass and dg_ok) else 'FAIL — 触发 Phase 2-Stop'}")


if __name__ == "__main__":
    main()
