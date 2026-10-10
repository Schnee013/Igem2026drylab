#!/usr/bin/env python3
"""Wait out performance timing, then run single-thread input preparation only."""
import argparse,fcntl,json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone

def save(p,v):
 t=Path(str(p)+'.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
def now():return datetime.now(timezone.utc).isoformat()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();r=b/'operator_records/codex_takeover_v1'
 lock=(r/'new_lid_input_setup.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 status=r/'new_lid_input_setup_status.json';save(status,{'state':'WAITING_PERFORMANCE_TIMING','pid':os.getpid(),'at':now()})
 until=time.monotonic()+4200
 while True:
  p=b/'operator_records/performance_windows_v1/production_resume.json'
  if p.exists():break
  if time.monotonic()>until:raise RuntimeError('Performance wait exceeded bound; no input setup started')
  time.sleep(20)
 results=[]
 for case in ('v368r_ascr3_lid_rebuilt_own_pose_v1','native_wt_ascr3_lid_rebuilt_own_pose_v1'):
  save(status,{'state':'CPU_INPUT_SETUP','case':case,'pid':os.getpid(),'at':now(),'md_started':False})
  with (r/(case+'.input_setup.console.txt')).open('x') as f:
   result=subprocess.run([sys.executable,'-E',str(r/'new_lid_inputs.py'),'--bundle',str(b),'--case',case],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'),timeout=900)
  results.append({'case_id':case,'returncode':result.returncode,'no_md_started':True})
 save(status,{'state':'INPUT_SETUP_FINISHED_REVIEW_REQUIRED','pid':os.getpid(),'at':now(),'results':results})
if __name__=='__main__':main()
