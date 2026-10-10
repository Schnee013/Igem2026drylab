#!/usr/bin/env python
"""Compare matched ligand paths in a common receptor reference frame.

This shared structural-triage driver complements the seven canonical metric
drivers. It localizes ligand centroid movement and time-resolved receptor
contacts without assigning a stable/unstable cutoff or a mutation effect.

Each arm is aligned with an equal-weight Kabsch fit to one arm's frame-0
receptor reference. Absolute between-arm ligand positions remain descriptive
when the starting poses or construction chains differ.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array
import numpy as np
import pandas as pd


sys.path.insert(0, str(Path("src/modeling/md-analysis").resolve()))

from common import analysis_context, equal_weight_kabsch_coordinates, time_ns


def parse_named_paths(values: list[str], option: str) -> dict[str, Path]:
    """Parse repeated ``NAME=PATH`` values and reject ambiguous labels."""
    parsed: dict[str, Path] = {}
    for raw in values:
        if "=" not in raw:
            raise ValueError(f"{option} requires NAME=PATH, got {raw!r}")
        name, path = raw.split("=", 1)
        name = name.strip()
        path = path.strip()
        if not name or not path:
            raise ValueError(f"{option} requires non-empty NAME=PATH, got {raw!r}")
        if name in parsed:
            raise ValueError(f"duplicate {option} label: {name}")
        parsed[name] = Path(path)
    return parsed


def equal_weight_fit(
    mobile_fit_positions: np.ndarray,
    reference_fit_positions: np.ndarray,
    coordinates: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Align coordinates using an equal-weight receptor Kabsch transform."""
    return equal_weight_kabsch_coordinates(
        mobile_fit_positions,
        reference_fit_positions,
        coordinates,
    )


def contact_residue_set(
    receptor,
    ligand,
    cutoff_A: float,
) -> tuple[set[tuple[int, str]], float]:
    """Return contacting receptor residues and the protein-ligand minimum."""
    distances = distance_array(receptor.positions, ligand.positions)
    atom_pairs = np.argwhere(distances <= cutoff_A)
    contacts = {
        (int(receptor[receptor_index].resid), str(receptor[receptor_index].resname))
        for receptor_index, _ in atom_pairs
    }
    return contacts, float(distances.min())


def summarize_contact_occupancy(
    arm: str,
    times_ns: np.ndarray,
    frame_contacts: list[set[tuple[int, str]]],
    window_start_ns: float,
    cutoff_A: float,
) -> list[dict]:
    """Summarize early/late residue-contact occupancy without thresholding."""
    if len(times_ns) != len(frame_contacts):
        raise ValueError("times and frame_contacts length mismatch")
    if len(times_ns) == 0:
        raise ValueError("cannot summarize an empty trajectory")
    early_indices = np.flatnonzero(times_ns < window_start_ns)
    late_indices = np.flatnonzero(times_ns >= window_start_ns)
    if len(early_indices) == 0 or len(late_indices) == 0:
        raise ValueError(
            f"window_start_ns={window_start_ns:g} must leave both early and late frames"
        )

    all_residues = sorted(set().union(*frame_contacts))
    rows = []
    for resid, resname in all_residues:
        key = (resid, resname)
        early_hits = sum(key in frame_contacts[index] for index in early_indices)
        late_hits = sum(key in frame_contacts[index] for index in late_indices)
        contact_indices = [
            index for index, contacts in enumerate(frame_contacts) if key in contacts
        ]
        early_occupancy = early_hits / len(early_indices)
        late_occupancy = late_hits / len(late_indices)
        rows.append(
            {
                "arm": arm,
                "receptor_resid": resid,
                "receptor_resname": resname,
                "initial_contact": key in frame_contacts[0],
                "early_occupancy": early_occupancy,
                "late_occupancy": late_occupancy,
                "late_minus_early": late_occupancy - early_occupancy,
                "first_contact_ns": float(times_ns[contact_indices[0]]),
                "last_contact_ns": float(times_ns[contact_indices[-1]]),
                "contact_cutoff_A": cutoff_A,
                "window_start_ns": window_start_ns,
            }
        )
    return rows


