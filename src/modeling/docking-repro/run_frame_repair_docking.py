"""Run the gated WT/mutant docking matrix from one frame-repair run root."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar

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
    verify_pdbqt_manifest,
    write_job_manifest,
)
from frame_alignment import canonical_json_bytes, write_canonical_json
from grid_box import GridBox, compute_box_center_of_mass
from utils import load_config


SMOKE_SUBJECTS = {
    "Gpr2": ("WT", "R59C"),
    "Gpr3": ("WT", "R167Y"),
}
_T = TypeVar("_T")
_R = TypeVar("_R")


class DockingJobFailure(RuntimeError):
    """Preserve one failed job's immutable attempt evidence for aggregation."""

    def __init__(self, record: dict[str, Any]) -> None:
        self.record = record
        super().__init__(
            f"{record['receptor']}/{record['mutation']}/{record['ligand']} "
            f"attempt-{record['attempt_number']:03d}: {record['error']}"
        )


def _resolve_box(
    config: dict[str, Any],
    *,
    receptor: str,
    wt_tm_pdb: Path,
) -> dict[str, list[float]]:
    default_size = float(config["vina"]["singlestage"]["box_size"])
    box_size = get_receptor_box_size(config, receptor) or default_size
    manual = get_manual_box_center(config, receptor)
    if manual is not None:
        box = GridBox(
            center_x=manual[0],
            center_y=manual[1],
            center_z=manual[2],
            size_x=box_size,
            size_y=box_size,
            size_z=box_size,
        )
    else:
        box = compute_box_center_of_mass(
            wt_tm_pdb,
            box_size=box_size,
            tm_helix_ranges=get_tm_helix_ranges(config, receptor),
        )
        offset = get_box_center_offset(config, receptor)
        box = GridBox(
            center_x=box.center_x + offset[0],
            center_y=box.center_y + offset[1],
            center_z=box.center_z + offset[2],
            size_x=box.size_x,
            size_y=box.size_y,
            size_z=box.size_z,
        )
    return {
        "center": [box.center_x, box.center_y, box.center_z],
        "size": [box.size_x, box.size_y, box.size_z],
    }


def build_subject_matrix(
    run_manifest: dict[str, Any],
    *,
    run_mode: str,
) -> list[tuple[str, str, str]]:
    ligands = ("ascr18", "ascr3")
    if run_mode == "smoke":
        return [
            (receptor, subject, ligand)
            for receptor in ("Gpr2", "Gpr3")
            for subject in SMOKE_SUBJECTS[receptor]
            for ligand in ligands
        ]
    if run_mode != "full":
        raise ValueError(f"未知 run mode: {run_mode}")
    subjects: dict[str, list[str]] = {"Gpr2": ["WT"], "Gpr3": ["WT"]}
    for record in run_manifest.get("records", []):
        receptor = record["receptor"]
        if receptor not in subjects:
            raise ValueError(f"full matrix 包含禁止 receptor: {receptor}")
        subjects[receptor].append(record["mutation"])
    matrix = [
        (receptor, subject, ligand)
        for receptor in ("Gpr2", "Gpr3")
        for subject in sorted(subjects[receptor], key=lambda value: (value != "WT", value))
        for ligand in ligands
    ]
    if len(matrix) != 328:
        raise ValueError(f"full docking matrix 必须为 328 jobs，实际 {len(matrix)}")
    return matrix


def should_continue_after_technical_failure(
    *,
    run_mode: str,
    continue_smoke_after_technical_failure: bool,
) -> bool:
    if continue_smoke_after_technical_failure and run_mode != "smoke":
        raise ValueError(
            "--continue-smoke-after-technical-failure 仅允许用于 smoke"
        )
    return continue_smoke_after_technical_failure


