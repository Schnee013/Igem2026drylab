"""Aggregate verified jobs into smoke evidence or a 162-mutant terminal matrix."""

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
)
from evaluate_frame_repair_geometry import verify_ifp_report
from frame_alignment import canonical_json_bytes, write_canonical_json
from run_frame_repair_docking import build_subject_matrix
from utils import load_config


ALLOWED_PROVENANCE = {
    "canonical_wt_coordinate",
    "af3_request_and_coordinate",
    "local_af3_coordinate_only",
}


def verify_geometry_report(
    path: Path,
    *,
    job: dict[str, Any],
) -> dict[str, Any]:
    report = load_json(path)
    if report.get("schema") != "docking-geometry-report-v2":
        raise ValueError("未知 geometry report schema")
    payload = dict(report)
    expected_identity = payload.pop("manifest_identity", None)
    actual_identity = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    if not expected_identity or actual_identity != expected_identity:
        raise ValueError("geometry report content identity mismatch")
    if report.get("job", {}).get("job_identity") != job["job_identity"]:
        raise ValueError("geometry report 绑定到不同 job")
    if report.get("pose_file", {}).get("sha256") != job["outputs"]["poses"]["sha256"]:
        raise ValueError("geometry report pose file 与 job 不同源")
    job_models = {
        item["model_number"]: item for item in job["outputs"]["poses"]["models"]
    }
    if len(report.get("poses", [])) != len(job_models):
        raise ValueError("geometry report MODEL 数量不完整")
    for model in report["poses"]:
        source = job_models.get(model["model"])
        if source is None or source["body_sha256"] != model["pose_body_sha256"]:
            raise ValueError("geometry report MODEL body 与 job 不同源")
        if source["affinity"] != model["affinity"]:
            raise ValueError("geometry report affinity 与 pose body 不同源")
    if (
        bool(report.get("model1_pass"))
        != bool(report["poses"][0]["pass"])
        or int(report.get("passing_mode_count", -1))
        != sum(bool(model["pass"]) for model in report["poses"])
        or bool(report.get("pass"))
        != (
            bool(report.get("model1_pass"))
            and bool(report.get("distribution_pass"))
        )
    ):
        raise ValueError("geometry report 聚合 gate 与逐 MODEL 结果不一致")
    return report


