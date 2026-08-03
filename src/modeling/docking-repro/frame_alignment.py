"""Rigidly align AF3 mutant receptors into their WT docking frame.

The alignment contract is deliberately narrow: one chain, the seven configured
TM helices, and one CA atom per configured residue.  Any missing or duplicated
alignment atom, unexpected residue identity, or improper rotation fails closed.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


ONE_LETTER = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}

FRAME_MANIFEST_SCHEMA = "docking-frame-alignment-v2"
MUTATION_RE = re.compile(r"^([A-Z])(\d+)([A-Z])$")


@dataclass(frozen=True)
class AtomRecord:
    record: str
    atom_name: str
    resname: str
    chain: str
    resseq: int
    icode: str
    coord: np.ndarray
    element: str
    line_index: int

    @property
    def residue_key(self) -> tuple[str, int, str]:
        return (self.chain, self.resseq, self.icode)

    @property
    def atom_key(self) -> tuple[str, int, str, str]:
        return (*self.residue_key, self.atom_name)


@dataclass(frozen=True)
class RigidTransform:
    rotation: np.ndarray
    translation: np.ndarray

    def apply(self, coordinates: np.ndarray) -> np.ndarray:
        coordinates = np.asarray(coordinates, dtype=float)
        return coordinates @ self.rotation.T + self.translation

    def inverse(self) -> "RigidTransform":
        inverse_rotation = self.rotation.T
        inverse_translation = -self.translation @ self.rotation
        return RigidTransform(inverse_rotation, inverse_translation)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def write_canonical_json(path: Path, payload: object) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(canonical_json_bytes(payload))


def parse_atom_lines(
    lines: Iterable[str],
    *,
    source: str = "<memory>",
    first_model_only: bool = True,
) -> list[AtomRecord]:
    """Parse PDB/PDBQT atom records without creating temporary files."""
    atoms: list[AtomRecord] = []
    seen_model = False
    for index, line in enumerate(lines):
        if line.startswith("MODEL"):
            if seen_model and first_model_only:
                break
            seen_model = True
            continue
        if line.startswith("ENDMDL") and first_model_only:
            break
        if not line.startswith(("ATOM  ", "HETATM")) or len(line) < 54:
            continue
        try:
            coord = np.array(
                [float(line[30:38]), float(line[38:46]), float(line[46:54])],
                dtype=float,
            )
            resseq = int(line[22:26])
        except ValueError as exc:
            raise ValueError(f"无法解析 PDB 坐标行 {source}:{index + 1}") from exc
        atoms.append(
            AtomRecord(
                record=line[:6].strip(),
                atom_name=line[12:16].strip(),
                resname=line[17:21].strip().upper(),
                chain=line[21:22] or " ",
                resseq=resseq,
                icode=line[26:27] or " ",
                coord=coord,
                element=(line[76:78].strip().upper() if len(line) >= 78 else ""),
                line_index=index,
            )
        )
    if not atoms:
        raise ValueError(f"未在输入中找到可解析原子: {source}")
    return atoms


def parse_atoms(path: Path, *, first_model_only: bool = True) -> list[AtomRecord]:
    return parse_atom_lines(
        Path(path).read_text(errors="replace").splitlines(),
        source=str(path),
        first_model_only=first_model_only,
    )


def parse_mutation_label(label: str) -> tuple[str, int, str]:
    match = MUTATION_RE.fullmatch(label.upper())
    if not match:
        raise ValueError(f"突变标签格式错误: {label}")
    wt, number, mutant = match.groups()
    return wt, int(number), mutant


def ordered_tm_residues(helices: Sequence[Sequence[int]]) -> list[int]:
    residues: list[int] = []
    for interval in helices:
        if len(interval) != 2:
            raise ValueError(f"TM 区间必须是 [start, end]: {interval}")
        start, end = int(interval[0]), int(interval[1])
        if end < start:
            raise ValueError(f"TM 区间反向: {interval}")
        residues.extend(range(start, end + 1))
    if len(residues) != len(set(residues)):
        raise ValueError("TM 区间互相重叠")
    return residues


def ca_map(atoms: Iterable[AtomRecord]) -> dict[tuple[str, int, str], AtomRecord]:
    result: dict[tuple[str, int, str], AtomRecord] = {}
    for atom in atoms:
        if atom.record != "ATOM" or atom.atom_name != "CA":
            continue
        if atom.residue_key in result:
            raise ValueError(f"重复 CA 原子: {atom.residue_key}")
        result[atom.residue_key] = atom
    return result


def select_tm_ca(
    atoms: Iterable[AtomRecord],
    helices: Sequence[Sequence[int]],
    *,
    chain: str = "A",
) -> list[AtomRecord]:
    mapping = ca_map(atoms)
    selected: list[AtomRecord] = []
    for resseq in ordered_tm_residues(helices):
        key = (chain, resseq, " ")
        atom = mapping.get(key)
        if atom is None:
            matches = [value for key_, value in mapping.items() if key_[:2] == (chain, resseq)]
            if len(matches) == 1:
                atom = matches[0]
            else:
                raise ValueError(f"TM CA 缺失或 insertion code 歧义: {chain}:{resseq}")
        selected.append(atom)
    return selected


def kabsch_transform(source: np.ndarray, target: np.ndarray) -> RigidTransform:
    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    if source.shape != target.shape or source.ndim != 2 or source.shape[1] != 3:
        raise ValueError(f"Kabsch 坐标维度不一致: {source.shape} vs {target.shape}")
    if source.shape[0] < 3:
        raise ValueError("Kabsch 至少需要 3 个点")

    source_center = source.mean(axis=0)
    target_center = target.mean(axis=0)
    covariance = (source - source_center).T @ (target - target_center)
    u, _, vt = np.linalg.svd(covariance)
    rotation = vt.T @ u.T
    if np.linalg.det(rotation) < 0:
        vt[-1, :] *= -1
        rotation = vt.T @ u.T
    translation = target_center - source_center @ rotation.T
    return RigidTransform(rotation=rotation, translation=translation)


def rmsd(source: np.ndarray, target: np.ndarray) -> float:
    delta = np.asarray(source, dtype=float) - np.asarray(target, dtype=float)
    return float(np.sqrt(np.mean(np.sum(delta * delta, axis=1))))


def validate_mutation_identity(
    wt_atoms: Iterable[AtomRecord],
    mutant_atoms: Iterable[AtomRecord],
    mutation: str,
    *,
    chain: str = "A",
) -> dict:
    wt_letter, residue_number, mutant_letter = parse_mutation_label(mutation)
    wt_ca = ca_map(wt_atoms)
    mut_ca = ca_map(mutant_atoms)
    wt_keys = set(wt_ca)
    mutant_keys = set(mut_ca)
    if wt_keys != mutant_keys:
        missing = sorted(wt_keys - mutant_keys)
        extra = sorted(mutant_keys - wt_keys)
        raise ValueError(
            "WT 与 mutant 的 full-receptor CA 集不一致: "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    common = sorted(wt_keys)

    target_keys = [key for key in common if key[0] == chain and key[1] == residue_number]
    if len(target_keys) != 1:
        raise ValueError(f"目标残基 {chain}:{residue_number} 不唯一或缺失")
    target = target_keys[0]
    actual_wt = ONE_LETTER.get(wt_ca[target].resname, "X")
    actual_mutant = ONE_LETTER.get(mut_ca[target].resname, "X")
    if actual_wt != wt_letter or actual_mutant != mutant_letter:
        raise ValueError(
            f"{mutation} 身份不一致: WT={actual_wt}, mutant={actual_mutant}"
        )

    unexpected: list[dict] = []
    for key in common:
        if key == target:
            continue
        wt_identity = ONE_LETTER.get(wt_ca[key].resname, "X")
        mutant_identity = ONE_LETTER.get(mut_ca[key].resname, "X")
        if wt_identity != mutant_identity:
            unexpected.append(
                {
                    "chain": key[0],
                    "residue_number": key[1],
                    "insertion_code": key[2].strip(),
                    "wt": wt_identity,
                    "mutant": mutant_identity,
                }
            )
    if unexpected:
        raise ValueError(f"{mutation} 存在非预期身份差异: {unexpected[:5]}")
    return {
        "mutation": mutation,
        "chain": chain,
        "residue_number": residue_number,
        "wt_identity": actual_wt,
        "mutant_identity": actual_mutant,
        "common_ca_count": len(common),
        "wt_ca_count": len(wt_ca),
        "mutant_ca_count": len(mut_ca),
        "full_ca_key_sets_equal": True,
        "unexpected_identity_differences": [],
    }


def apply_transform_to_pdb(
    source_path: Path,
    output_path: Path,
    transform: RigidTransform,
) -> None:
    source_path = Path(source_path)
    lines = source_path.read_text(errors="replace").splitlines(keepends=True)
    atom_lookup = {atom.line_index: atom for atom in parse_atoms(source_path, first_model_only=False)}
    output_lines: list[str] = []
    for index, line in enumerate(lines):
        atom = atom_lookup.get(index)
        if atom is None:
            output_lines.append(line)
            continue
        transformed = transform.apply(atom.coord[np.newaxis, :])[0]
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        if len(body) < 54:
            raise ValueError(f"PDB 原子行过短: {source_path}:{index + 1}")
        body = (
            f"{body[:30]}{transformed[0]:8.3f}{transformed[1]:8.3f}"
            f"{transformed[2]:8.3f}{body[54:]}"
        )
        output_lines.append(body + newline)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("".join(output_lines), encoding="utf-8")


def align_mutant_to_wt(
    *,
    receptor: str,
    mutation: str,
    wt_full_pdb: Path,
    wt_tm_pdb: Path,
    mutant_full_pdb: Path,
    mutant_tm_pdb: Path,
    aligned_full_pdb: Path,
    aligned_tm_pdb: Path,
    manifest_path: Path,
    helices: Sequence[Sequence[int]],
    chain: str = "A",
    provenance_status: str = "af3_request_and_coordinate",
) -> dict:
    wt_full_atoms = parse_atoms(wt_full_pdb)
    wt_tm_atoms = parse_atoms(wt_tm_pdb)
    mutant_full_atoms = parse_atoms(mutant_full_pdb)
    mutant_tm_atoms = parse_atoms(mutant_tm_pdb)
    identity = validate_mutation_identity(
        wt_full_atoms, mutant_full_atoms, mutation, chain=chain
    )

    wt_selected = select_tm_ca(wt_tm_atoms, helices, chain=chain)
    mutant_selected = select_tm_ca(mutant_tm_atoms, helices, chain=chain)
    wt_keys = [atom.residue_key for atom in wt_selected]
    mutant_keys = [atom.residue_key for atom in mutant_selected]
    if wt_keys != mutant_keys:
        raise ValueError(f"{receptor}/{mutation}: TM CA residue pairing mismatch")

    source = np.vstack([atom.coord for atom in mutant_selected])
    target = np.vstack([atom.coord for atom in wt_selected])
    transform = kabsch_transform(source, target)
    aligned = transform.apply(source)
    determinant = float(np.linalg.det(transform.rotation))
    orthogonality_error = float(
        np.max(np.abs(transform.rotation.T @ transform.rotation - np.eye(3)))
    )
    if not np.isclose(determinant, 1.0, atol=1e-8):
        raise ValueError(f"{receptor}/{mutation}: improper rotation det={determinant}")
    if orthogonality_error > 1e-8:
        raise ValueError(
            f"{receptor}/{mutation}: rotation orthogonality error={orthogonality_error}"
        )

    apply_transform_to_pdb(mutant_full_pdb, aligned_full_pdb, transform)
    apply_transform_to_pdb(mutant_tm_pdb, aligned_tm_pdb, transform)

    rounded_aligned_tm = np.vstack(
        [atom.coord for atom in select_tm_ca(parse_atoms(aligned_tm_pdb), helices, chain=chain)]
    )
    rounded_rmsd = rmsd(rounded_aligned_tm, target)
    manifest = {
        "schema": FRAME_MANIFEST_SCHEMA,
        "status": "frame_aligned",
        "receptor": receptor,
        "mutation": mutation,
        "target_frame": f"{receptor}_WT_docking_frame",
        "provenance_status": provenance_status,
        "alignment_selection": {
            "chain": chain,
            "helices": [list(map(int, interval)) for interval in helices],
            "ca_count": len(wt_selected),
            "residue_pairs": [
                {
                    "chain": key[0],
                    "residue_number": key[1],
                    "insertion_code": key[2].strip(),
                }
                for key in wt_keys
            ],
        },
        "identity_validation": identity,
        "transform": {
            "convention": "row_vector: aligned = source @ rotation.T + translation",
            "rotation": transform.rotation.tolist(),
            "translation": transform.translation.tolist(),
            "determinant": determinant,
            "orthogonality_max_abs_error": orthogonality_error,
        },
        "metrics_angstrom": {
            "pre_alignment_center_distance": float(
                np.linalg.norm(source.mean(axis=0) - target.mean(axis=0))
            ),
            "pre_alignment_rmsd_without_transform": rmsd(source, target),
            "post_alignment_rmsd": rmsd(aligned, target),
            "post_write_rounding_rmsd": rounded_rmsd,
        },
        "files": {
            "wt_full_pdb": {
                "path": str(Path(wt_full_pdb).resolve()),
                "sha256": sha256_file(wt_full_pdb),
            },
            "wt_tm_pdb": {
                "path": str(Path(wt_tm_pdb).resolve()),
                "sha256": sha256_file(wt_tm_pdb),
            },
            "mutant_full_pdb": {
                "path": str(Path(mutant_full_pdb).resolve()),
                "sha256": sha256_file(mutant_full_pdb),
            },
            "mutant_tm_pdb": {
                "path": str(Path(mutant_tm_pdb).resolve()),
                "sha256": sha256_file(mutant_tm_pdb),
            },
            "aligned_full_pdb": {
                "path": str(Path(aligned_full_pdb).resolve()),
                "sha256": sha256_file(aligned_full_pdb),
            },
            "aligned_tm_pdb": {
                "path": str(Path(aligned_tm_pdb).resolve()),
                "sha256": sha256_file(aligned_tm_pdb),
            },
        },
    }
    manifest["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(manifest)
    ).hexdigest()
    write_canonical_json(manifest_path, manifest)
    return manifest


def materialize_wt_frame_reference(
    *,
    receptor: str,
    wt_full_pdb: Path,
    wt_tm_pdb: Path,
    run_full_pdb: Path,
    run_tm_pdb: Path,
    manifest_path: Path,
    helices: Sequence[Sequence[int]],
    chain: str = "A",
) -> dict:
    """Materialize the WT receptor as a run-local identity-frame input."""
    wt_full_atoms = parse_atoms(wt_full_pdb)
    wt_tm_atoms = parse_atoms(wt_tm_pdb)
    full_ca = ca_map(wt_full_atoms)
    selected = select_tm_ca(wt_tm_atoms, helices, chain=chain)
    if len(selected) != 147:
        raise ValueError(f"{receptor}/WT: expected 147 TM CA, got {len(selected)}")

    run_full_pdb.parent.mkdir(parents=True, exist_ok=True)
    run_tm_pdb.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(wt_full_pdb, run_full_pdb)
    shutil.copyfile(wt_tm_pdb, run_tm_pdb)

    identity_rotation = np.eye(3)
    identity_translation = np.zeros(3)
    manifest = {
        "schema": FRAME_MANIFEST_SCHEMA,
        "status": "wt_frame_reference",
        "receptor": receptor,
        "mutation": "WT",
        "target_frame": f"{receptor}_WT_docking_frame",
        "provenance_status": "canonical_wt_coordinate",
        "alignment_selection": {
            "chain": chain,
            "helices": [list(map(int, interval)) for interval in helices],
            "ca_count": len(selected),
            "residue_pairs": [
                {
                    "chain": atom.chain,
                    "residue_number": atom.resseq,
                    "insertion_code": atom.icode.strip(),
                }
                for atom in selected
            ],
        },
        "identity_validation": {
            "mutation": "WT",
            "full_ca_count": len(full_ca),
            "full_ca_key_sets_equal": True,
            "unexpected_identity_differences": [],
        },
        "transform": {
            "convention": "row_vector: aligned = source @ rotation.T + translation",
            "rotation": identity_rotation.tolist(),
            "translation": identity_translation.tolist(),
            "determinant": 1.0,
            "orthogonality_max_abs_error": 0.0,
        },
        "metrics_angstrom": {
            "pre_alignment_center_distance": 0.0,
            "pre_alignment_rmsd_without_transform": 0.0,
            "post_alignment_rmsd": 0.0,
            "post_write_rounding_rmsd": 0.0,
        },
        "files": {
            "wt_full_pdb": {
                "path": str(Path(wt_full_pdb).resolve()),
                "sha256": sha256_file(wt_full_pdb),
            },
            "wt_tm_pdb": {
                "path": str(Path(wt_tm_pdb).resolve()),
                "sha256": sha256_file(wt_tm_pdb),
            },
            "aligned_full_pdb": {
                "path": str(Path(run_full_pdb).resolve()),
                "sha256": sha256_file(run_full_pdb),
            },
            "aligned_tm_pdb": {
                "path": str(Path(run_tm_pdb).resolve()),
                "sha256": sha256_file(run_tm_pdb),
            },
        },
    }
    manifest["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(manifest)
    ).hexdigest()
    write_canonical_json(manifest_path, manifest)
    return manifest
