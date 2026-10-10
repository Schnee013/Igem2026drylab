#!/usr/bin/env python3
"""Preparation snapshot audit, not a production-trajectory analysis driver."""
import argparse
from collections import defaultdict
import json
import hashlib
import math
from pathlib import Path


def read_gro(path):
    lines=path.read_text().splitlines();n=int(lines[1])
    atoms=[(int(l[:5]),l[5:10].strip(),l[10:15].strip(),[float(l[i:i+8]) for i in (20,28,36)]) for l in lines[2:2+n]]
    return atoms,list(map(float,lines[2+n].split()))


def equilibrium_bonds(case):
    """Expand the actual preprocessed original topology, including all POPC copies."""
    source=case/'em.processed.top';data=source.read_bytes();sha=hashlib.sha256(data).hexdigest();cache=case/'original_bond_contract.json'
    if cache.exists():
        contract=json.loads(cache.read_text())
        if contract['source_sha256']==sha:return contract
    params={};molecules={};counts=[];section='';current=None
    for line in data.decode().splitlines():
        t=line.split(';')[0].strip()
        if not t or t.startswith('#'):continue
        if t.startswith('['):section=t.strip('[] ').strip();continue
        f=t.split()
        if section=='bondtypes':params[tuple(sorted(f[:2]))+(f[2],)]=float(f[3])
        elif section=='moleculetype':current=f[0];molecules[current]={'atoms':{},'bonds':[]}
        elif section=='atoms':molecules[current]['atoms'][int(f[0])]=f
        elif section=='bonds':molecules[current]['bonds'].append(f)
        elif section=='molecules':counts.append((f[0],int(f[1])))
    bonds=[];offset=0
    for name,count in counts:
        m=molecules[name];na=len(m['atoms']);assert set(m['atoms'])==set(range(1,na+1))
        for copy in range(count):
            for f in m['bonds']:
                i,j=int(f[0]),int(f[1]);assert f[2]=='1',f
                length=float(f[3]) if len(f)>=5 else params[tuple(sorted([m['atoms'][i][1],m['atoms'][j][1]]))+(f[2],)]
                bonds.append([offset+i-1,offset+j-1,length,name])
            offset+=na
    contract={'source':str(source),'source_sha256':sha,'atom_count':offset,'bonds':bonds}
    cache.write_text(json.dumps(contract,separators=(',',':')));return contract


