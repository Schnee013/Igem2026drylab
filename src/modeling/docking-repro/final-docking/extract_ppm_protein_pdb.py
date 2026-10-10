#!/usr/bin/env python3
"""Extract one unchanged protein chain from a raw PPM PDB."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from parse_tm_topology import (
    InputError,
    MinimalArgumentParser,
    atomic_write_text,
    ensure_distinct_output,
    ensure_output_available,
    read_text_file,
)


@dataclass(frozen=True)
class AtomRecord:
    line_number: int
    line: str
    record_name: str
    serial: int
    atom_name: str
    residue_name: str
    chain: str
    residue_number: int
    insertion_code: str


def _integer_field(raw: str, source: str, line_number: int, field: str) -> int:
    try:
        return int(raw.strip())
    except ValueError as exc:
        raise InputError(
            f"{source}: invalid {field} at line {line_number}: {raw!r}"
        ) from exc


def _decimal_field(raw: str, source: str, line_number: int, field: str) -> None:
    try:
        value = Decimal(raw.strip())
    except InvalidOperation as exc:
        raise InputError(
            f"{source}: invalid {field} at line {line_number}: {raw!r}"
        ) from exc
    if not value.is_finite():
        raise InputError(
            f"{source}: non-finite {field} at line {line_number}: {raw!r}"
        )


def parse_atom_record(line: str, line_number: int, source: str) -> AtomRecord:
    """Validate fixed PDB atom fields while retaining the original line."""
    if len(line) < 66:
        raise InputError(
            f"{source}: {line[0:6].strip()} line {line_number} is shorter than "
            "the B-factor field"
        )
    record_name = line[0:6].strip()
    serial = _integer_field(line[6:11], source, line_number, "atom serial")
    atom_name = line[12:16].strip()
    residue_name = line[17:20].strip()
    if not atom_name:
        raise InputError(f"{source}: empty atom name at line {line_number}")
    if not residue_name:
        raise InputError(f"{source}: empty residue name at line {line_number}")
    residue_number = _integer_field(
        line[22:26], source, line_number, "residue number"
    )
    for field, start, end in (
        ("X coordinate", 30, 38),
        ("Y coordinate", 38, 46),
        ("Z coordinate", 46, 54),
        ("occupancy", 54, 60),
        ("B-factor", 60, 66),
    ):
        _decimal_field(line[start:end], source, line_number, field)
    return AtomRecord(
        line_number=line_number,
        line=line,
        record_name=record_name,
        serial=serial,
        atom_name=atom_name,
        residue_name=residue_name,
        chain=line[21],
        residue_number=residue_number,
        insertion_code=line[26],
    )


def parse_conect(line: str, line_number: int, source: str) -> list[int]:
    """Return every serial referenced by one fixed-column CONECT record."""
    serials: list[int] = []
    for start in range(6, len(line), 5):
        raw = line[start : start + 5]
        if raw.strip():
            serial = _integer_field(raw, source, line_number, "CONECT serial")
            if serial < 1:
                raise InputError(
                    f"{source}: CONECT serial must be positive at line {line_number}"
                )
            serials.append(serial)
    if len(serials) < 2:
        raise InputError(
            f"{source}: CONECT line {line_number} must reference at least two atoms"
        )
    return serials


def describe_hetero(records: list[AtomRecord]) -> str:
    grouped: dict[tuple[str, str, int, str], list[int]] = {}
    for record in records:
        key = (
            record.residue_name,
            record.chain,
            record.residue_number,
            record.insertion_code,
        )
        grouped.setdefault(key, []).append(record.line_number)
    descriptions: list[str] = []
    for (residue, chain, number, insertion), line_numbers in grouped.items():
        chain_text = chain or "<blank>"
        residue_id = f"{number}{insertion.strip()}"
        lines = ", ".join(str(value) for value in line_numbers)
        descriptions.append(
            f"  {residue} chain {chain_text} residue {residue_id}: line(s) {lines}"
        )
    return "\n".join(descriptions)


def extract_records(
    text: str, source: Path, chain: str
) -> tuple[str, int, int, int]:
    """Build and verify the filtered PDB entirely in memory."""
    lines = text.splitlines()
    atom_records: dict[int, AtomRecord] = {}
    serial_lines: dict[int, int] = {}
    selected_atoms: list[AtomRecord] = []
    dum_atoms: list[AtomRecord] = []
    other_hetero: list[AtomRecord] = []

    for line_number, line in enumerate(lines, start=1):
        record_name = line[0:6].strip()
        if record_name not in {"ATOM", "HETATM"}:
            continue
        record = parse_atom_record(line, line_number, str(source))
        if record.serial in serial_lines:
            raise InputError(
                f"{source}: duplicate atom serial {record.serial} at lines "
                f"{serial_lines[record.serial]} and {line_number}"
            )
        serial_lines[record.serial] = line_number
        atom_records[line_number] = record
        if record.residue_name == "DUM":
            dum_atoms.append(record)
        elif record.record_name == "HETATM":
            other_hetero.append(record)
        elif record.chain == chain:
            selected_atoms.append(record)

    if not selected_atoms:
        raise InputError(f"{source}: no protein ATOM records found for chain {chain!r}")
    if not dum_atoms:
        raise InputError(f"{source}: no DUM ATOM or HETATM records found")
    if other_hetero:
        raise InputError(
            f"{source}: non-DUM HETATM records require human review:\n"
            f"{describe_hetero(other_hetero)}"
        )

    selected_serials = {record.serial for record in selected_atoms}
    dum_serials = {record.serial for record in dum_atoms}
    output_lines: list[str] = []
    end_line: str | None = None

    for line_number, line in enumerate(lines, start=1):
        record_name = line[0:6].strip()
        if record_name in {"ATOM", "HETATM"}:
            record = atom_records[line_number]
            if record.serial in selected_serials:
                output_lines.append(line)
        elif record_name == "CONECT":
            references = set(parse_conect(line, line_number, str(source)))
            if references <= dum_serials:
                continue
            if references & dum_serials:
                raise InputError(
                    f"{source}: CONECT line {line_number} mixes DUM and non-DUM "
                    "serials; human review is required"
                )
            excluded = references - selected_serials
            if excluded:
                values = ", ".join(str(value) for value in sorted(excluded))
                raise InputError(
                    f"{source}: CONECT line {line_number} references atom serial(s) "
                    f"outside selected chain {chain!r}: {values}"
                )
            output_lines.append(line)
        elif record_name == "TER" and len(line) > 21 and line[21] == chain:
            output_lines.append(line)
        elif record_name == "END" and end_line is None:
            end_line = line

    output_lines.append(end_line or "END")
    output_text = "\n".join(output_lines) + "\n"
    output_count = verify_output(
        output_text,
        selected_atoms,
        selected_serials,
        dum_serials,
        chain,
    )
    return output_text, len(selected_atoms), len(dum_atoms), output_count


def verify_output(
    output_text: str,
    input_atoms: list[AtomRecord],
    selected_serials: set[int],
    dum_serials: set[int],
    chain: str,
) -> int:
    """Require identical atom lines and coordinates with no DUM remnants."""
    output_atoms: list[AtomRecord] = []
    for line_number, line in enumerate(output_text.splitlines(), start=1):
        record_name = line[0:6].strip()
        if record_name in {"ATOM", "HETATM"}:
            record = parse_atom_record(line, line_number, "generated output")
            if record.record_name != "ATOM" or record.chain != chain:
                raise InputError(
                    "internal verification failed: output contains a non-protein "
                    "or wrong-chain atom"
                )
            if record.residue_name == "DUM":
                raise InputError(
                    "internal verification failed: output still contains DUM"
                )
            output_atoms.append(record)
        elif record_name == "CONECT":
            references = set(parse_conect(line, line_number, "generated output"))
            if references & dum_serials or not references <= selected_serials:
                raise InputError(
                    "internal verification failed: output CONECT has an invalid "
                    "atom reference"
                )

    if len(output_atoms) != len(input_atoms):
        raise InputError(
            "internal verification failed: input/output protein atom counts differ"
        )
    for index, (input_atom, output_atom) in enumerate(
        zip(input_atoms, output_atoms, strict=True), start=1
    ):
        if input_atom.line[30:54] != output_atom.line[30:54]:
            raise InputError(
                f"internal verification failed: coordinates differ at atom {index}"
            )
        if input_atom.line != output_atom.line:
            raise InputError(
                f"internal verification failed: atom record differs at atom {index}"
            )
    return len(output_atoms)


def validate_chain(chain: str) -> None:
    if len(chain) != 1 or not chain.isascii() or not chain.isalnum():
        raise InputError("--chain must be one alphanumeric PDB chain identifier")


def build_parser() -> MinimalArgumentParser:
    template = (
        "extract_ppm_protein_pdb.py --input <ppm.pdb> --chain <chain> "
        "--output <receptor.pdb> [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Extract one protein chain from a raw PPM PDB without changing any "
            "protein atom record or coordinate."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Input requirements:\n"
            "  readable fixed-column PDB with protein ATOM and at least one DUM\n"
            "  any non-DUM HETATM stops extraction for human review\n\n"
            "Call template:\n"
            f"  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--input", required=True, type=Path, help="raw PPM PDB")
    required.add_argument("--chain", required=True, help="one PDB chain identifier")
    required.add_argument(
        "--output", required=True, type=Path, help="output receptor PDB"
    )
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument(
        "--force", action="store_true", help="overwrite an existing output"
    )
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_path = args.input.expanduser()
    output_path = args.output.expanduser()
    try:
        ensure_distinct_output(output_path, (("--input", input_path),))
        ensure_output_available(output_path, args.force)
        validate_chain(args.chain)
        text = read_text_file(input_path, "PPM PDB")
        output_text, input_count, dum_count, output_count = extract_records(
            text, input_path, args.chain
        )
        atomic_write_text(output_path, output_text, args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"input_protein_atoms={input_count}")
    print(f"removed_dum_atoms={dum_count}")
    print(f"output_protein_atoms={output_count}")
    write_tool_result([ToolArtifact(output_path, "PPM 蛋白结构")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