def collect_job(
    *,
    frame_run_root: Path,
    receptor: str,
    mutation: str,
    ligand: str,
    requested_max_modes: int,
    expected_environment_identity: str,
    expected_config_sha256: str,
    expected_run_identity: str,
) -> dict[str, Any]:
    job_root = (
        frame_run_root / "docking" / "jobs" / receptor / mutation / ligand
    )
    job_manifest_path = job_root / "job_manifest.json"
    job = verify_job_manifest(
        job_manifest_path,
        expected_receptor=receptor,
        expected_mutation=mutation,
        expected_ligand=ligand,
        requested_max_modes=requested_max_modes,
    )
    ifp_path = job_root / "ifp" / "ifp_report.json"
    ifp, _ = verify_ifp_report(ifp_path, job=job)
    geometry_path = job_root / "geometry" / "geometry_report.json"
    geometry = verify_geometry_report(geometry_path, job=job)
    if (
        job["inputs"]["environment"]["manifest_identity"]
        != expected_environment_identity
        or ifp.get("configuration", {}).get("sha256")
        != expected_config_sha256
        or geometry.get("configuration", {}).get("sha256")
        != expected_config_sha256
        or geometry.get("environment", {}).get("manifest_identity")
        != expected_environment_identity
        or geometry.get("frame_run", {}).get("run_identity")
        != expected_run_identity
    ):
        raise ValueError(
            f"{receptor}/{mutation}/{ligand}: "
            "job/IFP/geometry 与当前 run/config/environment 不同源"
        )
    receptor_manifest = load_json(
        Path(job["inputs"]["receptor_pdbqt"]["manifest"]["path"])
    )
    frame_manifest = load_json(
        Path(receptor_manifest["frame_manifest"]["path"])
    )
    provenance = frame_manifest.get("provenance_status")
    if provenance not in ALLOWED_PROVENANCE:
        raise ValueError(
            f"{receptor}/{mutation}: 未裁决 provenance status {provenance}"
        )
    return {
        "receptor": receptor,
        "mutation": mutation,
        "ligand": ligand,
        "job_identity": job["job_identity"],
        "job_manifest_identity": job["manifest_identity"],
        "job_manifest": str(job_manifest_path),
        "pose_sha256": job["outputs"]["poses"]["sha256"],
        "pose_model_count": job["outputs"]["poses"]["model_count"],
        "model1_affinity": job["outputs"]["score"]["model1_affinity"],
        "ifp_report": str(ifp_path),
        "ifp_manifest_identity": ifp["manifest_identity"],
        "ifp_complete": (
            len(ifp["models"]) == job["outputs"]["poses"]["model_count"]
        ),
        "geometry_report": str(geometry_path),
        "geometry_manifest_identity": geometry["manifest_identity"],
        "geometry_pass": bool(geometry["pass"]),
        "model1_geometry_pass": bool(geometry["model1_pass"]),
        "passing_mode_count": int(geometry["passing_mode_count"]),
        "provenance_status": provenance,
        "provenance_gap": provenance == "local_af3_coordinate_only",
        "provenance_pass": True,
        "technical_pose_pass": (
            1
            <= job["outputs"]["poses"]["model_count"]
            <= requested_max_modes
        ),
        "pose_population_pass": bool(
            job["outputs"]["pose_population"]["comparable"]
        ),
        "contract": {
            "box": job["inputs"]["box"],
            "ligand_pdbqt": job["inputs"]["ligand_pdbqt"],
            "vina": job["inputs"]["vina"],
            "seed": job["inputs"]["seed"],
            "environment": job["inputs"]["environment"],
        },
    }