def validate_max_new_smoke_attempts(
    *,
    run_mode: str,
    max_new_smoke_attempts: int | None,
) -> int | None:
    if max_new_smoke_attempts is None:
        return None
    if run_mode != "smoke":
        raise ValueError("--max-new-smoke-attempts 仅允许用于 smoke")
    if max_new_smoke_attempts < 1:
        raise ValueError("--max-new-smoke-attempts 必须为正整数")
    return max_new_smoke_attempts


def validate_max_parallel_jobs(
    *,
    run_mode: str,
    max_parallel_jobs: int,
    cpu_per_job: int,
) -> int:
    if max_parallel_jobs < 1:
        raise ValueError("--max-parallel-jobs 必须为正整数")
    if run_mode == "smoke" and max_parallel_jobs != 1:
        raise ValueError("smoke 必须保持单 job 顺序执行")
    if max_parallel_jobs * cpu_per_job > 128:
        raise ValueError(
            "并发 docking 超过 E2 单人 128-thread 硬上限: "
            f"{max_parallel_jobs} jobs × {cpu_per_job} CPU"
        )
    return max_parallel_jobs


def run_bounded_fail_fast(
    items: list[_T],
    worker: Callable[[_T], _R],
    *,
    max_workers: int,
) -> list[_R]:
    """Run at most ``max_workers`` jobs and stop scheduling after a failure."""
    if max_workers < 1:
        raise ValueError("max_workers must be positive")
    if max_workers == 1:
        return [worker(item) for item in items]

    results: list[_R | None] = [None] * len(items)
    indexed = iter(enumerate(items))
    executor = ThreadPoolExecutor(max_workers=max_workers)
    pending: dict[Future[_R], int] = {}

    def submit_next() -> bool:
        try:
            index, item = next(indexed)
        except StopIteration:
            return False
        pending[executor.submit(worker, item)] = index
        return True

    try:
        for _ in range(min(max_workers, len(items))):
            submit_next()
        while pending:
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                index = pending.pop(future)
                results[index] = future.result()
                submit_next()
    except Exception:
        for future in pending:
            future.cancel()
        executor.shutdown(wait=True, cancel_futures=True)
        raise
    executor.shutdown(wait=True)
    if any(result is None for result in results):
        raise RuntimeError("bounded runner completed with missing results")
    return [result for result in results if result is not None]


def assert_run_accepts_docking(
    frame_run_root: Path,
    *,
    run_mode: str,
) -> None:
    if run_mode != "smoke":
        return
    terminal_authorities = (
        frame_run_root / "terminal" / "smoke_terminal.json",
        frame_run_root / "run_state_events.tsv",
        frame_run_root / "terminal_status.tsv",
    )
    existing = [path for path in terminal_authorities if path.exists()]
    if existing:
        joined = ", ".join(str(path) for path in existing)
        raise FileExistsError(
            "smoke run 已形成 terminal authority，拒绝新增 attempt: "
            f"{joined}"
        )


def _file_record(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256_file(path)}


def minimum_returned_modes(
    config: dict[str, Any], *, receptor: str, ligand: str
) -> int:
    """Reuse the frozen absolute geometry minimum as population sufficiency."""
    return int(
        config["frame_repair"]["geometry_gate"][receptor]["by_ligand"][
            ligand
        ]["min_passing_modes"]
    )


def _attempt_artifacts(attempt_dir: Path, pair_name: str) -> dict[str, Any]:
    stem = f"{pair_name}_poses"
    records: dict[str, Any] = {}
    for key, suffix in (
        ("command", ".vina.command.json"),
        ("stdout", ".vina.stdout.txt"),
        ("stderr", ".vina.stderr.txt"),
        ("poses", ".pdbqt"),
    ):
        path = attempt_dir / f"{stem}{suffix}"
        if path.is_file():
            records[key] = _file_record(path)
    command_record = records.get("command")
    if command_record:
        command = load_json(Path(command_record["path"]))
        records["process"] = {
            "returncode": command.get("returncode"),
            "elapsed_sec": command.get("elapsed_sec"),
            "status": command.get("status"),
        }
    return records


