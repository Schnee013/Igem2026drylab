#!/usr/bin/env python
"""
Check POPC collision with aligned docking ligand PDB.

Reads step5_input.gro (membrane system) and aligned ligand PDB,
reports POPC residues with any heavy atom < 2.0 Å from ligand.

Dependencies: numpy
Usage: conda run -n docking python check_popc_collision.py
"""

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

CUTOFF = 2.0  # Å — below this is a steric clash


def parse_gro_by_resname(gro_path, target_resname):
    """Parse GRO file, return {resid: [(atom_name, np.array(x,y,z in Å))]}."""
    residues = {}
    with open(gro_path) as f:
        title = f.readline()
        n_atoms = int(f.readline().strip())
        for _ in range(n_atoms):
            line = f.readline()
            resnum = int(line[0:5].strip())
            resname = line[5:10].strip()
            atom_name = line[10:15].strip()
            if resname == target_resname:
                # GRO coords are in nm → convert to Å
                x = float(line[20:28]) * 10.0
                y = float(line[28:36]) * 10.0
                z = float(line[36:44]) * 10.0
                residues.setdefault(resnum, []).append(
                    (atom_name, np.array([x, y, z]))
                )
    return residues


def parse_ligand_pdb(pdb_path):
    """Parse heavy atoms from aligned ligand PDB. Returns list of np.array."""
    coords = []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("HETATM") and len(line) >= 54:
                element = line[12:16].strip()
                if element.startswith("H"):
                    continue  # skip hydrogens
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords.append(np.array([x, y, z]))
    return coords


def check_collisions(system_name, gro_path, ligand_pdb_path):
    print(f"\n{'='*50}")
    print(f"  {system_name} POPC collision check")
    print(f"{'='*50}")

    # Parse POPC residues
    popc_residues = parse_gro_by_resname(gro_path, "POPC")
    print(f"  POPC residues: {len(popc_residues)}")

    # Parse ligand heavy atoms
    lig_coords = parse_ligand_pdb(ligand_pdb_path)
    lig_arr = np.array(lig_coords)
    print(f"  Ligand heavy atoms: {len(lig_arr)}")
    print(f"  Ligand Z range: {lig_arr[:,2].min():.1f} – {lig_arr[:,2].max():.1f} Å")

    # Check each POPC
    clashes = []
    close_contacts = []
    for resid, atoms in sorted(popc_residues.items()):
        min_dist = float("inf")
        for atom_name, popc_pos in atoms:
            dists = np.linalg.norm(lig_arr - popc_pos, axis=1)
            d = dists.min()
            if d < min_dist:
                min_dist = d
        if min_dist < CUTOFF:
            clashes.append((resid, min_dist))
        elif min_dist < 3.0:
            close_contacts.append((resid, min_dist))

    print(f"\n  Clashes (< {CUTOFF} Å):")
    if clashes:
        for resid, d in sorted(clashes, key=lambda x: x[1]):
            print(f"    POPC resid {resid}: min distance = {d:.2f} Å  *** REMOVE ***")
    else:
        print(f"    None — all POPC > {CUTOFF} Å from ligand")

    print(f"\n  Close contacts ({CUTOFF}–3.0 Å):")
    if close_contacts:
        for resid, d in sorted(close_contacts, key=lambda x: x[1]):
            print(f"    POPC resid {resid}: min distance = {d:.2f} Å  (EM will resolve)")
    else:
        print(f"    None")

    return [r for r, _ in clashes]


def main():
    systems = {
        "Gpr2_WT": {
            "gro": ROOT / "experiments/md-simulation/systems/Gpr2_WT/gromacs/step5_input.gro",
            "lig": ROOT / "experiments/md-simulation/structures/docking_poses/Gpr2_ascr18_3doffset_model1_aligned.pdb",
        },
        "Gpr3_WT": {
            "gro": ROOT / "experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.gro",
            "lig": ROOT / "experiments/md-simulation/structures/docking_poses/Gpr3_ascr18_model1_aligned.pdb",
        },
    }

    results = {}
    for name, paths in systems.items():
        clashed = check_collisions(name, paths["gro"], paths["lig"])
        results[name] = clashed

    print(f"\n{'='*50}")
    print("  Summary")
    print(f"{'='*50}")
    for name, clashed in results.items():
        if clashed:
            print(f"  {name}: DELETE POPC resid(s) {clashed}")
        else:
            print(f"  {name}: No collision — direct merge OK")


if __name__ == "__main__":
    main()
