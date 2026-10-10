#!/usr/bin/env python3
"""Run an explicit Meeko ligand-preparation command without shell expansion."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from atomic_publish import AtomicPublishError, publish_staged_files
from check_sdf_pdbqt_mapping import CliError as MappingCliError
from check_sdf_pdbqt_mapping import check_mapping
from docking_tool_result import ToolArtifact, write_tool_result
from external_process import run_external

_ORIGINAL_SUBPROCESS_RUN = subprocess.run
DEFAULT_MEEKO_ENTRYPOINT = ["-m", "meeko.cli.mk_prepare_ligand"]
CHARGE_MODELS = ("gasteiger", "espaloma", "zero", "read")
DEFAULT_COORDINATE_TOLERANCE = 0.001


class CliError(ValueError):
    """User-correctable CLI or input error."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, f"Error: {message}\nUse -h or --help for details.\n")


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        description=(
            "Prepare ligand PDBQT from a user-selected SDF microstate by launching "
            "Meeko. When --atom-map and --mapping-output are supplied, validate the "
            "staged PDBQT before publishing either the PDBQT or mapping report."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python src/prepare_ligand_pdbqt.py \\
    --ligand-sdf ligand_selected_microstate.sdf \\
    --output-pdbqt ligand.pdbqt \\
    --atom-map ligand_map.json \\
    --mapping-output ligand.pdbqt-mapping.json \\
    --meeko-executable python3 \\
    --meeko-arg=--rigid_macrocycles

Meeko standard output and standard error remain visible. A non-zero Meeko exit
code or mapping mismatch is returned without publishing either output. Omitting
both mapping options retains the legacy preparation-only CLI behavior.
""",
    )
    parser.add_argument("--ligand-sdf", required=True, type=Path, help="Input SDF for the user-selected ligand microstate.")
    parser.add_argument("--output-pdbqt", required=True, type=Path, help="Target ligand PDBQT path.")
    parser.add_argument(
        "--atom-map",
        type=Path,
        help="Explicit JSON atom/bond map used to validate the staged PDBQT.",
    )
    parser.add_argument(
        "--mapping-output",
        type=Path,
        help="JSON mapping report published together with the validated PDBQT.",
    )
    parser.add_argument(
        "--coordinate-tolerance",
        type=float,
        default=DEFAULT_COORDINATE_TOLERANCE,
        help=(
            "Maximum mapped coordinate distance in Angstrom when validation is "
            f"enabled (default: {DEFAULT_COORDINATE_TOLERANCE:g})."
        ),
    )
    parser.add_argument("--meeko-executable", required=True, help="Executable used for Meeko, e.g. python3 or mk_prepare_ligand.py.")
    parser.add_argument(
        "--meeko-entrypoint",
        action="append",
        default=None,
        help="One startup item for Meeko; repeat in order for forms such as '-m' followed by a module name.",
    )
    parser.add_argument("--input-flag", default="-i", help="Meeko option that receives the ligand SDF path.")
    parser.add_argument("--output-flag", default="-o", help="Meeko option that receives the output PDBQT path.")
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
        str(args.ligand_sdf),
        args.output_flag,
        str(output_path),
        "--charge_model",
        args.charge_model,
        "--add_index_map",
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
    if not args.ligand_sdf.exists():
        raise CliError(f"--ligand-sdf does not exist: {args.ligand_sdf}")
    if not args.ligand_sdf.is_file():
        raise CliError(f"--ligand-sdf is not a regular file: {args.ligand_sdf}")
    if args.ligand_sdf.suffix.lower() != ".sdf":
        raise CliError(f"--ligand-sdf must have .sdf suffix: {args.ligand_sdf}")
    if _resolved(args.ligand_sdf) == _resolved(args.output_pdbqt):
        raise CliError("--output-pdbqt must not be the same path as --ligand-sdf")
    if args.output_pdbqt.suffix.lower() != ".pdbqt":
        raise CliError(f"--output-pdbqt must have .pdbqt suffix: {args.output_pdbqt}")
    if args.output_pdbqt.exists() and not args.overwrite:
        raise CliError(f"--output-pdbqt already exists: {args.output_pdbqt}; use --overwrite to replace it")
    if (args.atom_map is None) != (args.mapping_output is None):
        raise CliError("--atom-map and --mapping-output must be supplied together")
    if args.atom_map is not None and args.mapping_output is not None:
        resolved_inputs = {_resolved(args.ligand_sdf), _resolved(args.atom_map)}
        resolved_outputs = {
            _resolved(args.output_pdbqt),
            _resolved(args.mapping_output),
        }
        if len(resolved_outputs) != 2:
            raise CliError("--mapping-output must differ from --output-pdbqt")
        if resolved_inputs & resolved_outputs:
            raise CliError(
                "--output-pdbqt and --mapping-output must differ from all inputs"
            )
        if args.mapping_output.suffix.lower() != ".json":
            raise CliError(
                f"--mapping-output must have .json suffix: {args.mapping_output}"
            )
        if args.mapping_output.exists() and not args.overwrite:
            raise CliError(
                f"--mapping-output already exists: {args.mapping_output}; "
                "use --overwrite to replace it"
            )
        args.mapping_output.parent.mkdir(parents=True, exist_ok=True)
    args.output_pdbqt.parent.mkdir(parents=True, exist_ok=True)


def run(args: argparse.Namespace) -> int:
    _validate_common(args)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{args.output_pdbqt.name}.", suffix=".tmp", dir=str(args.output_pdbqt.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    tmp_path.unlink()
    tmp_report: Path | None = None
    argv = build_meeko_argv(args, tmp_path)
    try:
        completed = _run_meeko_argv(argv)
        if completed.returncode != 0:
            return completed.returncode
        if not tmp_path.exists():
            raise CliError(f"Meeko command returned 0 but did not create expected output: {tmp_path}")
        outputs = [(tmp_path, args.output_pdbqt)]
        artifacts = [ToolArtifact(args.output_pdbqt, "配体 PDBQT")]
        if args.atom_map is not None and args.mapping_output is not None:
            try:
                report = check_mapping(
                    args.ligand_sdf,
                    tmp_path,
                    args.atom_map,
                    args.coordinate_tolerance,
                )
            except MappingCliError as error:
                raise CliError(str(error)) from error
            report["pdbqt"] = str(_resolved(args.output_pdbqt))
            rendered = json.dumps(
                report, ensure_ascii=False, indent=2, sort_keys=True
            ) + "\n"
            if report["mismatch_count"]:
                print(rendered, end="")
                raise CliError(
                    f"mapping mismatches found: {report['mismatch_count']}; "
                    "the prepared PDBQT was not published"
                )
            descriptor, tmp_report_name = tempfile.mkstemp(
                prefix=f".{args.mapping_output.name}.",
                suffix=".tmp",
                dir=str(args.mapping_output.parent),
            )
            tmp_report = Path(tmp_report_name)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(rendered)
                handle.flush()
                os.fsync(handle.fileno())
            outputs.append((tmp_report, args.mapping_output))
            artifacts.append(
                ToolArtifact(args.mapping_output, "SDF-PDBQT 映射报告")
            )
        try:
            publish_staged_files(tuple(outputs), overwrite=args.overwrite)
        except FileExistsError as error:
            target_label = (
                "--output-pdbqt or --mapping-output"
                if args.mapping_output is not None
                else "--output-pdbqt"
            )
            raise CliError(
                f"{target_label} already exists; "
                "use --overwrite to replace it"
            ) from error
        except AtomicPublishError as error:
            raise CliError(f"could not publish ligand outputs: {error}") from error
        print(f"wrote: {args.output_pdbqt}")
        if args.mapping_output is not None:
            print(f"wrote: {args.mapping_output}")
        write_tool_result(artifacts)
        return 0
    finally:
        tmp_path.unlink(missing_ok=True)
        if tmp_report is not None:
            tmp_report.unlink(missing_ok=True)


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
