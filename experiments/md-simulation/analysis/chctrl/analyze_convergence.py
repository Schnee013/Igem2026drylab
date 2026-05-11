#!/usr/bin/env python
from pathlib import Path
import sys
sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from common import replicates, analysis_base, ensure_dir, BACKBONE, CA, time_ns, linear_slope, save_csv, write_judgement
from plotting import lineplot_by_rep

out = ensure_dir(analysis_base() / 'convergence')
rows = []
for rep in replicates():
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    r = rms.RMSD(u, u, select=BACKBONE, ref_frame=0).run()
    rg_sel = u.select_atoms(CA)
    rg = []
    for ts in u.trajectory:
        rg.append({'rep': rep.rep, 'time_ns': time_ns(ts), 'rg_A': rg_sel.radius_of_gyration()})
    for frame, t_ps, val in r.results.rmsd[:, :3]:
        rows.append({'rep': rep.rep, 'time_ns': float(t_ps)/1000.0, 'backbone_rmsd_A': float(val)})
    save_csv(out / f'{rep.rep}_rg.csv', rg)

df = save_csv(out / 'rmsd_summary.csv', rows)
rg_df = __import__('pandas').concat([__import__('pandas').read_csv(out / f'rep{i}_rg.csv') for i in (1,2,3)])
rg_df.to_csv(out / 'rg_summary.csv', index=False)
lineplot_by_rep(df, 'time_ns', 'backbone_rmsd_A', out / 'rmsd_3rep.png', 'chctrl backbone RMSD', 'Backbone RMSD (A)')
lineplot_by_rep(rg_df, 'time_ns', 'rg_A', out / 'rg_3rep.png', 'chctrl protein CA Rg', 'Rg (A)')
lines=[]
for rep, sub in df.groupby('rep'):
    tail=sub[sub.time_ns >= max(100, sub.time_ns.max()-100)]
    slope=linear_slope(tail.time_ns.to_numpy(), tail.backbone_rmsd_A.to_numpy())
    lines.append(f"{rep}: final100/after100 RMSD slope = {slope:.4g} A/ns; mean RMSD = {tail.backbone_rmsd_A.mean():.2f} A")
write_judgement(out / 'judgement.md', 'chctrl convergence judgement', lines)
