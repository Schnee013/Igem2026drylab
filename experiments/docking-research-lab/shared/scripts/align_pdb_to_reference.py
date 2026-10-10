#!/usr/bin/env python3
"""Rigidly align one PDB model to a reference using matched C-alpha ranges."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from Bio.PDB import PDBIO, PDBParser, Superimposer


def parse_ranges(value: str) -> list[int]:
    residues: list[int] = []
    for item in value.split(","):
        start_text, end_text = item.strip().split("-", 1)
        start, end = int(start_text), int(end_text)
        if start > end:
            raise ValueError(f"Invalid range {item!r}: start exceeds end")
        residues.extend(range(start, end + 1))
    if len(residues) != len(set(residues)):
        raise ValueError("Residue ranges overlap")
    return residues


def ca_atoms(structure, chain_id: str, residue_numbers: list[int]):
    chain = structure[0][chain_id]
    atoms = []
    for number in residue_numbers:
        residue_id = (" ", number, " ")
        if residue_id not in chain or "CA" not in chain[residue_id]:
            raise ValueError(f"Missing CA atom for chain {chain_id} residue {number}")
        atoms.append(chain[residue_id]["CA"])
    return atoms


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align a moving PDB to a reference PDB using matched CA residues."
    )
    parser.add_argument("--moving-pdb", required=True, type=Path)
    parser.add_argument("--reference-pdb", required=True, type=Path)
    parser.add_argument("--output-pdb", required=True, type=Path)
    parser.add_argument("--moving-chain", default="A")
    parser.add_argument("--reference-chain", default="A")
    parser.add_argument("--moving-ranges", required=True)
    parser.add_argument("--reference-ranges", required=True)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    targets = [args.output_pdb]
    if args.report_json:
        targets.append(args.report_json)
    existing = [str(path) for path in targets if path.exists()]
    if existing and not args.overwrite:
        parser.error("Refusing to overwrite: " + ", ".join(existing))

    moving_numbers = parse_ranges(args.moving_ranges)
    reference_numbers = parse_ranges(args.reference_ranges)
    if len(moving_numbers) != len(reference_numbers):
        parser.error("Moving and reference ranges must contain the same residue count")

    pdb_parser = PDBParser(QUIET=True)
    moving = pdb_parser.get_structure("moving", args.moving_pdb)
    reference = pdb_parser.get_structure("reference", args.reference_pdb)
    moving_ca = ca_atoms(moving, args.moving_chain, moving_numbers)
    reference_ca = ca_atoms(reference, args.reference_chain, reference_numbers)

    before = float(
        np.sqrt(
            np.mean(
                [
                    np.sum((moving_atom.coord - reference_atom.coord) ** 2)
                    for moving_atom, reference_atom in zip(moving_ca, reference_ca)
                ]
            )
        )
    )
    superimposer = Superimposer()
    superimposer.set_atoms(reference_ca, moving_ca)
    superimposer.apply(list(moving.get_atoms()))

    args.output_pdb.parent.mkdir(parents=True, exist_ok=True)
    writer = PDBIO()
    writer.set_structure(moving)
    writer.save(str(args.output_pdb))

    report = {
        "moving_pdb": str(args.moving_pdb.resolve()),
        "reference_pdb": str(args.reference_pdb.resolve()),
        "output_pdb": str(args.output_pdb.resolve()),
        "moving_chain": args.moving_chain,
        "reference_chain": args.reference_chain,
        "moving_ranges": args.moving_ranges,
        "reference_ranges": args.reference_ranges,
        "matched_ca_count": len(moving_ca),
        "ca_rmsd_before_angstrom": before,
        "ca_rmsd_after_angstrom": float(superimposer.rms),
        "rotation_matrix": superimposer.rotran[0].tolist(),
        "translation_vector": superimposer.rotran[1].tolist(),
    }
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
