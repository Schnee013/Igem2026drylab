#!/usr/bin/env python3
"""Report observable receptor chemistry facts from a PDB file."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

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
# Heavy-atom counts for a complete residue: four backbone atoms (N, CA, C, O)
# plus the side chain. Heavy atoms are used because the total atom count varies
# with protonation state, which is exactly what the reviewer still has to decide.
# A C-terminal residue carries one extra OXT, handled at comparison time.
EXPECTED_HEAVY_ATOM_COUNTS = {
    "ASP": 8,
    "GLU": 9,
    "HIS": 10,
    "CYS": 6,
    "LYS": 9,
    "ARG": 11,
    "TYR": 12,
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
    pocket = parser.add_argument_group(
        "pocket proximity",
        "Optional. Without either anchor the report lists ionizable residues structure-wide, "
        "which cannot answer whether a residue sits near the intended binding site.",
    )
    anchor = pocket.add_mutually_exclusive_group()
    anchor.add_argument(
        "--pocket-ligand",
        metavar="COMPONENT_ID",
        help="Anchor on a component already present in the PDB, e.g. A:STI:1 "
        "(the ids listed under hetero_components). Distances are atom-to-atom.",
    )
    anchor.add_argument(
        "--pocket-center",
        metavar="X,Y,Z",
        help="Anchor on a manual coordinate, e.g. 12.5,-3.0,44.25.",
    )
    pocket.add_argument(
        "--pocket-radius",
        type=float,
        default=5.0,
        help="Neighborhood radius in angstroms (visible default: 5.0). Requires an anchor.",
    )
    return parser


def _parse_pocket_center(raw: str | None) -> tuple[float, float, float] | None:
    if raw is None:
        return None
    fields = [field.strip() for field in raw.split(",")]
    if len(fields) != 3:
        raise CliError(f"--pocket-center must be X,Y,Z with three values: {raw!r}")
    values = []
    for axis, field in zip("xyz", fields):
        try:
            value = float(field)
        except ValueError as exc:
            raise CliError(f"--pocket-center {axis} is not a number: {field!r}") from exc
        if not math.isfinite(value):
            raise CliError(f"--pocket-center {axis} is not finite: {field!r}")
        values.append(value)
    return (values[0], values[1], values[2])


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


def _parse_coordinate(field: str) -> float | None:
    try:
        value = float(field)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


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
        x = _parse_coordinate(line[30:38])
        y = _parse_coordinate(line[38:46])
        z = _parse_coordinate(line[46:54])
        yield {
            "line": line_number,
            "record": record,
            "atom_name": atom_name,
            "residue_name": residue_name,
            "chain_id": chain_id,
            "residue_number": residue_number,
            "insertion_code": insertion_code,
            "element": element,
            "x": x,
            "y": y,
            "z": z,
            "residue_id": f"{chain_id}:{residue_name}:{residue_number}{insertion_code}",
        }


def _is_hydrogen(atom: dict[str, Any]) -> bool:
    """Classify by the element column, falling back to the PDB atom-name convention."""

    if atom["element"]:
        return atom["element"] == "H"
    name = atom["atom_name"]
    if not name:
        return False
    # In columns 13-16 a leading digit is a branch index, so H is at position 2.
    return name[0] == "H" or (name[0].isdigit() and len(name) > 1 and name[1] == "H")


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


def _minimum_distance(
    points: Sequence[tuple[float, float, float]],
    anchor: Sequence[tuple[float, float, float]],
) -> float | None:
    best: float | None = None
    for point in points:
        for target in anchor:
            distance = math.dist(point, target)
            if best is None or distance < best:
                best = distance
    return best


def _chain_rows(residues: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate per chain so the reviewer can decide which chains to keep."""

    chains: dict[str, dict[str, Any]] = {}
    for residue in residues:
        chain = chains.setdefault(
            residue["chain_id"],
            {
                "chain_id": residue["chain_id"],
                "polymer_residue_count": 0,
                "water_residue_count": 0,
                "hetero_component_count": 0,
                "atom_count": 0,
                "hetero_residue_names": set(),
            },
        )
        chain["atom_count"] += residue["atom_count"]
        if residue["record"] == "ATOM":
            chain["polymer_residue_count"] += 1
        elif residue["residue_name"] in WATER_NAMES:
            chain["water_residue_count"] += 1
        else:
            chain["hetero_component_count"] += 1
            chain["hetero_residue_names"].add(residue["residue_name"])
    rows = []
    for chain in chains.values():
        chain["hetero_residue_names"] = sorted(chain["hetero_residue_names"])
        rows.append(chain)
    rows.sort(key=lambda item: item["chain_id"])
    return rows


