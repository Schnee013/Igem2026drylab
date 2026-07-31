"""Evaluate one verified docking job against frozen membrane/pocket gates."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from docking_manifest import (
    load_json,
    sha256_file,
    verify_environment_manifest,
    verify_frame_run_manifest,
    verify_job_manifest,
    verify_pdbqt_manifest,
)
from frame_alignment import canonical_json_bytes, write_canonical_json
from geometry_gate import (
    evaluate_pose_set,
    verify_membrane_transform_manifest,
)
from run_frame_repair_ifp import IFP_REPORT_SCHEMA
from utils import load_config


def verify_ifp_report(
    path: Path,
    *,
    job: dict[str, Any],
) -> tuple[dict[str, Any], dict[int, bool]]:
    report = load_json(path)
    if report.get("schema") != IFP_REPORT_SCHEMA or report.get("status") != "complete":
        raise ValueError("IFP report 状态或 schema 不可用")
    payload = dict(report)
    expected_identity = payload.pop("manifest_identity", None)
    actual_identity = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    if not expected_identity or actual_identity != expected_identity:
        raise ValueError("IFP report content identity mismatch")
    if report.get("job", {}).get("job_identity") != job["job_identity"]:
        raise ValueError("IFP report 绑定到不同 job")
    if report.get("pose_file", {}).get("sha256") != job["outputs"]["poses"]["sha256"]:
        raise ValueError("IFP report pose body 与 job 不同源")
    pose_models = {
        item["model_number"]: item
        for item in job["outputs"]["poses"]["models"]
    }
    contacts: dict[int, bool] = {}
    for model in report.get("models", []):
        model_number = int(model["model_number"])
        if model_number in contacts:
            raise ValueError("IFP report 包含重复 MODEL")
        source = pose_models.get(model_number)
        if source is None or source["body_sha256"] != model["pose_body_sha256"]:
            raise ValueError("IFP report MODEL body 与 job 不同源")
        contacts[model_number] = bool(model["has_standard_prolif_contact"])
    if set(contacts) != set(pose_models):
        raise ValueError("IFP report MODEL 集合与 job pose 不完整对应")
    sdf_binding = report.get("conversion", {}).get("sdf_pose_binding", [])
    if len(sdf_binding) != len(pose_models):
        raise ValueError("IFP report 缺少完整 SDF/PDBQT MODEL 绑定")
    for binding in sdf_binding:
        source = pose_models.get(int(binding["model_number"]))
        if (
            source is None
            or source["body_sha256"] != binding["pose_body_sha256"]
            or source["affinity"] != binding["affinity"]
            or source["atom_count"] != binding["atom_count"]
        ):
            raise ValueError("IFP SDF/PDBQT binding 与 job pose 不同源")
    return report, contacts


def thresholds_for(
    config: dict[str, Any],
    *,
    receptor: str,
    ligand: str,
) -> dict[str, Any]:
    gate = config["frame_repair"]["geometry_gate"]
    common = gate["common"]
    receptor_gate = gate[receptor]
    ligand_gate = receptor_gate["by_ligand"][ligand]
    return {
        "calibration_status": receptor_gate["calibration_status"],
        "requested_max_modes": common["requested_max_modes"],
        "radial_max_angstrom": receptor_gate["radial_max_angstrom"],
        "membrane_height_min_angstrom": ligand_gate[
            "membrane_height_min_angstrom"
        ],
        "membrane_height_max_angstrom": ligand_gate[
            "membrane_height_max_angstrom"
        ],
        "min_passing_modes": ligand_gate["min_passing_modes"],
        "contact_cutoff_angstrom": common["distance_contact_audit_cutoff_angstrom"],
        "min_protein_closer_atoms": ligand_gate[
            "min_protein_closer_atoms"
        ],
        "require_ifp_contact": common["require_standard_prolif_contact"],
        "sources": {
            "common": common["source"],
            "receptor": receptor_gate.get(
                "source",
                {"calibration_artifact": gate["calibration_artifact"]},
            ),
            "ligand_calibration": ligand_gate["calibration"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--job-manifest", required=True)
    parser.add_argument("--ifp-report", default=None)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    job_manifest_path = Path(args.job_manifest).resolve()
    job = verify_job_manifest(job_manifest_path)
    ifp_path = (
        Path(args.ifp_report).resolve()
        if args.ifp_report
        else job_manifest_path.parent / "ifp" / "ifp_report.json"
    )
    ifp_report, contacts = verify_ifp_report(ifp_path, job=job)
    inputs = job["inputs"]
    receptor_pdbqt_manifest_path = Path(
        inputs["receptor_pdbqt"]["manifest"]["path"]
    )
    receptor_pdbqt_manifest = verify_pdbqt_manifest(
        receptor_pdbqt_manifest_path,
        pdbqt_path=Path(inputs["receptor_pdbqt"]["path"]),
        expected_receptor=inputs["receptor"],
        expected_mutation=inputs["mutation"],
    )
    receptor_pdb = Path(receptor_pdbqt_manifest["aligned_pdb"]["path"])
    environment_manifest_path = Path(inputs["environment"]["path"])
    environment = verify_environment_manifest(environment_manifest_path)
    environment_config = environment["configuration"]
    if (
        Path(environment_config["path"]).resolve() != config_path
        or environment_config["sha256"] != sha256_file(config_path)
    ):
        raise ValueError("geometry config 与 docking environment manifest 不同源")
    if (
        Path(ifp_report.get("configuration", {}).get("path", "")).resolve()
        != config_path
        or ifp_report.get("configuration", {}).get("sha256")
        != sha256_file(config_path)
    ):
        raise ValueError("IFP report 与 geometry config 不同源")
    run_manifest_path = Path(environment["frame_run"]["path"]).resolve()
    frame_run_root = run_manifest_path.parent
    run_manifest = verify_frame_run_manifest(
        run_manifest_path,
        verify_records=True,
    )
    if run_manifest["run_identity"] != environment["frame_run"]["run_identity"]:
        raise ValueError("geometry environment 与 frame run identity 不一致")
    run_config = run_manifest["inputs"]["config"]
    if (
        Path(run_config["path"]).resolve() != config_path
        or run_config["sha256"] != sha256_file(config_path)
    ):
        raise ValueError("geometry config 与 frame run 不同源")
    receptor_records = [
        *run_manifest["wt_records"],
        *run_manifest["records"],
    ]
    receptor_record = next(
        (
            record
            for record in receptor_records
            if record["receptor"] == inputs["receptor"]
            and record["mutation"] == inputs["mutation"]
        ),
        None,
    )
    if receptor_record is None:
        raise ValueError("job receptor 不属于当前 frame run")
    frame_record = receptor_pdbqt_manifest["frame_manifest"]
    if (
        receptor_record["frame_manifest_identity"]
        != frame_record["manifest_identity"]
        or Path(receptor_record["frame_manifest"]).resolve()
        != Path(frame_record["path"]).resolve()
    ):
        raise ValueError("job PDBQT frame manifest 与 frame run record 不一致")
    membrane_record = next(
        (
            record
            for record in run_manifest["membrane_frames"]
            if record["receptor"] == inputs["receptor"]
        ),
        None,
    )
    if membrane_record is None:
        raise ValueError("frame run 缺少 receptor membrane record")
    membrane_transform = Path(membrane_record["manifest"]).resolve()
    membrane_manifest = verify_membrane_transform_manifest(
        membrane_transform,
        expected_receptor=inputs["receptor"],
    )
    if (
        sha256_file(membrane_transform) != membrane_record["sha256"]
        or membrane_manifest["manifest_identity"]
        != membrane_record["manifest_identity"]
    ):
        raise ValueError("membrane transform 与 frame run record 不一致")
    thresholds = thresholds_for(
        config,
        receptor=inputs["receptor"],
        ligand=inputs["ligand"],
    )
    report = evaluate_pose_set(
        pose_pdbqt=Path(job["outputs"]["poses"]["path"]),
        receptor_pdb=receptor_pdb,
        membrane_transform_manifest=membrane_transform,
        box=inputs["box"],
        thresholds=thresholds,
        ifp_contact_by_model=contacts,
    )
    report["job"] = {
        "manifest_path": str(job_manifest_path),
        "manifest_sha256": sha256_file(job_manifest_path),
        "job_identity": job["job_identity"],
        "manifest_identity": job["manifest_identity"],
    }
    report["frame_run"] = {
        "path": str(run_manifest_path),
        "sha256": sha256_file(run_manifest_path),
        "run_identity": run_manifest["run_identity"],
    }
    report["environment"] = {
        "path": str(environment_manifest_path.resolve()),
        "sha256": sha256_file(environment_manifest_path),
        "manifest_identity": environment["manifest_identity"],
    }
    report["configuration"] = {
        "path": str(config_path),
        "sha256": sha256_file(config_path),
    }
    report["ifp_report"] = {
        "path": str(ifp_path),
        "sha256": sha256_file(ifp_path),
        "manifest_identity": ifp_report["manifest_identity"],
    }
    report["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(report)
    ).hexdigest()
    output = (
        Path(args.output).resolve()
        if args.output
        else job_manifest_path.parent / "geometry" / "geometry_report.json"
    )
    if output.exists():
        raise FileExistsError(f"拒绝覆盖既有 geometry report: {output}")
    write_canonical_json(output, report)
    print(output)


if __name__ == "__main__":
    main()
