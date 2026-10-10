#!/usr/bin/env python3
"""Two owned production workers; actual gates, finite closure and native-CPT continuation."""
import argparse,fcntl,json,os,re,signal,subprocess,sys,time
from pathlib import Path
import remaining_runtime_v1 as d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--batch',choices=list(d.BATCHES),required=True);ap.add_argument('--cases',nargs='+',choices=list(d.CASES),required=True);a=ap.parse_args();b=a.bundle.resolve();code=b/'operator_records/codex_takeover_v1';out=b/'operator_records'/('remaining_dual_'+a.batch+'_v1');d.need(set(a.cases)<=set(d.BATCHES[a.batch]) and len(a.cases)==len(set(a.cases)), 'Invalid authorized batch');selected={c:d.CASES[c] for c in d.BATCHES[a.batch] if c in a.cases};out.mkdir(exist_ok=True)
 locks=[];active={};states={};cohort=None;samples=[];timing_start=None
 for path in (b/'operator_records/codex_scheduler.lock',b/'operator_records/equilibration_prep_v2_2_2/serial.lock'):
  f=path.open('a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 q,(_,core,_)=d.load_core(b);six=d.SixCore(core)
 lease={'pid':os.getpid(),'started_at':d.now(),'slots':{str(d.BATCHES[a.batch].index(case)):case for case in selected},'controller_sha256':d.sha(Path(__file__)),'worker_sha256':d.sha(code/'run_stage_remaining_dual_v1.py'),'runtime_sha256':d.sha(code/'remaining_runtime_v1.py')};d.save(out/'lease.json',lease)
 configuration={'threads_per_worker':6,'nstlist':200,'cores':d.CORES,'mps':False}
 def ref(p):return {'path':str(p),'sha256':d.sha(p)}
 def status():d.save(out/'status.json',{'pid':os.getpid(),'observed_at':d.now(),'state':'PRODUCING' if active else 'VALIDATING_OR_DISPATCHING','configuration':configuration,'cases':states,'workers':{c:{'supervisor_pid':v['p'].pid,'slot':v['slot'],'segment':v['n'],'start_ps':v['start']} for c,v in active.items()}})
 def stop(signum=None,frame=None):
  for v in active.values():
   if v['p'].poll() is None:v['p'].send_signal(signal.SIGTERM)
  raise RuntimeError('Dispatcher stopped; owned supervisors requested graceful MD stop')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 contexts={}
 for case,cfg in selected.items():
  slot=d.BATCHES[a.batch].index(case);work=b/cfg['work'];records=b/cfg['records'];records.mkdir(exist_ok=True);c=d.case_validator(case)
  initial=work/'source_preflight.json';review=d.read(initial);qualification=b/cfg['qualifier']/'qualification.json';qualified=d.read(qualification)
  d.need(qualified['status']=='PASS_OWN_SIX_THREAD_FORCE_START_RESTART' and qualified['case_id']==case and qualified['slot']==slot,'Own six-thread qualification absent')
  for name,h in qualified['evidence_sha256'].items():d.need(d.sha(qualification.parent/name)==h,'Own qualification evidence changed')
  d.need(review['case_id']==case and review['structure']['pass'] and review['preparation_evidence']['box_density_settled'],'Own preparation/source purpose not accepted')
  d.need(review['production_tpr_sha256']==d.sha(work/'production.tpr')==qualified['cases'][case]['production_tpr_sha256'],'Own reviewed/tested TPR differs')
  for rel,h in review['source_sha256'].items():d.need(d.sha(b/rel)==h,'Own immutable source changed')
  recovery=b/'operator_records/e2_archive_v1'/(qualification.parent.name+'_segment_001.transfer.json');rr=d.read(recovery)
  d.need(rr['rsync_receiver_checksum_comparison']=='PASS' and d.sha(b/rr['manifest'])==rr['manifest_sha256'],'Own qualification not transferred with receiver content comparison')
  archive=d.read(b/rr['manifest']);d.need(any(f['relative_path']==str(qualification.relative_to(b)) and f['sha256']==d.sha(qualification) for f in archive['files']),'Own qualification absent from archive')
  closed=sorted(records.glob('segment_*/closed_segment.json'));start=0.
  for path in closed:
   v=d.read(path);d.need(v['case_id']==case and v['pass'] and v['start_ps']==start and v['production_tpr_sha256']==d.sha(work/'production.tpr'),'Closed history is discontinuous or changed');start=v['end_ps']
   for f in v['files']:d.need(d.sha(f['path'])==f['sha256'],'Closed history file changed')
  if not closed:d.need(not list(work.glob(case+'_rep1_production*.log')),'Unvalidated existing production output')
  tprfile=qualification.parent/'probe/production_dump.stdout.txt'
  contexts[case]={'slot':slot,'work':work,'records':records,'c':c,'initial':initial,'closed':closed,'start':start,'tprdump':tprfile.read_text(),'first_dual':not closed,'qualification':qualification,'qualified':qualified,'recovery':recovery};states[case]={'state':'COMPLETE_PENDING_RECOVERY' if start==100000 else 'READY','closed_ps':start}
 try:
  while True:
   for case,ctx in contexts.items():
    if case in active or states[case]['state']=='HOLD' or ctx['start']>=100000:continue
    w=ctx['work'];c=ctx['c'];qualification=ctx['qualification'];qualified=ctx['qualified'];n=len(ctx['closed'])+1;segment=ctx['records']/f'segment_{n:03d}';segment.mkdir(exist_ok=False)
    live=d.live(b,[v['p'].pid for v in active.values()]);d.save(segment/'live_preflight.json',live)
    d.need(d.sha(w/'production.tpr')==qualified['cases'][case]['production_tpr_sha256'],'Immutable production input changed')
    gate={'case_id':case,'replicate':1,'production_ns':100,'tpr_sha256':d.sha(w/'production.tpr'),'live_verified_at':live['utc'],'checks':{},'evidence':{},'continuation_checkpoint':None,'dual_qualification':ref(qualification)}
    # Baseline own preparation/source/restart reviews and actual new dual qualification
    # above must both pass; these booleans are never edited to bypass a failed check.
    for key in c.CHECKS:gate['checks'][key]=True;gate['evidence'][key]=[ref(ctx['initial']),ref(qualification)]
    gate['evidence']['resources']=[ref(segment/'live_preflight.json')];gate['evidence']['storage_and_recovery'] += [ref(ctx['recovery'])]
    if ctx['start']:
     prev=d.read(ctx['closed'][-1]);cp=w/(case+'_rep1_production.cpt');d.need(d.sha(cp)==prev['checkpoint']['sha256'],'Latest CPT not the validated boundary')
     gate['continuation_checkpoint']={**ref(cp),'step':prev['step'],'time_ps':ctx['start']};gate['evidence']['restart_test'].append(ref(ctx['closed'][-1]))
    d.save(segment/'production_gate.json',gate);d.save(segment/'dual_runtime.json',{'configuration':configuration,'slot':ctx['slot'],'source_qualification':ref(qualification),'production_credit_rule':'Only this case own unchanged formal TPR/CPT trajectory counts'})
    old_logs={str(p) for p in w.glob(case+'_rep1_production*.log')}
    cmd=[sys.executable,'-E',str(code/'run_stage_remaining_dual_v1.py'),'--batch',a.batch,'--case',case,'--stage','production','--workdir',str(w),'--tpr',str(w/'production.tpr'),'--prefix',case+'_rep1_production','--threads','6','--slot',str(ctx['slot']),'--dispatcher-pid',str(os.getpid()),'--offload','gpu','--maxh',str(.12 if ctx['first_dual'] else 1),'--expected-end-ps','100000','--min-free-gb','5','--gate',str(segment/'production_gate.json')]
    if ctx['start']:cmd+=['--cpi',str(w/(case+'_rep1_production.cpt'))]
    f=(segment/'supervisor.console.txt').open('x');p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=d.env(ctx['slot']))
    active[case]={'p':p,'f':f,'slot':ctx['slot'],'n':n,'out':segment,'start':ctx['start'],'old_logs':old_logs};states[case]={'state':'SUPERVISING','closed_ps':ctx['start'],'segment':n,'supervisor_pid':p.pid};d.save(ctx['records']/'controller_status.json',{'pid':os.getpid(),'case':case,'state':'DUAL_SUPERVISING','segment':n,'start_ps':ctx['start'],'slot':ctx['slot'],'gate':str(segment/'production_gate.json')});ctx['first_dual']=False
    status()
   for case,v in list(active.items()):
    if v['p'].poll() is None:continue
    ctx=contexts[case];c=ctx['c'];v['f'].close()
    try:
     d.need(v['p'].returncode==0,'Owned supervisor failed; inspect actual issue, no automatic restart')
     accepted=c.validate_closed(b,ctx['work'],v['out'],six,d.GMX,v['start'],ctx['tprdump'],v['old_logs']);d.need(accepted['start_ps']==ctx['start'],'Case continuity failure')
     ctx['closed'].append(v['out']/'closed_segment.json');ctx['start']=accepted['end_ps'];states[case]={'state':'COMPLETE_PENDING_RECOVERY' if ctx['start']==100000 else 'READY','closed_ps':ctx['start']}
     with (ctx['records']/'closed_segments.jsonl').open('a') as f:f.write(json.dumps({'manifest':str(ctx['closed'][-1]),'sha256':d.sha(ctx['closed'][-1]),'end_ps':ctx['start']})+'\n')
     c.event(ctx['work'],'TERMINAL_NORMAL',f'Dual production segment validated; own production_ps={ctx["start"]}; recovery pending',str(ctx['closed'][-1]))
     d.save(ctx['records']/'controller_status.json',{'pid':os.getpid(),'case':case,'state':'100NS_REACHED_RECOVERY_PENDING' if ctx['start']==100000 else 'DUAL_VALIDATED_BOUNDARY','production_ps':ctx['start'],'closed_segments':len(ctx['closed'])})
    except Exception as exc:
     states[case]={'state':'HOLD','closed_ps':ctx['start'],'error':str(exc)};d.save(ctx['records']/'controller_status.json',{'pid':os.getpid(),'case':case,**states[case]});c.event(ctx['work'],'TERMINAL_ABNORMAL',str(exc),str(v['out']))
     evidence='\n'.join(p.read_text(errors='replace') for p in ctx['work'].glob(case+'_rep1_production*.log') if str(p) not in v['old_logs'])
     if re.search(r'CUDA error|cudaError|out of memory|GPU.*(?:failed|lost)|cuFFT.*error',evidence,re.I):raise RuntimeError('Shared GPU/runtime failure; stop both owned workers') from exc
    del active[case];status()
   if not active and all(s['state'] in ('HOLD','COMPLETE_PENDING_RECOVERY') for s in states.values()):break
   time.sleep(5)
  d.save(out/'status.json',{'pid':os.getpid(),'observed_at':d.now(),'state':'BATCH_CLOSED','cases':states,'six_case_completion':False,'next':'Queue may prepare the next authorized own-source batch; completion still requires six full trajectories and independent E2 hashes.'})
 except Exception as exc:
  d.save(out/'status.json',{'pid':os.getpid(),'observed_at':d.now(),'state':'DISPATCHER_HOLD','error':str(exc),'cases':states})
  for v in active.values():
   if v['p'].poll() is None:v['p'].send_signal(signal.SIGTERM)
  for v in active.values():
   if v['p'].poll() is None:
    try:v['p'].wait(timeout=150)
    except subprocess.TimeoutExpired:v['p'].kill()
  raise
 finally:
  for f in locks:fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main()
