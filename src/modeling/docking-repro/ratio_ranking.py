"""Rebuild Gpr2/Gpr3 ratio rankings from one frame-corrected run only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Any

from docking_manifest import load_json, verify_job_manifest
from frame_alignment import canonical_json_bytes, sha256_file, write_canonical_json
from utils import load_config


ALLOWED_RECEPTORS = {"Gpr2", "Gpr3"}
REQUIRED_EVIDENCE_FIELDS = {
    "job_ascr18_identity",
    "job_ascr3_identity",
    "pose_ascr18_sha256",
    "pose_ascr3_sha256",
    "geometry_pass",
    "model1_geometry_pass",
    "ifp_pass",
    "provenance_pass",
    "technical_pose_pass",
    "pose_population_pass",
    "evidence",
}


def calculate_selectivity(dg_ascr18: float, dg_ascr3: float) -> float:
    return float(dg_ascr18) - float(dg_ascr3)


def classify(record: dict[str, Any], *, threshold: float, affinity_floor: float) -> str:
    selectivity = calculate_selectivity(record["dg_ascr18"], record["dg_ascr3"])
    if selectivity < -threshold and abs(float(record["dg_ascr18"])) >= affinity_floor:
        return "A"
    if selectivity > threshold and abs(float(record["dg_ascr3"])) >= affinity_floor:
        return "B"
    return "neutral"


def validate_record(record: dict[str, Any]) -> None:
    if record.get("receptor") not in ALLOWED_RECEPTORS:
        raise ValueError(f"active ratio universe 只允许 Gpr2/Gpr3: {record.get('receptor')}")
    missing = sorted(REQUIRED_EVIDENCE_FIELDS - set(record))
    if missing:
        raise ValueError(
            f"{record.get('receptor')}/{record.get('mutation')} 缺少证据字段: {missing}"
        )
    expected = calculate_selectivity(record["dg_ascr18"], record["dg_ascr3"])
    if abs(expected - float(record["sel_mut"])) > 1e-9:
        raise ValueError("sel_mut 与 run-local score 重算不一致")
    for field in (
        "job_ascr18_identity",
        "job_ascr3_identity",
        "pose_ascr18_sha256",
        "pose_ascr3_sha256",
    ):
        if not isinstance(record[field], str) or len(record[field]) != 64:
            raise ValueError(f"内容身份字段非法: {field}")
    for ligand, score_field, job_field, pose_field in (
        ("ascr18", "dg_ascr18", "job_ascr18_identity", "pose_ascr18_sha256"),
        ("ascr3", "dg_ascr3", "job_ascr3_identity", "pose_ascr3_sha256"),
    ):
        evidence = record["evidence"].get(ligand)
        if not isinstance(evidence, dict):
            raise ValueError(f"terminal evidence 缺少 {ligand}")
        job = verify_job_manifest(
            Path(evidence["job_manifest"]),
            expected_receptor=record["receptor"],
            expected_mutation=record["mutation"],
            expected_ligand=ligand,
        )
        if job["job_identity"] != record[job_field]:
            raise ValueError(f"{ligand} job identity 与 terminal row 不一致")
        if job["outputs"]["poses"]["sha256"] != record[pose_field]:
            raise ValueError(f"{ligand} pose body 与 terminal row 不一致")
        if job["outputs"]["score"]["model1_affinity"] != float(record[score_field]):
            raise ValueError(f"{ligand} MODEL1 score 与 terminal row 不一致")
    expected_terminal_status = (
        "eligible" if is_eligible(record) else "non_comparable_gate_failure"
    )
    if record.get("terminal_status") != expected_terminal_status:
        raise ValueError("terminal_status 与 gate evidence 不一致")


def is_eligible(record: dict[str, Any]) -> bool:
    return all(
        bool(record[field])
        for field in (
            "geometry_pass",
            "model1_geometry_pass",
            "ifp_pass",
            "provenance_pass",
            "technical_pose_pass",
            "pose_population_pass",
        )
    )


def build_spectrum(
    records: list[dict[str, Any]],
    *,
    threshold: float,
    affinity_floor: float,
) -> list[dict[str, Any]]:
    labels: set[str] = set()
    result: list[dict[str, Any]] = []
    for source in records:
        validate_record(source)
        record = dict(source)
        label = f"{record['receptor']}_{record['mutation']}"
        if label in labels:
            raise ValueError(f"重复 mutant record: {label}")
        labels.add(label)
        record["label"] = label
        record["sel_mut"] = calculate_selectivity(
            record["dg_ascr18"], record["dg_ascr3"]
        )
        record["channel"] = classify(
            record, threshold=threshold, affinity_floor=affinity_floor
        )
        record["eligible"] = is_eligible(record)
        result.append(record)
    result.sort(key=lambda item: (item["sel_mut"], item["label"]))
    return result


def build_pairings(spectrum: list[dict[str, Any]]) -> list[dict[str, Any]]:
    channel_a = [
        item for item in spectrum if item["eligible"] and item["channel"] == "A"
    ]
    channel_b = [
        item for item in spectrum if item["eligible"] and item["channel"] == "B"
    ]
    pairings: list[dict[str, Any]] = []
    for a, b in product(channel_a, channel_b):
        if a["receptor"] == b["receptor"]:
            continue
        separation = a["sel_mut"] - b["sel_mut"]
        magnitude_sum = abs(a["sel_mut"]) + abs(b["sel_mut"])
        balance = abs(a["sel_mut"]) / magnitude_sum if magnitude_sum else 0.5
        pairings.append(
            {
                "channel_a": a["label"],
                "channel_b": b["label"],
                "receptor_a": a["receptor"],
                "receptor_b": b["receptor"],
                "sel_a": a["sel_mut"],
                "sel_b": b["sel_mut"],
                "D": separation,
                "balance": balance,
                "balance_distance": abs(balance - 0.5),
                "model1_target_affinity_sum": float(a["dg_ascr18"])
                + float(b["dg_ascr3"]),
                "channel_a_job_identity": a["job_ascr18_identity"],
                "channel_b_job_identity": b["job_ascr3_identity"],
                "channel_a_pose_sha256": a["pose_ascr18_sha256"],
                "channel_b_pose_sha256": b["pose_ascr3_sha256"],
            }
        )
    pairings.sort(
        key=lambda item: (
            item["D"],
            item["balance_distance"],
            item["model1_target_affinity_sum"],
            item["channel_a"],
            item["channel_b"],
        )
    )
    for rank, pairing in enumerate(pairings, start=1):
        pairing["rank"] = rank
    return pairings


def _gpr2_identity(pairing: dict[str, Any]) -> str:
    if pairing["receptor_a"] == "Gpr2":
        return pairing["channel_a"]
    if pairing["receptor_b"] == "Gpr2":
        return pairing["channel_b"]
    raise ValueError("pairing 不含 Gpr2")


def select_panel(
    pairings: list[dict[str, Any]],
    *,
    panel_size: int = 7,
    min_distinct_gpr2: int = 2,
) -> list[dict[str, Any]]:
    if len(pairings) < panel_size:
        raise ValueError(f"合格 pairing 少于 {panel_size}")
    selected = list(pairings[:panel_size])
    identities = {_gpr2_identity(item) for item in selected}
    if len(identities) < min_distinct_gpr2:
        replacement = next(
            (
                item
                for item in pairings[panel_size:]
                if _gpr2_identity(item) not in identities
            ),
            None,
        )
        if replacement is None:
            raise ValueError("无法满足 Gpr2 mutant identity 多样性")
        selected[-1] = replacement
        selected.sort(key=lambda item: item["rank"])
    if len({_gpr2_identity(item) for item in selected}) < min_distinct_gpr2:
        raise ValueError("Gpr2 多样性约束未满足")
    if not any(
        item["receptor_a"] == "Gpr3" or item["receptor_b"] == "Gpr3"
        for item in selected
    ):
        raise ValueError("panel 缺少 Gpr3")
    return selected


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"拒绝写空表: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_frozen_policy(config: dict[str, Any]) -> dict[str, Any]:
    policy = config["frame_repair"]["ratio_ranking"]
    required = {
        "implementation",
        "allowed_receptors",
        "sel_mut_formula",
        "channel_threshold",
        "affinity_floor",
        "pairing_separation_formula",
        "pairing_sort_direction",
        "balance_formula",
        "pairing_tie_break",
        "panel_size",
        "min_distinct_gpr2_mutants",
        "requires_gpr3",
        "old_candidate_privilege",
        "ligand_quota",
        "insufficient_panel_action",
        "test_vectors",
    }
    missing = sorted(required - set(policy))
    if missing:
        raise ValueError(f"ratio policy 缺少冻结字段: {missing}")
    if (
        set(policy["allowed_receptors"]) != ALLOWED_RECEPTORS
        or policy["sel_mut_formula"] != "dg_ascr18 - dg_ascr3"
        or policy["pairing_separation_formula"] != "sel_A - sel_B"
        or policy["pairing_sort_direction"] != "ascending"
        or policy["balance_formula"]
        != "abs(sel_A)/(abs(sel_A)+abs(sel_B))"
        or policy["pairing_tie_break"]
        != [
            "abs(balance-0.5) ascending",
            "target MODEL1 affinity sum ascending",
            "channel_a identifier ascending",
            "channel_b identifier ascending",
        ]
        or int(policy["panel_size"]) != 7
        or int(policy["min_distinct_gpr2_mutants"]) < 2
        or not policy["requires_gpr3"]
        or policy["old_candidate_privilege"] is not False
        or policy["ligand_quota"] is not None
        or policy["insufficient_panel_action"]
        != "stop_without_backfill_or_threshold_relaxation"
    ):
        raise ValueError("ratio policy 与已冻结 canonical 公式/面板规则冲突")
    threshold = float(policy["channel_threshold"])
    affinity_floor = float(policy["affinity_floor"])
    if threshold <= 0 or affinity_floor <= 0:
        raise ValueError("ratio threshold/affinity floor 必须为正")
    vectors = policy["test_vectors"]
    if not isinstance(vectors, list) or len(vectors) < 2:
        raise ValueError("ratio policy 缺少冻结测试向量")
    for vector in vectors:
        calculated = calculate_selectivity(
            vector["dg_ascr18"],
            vector["dg_ascr3"],
        )
        if abs(calculated - float(vector["expected_sel_mut"])) > 1e-9:
            raise ValueError("ratio policy 测试向量的 sel_mut 不一致")
        if (
            classify(
                vector,
                threshold=threshold,
                affinity_floor=affinity_floor,
            )
            != vector["expected_channel"]
        ):
            raise ValueError("ratio policy 测试向量的 channel 不一致")
    return policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.yaml"))
    parser.add_argument("--terminal-manifest", required=True)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    policy = load_frozen_policy(config)
    terminal_manifest_path = Path(args.terminal_manifest).resolve()
    terminal_manifest = load_json(terminal_manifest_path)
    if (
        terminal_manifest.get("schema")
        != "docking-frame-repair-terminal-matrix-v1"
        or terminal_manifest.get("status") != "complete"
    ):
        raise ValueError("ratio rebuild 只接受完整 frame-repair terminal manifest")
    manifest_body = dict(terminal_manifest)
    expected_manifest_identity = manifest_body.pop("manifest_identity", None)
    if (
        not expected_manifest_identity
        or hashlib.sha256(canonical_json_bytes(manifest_body)).hexdigest()
        != expected_manifest_identity
    ):
        raise ValueError("terminal manifest content identity mismatch")
    if (
        Path(terminal_manifest.get("configuration", {}).get("path", "")).resolve()
        != config_path
        or terminal_manifest.get("configuration", {}).get("sha256")
        != sha256_file(config_path)
    ):
        raise ValueError("ratio ranking config 与 terminal matrix 不同源")
    scope = terminal_manifest.get("scope", {})
    if (
        scope.get("job_count") != 328
        or scope.get("mutant_count") != 162
        or scope.get("mutant_counts") != {"Gpr2": 46, "Gpr3": 116}
        or set(scope.get("receptors", [])) != ALLOWED_RECEPTORS
        or set(scope.get("ligands", [])) != {"ascr18", "ascr3"}
    ):
        raise ValueError("ratio ranking 只接受完整 Gpr2/Gpr3 328-job terminal scope")
    input_record = terminal_manifest["outputs"]["terminal_matrix"]
    input_path = Path(input_record["path"]).resolve()
    if sha256_file(input_path) != input_record["sha256"]:
        raise ValueError("terminal matrix hash mismatch")
    output_root = Path(args.output_root).resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError(f"拒绝复用非空 ratio output root: {output_root}")
    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or len(records) != 162:
        raise ValueError("ratio rebuild 必须读取完整 162-mutant terminal matrix")
    spectrum = build_spectrum(
        records,
        threshold=float(policy["channel_threshold"]),
        affinity_floor=float(policy["affinity_floor"]),
    )
    actual_counts = {
        receptor: sum(item["receptor"] == receptor for item in spectrum)
        for receptor in ALLOWED_RECEPTORS
    }
    if actual_counts != {"Gpr2": 46, "Gpr3": 116}:
        raise ValueError(f"ratio spectrum mutant counts mismatch: {actual_counts}")
    pairings = build_pairings(spectrum)
    panel = select_panel(
        pairings,
        panel_size=int(policy["panel_size"]),
        min_distinct_gpr2=int(policy["min_distinct_gpr2_mutants"]),
    )
    spectrum_path = output_root / "ratio_spectrum.csv"
    pairings_path = output_root / "ratio_pairings.csv"
    panel_path = output_root / "wetlab_panel_7_pairs.json"
    manifest_path = output_root / "ratio_manifest.json"
    for output in (
        spectrum_path,
        pairings_path,
        panel_path,
        manifest_path,
    ):
        if output.exists():
            raise FileExistsError(f"拒绝覆盖 ratio output: {output}")
    write_csv(spectrum_path, spectrum)
    write_csv(pairings_path, pairings)
    write_canonical_json(panel_path, panel)
    manifest = {
        "schema": "docking-ratio-ranking-v1",
        "status": "complete",
        "input": {
            "terminal_manifest": {
                "path": str(terminal_manifest_path),
                "sha256": sha256_file(terminal_manifest_path),
                "manifest_identity": terminal_manifest["manifest_identity"],
            },
            "terminal_matrix": {
                "path": str(input_path),
                "sha256": sha256_file(input_path),
            },
        },
        "configuration": {
            "path": str(config_path),
            "sha256": sha256_file(config_path),
        },
        "formula": {
            "sel_mut": "dg_ascr18 - dg_ascr3",
            "D": "sel_A - sel_B; ascending",
            "balance": "abs(sel_A)/(abs(sel_A)+abs(sel_B)); distance to 0.5 ascending",
            "tie_break": [
                "D ascending",
                "abs(balance-0.5) ascending",
                "target MODEL1 affinity sum ascending",
                "channel_a then channel_b identifier",
            ],
        },
        "threshold": float(policy["channel_threshold"]),
        "affinity_floor": float(policy["affinity_floor"]),
        "frozen_test_vectors": policy["test_vectors"],
        "scope": {"receptors": sorted(ALLOWED_RECEPTORS), "mutant_count": 162},
        "selection": {
            "panel_size": int(policy["panel_size"]),
            "min_distinct_gpr2_mutants": int(
                policy["min_distinct_gpr2_mutants"]
            ),
            "requires_gpr3": bool(policy["requires_gpr3"]),
            "old_candidate_privilege": bool(
                policy["old_candidate_privilege"]
            ),
            "ligand_quota": policy["ligand_quota"],
            "insufficient_panel_action": policy[
                "insufficient_panel_action"
            ],
        },
        "outputs": {
            "spectrum": {"path": str(spectrum_path), "sha256": sha256_file(spectrum_path)},
            "pairings": {"path": str(pairings_path), "sha256": sha256_file(pairings_path)},
            "panel": {"path": str(panel_path), "sha256": sha256_file(panel_path)},
        },
    }
    manifest["manifest_identity"] = hashlib.sha256(
        canonical_json_bytes(manifest)
    ).hexdigest()
    write_canonical_json(manifest_path, manifest)


if __name__ == "__main__":
    main()