def audit(case, snapshot, config, allow_box_change=False):
    info=json.loads((case/'input_contract.json').read_text())
    ref,box=read_gro(case/'ionized.gro');out,box2=read_gro(snapshot)
    assert len(ref)==len(out) and len(box)==3 and len(box2)==3
    affine_scale=[1.0,1.0,1.0]
    if allow_box_change:
        assert all(v>0 and math.isfinite(v) for v in box2)
        affine_scale=[v/u for u,v in zip(box,box2)]
        # Map the reference periodically into the new cell. Positive axis scaling
        # preserves chirality; coordinate displacement now includes this mapping.
        ref=[(r,res,name,[v*s for v,s in zip(pos,affine_scale)]) for r,res,name,pos in ref]
        box=box2
    else:
        assert box==box2
    assert [a[:3] for a in ref]==[a[:3] for a in out]
    assert all(math.isfinite(x) for a in out for x in a[3])
    def delta(a,b):return [v-round(v/L)*L for v,L in zip([x-y for x,y in zip(a,b)],box)]
    def dist(a,b):return math.sqrt(sum(x*x for x in delta(a,b)))
    def det(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
    def volume(m,center,names):
        return det(*[delta(m[k],m[center]) for k in names])
    nr=info['atoms'];pr=[{(a[0],a[2]):a[3] for a in aa[:nr]} for aa in (ref,out)]
    inversions=[]
    for r in range(1,407):
        for center,names in [('CA',['N','C','CB']),('CB',['CA','OG1','CG2']),('CB',['CA','CG1','CG2'])]:
            keys=[(r,k) for k in names]
            if all(k in pr[0] for k in keys) and volume(pr[0],(r,center),keys)*volume(pr[1],(r,center),keys)<=0:
                inversions.append([r,center])
    ss=dist(pr[1][99,'SG'],pr[1][173,'SG'])
    peptide=[dist(pr[1][r,'C'],pr[1][r+1,'N']) for r in range(1,406)]
    cfg=config[info['pose_mapping']];nl=len(cfg['atom_names'])
    lig=[{a[2]:a[3] for a in aa[nr:nr+nl]} for aa in (ref,out)]
    assert list(lig[0])==cfg['atom_names']
    ligand_inversions=[]
    for chiral in cfg['stereocenters']:
        names=chiral['neighbors'];d=names[3]
        v=volume(lig[1],d,names[:3])
        if v*chiral['source_volume_A3']<=0:ligand_inversions.append(chiral['center'])
    bond_details=[{'atoms':[a,b],'seed_A':length,'snapshot_A':dist(lig[1][a],lig[1][b])*10,
                   'ratio':max(dist(lig[1][a],lig[1][b])/(length/10),(length/10)/dist(lig[1][a],lig[1][b]))}
                  for a,b,length in cfg['bonds']]
    worst_bond=max(bond_details,key=lambda b:b['ratio']);ligand_bond_ratio=worst_bond['ratio']
    lipid_inversions=[]
    lipid=[defaultdict(dict),defaultdict(dict)]
    for j,aa in enumerate((ref,out)):
        for r,res,name,pos in aa:
            if res=='POPC':lipid[j][r][name]=pos
    for r in lipid[0]:
        if volume(lipid[0][r],'C2',['C1','C3','O21'])*volume(lipid[1][r],'C2',['C1','C3','O21'])<=0:lipid_inversions.append(r)
    waters=defaultdict(list)
    for r,res,name,pos in out:
        if res=='SOL':waters[r].append(pos)
    err=0
    for pp in waters.values():
        assert len(pp)==3
        err=max(err,abs(dist(pp[0],pp[1])-.09572),abs(dist(pp[0],pp[2])-.09572),abs(dist(pp[1],pp[2])-.15139))
    heavy=cfg['heavy_atoms'];lid=[a[3] for a in out[:nr] if 164<=a[0]<=178 and not a[2].startswith('H')]
    mind=min(dist(a,lig[1][b]) for a in lid for b in heavy)*10
    rms=math.sqrt(sum(dist(lig[0][k],lig[1][k])**2 for k in heavy)/len(heavy))*10
    cycle=[(99,'SG'),(99,'CB'),(99,'CA'),(99,'C')]+[(r,k) for r in range(100,173) for k in ['N','CA','C']]+[(173,'N'),(173,'CA'),(173,'CB'),(173,'SG')]
    def unwrap(points):
        unwrapped=[points[0]]
        for previous,current in zip(points,points[1:]):unwrapped.append([v+d for v,d in zip(unwrapped[-1],delta(current,previous))])
        return unwrapped
    def links(curve,ring):
        curve,ring=unwrap(curve),unwrap(ring)
        shift=[a+d-b for a,d,b in zip(curve[0],delta(ring[0],curve[0]),ring[0])]
        ring=[[v+s for v,s in zip(p,shift)] for p in ring];linkings=[]
        cross=lambda a,b:a[0]*b[1]-a[1]*b[0]
        for rot in config['_topology_projection_rotations']:
            project=lambda points:[[sum(p[k]*rot[k][j] for k in range(3)) for j in range(3)] for p in points]
            aa,bb=project(curve),project(ring);signed=0
            for i,p in enumerate(aa):
                u=[v-w for v,w in zip(aa[(i+1)%len(aa)],p)]
                for j,q in enumerate(bb):
                    v=[x-y for x,y in zip(bb[(j+1)%len(bb)],q)];w=[x-y for x,y in zip(q,p)];det=cross(u,v)
                    if abs(det)<1e-12:continue
                    t,s=cross(w,v)/det,cross(w,u)/det
                    if 1e-8<t<1-1e-8 and 1e-8<s<1-1e-8:
                        dz=q[2]+s*v[2]-p[2]-t*u[2];signed-=1 if det*dz>0 else -1
            linkings.append(signed/2)
        return sorted(set(linkings))
    sugar=[lig[1][k] for k in cfg['sugar_ring_names']]
    linking_values=links([pr[1][k] for k in cycle],sugar)
    bc=equilibrium_bonds(case);assert bc['atom_count']==len(out);worst={};bad_bonds=[]
    # Severe clashes can trap sugar through an aromatic ring as well as the SS loop.
    phenyl=['CG','CD1','CE1','CZ','CE2','CD2'];imidazole=['CG','ND1','CE1','NE2','CD2']
    ring_defs={'PHE':[phenyl],'TYR':[phenyl],'HSD':[imidazole],'HSE':[imidazole],'HSP':[imidazole],
               'PRO':[['N','CA','CB','CG','CD']],
               'TRP':[['CG','CD1','NE1','CE2','CD2'],['CD2','CE2','CZ2','CH2','CZ3','CE3']]}
    residue_names={a[0]:a[1] for a in out[:nr]};protein_indices={(a[0],a[2]):i for i,a in enumerate(out[:nr])}
    edges={tuple(sorted([i,j])) for i,j,eq,name in bc['bonds']};ring_links=[];ring_count=0
    for residue,resname in residue_names.items():
        for names in ring_defs.get(resname,[]):
            indices=[protein_indices[residue,k] for k in names]
            assert all(tuple(sorted([indices[i],indices[(i+1)%len(indices)]])) in edges for i in range(len(indices)))
            values=links([pr[1][residue,k] for k in names],sugar);ring_count+=1
            if values!=[0]:ring_links.append({'residue':residue,'resname':resname,'ring_atoms':names,'linking_numbers':values})
    for i,j,eq,name in bc['bonds']:
        length=dist(out[i][3],out[j][3]);ratio=max(length/eq,eq/length) if length>0 else float('inf')
        detail={'molecule':name,'atom_indices_1based':[i+1,j+1],'atoms':[out[i][:3],out[j][:3]],'equilibrium_A':eq*10,'snapshot_A':length*10,'ratio':ratio}
        if name not in worst or ratio>worst[name]['ratio']:worst[name]=detail
        if ratio>=1.20:bad_bonds.append(detail)
    passed=not(inversions or ligand_inversions or lipid_inversions or bad_bonds or ring_links) and .19<ss<.22 and min(peptide)>.10 and max(peptide)<.18 and err<.003 and ligand_bond_ratio<1.20 and linking_values==[0]
    return {'case':info['id'],'snapshot':str(snapshot),'finite_coordinates':True,'protein_chirality_inversions':inversions,
            'reference_affine_box_scale':affine_scale,
            'ligand_chirality_inversions':ligand_inversions,'popc_chirality_inversions':lipid_inversions,
            'ss_distance_A':ss*10,'peptide_bond_range_A':[min(peptide)*10,max(peptide)*10],
            'ligand_max_bond_ratio_vs_seed':ligand_bond_ratio,'ligand_worst_bond':worst_bond,
            'ligand_bond_ratio_limit':1.20,'water_max_distance_error_nm':err,
            'lid_ligand_min_heavy_A':mind,'ligand_heavy_no_fit_rmsd_vs_start_A':rms,'pass':passed,
            'ss_loop_sugar_linking_numbers':linking_values,'topology_views':len(config['_topology_projection_rotations']),
            'protein_ring_pairs_checked':ring_count,'protein_ring_sugar_links':ring_links,
            'all_bond_count':len(bc['bonds']),'all_bond_worst_by_molecule':worst,'all_bonds_outside_20pct':bad_bonds,
            'topology_note':'Closed covalent-loop diagnostic under the retained 99-173 disulfide assumption; zero linking number is not a proof against every possible link type',
            'scope':'preparation snapshot geometry only; no thermodynamic or mechanistic inference'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('snapshot',type=Path);p.add_argument('config',type=Path);p.add_argument('output',type=Path);p.add_argument('--allow-box-change',action='store_true');a=p.parse_args()
    report=audit(a.case,a.snapshot,json.loads(a.config.read_text()),a.allow_box_change);a.output.write_text(json.dumps(report,indent=2));print(json.dumps(report));assert report['pass'],report
