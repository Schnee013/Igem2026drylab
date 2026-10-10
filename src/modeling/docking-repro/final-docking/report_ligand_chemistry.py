#!/usr/bin/env python3
"""Report observable ligand chemistry facts from an SDF file."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from atomic_publish import publish_staged_file
from docking_tool_result import ToolArtifact, write_tool_result


V2000_CHARGE_CODES = {
    0: 0,
    1: 3,
    2: 2,
    3: 1,
    4: 0,  # Doublet radical; this code does not itself carry formal charge.
    5: -1,
    6: -2,
    7: -3,
}
# Atom-line stereo parity codes: 0 = not a stereocenter, 1 = odd, 2 = even,
# 3 = either (stereo present in the drawing but unspecified). Code 3 is the
# value that most deserves a manual look, so the report keeps it visible.
V2000_STEREO_PARITY_CODES = {0, 1, 2, 3}


class CliError(ValueError):
    """User-correctable CLI or input error."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, f"Error: {message}\nUse -h or --help for details.\n")


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        description=(
            "Report observable ligand facts from an SDF V2000 record: atoms, "
            "formal charge records, bond orders, stereo flags, hydrogens, and "
            "coordinates. This command does not choose a tautomer or microstate."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python src/report_ligand_chemistry.py --ligand-sdf ligand.sdf
  python src/report_ligand_chemistry.py --ligand-sdf ligand.sdf --format json --output ligand_chemistry.json
""",
    )
    parser.add_argument("--ligand-sdf", required=True, type=Path, help="Input ligand SDF file.")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Report format for stdout or --output (visible default: text).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional report file: .txt for text or .json for json. Existing files are refused unless --overwrite is set.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing --output. Without this flag, existing outputs are refused.",
    )
    return parser


def _read_required_text(path: Path, label: str) -> str:
    if not path.exists():
        raise CliError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise CliError(f"{label} is not a regular file: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CliError(f"{label} is not UTF-8 text: {path} ({exc})") from exc
    except OSError as exc:
        raise CliError(f"{label} is not readable: {path} ({exc})") from exc


def _resolved(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _validate_output_path(output: Path | None, input_path: Path, report_format: str) -> None:
    if output is None:
        return
    if _resolved(output) == _resolved(input_path):
        raise CliError("--output must not be the same path as --ligand-sdf")
    expected_suffix = ".json" if report_format == "json" else ".txt"
    if output.suffix.casefold() != expected_suffix:
        raise CliError(
            f"--format {report_format} requires --output to end with {expected_suffix}: {output}"
        )


def _numeric_error(path: Path, row: int, field: str, value: object, kind: str) -> CliError:
    return CliError(f"{path}: row {row} field {field!r} has invalid {kind} value {value!r}")


def _parse_int(value: object, path: Path, row: int, field: str) -> int:
    if isinstance(value, bool):
        raise _numeric_error(path, row, field, value, "integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise _numeric_error(path, row, field, value, "integer") from exc


def _parse_float(value: object, path: Path, row: int, field: str) -> float:
    if isinstance(value, bool):
        raise _numeric_error(path, row, field, value, "number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise _numeric_error(path, row, field, value, "number") from exc
    if not math.isfinite(parsed):
        raise _numeric_error(path, row, field, value, "finite number")
    return parsed


def _parse_counts_line(line: str, path: Path) -> tuple[int, int]:
    if len(line) < 6:
        raise CliError(f"{path}: row 4 field 'counts' has invalid V2000 value {line!r}")
    atom_count = _parse_int(line[0:3], path, 4, "atom_count")
    bond_count = _parse_int(line[3:6], path, 4, "bond_count")
    if atom_count < 0:
        raise _numeric_error(path, 4, "atom_count", line[0:3], "non-negative integer")
    if bond_count < 0:
        raise _numeric_error(path, 4, "bond_count", line[3:6], "non-negative integer")
    return atom_count, bond_count


def parse_sdf_v2000(path: Path) -> dict[str, Any]:
    text = _read_required_text(path, "ligand SDF")
    records = text.split("$$$$")
    first = records[0].splitlines()
    if len(first) < 4:
        raise CliError(f"{path}: SDF record is shorter than the V2000 header")
    atom_count, bond_count = _parse_counts_line(first[3], path)
    expected_lines = 4 + atom_count + bond_count
    if len(first) < expected_lines:
        raise CliError(
            f"{path}: SDF record ended before declared atoms/bonds were present "
            f"(atoms={atom_count}, bonds={bond_count})"
        )

    atoms = []
    for index, line in enumerate(first[4 : 4 + atom_count], start=1):
        row = index + 4
        fields = line.split()
        if len(fields) < 4:
            raise CliError(f"{path}: row {row} field 'atom' has invalid value {line!r}: fewer than 4 fields")
        x = _parse_float(fields[0], path, row, "x")
        y = _parse_float(fields[1], path, row, "y")
        z = _parse_float(fields[2], path, row, "z")
        # Charge code and stereo parity sit in fixed columns (1-indexed: 37-39
        # and 40-42); whitespace splitting is not reliable here because the
        # optional mass-difference column (35-36) shifts the field count.
        charge_code = _parse_int(
            line[36:39].strip(), path, row, "charge_code"
        ) if len(line) >= 39 and line[36:39].strip() else 0
        if charge_code not in V2000_CHARGE_CODES:
            raise _numeric_error(path, row, "charge_code", line[36:39], "V2000 charge code 0-7")
        stereo_parity = _parse_int(
            line[39:42].strip(), path, row, "stereo_parity"
        ) if len(line) >= 42 and line[39:42].strip() else 0
        if stereo_parity not in V2000_STEREO_PARITY_CODES:
            raise _numeric_error(path, row, "stereo_parity", line[39:42], "V2000 stereo parity code 0-3")
        atoms.append(
            {
                "index": index,
                "element": fields[3],
                "x": x,
                "y": y,
                "z": z,
                "charge_code": charge_code,
                "atom_block_formal_charge": V2000_CHARGE_CODES[charge_code],
                "stereo_parity": stereo_parity,
            }
        )

    bonds = []
    for index, line in enumerate(first[4 + atom_count : expected_lines], start=1):
        row = 4 + atom_count + index
        fields = line.split()
        if len(fields) < 3:
            raise CliError(f"{path}: row {row} field 'bond' has invalid value {line!r}: fewer than 3 fields")
        atom_1 = _parse_int(fields[0], path, row, "atom_1")
        atom_2 = _parse_int(fields[1], path, row, "atom_2")
        order = _parse_int(fields[2], path, row, "order")
        stereo = _parse_int(fields[3], path, row, "stereo") if len(fields) > 3 else 0
        for field, value in (("atom_1", atom_1), ("atom_2", atom_2)):
            if value < 1 or value > atom_count:
                raise CliError(
                    f"{path}: row {row} field {field!r} has out-of-range value {value!r}; "
                    f"declared atom count is {atom_count}"
                )
        bonds.append({"index": index, "atom_1": atom_1, "atom_2": atom_2, "order": order, "stereo": stereo})

    m_chg_records = []
    for row, raw_line in enumerate(first[expected_lines:], start=expected_lines + 1):
        line = raw_line.strip()
        if not line.startswith("M  CHG"):
            continue
        fields = line.split()
        if len(fields) < 4:
            raise CliError(f"{path}: row {row} field 'M_CHG' has invalid value {raw_line!r}: missing fields")
        charge_pairs = _parse_int(fields[2], path, row, "M_CHG_pair_count")
        if charge_pairs < 1:
            raise _numeric_error(path, row, "M_CHG_pair_count", fields[2], "positive integer")
        expected = 3 + charge_pairs * 2
        if len(fields) != expected:
            raise CliError(
                f"{path}: row {row} field 'M_CHG_pairs' has invalid value {fields[3:]!r}; "
                f"declared {charge_pairs} atom/charge pairs"
            )
        for offset in range(3, expected, 2):
            pair_number = (offset - 3) // 2 + 1
            atom = _parse_int(fields[offset], path, row, f"M_CHG_atom_{pair_number}")
            charge = _parse_int(fields[offset + 1], path, row, f"M_CHG_charge_{pair_number}")
            if atom < 1 or atom > atom_count:
                raise CliError(
                    f"{path}: row {row} field 'M_CHG_atom_{pair_number}' has out-of-range value {atom!r}; "
                    f"declared atom count is {atom_count}"
                )
            m_chg_records.append({"atom": atom, "charge": charge, "row": row})

    atom_block_charges = {
        atom["index"]: atom["atom_block_formal_charge"]
        for atom in atoms
        if atom["atom_block_formal_charge"] != 0
    }
    if m_chg_records:
        effective_charges: dict[int, int] = {}
        for record in m_chg_records:
            if record["atom"] in effective_charges:
                raise CliError(
                    f"{path}: row {record['row']} field 'M_CHG_atom' has duplicate value {record['atom']!r}"
                )
            effective_charges[record["atom"]] = record["charge"]
        charge_source = "M_CHG_overrides_atom_block"
    else:
        effective_charges = atom_block_charges
        charge_source = "atom_block_charge_code"

    formal_charges = [
        {"atom": atom, "charge": charge}
        for atom, charge in sorted(effective_charges.items())
        if charge != 0
    ]

    return {
        "atoms": atoms,
        "bonds": bonds,
        "atom_block_formal_charge_records": [
            {"atom": atom, "charge": charge} for atom, charge in sorted(atom_block_charges.items())
        ],
        "m_chg_records": [
            {"atom": record["atom"], "charge": record["charge"]} for record in m_chg_records
        ],
        "formal_charges": formal_charges,
        "formal_charge_source": charge_source,
    }


def _hill_formula(element_counts: Mapping[str, int]) -> str:
    """Hill notation: carbon first, hydrogen second, then alphabetical."""

    if not element_counts:
        return ""
    remaining = dict(element_counts)
    ordered = []
    if "C" in remaining:
        ordered.append(("C", remaining.pop("C")))
        if "H" in remaining:
            ordered.append(("H", remaining.pop("H")))
    ordered.extend(sorted(remaining.items()))
    return "".join(
        element if count == 1 else f"{element}{count}" for element, count in ordered
    )


def _fragment_rows(
    atoms: Sequence[Mapping[str, Any]],
    bonds: Sequence[Mapping[str, Any]],
    formal_charges: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Split the record into bonded fragments.

    More than one fragment means the file carries a salt, counter-ion, or solvent
    alongside the molecule, which is a decision the reviewer has to make before
    docking. Connectivity comes from the bond block alone; SDF has no other
    statement about which atoms belong together.
    """

    atom_count = len(atoms)
    parent = list(range(atom_count + 1))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for bond in bonds:
        left, right = find(bond["atom_1"]), find(bond["atom_2"])
        if left != right:
            parent[right] = left

    groups: dict[int, list[int]] = {}
    for atom in atoms:
        groups.setdefault(find(atom["index"]), []).append(atom["index"])

    charge_by_atom = {item["atom"]: item["charge"] for item in formal_charges}
    element_by_atom = {atom["index"]: atom["element"] for atom in atoms}

    rows = []
    for members in groups.values():
        members.sort()
        element_counts = Counter(element_by_atom[index] for index in members)
        heavy = sum(count for element, count in element_counts.items() if element != "H")
        rows.append(
            {
                "atom_indices": members,
                "atom_count": len(members),
                "heavy_atom_count": heavy,
                "element_counts": dict(sorted(element_counts.items())),
                "formula": _hill_formula(element_counts),
                "formal_charge": sum(charge_by_atom.get(index, 0) for index in members),
            }
        )
    # Largest first: the intended molecule is normally the biggest fragment.
    rows.sort(key=lambda row: (-row["heavy_atom_count"], row["atom_indices"][0]))
    for position, row in enumerate(rows, start=1):
        row["index"] = position
    return rows


def analyze_ligand(path: Path) -> dict[str, Any]:
    parsed = parse_sdf_v2000(path)
    atoms = parsed["atoms"]
    bonds = parsed["bonds"]
    element_counts = Counter(atom["element"] for atom in atoms)
    explicit_h = element_counts.get("H", 0)
    heavy_atoms = [atom for atom in atoms if atom["element"] != "H"]
    coordinate_rows = [
        (atom["x"], atom["y"], atom["z"]) for atom in atoms
    ]
    nonzero_coordinates = any(any(value != 0.0 for value in row) for row in coordinate_rows)
    bond_orders = Counter(str(bond["order"]) for bond in bonds)
    stereo_bonds = [bond for bond in bonds if bond["stereo"] != 0]
    stereo_atoms = [atom for atom in atoms if atom["stereo_parity"] != 0]
    total_formal_charge = sum(item["charge"] for item in parsed["formal_charges"])
    fragments = _fragment_rows(atoms, bonds, parsed["formal_charges"])
    return {
        "source_file": str(path),
        "atom_count": len(atoms),
        "heavy_atom_count": len(heavy_atoms),
        "explicit_hydrogen_atom_count": explicit_h,
        "element_counts": dict(sorted(element_counts.items())),
        "bond_count": len(bonds),
        "bond_order_counts": dict(sorted(bond_orders.items())),
        "atom_block_formal_charge_records": parsed["atom_block_formal_charge_records"],
        "m_chg_records": parsed["m_chg_records"],
        "formal_charge_records": parsed["formal_charges"],
        "formal_charge_source": parsed["formal_charge_source"],
        "total_formal_charge_from_records": total_formal_charge,
        "fragment_count": len(fragments),
        "fragments": fragments,
        "stereo_bond_count": len(stereo_bonds),
        "stereo_bonds": stereo_bonds,
        "atom_stereo_parity_count": len(stereo_atoms),
        "atom_stereo_parities": stereo_atoms,
        "coordinates_present": bool(atoms),
        "any_nonzero_coordinate": nonzero_coordinates,
        "scope": (
            "This report lists chemistry features present in the input structure. "
            "It does not choose a tautomer, protomer, or conformer and does not "
            "decide docking readiness."
        ),
    }


def render_report(report: dict[str, Any], report_format: str) -> str:
    if report_format == "json":
        return json.dumps(report, indent=2, sort_keys=True) + "\n"
    lines = [
        "Ligand chemistry observable facts",
        f"source_file: {report['source_file']}",
        f"atom_count: {report['atom_count']}",
        f"heavy_atom_count: {report['heavy_atom_count']}",
        f"explicit_hydrogen_atom_count: {report['explicit_hydrogen_atom_count']}",
        f"element_counts: {json.dumps(report['element_counts'], sort_keys=True)}",
        f"bond_count: {report['bond_count']}",
        f"bond_order_counts: {json.dumps(report['bond_order_counts'], sort_keys=True)}",
        f"formal_charge_source: {report['formal_charge_source']}",
        f"total_formal_charge_from_records: {report['total_formal_charge_from_records']}",
        f"fragment_count: {report['fragment_count']}",
        "fragments:",
    ]
    for fragment in report["fragments"]:
        lines.append(
            f"  - #{fragment['index']} {fragment['formula']} "
            f"heavy_atoms={fragment['heavy_atom_count']} "
            f"formal_charge={fragment['formal_charge']} "
            f"atom_indices={fragment['atom_indices']}"
        )
    lines += [
        f"stereo_bond_count: {report['stereo_bond_count']}",
        f"atom_stereo_parity_count: {report['atom_stereo_parity_count']}",
        f"coordinates_present: {report['coordinates_present']}",
        f"any_nonzero_coordinate: {report['any_nonzero_coordinate']}",
        f"scope: {report['scope']}",
    ]
    return "\n".join(lines) + "\n"


def _atomic_write(path: Path, text: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise CliError(f"--output already exists: {path}; use --overwrite to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        try:
            publish_staged_file(tmp_path, path, overwrite=overwrite)
        except FileExistsError as error:
            raise CliError(
                f"--output already exists: {path}; use --overwrite to replace it"
            ) from error
    finally:
        tmp_path.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _validate_output_path(args.output, args.ligand_sdf, args.format)
        report = analyze_ligand(args.ligand_sdf)
        rendered = render_report(report, args.format)
        if args.output:
            _atomic_write(args.output, rendered, args.overwrite)
        else:
            sys.stdout.write(rendered)
        write_tool_result(
            [ToolArtifact(args.output, "配体化学报告")]
            if args.output is not None
            else ()
        )
        return 0
    except CliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
