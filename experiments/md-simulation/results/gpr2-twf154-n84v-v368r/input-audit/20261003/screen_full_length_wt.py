"""Read-only screen of local full-length WT models against two ligand seed poses."""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
AA=dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),'ARNDCQEGHILKMFPSTWYV'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def atoms(p):
 out=[]
 for l in p.read_text().splitlines():
  if not l.startswith(('ATOM  ','HETATM')): continue
  name=l[12:16].strip(); el=l[76:78].strip() or name[0]
  if el=='H': continue
  out.append(dict(res=int(l[22:26]),chain=l[21],name=name,resname=l[17:20].strip(),xyz=[float(l[x:x+8]) for x in (30,38,46)],b=float(l[60:66])))
 return out

def xyz(a): return np.array([z['xyz'] for z in a])
def sdf(p):
 l=p.read_text().splitlines(); n=int(l[3][:3]); return np.array([[float(a[i:i+10]) for i in (0,10,20)] for a in l[4:4+n] if a[31:34].strip()!='H'])
def fit(x,y):
 xc=x-x.mean(0); yc=y-y.mean(0); u,_,vt=np.linalg.svd(xc.T@yc); r=u@np.diag([1,1,np.linalg.det(u@vt)])@vt; t=y.mean(0)-x.mean(0)@r
 return r,t,float(np.sqrt(np.mean(np.sum((x@r+t-y)**2,axis=1))))
def geometry(a,lig):
 d=np.linalg.norm(xyz(a)[:,None,:]-lig[None,:,:],axis=2)
 i,j=np.unravel_index(d.argmin(),d.shape)
 return dict(min_distance_A=float(d[i,j]),pairs_below_2A=int((d<2).sum()),pairs_below_1_5A=int((d<1.5).sum()),nearest_receptor_atom=f"{a[i]['resname']}{a[i]['res']}:{a[i]['name']}")
ap=argparse.ArgumentParser();ap.add_argument('--docking',type=Path,required=True);ap.add_argument('--handoff',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
f=args.docking/'inputs/receptors/fasta/Gpr2_TWF154_TGJ68930.1.fasta';seq=''.join(x.strip() for x in f.read_text().splitlines() if not x.startswith('>'))
refpath=args.handoff/'05_n84v/docking_receptor/input.pdb'; ref=atoms(refpath)
ranges=[(30,50),(62,83),(101,126),(144,163),(182,201),(326,346),(358,380)]
refca={z['res']:z for z in ref if z['name']=='CA' and any(lo<=z['res']<=hi for lo,hi in ranges)}; ids=sorted(refca)
ligpaths={'ascr18':args.handoff/'05_n84v/ascr18/top1.sdf','ascr3':args.handoff/'05_v368r/ascr3/top1.sdf'}; ligs={k:sdf(p) for k,p in ligpaths.items()}
paths=sorted((args.docking/'inputs/receptors/af3/pdb/gpr2_twf154_wt/wt').glob('*.pdb'))+sorted((args.docking/'inputs/receptors/af2/GPR2_TWF154_WT_AF2ptm_ColabOnline_a28e6').glob('*.pdb'))
rep=dict(method='Rigid Kabsch fit using the 153 mapped TM CA residues to N84V docking receptor input frame; same two selected ligand seeds for every model. Heavy-atom geometric screen only, no energy evaluation. Below-2 A counts are diagnostic, not full force-field acceptance.',sources=[dict(path=str(p),sha256=sha(p)) for p in [f,refpath,*ligpaths.values()]],producer=dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__))),python=sys.version,numpy=np.__version__,models=[])
for p in paths:
 a=atoms(p); ca={z['res']:z for z in a if z['name']=='CA'}; actual=''.join(AA[ca[i]['resname']] for i in sorted(ca))
 r=dict(path=str(p),sha256=sha(p),sequence_matches=actual==seq,residue_count=len(ca))
 if actual!=seq: rep['models'].append(r);continue
 R,t,err=fit(xyz([ca[i] for i in ids]),xyz([refca[i] for i in ids])); moved=[dict(z,xyz=v.tolist()) for z,v in zip(a,xyz(a)@R+t)]
 r.update(core_CA_RMSD_A=err,alignment_CA_count=len(ids),rotation_matrix=R.tolist(),translation_vector=t.tolist(),ligands={})
 r['lid_CA_confidence']=dict(mean=float(np.mean([ca[i]['b'] for i in range(164,179)])),min=min(ca[i]['b'] for i in range(164,179)),max=max(ca[i]['b'] for i in range(164,179)))
 sulfur={z['res']:z for z in moved if z['name']=='SG' and z['resname']=='CYS'}
 r['C99_C173_SG_distance_A']=float(np.linalg.norm(xyz([sulfur[99]])-xyz([sulfur[173]])))
 for k,l in ligs.items():
  r['ligands'][k]={name:geometry(sub,l) for name,sub in [('full',moved),('lid',[z for z in moved if 164<=z['res']<=178]),('lid_backbone',[z for z in moved if 164<=z['res']<=178 and z['name'] in ('N','CA','C','O')]),('non_lid',[z for z in moved if not 164<=z['res']<=178])]}
 rep['models'].append(r)
args.output.write_text(json.dumps(rep,indent=2)+'\n')
for r in rep['models']:
 print(Path(r['path']).name, 'seq',r['sequence_matches'],'core',round(r.get('core_CA_RMSD_A',999),3),'S-S',round(r.get('C99_C173_SG_distance_A',999),3),'lidConf',round(r.get('lid_CA_confidence',{}).get('mean',0),2),'ligands', {k:{'lid_min':round(v['lid']['min_distance_A'],3),'lid_pairs<2':v['lid']['pairs_below_2A'],'nonlid_min':round(v['non_lid']['min_distance_A'],3)} for k,v in r.get('ligands',{}).items()})
