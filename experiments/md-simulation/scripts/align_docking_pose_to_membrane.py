#!/usr/bin/env python
"""
Align docking top poses into membrane system coordinate frame.

Workflow:
1. Extract MODEL 1 (top pose) from Vina multi-model PDBQT
2. Convert PDBQT → PDB via Open Babel
3. Superimpose docking receptor onto membrane receptor (CA backbone)
4. Apply the same rotation+translation to ligand coordinates
5. Write aligned ligand PDB

Dependencies: MDAnalysis, numpy, Open Babel CLI (obabel)
Usage: conda run -n docking python align_docking_pose_to_membrane.py

Input/output paths → see SYSTEMS dict below.
"""

import subprocess
import tempfile
from pathlib import Path

import MDAnalysis as mda
import numpy as np
from MDAnalysis.analysis import align

# ── project root ──
ROOT = Path(__file__).resolve().parents[3]  # experiments/md-simulation/scripts/../../../

# ── system definitions ──
SYSTEMS = {
    "Gpr2_ascr18": {
        "pose_pdbqt": ROOT / "experiments/docking-repro/results/wt_singlestage_gpr2_redock/poses/Gpr2_ascr18/Gpr2_ascr18_poses.pdbqt",
        "dock_receptor": ROOT / "experiments/docking-repro/prepared/receptors/Gpr2_G1X9E2_tm.pdbqt",
        "membrane_pdb": ROOT / "experiments/md-simulation/systems/Gpr2_WT/gromacs/step5_input.pdb",
    },
    "Gpr2_ascr3": {
        "pose_pdbqt": ROOT / "experiments/docking-repro/results/wt_singlestage_gpr2_redock/poses/Gpr2_ascr3/Gpr2_ascr3_poses.pdbqt",
        "dock_receptor": ROOT / "experiments/docking-repro/prepared/receptors/Gpr2_G1X9E2_tm.pdbqt",
        "membrane_pdb": ROOT / "experiments/md-simulation/systems/Gpr2_WT/gromacs/step5_input.pdb",
    },
    "Gpr3_ascr18": {
        "pose_pdbqt": ROOT / "experiments/docking-repro/results/wt_singlestage/poses/Gpr3_ascr18/Gpr3_ascr18_poses.pdbqt",
        "dock_receptor": ROOT / "experiments/docking-repro/prepared/receptors/Gpr3_G1XJN1_tm.pdbqt",
        "membrane_pdb": ROOT / "experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.pdb",
    },
}

OUTDIR = ROOT / "experiments/md-simulation/structures/docking_poses"


def extract_model1(pdbqt_path: Path, out_path: Path) -> None:
    """Extract MODEL 1 block from multi-model PDBQT file."""
    lines = []
    inside = False
    with open(pdbqt_path) as fh:
        for line in fh:
            if line.startswith("MODEL") and line.split()[1] == "1":
                inside = True
                continue
            if inside and line.startswith("ENDMDL"):
                break
            if inside:
                lines.append(line)
    out_path.write_text("".join(lines))
    print(f"  Extracted MODEL 1 → {out_path.name} ({len(lines)} lines)")


