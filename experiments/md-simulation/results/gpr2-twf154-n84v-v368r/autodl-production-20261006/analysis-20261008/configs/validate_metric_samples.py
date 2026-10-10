"""Independent numerical reproduction of existing RMSD output at sampled frames."""
import json,sys
from pathlib import Path
import numpy as np
import pandas as pd
import MDAnalysis as mda
batch=json.loads(Path(sys.argv[1]).read_text())
rows=[]
for case in batch['cases']:
 base=Path(batch['output_root'])/case['id']
 cfg=json.loads((base/'system_config.json').read_text())['systems'][case['id']]
 u=mda.Universe(str(base/'processed/rep1/protein_ref.pdb'),str(base/'processed/rep1/prod_protein.xtc'))
 backbone=u.select_atoms(cfg['backbone_selection']); ligand=u.select_atoms(cfg['selection_rmsd_selection'])
 u.trajectory[0];ref_backbone=backbone.positions.astype(float).copy();ref_ligand=ligand.positions.astype(float).copy()
 tables={'receptor':pd.read_csv(base/'analysis/convergence/rmsd_summary.csv'),'ligand':pd.read_csv(base/'analysis/selection_rmsd/selection_rmsd.csv')}
 reference_center=ref_backbone.mean(axis=0)
 for frame in [0,2500,5000,7500,10000]:
  u.trajectory[frame];mobile=backbone.positions.astype(float);center=mobile.mean(axis=0)
  left,singular,right=np.linalg.svd((mobile-center).T@(ref_backbone-reference_center))
  correction=np.diag([1,1,np.linalg.det(left@right)])
  rotation=left@correction@right
  fitted=(mobile-center)@rotation+reference_center
  fitted_ligand=(ligand.positions.astype(float)-center)@rotation+reference_center
  for label,computed,column in [('receptor',np.sqrt(np.mean(np.sum((fitted-ref_backbone)**2,axis=1))),'backbone_rmsd_A'),('ligand',np.sqrt(np.mean(np.sum((fitted_ligand-ref_ligand)**2,axis=1))),'selection_rmsd_A')]:
   observed=float(tables[label].iloc[frame][column]);delta=abs(observed-computed)
   rows.append({'case_id':case['id'],'metric':label+'_RMSD','frame':frame,'time_ns':float(u.trajectory.ts.time)/1000,'shared_driver_A':observed,'independent_SVD_A':computed,'difference_A':delta,'status':'PASS' if delta<1e-4 else 'FAIL'})
result=pd.DataFrame(rows)
result.to_csv(sys.argv[2],index=False)
print('checks',len(result),'max_difference_A',result.difference_A.max(),'statuses',result.status.value_counts().to_dict())
if not result.status.eq('PASS').all():raise SystemExit(1)
