"""Recompute and verify frozen WT geometry-gate calibration evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from math import ceil
from pathlib import Path
from typing import Any

import numpy as np

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

from docking_manifest import parse_vina_pose_models
from frame_alignment import (
    canonical_json_bytes,
    parse_atom_lines,
    parse_atoms,
    sha256_file,
)
from geometry_gate import (
    _heavy_receptor_coordinates,
    _membrane_lipid_coordinates,
    build_membrane_transform,
    ligand_heavy_coordinates,
    membrane_frame_from_manifest,
    protein_vs_membrane_nearest_count,
    radial_and_heights,
)
from utils import get_project_root, load_config


CALIBRATION_SCHEMA = "docking-geometry-calibration-verification-v1"
CURRENT_GATE_ARTIFACT_SCHEMA = "docking-wt-geometry-gate-calibration-v1"
CURRENT_GATE_CALIBRATION_SEEDS = (42, 43)
_FLOAT_TOLERANCE = 1e-6


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _require_hash(path: Path, expected: str, *, label: str) -> None:
    if not path.is_file() or sha256_file(path) != expected:
        raise ValueError(f"{label} hash mismatch: {path}")


def _require_close(actual: float, expected: float, *, label: str) -> None:
    if not np.isclose(
        float(actual),
        float(expected),
        atol=_FLOAT_TOLERANCE,
        rtol=0.0,
    ):
        raise ValueError(f"{label} mismatch: expected={expected}, actual={actual}")


def _verify_identity(
    payload: dict[str, Any],
    *,
    identity_key: str,
    label: str,
) -> None:
    body = dict(payload)
    expected = body.pop(identity_key, None)
    actual = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    if not isinstance(expected, str) or expected != actual:
        raise ValueError(f"{label} content identity mismatch")


def _round_threshold(value: float) -> float:
    return round(float(value), 6)


def derive_current_toolchain_gate(
    source_arms: list[dict[str, Any]],
    *,
    method: dict[str, Any],
) -> dict[str, Any]:
    """Derive a portable WT-only gate before viewing holdout or mutant results."""
    calibration_seeds = sorted(
        int(value) for value in method["calibration_seeds"]
    )
    requested_max_modes = int(method["requested_max_modes"])
    height_margin = float(method["height_margin_angstrom"])
    radial_margin = float(method["radial_margin_angstrom"])
    protein_fraction = float(method["protein_closer_fraction"])
    passing_margin = int(method["passing_mode_margin"])
    if len(calibration_seeds) != 2 or len(set(calibration_seeds)) != 2:
        raise ValueError("current-toolchain gate requires two distinct WT seeds")
    if requested_max_modes < 1 or passing_margin < 0:
        raise ValueError("invalid requested-mode or passing-margin contract")
    if height_margin <= 0.0 or radial_margin <= 0.0:
        raise ValueError("geometry margins must be positive")
    if not 0.0 < protein_fraction <= 1.0:
        raise ValueError("protein-closer fraction must be in (0, 1]")

    expected_keys = {
        (seed, receptor, ligand)
        for seed in calibration_seeds
        for receptor in ("Gpr2", "Gpr3")
        for ligand in ("ascr18", "ascr3")
    }
    actual_keys: set[tuple[int, str, str]] = set()
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for arm in source_arms:
        if arm.get("mutation") != "WT":
            raise ValueError("geometry calibration source must be WT-only")
        seed = int(arm["seed"])
        receptor = str(arm["receptor"])
        ligand = str(arm["ligand"])
        key = (seed, receptor, ligand)
        if key in actual_keys:
            raise ValueError(f"duplicate WT calibration arm: {key}")
        actual_keys.add(key)
        rows = arm.get("poses", [])
        if (
            int(arm.get("actual_modes", -1)) != requested_max_modes
            or len(rows) != requested_max_modes
        ):
            raise ValueError(f"WT calibration arm is not complete: {key}")
        models = sorted(int(row["model"]) for row in rows)
        if models != list(range(1, requested_max_modes + 1)):
            raise ValueError(f"WT calibration MODEL set is incomplete: {key}")
        grouped.setdefault((receptor, ligand), []).append(arm)
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        raise ValueError(
            f"WT calibration matrix mismatch: missing={missing}, extra={extra}"
        )

    accepted_by_pair: dict[tuple[str, str], dict[int, list[int]]] = {}
    dominant_by_pair: dict[tuple[str, str], int] = {}
    accepted_rows_by_receptor: dict[str, list[dict[str, Any]]] = {
        "Gpr2": [],
        "Gpr3": [],
    }
    for pair, arms in grouped.items():
        counts = Counter(
            int(row["protein_closer_atom_count"])
            for arm in arms
            for row in arm["poses"]
        )
        if not counts:
            raise ValueError(f"WT calibration pair has no pose metrics: {pair}")
        highest_frequency = max(counts.values())
        dominant_candidates = sorted(
            count
            for count, frequency in counts.items()
            if frequency == highest_frequency
        )
        if len(dominant_candidates) != 1:
            raise ValueError(
                f"protein-closer mode is not unique for {pair}: "
                f"{dominant_candidates}"
            )
        dominant = dominant_candidates[0]
        dominant_by_pair[pair] = dominant
        accepted_by_pair[pair] = {}
        for arm in arms:
            seed = int(arm["seed"])
            accepted = [
                row
                for row in arm["poses"]
                if (
                    bool(row["inside_shared_box"])
                    and bool(row["standard_prolif_contact"])
                    and int(row["protein_closer_atom_count"]) == dominant
                )
            ]
            if not accepted:
                raise ValueError(
                    f"WT calibration produced no accepted poses: "
                    f"{seed}/{pair[0]}/{pair[1]}"
                )
            accepted_by_pair[pair][seed] = sorted(
                int(row["model"]) for row in accepted
            )
            accepted_rows_by_receptor[pair[0]].extend(accepted)

    receptor_thresholds: dict[str, dict[str, Any]] = {}
    for receptor in ("Gpr2", "Gpr3"):
        accepted = accepted_rows_by_receptor[receptor]
        if not accepted:
            raise ValueError(f"WT calibration has no accepted poses: {receptor}")
        height_min = _round_threshold(
            min(
                float(row["membrane_absolute_height_angstrom"])
                for row in accepted
            )
            - height_margin
        )
        height_max = _round_threshold(
            max(
                float(row["membrane_absolute_height_angstrom"])
                for row in accepted
            )
            + height_margin
        )
        radial_max = _round_threshold(
            max(float(row["radial_to_tm_axis_angstrom"]) for row in accepted)
            + radial_margin
        )
        by_ligand: dict[str, Any] = {}
        for ligand in ("ascr18", "ascr3"):
            pair = (receptor, ligand)
            dominant = dominant_by_pair[pair]
            min_protein = int(ceil(dominant * protein_fraction))
            passing_models_by_seed: dict[str, list[int]] = {}
            for arm in grouped[pair]:
                passing = [
                    int(row["model"])
                    for row in arm["poses"]
                    if (
                        bool(row["inside_shared_box"])
                        and bool(row["standard_prolif_contact"])
                        and float(row["radial_to_tm_axis_angstrom"])
                        < radial_max
                        and height_min
                        <= float(row["membrane_absolute_height_angstrom"])
                        <= height_max
                        and int(row["protein_closer_atom_count"])
                        >= min_protein
                    )
                ]
                if 1 not in passing:
                    raise ValueError(
                        f"WT MODEL 1 would fail derived gate: "
                        f"{arm['seed']}/{receptor}/{ligand}"
                    )
                passing_models_by_seed[str(int(arm["seed"]))] = sorted(
                    passing
                )
            minimum_observed = min(
                len(models) for models in passing_models_by_seed.values()
            )
            min_passing_modes = minimum_observed - passing_margin
            if min_passing_modes < 1:
                raise ValueError(
                    f"derived pose-population gate is non-positive: {pair}"
                )
            by_ligand[ligand] = {
                "dominant_protein_closer_atom_count": dominant,
                "min_protein_closer_atoms": min_protein,
                "min_passing_modes": min_passing_modes,
                "calibration_accepted_models_by_seed": {
                    str(seed): accepted_by_pair[pair][seed]
                    for seed in calibration_seeds
                },
                "calibration_passing_models_by_seed": passing_models_by_seed,
            }
        receptor_thresholds[receptor] = {
            "radial_max_angstrom": radial_max,
            "membrane_height_min_angstrom": height_min,
            "membrane_height_max_angstrom": height_max,
            "by_ligand": by_ligand,
        }
    return {
        "calibration_seeds": calibration_seeds,
        "requested_max_modes": requested_max_modes,
        "receptors": receptor_thresholds,
    }


def _receptor_inputs(
    config: dict[str, Any],
    *,
    root: Path,
    receptor: str,
) -> tuple[Path, Path, list[list[int]]]:
    receptor_cfg = config["receptors"][receptor]
    wt_tm = (
        root
        / config["paths"]["prepared_dir"]
        / "receptors"
        / f"{Path(receptor_cfg['pdb_file']).stem}_tm.pdb"
    )
    membrane = _resolve(
        root, config["frame_repair"]["membrane_references"][receptor]
    )
    helices = [
        config["tm_topology"][receptor]["helices"][key]
        for key in sorted(config["tm_topology"][receptor]["helices"])
    ]
    return wt_tm, membrane, helices


def _pose_geometry_rows(
    *,
    pose_path: Path,
    frame_manifest: dict[str, Any],
    wt_tm: Path,
    membrane: Path,
) -> list[dict[str, Any]]:
    frame = membrane_frame_from_manifest(frame_manifest)
    receptor_membrane = frame.transform.apply(
        _heavy_receptor_coordinates(parse_atoms(wt_tm))
    )
    lipid_membrane = _membrane_lipid_coordinates(membrane)
    rows: list[dict[str, Any]] = []
    for model in parse_vina_pose_models(pose_path):
        atoms = parse_atom_lines(
            model.body.splitlines(),
            source=f"{pose_path}#MODEL{model.model_number}",
            first_model_only=False,
        )
        ligand_docking = ligand_heavy_coordinates(atoms)
        ligand_membrane = frame.transform.apply(ligand_docking)
        radial, absolute_height, relative_height = radial_and_heights(
            ligand_membrane.mean(axis=0), frame
        )
        nearest = protein_vs_membrane_nearest_count(
            ligand_membrane, receptor_membrane, lipid_membrane
        )
        rows.append(
            {
                "model": model.model_number,
                "pose_body_sha256": model.body_sha256,
                "heavy_atom_count": len(ligand_docking),
                "radial_to_tm_axis_angstrom": radial,
                "membrane_absolute_height_angstrom": absolute_height,
                "tm_relative_height_angstrom": relative_height,
                "protein_closer_heavy_atom_count": nearest[
                    "protein_closer_atom_count"
                ],
            }
        )
    return rows


def _largest_gap_extracellular_cluster(
    rows: list[dict[str, Any]],
    *,
    upper_phosphate_height: float,
) -> dict[str, Any]:
    if len(rows) < 3:
        raise ValueError("height calibration requires at least three poses")
    ordered = sorted(
        (
            float(row["membrane_absolute_height_angstrom"]),
            int(row["model"]),
        )
        for row in rows
    )
    gaps = [
        ordered[index + 1][0] - ordered[index][0]
        for index in range(len(ordered) - 1)
    ]
    largest_index = int(np.argmax(gaps))
    largest_gap = float(gaps[largest_index])
    second_largest = float(sorted(gaps, reverse=True)[1])
    if np.isclose(largest_gap, second_largest, atol=1e-12, rtol=0.0):
        raise ValueError("height calibration largest gap is not unique")
    retained = ordered[largest_index + 1 :]
    retained_heights = [height for height, _ in retained]
    if float(np.median(retained_heights)) <= float(upper_phosphate_height):
        raise ValueError("higher-coordinate height cluster is not extracellular")
    return {
        "largest_height_gap_angstrom": largest_gap,
        "discarded_height_max_angstrom": float(ordered[largest_index][0]),
        "membrane_height_min_angstrom": float(min(retained_heights)),
        "membrane_height_max_angstrom": float(max(retained_heights)),
        "retained_models": sorted(model for _, model in retained),
    }


def _verify_source_log(
    root: Path,
    source: dict[str, Any],
    *,
    label: str,
) -> dict[str, str]:
    record = source["method_log"]
    path = _resolve(root, record["path"])
    _require_hash(path, record["sha256"], label=f"{label} method log")
    return {
        "path": str(path),
        "sha256": record["sha256"],
        "lines": str(record["lines"]),
    }


def _verify_gpr2(
    config: dict[str, Any],
    *,
    root: Path,
) -> dict[str, Any]:
    gate = config["frame_repair"]["geometry_gate"]["Gpr2"]
    if gate.get("calibration_status") != "FROZEN_BEFORE_MUTANT_RESULTS":
        raise ValueError("Gpr2 geometry calibration is not frozen")
    wt_tm, membrane, helices = _receptor_inputs(
        config, root=root, receptor="Gpr2"
    )
    transform = build_membrane_transform(
        receptor="Gpr2",
        wt_docking_pdb=wt_tm,
        membrane_pdb=membrane,
        helices=helices,
    )
    upper_phosphate = float(
        transform["membrane_geometry"]["upper_phosphate_height"]
    )
    ligand_reports: dict[str, Any] = {}
    for ligand in config["frame_repair"]["ligands"]:
        frozen = gate["by_ligand"][ligand]
        calibration = frozen["calibration"]
        pose_path = _resolve(root, calibration["pose_file"])
        _require_hash(
            pose_path,
            calibration["pose_sha256"],
            label=f"Gpr2/{ligand} calibration pose",
        )
        rows = _pose_geometry_rows(
            pose_path=pose_path,
            frame_manifest=transform,
            wt_tm=wt_tm,
            membrane=membrane,
        )
        if len(rows) != int(calibration["model_count"]):
            raise ValueError(f"Gpr2/{ligand} calibration pose count mismatch")
        cluster = _largest_gap_extracellular_cluster(
            rows, upper_phosphate_height=upper_phosphate
        )
        for key in (
            "membrane_height_min_angstrom",
            "membrane_height_max_angstrom",
        ):
            _require_close(cluster[key], frozen[key], label=f"Gpr2/{ligand} {key}")
        _require_close(
            cluster["largest_height_gap_angstrom"],
            calibration["largest_height_gap_angstrom"],
            label=f"Gpr2/{ligand} largest height gap",
        )
        if cluster["retained_models"] != calibration["retained_models"]:
            raise ValueError(f"Gpr2/{ligand} retained MODEL set mismatch")

        retained = [
            row for row in rows if row["model"] in set(cluster["retained_models"])
        ]
        minimum_protein_closer = min(
            int(row["protein_closer_heavy_atom_count"]) for row in retained
        )
        if minimum_protein_closer != int(frozen["min_protein_closer_atoms"]):
            raise ValueError(f"Gpr2/{ligand} protein-closer threshold mismatch")
        passing_models = [
            int(row["model"])
            for row in rows
            if (
                float(row["radial_to_tm_axis_angstrom"])
                < float(gate["radial_max_angstrom"])
                and float(frozen["membrane_height_min_angstrom"])
                <= float(row["membrane_absolute_height_angstrom"])
                <= float(frozen["membrane_height_max_angstrom"])
                and int(row["protein_closer_heavy_atom_count"])
                >= int(frozen["min_protein_closer_atoms"])
            )
        ]
        if len(passing_models) != int(frozen["min_passing_modes"]):
            raise ValueError(f"Gpr2/{ligand} passing-mode threshold mismatch")
        ligand_reports[ligand] = {
            "pose_file": {
                "path": str(pose_path),
                "sha256": calibration["pose_sha256"],
                "model_count": len(rows),
            },
            "derived": {
                **cluster,
                "min_protein_closer_atoms": minimum_protein_closer,
                "passing_models": passing_models,
                "min_passing_modes": len(passing_models),
            },
        }
    return {
        "source_log": _verify_source_log(root, gate["source"], label="Gpr2"),
        "membrane_transform": transform,
        "ligands": ligand_reports,
    }


def _verify_gpr3(
    config: dict[str, Any],
    *,
    root: Path,
) -> dict[str, Any]:
    gate = config["frame_repair"]["geometry_gate"]["Gpr3"]
    if gate.get("calibration_status") != "FROZEN_BEFORE_MUTANT_RESULTS":
        raise ValueError("Gpr3 geometry calibration is not frozen")
    wt_tm, membrane, helices = _receptor_inputs(
        config, root=root, receptor="Gpr3"
    )
    transform = build_membrane_transform(
        receptor="Gpr3",
        wt_docking_pdb=wt_tm,
        membrane_pdb=membrane,
        helices=helices,
    )
    ligand_reports: dict[str, Any] = {}
    for ligand in config["frame_repair"]["ligands"]:
        frozen = gate["by_ligand"][ligand]
        calibration = frozen["calibration"]
        pose_path = _resolve(root, calibration["pose_file"])
        _require_hash(
            pose_path,
            calibration["pose_sha256"],
            label=f"Gpr3/{ligand} calibration pose",
        )
        rows = _pose_geometry_rows(
            pose_path=pose_path,
            frame_manifest=transform,
            wt_tm=wt_tm,
            membrane=membrane,
        )
        if len(rows) != int(calibration["observed_model_count"]):
            raise ValueError(f"Gpr3/{ligand} historical pose count mismatch")
        if calibration.get("completeness_boundary") != (
            "historical_artifact_incomplete_not_current_positive_control"
        ):
            raise ValueError("Gpr3 historical completeness boundary is missing")
        if len(rows) >= int(
            config["frame_repair"]["geometry_gate"]["common"][
                "requested_max_modes"
            ]
        ):
            raise ValueError("Gpr3 historical incomplete-artifact boundary drifted")
        for actual, expected, label in (
            (frozen["membrane_height_min_angstrom"], 108.5, "height min"),
            (frozen["membrane_height_max_angstrom"], 114.0, "height max"),
            (frozen["min_protein_closer_atoms"], 14, "protein closer"),
            (frozen["min_passing_modes"], 15, "passing modes"),
        ):
            _require_close(actual, expected, label=f"Gpr3/{ligand} {label}")
        ligand_reports[ligand] = {
            "pose_file": {
                "path": str(pose_path),
                "sha256": calibration["pose_sha256"],
                "observed_model_count": len(rows),
            },
            "completeness_boundary": calibration["completeness_boundary"],
            "model1": rows[0],
        }
    return {
        "source_log": _verify_source_log(root, gate["source"], label="Gpr3"),
        "membrane_transform": transform,
        "ligands": ligand_reports,
    }


def _verify_current_toolchain_gate(
    config: dict[str, Any],
    *,
    root: Path,
) -> dict[str, Any]:
    geometry_gate = config["frame_repair"]["geometry_gate"]
    artifact_record = geometry_gate.get("calibration_artifact", {})
    artifact_path = _resolve(root, artifact_record.get("path", ""))
    _require_hash(
        artifact_path,
        artifact_record.get("sha256", ""),
        label="current-toolchain geometry calibration artifact",
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if (
        artifact.get("schema") != CURRENT_GATE_ARTIFACT_SCHEMA
        or artifact.get("status")
        != "frozen_before_holdout_and_mutant_results"
    ):
        raise ValueError("current-toolchain geometry artifact is not frozen")
    _verify_identity(
        artifact,
        identity_key="gate_identity",
        label="current-toolchain geometry artifact",
    )
    if artifact.get("gate_identity") != artifact_record.get("gate_identity"):
        raise ValueError("current-toolchain gate identity mismatch")
    observed_seeds = tuple(
        sorted(int(seed) for seed in artifact.get("method", {}).get(
            "calibration_seeds", []
        ))
    )
    if observed_seeds != CURRENT_GATE_CALIBRATION_SEEDS:
        raise ValueError(
            "current-toolchain calibration seeds must be exactly 42 and 43"
        )
    derived = derive_current_toolchain_gate(
        artifact.get("source_arms", []),
        method=artifact.get("method", {}),
    )
    if derived != artifact.get("derived_gate"):
        raise ValueError("current-toolchain derived gate content mismatch")
    production_seed = int(config["vina"]["seed"])
    if production_seed in set(derived["calibration_seeds"]):
        raise ValueError("production/holdout seed must be independent of calibration")
    common = geometry_gate["common"]
    if int(common["requested_max_modes"]) != int(
        derived["requested_max_modes"]
    ):
        raise ValueError("current-toolchain requested maximum drifted")

    receptor_reports: dict[str, Any] = {}
    for receptor in ("Gpr2", "Gpr3"):
        configured = geometry_gate[receptor]
        expected = derived["receptors"][receptor]
        if configured.get("calibration_status") != (
            "FROZEN_BEFORE_MUTANT_RESULTS"
        ):
            raise ValueError(f"{receptor} current-toolchain gate is not frozen")
        _require_close(
            configured["radial_max_angstrom"],
            expected["radial_max_angstrom"],
            label=f"{receptor} radial maximum",
        )
        ligand_reports: dict[str, Any] = {}
        for ligand in ("ascr18", "ascr3"):
            configured_ligand = configured["by_ligand"][ligand]
            expected_ligand = expected["by_ligand"][ligand]
            for key, expected_value in (
                (
                    "membrane_height_min_angstrom",
                    expected["membrane_height_min_angstrom"],
                ),
                (
                    "membrane_height_max_angstrom",
                    expected["membrane_height_max_angstrom"],
                ),
                (
                    "min_protein_closer_atoms",
                    expected_ligand["min_protein_closer_atoms"],
                ),
                (
                    "min_passing_modes",
                    expected_ligand["min_passing_modes"],
                ),
            ):
                _require_close(
                    configured_ligand[key],
                    expected_value,
                    label=f"{receptor}/{ligand} {key}",
                )
            calibration = configured_ligand.get("calibration", {})
            if (
                calibration.get("gate_identity")
                != artifact["gate_identity"]
                or sorted(calibration.get("seeds", []))
                != derived["calibration_seeds"]
            ):
                raise ValueError(
                    f"{receptor}/{ligand} calibration binding mismatch"
                )
            ligand_reports[ligand] = expected_ligand
        wt_tm, membrane, helices = _receptor_inputs(
            config,
            root=root,
            receptor=receptor,
        )
        receptor_reports[receptor] = {
            "membrane_transform": build_membrane_transform(
                receptor=receptor,
                wt_docking_pdb=wt_tm,
                membrane_pdb=membrane,
                helices=helices,
            ),
            "derived": expected,
            "ligands": ligand_reports,
        }
    return {
        "artifact": {
            "path": str(artifact_path),
            "sha256": sha256_file(artifact_path),
            "gate_identity": artifact["gate_identity"],
        },
        "calibration_seeds": derived["calibration_seeds"],
        "production_seed": production_seed,
        "receptors": receptor_reports,
    }


def verify_frozen_geometry_calibration(
    config: dict[str, Any],
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    root = (
        Path(root).resolve()
        if root is not None
        else get_project_root(config).resolve()
    )
    geometry_gate = config["frame_repair"]["geometry_gate"]
    schema = geometry_gate.get("schema_version")
    if schema == "docking-geometry-gate-v3":
        current = _verify_current_toolchain_gate(config, root=root)
        payload: dict[str, Any] = {
            "schema": CALIBRATION_SCHEMA,
            "status": "verified_frozen_before_mutant_results",
            "policy": geometry_gate["policy"],
            "calibration_artifact": current["artifact"],
            "calibration_seeds": current["calibration_seeds"],
            "production_seed": current["production_seed"],
            "receptors": current["receptors"],
        }
        payload["calibration_identity"] = hashlib.sha256(
            canonical_json_bytes(payload)
        ).hexdigest()
        return payload
    if schema != "docking-geometry-gate-v2":
        raise ValueError("unknown geometry gate schema")
    payload: dict[str, Any] = {
        "schema": CALIBRATION_SCHEMA,
        "status": "verified_frozen_before_mutant_results",
        "policy": geometry_gate["policy"],
        "receptors": {
            "Gpr2": _verify_gpr2(config, root=root),
            "Gpr3": _verify_gpr3(config, root=root),
        },
    }
    payload["calibration_identity"] = hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    return payload


def main() -> None:
    config_path = _THIS_DIR / "config.yaml"
    config = load_config(config_path)
    report = verify_frozen_geometry_calibration(config)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
