#!/usr/bin/env python
from pathlib import Path
import argparse, sys, numpy as np, pandas as pd
sys.path.insert(0, str(Path('src/modeling/md-analysis').resolve()))
from MDAnalysis.lib.distances import distance_array
import MDAnalysis as mda
from common import add_system_argument, analysis_context, ensure_dir, write_judgement
from plotting import barplot

parser=argparse.ArgumentParser()
add_system_argument(parser)
parser.add_argument('--step', type=int, default=5, help='Frame stride for H-bond analysis')
args=parser.parse_args()
ctx = analysis_context(args.system)
out=ensure_dir(ctx.analysis_base/'hbond')

DONOR_HEAVY = {'N','O','S'}
ACCEPTOR_HEAVY = {'N','O','S'}

def elem(atom):
    e=(getattr(atom, 'element', '') or '').strip().upper()
    if e: return e
    name=atom.name.strip().upper()
    if name.startswith('H'): return 'H'
    return name[0]

def atom_label(a):
    return f"{a.segid}:{a.resname}{a.resid}:{a.name}"

def donor_h_pairs(group):
    pairs=[]
    byres={}
    for a in group:
        byres.setdefault((a.segid,a.resid,a.resname), []).append(a)
    for atoms in byres.values():
        hyd=[a for a in atoms if elem(a)=='H']
        heavy=[a for a in atoms if elem(a) in DONOR_HEAVY]
        if not hyd or not heavy: continue
        hpos=np.array([a.position for a in hyd])
        dpos=np.array([a.position for a in heavy])
        dist=distance_array(hpos, dpos)
        for i,h in enumerate(hyd):
            j=int(dist[i].argmin())
            if dist[i,j] <= 1.35:
                pairs.append((heavy[j].ix, h.ix, atom_label(heavy[j])+'-H:'+h.name))
    return pairs

def acceptors(group):
    return [(a.ix, atom_label(a)) for a in group if elem(a) in ACCEPTOR_HEAVY]

def scan_direction(u, donor_sel, acceptor_sel, rep, tag):
    donors=donor_h_pairs(donor_sel)
    acc=acceptors(acceptor_sel)
    events=[]; n=0
    if not donors or not acc:
        return events, n
    d_idx=np.array([x[0] for x in donors], dtype=int)
    h_idx=np.array([x[1] for x in donors], dtype=int)
    a_idx=np.array([x[0] for x in acc], dtype=int)
    d_labels=[x[2] for x in donors]
    a_labels=[x[1] for x in acc]
    for ts in u.trajectory[::args.step]:
        n+=1
        dpos=u.atoms[d_idx].positions; hpos=u.atoms[h_idx].positions; apos=u.atoms[a_idx].positions
        da=distance_array(dpos, apos)
        cand=np.argwhere(da <= 3.0)
        for i,j in cand:
            v1=dpos[i]-hpos[i]
            v2=apos[j]-hpos[i]
            denom=np.linalg.norm(v1)*np.linalg.norm(v2)
            if denom == 0: continue
            angle=np.degrees(np.arccos(np.clip(np.dot(v1,v2)/denom, -1, 1)))
            if angle >= 150.0:
                events.append({'rep':rep,'direction':tag,'pair':d_labels[i]+' -> '+a_labels[j], 'distance_A':float(da[i,j]), 'angle_deg':float(angle)})
    return events, n

all_events=[]; frame_counts={}
for rep in ctx.replicates():
    u=mda.Universe(str(rep.topology), str(rep.trajectory))
    galpha=u.select_atoms(ctx.galpha_selection)
    iface=u.select_atoms(ctx.receptor_interface_selection)
    if len(galpha) == 0 or len(iface) == 0:
        raise RuntimeError(
            f'empty H-bond selection for {ctx.system} {rep.rep}: '
            f'{ctx.galpha_name}={len(galpha)} {ctx.receptor_name}_interface={len(iface)}'
        )
    receptor_to_galpha=f'{ctx.receptor_name}_iface_to_{ctx.galpha_name}'
    galpha_to_receptor=f'{ctx.galpha_name}_to_{ctx.receptor_name}_iface'
    ev,n=scan_direction(u, iface, galpha, rep.rep, receptor_to_galpha)
    all_events.extend(ev); frame_counts[(rep.rep,receptor_to_galpha)]=n
    u=mda.Universe(str(rep.topology), str(rep.trajectory))
    galpha=u.select_atoms(ctx.galpha_selection)
    iface=u.select_atoms(ctx.receptor_interface_selection)
    ev,n=scan_direction(u, galpha, iface, rep.rep, galpha_to_receptor)
    all_events.extend(ev); frame_counts[(rep.rep,galpha_to_receptor)]=n

if all_events:
    raw=pd.DataFrame(all_events); raw.to_csv(out/'hbond_events.csv', index=False)
    summary=(raw.groupby(['rep','direction','pair']).agg(events=('pair','size'), mean_distance_A=('distance_A','mean'), mean_angle_deg=('angle_deg','mean')).reset_index())
    summary['n_frames']=summary.apply(lambda r: frame_counts.get((r.rep,r.direction), 1), axis=1)
    summary['occupancy']=summary.events/summary.n_frames
    summary=summary.sort_values(['rep','occupancy'], ascending=[True,False])
else:
    summary=pd.DataFrame(columns=['rep','direction','pair','events','mean_distance_A','mean_angle_deg','n_frames','occupancy'])
summary.to_csv(out/'hbond_summary.csv', index=False)
if len(summary):
    agg=summary.groupby('pair').agg(occupancy=('occupancy','mean'), reps=('rep','nunique')).reset_index().sort_values('occupancy', ascending=False)
    barplot(agg, 'pair', 'occupancy', out/'occupancy_top10.png', f'{ctx.label} interface H-bond occupancy (top)', 'Mean occupancy', limit=10)
lines=[]
for rep, sub in summary.groupby('rep'):
    top=sub.occupancy.max() if len(sub) else 0
    lines.append(f"{rep}: top pair occupancy={top:.3f}; reporting threshold >0.10 is project heuristic; manual geometry 3.0 A / 150 deg is MDAnalysis-style, stride={args.step}")
if not lines: lines=['No H-bonds detected with manual 3.0 A / 150 deg geometry under current stride/selection.']
write_judgement(out/'judgement.md', f'{ctx.label} H-bond judgement', lines)