def representative_indices(
    times_ns: np.ndarray,
    displacement_A: np.ndarray,
    window_start_ns: float,
) -> list[tuple[str, int]]:
    """Select deterministic structural-triage frame indices."""
    targets = [
        ("initial", 0),
        (
            "window_start",
            int(np.argmin(np.abs(times_ns - window_start_ns))),
        ),
        (
            "late_midpoint",
            int(
                np.argmin(
                    np.abs(
                        times_ns
                        - (window_start_ns + float(times_ns[-1])) / 2.0
                    )
                )
            ),
        ),
        ("max_displacement", int(np.argmax(displacement_A))),
        ("final", len(times_ns) - 1),
    ]
    seen: set[int] = set()
    return [
        (label, index)
        for label, index in targets
        if not (index in seen or seen.add(index))
    ]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def arm_inputs(
    config_path: Path,
    payload_base: Path,
    replicate: int,
) -> tuple[object, Path, Path]:
    context = analysis_context(
        config_path=config_path,
        payload_base=payload_base,
    )
    processed = payload_base / "processed" / f"rep{replicate}"
    topology = processed / "protein_ref.pdb"
    trajectory = processed / "prod_protein.xtc"
    for path in (config_path, topology, trajectory):
        if not path.is_file():
            raise FileNotFoundError(path)
    return context, topology, trajectory


