#!/usr/bin/env python
"""Compute initial receptor-partner interface contact persistence.

Initial residue contacts are configured receptor-interface residues vs all
configured partner residues with minimum heavy-atom distance <= cutoff in
frame 0. Persistence is the fraction of these initial residue pairs retained
over time.
"""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))

import numpy as np
import pandas as pd
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

from common import add_system_argument, analysis_context, ensure_dir, time_ns, replicate_plot_path, write_judgement
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
    partner = heavy(u.select_atoms(ctx.galpha_selection))
    if len(receptor) == 0 or len(partner) == 0:
        raise RuntimeError(
            f'empty selection for {ctx.system} {rep.rep}: '
            f'{ctx.receptor_name}_interface={len(receptor)} '
            f'{ctx.interaction_partner_role}={len(partner)}'
        )

    u.trajectory[0]
    d0 = distance_array(receptor.positions, partner.positions)
    pairs = np.argwhere(d0 <= args.cutoff)
    initial_pairs = set()
    for i, j in pairs:
        initial_pairs.add((receptor[i].resid, receptor[i].resname, partner[j].resid, partner[j].resname))
    if not initial_pairs:
        raise RuntimeError(f'no initial contacts for {rep.rep}')

    # Pre-group atoms by residue for repeated minimum-distance checks.
    receptor_res = {}
    partner_res = {}
    for atom in receptor:
        receptor_res.setdefault((atom.resid, atom.resname), []).append(atom.ix)
    for atom in partner:
        partner_res.setdefault((atom.resid, atom.resname), []).append(atom.ix)

    initial_pairs = sorted(initial_pairs)
    per_pair_counts = {p: 0 for p in initial_pairs}
    n_frames = 0
    for ts in u.trajectory[::args.stride]:
        retained = 0
        for p in initial_pairs:
            receptor_resid, receptor_resname, partner_resid, partner_resname = p
            receptor_idx = receptor_res[(receptor_resid, receptor_resname)]
            partner_idx = partner_res[(partner_resid, partner_resname)]
            min_dist = distance_array(u.atoms[receptor_idx].positions, u.atoms[partner_idx].positions).min()
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
        receptor_resid, receptor_resname, partner_resid, partner_resname = p
        row = {
            'rep': rep.rep,
            'receptor_name': ctx.receptor_name,
            'receptor_resid': receptor_resid,
            'receptor_resname': receptor_resname,
            'partner_role': ctx.interaction_partner_role,
            'partner_name': ctx.galpha_name,
            'partner_resid': partner_resid,
            'partner_resname': partner_resname,
            'occupancy': count / n_frames,
            'n_frames': n_frames,
            'cutoff_A': args.cutoff,
            'stride': args.stride,
        }
        # Preserve the historical chimeric-output columns only when the
        # configured interaction partner is actually a Galpha protein.
        if ctx.interaction_partner_role == 'galpha':
            row.update({
                'galpha_name': ctx.galpha_name,
                'galpha_resid': partner_resid,
                'galpha_resname': partner_resname,
            })
        contact_rows.append(row)

summary = pd.DataFrame(summary_rows)
summary.to_csv(out / 'contact_persistence.csv', index=False)
contacts = pd.DataFrame(contact_rows).sort_values(['rep', 'occupancy'], ascending=[True, False])
contacts.to_csv(out / 'initial_contact_occupancy.csv', index=False)
lineplot_by_rep(summary, 'time_ns', 'retained_fraction', replicate_plot_path(out, 'contact_persistence'), f'{ctx.label} initial contact persistence', 'Retained initial-contact fraction')

heuristic = ctx.contact_mean_fraction_heuristic
if heuristic is not None:
    retention_above = float(heuristic['supports_retention_above'])
    if not 0.0 <= retention_above <= 1.0:
        raise ValueError(
            'contact_mean_fraction_heuristic.supports_retention_above '
            'must be between 0 and 1'
        )
lines = []
for rep, sub in summary.groupby('rep'):
    tail = sub[sub.time_ns >= 100] if sub.time_ns.max() >= 100 else sub
    mean_frac = tail.retained_fraction.mean()
    min_frac = tail.retained_fraction.min()
    init_n = int(sub.initial_contacts.iloc[0])
    if heuristic is None:
        lines.append(
            f'{rep}: initial residue contacts={init_n}; after100 mean retained={mean_frac:.3f}, '
            f'min={min_frac:.3f}; descriptive only (no configured retention threshold)'
        )
        continue
    status = (
        f'supports retention under configured project operational >{retention_above:g} heuristic'
        if mean_frac > retention_above
        else f'caveat under configured project operational >{retention_above:g} heuristic'
    )
    lines.append(f'{rep}: initial residue contacts={init_n}; after100 mean retained={mean_frac:.3f}, min={min_frac:.3f}; {status}')
title_suffix = 'judgement' if heuristic is not None else 'descriptive summary'
write_judgement(out / 'judgement.md', f'{ctx.label} contact persistence {title_suffix}', lines)
print('[contacts] done', flush=True)
