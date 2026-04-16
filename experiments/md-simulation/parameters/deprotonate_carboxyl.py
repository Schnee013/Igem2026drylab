#!/usr/bin/env python3
"""Remove the carboxyl proton from ascaroside SDFs to produce COO- form.

For both ascr18 and ascr3, the carboxyl OH proton is the last atom in the SDF.
The O it's bonded to (atom 5 in both cases) gets formal charge -1.

Usage:
    python deprotonate_carboxyl.py

Reads from protonated/ subdirectories, writes to deprotonated/.
"""

import re
from pathlib import Path

BASE = Path(__file__).parent


def deprotonate_sdf(input_path: Path, output_path: Path, o_atom_idx: int, h_atom_idx: int):
    """Remove carboxyl H from SDF and set formal charge on O.

    Args:
        input_path: Path to protonated SDF
        output_path: Path to write deprotonated SDF
        o_atom_idx: 1-based atom index of the carboxyl O (gets charge -1)
        h_atom_idx: 1-based atom index of the carboxyl H (gets removed)
    """
    lines = input_path.read_text().splitlines()

    # Parse counts line (line index 3, 0-based)
    counts_line = lines[3]
    match = re.match(r'\s*(\d+)\s+(\d+)', counts_line)
    n_atoms = int(match.group(1))
    n_bonds = int(match.group(2))

    assert h_atom_idx == n_atoms, (
        f"Expected H to be last atom ({n_atoms}), got {h_atom_idx}"
    )

    # New counts — V2000 uses 3-char wide fields for atom/bond counts
    new_n_atoms = n_atoms - 1
    new_n_bonds = n_bonds - 1
    new_counts = f'{new_n_atoms:3d}{new_n_bonds:3d}' + counts_line[6:]

    # Atom block: lines[4] to lines[4 + n_atoms - 1]
    atom_start = 4
    atom_end = atom_start + n_atoms  # exclusive
    h_line_idx = atom_start + h_atom_idx - 1  # 0-based line index of the H atom

    # Bond block: lines[atom_end] to lines[atom_end + n_bonds - 1]
    bond_start = atom_end
    bond_end = bond_start + n_bonds

    # Find the bond connecting O to H
    bond_to_remove = None
    for i in range(bond_start, bond_end):
        parts = lines[i].split()
        a1, a2 = int(parts[0]), int(parts[1])
        if (a1 == o_atom_idx and a2 == h_atom_idx) or \
           (a1 == h_atom_idx and a2 == o_atom_idx):
            bond_to_remove = i
            break

    assert bond_to_remove is not None, (
        f"Could not find bond {o_atom_idx}-{h_atom_idx}"
    )

    # Build output
    out = []
    # Header (lines 0-2)
    out.extend(lines[:3])
    # Updated counts line
    out.append(new_counts)
    # Atom block minus the H
    for i in range(atom_start, atom_end):
        if i != h_line_idx:
            out.append(lines[i])
    # Bond block minus the O-H bond
    for i in range(bond_start, bond_end):
        if i != bond_to_remove:
            out.append(lines[i])
    # Add M CHG line for the carboxylate O, then rest of file
    remaining_start = bond_end
    for i in range(remaining_start, len(lines)):
        if lines[i].strip() == 'M  END':
            out.append(f'M  CHG  1   {o_atom_idx}  -1')
            out.append('M  END')
        else:
            out.append(lines[i])

    output_path.write_text('\n'.join(out) + '\n')
    print(f"  wrote {output_path}")
    print(f"  atoms: {n_atoms} -> {new_n_atoms}, bonds: {n_bonds} -> {new_n_bonds}")
    print(f"  removed H atom {h_atom_idx}, set formal charge -1 on O atom {o_atom_idx}")


def main():
    # ascr18: O5 = atom 5, H32 = atom 55 (last atom)
    ascr18_in = BASE / "ascr18/protonated/charmm-gui-7628908749/ascr18_CID71514784.sdf"
    ascr18_out = BASE / "ascr18/deprotonated/ascr18_deprotonated.sdf"
    print("ascr18:")
    deprotonate_sdf(ascr18_in, ascr18_out, o_atom_idx=5, h_atom_idx=55)

    # ascr3: O5 = atom 5, H26 = atom 47 (last atom)
    ascr3_in = BASE / "ascr3/protonated/charmm-gui-7628970666/ascr3_CID16066476.sdf"
    ascr3_out = BASE / "ascr3/deprotonated/ascr3_deprotonated.sdf"
    print("\nascr3:")
    deprotonate_sdf(ascr3_in, ascr3_out, o_atom_idx=5, h_atom_idx=47)


if __name__ == "__main__":
    main()
