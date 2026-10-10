#!/usr/bin/env python3
"""List score-ranked SwissDock AC cluster leaders and simple contact evidence."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
import sys
from pathlib import Path


def load_pose_parser():
    parser_path = Path(__file__).with_name("extract_swissdock_ac_pose.py")
    spec = importlib.util.spec_from_file_location("swissdock_pose_parser", parser_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {parser_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def receptor_heavy_atoms(path: Path) -> list[tuple[str, int, str, float, float, float]]:
    atoms: list[tuple[str, int, str, float, float, float]] = []
    for line in path.read_text().splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        try:
            atom_name = line[12:16].strip()
            residue_name = line[17:20].strip()
            residue_number = int(line[22:26])
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
        except ValueError:
            continue
        if atom_name.startswith("H"):
            continue
        atoms.append((residue_name, residue_number, atom_name, x, y, z))
    if not atoms:
        raise ValueError(f"No receptor atoms found in {path}")
    return atoms


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dock4", type=Path, required=True)
    parser.add_argument("--receptor", type=Path, required=True)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--cutoff", type=float, default=4.5)
    parser.add_argument("--anchor-residue", type=int)
    parser.add_argument("--pocket-center", type=float, nargs=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    pose_parser = load_pose_parser()
    poses = pose_parser.parse_dock4(args.dock4)
    leaders = [pose for pose in poses if pose.metadata.get("CLUSTER_MEMBER") == "1"]
    leaders.sort(key=lambda pose: (pose.ac_score, pose.source_index))
    receptor_atoms = receptor_heavy_atoms(args.receptor)

    fields = [
        "leader_rank",
        "source_pose_index",
        "chimerax_submodel",
        "cluster_num",
        "ac_score",
        "sp_dg",
        "ligand_centroid_to_pocket_A",
        "ligand_min_atom_to_pocket_A",
        "anchor_min_distance_A",
        "contact_residues_4.5A",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for rank, pose in enumerate(leaders[: args.top], 1):
            ligand_atoms: list[tuple[float, float, float]] = []
            for line in pose.atom_lines:
                _, x, y, z, element = pose_parser.atom_from_dock4(line)
                if element != "H":
                    ligand_atoms.append((x, y, z))

            centroid_distance = ""
            minimum_pocket_distance = ""
            if args.pocket_center:
                centroid = tuple(
                    sum(atom[axis] for atom in ligand_atoms) / len(ligand_atoms)
                    for axis in range(3)
                )
                centroid_distance = f"{math.dist(centroid, args.pocket_center):.3f}"
                minimum_pocket_distance = f"{min(math.dist(atom, args.pocket_center) for atom in ligand_atoms):.3f}"

            contacts: dict[tuple[str, int], float] = {}
            anchor_distance: float | None = None
            for residue_name, residue_number, _, x, y, z in receptor_atoms:
                distance = min(
                    math.dist((x, y, z), ligand_atom)
                    for ligand_atom in ligand_atoms
                )
                if distance <= args.cutoff:
                    key = (residue_name, residue_number)
                    contacts[key] = min(distance, contacts.get(key, math.inf))
                if residue_number == args.anchor_residue:
                    anchor_distance = min(anchor_distance or math.inf, distance)

            contact_text = ",".join(
                f"{residue_name}{residue_number}({distance:.2f})"
                for (residue_name, residue_number), distance in sorted(
                    contacts.items(), key=lambda item: item[1]
                )
            )
            writer.writerow(
                {
                    "leader_rank": rank,
                    "source_pose_index": pose.source_index,
                    "chimerax_submodel": f"#2.{pose.source_index}",
                    "cluster_num": pose.metadata.get("CLUSTER_NUM", ""),
                    "ac_score": pose.metadata.get("MEMBER_SCORE", ""),
                    "sp_dg": pose.metadata.get("SP-dG", ""),
                    "ligand_centroid_to_pocket_A": centroid_distance,
                    "ligand_min_atom_to_pocket_A": minimum_pocket_distance,
                    "anchor_min_distance_A": (
                        f"{anchor_distance:.3f}" if anchor_distance is not None else ""
                    ),
                    "contact_residues_4.5A": contact_text,
                }
            )

    print(f"Wrote {min(args.top, len(leaders))} cluster leaders to {args.output}")


if __name__ == "__main__":
    main()
