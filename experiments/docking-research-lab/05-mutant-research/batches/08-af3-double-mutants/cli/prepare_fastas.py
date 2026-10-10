"""User-run batch08 full-length FASTA generation; never overwrite existing output."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
MANIFEST=ROOT/'outputs/batches/08-af3-double-mutants/manifests/double-mutants.json'
AA=set('ACDEFGHIKLMNPQRSTVWY')
def require(ok,msg):
    if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def records(path):
    out={};name=None
    for line in path.read_text().splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('>'):
            name=line[1:];require(bool(name) and name not in out,'Empty/duplicate header');out[name]=''
        else:require(name is not None,'Missing header');out[name]+=line
    require(bool(out),'Empty FASTA');return out

def check(m):
    source=ROOT/m['source_fasta'];require(sha(source.read_bytes())==m['source_fasta_sha256'],'WT file changed')
    rec=records(source);require(len(rec)==1,'Expected one WT sequence');wt=next(iter(rec.values()))
    require(len(wt)==406 and set(wt)<=AA and sha(wt.encode())==m['source_sequence_sha256'],'WT sequence mismatch')
    require([wt[p-1] for p in [84,110,338,368]]==list('NVWV'),'Source sites mismatch')
    plan=ROOT/m['plan'];require(sha(plan.read_bytes())==m['plan_sha256'],'Plan changed; review manifest before proceeding')
    listed=re.findall(r'^\| ([A-F])：[^|]+\| ([A-Z]\d+[A-Z]_[A-Z]\d+[A-Z]) \|',plan.read_text(),re.M)
    rows=m['variants'];require([(r['module'],r['id']) for r in rows]==listed and len(rows)==18,'Design/plan mismatch')
    require({k:sum(r['module']==k for r in rows) for k in 'ABCDEF'}==dict(zip('ABCDEF',[4,2,4,4,2,2])),'Module counts mismatch')
    exp={}
    for r in rows:
        name=r['af_job_name'];require(name=='08_'+r['id'].lower() and name not in exp,'Job name mismatch')
        mm=r['mutations'];positions=[x['position'] for x in mm]
        require(len(mm)==2 and positions==sorted(set(positions)),'Expected exactly two ordered sites')
        require('_'.join(f"{x['from']}{x['position']}{x['to']}" for x in mm)==r['id'],'Mutation ID mismatch')
        s=list(wt)
        for x in mm:
            p=x['position'];require(1<=p<=406 and wt[p-1]==x['from'] and x['to'] in AA and x['to']!=x['from'],'Invalid substitution');s[p-1]=x['to']
        seq=''.join(s);require(len(seq)==406 and sha(seq.encode())==r['sequence_sha256'],'Mutant sequence hash mismatch');exp[name]=seq
    require(len(set(exp.values()))==18,'Duplicate sequences')
    print('SOURCE PASS: 406 aa; N84/V110/W338/V368 verified; 16 core + 2 exploratory double mutants')
    return wt,exp

def fasta(n,s):return f'>{n}\n'+'\n'.join(s[i:i+70] for i in range(0,len(s),70))+'\n'
def table(m):return 'module\trole\tvariant_id\taf_job_name\tfasta_path\n'+''.join(f"{r['module']}\t{r['role']}\t{r['id']}\t{r['af_job_name']}\tindividual/{r['af_job_name']}.fasta\n" for r in m['variants'])
def validate(m,wt,exp,out,allow_baseline=False):
    extra={"individual/08_baseline.fasta","all_19.fasta","submission_jobs_19.tsv","checksums_19.json"} if allow_baseline else set()
    require({p.name for p in (out/'individual').iterdir() if p.name != '.DS_Store' and not (allow_baseline and p.name=='08_baseline.fasta')}=={n+'.fasta' for n in exp},'Individual file inventory differs')
    for r in m['variants']:
        n=r['af_job_name'];actual=records(out/'individual'/f'{n}.fasta');require(actual=={n:exp[n]},f'Header/sequence mismatch: {n}')
        diffs=[(i+1,a,b) for i,(a,b) in enumerate(zip(wt,actual[n])) if a!=b]
        require(len(actual[n])==406 and diffs==[(x['position'],x['from'],x['to']) for x in r['mutations']],f'Exact substitutions failed: {n}')
    require(records(out/'all_18.fasta')==exp,'Combined FASTA differs')
    require((out/'submission_jobs.tsv').read_text()==table(m),'Submission table differs')
    receipt=json.loads((out/'checksums.json').read_text());require(receipt['manifest_sha256']==sha(MANIFEST.read_bytes()),'Manifest changed')
    names={str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p!=out/'checksums.json' and p.name != '.DS_Store'};require(names-extra==set(receipt['files']),'Output inventory changed')
    for name,h in receipt['files'].items():require(sha((out/name).read_bytes())==h,f'Output changed: {name}')
    print('FASTA PASS: 18 unique full-length sequences; exactly 2 substitutions each; 08_ job names; hashes verified')
    print(out)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['check','generate','validate']);a=p.parse_args()
    m=json.loads(MANIFEST.read_text());wt,exp=check(m);out=(ROOT / 'vina/inputs/receptors/fasta' / Path(__file__).resolve().parents[1].name)
    if a.stage=='check':return
    if a.stage=='generate':
        require(not out.exists(),f'Refusing existing output: {out}');(out/'individual').mkdir(parents=True,exist_ok=False)
        for n,s in exp.items():(out/'individual'/f'{n}.fasta').write_text(fasta(n,s))
        (out/'all_18.fasta').write_text(''.join(fasta(n,s) for n,s in exp.items()));(out/'submission_jobs.tsv').write_text(table(m))
        receipt={'manifest_sha256':sha(MANIFEST.read_bytes()),'files':{str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}}
        (out/'checksums.json').write_text(json.dumps(receipt,indent=2)+'\n')
    validate(m,wt,exp,out,allow_baseline=(out/"checksums_19.json").exists())
    if (out/"checksums_19.json").exists():
        from add_baseline import validate19
        validate19(out,wt,exp)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as exc:raise SystemExit(f'STOP: {exc}')
