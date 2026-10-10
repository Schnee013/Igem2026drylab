#!/usr/bin/env python
from __future__ import annotations

from pathlib import Path
import argparse
import sys

import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path("src/modeling/md-analysis").resolve()))
from common import add_system_argument, analysis_context, ensure_dir, write_judgement, in_time_window, time_ns
from plotting import barplot


DONOR_HEAVY = {"N", "O", "S"}
ACCEPTOR_HEAVY = {"N", "O", "S"}
EVENT_COLUMNS = ["rep", "direction", "pair", "distance_A", "angle_deg", "time_ns"]
SUMMARY_COLUMNS = [
    "rep",
    "direction",
    "pair",
    "events",
    "mean_distance_A",
    "mean_angle_deg",
    "n_frames",
    "occupancy",
]
AGGREGATE_COLUMNS = [
    "direction",
    "pair",
    "occupancy",
    "observed_reps",
    "configured_reps",
]


def elem(atom):
    element = (getattr(atom, "element", "") or "").strip().upper()
    if element:
        return element
    name = atom.name.strip().upper()
    if name.startswith("H"):
        return "H"
    return name[0]


def atom_label(atom):
    return f"{atom.segid}:{atom.resname}{atom.resid}:{atom.name}"


def donor_h_pairs(group):
    pairs = []
    by_residue = {}
    for atom in group:
        by_residue.setdefault((atom.segid, atom.resid, atom.resname), []).append(atom)
    for atoms in by_residue.values():
        hydrogens = [atom for atom in atoms if elem(atom) == "H"]
        heavy_atoms = [atom for atom in atoms if elem(atom) in DONOR_HEAVY]
        if not hydrogens or not heavy_atoms:
            continue
        hydrogen_positions = np.array([atom.position for atom in hydrogens])
        heavy_positions = np.array([atom.position for atom in heavy_atoms])
        distances = distance_array(hydrogen_positions, heavy_positions)
        for index, hydrogen in enumerate(hydrogens):
            nearest = int(distances[index].argmin())
            if distances[index, nearest] <= 1.35:
                pairs.append(
                    (
                        heavy_atoms[nearest].ix,
                        hydrogen.ix,
                        atom_label(heavy_atoms[nearest]) + "-H:" + hydrogen.name,
                    )
                )
    return pairs


def acceptors(group):
    return [(atom.ix, atom_label(atom)) for atom in group if elem(atom) in ACCEPTOR_HEAVY]


def scan_direction(universe, donor_selection, acceptor_selection, rep, tag, step, window=None):
    donors = donor_h_pairs(donor_selection)
    acceptor_atoms = acceptors(acceptor_selection)
    events = []
    frame_count = 0
    if not donors or not acceptor_atoms:
        return events, frame_count

    donor_indexes = np.array([item[0] for item in donors], dtype=int)
    hydrogen_indexes = np.array([item[1] for item in donors], dtype=int)
    acceptor_indexes = np.array([item[0] for item in acceptor_atoms], dtype=int)
    donor_labels = [item[2] for item in donors]
    acceptor_labels = [item[1] for item in acceptor_atoms]

    for ts in universe.trajectory[::step]:
        if not in_time_window(ts, window):
            continue
        frame_count += 1
        donor_positions = universe.atoms[donor_indexes].positions
        hydrogen_positions = universe.atoms[hydrogen_indexes].positions
        acceptor_positions = universe.atoms[acceptor_indexes].positions
        donor_acceptor_distances = distance_array(donor_positions, acceptor_positions)
        candidates = np.argwhere(donor_acceptor_distances <= 3.0)
        for donor_index, acceptor_index in candidates:
            donor_vector = donor_positions[donor_index] - hydrogen_positions[donor_index]
            acceptor_vector = acceptor_positions[acceptor_index] - hydrogen_positions[donor_index]
            denominator = np.linalg.norm(donor_vector) * np.linalg.norm(acceptor_vector)
            if denominator == 0:
                continue
            angle = np.degrees(
                np.arccos(
                    np.clip(
                        np.dot(donor_vector, acceptor_vector) / denominator,
                        -1,
                        1,
                    )
                )
            )
            if angle >= 150.0:
                events.append(
                    {
                        "rep": rep,
                        "direction": tag,
                        "pair": donor_labels[donor_index]
                        + " -> "
                        + acceptor_labels[acceptor_index],
                        "distance_A": float(donor_acceptor_distances[donor_index, acceptor_index]),
                        "angle_deg": float(angle),
                        "time_ns": time_ns(ts),
                    }
                )
    return events, frame_count


def summarize_events(all_events, frame_counts):
    """Build deterministic raw/summary tables, including fixed empty schemas."""
    raw = pd.DataFrame(all_events, columns=EVENT_COLUMNS)
    if raw.empty:
        return raw, pd.DataFrame(columns=SUMMARY_COLUMNS)

    summary = (
        raw.groupby(["rep", "direction", "pair"])
        .agg(
            events=("pair", "size"),
            mean_distance_A=("distance_A", "mean"),
            mean_angle_deg=("angle_deg", "mean"),
        )
        .reset_index()
    )
    summary["n_frames"] = summary.apply(
        lambda row: frame_counts.get((row.rep, row.direction), 1), axis=1
    )
    summary["occupancy"] = summary.events / summary.n_frames
    return raw, summary.sort_values(
        ["rep", "occupancy"], ascending=[True, False]
    )


