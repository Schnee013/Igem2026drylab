"""Reproducible membrane/pocket geometry gates in a traceable common frame."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from docking_manifest import parse_vina_pose_models
from frame_alignment import (
    ONE_LETTER,
    AtomRecord,
    RigidTransform,
    canonical_json_bytes,
    kabsch_transform,
    parse_atom_lines,
    parse_atoms,
    rmsd,
    select_tm_ca,
    sha256_file,
    write_canonical_json,
)


MEMBRANE_TRANSFORM_SCHEMA = "docking-wt-to-membrane-transform-v1"
MEMBRANE_RESNAME_ALIASES = {
    "HSD": "HIS",
    "HSE": "HIS",
    "HSP": "HIS",
}


@dataclass(frozen=True)
class MembraneFrame:
    transform: RigidTransform
    membrane_normal: np.ndarray
    tm_axis_origin: np.ndarray
    lower_phosphate_height: float
    upper_phosphate_height: float


def _manifest_identity(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _protein_ca_by_number_identity(
    atoms: Iterable[AtomRecord],
) -> dict[tuple[int, str], AtomRecord]:
    mapping: dict[tuple[int, str], AtomRecord] = {}
    for atom in atoms:
        canonical_resname = MEMBRANE_RESNAME_ALIASES.get(
            atom.resname, atom.resname
        )
        if (
            atom.record != "ATOM"
            or atom.atom_name != "CA"
            or canonical_resname not in ONE_LETTER
        ):
            continue
        key = (atom.resseq, canonical_resname)
        if key in mapping:
            raise ValueError(f"膜体系中 residue number + identity 不唯一: {key}")
        mapping[key] = atom
    return mapping


def build_membrane_transform(
    *,
    receptor: str,
    wt_docking_pdb: Path,
    membrane_pdb: Path,
    helices: Sequence[Sequence[int]],
    docking_chain: str = "A",
) -> dict[str, Any]:
    """Build WT docking-frame -> membrane-frame transform without chain matching."""
    docking_atoms = parse_atoms(wt_docking_pdb)
    membrane_atoms = parse_atoms(membrane_pdb)
    docking_tm = select_tm_ca(docking_atoms, helices, chain=docking_chain)
    if len(docking_tm) != 147:
        raise ValueError(f"{receptor}: expected 147 docking TM CA")
    membrane_ca = _protein_ca_by_number_identity(membrane_atoms)
    docking_alignment = [
        atom
        for atom in docking_atoms
        if atom.record == "ATOM" and atom.atom_name == "CA"
    ]
    membrane_alignment: list[AtomRecord] = []
    residue_pairs: list[dict[str, Any]] = []
    for atom in docking_alignment:
        canonical_docking_resname = MEMBRANE_RESNAME_ALIASES.get(
            atom.resname, atom.resname
        )
        key = (atom.resseq, canonical_docking_resname)
        membrane_atom = membrane_ca.get(key)
        if membrane_atom is None:
            raise ValueError(
                f"{receptor}: membrane CA 缺失或身份不符: "
                f"{atom.resseq}/{atom.resname}"
            )
        membrane_alignment.append(membrane_atom)
        residue_pairs.append(
            {
                "residue_number": atom.resseq,
                "resname": canonical_docking_resname,
                "docking_chain": atom.chain,
                "membrane_chain": membrane_atom.chain.strip(),
            }
        )

    source = np.vstack([atom.coord for atom in docking_alignment])
    target = np.vstack([atom.coord for atom in membrane_alignment])
    transform = kabsch_transform(source, target)
    transformed = transform.apply(source)
    membrane_tm = [
        membrane_ca[
            (
                atom.resseq,
                MEMBRANE_RESNAME_ALIASES.get(atom.resname, atom.resname),
            )
        ]
        for atom in docking_tm
    ]
    tm_target = np.vstack([atom.coord for atom in membrane_tm])
    determinant = float(np.linalg.det(transform.rotation))
    orthogonality_error = float(
        np.max(np.abs(transform.rotation.T @ transform.rotation - np.eye(3)))
    )
    if not np.isclose(determinant, 1.0, atol=1e-8):
        raise ValueError(f"{receptor}: WT->membrane rotation improper")
    if orthogonality_error > 1e-8:
        raise ValueError(f"{receptor}: WT->membrane rotation non-orthogonal")

    popc_p = [
        atom.coord
        for atom in membrane_atoms
        if atom.resname == "POPC" and atom.atom_name == "P"
    ]
    if not popc_p:
        raise ValueError(f"{receptor}: membrane PDB 缺少 POPC P 原子")
    phosphate_heights = np.array([coord[2] for coord in popc_p], dtype=float)
    median = float(np.median(phosphate_heights))
    lower = phosphate_heights[phosphate_heights < median]
    upper = phosphate_heights[phosphate_heights > median]
    if not len(lower) or not len(upper):
        raise ValueError(f"{receptor}: 无法分离双层膜磷面")

    membrane_normal = np.array([0.0, 0.0, 1.0])
    tm_axis_origin = tm_target.mean(axis=0)
    payload: dict[str, Any] = {
        "schema": MEMBRANE_TRANSFORM_SCHEMA,
        "status": "traceable_membrane_frame",
        "receptor": receptor,
        "source_frame": f"{receptor}_WT_docking_frame",
        "target_frame": f"{receptor}_WT_membrane_frame",
        "pairing_rule": (
            "configured seven-TM CA; unique residue number + residue identity; "
            "chain intentionally ignored because membrane PDB chain is blank"
        ),
        "alignment_selection": {
            "docking_chain": docking_chain,
            "ca_count": len(docking_alignment),
            "residue_pairs": residue_pairs,
        },
        "tm_axis_selection": {
            "ca_count": len(docking_tm),
            "helices": [list(map(int, interval)) for interval in helices],
        },
        "transform": {
            "convention": "row_vector: membrane = docking @ rotation.T + translation",
            "rotation": transform.rotation.tolist(),
            "translation": transform.translation.tolist(),
            "determinant": determinant,
            "orthogonality_max_abs_error": orthogonality_error,
        },
        "metrics_angstrom": {
            "post_alignment_rmsd": rmsd(transformed, target),
        },
        "membrane_geometry": {
            "normal": membrane_normal.tolist(),
            "extracellular_direction": "+normal",
            "tm_axis_origin": tm_axis_origin.tolist(),
            "lower_phosphate_height": float(np.median(lower)),
            "upper_phosphate_height": float(np.median(upper)),
            "absolute_height_definition": "dot(membrane_coordinate, membrane_normal)",
            "tm_relative_height_definition": (
                "dot(membrane_coordinate - tm_axis_origin, membrane_normal)"
            ),
            "radial_definition": (
                "distance to line through tm_axis_origin parallel to membrane_normal"
            ),
        },
        "files": {
            "wt_docking_pdb": {
                "path": str(Path(wt_docking_pdb).resolve()),
                "sha256": sha256_file(wt_docking_pdb),
            },
            "membrane_pdb": {
                "path": str(Path(membrane_pdb).resolve()),
                "sha256": sha256_file(membrane_pdb),
            },
        },
    }
    payload["manifest_identity"] = _manifest_identity(payload)
    return payload


def write_membrane_transform_manifest(
    path: Path,
    **kwargs: Any,
) -> dict[str, Any]:
    payload = build_membrane_transform(**kwargs)
    write_canonical_json(path, payload)
    return payload


def verify_membrane_transform_manifest(
    path: Path,
    *,
    expected_receptor: str | None = None,
) -> dict[str, Any]:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if manifest.get("schema") != MEMBRANE_TRANSFORM_SCHEMA:
        raise ValueError("未知 membrane transform schema")
    if manifest.get("status") != "traceable_membrane_frame":
        raise ValueError("membrane transform 状态不可用")
    if expected_receptor and manifest.get("receptor") != expected_receptor:
        raise ValueError("membrane transform receptor mismatch")
    payload = dict(manifest)
    expected_identity = payload.pop("manifest_identity", None)
    if not expected_identity or _manifest_identity(payload) != expected_identity:
        raise ValueError("membrane transform content identity mismatch")
    for label, record in manifest.get("files", {}).items():
        file_path = Path(record.get("path", ""))
        if not file_path.is_file() or sha256_file(file_path) != record.get("sha256"):
            raise ValueError(f"membrane transform file hash mismatch: {label}")
    if manifest.get("alignment_selection", {}).get("ca_count", 0) < 147:
        raise ValueError("membrane transform CA 对齐集合不完整")
    if manifest.get("tm_axis_selection", {}).get("ca_count") != 147:
        raise ValueError("membrane TM axis 必须使用 147 个 TM CA")
    return manifest


def membrane_frame_from_manifest(manifest: dict[str, Any]) -> MembraneFrame:
    transform = manifest["transform"]
    geometry = manifest["membrane_geometry"]
    return MembraneFrame(
        transform=RigidTransform(
            rotation=np.asarray(transform["rotation"], dtype=float),
            translation=np.asarray(transform["translation"], dtype=float),
        ),
        membrane_normal=np.asarray(geometry["normal"], dtype=float),
        tm_axis_origin=np.asarray(geometry["tm_axis_origin"], dtype=float),
        lower_phosphate_height=float(geometry["lower_phosphate_height"]),
        upper_phosphate_height=float(geometry["upper_phosphate_height"]),
    )


def split_pdbqt_models(path: Path) -> list[list[AtomRecord]]:
    """Compatibility wrapper backed by the strict in-memory pose parser."""
    return [
        parse_atom_lines(
            model.body.splitlines(),
            source=f"{path}#MODEL{model.model_number}",
            first_model_only=False,
        )
        for model in parse_vina_pose_models(path)
    ]


def ligand_heavy_coordinates(atoms: Iterable[AtomRecord]) -> np.ndarray:
    coordinates = []
    for atom in atoms:
        element = atom.element or atom.atom_name[:1].upper()
        if element != "H":
            coordinates.append(atom.coord)
    if not coordinates:
        raise ValueError("pose 中没有 ligand 重原子")
    return np.vstack(coordinates)


def radial_and_heights(
    point_membrane: np.ndarray,
    frame: MembraneFrame,
) -> tuple[float, float, float]:
    point = np.asarray(point_membrane, dtype=float)
    normal = frame.membrane_normal / np.linalg.norm(frame.membrane_normal)
    relative = point - frame.tm_axis_origin
    tm_relative_height = float(np.dot(relative, normal))
    radial_vector = relative - tm_relative_height * normal
    absolute_membrane_height = float(np.dot(point, normal))
    return (
        float(np.linalg.norm(radial_vector)),
        absolute_membrane_height,
        tm_relative_height,
    )


def centroid_in_axis_aligned_box(
    centroid: np.ndarray,
    center: Iterable[float],
    size: Iterable[float],
    *,
    tolerance: float = 1e-6,
) -> bool:
    centroid = np.asarray(centroid, dtype=float)
    center = np.asarray(list(center), dtype=float)
    half_size = np.asarray(list(size), dtype=float) / 2.0
    return bool(np.all(np.abs(centroid - center) <= half_size + tolerance))


def contact_metrics(
    ligand_coordinates: np.ndarray,
    receptor_coordinates: np.ndarray,
    *,
    contact_cutoff_angstrom: float,
) -> dict[str, Any]:
    pairwise = np.linalg.norm(
        ligand_coordinates[:, np.newaxis, :]
        - receptor_coordinates[np.newaxis, :, :],
        axis=2,
    )
    nearest = pairwise.min(axis=1)
    return {
        "minimum_distance_angstrom": float(nearest.min()),
        "ligand_heavy_atoms_with_distance_contact": int(
            np.count_nonzero(nearest <= contact_cutoff_angstrom)
        ),
        "ligand_heavy_atom_count": int(len(ligand_coordinates)),
        "contact_cutoff_angstrom": float(contact_cutoff_angstrom),
        "definition": "explicit nearest-neighbor audit; not a ProLIF substitute",
    }


def protein_vs_membrane_nearest_count(
    ligand_coordinates: np.ndarray,
    receptor_coordinates: np.ndarray,
    membrane_coordinates: np.ndarray,
) -> dict[str, int]:
    receptor_dist = np.linalg.norm(
        ligand_coordinates[:, None, :] - receptor_coordinates[None, :, :],
        axis=2,
    ).min(axis=1)
    membrane_dist = np.linalg.norm(
        ligand_coordinates[:, None, :] - membrane_coordinates[None, :, :],
        axis=2,
    ).min(axis=1)
    protein_closer = int(np.count_nonzero(receptor_dist < membrane_dist))
    return {
        "protein_closer_atom_count": protein_closer,
        "membrane_closer_or_tied_atom_count": int(
            len(ligand_coordinates) - protein_closer
        ),
        "ligand_heavy_atom_count": int(len(ligand_coordinates)),
    }


def _require_frozen_thresholds(thresholds: dict[str, Any]) -> None:
    required = {
        "calibration_status",
        "requested_max_modes",
        "radial_max_angstrom",
        "membrane_height_min_angstrom",
        "membrane_height_max_angstrom",
        "min_passing_modes",
        "contact_cutoff_angstrom",
        "min_protein_closer_atoms",
        "require_ifp_contact",
    }
    missing = sorted(required - set(thresholds))
    if missing:
        raise ValueError(f"geometry thresholds 缺少字段: {missing}")
    if thresholds["calibration_status"] != "FROZEN_BEFORE_MUTANT_RESULTS":
        raise ValueError("geometry calibration 未冻结，拒绝评估 mutant pose")
    for key in required:
        value = thresholds[key]
        if isinstance(value, str) and value.startswith("PENDING"):
            raise ValueError(f"geometry threshold 仍为 pending: {key}")


def _heavy_receptor_coordinates(atoms: Iterable[AtomRecord]) -> np.ndarray:
    coords = [
        atom.coord
        for atom in atoms
        if atom.record == "ATOM"
        and (atom.element or atom.atom_name[:1].upper()) != "H"
    ]
    if not coords:
        raise ValueError("receptor 不含重原子")
    return np.vstack(coords)


def _membrane_lipid_coordinates(membrane_pdb: Path) -> np.ndarray:
    coords = [
        atom.coord
        for atom in parse_atoms(membrane_pdb)
        if atom.resname == "POPC"
        and (atom.element or atom.atom_name[:1].upper()) != "H"
    ]
    if not coords:
        raise ValueError("膜参考不含 POPC 重原子")
    return np.vstack(coords)


def evaluate_pose_set(
    *,
    pose_pdbqt: Path,
    receptor_pdb: Path,
    membrane_transform_manifest: Path,
    box: dict[str, Any],
    thresholds: dict[str, Any],
    ifp_contact_by_model: dict[int, bool] | None,
) -> dict[str, Any]:
    """Evaluate MODEL 1 and the complete distribution in the membrane frame."""
    _require_frozen_thresholds(thresholds)
    membrane_manifest = verify_membrane_transform_manifest(
        membrane_transform_manifest
    )
    frame = membrane_frame_from_manifest(membrane_manifest)
    models = parse_vina_pose_models(pose_pdbqt)
    requested_max_modes = int(thresholds["requested_max_modes"])
    if not 1 <= len(models) <= requested_max_modes:
        raise ValueError(
            "pose 技术完整性失败: "
            f"requested_max={requested_max_modes}, actual={len(models)}"
        )
    if thresholds["require_ifp_contact"]:
        if ifp_contact_by_model is None:
            raise ValueError("geometry gate 要求 ProLIF contact，但未提供 IFP 逐 MODEL 证据")
        if set(ifp_contact_by_model) != set(range(1, len(models) + 1)):
            raise ValueError("IFP contact MODEL 集合与 pose 不一致")

    receptor_docking = _heavy_receptor_coordinates(parse_atoms(receptor_pdb))
    receptor_membrane = frame.transform.apply(receptor_docking)
    membrane_pdb = Path(membrane_manifest["files"]["membrane_pdb"]["path"])
    lipid_membrane = _membrane_lipid_coordinates(membrane_pdb)

    pose_reports: list[dict[str, Any]] = []
    for model in models:
        ligand_atoms = parse_atom_lines(
            model.body.splitlines(),
            source=f"{pose_pdbqt}#MODEL{model.model_number}",
            first_model_only=False,
        )
        ligand_docking = ligand_heavy_coordinates(ligand_atoms)
        centroid_docking = ligand_docking.mean(axis=0)
        ligand_membrane = frame.transform.apply(ligand_docking)
        centroid_membrane = ligand_membrane.mean(axis=0)
        radial, membrane_height, tm_relative_height = radial_and_heights(
            centroid_membrane, frame
        )
        contacts = contact_metrics(
            ligand_membrane,
            receptor_membrane,
            contact_cutoff_angstrom=float(
                thresholds["contact_cutoff_angstrom"]
            ),
        )
        nearest = protein_vs_membrane_nearest_count(
            ligand_membrane, receptor_membrane, lipid_membrane
        )
        checks = {
            "inside_shared_box": centroid_in_axis_aligned_box(
                centroid_docking, box["center"], box["size"]
            ),
            "central_radial": radial
            < float(thresholds["radial_max_angstrom"]),
            "membrane_absolute_height": (
                float(thresholds["membrane_height_min_angstrom"])
                <= membrane_height
                <= float(thresholds["membrane_height_max_angstrom"])
            ),
            "protein_over_membrane": nearest["protein_closer_atom_count"]
            >= int(thresholds["min_protein_closer_atoms"]),
        }
        if thresholds["require_ifp_contact"]:
            checks["prolif_contact"] = bool(
                ifp_contact_by_model[model.model_number]
            )
        checks["central_pocket_not_membrane_interface"] = all(
            checks[key]
            for key in (
                "central_radial",
                "membrane_absolute_height",
                "protein_over_membrane",
            )
        )
        pose_reports.append(
            {
                "model": model.model_number,
                "pose_body_sha256": model.body_sha256,
                "affinity": model.affinity,
                "centroid_docking_frame": centroid_docking.tolist(),
                "centroid_membrane_frame": centroid_membrane.tolist(),
                "radial_to_tm_axis_angstrom": radial,
                "membrane_absolute_height_angstrom": membrane_height,
                "tm_relative_height_angstrom": tm_relative_height,
                "contact": contacts,
                "audits": {
                    "has_distance_contact_within_audit_cutoff": contacts[
                        "ligand_heavy_atoms_with_distance_contact"
                    ]
                    > 0,
                },
                "protein_vs_membrane": nearest,
                "checks": checks,
                "pass": all(checks.values()),
            }
        )

    passed_count = sum(bool(report["pass"]) for report in pose_reports)
    model1_pass = bool(pose_reports[0]["pass"])
    distribution_pass = passed_count >= int(thresholds["min_passing_modes"])
    return {
        "schema": "docking-geometry-report-v2",
        "status": "evaluated",
        "pose_file": {
            "path": str(Path(pose_pdbqt).resolve()),
            "sha256": sha256_file(pose_pdbqt),
        },
        "receptor_file": {
            "path": str(Path(receptor_pdb).resolve()),
            "sha256": sha256_file(receptor_pdb),
        },
        "membrane_transform": {
            "path": str(Path(membrane_transform_manifest).resolve()),
            "sha256": sha256_file(membrane_transform_manifest),
            "manifest_identity": membrane_manifest["manifest_identity"],
        },
        "thresholds": thresholds,
        "requested_max_modes": requested_max_modes,
        "actual_modes": len(models),
        "model1_pass": model1_pass,
        "passing_mode_count": passed_count,
        "distribution_pass": distribution_pass,
        "pass": model1_pass and distribution_pass,
        "poses": pose_reports,
    }
