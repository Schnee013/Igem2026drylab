#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import filecmp
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from meeko import Polymer
from rdkit import Chem
from project_paths import REPOSITORY_ROOT, resolve_paths


EXPECTED_JOBS = 70
EXPECTED_MODELS = 35
EXPECTED_LIGANDS = {
    "ascr3_deprotonated",
    "ascr18_deprotonated",
}
IFP_FILES = {
    "fingerprint.pkl",
    "ifp_counts.csv",
    "ifp_presence.csv",
    "interaction_frequency.csv",
    "run_metadata.json",
}


@dataclass(frozen=True)
class Job:
    model_rel: Path
    ligand: str
    run_name: str
    poses_pdbqt: Path
    receptor_pdb: Path
    receptor_pdbqt: Path

    @property
    def key(self) -> str:
        return f"{self.model_rel}/{self.ligand}/{self.run_name}"


def parse_args() -> argparse.Namespace:
    script_root = REPOSITORY_ROOT
    parser = argparse.ArgumentParser(
        description=(
            "Prepare Meeko receptor JSON and pose SDF inputs, validate their "
            "lineage, and run ProLIF for the AF3 docking result tree."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=script_root,
        help="Drylab repository root; paths are read from configs/paths.json.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Output root (default: prolif_results in configs/paths.json).",
    )
    parser.add_argument("--docking-root", type=Path, default=None)
    parser.add_argument("--receptor-pdb-root", type=Path, default=None)
    parser.add_argument("--receptor-pdbqt-root", type=Path, default=None)
    parser.add_argument(
        "--receptor-json-root", type=Path, default=None,
        help="Meeko cache root (default: DRYLAB_PAYLOAD_ROOT/final-docking/prolif/af3).",
    )
    parser.add_argument(
        "--limit-models",
        type=int,
        default=0,
        help="Process only the first N receptor models; 0 means all models.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Validate and skip already complete job directories.",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=1,
        help="ProLIF worker count per ligand job (default: 1).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate discovery and print selected jobs without creating outputs.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise RuntimeError(message)


def run_command(command: list[str]) -> None:
    print(f"$ {shlex.join(command)}", flush=True)
    subprocess.run(command, check=True)


def require_executable(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        fail(
            f"Required executable not found: {name}. "
            "Run this script inside the local conda environment 'docking'."
        )
    return path


def count_pdbqt_models(path: Path) -> int:
    count = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("MODEL "):
                count += 1
    return count or 1


def ligand_charge_from_pdbqt(path: Path) -> int:
    smiles_values: set[str] = set()
    prefix = "REMARK SMILES "
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith(prefix) and not line.startswith("REMARK SMILES IDX"):
                smiles_values.add(line[len(prefix) :].strip())
    if not smiles_values:
        fail(f"No REMARK SMILES found in docking PDBQT: {path}")
    if len(smiles_values) != 1:
        fail(f"Multiple ligand SMILES found in docking PDBQT: {path}")
    smiles = next(iter(smiles_values))
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        fail(f"RDKit failed to parse PDBQT REMARK SMILES in {path}: {smiles}")
    return sum(atom.GetFormalCharge() for atom in molecule.GetAtoms())


def validate_pose_sdf(
    path: Path,
    expected_poses: int,
    expected_formal_charge: int,
) -> dict[str, object]:
    supplier = Chem.SDMolSupplier(str(path), removeHs=False)
    molecules = list(supplier)
    invalid = [index + 1 for index, mol in enumerate(molecules) if mol is None]
    if invalid:
        fail(f"Invalid SDF records in {path}: {invalid}")
    if len(molecules) != expected_poses:
        fail(
            f"Pose count mismatch for {path}: "
            f"PDBQT has {expected_poses}, SDF has {len(molecules)}"
        )

    hydrogen_counts = [
        sum(atom.GetAtomicNum() == 1 for atom in mol.GetAtoms())
        for mol in molecules
        if mol is not None
    ]
    missing_h = [index + 1 for index, value in enumerate(hydrogen_counts) if value == 0]
    if missing_h:
        fail(f"SDF poses without explicit hydrogen in {path}: {missing_h}")

    formal_charges = [
        sum(atom.GetFormalCharge() for atom in mol.GetAtoms())
        for mol in molecules
        if mol is not None
    ]
    wrong_charges = [
        index + 1
        for index, value in enumerate(formal_charges)
        if value != expected_formal_charge
    ]
    if wrong_charges:
        fail(
            f"SDF pose charge differs from docking PDBQT REMARK SMILES in {path}: "
            f"expected {expected_formal_charge:+d}, bad records {wrong_charges}, "
            f"observed {formal_charges}"
        )
    return {
        "n_poses": len(molecules),
        "pose_explicit_hydrogens": hydrogen_counts,
        "expected_formal_charge_from_pdbqt_smiles": expected_formal_charge,
        "pose_formal_charges": formal_charges,
    }


def receptor_json_stats(path: Path) -> dict[str, int]:
    polymer = Polymer.from_json(path.read_text(encoding="utf-8"))
    monomers = polymer.get_valid_monomers()
    if len(monomers) < 2:
        fail(f"Meeko JSON has too few valid monomers: {path}")

    atoms = 0
    hydrogens = 0
    formal_charge = 0
    for monomer in monomers.values():
        molecule = monomer.rdkit_mol
        atoms += molecule.GetNumAtoms()
        hydrogens += sum(atom.GetAtomicNum() == 1 for atom in molecule.GetAtoms())
        formal_charge += sum(atom.GetFormalCharge() for atom in molecule.GetAtoms())
    if hydrogens == 0:
        fail(f"Meeko receptor JSON has no explicit hydrogen: {path}")
    return {
        "residue_count": len(monomers),
        "atom_count": atoms,
        "explicit_hydrogens": hydrogens,
        "formal_charge": formal_charge,
    }


def discover_jobs(
    root: Path,
    *,
    docking_root: Path | None = None,
    receptor_pdb_root: Path | None = None,
    receptor_pdbqt_root: Path | None = None,
) -> tuple[list[Job], dict[Path, list[Job]]]:
    paths = resolve_paths(root)
    docking_root = docking_root or paths["vina_results"]
    receptor_pdb_root = receptor_pdb_root or paths["receptor_pdb"]
    receptor_pdbqt_root = receptor_pdbqt_root or paths["receptor_pdbqt"]
    jobs: list[Job] = []

    for poses_pdbqt in sorted(docking_root.rglob("poses.pdbqt")):
        relative = poses_pdbqt.relative_to(docking_root)
        parts = relative.parts
        if "ligands" not in parts:
            fail(f"Unexpected docking path without 'ligands': {poses_pdbqt}")
        ligand_index = parts.index("ligands")
        if len(parts) != ligand_index + 4:
            fail(f"Unexpected docking result depth: {poses_pdbqt}")

        model_rel = Path(*parts[:ligand_index])
        ligand = parts[ligand_index + 1]
        run_name = parts[ligand_index + 2]
        receptor_pdb = receptor_pdb_root / model_rel.with_suffix(".pdb")
        receptor_pdbqt = receptor_pdbqt_root / model_rel.with_suffix(".pdbqt")
        if not receptor_pdb.is_file():
            fail(f"Missing receptor PDB for {poses_pdbqt}: {receptor_pdb}")
        if not receptor_pdbqt.is_file():
            fail(f"Missing receptor PDBQT for {poses_pdbqt}: {receptor_pdbqt}")

        jobs.append(
            Job(
                model_rel=model_rel,
                ligand=ligand,
                run_name=run_name,
                poses_pdbqt=poses_pdbqt,
                receptor_pdb=receptor_pdb,
                receptor_pdbqt=receptor_pdbqt,
            )
        )

    by_model: dict[Path, list[Job]] = defaultdict(list)
    for job in jobs:
        by_model[job.model_rel].append(job)

    if len(jobs) != EXPECTED_JOBS:
        fail(f"Expected {EXPECTED_JOBS} pose jobs, discovered {len(jobs)}")
    if len(by_model) != EXPECTED_MODELS:
        fail(f"Expected {EXPECTED_MODELS} receptor models, discovered {len(by_model)}")

    for model_rel, model_jobs in by_model.items():
        ligands = {job.ligand for job in model_jobs}
        if len(model_jobs) != 2 or ligands != EXPECTED_LIGANDS:
            fail(
                f"Expected ASCR3 and ASCR18 once for {model_rel}; "
                f"found {[job.ligand for job in model_jobs]}"
            )
    return jobs, by_model


def receptor_output_dir(output_root: Path, model_rel: Path) -> Path:
    return output_root / model_rel / "receptor"


def job_output_dir(output_root: Path, job: Job) -> Path:
    return (
        output_root
        / job.model_rel
        / "ligands"
        / job.ligand
        / job.run_name
    )


def validate_complete_job(path: Path, expected_poses: int) -> None:
    required = {
        path / "poses.sdf",
        path / "job_metadata.json",
    }
    required.update(path / "ifp" / name for name in IFP_FILES)
    missing = sorted(str(item) for item in required if not item.is_file())
    if missing:
        fail(f"Incomplete existing job directory {path}; missing: {missing}")

    metadata = json.loads((path / "ifp" / "run_metadata.json").read_text())
    if metadata.get("n_poses") != expected_poses:
        fail(
            f"Existing job pose count mismatch in {path}: "
            f"expected {expected_poses}, found {metadata.get('n_poses')}"
        )


def prepare_receptor(
    model_rel: Path,
    model_jobs: list[Job],
    output_root: Path,
    mk_prepare_receptor: str,
    receptor_json_root: Path,
) -> tuple[Path, dict[str, int]]:
    first = model_jobs[0]
    destination = receptor_output_dir(output_root, model_rel)
    receptor_json = receptor_output_dir(receptor_json_root, model_rel) / "receptor.json"
    regenerated_pdbqt = destination / "receptor_regenerated.pdbqt"
    validation_path = destination / "receptor_validation.json"

    existing = [receptor_json.exists(), regenerated_pdbqt.exists(), validation_path.exists()]
    if all(existing):
        if not filecmp.cmp(first.receptor_pdbqt, regenerated_pdbqt, shallow=False):
            fail(f"Existing regenerated receptor PDBQT differs: {model_rel}")
        stats = receptor_json_stats(receptor_json)
        print(f"REUSE receptor {model_rel}", flush=True)
        return receptor_json, stats

    if any(existing) and existing != [False, True, True]:
        fail(f"Partial receptor output exists; inspect manually: {destination}")

    destination.mkdir(parents=True, exist_ok=True)
    receptor_json.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".prepare-", dir=destination) as temp_name:
        temp_dir = Path(temp_name)
        temp_json = temp_dir / "receptor.json"
        temp_pdbqt = temp_dir / "receptor_regenerated.pdbqt"
        run_command(
            [
                mk_prepare_receptor,
                "--read_pdb",
                str(first.receptor_pdb),
                "-p",
                str(temp_pdbqt),
                "-j",
                str(temp_json),
            ]
        )
        if not filecmp.cmp(first.receptor_pdbqt, temp_pdbqt, shallow=False):
            fail(
                "STOP: regenerated receptor PDBQT differs from the exact "
                f"docking input for {model_rel}"
            )
        stats = receptor_json_stats(temp_json)
        validation = {
            "model_rel": str(model_rel),
            "source_receptor_pdb": str(first.receptor_pdb.resolve()),
            "source_receptor_pdbqt": str(first.receptor_pdbqt.resolve()),
            "pdbqt_byte_identical": True,
            **stats,
        }
        shutil.move(str(temp_json), receptor_json)
        temp_pdbqt.replace(regenerated_pdbqt)
        validation_path.write_text(
            json.dumps(validation, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        f"PASS receptor {model_rel}: "
        f"{stats['residue_count']} residues, charge {stats['formal_charge']:+d}",
        flush=True,
    )
    return receptor_json, stats


def run_ligand_job(
    job: Job,
    receptor_json: Path,
    receptor_stats: dict[str, int],
    output_root: Path,
    mk_export: str,
    prolif_script: Path,
    n_jobs: int,
    resume: bool,
) -> str:
    expected_poses = count_pdbqt_models(job.poses_pdbqt)
    expected_formal_charge = ligand_charge_from_pdbqt(job.poses_pdbqt)
    destination = job_output_dir(output_root, job)
    if destination.exists():
        if not resume:
            fail(f"Job output already exists; rerun with --resume: {destination}")
        validate_complete_job(destination, expected_poses)
        print(f"SKIP complete {job.key}", flush=True)
        return "skipped"

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{job.run_name}-", dir=destination.parent) as temp_name:
        temp_dir = Path(temp_name)
        poses_sdf = temp_dir / "poses.sdf"
        ifp_dir = temp_dir / "ifp"
        run_command([mk_export, str(job.poses_pdbqt), "-s", str(poses_sdf)])
        pose_stats = validate_pose_sdf(
            poses_sdf,
            expected_poses,
            expected_formal_charge,
        )

        run_command(
            [
                sys.executable,
                str(prolif_script),
                "--receptor-json",
                str(receptor_json),
                "--poses",
                str(poses_sdf),
                "--out-dir",
                str(ifp_dir),
                "--n-jobs",
                str(n_jobs),
            ]
        )
        missing_ifp = sorted(
            name for name in IFP_FILES if not (ifp_dir / name).is_file()
        )
        if missing_ifp:
            fail(f"ProLIF output incomplete for {job.key}: {missing_ifp}")

        run_metadata_path = ifp_dir / "run_metadata.json"
        run_metadata = json.loads(run_metadata_path.read_text())
        if run_metadata.get("n_poses") != expected_poses:
            fail(
                f"ProLIF pose count mismatch for {job.key}: "
                f"expected {expected_poses}, found {run_metadata.get('n_poses')}"
            )
        final_poses = destination / "poses.sdf"
        run_metadata.update(
            {
                "poses": str(final_poses.resolve()),
                "source_poses_pdbqt": str(job.poses_pdbqt.resolve()),
                "model_rel": str(job.model_rel),
                "ligand": job.ligand,
                "run_name": job.run_name,
            }
        )
        run_metadata_path.write_text(
            json.dumps(run_metadata, indent=2) + "\n",
            encoding="utf-8",
        )
        job_metadata = {
            "model_rel": str(job.model_rel),
            "ligand": job.ligand,
            "run_name": job.run_name,
            "source_poses_pdbqt": str(job.poses_pdbqt.resolve()),
            "receptor_json": str(receptor_json.resolve()),
            "expected_poses_from_pdbqt": expected_poses,
            **pose_stats,
            "receptor": receptor_stats,
        }
        (temp_dir / "job_metadata.json").write_text(
            json.dumps(job_metadata, indent=2) + "\n",
            encoding="utf-8",
        )
        temp_dir.replace(destination)

    validate_complete_job(destination, expected_poses)
    print(
        f"PASS ligand {job.key}: {expected_poses} poses",
        flush=True,
    )
    return "completed"


def write_manifest(
    path: Path,
    jobs: list[Job],
    selected_models: set[Path],
    statuses: dict[str, str],
    output_root: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "model_rel",
            "ligand",
            "run_name",
            "source_poses_pdbqt",
            "output_dir",
            "selected",
            "status",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for job in jobs:
            writer.writerow(
                {
                    "model_rel": str(job.model_rel),
                    "ligand": job.ligand,
                    "run_name": job.run_name,
                    "source_poses_pdbqt": str(job.poses_pdbqt),
                    "output_dir": str(job_output_dir(output_root, job)),
                    "selected": job.model_rel in selected_models,
                    "status": statuses.get(
                        job.key,
                        "pending" if job.model_rel in selected_models else "not_selected",
                    ),
                }
            )


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    payload_root = Path(os.environ.get("DRYLAB_PAYLOAD_ROOT", str(root.parent / "drylab-payloads")))
    receptor_json_root = (
        args.receptor_json_root.expanduser().resolve()
        if args.receptor_json_root is not None
        else payload_root.expanduser().resolve() / "final-docking" / "prolif" / "af3"
    )
    output_root = (
        args.output_root.resolve()
        if args.output_root is not None
        else resolve_paths(root)["prolif_results"]
    )
    if args.limit_models < 0:
        fail("--limit-models must be >= 0")
    if args.n_jobs < 1:
        fail("--n-jobs must be >= 1")

    prolif_script = Path(__file__).resolve().with_name("prolif_ifp.py")
    if not prolif_script.is_file():
        fail(f"Missing ProLIF script: {prolif_script}")
    if "--receptor-json" not in prolif_script.read_text(encoding="utf-8"):
        fail(f"ProLIF script is not the validated JSON-input version: {prolif_script}")

    jobs, by_model = discover_jobs(
        root,
        docking_root=args.docking_root,
        receptor_pdb_root=args.receptor_pdb_root,
        receptor_pdbqt_root=args.receptor_pdbqt_root,
    )
    ordered_models = sorted(by_model, key=str)
    selected_model_list = (
        ordered_models[: args.limit_models]
        if args.limit_models
        else ordered_models
    )
    selected_models = set(selected_model_list)
    selected_jobs = [job for job in jobs if job.model_rel in selected_models]

    print(
        f"DISCOVERY: {len(jobs)} jobs, {len(by_model)} models; "
        f"selected {len(selected_jobs)} jobs across {len(selected_models)} models",
        flush=True,
    )
    for model_rel in selected_model_list:
        print(f"SELECT model {model_rel}", flush=True)
        for job in sorted(by_model[model_rel], key=lambda item: item.ligand):
            print(f"  - {job.ligand}/{job.run_name}", flush=True)

    if args.dry_run:
        return

    manifest_path = output_root / "batch_manifest.csv"
    if manifest_path.exists() and not args.resume:
        fail("Output already has a batch_manifest.csv; use a new --output-root or --resume.")
    mk_prepare_receptor = require_executable("mk_prepare_receptor.py")
    mk_export = require_executable("mk_export.py")
    statuses: dict[str, str] = {}
    write_manifest(manifest_path, jobs, selected_models, statuses, output_root)

    for model_rel in selected_model_list:
        model_jobs = sorted(by_model[model_rel], key=lambda item: item.ligand)
        receptor_json, receptor_stats = prepare_receptor(
            model_rel,
            model_jobs,
            output_root,
            mk_prepare_receptor,
            receptor_json_root,
        )
        for job in model_jobs:
            try:
                statuses[job.key] = run_ligand_job(
                    job,
                    receptor_json,
                    receptor_stats,
                    output_root,
                    mk_export,
                    prolif_script,
                    args.n_jobs,
                    args.resume,
                )
            except Exception:
                statuses[job.key] = "failed"
                write_manifest(manifest_path, jobs, selected_models, statuses, output_root)
                raise
            write_manifest(manifest_path, jobs, selected_models, statuses, output_root)

    completed = sum(value == "completed" for value in statuses.values())
    skipped = sum(value == "skipped" for value in statuses.values())
    print(
        f"BATCH PASS: completed={completed}, skipped={skipped}, "
        f"selected={len(selected_jobs)}, manifest={manifest_path}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BATCH STOP: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
