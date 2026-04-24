#!/usr/bin/env python
"""Analyze Gpr3 box=25 poses across 4 ligands (Phase 1c 验证).

依赖：
- membrane system: experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.pdb
- docking receptor: experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdbqt
- poses: experiments/docking-repro/results/wt_singlestage_gpr3_box25_test/poses/Gpr3_ascr{1,3,7,18}/

判定阈值（plan Phase 1 §4 对照 Phase 0-B Gpr2 3D offset 基线）：
  - 距 TM 中轴 XY 中位数 < 7.6 Å  (= Gpr2 基线 6.34 × 1.2)
  - ≥ 15/20 pose 距中轴 < 7.6 Å
  - ≥ 15/20 pose closer_prot_frac ≥ 14/26 = 53.8%
  - best ΔG vs 旧 Gpr3 ascr18 (-5.755) 不下跌 > 1.0 kcal/mol
"""

from pathlib import Path
import numpy as np
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

LIGANDS = ("ascr1", "ascr3", "ascr7", "ascr18")
MEMB_PDB = "experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.pdb"
DOCK_REC = "experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdbqt"
POSE_TPL = "experiments/docking-repro/results/wt_singlestage_gpr3_box25_test/poses/Gpr3_{lig}/Gpr3_{lig}_poses.pdbqt"

# Phase 0-B Gpr2 基线（log: analyze_all_gpr2_poses_3doffset.log）
GPR2_BASELINE_DIST = 6.34
PASS_DIST_THRESHOLD = GPR2_BASELINE_DIST * 1.2  # 7.6 Å
PASS_CLOSER_FRAC = 14 / 26  # ≥ 14/26 原子离蛋白更近
PASS_N = 15  # ≥ 15/20 pose 满足上述条件

# 旧 Gpr3 ascr18 best ΔG（2026-04-16 记录）
OLD_ASCR18_BEST_DG = -5.755


def build_alignment(memb_pdb, dock_rec):
    u_memb = mda.Universe(memb_pdb)
    dock_u = mda.Universe(dock_rec)
    ca_d = dock_u.select_atoms("name CA")
    ca_m = u_memb.select_atoms("name CA")
    common = np.intersect1d(ca_d.resids, ca_m.resids)
    sel = "resid " + " ".join(str(r) for r in common)
    pd_ = ca_d.select_atoms(sel).positions.copy()
    pm_ = ca_m.select_atoms(sel).positions.copy()
    cd, cm = pd_.mean(axis=0), pm_.mean(axis=0)
    H = (pd_ - cd).T @ (pm_ - cm)
    U, S, Vt = np.linalg.svd(H)
    d = np.linalg.det(Vt.T @ U.T)
    R = Vt.T @ np.diag([1, 1, np.sign(d)]) @ U.T
    t = cm - R @ cd
    return u_memb, R, t


def tm_geometry(u_memb):
    popc_p = u_memb.select_atoms("resname POPC and name P")
    pz = popc_p.positions[:, 2]
    upper_z = np.median(pz[pz > np.median(pz)])
    lower_z = np.median(pz[pz < np.median(pz)])
    tm_ca = u_memb.select_atoms(
        "protein and name CA and prop z > {} and prop z < {}".format(lower_z, upper_z)
    )
    return tm_ca.positions[:, :2].mean(axis=0), lower_z, upper_z


def analyze(lig, u_memb, R, t, tm_xy, radius_75):
    prot = u_memb.select_atoms("protein")
    popc = u_memb.select_atoms("resname POPC")
    pose_file = POSE_TPL.format(lig=lig)
    text = Path(pose_file).read_text()
    models = text.split("MODEL ")

    print(f"\n=== Gpr3_{lig} (box=25) ===")
    print("{:>5} {:>7} {:>10} {:>12} {:>9} {:>7} {}".format(
        "Model", "dG", "Dist_axis", "Closer_prot", "Min_POPC", "Z_cent", "Location"
    ))
    print("-" * 75)

    dist_list, cf_list, dg_list = [], [], []
    pass_dist = 0
    pass_close = 0

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
        "best_dg": float(min(dg_list)),
        "pass_dist": pass_dist,
        "pass_close": pass_close,
        "n": len(dist_list),
    }


def main():
    u_memb, R, t = build_alignment(MEMB_PDB, DOCK_REC)
    tm_xy, lz, uz = tm_geometry(u_memb)
    tm_ca = u_memb.select_atoms(
        "protein and name CA and prop z > {} and prop z < {}".format(lz, uz)
    )
    radii = np.sqrt(((tm_ca.positions[:, :2] - tm_xy) ** 2).sum(axis=1))
    radius_75 = float(np.percentile(radii, 75))

    print(f"TM bundle center XY: ({tm_xy[0]:.1f}, {tm_xy[1]:.1f})")
    print(f"Bilayer: lower P={lz:.1f}, upper P={uz:.1f}")
    print(f"TM bundle 75th-percentile radius: {radius_75:.2f} Å")
    print(f"\nPass 阈值（Phase 0-B Gpr2 基线 × 1.2）：")
    print(f"  dist_axis < {PASS_DIST_THRESHOLD:.2f} Å, closer_frac ≥ {PASS_CLOSER_FRAC:.2%}, ≥ {PASS_N}/20 pose")

    results = [analyze(l, u_memb, R, t, tm_xy, radius_75) for l in LIGANDS]

    print("\n" + "=" * 90)
    print("Phase 1c 判定表：Gpr3 box=25 vs Phase 0-B 基线（7.6 Å / 53.8% / 15/20）")
    print("=" * 90)
    print(f"{'lig':<8} {'dist_med':>10} {'dist_max':>10} {'closer_med':>12} "
          f"{'pass_dist':>10} {'pass_close':>11} {'best_dG':>10} {'verdict':>10}")
    all_pass = True
    for r in results:
        verdict_dist = "PASS" if r["pass_dist"] >= PASS_N else "FAIL"
        verdict_close = "PASS" if r["pass_close"] >= PASS_N else "FAIL"
        verdict = "PASS" if (r["pass_dist"] >= PASS_N and r["pass_close"] >= PASS_N) else "FAIL"
        if verdict == "FAIL":
            all_pass = False
        print(f"{r['ligand']:<8} {r['dist_median']:>10.2f} {r['dist_max']:>10.2f} "
              f"{r['closer_median']:>12.2%} {r['pass_dist']:>4}/{r['n']:<4} "
              f"{r['pass_close']:>5}/{r['n']:<4} {r['best_dg']:>10.3f} {verdict:>10}")

    ascr18_new = next(r for r in results if r["ligand"] == "ascr18")
    dg_shift = ascr18_new["best_dg"] - OLD_ASCR18_BEST_DG
    dg_ok = dg_shift < 1.0  # 不下跌 > 1.0 kcal/mol（下跌=变正）
    print(f"\nascr18 best ΔG: 新 {ascr18_new['best_dg']:.3f} vs 旧 {OLD_ASCR18_BEST_DG:.3f} "
          f"→ Δ={dg_shift:+.3f}  [{'PASS' if dg_ok else 'FAIL'} (阈值 < +1.0)]")

    print(f"\n整体判定: {'PASS — 进 Phase 1.5 PyMOL 复查' if (all_pass and dg_ok) else 'FAIL — 触发 Phase 2-Stop，告知用户'}")


if __name__ == "__main__":
    main()
