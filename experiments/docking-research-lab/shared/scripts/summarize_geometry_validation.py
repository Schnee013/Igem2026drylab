#!/usr/bin/env python3
"""Extract explicit mechanical metrics from a native geometry result JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from parse_tm_topology import InputError, MinimalArgumentParser, atomic_write_text, ensure_output_available, read_text_file
from report_af_confidence import _json_pointer


def parse_metric(raw: str) -> tuple[str, str]:
    name, separator, pointer = raw.partition("=")
    if not separator or not name or not pointer:
        raise argparse.ArgumentTypeError("metric must be NAME=/json/pointer")
    if not pointer.startswith("/"):
        raise argparse.ArgumentTypeError("metric JSON pointer must start with '/'")
    return name, pointer


def build_summary(input_path: Path, result_format: str, metrics: list[tuple[str, str]]) -> dict[str, Any]:
    if result_format != "json-pointer-v1":
        raise InputError(f"unsupported --result-format: {result_format!r}")
    text = read_text_file(input_path, "geometry validation result")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(
            f"{input_path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    extracted: dict[str, Any] = {}
    for name, pointer in metrics:
        value = _json_pointer(data, pointer)
        if isinstance(value, (dict, list)):
            raise InputError(f"metric {name!r} points to a container, not a scalar")
        extracted[name] = value
    return {
        "source_file": str(input_path.resolve()),
        "result_format": result_format,
        "metrics": extracted,
        "scope": (
            "This report extracts the requested scalar metrics from the native result. "
            "It does not decide whether the geometry passes or fails."
        ),
    }


def build_parser() -> MinimalArgumentParser:
    template = (
        "summarize_geometry_validation.py --input <native.json> "
        "--metric <name=/json/pointer> --output <summary.json> "
        "[--result-format json-pointer-v1] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Extract user-declared scalar metrics from an explicit native geometry "
            "result JSON. No backend substitution or pass/fail threshold is applied."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Call template:\n  {template}",
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--input", required=True, type=Path, help="native geometry JSON")
    required.add_argument("--metric", required=True, action="append", type=parse_metric, help="repeatable NAME=/json/pointer scalar extraction")
    required.add_argument("--output", required=True, type=Path, help="summary JSON output")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--result-format", default="json-pointer-v1", help="input layout to read (default: json-pointer-v1)")
    optional.add_argument("--force", action="store_true", help="overwrite an existing output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output_path = args.output.expanduser()
    try:
        if output_path.resolve() == args.input.expanduser().resolve():
            raise InputError("--output must differ from --input")
        ensure_output_available(output_path, args.force)
        summary = build_summary(args.input.expanduser(), args.result_format, args.metric)
        atomic_write_text(output_path, json.dumps(summary, indent=2, sort_keys=True) + "\n", args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {output_path}")
    write_tool_result([ToolArtifact(output_path, "几何检查摘要")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
