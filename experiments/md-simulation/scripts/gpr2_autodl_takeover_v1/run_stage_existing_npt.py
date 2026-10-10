#!/usr/bin/env python3
"""v3-qualified preparation-only supervisor; derived from original run_stage.py.

This is not a scientific acceptance validator. Dots must produce a current,
evidence-backed gate before production. A zero exit code is only segment closure.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def write(p, x): p.write_text(json.dumps(x, indent=2)+'\n')
def event(root, state, detail, source):
    p=root/'run_state_events.tsv'
    if not p.exists(): p.write_text('observed_at\tstate\tsource\tdetail\n')
    with p.open('a') as f: f.write(f'{now()}\t{state}\t{source}\t{detail}\n')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case',choices=['native_wt_ascr18','raw_n84v_ascr3','raw_v368r_ascr18'],required=True)
    ap.add_argument('--stage',choices=['npt'],required=True)
    ap.add_argument('--workdir',type=Path,required=True)
    ap.add_argument('--tpr',type=Path,required=True)
    ap.add_argument('--prefix',required=True)
    ap.add_argument('--gmx',default='/opt/drylab/gromacs-2025.4/bin.AVX2_256/gmx_mpi')
    ap.add_argument('--threads',type=int,choices=[8],default=8)
    ap.add_argument('--offload',choices=['gpu'],default='gpu')
    ap.add_argument('--maxh',type=float,required=True)
    ap.add_argument('--expected-end-ps',type=float,required=True)
    ap.add_argument('--cpi',type=Path)
    ap.add_argument('--gate',type=Path,required=True)
    ap.add_argument('--poll-seconds',type=float,default=30)
    ap.add_argument('--min-free-gb',type=float,default=2)
    a=ap.parse_args()
    if a.cpi is not None:ap.error("Checkpoint continuation is outside this controlled first-stage entry; preserve outputs for separately reviewed recovery")
    pkg=Path(__file__).resolve().parents[2]
    order=json.loads((pkg/'WORK_ORDER.json').read_text())
    from prepare_existing_npt import gate_check, verify_sources, checked_workdir, validate_launch_tpr, previous_stage, command, validate_manifest, fixed_expected_hashes, require, stage_output_names, validate_npt01_import
    require(a.case in ('raw_n84v_ascr3','raw_v368r_ascr18') and a.prefix in ('npt01','npt02','npt03','npt04','npt05'),'Only two own original prepared branches and original five NPT stages')
    require(json.loads(a.gate.read_text()).get('allowed_stages')==[a.prefix],'Supervisor requires an explicit single-stage gate')
    plan=verify_sources(pkg,a.case)
    gate_check(a.gate.resolve(),plan,Path(a.gmx).resolve())
    require(a.prefix in json.loads(a.gate.read_text())['allowed_stages'], 'Stage outside reviewed gate scope')
    require(125 < a.expected_end_ps <= 6750, 'Only bounded preparation stages')
    require(a.case in order['cases'] and order['production_scope_authorized'], "Supervisor safety condition failed: a.case in order['cases'] and order['production_scope_authorized']")
    require(0 < a.maxh <= 12 and 1 <= a.threads <= 16 and (a.poll_seconds >= 1), 'Supervisor safety condition failed: 0 < a.maxh <= 12 and 1 <= a.threads <= 16 and (a.poll_seconds >= 1)')
    require(re.fullmatch('[A-Za-z0-9_.-]+', a.prefix), "Supervisor safety condition failed: re.fullmatch('[A-Za-z0-9_.-]+', a.prefix)")
    root=checked_workdir(pkg,a.workdir)
    inputs=json.loads((root/'preparation_inputs.json').read_text())
    expected_inputs=fixed_expected_hashes(pkg,plan)
    validate_manifest(root,inputs.get('fixed_files_sha256'),set(expected_inputs))
    require(inputs.get('case_id') == a.case and inputs['fixed_files_sha256'] == expected_inputs, 'Case source binding mismatch')
    lock=(root/'stage.lock').open('a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if a.prefix=='npt01':
        initial=json.loads((root/'initial_complete.json').read_text())
        require(initial['case_id']==a.case and initial['replicate']==1,'Wrong own preheat acceptance')
        validate_manifest(root,initial['evidence_sha256'],set(initial['evidence_sha256']))
    else:
        prior=previous_stage(a.prefix);validated=json.loads((root/(prior+'.validated.json')).read_text())
        require(validated.get('case_id')==a.case and validated.get('replicate')==1 and validated.get('stage')==prior and validated.get('pass_stage') is True,'Own predecessor has not passed')
        validate_manifest(root,validated['output_sha256'],stage_output_names(prior))
    tpr=a.tpr.resolve(); require(tpr.is_file(), 'Missing stage TPR')
    existing=[p for suffix in ['.log','.cpt','.gro','.xtc','.trr','.edr']
              for p in root.glob(a.prefix+'*'+suffix)]
    if not a.cpi: require(not existing, 'Existing outputs require explicit checkpoint continuation')
    require(tpr == root / (a.prefix + '.tpr'), 'TPR must be the selected local preparation stage')
    dump=command([a.gmx,'dump','-s',tpr],root/('audit.'+a.prefix+'.supervisor_tpr.dump.txt'),root)
    validate_launch_tpr(dump,a.prefix,a.expected_end_ps,plan['atom_count'],root/(previous_stage(a.prefix)+'.gro'))
    cmd=[a.gmx,'mdrun','-s',str(tpr),'-deffnm',a.prefix,'-ntomp',str(a.threads),'-pin','off','-cpt','5','-maxh',str(a.maxh),'-notunepme']
    cmd+=['-nb','gpu','-pme','gpu','-bonded','gpu','-update','gpu']
    if a.cpi:
        require(a.cpi.is_file(), 'Supervisor safety condition failed: a.cpi.is_file()')
        cmd+=['-cpi',str(a.cpi.resolve()),'-noappend']
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_id=f'{a.prefix}_{stamp}'
    console=root/(run_id+'.console.txt')
    manifest=dict(case_id=a.case,stage=a.stage,command=cmd,tpr_sha256=sha(tpr),started_at=now(),
                  expected_end_ps=a.expected_end_ps,checkpoint_sha256=sha(a.cpi) if a.cpi else None)
    write(root/(run_id+'.command.json'),manifest)
    env=dict(os.environ,OMP_NUM_THREADS=str(a.threads),OPENBLAS_NUM_THREADS='1')
    issue=None;last_step=None;last_progress=time.monotonic();started=time.monotonic()
    with console.open('x') as f:
        p=subprocess.Popen(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT)
        manifest['pid']=p.pid;write(root/(run_id+'.command.json'),manifest)
        def stop(signum=None,frame=None):
            nonlocal issue
            issue=issue or 'Operator or supervisor requested a stop'
            if p.poll() is None:p.send_signal(signal.SIGTERM)
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        deadline=None
        while True:
            logs=sorted(root.glob(a.prefix+'*.log'),key=lambda x:x.stat().st_mtime)
            log=logs[-1] if logs else None
            text=log.read_text(errors='replace') if log else ''
            content=console.read_text(errors='replace')+'\n'+text
            bad=[x for x in content.splitlines() if re.search(r'LINCS WARNING|cannot be settled|Fatal error|\bnan\b|\binf\b',x,re.I)
                 and not re.fullmatch(r'\s*epsilon-rf\s*=\s*inf\s*',x)]
            steps=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+([-+\d.eE]+)',text)
            latest=steps[-1] if steps else None
            if latest!=last_step and latest:
                last_step=latest;last_progress=time.monotonic()
            free=shutil.disk_usage(root).free/1e9
            if bad:issue='Numerical/runtime issue: '+bad[0][:250]
            if free<a.min_free_gb:issue=f'Disk reserve below {a.min_free_gb} GB'
            if time.monotonic()-last_progress>900:issue='No observed step progress for 15 minutes; investigate before restart'
            if time.monotonic()-started>a.maxh*3600+600:issue='Exceeded segment walltime plus 10 minute cleanup allowance'
            snap=dict(observed_at=now(),pid=p.pid,process_alive=p.poll() is None,
                      log=str(log) if log else None,step=int(latest[0]) if latest else None,
                      time_ps=float(latest[1]) if latest else None,disk_free_gb=free,issue=issue)
            try:
                r=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,power.draw,clocks.sm,memory.used','--format=csv,noheader'],text=True,capture_output=True,timeout=10)
                snap['gpu']=r.stdout.strip()
            except (OSError,subprocess.TimeoutExpired):snap['gpu']=None
            with (root/(run_id+'.monitor.jsonl')).open('a') as m:m.write(json.dumps(snap)+'\n')
            write(root/'live_status.json',snap)
            if p.poll() is not None:break
            state='RUNNING_VERIFIED' if log and latest and not issue else 'UNRESOLVED'
            event(root,state,f'pid={p.pid}; step={snap["step"]}; time_ps={snap["time_ps"]}; issue={issue}',str(log.name) if log else console.name)
            if issue and deadline is None:
                p.send_signal(signal.SIGTERM);deadline=time.monotonic()+120
            elif deadline is not None and time.monotonic()>deadline:
                p.kill();issue+='; did not stop gracefully within 120 seconds; inspect checkpoint integrity'
            time.sleep(a.poll_seconds)
    code=p.wait()
    closed=code==0 and 'Finished mdrun' in text and not issue
    reached=bool(closed and latest and abs(float(latest[1])-a.expected_end_ps)<.01)
    result=dict(**manifest,finished_at=now(),exit_code=code,segment_closed_normally=closed,
                observed_target_time_reached=reached,full_production_verified=False,issue=issue,
                next_action='Validate CPT/XTC/EDR endpoints and hashes before declaring completion' if reached else 'Inspect and continue from latest valid checkpoint if authorized')
    write(root/(run_id+'.result.json'),result)
    event(root,'TERMINAL_NORMAL' if closed else 'TERMINAL_ABNORMAL',
          f'Segment closed; target_time_reached={reached}; full trajectory completion NOT validated; issue={issue}',run_id+'.result.json')
    if not closed:raise SystemExit(1)

if __name__=='__main__':main()
