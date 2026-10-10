#!/usr/bin/env python3
"""Generate a minimal pre-PPM PyMOL review script from topology JSON."""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path
from typing import Iterator, Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from parse_tm_topology import (
    InputError,
    MinimalArgumentParser,
    atomic_write_text,
    ensure_distinct_output,
    ensure_output_available,
    load_topology_json,
    read_single_fasta,
    read_text_file,
)


AA3_TO_AA1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}
SAFE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
SAFE_CHAIN = re.compile(r"[A-Za-z0-9_]+")
SAFE_COLOR = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_]*|0x[0-9A-Fa-f]{6}|\d+)")
PYMOL_BASE_COLOR = "gray70"
PYMOL_ACCENT_COLOR = "cyan"
TM_COLOR_PALETTE = ("red", "orange", "yellow", "green", "cyan", "blue", "magenta")
DEFAULT_OBJECT_NAME = "receptor"


def validate_object_name(name: str, helix_count: int, *, ppm: bool = False) -> None:
    """Reject names that are unsafe or collide with generated selections."""
    forbidden = {"all", "none"}
    forbidden.update(f"tm{index}" for index in range(1, helix_count + 1))
    if ppm:
        forbidden.update({"z_low", "z_high"})
    if not SAFE_NAME.fullmatch(name) or name.lower() in forbidden:
        raise InputError(
            f"--object-name is not a safe, non-conflicting PyMOL name: {name!r}"
        )


def validate_chain(chain: str) -> None:
    if not SAFE_CHAIN.fullmatch(chain):
        raise InputError(f"--chain is not safe for a PyMOL selection: {chain!r}")


def validate_color(color: str, option: str) -> None:
    if not SAFE_COLOR.fullmatch(color):
        raise InputError(f"{option} is not a safe PyMOL color token: {color!r}")


def parse_tm_colors(raw: str, helix_count: int) -> list[str]:
    colors = [color.strip() for color in raw.split(",")]
    if any(not color for color in colors):
        raise InputError("--tm-colors contains an empty color value")
    if len(colors) != helix_count:
        raise InputError(
            f"--tm-colors provides {len(colors)} color(s), but topology JSON "
            f"contains {helix_count} TM segment(s)"
        )
    for color in colors:
        validate_color(color, "--tm-colors")
    return colors


def default_tm_colors(helix_count: int) -> list[str]:
    """Return the shared PyMOL palette sized to the topology."""
    if helix_count < 1:
        raise InputError("topology must contain at least one TM segment")
    return [TM_COLOR_PALETTE[index % len(TM_COLOR_PALETTE)] for index in range(helix_count)]


def _add_residue(
    residues: dict[int, str],
    *,
    number: int,
    insertion_code: str,
    residue_name: str,
    source: str,
) -> None:
    if insertion_code:
        raise InputError(
            f"{source}: insertion code {insertion_code!r} at residue {number} "
            "makes resi start-end selection unreliable"
        )
    prior = residues.get(number)
    if prior is not None and prior != residue_name:
        raise InputError(
            f"{source}: residue {number} has conflicting names {prior!r} and "
            f"{residue_name!r}"
        )
    residues[number] = residue_name


def _display_chains(chains: set[str]) -> str:
    if not chains:
        return "none"
    return ", ".join("<blank>" if not chain else chain for chain in sorted(chains))


def parse_pdb_residues(text: str, path: Path, chain: str) -> dict[int, str]:
    residues: dict[int, str] = {}
    chains: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line[0:6].strip() != "ATOM":
            continue
        if len(line) < 27:
            raise InputError(f"{path}: PDB ATOM line {line_number} is too short")
        atom_chain = line[21].strip()
        residue_name = line[17:20].strip().upper()
        if residue_name == "DUM":
            continue
        chains.add(atom_chain)
        if atom_chain != chain:
            continue
        raw_number = line[22:26].strip()
        try:
            number = int(raw_number)
        except ValueError as exc:
            raise InputError(
                f"{path}: invalid residue number {raw_number!r} at PDB line {line_number}"
            ) from exc
        _add_residue(
            residues,
            number=number,
            insertion_code=line[26].strip(),
            residue_name=residue_name,
            source=f"{path} line {line_number}",
        )
    if chain not in chains:
        raise InputError(
            f"{path}: chain {chain!r} was not found; ATOM chains found: "
            f"{_display_chains(chains)}"
        )
    return residues


def _cif_tokens(text: str, path: Path) -> Iterator[str]:
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(";"):
            block: list[str] = [line[1:]] if len(line) > 1 else []
            index += 1
            while index < len(lines) and not lines[index].startswith(";"):
                block.append(lines[index])
                index += 1
            if index == len(lines):
                raise InputError(f"{path}: unterminated semicolon-delimited CIF value")
            yield "\n".join(block)
        else:
            lexer = shlex.shlex(line, posix=True)
            lexer.whitespace_split = True
            lexer.commenters = "#"
            try:
                yield from lexer
            except ValueError as exc:
                raise InputError(f"{path}: invalid CIF quoting at line {index + 1}: {exc}") from exc
        index += 1


