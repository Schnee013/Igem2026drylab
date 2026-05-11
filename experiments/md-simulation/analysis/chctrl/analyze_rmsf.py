#!/usr/bin/env python
from pathlib import Path
import sys, pandas as pd
sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from common import replicates, analysis_base, ensure_dir, CA, write_judgement
from plotting import lineplot_by_rep

out=ensure_dir(analysis_base()/'rmsf')
rows=[]
for rep in replicates():
    u=mda.Universe(str(rep.topology), str(rep.trajectory))
    ca=u.select_atoms(CA)
    r=rms.RMSF(ca).run()
    for atom, val in zip(ca, r.results.rmsf):
        rows.append({'rep': rep.rep, 'segid': atom.segid, 'resid': atom.resid, 'resname': atom.resname, 'rmsf_A': float(val), 'axis': f'{atom.segid}:{atom.resid}'})
df=pd.DataFrame(rows); df.to_csv(out/'rmsf.csv', index=False)
# Numeric x per segment for readable plotting.
plot=df.copy(); plot['x']=plot.apply(lambda r: r.resid + (0 if r.segid=='PROA' else 500), axis=1)
lineplot_by_rep(plot, 'x', 'rmsf_A', out/'rmsf_baseline.png', 'chctrl CA RMSF baseline (PROA then PROB+500)', 'CA RMSF (A)')
write_judgement(out/'judgement.md', 'chctrl RMSF baseline', ['RMSF baseline generated for future Ch-1/2/4 junction comparison; chctrl itself has no junction threshold.'])
