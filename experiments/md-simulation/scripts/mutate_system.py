#!/usr/bin/env python3
"""Assemble in-place mutant MD system from WT equilibrated structure.

Replaces protein in WT step6.6.gro with CHARMM-GUI-processed mutant protein.
Copies non-protein atoms (membrane, ions, water, ligand) from WT unchanged.
Copies topology files from WT, replacing only PROA.itp with the new mutant version.

Dependencies: none (pure Python 3)
Usage:
  python3 mutate_system.py --wt Gpr3 --mut F170E \
    --charmm-dir /path/to/charmm-gui-download/gromacs/

  python3 mutate_system.py --wt Gpr3 --mut F170E \
    --charmm-protein /path/to/step1_pdbreader.gro \
    --charmm-proa /path/to/toppar/PROA.itp
"""

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SYSTEMS_DIR = PROJECT_ROOT / "experiments" / "md-simulation" / "systems"

# Mapping: (wt_system, mutation_name) -> output directory
MUTANT_DIRS = {
    ("Gpr3", "V138R"): "gpr3-V138R-ascr18",
    ("Gpr3", "F170E"): "gpr3-F170E-ascr18",
    ("Gpr3", "I141A"): "gpr3-I141A-ascr18",
    ("Gpr2", "M327A"): "gpr2-M327A-ascr18",
    ("Gpr2", "M327D"): "gpr2-M327D-ascr18",
    ("Gpr2", "R59F"):  "gpr2-R59F-ascr18",
}

AA_RESNAMES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
    "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
    "HSD", "HSE", "HSP", "HID", "HIE", "HIP",
}

MEMB_RESNAMES = {"POPC"}
SOLV_RESNAMES = {"POT", "CLA", "TIP3", "SOL", "NA", "K"}


# ── GRO I/O (same as assemble_complex.py) ──

def parse_gro(path):
    """Parse GRO file -> (title, atoms, box_line)."""
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
    """Generate index.ndx with SOLU/MEMB/SOLV/SOLU_MEMB/SYSTEM/TIP3 groups."""
    solu, memb, solv = [], [], []
    solu_resnames = set()

    for i, atom in enumerate(atoms):
        anum = i + 1
        rn = atom["resname"]
        if rn in MEMB_RESNAMES:
            memb.append(anum)
        elif rn in SOLV_RESNAMES:
            solv.append(anum)
        else:
            solu.append(anum)
            solu_resnames.add(rn)

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


# ── Core assembly logic ──

def split_protein_nonprotein(atoms):
    """Split atoms at the protein/non-protein boundary.

    Returns (protein_atoms, non_protein_atoms).
    Assumes protein comes first, followed by non-protein (ASCR18, POPC, ions, water).
    """
    protein_end = 0
    for i, atom in enumerate(atoms):
        if atom["resname"] in AA_RESNAMES:
            protein_end = i + 1
    return atoms[:protein_end], atoms[protein_end:]


def assemble_mutant(wt_gro_path, charmm_protein_path, output_gro_path):
    """Replace protein in WT system with CHARMM-GUI-processed mutant protein."""
    # 1. Parse WT system
    title, wt_atoms, box_line = parse_gro(wt_gro_path)
    wt_protein, non_protein = split_protein_nonprotein(wt_atoms)
    print(f"  WT system: {len(wt_atoms)} atoms (protein: {len(wt_protein)}, non-protein: {len(non_protein)})")

    # 2. Parse CHARMM-GUI mutant protein
    _, mut_protein, _ = parse_gro(charmm_protein_path)
    print(f"  Mutant protein: {len(mut_protein)} atoms")

    # 3. Validate: residue count should match (single point mutation)
    wt_resids = sorted({a["resnum"] for a in wt_protein})
    mut_resids = sorted({a["resnum"] for a in mut_protein})
    if len(wt_resids) != len(mut_resids):
        print(f"  WARNING: residue count differs (WT: {len(wt_resids)}, mutant: {len(mut_resids)})")

    # 4. Atom count delta
    delta = len(mut_protein) - len(wt_protein)
    if delta != 0:
        print(f"  Atom count delta: {delta:+d} (mutation changes sidechain size)")

    # 5. Assemble: mutant protein + WT non-protein
    assembled = mut_protein + non_protein
    print(f"  Assembled: {len(assembled)} atoms")

    # 6. Write output
    write_gro(output_gro_path, f"{title} mutant", assembled, box_line)

    return assembled


