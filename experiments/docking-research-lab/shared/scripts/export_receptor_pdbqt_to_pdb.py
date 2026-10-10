#!/usr/bin/env python3
"""Export an AutoDock receptor PDBQT pose to prepared PDB for Maestro LID."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from atomic_publish import publish_staged_file
from docking_tool_result import ToolArtifact, write_tool_result


COORDINATE_TOLERANCE_ANGSTROM = 0.0001
AUTODOCK_ELEMENTS = {
    "A": "C",
    "B": "B",
    "BR": "Br",
    "C": "C",
    "CA": "Ca",
    "CL": "Cl",
    "CO": "Co",
    "CU": "Cu",
    "F": "F",
    "FE": "Fe",
    "H": "H",
    "HD": "H",
    "HS": "H",
    "I": "I",
    "MG": "Mg",
    "MN": "Mn",
    "N": "N",
    "NA": "N",
    "NI": "Ni",
    "NS": "N",
    "O": "O",
    "OA": "O",
    "OS": "O",
    "P": "P",
    "S": "S",
    "SA": "S",
    "SI": "Si",
    "ZN": "Zn",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert receptor .pdbqt to prepared .pdb while preserving atom "
            "order and coordinates."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python src/export_receptor_pdbqt_to_pdb.py "
            "--input receptor.pdbqt --output receptor.pdb\n\n"
            "Coordinate handling:\n"
            "  The output keeps each atom coordinate within "
            f"{COORDINATE_TOLERANCE_ANGSTROM:g} angstrom."
        ),
    )
    parser.add_argument(
        "--input", required=True, type=Path, help="source receptor .pdbqt"
    )
    parser.add_argument("--output", required=True, type=Path, help="target receptor .pdb")
    parser.add_argument(
        "--overwrite", action="store_true", help="replace an existing output file"
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _validate_paths(source: Path, target: Path, overwrite: bool) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"input file not found: {source}")
    if source.suffix.lower() != ".pdbqt":
        raise ValueError("input filename must end in .pdbqt")
    if target.suffix.lower() != ".pdb":
        raise ValueError("output filename must end in .pdb")
    if target.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {target} (use --overwrite)")


def pdbqt_atom_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith(("ATOM  ", "HETATM")):
            if len(line) < 78:
                raise ValueError(f"short PDBQT atom line at {path}:{line_number}")
            try:
                records.append(
                    {
                        "serial": int(line[6:11]),
                        "name": line[12:16].strip(),
                        "coord": tuple(
                            float(line[start:end])
                            for start, end in ((30, 38), (38, 46), (46, 54))
                        ),
                        "autodock_type": line[77:].strip(),
                        "line": line,
                    }
                )
            except ValueError as error:
                raise ValueError(
                    f"invalid PDBQT atom line at {path}:{line_number}"
                ) from error
    if not records:
        raise ValueError(f"no ATOM/HETATM records found in {path}")
    return records


def pdbqt_element(autodock_type: str, atom_name: str) -> str:
    atom_type = autodock_type.upper()
    try:
        return AUTODOCK_ELEMENTS[atom_type]
    except KeyError as error:
        raise ValueError(
            f"unsupported AutoDock atom type {autodock_type!r} for atom {atom_name!r}"
        ) from error


def _pdb_element_field(element: str) -> str:
    return f"{element:>2}"[-2:]


def _pdb_atom_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(("ATOM  ", "HETATM")):
            records.append(
                {
                    "serial": int(line[6:11]),
                    "name": line[12:16].strip(),
                    "coord": tuple(
                        float(line[start:end])
                        for start, end in ((30, 38), (38, 46), (46, 54))
                    ),
                }
            )
    return records


def maximum_coordinate_delta(
    source_records: list[dict[str, Any]], target_records: list[dict[str, Any]]
) -> float:
    deltas = []
    for source, target in zip(source_records, target_records, strict=True):
        if (source["serial"], source["name"]) != (target["serial"], target["name"]):
            raise RuntimeError("conversion changed atom identity or order")
        deltas.append(math.dist(source["coord"], target["coord"]))
    return max(deltas, default=0.0)


def convert_receptor_pdbqt_to_pdb(source: Path, target: Path) -> dict[str, Any]:
    """Strip AutoDock-only columns while retaining every serialized atom and coordinate."""
    source_records = pdbqt_atom_records(source)
    output_lines = []
    for raw_line in source.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith(("ATOM  ", "HETATM")):
            atom_type = raw_line[77:].strip()
            atom_name = raw_line[12:16].strip()
            element = _pdb_element_field(pdbqt_element(atom_type, atom_name))
            output_lines.append(f"{raw_line[:66]:<76}{element}  ")
        elif raw_line.startswith(("TER", "MODEL", "ENDMDL", "END")):
            output_lines.append(raw_line)
    if not output_lines or not output_lines[-1].startswith("END"):
        output_lines.append("END")
    target.write_text("\n".join(output_lines) + "\n", encoding="utf-8")

    converted_records = _pdb_atom_records(target)
    if len(converted_records) != len(source_records):
        raise RuntimeError("receptor conversion changed the atom count")
    maximum_delta = maximum_coordinate_delta(source_records, converted_records)
    if maximum_delta > COORDINATE_TOLERANCE_ANGSTROM:
        raise RuntimeError(
            f"receptor conversion changed coordinates: max_delta={maximum_delta:.6f} Å"
        )
    return {
        "converted": True,
        "source_format": "pdbqt",
        "target_format": "pdb",
        "atom_count": len(source_records),
        "max_coordinate_delta_angstrom": maximum_delta,
    }


def export_receptor(
    source: Path, target: Path, *, overwrite: bool = False
) -> dict[str, Any]:
    source = source.expanduser().resolve()
    target = target.expanduser().resolve()
    _validate_paths(source, target, overwrite)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
        report = convert_receptor_pdbqt_to_pdb(source, temporary_path)
        publish_staged_file(temporary_path, target, overwrite=overwrite)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    return {
        **{key: value for key, value in report.items() if key != "temporary"},
        "source": str(source),
        "output": str(target),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = export_receptor(args.input, args.output, overwrite=args.overwrite)
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    write_tool_result([ToolArtifact(args.output, "导出的受体 PDB")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
