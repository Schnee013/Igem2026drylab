"""Validate and archive the user-supplied batch06 AF3 ZIP without altering source files."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, shutil, zipfile
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

ROOT = Path(__file__).resolve().parents[4]
BATCH = ROOT / 'outputs/batches/06-af3-supplement-singles'
DEST = ROOT / 'vina/inputs/receptors/af3/gpr2_batch06_20260917'
ZIPS = [Path('/Users/yangruoxi/Downloads/folds_2026_09_17_10_20.zip')]
AA = dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(), 'ARNDCQEGHILKMFPSTWYV'))

def require(ok, msg):
    if not ok: raise ValueError(msg)
def sha(data): return hashlib.sha256(data).hexdigest()
def rel(p): return str(p.relative_to(ROOT))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    require(not DEST.exists(), f'Refusing to overwrite {DEST}')
    report_path = BATCH / 'manifests/received-af3.json'
    require(not report_path.exists(), f'Refusing to overwrite {report_path}')
    design = json.loads((BATCH / 'manifests/supplement-singles.json').read_text())
    wt = ''.join(x.strip() for x in (ROOT / design['source_fasta']).read_text().splitlines() if not x.startswith('>'))
    require(sha(wt.encode()) == design['source_sequence_sha256'], 'WT hash mismatch')
    rows = {r['id']: r for r in design['variants']}
    jobs, sources = {}, []
    for zip_path in ZIPS:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            require(len(names) == len(set(names)), 'Duplicate ZIP paths')
            for info in z.infolist():
                p = PurePosixPath(info.filename)
                require(not p.is_absolute() and '..' not in p.parts and '\\' not in info.filename, 'Unsafe ZIP path')
                require((info.external_attr >> 16) & 0o170000 != 0o120000, 'ZIP symlink')
            require(z.testzip() is None, 'ZIP CRC failure')
            sources.append({'path':str(zip_path), 'sha256':sha(zip_path.read_bytes()), 'members':len(names)})
            for req in [n for n in names if n.endswith('_job_request.json')]:
                data = json.loads(z.read(req))
                require(isinstance(data,list) and len(data)==1, f'Invalid request: {req}')
                job = data[0]; name = job['name']
                prefix = '06_'
                require(name.startswith(prefix), f'Unexpected name {name}')
                token = name[len(prefix):]
                variant = 'baseline' if token=='baseline' else token.upper()
                require(variant in rows and variant not in jobs, f'Unknown/duplicate {variant}')
                r = rows[variant]; require(name == r['af_job_name'], 'Manifest job name mismatch'); expected = list(wt)
                if r['position'] is not None: expected[r['position']-1] = r['to']
                expected = ''.join(expected)
                require(len(job['sequences'])==1, 'Expected one protein')
                protein = job['sequences'][0]['proteinChain']
                require(protein['count']==1 and protein['sequence']==expected, f'Job sequence mismatch {variant}')
                fasta = (ROOT / 'vina/inputs/receptors/fasta' / Path(__file__).resolve().parents[1].name) / 'individual' / f'{name}.fasta'
                seq = ''.join(x.strip() for x in fasta.read_text().splitlines() if not x.startswith('>'))
                require(seq==expected, f'Existing FASTA mismatch {variant}')
                folder = str(PurePosixPath(req).parent)
                models=[]
                for i in range(5):
                    member=f'{folder}/fold_{name}_model_{i}.cif'
                    raw=z.read(member); cif=MMCIF2Dict(io.StringIO(raw.decode()))
                    residues={}
                    for group,chain,num,res,atom in zip(cif['_atom_site.group_PDB'],cif['_atom_site.auth_asym_id'],cif['_atom_site.auth_seq_id'],cif['_atom_site.label_comp_id'],cif['_atom_site.label_atom_id']):
                        require(group=='ATOM' and chain=='A', f'Unexpected atom/chain: {member}')
                        if atom=='CA':
                            n=int(num); require(n not in residues, f'Duplicate CA: {member}')
                            residues[n]=AA[res]
                    require(set(residues)==set(range(1,407)), f'Residue numbering mismatch: {member}')
                    require(''.join(residues[n] for n in range(1,407))==expected, f'CIF sequence mismatch: {member}')
                    for suffix in [f'full_data_{i}.json',f'summary_confidences_{i}.json']:
                        json.loads(z.read(f'{folder}/fold_{name}_{suffix}'))
                    models.append({'path':rel(DEST/'original_cif'/zip_path.stem/member),'sha256':sha(raw)})
                request_path=DEST/'original_cif'/zip_path.stem/req
                jobs[variant]={'id':variant,'alias':name,'original_job_name':name,'source_zip':zip_path.name,'source':'new_batch06_prediction','baseline':'baseline','selected_model':0,'models':models,'job_request':rel(request_path),'job_request_sha256':sha(z.read(req)),'expected_fasta':rel(DEST/'fasta_full_length'/f'{name}.fasta'),'fasta_sha256':sha(fasta.read_bytes()),'sequence_sha256':sha(expected.encode()),'historical_source':None}
    require(set(jobs)==set(rows), f'Missing tasks: {set(rows)-set(jobs)}')
    print('ZIP AUDIT PASS: 7 jobs, 35 full-length models; sequences, numbering and CRC verified.')
    if args.check_only: return
    DEST.mkdir(parents=True)
    (DEST/'source_zips').mkdir(); (DEST/'fasta_full_length').mkdir()
    for zip_path in ZIPS:
        shutil.copy2(zip_path, DEST/'source_zips'/zip_path.name)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(DEST/'original_cif'/zip_path.stem)
    for v,j in jobs.items():
        shutil.copy2((ROOT / 'vina/inputs/receptors/fasta' / Path(__file__).resolve().parents[1].name)/'individual'/f'{j["original_job_name"]}.fasta',ROOT/j['expected_fasta'])
        require(sha((ROOT/j['expected_fasta']).read_bytes())==j['fasta_sha256'], 'Copy mismatch')
        require(sha((ROOT/j['job_request']).read_bytes())==j['job_request_sha256'], 'Request copy mismatch')
        for model in j['models']:
            require(sha((ROOT/model['path']).read_bytes())==model['sha256'], 'CIF copy mismatch')
    report={'status':'validated','counts':{'jobs':7,'mutants':6,'baseline':1,'models_checked':35},'archive':rel(DEST),'source_zips':sources,'jobs':[jobs[v] for v in rows]}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('ARCHIVE PASS: 7 jobs, 35 full-length models; all sequences and numbering verified.')
    print(DEST)

if __name__=='__main__': main()
