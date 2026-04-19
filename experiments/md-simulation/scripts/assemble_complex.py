#!/usr/bin/env python3
"""
Assemble protein-ligand-membrane complex for MD simulation.

Reads step5_input.gro + ligand.gro → step5_complex.gro
Modifies topol.top to include CGenFF params + ASCR18.
Generates index.ndx with SOLU/MEMB/SOLV/SOLU_MEMB/SYSTEM groups.

Dependencies: none (pure Python 3)
Usage:
  python3 assemble_complex.py --system Gpr2 --ligand ligand.gro [--remove-popc 514]
  python3 assemble_complex.py --rebuild-index step5_complex_ion.gro
"""

import argparse
import os
import re
import shutil
from pathlib import Path


def parse_gro(path):
    """Parse GRO file → (title, atoms, box_line).
    Each atom is a dict with keys: resnum, resname, atomname, atomnum, x, y, z, raw.
    """
    with open(path) as f:
        title = f.readline().strip()
        n_atoms = int(f.readline().strip())
        atoms = []
        for _ in range(n_atoms):
            line = f.readline()
            atoms.append({
                "resnum": int(line[0:5].strip()),
                "resname": line[5:10].strip(),
                "atomname": line[10:15].strip(),
                "atomnum": int(line[15:20].strip()),
                "x": float(line[20:28]),
                "y": float(line[28:36]),
                "z": float(line[36:44]),
                "raw": line,
            })
        box_line = f.readline()
    return title, atoms, box_line


def write_gro(path, title, atoms, box_line):
    """Write GRO with renumbered atoms."""
    with open(path, "w") as f:
        f.write(f"{title}\n")
        f.write(f"{len(atoms):5d}\n")
        for i, atom in enumerate(atoms):
            anum = (i + 1) % 100000
            f.write(
                f"{atom['resnum']:5d}{atom['resname']:<5s}"
                f"{atom['atomname']:>5s}{anum:5d}"
                f"{atom['x']:8.3f}{atom['y']:8.3f}{atom['z']:8.3f}\n"
            )
        f.write(box_line)
    print(f"  Wrote {path} ({len(atoms)} atoms)")


def build_index(atoms, path):
    """Generate index.ndx with SOLU/MEMB/SOLV/SOLU_MEMB/SYSTEM groups."""
    solu = []
    memb = []
    solv = []

    solu_resnames = set()
    memb_resnames = {"POPC"}
    solv_resnames = {"POT", "CLA", "TIP3", "SOL", "NA", "K"}

    for i, atom in enumerate(atoms):
        anum = i + 1
        rn = atom["resname"]
        if rn in memb_resnames:
            memb.append(anum)
        elif rn in solv_resnames:
            solv.append(anum)
        else:
            solu.append(anum)
            solu_resnames.add(rn)

    # TIP3-only group for genion (name must match moleculetype in topol.top)
    tip3 = [i + 1 for i, a in enumerate(atoms) if a["resname"] in ("TIP3", "SOL")]

    groups = {
        "SOLU": solu,
        "MEMB": memb,
        "SOLV": solv,
        "SOLU_MEMB": solu + memb,
        "SYSTEM": list(range(1, len(atoms) + 1)),
        "TIP3": tip3,
    }

    with open(path, "w") as f:
        for name, indices in groups.items():
            f.write(f"[ {name} ]\n")
            for j, idx in enumerate(indices):
                f.write(f" {idx}")
                if (j + 1) % 15 == 0:
                    f.write("\n")
            if len(indices) % 15 != 0:
                f.write("\n")
            f.write("\n")

    print(f"  Wrote {path}")
    print(f"    SOLU: {len(solu)} atoms (resnames: {sorted(solu_resnames)})")
    print(f"    MEMB: {len(memb)} atoms")
    print(f"    SOLV: {len(solv)} atoms")


