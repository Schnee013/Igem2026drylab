#!/usr/bin/env python3
"""Validate GROMACS input or warning evidence against an explicit JSON contract.

Supported local runnable-input gates:

* ``input``: checks checksums, include paths/duplicates, topology molecule
  counts, coordinate molecule/atom order, ASCR3 order, and package-local index.
* ``warning``: normalizes GROMACS warning blocks, enforces an exact reviewed
  whitelist, checks the recorded exit code, and scans terminal failure terms.
* ``geometry``: audits one named molecule type against its bonded equilibrium
  distances, with periodic minimum-image handling and contract-supplied
  operational thresholds.

All expected values come from the supplied contract.  No Gpr2 counts, ligand
names, lipid counts, geometry thresholds, warning counts, or MAXWARN values are
built into this validator.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shlex
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from assemble_complex import (
    parse_gro,
    parse_itp_atoms,
    parse_topology_molecules,
    sha256,
    topology_molecule_counts,
    topology_includes,
    write_tsv,
)


FAILURE_TERMS = (
    "fatal error",
    "segmentation fault",
    "segfault",
    "out of memory",
    "killed",
    "cudaerror",
    "invalid ptx",
    "nan",
    "lincs warning",
)


def require_fields(mapping: dict[str, Any], fields: Iterable[str], label: str) -> None:
    missing = sorted(set(fields) - set(mapping))
    if missing:
        raise ValueError(f"{label} missing required fields: {missing}")


def load_contract(path: Path, gate: str) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    require_fields(contract, {"contract_id", "arm", "files", "expected"}, "contract")
    if contract.get("gate") != gate:
        raise ValueError(f"contract gate mismatch: {contract.get('gate')} != {gate}")
    return contract


def resolve_path(contract_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (contract_path.parent / path).resolve()


def parse_index(path: Path) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {}
    current: str | None = None
    header = re.compile(r"^\s*\[\s*(.+?)\s*\]\s*$")
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith(";"):
            continue
        match = header.match(raw)
        if match:
            current = match.group(1)
            if current in groups:
                raise ValueError(f"duplicate index group {current} in {path}")
            groups[current] = []
            continue
        if current is None:
            raise ValueError(f"index values before first group at line {line_number}")
        for token in raw.split():
            if not token.isdigit():
                raise ValueError(
                    f"invalid/possibly concatenated index token {token!r} "
                    f"at {path}:{line_number}"
                )
            groups[current].append(int(token))
    if not groups:
        raise ValueError(f"no index groups in {path}")
    return groups


def parse_molecule_type_atoms(path: Path) -> dict[str, list[str]]:
    section = ""
    current_moltype: str | None = None
    result: dict[str, list[str]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r"\[\s*([^\]]+?)\s*\]", line)
        if match:
            section = match.group(1).strip().lower()
            continue
        if line.startswith("#"):
            continue
        fields = line.split()
        if section == "moleculetype":
            current_moltype = fields[0]
            if current_moltype in result:
                raise ValueError(f"duplicate moleculetype {current_moltype} in {path}")
            result[current_moltype] = []
        elif section == "atoms" and current_moltype is not None:
            if len(fields) < 5:
                raise ValueError(f"malformed [ atoms ] row in {path}: {raw}")
            result[current_moltype].append(fields[4])
    return {name: atoms for name, atoms in result.items() if atoms}


def included_molecule_types(topology: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for include in topology_includes(topology):
        include_path = topology.parent / include
        if not include_path.is_file():
            raise FileNotFoundError(f"topology include does not exist: {include_path}")
        for moltype, atoms in parse_molecule_type_atoms(include_path).items():
            if moltype in result:
                raise ValueError(f"duplicate included moleculetype: {moltype}")
            result[moltype] = atoms
    return result


def validate_coordinate_blocks(
    atoms: list[dict[str, Any]],
    topology_rows: list[tuple[str, int]],
    moltype_atoms: dict[str, list[str]],
) -> list[tuple[str, int, int, int, str]]:
    cursor = 0
    audit = []
    for moltype, molecule_count in topology_rows:
        if moltype not in moltype_atoms:
            raise ValueError(f"no included [ atoms ] definition for {moltype}")
        names = moltype_atoms[moltype]
        atoms_per_molecule = len(names)
        for molecule_index in range(molecule_count):
            block = atoms[cursor : cursor + atoms_per_molecule]
            if len(block) != atoms_per_molecule:
                raise ValueError(
                    f"coordinate truncated inside {moltype} molecule {molecule_index + 1}"
                )
            actual_names = [atom["atomname"] for atom in block]
            if actual_names != names:
                first = next(
                    (
                        index
                        for index, (actual, expected) in enumerate(
                            zip(actual_names, names, strict=True), 1
                        )
                        if actual != expected
                    ),
                    None,
                )
                raise ValueError(
                    f"coordinate atom order mismatch for {moltype} molecule "
                    f"{molecule_index + 1} at local atom {first}"
                )
            cursor += atoms_per_molecule
        audit.append(
            (
                moltype,
                molecule_count,
                atoms_per_molecule,
                molecule_count * atoms_per_molecule,
                "PASS",
            )
        )
    if cursor != len(atoms):
        raise ValueError(
            f"coordinate/topology atom total mismatch: consumed {cursor}, "
            f"coordinate has {len(atoms)}"
        )
    return audit


def validate_input(contract_path: Path, contract: dict[str, Any], output_dir: Path) -> None:
    files = contract["files"]
    expected = contract["expected"]
    require_fields(
        files,
        {"coordinate", "topology", "index", "ligand_itp"},
        "input files",
    )
    require_fields(
        expected,
        {
            "coordinate_atom_count",
            "molecule_counts",
            "ligand_moltype",
            "ligand_atom_count",
            "ligand_atom_names",
            "required_index_groups",
            "index_group_counts",
            "checksums",
        },
        "input expected",
    )
    paths = {name: resolve_path(contract_path, value) for name, value in files.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"contract input files missing: {missing}")

    checksum_rows = []
    expected_checksums = expected["checksums"]
    require_fields(expected_checksums, files.keys(), "input expected.checksums")
    for name, path in paths.items():
        actual = sha256(path)
        wanted = expected_checksums[name]
        status = "PASS" if actual == wanted else "FAIL"
        checksum_rows.append((name, str(path), actual, wanted, status))
        if status == "FAIL":
            raise ValueError(f"checksum mismatch for {name}: {path}")

    coordinate = paths["coordinate"]
    topology = paths["topology"]
    index_path = paths["index"]
    ligand_itp = paths["ligand_itp"]
    _, atoms, _ = parse_gro(coordinate)
    if len(atoms) != int(expected["coordinate_atom_count"]):
        raise ValueError("coordinate atom count does not match expected contract")

    includes = topology_includes(topology)
    duplicate_includes = sorted(
        {include for include in includes if includes.count(include) > 1}
    )
    if duplicate_includes:
        raise ValueError(f"duplicate topology includes: {duplicate_includes}")
    include_rows = []
    for include in includes:
        include_path = topology.parent / include
        status = "PASS" if include_path.is_file() else "FAIL"
        include_rows.append((include, str(include_path), includes.count(include), status))
        if status == "FAIL":
            raise FileNotFoundError(include_path)

    topology_rows = parse_topology_molecules(topology)
    actual_molecule_counts = topology_molecule_counts(topology_rows)
    expected_molecule_counts = Counter(
        {str(key): int(value) for key, value in expected["molecule_counts"].items()}
    )
    if actual_molecule_counts != expected_molecule_counts:
        raise ValueError(
            f"topology [ molecules ] mismatch: {actual_molecule_counts} "
            f"!= {expected_molecule_counts}"
        )
    moltype_atoms = included_molecule_types(topology)
    molecule_audit = validate_coordinate_blocks(atoms, topology_rows, moltype_atoms)

    ligand_moltype = expected["ligand_moltype"]
    ligand_names = parse_itp_atoms(ligand_itp, expected_moltype=ligand_moltype)
    if ligand_names != expected["ligand_atom_names"]:
        raise ValueError("ligand ITP atom order does not match expected contract")
    if len(ligand_names) != int(expected["ligand_atom_count"]):
        raise ValueError("ligand ITP atom count does not match expected contract")
    if moltype_atoms.get(ligand_moltype) != ligand_names:
        raise ValueError("included ligand ITP does not match named ligand ITP")

    groups = parse_index(index_path)
    required_groups = [str(value) for value in expected["required_index_groups"]]
    expected_group_counts = {
        str(name): int(count)
        for name, count in expected["index_group_counts"].items()
    }
    if set(groups) != set(expected_group_counts):
        raise ValueError(
            f"index group name set mismatch: {sorted(groups)} "
            f"!= {sorted(expected_group_counts)}"
        )
    index_rows = []
    for name, values in groups.items():
        if name in required_groups and not values:
            raise ValueError(f"required index group is empty: {name}")
        if any(value < 1 or value > len(atoms) for value in values):
            raise ValueError(f"index group has out-of-range atom number: {name}")
        if len(values) != len(set(values)):
            raise ValueError(f"index group has duplicate atom numbers: {name}")
        actual = len(values)
        wanted = expected_group_counts[name]
        status = "PASS" if actual == wanted else "FAIL"
        index_rows.append((name, actual, wanted, status))
        if status == "FAIL":
            raise ValueError(f"index group count mismatch: {name}")

    write_tsv(
        output_dir / "input_checksum_audit.tsv",
        ["role", "path", "actual_sha256", "expected_sha256", "status"],
        checksum_rows,
    )
    write_tsv(
        output_dir / "include_audit.tsv",
        ["include", "resolved_path", "count", "status"],
        include_rows,
    )
    write_tsv(
        output_dir / "molecule_atom_audit.tsv",
        [
            "molecule",
            "molecule_count",
            "atoms_per_molecule",
            "coordinate_atoms",
            "status",
        ],
        molecule_audit,
    )
    write_tsv(
        output_dir / "index_audit.tsv",
        ["group", "actual_count", "expected_count", "status"],
        index_rows,
    )
    write_tsv(
        output_dir / "input_summary.tsv",
        ["check", "actual", "expected", "status"],
        [
            (
                "coordinate_atom_count",
                len(atoms),
                expected["coordinate_atom_count"],
                "PASS",
            ),
            (
                "ligand_atom_count",
                len(ligand_names),
                expected["ligand_atom_count"],
                "PASS",
            ),
            (
                "topology_molecule_counts",
                json.dumps(dict(actual_molecule_counts), sort_keys=True),
                json.dumps(dict(expected_molecule_counts), sort_keys=True),
                "PASS",
            ),
            (
                "index_group_counts",
                json.dumps({name: len(values) for name, values in groups.items()}, sort_keys=True),
                json.dumps(expected_group_counts, sort_keys=True),
                "PASS",
            ),
        ],
    )
    write_tsv(
        output_dir / "terminal_status.tsv",
        ["gate", "status", "detail"],
        [("input", "PASS", contract["contract_id"])],
    )


def parse_molecule_bond_definition(
    path: Path,
    expected_moltype: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    section = ""
    moltype: str | None = None
    atoms: list[dict[str, Any]] = []
    bonds: list[dict[str, Any]] = []
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw.split(";", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"\[\s*([^\]]+?)\s*\]", line)
        if match:
            section = match.group(1).strip().lower()
            continue
        fields = line.split()
        if section == "moleculetype" and moltype is None:
            moltype = fields[0]
        elif section == "atoms":
            if len(fields) < 5:
                raise ValueError(f"malformed [ atoms ] row at {path}:{line_number}")
            atoms.append(
                {
                    "index": int(fields[0]),
                    "atom_type": fields[1],
                    "atom_name": fields[4],
                }
            )
        elif section == "bonds":
            if len(fields) < 3:
                raise ValueError(f"malformed [ bonds ] row at {path}:{line_number}")
            bonds.append(
                {
                    "atom_i": int(fields[0]),
                    "atom_j": int(fields[1]),
                    "function": int(fields[2]),
                    "inline_b0_nm": float(fields[3]) if len(fields) >= 4 else None,
                    "line_number": line_number,
                }
            )
    if moltype != expected_moltype:
        raise ValueError(
            f"moleculetype mismatch in {path}: {moltype} != {expected_moltype}"
        )
    expected_indices = list(range(1, len(atoms) + 1))
    actual_indices = [int(row["index"]) for row in atoms]
    if actual_indices != expected_indices:
        raise ValueError(f"non-contiguous [ atoms ] indices in {path}")
    if not bonds:
        raise ValueError(f"no [ bonds ] entries in {path}")
    valid_indices = set(expected_indices)
    for bond in bonds:
        if bond["atom_i"] not in valid_indices or bond["atom_j"] not in valid_indices:
            raise ValueError(
                f"bond references unknown atom at {path}:{bond['line_number']}"
            )
    return atoms, bonds


def parse_bondtypes(path: Path) -> dict[tuple[str, str, int], float]:
    section = ""
    result: dict[tuple[str, str, int], float] = {}
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw.split(";", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"\[\s*([^\]]+?)\s*\]", line)
        if match:
            section = match.group(1).strip().lower()
            continue
        if section != "bondtypes":
            continue
        fields = line.split()
        if len(fields) < 5:
            raise ValueError(f"malformed [ bondtypes ] row at {path}:{line_number}")
        atom_i, atom_j = sorted((fields[0], fields[1]))
        key = (atom_i, atom_j, int(fields[2]))
        b0_nm = float(fields[3])
        if key in result and not math.isclose(
            result[key], b0_nm, rel_tol=0.0, abs_tol=1e-12
        ):
            raise ValueError(
                f"conflicting equilibrium bond lengths for {key} in {path}"
            )
        result[key] = b0_nm
    if not result:
        raise ValueError(f"no [ bondtypes ] entries in {path}")
    return result


def gro_box_matrix(box_line: str) -> list[list[float]]:
    values = [float(value) for value in box_line.split()]
    if len(values) == 3:
        return [
            [values[0], 0.0, 0.0],
            [0.0, values[1], 0.0],
            [0.0, 0.0, values[2]],
        ]
    if len(values) == 9:
        return [
            [values[0], values[5], values[7]],
            [values[3], values[1], values[8]],
            [values[4], values[6], values[2]],
        ]
    raise ValueError(f"GRO box must contain 3 or 9 values, found {len(values)}")


def invert_3x3(matrix: list[list[float]]) -> list[list[float]]:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    determinant = (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    )
    if math.isclose(determinant, 0.0, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("GRO box matrix is singular")
    return [
        [
            (e * i - f * h) / determinant,
            (c * h - b * i) / determinant,
            (b * f - c * e) / determinant,
        ],
        [
            (f * g - d * i) / determinant,
            (a * i - c * g) / determinant,
            (c * d - a * f) / determinant,
        ],
        [
            (d * h - e * g) / determinant,
            (b * g - a * h) / determinant,
            (a * e - b * d) / determinant,
        ],
    ]


def matrix_vector(
    matrix: list[list[float]],
    vector: tuple[float, float, float] | list[float],
) -> list[float]:
    return [
        sum(row[column] * vector[column] for column in range(3))
        for row in matrix
    ]


def minimum_image_distance(
    atom_i: dict[str, Any],
    atom_j: dict[str, Any],
    box: list[list[float]],
    inverse_box: list[list[float]],
) -> float:
    delta = (
        float(atom_j["x"]) - float(atom_i["x"]),
        float(atom_j["y"]) - float(atom_i["y"]),
        float(atom_j["z"]) - float(atom_i["z"]),
    )
    fractional = matrix_vector(inverse_box, delta)
    wrapped = [value - round(value) for value in fractional]
    cartesian = matrix_vector(box, wrapped)
    return math.sqrt(sum(value * value for value in cartesian))


def target_molecule_blocks(
    atoms: list[dict[str, Any]],
    topology_rows: list[tuple[str, int]],
    moltype_atoms: dict[str, list[str]],
    target_moltype: str,
) -> list[tuple[int, list[dict[str, Any]]]]:
    cursor = 0
    target_index = 0
    blocks: list[tuple[int, list[dict[str, Any]]]] = []
    for moltype, molecule_count in topology_rows:
        if moltype not in moltype_atoms:
            raise ValueError(f"no included [ atoms ] definition for {moltype}")
        expected_names = moltype_atoms[moltype]
        atoms_per_molecule = len(expected_names)
        for _ in range(molecule_count):
            block = [
                dict(atom, global_index=cursor + offset + 1)
                for offset, atom in enumerate(
                    atoms[cursor : cursor + atoms_per_molecule]
                )
            ]
            if len(block) != atoms_per_molecule:
                raise ValueError(f"coordinate truncated inside {moltype}")
            actual_names = [atom["atomname"] for atom in block]
            if actual_names != expected_names:
                raise ValueError(
                    f"coordinate atom order mismatch for {moltype} at atom {cursor + 1}"
                )
            if moltype == target_moltype:
                target_index += 1
                blocks.append((target_index, block))
            cursor += atoms_per_molecule
    if cursor != len(atoms):
        raise ValueError(
            f"coordinate/topology atom total mismatch: consumed {cursor}, "
            f"coordinate has {len(atoms)}"
        )
    return blocks


def validate_geometry(
    contract_path: Path,
    contract: dict[str, Any],
    output_dir: Path,
) -> None:
    files = contract["files"]
    expected = contract["expected"]
    require_fields(
        files,
        {"coordinate", "topology", "molecule_itp", "forcefield_itp"},
        "geometry files",
    )
    require_fields(
        expected,
        {
            "coordinate_atom_count",
            "molecule_type",
            "molecule_count",
            "bond_deviation_threshold_nm",
            "max_outlier_bonds",
            "max_abs_bond_deviation_nm",
            "criterion_label",
            "checksums",
        },
        "geometry expected",
    )
    paths = {name: resolve_path(contract_path, value) for name, value in files.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"geometry input files missing: {missing}")

    checksum_rows = []
    expected_checksums = expected["checksums"]
    unknown_checksum_names = sorted(set(expected_checksums) - set(paths))
    if unknown_checksum_names:
        raise ValueError(
            f"geometry checksum names unknown files: {unknown_checksum_names}"
        )
    for name, path in paths.items():
        actual = sha256(path)
        wanted = expected_checksums.get(name, "RUNTIME_OUTPUT_RECORDED_ONLY")
        status = "PASS" if wanted == "RUNTIME_OUTPUT_RECORDED_ONLY" or actual == wanted else "FAIL"
        checksum_rows.append((name, str(path), actual, wanted, status))
        if status == "FAIL":
            raise ValueError(f"geometry checksum mismatch for {name}: {path}")

    _, coordinate_atoms, box_line = parse_gro(paths["coordinate"])
    expected_atom_count = int(expected["coordinate_atom_count"])
    if len(coordinate_atoms) != expected_atom_count:
        raise ValueError(
            f"coordinate atom count mismatch: {len(coordinate_atoms)} "
            f"!= {expected_atom_count}"
        )
    molecule_type = str(expected["molecule_type"])
    molecule_atoms, bonds = parse_molecule_bond_definition(
        paths["molecule_itp"], molecule_type
    )
    moltype_atoms = included_molecule_types(paths["topology"])
    expected_names = [str(row["atom_name"]) for row in molecule_atoms]
    if moltype_atoms.get(molecule_type) != expected_names:
        raise ValueError(
            f"topology include atom definition does not match {paths['molecule_itp']}"
        )
    blocks = target_molecule_blocks(
        coordinate_atoms,
        parse_topology_molecules(paths["topology"]),
        moltype_atoms,
        molecule_type,
    )
    expected_molecule_count = int(expected["molecule_count"])
    if len(blocks) != expected_molecule_count:
        raise ValueError(
            f"{molecule_type} molecule count mismatch: {len(blocks)} "
            f"!= {expected_molecule_count}"
        )

    bondtypes = parse_bondtypes(paths["forcefield_itp"])
    box = gro_box_matrix(box_line)
    inverse_box = invert_3x3(box)
    deviation_threshold = float(expected["bond_deviation_threshold_nm"])
    outliers = []
    maximum: dict[str, Any] | None = None
    bonds_audited = 0
    for molecule_index, block in blocks:
        for bond in bonds:
            local_i = int(bond["atom_i"])
            local_j = int(bond["atom_j"])
            definition_i = molecule_atoms[local_i - 1]
            definition_j = molecule_atoms[local_j - 1]
            b0_nm = bond["inline_b0_nm"]
            if b0_nm is None:
                atom_type_i, atom_type_j = sorted(
                    (
                        str(definition_i["atom_type"]),
                        str(definition_j["atom_type"]),
                    )
                )
                key = (atom_type_i, atom_type_j, int(bond["function"]))
                if key not in bondtypes:
                    raise ValueError(
                        f"no equilibrium bond type for {key} "
                        f"at {paths['molecule_itp']}:{bond['line_number']}"
                    )
                b0_nm = bondtypes[key]
            coordinate_i = block[local_i - 1]
            coordinate_j = block[local_j - 1]
            observed_nm = minimum_image_distance(
                coordinate_i, coordinate_j, box, inverse_box
            )
            deviation_nm = abs(observed_nm - float(b0_nm))
            bonds_audited += 1
            row = {
                "molecule_index": molecule_index,
                "coordinate_residue": coordinate_i["resnum"],
                "atom_i_local": local_i,
                "atom_j_local": local_j,
                "atom_i_name": definition_i["atom_name"],
                "atom_j_name": definition_j["atom_name"],
                "atom_i_global": coordinate_i["global_index"],
                "atom_j_global": coordinate_j["global_index"],
                "equilibrium_nm": float(b0_nm),
                "observed_nm": observed_nm,
                "abs_deviation_nm": deviation_nm,
            }
            if maximum is None or deviation_nm > float(maximum["abs_deviation_nm"]):
                maximum = row
            if deviation_nm > deviation_threshold:
                outliers.append(row)
    if maximum is None:
        raise ValueError(f"no {molecule_type} bonds audited")

    failures = []
    if len(outliers) > int(expected["max_outlier_bonds"]):
        failures.append(
            f"outlier bonds {len(outliers)} > {expected['max_outlier_bonds']}"
        )
    if float(maximum["abs_deviation_nm"]) > float(
        expected["max_abs_bond_deviation_nm"]
    ):
        failures.append(
            "maximum absolute bond deviation "
            f"{maximum['abs_deviation_nm']:.6f} > "
            f"{float(expected['max_abs_bond_deviation_nm']):.6f} nm"
        )

    write_tsv(
        output_dir / "geometry_checksum_audit.tsv",
        ["role", "path", "actual_sha256", "expected_sha256", "status"],
        checksum_rows,
    )
    audit_header = [
        "molecule_index",
        "coordinate_residue",
        "atom_i_local",
        "atom_j_local",
        "atom_i_name",
        "atom_j_name",
        "atom_i_global",
        "atom_j_global",
        "equilibrium_nm",
        "observed_nm",
        "abs_deviation_nm",
    ]
    write_tsv(
        output_dir / "geometry_bond_outliers.tsv",
        audit_header,
        [
            (
                row["molecule_index"],
                row["coordinate_residue"],
                row["atom_i_local"],
                row["atom_j_local"],
                row["atom_i_name"],
                row["atom_j_name"],
                row["atom_i_global"],
                row["atom_j_global"],
                f"{row['equilibrium_nm']:.6f}",
                f"{row['observed_nm']:.6f}",
                f"{row['abs_deviation_nm']:.6f}",
            )
            for row in sorted(
                outliers,
                key=lambda item: float(item["abs_deviation_nm"]),
                reverse=True,
            )
        ],
    )
    write_tsv(
        output_dir / "geometry_summary.tsv",
        ["key", "value"],
        [
            ("status", "BLOCKED" if failures else "PASS"),
            ("criterion_label", expected["criterion_label"]),
            ("molecule_type", molecule_type),
            ("molecule_count", len(blocks)),
            ("bonds_per_molecule", len(bonds)),
            ("bonds_audited", bonds_audited),
            ("bond_deviation_threshold_nm", f"{deviation_threshold:.6f}"),
            ("outlier_bonds", len(outliers)),
            (
                "max_allowed_outlier_bonds",
                int(expected["max_outlier_bonds"]),
            ),
            (
                "maximum_abs_bond_deviation_nm",
                f"{maximum['abs_deviation_nm']:.6f}",
            ),
            (
                "max_allowed_abs_bond_deviation_nm",
                f"{float(expected['max_abs_bond_deviation_nm']):.6f}",
            ),
            (
                "maximum_pair",
                f"{maximum['molecule_index']}:{maximum['atom_i_name']}-"
                f"{maximum['atom_j_name']}",
            ),
        ],
    )

    if failures:
        raise ValueError("; ".join(failures))
    write_tsv(
        output_dir / "terminal_status.tsv",
        ["gate", "status", "detail"],
        [("geometry", "PASS", contract["contract_id"])],
    )


def normalize_warning_blocks(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    warnings = []
    index = 0
    header_pattern = re.compile(r"^\s*WARNING\s+\d+\s+\[(.+?)\]:\s*$")
    while index < len(lines):
        match = header_pattern.match(lines[index])
        if not match:
            index += 1
            continue
        source = " ".join(match.group(1).split())
        index += 1
        body = []
        while index < len(lines):
            if header_pattern.match(lines[index]):
                break
            if not lines[index].strip():
                if body:
                    index += 1
                    break
                index += 1
                continue
            body.append(lines[index].strip())
            index += 1
        normalized_body = " ".join(" ".join(body).split())
        normalized = f"{source}|{normalized_body}"
        warnings.append(
            {
                "source": source,
                "normalized_text": normalized_body,
                "fingerprint_sha256": hashlib.sha256(
                    normalized.encode("utf-8")
                ).hexdigest(),
            }
        )
    return warnings


def validate_warning(
    contract_path: Path,
    contract: dict[str, Any],
    output_dir: Path,
) -> None:
    files = contract["files"]
    expected = contract["expected"]
    require_fields(files, {"grompp_log", "exit_code"}, "warning files")
    require_fields(
        expected,
        {
            "warning_count",
            "accepted_warnings",
            "expected_exit_code",
            "forbidden_terms",
            "checksums",
        },
        "warning expected",
    )
    paths = {name: resolve_path(contract_path, value) for name, value in files.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"warning evidence files missing: {missing}")
    for name, wanted in expected["checksums"].items():
        if name not in paths:
            raise ValueError(f"warning checksum names unknown file: {name}")
        if sha256(paths[name]) != wanted:
            raise ValueError(f"warning evidence checksum mismatch: {name}")

    log_text = paths["grompp_log"].read_text(encoding="utf-8", errors="replace")
    warnings = normalize_warning_blocks(log_text)
    actual_fingerprints = Counter(row["fingerprint_sha256"] for row in warnings)
    accepted_fingerprints: Counter[str] = Counter()
    review_by_fingerprint: dict[str, dict[str, Any]] = {}
    for row in expected["accepted_warnings"]:
        require_fields(
            row,
            {"fingerprint_sha256", "count", "review_status", "review_note"},
            "accepted warning",
        )
        if not str(row["review_status"]).startswith("ACCEPTED"):
            raise ValueError(f"warning whitelist row not accepted: {row}")
        fingerprint = row["fingerprint_sha256"]
        accepted_fingerprints[fingerprint] += int(row["count"])
        review_by_fingerprint[fingerprint] = row
    if len(warnings) != int(expected["warning_count"]):
        raise ValueError(
            f"warning count mismatch: {len(warnings)} != {expected['warning_count']}"
        )
    if actual_fingerprints != accepted_fingerprints:
        raise ValueError(
            f"unexpected/missing warning fingerprints: actual={actual_fingerprints}, "
            f"accepted={accepted_fingerprints}"
        )

    exit_text = paths["exit_code"].read_text(encoding="utf-8").strip()
    exit_code = int(exit_text)
    if exit_code != int(expected["expected_exit_code"]):
        raise ValueError(
            f"grompp exit-code mismatch: {exit_code} "
            f"!= {expected['expected_exit_code']}"
        )
    forbidden = [str(value).lower() for value in expected["forbidden_terms"]]
    unexpected_terms = sorted(
        {
            term
            for term in (*FAILURE_TERMS, *forbidden)
            if term and term in log_text.lower()
        }
    )
    if unexpected_terms:
        raise ValueError(f"terminal failure terms in grompp log: {unexpected_terms}")

    write_tsv(
        output_dir / "warning_inventory.tsv",
        [
            "ordinal",
            "source",
            "normalized_text",
            "fingerprint_sha256",
            "review_status",
            "review_note",
        ],
        [
            (
                index,
                row["source"],
                row["normalized_text"],
                row["fingerprint_sha256"],
                review_by_fingerprint[row["fingerprint_sha256"]]["review_status"],
                review_by_fingerprint[row["fingerprint_sha256"]]["review_note"],
            )
            for index, row in enumerate(warnings, 1)
        ],
    )
    write_tsv(
        output_dir / "warning_summary.tsv",
        ["check", "actual", "expected", "status"],
        [
            ("warning_count", len(warnings), expected["warning_count"], "PASS"),
            ("grompp_exit_code", exit_code, expected["expected_exit_code"], "PASS"),
            ("unexpected_warning", 0, 0, "PASS"),
            ("terminal_failure_terms", "", "", "PASS"),
        ],
    )
    write_tsv(
        output_dir / "terminal_status.tsv",
        ["gate", "status", "detail"],
        [("warning", "PASS", contract["contract_id"])],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=["input", "warning", "geometry"])
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--coordinate-override",
        type=Path,
        help="geometry gate only: audit this runtime coordinate with the frozen contract",
    )
    args = parser.parse_args()
    if args.coordinate_override is not None and args.gate != "geometry":
        parser.error("--coordinate-override is only valid for the geometry gate")
    if args.output_dir.exists():
        raise FileExistsError(f"refusing to overwrite validation output: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    try:
        contract = load_contract(args.contract, args.gate)
        if args.coordinate_override is not None:
            contract["files"]["coordinate"] = str(args.coordinate_override.resolve())
            contract["expected"]["checksums"].pop("coordinate", None)
        if args.gate == "input":
            validate_input(args.contract, contract, args.output_dir)
        elif args.gate == "warning":
            validate_warning(args.contract, contract, args.output_dir)
        else:
            validate_geometry(args.contract, contract, args.output_dir)
    except Exception as error:
        write_tsv(
            args.output_dir / "terminal_status.tsv",
            ["gate", "status", "detail"],
            [(args.gate, "BLOCKED", str(error))],
        )
        (args.output_dir / "failure_command.txt").write_text(
            shlex.join([sys.executable, *sys.argv]) + "\n", encoding="utf-8"
        )
        (args.output_dir / "failure_stdout_stderr.txt").write_text(
            f"{type(error).__name__}: {error}\n", encoding="utf-8"
        )
        print(f"ERROR: {error}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
