#!/usr/bin/env python
from pathlib import Path
import argparse
import sys, pandas as pd
sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from common import add_system_argument, analysis_context, ensure_dir, write_judgement
from plotting import lineplot_by_rep

parser = argparse.ArgumentParser()
add_system_argument(parser)
args = parser.parse_args()
ctx = analysis_context(args.system)

out=ensure_dir(ctx.analysis_base/'rmsf')
rows=[]
for rep in ctx.replicates():
    u=mda.Universe(str(rep.topology), str(rep.trajectory))
    ca=u.select_atoms(ctx.ca_selection)
    r=rms.RMSF(ca).run()
    for atom, val in zip(ca, r.results.rmsf):
        rows.append({'rep': rep.rep, 'segid': atom.segid, 'resid': atom.resid, 'resname': atom.resname, 'rmsf_A': float(val), 'axis': f'{atom.segid}:{atom.resid}'})
df=pd.DataFrame(rows); df.to_csv(out/'rmsf.csv', index=False)
# Numeric x per segment for readable plotting.
offsets={segid: i * 600 for i, segid in enumerate(ctx.plot_segids)}
plot=df.copy()
plot['x']=plot.apply(lambda r: r.resid + offsets.get(r.segid, 1200), axis=1)
lineplot_by_rep(plot, 'x', 'rmsf_A', out/'rmsf_baseline.png', f'{ctx.label} CA RMSF baseline', 'CA RMSF (A)')
if ctx.junction_rmsf_regions:
    regions=', '.join(ctx.junction_rmsf_regions)
    lines=[f'RMSF baseline generated; configured junction/graft regions for follow-up comparison: {regions}.']
else:
    lines=['RMSF baseline generated; no region-specific RMSF interpretation threshold is configured for this system.']
write_judgement(out/'judgement.md', f'{ctx.label} RMSF baseline', lines)