def modify_topol(topol_path, popc_removed=0):
    """Modify topol.top: add CGenFF includes + ASCR18 molecule entry."""
    backup = str(topol_path) + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(topol_path, backup)
        print(f"  Backed up {topol_path} → {backup}")

    lines = Path(topol_path).read_text().splitlines(keepends=True)
    new_lines = []
    molecules_section = False
    proa_written = False

    for line in lines:
        stripped = line.strip()

        # Add CGenFF delta after forcefield.itp include
        if '#include "toppar/forcefield.itp"' in stripped:
            new_lines.append(line)
            new_lines.append('#include "toppar/cgenff_ASCR18.itp"\n')
            continue

        # Add ASCR18 itp + posre after PROA.itp include
        if '#include "toppar/PROA.itp"' in stripped:
            new_lines.append(line)
            new_lines.append('#include "ASCR18.itp"\n')
            new_lines.append("#ifdef POSRES\n")
            new_lines.append('#include "posre_ASCR18.itp"\n')
            new_lines.append("#endif\n")
            continue

        # In [ molecules ] section: add ASCR18 after PROA, adjust POPC count
        if stripped == "[ molecules ]":
            molecules_section = True
        if molecules_section:
            if stripped.startswith("PROA") and not proa_written:
                new_lines.append(line)
                new_lines.append("ASCR18\t           1\n")
                proa_written = True
                continue
            if stripped.startswith("POPC") and popc_removed > 0:
                parts = stripped.split()
                old_count = int(parts[1])
                new_count = old_count - popc_removed
                new_lines.append(f"POPC  \t         {new_count}\n")
                print(f"  POPC count: {old_count} → {new_count}")
                continue

        new_lines.append(line)

    Path(topol_path).write_text("".join(new_lines))
    print(f"  Modified {topol_path}")


def assemble(args):
    """Main assembly: merge ligand into membrane system."""
    work_dir = Path(args.work_dir)
    gro_in = work_dir / "step5_input.gro"
    gro_out = work_dir / "step5_complex.gro"
    lig_gro = work_dir / args.ligand
    topol = work_dir / "topol.top"
    ndx_out = work_dir / "index.ndx"

    print(f"\nAssembling {args.system} complex")
    print(f"  Work dir: {work_dir}")

    # 1. Parse input GRO
    title, sys_atoms, box_line = parse_gro(gro_in)
    print(f"  System: {len(sys_atoms)} atoms")

    # 2. Parse ligand GRO
    _, lig_atoms, _ = parse_gro(lig_gro)
    print(f"  Ligand: {len(lig_atoms)} atoms")

    # 3. Remove colliding POPC if specified
    popc_removed = 0
    if args.remove_popc:
        remove_set = set(args.remove_popc)
        before = len(sys_atoms)
        sys_atoms = [a for a in sys_atoms if not (a["resname"] == "POPC" and a["resnum"] in remove_set)]
        removed = before - len(sys_atoms)
        popc_removed = len(remove_set)
        print(f"  Removed {removed} atoms from POPC resid(s) {list(remove_set)}")

    # 4. Find protein end (last amino acid atom before POPC/ions/water)
    aa_resnames = {
        "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
        "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
        "HSD", "HSE", "HSP", "HID", "HIE", "HIP",
    }
    proa_end = 0
    for i, atom in enumerate(sys_atoms):
        if atom["resname"] in aa_resnames:
            proa_end = i + 1  # insert AFTER this index

    # Assign ligand resnum = last_protein_resnum + 1
    last_protein_resnum = sys_atoms[proa_end - 1]["resnum"] if proa_end > 0 else 0
    lig_resnum = last_protein_resnum + 1
    for atom in lig_atoms:
        atom["resnum"] = lig_resnum

    # 5. Insert ligand after protein
    assembled = sys_atoms[:proa_end] + lig_atoms + sys_atoms[proa_end:]
    print(f"  Assembled: {len(assembled)} atoms (protein ends at idx {proa_end})")

    # 6. Write complex GRO
    write_gro(gro_out, f"{title} + ASCR18", assembled, box_line)

    # 7. Modify topol.top
    modify_topol(topol, popc_removed=popc_removed)

    # 8. Generate index.ndx
    build_index(assembled, ndx_out)

    print(f"\n✓ Assembly complete for {args.system}")
    print(f"  Next: run genion + EM + equilibration")


def rebuild_index(args):
    """Rebuild index.ndx from a GRO file (e.g., after genion)."""
    gro_path = Path(args.rebuild_index)
    ndx_path = gro_path.parent / "index.ndx"
    _, atoms, _ = parse_gro(gro_path)
    build_index(atoms, ndx_path)
    print(f"\n✓ Rebuilt index.ndx from {gro_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Assemble MD complex")
    parser.add_argument("--system", type=str, help="System name (Gpr2 or Gpr3)")
    parser.add_argument("--work-dir", type=str, default=".", help="GROMACS working directory")
    parser.add_argument("--ligand", type=str, default="ligand.gro", help="Ligand GRO file")
    parser.add_argument("--remove-popc", type=int, nargs="*", help="POPC resid(s) to remove")
    parser.add_argument("--rebuild-index", type=str, help="Rebuild index.ndx from GRO")

    args = parser.parse_args()

    if args.rebuild_index:
        rebuild_index(args)
    elif args.system:
        assemble(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
