#!/usr/bin/env python3
"""One-time archive replacement only after the existing transfer batch closes normally."""
import argparse,fcntl,os,subprocess,sys,time
from pathlib import Path
import dual_runtime as d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--old-pid',type=int,required=True);a=ap.parse_args();b=a.bundle.resolve();code=Path(__file__).resolve().parent;out=b/'operator_records/archive_handoff_v1_3';out.mkdir(exist_ok=False)
 lock=(out/'handoff.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 ar=b/'operator_records/e2_archive_v1';stop=ar/'STOP';target=code/'archive_closed_v1_3.py';expected=d.sha(target);token='Normal-batch handoff to archive_closed_v1_3; no interruption of active transfer.\n'
 def status(state,**kw):d.save(out/'status.json',{'at':d.now(),'pid':os.getpid(),'state':state,'old_archive_pid':a.old_pid,**kw})
 try:
  proc=Path(f'/proc/{a.old_pid}/cmdline');d.need(proc.exists() and str(code/'archive_closed_v1_2.py').encode() in proc.read_bytes().split(b'\0'),'Old archiver identity absent')
  d.need(not stop.exists(),'Another archive stop request exists')
  with stop.open('x') as f:f.write(token)
  status('WAITING_NORMAL_CURRENT_BATCH',new_source_sha256=expected);deadline=time.monotonic()+7200
  while proc.exists() and str(code/'archive_closed_v1_2.py').encode() in proc.read_bytes().split(b'\0'):
   d.need(d.read(ar/'status.json')['state']!='ERROR','Old transfer failed; agent must classify, not auto-restart')
   d.need(time.monotonic()<deadline,'Normal handoff exceeded2h; inspect current transfer')
   time.sleep(30)
  d.need(d.read(ar/'status.json')['state']=='IDLE','Old archiver did not finish normally')
  for key in ('codex_takeover_v1_segment_006','n84v_production_v1_segment_002'):
   r=d.read(ar/(key+'.transfer.json'));d.need(r['rsync_receiver_checksum_comparison']=='PASS' and d.sha(b/r['manifest'])==r['manifest_sha256'],'Current new batch lacks verified transfer closure')
  d.need(stop.read_text()==token and d.sha(target)==expected,'Handoff request or reviewed source changed');stop.rename(out/'completed_stop_request.txt')
  with (out/'new_archive.console.txt').open('x') as log:
   child=subprocess.Popen([sys.executable,'-E',str(target),'--bundle',str(b)],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  time.sleep(2);d.need(child.poll() is None,'New archiver failed to stay running');status('ARCHIVE_V1_3_STARTED',new_pid=child.pid,new_source_sha256=expected)
 except Exception as exc:status('HANDOFF_HOLD',error=str(exc));raise
if __name__=='__main__':main()
