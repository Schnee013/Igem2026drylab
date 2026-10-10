#!/usr/bin/env python3
"""Continue the closest next case after WT; preserve per-case holds."""
import argparse,fcntl,json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone

def save(p,v):
 t=Path(str(p)+'.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
def now():return datetime.now(timezone.utc).isoformat()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();code=b/'operator_records/codex_takeover_v1';r=b/'operator_records/successor_queue_v1';r.mkdir(exist_ok=True)
 lock=(r/'queue.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 status=r/'status.json';save(status,{'state':'WAITING_WT_100NS','pid':os.getpid(),'at':now(),'gpu_jobs_submitted':False})
 while True:
  s=json.loads((code/'controller_status.json').read_text())
  if s['state']=='100NS_REACHED_RECOVERY_PENDING':break
  if s['state']=='HOLD':
   save(status,{'state':'WT_HOLD_REQUIRES_AGENT_CLASSIFICATION','at':now(),'upstream':s,'note':'Do not infer a shared versus case-specific fault; heartbeat must classify before dispatching next independent case.'})
  if (r/'ALLOW_AFTER_CASE_SPECIFIC_HOLD').exists() and s['state']=='HOLD':break
  time.sleep(30)
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1');events=[]
 def run(name,args):
  save(status,{'state':'EXECUTING','step':name,'pid':os.getpid(),'at':now(),'events':events})
  with (r/(name+'.console.txt')).open('x') as f:p=subprocess.Popen([sys.executable,'-E',*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
  rc=p.wait();events.append({'step':name,'returncode':rc,'finished_at':now()});save(r/'events.json',events);return rc
 w=b/'runs/raw_n84v_ascr18/rep1_codex_v1'
 rc=run('n84v_own_start_restart',[code/'qualify_n84v_production.py','--bundle',b,'--workdir',w,'--out',b/'operator_records/n84v_production_qualifier_v1','--execute'])
 if rc==0:run('n84v_100ns',[code/'n84v_controller.py','--bundle',b,'--records',b/'operator_records/n84v_production_v1','--receipt',code/'FROZEN_INPUT_RECOVERY.json','--execute'])
 for case in ('raw_n84v_ascr3','raw_v368r_ascr18'):
  run(case+'_npt',[code/'existing_npt_sequence.py','--bundle',b,'--case',case,'--receipt',code/'FROZEN_INPUT_RECOVERY.json'])
 save(status,{'state':'NEXT_PREPARATION_AND_PRODUCTION_QUALIFICATION_REQUIRED','at':now(),'events':events,'complete':False,'remaining':'Own production compile/restart for two NPT cases and full own new-lid preparation; no completion claim'})
if __name__=='__main__':main()
