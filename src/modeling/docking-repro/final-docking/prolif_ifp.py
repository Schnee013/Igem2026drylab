#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import prolif as plf
from meeko import Polymer
from rdkit import Chem, rdBase


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate ProLIF interaction fingerprints from a "
            "Meeko receptor JSON and docked-pose SDF."
        )
    )
    parser.add_argument(
        "--receptor-json",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--poses",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--vicinity-cutoff",
        type=float,
        default=6.0,
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--interactions",
        nargs="+",
        default=None,
        help="Interaction names; omit to use ProLIF defaults.",
    )
    return parser.parse_args()


def hydrogen_count(mol: plf.Molecule) -> int:
    return sum(
        atom.GetAtomicNum() == 1
        for atom in mol.GetAtoms()
    )


def load_receptor(path: Path) -> plf.Molecule:
    try:
        polymer = Polymer.from_json(
            path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        raise SystemExit(
            f"Failed to load Meeko receptor JSON: {path}\n{exc}"
        ) from exc

    combined = Chem.Mol()

    for residue_id, monomer in (
        polymer.get_valid_monomers().items()
    ):
        chain, number_text = residue_id.split(":", 1)

        if number_text[-1:].isalpha():
            insertion_code = number_text[-1]
            residue_number = int(number_text[:-1])
        else:
            insertion_code = ""
            residue_number = int(number_text)

        residue = Chem.Mol(monomer.rdkit_mol)

        for atom, atom_name in zip(
            residue.GetAtoms(),
            monomer.atom_names,
            strict=True,
        ):
            info = Chem.AtomPDBResidueInfo()
            info.SetName(f"{atom_name:>4s}")
            info.SetResidueName(
                monomer.input_resname
            )
            info.SetResidueNumber(
                residue_number
            )
            info.SetChainId(chain)
            info.SetInsertionCode(
                insertion_code
            )
            info.SetIsHeteroAtom(False)
            atom.SetMonomerInfo(info)

        combined = Chem.CombineMols(
            combined,
            residue,
        )

    try:
        Chem.SanitizeMol(combined)
    except Exception as exc:
        raise SystemExit(
            f"Failed to sanitize receptor graph: {exc}"
        ) from exc

    protein = plf.Molecule.from_rdkit(combined)

    if hydrogen_count(protein) == 0:
        raise SystemExit(
            "Receptor has no explicit hydrogens."
        )

    if len(protein.residues) < 2:
        raise SystemExit(
            "Receptor residue metadata was not restored."
        )

    return protein


def load_poses(path: Path) -> list[plf.Molecule]:
    try:
        poses = list(
            plf.sdf_supplier(str(path))
        )
    except Exception as exc:
        raise SystemExit(
            f"Failed to parse pose SDF: {path}\n{exc}"
        ) from exc

    if not poses:
        raise SystemExit(
            f"No valid molecule records found: {path}"
        )

    missing_hydrogens = [
        index + 1
        for index, pose in enumerate(poses)
        if hydrogen_count(pose) == 0
    ]

    if missing_hydrogens:
        raise SystemExit(
            "Pose records without explicit hydrogens: "
            + ", ".join(map(str, missing_hydrogens))
        )

    return poses


def summarize_interactions(
    counts: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "protein",
        "interaction",
        "poses_with_interaction",
        "pose_frequency",
        "total_geometries",
    ]

    if len(counts.columns) == 0:
        return pd.DataFrame(columns=columns)

    presence = counts.astype(bool)

    presence_by_residue = (
        presence.T
        .groupby(
            level=["protein", "interaction"]
        )
        .max()
        .T
    )

    counts_by_residue = (
        counts.T
        .groupby(
            level=["protein", "interaction"]
        )
        .sum()
        .T
    )

    summary = pd.DataFrame(
        {
            "poses_with_interaction":
                presence_by_residue.sum(),
            "pose_frequency":
                presence_by_residue.mean(),
            "total_geometries":
                counts_by_residue.sum(),
        }
    ).reset_index()

    summary.sort_values(
        [
            "pose_frequency",
            "poses_with_interaction",
            "protein",
            "interaction",
        ],
        ascending=[
            False,
            False,
            True,
            True,
        ],
        inplace=True,
    )

    return summary


def main() -> None:
    args = parse_args()

    if args.n_jobs < 1:
        raise SystemExit(
            "--n-jobs must be >= 1"
        )

    if not args.receptor_json.is_file():
        raise SystemExit(
            "Receptor JSON not found: "
            f"{args.receptor_json}"
        )

    if not args.poses.is_file():
        raise SystemExit(
            f"Pose SDF not found: {args.poses}"
        )

    protein = load_receptor(
        args.receptor_json
    )
    poses = load_poses(args.poses)

    protein_h = hydrogen_count(protein)
    ligand_h = [
        hydrogen_count(pose)
        for pose in poses
    ]

    fingerprint = plf.Fingerprint(
        interactions=args.interactions,
        count=True,
        vicinity_cutoff=args.vicinity_cutoff,
    )

    fingerprint.run_from_iterable(
        poses,
        protein,
        n_jobs=args.n_jobs,
        progress=True,
    )

    counts = fingerprint.to_dataframe(
        index_col="Pose"
    )
    presence = counts.astype(bool)
    summary = summarize_interactions(
        counts
    )

    args.out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    counts.to_csv(
        args.out_dir / "ifp_counts.csv"
    )
    presence.to_csv(
        args.out_dir / "ifp_presence.csv"
    )
    summary.to_csv(
        args.out_dir
        / "interaction_frequency.csv",
        index=False,
    )
    fingerprint.to_pickle(
        args.out_dir / "fingerprint.pkl"
    )

    configured_interactions = sorted(
        set(fingerprint.interactions)
        | set(
            fingerprint.bridged_interactions
        )
    )

    if len(counts.columns):
        observed_interactions = sorted(
            set(
                counts.columns.get_level_values(
                    "interaction"
                )
            )
        )
    else:
        observed_interactions = []

    metadata = {
        "prolif_version": plf.__version__,
        "rdkit_version":
            rdBase.rdkitVersion,
        "pandas_version":
            pd.__version__,
        "receptor_json": str(
            args.receptor_json.resolve()
        ),
        "poses": str(
            args.poses.resolve()
        ),
        "n_poses": len(poses),
        "protein_residue_count":
            len(protein.residues),
        "protein_formal_charge": sum(
            atom.GetFormalCharge()
            for atom in protein.GetAtoms()
        ),
        "protein_explicit_hydrogens":
            protein_h,
        "pose_explicit_hydrogens":
            ligand_h,
        "vicinity_cutoff_A":
            args.vicinity_cutoff,
        "n_jobs": args.n_jobs,
        "configured_interactions":
            configured_interactions,
        "observed_interactions":
            observed_interactions,
        "feature_count":
            len(counts.columns),
        "total_geometries": int(
            counts.to_numpy().sum()
        ),
    }

    (
        args.out_dir
        / "run_metadata.json"
    ).write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"ProLIF {plf.__version__}: "
        f"{len(poses)} poses, "
        f"{len(counts.columns)} features, "
        f"{metadata['total_geometries']} "
        f"geometries -> {args.out_dir}"
    )


if __name__ == "__main__":
    main()