"""User-run generation and verification of batch07 full-length AF input FASTAs."""
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
MANIFEST=ROOT/'outputs/batches/07-af3-w338-saturation/manifests/w338-saturation.json'
AA=set('ACDEFGHIKLMNPQRSTVWY')

def require(ok,msg):
    if not ok: raise ValueError(msg)
def digest(data): return hashlib.sha256(data).hexdigest()
def records(path):
    result={}; name=None
    for line in path.read_text().splitlines():
        line=line.strip()
        if not line: continue
        if line.startswith('>'):
            name=line[1:].split()[0]; require(name not in result,'Duplicate FASTA header'); result[name]=''
        else:
            require(name is not None,'Missing FASTA header'); result[name]+=line
    require(bool(result),'Empty FASTA'); return result

def check(m):
    source=records(ROOT/m['source_fasta']); require(len(source)==1,'Expected one WT')
    wt=next(iter(source.values()))
    require(len(wt)==406 and set(wt)<=AA and digest(wt.encode())==m['source_sequence_sha256'],'WT sequence mismatch')
    rows=m['variants']; require(len(rows)==20 and {r['id'] for r in rows}==({'baseline'} | {'W338'+aa for aa in AA-{'W'}}),'Design coverage mismatch')
    for r in rows:
        require(r['af_job_name']=='07_'+r['id'].lower(),'Job name mismatch')
        if r['id']=='baseline': require(r['position'] is None and r['from'] is None and r['to'] is None,'Baseline must be WT')
        else:
            require(r['id']==f'{r["from"]}{r["position"]}{r["to"]}','Mutation ID mismatch')
            require(wt[r['position']-1]==r['from'] and r['to'] in AA and r['to']!=r['from'],'Invalid mutation')
    print('SOURCE PASS: 406 aa; W338; 19 mutants + baseline')
    return wt

def expected(m,wt):
    result={}
    for r in m['variants']:
        s=list(wt)
        if r['position'] is not None: s[r['position']-1]=r['to']
        result[r['af_job_name']]=''.join(s)
    return result

def fasta(name,s): return f'>{name}\n'+'\n'.join(s[i:i+70] for i in range(0,len(s),70))+'\n'
def table(m): return 'variant_id\taf_job_name\tfasta_path\n'+''.join(f'{r["id"]}\t{r["af_job_name"]}\tindividual/{r["af_job_name"]}.fasta\n' for r in m['variants'])

def validate(m,wt,out):
    exp=expected(m,wt)
    require({p.name for p in (out/'individual').iterdir()}=={f'{n}.fasta' for n in exp},'FASTA inventory mismatch')
    for r in m['variants']:
        n=r['af_job_name']; found=records(out/'individual'/f'{n}.fasta')
        require(found=={n:exp[n]},f'Sequence/header mismatch: {n}')
        seq=found[n]; diffs=[(i+1,a,b) for i,(a,b) in enumerate(zip(wt,seq)) if a!=b]
        require(len(seq)==406 and diffs==([] if r['position'] is None else [(r['position'],r['from'],r['to'])]),f'Mutation mismatch: {n}')
    require(len(set(exp.values()))==20,'Duplicate sequence')
    require(records(out/'all_20.fasta')==exp,'Combined FASTA mismatch')
    require((out/'submission_jobs.tsv').read_text()==table(m),'Submission table mismatch')
    receipt=json.loads((out/'checksums.json').read_text())
    require(receipt['manifest_sha256']==digest(MANIFEST.read_bytes()),'Manifest changed')
    files={str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p.name!='checksums.json'}
    require(files==set(receipt['files']),'Output inventory changed')
    for rel,h in receipt['files'].items(): require(digest((out/rel).read_bytes())==h,f'Hash mismatch: {rel}')
    print('FASTA PASS: 20 unique full-length sequences; exact substitutions; 07_ job names; hashes verified')
    print(out)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('stage',choices=['check','generate','validate']); a=p.parse_args()
    m=json.loads(MANIFEST.read_text()); wt=check(m); out=(ROOT / 'vina/inputs/receptors/fasta' / Path(__file__).resolve().parents[1].name)
    if a.stage=='check': return
    if a.stage=='generate':
        require(not out.exists(),f'Refusing existing output directory: {out}')
        exp=expected(m,wt); (out/'individual').mkdir(parents=True,exist_ok=False)
        for n,s in exp.items(): (out/'individual'/f'{n}.fasta').write_text(fasta(n,s))
        (out/'all_20.fasta').write_text(''.join(fasta(n,s) for n,s in exp.items()))
        (out/'submission_jobs.tsv').write_text(table(m))
        receipt={'manifest_sha256':digest(MANIFEST.read_bytes()),'files':{str(p.relative_to(out)):digest(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}}
        (out/'checksums.json').write_text(json.dumps(receipt,indent=2)+'\n')
    validate(m,wt,out)
if __name__=='__main__':
    try: main()
    except (ValueError,OSError,KeyError) as exc: raise SystemExit(f'STOP: {exc}')
