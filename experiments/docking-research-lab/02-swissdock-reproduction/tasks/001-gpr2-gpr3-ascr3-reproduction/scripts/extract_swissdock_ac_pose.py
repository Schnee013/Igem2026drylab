#!/usr/bin/env python3
"""Parse a SwissDock AC dock4 result and export the pre-defined top pose."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


REMARK_RE = re.compile(r"^REMARK\s+(.+?)\s*:\s*(.*?)\s*$")


@dataclass
class Pose:
    source_index: int
    metadata: dict[str, str]
    atom_lines: list[str]

    @property
    def ac_score(self) -> float:
        return float(self.metadata["MEMBER_SCORE"])


def parse_dock4(path: Path) -> list[Pose]:
    poses: list[Pose] = []
    metadata: dict[str, str] | None = None
    atom_lines: list[str] = []

    for raw_line in path.read_text().splitlines():
        if raw_line.startswith("REMARK FILE_NAME"):
            if metadata is not None:
                poses.append(Pose(len(poses) + 1, metadata, atom_lines))
            metadata = {}
            atom_lines = []

        if metadata is None:
            continue

        match = REMARK_RE.match(raw_line)
        if match:
            metadata[match.group(1).strip()] = match.group(2).strip()
        elif raw_line.startswith(("ATOM  ", "HETATM")):
            atom_lines.append(raw_line)

    if metadata is not None:
        poses.append(Pose(len(poses) + 1, metadata, atom_lines))

    if not poses:
        raise ValueError(f"No poses found in {path}")
    for pose in poses:
        if "MEMBER_SCORE" not in pose.metadata or not pose.atom_lines:
            raise ValueError(f"Incomplete pose {pose.source_index} in {path}")
    return poses


def value(pose: Pose, key: str) -> str:
    return pose.metadata.get(key, "")


def atom_from_dock4(line: str) -> tuple[str, float, float, float, str]:
    fields = line.split()
    if len(fields) < 8:
        raise ValueError(f"Cannot parse atom line: {line}")
    atom_name = fields[2]
    x, y, z = map(float, fields[5:8])
    letters = "".join(char for char in atom_name if char.isalpha())
    element = (letters[:1] or "X").upper()
    return atom_name, x, y, z, element


def pdb_atom_line(
    serial: int,
    atom_name: str,
    x: float,
    y: float,
    z: float,
    element: str,
) -> str:
    return (
        f"HETATM{serial:5d} {atom_name:>4s} LIG L{1:4d}    "
        f"{x:8.3f}{y:8.3f}{z:8.3f}{1.00:6.2f}{0.00:6.2f}"
        f"          {element:>2s}  "
    )


def ligand_lines(pose: Pose, starting_serial: int = 1) -> list[str]:
    output: list[str] = []
    for offset, line in enumerate(pose.atom_lines):
        atom_name, x, y, z, element = atom_from_dock4(line)
        output.append(
            pdb_atom_line(starting_serial + offset, atom_name, x, y, z, element)
        )
    return output


def write_scores(path: Path, ranked: list[Pose]) -> None:
    fields = [
        "score_rank",
        "source_pose_index",
        "cluster_num",
        "cluster_member",
        "file_name",
        "ac_score",
        "sp_dg",
        "member_energy",
        "polar",
        "nonpolar",
        "inter",
        "polar15",
        "rmsd",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for rank, pose in enumerate(ranked, 1):
            writer.writerow(
                {
                    "score_rank": rank,
                    "source_pose_index": pose.source_index,
                    "cluster_num": value(pose, "CLUSTER_NUM"),
                    "cluster_member": value(pose, "CLUSTER_MEMBER"),
                    "file_name": value(pose, "FILE_NAME"),
                    "ac_score": value(pose, "MEMBER_SCORE"),
                    "sp_dg": value(pose, "SP-dG"),
                    "member_energy": value(pose, "MEMBER_ENERGY"),
                    "polar": value(pose, "Polar"),
                    "nonpolar": value(pose, "Nonpolar"),
                    "inter": value(pose, "Inter"),
                    "polar15": value(pose, "Polar15"),
                    "rmsd": value(pose, "RMSD"),
                }
            )


def write_ligand(path: Path, pose: Pose) -> None:
    remarks = [
        "REMARK Selected by minimum SwissDock AC MEMBER_SCORE",
        f"REMARK FILE_NAME {value(pose, 'FILE_NAME')}",
        f"REMARK CLUSTER_NUM {value(pose, 'CLUSTER_NUM')}",
        f"REMARK CLUSTER_MEMBER {value(pose, 'CLUSTER_MEMBER')}",
        f"REMARK AC_SCORE {value(pose, 'MEMBER_SCORE')}",
        f"REMARK SP_DG {value(pose, 'SP-dG')}",
    ]
    path.write_text("\n".join(remarks + ligand_lines(pose) + ["TER", "END", ""]))


def write_complex(path: Path, receptor: Path, pose: Pose) -> None:
    receptor_atoms = [
        line
        for line in receptor.read_text().splitlines()
        if line.startswith(("ATOM  ", "HETATM"))
    ]
    if not receptor_atoms:
        raise ValueError(f"No receptor atoms found in {receptor}")
    max_serial = max(int(line[6:11]) for line in receptor_atoms)
    remarks = [
        "REMARK Receptor coordinates and pLDDT copied from the frozen AF2 PDB",
        "REMARK Ligand pose selected by minimum SwissDock AC MEMBER_SCORE",
        f"REMARK FILE_NAME {value(pose, 'FILE_NAME')}",
        f"REMARK CLUSTER_NUM {value(pose, 'CLUSTER_NUM')}",
        f"REMARK CLUSTER_MEMBER {value(pose, 'CLUSTER_MEMBER')}",
        f"REMARK AC_SCORE {value(pose, 'MEMBER_SCORE')}",
        f"REMARK SP_DG {value(pose, 'SP-dG')}",
    ]
    output = remarks + receptor_atoms + ["TER"]
    output.extend(ligand_lines(pose, max_serial + 1))
    output.extend(["TER", "END", ""])
    path.write_text("\n".join(output))


def write_report(path: Path, dock4: Path, poses: list[Pose], selected: Pose) -> None:
    cluster_count = len({value(pose, "CLUSTER_NUM") for pose in poses})
    text = f"""# SwissDock AC representative-pose selection