def aggregate_pair_occupancy(summary, rep_labels):
    """Mean each direction/pair over every configured replicate, absent = zero."""
    if len(rep_labels) != len(set(rep_labels)):
        raise ValueError(f"duplicate configured replicate labels: {rep_labels}")
    if summary.empty:
        return pd.DataFrame(columns=AGGREGATE_COLUMNS)

    pairs = summary[["direction", "pair"]].drop_duplicates()
    complete = pd.DataFrame({"rep": rep_labels}).merge(pairs, how="cross")
    complete = complete.merge(
        summary[["rep", "direction", "pair", "occupancy"]],
        on=["rep", "direction", "pair"],
        how="left",
        validate="one_to_one",
    )
    complete["observed"] = complete.occupancy.notna()
    complete["occupancy"] = complete.occupancy.fillna(0.0)
    return (
        complete.groupby(["direction", "pair"])
        .agg(
            occupancy=("occupancy", "mean"),
            observed_reps=("observed", "sum"),
            configured_reps=("rep", "nunique"),
        )
        .reset_index()
        .sort_values("occupancy", ascending=False)
    )


def interpretation_contract(heuristic):
    if heuristic is None:
        return (
            "descriptive only (no configured occupancy interpretation threshold)",
            "descriptive summary",
        )
    occupancy_above = float(heuristic["occupancy_above"])
    if not 0.0 <= occupancy_above <= 1.0:
        raise ValueError(
            "hbond_occupancy_reporting_heuristic.occupancy_above "
            "must be between 0 and 1"
        )
    return (
        f"configured project operational reporting heuristic >{occupancy_above:g}; "
        "CSV remains unfiltered",
        "judgement",
    )


def judgement_lines(summary, rep_labels, heuristic, step):
    interpretation, title_suffix = interpretation_contract(heuristic)
    lines = []
    for rep in rep_labels:
        rep_summary = summary.loc[summary.rep == rep]
        top = float(rep_summary.occupancy.max()) if not rep_summary.empty else 0.0
        detection_note = "no detected pairs; " if rep_summary.empty else ""
        lines.append(
            f"{rep}: {detection_note}top pair occupancy={top:.3f}; {interpretation}; "
            f"manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride={step}"
        )
    return lines, title_suffix


def write_outputs(out, raw, summary, aggregate, rep_labels, label, heuristic, step):
    """Replace the complete H-bond evidence set, removing stale empty-run plots."""
    lines, title_suffix = judgement_lines(
        summary, rep_labels, heuristic=heuristic, step=step
    )
    raw.to_csv(out / "hbond_events.csv", index=False)
    summary.to_csv(out / "hbond_summary.csv", index=False)
    aggregate.to_csv(out / "hbond_pair_mean_occupancy.csv", index=False)

    plot_path = out / "occupancy_top10.png"
    if aggregate.empty:
        plot_path.unlink(missing_ok=True)
    else:
        barplot(
            aggregate,
            "pair",
            "occupancy",
            plot_path,
            f"{label} interface H-bond occupancy (configured-rep mean)",
            "Mean occupancy (absent pairs = 0)",
            limit=10,
        )

    write_judgement(out / "judgement.md", f"{label} H-bond {title_suffix}", lines)


def parse_args():
    parser = argparse.ArgumentParser()
    add_system_argument(parser)
    parser.add_argument("--step", type=int, default=5, help="Frame stride for H-bond analysis")
    args = parser.parse_args()
    if args.step <= 0:
        parser.error("--step must be a positive integer")
    return args


def main():
    args = parse_args()
    context = analysis_context(args.system)
    out = ensure_dir(context.analysis_base / "hbond")
    configured_reps = context.replicates()
    rep_labels = [rep.rep for rep in configured_reps]
    all_events = []
    frame_counts = {}

    for rep in configured_reps:
        universe = mda.Universe(str(rep.topology), str(rep.trajectory))
        partner = universe.select_atoms(context.galpha_selection)
        interface = universe.select_atoms(context.receptor_interface_selection)
        if len(partner) == 0 or len(interface) == 0:
            raise RuntimeError(
                f"empty H-bond selection for {context.system} {rep.rep}: "
                f"{context.galpha_name}={len(partner)} "
                f"{context.receptor_name}_interface={len(interface)}"
            )

        receptor_to_partner = (
            f"{context.receptor_name}_iface_to_{context.galpha_name}"
        )
        partner_to_receptor = (
            f"{context.galpha_name}_to_{context.receptor_name}_iface"
        )
        events, frame_count = scan_direction(
            universe,
            interface,
            partner,
            rep.rep,
            receptor_to_partner,
            args.step,
            context.window('occupancy_window_ns'),
        )
        all_events.extend(events)
        frame_counts[(rep.rep, receptor_to_partner)] = frame_count

        universe = mda.Universe(str(rep.topology), str(rep.trajectory))
        partner = universe.select_atoms(context.galpha_selection)
        interface = universe.select_atoms(context.receptor_interface_selection)
        events, frame_count = scan_direction(
            universe,
            partner,
            interface,
            rep.rep,
            partner_to_receptor,
            args.step,
            context.window('occupancy_window_ns'),
        )
        all_events.extend(events)
        frame_counts[(rep.rep, partner_to_receptor)] = frame_count

    raw, summary = summarize_events(all_events, frame_counts)
    if context.window('occupancy_window_ns') is not None:
        (out / 'sampling_window.json').write_text(
            __import__('json').dumps({'window_ns': context.window('occupancy_window_ns'),
                                     'frame_counts': {str(k): v for k,v in frame_counts.items()},
                                     'stride': args.step}, indent=2) + '\n'
        )
    aggregate = aggregate_pair_occupancy(summary, rep_labels)
    write_outputs(
        out,
        raw,
        summary,
        aggregate,
        rep_labels,
        context.label,
        context.hbond_occupancy_reporting_heuristic,
        args.step,
    )


if __name__ == "__main__":
    main()
