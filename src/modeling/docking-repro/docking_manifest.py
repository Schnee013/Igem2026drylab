"""Fail-closed manifests for frame-corrected docking inputs and outputs."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from frame_alignment import (
    FRAME_MANIFEST_SCHEMA,
    canonical_json_bytes,
    parse_atom_lines,
    parse_atoms,
    sha256_file,
    write_canonical_json,
)


PDBQT_MANIFEST_SCHEMA = "docking-receptor-pdbqt-v2"
ENVIRONMENT_MANIFEST_SCHEMA = "docking-environment-preflight-v3"
JOB_MANIFEST_SCHEMA = "docking-job-v3"
FRAME_RUN_SCHEMA = "docking-frame-repair-run-v2"
VINA_RESULT_RE = re.compile(
    r"^REMARK VINA RESULT:\s+([-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?)"
)
VINA_STDOUT_RESULT_RE = re.compile(
    r"^\s*\d+\s+([-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?)"
    r"\s+[-+]?\d+(?:\.\d+)?\s+[-+]?\d+(?:\.\d+)?\s*$"
)


@dataclass(frozen=True)
class PoseModel:
    model_number: int
    affinity: float
    body: str
    body_sha256: str
    atom_count: int


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"manifest 必须是 JSON object: {path}")
    return payload


def _verify_manifest_identity(manifest: dict[str, Any], *, label: str) -> None:
    payload = dict(manifest)
    expected = payload.pop("manifest_identity", None)
    actual = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    if not expected or actual != expected:
        raise ValueError(f"{label} content identity mismatch")


def _verify_file_record(record: dict[str, Any], *, label: str) -> Path:
    path_value = record.get("path")
    expected_hash = record.get("sha256")
    if not isinstance(path_value, str) or not isinstance(expected_hash, str):
        raise ValueError(f"{label} 缺少 path/sha256")
    path = Path(path_value)
    if not path.is_file() or sha256_file(path) != expected_hash:
        raise ValueError(f"{label} hash mismatch")
    return path


def verify_frame_manifest(
    manifest_path: Path,
    *,
    aligned_pdb: Path | None = None,
    aligned_tm_pdb: Path | None = None,
    expected_receptor: str | None = None,
    expected_mutation: str | None = None,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("schema") != FRAME_MANIFEST_SCHEMA:
        raise ValueError(f"非当前 frame-corrected manifest: {manifest_path}")
    if manifest.get("status") not in {"frame_aligned", "wt_frame_reference"}:
        raise ValueError(f"frame manifest 状态不可用: {manifest_path}")
    if expected_receptor and manifest.get("receptor") != expected_receptor:
        raise ValueError("frame manifest receptor mismatch")
    if expected_mutation and manifest.get("mutation") != expected_mutation:
        raise ValueError("frame manifest mutation mismatch")
    if manifest.get("alignment_selection", {}).get("ca_count") != 147:
        raise ValueError("frame manifest 必须包含 147 个 TM CA")
    if not manifest.get("identity_validation", {}).get("full_ca_key_sets_equal"):
        raise ValueError("frame manifest 缺少 full-receptor CA 集合相等证明")
    _verify_manifest_identity(manifest, label="frame manifest")

    for key, explicit_path in (
        ("aligned_full_pdb", aligned_pdb),
        ("aligned_tm_pdb", aligned_tm_pdb),
    ):
        record = manifest.get("files", {}).get(key)
        if not isinstance(record, dict):
            raise ValueError(f"frame manifest 缺少 {key}")
        if explicit_path is None:
            _verify_file_record(record, label=f"frame manifest {key}")
        else:
            path = Path(explicit_path)
            if not path.is_file() or sha256_file(path) != record.get("sha256"):
                raise ValueError(f"frame manifest hash mismatch: {key}")
    return manifest


def verify_frame_run_manifest(
    manifest_path: Path,
    *,
    verify_records: bool = True,
) -> dict[str, Any]:
    """Verify one immutable v2 frame run and, optionally, all receptor records."""
    manifest = load_json(manifest_path)
    if manifest.get("schema") != FRAME_RUN_SCHEMA:
        raise ValueError("拒绝旧或未知 frame run manifest")
    if manifest.get("status") != "aligned_pdb_complete_pdbqt_pending":
        raise ValueError("frame run 状态不可用于 receptor preparation/docking")
    payload = dict(manifest)
    expected_identity = payload.pop("run_identity", None)
    actual_identity = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    if not expected_identity or actual_identity != expected_identity:
        raise ValueError("frame run content identity mismatch")

    scope = manifest.get("scope", {})
    if scope.get("mutant_counts") != {"Gpr2": 46, "Gpr3": 116}:
        raise ValueError("frame run mutant counts mismatch")
    if (
        scope.get("mutant_total") != 162
        or scope.get("mutant_docking_jobs") != 324
        or scope.get("wt_baseline_jobs") != 4
    ):
        raise ValueError("frame run scope mismatch")

    inputs = manifest.get("inputs", {})
    for key in ("config", "mutation_inventory", "geometry_calibration"):
        _verify_file_record(inputs.get(key, {}), label=f"frame run input {key}")
    calibration = load_json(Path(inputs["geometry_calibration"]["path"]))
    calibration_body = dict(calibration)
    calibration_identity = calibration_body.pop("calibration_identity", None)
    if (
        not calibration_identity
        or hashlib.sha256(canonical_json_bytes(calibration_body)).hexdigest()
        != calibration_identity
        or calibration_identity
        != inputs["geometry_calibration"].get("calibration_identity")
    ):
        raise ValueError("frame run geometry calibration identity mismatch")

    records = manifest.get("records", [])
    wt_records = manifest.get("wt_records", [])
    membrane_frames = manifest.get("membrane_frames", [])
    if len(records) != 162 or len(wt_records) != 2 or len(membrane_frames) != 2:
        raise ValueError("frame run record counts mismatch")
    record_keys = [(item.get("receptor"), item.get("mutation")) for item in records]
    if len(set(record_keys)) != 162:
        raise ValueError("frame run mutant records are not unique")
    if {item.get("receptor") for item in wt_records} != {"Gpr2", "Gpr3"}:
        raise ValueError("frame run WT records mismatch")
    if {item.get("receptor") for item in membrane_frames} != {"Gpr2", "Gpr3"}:
        raise ValueError("frame run membrane records mismatch")

    if verify_records:
        for record in [*wt_records, *records]:
            frame_path = _verify_file_record(
                {
                    "path": record.get("frame_manifest"),
                    "sha256": record.get("frame_manifest_sha256"),
                },
                label=(
                    f"frame run receptor manifest "
                    f"{record.get('receptor')}/{record.get('mutation')}"
                ),
            )
            frame = verify_frame_manifest(
                frame_path,
                expected_receptor=record["receptor"],
                expected_mutation=record["mutation"],
            )
            if frame["manifest_identity"] != record.get("frame_manifest_identity"):
                raise ValueError("frame run/frame manifest identity mismatch")
        from geometry_gate import verify_membrane_transform_manifest

        for record in membrane_frames:
            path = _verify_file_record(
                {
                    "path": record.get("manifest"),
                    "sha256": record.get("sha256"),
                },
                label=f"frame run membrane manifest {record.get('receptor')}",
            )
            membrane = verify_membrane_transform_manifest(
                path, expected_receptor=record["receptor"]
            )
            if membrane["manifest_identity"] != record.get("manifest_identity"):
                raise ValueError("frame run/membrane manifest identity mismatch")
    return manifest


def _heavy_atom_map(path: Path) -> dict[tuple[str, int, str, str], np.ndarray]:
    mapping: dict[tuple[str, int, str, str], np.ndarray] = {}
    for atom in parse_atoms(path):
        element = atom.element or atom.atom_name[:1].upper()
        if element == "H":
            continue
        if atom.atom_key in mapping:
            raise ValueError(f"重复重原子: {atom.atom_key} in {path}")
        mapping[atom.atom_key] = atom.coord
    return mapping


def compare_pdb_pdbqt_frame(
    aligned_pdb: Path,
    pdbqt_path: Path,
    *,
    tolerance_angstrom: float = 0.002,
) -> dict[str, Any]:
    """Require complete heavy-atom coverage and coordinate preservation."""
    pdb_atoms = _heavy_atom_map(aligned_pdb)
    pdbqt_atoms = _heavy_atom_map(pdbqt_path)
    pdb_keys = set(pdb_atoms)
    pdbqt_keys = set(pdbqt_atoms)
    if pdb_keys != pdbqt_keys:
        raise ValueError(
            "PDB/PDBQT 重原子集合不一致: "
            f"missing={sorted(pdb_keys - pdbqt_keys)[:5]}, "
            f"extra={sorted(pdbqt_keys - pdb_keys)[:5]}"
        )
    keys = sorted(pdb_keys)
    distances = np.array(
        [np.linalg.norm(pdb_atoms[key] - pdbqt_atoms[key]) for key in keys],
        dtype=float,
    )
    maximum = float(distances.max())
    if maximum > tolerance_angstrom:
        raise ValueError(
            f"PDBQT 改变 receptor frame: max heavy-atom delta={maximum:.6f} Å"
        )
    return {
        "coverage": "complete_heavy_atom_key_set",
        "common_heavy_atom_count": len(keys),
        "pdb_heavy_atom_count": len(pdb_atoms),
        "pdbqt_heavy_atom_count": len(pdbqt_atoms),
        "max_coordinate_delta_angstrom": maximum,
        "rms_coordinate_delta_angstrom": float(np.sqrt(np.mean(distances**2))),
        "tolerance_angstrom": tolerance_angstrom,
    }


def verify_environment_manifest(
    manifest_path: Path,
    *,
    expected_frame_run_root: Path | None = None,
    require_production_ready: bool = True,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("schema") != ENVIRONMENT_MANIFEST_SCHEMA:
        raise ValueError("未知 environment manifest schema")
    _verify_manifest_identity(manifest, label="environment manifest")
    if require_production_ready and manifest.get("status") != "production_ready":
        raise ValueError(
            f"工具链未冻结: {manifest.get('status', 'missing_status')}"
        )

    frame_record = manifest.get("frame_run", {})
    run_manifest_path = _verify_file_record(
        frame_record, label="environment frame run manifest"
    )
    run_manifest = verify_frame_run_manifest(
        run_manifest_path, verify_records=False
    )
    if run_manifest.get("run_identity") != frame_record.get("run_identity"):
        raise ValueError("environment/frame run identity mismatch")
    if expected_frame_run_root is not None:
        expected = Path(expected_frame_run_root).resolve() / "run_manifest.json"
        if run_manifest_path.resolve() != expected:
            raise ValueError("environment manifest 绑定到不同 frame run")

    configuration = manifest.get("configuration", {})
    _verify_file_record(
        configuration,
        label="environment configuration",
    )
    _verify_file_record(
        configuration.get("environment_lock", {}),
        label="environment lock",
    )

    for name in ("vina", "openbabel", "adfr_prepare_receptor"):
        record = manifest.get("executables", {}).get(name)
        if not isinstance(record, dict):
            raise ValueError(f"environment manifest 缺少 executable: {name}")
        if record.get("path") is not None:
            _verify_file_record(record, label=f"environment executable {name}")
        elif record.get("sha256") is not None:
            raise ValueError(f"environment executable {name} path/hash 不一致")
    compute = manifest.get("compute_contract", {})
    required_compute = {
        "cpu_per_job",
        "requested_max_modes",
        "energy_range",
        "min_rmsd",
        "max_evals",
    }
    if sorted(required_compute - set(compute)):
        raise ValueError("environment manifest 缺少完整 compute contract")
    if int(compute["cpu_per_job"]) < 1 or int(compute["requested_max_modes"]) < 1:
        raise ValueError("environment compute contract 非法")
    return manifest


def create_pdbqt_manifest(
    *,
    frame_manifest_path: Path,
    aligned_pdb: Path,
    pdbqt_path: Path,
    output_manifest_path: Path,
    preparation_command: list[str],
    environment_manifest_path: Path,
    tolerance_angstrom: float = 0.002,
) -> dict[str, Any]:
    frame_manifest = verify_frame_manifest(
        frame_manifest_path,
        aligned_tm_pdb=aligned_pdb,
    )
    environment = verify_environment_manifest(
        environment_manifest_path,
        expected_frame_run_root=Path(frame_manifest_path).resolve().parents[3],
    )
    coordinate_check = compare_pdb_pdbqt_frame(
        aligned_pdb, pdbqt_path, tolerance_angstrom=tolerance_angstrom
    )
    adfr = environment["executables"]["adfr_prepare_receptor"]
    payload: dict[str, Any] = {
        "schema": PDBQT_MANIFEST_SCHEMA,
        "status": "prepared_from_frame_aligned_pdb",
        "receptor": frame_manifest["receptor"],
        "mutation": frame_manifest["mutation"],
        "target_frame": frame_manifest["target_frame"],
        "frame_manifest": {
            "path": str(Path(frame_manifest_path).resolve()),
            "sha256": sha256_file(frame_manifest_path),
            "manifest_identity": frame_manifest["manifest_identity"],
        },
        "aligned_pdb": {
            "path": str(Path(aligned_pdb).resolve()),
            "sha256": sha256_file(aligned_pdb),
        },
        "pdbqt": {
            "path": str(Path(pdbqt_path).resolve()),
            "sha256": sha256_file(pdbqt_path),
        },
        "preparation": {
            "command": preparation_command,
            "tool": {
                "name": "ADFR prepare_receptor",
                "path": adfr["path"],
                "sha256": adfr["sha256"],
                "version": environment["observed_versions"][
                    "adfr_prepare_receptor"
                ],
            },
            "environment_manifest": {
                "path": str(Path(environment_manifest_path).resolve()),
                "sha256": sha256_file(environment_manifest_path),
                "manifest_identity": environment["manifest_identity"],
            },
        },
        "coordinate_check": coordinate_check,
    }
    payload["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    write_canonical_json(output_manifest_path, payload)
    return payload


def verify_pdbqt_manifest(
    manifest_path: Path,
    *,
    pdbqt_path: Path,
    expected_receptor: str,
    expected_mutation: str,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("schema") != PDBQT_MANIFEST_SCHEMA:
        raise ValueError("拒绝旧或未知 PDBQT manifest")
    if manifest.get("status") != "prepared_from_frame_aligned_pdb":
        raise ValueError("PDBQT manifest 状态不可用")
    if manifest.get("receptor") != expected_receptor:
        raise ValueError("PDBQT manifest receptor mismatch")
    if manifest.get("mutation") != expected_mutation:
        raise ValueError("PDBQT manifest mutation mismatch")
    _verify_manifest_identity(manifest, label="PDBQT manifest")
    if sha256_file(pdbqt_path) != manifest.get("pdbqt", {}).get("sha256"):
        raise ValueError("PDBQT body hash mismatch")
    frame_record = manifest.get("frame_manifest", {})
    frame_path = _verify_file_record(frame_record, label="PDBQT frame manifest")
    frame = verify_frame_manifest(
        frame_path,
        expected_receptor=expected_receptor,
        expected_mutation=expected_mutation,
    )
    if frame["manifest_identity"] != frame_record.get("manifest_identity"):
        raise ValueError("PDBQT/frame manifest identity mismatch")
    aligned_pdb = _verify_file_record(
        manifest.get("aligned_pdb", {}), label="PDBQT aligned source"
    )
    compare_pdb_pdbqt_frame(aligned_pdb, pdbqt_path)
    env_record = manifest.get("preparation", {}).get("environment_manifest", {})
    env_path = _verify_file_record(env_record, label="PDBQT environment manifest")
    environment = verify_environment_manifest(env_path)
    if environment["manifest_identity"] != env_record.get("manifest_identity"):
        raise ValueError("PDBQT/environment identity mismatch")
    return manifest


def parse_vina_pose_models(path: Path) -> list[PoseModel]:
    """Parse MODEL bodies, affinities and hashes entirely in memory."""
    lines = Path(path).read_text(errors="replace").splitlines(keepends=True)
    models: list[PoseModel] = []
    current: list[str] | None = None
    for line_number, line in enumerate(lines, start=1):
        if line.startswith("MODEL"):
            if current is not None:
                raise ValueError(f"嵌套 MODEL: {path}:{line_number}")
            current = [line]
            continue
        if line.startswith("ENDMDL"):
            if current is None:
                raise ValueError(f"ENDMDL 无对应 MODEL: {path}:{line_number}")
            current.append(line)
            header = current[0].split()
            if len(header) != 2:
                raise ValueError(f"MODEL header 非法: {current[0].rstrip()}")
            model_number = int(header[1])
            affinity_values = [
                float(match.group(1))
                for body_line in current
                if (match := VINA_RESULT_RE.match(body_line))
            ]
            if len(affinity_values) != 1:
                raise ValueError(
                    f"MODEL {model_number} 必须恰有一个 VINA RESULT"
                )
            atoms = parse_atom_lines(
                current,
                source=f"{path}#MODEL{model_number}",
                first_model_only=False,
            )
            body = "".join(current)
            models.append(
                PoseModel(
                    model_number=model_number,
                    affinity=affinity_values[0],
                    body=body,
                    body_sha256=hashlib.sha256(body.encode("utf-8")).hexdigest(),
                    atom_count=len(atoms),
                )
            )
            current = None
            continue
        if current is not None:
            current.append(line)
    if current is not None:
        raise ValueError(f"未闭合 MODEL: {path}")
    if not models:
        raise ValueError(f"pose 文件不含 MODEL: {path}")
    expected_numbers = list(range(1, len(models) + 1))
    actual_numbers = [model.model_number for model in models]
    if actual_numbers != expected_numbers:
        raise ValueError(
            f"MODEL 编号必须连续从 1 开始: {actual_numbers}"
        )
    return models


def pose_evidence(path: Path, *, requested_max_modes: int) -> dict[str, Any]:
    models = parse_vina_pose_models(path)
    if not 1 <= len(models) <= requested_max_modes:
        raise ValueError(
            "pose 技术完整性失败: "
            f"requested_max={requested_max_modes}, actual={len(models)}"
        )
    return {
        "path": str(Path(path).resolve()),
        "sha256": sha256_file(path),
        "requested_max_modes": requested_max_modes,
        "model_count": len(models),
        "models": [
            {
                "model_number": model.model_number,
                "body_sha256": model.body_sha256,
                "affinity": model.affinity,
                "atom_count": model.atom_count,
            }
            for model in models
        ],
    }


def _command_flag_values(argv: list[str]) -> dict[str, str]:
    flags: dict[str, str] = {}
    index = 1
    while index < len(argv):
        flag = argv[index]
        if not flag.startswith("--") or index + 1 >= len(argv):
            raise ValueError(f"Vina argv 非法: {argv}")
        if flag in flags:
            raise ValueError(f"Vina argv 重复 flag: {flag}")
        flags[flag] = argv[index + 1]
        index += 2
    return flags


def verify_vina_attempt(
    attempt: dict[str, Any],
    *,
    inputs: dict[str, Any],
    poses: dict[str, Any],
) -> dict[str, Any]:
    """Verify process completion, invocation flags and stdout/pose affinity binding."""
    command_path = _verify_file_record(
        attempt.get("command", {}), label="Vina command evidence"
    )
    stdout_path = _verify_file_record(
        attempt.get("stdout", {}), label="Vina stdout evidence"
    )
    _verify_file_record(attempt.get("stderr", {}), label="Vina stderr evidence")
    command = load_json(command_path)
    if command.get("schema") != "vina-command-v2":
        raise ValueError("拒绝旧或未知 Vina command evidence")
    argv = command.get("argv")
    if not isinstance(argv, list) or not all(
        isinstance(value, str) for value in argv
    ):
        raise ValueError("Vina command argv 缺失")
    if (
        command.get("status") != "process_complete"
        or command.get("returncode") != 0
        or attempt.get("returncode") != 0
    ):
        raise ValueError("Vina process 未正常完成")
    elapsed = command.get("elapsed_sec")
    if (
        not isinstance(elapsed, (int, float))
        or elapsed < 0
        or abs(float(attempt.get("elapsed_sec", -1)) - float(elapsed)) > 1e-9
    ):
        raise ValueError("Vina elapsed evidence mismatch")

    vina = inputs["vina"]
    box = inputs["box"]
    expected_flags = {
        "--receptor": inputs["receptor_pdbqt"]["path"],
        "--ligand": inputs["ligand_pdbqt"]["path"],
        "--center_x": f"{float(box['center'][0]):.4f}",
        "--center_y": f"{float(box['center'][1]):.4f}",
        "--center_z": f"{float(box['center'][2]):.4f}",
        "--size_x": f"{float(box['size'][0]):.2f}",
        "--size_y": f"{float(box['size'][1]):.2f}",
        "--size_z": f"{float(box['size'][2]):.2f}",
        "--spacing": f"{float(vina['spacing']):.3f}",
        "--exhaustiveness": str(int(vina["exhaustiveness"])),
        "--num_modes": str(int(vina["requested_max_modes"])),
        "--energy_range": f"{float(vina['energy_range']):.1f}",
        "--min_rmsd": f"{float(vina['min_rmsd']):.1f}",
        "--max_evals": str(int(vina["max_evals"])),
        "--cpu": str(int(vina["cpu"])),
        "--seed": str(int(inputs["seed"])),
        "--out": poses["path"],
    }
    flags = _command_flag_values(argv)
    if argv[0] != vina["executable_path"] or flags != expected_flags:
        raise ValueError("Vina command 与 frozen job invocation 不一致")

    stdout_affinities = [
        float(match.group(1))
        for line in stdout_path.read_text(errors="replace").splitlines()
        if (match := VINA_STDOUT_RESULT_RE.match(line))
    ]
    pose_affinities = [model["affinity"] for model in poses["models"]]
    if stdout_affinities != pose_affinities:
        raise ValueError("Vina stdout affinity/count 与 pose body 不同源")
    return {
        "returncode": 0,
        "elapsed_sec": float(elapsed),
        "stdout_affinities": stdout_affinities,
    }


def _job_identity_payload(inputs: dict[str, Any]) -> dict[str, Any]:
    required = {
        "receptor",
        "mutation",
        "ligand",
        "receptor_pdbqt",
        "ligand_pdbqt",
        "box",
        "vina",
        "seed",
        "environment",
    }
    missing = sorted(required - set(inputs))
    if missing:
        raise ValueError(f"job identity 缺少字段: {missing}")
    receptor = inputs["receptor_pdbqt"]
    ligand = inputs["ligand_pdbqt"]
    vina = inputs["vina"]
    environment = inputs["environment"]
    return {
        "receptor": inputs["receptor"],
        "mutation": inputs["mutation"],
        "ligand": inputs["ligand"],
        "receptor_pdbqt_sha256": receptor["sha256"],
        "receptor_pdbqt_manifest_identity": receptor["manifest_identity"],
        "ligand_pdbqt_sha256": ligand["sha256"],
        "box": inputs["box"],
        "vina": {
            "executable_sha256": vina["executable_sha256"],
            "version": vina["version"],
            "package_build": vina["package_build"],
            "package_build_number": vina["package_build_number"],
            "spacing": vina["spacing"],
            "exhaustiveness": vina["exhaustiveness"],
            "requested_max_modes": vina["requested_max_modes"],
            "energy_range": vina["energy_range"],
            "min_rmsd": vina["min_rmsd"],
            "max_evals": vina["max_evals"],
            "cpu": vina["cpu"],
        },
        "seed": inputs["seed"],
        "environment_identity": environment["manifest_identity"],
    }


def build_job_identity(inputs: dict[str, Any]) -> str:
    return hashlib.sha256(
        canonical_json_bytes(_job_identity_payload(inputs))
    ).hexdigest()


def write_job_manifest(
    path: Path,
    *,
    inputs: dict[str, Any],
    pose_path: Path,
    requested_max_modes: int,
    minimum_returned_modes: int,
    attempt: dict[str, Any],
) -> dict[str, Any]:
    """Write a stable input identity plus a distinct output/attempt identity."""
    poses = pose_evidence(
        pose_path, requested_max_modes=requested_max_modes
    )
    attempt_check = verify_vina_attempt(attempt, inputs=inputs, poses=poses)
    population_comparable = poses["model_count"] >= minimum_returned_modes
    body: dict[str, Any] = {
        "schema": JOB_MANIFEST_SCHEMA,
        "status": "technical_complete",
        "inputs": inputs,
        "outputs": {
            "poses": poses,
            "score": {
                "model1_affinity": poses["models"][0]["affinity"],
                "all_affinities": [
                    model["affinity"] for model in poses["models"]
                ],
            },
            "pose_population": {
                "actual_modes": poses["model_count"],
                "requested_max_modes": requested_max_modes,
                "minimum_returned_modes": minimum_returned_modes,
                "status": (
                    "comparable"
                    if population_comparable
                    else "non_comparable_pose_population"
                ),
                "comparable": population_comparable,
            },
        },
        "attempt": {**attempt, "verified_process": attempt_check},
    }
    body["job_identity"] = build_job_identity(inputs)
    body["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(body)
    ).hexdigest()
    write_canonical_json(path, body)
    return body


def verify_job_manifest(
    manifest_path: Path,
    *,
    expected_receptor: str | None = None,
    expected_mutation: str | None = None,
    expected_ligand: str | None = None,
    requested_max_modes: int | None = None,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("schema") != JOB_MANIFEST_SCHEMA:
        raise ValueError("拒绝旧或未知 docking job manifest")
    if manifest.get("status") != "technical_complete":
        raise ValueError("docking job 尚未技术完成")
    _verify_manifest_identity(manifest, label="docking job manifest")
    inputs = manifest.get("inputs", {})
    if manifest.get("job_identity") != build_job_identity(inputs):
        raise ValueError("job input identity mismatch")
    for expected, field in (
        (expected_receptor, "receptor"),
        (expected_mutation, "mutation"),
        (expected_ligand, "ligand"),
    ):
        if expected is not None and inputs.get(field) != expected:
            raise ValueError(f"job {field} mismatch")

    receptor_record = inputs.get("receptor_pdbqt", {})
    receptor_path = _verify_file_record(
        receptor_record, label="job receptor PDBQT"
    )
    receptor_manifest_path = _verify_file_record(
        receptor_record.get("manifest", {}),
        label="job receptor PDBQT manifest",
    )
    receptor_manifest = verify_pdbqt_manifest(
        receptor_manifest_path,
        pdbqt_path=receptor_path,
        expected_receptor=inputs["receptor"],
        expected_mutation=inputs["mutation"],
    )
    if receptor_manifest["manifest_identity"] != receptor_record.get(
        "manifest_identity"
    ):
        raise ValueError("job receptor manifest identity mismatch")
    _verify_file_record(inputs.get("ligand_pdbqt", {}), label="job ligand PDBQT")
    environment_record = inputs.get("environment", {})
    environment_path = _verify_file_record(
        environment_record, label="job environment manifest"
    )
    environment = verify_environment_manifest(environment_path)
    if environment["manifest_identity"] != environment_record.get(
        "manifest_identity"
    ):
        raise ValueError("job environment identity mismatch")
    vina = inputs.get("vina", {})
    compute = environment["compute_contract"]
    expected_compute = {
        "cpu_per_job": int(vina["cpu"]),
        "requested_max_modes": int(vina["requested_max_modes"]),
        "energy_range": float(vina["energy_range"]),
        "min_rmsd": float(vina["min_rmsd"]),
        "max_evals": int(vina["max_evals"]),
    }
    if compute != expected_compute:
        raise ValueError("job Vina invocation 与 environment compute contract 不一致")
    package = environment["package_manager_identities"]["vina"]
    if (
        vina.get("version") != package.get("version")
        or vina.get("package_build") != package.get("build")
        or vina.get("package_build_number") != package.get("build_number")
    ):
        raise ValueError("job Vina package identity mismatch")

    recorded_poses = manifest.get("outputs", {}).get("poses", {})
    pose_path = _verify_file_record(recorded_poses, label="job pose body")
    manifest_max = int(inputs["vina"]["requested_max_modes"])
    if requested_max_modes is not None and manifest_max != requested_max_modes:
        raise ValueError("job requested maximum mode contract mismatch")
    actual = pose_evidence(pose_path, requested_max_modes=manifest_max)
    if actual != recorded_poses:
        raise ValueError("job pose MODEL/body/affinity evidence mismatch")
    expected_score = {
        "model1_affinity": actual["models"][0]["affinity"],
        "all_affinities": [model["affinity"] for model in actual["models"]],
    }
    if manifest.get("outputs", {}).get("score") != expected_score:
        raise ValueError("job score 与实际 pose body 不同源")
    population = manifest.get("outputs", {}).get("pose_population", {})
    minimum_returned_modes = int(population.get("minimum_returned_modes", 0))
    expected_population = {
        "actual_modes": actual["model_count"],
        "requested_max_modes": manifest_max,
        "minimum_returned_modes": minimum_returned_modes,
        "status": (
            "comparable"
            if actual["model_count"] >= minimum_returned_modes
            else "non_comparable_pose_population"
        ),
        "comparable": actual["model_count"] >= minimum_returned_modes,
    }
    if minimum_returned_modes < 1 or population != expected_population:
        raise ValueError("job pose-population evidence mismatch")
    verify_vina_attempt(
        manifest.get("attempt", {}),
        inputs=inputs,
        poses=actual,
    )
    return manifest
