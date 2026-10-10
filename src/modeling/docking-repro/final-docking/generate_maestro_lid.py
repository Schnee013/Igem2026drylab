#!/usr/bin/env python3
"""Generate a Schrödinger LID image from docking outputs without saved adapters."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from atomic_publish import publish_staged_file
from docking_tool_result import ToolArtifact, write_tool_result
from external_process import run_external
from export_ligand_pdbqt_to_sdf import convert_ligand_pdbqt_to_sdf
from export_receptor_pdbqt_to_pdb import convert_receptor_pdbqt_to_pdb
from transient_paths import transient_root

_ORIGINAL_SUBPROCESS_RUN = subprocess.run


PREPARED_RECEPTOR_SUFFIXES = {".pdb"}
PREPARED_LIGAND_SUFFIXES = {".sdf", ".sd"}
RECEPTOR_SUFFIXES = PREPARED_RECEPTOR_SUFFIXES | {".pdbqt"}
LIGAND_SUFFIXES = PREPARED_LIGAND_SUFFIXES | {".pdbqt"}
OUTPUT_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg"}
LAYOUT_MAX_WIDTH = 800
LAYOUT_MAX_HEIGHT = 800
DEFAULT_EXPORT_WIDTH = 2400
DEFAULT_EXPORT_HEIGHT = 2400
RESULT_SCHEMA = "maestro-lid-result/v1"


@dataclass(frozen=True)
class LidOptions:
    receptor: Path
    ligand: Path
    output: Path
    receptor_index: int = 1
    ligand_index: int = 1
    export_width: int = DEFAULT_EXPORT_WIDTH
    export_height: int = DEFAULT_EXPORT_HEIGHT
    bond_labels: bool = True
    salt_bridges: bool = True
    h_bonds: bool = True
    pi_pi: bool = True
    pi_cation: bool = True
    overwrite: bool = False
    meeko_python: Path | None = None


@dataclass(frozen=True)
class LidResult:
    output: Path
    width: int
    height: int
    receptor_atoms: int
    ligand_atoms: int
    receptor_conversion: dict[str, Any]
    ligand_conversion: dict[str, Any]


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def build_parser(*, engine_mode: bool = False) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a 2D diagram with Schrödinger's native LID engine. "
            "Docking PDBQT inputs are adapted to PDB/SDF in a session temporary "
            "directory and deleted after Maestro returns."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python src/generate_maestro_lid.py "
            "--schrodinger-run /path/to/schrodinger/run "
            "--meeko-python /path/to/docking/python "
            "--receptor receptor.pdbqt --ligand selected_pose.pdbqt --output lid.png "
            "--export-width 2400 --export-height 2400"
        ),
    )
    parser.add_argument(
        "--schrodinger-run",
        type=Path,
        required=not engine_mode,
        help="Schrödinger suite run launcher used by the outer CLI",
    )
    parser.add_argument(
        "--_engine",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--meeko-python",
        type=Path,
        help=(
            "Python executable with Meeko and RDKit, required only when the "
            "ligand input is PDBQT"
        ),
    )
    parser.add_argument(
        "--receptor",
        required=True,
        type=Path,
        help="receptor .pdbqt docking input or already prepared .pdb file",
    )
    parser.add_argument(
        "--ligand",
        required=True,
        type=Path,
        help="ligand docking poses as .pdbqt, or an already prepared .sdf/.sd file",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="output .png, .jpg, .jpeg, or .svg file",
    )
    parser.add_argument(
        "--receptor-index",
        type=_positive_int,
        default=1,
        help="1-based structure position inside the receptor file (usually 1)",
    )
    parser.add_argument(
        "--ligand-index",
        type=_positive_int,
        default=1,
        help=(
            "1-based pose position inside a ligand PDBQT, or structure position "
            "inside a prepared SDF (default: 1)"
        ),
    )
    parser.add_argument(
        "--export-width",
        "--max-width",
        dest="export_width",
        type=_positive_int,
        default=DEFAULT_EXPORT_WIDTH,
        help="maximum exported image width in pixels (default: 2400)",
    )
    parser.add_argument(
        "--export-height",
        "--max-height",
        dest="export_height",
        type=_positive_int,
        default=DEFAULT_EXPORT_HEIGHT,
        help="maximum exported image height in pixels (default: 2400)",
    )
    parser.add_argument(
        "--bond-labels", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--salt-bridges", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument("--h-bonds", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--pi-pi", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--pi-cation", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="replace an existing output file"
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = sys.argv[1:] if argv is None else argv
    parser = build_parser(engine_mode="--_engine" in raw_args)
    return parser.parse_args(raw_args)


def _require_path(value: Path | None, name: str) -> Path:
    if value is None:
        raise ValueError(f"missing --{name}")
    return value.expanduser().resolve()


def options_from_args(args: argparse.Namespace) -> LidOptions:
    return LidOptions(
        receptor=_require_path(args.receptor, "receptor"),
        ligand=_require_path(args.ligand, "ligand"),
        output=_require_path(args.output, "output"),
        receptor_index=args.receptor_index,
        ligand_index=args.ligand_index,
        export_width=args.export_width,
        export_height=args.export_height,
        bond_labels=args.bond_labels,
        salt_bridges=args.salt_bridges,
        h_bonds=args.h_bonds,
        pi_pi=args.pi_pi,
        pi_cation=args.pi_cation,
        overwrite=args.overwrite,
        meeko_python=(
            args.meeko_python.expanduser().resolve()
            if args.meeko_python is not None
            else None
        ),
    )


def validate_options(options: LidOptions, *, prepared_only: bool = False) -> None:
    receptor_suffixes = (
        PREPARED_RECEPTOR_SUFFIXES if prepared_only else RECEPTOR_SUFFIXES
    )
    ligand_suffixes = PREPARED_LIGAND_SUFFIXES if prepared_only else LIGAND_SUFFIXES
    for label, path, suffixes in (
        ("receptor", options.receptor, receptor_suffixes),
        ("ligand", options.ligand, ligand_suffixes),
    ):
        if not path.is_file():
            raise FileNotFoundError(f"{label} file not found: {path}")
        if path.suffix.lower() not in suffixes:
            allowed = ", ".join(sorted(suffixes))
            raise ValueError(f"{label} input must be one of: {allowed}")
    if options.ligand.suffix.lower() == ".pdbqt" and options.meeko_python is None:
        raise ValueError("--meeko-python is required for ligand PDBQT conversion")
    if options.output.suffix.lower() not in OUTPUT_SUFFIXES:
        raise ValueError("output filename must end in .png, .jpg, .jpeg, or .svg")
    if options.output.exists() and not options.overwrite:
        raise FileExistsError(
            f"output already exists: {options.output} (use --overwrite to replace it)"
        )


def _load_schrodinger():
    try:
        from schrodinger import structure
        from schrodinger.infra import mmerr
        from schrodinger.ui import sketcher
        from schrodinger.utils import qapplication
    except ImportError as error:
        raise RuntimeError(
            "Schrödinger Python is unavailable. Run this script as: "
            "$SCHRODINGER/run python3 generate_maestro_lid.py"
        ) from error
    return structure, mmerr, sketcher, qapplication


def generate_lid(options: LidOptions):
    """Generate one diagram from prepared inputs and return its image and summary."""
    validate_options(options, prepared_only=True)
    structure, mmerr, sketcher, qapplication = _load_schrodinger()
    qapplication.get_application()

    receptor_report: dict[str, Any] = {
        "converted": False,
        "source_format": options.receptor.suffix.lower().lstrip("."),
    }
    ligand_report: dict[str, Any] = {
        "converted": False,
        "source_format": options.ligand.suffix.lower().lstrip("."),
    }
    receptor = structure.StructureReader.read(
        str(options.receptor), index=options.receptor_index
    )
    ligand = structure.StructureReader.read(str(options.ligand), index=options.ligand_index)

    with mmerr.disable_mmerr():
        canvas = sketcher.LIDSketcher()
        canvas.showBondCustomLabels(options.bond_labels)
        canvas.setMaximumWidth(LAYOUT_MAX_WIDTH)
        canvas.setMaximumHeight(LAYOUT_MAX_HEIGHT)
        lid = sketcher.sketcherLID(canvas.getScene())
        lid.setLigand(ligand)
        lid.setReceptor(receptor)
        if options.salt_bridges:
            lid.pullSaltBridges()
        if options.h_bonds:
            lid.pullHBonds()
        if options.pi_pi or options.pi_cation:
            lid.pullPiInteractions(options.pi_pi, options.pi_cation)
        lid.compute()
        image = canvas.getQImage(options.export_width, options.export_height)

    if image.isNull():
        raise RuntimeError("Schrödinger LID returned an empty image")
    options.output.parent.mkdir(parents=True, exist_ok=True)
    if options.output.suffix.lower() == ".svg":
        canvas.getScene().saveSVG(
            options.export_width, options.export_height, str(options.output)
        )
        if not options.output.is_file() or options.output.stat().st_size == 0:
            raise RuntimeError(f"could not save image: {options.output}")
    else:
        image_format = "PNG" if options.output.suffix.lower() == ".png" else "JPG"
        if not image.save(str(options.output), image_format):
            raise RuntimeError(f"could not save image: {options.output}")
    result = LidResult(
        output=options.output,
        width=image.width(),
        height=image.height(),
        receptor_atoms=receptor.atom_total,
        ligand_atoms=ligand.atom_total,
        receptor_conversion=receptor_report,
        ligand_conversion=ligand_report,
    )
    return image, result


def _conversion_summary(result: LidResult) -> str:
    converted = []
    if result.receptor_conversion["converted"]:
        converted.append(
            "receptor:"
            f"{result.receptor_conversion['source_format']}→"
            f"{result.receptor_conversion['target_format']}"
        )
    if result.ligand_conversion["converted"]:
        converted.append(
            "ligand:"
            f"{result.ligand_conversion['source_format']}→"
            f"{result.ligand_conversion['target_format']}"
        )
    return ",".join(converted) if converted else "none"


def _result_payload(result: LidResult) -> dict[str, Any]:
    return {
        "schema": RESULT_SCHEMA,
        "saved": str(result.output),
        "width": result.width,
        "height": result.height,
        "ligand_atoms": result.ligand_atoms,
        "receptor_atoms": result.receptor_atoms,
        "conversions": _conversion_summary(result),
        "conversion_report": {
            "receptor": result.receptor_conversion,
            "ligand": result.ligand_conversion,
        },
    }


def _engine_command(runner: Path, options: LidOptions) -> list[str]:
    command = [
        str(runner),
        "python3",
        str(Path(__file__).resolve()),
        "--_engine",
        "--receptor",
        str(options.receptor),
        "--ligand",
        str(options.ligand),
        "--output",
        str(options.output),
        "--receptor-index",
        str(options.receptor_index),
        "--ligand-index",
        str(options.ligand_index),
        "--export-width",
        str(options.export_width),
        "--export-height",
        str(options.export_height),
    ]
    for name, enabled in (
        ("bond-labels", options.bond_labels),
        ("salt-bridges", options.salt_bridges),
        ("h-bonds", options.h_bonds),
        ("pi-pi", options.pi_pi),
        ("pi-cation", options.pi_cation),
    ):
        command.append(f"--{name}" if enabled else f"--no-{name}")
    if options.overwrite:
        command.append("--overwrite")
    return command


def _validate_runner(runner: Path) -> Path:
    resolved = runner.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Schrödinger run launcher not found: {resolved}")
    if not os.access(resolved, os.X_OK):
        raise PermissionError(f"Schrödinger run launcher is not executable: {resolved}")
    return resolved


def _temporary_output_path(final_output: Path) -> Path:
    final_output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_path = tempfile.mkstemp(
        prefix=f".{final_output.stem}.",
        suffix=final_output.suffix,
        dir=final_output.parent,
    )
    os.close(descriptor)
    temporary = Path(raw_path)
    temporary.unlink()
    return temporary


def _pdbqt_models(text: str) -> list[list[str]]:
    """Return validated MODEL blocks from PDBQT text, if present."""
    models: list[list[str]] = []
    current_model: list[str] | None = None
    current_model_line = 0
    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        record_name = line[:6].strip().upper()
        if record_name == "MODEL":
            if current_model is not None:
                raise ValueError(
                    "invalid ligand PDBQT: nested MODEL record at line "
                    f"{line_number} (previous MODEL starts at line {current_model_line})"
                )
            current_model = [line]
            current_model_line = line_number
            continue
        if record_name == "ENDMDL":
            if current_model is None:
                raise ValueError(
                    f"invalid ligand PDBQT: ENDMDL without MODEL at line {line_number}"
                )
            current_model.append(line)
            models.append(current_model)
            current_model = None
            current_model_line = 0
            continue
        if current_model is not None:
            current_model.append(line)

    if current_model is not None:
        raise ValueError(
            "invalid ligand PDBQT: MODEL at line "
            f"{current_model_line} has no matching ENDMDL"
        )
    return models


def count_pdbqt_poses(source: Path) -> int:
    """Return the number of selectable poses in a ligand PDBQT file."""
    text = source.read_text(encoding="utf-8")
    return len(_pdbqt_models(text)) or 1


def _extract_pdbqt_pose(source: Path, target: Path, pose_index: int) -> int:
    """Write one 1-based MODEL pose and return the number of available poses."""
    if pose_index < 1:
        raise ValueError("ligand pose index must be at least 1")
    text = source.read_text(encoding="utf-8")
    models = _pdbqt_models(text)

    pose_count = len(models) or 1
    if pose_index > pose_count:
        raise ValueError(
            f"ligand pose index {pose_index} is out of range; "
            f"available poses: 1-{pose_count}"
        )
    selected_text = "".join(models[pose_index - 1]) if models else text
    target.write_text(selected_text, encoding="utf-8")
    return pose_count


def _prepare_lid_inputs(
    options: LidOptions, temporary_directory: Path
) -> tuple[LidOptions, dict[str, Any], dict[str, Any]]:
    """Convert docking formats inside one disposable directory for the LID engine."""
    receptor = options.receptor
    ligand = options.ligand
    receptor_report: dict[str, Any] = {
        "converted": False,
        "source_format": receptor.suffix.lower().lstrip("."),
    }
    ligand_report: dict[str, Any] = {
        "converted": False,
        "source_format": ligand.suffix.lower().lstrip("."),
    }
    if receptor.suffix.lower() == ".pdbqt":
        receptor = temporary_directory / "receptor.pdb"
        receptor_report = convert_receptor_pdbqt_to_pdb(options.receptor, receptor)
    if ligand.suffix.lower() == ".pdbqt":
        if options.meeko_python is None:
            raise ValueError("--meeko-python is required for ligand PDBQT conversion")
        selected_pose = temporary_directory / "selected-pose.pdbqt"
        pose_count = _extract_pdbqt_pose(
            options.ligand, selected_pose, options.ligand_index
        )
        ligand = temporary_directory / "selected-pose.sdf"
        ligand_report = convert_ligand_pdbqt_to_sdf(
            selected_pose,
            ligand,
            meeko_python=options.meeko_python,
        )
        ligand_report = {
            **ligand_report,
            "selected_pose_index": options.ligand_index,
            "available_pose_count": pose_count,
        }
    prepared = replace(
        options,
        receptor=receptor,
        ligand=ligand,
        ligand_index=(
            1
            if options.ligand.suffix.lower() == ".pdbqt"
            else options.ligand_index
        ),
        meeko_python=None,
    )
    validate_options(prepared, prepared_only=True)
    return prepared, receptor_report, ligand_report


def _run_engine_process(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    if subprocess.run is not _ORIGINAL_SUBPROCESS_RUN:
        return subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
    return run_external(
        command,
        cwd=str(cwd),
        text=True,
        check=False,
        forward_stdout=False,
        forward_stderr=False,
    )  # type: ignore[return-value]


def _result_from_line(line: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or payload.get("schema") != RESULT_SCHEMA:
        return None
    required = {
        "saved": str,
        "width": int,
        "height": int,
        "conversions": str,
    }
    if all(isinstance(payload.get(key), kind) for key, kind in required.items()):
        return payload
    raise RuntimeError("LID 引擎返回的 JSON 结果字段无效")


def run_outer(args: argparse.Namespace) -> int:
    options = options_from_args(args)
    validate_options(options)
    runner = _validate_runner(args.schrodinger_run)
    final_output = options.output
    temporary_output = _temporary_output_path(final_output)
    try:
        with tempfile.TemporaryDirectory(
            prefix="maestro-lid-inputs-", dir=transient_root()
        ) as raw_temporary_directory:
            prepared, _receptor_report, _ligand_report = _prepare_lid_inputs(
                options, Path(raw_temporary_directory)
            )
            engine_options = replace(
                prepared, output=temporary_output, overwrite=False
            )
            completed = _run_engine_process(
                _engine_command(runner, engine_options),
                cwd=str(Path(__file__).resolve().parent),
            )
        if completed.returncode != 0:
            if completed.stdout:
                print(completed.stdout, end="")
            if completed.stderr:
                print(completed.stderr, end="", file=sys.stderr)
            return completed.returncode
        _parse_engine_result(completed.stdout)
        if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
            raise RuntimeError(f"LID engine did not produce a nonempty image: {temporary_output}")
        publish_staged_file(
            temporary_output, final_output, overwrite=options.overwrite
        )
        print(f"Saved: {final_output}")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        write_tool_result([ToolArtifact(final_output, "Maestro LID 图像")])
        return 0
    finally:
        temporary_output.unlink(missing_ok=True)


def _parse_engine_result(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        payload = _result_from_line(line)
        if payload is not None:
            return payload
    raise RuntimeError("LID 引擎已结束，但没有返回可识别的 JSON 结果")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args._engine:
        try:
            return run_outer(args)
        except Exception as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
    try:
        _, result = generate_lid(options_from_args(args))
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(_result_payload(result), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
