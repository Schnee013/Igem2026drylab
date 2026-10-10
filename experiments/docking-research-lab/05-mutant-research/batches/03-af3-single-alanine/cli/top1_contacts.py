"""User-run ProLIF analysis of the minimum-score pose, with PyMOL residue display."""
import argparse
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True,help='One receptor/ligand docking directory')
    a=parser.parse_args();run_dir=a.run_dir.resolve();receptor_dir=run_dir.parent
    root=next(p for p in Path(__file__).resolve().parents if (p / "vina/src/run_vina.py").is_file())
    source=run_dir/'poses.pdbqt';report=json.loads((run_dir/'run.json').read_text())
    assert report['return_code']==0
    assert hashlib.sha256(source.read_bytes()).hexdigest()==report['output']['sha256']
    assert hashlib.sha256((receptor_dir/'receptor.pdbqt').read_bytes()).hexdigest()==report['inputs']['receptor']['sha256']
    text=source.read_text()
    blocks=re.findall(r'^MODEL\s+\d+[^\n]*\n.*?^ENDMDL[^\n]*(?:\n|$)',text,re.M|re.S)
    assert blocks,'No complete MODEL blocks found'
    candidates=[]
    for block in blocks:
        score=re.search(r'^REMARK VINA RESULT:\s+([-+\d.eE]+)',block,re.M)
        assert score, 'Missing Vina score'
        candidates.append((float(score[1]),int(re.match(r'MODEL\s+(\d+)',block)[1]),block))
    score,mode,block=min(candidates,key=lambda item:(item[0],item[1]))
    out=run_dir/'top1_contacts'
    assert not out.exists(),f'Refusing to overwrite: {out}'
    out.mkdir()
    # Preserve all Meeko metadata stored in the chosen model and any pre-model header.
    header=text[:text.index(blocks[0])]
    (out/'top1.pdbqt').write_text(header+block)
    subprocess.run([sys.executable,str(root/'vina/src/export_ligand_pdbqt_to_sdf.py'),
        '--input',str(out/'top1.pdbqt'),'--output',str(out/'top1.sdf'),
        '--meeko-python',sys.executable],check=True)
    from rdkit import Chem
    molecules=list(Chem.SDMolSupplier(str(out/'top1.sdf'),removeHs=False))
    assert len(molecules)==1 and molecules[0] is not None,'Expected exactly one exported pose'
    shared_path=root/'outputs/batches/01-sidechain-combination/cli/helpers.py'
    spec=importlib.util.spec_from_file_location('gpr2_contact_helpers',shared_path)
    shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
    shared.contacts(receptor_dir/'receptor.json',out/'top1.sdf',out/'ifp')
    rows=list(csv.reader((out/'ifp/ifp_presence.csv').open()))
    assert len(rows[4:])==1,'Expected exactly one contact row'
    contacts={}
    for i,value in enumerate(rows[4][1:],1):
        if value.lower()=='true':contacts.setdefault(rows[1][i],set()).add(rows[2][i])
    def residue_number(label):
        match=re.fullmatch(r'[A-Z]+(\d+)\.A',label);assert match,label
        return int(match[1])
    labels=sorted(contacts,key=residue_number)
    with (out/'contact_residues.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['residue','original_number','interaction_types'])
        for label in labels:writer.writerow([label,residue_number(label),';'.join(sorted(contacts[label]))])
    prefix=re.sub(r'[^A-Za-z0-9_]','_',receptor_dir.name+'_'+run_dir.name)
    protein=prefix+'_receptor';ligand=prefix+'_top1';selection=prefix+'_contacts'
    residues='+'.join(str(residue_number(label)) for label in labels)
    commands=[f'load "{receptor_dir / "prepared.pdb"}", {protein}',
              f'load "{out / "top1.sdf"}", {ligand}',
              f'hide everything, {protein} or {ligand}',f'show cartoon, {protein}',
              f'color gray70, {protein}',f'show sticks, {ligand}',f'color cyan, {ligand}',
              f'select {selection}, '+(f'{protein} and chain A and resi {residues}' if residues else 'none'),
              f'show sticks, {selection}',f'color yellow, {selection} and elem C',
              f'label {selection} and name CA, "%s%s" % (resn, resi)',
              f'hide everything, ({protein} or {ligand}) and hydro',f'zoom {ligand}, 8']
    (out/'view_contacts.pml').write_text('\n'.join(commands)+'\n')
    (out/'selection.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'selected_original_mode':mode,'vina_score_kcal_mol':score,'tied_minimum_modes':[m for s,m,b in candidates if s==score],
        'selection_rule':'Minimum reported Vina score; lowest mode number breaks ties',
        'analyzed_pose_count':1,'unique_contact_residues':len(labels),'pose_index_in_ifp':0},indent=2)+'\n')
    print(f'Selected Vina mode {mode}, score {score}; analyzed one pose, {len(labels)} contact residues.')
    print(out/'contact_residues.csv');print(out/'view_contacts.pml')


if __name__=='__main__':main()
