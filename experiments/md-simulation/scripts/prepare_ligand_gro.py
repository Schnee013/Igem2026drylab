#!/usr/bin/env python
"""
Prepare ASCR18 ligand GRO from docking-aligned PDB + CGenFF .itp.

Maps 25 docking PDB atoms (23 heavy + 2 OH H) to CGenFF naming,
generates 29 missing non-polar H coordinates via sp3 geometry,
outputs GRO with all 54 atoms in .itp order.

Dependencies: numpy
Usage: conda run -n docking python prepare_ligand_gro.py
"""

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# ── Docking PDB atom# → (CGenFF atom name, CGenFF 1-based index in .itp) ──
# Atom 14 (H, carboxylate proton) is deleted for deprotonated form.
DOCK_TO_CGENFF = {
    1:  ("C6",  12),   2:  ("C12", 18),   3:  ("C7",  13),
    4:  ("C8",  14),   5:  ("C9",  15),   6:  ("C11", 17),
    7:  ("C13", 19),   8:  ("C14", 20),   9:  ("C15", 21),
    10: ("C16", 22),  11: ("C17", 23),  12: ("O5",   5),
    13: ("O6",   6),  15: ("O2",   2),  16: ("C4",  10),
    17: ("C1",   7),  18: ("C3",   9),  19: ("C2",   8),
    20: ("C5",  11),  21: ("O1",   1),  22: ("C10", 16),
    23: ("O3",   3),  24: ("H24", 47),  25: ("O4",   4),
    26: ("H25", 48),
}

# ── .itp atom table: (index, name) in order ──
ITP_ATOMS = [
    (1, "O1"), (2, "O2"), (3, "O3"), (4, "O4"), (5, "O5"), (6, "O6"),
    (7, "C1"), (8, "C2"), (9, "C3"), (10, "C4"), (11, "C5"), (12, "C6"),
    (13, "C7"), (14, "C8"), (15, "C9"), (16, "C10"), (17, "C11"), (18, "C12"),
    (19, "C13"), (20, "C14"), (21, "C15"), (22, "C16"), (23, "C17"),
    (24, "H1"), (25, "H2"), (26, "H3"), (27, "H4"), (28, "H5"), (29, "H6"),
    (30, "H7"), (31, "H8"), (32, "H9"), (33, "H10"), (34, "H11"),
    (35, "H12"), (36, "H13"), (37, "H14"), (38, "H15"), (39, "H16"),
    (40, "H17"), (41, "H18"), (42, "H19"), (43, "H20"),
    (44, "H21"), (45, "H22"), (46, "H23"),
    (47, "H24"), (48, "H25"),
    (49, "H26"), (50, "H27"), (51, "H28"), (52, "H29"),
    (53, "H30"), (54, "H31"),
]

# ── H parent mapping from .itp [ bonds ]: H_itp_index → parent heavy atom index ──
H_PARENT = {
    24: 7,  25: 8,  26: 9,  27: 9,  28: 10, 29: 11,
    30: 12, 31: 13, 32: 13, 33: 14, 34: 14, 35: 15,
    36: 15, 37: 16, 38: 16, 39: 16, 40: 17, 41: 17,
    42: 19, 43: 19, 44: 18, 45: 18, 46: 18,
    47: 3,  48: 4,
    49: 20, 50: 20, 51: 21, 52: 21, 53: 22, 54: 22,
}

# ── Heavy-atom neighbor list (itp index → [heavy neighbor indices]) ──
HEAVY_NEIGHBORS = {
    1:  [10, 11],       # O1:  C4, C5
    2:  [10, 12],       # O2:  C4, C6
    3:  [7],            # O3:  C1
    4:  [8],            # O4:  C2
    5:  [23],           # O5:  C17
    6:  [23],           # O6:  C17
    7:  [3, 9, 10],     # C1:  O3, C3, C4
    8:  [4, 9, 11],     # C2:  O4, C3, C5
    9:  [7, 8],         # C3:  C1, C2
    10: [1, 2, 7],      # C4:  O1, O2, C1
    11: [1, 8, 16],     # C5:  O1, C2, C10
    12: [2, 13, 18],    # C6:  O2, C7, C12
    13: [12, 14],       # C7:  C6, C8
    14: [13, 15],       # C8:  C7, C9
    15: [14, 17],       # C9:  C8, C11
    16: [11],           # C10: C5
    17: [15, 19],       # C11: C9, C13
    18: [12],           # C12: C6
    19: [17, 20],       # C13: C11, C14
    20: [19, 21],       # C14: C13, C15
    21: [20, 22],       # C15: C14, C16
    22: [21, 23],       # C16: C15, C17
    23: [5, 6, 22],     # C17: O5, O6, C16
}

