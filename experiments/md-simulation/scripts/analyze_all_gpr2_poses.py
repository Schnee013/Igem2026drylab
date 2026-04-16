#!/usr/bin/env python
"""
Analyze all 20 Gpr2_ascr18 docking poses for membrane compatibility.

For each Vina pose, applies the Kabsch alignment (docking receptor -> membrane
system), then reports the ligand centroid Z relative to the bilayer center.
Poses with Z_cent >= ~85 and within the TM bundle are candidates for MD.

Dependencies: numpy
Usage: conda run -n docking python analyze_all_gpr2_poses.py
"""

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def parse_ca_from_pdb(path, binary=False):
    """Parse CA atom coords from PDB/PDBQT, returning {resid: (resname, x, y, z)}."""
    if binary:
        with open(path, "rb") as f:
            text = f.read().decode("utf-8", errors="replace")
    else:
        with open(path) as f:
            text = f.read()
    cas = {}
    for line in text.split("\n"):
        if (line.startswith("ATOM") or line.startswith("HETATM")) and len(line) >= 54:
            atom_name = line[12:16].strip()
            if atom_name == "CA":
                try:
                    resid = int(line[22:26].strip())
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    # handle both 3-char and 4-char resname
                    resname = line[17:21].strip()
                    cas[resid] = (resname, x, y, z)
                except ValueError:
                    pass
    return cas


def parse_p_atoms(path):
    """Parse POPC phosphorus atoms. Handles CHARMM 4-char resnames."""
    coords = []
    with open(path) as f:
        for line in f:
            if (line.startswith("ATOM") or line.startswith("HETATM")) and len(line) >= 54:
                # CHARMM-GUI: resname at 17:21 (4-char)
                resname = line[17:21].strip()
                atom_name = line[12:16].strip()
                if resname == "POPC" and atom_name == "P":
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append([x, y, z])
    return np.array(coords)


def parse_protein_ca(path):
    """Parse protein CA atoms within bilayer Z range (TM region)."""
    aa3 = {
        "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
        "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
        "HSD", "HSE", "HSP",
    }
    cas = []
    with open(path) as f:
        for line in f:
            if line.startswith("ATOM") and len(line) >= 54:
                resname = line[17:21].strip()
                atom_name = line[12:16].strip()
                if resname in aa3 and atom_name == "CA":
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    cas.append([x, y, z])
    return np.array(cas)


def kabsch(pos_mobile, pos_ref):
    """Kabsch alignment. Returns R, t such that aligned = R @ mobile + t."""
    cd = pos_mobile.mean(axis=0)
    cm = pos_ref.mean(axis=0)
    H = (pos_mobile - cd).T @ (pos_ref - cm)
    U, S, Vt = np.linalg.svd(H)
    d = np.linalg.det(Vt.T @ U.T)
    R = Vt.T @ np.diag([1, 1, np.sign(d)]) @ U.T
    t = cm - R @ cd
    return R, t


