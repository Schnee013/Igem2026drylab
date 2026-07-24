#!/usr/bin/env python3
"""Prepare the shared Gpr3 ASCR3 coordinate and pair-specific clash evidence.

The selected 46-atom ligand is transformed in two explicit stages:

1. docking receptor -> PPM-oriented matched-WT receptor;
2. matched-WT receptor -> the reused WT CHARMM-GUI base frame.

The resulting base-frame ligand body is shared byte-for-byte by the WT and
R167Y arms.  The script audits the R167Y base against an independently derived
matched-WT -> R167Y-base bridge and refuses material frame disagreement.

Clash decisions use a dimensionless van-der-Waals overlap ratio rather than the
historical Gpr2 fixed-distance assumptions.  The radii and ratio cutoff are an
explicit project operational criterion pending source review; proposed POPC
removals remain PENDING_REVIEW until a separate reviewed TSV is created.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shlex
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from assemble_complex import (
    PROTEIN_RESNAMES,
    coordinate_molecule_counts,
    parse_gro,
    parse_topology_molecules,
    sha256,
    write_gro,
    write_tsv,
)


BACKBONE_NAMES = {"N", "CA", "C", "O"}
VDW_RADII_A = {
    "C": 1.70,
    "N": 1.55,
    "O": 1.52,
    "P": 1.80,
    "S": 1.80,
}
OVERLAP_RATIO_CUTOFF = 0.75
ALIGNMENT_SENSITIVITY_LIMIT_A = 0.50
CRITERION_STATUS = "OPERATIONAL_CRITERION_PENDING_SOURCE_REVIEW"
ALIGNMENT_SELECTIONS = {
    "common-ca",
    "common-backbone",
    "common-heavy",
    "plddt70-ca",
    "plddt80-ca",
    "plddt70-backbone",
}


def parse_pdb_atoms(
    path: Path,
    *,
    segment: str | None = None,
) -> dict[tuple[int, str], dict[str, Any]]:
    atoms: dict[tuple[int, str], dict[str, Any]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        if segment is not None and line[72:76].strip() != segment:
            continue
        key = (int(line[22:26]), line[12:16].strip())
        if key in atoms:
            raise ValueError(f"non-unique residue/atom mapping key {key} in {path}")
        atoms[key] = {
            "resid": key[0],
            "atomname": key[1],
            "resname": line[17:20].strip(),
            "xyz": np.array(
                [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            ),
            "bfactor": float(line[60:66] or 0.0),
            "line_number": line_number,
        }
    if not atoms:
        raise ValueError(f"no selected PDB atoms in {path}")
    return atoms


def alignment_keys(
    mobile: dict[tuple[int, str], dict[str, Any]],
    target: dict[tuple[int, str], dict[str, Any]],
    selection: str,
) -> list[tuple[int, str]]:
    if selection not in ALIGNMENT_SELECTIONS:
        raise ValueError(f"unsupported alignment selection: {selection}")
    keys = []
    for key, mobile_atom in mobile.items():
        target_atom = target.get(key)
        if target_atom is None or mobile_atom["resname"] != target_atom["resname"]:
            continue
        atomname = key[1]
        if selection == "common-ca" and atomname != "CA":
            continue
        if selection == "common-backbone" and atomname not in BACKBONE_NAMES:
            continue
        if selection == "common-heavy" and atomname.startswith("H"):
            continue
        if selection == "plddt70-ca" and (
            atomname != "CA" or mobile_atom["bfactor"] < 70.0
        ):
            continue
        if selection == "plddt80-ca" and (
            atomname != "CA" or mobile_atom["bfactor"] < 80.0
        ):
            continue
        if selection == "plddt70-backbone" and (
            atomname not in BACKBONE_NAMES or mobile_atom["bfactor"] < 70.0
        ):
            continue
        keys.append(key)
    keys.sort()
    if len(keys) < 3:
        raise ValueError(f"alignment selection has too few unique atoms: {selection}")
    return keys


def kabsch(
    mobile: dict[tuple[int, str], dict[str, Any]],
    target: dict[tuple[int, str], dict[str, Any]],
    keys: list[tuple[int, str]],
) -> tuple[np.ndarray, np.ndarray, float, float, np.ndarray]:
    xyz_mobile = np.array([mobile[key]["xyz"] for key in keys])
    xyz_target = np.array([target[key]["xyz"] for key in keys])
    center_mobile = xyz_mobile.mean(axis=0)
    center_target = xyz_target.mean(axis=0)
    left, _, right_t = np.linalg.svd(
        (xyz_mobile - center_mobile).T @ (xyz_target - center_target)
    )
    rotation = (
        right_t.T
        @ np.diag(
            [1.0, 1.0, np.sign(np.linalg.det(right_t.T @ left.T))]
        )
        @ left.T
    )
    translation = center_target - rotation @ center_mobile
    fitted = (rotation @ xyz_mobile.T).T + translation
    deltas = np.linalg.norm(fitted - xyz_target, axis=1)
    return (
        rotation,
        translation,
        float(np.sqrt(np.mean(deltas**2))),
        float(deltas.max()),
        deltas,
    )


def ligand_arrays(path: Path) -> tuple[str, list[dict[str, Any]], str, np.ndarray]:
    title, atoms, box_line = parse_gro(path)
    if len(atoms) != 46:
        raise ValueError(f"canonical ASCR3 ligand must contain 46 atoms, found {len(atoms)}")
    if any(atom["resname"] != "ASCR3" for atom in atoms):
        raise ValueError("canonical ligand residue name/order is not ASCR3")
    xyz_a = np.array([[atom["x"], atom["y"], atom["z"]] for atom in atoms]) * 10.0
    return title, atoms, box_line, xyz_a


def transformed_atoms(
    template: list[dict[str, Any]],
    xyz_a: np.ndarray,
) -> list[dict[str, Any]]:
    output = []
    for atom, xyz in zip(template, xyz_a, strict=True):
        output.append(
            dict(
                atom,
                x=float(xyz[0] / 10.0),
                y=float(xyz[1] / 10.0),
                z=float(xyz[2] / 10.0),
            )
        )
    return output


def element(atom_name: str) -> str:
    for character in atom_name:
        if character.isalpha():
            value = character.upper()
            if value in VDW_RADII_A:
                return value
            break
    raise ValueError(f"no operational VDW radius for atom name: {atom_name}")


def parse_base_heavy(
    gro_path: Path,
) -> tuple[
    int,
    list[dict[str, Any]],
    dict[int, list[dict[str, Any]]],
    np.ndarray,
    list[dict[str, Any]],
]:
    _, atoms, box_line = parse_gro(gro_path)
    raw_box = [float(value) for value in box_line.split()]
    if len(raw_box) == 3:
        box_values = [value * 10.0 for value in raw_box]
    elif len(raw_box) == 9 and all(abs(value) < 1e-12 for value in raw_box[3:]):
        box_values = [value * 10.0 for value in raw_box[:3]]
    else:
        raise ValueError(f"triclinic/non-orthorhombic box not supported: {gro_path}")
    protein = []
    popc: dict[int, list[dict[str, Any]]] = {}
    for index, atom in enumerate(atoms, 1):
        if atom["atomname"].startswith("H"):
            continue
        row = {
            "index": index,
            "resid": atom["resnum"],
            "resname": atom["resname"],
            "atomname": atom["atomname"],
            "xyz": np.array([atom["x"], atom["y"], atom["z"]]) * 10.0,
        }
        if atom["resname"] in PROTEIN_RESNAMES:
            protein.append(row)
        elif atom["resname"] == "POPC":
            popc.setdefault(atom["resnum"], []).append(row)
    if not protein or not popc:
        raise ValueError(f"base lacks protein or POPC heavy atoms: {gro_path}")
    return len(atoms), protein, popc, np.array(box_values), atoms


def nearest_pair(
    ligand_name: str,
    ligand_xyz: np.ndarray,
    partners: list[dict[str, Any]],
) -> tuple[dict[str, Any], float, float, float]:
    partner_xyz = np.array([atom["xyz"] for atom in partners])
    distances = np.linalg.norm(partner_xyz - ligand_xyz, axis=1)
    index = int(np.argmin(distances))
    partner = partners[index]
    distance = float(distances[index])
    radii_sum = VDW_RADII_A[element(ligand_name)] + VDW_RADII_A[
        element(partner["atomname"])
    ]
    return partner, distance, radii_sum, distance / radii_sum


def audit_arm(
    arm: str,
    gro_path: Path,
    ligand_atoms: list[dict[str, Any]],
    ligand_xyz_a: np.ndarray,
    output_dir: Path,
) -> dict[str, Any]:
    base_atom_count, protein, popc, box_a, base_atoms = parse_base_heavy(gro_path)
    if np.any(ligand_xyz_a < 0.0) or np.any(ligand_xyz_a > box_a):
        raise ValueError(
            f"{arm} ligand outside box: min={ligand_xyz_a.min(axis=0)}, "
            f"max={ligand_xyz_a.max(axis=0)}, box={box_a}"
        )
    heavy_indices = [
        index
        for index, atom in enumerate(ligand_atoms)
        if not atom["atomname"].startswith("H")
    ]
    clash_rows = []
    protein_min_ratio = float("inf")
    protein_min_distance = float("inf")
    for index in heavy_indices:
        ligand_atom = ligand_atoms[index]
        partner, distance, radii_sum, ratio = nearest_pair(
            ligand_atom["atomname"], ligand_xyz_a[index], protein
        )
        protein_min_ratio = min(protein_min_ratio, ratio)
        protein_min_distance = min(protein_min_distance, distance)
        classification = "SEVERE_OVERLAP" if ratio < OVERLAP_RATIO_CUTOFF else "RETAIN"
        clash_rows.append(
            (
                arm,
                "protein",
                index + 1,
                ligand_atom["atomname"],
                partner["resid"],
                partner["resname"],
                partner["atomname"],
                f"{distance:.6f}",
                f"{radii_sum:.6f}",
                f"{ratio:.6f}",
                classification,
                CRITERION_STATUS,
            )
        )
    if protein_min_ratio < OVERLAP_RATIO_CUTOFF:
        raise ValueError(
            f"{arm} unacceptable protein overlap ratio={protein_min_ratio:.6f} "
            f"distance_A={protein_min_distance:.6f}"
        )

    popc_rows = []
    proposed_rows = []
    remove_popc = []
    for resid, atoms in sorted(popc.items()):
        best: tuple[int, dict[str, Any], float, float, float] | None = None
        for index in heavy_indices:
            ligand_atom = ligand_atoms[index]
            partner, distance, radii_sum, ratio = nearest_pair(
                ligand_atom["atomname"], ligand_xyz_a[index], atoms
            )
            candidate = (index, partner, distance, radii_sum, ratio)
            if best is None or ratio < best[4]:
                best = candidate
        assert best is not None
        index, partner, distance, radii_sum, ratio = best
        action = "remove" if ratio < OVERLAP_RATIO_CUTOFF else "retain"
        if action == "remove":
            remove_popc.append(resid)
        popc_rows.append(
            (
                arm,
                "POPC",
                index + 1,
                ligand_atoms[index]["atomname"],
                resid,
                "POPC",
                partner["atomname"],
                f"{distance:.6f}",
                f"{radii_sum:.6f}",
                f"{ratio:.6f}",
                "SEVERE_OVERLAP" if action == "remove" else "RETAIN",
                CRITERION_STATUS,
            )
        )
        proposed_rows.append(
            (
                arm,
                resid,
                f"{distance:.6f}",
                f"{radii_sum:.6f}",
                f"{ratio:.6f}",
                action,
                "PENDING_REVIEW",
                CRITERION_STATUS,
                "",
            )
        )

    output_dir.mkdir(parents=True, exist_ok=False)
    write_tsv(
        output_dir / "clash_audit.tsv",
        [
            "arm",
            "component",
            "ligand_atom_index",
            "ligand_atom_name",
            "partner_resid",
            "partner_resname",
            "partner_atom_name",
            "min_heavy_distance_A",
            "vdw_radii_sum_A",
            "distance_to_vdw_sum_ratio",
            "classification",
            "criterion_status",
        ],
        clash_rows + popc_rows,
    )
    write_tsv(
        output_dir / "proposed_popc_removal.tsv",
        [
            "arm",
            "popc_resid",
            "min_heavy_distance_A",
            "vdw_radii_sum_A",
            "distance_to_vdw_sum_ratio",
            "proposed_action",
            "review_status",
            "criterion_status",
            "review_note",
        ],
        proposed_rows,
    )
    return {
        "base_atom_count": base_atom_count,
        "base_atoms": base_atoms,
        "box_A": box_a.tolist(),
        "protein_min_heavy_distance_A": protein_min_distance,
        "protein_min_vdw_ratio": protein_min_ratio,
        "remove_popc_resids": remove_popc,
    }


def expected_index_counts(
    base_atoms: list[dict[str, Any]],
    ligand_atoms: list[dict[str, Any]],
    remove_popc: list[int],
) -> dict[str, int]:
    retained = [
        atom
        for atom in base_atoms
        if not (atom["resname"] == "POPC" and atom["resnum"] in set(remove_popc))
    ]
    protein = sum(atom["resname"] in PROTEIN_RESNAMES for atom in retained)
    membrane = sum(atom["resname"] == "POPC" for atom in retained)
    solvent = sum(
        atom["resname"] in {"POT", "CLA", "TIP3", "SOL", "NA", "K"}
        for atom in retained
    )
    tip3 = sum(atom["resname"] in {"TIP3", "SOL"} for atom in retained)
    ligand = len(ligand_atoms)
    return {
        "PROA": protein,
        "ASCR3": ligand,
        "SOLU": protein + ligand,
        "MEMB": membrane,
        "SOLV": solvent,
        "SOLU_MEMB": protein + ligand + membrane,
        "SYSTEM": len(retained) + ligand,
        "TIP3": tip3,
    }


def write_matrix_rows(
    output_path: Path,
    records: list[tuple[str, np.ndarray, np.ndarray, float, float, int]],
) -> None:
    rows = []
    for name, rotation, translation, rmsd, max_delta, count in records:
        rows.extend(
            [
                (name, "atom_count", count),
                (name, "rmsd_A", f"{rmsd:.9f}"),
                (name, "max_delta_A", f"{max_delta:.9f}"),
                (name, "rotation_row_1", " ".join(f"{x:.12f}" for x in rotation[0])),
                (name, "rotation_row_2", " ".join(f"{x:.12f}" for x in rotation[1])),
                (name, "rotation_row_3", " ".join(f"{x:.12f}" for x in rotation[2])),
                (name, "translation_A", " ".join(f"{x:.12f}" for x in translation)),
            ]
        )
    write_tsv(output_path, ["transform", "metric", "value"], rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dock-receptor", type=Path, required=True)
    parser.add_argument("--matched-wt-receptor", type=Path, required=True)
    parser.add_argument("--ligand-gro", type=Path, required=True)
    parser.add_argument("--wt-base", type=Path, required=True)
    parser.add_argument("--r167y-base", type=Path, required=True)
    parser.add_argument(
        "--alignment-selection",
        choices=sorted(ALIGNMENT_SELECTIONS),
        required=True,
    )
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    if args.output_root.exists():
        raise FileExistsError(f"refusing to overwrite output root: {args.output_root}")
    required = [
        args.dock_receptor,
        args.matched_wt_receptor,
        args.ligand_gro,
        args.wt_base / "step5_input.pdb",
        args.wt_base / "step5_input.gro",
        args.wt_base / "topol.top",
        args.r167y_base / "step5_input.pdb",
        args.r167y_base / "step5_input.gro",
        args.r167y_base / "topol.top",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"required canonical inputs missing: {missing}")

    args.output_root.mkdir(parents=True)
    shared_dir = args.output_root / "shared"
    shared_dir.mkdir()
    try:
        dock = parse_pdb_atoms(args.dock_receptor)
        matched = parse_pdb_atoms(args.matched_wt_receptor)
        wt_pdb = parse_pdb_atoms(args.wt_base / "step5_input.pdb", segment="PROA")
        r167y_pdb = parse_pdb_atoms(
            args.r167y_base / "step5_input.pdb", segment="PROA"
        )
        if len(wt_pdb) == 0 or len(r167y_pdb) == 0:
            raise ValueError("PROA segment parsing failed for one receptor base")

        ligand_title, ligand_atoms, _, ligand_xyz_a = ligand_arrays(args.ligand_gro)
        sensitivity_rows = []
        transformed_by_selection: dict[str, np.ndarray] = {}
        selected_transform: tuple[np.ndarray, np.ndarray, float, float, int] | None = None
        mapping_rows = []
        for selection in sorted(ALIGNMENT_SELECTIONS):
            keys = alignment_keys(dock, matched, selection)
            rotation, translation, rmsd, max_delta, deltas = kabsch(
                dock, matched, keys
            )
            transformed = (rotation @ ligand_xyz_a.T).T + translation
            transformed_by_selection[selection] = transformed
            for key, delta in zip(keys, deltas, strict=True):
                if selection == args.alignment_selection:
                    mapping_rows.append(
                        (
                            key[0],
                            key[1],
                            dock[key]["resname"],
                            matched[key]["resname"],
                            f"{delta:.9f}",
                        )
                    )
            if selection == args.alignment_selection:
                selected_transform = (
                    rotation,
                    translation,
                    rmsd,
                    max_delta,
                    len(keys),
                )
            sensitivity_rows.append(
                (
                    selection,
                    len(keys),
                    f"{rmsd:.9f}",
                    f"{max_delta:.9f}",
                    "",
                    "",
                    CRITERION_STATUS,
                )
            )
        assert selected_transform is not None
        selected_matched_xyz = transformed_by_selection[args.alignment_selection]
        max_sensitivity = 0.0
        updated_sensitivity = []
        for row in sensitivity_rows:
            candidate = transformed_by_selection[row[0]]
            displacement = np.linalg.norm(candidate - selected_matched_xyz, axis=1)
            ligand_rmsd = float(np.sqrt(np.mean(displacement**2)))
            ligand_max = float(displacement.max())
            max_sensitivity = max(max_sensitivity, ligand_max)
            updated_sensitivity.append(
                row[:4] + (f"{ligand_rmsd:.9f}", f"{ligand_max:.9f}") + row[6:]
            )
        if max_sensitivity > ALIGNMENT_SENSITIVITY_LIMIT_A:
            raise ValueError(
                f"alignment decision required: ligand max selection sensitivity "
                f"{max_sensitivity:.6f} A exceeds operational limit "
                f"{ALIGNMENT_SENSITIVITY_LIMIT_A:.6f} A"
            )

        wt_bridge_keys = alignment_keys(matched, wt_pdb, "common-backbone")
        wt_rotation, wt_translation, wt_rmsd, wt_max, _ = kabsch(
            matched, wt_pdb, wt_bridge_keys
        )
        r167y_bridge_keys = alignment_keys(matched, r167y_pdb, "common-backbone")
        r167y_rotation, r167y_translation, r167y_rmsd, r167y_max, _ = kabsch(
            matched, r167y_pdb, r167y_bridge_keys
        )
        shared_base_xyz = (
            wt_rotation @ selected_matched_xyz.T
        ).T + wt_translation
        independent_r167y_xyz = (
            r167y_rotation @ selected_matched_xyz.T
        ).T + r167y_translation
        bridge_displacement = np.linalg.norm(
            shared_base_xyz - independent_r167y_xyz, axis=1
        )
        bridge_ligand_max = float(bridge_displacement.max())
        bridge_ligand_rmsd = float(np.sqrt(np.mean(bridge_displacement**2)))
        if bridge_ligand_max > ALIGNMENT_SENSITIVITY_LIMIT_A:
            raise ValueError(
                f"WT/R167Y base-frame decision required: ligand max displacement "
                f"{bridge_ligand_max:.6f} A exceeds operational limit "
                f"{ALIGNMENT_SENSITIVITY_LIMIT_A:.6f} A"
            )

        matched_gro = shared_dir / "ASCR3_matched_wt_frame.gro"
        shared_base_gro = shared_dir / "ASCR3_shared_base_frame.gro"
        write_gro(
            matched_gro,
            f"{ligand_title}; docking receptor -> matched WT",
            transformed_atoms(ligand_atoms, selected_matched_xyz),
            "0.00000 0.00000 0.00000\n",
        )
        wt_box_line = (args.wt_base / "step5_input.gro").read_text(
            encoding="utf-8"
        ).splitlines()[-1]
        write_gro(
            shared_base_gro,
            f"{ligand_title}; shared WT/R167Y base frame",
            transformed_atoms(ligand_atoms, shared_base_xyz),
            f"{wt_box_line}\n",
        )
        if [atom["atomname"] for atom in parse_gro(shared_base_gro)[1]] != [
            atom["atomname"] for atom in ligand_atoms
        ]:
            raise ValueError("transformed ligand atom order changed")

        write_tsv(
            shared_dir / "receptor_alignment.tsv",
            [
                "resid",
                "atomname",
                "dock_resname",
                "matched_wt_resname",
                "postfit_delta_A",
            ],
            mapping_rows,
        )
        write_tsv(
            shared_dir / "alignment_sensitivity.tsv",
            [
                "selection",
                "atom_count",
                "receptor_rmsd_A",
                "receptor_max_delta_A",
                "ligand_rmsd_vs_selected_A",
                "ligand_max_delta_vs_selected_A",
                "criterion_status",
            ],
            updated_sensitivity,
        )
        dock_rotation, dock_translation, dock_rmsd, dock_max, dock_count = (
            selected_transform
        )
        write_matrix_rows(
            shared_dir / "rigid_transforms.tsv",
            [
                (
                    "dock_to_matched_wt",
                    dock_rotation,
                    dock_translation,
                    dock_rmsd,
                    dock_max,
                    dock_count,
                ),
                (
                    "matched_wt_to_shared_wt_base",
                    wt_rotation,
                    wt_translation,
                    wt_rmsd,
                    wt_max,
                    len(wt_bridge_keys),
                ),
                (
                    "matched_wt_to_r167y_base_audit_only",
                    r167y_rotation,
                    r167y_translation,
                    r167y_rmsd,
                    r167y_max,
                    len(r167y_bridge_keys),
                ),
            ],
        )
        write_tsv(
            shared_dir / "base_frame_consistency.tsv",
            ["metric", "value", "criterion_status"],
            [
                ("shared_ligand_source", "WT base bridge", CRITERION_STATUS),
                ("r167y_independent_bridge_ligand_rmsd_A", f"{bridge_ligand_rmsd:.9f}", CRITERION_STATUS),
                ("r167y_independent_bridge_ligand_max_delta_A", f"{bridge_ligand_max:.9f}", CRITERION_STATUS),
                ("material_difference_limit_A", f"{ALIGNMENT_SENSITIVITY_LIMIT_A:.6f}", CRITERION_STATUS),
                ("shared_coordinate_policy", "byte-identical ligand GRO for WT and R167Y assembly", CRITERION_STATUS),
            ],
        )

        arm_inputs = {
            "wt": args.wt_base,
            "r167y": args.r167y_base,
        }
        observations: dict[str, dict[str, Any]] = {}
        for arm, base in arm_inputs.items():
            arm_dir = args.output_root / arm
            audit = audit_arm(
                arm,
                base / "step5_input.gro",
                ligand_atoms,
                shared_base_xyz,
                arm_dir,
            )
            topology_counts = Counter(
                dict(parse_topology_molecules(base / "topol.top"))
            )
            coordinate_counts = coordinate_molecule_counts(audit["base_atoms"])
            if topology_counts != coordinate_counts:
                raise ValueError(
                    f"{arm} base coordinate/topology molecule mismatch: "
                    f"{coordinate_counts} != {topology_counts}"
                )
            final_counts = Counter(topology_counts)
            final_counts["POPC"] -= len(audit["remove_popc_resids"])
            final_counts["ASCR3"] += 1
            popc_atoms_removed = sum(
                1
                for atom in audit["base_atoms"]
                if atom["resname"] == "POPC"
                and atom["resnum"] in set(audit["remove_popc_resids"])
            )
            final_atom_count = (
                audit["base_atom_count"] - popc_atoms_removed + len(ligand_atoms)
            )
            index_counts = expected_index_counts(
                audit["base_atoms"], ligand_atoms, audit["remove_popc_resids"]
            )
            if final_atom_count != index_counts["SYSTEM"]:
                raise ValueError(f"{arm} internal final atom-count calculation mismatch")
            observation = {
                "arm": arm,
                "criterion_status": CRITERION_STATUS,
                "base_gro": str(base / "step5_input.gro"),
                "base_gro_sha256": sha256(base / "step5_input.gro"),
                "base_topology": str(base / "topol.top"),
                "base_topology_sha256": sha256(base / "topol.top"),
                "base_atom_count": audit["base_atom_count"],
                "base_molecule_counts": dict(topology_counts),
                "ligand_gro": str(shared_base_gro),
                "ligand_gro_sha256": sha256(shared_base_gro),
                "ligand_atom_count": len(ligand_atoms),
                "ligand_atom_names": [atom["atomname"] for atom in ligand_atoms],
                "box_A": audit["box_A"],
                "protein_min_heavy_distance_A": audit[
                    "protein_min_heavy_distance_A"
                ],
                "protein_min_vdw_ratio": audit["protein_min_vdw_ratio"],
                "proposed_remove_popc_resids": audit["remove_popc_resids"],
                "proposed_final_molecule_counts": dict(final_counts),
                "proposed_final_atom_count": final_atom_count,
                "proposed_index_group_counts": index_counts,
                "review_status": "PENDING_POPC_REVIEW",
            }
            (arm_dir / "assembly_observations.json").write_text(
                json.dumps(observation, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            observations[arm] = observation

        if sha256(shared_base_gro) != observations["wt"]["ligand_gro_sha256"]:
            raise ValueError("WT transformed ligand checksum drift")
        if observations["wt"]["ligand_gro_sha256"] != observations["r167y"][
            "ligand_gro_sha256"
        ]:
            raise ValueError("WT and R167Y did not receive the same transformed ligand")

        manifest_paths = [
            ("dock_receptor", args.dock_receptor),
            ("matched_wt_receptor", args.matched_wt_receptor),
            ("canonical_ligand", args.ligand_gro),
            ("wt_base_gro", args.wt_base / "step5_input.gro"),
            ("wt_base_topology", args.wt_base / "topol.top"),
            ("r167y_base_gro", args.r167y_base / "step5_input.gro"),
            ("r167y_base_topology", args.r167y_base / "topol.top"),
            ("matched_frame_ligand", matched_gro),
            ("shared_base_frame_ligand", shared_base_gro),
        ]
        write_tsv(
            shared_dir / "coordinate_manifest.tsv",
            ["role", "path", "bytes", "sha256"],
            [
                (role, str(path), path.stat().st_size, sha256(path))
                for role, path in manifest_paths
            ],
        )
        write_tsv(
            args.output_root / "terminal_status.tsv",
            ["gate", "status", "detail"],
            [
                (
                    "docking_receptor_provenance",
                    "PASS",
                    f"{args.dock_receptor} sha256={sha256(args.dock_receptor)}",
                ),
                (
                    "alignment_mapping",
                    "PASS",
                    f"{args.alignment_selection}; atoms={dock_count}; "
                    f"rmsd_A={dock_rmsd:.6f}; max_A={dock_max:.6f}",
                ),
                (
                    "alignment_sensitivity",
                    "PASS",
                    f"max_ligand_delta_A={max_sensitivity:.6f}; "
                    f"criterion={CRITERION_STATUS}",
                ),
                (
                    "shared_transformed_ligand",
                    "PASS",
                    f"atoms=46; sha256={sha256(shared_base_gro)}",
                ),
                (
                    "wt_clash_inventory",
                    "PASS_PENDING_POPC_REVIEW",
                    f"proposed_remove={observations['wt']['proposed_remove_popc_resids']}",
                ),
                (
                    "r167y_clash_inventory",
                    "PASS_PENDING_POPC_REVIEW",
                    f"proposed_remove={observations['r167y']['proposed_remove_popc_resids']}",
                ),
                (
                    "preparation",
                    "PASS_PREPARATION_PENDING_POPC_REVIEW",
                    CRITERION_STATUS,
                ),
            ],
        )
    except Exception as error:
        write_tsv(
            args.output_root / "terminal_status.tsv",
            ["gate", "status", "detail"],
            [("preparation", "BLOCKED", str(error))],
        )
        (args.output_root / "failure_command.txt").write_text(
            shlex.join([sys.executable, *sys.argv]) + "\n", encoding="utf-8"
        )
        (args.output_root / "failure_stdout_stderr.txt").write_text(
            f"{type(error).__name__}: {error}\n", encoding="utf-8"
        )
        available_rows = []
        for path in required:
            if path.is_file():
                available_rows.append(
                    (str(path), path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest())
                )
        write_tsv(
            args.output_root / "failure_input_checksums.tsv",
            ["path", "bytes", "sha256"],
            available_rows,
        )
        raise


if __name__ == "__main__":
    main()
