#!/usr/bin/env python
"""Compute receptor-Galpha buried surface area from protein-only trajectories.

Uses MDTraj Shrake-Rupley SASA on stride-sampled frames:
BSA = SASA(Galpha) + SASA(receptor) - SASA(complex)
Units are converted from nm^2 to A^2.
"""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))

import mdtraj as md
import MDAnalysis as mda
import pandas as pd

from common import add_system_argument, analysis_context, ensure_dir, replicate_plot_path, write_judgement
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
add_system_argument(parser)
parser.add_argument('--stride', type=int, default=5, help='Frame stride; 5 means 0.5 ns for 100 ps XTC spacing')
parser.add_argument('--n-sphere-points', type=int, default=240, help='Shrake-Rupley sphere points; lower is faster, relative BSA trend is the target')
args = parser.parse_args()
ctx = analysis_context(args.system)

out = ensure_dir(ctx.analysis_base / 'bsa')
rows = []
for rep in ctx.replicates():
    print(f'[bsa] loading {rep.rep} stride={args.stride}', flush=True)
    u = mda.Universe(str(rep.topology))
    galpha_idx = u.select_atoms(ctx.galpha_selection).indices
    receptor_idx = u.select_atoms(ctx.receptor_selection).indices
    if len(galpha_idx) == 0 or len(receptor_idx) == 0:
        raise RuntimeError(
            f'empty BSA selection for {ctx.system} {rep.rep}: '
            f'{ctx.galpha_name}={len(galpha_idx)} {ctx.receptor_name}={len(receptor_idx)}'
        )

    traj = md.load_xtc(str(rep.trajectory), top=str(rep.topology), stride=args.stride)
    time_ns = traj.time / 1000.0

    complex_sasa = md.shrake_rupley(traj, mode='atom', n_sphere_points=args.n_sphere_points).sum(axis=1)
    galpha_sasa = md.shrake_rupley(traj.atom_slice(galpha_idx), mode='atom', n_sphere_points=args.n_sphere_points).sum(axis=1)
    receptor_sasa = md.shrake_rupley(traj.atom_slice(receptor_idx), mode='atom', n_sphere_points=args.n_sphere_points).sum(axis=1)
    bsa_a2 = (galpha_sasa + receptor_sasa - complex_sasa) * 100.0

    initial = float(bsa_a2[0]) if len(bsa_a2) else float('nan')
    for t, val in zip(time_ns, bsa_a2):
        rows.append({
            'rep': rep.rep,
            'time_ns': float(t),
            'bsa_A2': float(val),
            'bsa_fraction_of_initial': float(val / initial) if initial else float('nan'),
            'stride': args.stride,
            'n_sphere_points': args.n_sphere_points,
        })

df = pd.DataFrame(rows)
df.to_csv(out / 'bsa.csv', index=False)
lineplot_by_rep(df, 'time_ns', 'bsa_A2', replicate_plot_path(out, 'bsa'), f'{ctx.label} {ctx.receptor_name}-{ctx.galpha_name} BSA', 'BSA (A^2)')
lineplot_by_rep(df, 'time_ns', 'bsa_fraction_of_initial', replicate_plot_path(out, 'bsa_fraction'), f'{ctx.label} BSA fraction of initial', 'BSA / initial')

heuristic = ctx.bsa_mean_fraction_heuristic
if heuristic is not None:
    retention_at_or_above = float(heuristic['supports_retention_at_or_above'])
    if not 0.0 <= retention_at_or_above <= 1.0:
        raise ValueError(
            'bsa_mean_fraction_heuristic.supports_retention_at_or_above '
            'must be between 0 and 1'
        )
lines = []
for rep, sub in df.groupby('rep'):
    tail = sub[sub.time_ns >= 100] if sub.time_ns.max() >= 100 else sub
    mean_frac = tail.bsa_fraction_of_initial.mean()
    min_frac = tail.bsa_fraction_of_initial.min()
    if heuristic is None:
        lines.append(
            f'{rep}: after100 mean fraction={mean_frac:.3f}, min fraction={min_frac:.3f}; '
            'descriptive only (no configured retention threshold)'
        )
        continue
    status = (
        f'supports retention under configured project operational >={retention_at_or_above:g} heuristic'
        if mean_frac >= retention_at_or_above
        else f'caveat under configured project operational >={retention_at_or_above:g} heuristic'
    )
    lines.append(f'{rep}: after100 mean fraction={mean_frac:.3f}, min fraction={min_frac:.3f}; {status}')
title_suffix = 'judgement' if heuristic is not None else 'descriptive summary'
write_judgement(out / 'judgement.md', f'{ctx.label} BSA {title_suffix}', lines)
print('[bsa] done', flush=True)
