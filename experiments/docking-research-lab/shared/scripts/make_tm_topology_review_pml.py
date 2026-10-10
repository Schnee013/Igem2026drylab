#!/usr/bin/env python3
"""Parse one topology source in memory and write the final PyMOL review PML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from make_tm_review_pml import (
    DEFAULT_OBJECT_NAME,
    PYMOL_BASE_COLOR,
    build_tm_pml,
    default_tm_colors,
    parse_tm_colors,
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
    parse_deeptmhmm_gff3,
    parse_phyre2_memsat_svm,
    read_single_fasta,
    validate_topology_json,
)


def parse_topology_source(
    topology_source: Path,
    fasta_path: Path,
    *,
    topology_format: str | None = None,
) -> dict[str, Any]:
    """Return validated topology data without writing the intermediate JSON."""
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


def build_parser() -> MinimalArgumentParser:
    template = (
        "make_tm_topology_review_pml.py --topology-source <topology_file> "
        "--fasta <single_record_fasta> --structure <pdb_or_cif> --chain <chain_id> "
        "--output <pml> [--topology-format <source_format>] "
        "[--object-name <pymol_object>] [--base-color <pymol_color>] "
        "[--tm-colors <c1,c2,...,cN>] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "直接从 DeepTMHMM 或 Phyre 2.2 拓扑来源生成 PyMOL 复核脚本。"
            "中间统一 topology JSON 只在内存中使用，不写入磁盘。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "默认自动识别拓扑来源格式；只有兼容旧文件时才需要 --topology-format。\n\n"
            "Call template:\n"
            f"  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--topology-source", required=True, type=Path, help="DeepTMHMM or Phyre topology source")
    required.add_argument("--fasta", required=True, type=Path, help="single-record FASTA")
    required.add_argument("--structure", required=True, type=Path, help="PDB or mmCIF structure")
    required.add_argument("--chain", required=True, help="structure chain identifier")
    required.add_argument("--output", required=True, type=Path, help="output PML path")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--topology-format", choices=SOURCE_FORMATS, help="expert compatibility override for source format")
    optional.add_argument("--object-name", default=DEFAULT_OBJECT_NAME, help=f"safe PyMOL object name (default: {DEFAULT_OBJECT_NAME})")
    optional.add_argument("--base-color", default=PYMOL_BASE_COLOR, help=f"base PyMOL color (default: {PYMOL_BASE_COLOR})")
    optional.add_argument("--tm-colors", help="comma-separated TM colors; defaults to a repeated display palette sized to the topology")
    optional.add_argument("--force", action="store_true", help="overwrite an existing output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    topology_source = args.topology_source.expanduser()
    fasta_path = args.fasta.expanduser()
    structure_path = args.structure.expanduser()
    output_path = args.output.expanduser()
    try:
        ensure_distinct_output(
            output_path,
            (
                ("--topology-source", topology_source),
                ("--fasta", fasta_path),
                ("--structure", structure_path),
            ),
        )
        ensure_output_available(output_path, args.force)
        _, sequence = read_single_fasta(fasta_path)
        topology = parse_topology_source(
            topology_source,
            fasta_path,
            topology_format=args.topology_format,
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
    write_tool_result([ToolArtifact(output_path, "跨膜拓扑复核脚本")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