CH_BOND = 1.09  # Å, standard C-H bond length


def parse_docking_pdb(path):
    """Parse HETATM from docking-aligned PDB → {dock_atom#: np.array([x,y,z])}."""
    coords = {}
    with open(path) as f:
        for line in f:
            if line.startswith("HETATM") and len(line) >= 54:
                serial = int(line[6:11].strip())
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords[serial] = np.array([x, y, z])
    return coords


def normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def perpendicular_vector(v):
    """Return an arbitrary unit vector perpendicular to v."""
    v = normalize(v)
    if abs(v[0]) < 0.9:
        ref = np.array([1.0, 0.0, 0.0])
    else:
        ref = np.array([0.0, 1.0, 0.0])
    p = np.cross(v, ref)
    return normalize(p)


def place_ch1(parent_pos, neighbor_positions):
    """Place 1 H on sp3 C with 3 heavy neighbors."""
    d_sum = np.zeros(3)
    for n in neighbor_positions:
        d_sum += normalize(n - parent_pos)
    h_dir = -normalize(d_sum)
    return [parent_pos + CH_BOND * h_dir]


def place_ch2(parent_pos, neighbor_positions):
    """Place 2 H on sp3 C with 2 heavy neighbors."""
    b1 = normalize(neighbor_positions[0] - parent_pos)
    b2 = normalize(neighbor_positions[1] - parent_pos)
    d = -normalize(b1 + b2)
    n = np.cross(b1, b2)
    n_norm = np.linalg.norm(n)
    if n_norm < 1e-12:
        n = perpendicular_vector(b1)
    else:
        n = n / n_norm
    # Solve for half-angle: cos(alpha) = 1 / (3 * cos(phi/2))
    cos_phi = np.clip(np.dot(b1, b2), -1.0, 1.0)
    cos_half_phi = np.sqrt((1.0 + cos_phi) / 2.0)
    cos_alpha = np.clip(1.0 / (3.0 * cos_half_phi), -1.0, 1.0)
    sin_alpha = np.sqrt(max(0.0, 1.0 - cos_alpha ** 2))
    h1 = parent_pos + CH_BOND * (cos_alpha * d + sin_alpha * n)
    h2 = parent_pos + CH_BOND * (cos_alpha * d - sin_alpha * n)
    return [h1, h2]


def place_ch3(parent_pos, neighbor_positions):
    """Place 3 H on sp3 C with 1 heavy neighbor (methyl group)."""
    b1 = normalize(neighbor_positions[0] - parent_pos)
    n1 = perpendicular_vector(b1)
    n2 = np.cross(b1, n1)
    # Tetrahedral: cos(theta) = 1/3
    cos_t = 1.0 / 3.0
    sin_t = np.sqrt(1.0 - cos_t ** 2)  # 2*sqrt(2)/3
    hs = []
    for i in range(3):
        angle = 2.0 * np.pi * i / 3.0
        h_dir = -cos_t * b1 + sin_t * (np.cos(angle) * n1 + np.sin(angle) * n2)
        hs.append(parent_pos + CH_BOND * normalize(h_dir))
    return hs