def setup_output_dir(wt_system, mut_name, output_dir, wt_gromacs_dir, charmm_proa_path):
    """Set up mutant gromacs directory with WT topology files + new PROA.itp."""
    output_dir.mkdir(parents=True, exist_ok=True)
    toppar_out = output_dir / "toppar"
    toppar_out.mkdir(exist_ok=True)

    # Copy WT topology files (except PROA.itp)
    wt_toppar = wt_gromacs_dir / "toppar"
    for src in wt_toppar.iterdir():
        if src.name == "PROA.itp":
            continue  # Will use new PROA.itp from CHARMM-GUI
        dst = toppar_out / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
            print(f"  Copied toppar/{src.name}")

    # Copy new PROA.itp from CHARMM-GUI
    shutil.copy2(charmm_proa_path, toppar_out / "PROA.itp")
    print(f"  Copied new PROA.itp from CHARMM-GUI")

    # Copy topol_phase3.top
    wt_topol = wt_gromacs_dir / "topol_phase3.top"
    dst_topol = output_dir / "topol.top"
    if not dst_topol.exists():
        shutil.copy2(wt_topol, dst_topol)
        print(f"  Copied topol.top (from topol_phase3.top)")

    # Copy ASCR18 files
    for name in ("ASCR18.itp", "posre_ASCR18.itp"):
        src = wt_gromacs_dir / name
        dst = output_dir / name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            print(f"  Copied {name}")

    # Copy MDP files
    for mdp in wt_gromacs_dir.glob("step6*.mdp"):
        dst = output_dir / mdp.name
        if not dst.exists():
            shutil.copy2(mdp, dst)
    print(f"  Copied MDP files (step6.0-6.6)")

    # Copy step7 extended eq MDP if available
    step7_mdp = PROJECT_ROOT / "experiments" / "md-simulation" / "mdp" / "step7_extended_eq.mdp"
    if step7_mdp.exists():
        dst = output_dir / "step7_extended_eq.mdp"
        if not dst.exists():
            shutil.copy2(step7_mdp, dst)
            print(f"  Copied step7_extended_eq.mdp")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--wt", required=True, choices=["Gpr2", "Gpr3"],
                        help="WT system name")
    parser.add_argument("--mut", required=True,
                        help="Mutation name (e.g., F170E, M327A)")
    # CHARMM-GUI input: either --charmm-dir or --charmm-protein + --charmm-proa
    parser.add_argument("--charmm-dir", type=Path,
                        help="CHARMM-GUI output directory (contains step1_pdbreader.gro + toppar/PROA.itp)")
    parser.add_argument("--charmm-protein", type=Path,
                        help="CHARMM-GUI processed protein GRO (explicit path)")
    parser.add_argument("--charmm-proa", type=Path,
                        help="CHARMM-GUI PROA.itp (explicit path)")
    args = parser.parse_args()

    # Resolve CHARMM-GUI paths
    if args.charmm_dir:
        charmm_protein = args.charmm_dir / "step1_pdbreader.gro"
        charmm_proa = args.charmm_dir / "toppar" / "PROA.itp"
    elif args.charmm_protein and args.charmm_proa:
        charmm_protein = args.charmm_protein
        charmm_proa = args.charmm_proa
    else:
        print("ERROR: provide either --charmm-dir or both --charmm-protein and --charmm-proa")
        sys.exit(1)

    for p, label in [(charmm_protein, "CHARMM-GUI protein GRO"), (charmm_proa, "PROA.itp")]:
        if not p.exists():
            print(f"ERROR: {label} not found: {p}")
            sys.exit(1)

    # Resolve directories
    key = (args.wt, args.mut.upper())
    if key not in MUTANT_DIRS:
        print(f"ERROR: unknown mutation {args.wt}_{args.mut}")
        print(f"Valid: {', '.join(f'{k[0]}_{k[1]}' for k in MUTANT_DIRS)}")
        sys.exit(1)

    mutant_dir_name = MUTANT_DIRS[key]
    wt_gromacs = SYSTEMS_DIR / f"{args.wt}_WT" / "gromacs"
    wt_gro = wt_gromacs / "step6.6.gro"
    output_dir = SYSTEMS_DIR / mutant_dir_name / "gromacs"
    output_gro = output_dir / "step5_mutant.gro"

    if not wt_gro.exists():
        print(f"ERROR: WT GRO not found: {wt_gro}")
        sys.exit(1)

    print(f"\n=== Assembling {args.wt}_{args.mut} (in-place mutant) ===")
    print(f"  WT: {wt_gro}")
    print(f"  CHARMM-GUI protein: {charmm_protein}")
    print(f"  Output: {output_dir}")

    # 1. Set up output directory with topology files
    print(f"\n--- Setting up output directory ---")
    setup_output_dir(args.wt, args.mut, output_dir, wt_gromacs, charmm_proa)

    # 2. Assemble mutant system
    print(f"\n--- Assembling system ---")
    assembled = assemble_mutant(wt_gro, charmm_protein, output_gro)

    # 3. Build index
    print(f"\n--- Building index ---")
    build_index(assembled, output_dir / "index.ndx")

    print(f"\n=== {args.wt}_{args.mut} assembly complete ===")
    print(f"  System GRO: {output_gro}")
    print(f"  Next: deploy to server and run EM + equilibration")


if __name__ == "__main__":
    main()
