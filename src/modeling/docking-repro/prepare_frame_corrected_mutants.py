"""Create a local, auditable aligned-receptor run for all Gpr2/Gpr3 mutants."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from frame_alignment import (
    align_mutant_to_wt,
    canonical_json_bytes,
    materialize_wt_frame_reference,
    sha256_file,
    write_canonical_json,
)
from geometry_calibration import verify_frozen_geometry_calibration
from geometry_gate import write_membrane_transform_manifest
from utils import get_project_root, load_config


PROVENANCE_GAPS = {
    "Gpr3": {
        "D100A", "F170A", "I141A", "I178A",
        "N171A", "Q93A", "R175A", "V138A",
    }
}


def enumerate_mutants(merged_json: Path) -> dict[str, list[str]]:
    raw = json.loads(Path(merged_json).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("merged mutagenesis JSON 必须是 list")
    selected: dict[str, set[str]] = {"Gpr2": set(), "Gpr3": set()}
    for record in raw:
        if not isinstance(record, dict):
            raise ValueError("merged mutagenesis JSON 包含非 object 记录")
        receptor = record.get("receptor")
        mutation = record.get("mutation")
        if receptor in selected:
            if not isinstance(mutation, str):
                raise ValueError(f"{receptor} mutation 字段缺失")
            selected[receptor].add(mutation.upper())
    result = {key: sorted(value) for key, value in selected.items()}
    expected = {"Gpr2": 46, "Gpr3": 116}
    actual = {key: len(value) for key, value in result.items()}
    if actual != expected:
        raise ValueError(f"mutant count mismatch: expected={expected}, actual={actual}")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(_THIS_DIR / "config.yaml"))
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--output-root",
        default=None,
        help="默认 temp/docking_frame_repair_<run-id>",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.project_root:
        config["paths"]["project_root"] = args.project_root
    root = get_project_root(config).resolve()
    repair_cfg = config["frame_repair"]
    merged_json = root / repair_cfg["mutation_inventory"]
    mutants = enumerate_mutants(merged_json)
    output_root = (
        Path(args.output_root).resolve()
        if args.output_root
        else root / "temp" / f"docking_frame_repair_{args.run_id}"
    )
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError(f"run root 已存在且非空，拒绝覆盖: {output_root}")

    calibration = verify_frozen_geometry_calibration(config, root=root)
    calibration_path = output_root / "geometry_calibration_report.json"
    write_canonical_json(calibration_path, calibration)

    records: list[dict] = []
    wt_records: list[dict] = []
    membrane_frames: list[dict] = []
    for receptor in repair_cfg["allowed_receptors"]:
        receptor_cfg = config["receptors"][receptor]
        wt_full = root / config["paths"]["receptor_dir"] / receptor_cfg["pdb_file"]
        wt_tm = (
            root
            / config["paths"]["prepared_dir"]
            / "receptors"
            / f"{Path(receptor_cfg['pdb_file']).stem}_tm.pdb"
        )
        helices = [
            config["tm_topology"][receptor]["helices"][key]
            for key in sorted(config["tm_topology"][receptor]["helices"])
        ]
        wt_out = output_root / "aligned_receptors" / receptor / "WT"
        wt_run_full = wt_out / "WT.aligned.pdb"
        wt_run_tm = wt_out / "WT_tm.aligned.pdb"
        wt_manifest_path = wt_out / "frame_manifest.json"
        wt_manifest = materialize_wt_frame_reference(
            receptor=receptor,
            wt_full_pdb=wt_full,
            wt_tm_pdb=wt_tm,
            run_full_pdb=wt_run_full,
            run_tm_pdb=wt_run_tm,
            manifest_path=wt_manifest_path,
            helices=helices,
        )
        wt_records.append(
            {
                "receptor": receptor,
                "mutation": "WT",
                "provenance_status": "canonical_wt_coordinate",
                "frame_manifest": str(wt_manifest_path.resolve()),
                "frame_manifest_sha256": sha256_file(wt_manifest_path),
                "frame_manifest_identity": wt_manifest["manifest_identity"],
            }
        )
        membrane_manifest_path = (
            output_root / "membrane_frames" / receptor / "transform_manifest.json"
        )
        membrane_pdb = root / repair_cfg["membrane_references"][receptor]
        membrane_manifest = write_membrane_transform_manifest(
            membrane_manifest_path,
            receptor=receptor,
            wt_docking_pdb=wt_tm,
            membrane_pdb=membrane_pdb,
            helices=helices,
        )
        membrane_frames.append(
            {
                "receptor": receptor,
                "manifest": str(membrane_manifest_path.resolve()),
                "sha256": sha256_file(membrane_manifest_path),
                "manifest_identity": membrane_manifest["manifest_identity"],
                "post_alignment_rmsd": membrane_manifest["metrics_angstrom"][
                    "post_alignment_rmsd"
                ],
            }
        )
        source_dir = (
            root
            / config["paths"]["mutagenesis_dir"]
            / "af3_structures"
            / receptor
        )
        for mutation in mutants[receptor]:
            mutant_full = source_dir / f"{mutation}.pdb"
            mutant_tm = source_dir / f"{mutation}_tm.pdb"
            if not mutant_full.is_file() or not mutant_tm.is_file():
                raise FileNotFoundError(f"缺少 mutant PDB/TM PDB: {receptor}/{mutation}")
            receptor_out = output_root / "aligned_receptors" / receptor / mutation
            aligned_full = receptor_out / f"{mutation}.aligned.pdb"
            aligned_tm = receptor_out / f"{mutation}_tm.aligned.pdb"
            manifest_path = receptor_out / "frame_manifest.json"
            provenance = (
                "local_af3_coordinate_only"
                if mutation in PROVENANCE_GAPS.get(receptor, set())
                else "af3_request_and_coordinate"
            )
            manifest = align_mutant_to_wt(
                receptor=receptor,
                mutation=mutation,
                wt_full_pdb=wt_full,
                wt_tm_pdb=wt_tm,
                mutant_full_pdb=mutant_full,
                mutant_tm_pdb=mutant_tm,
                aligned_full_pdb=aligned_full,
                aligned_tm_pdb=aligned_tm,
                manifest_path=manifest_path,
                helices=helices,
                provenance_status=provenance,
            )
            records.append(
                {
                    "receptor": receptor,
                    "mutation": mutation,
                    "provenance_status": provenance,
                    "frame_manifest": str(manifest_path.resolve()),
                    "frame_manifest_sha256": sha256_file(manifest_path),
                    "frame_manifest_identity": manifest["manifest_identity"],
                    "post_alignment_rmsd": manifest["metrics_angstrom"][
                        "post_alignment_rmsd"
                    ],
                }
            )

    summary = {
        "schema": "docking-frame-repair-run-v2",
        "status": "aligned_pdb_complete_pdbqt_pending",
        "run_id": args.run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "scope": {
            "receptors": repair_cfg["allowed_receptors"],
            "ligands": repair_cfg["ligands"],
            "mutant_counts": {key: len(value) for key, value in mutants.items()},
            "mutant_total": sum(len(value) for value in mutants.values()),
            "mutant_docking_jobs": sum(len(value) for value in mutants.values())
            * len(repair_cfg["ligands"]),
            "wt_baseline_jobs": len(repair_cfg["allowed_receptors"])
            * len(repair_cfg["ligands"]),
        },
        "inputs": {
            "config": {
                "path": str(Path(args.config).resolve()),
                "sha256": sha256_file(Path(args.config)),
            },
            "mutation_inventory": {
                "path": str(merged_json.resolve()),
                "sha256": sha256_file(merged_json),
                "use_boundary": "mutation labels only; historical scores are not consumed",
            },
            "geometry_calibration": {
                "path": str(calibration_path.resolve()),
                "sha256": sha256_file(calibration_path),
                "calibration_identity": calibration["calibration_identity"],
                "use_boundary": (
                    "frozen operational thresholds only; historical pose scores "
                    "are not current docking results"
                ),
            },
        },
        "provenance_gap_mutants": sorted(
            f"{receptor}/{mutation}"
            for receptor, mutations in PROVENANCE_GAPS.items()
            for mutation in mutations
        ),
        "wt_records": wt_records,
        "membrane_frames": membrane_frames,
        "records": records,
    }
    summary["run_identity"] = hashlib.sha256(canonical_json_bytes(summary)).hexdigest()
    write_canonical_json(output_root / "run_manifest.json", summary)
    print(
        json.dumps(
            {
                "run_root": str(output_root),
                "status": summary["status"],
                "scope": summary["scope"],
                "run_identity": summary["run_identity"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
