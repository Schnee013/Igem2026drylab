#!/usr/bin/env python3
"""Generate a minimal PyMOL review script for a raw PPM PDB with DUM planes."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from make_tm_review_pml import (
    PYMOL_BASE_COLOR,
    parse_tm_colors,
    default_tm_colors,
    protein_selection,
    pymol_quote,
    tm_style_lines,
    validate_chain,
    validate_color,
    validate_object_name,
    validate_structure_against_fasta,
)
from parse_tm_topology import (
    InputError,
    MinimalArgumentParser,
    SOURCE_FORMATS,
    atomic_write_text,
    detect_source_format,
    ensure_distinct_output,
    ensure_output_available,
    load_topology_json,
    parse_deeptmhmm_gff3,
    parse_phyre2_memsat_svm,
    read_single_fasta,
    read_text_file,
    validate_topology_json,
)

DEFAULT_PPM_OBJECT_NAME = "ppm_receptor"
DEFAULT_Z_LOW_COLOR = "blue"
DEFAULT_Z_HIGH_COLOR = "yellow"


def parse_topology_source(
    topology_source: Path,
    fasta_path: Path,
    *,
    topology_format: str | None = None,
) -> dict[str, object]:
    """Return validated topology data without writing an intermediate JSON file."""
    fasta_id, sequence = read_single_fasta(fasta_path)
    source_format = topology_format or detect_source_format(topology_source)
    parsed = (
        parse_deeptmhmm_gff3(topology_source)
        if source_format == "deeptmhmm-gff3"
        else parse_phyre2_memsat_svm(topology_source)
    )
    data = {
        "source_format": source_format,
        "source_file": str(topology_source.resolve()),
        "fasta_id": fasta_id,
        "sequence_length": len(sequence),
        "coordinate_system": "1-based-inclusive",
        **parsed,
    }
    return validate_topology_json(
        data,
        source=str(topology_source),
        expected_sequence_length=len(sequence),
    )


def find_dum_planes(path: Path) -> tuple[Decimal, Decimal]:
    """Return exactly two distinct DUM Z coordinates from a PPM PDB."""
    text = read_text_file(path, "PPM PDB")
    planes: set[Decimal] = set()
    invalid_lines: list[int] = []
    dum_count = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line[0:6].strip() not in {"ATOM", "HETATM"}:
            continue
        if len(line) < 20 or line[17:20].strip() != "DUM":
            continue
        dum_count += 1
        if len(line) < 54:
            invalid_lines.append(line_number)
            continue
        try:
            coordinates = tuple(
                Decimal(line[start:end].strip())
                for start, end in ((30, 38), (38, 46), (46, 54))
            )
        except InvalidOperation:
            invalid_lines.append(line_number)
            continue
        if not all(value.is_finite() for value in coordinates):
            invalid_lines.append(line_number)
            continue
        planes.add(coordinates[2])

    discovered = ", ".join(format(value, "f") for value in sorted(planes))
    discovered = f"[{discovered}]"
    if invalid_lines:
        raise InputError(
            f"{path}: DUM coordinate is incomplete or invalid at line(s) "
            f"{', '.join(map(str, invalid_lines))}; valid Z planes found: {discovered}"
        )
    if dum_count == 0:
        raise InputError(f"{path}: no DUM records found; Z planes found: []")
    if len(planes) != 2:
        raise InputError(
            f"{path}: expected exactly 2 distinct DUM Z planes, found "
            f"{len(planes)}: {discovered}"
        )
    z_low, z_high = sorted(planes)
    return z_low, z_high


def build_ppm_pml(
    ppm_path: Path,
    object_name: str,
    chain: str,
    base_color: str,
    segments: list[dict[str, int]],
    tm_colors: list[str],
    z_low_color: str,
    z_high_color: str,
    z_low: Decimal,
    z_high: Decimal,
) -> str:
    protein = protein_selection(object_name, chain)
    midpoint = (z_low + z_high) / Decimal(2)
    midpoint_text = format(midpoint, "f")
    lines = [
        f"load {pymol_quote(str(ppm_path.resolve()))}, {object_name}",
        f"hide everything, {object_name}",
        *tm_style_lines(object_name, chain, base_color, segments, tm_colors),
    ]
    lines.extend(
        (
            f"select z_low, ({object_name} and resn DUM and z < {midpoint_text})",
            f"select z_high, ({object_name} and resn DUM and z > {midpoint_text})",
            "show spheres, z_low",
            "color " + z_low_color + ", z_low",
            "show spheres, z_high",
            "color " + z_high_color + ", z_high",
            f"zoom ({protein} or z_low or z_high)",
        )
    )
    return "\n".join(lines) + "\n"


def build_parser() -> MinimalArgumentParser:
    template = (
        "make_ppm_review_pml.py --ppm-pdb <ppm_out_pdb> --fasta "
        "<single_record_fasta> --topology-source <topology_file> --chain <chain_id> "
        "--output <pml> [--topology-json <legacy_json>] "
        "[--topology-format <source_format>] [--object-name <pymol_object>] "
        "[--base-color <pymol_color>] [--tm-colors <c1,c2,...,cN>] "
        "[--z-low-color <pymol_color>] [--z-high-color <pymol_color>] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Generate a minimal PyMOL script showing validated TM segments and "
            "the two coordinate-sorted DUM planes in a raw PPM 2.0 PDB."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "可用输入：\n"
            "  raw PPM 2.0 PDB retaining DUM records on exactly two Z planes\n\n"
            "拓扑来源默认自动识别；旧 --topology-json 仅用于兼容历史中间产物。\n\n"
            "Call template:\n"
            f"  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--ppm-pdb", required=True, type=Path, help="raw PPM PDB with DUM records")
    required.add_argument("--fasta", required=True, type=Path, help="single-record FASTA")
    required.add_argument("--chain", required=True, help="protein chain identifier")
    required.add_argument("--output", required=True, type=Path, help="output PML path")
    topology = parser.add_mutually_exclusive_group(required=True)
    topology.add_argument("--topology-source", type=Path, help="DeepTMHMM or Phyre topology source")
    topology.add_argument("--topology-json", type=Path, help="legacy validated topology JSON")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--topology-format", choices=SOURCE_FORMATS, help="expert compatibility override for source format")
    optional.add_argument("--object-name", default=DEFAULT_PPM_OBJECT_NAME, help=f"safe PyMOL object name (default: {DEFAULT_PPM_OBJECT_NAME})")
    optional.add_argument("--base-color", default=PYMOL_BASE_COLOR, help=f"base protein color (default: {PYMOL_BASE_COLOR})")
    optional.add_argument("--tm-colors", help="comma-separated TM colors; defaults to a repeated display palette sized to the topology")
    optional.add_argument("--z-low-color", default=DEFAULT_Z_LOW_COLOR, help=f"color for the lower-Z DUM plane (default: {DEFAULT_Z_LOW_COLOR})")
    optional.add_argument("--z-high-color", default=DEFAULT_Z_HIGH_COLOR, help=f"color for the higher-Z DUM plane (default: {DEFAULT_Z_HIGH_COLOR})")
    optional.add_argument("--force", action="store_true", help="overwrite an existing output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ppm_path = args.ppm_pdb.expanduser()
    fasta_path = args.fasta.expanduser()
    topology_source = args.topology_source.expanduser() if args.topology_source else None
    topology_path = args.topology_json.expanduser() if args.topology_json else None
    output_path = args.output.expanduser()
    try:
        inputs = [("--ppm-pdb", ppm_path), ("--fasta", fasta_path)]
        if topology_source is not None:
            inputs.append(("--topology-source", topology_source))
        if topology_path is not None:
            inputs.append(("--topology-json", topology_path))
        ensure_distinct_output(output_path, tuple(inputs))
        ensure_output_available(output_path, args.force)
        _, sequence = read_single_fasta(fasta_path)
        if topology_source is not None:
            topology = parse_topology_source(
                topology_source,
                fasta_path,
                topology_format=args.topology_format,
            )
        else:
            if args.topology_format:
                raise InputError("--topology-format 只能与 --topology-source 一起使用")
            assert topology_path is not None
            topology = load_topology_json(
                topology_path, expected_sequence_length=len(sequence)
            )
        validate_object_name(args.object_name, topology["helix_count"], ppm=True)
        validate_chain(args.chain)
        validate_color(args.base_color, "--base-color")
        validate_color(args.z_low_color, "--z-low-color")
        validate_color(args.z_high_color, "--z-high-color")
        colors = (
            parse_tm_colors(args.tm_colors, topology["helix_count"])
            if args.tm_colors is not None
            else default_tm_colors(topology["helix_count"])
        )
        z_low, z_high = find_dum_planes(ppm_path)
        validate_structure_against_fasta(
            ppm_path, sequence, args.chain, structure_format="pdb"
        )
        pml = build_ppm_pml(
            ppm_path,
            args.object_name,
            args.chain,
            args.base_color,
            topology["tm_segments"],
            colors,
            args.z_low_color,
            args.z_high_color,
            z_low,
            z_high,
        )
        atomic_write_text(output_path, pml, args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output_path}")
    write_tool_result([ToolArtifact(output_path, "PPM 膜定位审查脚本")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