def _cif_control(token: str) -> bool:
    lowered = token.lower()
    return (
        token.startswith("_")
        or lowered in {"loop_", "stop_", "global_"}
        or lowered.startswith("data_")
        or lowered.startswith("save_")
    )


def parse_cif_residues(text: str, path: Path, chain: str) -> dict[int, str]:
    tokens = list(_cif_tokens(text, path))
    loop_index: int | None = None
    tags: list[str] = []
    data_start = 0
    index = 0
    while index < len(tokens):
        if tokens[index].lower() != "loop_":
            index += 1
            continue
        tag_start = index + 1
        tag_end = tag_start
        while tag_end < len(tokens) and tokens[tag_end].startswith("_"):
            tag_end += 1
        loop_tags = tokens[tag_start:tag_end]
        if any(tag.lower().startswith("_atom_site.") for tag in loop_tags):
            loop_index = index
            tags = loop_tags
            data_start = tag_end
            break
        index = tag_end
    if loop_index is None or not tags:
        raise InputError(f"{path}: no _atom_site loop was found in CIF input")

    columns = {tag.lower(): position for position, tag in enumerate(tags)}

    def column(*names: str) -> int:
        for name in names:
            if name in columns:
                return columns[name]
        raise InputError(
            f"{path}: _atom_site loop is missing required column: "
            f"{' or '.join(names)}"
        )

    group_col = column("_atom_site.group_pdb")
    chain_col = column("_atom_site.auth_asym_id", "_atom_site.label_asym_id")
    number_col = column("_atom_site.auth_seq_id", "_atom_site.label_seq_id")
    name_col = column("_atom_site.auth_comp_id", "_atom_site.label_comp_id")
    insertion_col = columns.get("_atom_site.pdbx_pdb_ins_code")

    width = len(tags)
    rows: list[list[str]] = []
    cursor = data_start
    while cursor < len(tokens) and not _cif_control(tokens[cursor]):
        if cursor + width > len(tokens):
            raise InputError(f"{path}: incomplete row in _atom_site loop")
        row = tokens[cursor : cursor + width]
        if any(_cif_control(token) for token in row):
            raise InputError(f"{path}: incomplete row before the end of _atom_site loop")
        rows.append(row)
        cursor += width
    if not rows:
        raise InputError(f"{path}: _atom_site loop contains no atom rows")

    residues: dict[int, str] = {}
    chains: set[str] = set()
    for row_number, row in enumerate(rows, start=1):
        if row[group_col].upper() != "ATOM":
            continue
        atom_chain = row[chain_col]
        if atom_chain in {".", "?"}:
            atom_chain = ""
        chains.add(atom_chain)
        if atom_chain != chain:
            continue
        raw_number = row[number_col]
        try:
            number = int(raw_number)
        except ValueError as exc:
            raise InputError(
                f"{path}: invalid residue number {raw_number!r} in _atom_site row "
                f"{row_number}"
            ) from exc
        insertion_code = ""
        if insertion_col is not None and row[insertion_col] not in {".", "?"}:
            insertion_code = row[insertion_col]
        _add_residue(
            residues,
            number=number,
            insertion_code=insertion_code,
            residue_name=row[name_col].upper(),
            source=f"{path} _atom_site row {row_number}",
        )
    if chain not in chains:
        raise InputError(
            f"{path}: chain {chain!r} was not found; ATOM chains found: "
            f"{_display_chains(chains)}"
        )
    return residues


def validate_structure_against_fasta(
    path: Path,
    sequence: str,
    chain: str,
    *,
    structure_format: str | None = None,
) -> None:
    """Require exact standard residues numbered 1 through FASTA length."""
    text = read_text_file(path, "structure file")
    if structure_format is None:
        suffix = path.suffix.lower()
        if suffix in {".pdb", ".ent"}:
            structure_format = "pdb"
        elif suffix in {".cif", ".mmcif"}:
            structure_format = "cif"
        else:
            raise InputError(
                f"{path}: unsupported structure suffix {path.suffix!r}; "
                "supported formats are PDB (.pdb/.ent) and mmCIF (.cif/.mmcif)"
            )
    residues = (
        parse_pdb_residues(text, path, chain)
        if structure_format == "pdb"
        else parse_cif_residues(text, path, chain)
    )

    residue_numbers = sorted(residues)
    expected_numbers = list(range(1, len(sequence) + 1))
    if residue_numbers != expected_numbers:
        for position, expected in enumerate(expected_numbers):
            if position >= len(residue_numbers):
                raise InputError(
                    f"{path}: chain {chain!r} is missing residue {expected}; "
                    "FASTA-to-resi numbering is not one-to-one"
                )
            actual = residue_numbers[position]
            if actual != expected:
                if actual > expected:
                    detail = f"missing residue {expected}; next structure residue is {actual}"
                else:
                    detail = f"unexpected structure residue {actual} before expected residue {expected}"
                raise InputError(
                    f"{path}: chain {chain!r} {detail}; FASTA-to-resi numbering "
                    "is not one-to-one"
                )
        extra = residue_numbers[len(expected_numbers)]
        raise InputError(
            f"{path}: chain {chain!r} has extra residue {extra} beyond FASTA "
            f"length {len(sequence)}"
        )

    for position, fasta_residue in enumerate(sequence, start=1):
        residue_name = residues[position]
        structure_residue = AA3_TO_AA1.get(residue_name)
        if structure_residue is None:
            raise InputError(
                f"{path}: chain {chain!r} residue {position} has non-standard "
                f"residue name {residue_name!r}"
            )
        if structure_residue != fasta_residue:
            raise InputError(
                f"{path}: first sequence mismatch at FASTA position / structure "
                f"resi {position}: FASTA {fasta_residue}, structure "
                f"{structure_residue} ({residue_name})"
            )


