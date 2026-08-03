"""Run one immutable four-job WT calibration replicate.

This entry point intentionally cannot run mutants or the 328-job production
matrix.  It reuses a verified frame-repair source run, changes only the
explicit Vina seed, and writes all outputs to a new calibration run root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from dock import (
    dock_pair_singlestage,
    get_box_center_offset,
    get_manual_box_center,
    get_receptor_box_size,
    get_tm_helix_ranges,
)
from docking_manifest import (
    build_job_identity,
    load_json,
    sha256_file,
    verify_environment_manifest,
    verify_frame_run_manifest,
    verify_job_manifest,
    write_job_manifest,
)
from frame_alignment import canonical_json_bytes, write_canonical_json
from run_frame_repair_docking import (
    _build_expected_job_inputs,
    _file_record,
    _resolve_box,
    _verify_config_binding,
)
from utils import load_config


WT_CALIBRATION_MATRIX = tuple(
    (receptor, "WT", ligand)
    for receptor in ("Gpr2", "Gpr3")
    for ligand in ("ascr18", "ascr3")
)


def build_wt_calibration_matrix() -> list[tuple[str, str, str]]:
    """Return the fixed four-arm WT-only calibration matrix."""
    return list(WT_CALIBRATION_MATRIX)


def validate_calibration_seed(seed: int, *, source_seed: int) -> int:
    if seed < 0:
        raise ValueError("Vina seed 必须为非负整数")
    if seed == source_seed:
        raise ValueError("WT calibration seed 必须不同于 source run seed")
    return seed


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_state_event(
    path: Path,
    *,
    state: str,
    source: str,
    detail: str,
) -> None:
    line = f"{_now()}\t{state}\t{source}\t{detail}\n"
    if path.exists():
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
    else:
        path.write_text(
            "observed_at\tstate\tsource\tdetail\n" + line,
            encoding="utf-8",
        )


def _write_terminal_snapshot(
    output_root: Path,
    *,
    state: str,
    detail: str,
) -> None:
    (output_root / "terminal_status.tsv").write_text(
        "observed_at\tstate\tsource\tdetail\n"
        f"{_now()}\t{state}\t"
        "run_frame_repair_wt_calibration.py\t"
        f"{detail}\n",
        encoding="utf-8",
    )


def _copy_review_inputs(
    *,
    source_frame_root: Path,
    output_root: Path,
) -> dict[str, dict[str, str]]:
    review_root = output_root / "review_inputs" / "receptors"
    review_root.mkdir(parents=True, exist_ok=False)
    records: dict[str, dict[str, str]] = {}
    for receptor in ("Gpr2", "Gpr3"):
        source = (
            source_frame_root
            / "aligned_receptors"
            / receptor
            / "WT"
            / "WT_tm.aligned.pdb"
        )
        destination = review_root / f"{receptor}_WT_tm.aligned.pdb"
        shutil.copy2(source, destination)
        records[receptor] = {
            "source_path": str(source),
            "source_sha256": sha256_file(source),
            "path": str(destination),
            "sha256": sha256_file(destination),
        }
    return records


def _build_plan(
    *,
    config: dict[str, Any],
    config_path: Path,
    source_frame_root: Path,
    output_root: Path,
    run_manifest_path: Path,
    run_manifest: dict[str, Any],
    environment_path: Path,
    environment: dict[str, Any],
    config_record: dict[str, str],
    seed: int,
    resolved_boxes: dict[str, dict[str, list[float]]],
    review_inputs: dict[str, dict[str, str]],
) -> dict[str, Any]:
    vina = environment["executables"]["vina"]
    singlestage = config["vina"]["singlestage"]
    plan: dict[str, Any] = {
        "schema": "docking-frame-repair-wt-calibration-plan-v1",
        "status": "compute_authorization_confirmed",
        "created_at_utc": _now(),
        "purpose": (
            "WT-only geometry calibration replicate; no mutant evidence may "
            "be used to freeze thresholds"
        ),
        "source_frame_run": {
            "root": str(source_frame_root),
            "manifest": _file_record(run_manifest_path),
            "run_identity": run_manifest["run_identity"],
        },
        "output_run_root": str(output_root),
        "runner": _file_record(Path(__file__).resolve()),
        "environment": {
            **_file_record(environment_path),
            "manifest_identity": environment["manifest_identity"],
        },
        "configuration": config_record,
        "vina_invocation": {
            "executable_path": vina["path"],
            "executable_sha256": vina["sha256"],
            "version": environment["observed_versions"]["vina_conda_package"],
            "package_build": environment["package_manager_identities"]["vina"][
                "build"
            ],
            "package_build_number": environment[
                "package_manager_identities"
            ]["vina"]["build_number"],
            "spacing": singlestage["spacing"],
            "exhaustiveness": singlestage["exhaustiveness"],
            "requested_max_modes": config["vina"]["num_modes"],
            "returned_mode_contract": (
                "1 <= actual_modes <= requested_max_modes"
            ),
            "minimum_returned_modes": 1,
            "energy_range": config["vina"]["energy_range"],
            "min_rmsd": config["vina"]["min_rmsd"],
            "max_evals": config["vina"]["max_evals"],
            "cpu": config["frame_repair"]["compute"]["cpu_per_job"],
            "seed": seed,
        },
        "boxes": resolved_boxes,
        "review_inputs": review_inputs,
        "jobs": [
            {"receptor": receptor, "mutation": subject, "ligand": ligand}
            for receptor, subject, ligand in build_wt_calibration_matrix()
        ],
    }
    plan["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(plan)
    ).hexdigest()
    return plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--source-frame-run-root", required=True)
    parser.add_argument("--output-run-root", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument(
        "--confirm-compute-authorization",
        action="store_true",
        help="必须由用户明确批准本次四任务 WT calibration 后提供",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.confirm_compute_authorization:
        raise PermissionError("未确认本次四任务 WT calibration 计算授权")

    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    source_frame_root = Path(args.source_frame_run_root).resolve()
    output_root = Path(args.output_run_root).resolve()
    if output_root.exists():
        raise FileExistsError(f"拒绝覆盖既有 calibration run: {output_root}")

    run_manifest_path = source_frame_root / "run_manifest.json"
    run_manifest = verify_frame_run_manifest(
        run_manifest_path,
        verify_records=True,
    )
    environment_path = source_frame_root / "environment_manifest.json"
    environment = verify_environment_manifest(
        environment_path,
        expected_frame_run_root=source_frame_root,
        require_production_ready=True,
    )
    config_record = _verify_config_binding(
        config_path=config_path,
        run_manifest_path=run_manifest_path,
        run_manifest=run_manifest,
        environment=environment,
    )
    seed = validate_calibration_seed(
        args.seed,
        source_seed=int(config["vina"]["seed"]),
    )
    requested_max_modes = int(
        config["frame_repair"]["requested_max_modes_per_job"]
    )
    if requested_max_modes != int(config["vina"]["num_modes"]):
        raise ValueError("frame repair 与 Vina requested maximum 不一致")
    expected_compute = {
        "cpu_per_job": int(
            config["frame_repair"]["compute"]["cpu_per_job"]
        ),
        "requested_max_modes": requested_max_modes,
        "energy_range": float(config["vina"]["energy_range"]),
        "min_rmsd": float(config["vina"]["min_rmsd"]),
        "max_evals": int(config["vina"]["max_evals"]),
    }
    if environment.get("compute_contract") != expected_compute:
        raise ValueError("environment compute contract 与 config 不一致")

    output_root.mkdir(parents=True, exist_ok=False)
    state_events = output_root / "run_state_events.tsv"
    _write_state_event(
        state_events,
        state="RUNNING_VERIFIED",
        source="run_frame_repair_wt_calibration.py",
        detail="four-job WT-only calibration started",
    )
    _write_terminal_snapshot(
        output_root,
        state="RUNNING_VERIFIED",
        detail="four-job WT-only calibration started",
    )

    try:
        resolved_boxes: dict[str, dict[str, list[float]]] = {}
        for receptor in ("Gpr2", "Gpr3"):
            wt_tm = (
                source_frame_root
                / "aligned_receptors"
                / receptor
                / "WT"
                / "WT_tm.aligned.pdb"
            )
            resolved_boxes[receptor] = _resolve_box(
                config,
                receptor=receptor,
                wt_tm_pdb=wt_tm,
            )
        review_inputs = _copy_review_inputs(
            source_frame_root=source_frame_root,
            output_root=output_root,
        )
        plan = _build_plan(
            config=config,
            config_path=config_path,
            source_frame_root=source_frame_root,
            output_root=output_root,
            run_manifest_path=run_manifest_path,
            run_manifest=run_manifest,
            environment_path=environment_path,
            environment=environment,
            config_record=config_record,
            seed=seed,
            resolved_boxes=resolved_boxes,
            review_inputs=review_inputs,
        )
        plan_path = output_root / "docking" / "wt_calibration_job_plan.json"
        write_canonical_json(plan_path, plan)

        completed: list[dict[str, Any]] = []
        vina = environment["executables"]["vina"]
        for receptor, subject, ligand in build_wt_calibration_matrix():
            job_root = (
                output_root
                / "docking"
                / "jobs"
                / receptor
                / subject
                / ligand
            )
            attempts_dir = job_root / "attempts"
            attempt_dir = attempts_dir / "attempt-001"
            attempt_dir.mkdir(parents=True, exist_ok=False)
            (
                expected_inputs,
                receptor_pdbqt,
                _receptor_manifest,
                ligand_pdbqt,
            ) = _build_expected_job_inputs(
                config=config,
                config_path=config_path,
                frame_run_root=source_frame_root,
                environment_path=environment_path,
                environment=environment,
                resolved_box=resolved_boxes[receptor],
                receptor=receptor,
                subject=subject,
                ligand=ligand,
            )
            expected_inputs["seed"] = seed
            pair_name = f"{receptor}_{subject}_{ligand}"
            result = dock_pair_singlestage(
                receptor_pdbqt=receptor_pdbqt,
                ligand_pdbqt=ligand_pdbqt,
                pair_name=pair_name,
                tm_pdb=(
                    source_frame_root
                    / "aligned_receptors"
                    / receptor
                    / "WT"
                    / "WT_tm.aligned.pdb"
                ),
                output_dir=attempt_dir,
                config=config,
                seed=seed,
                tm_helix_ranges=get_tm_helix_ranges(config, receptor),
                box_center_offset=get_box_center_offset(config, receptor),
                receptor_box_size=get_receptor_box_size(config, receptor),
                manual_box_center=get_manual_box_center(config, receptor),
                vina_bin_override=vina["path"],
            )
            if result.stage1_box != resolved_boxes[receptor]:
                raise ValueError(f"{pair_name}: runtime box 与 frozen box 不一致")
            if (
                result.spacing != expected_inputs["vina"]["spacing"]
                or result.exhaustiveness
                != expected_inputs["vina"]["exhaustiveness"]
            ):
                raise ValueError(
                    f"{pair_name}: runtime Vina 参数与 frozen contract 不一致"
                )
            poses_path = Path(result.poses_path)
            command_path = (
                attempt_dir / f"{poses_path.stem}.vina.command.json"
            )
            command = load_json(command_path)
            attempt = {
                "attempt_number": 1,
                "run_mode": "wt_calibration",
                "returncode": command["returncode"],
                "elapsed_sec": command["elapsed_sec"],
                "command": _file_record(command_path),
                "stdout": _file_record(
                    attempt_dir / f"{poses_path.stem}.vina.stdout.txt"
                ),
                "stderr": _file_record(
                    attempt_dir / f"{poses_path.stem}.vina.stderr.txt"
                ),
            }
            candidate_manifest = (
                attempt_dir / "candidate_job_manifest.json"
            )
            write_job_manifest(
                candidate_manifest,
                inputs=expected_inputs,
                pose_path=poses_path,
                requested_max_modes=requested_max_modes,
                minimum_returned_modes=1,
                attempt=attempt,
            )
            job = verify_job_manifest(
                candidate_manifest,
                expected_receptor=receptor,
                expected_mutation="WT",
                expected_ligand=ligand,
                requested_max_modes=requested_max_modes,
            )
            if job["job_identity"] != build_job_identity(expected_inputs):
                raise ValueError(f"{pair_name}: job identity mismatch")
            job_manifest_path = job_root / "job_manifest.json"
            candidate_manifest.replace(job_manifest_path)
            job = verify_job_manifest(
                job_manifest_path,
                expected_receptor=receptor,
                expected_mutation="WT",
                expected_ligand=ligand,
                requested_max_modes=requested_max_modes,
            )
            actual_modes = int(job["outputs"]["poses"]["model_count"])
            if not 1 <= actual_modes <= requested_max_modes:
                raise ValueError(
                    f"{pair_name}: actual_modes={actual_modes} 超出 1–"
                    f"{requested_max_modes}"
                )
            write_canonical_json(
                attempt_dir / "attempt_status.json",
                {
                    "status": "technical_complete",
                    "attempt_number": 1,
                    "job_identity": job["job_identity"],
                    "job_manifest": str(job_manifest_path),
                    "job_manifest_sha256": sha256_file(job_manifest_path),
                    "job_manifest_identity": job["manifest_identity"],
                    "actual_modes": actual_modes,
                    "requested_max_modes": requested_max_modes,
                    "returned_mode_contract": (
                        "1 <= actual_modes <= requested_max_modes"
                    ),
                },
            )
            completed.append(
                {
                    "receptor": receptor,
                    "mutation": "WT",
                    "ligand": ligand,
                    "job_identity": job["job_identity"],
                    "manifest": str(job_manifest_path),
                    "manifest_sha256": sha256_file(job_manifest_path),
                    "manifest_identity": job["manifest_identity"],
                    "actual_modes": actual_modes,
                    "requested_max_modes": requested_max_modes,
                }
            )

        if len(completed) != len(WT_CALIBRATION_MATRIX):
            raise ValueError("WT calibration technical completion count mismatch")
        completion: dict[str, Any] = {
            "schema": "docking-frame-repair-wt-calibration-completion-v1",
            "status": "technical_matrix_complete_ifp_geometry_pending",
            "completed_at_utc": _now(),
            "job_count": len(completed),
            "seed": seed,
            "returned_mode_contract": (
                "1 <= actual_modes <= requested_max_modes"
            ),
            "source_frame_run": plan["source_frame_run"],
            "environment": plan["environment"],
            "configuration": config_record,
            "job_plan": {
                **_file_record(plan_path),
                "manifest_identity": plan["manifest_identity"],
            },
            "jobs": completed,
        }
        completion["manifest_identity"] = hashlib.sha256(
            canonical_json_bytes(completion)
        ).hexdigest()
        completion_path = (
            output_root
            / "docking"
            / "wt_calibration_technical_completion.json"
        )
        write_canonical_json(completion_path, completion)
        _write_state_event(
            state_events,
            state="TERMINAL_NORMAL",
            source="run_frame_repair_wt_calibration.py",
            detail="four-job WT-only docking technical matrix complete",
        )
        _write_terminal_snapshot(
            output_root,
            state="TERMINAL_NORMAL",
            detail="four-job WT-only docking technical matrix complete",
        )
        print(
            json.dumps(
                {
                    "completed": len(completed),
                    "seed": seed,
                    "actual_modes": [
                        item["actual_modes"] for item in completed
                    ],
                },
                ensure_ascii=False,
            )
        )
    except Exception as exc:
        _write_state_event(
            state_events,
            state="TERMINAL_ABNORMAL",
            source="run_frame_repair_wt_calibration.py",
            detail=f"{type(exc).__name__}: {exc}",
        )
        _write_terminal_snapshot(
            output_root,
            state="TERMINAL_ABNORMAL",
            detail=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    main()
