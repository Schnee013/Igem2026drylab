#!/usr/bin/env python
"""Prepare chimeric Gpa1 complex structures for MD simulation.

Dependencies: BioPython (conda activate docking)
Usage:
    # AF3 CIF → clean multi-chain PDB
    python prepare_chimeric_system.py --mode af3 \
        --input <af3_cif_path> --output <clean_pdb_path>

    # PDB → clean multi-chain PDB (keep specified chains)
    python prepare_chimeric_system.py --mode pdb \
        --input <pdb_path> --output <clean_pdb_path> \
        --keep-chains R,A

Pipeline context: Phase C1 of chimeric-md-execution.md
"""

import argparse
import sys
from pathlib import Path

from Bio.PDB import PDBIO, Select
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser


class ChainSelect(Select):
    """Select specific chains, standard residues only, no H atoms."""

    def __init__(self, keep_chains=None, remove_hetatm=False, remove_h=False):
        self.keep_chains = set(keep_chains) if keep_chains else None
        self.remove_hetatm = remove_hetatm
        self.remove_h = remove_h

    def accept_chain(self, chain):
        if self.keep_chains is None:
            return True
        return chain.id in self.keep_chains

    def accept_residue(self, residue):
        if self.remove_hetatm and residue.id[0] != " ":
            return False
        return True

    def accept_atom(self, atom):
        if self.remove_h and atom.element == "H":
            return False
        return True


def rename_his_to_hsd(structure):
    """Rename all HIS residues to HSD for CHARMM36m force field.

    GROMACS pdb2gmx with CHARMM36m expects HSD (Nδ-protonated),
    HSE (Nε-protonated), or HSP (doubly protonated) instead of generic HIS.
    Default to HSD (most common in protein interiors).
    """
    count = 0
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.resname == "HIS":
                    residue.resname = "HSD"
                    count += 1
    return count


def process_af3(input_path, output_path):
    """Process AF3 CIF to clean multi-chain PDB."""
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("complex", str(input_path))
    model = structure[0]

    # Report chain info
    print("=== AF3 CIF chain summary ===")
    for chain in model:
        residues = [r for r in chain if r.id[0] == " "]
        print(
            f"  Chain {chain.id}: {len(residues)} residues "
            f"({residues[0].resname}{residues[0].id[1]}"
            f"–{residues[-1].resname}{residues[-1].id[1]})"
        )

    # HIS → HSD
    his_count = rename_his_to_hsd(structure)
    print(f"  HIS → HSD: {his_count} residues renamed")

    # Write PDB (all chains, standard residues only)
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(output_path), ChainSelect())
    print(f"  Output: {output_path}")

    return structure


def process_pdb(input_path, output_path, keep_chains):
    """Process PDB to clean multi-chain PDB."""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("complex", str(input_path))
    model = structure[0]

    # Report all chains before filtering
    print("=== PDB chain summary (before filtering) ===")
    for chain in model:
        residues = [r for r in chain if r.id[0] == " "]
        het_residues = [r for r in chain if r.id[0] != " "]
        if residues:
            print(
                f"  Chain {chain.id}: {len(residues)} std residues, "
                f"{len(het_residues)} HETATM"
            )
        else:
            print(f"  Chain {chain.id}: {len(het_residues)} HETATM only")

    print(f"  Keeping chains: {', '.join(keep_chains)}")

    # HIS → HSD
    his_count = rename_his_to_hsd(structure)
    print(f"  HIS → HSD: {his_count} residues renamed")

    # Write PDB (selected chains, no HETATM, no H)
    io = PDBIO()
    io.set_structure(structure)
    io.save(
        str(output_path),
        ChainSelect(keep_chains=keep_chains, remove_hetatm=True, remove_h=True),
    )

    # Report output chains
    parser2 = PDBParser(QUIET=True)
    out_struct = parser2.get_structure("out", str(output_path))
    print("=== Output chain summary ===")
    for chain in out_struct[0]:
        residues = [r for r in chain if r.id[0] == " "]
        print(
            f"  Chain {chain.id}: {len(residues)} residues "
            f"({residues[0].resname}{residues[0].id[1]}"
            f"–{residues[-1].resname}{residues[-1].id[1]})"
        )
    print(f"  Output: {output_path}")

    return structure


def main():
    parser = argparse.ArgumentParser(
        description="Prepare chimeric complex structures for MD"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["af3", "pdb"],
        help="Input format: af3 (mmCIF) or pdb",
    )
    parser.add_argument("--input", required=True, help="Input CIF/PDB path")
    parser.add_argument("--output", required=True, help="Output clean PDB path")
    parser.add_argument(
        "--keep-chains",
        help="Comma-separated chain IDs to keep (pdb mode only)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.mode == "af3":
        process_af3(input_path, output_path)
    elif args.mode == "pdb":
        if not args.keep_chains:
            print("ERROR: --keep-chains required for pdb mode", file=sys.stderr)
            sys.exit(1)
        chains = [c.strip() for c in args.keep_chains.split(",")]
        process_pdb(input_path, output_path, chains)


if __name__ == "__main__":
    main()
