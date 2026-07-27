#!/usr/bin/env python
"""Compute backbone-fitted RMSD for a config-selected molecular readout.

Interpretive bands are optional and system-scoped. Without a configured
``selection_rmsd_mean_heuristic``, the output is descriptive only.
"""
from pathlib import Path
import argparse
import sys

import numpy as np

sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
import MDAnalysis as mda
from common import (
    add_system_argument,
    analysis_context,
    ensure_dir,
    equal_weight_kabsch_coordinates,
    replicate_plot_path,
    save_csv,
    time_ns,
    write_judgement,
)
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
add_system_argument(parser)
args = parser.parse_args()
ctx = analysis_context(args.system)

metric_dir = ctx.config.get("selection_rmsd_dir", "selection_rmsd")
metric_label = ctx.config.get("selection_rmsd_label", "selection RMSD")
metric_selection_label = ctx.config.get("selection_rmsd_selection_label", "configured selection")

reps = ctx.replicates()
for rep in reps:
    mobile = mda.Universe(str(rep.topology), str(rep.trajectory))
    reference = mda.Universe(str(rep.topology), str(rep.trajectory))
    reference.trajectory[0]
    mobile_fit = mobile.select_atoms(ctx.backbone_selection)
    reference_fit = reference.select_atoms(ctx.backbone_selection)
    mobile_selection = mobile.select_atoms(ctx.selection_rmsd_selection)
    reference_selection = reference.select_atoms(ctx.selection_rmsd_selection)
    for label, mobile_atoms, reference_atoms in [
        ("fit", mobile_fit, reference_fit),
        ("readout", mobile_selection, reference_selection),
    ]:
        if len(mobile_atoms) == 0 or len(reference_atoms) == 0:
            raise RuntimeError(
                f"empty selection-RMSD {label} selection for {ctx.system} {rep.rep}: "
                f"mobile={len(mobile_atoms)} reference={len(reference_atoms)}"
            )
        if len(mobile_atoms) != len(reference_atoms) or not np.array_equal(
            mobile_atoms.indices, reference_atoms.indices
        ):
            raise RuntimeError(
                f"selection-RMSD {label} atom count/order mismatch for "
                f"{ctx.system} {rep.rep}"
            )

out = ensure_dir(ctx.analysis_base / metric_dir)
rows=[]
for rep in reps:
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    ref = mda.Universe(str(rep.topology), str(rep.trajectory))
    ref.trajectory[0]
    mob_fit = u.select_atoms(ctx.backbone_selection); ref_fit = ref.select_atoms(ctx.backbone_selection)
    mob_sel = u.select_atoms(ctx.selection_rmsd_selection); ref_sel = ref.select_atoms(ctx.selection_rmsd_selection)
    ref_fit_pos = ref_fit.positions.copy()
    ref_sel_pos = ref_sel.positions.copy()
    for ts in u.trajectory:
        sel, _ = equal_weight_kabsch_coordinates(
            mob_fit.positions,
            ref_fit_pos,
            mob_sel.positions,
        )
        diff = sel - ref_sel_pos
        val = float(np.sqrt((diff * diff).sum() / len(sel)))
        rows.append({'rep': rep.rep, 'time_ns': time_ns(ts), 'selection_rmsd_A': val})

df = save_csv(out / 'selection_rmsd.csv', rows)
lineplot_by_rep(
    df,
    'time_ns',
    'selection_rmsd_A',
    replicate_plot_path(out, 'selection_rmsd'),
    f'{ctx.label} {metric_label}',
    f'{metric_label} (A)',
)
heuristic = ctx.selection_rmsd_mean_heuristic
if heuristic is not None:
    pass_like_below = float(heuristic['pass_like_below_A'])
    severe_at_or_above = float(heuristic['severe_at_or_above_A'])
    if not pass_like_below < severe_at_or_above:
        raise ValueError(
            'selection_rmsd_mean_heuristic requires '
            'pass_like_below_A < severe_at_or_above_A'
        )

lines=[]
for rep, sub in df.groupby('rep'):
    tail=sub[sub.time_ns >= 100] if (sub.time_ns.max() >= 100) else sub
    m=tail.selection_rmsd_A.mean(); mx=tail.selection_rmsd_A.max()
    if heuristic is None:
        lines.append(
            f"{rep}: {metric_selection_label} after100 mean={m:.2f} A, "
            f"max={mx:.2f} A; descriptive only (no configured interpretation threshold)"
        )
        continue
    if m < pass_like_below:
        status = f'PASS-like by configured project operational <{pass_like_below:g} A heuristic'
    elif m < severe_at_or_above:
        status = (
            'WARN by configured project operational '
            f'{pass_like_below:g}-{severe_at_or_above:g} A heuristic'
        )
    else:
        status = f'SEVERE by configured project operational >={severe_at_or_above:g} A heuristic'
    lines.append(f"{rep}: {metric_selection_label} after100 mean={m:.2f} A, max={mx:.2f} A => {status}")
title_suffix = 'judgement' if heuristic is not None else 'descriptive summary'
write_judgement(out / 'judgement.md', f'{ctx.label} {metric_label} {title_suffix}', lines)
