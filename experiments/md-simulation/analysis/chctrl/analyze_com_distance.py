#!/usr/bin/env python
from pathlib import Path
import argparse
import sys, numpy as np
sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
import MDAnalysis as mda
from common import add_system_argument, analysis_context, ensure_dir, time_ns, linear_slope, save_csv, write_judgement
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
add_system_argument(parser)
args = parser.parse_args()
ctx = analysis_context(args.system)

out = ensure_dir(ctx.analysis_base / 'com_distance')
rows=[]
for rep in ctx.replicates():
    u=mda.Universe(str(rep.topology), str(rep.trajectory))
    last5=u.select_atoms(ctx.galpha_ect_selection)
    clusters={name: u.select_atoms(spec) for name, spec in ctx.receptor_interface_clusters.items()}
    for ts in u.trajectory:
        c2=last5.center_of_mass()
        for name, sel in clusters.items():
            rows.append({'rep': rep.rep, 'time_ns': time_ns(ts), 'cluster': name, 'distance_A': float(np.linalg.norm(sel.center_of_mass()-c2))})

df=save_csv(out/'com.csv', rows)
for cluster, sub in df.groupby('cluster'):
    lineplot_by_rep(sub, 'time_ns', 'distance_A', out/f'{cluster}_3rep.png', f'{ctx.label} COM distance {cluster} to {ctx.galpha_name} eCT', 'COM distance (A)')
lines=[]
for (rep, cluster), sub in df.groupby(['rep','cluster']):
    tail=sub[sub.time_ns >= 100] if sub.time_ns.max() >= 100 else sub
    slope=linear_slope(tail.time_ns.to_numpy(), tail.distance_A.to_numpy())
    lines.append(f"{rep} {cluster}: after100 slope={slope:.4g} A/ns; mean={tail.distance_A.mean():.2f} A (non-monotonic/near-zero slope preferred)")
write_judgement(out/'judgement.md', f'{ctx.label} COM distance judgement', lines)
