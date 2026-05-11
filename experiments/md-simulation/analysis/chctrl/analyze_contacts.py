#!/usr/bin/env python
"""Compute chctrl initial interface contact persistence.

Initial residue contacts are Ste2 interface residues vs all Gpa1 residues with
minimum heavy-atom distance <= cutoff in frame 0. Persistence is the fraction of
these initial residue pairs retained over time.
"""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))

import numpy as np
import pandas as pd
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

from common import replicates, analysis_base, ensure_dir, STE2_INTERFACE, GPA1, time_ns, write_judgement
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
parser.add_argument('--stride', type=int, default=5, help='Frame stride; 5 means 0.5 ns for 100 ps XTC spacing')
parser.add_argument('--cutoff', type=float, default=4.0, help='Heavy-atom residue contact cutoff in Angstrom')
args = parser.parse_args()

out = ensure_dir(analysis_base() / 'contacts')
summary_rows = []
contact_rows = []

def heavy(sel):
    return sel.select_atoms('not name H* and not type H')

for rep in replicates():
    print(f'[contacts] {rep.rep} stride={args.stride} cutoff={args.cutoff} A', flush=True)
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    ste = heavy(u.select_atoms(STE2_INTERFACE))
    gpa = heavy(u.select_atoms(GPA1))
    if len(ste) == 0 or len(gpa) == 0:
        raise RuntimeError(f'empty selection for {rep.rep}: ste={len(ste)} gpa={len(gpa)}')

    u.trajectory[0]
    d0 = distance_array(ste.positions, gpa.positions)
    pairs = np.argwhere(d0 <= args.cutoff)
    initial_pairs = set()
    for i, j in pairs:
        initial_pairs.add((ste[i].resid, ste[i].resname, gpa[j].resid, gpa[j].resname))
    if not initial_pairs:
        raise RuntimeError(f'no initial contacts for {rep.rep}')

    # Pre-group atoms by residue for repeated minimum-distance checks.
    ste_res = {}
    gpa_res = {}
    for atom in ste:
        ste_res.setdefault((atom.resid, atom.resname), []).append(atom.ix)
    for atom in gpa:
        gpa_res.setdefault((atom.resid, atom.resname), []).append(atom.ix)

    initial_pairs = sorted(initial_pairs)
    per_pair_counts = {p: 0 for p in initial_pairs}
    n_frames = 0
    for ts in u.trajectory[::args.stride]:
        retained = 0
        for p in initial_pairs:
            sr, sn, gr, gn = p
            si = ste_res[(sr, sn)]
            gi = gpa_res[(gr, gn)]
            min_dist = distance_array(u.atoms[si].positions, u.atoms[gi].positions).min()
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
        sr, sn, gr, gn = p
        contact_rows.append({
            'rep': rep.rep,
            'ste2_resid': sr,
            'ste2_resname': sn,
            'gpa1_resid': gr,
            'gpa1_resname': gn,
            'occupancy': count / n_frames,
            'n_frames': n_frames,
            'cutoff_A': args.cutoff,
            'stride': args.stride,
        })

summary = pd.DataFrame(summary_rows)
summary.to_csv(out / 'contact_persistence.csv', index=False)
contacts = pd.DataFrame(contact_rows).sort_values(['rep', 'occupancy'], ascending=[True, False])
contacts.to_csv(out / 'initial_contact_occupancy.csv', index=False)
lineplot_by_rep(summary, 'time_ns', 'retained_fraction', out / 'contact_persistence_3rep.png', 'chctrl initial contact persistence', 'Retained initial-contact fraction')

lines = []
for rep, sub in summary.groupby('rep'):
    tail = sub[sub.time_ns >= 100] if sub.time_ns.max() >= 100 else sub
    mean_frac = tail.retained_fraction.mean()
    min_frac = tail.retained_fraction.min()
    init_n = int(sub.initial_contacts.iloc[0])
    status = 'supports retention under project majority-retention heuristic >0.50' if mean_frac > 0.50 else 'caveat under project majority-retention heuristic >0.50'
    lines.append(f'{rep}: initial residue contacts={init_n}; after100 mean retained={mean_frac:.3f}, min={min_frac:.3f}; {status}')
write_judgement(out / 'judgement.md', 'chctrl contact persistence judgement', lines)
print('[contacts] done', flush=True)
