#!/usr/bin/env python
"""Independent NumPy checks of local-mechanism tables and representative frames."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np


def rows(path):
    with Path(path).open() as f:return list(csv.DictReader(f))


def independent_fit(mobile, reference, xyz):
    mc=mobile.mean(0);rc=reference.mean(0)
    U,_,V=np.linalg.svd((mobile-mc).T @ (reference-rc))
    D=np.diag([1,1,np.linalg.det(U@V)])
    return (xyz-mc) @ U @ D @ V + rc


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--delivery',required=True)
    ap.add_argument('--previous',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();cfg=json.loads(Path(a.config).read_text());base=Path(a.delivery);previous=Path(a.previous)
    checks=[]
    def record(case,test,value,tolerance):
        checks.append(dict(case=case,test=test,error=float(value),tolerance=float(tolerance),pass_check=bool(value<=tolerance)))
    # A nontrivial rigid transform must disappear under the independent fit.
    ref=np.array([[0.,0,0],[1,0,0],[0,2,0],[0,0,3]])
    R=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    mob=ref@R+np.array([3,5,7])
    record('synthetic','rigid_transform',np.max(abs(independent_fit(mob,ref,mob)-ref)),1e-10)
    for c in cfg['cases']:
        case=c['id'];p=base/case;done=json.loads((p/'completion.json').read_text())
        if done['status']!='complete':raise ValueError(case)
        f=rows(p/'frame_metrics.csv');times=np.array([float(r['time_ns']) for r in f])
        record(case,'sample_grid',np.max(abs(times-np.arange(1001)*.1)),1e-7)
        for r in f:
            if not all(np.isfinite(float(v)) for k,v in r.items() if k!='case'):raise ValueError('nonfinite '+case)
        old={round(float(r['time_ns']),7):float(r['selection_rmsd_A']) for r in rows(previous/case/'analysis/selection_rmsd/selection_rmsd.csv')}
        record(case,'all_sampled_global_rmsd_vs_existing',max(abs(float(r['ligand_rmsd_global_A'])-old[round(float(r['time_ns']),7)]) for r in f),1e-4)
        frames={round(float(r['time_ns']),7):r for r in f}
        z=np.load(p/'representative_coordinates.npz')
        names=z['names'];resids=z['resids'];lig=z['ligand_indices'];X=z['coordinates_A'].astype(float)
        protein=np.flatnonzero(resids<=406)
        fit={'global':np.array([i for i in protein if names[i] in ('N','CA','C','O')]),'core':z['core_fit_indices'],'pocket':z['pocket_fit_indices']}
        anchor_records={(float(r['time_ns']),int(r['resid'])):float(r['distance_A']) for r in rows(p/'anchor_distances.csv')}
        audit=np.load(p/'numeric_audit.npz')
        for i,t in enumerate(z['time_ns']):
            expected=frames[round(float(t),7)]
            for name,ids in fit.items():
                aligned=independent_fit(X[i,ids],X[0,ids],X[i,lig])
                value=np.sqrt(np.mean(np.sum((aligned-X[0,lig])**2,axis=1)))
                record(case,f'fit_{name}_{t:g}ns',abs(value-float(expected[f'ligand_rmsd_{name}_A'])),1e-4)
            for n in cfg['sites']+cfg['anchors']:
                ids=np.array([j for j in protein if resids[j]==n and not names[j].startswith('H')])
                dist=np.sqrt(np.sum((X[i][ids][:,None,:]-X[i][lig][None,:,:])**2,axis=-1)).min()
                record(case,f'anchor_{n}_{t:g}ns',abs(dist-anchor_records[(float(t),n)]),1e-4)
            for s in cfg['sites']:
                atomset=np.array([j for j in protein if resids[j]==s and names[j] not in ('N','CA','C','O') and not names[j].startswith('H')])
                for n in (31,80,102,186,189,345,364):
                    ids=np.array([j for j in protein if resids[j]==n and not names[j].startswith('H')])
                    dist=np.sqrt(np.sum((X[i][atomset][:,None,:]-X[i][ids][None,:,:])**2,axis=-1)).min()
                    record(case,f'neighbour_{s}_{n}_{t:g}ns',abs(dist-audit[f'site{s}_distances_A'][round(t*10),n-1]),1e-4)
        anchor_summary=rows(p/'anchor_summary.csv')
        late=times>=50
        for r in anchor_summary:
            n=int(r['resid']);cut=float(r['cutoff_A']);arr=np.array([float(zr[f'res{n}_ligand_distance_A']) for zr in f])
            record(case,f'occupancy_{n}_{cut:g}A',abs(np.mean(arr[late]<=cut)-float(r['late_occupancy'])),1e-12)
        for r in rows(p/'proximity_bridges.csv'):
            seq=[v for v in rows(p/'proximity_bridge_timeseries.csv') if all(v[k]==r[k] for k in ('site','neighbor','anchor'))]
            v=np.array([[float(zr[k]) for k in ('site_neighbor_A','neighbor_anchor_A','anchor_ligand_A')] for zr in seq])
            if len(v)!=1001:raise ValueError('bridge missing frames')
            joint=(v[:,0]<=4.5)&(v[:,1]<=4.5)&(v[:,2]<=4)
            record(case,f'bridge_joint_{r["site"]}_{r["neighbor"]}_{r["anchor"]}',abs(joint[late].mean()-float(r['late_bridge_and_anchor_ligand_occupancy'])),1e-12)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    with (out/'numerical_validation.csv').open('w') as h:
        w=csv.DictWriter(h,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
    failures=[r for r in checks if not r['pass_check']]
    result=dict(status='PASS' if not failures else 'FAIL',checks=len(checks),failures=failures,
                methods='Independent NumPy SVD and broadcast distances, existing shared-driver comparison, occupancy reconstruction')
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
