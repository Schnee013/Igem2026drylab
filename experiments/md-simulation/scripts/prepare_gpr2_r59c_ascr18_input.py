#!/usr/bin/env python3
"""Prepare the canonical Gpr2_R59C ASCR18 receptor-frame coordinate.

This reproduces the accepted Gpr2 WT ligand route with the package-local
mutant inputs:

1. fit the docking-frame mutant receptor onto the CHARMM-GUI receptor;
2. apply the same rigid transform to the selected ASCR18 docking pose;
3. reuse the accepted 26-to-54 atom completion contract;
4. audit protein and POPC heavy-atom contacts before assembly.

The script does not edit the returned CHARMM-GUI package or assemble the full
system.  It writes a small canonical ligand coordinate plus validator evidence
that downstream E2 assembly consumes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SYSTEM_DIR = ROOT / "experiments/md-simulation/systems/gpr2-R59C-ascr18"
DEFAULT_POSE = SYSTEM_DIR / "ligand/Gpr2_R59C_ascr18_pose1.sdf"
DEFAULT_DOCK_RECEPTOR = (
    ROOT
    / "experiments/docking-repro/results/ifp_analysis_mutants/receptors"
    / "Gpr2_R59C_tm.pdb"
)
DEFAULT_RETURN_DIR = (
    SYSTEM_DIR
    / "gromacs/charmm_gui_returned/charmm-gui-8417129094/gromacs"
)
DEFAULT_OUTPUT_DIR = SYSTEM_DIR / "gromacs/ascr18_receptor_frame"

PROTEIN_RESNAMES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS",
    "HSD", "HSE", "HSP", "ILE", "LEU", "LYS", "MET", "PHE", "PRO",
    "SER", "THR", "TRP", "TYR", "VAL",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_completion_helper():
    helper_path = ROOT / "experiments/md-simulation/scripts/prepare_ligand_gro.py"
    spec = importlib.util.spec_from_file_location("prepare_ligand_gro", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load completion helper: {helper_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, helper_path


def parse_ca(path: Path) -> dict[int, tuple[str, np.ndarray]]:
    atoms: dict[int, tuple[str, np.ndarray]] = {}
    with path.open() as handle:
        for line in handle:
            if not line.startswith(("ATOM  ", "HETATM")):
                continue
            if line[12:16].strip() != "CA":
                continue
            resid = int(line[22:26])
            atoms[resid] = (
                line[17:20].strip(),
                np.array(
                    [float(line[30:38]), float(line[38:46]), float(line[46:54])]
                ),
            )
    return atoms


def fit_receptor(mobile_path: Path, target_path: Path):
    mobile = parse_ca(mobile_path)
    target = parse_ca(target_path)
    common = sorted(set(mobile) & set(target))
    if len(common) < 200:
        raise RuntimeError(f"too few common CA residues: {len(common)}")
    if mobile.get(59, (None,))[0] != "CYS" or target.get(59, (None,))[0] != "CYS":
        raise RuntimeError("residue 59 is not CYS in both receptor layers")

    xyz_mobile = np.array([mobile[resid][1] for resid in common])
    xyz_target = np.array([target[resid][1] for resid in common])
    center_mobile = xyz_mobile.mean(axis=0)
    center_target = xyz_target.mean(axis=0)
    covariance = (xyz_mobile - center_mobile).T @ (xyz_target - center_target)
    left, _, right_t = np.linalg.svd(covariance)
    rotation = (
        right_t.T
        @ np.diag([1.0, 1.0, np.sign(np.linalg.det(right_t.T @ left.T))])
        @ left.T
    )
    translation = center_target - rotation @ center_mobile
    fitted = (rotation @ xyz_mobile.T).T + translation
    deltas = np.linalg.norm(fitted - xyz_target, axis=1)
    rmsd = float(np.sqrt(np.mean(deltas**2)))
    max_delta = float(deltas.max())
    if rmsd > 0.25 or max_delta > 1.0:
        raise RuntimeError(
            f"receptor fit outside package heuristic: RMSD={rmsd:.4f} A, "
            f"max={max_delta:.4f} A"
        )
    return common, rotation, translation, rmsd, max_delta


def parse_sdf_coordinates(path: Path) -> np.ndarray:
    lines = path.read_text().splitlines()
    atom_count = int(lines[3][0:3])
    if atom_count != 26:
        raise RuntimeError(f"expected 26 selected-pose atoms, found {atom_count}")
    return np.array(
        [
            [
                float(lines[4 + index][0:10]),
                float(lines[4 + index][10:20]),
                float(lines[4 + index][20:30]),
            ]
            for index in range(atom_count)
        ]
    )


def write_pdb(coords_by_itp, itp_atoms, output_path: Path) -> None:
    with output_path.open("w") as handle:
        for serial, (itp_index, atom_name) in enumerate(itp_atoms, 1):
            x, y, z = coords_by_itp[itp_index]
            element = "H" if atom_name.startswith("H") else atom_name[0]
            handle.write(
                f"HETATM{serial:5d} {atom_name:>4s} ASR L 407    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {element:>2s}\n"
            )
        handle.write("END\n")


def parse_gro_heavy_atoms(path: Path):
    protein = []
    popc: dict[int, list[tuple[str, np.ndarray]]] = {}
    with path.open() as handle:
        handle.readline()
        atom_count = int(handle.readline().strip())
        for _ in range(atom_count):
            line = handle.readline()
            resid = int(line[0:5])
            resname = line[5:10].strip()
            atom_name = line[10:15].strip()
            if atom_name.startswith("H"):
                continue
            xyz = np.array(
                [float(line[20:28]), float(line[28:36]), float(line[36:44])]
            ) * 10.0
            if resname == "POPC":
                popc.setdefault(resid, []).append((atom_name, xyz))
            elif resname in PROTEIN_RESNAMES:
                protein.append((resid, resname, atom_name, xyz))
        box = np.array([float(value) for value in handle.readline().split()[:3]]) * 10.0
    return atom_count, protein, popc, box


def contact_audit(ligand_heavy, protein, popc):
    protein_xyz = np.array([atom[3] for atom in protein])
    protein_distances = np.linalg.norm(
        ligand_heavy[:, None, :] - protein_xyz[None, :, :], axis=2
    )
    lig_index, protein_index = np.unravel_index(
        int(np.argmin(protein_distances)), protein_distances.shape
    )
    protein_min = float(protein_distances[lig_index, protein_index])
    protein_atom = protein[protein_index][:3]

    popc_rows = []
    for resid, atoms in sorted(popc.items()):
        popc_xyz = np.array([atom[1] for atom in atoms])
        distance = float(
            np.linalg.norm(ligand_heavy[:, None, :] - popc_xyz[None, :, :], axis=2).min()
        )
        if distance < 5.0:
            popc_rows.append((resid, distance))
    remove_popc = [resid for resid, distance in popc_rows if distance < 2.0]
    if protein_min < 2.0:
        raise RuntimeError(f"ligand-protein heavy-atom clash: {protein_min:.3f} A")
    if not remove_popc:
        raise RuntimeError("expected the audited POPC overlap but found none")
    return protein_min, protein_atom, popc_rows, remove_popc


def write_tsv(path: Path, header: list[str], rows) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pose", type=Path, default=DEFAULT_POSE)
    parser.add_argument("--dock-receptor", type=Path, default=DEFAULT_DOCK_RECEPTOR)
    parser.add_argument("--return-dir", type=Path, default=DEFAULT_RETURN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    target_pdb = args.return_dir / "step5_input.pdb"
    target_gro = args.return_dir / "step5_input.gro"
    for required in (args.pose, args.dock_receptor, target_pdb, target_gro):
        if not required.is_file():
            raise FileNotFoundError(required)

    helper, helper_path = load_completion_helper()
    common, rotation, translation, rmsd, max_delta = fit_receptor(
        args.dock_receptor, target_pdb
    )
    pose = parse_sdf_coordinates(args.pose)
    aligned_pose = (rotation @ pose.T).T + translation
    coords_by_itp = {
        itp_index: aligned_pose[dock_index - 1]
        for dock_index, (_, itp_index) in helper.DOCK_TO_CGENFF.items()
    }
    coords_by_itp = helper.generate_h_positions(coords_by_itp)
    if len(coords_by_itp) != 54:
        raise RuntimeError(f"expected 54 completed atoms, found {len(coords_by_itp)}")

    heavy_indices = [
        itp_index
        for itp_index, atom_name in helper.ITP_ATOMS
        if not atom_name.startswith("H")
    ]
    ligand_all = np.array([coords_by_itp[index] for index, _ in helper.ITP_ATOMS])
    ligand_heavy = np.array([coords_by_itp[index] for index in heavy_indices])
    base_atoms, protein, popc, box = parse_gro_heavy_atoms(target_gro)
    protein_min, protein_atom, popc_rows, remove_popc = contact_audit(
        ligand_heavy, protein, popc
    )
    if not (np.all(ligand_all >= 0.0) and np.all(ligand_all <= box)):
        raise RuntimeError("completed ligand coordinate falls outside the returned box")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    gro_path = args.output_dir / "ASCR18_receptor_frame.gro"
    pdb_path = args.output_dir / "ASCR18_receptor_frame.pdb"
    helper.write_gro(
        coords_by_itp,
        gro_path,
        title="Gpr2_R59C ASCR18 receptor-frame completed",
    )
    write_pdb(coords_by_itp, helper.ITP_ATOMS, pdb_path)

    alignment_rows = [
        ("common_ca_count", len(common)),
        ("ca_rmsd_A", f"{rmsd:.6f}"),
        ("ca_max_delta_A", f"{max_delta:.6f}"),
        ("rotation_row_1", " ".join(f"{value:.9f}" for value in rotation[0])),
        ("rotation_row_2", " ".join(f"{value:.9f}" for value in rotation[1])),
        ("rotation_row_3", " ".join(f"{value:.9f}" for value in rotation[2])),
        ("translation_A", " ".join(f"{value:.9f}" for value in translation)),
    ]
    write_tsv(args.output_dir / "receptor_alignment.tsv", ["metric", "value"], alignment_rows)

    contact_rows = [
        (
            "protein",
            f"{protein_atom[0]}:{protein_atom[1]}:{protein_atom[2]}",
            f"{protein_min:.6f}",
            "retain",
        )
    ]
    for resid, distance in popc_rows:
        action = "remove" if resid in remove_popc else "retain"
        contact_rows.append(("POPC", str(resid), f"{distance:.6f}", action))
    write_tsv(
        args.output_dir / "clash_audit.tsv",
        ["component", "residue_or_atom", "min_heavy_distance_A", "action"],
        contact_rows,
    )

    expected_pre_genion_atoms = base_atoms + 54 - 134 * len(remove_popc)
    expected_final_atoms = expected_pre_genion_atoms - 2
    decision_rows = [
        ("status", "PASS_RECEPTOR_FRAME_COORDINATE"),
        ("pose_sha256", sha256(args.pose)),
        ("dock_receptor_sha256", sha256(args.dock_receptor)),
        ("returned_step5_pdb_sha256", sha256(target_pdb)),
        ("returned_step5_gro_sha256", sha256(target_gro)),
        ("completion_helper_sha256", sha256(helper_path)),
        ("completed_gro_sha256", sha256(gro_path)),
        ("completed_pdb_sha256", sha256(pdb_path)),
        ("completed_atom_count", "54"),
        ("completed_heavy_atom_count", "23"),
        ("remove_popc_resids", ",".join(str(value) for value in remove_popc)),
        ("expected_popc_count", str(201 - len(remove_popc))),
        ("expected_pre_genion_atom_count", str(expected_pre_genion_atoms)),
        ("expected_final_atom_count", str(expected_final_atoms)),
        ("expected_pot_count_after_genion", "88"),
        ("expected_tip3_count_after_genion", "32404"),
    ]
    write_tsv(args.output_dir / "assembly_decision.tsv", ["field", "value"], decision_rows)

    print(f"completed_gro={gro_path}")
    print(f"alignment_ca={len(common)} rmsd_A={rmsd:.6f} max_A={max_delta:.6f}")
    print(f"protein_min_A={protein_min:.6f}")
    print(f"remove_popc={','.join(str(value) for value in remove_popc)}")
    print(f"expected_final_atoms={expected_final_atoms}")


if __name__ == "__main__":
    main()
