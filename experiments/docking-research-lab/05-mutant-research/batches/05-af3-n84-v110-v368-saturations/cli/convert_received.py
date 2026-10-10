"""User-run model_0 conversion and post-AF segment removal, driven by received manifest."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BATCH=ROOT/'outputs/batches/05-af3-saturation-combinations'

def require(ok,msg):
    if not ok: raise ValueError(msg)
def verify(path,digest):
    require(hashlib.sha256(path.read_bytes()).hexdigest()==digest, f'Input hash changed: {path}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('group',help='baseline, a variant such as N84C, its alias 05_n84c, or all-mutants')
    p.add_argument('--check-only',action='store_true')
    a=p.parse_args()
    manifest=json.loads((BATCH/'manifests/received-af3.json').read_text())
    require(manifest['status']=='validated','Archive is not validated')
    jobs=[j for j in manifest['jobs'] if (a.group=='all-mutants' and j['id']!='baseline') or a.group in (j['id'],j['alias'])]
    require(bool(jobs),f'Unknown selection: {a.group}')
    for j in jobs:
        require(j['selected_model']==0,'Expected model_0')
        model=j['models'][0]
        verify(ROOT/model['path'],model['sha256'])
        verify(ROOT/j['job_request'],j['job_request_sha256'])
        verify(ROOT/j['expected_fasta'],j['fasta_sha256'])
        require(not (BATCH/'run-01'/j['alias']).exists(),f'Output exists: {j["alias"]}; stop to avoid overwriting')
    print(f'PREFLIGHT PASS: {len(jobs)} jobs',flush=True)
    if a.check_only: return
    for j in jobs:
        out=BATCH/'run-01'/j['alias']; out.mkdir(parents=True,exist_ok=False)
        def run(args): subprocess.run([sys.executable,*map(str,args)],check=True)
        run([ROOT/'vina/src/cif_to_pdb.py','--input-file',ROOT/j['models'][0]['path'],'--output-file',out/'raw_model0.pdb'])
        run([ROOT/'outputs/batches/02-af3-combination/cli/trim_after_full_length_af3.py',
             '--input-pdb',out/'raw_model0.pdb','--expected-fasta',ROOT/j['expected_fasta'],
             '--job-request',ROOT/j['job_request'],'--output-pdb',out/'trimmed.pdb','--report-json',out/'trimming.json'])
        print(f'CONVERT/TRIM PASS: {j["alias"]}; 406 -> 370 residues; original numbering retained',flush=True)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc: raise SystemExit(f'STOP: {exc}')
