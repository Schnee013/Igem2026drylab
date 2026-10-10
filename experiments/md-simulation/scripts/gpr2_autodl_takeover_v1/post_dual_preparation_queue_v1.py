#!/usr/bin/env python3
"""After the current production pair closes, finish two existing preheats' own NPT."""
import argparse, fcntl, json, os, re, subprocess, sys, time
from pathlib import Path
import dual_runtime as d
import prepare_existing_npt as prep

CASES=('raw_n84v_ascr3','raw_v368r_ascr18')

def check(b):
    reports={}
    for case in CASES:
        plan=prep.verify_sources(b,case);w=b/'runs'/case/'rep1_codex_v1'
        initial=d.read(w/'initial_complete.json');prep.validate_manifest(w,initial['evidence_sha256'],prep.INITIAL_EVIDENCE)
        d.need(d.read(w/'start.structure.json')['pass'],'Own initial structure failed')
        reports[case]={'initial_complete_sha256':d.sha(w/'initial_complete.json'),'atom_count':plan['atom_count'],'source_hold_cpt_sha256':plan['source_sha256'][f'compute/cases/{case}/prepared/hold.cpt'],'production_ready':False}
    return reports

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--check-only',action='store_true');a=ap.parse_args();b=a.bundle.resolve();code=Path(__file__).resolve().parent
    checks=check(b)
    if a.check_only:print(json.dumps(checks));return
    out=b/'operator_records/post_dual_preparation_queue_v1';out.mkdir(exist_ok=True);lock=(out/'queue.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    d.need(not (out/'events.json').exists(),'This queue has already run; inspect before a versioned continuation')
    d.save(out/'source_preflight.json',checks)
    def status(state,**kw):d.save(out/'status.json',{'at':d.now(),'pid':os.getpid(),'state':state,**kw})
    while True:
        current=d.read(b/'operator_records/dual_dispatch_v1/status.json')
        if current['state']=='PAIR_CLOSED_NEXT_CASE_PREPARATION_REQUIRED' and all(v['state']=='COMPLETE_PENDING_RECOVERY' and v['closed_ps']==100000 for v in current['cases'].values()):
            pid=current['pid'];cmd=Path(f'/proc/{pid}/cmdline')
            if not cmd.exists() or b'dual_controller.py' not in cmd.read_bytes():break
        if current['state']=='DISPATCHER_HOLD' or any(v['state']=='HOLD' for v in current.get('cases',{}).values()):
            status('CURRENT_PAIR_HOLD_NEEDS_AGENT_CLASSIFICATION',upstream=current,gpu_jobs_submitted=False)
        else:status('WAITING_CURRENT_PAIR_NORMAL_100NS',gpu_jobs_submitted=False)
        time.sleep(60)
    for case,cfg in d.CASES.items():
        w=b/cfg['work'];closed=sorted((b/cfg['records']).glob('segment_*/closed_segment.json'));last=d.read(closed[-1])
        d.need(last['pass'] and last['end_ps']==100000 and d.sha(w/(case+'_rep1_production.cpt'))==last['checkpoint']['sha256'],'Current pair final CPT not actually accepted')
    events=[]
    for case in CASES:
        try:
            check(b);d.live(b);status('EXECUTING_OWN_NPT',case_id=case,events=events)
            cmd=[sys.executable,'-E',str(code/'existing_npt_sequence.py'),'--bundle',str(b),'--case',case,'--receipt',str(code/'FROZEN_INPUT_RECOVERY.json')]
            with (out/(case+'.console.txt')).open('x') as f:p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
            rc=p.wait();w=b/'runs'/case/'rep1_codex_v1'
            if rc:
                texts=(out/(case+'.console.txt')).read_text(errors='replace')+'\n'+'\n'.join(f.read_text(errors='replace') for f in w.glob('npt*.log'))
                d.live(b)
                if re.search(r'CUDA error|cudaError|out of memory|GPU.*(?:failed|lost)|cuFFT.*error',texts,re.I):raise RuntimeError('Shared runtime failure; do not dispatch another case')
                events.append({'case_id':case,'state':'CASE_HOLD','returncode':rc,'at':d.now()})
            else:
                result=d.read(w/'preparation_complete.json');d.need(result['case_id']==case and result['preparation_pass'] and result['final_time_ps']==2750,'Own NPT completion absent')
                with (out/(case+'.compile.console.txt')).open('x') as f:
                    compiled=subprocess.run([sys.executable,'-E',str(code/'compile_remaining_production_v1.py'),'--bundle',str(b),'--case',case],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
                events.append({'case_id':case,'state':'PREPARATION_PASSED_OWN_PRODUCTION_QUALIFICATION_PENDING' if compiled.returncode==0 else 'CASE_HOLD_OWN_COMPILATION_FAILED','compile_returncode':compiled.returncode,'at':d.now(),'evidence_sha256':d.sha(w/'preparation_complete.json')})
            d.save(out/'events.json',events)
        except Exception as exc:status('QUEUE_HOLD',error=str(exc),events=events);raise
    status('OWN_NEXT_PAIR_PRODUCTION_QUALIFICATION_REQUIRED',events=events,six_case_completion=False,next='Use these own accepted NPT states to compile/qualify the next zero-clock production pair. Do not run all new-lid preparation ahead of an already qualified production case; new_lid_preparation_v1 is separately deployed.')
if __name__=='__main__':main()
