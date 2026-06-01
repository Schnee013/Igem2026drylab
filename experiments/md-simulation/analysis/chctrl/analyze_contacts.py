#!/usr/bin/env python
"""Compute initial receptor-Galpha interface contact persistence.

Initial residue contacts are configured receptor-interface residues vs all
configured Galpha residues with minimum heavy-atom distance <= cutoff in frame
0. Persistence is the fraction of these initial residue pairs retained over
time.
"""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))

import numpy as np
import pandas as pd
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

from common import add_system_argument, analysis_context, ensure_dir, time_ns, write_judgement
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
add_system_argument(parser)
parser.add_argument('--stride', type=int, default=5, help='Frame stride; 5 means 0.5 ns for 100 ps XTC spacing')
parser.add_argument('--cutoff', type=float, default=4.0, help='Heavy-atom residue contact cutoff in Angstrom')
args = parser.parse_args()
ctx = analysis_context(args.system)

out = ensure_dir(ctx.analysis_base / 'contacts')
summary_rows = []
contact_rows = []

def heavy(sel):
    return sel.select_atoms('not name H* and not type H')

for rep in ctx.replicates():
    print(f'[contacts] {rep.rep} stride={args.stride} cutoff={args.cutoff} A', flush=True)
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    receptor = heavy(u.select_atoms(ctx.receptor_interface_selection))
    galpha = heavy(u.select_atoms(ctx.galpha_selection))
    if len(receptor) == 0 or len(galpha) == 0:
        raise RuntimeError(
            f'empty selection for {ctx.system} {rep.rep}: '
            f'{ctx.receptor_name}_interface={len(receptor)} {ctx.galpha_name}={len(galpha)}'
        )

    u.trajectory[0]
    d0 = distance_array(receptor.positions, galpha.positions)
    pairs = np.argwhere(d0 <= args.cutoff)
    initial_pairs = set()
    for i, j in pairs:
        initial_pairs.add((receptor[i].resid, receptor[i].resname, galpha[j].resid, galpha[j].resname))
    if not initial_pairs:
        raise RuntimeError(f'no initial contacts for {rep.rep}')

    # Pre-group atoms by residue for repeated minimum-distance checks.
    receptor_res = {}
    galpha_res = {}
    for atom in receptor:
        receptor_res.setdefault((atom.resid, atom.resname), []).append(atom.ix)
    for atom in galpha:
        galpha_res.setdefault((atom.resid, atom.resname), []).append(atom.ix)

    initial_pairs = sorted(initial_pairs)
    per_pair_counts = {p: 0 for p in initial_pairs}
    n_frames = 0
    for ts in u.trajectory[::args.stride]:
        retained = 0
        for p in initial_pairs:
            receptor_resid, receptor_resname, galpha_resid, galpha_resname = p
            receptor_idx = receptor_res[(receptor_resid, receptor_resname)]
            galpha_idx = galpha_res[(galpha_resid, galpha_resname)]
            min_dist = distance_array(u.atoms[receptor_idx].positions, u.atoms[galpha_idx].positions).min()
            if min_dist <= args.cutoff:
                retained += 1
                per_pair_counts[p] += 1
        frac = retained / len(initial_pairs)
        summary_rows.append({
            'rep': rep.rep,
            'time_ns': time_ns(ts),
            'initial_contacts': len(initial_pairs),
            'retained_contacts': retained,
            'retained_fraction': frac,
            'cutoff_A': args.cutoff,
            'stride': args.stride,
        })
        n_frames += 1

    for p, count in per_pair_counts.items():
        receptor_resid, receptor_resname, galpha_resid, galpha_resname = p
        contact_rows.append({
            'rep': rep.rep,
            'receptor_name': ctx.receptor_name,
            'receptor_resid': receptor_resid,
            'receptor_resname': receptor_resname,
            'galpha_name': ctx.galpha_name,
            'galpha_resid': galpha_resid,
            'galpha_resname': galpha_resname,
            'occupancy': count / n_frames,
            'n_frames': n_frames,
            'cutoff_A': args.cutoff,
            'stride': args.stride,
        })

summary = pd.DataFrame(summary_rows)
summary.to_csv(out / 'contact_persistence.csv', index=False)
contacts = pd.DataFrame(contact_rows).sort_values(['rep', 'occupancy'], ascending=[True, False])
contacts.to_csv(out / 'initial_contact_occupancy.csv', index=False)
lineplot_by_rep(summary, 'time_ns', 'retained_fraction', out / 'contact_persistence_3rep.png', f'{ctx.label} initial contact persistence', 'Retained initial-contact fraction')

lines = []
for rep, sub in summary.groupby('rep'):
    tail = sub[sub.time_ns >= 100] if sub.time_ns.max() >= 100 else sub
    mean_frac = tail.retained_fraction.mean()
    min_frac = tail.retained_fraction.min()
    init_n = int(sub.initial_contacts.iloc[0])
    status = 'supports retention under project majority-retention heuristic >0.50' if mean_frac > 0.50 else 'caveat under project majority-retention heuristic >0.50'
    lines.append(f'{rep}: initial residue contacts={init_n}; after100 mean retained={mean_frac:.3f}, min={min_frac:.3f}; {status}')
write_judgement(out / 'judgement.md', f'{ctx.label} contact persistence judgement', lines)
print('[contacts] done', flush=True)
