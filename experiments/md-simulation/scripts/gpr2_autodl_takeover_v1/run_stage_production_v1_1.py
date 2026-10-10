#!/usr/bin/env python3
"""Original nativeWT production-only adaptation; reviewed gate still required.

This is not a scientific acceptance validator. Dots must produce a current,
evidence-backed gate before production. A zero exit code is only segment closure.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
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

def fresh_segment_logs(root, prefix, previous):
    return sorted((p for p in root.glob(prefix+'*.log') if p.resolve() not in previous),key=lambda x:x.stat().st_mtime)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    if not __debug__:ap.error('Optimized Python disables original assertions; do not use -O')
    ap.add_argument('--case',choices=['native_wt_ascr18'],required=True)
    ap.add_argument('--stage',choices=['production'],required=True)
    ap.add_argument('--workdir',type=Path,required=True)
    ap.add_argument('--tpr',type=Path,required=True)
    ap.add_argument('--prefix',required=True)
    ap.add_argument('--gmx',default='/opt/drylab/gromacs-2025.4/bin.AVX2_256/gmx_mpi')
    ap.add_argument('--threads',type=int,choices=[8],default=8)
    ap.add_argument('--offload',choices=['gpu'],default='gpu')
    ap.add_argument('--maxh',type=float,required=True)
    ap.add_argument('--expected-end-ps',type=float,required=True)
    ap.add_argument('--cpi',type=Path)
    ap.add_argument('--gate',type=Path)
    ap.add_argument('--poll-seconds',type=float,default=30)
    ap.add_argument('--min-free-gb',type=float,default=5)
    a=ap.parse_args()
    pkg=Path(__file__).resolve().parents[2]
    order=json.loads((pkg/'WORK_ORDER.json').read_text())
    assert a.case in order['cases'] and order['production_scope_authorized']
    assert 0<a.maxh<=12 and 1<=a.threads<=16 and a.poll_seconds>=1
    assert re.fullmatch(r'[A-Za-z0-9_.-]+',a.prefix)
    root=a.workdir.resolve()
    assert root==pkg/'runs/native_wt_ascr18/rep1_npt01_attempt02' and root.is_dir(), 'Only the existing original WT rep1 directory'
    assert a.prefix=='native_wt_ascr18_rep1_production', 'Use the fixed scientific production prefix'
    assert a.min_free_gb>=5 and shutil.disk_usage(root).free>=a.min_free_gb*1e9, 'Production reserve must be reviewed and available'
    serial=(pkg/'operator_records/equilibration_prep_v2_2_2/serial.lock').open('r')
    fcntl.flock(serial,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert str(Path(a.gmx).resolve())=='/opt/drylab/gromacs-2025.4/bin.AVX2_256/gmx_mpi'
    assert sha(a.gmx)=='90a2a9be92d37b236e0772a91df7eef1ac7fe24c4522d2994f6519f6835f6bd7', 'Actual executable pin changed'
    import importlib.util
    source=pkg/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py'
    spec=importlib.util.spec_from_file_location('production_qualifier',source)
    qualifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(qualifier)
    _,core,_=qualifier.load_validators(pkg)
    lock=(root/'stage.lock').open('a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    tpr=a.tpr.resolve(); assert tpr.is_file()
    if a.stage=='production':
        assert a.expected_end_ps==100000 and tpr==root/'production.tpr', 'Only the unchanged authorized WT 100 ns TPR'
        assert a.gate, 'Current production gate required'
        gate=json.loads(a.gate.read_text())
        assert gate['case_id']==a.case and gate['tpr_sha256']==sha(tpr)
        checks=['source_identity','structure_purpose','preparation','numerical_compatibility','restart_test','resources','storage_and_recovery']
        assert all(gate['checks'].get(k) is True for k in checks)
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(gate['live_verified_at'])).total_seconds()
        assert 0<=age<=900, 'Refresh live verification within 15 minutes'
        assert gate['replicate']==1 and gate['production_ns']==100
        for check in checks:
            entries=gate.get('evidence',{}).get(check)
            assert isinstance(entries,list) and entries, 'Each true check needs reviewed evidence: '+check
            for entry in entries:
                path=Path(entry['path'])
                assert path.is_absolute() and path.is_file() and not path.is_symlink() and sha(path)==entry['sha256'], 'Gate evidence missing/changed: '+check
        restart=gate.get('continuation_checkpoint')
        if a.cpi:
            assert isinstance(restart,dict) and Path(restart['path']).resolve()==a.cpi.resolve() and restart['sha256']==sha(a.cpi), 'Continuation checkpoint is not bound by reviewed gate'
        else:
            assert restart is None and not (root/'state.cpt').exists(), 'Initial production must start only from its zero-clock TPR'
    # Read actual binary state, not a pre-written success marker.
    preflight_stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    tpr_dump=core.command([a.gmx,'dump','-s',tpr],root/('audit.production.'+preflight_stamp+'.tpr.dump.txt'),root)
    for key,value in {'natoms':145776,'tinit':0,'init-step':0,'dt':.002,'nsteps':50000000,'nstxout-compressed':5000,'nstenergy':500,'nstlog':5000}.items():
        assert core.scalar(tpr_dump,key)==value, 'Production TPR clock/output mismatch: '+key
    if a.cpi:
        assert a.cpi.is_file() and a.cpi.resolve()==root/(a.prefix+'.cpt'), 'Only the reviewed latest production CPT in this workdir'
        cp_dump=core.command([a.gmx,'dump','-cp',a.cpi.resolve()],root/('audit.production.'+preflight_stamp+'.cpt.dump.txt'),root)
        step=core.scalar(cp_dump,'step');time_ps=core.scalar(cp_dump,'t')
        assert core.scalar(cp_dump,'#atoms')==145776 and 0<step<50000000 and step.is_integer() and abs(time_ps-.002*step)<.001, 'CPT is not an in-range production-clock continuation'
        assert restart['step']==int(step) and abs(restart['time_ps']-time_ps)<.001, 'Reviewed CPT clock differs'
    existing=[p for suffix in ['.log','.cpt','.gro','.xtc','.trr','.edr']
              for p in root.glob(a.prefix+'*'+suffix)]
    if not a.cpi: assert not existing, 'Existing outputs require explicit checkpoint continuation'
    cmd=[a.gmx,'mdrun','-s',str(tpr),'-deffnm',a.prefix,'-ntomp',str(a.threads),'-pin','off','-cpt','5','-maxh',str(a.maxh),'-notunepme','-cpo',str(root/(a.prefix+'.cpt'))]
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
    runtime_checked=False
    runtime_log=None
    previous_logs={p.resolve() for p in root.glob(a.prefix+'*.log')}
    expected_initial_step=restart['step'] if a.cpi else 0
    expected_initial_time=restart['time_ps'] if a.cpi else 0.
    issue=None;last_step=None;last_progress=time.monotonic();started=time.monotonic()
    with console.open('x') as f:
        assert 0<=(datetime.now(timezone.utc)-datetime.fromisoformat(gate['live_verified_at'])).total_seconds()<=900, 'Live review became stale before mdrun'
        assert sha(tpr)==gate['tpr_sha256'], 'TPR changed after preflight'
        p=subprocess.Popen(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT)
        manifest['pid']=p.pid;write(root/(run_id+'.command.json'),manifest)
        def stop(signum=None,frame=None):
            nonlocal issue
            issue=issue or 'Operator or supervisor requested a stop'
            if p.poll() is None:p.send_signal(signal.SIGTERM)
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        deadline=None
        while True:
            logs=fresh_segment_logs(root,a.prefix,previous_logs)
            log=logs[-1] if logs else None
            text=log.read_text(errors='replace') if log else ''
            content=console.read_text(errors='replace')+'\n'+text
            bad=[x for x in content.splitlines() if re.search(r'LINCS WARNING|cannot be settled|Fatal error|\bnan\b|\binf\b',x,re.I)
                 and not re.fullmatch(r'\s*epsilon-rf\s*=\s*inf\s*',x)]
            steps=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+([-+\d.eE]+)',text)
            latest=steps[-1] if steps else None
            if log!=runtime_log:
                runtime_checked=False;runtime_log=log
            if latest and not runtime_checked:
                try:
                    stride=int(core.scalar(tpr_dump,'nstlog'))
                    expected_log_step=math.ceil(expected_initial_step/stride)*stride
                    assert int(steps[0][0])==expected_log_step and abs(float(steps[0][1])-.002*expected_log_step)<.001, 'First saved log frame differs from reviewed CPT plus original logging grid'
                    if a.cpi:assert 'Reading checkpoint file '+str(a.cpi.resolve()) in text, 'Runtime did not report reading the reviewed CPT'
                    core.runtime_parameters_check(tpr_dump,text)
                    runtime_checked=True
                except Exception as exc:
                    issue='Qualified runtime changed: '+str(exc)
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
    closed=code==0 and 'Finished mdrun' in text and not issue and runtime_checked
    reached=bool(closed and latest and abs(float(latest[1])-a.expected_end_ps)<.01)
    result=dict(**manifest,finished_at=now(),exit_code=code,segment_closed_normally=closed,
                observed_target_time_reached=reached,full_production_verified=False,issue=issue,
                next_action='Validate CPT/XTC/EDR endpoints and hashes before declaring completion' if reached else 'Inspect and continue from latest valid checkpoint if authorized')
    write(root/(run_id+'.result.json'),result)
    event(root,'TERMINAL_NORMAL' if closed else 'TERMINAL_ABNORMAL',
          f'Segment closed; target_time_reached={reached}; full trajectory completion NOT validated; issue={issue}',run_id+'.result.json')
    if not closed:raise SystemExit(1)

if __name__=='__main__':main()
