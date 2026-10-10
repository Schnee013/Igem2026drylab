#!/usr/bin/env python3
"""Generate a PyMOL review script for raw and relaxed structures."""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from make_tm_review_pml import PYMOL_ACCENT_COLOR, PYMOL_BASE_COLOR, pymol_quote, validate_color, validate_object_name
from parse_tm_topology import InputError, MinimalArgumentParser, atomic_write_text, ensure_output_available, read_text_file

DEFAULT_RAW_OBJECT = "raw_model"
DEFAULT_RELAXED_OBJECT = "relaxed_model"
DEFAULT_ATOM_SELECTION = "name CA"
REVIEW_ATOM_SELECTIONS = ("all-heavy", "ca-only", "backbone")
PYMOL_SELECTION_BY_REVIEW_SCOPE = {
    "all-heavy": "polymer.protein and not hydro",
    "ca-only": "polymer.protein and name CA",
    "backbone": "polymer.protein and name N+CA+C+O",
}


def pymol_selection_for_review_scope(scope: str) -> str:
    try:
        return PYMOL_SELECTION_BY_REVIEW_SCOPE[scope]
    except KeyError as exc:
        raise InputError(f"unsupported review atom selection: {scope!r}") from exc


def validate_input_structure(path: Path, label: str) -> None:
    read_text_file(path, label)


def build_pml(
    raw: Path,
    relaxed: Path,
    raw_object: str,
    relaxed_object: str,
    raw_color: str,
    relaxed_color: str,
    atom_selection: str,
) -> str:
    return "\n".join(
        [
            f"load {pymol_quote(str(raw.resolve()))}, {raw_object}",
            f"load {pymol_quote(str(relaxed.resolve()))}, {relaxed_object}",
            f"hide everything, {raw_object} or {relaxed_object}",
            f"show cartoon, {raw_object}",
            f"show cartoon, {relaxed_object}",
            f"color {raw_color}, {raw_object}",
            f"color {relaxed_color}, {relaxed_object}",
            f"align ({relaxed_object} and {atom_selection}), ({raw_object} and {atom_selection})",
            f"zoom {raw_object} or {relaxed_object}",
            "set transparency, 0.35, " + relaxed_object,
        ]
    ) + "\n"


def build_parser() -> MinimalArgumentParser:
    template = (
        "make_raw_relaxed_review_pml.py --raw <raw.pdb> --relaxed <relaxed.pdb> "
        "--output <review.pml> [--raw-object <name>] [--relaxed-object <name>] "
        "[--raw-color <color>] [--relaxed-color <color>] "
        "[--atom-selection <pymol-selection>] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Generate a minimal PyMOL review script for two explicitly supplied "
            "structures. The script creates visual review material only and makes "
            "no relaxed-structure acceptance decision."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Call template:\n  {template}",
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--raw", required=True, type=Path, help="raw PDB structure")
    required.add_argument("--relaxed", required=True, type=Path, help="relaxed PDB structure")
    required.add_argument("--output", required=True, type=Path, help="PML output")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--raw-object", default=DEFAULT_RAW_OBJECT, help=f"safe PyMOL object name for raw (default: {DEFAULT_RAW_OBJECT})")
    optional.add_argument("--relaxed-object", default=DEFAULT_RELAXED_OBJECT, help=f"safe PyMOL object name for relaxed (default: {DEFAULT_RELAXED_OBJECT})")
    optional.add_argument("--raw-color", default=PYMOL_BASE_COLOR, help=f"PyMOL color for raw (default: {PYMOL_BASE_COLOR})")
    optional.add_argument("--relaxed-color", default=PYMOL_ACCENT_COLOR, help=f"PyMOL color for relaxed (default: {PYMOL_ACCENT_COLOR})")
    optional.add_argument("--atom-selection", default=DEFAULT_ATOM_SELECTION, choices=("all", "name CA", "backbone", "polymer.protein"), help=f"PyMOL atom selection used by align (default: {DEFAULT_ATOM_SELECTION})")
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
        if args.raw_object == args.relaxed_object:
            raise InputError("--raw-object and --relaxed-object must differ")
        validate_object_name(args.raw_object, 0)
        validate_object_name(args.relaxed_object, 0)
        validate_color(args.raw_color, "--raw-color")
        validate_color(args.relaxed_color, "--relaxed-color")
        validate_input_structure(args.raw.expanduser(), "--raw")
        validate_input_structure(args.relaxed.expanduser(), "--relaxed")
        pml = build_pml(
            args.raw.expanduser(),
            args.relaxed.expanduser(),
            args.raw_object,
            args.relaxed_object,
            args.raw_color,
            args.relaxed_color,
            args.atom_selection,
        )
        atomic_write_text(output_path, pml, args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output_path}")
    write_tool_result([ToolArtifact(output_path, "优化前后结构审查脚本")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
