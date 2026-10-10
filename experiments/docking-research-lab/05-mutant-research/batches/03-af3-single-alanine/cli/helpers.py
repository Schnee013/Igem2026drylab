"""User-run archive preparation and adapters for eight single-mutant groups."""
import argparse
import hashlib
import importlib.util
import json
import shutil
import stat
import zipfile
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "vina/src/run_vina.py").is_file())
GROUPS = {'baseline': {}, 'N84A': {84:'N'}, 'L90A': {90:'L'},
          'R345A': {345:'R'}, 'V110A': {110:'V'}, 'R181A': {181:'R'},
          'W338A': {338:'W'}, 'V368A': {368:'V'}}


def unpack(zip_path, archive):
    source = ROOT/'projects-done/inputs&outputs-deltaNlid/inputs/receptors/fasta/Gpr2_TWF154_TGJ68930.1.fasta'
    full = ''.join(l.strip() for l in source.read_text().splitlines() if not l.startswith('>'))
    assert len(full)==406
    expected={}
    for group, sites in GROUPS.items():
        seq=list(full)
        for n,old in sites.items():
            assert seq[n-1]==old
            seq[n-1]='A'
        expected[group]=''.join(seq)
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None, 'Archive CRC check failed'
        records=[]
        jobs=[n for n in z.namelist() if n.endswith('_job_request.json')]
        assert len(jobs)==8, 'Expected eight AF3 jobs'
        for group in GROUPS:
            job='gpr2_'+group.lower()
            name=f'{job}/fold_{job}_job_request.json'
            requests=json.loads(z.read(name));assert len(requests)==1
            j=requests[0];assert len(j['sequences'])==1
            protein=j['sequences'][0]['proteinChain']
            assert protein['count']==1 and protein['sequence']==expected[group], f'Wrong full-length input: {group}'
            models=[f'{job}/fold_{job}_model_{i}.cif' for i in range(5)]
            assert all(p in z.namelist() for p in models)
            records.append({'group':group,'residues':406,'mutations':GROUPS[group],'modelSeeds':j.get('modelSeeds'),'job_request':name,'selected_model':models[0]})
        dest=archive/'original_cif'
        # Validate every extraction path and collision before writing any member.
        for info in z.infolist():
            target=dest/info.filename
            assert target.resolve().is_relative_to(dest.resolve()), info.filename
            assert not stat.S_ISLNK(info.external_attr>>16), info.filename
            if target.exists() and not info.is_dir():
                assert target.read_bytes()==z.read(info), f'Existing file differs: {target}'
        saved=archive/'original_archives'/zip_path.name
        if saved.exists():assert saved.read_bytes()==zip_path.read_bytes()
        else:
            saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(zip_path,saved)
        for info in z.infolist():
            target=dest/info.filename
            if info.is_dir():target.mkdir(parents=True,exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(info))
    fasta_dir=archive/'fasta_full_length';fasta_dir.mkdir(exist_ok=True)
    for group,seq in expected.items():
        text=f'>Gpr2_TWF154_full_length_{group}\n'+'\n'.join(seq[i:i+70] for i in range(0,len(seq),70))+'\n'
        target=fasta_dir/f'Gpr2_full_length_{group}.fasta'
        if target.exists():assert target.read_text()==text
        else:target.write_text(text)
    sha=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (archive/'original_archives/SHA256SUMS.txt').write_text(sha+'  '+zip_path.name+'\n')
    (archive/'input_audit.json').write_text(json.dumps({'archive_sha256':sha,'protocol':'406-aa full-length AF3 prediction; delete original 1-21 and 164-178 only after prediction; retain remaining coordinates and original numbering.','jobs':records},indent=2)+'\n')
    print('Archived and extracted eight verified full-length jobs:',archive)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('unpack');a.add_argument('zip_path',type=Path);a.add_argument('archive',type=Path)
    a=sub.add_parser('validate');a.add_argument('source',type=Path);a.add_argument('prepared',type=Path);a.add_argument('group',choices=GROUPS)
    a=sub.add_parser('contacts');a.add_argument('receptor_json',type=Path);a.add_argument('sdf',type=Path);a.add_argument('out',type=Path)
    for action in ['compare','compare_contacts']:
        a=sub.add_parser(action);a.add_argument('out',type=Path)
    args=vars(p.parse_args());action=args.pop('action')
    if action=='unpack':return unpack(**args)
    path=ROOT/'outputs/batches/01-sidechain-combination/cli/helpers.py'
    spec=importlib.util.spec_from_file_location('gpr2_shared_helpers',path)
    shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
    shared.GROUPS=GROUPS
    getattr(shared,action)(**args)


if __name__=='__main__':main()