def plot_timeseries(
    path_rows: pd.DataFrame,
    output_dir: Path,
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    for arm, sub in path_rows.groupby("arm", sort=False):
        axes[0].plot(
            sub["time_ns"],
            sub["centroid_displacement_from_arm_initial_in_common_frame_A"],
            label=arm,
            linewidth=1.2,
        )
        axes[1].plot(
            sub["time_ns"],
            sub["contacting_receptor_residues"],
            label=arm,
            linewidth=1.2,
        )
    axes[0].set_ylabel("Ligand centroid displacement (A)")
    axes[1].set_ylabel("Contacting receptor residues")
    axes[1].set_xlabel("Time (ns)")
    axes[0].legend()
    axes[0].grid(alpha=0.2)
    axes[1].grid(alpha=0.2)
    fig.suptitle("Ligand movement after common receptor refitting")
    fig.tight_layout()
    fig.savefig(output_dir / "matched_ligand_movement_timeseries.png", dpi=180)
    plt.close(fig)


def plot_common_frame_paths(
    path_rows: pd.DataFrame,
    reference_ca_positions: np.ndarray,
    output_dir: Path,
) -> None:
    projections = (("x_A", "y_A"), ("x_A", "z_A"), ("y_A", "z_A"))
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = plt.get_cmap("tab10")
    for axis, (x_column, y_column) in zip(axes, projections):
        coordinate_index = {"x_A": 0, "y_A": 1, "z_A": 2}
        axis.scatter(
            reference_ca_positions[:, coordinate_index[x_column]],
            reference_ca_positions[:, coordinate_index[y_column]],
            s=3,
            color="0.75",
            alpha=0.35,
            label="WT receptor CA frame 0",
        )
        for arm_index, (arm, sub) in enumerate(
            path_rows.groupby("arm", sort=False)
        ):
            thinned = sub.iloc[::10]
            color = colors(arm_index)
            axis.plot(
                thinned[x_column],
                thinned[y_column],
                color=color,
                alpha=0.75,
                linewidth=1.0,
                label=arm,
            )
            axis.scatter(
                sub.iloc[0][x_column],
                sub.iloc[0][y_column],
                color=color,
                s=45,
                marker="o",
            )
            axis.scatter(
                sub.iloc[-1][x_column],
                sub.iloc[-1][y_column],
                color=color,
                s=55,
                marker="x",
            )
        axis.set_xlabel(x_column.replace("_A", " (A)"))
        axis.set_ylabel(y_column.replace("_A", " (A)"))
        axis.set_aspect("equal", adjustable="datalim")
        axis.grid(alpha=0.15)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=len(labels),
    )
    fig.suptitle(
        "ASCR18 centroid paths in the WT frame-0 receptor reference "
        "(circle=start, x=end)"
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    fig.savefig(output_dir / "matched_centroid_path_common_frame.png", dpi=180)
    plt.close(fig)


def plot_contact_heatmap(
    occupancy: pd.DataFrame,
    output_dir: Path,
    top_n: int = 30,
) -> None:
    if occupancy.empty:
        return
    occupancy = occupancy.copy()
    occupancy["residue"] = (
        occupancy["receptor_resname"] + occupancy["receptor_resid"].astype(str)
    )
    ranking = (
        occupancy.groupby("residue")[["early_occupancy", "late_occupancy"]]
        .max()
        .max(axis=1)
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )
    occupancy = occupancy[occupancy["residue"].isin(ranking)]
    long_rows = []
    for row in occupancy.itertuples(index=False):
        long_rows.extend(
            [
                {
                    "residue": row.residue,
                    "column": f"{row.arm} early",
                    "occupancy": row.early_occupancy,
                },
                {
                    "residue": row.residue,
                    "column": f"{row.arm} late",
                    "occupancy": row.late_occupancy,
                },
            ]
        )
    matrix = (
        pd.DataFrame(long_rows)
        .pivot(index="residue", columns="column", values="occupancy")
        .fillna(0.0)
    )
    matrix = matrix.loc[[residue for residue in ranking if residue in matrix.index]]
    arm_order = list(occupancy["arm"].drop_duplicates())
    column_order = [
        f"{arm} {window}"
        for arm in arm_order
        for window in ("early", "late")
    ]
    matrix = matrix.reindex(columns=column_order, fill_value=0.0)

    fig_height = max(5.5, 0.28 * len(matrix))
    fig, axis = plt.subplots(figsize=(8, fig_height))
    image = axis.imshow(matrix.to_numpy(), aspect="auto", vmin=0, vmax=1)
    axis.set_xticks(range(len(matrix.columns)), labels=matrix.columns, rotation=30)
    axis.set_yticks(range(len(matrix.index)), labels=matrix.index)
    axis.set_title("Receptor residue contact occupancy (4 A direct contact)")
    fig.colorbar(image, ax=axis, label="Frame occupancy")
    fig.tight_layout()
    fig.savefig(output_dir / "matched_residue_contact_occupancy.png", dpi=180)
    plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--arm-config",
        action="append",
        required=True,
        help="Repeat NAME=CONFIG_JSON for each matched arm.",
    )
    parser.add_argument(
        "--arm-payload",
        action="append",
        required=True,
        help="Repeat NAME=RESULT_PAYLOAD_BASE for each matched arm.",
    )
    parser.add_argument("--reference-arm", required=True)
    parser.add_argument("--replicate", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--fit-selection",
        default="segid A and backbone",
        help="Equal-weight receptor fit selection shared by all arms.",
    )
    parser.add_argument(
        "--contact-cutoff-A",
        type=float,
        default=4.0,
        help="Direct receptor-ligand heavy-atom contact cutoff.",
    )
    parser.add_argument("--window-start-ns", type=float, default=100.0)
    parser.add_argument("--stride", type=int, default=1)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.replicate <= 0:
        raise ValueError("--replicate must be positive")
    if args.stride <= 0:
        raise ValueError("--stride must be positive")
    if args.contact_cutoff_A <= 0:
        raise ValueError("--contact-cutoff-A must be positive")

    configs = parse_named_paths(args.arm_config, "--arm-config")
    payloads = parse_named_paths(args.arm_payload, "--arm-payload")
    if set(configs) != set(payloads):
        raise ValueError(
            "--arm-config and --arm-payload labels differ: "
            f"{sorted(configs)} != {sorted(payloads)}"
        )
    if len(configs) < 2:
        raise ValueError("matched ligand-path comparison requires at least two arms")
    if args.reference_arm not in configs:
        raise ValueError(f"unknown --reference-arm {args.reference_arm!r}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reference_context, reference_topology, _ = arm_inputs(
        configs[args.reference_arm],
        payloads[args.reference_arm],
        args.replicate,
    )
    reference = mda.Universe(str(reference_topology))
    reference_fit = reference.select_atoms(args.fit_selection)
    reference_ca = reference.select_atoms(
        f"({reference_context.receptor_selection}) and name CA"
    )
    if len(reference_fit) == 0 or len(reference_ca) == 0:
        raise RuntimeError("empty reference fit or receptor CA selection")
    reference_fit_positions = reference_fit.positions.copy()
    reference_fit_identity = list(zip(reference_fit.resids, reference_fit.names))

    path_rows: list[dict] = []
    occupancy_rows: list[dict] = []
    representative_rows: list[dict] = []
    metadata = {
        "reference_arm": args.reference_arm,
        "replicate": args.replicate,
        "fit_selection": args.fit_selection,
        "contact_cutoff_A": args.contact_cutoff_A,
        "window_start_ns": args.window_start_ns,
        "stride": args.stride,
        "interpretation_boundary": (
            "descriptive structural triage; absolute between-arm positions do "
            "not establish a mutation effect when starting poses differ"
        ),
        "arms": {},
    }

    for arm, config_path in configs.items():
        context, topology, trajectory = arm_inputs(
            config_path,
            payloads[arm],
            args.replicate,
        )
        universe = mda.Universe(str(topology), str(trajectory))
        mobile_fit = universe.select_atoms(args.fit_selection)
        ligand = universe.select_atoms(context.selection_rmsd_selection)
        receptor = universe.select_atoms(
            f"({context.receptor_selection}) and not name H* and not type H"
        )
        if len(mobile_fit) == 0 or len(ligand) == 0 or len(receptor) == 0:
            raise RuntimeError(
                f"empty selection for {arm}: fit={len(mobile_fit)}, "
                f"ligand={len(ligand)}, receptor={len(receptor)}"
            )
        mobile_identity = list(zip(mobile_fit.resids, mobile_fit.names))
        if mobile_identity != reference_fit_identity:
            raise RuntimeError(
                f"fit atom resid/name correspondence differs for {arm}"
            )

        arm_rows: list[dict] = []
        frame_contacts: list[set[tuple[int, str]]] = []
        times: list[float] = []
        centroids: list[np.ndarray] = []
        for timestep in universe.trajectory[:: args.stride]:
            aligned_ligand, fit_rmsd = equal_weight_fit(
                mobile_fit.positions,
                reference_fit_positions,
                ligand.positions,
            )
            centroid = aligned_ligand.mean(axis=0)
            contacts, minimum_distance = contact_residue_set(
                receptor,
                ligand,
                args.contact_cutoff_A,
            )
            current_time = time_ns(timestep)
            centroids.append(centroid)
            times.append(current_time)
            frame_contacts.append(contacts)
            arm_rows.append(
                {
                    "arm": arm,
                    "system": context.system,
                    "replicate": f"rep{args.replicate}",
                    "time_ns": current_time,
                    "x_A": float(centroid[0]),
                    "y_A": float(centroid[1]),
                    "z_A": float(centroid[2]),
                    "fit_rmsd_A": fit_rmsd,
                    "minimum_receptor_ligand_distance_A": minimum_distance,
                    "contacting_receptor_residues": len(contacts),
                    "contact_residues": ";".join(
                        f"{resname}{resid}" for resid, resname in sorted(contacts)
                    ),
                }
            )

        centroid_array = np.asarray(centroids)
        time_array = np.asarray(times)
        displacement = np.linalg.norm(
            centroid_array - centroid_array[0],
            axis=1,
        )
        for row, value in zip(arm_rows, displacement):
            row[
                "centroid_displacement_from_arm_initial_in_common_frame_A"
            ] = float(value)
        path_rows.extend(arm_rows)
        occupancy_rows.extend(
            summarize_contact_occupancy(
                arm,
                time_array,
                frame_contacts,
                args.window_start_ns,
                args.contact_cutoff_A,
            )
        )
        for label, index in representative_indices(
            time_array,
            displacement,
            args.window_start_ns,
        ):
            representative_rows.append(
                {
                    "arm": arm,
                    "frame_label": label,
                    "frame_index": int(index * args.stride),
                    "time_ns": float(time_array[index]),
                    (
                        "centroid_displacement_from_arm_initial_in_common_frame_A"
                    ): float(displacement[index]),
                    "minimum_receptor_ligand_distance_A": arm_rows[index][
                        "minimum_receptor_ligand_distance_A"
                    ],
                    "contacting_receptor_residues": arm_rows[index][
                        "contacting_receptor_residues"
                    ],
                    "contact_residues": arm_rows[index]["contact_residues"],
                }
            )
        metadata["arms"][arm] = {
            "system": context.system,
            "config_path": str(config_path),
            "config_sha256": sha256(config_path),
            "topology_path": str(topology),
            "topology_sha256": sha256(topology),
            "trajectory_path": str(trajectory),
            "trajectory_sha256": sha256(trajectory),
            "frames_analyzed": len(arm_rows),
            "ligand_selection": context.selection_rmsd_selection,
            "receptor_selection": context.receptor_selection,
        }

    path_table = pd.DataFrame(path_rows)
    occupancy_table = pd.DataFrame(occupancy_rows).sort_values(
        ["arm", "late_occupancy", "early_occupancy"],
        ascending=[True, False, False],
    )
    representative_table = pd.DataFrame(representative_rows)
    path_table.to_csv(args.output_dir / "centroid_path.csv", index=False)
    occupancy_table.to_csv(
        args.output_dir / "residue_contact_occupancy.csv",
        index=False,
    )
    representative_table.to_csv(
        args.output_dir / "representative_frames.csv",
        index=False,
    )
    (args.output_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    plot_timeseries(path_table, args.output_dir)
    plot_common_frame_paths(
        path_table,
        reference_ca.positions.copy(),
        args.output_dir,
    )
    plot_contact_heatmap(occupancy_table, args.output_dir)

    for arm, sub in path_table.groupby("arm", sort=False):
        late = sub[sub["time_ns"] >= args.window_start_ns]
        print(
            f"{arm}: final centroid displacement="
            f"{sub.iloc[-1]['centroid_displacement_from_arm_initial_in_common_frame_A']:.3f} A; "
            f"late mean={late['centroid_displacement_from_arm_initial_in_common_frame_A'].mean():.3f} A; "
            f"late mean contact residues="
            f"{late['contacting_receptor_residues'].mean():.3f}"
        )


if __name__ == "__main__":
    main()
