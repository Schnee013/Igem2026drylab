#!/usr/bin/env python3
"""Independent static checks for own-parent lid candidates, not MD acceptance.

Reuses the existing local geometry screen and the projection-based linking
diagnostic from check_twf154_snapshot.py. Open-lid fan surfaces are descriptive
meshes with an artificial closing edge, never evidence of a real covalent link.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from rdkit import Chem

from sample_disulfide_lid import GeometryGate, read_pdb


def linking_numbers(curve, ring, rotations):
    values = []
    for rot in rotations:
        aa, bb = np.asarray(curve)@rot, np.asarray(ring)@rot
        signed = 0
        cross = lambda a,b: a[0]*b[1]-a[1]*b[0]
        for i,p in enumerate(aa):
            u = aa[(i+1)%len(aa)]-p
            for j,q in enumerate(bb):
                v = bb[(j+1)%len(bb)]-q
                w = q-p
                det = cross(u,v)
                if abs(det)<1e-12:
                    continue
                t,s = cross(w,v)/det,cross(w,u)/det
                if 1e-8<t<1-1e-8 and 1e-8<s<1-1e-8:
                    dz=q[2]+s*v[2]-p[2]-t*u[2]
                    signed -= 1 if det*dz>0 else -1
        values.append(signed/2)
    return sorted(set(values))


def segment_triangle(p,q,a,b,c):
    direction=q-p
    e1,e2=b-a,c-a
    h=np.cross(direction,e2)
    det=np.dot(e1,h)
    if abs(det)<1e-9:
        return None
    f=1/det;s=p-a;u=f*np.dot(s,h)
    if u < -1e-8 or u > 1+1e-8:
        return None
    z=np.cross(s,e1);v=f*np.dot(direction,z)
    if v < -1e-8 or u+v > 1+1e-8:
        return None
    t=f*np.dot(e2,z)
    if 1e-8<t<1-1e-8:
        return p+t*direction
    return None


def lid_surface_intersections(atoms, ligand_xyz, bonds):
    perimeter=np.array([atoms[(r,'CA')]['xyz'] for r in range(163,180)])
    # Two explicit choices of artificial spanning mesh; disagreement is retained.
    meshes={'centroid_fan':perimeter.mean(axis=0),'anchor_midpoint_fan':(perimeter[0]+perimeter[-1])/2}
    results={}
    for name,center in meshes.items():
        hits=[]
        for i,j in bonds:
            for k,a in enumerate(perimeter):
                pt=segment_triangle(ligand_xyz[i],ligand_xyz[j],center,a,perimeter[(k+1)%len(perimeter)])
                if pt is not None and not any(np.linalg.norm(pt-np.array(h['xyz_A']))<1e-5 for h in hits):
                    hits.append(dict(ligand_bond_1based=[i+1,j+1],xyz_A=pt.tolist()))
        results[name]=dict(count=len(hits),intersections=hits)
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',required=True,type=Path)
    ap.add_argument('--run',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    cfg=json.loads(args.config.read_text())
    assert len(cfg['ligands'])==1, 'This audit requires exactly the own combination pose'
    gate=GeometryGate(cfg)
    ligand_path=Path(next(iter(cfg['ligands'].values())))
    mol=Chem.SDMolSupplier(str(ligand_path),removeHs=False)[0]
    ligand_xyz=np.array(mol.GetConformer().GetPositions())
    rings=[list(r) for r in Chem.GetSymmSSSR(mol)]
    assert len(rings)==1 and len(rings[0])==6
    sugar=ligand_xyz[rings[0]]
    bonds=[(b.GetBeginAtomIdx(),b.GetEndAtomIdx()) for b in mol.GetBonds()
           if b.GetBeginAtom().GetAtomicNum()>1 and b.GetEndAtom().GetAtomicNum()>1]
    rng=np.random.default_rng(20261005)
    rotations=[]
    for _ in range(16):
        q,_=np.linalg.qr(rng.normal(size=(3,3)))
        q[:,2]*=np.linalg.det(q)
        rotations.append(q)
    cycle=[(99,'SG'),(99,'CB'),(99,'CA'),(99,'C')]+[(r,k) for r in range(100,173) for k in ['N','CA','C']]+[(173,'N'),(173,'CA'),(173,'CB'),(173,'SG')]
    phenyl=['CG','CD1','CE1','CZ','CE2','CD2']
    ring_defs={'PHE':[phenyl],'TYR':[phenyl],'HIS':[['CG','ND1','CE1','NE2','CD2']],
               'PRO':[['N','CA','CB','CG','CD']],
               'TRP':[['CG','CD1','NE1','CE2','CD2'],['CD2','CE2','CZ2','CH2','CZ3','CE3']]}
    rows=[]
    sources=[('parent',Path(cfg['receptor']))]+[(p.stem,p) for p in sorted(args.run.glob('candidate_*.pdb'))]
    for name,path in sources:
        atoms=read_pdb(path)
        geometry=gate.evaluate(atoms)
        closed_link=linking_numbers([atoms[k]['xyz'] for k in cycle],sugar,rotations)
        aromatic_links=[]
        for resid,resname in sorted({r:a['resname'] for (r,_),a in atoms.items()}.items()):
            for names in ring_defs.get(resname,[]):
                links=linking_numbers([atoms[resid,n]['xyz'] for n in names],sugar,rotations)
                if links!=[0.0]:
                    aromatic_links.append(dict(residue=resid,atoms=names,linking_numbers=links))
        surfaces=lid_surface_intersections(atoms,ligand_xyz,bonds)
        rows.append(dict(name=name,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            geometry=geometry,ss_loop_sugar_linking_numbers=closed_link,protein_ring_sugar_links=aromatic_links,
            covalent_cycle_link_screen_pass=closed_link==[0.0] and not aromatic_links,
            open_lid_artificial_surface_diagnostic=surfaces,
            eligible_for_visual_review=(geometry['geometric_screen_pass'] and closed_link==[0.0] and not aromatic_links),
            production_ready=False))
    result=dict(case_id=cfg['case_id'],ligand_source=str(ligand_path),ligand_sha256=hashlib.sha256(ligand_path.read_bytes()).hexdigest(),
        comparison='All candidates assessed against this case own fixed parent and own single pose',
        topology_method_source='check_twf154_snapshot.py projection-based signed crossings',projection_count=len(rotations),
        surface_scope='Open CA163-179 arc plus artificial closing chord; mesh intersections are diagnostics, not proof of a covalent interlock.',
        accepted_structure=None,rows=rows)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(case_id=cfg['case_id'],candidates=len(rows)-1,eligible_for_visual_review=sum(x['eligible_for_visual_review'] for x in rows[1:]))))


if __name__=='__main__':
    main()
