"""Validate and archive round-2 full-length AF3 inputs; never runs docking."""
import argparse
import hashlib
import importlib.util
import io
import json
import shutil
import stat
import zipfile
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "vina/src/run_vina.py").is_file())
FASTA = ROOT/'vina/inputs/receptors/fasta/04-af3-more-single-alanine'
NAMES = ['baseline','V110I','V110L','V110T','N84Q','N84S','V368I','V368L',
         'S80A','N102A','G103A','T106A','V368A','L27A','N28A','V110A','R181A','W338A','N84A_V110A_V368A']
AA = dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(), 'ARNDCQEGHILKMFPSTWYV'))

def sequences():
    files={p.stem:p for p in FASTA.glob('*/*.fasta')}
    files['baseline']=files['A81A']
    expected={g:''.join(l.strip() for l in files[g].read_text().splitlines() if not l.startswith('>')) for g in NAMES}
    source=ROOT/'projects-done/inputs&outputs-deltaNlid/inputs/receptors/fasta/Gpr2_TWF154_TGJ68930.1.fasta'
    wt=''.join(l.strip() for l in source.read_text().splitlines() if not l.startswith('>'))
    for g,s in expected.items():
        target=list(wt)
        if g!='baseline':
            for mutation in g.split('_'):
                pos=int(mutation[1:-1]);assert target[pos-1]==mutation[0]
                target[pos-1]=mutation[-1]
        assert len(s)==406 and s==''.join(target),g
    return expected

def audit(zip_path):
    from Bio.PDB.MMCIF2Dict import MMCIF2Dict
    expected=sequences();records=[]
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        jobs=[n for n in z.namelist() if n.endswith('_job_request.json')]
        assert len(jobs)==len(NAMES)
        for g in NAMES:
            job=g.lower();name=f'{job}/fold_{job}_job_request.json'
            requests=json.loads(z.read(name));assert len(requests)==1
            j=requests[0];assert len(j['sequences'])==1
            protein=j['sequences'][0]['proteinChain']
            assert protein['count']==1 and protein['sequence']==expected[g],g
            for i in range(5):
                model=f'{job}/fold_{job}_model_{i}.cif'
                d=MMCIF2Dict(io.StringIO(z.read(model).decode()))
                residues={}
                for chain,num,res in zip(d['_atom_site.auth_asym_id'],d['_atom_site.auth_seq_id'],d['_atom_site.label_comp_id']):
                    assert chain=='A'
                    n=int(num)
                    if n in residues:assert residues[n]==res
                    residues[n]=res
                assert set(residues)==set(range(1,407)),model
                assert ''.join(AA[residues[n]] for n in range(1,407))==expected[g],model
            records.append({'group':g,'residues':406,'models_verified':5,'job_request':name,'selected_model':f'{job}/fold_{job}_model_0.cif','modelSeeds':j.get('modelSeeds')})
    print('Verified 19 full-length jobs and all 95 model sequences.')
    return {'archive_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'jobs':records}

def unpack(zip_path,archive):
    report=audit(zip_path);dest=archive/'original_cif'
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            target=dest/info.filename
            assert target.resolve().is_relative_to(dest.resolve())
            assert not stat.S_ISLNK(info.external_attr>>16)
            if target.exists() and not info.is_dir():assert target.read_bytes()==z.read(info),target
        saved=archive/'original_archives'/zip_path.name
        if saved.exists():assert saved.read_bytes()==zip_path.read_bytes()
        else:
            saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(zip_path,saved)
        for info in z.infolist():
            target=dest/info.filename
            if info.is_dir():target.mkdir(parents=True,exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(info))
    fasta=archive/'fasta_full_length';fasta.mkdir(exist_ok=True)
    for g,s in sequences().items():
        path=fasta/f'Gpr2_full_length_{g}.fasta';content=f'>Gpr2_full_length_{g}\n{s}\n'
        if path.exists():assert path.read_text()==content
        else:path.write_text(content)
    (archive/'input_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Archive prepared:',archive)

def shared_module():
    spec=importlib.util.spec_from_file_location('shared',ROOT/'outputs/batches/01-sidechain-combination/cli/helpers.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    # Source PDB is already the AF3 mutant: retain every heavy atom for all substitutions.
    m.GROUPS={g:{} for g in NAMES}
    return m

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('groups')
    a=sub.add_parser('audit');a.add_argument('zip_path',type=Path)
    a=sub.add_parser('unpack');a.add_argument('zip_path',type=Path);a.add_argument('archive',type=Path)
    a=sub.add_parser('validate');a.add_argument('source',type=Path);a.add_argument('prepared',type=Path);a.add_argument('group',choices=NAMES)
    for name in ['compare','compare_contacts']:
        a=sub.add_parser(name);a.add_argument('out',type=Path)
    a=sub.add_parser('contacts');a.add_argument('receptor_json',type=Path);a.add_argument('sdf',type=Path);a.add_argument('out',type=Path)
    args=vars(p.parse_args());action=args.pop('action')
    if action=='groups':return print('\n'.join(NAMES))
    if action=='audit':return audit(**args)
    if action=='unpack':return unpack(**args)
    m=shared_module()
    if action=='validate':
        residues={k[1]:AA[v[17:20]] for k,v in m.atoms(args['source']).items()}
        assert set(residues)==m.EXPECTED
        expected=sequences()[args['group']]
        assert all(res==expected[n-1] for n,res in residues.items())
    getattr(m,action)(**args)
    if action=='compare':
        for g in NAMES:
            path=args['out']/g/'review.pml'
            path.write_text(path.read_text().replace('84+90+110+181+338+345+368','27+28+80+81+84+102+103+106+110+181+338+368'))

if __name__=='__main__':main()