def pdbqt_to_pdb(pdbqt_path: Path, pdb_path: Path) -> None:
    """Convert PDBQT to PDB using Open Babel."""
    result = subprocess.run(
        ["obabel", "-ipdbqt", str(pdbqt_path), "-opdb", "-O", str(pdb_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"obabel failed: {result.stderr}")
    print(f"  PDBQT → PDB: {pdb_path.name}")


def compute_alignment(dock_receptor_path: Path, membrane_pdb_path: Path):
    """
    Compute rotation matrix R and translation t that maps
    docking-receptor CA coords → membrane-system CA coords.

    Returns (R, t, rmsd, n_atoms) where new_pos = R @ old_pos + t.
    """
    u_dock = mda.Universe(str(dock_receptor_path))
    u_memb = mda.Universe(str(membrane_pdb_path))

    ca_dock = u_dock.select_atoms("name CA")
    ca_memb = u_memb.select_atoms("name CA")

    # find common residue IDs
    common_resids = np.intersect1d(ca_dock.resids, ca_memb.resids)
    assert len(common_resids) > 0, "No common residues found!"

    # build resid selection string
    resid_sel = "resid " + " ".join(str(r) for r in common_resids)
    sel_dock = ca_dock.select_atoms(resid_sel)
    sel_memb = ca_memb.select_atoms(resid_sel)

    # verify residue name consistency
    mismatches = []
    for a, b in zip(sel_dock, sel_memb):
        if a.resname != b.resname:
            mismatches.append((a.resid, a.resname, b.resname))
    if mismatches:
        print(f"  WARNING: {len(mismatches)} residue name mismatches:")
        for rid, rn1, rn2 in mismatches[:5]:
            print(f"    resid {rid}: dock={rn1} vs memb={rn2}")

    # positions
    pos_dock = sel_dock.positions.copy()  # (N, 3) — mobile
    pos_memb = sel_memb.positions.copy()  # (N, 3) — reference

    # compute centroids
    centroid_dock = pos_dock.mean(axis=0)
    centroid_memb = pos_memb.mean(axis=0)

    # center
    p = pos_dock - centroid_dock
    q = pos_memb - centroid_memb

    # Kabsch: SVD of cross-covariance matrix
    H = p.T @ q
    U, S, Vt = np.linalg.svd(H)

    # correct for reflection
    d = np.linalg.det(Vt.T @ U.T)
    sign_matrix = np.diag([1, 1, np.sign(d)])
    R = Vt.T @ sign_matrix @ U.T

    # translation: t = centroid_memb - R @ centroid_dock
    t = centroid_memb - R @ centroid_dock

    # RMSD after alignment
    aligned = (R @ pos_dock.T).T + t
    rmsd = np.sqrt(np.mean(np.sum((aligned - pos_memb) ** 2, axis=1)))

    print(f"  Alignment: {len(common_resids)} CA atoms, RMSD = {rmsd:.3f} Å")
    return R, t, rmsd, len(common_resids)


def transform_pdb(input_pdb: Path, output_pdb: Path, R: np.ndarray, t: np.ndarray) -> None:
    """Apply rotation R and translation t to all ATOM/HETATM coords in a PDB."""
    out_lines = []
    n_transformed = 0
    with open(input_pdb) as fh:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")) and len(line) >= 54:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                new_pos = R @ np.array([x, y, z]) + t
                new_line = f"{line[:30]}{new_pos[0]:8.3f}{new_pos[1]:8.3f}{new_pos[2]:8.3f}{line[54:]}"
                out_lines.append(new_line)
                n_transformed += 1
            else:
                out_lines.append(line)
    output_pdb.write_text("".join(out_lines))
    print(f"  Transformed {n_transformed} atoms → {output_pdb.name}")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    for name, paths in SYSTEMS.items():
        print(f"\n{'='*60}")
        print(f"Processing: {name}")
        print(f"{'='*60}")

        # 1. Extract MODEL 1
        model1_pdbqt = OUTDIR / f"{name}_model1.pdbqt"
        extract_model1(paths["pose_pdbqt"], model1_pdbqt)

        # 2. PDBQT → PDB
        model1_pdb = OUTDIR / f"{name}_model1_dockframe.pdb"
        pdbqt_to_pdb(model1_pdbqt, model1_pdb)

        # 3. Compute alignment (docking receptor → membrane system)
        R, t, rmsd, n_ca = compute_alignment(
            paths["dock_receptor"], paths["membrane_pdb"]
        )

        # 4. Apply transformation to ligand
        aligned_pdb = OUTDIR / f"{name}_model1_aligned.pdb"
        transform_pdb(model1_pdb, aligned_pdb, R, t)

        # 5. Summary
        print(f"\n  Output files:")
        print(f"    Docking frame:  {model1_pdb.relative_to(ROOT)}")
        print(f"    Aligned (memb): {aligned_pdb.relative_to(ROOT)}")
        print(f"    Alignment RMSD: {rmsd:.3f} Å over {n_ca} CA atoms")

        # 6. Quick sanity: check aligned ligand centroid Z vs membrane center
        u_memb = mda.Universe(str(paths["membrane_pdb"]))
        # membrane center ~ box center Z
        box_z = u_memb.dimensions[2] if u_memb.dimensions is not None else None

        u_lig = mda.Universe(str(aligned_pdb))
        lig_centroid = u_lig.atoms.positions.mean(axis=0)
        print(f"\n  Sanity check:")
        print(f"    Ligand centroid (aligned): ({lig_centroid[0]:.1f}, {lig_centroid[1]:.1f}, {lig_centroid[2]:.1f}) Å")
        if box_z:
            membrane_center_z = box_z / 2
            print(f"    Box Z = {box_z:.1f} Å, membrane center ≈ Z = {membrane_center_z:.1f} Å")
            if lig_centroid[2] > membrane_center_z:
                print(f"    ✓ Ligand above membrane center → extracellular side (expected)")
            else:
                print(f"    ⚠ Ligand below membrane center → check visually!")


if __name__ == "__main__":
    main()
