#!/usr/bin/env python3
"""Report observable receptor chemistry facts from a PDB file."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

from atomic_publish import publish_staged_file
from docking_tool_result import ToolArtifact, write_tool_result


IONIZABLE_RESIDUES = {
    "ASP": "carboxylate_side_chain",
    "GLU": "carboxylate_side_chain",
    "HIS": "imidazole_side_chain",
    "CYS": "thiol_or_thiolate_side_chain",
    "LYS": "amine_side_chain",
    "ARG": "guanidinium_side_chain",
    "TYR": "phenol_side_chain",
}
WATER_NAMES = {"HOH", "WAT", "H2O"}


class CliError(ValueError):
    """User-correctable CLI or input error."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, f"Error: {message}\nUse -h or --help for details.\n")


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        description=(
            "Report observable receptor chemistry facts from ATOM/HETATM records. "
            "This command does not select protonation states, histidine tautomers, "
            "disulfides, retained waters, ions, or docking-ready microstates."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python src/report_receptor_chemistry.py --receptor-pdb receptor.pdb
  python src/report_receptor_chemistry.py --receptor-pdb receptor.pdb --format json --output receptor_chemistry.json
""",
    )
    parser.add_argument(
        "--receptor-pdb",
        required=True,
        type=Path,
        help="Input receptor PDB file to inspect; must contain ATOM or HETATM records.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Report format for stdout or --output (visible default: text).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional report file: .txt for text or .json for json. Existing files are refused unless --overwrite is set.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing --output. Without this flag, existing outputs are refused.",
    )
    return parser


def _read_required_text(path: Path, label: str) -> str:
    if not path.exists():
        raise CliError(f"{label} does not exist: {path}")
    if not path.is_file():
        raise CliError(f"{label} is not a regular file: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CliError(f"{label} is not UTF-8 text: {path} ({exc})") from exc
    except OSError as exc:
        raise CliError(f"{label} is not readable: {path} ({exc})") from exc


def _resolved(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _validate_output_path(output: Path | None, input_path: Path, report_format: str) -> None:
    if output is None:
        return
    if _resolved(output) == _resolved(input_path):
        raise CliError("--output must not be the same path as --receptor-pdb")
    expected_suffix = ".json" if report_format == "json" else ".txt"
    if output.suffix.casefold() != expected_suffix:
        raise CliError(
            f"--format {report_format} requires --output to end with {expected_suffix}: {output}"
        )


def _pdb_records(text: str) -> Iterable[dict[str, Any]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        record = line[:6].strip()
        if record not in {"ATOM", "HETATM"}:
            continue
        atom_name = line[12:16].strip()
        residue_name = line[17:20].strip().upper()
        chain_id = line[21].strip() or "_"
        residue_number = line[22:26].strip()
        insertion_code = line[26].strip()
        element = line[76:78].strip().upper() if len(line) >= 78 else ""
        yield {
            "line": line_number,
            "record": record,
            "atom_name": atom_name,
            "residue_name": residue_name,
            "chain_id": chain_id,
            "residue_number": residue_number,
            "insertion_code": insertion_code,
            "element": element,
            "residue_id": f"{chain_id}:{residue_name}:{residue_number}{insertion_code}",
        }


def _residue_sort_key(residue: dict[str, Any]) -> tuple[str, tuple[int, int | str], str, str]:
    number = residue["residue_number"]
    if number.lstrip("-").isdigit():
        number_key: tuple[int, int | str] = (0, int(number))
    else:
        number_key = (1, number)
    return (
        residue["chain_id"],
        number_key,
        residue["insertion_code"],
        residue["residue_name"],
    )


def analyze_receptor(path: Path) -> dict[str, Any]:
    text = _read_required_text(path, "receptor PDB")
    atoms = list(_pdb_records(text))
    if not atoms:
        raise CliError(f"receptor PDB has no ATOM/HETATM records: {path}")

    residues: dict[str, dict[str, Any]] = {}
    water_residues: set[str] = set()
    hetero_components: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    atom_counts = Counter()

    for atom in atoms:
        atom_counts[atom["record"]] += 1
        residue_id = atom["residue_id"]
        residues.setdefault(
            residue_id,
            {
                "residue_id": residue_id,
                "residue_name": atom["residue_name"],
                "chain_id": atom["chain_id"],
                "residue_number": atom["residue_number"],
                "insertion_code": atom["insertion_code"],
                "atom_count": 0,
            },
        )["atom_count"] += 1
        if atom["record"] == "HETATM":
            if atom["residue_name"] in WATER_NAMES:
                water_residues.add(residue_id)
            else:
                key = (
                    atom["residue_name"],
                    atom["chain_id"],
                    atom["residue_number"],
                    atom["insertion_code"],
                )
                component = hetero_components.setdefault(
                    key,
                    {
                        "component_id": f"{atom['chain_id']}:{atom['residue_name']}:{atom['residue_number']}{atom['insertion_code']}",
                        "residue_name": atom["residue_name"],
                        "chain_id": atom["chain_id"],
                        "residue_number": atom["residue_number"],
                        "insertion_code": atom["insertion_code"],
                        "atom_count": 0,
                        "elements": Counter(),
                    },
                )
                component["atom_count"] += 1
                if atom["element"]:
                    component["elements"][atom["element"]] += 1

    ionizable = []
    histidines = []
    cysteines = []
    for residue in sorted(residues.values(), key=_residue_sort_key):
        residue_name = residue["residue_name"]
        if residue_name in IONIZABLE_RESIDUES:
            entry = {
                "residue_id": residue["residue_id"],
                "residue_name": residue_name,
                "observable_group": IONIZABLE_RESIDUES[residue_name],
                "atom_count": residue["atom_count"],
            }
            ionizable.append(entry)
            if residue_name == "HIS":
                histidines.append(entry)
            if residue_name == "CYS":
                cysteines.append(entry)

    hetero = []
    for component in hetero_components.values():
        component["elements"] = dict(sorted(component["elements"].items()))
        hetero.append(component)
    hetero.sort(key=lambda item: item["component_id"])

    return {
        "source_file": str(path),
        "atom_record_count": dict(sorted(atom_counts.items())),
        "residue_count": len(residues),
        "ionizable_residues": ionizable,
        "histidines": histidines,
        "cysteines": cysteines,
        "water_residue_count": len(water_residues),
        "water_residues": sorted(water_residues),
        "hetero_components": hetero,
        "scope": (
            "This report lists chemistry features present in the input structure. "
            "It does not choose microstates, protonation or tautomer states, decide "
            "which waters to retain, or accept or reject components."
        ),
    }


def format_text(report: dict[str, Any]) -> str:
    lines = [
        "Receptor chemistry observable facts",
        f"source_file: {report['source_file']}",
        f"atom_record_count: {json.dumps(report['atom_record_count'], sort_keys=True)}",
        f"residue_count: {report['residue_count']}",
        f"ionizable_residue_count: {len(report['ionizable_residues'])}",
        f"histidine_count: {len(report['histidines'])}",
        f"cysteine_count: {len(report['cysteines'])}",
        f"water_residue_count: {report['water_residue_count']}",
        f"hetero_component_count: {len(report['hetero_components'])}",
        "ionizable_residues:",
    ]
    for residue in report["ionizable_residues"]:
        lines.append(
            f"  - {residue['residue_id']} {residue['observable_group']} atoms={residue['atom_count']}"
        )
    lines.append("hetero_components:")
    for component in report["hetero_components"]:
        lines.append(
            f"  - {component['component_id']} atoms={component['atom_count']} elements={json.dumps(component['elements'], sort_keys=True)}"
        )
    lines.append(f"scope: {report['scope']}")
    return "\n".join(lines) + "\n"


def _atomic_write(path: Path, text: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise CliError(f"--output already exists: {path}; use --overwrite to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        try:
            publish_staged_file(tmp_path, path, overwrite=overwrite)
        except FileExistsError as error:
            raise CliError(
                f"--output already exists: {path}; use --overwrite to replace it"
            ) from error
    finally:
        tmp_path.unlink(missing_ok=True)


def render_report(report: dict[str, Any], report_format: str) -> str:
    if report_format == "json":
        return json.dumps(report, indent=2, sort_keys=True) + "\n"
    return format_text(report)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _validate_output_path(args.output, args.receptor_pdb, args.format)
        report = analyze_receptor(args.receptor_pdb)
        rendered = render_report(report, args.format)
        if args.output:
            _atomic_write(args.output, rendered, args.overwrite)
        else:
            sys.stdout.write(rendered)
        write_tool_result(
            [ToolArtifact(args.output, "受体化学报告")]
            if args.output is not None
            else ()
        )
        return 0
    except CliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
