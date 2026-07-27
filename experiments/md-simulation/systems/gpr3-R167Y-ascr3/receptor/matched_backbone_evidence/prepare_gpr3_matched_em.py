#!/usr/bin/env python3
"""Prepare and audit a Gpr3 R167Y exact-backbone local-EM prototype."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


BACKBONE = {"N", "CA", "C", "O"}


def pdb_atoms(path: Path) -> dict[tuple[str, int, str], str]:
    atoms: dict[tuple[str, int, str], str] = {}
    for line in path.read_text().splitlines():
        if line.startswith("ATOM  "):
            key = (line[21].strip(), int(line[22:26]), line[12:16].strip())
            atoms[key] = line
    return atoms


def xyz_from_pdb(line: str) -> tuple[float, float, float]:
    return tuple(float(line[start:end]) for start, end in ((30, 38), (38, 46), (46, 54)))


def replace_xyz(line: str, xyz: tuple[float, float, float]) -> str:
    return f"{line[:30]}{xyz[0]:8.3f}{xyz[1]:8.3f}{xyz[2]:8.3f}{line[54:]}"


def local_residues_from_pdb(path: Path, cutoff_angstrom: float = 5.0) -> set[int]:
    atoms = pdb_atoms(path)
    center = [
        xyz_from_pdb(line)
        for (chain, residue, atom), line in atoms.items()
        if chain == "A" and residue == 167 and not atom.startswith("H")
    ]
    return {
        residue
        for (chain, residue, atom), line in atoms.items()
        if chain == "A"
        and not atom.startswith("H")
        and any(math.dist(xyz_from_pdb(line), target) <= cutoff_angstrom for target in center)
    }


def write_exact_backbone(wt_path: Path, mutant_path: Path, output_path: Path) -> None:
    wt = pdb_atoms(wt_path)
    mutant = pdb_atoms(mutant_path)
    mutation_b_factor = wt[("A", 167, "CA")][60:66]
    output: list[str] = []
    for line in mutant_path.read_text().splitlines():
        if not line.startswith("ATOM  "):
            if line.startswith(("TER", "END")):
                output.append(line)
            continue
        chain = line[21].strip()
        residue = int(line[22:26])
        atom = line[12:16].strip()
        key = (chain, residue, atom)
        if atom in BACKBONE and key in wt:
            line = replace_xyz(line, xyz_from_pdb(wt[key]))
        if chain == "A" and residue == 167:
            line = f"{line[:60]}{mutation_b_factor}{line[66:]}"
        output.append(line)
    if not output or not output[-1].startswith("END"):
        output.append("END")
    output_path.write_text("\n".join(output) + "\n")


def parse_gro(path: Path) -> list[tuple[int, str, str, int, tuple[float, float, float]]]:
    lines = path.read_text().splitlines()
    atom_count = int(lines[1].strip())
    atoms = []
    for line in lines[2 : 2 + atom_count]:
        atoms.append(
            (
                int(line[0:5]),
                line[5:10].strip(),
                line[10:15].strip(),
                int(line[15:20]),
                tuple(float(line[start:end]) for start, end in ((20, 28), (28, 36), (36, 44))),
            )
        )
    return atoms


def write_frozen_index(gro_path: Path, index_path: Path) -> None:
    atoms = parse_gro(gro_path)
    center = [
        xyz
        for residue, _resname, atom_name, _atom_number, xyz in atoms
        if residue == 167 and not atom_name.startswith("H")
    ]
    mobile_residues = {
        residue
        for residue, _resname, atom_name, _atom_number, xyz in atoms
        if not atom_name.startswith("H")
        and any(math.dist(xyz, target) <= 0.5 for target in center)
    }
    backbone_with_hydrogens = {"N", "HN", "CA", "HA", "C", "O"}
    frozen = [
        atom_number
        for residue, _resname, atom_name, atom_number, _xyz in atoms
        if not (residue in mobile_residues and atom_name not in backbone_with_hydrogens)
    ]
    lines = ["[ Frozen ]"]
    for start in range(0, len(frozen), 15):
        lines.append(" ".join(str(value) for value in frozen[start : start + 15]))
    index_path.write_text("\n".join(lines) + "\n")


def merge_minimized_sidechain(
    exact_path: Path, minimized_gro_path: Path, output_path: Path
) -> None:
    mobile_residues = local_residues_from_pdb(exact_path)
    minimized_all = {
        (residue, atom_name): tuple(value * 10.0 for value in xyz)
        for residue, _resname, atom_name, _atom_number, xyz in parse_gro(minimized_gro_path)
        if residue in mobile_residues
    }
    exact = pdb_atoms(exact_path)
    shifts = []
    for atom_name in BACKBONE:
        exact_xyz = xyz_from_pdb(exact[("A", 167, atom_name)])
        minimized_xyz = minimized_all[(167, atom_name)]
        shifts.append(tuple(m - e for m, e in zip(minimized_xyz, exact_xyz)))
    shift = tuple(sum(values) / len(values) for values in zip(*shifts))
    minimized = {
        key: tuple(value - delta for value, delta in zip(xyz, shift))
        for key, xyz in minimized_all.items()
    }
    output: list[str] = []
    for line in exact_path.read_text().splitlines():
        if line.startswith("ATOM  ") and int(line[22:26]) in mobile_residues:
            atom_name = line[12:16].strip()
            residue = int(line[22:26])
            if atom_name not in BACKBONE and (residue, atom_name) in minimized:
                line = replace_xyz(line, minimized[(residue, atom_name)])
        output.append(line)
    output_path.write_text("\n".join(output) + "\n")
    print("mobile_residues\t" + ",".join(str(value) for value in sorted(mobile_residues)))


def audit(wt_path: Path, output_path: Path) -> None:
    wt = pdb_atoms(wt_path)
    output = pdb_atoms(output_path)
    assert len(wt) == 3157
    assert len(output) == 3158
    assert all(
        output[("A", 167, atom)][17:20].strip() == "TYR"
        for atom in BACKBONE | {"CB", "CG", "CD1", "CD2", "CE1", "CE2", "CZ", "OH"}
    )
    changed_common = []
    mobile_residues = local_residues_from_pdb(output_path)
    for key in sorted(wt.keys() & output.keys()):
        distance = math.dist(xyz_from_pdb(wt[key]), xyz_from_pdb(output[key]))
        if distance > 0.001:
            changed_common.append((key, distance))
    invalid = [
        (key, distance)
        for key, distance in changed_common
        if not (key[0] == "A" and key[1] in mobile_residues and key[2] not in BACKBONE)
    ]
    if invalid:
        raise SystemExit(f"non-sidechain coordinates changed: {invalid[:10]}")
    print(f"wt_atoms\t{len(wt)}")
    print(f"mutant_atoms\t{len(output)}")
    print(f"changed_common_atoms\t{len(changed_common)}")
    print(f"max_changed_common_A\t{max((d for _, d in changed_common), default=0.0):.6f}")
    print("mobile_residues\t" + ",".join(str(value) for value in sorted(mobile_residues)))
    print("backbone_identity\tPASS")
    print("mutation_identity\tPASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("exact", "index", "merge", "audit"))
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    if args.mode == "exact":
        write_exact_backbone(*args.paths)
    elif args.mode == "index":
        write_frozen_index(*args.paths)
    elif args.mode == "merge":
        merge_minimized_sidechain(*args.paths)
    else:
        audit(*args.paths)


if __name__ == "__main__":
    main()
