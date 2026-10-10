#!/usr/bin/env python3
"""Resolve an input overlap by scanning Trp174 side-chain torsions only.

This creates a geometric preparation candidate, not a dynamical unthreading path
or an affinity-ranked structure. Backbone, ligand and other atoms stay fixed.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from check_twf154_snapshot import read_gro, equilibrium_bonds, audit


def rotate(points, origin, axis, degrees):
    v=points-origin;u=axis/np.linalg.norm(axis);a=np.deg2rad(degrees)
    return origin+v*np.cos(a)+np.cross(u,v)*np.sin(a)+np.outer(v@u,u)*(1-np.cos(a))


def main():
    p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('geometry',type=Path);p.add_argument('out',type=Path);p.add_argument('--water-min',type=float,default=1.5);p.add_argument('--solute-min',type=float,default=2.1);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    ref=a.case/'ionized.gro';rows,box=read_gro(ref);box=np.array(box)*10
    xyz=np.array([r[3] for r in rows])*10
    info=json.loads((a.case/'input_contract.json').read_text());nr=info['atoms']
    idx={row[2]:i for i,row in enumerate(rows[:nr]) if row[0]==174};assert rows[idx['CA']][1]=='TRP'
    fixed_names={'N','HN','H','CA','HA','C','O','CB'}
    moving=[i for n,i in idx.items() if n not in fixed_names]
    ring=[i for n,i in idx.items() if n not in fixed_names|{'HB1','HB2','HB3'}]
    heavy=[i for i in moving if not rows[i][2].startswith('H')]
    assert set(rows[i][2] for i in heavy)=={'CG','CD1','CD2','NE1','CE2','CE3','CZ2','CZ3','CH2'}
    # Keep the candidate close to the original torsions while removing hard
    # nonbonded overlaps. Water can relax, but no near-coincident oxygen is allowed.
    tree=cKDTree(xyz%box,boxsize=box)
    near=tree.query_ball_point(xyz[idx['CB']]%box,10.0)
    env=[i for i in near if i not in moving and not rows[i][2].startswith('H')]
    bond=equilibrium_bonds(a.case);neighbors={i:set() for i in idx.values()}
    for i,j,*_ in bond['bonds']:
        if i in neighbors:neighbors[i].add(j)
        if j in neighbors:neighbors[j].add(i)
    permitted=np.ones((len(heavy),len(env)),dtype=bool)
    for n,i in enumerate(heavy):
        excluded={i}|neighbors[i]
        for j in neighbors[i]:excluded|=neighbors.get(j,set())
        permitted[n]=[j not in excluded for j in env]
    solute=np.array([rows[i][1] not in {'SOL','POT','CLA'} for i in env])
    trials=[];scanned=[]
    def coordinates(d1,d2):
        out=xyz.copy();out[moving]=rotate(out[moving],out[idx['CB']],out[idx['CB']]-out[idx['CA']],d1)
        out[ring]=rotate(out[ring],out[idx['CG']],out[idx['CG']]-out[idx['CB']],d2)
        return out
    for d1 in range(-180,180,10):
        for d2 in range(-180,180,10):
            out=coordinates(d1,d2)
            delta=out[heavy,None]-xyz[None,env];delta-=np.rint(delta/box)*box
            distances=np.linalg.norm(delta,axis=2);distances[~permitted]=100
            dsolute=float(distances[:,solute].min());dwater=float(distances[:,~solute].min())
            scanned.append({'d1':d1,'d2':d2,'solute':dsolute,'water':dwater})
            if dsolute<a.solute_min or dwater<a.water_min:continue
            penalty=float(np.maximum(2.8-distances[:,solute],0).sum())
            shift=float(np.sqrt(np.mean(np.sum((out[heavy]-xyz[heavy])**2,axis=1))))
            trials.append({'chi1_delta_deg':d1,'chi2_delta_deg':d2,'min_solute_heavy_A':dsolute,
                           'min_water_heavy_A':dwater,'overlap_penalty':penalty,'sidechain_rms_shift_A':shift})
    (a.out/'scan_summary.json').write_text(json.dumps({'best_solute':sorted(scanned,key=lambda x:x['solute'],reverse=True)[:10],
                                                    'require_resolvation':a.water_min<1.5},indent=2))
    assert trials,'No side-chain-only candidate satisfies nonbonded separation'
    trials.sort(key=lambda t:(-t['min_solute_heavy_A'],t['overlap_penalty'],t['sidechain_rms_shift_A']))
    original_lines=ref.read_text().splitlines();selected=None;cfg=json.loads(a.geometry.read_text())
    for k,t in enumerate(trials[:30]):
        out=coordinates(t['chi1_delta_deg'],t['chi2_delta_deg']);lines=original_lines.copy()
        lines[0]='Independent WT geometric input repair: Trp174 side-chain torsions only'
        for i in moving:lines[i+2]=lines[i+2][:20]+''.join(f'{v/10:8.3f}' for v in out[i])+lines[i+2][44:]
        candidate=a.out/f'candidate_{k+1:03d}.gro';candidate.write_text('\n'.join(lines)+'\n')
        check=audit(a.case,candidate,cfg)
        (a.out/f'candidate_{k+1:03d}_geometry.json').write_text(json.dumps(check,indent=2))
        # Unchanged solvent/lipid and newly generated S-H coordinates still await
        # their first CHARMM minimization. At this input-construction stage check
        # the modified residue and ligand bonds, chirality and ring topology.
        # The subsequent EM/heating checker still requires every bond to pass.
        local_bad=[b for b in check['all_bonds_outside_20pct'] if b['molecule'].startswith('ASCR')
                   or (b['molecule']=='PROA' and any(atom[0]==174 for atom in b['atoms']))]
        ok=not any(check[key] for key in ['protein_chirality_inversions','ligand_chirality_inversions',
              'popc_chirality_inversions','protein_ring_sugar_links']) and not local_bad and check['ss_loop_sugar_linking_numbers']==[0]
        if not ok:continue
        for i in range(len(rows)):
            if i not in moving:assert lines[i+2]==original_lines[i+2]
        selected={**t,'candidate':str(candidate),'changed_atom_names':[rows[i][2] for i in moving],
                  'unchanged_atoms':len(rows)-len(moving),'all_backbone_and_ligand_coordinates_unchanged':True,
                  'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'lid_ligand_min_A':check['lid_ligand_min_heavy_A']}
        break
    report={'source':str(ref),'source_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),
            'trials':1296,'feasible':len(trials),'selection_rule':'Increase worst nonbonded separation, then reduce overlap and side-chain shift; no affinity objective',
            'starting_solute_distance_minimum_A':a.solute_min,'starting_water_distance_minimum_A':a.water_min,
            'selected':selected,'candidate_ranking':trials[:30],
            'scope':'Discrete geometric repair, not a physical unthreading trajectory; remaining nonbonded overlaps require original-force-field minimization; no final acceptance criteria are relaxed'}
    (a.out/'orientation_repair.json').write_text(json.dumps(report,indent=2));assert selected
    print(json.dumps(selected,indent=2))


if __name__=='__main__':main()
