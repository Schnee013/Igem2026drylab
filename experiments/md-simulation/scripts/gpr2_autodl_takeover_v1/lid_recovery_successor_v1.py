#!/usr/bin/env python3
"""Fixed remaining four-case succession after the active pair; no retries or new scope."""
import argparse,fcntl,json,os,re,signal,subprocess,sys,time
from pathlib import Path
import remaining_runtime_v1 as d
import dual_runtime as first
import post_dual_preparation_queue_v1 as raw
import new_lid_preparation_v1_1 as lid

SHARED=r'CUDA error|cudaError|out of memory|GPU.*(?:failed|lost)|cuFFT.*error'
CODE=('remaining_closed_v1.py','remaining_runtime_v1.py','qualify_remaining_case_v1.py','run_stage_remaining_dual_v1.py','remaining_dual_controller_v1.py','compile_remaining_production_v1_1.py','new_lid_preparation_v1_1.py','run_stage_new_lid_v1.py','existing_npt_sequence.py','prepare_existing_npt.py','run_stage_existing_npt.py','dual_runtime.py','wt_controller_v1_5.py','lid_recovery_successor_v1.py')

def check(b,code):
    checks=raw.check(b)
    for case in d.BATCHES['lid']:checks[case]=lid.sources(b,case,code/'E2_CLOSED_INPUTS_20261006T0926Z.json')
    return {'own_sources':checks,'code_sha256':{n:d.sha(code/n) for n in CODE}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--check-only',action='store_true');a=ap.parse_args();b=a.bundle.resolve();code=Path(__file__).resolve().parent
    checks=check(b,code)
    if a.check_only:print(json.dumps(checks));return
    out=b/'operator_records/lid_recovery_successor_v1';out.mkdir(exist_ok=True)
    lock=(out/'queue.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    d.need(not (out/'source_preflight.json').exists(),'Queue already initialized; inspect saved events instead of repeating')
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=p.read_bytes().split(b'\0')
        except (FileNotFoundError,ProcessLookupError):continue
        d.need(not any(Path(x.decode(errors='replace')).name in ('post_dual_preparation_queue_v1.py','six_case_successor_v1.py','six_case_successor_v1_1.py') for x in args),'Old waiting queue still active')
    d.save(out/'source_preflight.json',checks);events=[];child=None
    def status(state,**kw):d.save(out/'status.json',{'pid':os.getpid(),'at':d.now(),'state':state,'events':events,**kw})
    def stop(signum,frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=150)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        status('OPERATOR_STOP_REQUESTED');raise RuntimeError('Queue stopped; owned child requested graceful stop')
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    def run(script,args,label,state,case=None):
        nonlocal child
        for n,h in checks['code_sha256'].items():d.need(d.sha(code/n)==h,'Reviewed execution source changed: '+n)
        d.live(b);status(state,case_id=case)
        with (out/(label+'.console.txt')).open('x') as f:
            child=subprocess.Popen([sys.executable,'-E',str(code/script),'--bundle',str(b),*map(str,args)],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
            status(state,case_id=case,child_pid=child.pid);rc=child.wait();child=None
        d.live(b)
        return rc
    def shared_failure(case,label):
        paths=[out/(label+'.console.txt')]+list((b/d.CASES[case]['work']).glob('*.log'))+list((b/d.CASES[case]['qualifier']).glob('probe/*.log'))
        return any(re.search(SHARED,p.read_text(errors='replace'),re.I) for p in paths if p.is_file())
    def archived(case):
        qp=b/d.CASES[case]['qualifier'];receipt=b/'operator_records/e2_archive_v1'/(qp.name+'_segment_001.transfer.json');deadline=time.monotonic()+7200
        while not receipt.exists():
            ar=d.read(b/'operator_records/e2_archive_v1/status.json');d.need(ar['state']!='ERROR','Archiver failure; preserve qualified work for recovery')
            proc=Path('/proc/'+str(ar['pid'])+'/cmdline');d.need(proc.exists() and b'archive_closed_v1_' in proc.read_bytes(),'Archive process absent; inspect recovery without rerunning MD')
            d.need(time.monotonic()<deadline,'Own qualification recovery exceeds120min; inspect without rerun')
            status('WAITING_OWN_QUALIFICATION_ARCHIVE',case_id=case);time.sleep(30)
        r=d.read(receipt);d.need(r['rsync_receiver_checksum_comparison']=='PASS' and d.sha(b/r['manifest'])==r['manifest_sha256'],'Own archive identity/comparison failed')
    try:
        current=d.read(b/'operator_records/remaining_dual_raw_v1/status.json')
        d.need(current['state']=='BATCH_CLOSED' and not Path('/proc/'+str(current['pid'])+'/cmdline').exists(),'Raw batch still active or not normally closed')
        for case in d.BATCHES['raw']:
            result=current['cases'][case];cfg=d.CASES[case]
            last=d.read(sorted((b/cfg['records']).glob('segment_*/closed_segment.json'))[-1])
            d.need(result['state']=='COMPLETE_PENDING_RECOVERY' and result['closed_ps']==last['end_ps']==100000 and last['pass'] and d.sha(b/cfg['work']/(case+'_rep1_production.cpt'))==last['checkpoint']['sha256'],'Raw final actual state differs')
        d.live(b)
        for batch,cases in [('lid',d.BATCHES['lid'])]:
            ready=[]
            for slot,case in enumerate(cases):
                stage='preparation';label=case+'.prepare'
                try:
                    args=['--case',case]
                    if batch=='raw':script='existing_npt_sequence.py';args+=['--receipt',code/'FROZEN_INPUT_RECOVERY.json']
                    else:script='new_lid_preparation_v1_1.py';args+=['--recovery-receipt',code/'E2_CLOSED_INPUTS_20261006T0926Z.json','--execute']
                    rc=run(script,args,label,'PREPARING_OWN_CASE',case);d.need(rc==0,'Own preparation failed; no blind retry')
                    stage='compilation';label=case+'.compile';rc=run('compile_remaining_production_v1_1.py',['--case',case],label,'COMPILING_OWN_ZERO_CLOCK',case);d.need(rc==0,'Own compilation failed')
                    stage='qualification';label=case+'.qualify';rc=run('qualify_remaining_case_v1.py',['--case',case,'--slot',slot],label,'QUALIFYING_OWN_START_AND_RESTART',case);d.need(rc==0,'Own qualification failed')
                    result=d.read(b/d.CASES[case]['qualifier']/'qualification.json');d.need(result['case_id']==case and result['status']=='PASS_OWN_SIX_THREAD_FORCE_START_RESTART','Own qualification absent')
                    stage='recovery';archived(case);ready.append(case);events.append({'case_id':case,'at':d.now(),'state':'OWN_QUALIFIED_ARCHIVED','qualification_sha256':d.sha(b/d.CASES[case]['qualifier']/'qualification.json')})
                except Exception as exc:
                    events.append({'case_id':case,'at':d.now(),'state':'CASE_HOLD','stage':stage,'error':str(exc)});d.save(out/'events.json',events)
                    d.live(b)
                    if shared_failure(case,label):raise RuntimeError('Shared GPU/runtime issue; preserve evidence and stop dispatch') from exc
                d.save(out/'events.json',events)
            if ready:
                rc=run('remaining_dual_controller_v1.py',['--batch',batch,'--cases',*ready],batch+'.production','PRODUCING_QUALIFIED_BATCH')
                result=d.read(b/'operator_records'/('remaining_dual_'+batch+'_v1')/'status.json')
                d.need(rc==0 and result['state']=='BATCH_CLOSED','Batch dispatcher abnormal; no automatic restart')
                events.append({'batch':batch,'at':d.now(),'state':'BATCH_CLOSED','cases':result['cases']});d.save(out/'events.json',events)
        status('ALL_DISPATCH_FINISHED_AGENT_RECOVERY_REQUIRED',six_case_completion=False,next='Independently verify six100ns continuous trajectories and all E2 file hashes; any CASE_HOLD remains incomplete. Stop archiver and heartbeat only after actual complete verification; then stop owned tasks and shut down AutoDL under latest user authorization before E2 postanalysis.')
    except Exception as exc:
        status('QUEUE_HOLD',error=str(exc));raise
if __name__=='__main__':main()
