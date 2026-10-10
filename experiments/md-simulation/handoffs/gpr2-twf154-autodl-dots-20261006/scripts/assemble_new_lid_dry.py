#!/usr/bin/env python3
"""Place a case-own rebuilt receptor into its own original dry membrane frame.

Requires a reviewed pdb2gmx protein.gro/protein.top made from THIS candidate.
Keeps the original own ligand and lipids byte-coordinate-identical. Stops on a
new lipid clash; does not delete lipids, move ligand, or switch protein parent.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gro(p):
    lines=p.read_text().splitlines();n=int(lines[1]);assert len(lines)==n+3
    return lines,[(int(l[:5]),l[5:10].strip(),l[10:15].strip(),np.array([float(l[i:i+8])*10 for i in [20,28,36]])) for l in lines[2:n+2]]
def itp(p):
    sec=None;out={}
    for line in p.read_text().splitlines():
        t=line.split(';')[0].strip()
        if t.startswith('['):sec=t.strip('[] ')
        elif t and not t.startswith('#') and sec:out.setdefault(sec,[]).append(t.split())
    return out
def parent_atoms(p):
    out={}
    for l in p.read_text().splitlines():
        if not l.startswith('ATOM  ') or l[76:78].strip()=='H':continue
        r=int(l[22:26]);name=l[12:16].strip()
        if l[17:20]=='ILE' and name=='CD1':name='CD'
        if r==406:name={'O':'OT1','OXT':'OT2'}.get(name,name)
        out[r,name]=np.array([float(l[i:i+8]) for i in [30,38,46]])
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case-dir',type=Path,required=True)
    ap.add_argument('--protein-gro',type=Path,required=True)
    ap.add_argument('--protein-top',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();case=a.case_dir.resolve();meta=json.loads((case/'case.json').read_text())
    assert meta['new_lid'];cfg=json.loads((case/'rebuild_support/input_contract.json').read_text())
    oldlines,old=gro(case/'reference/original_dry.gro');_,protein=gro(a.protein_gro)
    assert len(protein)==cfg['atoms']
    expected=itp(case/'rebuild_support/toppar/PROA.itp');actual=itp(a.protein_top)
    # Same residue identities, atom names/types, charges/masses and bonds.
    for x,y in zip(expected['atoms'],actual['atoms']):
        assert x[:6]==y[:6],(x,y)
        assert abs(float(x[6])-float(y[6]))<1e-6 and abs(float(x[7])-float(y[7]))<1e-5
    assert len(expected['atoms'])==len(actual['atoms'])==len(protein)
    edges=lambda top:{tuple(sorted(map(int,b[:2]))) for b in top['bonds']}
    assert edges(expected)==edges(actual), 'Changed covalent topology, including disulfide'
    assert [(r,n) for r,res,n,x in protein]==[(int(row[2]),row[4]) for row in expected['atoms']]
    new={(r,n):x for r,res,n,x in protein if not n.startswith('H')}
    candidate=parent_atoms(case/meta['candidate_receptor'])
    assert set(candidate)==set(new)
    terminal={(406,'OT1'),(406,'OT2')}
    differences={str(k):float(np.linalg.norm(new[k]-v)) for k,v in candidate.items()}
    assert max(float(np.linalg.norm(new[k]-v)) for k,v in candidate.items() if k not in terminal)<.02
    assert max(float(np.linalg.norm(new[k]-candidate[k])) for k in terminal)<.6
    tr=json.loads((case/'reference/docking_to_dry.json').read_text());rot=np.array(tr['rotation']);shift=np.array(tr['translation_A'])
    xyz=np.array([x for r,res,n,x in protein])@rot+shift
    ligand_and_lipids=old[len(protein):]
    box=np.array([float(v)*10 for v in oldlines[-1].split()]);assert len(box)==3
    heavy_lid=np.array([xyz[i] for i,(r,res,n,x) in enumerate(protein) if 164<=r<=178 and not n.startswith('H')])
    lipid=np.array([x for r,res,n,x in ligand_and_lipids if res=='POPC' and not n.startswith('H')])
    d=heavy_lid[:,None]-lipid[None];d-=np.rint(d/box)*box
    nearest=float(np.linalg.norm(d,axis=2).min())
    assert nearest>=2.8, f'New lid/POPC clash {nearest} A; review packing, do not silently delete molecules'
    a.output.mkdir(parents=True,exist_ok=False)
    shutil.copytree(case/'rebuild_support/toppar',a.output/'toppar')
    forcefield=case.parents[1]/'forcefields'/f"{meta['ligand']}.ff"
    shutil.copytree(forcefield,a.output/'ff')
    top=(case/'rebuild_support/topol.top').read_text().splitlines()
    top=[('#include "ff/forcefield.itp"' if 'forcefield.itp' in l and l.startswith('#include') else l) for l in top]
    (a.output/'topol.top').write_text('\n'.join(top)+'\n')
    lines=[meta['case_id']+' own lid dry start, NOT EQUILIBRATED',oldlines[1]]
    for i,((r,res,n,x),q) in enumerate(zip(protein,xyz),1):lines.append(f'{r%100000:5d}{res:>5s}{n:>5s}{i%100000:5d}'+''.join(f'{v/10:8.3f}' for v in q))
    lines+=oldlines[2+len(protein):]
    (a.output/'dry.gro').write_text('\n'.join(lines)+'\n')
    (a.output/'input_contract.json').write_text(json.dumps(cfg,indent=2)+'\n')
    report=dict(case_id=meta['case_id'],candidate_sha256=sha(case/meta['candidate_receptor']),
                protein_gro_sha256=sha(a.protein_gro),protein_top_sha256=sha(a.protein_top),
                ligand_and_lipid_coordinates_unchanged=True,protein_heavy_changes_in_pdb2gmx_A=differences,
                terminal_oxygen_preparation_changes_reported=True,lid_popc_min_heavy_A=nearest,
                rigid_transform=tr,production_ready=False)
    (a.output/'assembly_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'case':meta['case_id'],'dry_atoms':len(old),'lid_popc_min_A':nearest,'production_ready':False}))

if __name__=='__main__':main()
