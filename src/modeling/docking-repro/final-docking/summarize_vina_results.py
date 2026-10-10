#!/usr/bin/env python3
"""Extract mechanical AutoDock Vina mode scores without choosing a mode."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

from docking_tool_result import ToolArtifact, write_tool_result


SUPPORTED_FORMATS = ("vina-1.x-log",)
VERSION_RE = re.compile(
    r"^\s*AutoDock Vina\s+v?([A-Za-z0-9][A-Za-z0-9._+-]*)\s*$",
    re.IGNORECASE,
)
MODE_RE = re.compile(
    r"^\s*(?P<mode>\d+)\s+"
    r"(?P<affinity>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s+"
    r"(?P<rmsd_lb>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s+"
    r"(?P<rmsd_ub>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*$"
)


class InputError(ValueError):
    """A command input or output path violates the CLI contract."""


class VinaArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: object, short_usage: str, **kwargs: object) -> None:
        self.short_usage = short_usage
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        self.exit(
            2,
            f"Error: {message}\n"
            f"Usage: {self.short_usage}\n"
            "Use -h or --help for details.\n",
        )


def read_text_file(path: Path, label: str) -> str:
    if not path.exists():
        raise InputError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise InputError(f"{label} is not a regular file: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InputError(f"{label} is not valid UTF-8: {path} ({exc})") from exc
    except OSError as exc:
        raise InputError(f"{label} is not readable: {path} ({exc})") from exc


def ensure_readable_file(path: Path, label: str) -> None:
    if not path.exists():
        raise InputError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise InputError(f"{label} is not a regular file: {path}")
    try:
        with path.open("rb"):
            pass
    except OSError as exc:
        raise InputError(f"{label} is not readable: {path} ({exc})") from exc


def ensure_output_available(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise InputError(f"output already exists: {path} (use --force to overwrite)")
    if not path.parent.exists():
        raise InputError(f"output directory does not exist: {path.parent}")
    if not path.parent.is_dir():
        raise InputError(f"output parent is not a directory: {path.parent}")


def ensure_output_not_input(output: Path, inputs: Sequence[tuple[str, Path]]) -> None:
    output_resolved = output.resolve()
    for label, input_path in inputs:
        if output_resolved == input_path.resolve():
            raise InputError(f"--output must differ from {label}: {input_path}")


def atomic_write_text(path: Path, content: str, force: bool) -> None:
    ensure_output_available(path, force)
    descriptor: int | None = None
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            descriptor = None
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if force:
            os.replace(temporary_path, path)
            temporary_path = None
        else:
            try:
                os.link(temporary_path, path)
            except FileExistsError as exc:
                raise InputError(
                    f"output appeared during writing and was not overwritten: {path}"
                ) from exc
    except InputError:
        raise
    except OSError as exc:
        raise InputError(f"could not write output {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def _finite_float(raw: str, source: Path, line_number: int, field: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise InputError(
            f"{source}: line {line_number} {field} is not numeric: {raw!r}"
        ) from exc
    if not math.isfinite(value):
        raise InputError(f"{source}: line {line_number} {field} is not finite")
    return value


def parse_vina_log(text: str, source: Path) -> tuple[str | None, list[dict[str, Any]]]:
    version: str | None = None
    modes: list[dict[str, Any]] = []
    seen_modes: set[int] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        if version is None:
            version_match = VERSION_RE.search(line)
            if version_match:
                version = version_match.group(1)
        match = MODE_RE.match(line)
        if not match:
            continue
        mode = int(match.group("mode"))
        if mode in seen_modes:
            raise InputError(f"{source}: duplicate mode {mode} at line {line_number}")
        seen_modes.add(mode)
        modes.append(
            {
                "mode": mode,
                "affinity_kcal_per_mol": _finite_float(
                    match.group("affinity"), source, line_number, "affinity"
                ),
                "rmsd_lb": _finite_float(
                    match.group("rmsd_lb"), source, line_number, "rmsd lower bound"
                ),
                "rmsd_ub": _finite_float(
                    match.group("rmsd_ub"), source, line_number, "rmsd upper bound"
                ),
            }
        )
    if not modes:
        raise InputError(f"{source}: no Vina mode score rows were found")
    return version, modes


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    text = read_text_file(args.log, "Vina log")
    ensure_readable_file(args.pose, "--pose")
    version, modes = parse_vina_log(text, args.log)
    return {
        "format": args.format,
        "vina_version": version,
        "log_file": str(args.log.resolve()),
        "pose_file": str(args.pose.resolve()),
        "mode_count": len(modes),
        "modes": modes,
        "mechanical_extraction_only": True,
    }


def build_parser() -> VinaArgumentParser:
    template = (
        "summarize_vina_results.py --log <vina.log> --pose <poses.pdbqt> "
        "--output <summary.json> [--format vina-1.x-log] [--force]"
    )
    parser = VinaArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "Parse a versioned AutoDock Vina 1.x text log and write the mode "
            "score rows plus log/pose file locations. The output preserves mode "
            "order from the log and does not choose a mode or judge poses."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Extracted fields:\n"
            "  mode, affinity_kcal_per_mol, rmsd_lb, rmsd_ub, log_file, pose_file\n"
            "  vina_version is captured when the log contains an AutoDock Vina line.\n\n"
            "Call template:\n"
            f"  {template}"
        ),
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument("--log", required=True, type=Path, help="readable Vina 1.x log")
    required.add_argument("--pose", required=True, type=Path, help="readable Vina pose PDBQT")
    required.add_argument("--output", required=True, type=Path, help="output JSON summary")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument("--format", default=SUPPORTED_FORMATS[0], choices=SUPPORTED_FORMATS, help=f"Vina log layout to read (default: {SUPPORTED_FORMATS[0]})")
    optional.add_argument("--force", action="store_true", help="overwrite an existing output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.log = args.log.expanduser()
    args.pose = args.pose.expanduser()
    args.output = args.output.expanduser()
    try:
        ensure_output_available(args.output, args.force)
        ensure_output_not_input(
            args.output,
            (("--log", args.log), ("--pose", args.pose)),
        )
        summary = build_summary(args)
        content = json.dumps(summary, indent=2, sort_keys=True) + "\n"
        atomic_write_text(args.output, content, args.force)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output}")
    write_tool_result([ToolArtifact(args.output, "Vina 结果摘要")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
