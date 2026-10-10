#!/usr/bin/env python3
"""Assemble dry full-length complexes with one shared, clash-screened POPC slab.

Uses no historical receptor coordinates. PPM supplies a common rigid transform;
only POPC coordinates/topology and force-field parameters come from the old base.
Outputs require solvation, ions, minimization, and heating before interpretation.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import shutil
import numpy as np
from scipy.spatial import cKDTree
from assemble_complex import parse_gro, write_gro
from prepare_twf154_forcefield import prepare as prepare_forcefield


def pdb_rows(p):
    return [{'resnum':int(l[22:26]),'resname':l[17:20].strip(),'atomname':l[12:16].strip(),
             'element':l[76:78].strip() or l[12:16].strip()[0],
             **dict(zip('xyz',[float(l[i:i+8])/10 for i in (30,38,46)]))}
            for l in p.read_text().splitlines() if l.startswith(('ATOM  ','HETATM'))]


def array(rows):return np.array([[r[k] for k in 'xyz'] for r in rows])


def moved(rows, rot, shift):
    return [{**r,**dict(zip('xyz',v))} for r,v in zip(rows,array(rows)@rot+shift)]


def protein_itp(src,dst):
    text=src.read_text();text=text[text.index('[ moleculetype ]'):]
    text=text.split('; Include Position restraint file')[0]
    text=text.split('#ifdef POSRES')[0]
    assert '[ molecules ]' not in text
    text=text.replace('Protein_chain_A','PROA')
    section=None;atoms=[];bonds=[]
    for line in text.splitlines():
        t=line.split(';')[0].strip()
        if t.startswith('['):section=t.strip('[] ')
        elif t and not t.startswith('#'):
            if section=='atoms':atoms.append(t.split())
            if section=='bonds':bonds.append(t.split()[:2])
    sg={int(x[2]):x[0] for x in atoms if x[4]=='SG'}
    assert [sg[99],sg[173]] in bonds or [sg[173],sg[99]] in bonds
    text+='\n#ifdef POSRES\n[ position_restraints ]\n'
    for row in atoms:
        if float(row[7])<2 or 164<=int(row[2])<=178:continue
        fc='POSRES_FC_BB' if row[4] in {'N','CA','C','O','OT1','OT2'} else 'POSRES_FC_SC'
        text+=f'{row[0]} 1 {fc} {fc} {fc}\n'
    dst.write_text(text+'#endif\n')
    return {'atoms':len(atoms),'charge':sum(float(x[6]) for x in atoms),'ss_atom_indices':[int(sg[99]),int(sg[173])],
            'lid_position_restraints':False}


def cgenff_clean(src,dst,drop_atomtypes=False):
    section=None;out=[];seen={};removed=[]
    sizes={'atomtypes':1,'bondtypes':2,'pairtypes':2,'angletypes':3,'dihedraltypes':4}
    def norm(v):
        try:return round(float(v),9)
        except ValueError:return v
    for no,line in enumerate(src.read_text().splitlines(),1):
        t=line.split(';')[0].strip()
        if t.startswith('['):
            section=t.strip('[] ')
            if section!='defaults' and not (drop_atomtypes and section=='atomtypes'):out.append(line)
            continue
        if section=='defaults' or (drop_atomtypes and section=='atomtypes'):continue
        if not t:out.append(line);continue
        n=sizes[section];f=t.split();types=tuple(f[:n]);types=min(types,tuple(reversed(types))) if section!='atomtypes' else types
        key=(section,types,tuple(norm(v) for v in f[n:]))
        # Remove only numerically identical reverse-equivalent parameter rows.
        # Distinct Fourier terms are retained, not collapsed by atom-type tuple.
        if key in seen:removed.append({'line':no,'duplicate_of':seen[key],'text':t});continue
        seen[key]=no;out.append(line)
    dst.write_text('\n'.join(out)+'\n');return removed


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();cfg=json.loads(a.config.read_text());root=Path(cfg['runtime']);base=Path(cfg['base']);matrix=json.loads((root/'inputs/matrix02/matrix.json').read_text())
    tr=json.loads((root/'results/ppm_transform.json').read_text());assert tr['max_error_A']<0.001
    rot=np.array(tr['rotation_matrix']);shift=np.array(tr['translation_vector'])/10
    _,old,boxline=parse_gro(base/'step5_input.gro');box=np.array([float(v) for v in boxline.split()[:3]]);box[2]=18.0
    # Only lipid rows are read into the new assemblies; old protein/water/ions are discarded.
    lipids=defaultdict(list)
    for r in old:
        if r['resname']=='POPC':lipids[r['resnum']].append(r)
    pz=np.array([r['z'] for v in lipids.values() for r in v if r['atomname']=='P'])
    mid=(pz[pz<np.mean(pz)].mean()+pz[pz>np.mean(pz)].mean())/2
    origin=np.array([box[0]/2,box[1]/2,11.65]);shift+=origin
    rec={p.stem:pdb_rows(root/'inputs/protein_topologies02'/p.stem/'protein.pdb') for p in (root/'inputs/matrix02/receptors').glob('*.pdb')}
    rec={k:moved(v,rot,shift) for k,v in rec.items()}
    lig={p.stem:moved(pdb_rows(p),rot,shift) for p in (root/'inputs/matrix02/ligands').glob('*.pdb')}
    union=[r for rows in [*rec.values(),*lig.values()] for r in rows if r['element']!='H']
    xyz=array(union);tree=cKDTree(xyz%box,boxsize=box)
    # Orient/translate the lipid slab to fit its existing cavity to this parent.
    # No protein or ligand coordinates participate as a replaceable template.
    lipid_rows=[r for v in lipids.values() for r in v]
    heavy_rows=[r for r in lipid_rows if not r['atomname'].startswith('H')]
    hx=array(heavy_rows)-np.array([box[0]/2,box[1]/2,mid])
    hr=np.array([r['resnum'] for r in heavy_rows]);fitting=[]
    assert abs(box[0]-box[1])<1e-5, 'Slab rotation requires a square periodic cell'
    for angle in range(0,360,90):
        theta=np.deg2rad(angle);rz=np.array([[np.cos(theta),np.sin(theta),0],[-np.sin(theta),np.cos(theta),0],[0,0,1]])
        for dx in np.arange(-1.5,1.51,0.5):
            for dy in np.arange(-1.5,1.51,0.5):
                tt=origin+np.array([dx,dy,0]);dd=tree.query((hx@rz+tt)%box)[0]
                removed_ids=set(hr[dd<0.28]);fitting.append((len(removed_ids),abs(dx)+abs(dy),angle,float(dx),float(dy)))
    best=min(fitting);theta=np.deg2rad(best[2]);rz=np.array([[np.cos(theta),np.sin(theta),0],[-np.sin(theta),np.cos(theta),0],[0,0,1]])
    tt=origin+np.array([best[3],best[4],0])-np.array([box[0]/2,box[1]/2,mid])@rz
    retained=[];removal=[];counts=defaultdict(int)
    for resid,rows in lipids.items():
        rows=moved(rows,rz,tt)
        com=array(rows).mean(0);wrap=np.array([-np.floor(com[0]/box[0])*box[0],-np.floor(com[1]/box[1])*box[1],0])
        rows=moved(rows,np.eye(3),wrap);heavy=[r for r in rows if not r['atomname'].startswith('H')]
        distances,idx=tree.query(array(heavy)%box);d=float(distances.min())
        # Conservative 0.28 nm heavy-atom exclusion for the shared slab, before EM.
        leaflet='upper' if next(r['z'] for r in rows if r['atomname']=='P')>origin[2] else 'lower'
        if d<0.28:removal.append({'resid':resid,'leaflet':leaflet,'min_distance_nm':d});continue
        retained.extend(rows);counts[leaflet]+=1
    a.out.mkdir(parents=True,exist_ok=False)
    audit={'source_membrane':str(base/'step5_input.gro'),'only_reused_residue':'POPC','original_lipids':len(lipids),
           'retained_per_leaflet':dict(counts),'removed':removal,'box_nm':box.tolist(),'membrane_center_nm':origin.tolist(),
           'coordinate_transform':{'R':rot.tolist(),'t_nm':shift.tolist()},
           'slab_fit':{'best_deleted_count':best[0],'rotation_degrees':best[2],'shift_xy_nm':best[3:],
                       'trials':len(fitting),'criterion':'minimize removed lipid molecules using only lipid cavity geometry'},'cases':[]}
    (a.out/'membrane_audit.json').write_text(json.dumps(audit,indent=2))
    # Substantial slab damage requires a new packing route, never hidden equilibration.
    assert len(removal)<=25, f'Too many lipids removed for slab reuse: {len(removal)}'
    assert min(counts.values())>=80
    protected=set()
    for path in [base/'toppar/POPC.itp',*[root/'inputs/protein_topologies02'/k/'protein.top' for k in rec]]:
        section=''
        for line in path.read_text().splitlines():
            t=line.split(';')[0].strip()
            if t.startswith('['):section=t.strip('[] ')
            elif section=='atoms' and t and not t.startswith('#'):protected.add(t.split()[1])
    (a.out/'ff').mkdir()
    for ligand in ['ascr18','ascr3']:
        par=Path(matrix['config']['parameters'][ligand]);fragment=a.out/'ff'/f'{ligand}_fragment.itp'
        cgenff_clean(par/'gromacs/charmm36.itp',fragment)
        prepare_forcefield(root/'envs/charmm36-jul2022.ff',fragment,a.out/'ff'/f'{ligand}.ff',protected)
    for case in matrix['cases']:
        d=a.out/case['id'];d.mkdir();top=d/'toppar';top.mkdir()
        info=protein_itp(root/'inputs/protein_topologies02'/f"{case['lid']}_{case['genotype']}"/'protein.top',top/'PROA.itp')
        for name in ['POPC','POT','CLA']:
            shutil.copy2(base/'toppar'/f'{name}.itp',top/f'{name}.itp')
        shutil.copy2(root/'envs/charmm36-jul2022.ff/tip3p.itp',top/'water.itp')
        par=Path(matrix['config']['parameters'][case['ligand']]);upper=case['ligand'].upper()
        duplicates=cgenff_clean(par/'gromacs/charmm36.itp',top/'cgenff.itp',drop_atomtypes=True)
        ltext=(par/'gromacs'/f'{upper}.itp').read_text()
        ligand_rows=lig[case['pose_mapping']]
        ltext+='\n#ifdef POSRES\n[ position_restraints ]\n'
        for i,r in enumerate(ligand_rows,1):
            if r['element']!='H':ltext+=f'{i} 1 POSRES_FC_LIG POSRES_FC_LIG POSRES_FC_LIG\n'
        (top/f'{upper}.itp').write_text(ltext+'#endif\n')
        ligand_rows=[{**r,'resnum':407,'resname':upper[:5]} for r in ligand_rows]
        rows=rec[f"{case['lid']}_{case['genotype']}"]+ligand_rows+retained
        coords=array(rows)
        assert coords[:,2].min()>1.2 and coords[:,2].max()<box[2]-1.2
        write_gro(d/'dry.gro',case['id']+' dry diagnostic input',rows,' '.join(f'{v:.5f}' for v in box))
        includes=['cgenff','PROA',upper,'POPC','POT','CLA','water']
        text=f'#include "../ff/{case["ligand"]}.ff/forcefield.itp"\n'
        text+='\n'.join(f'#include "toppar/{x}.itp"' for x in includes)
        text+=f'\n\n[ system ]\n{case["id"]}\n\n[ molecules ]\nPROA 1\n{upper} 1\nPOPC {sum(counts.values())}\n'
        (d/'topol.top').write_text(text)
        info.update(case);info.update({'dry_atoms':len(rows),'removed_identical_parameter_rows':duplicates,'lipids':dict(counts)})
        (d/'input_contract.json').write_text(json.dumps(info,indent=2));audit['cases'].append(info)
    (a.out/'membrane_audit.json').write_text(json.dumps(audit,indent=2))
    shutil.copy2(__file__,a.out/'producer.py');shutil.copy2(a.config,a.out/'config.json')
    print(json.dumps({'cases':len(audit['cases']),'lipids':dict(counts),'removed':len(removal)}))


if __name__=='__main__':main()
