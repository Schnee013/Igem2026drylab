#!/usr/bin/env python3
"""Wait for the healthy WT boundary, then qualify the actual second case and pair."""
import argparse,fcntl,os,subprocess,sys,time
from pathlib import Path
import dual_runtime as d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();code=b/'operator_records/codex_takeover_v1';out=b/'operator_records/dual_transition_v1';out.mkdir(exist_ok=False)
 lock=(out/'transition.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);d.save(out/'status.json',{'state':'WAITING_VALIDATED_WT_BOUNDARY','pid':os.getpid(),'at':d.now()});start=time.monotonic()
 while True:
  s=d.read(code/'controller_status.json')
  if s['state']=='VALIDATED_BOUNDARY_PAUSED_DISPATCH':break
  if s['state']=='HOLD':d.save(out/'status.json',{'state':'UPSTREAM_WT_HOLD','upstream':s,'at':d.now()});return
  d.need(time.monotonic()-start<7200,'Boundary wait exceeded2h');time.sleep(10)
 def run(name,args,timeout):
  d.save(out/'status.json',{'state':name,'pid':os.getpid(),'at':d.now()})
  with (out/(name+'.console.txt')).open('x') as f:
   p=subprocess.Popen([sys.executable,'-E',*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
   try:rc=p.wait(timeout=timeout)
   except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=30);raise
  d.need(rc==0,name+' failed; preserve evidence')
 try:
  time.sleep(1)
  run('N84V_OWN_NEW_START_RESTART',[code/'qualify_n84v_production.py','--bundle',b,'--workdir',b/d.CASES['raw_n84v_ascr18']['work'],'--out',b/'operator_records/n84v_production_qualifier_v1','--execute'],600)
  q,(_,core,_)=d.load_core(b);cfg=d.CASES['raw_n84v_ascr18'];r=b/cfg['records'];r.mkdir(exist_ok=True);c=d.module(code/cfg['module'],'n84v_review');c.initial_review(b,b/cfg['work'],r,q,core,code/'FROZEN_INPUT_RECOVERY.json')
  run('REAL_PAIR_NUMERICAL_RESTART_CHECK',[code/'qualify_dual_pair.py','--bundle',b],1650)
  d.save(out/'status.json',{'state':'PAIR_QUALIFIED_AWAITING_DISPATCH','pid':os.getpid(),'at':d.now(),'qualification':str(b/'operator_records/dual_qualification_v1/qualification.json')})
 except Exception as exc:
  d.save(out/'status.json',{'state':'PAIR_NOT_RELEASED_RESTORE_VALIDATED_WT','at':d.now(),'error':str(exc)})
  # A failed candidate never consumes or overwrites the accepted formal source.
  (code/'pause_dispatch').unlink(missing_ok=True)
  with (out/'baseline_restore.console.txt').open('x') as f:p=subprocess.Popen([sys.executable,'-E',str(code/'wt_controller_v1_5.py'),'--bundle',str(b),'--records',str(code),'--receipt',str(code/'INITIAL_RECOVERY_RECEIPT.json'),'--execute'],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
  d.save(out/'baseline_restore.json',{'at':d.now(),'pid':p.pid,'reason':'candidate failed; previously qualified unchanged WT continuation only'})
  raise
if __name__=='__main__':main()
