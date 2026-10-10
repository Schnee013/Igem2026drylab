#!/usr/bin/env python3
"""Use one independent WT AF3 parent and its deltaN docking poses, without redocking."""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from rdkit import Chem

from prepare_twf154_lid_matrix import atoms, named_ligand, sha, xyz


def first_pose(source, pdbqt, sdf):
    text = source.read_text().split('ENDMDL', 1)[0] + 'ENDMDL\n'
    assert text.startswith('MODEL 1\n')
    pdbqt.write_text(text)
    smiles = next(l.split('REMARK SMILES ', 1)[1] for l in text.splitlines() if l.startswith('REMARK SMILES '))
    mol = Chem.MolFromSmiles(smiles)
    mapping = []
    positions = {}
    for line in text.splitlines():
        if line.startswith('REMARK SMILES IDX '):
            f = list(map(int, line.split()[3:])); mapping.extend(zip(f[::2], f[1::2]))
        if line.startswith(('ATOM ', 'HETATM')):
            positions[int(line[6:11])] = xyz(line)
    assert len(mapping) == mol.GetNumAtoms()
    assert set(i for i, _ in mapping) == set(range(1, mol.GetNumAtoms()+1))
    conf = Chem.Conformer(mol.GetNumAtoms())
    for i, serial in mapping:
        conf.SetAtomPosition(i-1, positions[serial])
    mol.AddConformer(conf)
    original = Chem.MolToSmiles(mol)
    check = Chem.Mol(mol)
    Chem.AssignStereochemistryFrom3D(check, replaceExistingTags=True)
    assert Chem.MolToSmiles(check) == original, 'Pose coordinates disagree with encoded stereochemistry'
    mol = Chem.AddHs(mol, addCoords=True)
    with Chem.SDWriter(str(sdf)) as writer:
        writer.write(mol)
    reread = Chem.SDMolSupplier(str(sdf), removeHs=False)[0]
    assert Chem.MolToSmiles(reread) == Chem.MolToSmiles(mol)
    err = max(np.linalg.norm(np.array(reread.GetConformer().GetAtomPosition(i-1))-positions[s]) for i,s in mapping)
    assert err < 1e-6
    return {'source': str(source), 'sha256': sha(source), 'model': 1,
            'score_kcal_mol': float(next(l.split()[3] for l in text.splitlines() if l.startswith('REMARK VINA RESULT:'))),
            'heavy_coordinate_max_error_A': err, 'chemical_smiles': original,
            'conversion': 'PDBQT SMILES IDX restores bond order and stereochemistry; heavy coordinates unchanged; hydrogen coordinates added'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);a=ap.parse_args()
    cfg=json.loads(a.config.read_text());root=Path(cfg['runtime'])
    matrix=root/'inputs/matrix02';rec=matrix/'receptors';lig=matrix/'ligands'
    rec.mkdir(parents=True,exist_ok=False);lig.mkdir()
    full,deleted=Path(cfg['full_length_pdb']),Path(cfg['delta_pdb'])
    aa,bb=atoms(full),atoms(deleted)
    assert set(bb)<=set(aa)
    assert all(np.array_equal(xyz(aa[k]),xyz(bb[k])) for k in bb)
    assert {k[0] for k in aa}==set(range(1,407))
    assert {k[0] for k in aa}-{k[0] for k in bb}==set(range(1,22))|set(range(164,179))
    codes=dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),'ARNDCQEGHILKMFPSTWYV'))
    seq=''.join(codes[aa[i,'CA'][17:20]] for i in range(1,407))
    fasta=''.join(l.strip() for l in Path(cfg['fasta']).read_text().splitlines() if not l.startswith('>'))
    assert seq==fasta and seq[83]=='N' and seq[367]=='V'
    target=rec/'native_wt.pdb';shutil.copy2(full,target)
    mappings={};poses={};cases=[]
    geom=json.loads(Path(cfg['geometry_reference']).read_text())
    contracts={k:v for k,v in geom.items() if k.startswith('_')}
    for ligand in ['ascr18','ascr3']:
        key='wt_'+ligand;out=matrix/key;out.mkdir()
        poses[key]=first_pose(Path(cfg['poses'][ligand]),out/'top1.pdbqt',out/'top1.sdf')
        mappings[key]=named_ligand(out/'top1.sdf',Path(cfg['parameters'][ligand]),ligand,lig/f'{key}.pdb')
        oldkey='n84v_ascr18' if ligand=='ascr18' else 'v368r_ascr3'
        contract=json.loads(json.dumps(geom[oldkey]));assert contract['atom_names']==mappings[key]['atom_names']
        pos={l[12:16].strip():xyz(l) for l in (lig/f'{key}.pdb').read_text().splitlines() if l.startswith('HETATM')}
        for center in contract['stereocenters']:
            n=center['neighbors'];v=float(np.linalg.det(np.array([pos[k]-pos[n[3]] for k in n[:3]])))
            assert v*center['source_volume_A3']>0
            center['source_volume_A3']=v
        contract['bonds']=[[i,j,float(np.linalg.norm(pos[i]-pos[j]))] for i,j,_ in contract['bonds']]
        contract['source']=str(out/'top1.sdf');contracts[key]=contract
        lid=np.array([xyz(v) for k,v in aa.items() if 164<=k[0]<=178])
        heavy=np.array([pos[k] for k in contract['heavy_atoms']])
        poses[key]['initial_lid_distance_A']=float(np.linalg.norm(lid[:,None]-heavy[None,:],axis=2).min())
        cases.append({'id':'native_wt_'+ligand,'genotype':'wt','ligand':ligand,'lid':'native',
                      'receptor':str(target),'pose':str(lig/f'{key}.pdb'),'pose_mapping':key,
                      'purpose':'independent WT full-length parent plus own deltaN pose','production_authorized':False})
    data={'config':cfg,'derivations':{},'receptor_source':{'full_length':str(full),'sha256':sha(full),
          'delta':str(deleted),'delta_sha256':sha(deleted),'sequence':seq,'shared_coordinate_error_A':0,
          'model_selection':'fixed AF3 model 0, same rule as mutant inputs; not selected by ligand preference'},
          'poses':poses,'ligand_mappings':mappings,'cases':cases,
          'checksums':{str(p):sha(p) for d in [rec,lig] for p in d.iterdir()}}
    (matrix/'matrix.json').write_text(json.dumps(data,indent=2)+'\n')
    (root/'inputs/ligand_geometry_contract_v2.json').write_text(json.dumps(contracts,indent=2)+'\n')
    print(json.dumps({'sequence_matches':True,'poses':poses},indent=2))


if __name__=='__main__':main()