def _verify_content_identity(payload: dict[str, Any], *, label: str) -> None:
    body = dict(payload)
    expected = body.pop("manifest_identity", None)
    if (
        not isinstance(expected, str)
        or hashlib.sha256(canonical_json_bytes(body)).hexdigest() != expected
    ):
        raise ValueError(f"{label} content identity mismatch")


def _verify_config_binding(
    *,
    config_path: Path,
    run_manifest_path: Path,
    run_manifest: dict[str, Any],
    environment: dict[str, Any],
) -> dict[str, str]:
    current = _file_record(config_path)
    run_config = run_manifest.get("inputs", {}).get("config", {})
    env_config = environment.get("configuration", {})
    if (
        Path(run_config.get("path", "")).resolve() != config_path.resolve()
        or run_config.get("sha256") != current["sha256"]
        or Path(env_config.get("path", "")).resolve() != config_path.resolve()
        or env_config.get("sha256") != current["sha256"]
    ):
        raise ValueError("config/frame run/environment content identity mismatch")
    env_frame = environment.get("frame_run", {})
    if (
        Path(env_frame.get("path", "")).resolve() != run_manifest_path.resolve()
        or env_frame.get("sha256") != sha256_file(run_manifest_path)
        or env_frame.get("run_identity") != run_manifest["run_identity"]
    ):
        raise ValueError("environment manifest 与 frame run 不同源")
    return current


def _build_expected_job_inputs(
    *,
    config: dict[str, Any],
    config_path: Path,
    frame_run_root: Path,
    environment_path: Path,
    environment: dict[str, Any],
    resolved_box: dict[str, list[float]],
    receptor: str,
    subject: str,
    ligand: str,
) -> tuple[dict[str, Any], Path, dict[str, Any], Path]:
    receptor_pdbqt = (
        frame_run_root
        / "prepared_receptors"
        / receptor
        / f"{subject}_tm.pdbqt"
    )
    receptor_manifest_path = receptor_pdbqt.with_name(
        f"{subject}_tm.pdbqt.manifest.json"
    )
    receptor_manifest = verify_pdbqt_manifest(
        receptor_manifest_path,
        pdbqt_path=receptor_pdbqt,
        expected_receptor=receptor,
        expected_mutation=subject,
    )
    ligand_pdbqt = (
        config_path.parents[3]
        / config["paths"]["prepared_dir"]
        / "ligands"
        / f"{ligand}_optimized.pdbqt"
    )
    if not ligand_pdbqt.is_file():
        raise FileNotFoundError(ligand_pdbqt)
    vina = environment["executables"]["vina"]
    singlestage = config["vina"]["singlestage"]
    inputs = {
        "receptor": receptor,
        "mutation": subject,
        "ligand": ligand,
        "receptor_pdbqt": {
            **_file_record(receptor_pdbqt),
            "manifest_identity": receptor_manifest["manifest_identity"],
            "manifest": _file_record(receptor_manifest_path),
        },
        "ligand_pdbqt": _file_record(ligand_pdbqt),
        "box": resolved_box,
        "vina": {
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
            "energy_range": config["vina"]["energy_range"],
            "min_rmsd": config["vina"]["min_rmsd"],
            "max_evals": config["vina"]["max_evals"],
            "cpu": config["frame_repair"]["compute"]["cpu_per_job"],
        },
        "seed": config["vina"]["seed"],
        "environment": {
            **_file_record(environment_path),
            "manifest_identity": environment["manifest_identity"],
        },
    }
    return inputs, receptor_pdbqt, receptor_manifest, ligand_pdbqt