- Source: `{dock4}`
- Returned poses: {len(poses)}
- Returned clusters: {cluster_count}
- Frozen selection rule: minimum AC `MEMBER_SCORE`; source order breaks exact ties
- Selected source pose: {selected.source_index}
- Selected file: `{value(selected, 'FILE_NAME')}`
- Cluster/member: {value(selected, 'CLUSTER_NUM')}/{value(selected, 'CLUSTER_MEMBER')}
- AC score: {value(selected, 'MEMBER_SCORE')}
- SwissParam SP-dG: {value(selected, 'SP-dG')} kcal/mol

The pose was selected before checking its location, contacts, or agreement with the
literature. SP-dG was not used for pose selection.
"""
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dock4", type=Path, required=True)
    parser.add_argument("--receptor", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    poses = parse_dock4(args.dock4)
    ranked = sorted(poses, key=lambda pose: (pose.ac_score, pose.source_index))
    selected = ranked[0]

    write_scores(args.out_dir / f"{args.prefix}_all_poses.tsv", ranked)
    write_ligand(args.out_dir / f"{args.prefix}_selected_ligand.pdb", selected)
    write_complex(
        args.out_dir / f"{args.prefix}_selected_complex.pdb", args.receptor, selected
    )
    write_report(args.out_dir / f"{args.prefix}_selection.md", args.dock4, poses, selected)

    print(f"Parsed poses: {len(poses)}")
    print(f"Selected AC score: {selected.ac_score:.6f}")
    print(f"Selected file: {value(selected, 'FILE_NAME')}")
    print(f"Output directory: {args.out_dir}")


if __name__ == "__main__":
    main()
