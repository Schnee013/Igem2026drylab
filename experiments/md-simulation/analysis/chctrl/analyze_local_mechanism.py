#!/usr/bin/env python
"""Config-driven, descriptive local mechanism analysis of existing trajectories.

Extends the shared analysis family with sidechain neighbourhoods, atom-resolved
anchors, local fits, and simultaneous two-edge proximity paths. Proximity paths
and temporal order are structural observations, never causal signalling paths.
No MD is started and trajectory inputs are opened with the read-only XDR API.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array, calc_dihedrals
from MDAnalysis.lib.formats.libmdaxdr import XTCFile
import mdtraj as md
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'src/modeling/md-analysis'))
from common import equal_weight_kabsch_coordinates


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def csv(path, rows, columns=None):
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


def heavy(group):
    return group[[not a.name.startswith('H') and a.mass > 2 for a in group]]


def stretches(values, minimum):
    blocks = []
    for n in sorted(values):
        if not blocks or n != blocks[-1][-1] + 1:
            blocks.append([])
        blocks[-1].append(n)
    return [n for b in blocks if len(b) >= minimum for n in b]


def first_run(mask, times, duration=1.0):
    start = None
    for i, yes in enumerate(mask):
        if yes and start is None:
            start = i
        if not yes:
            start = None
        if start is not None and times[i] - times[start] >= duration - 1e-6:
            return float(times[start])
    return None


def summary(y, times, window):
    late = (times >= window[0]) & (times <= window[1])
    return dict(initial=float(y[0]), early_mean=float(np.mean(y[times < window[0]])),
                late_mean=float(np.mean(y[late])), late_min=float(np.min(y[late])),
                late_max=float(np.max(y[late])))


def prepare(cfg):
    out = Path(cfg['shared_output']); out.mkdir(parents=True, exist_ok=True)
    helix_sets, pocket_sets, records = [], [], []
    for case in cfg['cases']:
        u = mda.Universe(case['topology'])
        ref = mda.Universe(case['reference'])
        protein = u.select_atoms('protein')
        assert len(protein.residues) == 406
        assert list(zip(protein.resids, protein.names)) == list(zip(ref.select_atoms('protein').resids, ref.select_atoms('protein').names))
        xyz = ref.atoms.positions
        p = heavy(protein); lig = heavy(u.atoms[len(protein):])
        near = set(map(int, p.resids[distance_array(xyz[p.indices], xyz[lig.indices]).min(axis=1) <= cfg['pocket_radius_A']]))
        pocket_sets.append(near)
        tr = md.load_pdb(case['reference'])
        ss = md.compute_dssp(tr, simplified=True)[0]
        h = {r.resSeq for r in tr.topology.residues if ss[r.index] == 'H'}
        full = mda.Universe(case['full_topology'])
        with XTCFile(case['full_trajectory'], 'r') as f:
            fx = f.read().x * 10
        phosphates = full.select_atoms('resname POPC and name P')
        assert len(phosphates) > 100
        z = fx[phosphates.indices, 2]
        mid = np.median(z)
        low, high = float(np.mean(z[z < mid])), float(np.mean(z[z >= mid]))
        ca = full.select_atoms('protein and name CA')
        membrane_resids = set(map(int, ca.resids[(fx[ca.indices, 2] >= low) & (fx[ca.indices, 2] <= high)]))
        selected = h & membrane_resids
        helix_sets.append(selected)
        records.append(dict(case=case['id'], helix_resids=sorted(h), membrane_resids=sorted(membrane_resids),
                            phosphate_plane_z_A=[low, high], initial_pocket_resids=sorted(near),
                            full_topology_sha256=sha(case['full_topology'])))
    core = stretches(set.intersection(*helix_sets), cfg['minimum_helix_run'])
    pocket = sorted(set.union(*pocket_sets) - set(cfg['lid_resids']))
    assert len(core) >= 35 and len(pocket) >= 8
    selections = dict(core_resids=core, pocket_resids=pocket, lid_resids=cfg['lid_resids'],
                      definition='Intersection of frame0 DSSP H and membrane phosphate slab across all arms; contiguous runs only. Pocket is union of frame0 6A ligand neighbours, excluding lid. No late frames used.',
                      records=records)
    dump(out / 'selections.json', selections)
    print('SELECTIONS', len(core), core, len(pocket), pocket, flush=True)


def ligand_groups(u, lig):
    """Assign groups from the actual TPR bonds, not ligand atom-name guesses."""
    ids = set(lig.indices)
    carbox = set()
    for a in lig:
        oxygens = [b for b in a.bonded_atoms if b.index in ids and b.name.startswith('O')]
        if a.name.startswith('C') and len(oxygens) == 2 and all(len(b.bonded_atoms) == 1 for b in oxygens):
            carbox.update([a.index] + [b.index for b in oxygens])
    # O bonded to two carbons in a six-membered ring seeds the sugar component.
    ring = set()
    graph = {a.index: [b.index for b in a.bonded_atoms if b.index in ids] for a in lig}
    for a in lig:
        if not a.name.startswith('O') or len(graph[a.index]) != 2:
            continue
        paths = [[a.index]]
        for _ in range(5):
            paths = [p + [j] for p in paths for j in graph[p[-1]] if j not in p]
        for p in paths:
            if a.index in graph[p[-1]]:
                ring.update(p)
    sugar = set(ring)
    for i in ring:
        for j in graph[i]:
            if u.atoms[j].name.startswith('O') or (u.atoms[j].name.startswith('C') and len(graph[j]) == 1):
                sugar.add(j)
    result = {i: ('carboxylate' if i in carbox else 'sugar_or_glycosidic_O' if i in sugar else 'side_chain') for i in ids}
    assert len(carbox) == 3 and len(ring) == 6
    return result


def hbond_candidates(u, protein, ligand):
    ligand_ids = set(ligand.indices)
    def acceptor(a):
        if a.index in ligand_ids:
            return a.name.startswith('O')
        if a.name.startswith('O'):
            return True
        return a.resname in ('HIS', 'HSD', 'HSE') and a.name in ('ND1', 'NE2') and not any(b.name.startswith('H') for b in a.bonded_atoms)
    def donors(group):
        return [(a.index, h.index) for a in group if a.name[0] in 'NOS'
                for h in a.bonded_atoms if h.name.startswith('H')]
    candidates = []
    for ds, acs, direction in [(protein, ligand, 'protein_to_ligand'), (ligand, protein, 'ligand_to_protein')]:
        for d, h in donors(ds):
            for a in acs:
                if acceptor(a):
                    candidates.append((d, h, a.index, direction))
    return candidates


def run_case(cfg, case, selections):
    out = Path(case['output']); out.mkdir(parents=True, exist_ok=True)
    if (out / 'completion.json').exists():
        raise RuntimeError(f'Refuse to overwrite completed analysis: {out}')
    identity = {}
    for key in ('topology', 'reference', 'trajectory'):
        expected = case['expected_' + key + '_sha256']
        actual = sha(case[key]); assert actual == expected, (key, actual, expected)
        identity[key] = dict(path=case[key], sha256=actual, bytes=Path(case[key]).stat().st_size)
    assert identity['trajectory']['bytes'] == case['expected_trajectory_bytes']
    u = mda.Universe(case['topology'])
    protein = u.select_atoms('protein'); ph = heavy(protein)
    lig_all = u.atoms[len(protein):]; lig = heavy(lig_all)
    assert len(lig_all.residues) == 1
    residues = list(protein.residues); resid_list = [int(r.resid) for r in residues]
    assert resid_list == list(range(1, 407))
    expected_site = {'wt':('ASN','VAL'), 'n84v':('VAL','VAL'), 'v368r':('ASN','ARG')}[case['genotype']]
    assert tuple(protein.select_atoms(f'resid {s}').residues[0].resname for s in cfg['sites']) == expected_site
    dump(out / 'input_identity.json', identity)
    positions, times, alltimes = [], [], []
    with XTCFile(case['trajectory'], 'r') as f:
        for i, frame in enumerate(f):
            alltimes.append(frame.time)
            if i % cfg['stride_frames'] == 0:
                x = frame.x * 10
                assert x.shape == (len(u.atoms), 3) and np.isfinite(x).all()
                positions.append(x.copy()); times.append(frame.time / 1000)
    assert np.allclose(alltimes, np.arange(10001)*10, atol=1e-4)
    X = np.asarray(positions); times = np.asarray(times)
    assert len(times) == 1001 and times[-1] == 100
    late = times >= cfg['window_ns'][0]
    atom_groups = ligand_groups(u, lig)
    csv(out / 'ligand_atom_mapping.csv', [dict(index=a.index, atom=a.name, type=a.type, charge=a.charge,
        group=atom_groups.get(a.index, 'H'), bonded_atoms=' '.join(b.name for b in a.bonded_atoms)) for a in lig_all])
    ca_ids = np.array([r.atoms.select_atoms('name CA').indices[0] for r in residues])
    residue_heavy = {int(r.resid):heavy(r.atoms).indices for r in residues}
    sidechains = {s:heavy(u.select_atoms(f'protein and resid {s} and not backbone')).indices for s in cfg['sites']}
    focal = cfg['sites'] + cfg['anchors']
    frame_rows, local_rows, anchor_rows, atom_events, hb_events = [], [], [], [], []
    fit_ids = {'global':protein.select_atoms('backbone').indices}
    for label, resids in [('core',selections['core_resids']),('pocket',selections['pocket_resids'])]:
        fit_ids[label] = protein.select_atoms('backbone and resid ' + ' '.join(map(str,resids))).indices
    lid = protein.select_atoms('backbone and resid ' + ' '.join(map(str,cfg['lid_resids']))).indices
    site_distances = {s:np.zeros((len(times),406)) for s in cfg['sites']}
    anchor_d = {a:np.zeros(len(times)) for a in focal}
    chi_indices = {}
    for s in cfg['sites']:
        r = protein.select_atoms(f'resid {s}').residues[0]
        terminal = 'CG1' if r.resname == 'VAL' else 'CG'
        chi_indices[s] = np.array([r.atoms.select_atoms('name '+n).indices[0] for n in ['N','CA','CB',terminal]])
    target_protein = u.select_atoms('protein and resid ' + ' '.join(map(str,focal)))
    hb_candidates = hbond_candidates(u, target_protein, lig_all)
    hb_triplets = np.array([z[:3] for z in hb_candidates], dtype=int)
    ref = X[0]; per_atom_frames = []
    for i, (x,t) in enumerate(zip(X,times)):
        row = dict(case=case['id'], time_ns=float(t))
        for label, ids in fit_ids.items():
            transformed, fit_rmsd = equal_weight_kabsch_coordinates(x[ids],ref[ids],x)
            row[f'{label}_fit_rmsd_A'] = fit_rmsd
            row[f'ligand_rmsd_{label}_A'] = float(np.sqrt(np.mean(np.sum((transformed[lig.indices]-ref[lig.indices])**2,axis=1))))
            row[f'ligand_displacement_{label}_A'] = float(np.linalg.norm(transformed[lig.indices].mean(0)-ref[lig.indices].mean(0)))
            row[f'lid_rmsd_{label}_A'] = float(np.sqrt(np.mean(np.sum((transformed[lid]-ref[lid])**2,axis=1))))
        row['lid_pocket_centroid_distance_A'] = float(np.linalg.norm(x[lid].mean(0)-x[fit_ids['pocket']].mean(0)))
        for s in cfg['sites']:
            q = x[chi_indices[s]]
            row[f'site{s}_chi1_deg'] = float(np.degrees(calc_dihedrals(*q)))
            dist = distance_array(x[sidechains[s]],x[ph.indices]).min(axis=0)
            for j,r in enumerate(resid_list):
                site_distances[s][i,j] = dist[ph.resids == r].min()
            row[f'site{s}_ligand_sidechain_distance_A'] = float(distance_array(x[sidechains[s]],x[lig.indices]).min())
        for a in focal:
            ids = residue_heavy[a]; ds=distance_array(x[ids],x[lig.indices])
            pa,la=np.unravel_index(ds.argmin(),ds.shape)
            anchor_d[a][i] = ds[pa,la]
            row[f'res{a}_ligand_distance_A'] = float(ds[pa,la])
            anchor_rows.append(dict(case=case['id'],time_ns=t,resid=a,resname=u.atoms[ids[0]].resname,
                distance_A=ds[pa,la],protein_atom=u.atoms[ids[pa]].name,ligand_atom=u.atoms[lig.indices[la]].name,
                ligand_group=atom_groups[lig.indices[la]]))
            for pi,li in np.argwhere(ds <= max(cfg['contact_cutoffs_A'])):
                atom_events.append(dict(time_ns=t,resid=a,protein_atom=u.atoms[ids[pi]].name,
                    ligand_atom=u.atoms[lig.indices[li]].name,ligand_group=atom_groups[lig.indices[li]],distance_A=ds[pi,li]))
        if len(hb_triplets):
            D,H,A = (x[hb_triplets[:,j]] for j in range(3))
            da=np.linalg.norm(D-A,axis=1); dh=D-H; ah=A-H
            angles=np.degrees(np.arccos(np.clip(np.sum(dh*ah,axis=1)/(np.linalg.norm(dh,axis=1)*np.linalg.norm(ah,axis=1)),-1,1)))
            for k in np.flatnonzero((da<=3.0)&(angles>=150)):
                d,h,a,direction=hb_candidates[k]
                pa = u.atoms[d] if direction=='protein_to_ligand' else u.atoms[a]
                la = a if direction=='protein_to_ligand' else d
                hb_events.append(dict(time_ns=t,resid=pa.resid,direction=direction,donor=f'{u.atoms[d].resid}:{u.atoms[d].name}',
                    hydrogen=u.atoms[h].name,acceptor=f'{u.atoms[a].resid}:{u.atoms[a].name}',ligand_group=atom_groups[la],distance_A=da[k],angle_deg=angles[k]))
        frame_rows.append(row)
    frames=pd.DataFrame(frame_rows);frames.to_csv(out/'frame_metrics.csv',index=False)
    csv(out/'anchor_distances.csv',anchor_rows)
    csv(out/'atom_contact_events.csv',atom_events)
    csv(out/'hbond_events.csv',hb_events,columns=['time_ns','resid','direction','donor','hydrogen','acceptor','ligand_group','distance_A','angle_deg'])
    metric_summary=[];blocks=[]
    for col in frames.columns:
        if col in ('case','time_ns') or 'chi1' in col: continue
        y=frames[col].to_numpy()
        metric_summary.append(dict(case=case['id'],metric=col,**summary(y,times,cfg['window_ns'])))
        for start in range(0,100,10):
            mask=(times>=start)&(times<(start+10) if start<90 else times<=100)
            blocks.append(dict(case=case['id'],metric=col,start_ns=start,end_ns=start+10,n_frames=int(mask.sum()),mean=float(y[mask].mean())))
    csv(out/'metric_summary.csv',metric_summary);csv(out/'ten_ns_blocks.csv',blocks)
    contact_summary=[]
    for a in focal:
        for cut in cfg['contact_cutoffs_A']:
            mask=anchor_d[a]<=cut
            contact_summary.append(dict(case=case['id'],resid=a,cutoff_A=cut,initial_contact=bool(mask[0]),
                early_occupancy=float(mask[~late].mean()),late_occupancy=float(mask[late].mean()),
                first_1ns_contact_ns=first_run(mask,times),first_1ns_absence_ns=first_run(~mask,times),**summary(anchor_d[a],times,cfg['window_ns'])))
    csv(out/'anchor_summary.csv',contact_summary)
    bridge_rows=[];bridge_frame_rows=[]
    for s in cfg['sites']:
        for j,r in enumerate(resid_list):
            if r==s:continue
            y=site_distances[s][:,j]
            if y.min()>6:continue
            row=dict(case=case['id'],site=s,site_name=u.select_atoms(f'protein and resid {s}').residues[0].resname,
                neighbor=r,neighbor_name=residues[j].resname,sequence_separation=abs(s-r),**summary(y,times,cfg['window_ns']))
            for cut in cfg['contact_cutoffs_A']:
                row[f'late_occupancy_{cut:g}A']=float((y[late]<=cut).mean())
            row['first_1ns_contact_4A_ns']=first_run(y<=4,times)
            local_rows.append(row)
            if abs(s-r)<=2 or y.min()>cfg['bridge_cutoff_A']:continue
            for a in cfg['anchors']:
                if r==a or abs(r-a)<=2:continue
                # Enumerate only simultaneous two-edge physical adjacency, not allostery.
                ids=residue_heavy[r]; target=residue_heavy[a]
                d2=np.array([distance_array(x[ids],x[target]).min() for x in X])
                simultaneous=(y<=cfg['bridge_cutoff_A'])&(d2<=cfg['bridge_cutoff_A'])
                if not simultaneous.any():continue
                joint=simultaneous&(anchor_d[a]<=4)
                bridge_rows.append(dict(case=case['id'],site=s,neighbor=r,anchor=a,
                    initial_bridge=bool(simultaneous[0]),early_bridge_occupancy=float(simultaneous[~late].mean()),
                    late_bridge_occupancy=float(simultaneous[late].mean()),late_bridge_and_anchor_ligand_occupancy=float(joint[late].mean()),
                    first_1ns_bridge_ns=first_run(simultaneous,times),first_1ns_joint_ns=first_run(joint,times)))
                for i,t in enumerate(times):
                    bridge_frame_rows.append(dict(time_ns=t,site=s,neighbor=r,anchor=a,site_neighbor_A=y[i],neighbor_anchor_A=d2[i],anchor_ligand_A=anchor_d[a][i]))
    csv(out/'site_neighborhoods.csv',local_rows)
    csv(out/'proximity_bridges.csv',bridge_rows,columns=['case','site','neighbor','anchor','initial_bridge','early_bridge_occupancy','late_bridge_occupancy','late_bridge_and_anchor_ligand_occupancy','first_1ns_bridge_ns','first_1ns_joint_ns'])
    csv(out/'proximity_bridge_timeseries.csv',bridge_frame_rows,columns=['time_ns','site','neighbor','anchor','site_neighbor_A','neighbor_anchor_A','anchor_ligand_A'])
    # Rotamer occupancy is circular; no arithmetic averaging across +/-180 degrees.
    rotamers=[]
    for s in cfg['sites']:
        angles=frames[f'site{s}_chi1_deg'].to_numpy()
        centers=np.array([-60,60,180]);delta=np.abs((angles[:,None]-centers+180)%360-180);states=delta.argmin(1)
        for j,center in enumerate(centers):
            rotamers.append(dict(case=case['id'],site=s,chi1_bin_center_deg=int(center),initial=bool(states[0]==j),early_occupancy=float((states[~late]==j).mean()),late_occupancy=float((states[late]==j).mean())))
    csv(out/'sidechain_rotamers.csv',rotamers)
    snap_idx=[int(np.argmin(abs(times-t))) for t in [0,10,25,50,75,100]]
    # Coordinates and topology needed for honest, data-derived structure figures.
    np.savez_compressed(out/'representative_coordinates.npz',coordinates_A=X[snap_idx],time_ns=times[snap_idx],
        resids=u.atoms.resids,names=u.atoms.names.astype(str),resnames=u.atoms.resnames.astype(str),
        ligand_indices=lig.indices,ca_indices=ca_ids,core_fit_indices=fit_ids['core'],pocket_fit_indices=fit_ids['pocket'])
    np.savez_compressed(out/'numeric_audit.npz',time_ns=times,site84_distances_A=site_distances[cfg['sites'][0]],
        site368_distances_A=site_distances[cfg['sites'][1]],anchor_distances_A=np.array([anchor_d[a] for a in focal]),anchors=np.array(focal))
    dump(out/'completion.json',dict(status='complete',case=case['id'],n_source_frames=len(alltimes),n_sampled_frames=len(times),
        n_late_frames=int(late.sum()),n_atoms=len(u.atoms),core_fit_atoms=len(fit_ids['core']),pocket_fit_atoms=len(fit_ids['pocket']),
        source_sha256=sha(__file__),config_sha256=cfg['_config_sha256'],input_identity=identity,
        interpretation='Single trajectory; correlated timepoints; distinct initial models/poses. Geometric adjacency is not causal coupling.'))
    print('COMPLETE',case['id'],len(times),'frames',len(bridge_rows),'two-edge paths',flush=True)


def pair_detail(cfg, case):
    """Chemical detail for predeclared local pairs; kept separate from first pass."""
    out=Path(case['output'])/'pair_details';out.mkdir(parents=True,exist_ok=True)
    u=mda.Universe(case['topology']);assert sha(case['trajectory'])==case['expected_trajectory_sha256']
    pairs=cfg['receptor_pairs'];definitions=[]
    for s,n in pairs:
        left=heavy(u.select_atoms(f'protein and resid {s} and not backbone'))
        right=heavy(u.select_atoms(f'protein and resid {n}'))
        definitions.append((s,n,left.indices,right.indices))
    r368=u.select_atoms('protein and resid 368').residues[0]
    chi={}
    if r368.resname=='ARG':
        for label,names in [('chi2',['CA','CB','CG','CD']),('chi3',['CB','CG','CD','NE']),('chi4',['CG','CD','NE','CZ'])]:
            chi[label]=[r368.atoms.select_atoms('name '+n).indices[0] for n in names]
        nitrogens=r368.atoms.select_atoms('name NE NH1 NH2').indices
        oxygens=u.select_atoms('protein and resid 70 and name OD1 OD2').indices
        triplets=[(d.index,h.index,a) for d in u.atoms[nitrogens] for h in d.bonded_atoms if h.name.startswith('H') for a in oxygens]
    rows=[];rr=[];snap=[]
    with XTCFile(case['trajectory'],'r') as f:
        for i,fr in enumerate(f):
            if i%cfg['stride_frames']:continue
            x=fr.x*10;t=fr.time/1000
            for s,n,left,right in definitions:
                ds=distance_array(x[left],x[right]);a,b=np.unravel_index(ds.argmin(),ds.shape)
                rows.append(dict(time_ns=t,site=s,neighbor=n,site_atom=u.atoms[left[a]].name,neighbor_atom=u.atoms[right[b]].name,distance_A=ds[a,b]))
            if r368.resname=='ARG':
                row=dict(time_ns=t,guanidinium_Asp70_distance_A=float(distance_array(x[nitrogens],x[oxygens]).min()))
                any_hbond=False
                for d,h,a in triplets:
                    da=np.linalg.norm(x[d]-x[a]);v=x[d]-x[h];w=x[a]-x[h]
                    angle=np.degrees(np.arccos(np.clip(np.dot(v,w)/(np.linalg.norm(v)*np.linalg.norm(w)),-1,1)))
                    any_hbond |= bool(da<=3 and angle>=150)
                row['Arg368_Asp70_hbond']=any_hbond
                for label,ids in chi.items():row[label+'_deg']=float(np.degrees(calc_dihedrals(*x[ids])))
                rr.append(row)
    csv(out/'receptor_pair_atoms.csv',rows)
    csv(out/'Arg368_Asp70_geometry.csv',rr,columns=['time_ns','guanidinium_Asp70_distance_A','Arg368_Asp70_hbond','chi2_deg','chi3_deg','chi4_deg'])
    summary_rows=[]
    for s,n,_,_ in definitions:
        sub=[r for r in rows if r['site']==s and r['neighbor']==n]
        times=np.array([r['time_ns'] for r in sub]);dist=np.array([r['distance_A'] for r in sub]);late=times>=50
        summary_rows.append(dict(case=case['id'],site=s,neighbor=n,**summary(dist,times,cfg['window_ns']),
            occupancy_4A_late=float((dist[late]<=4).mean()),first_1ns_contact_ns=first_run(dist<=4,times),first_1ns_absence_ns=first_run(dist>4,times)))
    csv(out/'pair_summary.csv',summary_rows)
    dump(out/'completion.json',dict(status='complete',case=case['id'],n_frames=len(times),source_sha256=sha(__file__),config_sha256=cfg['_config_sha256']))
    print('PAIR_DETAILS_COMPLETE',case['id'],flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--prepare',action='store_true');parser.add_argument('--pair-detail',action='store_true');parser.add_argument('--case')
    args=parser.parse_args();cfg=json.loads(Path(args.config).read_text());cfg['_config_sha256']=sha(args.config)
    if args.prepare:
        prepare(cfg);return
    selections=json.loads((Path(cfg['shared_output'])/'selections.json').read_text())
    for case in cfg['cases']:
        if args.case and case['id']!=args.case:continue
        if args.pair_detail:pair_detail(cfg,case)
        else:run_case(cfg,case,selections)


if __name__=='__main__':main()