def pymol_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def protein_selection(object_name: str, chain: str) -> str:
    return f"({object_name} and chain {chain} and polymer.protein)"


def tm_style_lines(
    object_name: str,
    chain: str,
    base_color: str,
    segments: list[dict[str, int]],
    tm_colors: list[str],
) -> list[str]:
    """Build the shared protein and TM-segment display commands."""
    protein = protein_selection(object_name, chain)
    lines = [
        f"show cartoon, {protein}",
        f"color {base_color}, {protein}",
    ]
    for segment, color in zip(segments, tm_colors, strict=True):
        selection_name = f"TM{segment['index']}"
        lines.extend(
            (
                f"select {selection_name}, ({protein} and resi "
                f"{segment['start']}-{segment['end']})",
                f"color {color}, {selection_name}",
            )
        )
    return lines


def build_tm_pml(
    structure_path: Path,
    object_name: str,
    chain: str,
    base_color: str,
    segments: list[dict[str, int]],
    tm_colors: list[str],
) -> str:
    protein = protein_selection(object_name, chain)
    lines = [
        f"load {pymol_quote(str(structure_path.resolve()))}, {object_name}",
        f"hide everything, {object_name}",
        *tm_style_lines(object_name, chain, base_color, segments, tm_colors),
    ]
    lines.append(f"zoom {protein}")
    return "\n".join(lines) + "\n"


def build_parser() -> MinimalArgumentParser:
    template = (
        "make_tm_review_pml.py --structure <pdb_or_cif> --fasta "
        "<single_record_fasta> --topology-json <json> --chain <chain_id> "
        "--output <pml> [--object-name <pymol_object>] "
        "[--base-color <pymol_color>] [--tm-colors <c1,c2,...,cN>] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Generate a minimal pre-PPM PyMOL script after strictly checking "
            "FASTA sequence, residue numbering, chain, topology, and colors."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "可用结构格式：\n"
            "  PDB (.pdb/.ent) and mmCIF (.cif/.mmcif)\n\n"
            "Call template:\n"
            f"  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--structure", required=True, type=Path, help="PDB or mmCIF structure")
    required.add_argument("--fasta", required=True, type=Path, help="single-record FASTA")
    required.add_argument("--topology-json", required=True, type=Path, help="validated topology JSON")
    required.add_argument("--chain", required=True, help="structure chain identifier")
    required.add_argument("--output", required=True, type=Path, help="output PML path")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--object-name", default=DEFAULT_OBJECT_NAME, help=f"safe PyMOL object name (default: {DEFAULT_OBJECT_NAME})")
    optional.add_argument("--base-color", default=PYMOL_BASE_COLOR, help=f"base PyMOL color (default: {PYMOL_BASE_COLOR})")
    optional.add_argument("--tm-colors", help="comma-separated TM colors; defaults to a repeated display palette sized to the topology")
    optional.add_argument("--force", action="store_true", help="overwrite an existing output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    structure_path = args.structure.expanduser()
    fasta_path = args.fasta.expanduser()
    topology_path = args.topology_json.expanduser()
    output_path = args.output.expanduser()
    try:
        ensure_distinct_output(
            output_path,
            (
                ("--structure", structure_path),
                ("--fasta", fasta_path),
                ("--topology-json", topology_path),
            ),
        )
        ensure_output_available(output_path, args.force)
        _, sequence = read_single_fasta(fasta_path)
        topology = load_topology_json(
            topology_path, expected_sequence_length=len(sequence)
        )
        validate_object_name(args.object_name, topology["helix_count"])
        validate_chain(args.chain)
        validate_color(args.base_color, "--base-color")
        colors = (
            parse_tm_colors(args.tm_colors, topology["helix_count"])
            if args.tm_colors is not None
            else default_tm_colors(topology["helix_count"])
        )
        validate_structure_against_fasta(structure_path, sequence, args.chain)
        pml = build_tm_pml(
            structure_path,
            args.object_name,
            args.chain,
            args.base_color,
            topology["tm_segments"],
            colors,
        )
        atomic_write_text(output_path, pml, args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output_path}")
    write_tool_result([ToolArtifact(output_path, "跨膜拓扑审查脚本")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
