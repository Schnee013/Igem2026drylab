#!/usr/bin/env python
"""Compute chctrl Ste2-Gpa1 buried surface area from protein-only trajectories.

Uses MDTraj Shrake-Rupley SASA on stride-sampled frames:
BSA = SASA(Gpa1) + SASA(Ste2) - SASA(complex)
Units are converted from nm^2 to A^2.
"""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))

import mdtraj as md
import MDAnalysis as mda
import pandas as pd

from common import replicates, analysis_base, ensure_dir, write_judgement
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
parser.add_argument('--stride', type=int, default=5, help='Frame stride; 5 means 0.5 ns for 100 ps XTC spacing')
parser.add_argument('--n-sphere-points', type=int, default=240, help='Shrake-Rupley sphere points; lower is faster, relative BSA trend is the target')
args = parser.parse_args()

out = ensure_dir(analysis_base() / 'bsa')
rows = []
for rep in replicates():
    print(f'[bsa] loading {rep.rep} stride={args.stride}', flush=True)
    u = mda.Universe(str(rep.topology))
    gpa_idx = u.select_atoms('segid PROA').indices
    ste_idx = u.select_atoms('segid PROB').indices

    traj = md.load_xtc(str(rep.trajectory), top=str(rep.topology), stride=args.stride)
    time_ns = traj.time / 1000.0

    complex_sasa = md.shrake_rupley(traj, mode='atom', n_sphere_points=args.n_sphere_points).sum(axis=1)
    gpa_sasa = md.shrake_rupley(traj.atom_slice(gpa_idx), mode='atom', n_sphere_points=args.n_sphere_points).sum(axis=1)
    ste_sasa = md.shrake_rupley(traj.atom_slice(ste_idx), mode='atom', n_sphere_points=args.n_sphere_points).sum(axis=1)
    bsa_a2 = (gpa_sasa + ste_sasa - complex_sasa) * 100.0

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
lineplot_by_rep(df, 'time_ns', 'bsa_A2', out / 'bsa_3rep.png', 'chctrl Ste2-Gpa1 BSA', 'BSA (A^2)')
lineplot_by_rep(df, 'time_ns', 'bsa_fraction_of_initial', out / 'bsa_fraction_3rep.png', 'chctrl BSA fraction of initial', 'BSA / initial')

lines = []
for rep, sub in df.groupby('rep'):
    tail = sub[sub.time_ns >= 100] if sub.time_ns.max() >= 100 else sub
    mean_frac = tail.bsa_fraction_of_initial.mean()
    min_frac = tail.bsa_fraction_of_initial.min()
    status = 'supports retention under project operational >=0.80 heuristic' if mean_frac >= 0.80 else 'caveat under project operational >=0.80 heuristic'
    lines.append(f'{rep}: after100 mean fraction={mean_frac:.3f}, min fraction={min_frac:.3f}; {status}')
write_judgement(out / 'judgement.md', 'chctrl BSA judgement', lines)
print('[bsa] done', flush=True)
