"""Rebuild compact delivery tables from the preserved per-case numerical output."""
from pathlib import Path
import csv,json,collections
import numpy as np

b=Path(__file__).resolve().parents[1];cfg=json.loads((b/'configs/mechanism_config.json').read_text())
def read(p):return list(csv.DictReader(Path(p).open()))
def write(name,rs):
    with (b/'tables'/name).open('w') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def first_run(mask,times):
    start=None
    for i,v in enumerate(mask):
        if v and start is None:start=i
        if not v:start=None
        if start is not None and times[i]-times[start]>=1-1e-6:return times[start]
    return None
summary=[];hbsummary=[];atomgroups=[];checks=[];anchors=[];pairs=[];timeline=[];chemical=[];bridges=[];rotamers=[]
old=read(b.parent/'analysis-20261008/comparison/ligand_paths/residue_contact_occupancy.csv')
for c in cfg['cases']:
 p=b/'e2_delivery'/c['id'];f=read(p/'frame_metrics.csv');late=[r for r in f if float(r['time_ns'])>=50]
 r={'case':c['id'],'genotype':c['genotype'],'ligand':c['ligand']}
 for k in f[0]:
  if k not in ('case','time_ns') and 'chi1' not in k:r[k]=float(np.mean([float(x[k]) for x in late]))
 summary.append(r);anchors.extend(read(p/'anchor_summary.csv'));pairs.extend(read(p/'pair_details/pair_summary.csv'));bridges.extend(read(p/'proximity_bridges.csv'));rotamers.extend(read(p/'sidechain_rotamers.csv'))
 ev=read(p/'hbond_events.csv')
 for resid in cfg['sites']+cfg['anchors']:
  ts={x['time_ns'] for x in ev if int(x['resid'])==resid and float(x['time_ns'])>=50};hbsummary.append({'case':c['id'],'resid':resid,'late_any_hbond_occupancy':len(ts)/501})
 alias={'wt':'WT','n84v':'N84V','v368r':'V368R'};arm=alias[c['genotype']]+'_'+('A18' if c['ligand']=='ascr18' else 'A3')+('_newlid' if 'rebuilt' in c['id'] else '')
 for resid in cfg['sites']+cfg['anchors']:
  sub=[x for x in late if abs(float(x['time_ns'])*2-round(float(x['time_ns'])*2))<1e-6];val=np.mean([float(x[f'res{resid}_ligand_distance_A'])<=4 for x in sub]);expect=next((float(x['late_occupancy']) for x in old if x['arm']==arm and int(x['receptor_resid'])==resid),0)
  checks.append({'case':c['id'],'resid':resid,'reconstructed_0p5ns_occupancy':val,'prior_occupancy':expect,'pass_check':abs(val-expect)<1e-12})
 events=read(p/'atom_contact_events.csv')
 for resid in cfg['sites']+cfg['anchors']:
  for group in ['carboxylate','sugar_or_glycosidic_O','side_chain']:
   ts={r['time_ns'] for r in events if int(r['resid'])==resid and r['ligand_group']==group and float(r['distance_A'])<=4 and float(r['time_ns'])>=50};atomgroups.append({'case':c['id'],'resid':resid,'ligand_group':group,'late_occupancy':len(ts)/501})
 for row in read(p/'anchor_summary.csv'):
  if float(row['cutoff_A'])==4:
   timeline.append({'case':c['id'],'event':f'residue_{row["resid"]}_ligand_contact','first_1ns_start_ns':row['first_1ns_contact_ns'],'definition':'minimum heavy atom distance <=4 A; 100 ps sampling'})
 q=read(p/'pair_details/Arg368_Asp70_geometry.csv')
 if q:
  times=np.array([float(r['time_ns']) for r in q]);dist=np.array([float(r['guanidinium_Asp70_distance_A']) for r in q]);late=times>=50
  loss=first_run(dist>4,times)
  chemical.append({'case':c['id'],'late_guanidinium_Asp70_mean_A':float(dist[late].mean()),'late_any_hbond_occupancy':float(np.mean([r['Arg368_Asp70_hbond']=='True' for r in q if float(r['time_ns'])>=50])),'first_1ns_charged_separation_ns':loss})
  timeline.append({'case':c['id'],'event':'Arg368_charged_group_Asp70_separation','first_1ns_start_ns':loss,'definition':'min NE/NH1/NH2 to OD1/OD2 >4 A; 100 ps sampling'})
for name,rs in [('six_case_local_summary.csv',summary),('anchor_hbond_union.csv',hbsummary),('anchor_group_occupancy.csv',atomgroups),('anchor_sensitivity.csv',anchors),('local_pair_summary.csv',pairs),('proximity_bridges.csv',bridges),('sidechain_rotamers.csv',rotamers),('event_timeline.csv',timeline),('Arg368_Asp70_summary.csv',chemical)]:write(name,rs)
with (b/'evidence/previous_contact_crosscheck.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
assert all(r['pass_check'] for r in checks)
print('summary tables regenerated;',len(checks),'previous contact checks PASS')
