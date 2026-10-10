#!/usr/bin/env python3
"""Run an explicit Meeko receptor-preparation command without shell expansion."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from atomic_publish import publish_staged_file
from docking_tool_result import ToolArtifact, write_tool_result
from external_process import run_external

_ORIGINAL_SUBPROCESS_RUN = subprocess.run
DEFAULT_MEEKO_ENTRYPOINT = ["-m", "meeko.cli.mk_prepare_receptor"]
CHARGE_MODELS = ("gasteiger", "espaloma", "zero")


class CliError(ValueError):
    """User-correctable CLI or input error."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, f"Error: {message}\nUse -h or --help for details.\n")


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        description=(
            "Prepare receptor PDBQT with Meeko. The Meeko executable is selected by "
            "the caller; upstream receptor entrypoint and input/output flags are "
            "used unless overridden."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python src/prepare_receptor_pdbqt.py \\
    --receptor-pdb receptor_confirmed_microstate.pdb \\
    --output-pdbqt receptor.pdbqt \\
    --meeko-executable python3 \\
    --meeko-arg=--delete_residues --meeko-arg HOH

Meeko standard output and standard error remain visible. A non-zero Meeko exit
code is returned without publishing --output-pdbqt.
""",
    )
    parser.add_argument("--receptor-pdb", required=True, type=Path, help="Input receptor PDB with user-confirmed chemistry state.")
    parser.add_argument("--output-pdbqt", required=True, type=Path, help="Target receptor PDBQT path.")
    parser.add_argument("--meeko-executable", required=True, help="Executable used for Meeko, e.g. python3 or mk_prepare_receptor.py.")
    parser.add_argument(
        "--meeko-entrypoint",
        action="append",
        default=None,
        help="One startup item for Meeko; repeat in order for forms such as '-m' followed by a module name.",
    )
    parser.add_argument("--input-flag", default="--read_pdb", help="Meeko option that receives the receptor PDB path.")
    parser.add_argument("--output-flag", default="-p", help="Meeko option that receives the output PDBQT path.")
    parser.add_argument(
        "--charge-model",
        choices=CHARGE_MODELS,
        default="gasteiger",
        help="Partial-charge model passed to Meeko (default: gasteiger).",
    )
    parser.add_argument("--meeko-arg", action="append", default=[], help="One additional Meeko argument; repeat in execution order.")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing --output-pdbqt.")
    return parser


def _resolve_executable(value: str) -> str:
    if os.sep in value:
        path = Path(value)
        if not path.exists():
            raise CliError(f"--meeko-executable does not exist: {value}")
        if not path.is_file():
            raise CliError(f"--meeko-executable is not a regular file: {value}")
        if not os.access(path, os.X_OK):
            raise CliError(f"--meeko-executable is not executable: {value}")
        return str(path)
    resolved = shutil.which(value)
    if resolved is None:
        raise CliError(f"--meeko-executable was not found on PATH: {value}")
    return resolved


def build_meeko_argv(args: argparse.Namespace, output_path: Path) -> list[str]:
    entrypoint = args.meeko_entrypoint or DEFAULT_MEEKO_ENTRYPOINT
    return [
        _resolve_executable(args.meeko_executable),
        *entrypoint,
        args.input_flag,
        str(args.receptor_pdb),
        args.output_flag,
        str(output_path),
        "--charge_model",
        args.charge_model,
        *args.meeko_arg,
    ]


def _run_meeko_argv(argv: list[str]) -> subprocess.CompletedProcess[str]:
    if subprocess.run is not _ORIGINAL_SUBPROCESS_RUN:
        return subprocess.run(argv, shell=False, text=True, capture_output=True)
    return run_external(argv, text=True)  # type: ignore[return-value]


def _resolved(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _validate_common(args: argparse.Namespace) -> None:
    if not args.receptor_pdb.exists():
        raise CliError(f"--receptor-pdb does not exist: {args.receptor_pdb}")
    if not args.receptor_pdb.is_file():
        raise CliError(f"--receptor-pdb is not a regular file: {args.receptor_pdb}")
    if args.receptor_pdb.suffix.lower() != ".pdb":
        raise CliError(f"--receptor-pdb must have .pdb suffix: {args.receptor_pdb}")
    if _resolved(args.receptor_pdb) == _resolved(args.output_pdbqt):
        raise CliError("--output-pdbqt must not be the same path as --receptor-pdb")
    if args.output_pdbqt.suffix.lower() != ".pdbqt":
        raise CliError(f"--output-pdbqt must have .pdbqt suffix: {args.output_pdbqt}")
    if args.output_pdbqt.exists() and not args.overwrite:
        raise CliError(f"--output-pdbqt already exists: {args.output_pdbqt}; use --overwrite to replace it")
    args.output_pdbqt.parent.mkdir(parents=True, exist_ok=True)


def run(args: argparse.Namespace) -> int:
    _validate_common(args)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{args.output_pdbqt.name}.", suffix=".tmp", dir=str(args.output_pdbqt.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    tmp_path.unlink()
    argv = build_meeko_argv(args, tmp_path)
    generated_path = tmp_path
    suffixed_generated_path = Path(f"{tmp_path}.pdbqt")
    try:
        completed = _run_meeko_argv(argv)
        if completed.returncode != 0:
            return completed.returncode
        if not generated_path.exists() and suffixed_generated_path.exists():
            generated_path = suffixed_generated_path
        if not generated_path.exists():
            raise CliError(f"Meeko command returned 0 but did not create expected output: {tmp_path}")
        try:
            publish_staged_file(
                generated_path, args.output_pdbqt, overwrite=args.overwrite
            )
        except FileExistsError as error:
            raise CliError(
                f"--output-pdbqt already exists: {args.output_pdbqt}; "
                "use --overwrite to replace it"
            ) from error
        print(f"wrote: {args.output_pdbqt}")
        write_tool_result([ToolArtifact(args.output_pdbqt, "受体 PDBQT")])
        return 0
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
        if suffixed_generated_path.exists():
            suffixed_generated_path.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except CliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
