#!/usr/bin/env python3
"""Compare raw and relaxed PDB coordinates under an explicit atom contract."""

from __future__ import annotations

import json
import math
import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from parse_tm_topology import InputError, MinimalArgumentParser, atomic_write_text, ensure_output_available, read_text_file


BACKBONE = {"N", "CA", "C", "O"}


@dataclass(frozen=True)
class Atom:
    key: tuple[str, int, str, str, str]
    xyz: tuple[float, float, float]


def _coord(raw: str, source: str, line_number: int, field: str) -> float:
    try:
        value = float(raw.strip())
    except ValueError as exc:
        raise InputError(f"{source}: invalid {field} at line {line_number}: {raw!r}") from exc
    if not math.isfinite(value):
        raise InputError(f"{source}: non-finite {field} at line {line_number}: {raw!r}")
    return value


def _selected(atom_name: str, element: str, selection: str) -> bool:
    if selection == "all-heavy":
        return element.upper() != "H" and not atom_name.upper().startswith("H")
    if selection == "ca-only":
        return atom_name.upper() == "CA"
    if selection == "backbone":
        return atom_name.upper() in BACKBONE
    raise InputError(f"unsupported --atom-selection: {selection!r}")


def parse_pdb_atoms(path: Path, selection: str) -> list[Atom]:
    text = read_text_file(path, "PDB structure")
    atoms: list[Atom] = []
    seen: set[tuple[str, int, str, str, str]] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line[0:6].strip() != "ATOM":
            continue
        if len(line) < 78:
            raise InputError(f"{path}: ATOM line {line_number} is shorter than the element field")
        atom_name = line[12:16].strip()
        altloc = line[16].strip()
        if altloc:
            raise InputError(f"{path}: alternate location at line {line_number} is unsupported")
        residue = line[17:20].strip()
        chain = line[21].strip()
        try:
            number = int(line[22:26].strip())
        except ValueError as exc:
            raise InputError(f"{path}: invalid residue number at line {line_number}") from exc
        insertion = line[26].strip()
        element = line[76:78].strip()
        if not _selected(atom_name, element, selection):
            continue
        key = (chain, number, insertion, residue, atom_name)
        if key in seen:
            raise InputError(f"{path}: duplicate selected atom key at line {line_number}: {key}")
        seen.add(key)
        atoms.append(
            Atom(
                key=key,
                xyz=(
                    _coord(line[30:38], str(path), line_number, "X coordinate"),
                    _coord(line[38:46], str(path), line_number, "Y coordinate"),
                    _coord(line[46:54], str(path), line_number, "Z coordinate"),
                ),
            )
        )
    if not atoms:
        raise InputError(f"{path}: no atoms matched --atom-selection {selection!r}")
    return atoms


def _centroid(points: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    count = len(points)
    return tuple(sum(point[index] for point in points) / count for index in range(3))  # type: ignore[return-value]


def _rotation_from_quaternion(q: list[float]) -> list[list[float]]:
    w, x, y, z = q
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ]


def _largest_eigenvector_symmetric(matrix: list[list[float]]) -> list[float]:
    a = [row[:] for row in matrix]
    vectors = [[1.0 if row == col else 0.0 for col in range(4)] for row in range(4)]
    for _ in range(80):
        p, q = 0, 1
        largest = abs(a[p][q])
        for row in range(4):
            for col in range(row + 1, 4):
                value = abs(a[row][col])
                if value > largest:
                    p, q, largest = row, col, value
        if largest <= 1e-14:
            break

        app = a[p][p]
        aqq = a[q][q]
        apq = a[p][q]
        if apq == 0.0:
            continue
        tau = (aqq - app) / (2.0 * apq)
        sign = 1.0 if tau >= 0.0 else -1.0
        tangent = sign / (abs(tau) + math.sqrt(1.0 + tau * tau))
        cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
        sine = tangent * cosine

        for index in range(4):
            if index in {p, q}:
                continue
            aip = a[index][p]
            aiq = a[index][q]
            a[index][p] = a[p][index] = cosine * aip - sine * aiq
            a[index][q] = a[q][index] = sine * aip + cosine * aiq

        a[p][p] = cosine * cosine * app - 2.0 * sine * cosine * apq + sine * sine * aqq
        a[q][q] = sine * sine * app + 2.0 * sine * cosine * apq + cosine * cosine * aqq
        a[p][q] = a[q][p] = 0.0

        for index in range(4):
            vip = vectors[index][p]
            viq = vectors[index][q]
            vectors[index][p] = cosine * vip - sine * viq
            vectors[index][q] = sine * vip + cosine * viq

    column = max(range(4), key=lambda index: a[index][index])
    eigenvector = [vectors[row][column] for row in range(4)]
    norm = math.sqrt(sum(value * value for value in eigenvector))
    if norm == 0.0:
        return [1.0, 0.0, 0.0, 0.0]
    eigenvector = [value / norm for value in eigenvector]
    if eigenvector[0] < 0.0:
        eigenvector = [-value for value in eigenvector]
    return eigenvector


