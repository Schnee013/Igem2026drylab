"""User-run WT addition preserving all original 18-mutant FASTA files and receipt."""
import argparse,json
from pathlib import Path
from prepare_fastas import ROOT,MANIFEST,check,validate,records,sha,fasta,require
BATCH=Path(__file__).resolve().parents[1]
FULL=BATCH/'manifests/af-inputs.json'
OUT=ROOT/'vina/inputs/receptors/fasta'/BATCH.name
NAMES=['individual/08_baseline.fasta','all_19.fasta','submission_jobs_19.tsv','checksums_19.json']
def expected(wt,exp):
    m=json.loads(FULL.read_text())
    require(m['previous_manifest_sha256']==sha(MANIFEST.read_bytes()),'Original manifest changed')
    require(len(m['variants'])==19 and len({r['af_job_name'] for r in m['variants']})==19,'Manifest inventory differs')
    original=json.loads(MANIFEST.read_text())
    for a,b in zip(m['variants'][:18],original['variants']):
        require(all(a[k]==b[k] for k in b if k!='parents'),'Double-mutant definition changed')
    baseline=m['variants'][-1]
    require(baseline['id']=='baseline' and baseline['af_job_name']=='08_baseline' and baseline['mutations']==[] and baseline['sequence_sha256']==sha(wt.encode()),'Baseline differs')
    allseq={**exp,'08_baseline':wt};require(len(set(allseq.values()))==19,'Duplicate WT/mutant sequence')
    table='module\trole\tvariant_id\taf_job_name\tfasta_path\n'+''.join(f"{r['module']}\t{r['role']}\t{r['id']}\t{r['af_job_name']}\tindividual/{r['af_job_name']}.fasta\n" for r in m['variants'])
    return {'individual/08_baseline.fasta':fasta('08_baseline',wt),'all_19.fasta':''.join(fasta(n,s) for n,s in allseq.items()),'submission_jobs_19.tsv':table}
def validate19(out,wt,exp):
    for name,content in expected(wt,exp).items():require((out/name).read_text()==content,f'Unexpected content: {name}')
    receipt=json.loads((out/'checksums_19.json').read_text());require(receipt['manifest_sha256']==sha(FULL.read_bytes()),'19-job manifest changed')
    require(receipt['original_receipt_sha256']==sha((out/'checksums.json').read_bytes()),'Original receipt changed')
    found={str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p.name!='.DS_Store' and p!=out/'checksums_19.json'}
    require(found==set(receipt['files']),'19-job inventory mismatch')
    for name,h in receipt['files'].items():require(sha((out/name).read_bytes())==h,f'Changed file: {name}')
    print('BASELINE PASS: 08_baseline; 406 aa; exact WT sequence')
    print('FASTA PASS: 19 unique sequences; 18 double mutants + 1 WT; original 18 FASTAs unchanged')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['check','generate','validate']);a=p.parse_args()
    m=json.loads(MANIFEST.read_text());wt,exp=check(m)
    validate(m,wt,exp,OUT,allow_baseline=a.stage=='validate')
    content=expected(wt,exp)
    if a.stage=='validate':validate19(OUT,wt,exp);return
    for name in NAMES:require(not (OUT/name).exists(),f'Refusing overwrite: {OUT/name}; use validate if complete')
    print('ADD BASELINE PREFLIGHT PASS: one new WT; no new single-mutant jobs')
    if a.stage=='check':return
    for name,body in content.items():
        with (OUT/name).open('x') as f:f.write(body)
    receipt={'manifest_sha256':sha(FULL.read_bytes()),'original_receipt_sha256':sha((OUT/'checksums.json').read_bytes()),'files':{str(p.relative_to(OUT)):sha(p.read_bytes()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='.DS_Store'}}
    with (OUT/'checksums_19.json').open('x') as f:f.write(json.dumps(receipt,indent=2)+'\n')
    validate(m,wt,exp,OUT,allow_baseline=True);validate19(OUT,wt,exp)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as exc:raise SystemExit(f'STOP: {exc}')
