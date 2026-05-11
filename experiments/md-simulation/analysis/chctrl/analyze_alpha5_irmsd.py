#!/usr/bin/env python
from pathlib import Path
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
import MDAnalysis as mda
from MDAnalysis.analysis import align
from common import replicates, analysis_base, ensure_dir, BACKBONE, ALPHA5, time_ns, save_csv, write_judgement
from plotting import lineplot_by_rep

out = ensure_dir(analysis_base() / 'alpha5_irmsd')
rows=[]
for rep in replicates():
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    ref = mda.Universe(str(rep.topology), str(rep.trajectory))
    ref.trajectory[0]
    mob_fit = u.select_atoms(BACKBONE); ref_fit = ref.select_atoms(BACKBONE)
    mob_a5 = u.select_atoms(ALPHA5); ref_a5 = ref.select_atoms(ALPHA5)
    ref_fit_com = ref_fit.center_of_mass(); ref_fit_pos = ref_fit.positions - ref_fit_com
    ref_a5_pos = ref_a5.positions - ref_fit_com
    for ts in u.trajectory:
        mob_com = mob_fit.center_of_mass()
        R, _ = align.rotation_matrix(mob_fit.positions - mob_com, ref_fit_pos)
        a5 = np.dot(mob_a5.positions - mob_com, R)
        diff = a5 - ref_a5_pos
        val = float(np.sqrt((diff * diff).sum() / len(a5)))
        rows.append({'rep': rep.rep, 'time_ns': time_ns(ts), 'alpha5_irmsd_A': val})

df = save_csv(out / 'a5_irmsd.csv', rows)
lineplot_by_rep(df, 'time_ns', 'alpha5_irmsd_A', out / 'a5_irmsd_3rep.png', 'chctrl alpha5 iRMSD', 'alpha5 iRMSD (A)')
lines=[]
for rep, sub in df.groupby('rep'):
    tail=sub[sub.time_ns >= 100] if (sub.time_ns.max() >= 100) else sub
    m=tail.alpha5_irmsd_A.mean(); mx=tail.alpha5_irmsd_A.max()
    status='PASS-like by project operational <3 A band' if m < 3 else ('WARN by project operational 3-5 A band' if m < 5 else 'SEVERE by project operational >5 A band')
    lines.append(f"{rep}: after100 mean={m:.2f} A, max={mx:.2f} A => {status}")
write_judgement(out / 'judgement.md', 'chctrl alpha5 iRMSD judgement', lines)