def main():
    memb_pdb = ROOT / "experiments/md-simulation/systems/Gpr2_WT/gromacs/step5_input.pdb"
    dock_rec = ROOT / "experiments/docking-repro/prepared/receptors/Gpr2_G1X9E2_tm.pdbqt"
    pose_file = ROOT / "experiments/docking-repro/results/wt_singlestage/poses/Gpr2_ascr18/Gpr2_ascr18_poses.pdbqt"

    # 1. Membrane geometry
    p_coords = parse_p_atoms(str(memb_pdb))
    pz = p_coords[:, 2]
    med_z = np.median(pz)
    upper_z = np.median(pz[pz > med_z])
    lower_z = np.median(pz[pz < med_z])
    bilayer_center = (lower_z + upper_z) / 2

    protein_ca = parse_protein_ca(str(memb_pdb))
    tm_mask = (protein_ca[:, 2] > lower_z) & (protein_ca[:, 2] < upper_z)
    tm_center_xy = protein_ca[tm_mask, :2].mean(axis=0)

    print(f"Membrane geometry:")
    print(f"  Lower leaflet P = {lower_z:.1f}")
    print(f"  Bilayer center   = {bilayer_center:.1f}")
    print(f"  Upper leaflet P  = {upper_z:.1f}")
    print(f"  TM bundle center XY = ({tm_center_xy[0]:.1f}, {tm_center_xy[1]:.1f})")
    print(f"  Extracellular = Z > {bilayer_center:.1f}")
    print()

    # 2. Kabsch alignment
    dock_cas = parse_ca_from_pdb(str(dock_rec), binary=True)
    memb_cas = parse_ca_from_pdb(str(memb_pdb))
    common = sorted(set(dock_cas.keys()) & set(memb_cas.keys()))
    print(f"Alignment: {len(common)} common CA residues")

    pos_d = np.array([[dock_cas[r][1], dock_cas[r][2], dock_cas[r][3]] for r in common])
    pos_m = np.array([[memb_cas[r][1], memb_cas[r][2], memb_cas[r][3]] for r in common])

    R, t_vec = kabsch(pos_d, pos_m)

    aligned_dock = (R @ pos_d.T).T + t_vec
    rmsd = np.sqrt(np.mean(np.sum((aligned_dock - pos_m) ** 2, axis=1)))
    print(f"Alignment RMSD = {rmsd:.3f} A")
    print()

    # 3. Parse all models
    with open(str(pose_file), "rb") as f:
        text = f.read().decode("utf-8", errors="replace")
    models = text.split("MODEL ")
    n_models = len(models) - 1
    print(f"Total poses: {n_models}")
    print()

    # 4. Analyze each model
    header = f"{'Rank':>4} {'dG':>7} {'RMSD_lb':>8} {'Dist_XY':>8} {'Z_cent':>7} {'dZ':>6} Location"
    print(header)
    print("-" * 75)

    good_poses = []

    for block in models[1:]:
        lines = block.strip().split("\n")
        model_num = int(lines[0].strip())
        energy_line = [l for l in lines if "VINA RESULT" in l][0]
        parts = energy_line.split(":")[1].split()
        dg = float(parts[0])
        rmsd_lb = float(parts[1])

        atom_lines = [l for l in lines if l.startswith("ATOM") or l.startswith("HETATM")]
        coords = []
        for l in atom_lines:
            try:
                x, y, z = float(l[30:38]), float(l[38:46]), float(l[46:54])
                pos = R @ np.array([x, y, z]) + t_vec
                coords.append(pos)
            except ValueError:
                pass
        coords = np.array(coords)
        centroid = coords.mean(axis=0)
        dist_axis = np.sqrt(np.sum((centroid[:2] - tm_center_xy) ** 2))
        dz = centroid[2] - bilayer_center

        # Z classification
        if centroid[2] >= bilayer_center + 5:
            z_loc = "EXTRACELL"
        elif centroid[2] >= bilayer_center:
            z_loc = "near_EC"
        elif centroid[2] >= bilayer_center - 5:
            z_loc = "near_IC"
        else:
            z_loc = "INTRACELL"

        # Lateral position
        if dist_axis < 8:
            lat = "deep-TM"
        elif dist_axis < 14:
            lat = "TM-edge"
        elif dist_axis < 19:
            lat = "periph"
        else:
            lat = "OUTSIDE"

        good = centroid[2] >= 85.0 and dist_axis < 14
        tag = " ** GOOD **" if good else ""
        if good:
            good_poses.append(model_num)

        print(
            f"{model_num:>4} {dg:>7.3f} {rmsd_lb:>8.1f} {dist_axis:>8.1f} "
            f"{centroid[2]:>7.1f} {dz:>+6.1f} {z_loc}/{lat}{tag}"
        )

    print()
    if good_poses:
        print(f"GOOD poses (Z>=85, in TM bundle): {good_poses}")
    else:
        print("WARNING: No poses meet the extracellular + TM criteria (Z>=85, dist_axis<14)")
    print(f"Bilayer center Z = {bilayer_center:.1f}")


if __name__ == "__main__":
    main()
