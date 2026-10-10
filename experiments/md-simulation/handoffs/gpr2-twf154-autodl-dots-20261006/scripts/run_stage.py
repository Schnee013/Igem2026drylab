#!/usr/bin/env python3
"""One isolated finite GROMACS segment, with monitoring and graceful stop.

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
    ap.add_argument('--case',required=True)
    ap.add_argument('--stage',choices=['em','heat','hold','npt','benchmark','production'],required=True)
    ap.add_argument('--workdir',type=Path,required=True)
    ap.add_argument('--tpr',type=Path,required=True)
    ap.add_argument('--prefix',required=True)
    ap.add_argument('--gmx',default='/opt/drylab/gromacs-2025.4/bin/gmx_mpi')
    ap.add_argument('--threads',type=int,default=8)
    ap.add_argument('--offload',choices=['cpu','compat','gpu'],default='compat')
    ap.add_argument('--maxh',type=float,required=True)
    ap.add_argument('--expected-end-ps',type=float,required=True)
    ap.add_argument('--cpi',type=Path)
    ap.add_argument('--gate',type=Path)
    ap.add_argument('--poll-seconds',type=float,default=30)
    ap.add_argument('--min-free-gb',type=float,default=2)
    a=ap.parse_args()
    pkg=Path(__file__).resolve().parents[2]
    order=json.loads((pkg/'WORK_ORDER.json').read_text())
    assert a.case in order['cases'] and order['production_scope_authorized']
    assert 0<a.maxh<=12 and 1<=a.threads<=16 and a.poll_seconds>=1
    assert re.fullmatch(r'[A-Za-z0-9_.-]+',a.prefix)
    root=a.workdir.resolve(); root.mkdir(parents=True,exist_ok=True)
    lock=(root/'stage.lock').open('a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    tpr=a.tpr.resolve(); assert tpr.is_file()
    if a.stage=='production':
        assert a.expected_end_ps==100000, 'Only the authorized 100 ns rep1 target'
        assert a.gate, 'Current production gate required'
        gate=json.loads(a.gate.read_text())
        assert gate['case_id']==a.case and gate['tpr_sha256']==sha(tpr)
        checks=['source_identity','structure_purpose','preparation','numerical_compatibility','restart_test','resources','storage_and_recovery']
        assert all(gate['checks'].get(k) is True for k in checks)
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(gate['live_verified_at'])).total_seconds()
        assert 0<=age<=900, 'Refresh live verification within 15 minutes'
        assert gate['replicate']==1 and gate['production_ns']==100
    existing=[p for suffix in ['.log','.cpt','.gro','.xtc','.trr','.edr']
              for p in root.glob(a.prefix+'*'+suffix)]
    if not a.cpi: assert not existing, 'Existing outputs require explicit checkpoint continuation'
    cmd=[a.gmx,'mdrun','-s',str(tpr),'-deffnm',a.prefix,'-ntomp',str(a.threads),'-pin','off','-cpt','5','-maxh',str(a.maxh)]
    cmd+= {'cpu':['-nb','cpu','-pme','cpu','-bonded','cpu','-update','cpu'],
           'compat':['-nb','gpu','-pme','gpu','-bonded','cpu','-update','cpu'],
           'gpu':['-nb','gpu','-pme','gpu','-bonded','gpu','-update','gpu']}[a.offload]
    if a.cpi:
        assert a.cpi.is_file()
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
