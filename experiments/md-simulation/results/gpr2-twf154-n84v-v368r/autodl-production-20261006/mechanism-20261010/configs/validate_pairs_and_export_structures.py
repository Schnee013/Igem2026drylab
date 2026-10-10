from pathlib import Path
import csv,json
import numpy as np

base=Path(__file__).resolve().parents[1]
cfg=json.loads((base/'configs/pair_detail_config.json').read_text())
checks=[]
def check(case,name,err,tol=1e-4):checks.append(dict(case=case,test=name,error=float(err),tolerance=tol,pass_check=bool(err<=tol)))
def torsion(p):
    b0=-(p[1]-p[0]);b1=p[2]-p[1];b2=p[3]-p[2];b1=b1/np.linalg.norm(b1)
    v=b0-np.dot(b0,b1)*b1;w=b2-np.dot(b2,b1)*b1
    return np.degrees(np.arctan2(np.dot(np.cross(b1,v),w),np.dot(v,w)))
for c in cfg['cases']:
    p=base/'e2_delivery'/c['id'];z=np.load(p/'representative_coordinates.npz');X=z['coordinates_A'].astype(float);names=z['names'];resids=z['resids']
    pair=list(csv.DictReader((p/'pair_details/receptor_pair_atoms.csv').open()))
    lookup={(float(r['time_ns']),int(r['site']),int(r['neighbor'])):r for r in pair}
    geom={float(r['time_ns']):r for r in csv.DictReader((p/'pair_details/Arg368_Asp70_geometry.csv').open())}
    idx={(int(resids[j]),str(names[j])):j for j in range(len(names))}
    template=(base.parent/'analysis-20261008/e2_delivery'/c['id']/'processed/rep1/protein_ref.pdb').read_text().splitlines()
    atomlines=[s for s in template if s.startswith(('ATOM  ','HETATM'))];assert len(atomlines)==X.shape[1]
    model_lines=['REMARK   1 Existing rep1 representative frames. Coordinates in Angstrom.']
    for k,t in enumerate(z['time_ns']):
        x=X[k]
        for s,n in cfg['receptor_pairs']:
            left=np.flatnonzero((resids==s)&np.array([not n.startswith('H') and n not in ('N','CA','C','O') for n in names]))
            right=np.flatnonzero((resids==n)&np.array([not n.startswith('H') for n in names]))
            ds=np.linalg.norm(x[left][:,None,:]-x[right][None,:,:],axis=2)
            check(c['id'],f'pair_{s}_{n}_{t:g}ns',abs(ds.min()-float(lookup[(float(t),s,n)]['distance_A'])))
        if geom:
            ns=[idx[(368,n)] for n in ['NE','NH1','NH2']];os=[idx[(70,n)] for n in ['OD1','OD2']]
            distance=np.linalg.norm(x[ns][:,None,:]-x[os][None,:,:],axis=2).min();r=geom[float(t)]
            check(c['id'],f'charged_distance_{t:g}ns',abs(distance-float(r['guanidinium_Asp70_distance_A'])))
            hb=False
            for donor,h in [('NE','HE'),('NH1','HH11'),('NH1','HH12'),('NH2','HH21'),('NH2','HH22')]:
                d,hidx=idx[(368,donor)],idx[(368,h)]
                for o in os:
                    v=x[d]-x[hidx];w=x[o]-x[hidx];angle=np.degrees(np.arccos(np.clip(np.dot(v,w)/np.linalg.norm(v)/np.linalg.norm(w),-1,1)))
                    hb |= bool(np.linalg.norm(x[d]-x[o])<=3 and angle>=150)
            check(c['id'],f'charged_hbond_{t:g}ns',int(hb!=(r['Arg368_Asp70_hbond']=='True')),0)
            for label,ns4 in [('chi2',['CA','CB','CG','CD']),('chi3',['CB','CG','CD','NE']),('chi4',['CG','CD','NE','CZ'])]:
                value=torsion(x[[idx[(368,n)] for n in ns4]]);error=abs((value-float(r[label+'_deg'])+180)%360-180)
                check(c['id'],f'{label}_{t:g}ns',error,1e-3)
        model_lines.extend([f'MODEL     {k+1:4d}',f'REMARK   2 TIME_NS {t:g}'])
        for line,pos in zip(atomlines,x):model_lines.append(line[:30]+f'{pos[0]:8.3f}{pos[1]:8.3f}{pos[2]:8.3f}'+line[54:])
        model_lines.append('ENDMDL')
    model_lines.append('END')
    (base/'structures'/f'{c["id"]}_six_frames.pdb').write_text('\n'.join(model_lines)+'\n')
with (base/'evidence/pair_numerical_validation.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
result={'status':'PASS' if all(r['pass_check'] for r in checks) else 'FAIL','checks':len(checks),'failures':[r for r in checks if not r['pass_check']]}
(base/'evidence/pair_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));assert result['status']=='PASS'
