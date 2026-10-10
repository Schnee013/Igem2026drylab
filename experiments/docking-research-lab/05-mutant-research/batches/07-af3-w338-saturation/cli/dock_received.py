"""User-run bounded Vina scheduling; source hashes checked and completed results protected."""
from model_selection import load_manifest, model_note
import argparse, concurrent.futures as futures, json, os, re, subprocess, sys
from pathlib import Path
from configure_received import ROOT, BATCH, LIGANDS, verify_report, validate_config, require, digest

OUTPUTS=['poses.pdbqt','vina.stdout.txt','vina.stderr.txt','run.json','summary.json','runner.log','docking_validation.json','.dock.lock']

def preflight(j,ligand):
    d=BATCH/'run-01'/j['alias']; folder=d/ligand
    verify_report(d/'alignment_provenance.json')
    verify_report(d/'preparation_validation.json')
    verify_report(folder/'config_provenance.json')
    validate_config(folder/'vina.conf',d/'receptor.pdbqt',LIGANDS/f'{ligand}_deprotonated.pdbqt')
    for name in OUTPUTS: require(not (folder/name).exists(),f'Refusing existing output: {folder/name}')
    return folder

def run_one(task,args):
    j,ligand=task; folder=preflight(j,ligand)
    with (folder/'.dock.lock').open('x') as f: f.write(f'pid={os.getpid()}\n')
    print(f'START: {j["alias"]} {ligand}',flush=True)
    cmd=[sys.executable,str(ROOT/'vina/src/run_vina.py'),'--vina-executable',str(args.vina),
         '--config',str(folder/'vina.conf'),'--output-pdbqt',str(folder/'poses.pdbqt'),
         '--stdout-log',str(folder/'vina.stdout.txt'),'--stderr-log',str(folder/'vina.stderr.txt'),
         '--report-json',str(folder/'run.json'),'--cpu',str(args.cpu),
         '--spacing','0.375','--min-rmsd','1','--max-evals','0']
    with (folder/'runner.log').open('x') as log:
        subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
        report=json.loads((folder/'run.json').read_text())
        require(report['return_code']==0 and report['output'],f'Missing successful result: {folder}')
        for record in [report['config'],report['output'],*report['inputs'].values()]:
            require(digest(Path(record['path']))==record['sha256'],f'Run hash mismatch: {folder}')
        require(report['runtime_overrides']=={'cpu':args.cpu,'spacing':0.375,'min_rmsd':1.0,'max_evals':0},'Runtime mismatch')
        subprocess.run([sys.executable,str(ROOT/'vina/src/summarize_vina_results.py'),
                        '--log',str(folder/'vina.stdout.txt'),'--pose',str(folder/'poses.pdbqt'),
                        '--output',str(folder/'summary.json')],stdout=log,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
    poses=[]; model=None
    for line in (folder/'poses.pdbqt').read_text().splitlines():
        if line.startswith('MODEL'): model=int(line.split()[1])
        if line.startswith('REMARK VINA RESULT:'):
            require(model is not None,'Score without MODEL')
            score=float(line.split()[3]); poses.append((score,model))
    require(1<=len(poses)<=9 and len({p[1] for p in poses})==len(poses),'Invalid pose inventory')
    best,model=min(poses)
    out={'alias':j['alias'],'ligand':ligand,'pose_count':len(poses),'lowest_score':best,'selected_model':model,
         'selection_rule':'minimum score, then minimum MODEL number','files':{str(folder/n):digest(folder/n) for n in OUTPUTS if n not in ['.dock.lock','docking_validation.json']}}
    (folder/'docking_validation.json').write_text(json.dumps(out,indent=2)+'\n')
    (folder/'.dock.lock').unlink()
    print(f'DOCK PASS: {j["alias"]} {ligand}; poses={len(poses)}; best={best:.3f}; MODEL={model}',flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group',choices=['baseline','all-mutants'])
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--cpu',type=int,default=4)
    parser.add_argument('--vina',type=Path,default=Path('/Users/yangruoxi/miniconda3/envs/docking/bin/vina'))
    parser.add_argument('--check-only',action='store_true')
    a=parser.parse_args()
    require(a.workers>0 and a.cpu>0,'CPU/workers must be positive')
    require(a.workers*a.cpu<=(os.cpu_count() or 1),'Requested threads exceed detected logical CPUs')
    require(a.vina.is_file(),'Missing Vina executable')
    version=subprocess.run([str(a.vina),'--version'],capture_output=True,text=True,check=True)
    require('v1.2.5' in version.stdout+version.stderr,'Vina version differs from frozen v1.2.5')
    m=load_manifest(BATCH)
    require(len(m['jobs'])==20 and {j['alias'] for j in m['jobs']}==({'07_baseline'} | {'07_w338'+a for a in 'acdefghiklmnpqrstv y'.replace(' ','')}),'Batch07 manifest mismatch')
    jobs=[j for j in m['jobs'] if (j['id']=='baseline')==(a.group=='baseline')]
    tasks=[(j,ligand) for j in jobs for ligand in ['ascr3','ascr18']]
    for task in tasks: preflight(*task)
    print(f'PREFLIGHT PASS: {len(tasks)} docking tasks; workers={a.workers}; cpu/task={a.cpu}; max threads={a.workers*a.cpu}; Vina v1.2.5',flush=True)
    if a.check_only: return
    queue=iter(tasks); failures=[]
    with futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        active={pool.submit(run_one,t,a):t for t in [next(queue,None) for _ in range(min(a.workers,len(tasks)))] if t is not None}
        while active:
            done,_=futures.wait(active,return_when=futures.FIRST_COMPLETED)
            for future in done:
                task=active.pop(future)
                try: future.result()
                except Exception as exc:
                    failures.append(str(exc)); print(f'STOP: {task[0]["alias"]} {task[1]}: {exc}',flush=True)
            if not failures:
                while len(active)<a.workers:
                    task=next(queue,None)
                    if task is None: break
                    active[pool.submit(run_one,task,a)]=task
    require(not failures,'A task failed; no further tasks scheduled. Keep logs and outputs for inspection.')
    print(f'BATCH PASS: {len(tasks)} docking tasks completed',flush=True)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc: raise SystemExit(f'STOP: {exc}')
