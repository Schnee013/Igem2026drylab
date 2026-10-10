"""User-run selected AF model conversion and post-AF segment removal, driven by received manifest."""
from model_selection import load_manifest, model_note
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BATCH=ROOT/'outputs/batches/07-af3-w338-saturation'

def require(ok,msg):
    if not ok: raise ValueError(msg)
def verify(path,digest):
    require(hashlib.sha256(path.read_bytes()).hexdigest()==digest, f'Input hash changed: {path}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('group',help='baseline, a variant such as W338A, its alias 07_w338a, or all-mutants')
    p.add_argument('--check-only',action='store_true')
    a=p.parse_args()
    manifest=load_manifest(BATCH)
    require(manifest['status']=='validated','Archive is not validated')
    jobs=[j for j in manifest['jobs'] if (a.group=='all-mutants' and j['id']!='baseline') or a.group in (j['id'],j['alias'])]
    require(bool(jobs),f'Unknown selection: {a.group}')
    for j in jobs:
        require(j['selected_model'] in (0,1),'Unexpected AF model')
        model=j['models'][j['selected_model']]
        verify(ROOT/model['path'],model['sha256'])
        verify(ROOT/j['job_request'],j['job_request_sha256'])
        verify(ROOT/j['expected_fasta'],j['fasta_sha256'])
        require(not (BATCH/'run-01'/j['alias']).exists(),f'Output exists: {j["alias"]}; stop to avoid overwriting')
    print(f'PREFLIGHT PASS: {len(jobs)} jobs',flush=True)
    if a.check_only: return
    for j in jobs:
        out=BATCH/'run-01'/j['alias']; out.mkdir(parents=True,exist_ok=False)
        model=j['models'][j['selected_model']]
        raw=out/f"raw_model{j['selected_model']}.pdb"
        (out/'af_model_selection.json').write_text(json.dumps({'af_model':j['selected_model'],'source':model,'reason':j.get('model_selection_reason','default model_0')},indent=2)+'\n')
        def run(args): subprocess.run([sys.executable,*map(str,args)],check=True)
        run([ROOT/'vina/src/cif_to_pdb.py','--input-file',ROOT/model['path'],'--output-file',raw])
        run([ROOT/'outputs/batches/02-af3-combination/cli/trim_after_full_length_af3.py',
             '--input-pdb',raw,'--expected-fasta',ROOT/j['expected_fasta'],
             '--job-request',ROOT/j['job_request'],'--output-pdb',out/'trimmed.pdb','--report-json',out/'trimming.json'])
        print(f'CONVERT/TRIM PASS: {j["alias"]}; 406 -> 370 residues; original numbering retained',flush=True)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc: raise SystemExit(f'STOP: {exc}')