def _verify_existing_job_contract(
    manifest_path: Path,
    *,
    expected_inputs: dict[str, Any],
    requested_max_modes: int,
) -> dict[str, Any]:
    existing = verify_job_manifest(
        manifest_path,
        expected_receptor=expected_inputs["receptor"],
        expected_mutation=expected_inputs["mutation"],
        expected_ligand=expected_inputs["ligand"],
        requested_max_modes=requested_max_modes,
    )
    expected_identity = build_job_identity(expected_inputs)
    if (
        existing["job_identity"] != expected_identity
        or existing.get("inputs") != expected_inputs
    ):
        raise ValueError(
            "既有 job 与当前 box/environment/seed/ligand/Vina 合同不一致"
        )
    return existing


def _verify_passing_smoke_terminal(
    *,
    frame_run_root: Path,
    run_manifest: dict[str, Any],
    environment: dict[str, Any],
    config_record: dict[str, str],
    requested_max_modes: int,
) -> dict[str, Any]:
    path = frame_run_root / "terminal" / "smoke_terminal.json"
    payload = load_json(path)
    if (
        payload.get("schema") != "docking-frame-repair-smoke-terminal-v2"
        or payload.get("status") != "pass"
        or payload.get("job_count") != 8
    ):
        raise ValueError("full run requires a passing current 8-job smoke terminal")
    _verify_content_identity(payload, label="smoke terminal")
    if (
        payload.get("frame_run", {}).get("run_identity")
        != run_manifest["run_identity"]
        or payload.get("environment", {}).get("manifest_identity")
        != environment["manifest_identity"]
        or payload.get("configuration", {}).get("sha256")
        != config_record["sha256"]
    ):
        raise ValueError("smoke terminal 与当前 frame/config/environment 不同源")
    expected_keys = set(build_subject_matrix(run_manifest, run_mode="smoke"))
    jobs = payload.get("jobs", [])
    actual_keys = {
        (job.get("receptor"), job.get("mutation"), job.get("ligand"))
        for job in jobs
    }
    if actual_keys != expected_keys:
        raise ValueError("smoke terminal matrix mismatch")
    for recorded in jobs:
        for field in (
            "geometry_pass",
            "model1_geometry_pass",
            "ifp_complete",
            "provenance_pass",
            "technical_pose_pass",
            "pose_population_pass",
        ):
            if not recorded.get(field):
                raise ValueError(f"smoke terminal gate failed: {field}")
        manifest_path = Path(recorded["job_manifest"])
        current = verify_job_manifest(
            manifest_path,
            expected_receptor=recorded["receptor"],
            expected_mutation=recorded["mutation"],
            expected_ligand=recorded["ligand"],
            requested_max_modes=requested_max_modes,
        )
        if (
            current["job_identity"] != recorded["job_identity"]
            or current["manifest_identity"] != recorded["job_manifest_identity"]
            or current["outputs"]["poses"]["sha256"] != recorded["pose_sha256"]
        ):
            raise ValueError("smoke terminal docking evidence drift")
        for report_key, identity_key, required_passes in (
            (
                "ifp_report",
                "ifp_manifest_identity",
                (),
            ),
            (
                "geometry_report",
                "geometry_manifest_identity",
                ("pass", "model1_pass"),
            ),
        ):
            report = load_json(Path(recorded[report_key]))
            _verify_content_identity(report, label=report_key)
            if report.get("manifest_identity") != recorded[identity_key]:
                raise ValueError(f"smoke terminal evidence drift: {identity_key}")
            if report.get("job", {}).get("job_identity") != current["job_identity"]:
                raise ValueError(f"{report_key} 绑定到不同 smoke job")
            if report.get("pose_file", {}).get("sha256") != recorded["pose_sha256"]:
                raise ValueError(f"{report_key} pose identity drift")
            if any(not report.get(field) for field in required_passes):
                raise ValueError(f"{report_key} gate no longer passes")
    return payload