def _pocket_report(
    residues: Mapping[str, dict[str, Any]],
    ionizable: Sequence[dict[str, Any]],
    center: tuple[float, float, float] | None,
    ligand_id: str | None,
    radius: float,
) -> dict[str, Any] | None:
    """List ionizable residues within `radius` of a manual point or a named component.

    Distances are minimum atom-to-atom, not centroid-to-centroid, so a large
    cofactor does not push its own contact residues out of range.
    """

    if center is None and ligand_id is None:
        return None
    if center is not None:
        anchor = [center]
        anchor_label = f"({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})"
        anchor_kind = "manual_center"
    else:
        residue = residues.get(ligand_id)
        if residue is None:
            raise CliError(
                f"--pocket-ligand not found in receptor PDB: {ligand_id}; "
                "use the component id shown in hetero_components, e.g. A:STI:1"
            )
        anchor = residue["coordinates"]
        if not anchor:
            raise CliError(f"--pocket-ligand has no parsable coordinates: {ligand_id}")
        anchor_label = ligand_id
        anchor_kind = "component"

    neighbors = []
    for entry in ionizable:
        coordinates = residues[entry["residue_id"]]["coordinates"]
        if not coordinates:
            continue
        distance = _minimum_distance(coordinates, anchor)
        if distance is not None and distance <= radius:
            neighbor = dict(entry)
            neighbor["distance_to_anchor"] = round(distance, 3)
            neighbors.append(neighbor)
    neighbors.sort(key=lambda item: item["distance_to_anchor"])
    return {
        "anchor_kind": anchor_kind,
        "anchor_label": anchor_label,
        "radius": radius,
        "neighbor_count": len(neighbors),
        "neighbors": neighbors,
    }


def analyze_receptor(
    path: Path,
    pocket_center: tuple[float, float, float] | None = None,
    pocket_ligand: str | None = None,
    pocket_radius: float = 5.0,
) -> dict[str, Any]:
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
        residue = residues.setdefault(
            residue_id,
            {
                "residue_id": residue_id,
                "residue_name": atom["residue_name"],
                "chain_id": atom["chain_id"],
                "residue_number": atom["residue_number"],
                "insertion_code": atom["insertion_code"],
                "record": atom["record"],
                "atom_count": 0,
                "heavy_atom_count": 0,
                "has_terminal_oxygen": False,
                "coordinates": [],
            },
        )
        residue["atom_count"] += 1
        if not _is_hydrogen(atom):
            residue["heavy_atom_count"] += 1
        if atom["atom_name"] == "OXT":
            residue["has_terminal_oxygen"] = True
        if atom["x"] is not None and atom["y"] is not None and atom["z"] is not None:
            residue["coordinates"].append((atom["x"], atom["y"], atom["z"]))
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
            expected = EXPECTED_HEAVY_ATOM_COUNTS[residue_name]
            if residue["has_terminal_oxygen"]:
                expected += 1
            observed = residue["heavy_atom_count"]
            entry = {
                "residue_id": residue["residue_id"],
                "residue_name": residue_name,
                "observable_group": IONIZABLE_RESIDUES[residue_name],
                "atom_count": residue["atom_count"],
                "heavy_atom_count": observed,
                "expected_heavy_atom_count": expected,
                "heavy_atom_difference": observed - expected,
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

    chains = _chain_rows(residues.values())
    polymer_residue_count = sum(chain["polymer_residue_count"] for chain in chains)
    pocket = _pocket_report(residues, ionizable, pocket_center, pocket_ligand, pocket_radius)

    return {
        "source_file": str(path),
        "atom_record_count": dict(sorted(atom_counts.items())),
        "residue_count": len(residues),
        "polymer_residue_count": polymer_residue_count,
        "chain_count": len(chains),
        "chains": chains,
        "ionizable_residues": ionizable,
        "histidines": histidines,
        "cysteines": cysteines,
        "water_residue_count": len(water_residues),
        "water_residues": sorted(water_residues),
        "hetero_components": hetero,
        "pocket": pocket,
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
        f"residue_count_including_water_and_hetero: {report['residue_count']}",
        f"polymer_residue_count: {report['polymer_residue_count']}",
        f"chain_count: {report['chain_count']}",
        f"ionizable_residue_count: {len(report['ionizable_residues'])}",
        f"histidine_count: {len(report['histidines'])}",
        f"cysteine_count: {len(report['cysteines'])}",
        f"water_residue_count: {report['water_residue_count']}",
        f"hetero_component_count: {len(report['hetero_components'])}",
        "chains:",
    ]
    for chain in report["chains"]:
        lines.append(
            f"  - {chain['chain_id']} polymer={chain['polymer_residue_count']} "
            f"water={chain['water_residue_count']} hetero={chain['hetero_component_count']}"
        )
    pocket = report.get("pocket")
    if pocket is None:
        lines.append("pocket: not requested (no --pocket-ligand or --pocket-center)")
    else:
        lines.append(
            f"pocket: anchor={pocket['anchor_label']} radius={pocket['radius']} "
            f"neighbors={pocket['neighbor_count']}"
        )
        for neighbor in pocket["neighbors"]:
            lines.append(
                f"  - {neighbor['residue_id']} {neighbor['observable_group']} "
                f"distance={neighbor['distance_to_anchor']}"
            )
    lines.append("ionizable_residues:")
    for residue in report["ionizable_residues"]:
        lines.append(
            f"  - {residue['residue_id']} {residue['observable_group']} "
            f"heavy_atoms={residue['heavy_atom_count']}/{residue['expected_heavy_atom_count']}"
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
        if args.pocket_radius <= 0 or not math.isfinite(args.pocket_radius):
            raise CliError(f"--pocket-radius must be a positive number: {args.pocket_radius}")
        # The GUI always passes the visible default, even without an anchor;
        # the radius is simply unused then.
        report = analyze_receptor(
            args.receptor_pdb,
            pocket_center=_parse_pocket_center(args.pocket_center),
            pocket_ligand=args.pocket_ligand,
            pocket_radius=args.pocket_radius,
        )
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