def verify_comparable_job_contracts(
    jobs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Require WT/mutant jobs to share one immutable search contract."""
    by_key = {
        (job["receptor"], job["mutation"], job["ligand"]): job for job in jobs
    }
    if len(by_key) != len(jobs):
        raise ValueError("job contract audit contains duplicate identities")
    for receptor in ("Gpr2", "Gpr3"):
        for ligand in ("ascr18", "ascr3"):
            if (receptor, "WT", ligand) not in by_key:
                raise ValueError(f"job contract audit 缺少 WT: {receptor}/{ligand}")

    environments = {
        job["contract"]["environment"]["manifest_identity"] for job in jobs
    }
    vina_contracts = {
        canonical_json_bytes(job["contract"]["vina"]) for job in jobs
    }
    seeds = {job["contract"]["seed"] for job in jobs}
    if len(environments) != 1 or len(vina_contracts) != 1 or len(seeds) != 1:
        raise ValueError("job matrix 的 environment/Vina/seed 不统一")

    receptor_boxes: dict[str, dict[str, Any]] = {}
    for receptor in ("Gpr2", "Gpr3"):
        boxes = {
            canonical_json_bytes(job["contract"]["box"])
            for job in jobs
            if job["receptor"] == receptor
        }
        if len(boxes) != 1:
            raise ValueError(f"{receptor}: WT/mutant search volume 不一致")
        receptor_boxes[receptor] = next(
            job["contract"]["box"]
            for job in jobs
            if job["receptor"] == receptor
        )

    ligand_records: dict[str, dict[str, Any]] = {}
    for ligand in ("ascr18", "ascr3"):
        records = {
            canonical_json_bytes(job["contract"]["ligand_pdbqt"])
            for job in jobs
            if job["ligand"] == ligand
        }
        if len(records) != 1:
            raise ValueError(f"{ligand}: job matrix 使用了不同 ligand input")
        ligand_records[ligand] = next(
            job["contract"]["ligand_pdbqt"]
            for job in jobs
            if job["ligand"] == ligand
        )

    for job in jobs:
        wt = by_key[(job["receptor"], "WT", job["ligand"])]
        for field in ("box", "ligand_pdbqt", "vina", "seed", "environment"):
            if job["contract"][field] != wt["contract"][field]:
                raise ValueError(
                    f"{job['receptor']}/{job['mutation']}/{job['ligand']}: "
                    f"与 WT 的 {field} 合同不一致"
                )
    return {
        "status": "pass",
        "environment_manifest_identity": next(iter(environments)),
        "vina": jobs[0]["contract"]["vina"],
        "seed": jobs[0]["contract"]["seed"],
        "receptor_boxes": receptor_boxes,
        "ligand_inputs": ligand_records,
    }


def verify_smoke_terminal_manifest(
    path: Path,
    *,
    frame_run_root: Path,
    requested_max_modes: int,
    expected_environment_identity: str,
    expected_config_sha256: str,
    expected_run_identity: str,
) -> dict[str, Any]:
    payload = load_json(path)
    if (
        payload.get("schema") != "docking-frame-repair-smoke-terminal-v2"
        or payload.get("status") != "pass"
        or payload.get("job_count") != 8
    ):
        raise ValueError("full run requires a passing 8-job smoke terminal")
    body = dict(payload)
    expected_identity = body.pop("manifest_identity", None)
    if (
        not expected_identity
        or hashlib.sha256(canonical_json_bytes(body)).hexdigest()
        != expected_identity
    ):
        raise ValueError("smoke terminal content identity mismatch")
    if (
        payload.get("frame_run", {}).get("run_identity")
        != expected_run_identity
        or payload.get("environment", {}).get("manifest_identity")
        != expected_environment_identity
        or payload.get("configuration", {}).get("sha256")
        != expected_config_sha256
    ):
        raise ValueError("smoke terminal 与当前 run/config/environment 不同源")
    expected_keys = set(
        build_subject_matrix(
            verify_frame_run_manifest(
                Path(frame_run_root) / "run_manifest.json",
                verify_records=False,
            ),
            run_mode="smoke",
        )
    )
    actual_keys = {
        (job.get("receptor"), job.get("mutation"), job.get("ligand"))
        for job in payload.get("jobs", [])
    }
    if actual_keys != expected_keys:
        raise ValueError("smoke terminal job matrix mismatch")
    current_jobs: list[dict[str, Any]] = []
    for recorded in payload["jobs"]:
        if not all(
            bool(recorded.get(field))
            for field in (
                "geometry_pass",
                "model1_geometry_pass",
                "ifp_complete",
                "provenance_pass",
                "technical_pose_pass",
                "pose_population_pass",
            )
        ):
            raise ValueError("smoke terminal contains a failed gate")
        current = collect_job(
            frame_run_root=Path(frame_run_root),
            receptor=recorded["receptor"],
            mutation=recorded["mutation"],
            ligand=recorded["ligand"],
            requested_max_modes=requested_max_modes,
            expected_environment_identity=expected_environment_identity,
            expected_config_sha256=expected_config_sha256,
            expected_run_identity=expected_run_identity,
        )
        current_jobs.append(current)
        for field in (
            "job_identity",
            "job_manifest_identity",
            "pose_sha256",
            "ifp_manifest_identity",
            "geometry_manifest_identity",
        ):
            if current[field] != recorded.get(field):
                raise ValueError(f"smoke terminal evidence drift: {field}")
    current_contract = verify_comparable_job_contracts(current_jobs)
    if payload.get("contract_audit") != current_contract:
        raise ValueError("smoke terminal comparable-search contract drift")
    return payload


def build_terminal_rows(
    run_manifest: dict[str, Any],
    jobs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_key = {
        (job["receptor"], job["mutation"], job["ligand"]): job for job in jobs
    }
    if len(by_key) != len(jobs):
        raise ValueError("terminal jobs contain duplicate identities")
    wt_scores = {
        (receptor, ligand): by_key[(receptor, "WT", ligand)][
            "model1_affinity"
        ]
        for receptor in ("Gpr2", "Gpr3")
        for ligand in ("ascr18", "ascr3")
    }
    terminal_rows: list[dict[str, Any]] = []
    for record in run_manifest["records"]:
        receptor = record["receptor"]
        mutation = record["mutation"]
        ascr18 = by_key[(receptor, mutation, "ascr18")]
        ascr3 = by_key[(receptor, mutation, "ascr3")]
        if ascr18["provenance_status"] != ascr3["provenance_status"]:
            raise ValueError(
                f"{receptor}/{mutation}: 双配体 provenance status 不一致"
            )
        dg18 = float(ascr18["model1_affinity"])
        dg3 = float(ascr3["model1_affinity"])
        geometry_pass = ascr18["geometry_pass"] and ascr3["geometry_pass"]
        model1_geometry_pass = (
            ascr18["model1_geometry_pass"]
            and ascr3["model1_geometry_pass"]
        )
        ifp_pass = ascr18["ifp_complete"] and ascr3["ifp_complete"]
        provenance_pass = (
            ascr18["provenance_pass"] and ascr3["provenance_pass"]
        )
        technical_pose_pass = (
            ascr18["technical_pose_pass"]
            and ascr3["technical_pose_pass"]
        )
        pose_population_pass = (
            ascr18["pose_population_pass"]
            and ascr3["pose_population_pass"]
        )
        eligible = (
            geometry_pass
            and model1_geometry_pass
            and ifp_pass
            and provenance_pass
            and technical_pose_pass
            and pose_population_pass
        )
        row = {
            "receptor": receptor,
            "mutation": mutation,
            "dg_ascr18": dg18,
            "dg_ascr3": dg3,
            "dg_wt_ascr18": wt_scores[(receptor, "ascr18")],
            "dg_wt_ascr3": wt_scores[(receptor, "ascr3")],
            "sel_mut": dg18 - dg3,
            "job_ascr18_identity": ascr18["job_identity"],
            "job_ascr3_identity": ascr3["job_identity"],
            "pose_ascr18_sha256": ascr18["pose_sha256"],
            "pose_ascr3_sha256": ascr3["pose_sha256"],
            "geometry_pass": geometry_pass,
            "model1_geometry_pass": model1_geometry_pass,
            "ifp_pass": ifp_pass,
            "provenance_pass": provenance_pass,
            "technical_pose_pass": technical_pose_pass,
            "pose_population_pass": pose_population_pass,
            "provenance_status": ascr18["provenance_status"],
            "provenance_gap": (
                ascr18["provenance_gap"] or ascr3["provenance_gap"]
            ),
            "terminal_status": (
                "eligible" if eligible else "non_comparable_gate_failure"
            ),
            "evidence": {"ascr18": ascr18, "ascr3": ascr3},
        }
        terminal_rows.append(row)
    terminal_rows.sort(key=lambda row: (row["receptor"], row["mutation"]))
    expected_counts = {"Gpr2": 46, "Gpr3": 116}
    actual_counts = {
        receptor: sum(row["receptor"] == receptor for row in terminal_rows)
        for receptor in expected_counts
    }
    if len(terminal_rows) != 162 or actual_counts != expected_counts:
        raise ValueError(f"162-mutant terminal matrix mismatch: {actual_counts}")
    return terminal_rows


def verify_technical_completion(
    path: Path,
    *,
    mode: str,
    jobs: list[dict[str, Any]],
    expected_run_identity: str,
    expected_environment_identity: str,
    expected_config_sha256: str,
) -> dict[str, Any]:
    payload = load_json(path)
    if (
        payload.get("schema") != "docking-frame-repair-run-completion-v2"
        or payload.get("status")
        != "technical_matrix_complete_geometry_ifp_pending"
        or payload.get("run_mode") != mode
        or payload.get("job_count") != len(jobs)
    ):
        raise ValueError("technical completion 状态或范围不匹配")
    body = dict(payload)
    expected_identity = body.pop("manifest_identity", None)
    if (
        not expected_identity
        or hashlib.sha256(canonical_json_bytes(body)).hexdigest()
        != expected_identity
    ):
        raise ValueError("technical completion content identity mismatch")
    if (
        payload.get("frame_run", {}).get("run_identity")
        != expected_run_identity
        or payload.get("environment", {}).get("manifest_identity")
        != expected_environment_identity
        or payload.get("configuration", {}).get("sha256")
        != expected_config_sha256
    ):
        raise ValueError("technical completion 与当前 run/config/environment 不同源")
    current = {
        (job["receptor"], job["mutation"], job["ligand"]): job for job in jobs
    }
    recorded = {
        (job["receptor"], job["mutation"], job["ligand"]): job
        for job in payload.get("jobs", [])
    }
    if set(current) != set(recorded):
        raise ValueError("technical completion job matrix drift")
    for key, job in current.items():
        entry = recorded[key]
        if (
            entry.get("job_identity") != job["job_identity"]
            or entry.get("manifest_identity") != job["job_manifest_identity"]
            or entry.get("manifest_sha256")
            != sha256_file(Path(job["job_manifest"]))
        ):
            raise ValueError("technical completion job evidence drift")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--frame-run-root", required=True)
    parser.add_argument("--mode", choices=("smoke", "full"), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    frame_run_root = Path(args.frame_run_root).resolve()
    run_manifest_path = frame_run_root / "run_manifest.json"
    run_manifest = verify_frame_run_manifest(
        run_manifest_path, verify_records=True
    )
    environment_path = frame_run_root / "environment_manifest.json"
    environment = verify_environment_manifest(
        environment_path,
        expected_frame_run_root=frame_run_root,
        require_production_ready=True,
    )
    config_sha256 = sha256_file(config_path)
    if (
        Path(run_manifest["inputs"]["config"]["path"]).resolve() != config_path
        or run_manifest["inputs"]["config"]["sha256"] != config_sha256
        or Path(environment["configuration"]["path"]).resolve() != config_path
        or environment["configuration"]["sha256"] != config_sha256
    ):
        raise ValueError("terminal aggregation config/run/environment 不同源")
    matrix = build_subject_matrix(run_manifest, run_mode=args.mode)
    requested_max_modes = config["frame_repair"][
        "requested_max_modes_per_job"
    ]
    output_root = frame_run_root / "terminal"
    if args.mode == "smoke":
        outputs = (output_root / "smoke_terminal.json",)
    else:
        outputs = (
            output_root / "terminal_matrix_162.json",
            output_root / "terminal_jobs_328.json",
            output_root / "terminal_manifest.json",
        )
        verify_smoke_terminal_manifest(
            output_root / "smoke_terminal.json",
            frame_run_root=frame_run_root,
            requested_max_modes=requested_max_modes,
            expected_environment_identity=environment["manifest_identity"],
            expected_config_sha256=config_sha256,
            expected_run_identity=run_manifest["run_identity"],
        )
    for output in outputs:
        if output.exists():
            raise FileExistsError(f"拒绝覆盖 terminal output: {output}")

    jobs = [
        collect_job(
            frame_run_root=frame_run_root,
            receptor=receptor,
            mutation=mutation,
            ligand=ligand,
            requested_max_modes=requested_max_modes,
            expected_environment_identity=environment["manifest_identity"],
            expected_config_sha256=config_sha256,
            expected_run_identity=run_manifest["run_identity"],
        )
        for receptor, mutation, ligand in matrix
    ]
    expected_jobs = 8 if args.mode == "smoke" else 328
    if len(jobs) != expected_jobs:
        raise ValueError("terminal job matrix incomplete")
    contract_audit = verify_comparable_job_contracts(jobs)
    technical_completion_path = (
        frame_run_root
        / "docking"
        / f"{args.mode}_technical_completion.json"
    )
    technical_completion = verify_technical_completion(
        technical_completion_path,
        mode=args.mode,
        jobs=jobs,
        expected_run_identity=run_manifest["run_identity"],
        expected_environment_identity=environment["manifest_identity"],
        expected_config_sha256=config_sha256,
    )

    common_provenance = {
        "frame_run": {
            "path": str(run_manifest_path),
            "sha256": sha256_file(run_manifest_path),
            "run_identity": run_manifest["run_identity"],
        },
        "environment": {
            "path": str(environment_path),
            "sha256": sha256_file(environment_path),
            "manifest_identity": environment["manifest_identity"],
        },
        "configuration": {
            "path": str(config_path),
            "sha256": config_sha256,
        },
        "technical_completion": {
            "path": str(technical_completion_path),
            "sha256": sha256_file(technical_completion_path),
            "manifest_identity": technical_completion["manifest_identity"],
        },
        "contract_audit": contract_audit,
    }
    if args.mode == "smoke":
        smoke_pass = all(
            job["geometry_pass"]
            and job["model1_geometry_pass"]
            and job["ifp_complete"]
            and job["provenance_pass"]
            and job["technical_pose_pass"]
            and job["pose_population_pass"]
            for job in jobs
        )
        payload: dict[str, Any] = {
            "schema": "docking-frame-repair-smoke-terminal-v2",
            "status": "pass" if smoke_pass else "fail_stop_before_full",
            "job_count": len(jobs),
            **common_provenance,
            "jobs": jobs,
        }
        payload["manifest_identity"] = hashlib.sha256(
            canonical_json_bytes(payload)
        ).hexdigest()
        output = outputs[0]
        write_canonical_json(output, payload)
        if not smoke_pass:
            raise RuntimeError("smoke gate failed; full run is forbidden")
        print(output)
        return

    terminal_rows = build_terminal_rows(run_manifest, jobs)
    expected_counts = {"Gpr2": 46, "Gpr3": 116}
    actual_counts = {
        receptor: sum(row["receptor"] == receptor for row in terminal_rows)
        for receptor in expected_counts
    }

    matrix_path, jobs_path, manifest_path = outputs
    write_canonical_json(matrix_path, terminal_rows)
    write_canonical_json(jobs_path, jobs)
    manifest: dict[str, Any] = {
        "schema": "docking-frame-repair-terminal-matrix-v1",
        "status": "complete",
        **common_provenance,
        "smoke_terminal": {
            "path": str(output_root / "smoke_terminal.json"),
            "sha256": sha256_file(output_root / "smoke_terminal.json"),
            "manifest_identity": load_json(
                output_root / "smoke_terminal.json"
            )["manifest_identity"],
        },
        "scope": {
            "job_count": len(jobs),
            "mutant_count": len(terminal_rows),
            "mutant_counts": actual_counts,
            "pose_model_count": sum(
                job["pose_model_count"] for job in jobs
            ),
            "receptors": ["Gpr2", "Gpr3"],
            "ligands": ["ascr18", "ascr3"],
        },
        "outputs": {
            "terminal_matrix": {
                "path": str(matrix_path),
                "sha256": sha256_file(matrix_path),
            },
            "terminal_jobs": {
                "path": str(jobs_path),
                "sha256": sha256_file(jobs_path),
            },
        },
    }
    manifest["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(manifest)
    ).hexdigest()
    write_canonical_json(manifest_path, manifest)
    print(manifest_path)


if __name__ == "__main__":
    main()
