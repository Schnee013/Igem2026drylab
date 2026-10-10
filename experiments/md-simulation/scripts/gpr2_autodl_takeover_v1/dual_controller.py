#!/usr/bin/env python3
"""Two owned production workers; actual gates, finite closure and native-CPT continuation."""
import argparse,fcntl,json,os,re,signal,subprocess,sys,time
from pathlib import Path
import dual_runtime as d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();code=b/'operator_records/codex_takeover_v1';out=b/'operator_records/dual_dispatch_v1';out.mkdir(exist_ok=True)
 locks=[];active={};states={};cohort=None;samples=[];timing_start=None
 for path in (b/'operator_records/codex_scheduler.lock',b/'operator_records/equilibration_prep_v2_2_2/serial.lock'):
  f=path.open('a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 q,(_,core,_)=d.load_core(b);six=d.SixCore(core);qualification=b/'operator_records/dual_qualification_v1/qualification.json';qualified=d.read(qualification)
 d.need(qualified['status']=='PASS_OWN_TWO_CASE_SIX_THREAD_FORCE_AND_RESTART','Actual dual-case qualification is absent')
 for name,expected in qualified['evidence_sha256'].items():d.need(d.sha(qualification.parent/name)==expected,'Dual qualification evidence changed: '+name)
 review_path=qualification.parent/'dual_production_review.json';dual_review=d.read(review_path)
 d.need(dual_review['status']=='ACCEPT_OWN_TWO_CASE_DUAL_PRODUCTION' and dual_review['qualification_sha256']==d.sha(qualification),'Supplemental actual-energy review absent')
 for path,expected in dual_review['evidence_sha256'].items():d.need(d.sha(path)==expected,'Supplemental reviewed evidence changed')
 lease={'pid':os.getpid(),'started_at':d.now(),'slots':{str(i):case for i,case in enumerate(d.CASES)},'controller_sha256':d.sha(Path(__file__)),'worker_sha256':d.sha(code/'run_stage_dual_v1.py'),'runtime_sha256':d.sha(code/'dual_runtime.py')};d.save(out/'lease.json',lease)
 def ref(p):return {'path':str(p),'sha256':d.sha(p)}
 def status():d.save(out/'status.json',{'pid':os.getpid(),'observed_at':d.now(),'state':'PRODUCING' if active else 'VALIDATING_OR_DISPATCHING','configuration':qualified['configuration'],'cases':states,'workers':{c:{'supervisor_pid':v['p'].pid,'slot':v['slot'],'segment':v['n'],'start_ps':v['start']} for c,v in active.items()}})
 def stop(signum=None,frame=None):
  for v in active.values():
   if v['p'].poll() is None:v['p'].send_signal(signal.SIGTERM)
  raise RuntimeError('Dispatcher stopped; owned supervisors requested graceful MD stop')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 contexts={}
 for slot,(case,cfg) in enumerate(d.CASES.items()):
  work=b/cfg['work'];records=b/cfg['records'];c=d.module(code/cfg['module'],'case_'+case);initial=records/'initial_review.json';review=d.read(initial)
  d.need(review['production_tpr_sha256']==d.sha(work/'production.tpr')==qualified['cases'][case]['production_tpr_sha256'],'Own reviewed/tested TPR differs')
  for rel,expected in review['preparation_source_sha256'].items():d.need(d.sha(b/rel)==expected,'Own immutable source changed')
  closed=sorted(records.glob('segment_*/closed_segment.json'));start=d.read(closed[-1])['end_ps'] if closed else 0.
  if not closed:d.need(not list(work.glob(case+'_rep1_production*.log')),'Unvalidated existing production output')
  tprfile=b/('operator_records/wt_production_start_restart_20261006T0400Z/production_tpr_dump.stdout.txt' if case=='native_wt_ascr18' else 'operator_records/n84v_production_qualifier_v1/production_tpr_dump.stdout.txt')
  contexts[case]={'slot':slot,'work':work,'records':records,'c':c,'initial':initial,'closed':closed,'start':start,'tprdump':tprfile.read_text(),'first_dual':True};states[case]={'state':'READY','closed_ps':start}
 try:
  while True:
   for case,ctx in contexts.items():
    if case in active or states[case]['state']=='HOLD' or ctx['start']>=100000:continue
    w=ctx['work'];c=ctx['c'];n=len(ctx['closed'])+1;segment=ctx['records']/f'segment_{n:03d}';segment.mkdir(exist_ok=False)
    live=d.live(b,[v['p'].pid for v in active.values()]);d.save(segment/'live_preflight.json',live)
    d.need(d.sha(w/'production.tpr')==qualified['cases'][case]['production_tpr_sha256'],'Immutable production input changed')
    gate={'case_id':case,'replicate':1,'production_ns':100,'tpr_sha256':d.sha(w/'production.tpr'),'live_verified_at':live['utc'],'checks':{},'evidence':{},'continuation_checkpoint':None,'dual_qualification':ref(qualification)}
    # Baseline own preparation/source/restart reviews and actual new dual qualification
    # above must both pass; these booleans are never edited to bypass a failed check.
    for key in c.CHECKS:gate['checks'][key]=True;gate['evidence'][key]=[ref(ctx['initial']),ref(qualification),ref(review_path)]
    gate['evidence']['resources']=[ref(segment/'live_preflight.json')];gate['evidence']['storage_and_recovery'] += [ref(code/('INITIAL_RECOVERY_RECEIPT.json' if case=='native_wt_ascr18' else 'FROZEN_INPUT_RECOVERY.json'))]
    if ctx['start']:
     prev=d.read(ctx['closed'][-1]);cp=w/(case+'_rep1_production.cpt');d.need(d.sha(cp)==prev['checkpoint']['sha256'],'Latest CPT not the validated boundary')
     gate['continuation_checkpoint']={**ref(cp),'step':prev['step'],'time_ps':ctx['start']};gate['evidence']['restart_test'].append(ref(ctx['closed'][-1]))
    d.save(segment/'production_gate.json',gate);d.save(segment/'dual_runtime.json',{'configuration':qualified['configuration'],'slot':ctx['slot'],'source_qualification':ref(qualification),'production_credit_rule':'Only this case own unchanged formal TPR/CPT trajectory counts'})
    old_logs={str(p) for p in w.glob(case+'_rep1_production*.log')}
    cmd=[sys.executable,'-E',str(code/'run_stage_dual_v1.py'),'--case',case,'--stage','production','--workdir',str(w),'--tpr',str(w/'production.tpr'),'--prefix',case+'_rep1_production','--threads','6','--slot',str(ctx['slot']),'--dispatcher-pid',str(os.getpid()),'--offload','gpu','--maxh',str(.12 if ctx['first_dual'] else 1),'--expected-end-ps','100000','--min-free-gb','5','--gate',str(segment/'production_gate.json')]
    if ctx['start']:cmd+=['--cpi',str(w/(case+'_rep1_production.cpt'))]
    f=(segment/'supervisor.console.txt').open('x');p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=d.env(ctx['slot']))
    active[case]={'p':p,'f':f,'slot':ctx['slot'],'n':n,'out':segment,'start':ctx['start'],'old_logs':old_logs};states[case]={'state':'SUPERVISING','closed_ps':ctx['start'],'segment':n,'supervisor_pid':p.pid};d.save(ctx['records']/'controller_status.json',{'pid':os.getpid(),'case':case,'state':'DUAL_SUPERVISING','segment':n,'start_ps':ctx['start'],'slot':ctx['slot'],'gate':str(segment/'production_gate.json')});ctx['first_dual']=False
    status()
   if len(active)==2:
    current=tuple((c,v['p'].pid) for c,v in active.items())
    if current!=cohort:cohort=current;samples=[];timing_start=time.monotonic()
    point={'monotonic':time.monotonic(),'at':d.now(),'time_ps':{}}
    for case,v in active.items():
     logs=[p for p in contexts[case]['work'].glob(case+'_rep1_production*.log') if str(p) not in v['old_logs']]
     if len(logs)==1:
      matches=re.findall(r'Step\s+Time\s*\n\s*\d+\s+([-+\d.eE]+)',logs[0].read_text());point['time_ps'][case]=float(matches[-1]) if matches else None
    if time.monotonic()-timing_start>=60 and len(point['time_ps'])==2 and all(v is not None for v in point['time_ps'].values()) and all(v['p'].poll() is None for v in active.values()):
     samples.append(point)
     with (out/'common_samples.jsonl').open('a') as f:f.write(json.dumps(point)+'\n')
   for case,v in list(active.items()):
    if v['p'].poll() is None:continue
    ctx=contexts[case];c=ctx['c'];v['f'].close()
    if samples and cohort and len(samples)>1:
     seconds=samples[-1]['monotonic']-samples[0]['monotonic']
     if seconds>=300:
      speeds={key:(samples[-1]['time_ps'][key]-samples[0]['time_ps'][key])/1000/seconds*86400 for key in samples[0]['time_ps']};d.save(out/('throughput_'+str(v['p'].pid)+'.json'),{'at':d.now(),'common_seconds':seconds,'per_case_ns_day':speeds,'aggregate_ns_day':sum(speeds.values()),'source':'actual two different formal production cases; first60s excluded','cases_and_supervisors':cohort})
     samples=[];cohort=None
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
  d.save(out/'status.json',{'pid':os.getpid(),'observed_at':d.now(),'state':'PAIR_CLOSED_NEXT_CASE_PREPARATION_REQUIRED','cases':states,'six_case_completion':False,'next':'Prepare and independently qualify the remaining cases, retaining the same six-thread two-task policy; do not count this pair as600ns.'})
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
