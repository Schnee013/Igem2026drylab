#!/usr/bin/env python3
"""Check explicit SDF-to-PDBQT atom mapping without auto-repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from atomic_publish import publish_staged_file
from docking_tool_result import ToolArtifact, write_tool_result


class CliError(ValueError):
    """User-correctable CLI or input error."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, f"Error: {message}\nUse -h or --help for details.\n")


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(
        description=(
            "Check heavy atom, element, coordinate, explicit atom-map, and mapped "
            "bond/stereo consistency between an SDF microstate and a PDBQT output. "
            "The command reports exact mismatches and never reorders or repairs atoms."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Atom-map JSON format:
  {
    "atoms": [{"sdf_atom": 1, "smiles_atom": 1, "pdbqt_atom": 1}],
    "bonds": [{"pdbqt_atom_1": 1, "pdbqt_atom_2": 2, "order": 1, "stereo": 0}]
  }
Each atom row is checked independently against Meeko REMARK SMILES IDX and
REMARK INDEX MAP metadata.
Examples:
  python src/check_sdf_pdbqt_mapping.py --sdf ligand.sdf --pdbqt ligand.pdbqt --atom-map ligand_map.json --coordinate-tolerance 0.001
""",
    )
    parser.add_argument("--sdf", required=True, type=Path, help="Input SDF microstate.")
    parser.add_argument("--pdbqt", required=True, type=Path, help="Prepared PDBQT file.")
    parser.add_argument("--atom-map", required=True, type=Path, help="Explicit JSON atom/bond map to check.")
    parser.add_argument(
        "--coordinate-tolerance",
        required=True,
        type=float,
        help="Maximum allowed mapped coordinate distance in Angstrom; no default is provided.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON mismatch report path. Existing files are refused unless --overwrite is set.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing --output.")
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


def _validate_output_path(output: Path | None, inputs: Sequence[tuple[str, Path]]) -> None:
    if output is None:
        return
    resolved_output = _resolved(output)
    for option_name, input_path in inputs:
        if resolved_output == _resolved(input_path):
            raise CliError(f"--output must not be the same path as {option_name}")


def _numeric_error(path: Path, row: int, field: str, value: object, kind: str) -> CliError:
    return CliError(f"{path}: row {row} field {field!r} has invalid {kind} value {value!r}")


def _parse_int(value: object, path: Path, row: int, field: str) -> int:
    if isinstance(value, bool) or isinstance(value, float):
        raise _numeric_error(path, row, field, value, "integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise _numeric_error(path, row, field, value, "integer") from exc


def _parse_float(value: object, path: Path, row: int, field: str) -> float:
    if isinstance(value, bool):
        raise _numeric_error(path, row, field, value, "number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise _numeric_error(path, row, field, value, "number") from exc
    if not math.isfinite(parsed):
        raise _numeric_error(path, row, field, value, "finite number")
    return parsed


def _parse_sdf(path: Path) -> dict[str, Any]:
    text = _read_required_text(path, "SDF")
    lines = text.split("$$$$")[0].splitlines()
    if len(lines) < 4:
        raise CliError(f"{path}: SDF record is shorter than the V2000 header")
    if len(lines[3]) < 6:
        raise CliError(f"{path}: row 4 field 'counts' has invalid V2000 value {lines[3]!r}")
    atom_count = _parse_int(lines[3][0:3], path, 4, "atom_count")
    bond_count = _parse_int(lines[3][3:6], path, 4, "bond_count")
    if atom_count < 0:
        raise _numeric_error(path, 4, "atom_count", lines[3][0:3], "non-negative integer")
    if bond_count < 0:
        raise _numeric_error(path, 4, "bond_count", lines[3][3:6], "non-negative integer")
    expected = 4 + atom_count + bond_count
    if len(lines) < expected:
        raise CliError(f"{path}: SDF record ended before declared atoms/bonds were present")
    atoms = {}
    for index, line in enumerate(lines[4 : 4 + atom_count], start=1):
        row = index + 4
        fields = line.split()
        if len(fields) < 4:
            raise CliError(f"{path}: row {row} field 'atom' has invalid value {line!r}: fewer than 4 fields")
        atoms[index] = {
            "index": index,
            "element": fields[3],
            "x": _parse_float(fields[0], path, row, "x"),
            "y": _parse_float(fields[1], path, row, "y"),
            "z": _parse_float(fields[2], path, row, "z"),
        }
    bonds = []
    seen_bonds: set[tuple[int, int]] = set()
    for index, line in enumerate(lines[4 + atom_count : expected], start=1):
        row = 4 + atom_count + index
        fields = line.split()
        if len(fields) < 3:
            raise CliError(f"{path}: row {row} field 'bond' has invalid value {line!r}: fewer than 3 fields")
        atom_1 = _parse_int(fields[0], path, row, "atom_1")
        atom_2 = _parse_int(fields[1], path, row, "atom_2")
        order = _parse_int(fields[2], path, row, "order")
        stereo = _parse_int(fields[3], path, row, "stereo") if len(fields) > 3 else 0
        for field, value in (("atom_1", atom_1), ("atom_2", atom_2)):
            if value < 1 or value > atom_count:
                raise CliError(
                    f"{path}: row {row} field {field!r} has out-of-range value {value!r}; "
                    f"declared atom count is {atom_count}"
                )
        pair = tuple(sorted((atom_1, atom_2)))
        if atom_1 == atom_2 or pair in seen_bonds:
            raise CliError(f"{path}: row {row} field 'bond_atoms' has duplicate/self value {list(pair)!r}")
        seen_bonds.add(pair)
        bonds.append({"atom_1": atom_1, "atom_2": atom_2, "order": order, "stereo": stereo})
    return {"atoms": atoms, "bonds": bonds}


def _guess_element(atom_name: str, explicit: str) -> str:
    if explicit:
        atom_type = explicit.upper()
        autodock_elements = {
            "A": "C",
            "C": "C",
            "N": "N",
            "NA": "N",
            "NS": "N",
            "O": "O",
            "OA": "O",
            "OS": "O",
            "S": "S",
            "SA": "S",
            "P": "P",
            "F": "F",
            "CL": "Cl",
            "BR": "Br",
            "I": "I",
            "H": "H",
            "HD": "H",
            "HS": "H",
        }
        if atom_type in autodock_elements:
            return autodock_elements[atom_type]
    letters = "".join(ch for ch in atom_name if ch.isalpha())
    if not letters:
        return ""
    if len(letters) >= 2 and letters[:2].upper() in {"CL", "BR"}:
        return letters[:2].capitalize()
    return letters[0].upper()


def _parse_pdbqt(path: Path) -> dict[str, Any]:
    text = _read_required_text(path, "PDBQT")
    atoms: dict[int, dict[str, Any]] = {}
    smiles_values: list[tuple[int, str]] = []
    smiles_idx_tokens: list[tuple[int, str]] = []
    index_map_tokens: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("REMARK SMILES IDX"):
            prefix = "REMARK SMILES IDX"
            remainder = line[len(prefix) :].strip()
            if not remainder:
                raise CliError(
                    f"{path}: row {line_number} field 'REMARK SMILES IDX' has invalid value {remainder!r}"
                )
            smiles_idx_tokens.extend((line_number, token) for token in remainder.split())
            continue
        if line.startswith("REMARK INDEX MAP"):
            prefix = "REMARK INDEX MAP"
            remainder = line[len(prefix) :].strip()
            if not remainder:
                raise CliError(
                    f"{path}: row {line_number} field 'REMARK INDEX MAP' has invalid value {remainder!r}"
                )
            index_map_tokens.extend((line_number, token) for token in remainder.split())
            continue
        if line.startswith("REMARK SMILES"):
            prefix = "REMARK SMILES"
            smiles_values.append((line_number, line[len(prefix) :].strip()))
            continue
        if line[:6].strip() not in {"ATOM", "HETATM"}:
            continue
        serial = _parse_int(line[6:11].strip(), path, line_number, "serial")
        x = _parse_float(line[30:38].strip(), path, line_number, "x")
        y = _parse_float(line[38:46].strip(), path, line_number, "y")
        z = _parse_float(line[46:54].strip(), path, line_number, "z")
        if serial in atoms:
            raise CliError(f"{path}: row {line_number} field 'serial' has duplicate value {serial!r}")
        atom_name = line[12:16].strip()
        explicit = line[76:78].strip() if len(line) >= 78 else ""
        atoms[serial] = {
            "serial": serial,
            "element": _guess_element(atom_name, explicit),
            "x": x,
            "y": y,
            "z": z,
        }
    if not atoms:
        raise CliError(f"PDBQT has no ATOM/HETATM records: {path}")
    if len(smiles_values) != 1 or not smiles_values[0][1]:
        values = [value for _, value in smiles_values]
        raise CliError(
            f"{path}: required Meeko metadata 'REMARK SMILES' must occur once with a non-empty value; "
            f"found {values!r}"
        )
    if not smiles_idx_tokens:
        raise CliError(f"{path}: required Meeko metadata 'REMARK SMILES IDX' is missing")
    if len(smiles_idx_tokens) % 2:
        row, value = smiles_idx_tokens[-1]
        raise CliError(
            f"{path}: row {row} field 'REMARK SMILES IDX pair' has invalid value {value!r}: missing partner"
        )

    smiles_to_pdbqt: dict[int, int] = {}
    pdbqt_to_smiles: dict[int, int] = {}
    for offset in range(0, len(smiles_idx_tokens), 2):
        smiles_row, smiles_value = smiles_idx_tokens[offset]
        pdbqt_row, pdbqt_value = smiles_idx_tokens[offset + 1]
        smiles_atom = _parse_int(smiles_value, path, smiles_row, "SMILES_IDX_smiles_atom")
        pdbqt_atom = _parse_int(pdbqt_value, path, pdbqt_row, "SMILES_IDX_pdbqt_atom")
        if smiles_atom < 1:
            raise _numeric_error(path, smiles_row, "SMILES_IDX_smiles_atom", smiles_value, "positive integer")
        if pdbqt_atom < 1:
            raise _numeric_error(path, pdbqt_row, "SMILES_IDX_pdbqt_atom", pdbqt_value, "positive integer")
        if smiles_atom in smiles_to_pdbqt:
            raise CliError(
                f"{path}: row {smiles_row} field 'SMILES_IDX_smiles_atom' has duplicate value {smiles_atom!r}"
            )
        if pdbqt_atom in pdbqt_to_smiles:
            raise CliError(
                f"{path}: row {pdbqt_row} field 'SMILES_IDX_pdbqt_atom' has duplicate value {pdbqt_atom!r}"
            )
        smiles_to_pdbqt[smiles_atom] = pdbqt_atom
        pdbqt_to_smiles[pdbqt_atom] = smiles_atom

    if not index_map_tokens:
        raise CliError(f"{path}: required Meeko metadata 'REMARK INDEX MAP' is missing")
    if len(index_map_tokens) % 2:
        row, value = index_map_tokens[-1]
        raise CliError(
            f"{path}: row {row} field 'REMARK INDEX MAP pair' has invalid value {value!r}: missing partner"
        )

    sdf_to_pdbqt: dict[int, int] = {}
    pdbqt_to_sdf: dict[int, int] = {}
    for offset in range(0, len(index_map_tokens), 2):
        sdf_row, sdf_value = index_map_tokens[offset]
        pdbqt_row, pdbqt_value = index_map_tokens[offset + 1]
        sdf_atom = _parse_int(sdf_value, path, sdf_row, "INDEX_MAP_sdf_atom")
        pdbqt_atom = _parse_int(pdbqt_value, path, pdbqt_row, "INDEX_MAP_pdbqt_atom")
        if sdf_atom < 1:
            raise _numeric_error(path, sdf_row, "INDEX_MAP_sdf_atom", sdf_value, "positive integer")
        if pdbqt_atom < 1:
            raise _numeric_error(path, pdbqt_row, "INDEX_MAP_pdbqt_atom", pdbqt_value, "positive integer")
        if sdf_atom in sdf_to_pdbqt:
            raise CliError(f"{path}: row {sdf_row} field 'INDEX_MAP_sdf_atom' has duplicate value {sdf_atom!r}")
        if pdbqt_atom in pdbqt_to_sdf:
            raise CliError(
                f"{path}: row {pdbqt_row} field 'INDEX_MAP_pdbqt_atom' has duplicate value {pdbqt_atom!r}"
            )
        sdf_to_pdbqt[sdf_atom] = pdbqt_atom
        pdbqt_to_sdf[pdbqt_atom] = sdf_atom

    smiles = smiles_values[0][1]
    return {
        "atoms": atoms,
        "smiles": smiles,
        "smiles_sha256": hashlib.sha256(smiles.encode("utf-8")).hexdigest(),
        "smiles_to_pdbqt": smiles_to_pdbqt,
        "pdbqt_to_smiles": pdbqt_to_smiles,
        "sdf_to_pdbqt": sdf_to_pdbqt,
        "pdbqt_to_sdf": pdbqt_to_sdf,
    }


def _read_map(path: Path) -> dict[str, Any]:
    text = _read_required_text(path, "atom map JSON")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CliError(f"{path}: --atom-map is not valid JSON at row {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("atoms"), list):
        value = data.get("atoms") if isinstance(data, dict) else data
        raise CliError(f"{path}: row 1 field 'atoms' has invalid list value {value!r}")
    if "bonds" in data and not isinstance(data["bonds"], list):
        raise CliError(f"{path}: row 1 field 'bonds' has invalid list value {data['bonds']!r}")
    return data


def _distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    return math.sqrt(
        (first["x"] - second["x"]) ** 2
        + (first["y"] - second["y"]) ** 2
        + (first["z"] - second["z"]) ** 2
    )


def _map_row_int(row: object, path: Path, section: str, row_number: int, field: str) -> int:
    if not isinstance(row, dict):
        raise CliError(f"{path}: {section} row {row_number} field 'row' has invalid object value {row!r}")
    if field not in row:
        raise CliError(f"{path}: {section} row {row_number} field {field!r} has invalid value '<missing>'")
    return _parse_int(row[field], path, row_number, f"{section}.{field}")


def check_mapping(sdf_path: Path, pdbqt_path: Path, map_path: Path, tolerance: float) -> dict[str, Any]:
    if tolerance < 0 or not math.isfinite(tolerance):
        raise CliError("--coordinate-tolerance must be a finite non-negative number")
    sdf = _parse_sdf(sdf_path)
    pdbqt = _parse_pdbqt(pdbqt_path)
    pdbqt_atoms = pdbqt["atoms"]
    mapping = _read_map(map_path)
    mismatches: list[dict[str, Any]] = []

    sdf_heavy = {index: atom for index, atom in sdf["atoms"].items() if atom["element"].upper() != "H"}
    pdbqt_heavy = {index: atom for index, atom in pdbqt_atoms.items() if atom["element"].upper() != "H"}
    if len(sdf_heavy) != len(pdbqt_heavy):
        mismatches.append({"type": "heavy_atom_count", "sdf": len(sdf_heavy), "pdbqt": len(pdbqt_heavy)})

    mapped_sdf: set[int] = set()
    mapped_pdbqt: set[int] = set()
    mapped_smiles: set[int] = set()
    sdf_to_pdbqt: dict[int, int] = {}
    for row_number, row in enumerate(mapping["atoms"], start=1):
        sdf_atom = _map_row_int(row, map_path, "atoms", row_number, "sdf_atom")
        smiles_atom = _map_row_int(row, map_path, "atoms", row_number, "smiles_atom")
        pdbqt_atom = _map_row_int(row, map_path, "atoms", row_number, "pdbqt_atom")
        for field, value in (
            ("sdf_atom", sdf_atom),
            ("smiles_atom", smiles_atom),
            ("pdbqt_atom", pdbqt_atom),
        ):
            if value < 1:
                raise CliError(
                    f"{map_path}: atoms row {row_number} field {field!r} has invalid positive integer value {value!r}"
                )
        if sdf_atom in mapped_sdf:
            raise CliError(
                f"{map_path}: atoms row {row_number} field 'sdf_atom' has duplicate value {sdf_atom!r}"
            )
        if pdbqt_atom in mapped_pdbqt:
            raise CliError(
                f"{map_path}: atoms row {row_number} field 'pdbqt_atom' has duplicate value {pdbqt_atom!r}"
            )
        if smiles_atom in mapped_smiles:
            raise CliError(
                f"{map_path}: atoms row {row_number} field 'smiles_atom' has duplicate value {smiles_atom!r}"
            )
        mapped_sdf.add(sdf_atom)
        mapped_pdbqt.add(pdbqt_atom)
        mapped_smiles.add(smiles_atom)
        sdf_to_pdbqt[sdf_atom] = pdbqt_atom
        metadata_pdbqt_atom = pdbqt["smiles_to_pdbqt"].get(smiles_atom)
        if metadata_pdbqt_atom != pdbqt_atom:
            mismatches.append(
                {
                    "type": "smiles_idx_mapping",
                    "row": row_number,
                    "smiles_atom": smiles_atom,
                    "map_pdbqt_atom": pdbqt_atom,
                    "metadata_pdbqt_atom": metadata_pdbqt_atom,
                }
            )
        index_map_pdbqt_atom = pdbqt["sdf_to_pdbqt"].get(sdf_atom)
        if index_map_pdbqt_atom != pdbqt_atom:
            mismatches.append(
                {
                    "type": "index_map_mapping",
                    "row": row_number,
                    "sdf_atom": sdf_atom,
                    "map_pdbqt_atom": pdbqt_atom,
                    "metadata_pdbqt_atom": index_map_pdbqt_atom,
                }
            )
        if sdf_atom not in sdf_heavy:
            mismatches.append({"type": "mapped_sdf_atom_missing_or_hydrogen", "sdf_atom": sdf_atom})
            continue
        if pdbqt_atom not in pdbqt_heavy:
            mismatches.append({"type": "mapped_pdbqt_atom_missing_or_hydrogen", "pdbqt_atom": pdbqt_atom})
            continue
        sdf_atom_data = sdf_heavy[sdf_atom]
        pdbqt_atom_data = pdbqt_heavy[pdbqt_atom]
        if sdf_atom_data["element"].upper() != pdbqt_atom_data["element"].upper():
            mismatches.append(
                {
                    "type": "element",
                    "sdf_atom": sdf_atom,
                    "pdbqt_atom": pdbqt_atom,
                    "sdf_element": sdf_atom_data["element"],
                    "pdbqt_element": pdbqt_atom_data["element"],
                }
            )
        distance = _distance(sdf_atom_data, pdbqt_atom_data)
        if distance > tolerance:
            mismatches.append(
                {
                    "type": "coordinate",
                    "sdf_atom": sdf_atom,
                    "pdbqt_atom": pdbqt_atom,
                    "distance": distance,
                    "coordinate_tolerance": tolerance,
                }
            )

    missing_sdf = sorted(set(sdf_heavy) - mapped_sdf)
    missing_pdbqt = sorted(set(pdbqt_heavy) - mapped_pdbqt)
    if missing_sdf:
        mismatches.append({"type": "unmapped_sdf_heavy_atoms", "atoms": missing_sdf})
    if missing_pdbqt:
        mismatches.append({"type": "unmapped_pdbqt_heavy_atoms", "atoms": missing_pdbqt})
    missing_smiles = sorted(set(pdbqt["smiles_to_pdbqt"]) - mapped_smiles)
    extra_smiles = sorted(mapped_smiles - set(pdbqt["smiles_to_pdbqt"]))
    if missing_smiles:
        mismatches.append({"type": "unmapped_smiles_idx_atoms", "atoms": missing_smiles})
    if extra_smiles:
        mismatches.append({"type": "unknown_smiles_idx_atoms", "atoms": extra_smiles})
    metadata_pdbqt_atoms = set(pdbqt["pdbqt_to_smiles"])
    missing_metadata_pdbqt = sorted(set(pdbqt_heavy) - metadata_pdbqt_atoms)
    unknown_metadata_pdbqt = sorted(metadata_pdbqt_atoms - set(pdbqt_heavy))
    if missing_metadata_pdbqt:
        mismatches.append({"type": "pdbqt_heavy_atoms_missing_smiles_idx", "atoms": missing_metadata_pdbqt})
    if unknown_metadata_pdbqt:
        mismatches.append({"type": "smiles_idx_unknown_or_hydrogen_pdbqt_atoms", "atoms": unknown_metadata_pdbqt})
    index_map_heavy_sdf = {
        sdf_atom
        for sdf_atom, pdbqt_atom in pdbqt["sdf_to_pdbqt"].items()
        if pdbqt_atom in pdbqt_heavy
    }
    missing_index_map_sdf = sorted(set(sdf_heavy) - index_map_heavy_sdf)
    unknown_index_map_sdf = sorted(index_map_heavy_sdf - set(sdf_heavy))
    if missing_index_map_sdf:
        mismatches.append({"type": "sdf_heavy_atoms_missing_index_map", "atoms": missing_index_map_sdf})
    if unknown_index_map_sdf:
        mismatches.append({"type": "index_map_unknown_sdf_heavy_atoms", "atoms": unknown_index_map_sdf})
    index_map_pdbqt_atoms = set(pdbqt["pdbqt_to_sdf"])
    missing_index_map_pdbqt = sorted(set(pdbqt_atoms) - index_map_pdbqt_atoms)
    unknown_index_map_pdbqt = sorted(index_map_pdbqt_atoms - set(pdbqt_atoms))
    if missing_index_map_pdbqt:
        mismatches.append({"type": "pdbqt_atoms_missing_index_map", "atoms": missing_index_map_pdbqt})
    if unknown_index_map_pdbqt:
        mismatches.append({"type": "index_map_unknown_pdbqt_atoms", "atoms": unknown_index_map_pdbqt})

    expected_bonds: dict[tuple[int, int], dict[str, int]] = {}
    for row_number, row in enumerate(mapping.get("bonds", []), start=1):
        first = _map_row_int(row, map_path, "bonds", row_number, "pdbqt_atom_1")
        second = _map_row_int(row, map_path, "bonds", row_number, "pdbqt_atom_2")
        order = _map_row_int(row, map_path, "bonds", row_number, "order")
        stereo = 0
        if isinstance(row, dict) and "stereo" in row:
            stereo = _parse_int(row["stereo"], map_path, row_number, "bonds.stereo")
        for field, value in (("pdbqt_atom_1", first), ("pdbqt_atom_2", second), ("order", order)):
            if value < 1:
                raise CliError(
                    f"{map_path}: bonds row {row_number} field {field!r} has invalid positive integer value {value!r}"
                )
        pair = tuple(sorted((first, second)))
        if first == second:
            raise CliError(
                f"{map_path}: bonds row {row_number} field 'bond_atoms' has invalid self-bond value {list(pair)!r}"
            )
        if pair in expected_bonds:
            raise CliError(
                f"{map_path}: bonds row {row_number} field 'bond_atoms' has duplicate value {list(pair)!r}"
            )
        expected_bonds[pair] = {"order": order, "stereo": stereo}

    mapped_sdf_bonds: set[tuple[int, int]] = set()
    for bond in sdf["bonds"]:
        if bond["atom_1"] not in sdf_heavy or bond["atom_2"] not in sdf_heavy:
            continue
        if bond["atom_1"] not in sdf_to_pdbqt or bond["atom_2"] not in sdf_to_pdbqt:
            continue
        mapped_pair = tuple(sorted((sdf_to_pdbqt[bond["atom_1"]], sdf_to_pdbqt[bond["atom_2"]])))
        mapped_sdf_bonds.add(mapped_pair)
        expected = expected_bonds.get(mapped_pair)
        if expected is None:
            mismatches.append({"type": "missing_mapped_bond", "sdf_bond": bond, "mapped_pdbqt_pair": list(mapped_pair)})
            continue
        if expected["order"] != bond["order"] or expected["stereo"] != bond["stereo"]:
            mismatches.append(
                {
                    "type": "bond_order_or_stereo",
                    "sdf_bond": bond,
                    "mapped_pdbqt_pair": list(mapped_pair),
                    "mapped_bond": expected,
                }
            )
    for extra_pair in sorted(set(expected_bonds) - mapped_sdf_bonds):
        mismatches.append(
            {
                "type": "extra_mapped_bond",
                "mapped_pdbqt_pair": list(extra_pair),
                "mapped_bond": expected_bonds[extra_pair],
            }
        )

    mismatch_types = {item["type"] for item in mismatches}
    atom_mapping_mismatch_types = {
        "mapped_sdf_atom_missing_or_hydrogen",
        "mapped_pdbqt_atom_missing_or_hydrogen",
        "unmapped_sdf_heavy_atoms",
        "unmapped_pdbqt_heavy_atoms",
    }
    metadata_mismatch_types = atom_mapping_mismatch_types | {
        "smiles_idx_mapping",
        "index_map_mapping",
        "unmapped_smiles_idx_atoms",
        "unknown_smiles_idx_atoms",
        "pdbqt_heavy_atoms_missing_smiles_idx",
        "smiles_idx_unknown_or_hydrogen_pdbqt_atoms",
        "sdf_heavy_atoms_missing_index_map",
        "index_map_unknown_sdf_heavy_atoms",
        "pdbqt_atoms_missing_index_map",
        "index_map_unknown_pdbqt_atoms",
    }
    bond_mismatch_types = atom_mapping_mismatch_types | {
        "missing_mapped_bond",
        "bond_order_or_stereo",
        "extra_mapped_bond",
    }

    return {
        "sdf": str(sdf_path),
        "pdbqt": str(pdbqt_path),
        "atom_map": str(map_path),
        "coordinate_tolerance": tolerance,
        "sdf_heavy_atom_count": len(sdf_heavy),
        "pdbqt_heavy_atom_count": len(pdbqt_heavy),
        "sdf_element_counts": dict(sorted(Counter(atom["element"] for atom in sdf_heavy.values()).items())),
        "pdbqt_element_counts": dict(sorted(Counter(atom["element"] for atom in pdbqt_heavy.values()).items())),
        "mapping_metadata": {
            "pdbqt_smiles": pdbqt["smiles"],
            "pdbqt_smiles_sha256": pdbqt["smiles_sha256"],
            "pdbqt_smiles_present": True,
            "pdbqt_smiles_idx_pair_count": len(pdbqt["smiles_to_pdbqt"]),
            "pdbqt_index_map_pair_count": len(pdbqt["sdf_to_pdbqt"]),
            "user_atom_map_row_count": len(mapping["atoms"]),
            "user_bond_map_row_count": len(mapping.get("bonds", [])),
            "sdf_heavy_bond_count": len(mapped_sdf_bonds),
            "graph_stereo_verification_basis": (
                "SDF bond/order/stereo projected through an atom map independently anchored by Meeko INDEX MAP "
                "and SMILES IDX"
            ),
            "smiles_graph_parsing": "not_performed_without_a_full_SMILES_parser_dependency",
        },
        "checks": {
            "pdbqt_smiles_metadata_present": True,
            "pdbqt_index_map_metadata_present": True,
            "metadata_map_consistent": not bool(mismatch_types & metadata_mismatch_types),
            "sdf_bond_stereo_map_consistent": not bool(mismatch_types & bond_mismatch_types),
            "elements_consistent": "element" not in mismatch_types,
            "coordinates_within_tolerance": "coordinate" not in mismatch_types,
        },
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "scope": (
            "This report checks atom mapping, element identity, mapped bond order and stereo, "
            "and coordinate tolerance. PDBQT SMILES metadata is included but is not graph-parsed "
            "without a full SMILES parser. The report does not reorder or repair atoms and does "
            "not decide docking readiness."
        ),
    }


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _validate_output_path(
            args.output,
            (
                ("--sdf", args.sdf),
                ("--pdbqt", args.pdbqt),
                ("--atom-map", args.atom_map),
            ),
        )
        report = check_mapping(args.sdf, args.pdbqt, args.atom_map, args.coordinate_tolerance)
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            _atomic_write(args.output, rendered, args.overwrite)
        else:
            sys.stdout.write(rendered)
        if report["mismatch_count"]:
            print(f"Error: mapping mismatches found: {report['mismatch_count']}", file=sys.stderr)
            return 1
        write_tool_result(
            [ToolArtifact(args.output, "SDF-PDBQT 映射报告")]
            if args.output is not None
            else ()
        )
        return 0
    except CliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
