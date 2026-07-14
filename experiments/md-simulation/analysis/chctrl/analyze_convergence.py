#!/usr/bin/env python
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
import MDAnalysis as mda
from MDAnalysis.analysis import rms
import pandas as pd
from common import add_system_argument, analysis_context, ensure_dir, time_ns, linear_slope, replicate_plot_path, save_csv, write_judgement
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
add_system_argument(parser)
args = parser.parse_args()
ctx = analysis_context(args.system)

out = ensure_dir(ctx.analysis_base / 'convergence')
rows = []
rg_rows = []
for rep in ctx.replicates():
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    r = rms.RMSD(u, u, select=ctx.backbone_selection, ref_frame=0).run()
    rg_sel = u.select_atoms(ctx.ca_selection)
    for ts in u.trajectory:
        rg_rows.append({'rep': rep.rep, 'time_ns': time_ns(ts), 'rg_A': rg_sel.radius_of_gyration()})
    for frame, t_ps, val in r.results.rmsd[:, :3]:
        rows.append({'rep': rep.rep, 'time_ns': float(t_ps)/1000.0, 'backbone_rmsd_A': float(val)})

df = save_csv(out / 'rmsd_summary.csv', rows)
rg_df = pd.DataFrame(rg_rows)
rg_df.to_csv(out / 'rg_summary.csv', index=False)
lineplot_by_rep(df, 'time_ns', 'backbone_rmsd_A', replicate_plot_path(out, 'rmsd'), f'{ctx.label} backbone RMSD', 'Backbone RMSD (A)')
lineplot_by_rep(rg_df, 'time_ns', 'rg_A', replicate_plot_path(out, 'rg'), f'{ctx.label} protein CA Rg', 'Rg (A)')
lines=[]
for rep, sub in df.groupby('rep'):
    tail=sub[sub.time_ns >= max(100, sub.time_ns.max()-100)]
    slope=linear_slope(tail.time_ns.to_numpy(), tail.backbone_rmsd_A.to_numpy())
    lines.append(f"{rep}: final100/after100 RMSD slope = {slope:.4g} A/ns; mean RMSD = {tail.backbone_rmsd_A.mean():.2f} A")
write_judgement(out / 'judgement.md', f'{ctx.label} convergence judgement', lines)
