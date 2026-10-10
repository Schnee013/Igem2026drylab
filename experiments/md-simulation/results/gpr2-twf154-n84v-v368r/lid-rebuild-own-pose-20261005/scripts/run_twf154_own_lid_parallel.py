#!/usr/bin/env python3
"""Launch two bounded local samplers with independent inputs and one thread each.

Requires an existing Python environment containing PyRosetta, NumPy and RDKit.
This only generates modelling candidates. It does not accept structures or run MD.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')


def event(path, state, source, detail):
    with path.open('a') as f:
        f.write(f'{datetime.now(timezone.utc).isoformat()}\t{state}\t{source}\t{detail}\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--python', required=True, type=Path)
    ap.add_argument('--sampler', required=True, type=Path)
    ap.add_argument('--configs', nargs=2, required=True, type=Path)
    ap.add_argument('--runtime', required=True, type=Path)
    ap.add_argument('--result', required=True, type=Path)
    ap.add_argument('--max-seconds', type=int, default=2400)
    args = ap.parse_args()
    env = os.environ.copy()
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
        env[name] = '1'
    env['PYTHONUNBUFFERED'] = '1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['TMPDIR'] = str(args.runtime/'tmp')
    Path(env['TMPDIR']).mkdir(exist_ok=True)
    jobs = []
    run_root = args.runtime/'runs'
    run_root.mkdir(exist_ok=True)
    events = args.result/'run_state_events.tsv'
    try:
        for cp in args.configs:
            cfg = json.loads(cp.read_text())
            cid = cfg['case_id']
            out = run_root/cid
            if out.exists():
                raise RuntimeError(f'Refusing to overwrite {out}')
            log_path = args.runtime/'logs'/f'{cid}.log'
            log = log_path.open('w')
            command = [str(args.python), '-u', str(args.sampler), '--config', str(cp), '--output', str(out)]
            process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
            jobs.append(dict(case_id=cid,process=process,log_handle=log,command=command,log=str(log_path),output=str(out),started_utc=datetime.now(timezone.utc).isoformat()))
        save(args.result/'processes.json',dict(observed_at=datetime.now(timezone.utc).isoformat(),
            jobs=[{k:v for k,v in j.items() if k not in ('process','log_handle')}|{'pid':j['process'].pid} for j in jobs],
            launcher_pid=os.getpid(),max_wall_seconds=args.max_seconds,threads_per_process=1))
        started = time.monotonic()
        while True:
            rows = []
            for j in jobs:
                code = j['process'].poll()
                out = Path(j['output'])
                candidates = out/'candidates.json'
                try:
                    cs = json.loads(candidates.read_text()) if candidates.exists() else []
                except json.JSONDecodeError:
                    cs = []
                row = dict(case_id=j['case_id'],pid=j['process'].pid,process_alive=(code is None),exit_code=code,
                    completed_attempts=len(cs),geometry_screen_passes=sum(c.get('geometric_screen_pass',False) for c in cs),
                    environment_record_exists=(out/'environment.json').exists())
                rows.append(row)
            status = dict(observed_at=datetime.now(timezone.utc).isoformat(),elapsed_s=round(time.monotonic()-started,1),jobs=rows,
                          production_ready=False)
            save(args.result/'live_status.json',status)
            print(json.dumps(status),flush=True)
            alive = [j for j in jobs if j['process'].poll() is None]
            if not alive:
                break
            initialized = sum(r['environment_record_exists'] and r['process_alive'] for r in rows)
            event(events,'RUNNING_VERIFIED' if initialized else 'UNRESOLVED','live_status.json',
                  f'{len(alive)} live sampler processes; {initialized} have environment output; completed attempts '+str([r['completed_attempts'] for r in rows]))
            if time.monotonic()-started > args.max_seconds:
                for j in alive:
                    j['process'].terminate()
                for j in alive:
                    try:
                        j['process'].wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        j['process'].kill()
                event(events,'TERMINAL_ABNORMAL','live_status.json','Bounded local sampling time reached; completed candidates preserved')
                raise RuntimeError('Sampling time limit reached')
            time.sleep(30)
        ok = all(j['process'].returncode == 0 for j in jobs)
        event(events,'TERMINAL_NORMAL' if ok else 'TERMINAL_ABNORMAL','live_status.json',
              'Local candidate batches finished; structural acceptance remains separate')
        if not ok:
            raise SystemExit(1)
    finally:
        for j in jobs:
            if j['process'].poll() is None:
                j['process'].terminate()
                try:
                    j['process'].wait(timeout=10)
                except subprocess.TimeoutExpired:
                    j['process'].kill()
            j['log_handle'].close()


if __name__ == '__main__':
    main()