def best_fit_rotation(raw: list[tuple[float, float, float]], relaxed: list[tuple[float, float, float]]) -> list[list[float]]:
    sxx = sxy = sxz = syx = syy = syz = szx = szy = szz = 0.0
    for a, b in zip(raw, relaxed, strict=True):
        ax, ay, az = a
        bx, by, bz = b
        sxx += bx * ax
        sxy += bx * ay
        sxz += bx * az
        syx += by * ax
        syy += by * ay
        syz += by * az
        szx += bz * ax
        szy += bz * ay
        szz += bz * az
    trace = sxx + syy + szz
    matrix = [
        [trace, syz - szy, szx - sxz, sxy - syx],
        [syz - szy, sxx - syy - szz, sxy + syx, szx + sxz],
        [szx - sxz, sxy + syx, -sxx + syy - szz, syz + szy],
        [sxy - syx, szx + sxz, syz + szy, -sxx - syy + szz],
    ]
    return _rotation_from_quaternion(_largest_eigenvector_symmetric(matrix))


def _apply(rotation: list[list[float]], point: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(sum(rotation[row][col] * point[col] for col in range(3)) for row in range(3))  # type: ignore[return-value]


def compare(raw_path: Path, relaxed_path: Path, selection: str) -> dict[str, object]:
    raw_atoms = parse_pdb_atoms(raw_path, selection)
    relaxed_atoms = parse_pdb_atoms(relaxed_path, selection)
    raw_keys = [atom.key for atom in raw_atoms]
    relaxed_keys = [atom.key for atom in relaxed_atoms]
    if raw_keys != relaxed_keys:
        raise InputError("raw and relaxed selected atom keys differ; no atoms are discarded")
    raw_xyz = [atom.xyz for atom in raw_atoms]
    relaxed_xyz = [atom.xyz for atom in relaxed_atoms]
    raw_center = _centroid(raw_xyz)
    relaxed_center = _centroid(relaxed_xyz)
    raw_centered = [tuple(point[i] - raw_center[i] for i in range(3)) for point in raw_xyz]
    relaxed_centered = [tuple(point[i] - relaxed_center[i] for i in range(3)) for point in relaxed_xyz]
    rotation = best_fit_rotation(raw_centered, relaxed_centered)
    distances: list[float] = []
    for raw_point, relaxed_point in zip(raw_centered, relaxed_centered, strict=True):
        fitted = _apply(rotation, relaxed_point)
        distances.append(math.sqrt(sum((fitted[index] - raw_point[index]) ** 2 for index in range(3))))
    return {
        "raw_file": str(raw_path.resolve()),
        "relaxed_file": str(relaxed_path.resolve()),
        "atom_selection": selection,
        "alignment": "least-squares-superposition-selected-atoms",
        "atom_count": len(raw_atoms),
        "rmsd": math.sqrt(sum(distance * distance for distance in distances) / len(distances)),
        "max_displacement": max(distances),
        "scope": (
            "This report presents numeric coordinate differences after superposition. "
            "It does not decide whether the relaxed structure is suitable for use."
        ),
    }


def build_parser() -> MinimalArgumentParser:
    template = (
        "compare_raw_relaxed.py --raw <raw.pdb> --relaxed <relaxed.pdb> "
        "--atom-selection <all-heavy|ca-only|backbone> --output <report.json> [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Superpose raw and relaxed PDB structures using the explicit selected "
            "atom set, then report RMSD and maximum displacement in angstrom. "
            "Mismatched atoms stop the run; no atoms are silently discarded."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Call template:\n  {template}",
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--raw", required=True, type=Path, help="raw input PDB")
    required.add_argument("--relaxed", required=True, type=Path, help="relaxed input PDB")
    required.add_argument("--atom-selection", required=True, choices=("all-heavy", "ca-only", "backbone"), help="explicit atom set used for alignment and displacement")
    required.add_argument("--output", required=True, type=Path, help="JSON comparison report")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--force", action="store_true", help="overwrite an existing output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output_path = args.output.expanduser()
    try:
        if output_path.resolve() in {args.raw.expanduser().resolve(), args.relaxed.expanduser().resolve()}:
            raise InputError("--output must differ from --raw and --relaxed")
        ensure_output_available(output_path, args.force)
        result = compare(args.raw.expanduser(), args.relaxed.expanduser(), args.atom_selection)
        atomic_write_text(output_path, json.dumps(result, indent=2, sort_keys=True) + "\n", args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output_path}")
    write_tool_result([ToolArtifact(output_path, "结构比较报告")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