def _execute_job(
    job_key: tuple[str, str, str],
    *,
    config: dict[str, Any],
    config_path: Path,
    frame_run_root: Path,
    environment_path: Path,
    environment: dict[str, Any],
    resolved_boxes: dict[str, dict[str, list[float]]],
    requested_max_modes: int,
    run_mode: str,
) -> dict[str, Any]:
    receptor, subject, ligand = job_key
    job_root = (
        frame_run_root / "docking" / "jobs" / receptor / subject / ligand
    )
    job_manifest_path = job_root / "job_manifest.json"
    (
        expected_inputs,
        receptor_pdbqt,
        _,
        ligand_pdbqt,
    ) = _build_expected_job_inputs(
        config=config,
        config_path=config_path,
        frame_run_root=frame_run_root,
        environment_path=environment_path,
        environment=environment,
        resolved_box=resolved_boxes[receptor],
        receptor=receptor,
        subject=subject,
        ligand=ligand,
    )
    if job_manifest_path.exists():
        existing = _verify_existing_job_contract(
            job_manifest_path,
            expected_inputs=expected_inputs,
            requested_max_modes=requested_max_modes,
        )
        return {
            "receptor": receptor,
            "mutation": subject,
            "ligand": ligand,
            "job_identity": existing["job_identity"],
            "manifest": str(job_manifest_path),
            "manifest_sha256": sha256_file(job_manifest_path),
            "manifest_identity": existing["manifest_identity"],
            "reused_verified_existing_job": True,
            "reused_verified_smoke_member": (
                run_mode == "full"
                and subject in SMOKE_SUBJECTS[receptor]
            ),
        }

    wt_tm = (
        frame_run_root
        / "aligned_receptors"
        / receptor
        / "WT"
        / "WT_tm.aligned.pdb"
    )
    attempts_dir = job_root / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    attempt_number = len(
        [path for path in attempts_dir.glob("attempt-*") if path.is_dir()]
    ) + 1
    attempt_dir = attempts_dir / f"attempt-{attempt_number:03d}"
    attempt_dir.mkdir(parents=False, exist_ok=False)
    pair_name = f"{receptor}_{subject}_{ligand}"
    attempt_status_path = attempt_dir / "attempt_status.json"
    try:
        result = dock_pair_singlestage(
            receptor_pdbqt=receptor_pdbqt,
            ligand_pdbqt=ligand_pdbqt,
            pair_name=pair_name,
            tm_pdb=wt_tm,
            output_dir=attempt_dir,
            config=config,
            seed=config["vina"]["seed"],
            tm_helix_ranges=get_tm_helix_ranges(config, receptor),
            box_center_offset=get_box_center_offset(config, receptor),
            receptor_box_size=get_receptor_box_size(config, receptor),
            manual_box_center=get_manual_box_center(config, receptor),
            vina_bin_override=environment["executables"]["vina"]["path"],
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
        command_path = attempt_dir / f"{poses_path.stem}.vina.command.json"
        stdout_path = attempt_dir / f"{poses_path.stem}.vina.stdout.txt"
        stderr_path = attempt_dir / f"{poses_path.stem}.vina.stderr.txt"
        command = load_json(command_path)
        attempt = {
            "attempt_number": attempt_number,
            "run_mode": run_mode,
            "returncode": command["returncode"],
            "elapsed_sec": command["elapsed_sec"],
            "command": _file_record(command_path),
            "stdout": _file_record(stdout_path),
            "stderr": _file_record(stderr_path),
        }
        candidate_manifest_path = (
            attempt_dir / "candidate_job_manifest.json"
        )
        write_job_manifest(
            candidate_manifest_path,
            inputs=expected_inputs,
            pose_path=poses_path,
            requested_max_modes=requested_max_modes,
            minimum_returned_modes=minimum_returned_modes(
                config, receptor=receptor, ligand=ligand
            ),
            attempt=attempt,
        )
        verified_candidate = _verify_existing_job_contract(
            candidate_manifest_path,
            expected_inputs=expected_inputs,
            requested_max_modes=requested_max_modes,
        )
        if job_manifest_path.exists():
            raise FileExistsError(
                f"正式 job manifest 已出现，拒绝覆盖: {job_manifest_path}"
            )
        candidate_manifest_path.replace(job_manifest_path)
        job = _verify_existing_job_contract(
            job_manifest_path,
            expected_inputs=expected_inputs,
            requested_max_modes=requested_max_modes,
        )
        if job["manifest_identity"] != verified_candidate["manifest_identity"]:
            raise ValueError("candidate job manifest 原子移动后身份漂移")
        write_canonical_json(
            attempt_status_path,
            {
                "status": "technical_complete",
                "attempt_number": attempt_number,
                "job_identity": job["job_identity"],
                "job_manifest": str(job_manifest_path),
                "job_manifest_sha256": sha256_file(job_manifest_path),
                "job_manifest_identity": job["manifest_identity"],
                "actual_modes": job["outputs"]["poses"]["model_count"],
                "requested_max_modes": requested_max_modes,
                "pose_population": job["outputs"]["pose_population"],
            },
        )
        if not job["outputs"]["pose_population"]["comparable"]:
            write_canonical_json(
                attempt_status_path,
                {
                    "status": "non_comparable_pose_population",
                    "attempt_number": attempt_number,
                    "job_identity": job["job_identity"],
                    "job_manifest": str(job_manifest_path),
                    "job_manifest_sha256": sha256_file(job_manifest_path),
                    "job_manifest_identity": job["manifest_identity"],
                    "pose_population": job["outputs"]["pose_population"],
                },
            )
            raise RuntimeError(
                f"{pair_name}: non_comparable_pose_population"
            )
    except Exception as exc:
        if not attempt_status_path.exists():
            write_canonical_json(
                attempt_status_path,
                {
                    "status": "technical_failure",
                    "attempt_number": attempt_number,
                    "expected_job_identity": build_job_identity(
                        expected_inputs
                    ),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "artifacts": _attempt_artifacts(
                        attempt_dir, pair_name
                    ),
                },
            )
        raise DockingJobFailure(
            {
                "receptor": receptor,
                "mutation": subject,
                "ligand": ligand,
                "attempt_number": attempt_number,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        ) from exc
    return {
        "receptor": receptor,
        "mutation": subject,
        "ligand": ligand,
        "job_identity": job["job_identity"],
        "manifest": str(job_manifest_path),
        "manifest_sha256": sha256_file(job_manifest_path),
        "manifest_identity": job["manifest_identity"],
        "reused_verified_existing_job": False,
        "reused_verified_smoke_member": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--frame-run-root", required=True)
    parser.add_argument("--run-mode", choices=("smoke", "full"), required=True)
    parser.add_argument(
        "--confirm-compute-authorization",
        action="store_true",
        help="必须由用户明确批准本阶段计算后提供",
    )
    parser.add_argument(
        "--continue-smoke-after-technical-failure",
        action="store_true",
        help=(
            "smoke 单项技术失败后继续尝试冻结矩阵的其余 job；"
            "矩阵走完后仍以失败退出且不写 technical completion"
        ),
    )
    parser.add_argument(
        "--max-new-smoke-attempts",
        type=int,
        default=None,
        help=(
            "本次 smoke invocation 最多创建的新 attempt 数；"
            "用于可审计的有界重试，不改变 job 科学合同"
        ),
    )
    parser.add_argument(
        "--max-parallel-jobs",
        type=int,
        default=1,
        help=(
            "同一时刻最多运行的 docking jobs；smoke 固定为 1，"
            "full 仍受 E2 128-thread 硬上限约束"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.confirm_compute_authorization:
        raise PermissionError(
            "未确认本阶段计算授权；拒绝运行 smoke/full docking"
        )
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    frame_run_root = Path(args.frame_run_root).resolve()
    assert_run_accepts_docking(frame_run_root, run_mode=args.run_mode)
    run_manifest_path = frame_run_root / "run_manifest.json"
    run_manifest = verify_frame_run_manifest(
        run_manifest_path,
        verify_records=True,
    )
    environment_path = frame_run_root / "environment_manifest.json"
    environment = verify_environment_manifest(
        environment_path,
        expected_frame_run_root=frame_run_root,
        require_production_ready=True,
    )
    config_record = _verify_config_binding(
        config_path=config_path,
        run_manifest_path=run_manifest_path,
        run_manifest=run_manifest,
        environment=environment,
    )
    vina = environment["executables"]["vina"]
    matrix = build_subject_matrix(run_manifest, run_mode=args.run_mode)
    continue_after_failure = should_continue_after_technical_failure(
        run_mode=args.run_mode,
        continue_smoke_after_technical_failure=(
            args.continue_smoke_after_technical_failure
        ),
    )
    max_new_attempts = validate_max_new_smoke_attempts(
        run_mode=args.run_mode,
        max_new_smoke_attempts=args.max_new_smoke_attempts,
    )
    expected_jobs = 8 if args.run_mode == "smoke" else 328
    requested_max_modes = config["frame_repair"][
        "requested_max_modes_per_job"
    ]
    if requested_max_modes != config["vina"]["num_modes"]:
        raise ValueError("frame repair 与 Vina requested maximum 不一致")
    expected_compute = {
        "cpu_per_job": int(
            config["frame_repair"]["compute"]["cpu_per_job"]
        ),
        "requested_max_modes": int(config["vina"]["num_modes"]),
        "energy_range": float(config["vina"]["energy_range"]),
        "min_rmsd": float(config["vina"]["min_rmsd"]),
        "max_evals": int(config["vina"]["max_evals"]),
    }
    max_parallel_jobs = validate_max_parallel_jobs(
        run_mode=args.run_mode,
        max_parallel_jobs=args.max_parallel_jobs,
        cpu_per_job=expected_compute["cpu_per_job"],
    )
    if environment.get("compute_contract") != expected_compute:
        raise ValueError("environment compute contract 与 config 不一致")
    if len(matrix) != expected_jobs:
        raise ValueError("docking matrix completeness failure")
    if args.run_mode == "full":
        _verify_passing_smoke_terminal(
            frame_run_root=frame_run_root,
            run_manifest=run_manifest,
            environment=environment,
            config_record=config_record,
            requested_max_modes=requested_max_modes,
        )

    resolved_boxes: dict[str, dict[str, list[float]]] = {}
    for receptor in ("Gpr2", "Gpr3"):
        wt_tm = (
            frame_run_root
            / "aligned_receptors"
            / receptor
            / "WT"
            / "WT_tm.aligned.pdb"
        )
        resolved_boxes[receptor] = _resolve_box(
            config, receptor=receptor, wt_tm_pdb=wt_tm
        )

    plan: dict[str, Any] = {
        "schema": "docking-frame-repair-job-plan-v2",
        "status": "compute_authorization_confirmed",
        "run_mode": args.run_mode,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
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
        "configuration": config_record,
        "execution": {
            "max_parallel_jobs": max_parallel_jobs,
            "bounded_fail_fast": True,
        },
        "vina_invocation": {
            "executable_path": vina["path"],
            "executable_sha256": vina["sha256"],
            "version": environment["observed_versions"][
                "vina_conda_package"
            ],
            "package_build": environment["package_manager_identities"]["vina"][
                "build"
            ],
            "package_build_number": environment[
                "package_manager_identities"
            ]["vina"]["build_number"],
            "spacing": config["vina"]["singlestage"]["spacing"],
            "exhaustiveness": config["vina"]["singlestage"][
                "exhaustiveness"
            ],
            "requested_max_modes": requested_max_modes,
            "energy_range": config["vina"]["energy_range"],
            "min_rmsd": config["vina"]["min_rmsd"],
            "max_evals": config["vina"]["max_evals"],
            "cpu": config["frame_repair"]["compute"]["cpu_per_job"],
            "seed": config["vina"]["seed"],
        },
        "boxes": resolved_boxes,
        "jobs": [
            {"receptor": receptor, "mutation": subject, "ligand": ligand}
            for receptor, subject, ligand in matrix
        ],
    }
    plan["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(plan)
    ).hexdigest()
    plan_path = frame_run_root / "docking" / f"{args.run_mode}_job_plan.json"
    if plan_path.exists():
        existing_plan = load_json(plan_path)
        _verify_content_identity(existing_plan, label="job plan")
        if (
            existing_plan.get("schema") != plan["schema"]
            or existing_plan.get("run_mode") != args.run_mode
            or existing_plan.get("frame_run", {}).get("run_identity")
            != run_manifest["run_identity"]
            or existing_plan.get("environment", {}).get("manifest_identity")
            != environment["manifest_identity"]
            or existing_plan.get("configuration") != config_record
            or existing_plan.get("execution") != plan["execution"]
            or existing_plan.get("vina_invocation")
            != plan["vina_invocation"]
            or existing_plan.get("boxes") != resolved_boxes
            or existing_plan.get("jobs") != plan["jobs"]
        ):
            raise ValueError("既有 job plan 与当前输入不一致")
        active_plan = existing_plan
    else:
        write_canonical_json(plan_path, plan)
        active_plan = plan

    completion_path = (
        frame_run_root
        / "docking"
        / f"{args.run_mode}_technical_completion.json"
    )
    if completion_path.exists():
        raise FileExistsError(
            f"technical completion 已存在，拒绝覆盖或重跑: {completion_path}"
        )

    def execute(job_key: tuple[str, str, str]) -> dict[str, Any]:
        return _execute_job(
            job_key,
            config=config,
            config_path=config_path,
            frame_run_root=frame_run_root,
            environment_path=environment_path,
            environment=environment,
            resolved_boxes=resolved_boxes,
            requested_max_modes=requested_max_modes,
            run_mode=args.run_mode,
        )

    completed: list[dict[str, Any]] = []
    technical_failures: list[dict[str, Any]] = []
    if args.run_mode == "full":
        completed = run_bounded_fail_fast(
            matrix,
            execute,
            max_workers=max_parallel_jobs,
        )
    else:
        new_attempts = 0
        for job_key in matrix:
            receptor, subject, ligand = job_key
            job_manifest_path = (
                frame_run_root
                / "docking"
                / "jobs"
                / receptor
                / subject
                / ligand
                / "job_manifest.json"
            )
            if (
                not job_manifest_path.exists()
                and max_new_attempts is not None
                and new_attempts >= max_new_attempts
            ):
                break
            was_existing = job_manifest_path.exists()
            try:
                completed.append(execute(job_key))
            except DockingJobFailure as exc:
                technical_failures.append(exc.record)
                if not continue_after_failure:
                    raise
            if not was_existing:
                new_attempts += 1

    if technical_failures:
        failure_summary = "; ".join(
            (
                f"{item['receptor']}/{item['mutation']}/{item['ligand']}"
                f" attempt-{item['attempt_number']:03d}: {item['error']}"
            )
            for item in technical_failures
        )
        raise RuntimeError(
            "smoke matrix attempted with technical failures; "
            f"technical completion not written: {failure_summary}"
        )
    if len(completed) != expected_jobs:
        raise ValueError("technical completion matrix count mismatch")
    completion = {
        "schema": "docking-frame-repair-run-completion-v2",
        "status": "technical_matrix_complete_geometry_ifp_pending",
        "run_mode": args.run_mode,
        "job_count": len(completed),
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
        "configuration": config_record,
        "job_plan": {
            "path": str(plan_path),
            "sha256": sha256_file(plan_path),
            "manifest_identity": active_plan["manifest_identity"],
        },
        "jobs": completed,
    }
    completion["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(completion)
    ).hexdigest()
    write_canonical_json(completion_path, completion)
    print(json.dumps({"completed": len(completed)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