def generate_h_positions(coords_by_itp):
    """Generate all 29 missing non-polar H positions.

    coords_by_itp: {itp_index: np.array([x,y,z])} for known atoms.
    Returns: updated dict with all 54 atoms.
    """
    result = dict(coords_by_itp)

    # Group H atoms by parent carbon
    parent_to_hs = {}
    for h_idx, p_idx in H_PARENT.items():
        if h_idx in result:
            continue  # H24 (47), H25 (48) already have coordinates
        parent_to_hs.setdefault(p_idx, []).append(h_idx)

    for parent_idx, h_indices in parent_to_hs.items():
        parent_pos = result[parent_idx]
        heavy_nbrs = HEAVY_NEIGHBORS[parent_idx]
        nbr_positions = [result[n] for n in heavy_nbrs]
        n_h = len(h_indices)

        if n_h == 1:
            positions = place_ch1(parent_pos, nbr_positions)
        elif n_h == 2:
            positions = place_ch2(parent_pos, nbr_positions)
        elif n_h == 3:
            positions = place_ch3(parent_pos, nbr_positions)
        else:
            raise ValueError(f"Unexpected {n_h} H on atom {parent_idx}")

        for h_idx, pos in zip(sorted(h_indices), positions):
            result[h_idx] = pos

    return result


def write_gro(coords_by_itp, out_path, title="ASCR18 ligand"):
    """Write GRO file with 54 atoms in .itp order. Coords in Å → nm."""
    lines = [f"{title}\n", f"{len(ITP_ATOMS):5d}\n"]
    resnum = 1
    resname = "LIG"  # GRO resname max 5 chars; topology matches by order, not name
    # GRO format: %5d%-5s%5s%5d%8.3f%8.3f%8.3f
    for itp_idx, atom_name in ITP_ATOMS:
        pos = coords_by_itp[itp_idx] / 10.0  # Å → nm
        lines.append(
            f"{resnum:5d}{resname:<5s}{atom_name:>5s}{itp_idx:5d}"
            f"{pos[0]:8.3f}{pos[1]:8.3f}{pos[2]:8.3f}\n"
        )
    lines.append("   0.00000   0.00000   0.00000\n")  # no box for standalone ligand
    out_path.write_text("".join(lines))
    print(f"  Wrote {out_path} ({len(ITP_ATOMS)} atoms)")


def process_system(name, aligned_pdb_path, out_gro_path):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")

    # 1. Parse docking PDB
    dock_coords = parse_docking_pdb(aligned_pdb_path)
    print(f"  Parsed {len(dock_coords)} atoms from {aligned_pdb_path.name}")

    # 2. Map to CGenFF indices
    coords_by_itp = {}
    for dock_idx, (cgenff_name, itp_idx) in DOCK_TO_CGENFF.items():
        if dock_idx not in dock_coords:
            raise KeyError(f"Docking atom {dock_idx} not found in PDB")
        coords_by_itp[itp_idx] = dock_coords[dock_idx]

    print(f"  Mapped {len(coords_by_itp)} atoms to CGenFF naming")

    # 3. Generate missing H positions
    coords_by_itp = generate_h_positions(coords_by_itp)
    print(f"  Total atoms after H generation: {len(coords_by_itp)}")

    # Sanity: verify all 54 present
    missing = [idx for idx, _ in ITP_ATOMS if idx not in coords_by_itp]
    if missing:
        raise RuntimeError(f"Missing atom indices: {missing}")

    # 4. Write GRO
    write_gro(coords_by_itp, out_gro_path, title=f"{name} deprotonated ASCR18")
    print(f"  Done: {out_gro_path.name}")


def main():
    outdir = ROOT / "experiments/md-simulation/structures/docking_poses"
    outdir.mkdir(parents=True, exist_ok=True)

    systems = {
        "Gpr2_ascr18": {
            "aligned_pdb": ROOT / "experiments/md-simulation/structures/docking_poses/Gpr2_ascr18_3doffset_model1_aligned.pdb",
            "out_gro": outdir / "Gpr2_ASCR18_aligned.gro",
        },
        "Gpr3_ascr18": {
            "aligned_pdb": ROOT / "experiments/md-simulation/structures/docking_poses/Gpr3_ascr18_model1_aligned.pdb",
            "out_gro": outdir / "Gpr3_ASCR18_aligned.gro",
        },
    }

    for name, paths in systems.items():
        process_system(name, paths["aligned_pdb"], paths["out_gro"])

    print("\n✓ All ligand GRO files prepared.")


if __name__ == "__main__":
    main()
