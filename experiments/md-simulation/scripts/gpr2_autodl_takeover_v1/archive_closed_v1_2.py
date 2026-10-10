#!/usr/bin/env python3
"""Transfer validated immutable parts directly to the dedicated E2 archive."""
import argparse,fcntl,hashlib,json,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
 t=Path(str(p)+'.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve()
 out=b/'operator_records/e2_archive_v1';out.mkdir(exist_ok=True)
 lock=(out/'archive.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 ssh='ssh -i /root/.ssh/gpr2_e2_archive -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/root/.ssh/gpr2_e2_known_hosts -p 40042'
 while True:
  try:
   manifests=sorted(b.glob('operator_records/*/segment_*/closed_segment.json'))
   for m in manifests:
    key=m.parent.parent.name+'_'+m.parent.name;receipt=out/(key+'.transfer.json')
    if receipt.exists():continue
    data=json.loads(m.read_text());assert data['pass'] is True
    files={Path(f['path']).resolve():f['sha256'] for f in data['files']}
    files[m]=sha(m)
    # All segment evidence is closed before this manifest is emitted.
    for p in m.parent.rglob('*'):
     if p.is_file() and p.suffix!='.pyc':files[p]=sha(p)
    work=next(Path(f['path']).parent for f in data['files'] if f['path'].endswith('.log'))
    for name in ('production.tpr','production.mdp','input_contract.json'):
     p=work/name
     if p.exists():files[p]=sha(p)
    assert all(p.is_relative_to(b) and not p.is_symlink() and sha(p)==v for p,v in files.items())
    entries=[{'relative_path':str(p.relative_to(b)),'sha256':v,'bytes':p.stat().st_size} for p,v in sorted(files.items())]
    manifest=out/(key+'.manifest.json');save(manifest,{'case_id':data['case_id'],'stage_kind':data.get('stage_kind','production'),'stage':data.get('stage','production'),'production_credit_ns':data.get('production_credit_ns',(data['end_ps']-data['start_ps'])/1000),'start_ps':data['start_ps'],'end_ps':data['end_ps'],'files':entries})
    filelist=out/(key+'.files.txt');filelist.write_text('\n'.join([x['relative_path'] for x in entries]+[str(manifest.relative_to(b))])+'\n')
    argv=['rsync','-aR','--omit-dir-times','--partial','--timeout=120','--bwlimit=15000','--files-from='+str(filelist),'-e',ssh,str(b)+'/', 'dengwei@e2.tongyuangene.com:./']
    with (out/(key+'.rsync.log')).open('a') as log:subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
    check=subprocess.run(argv[:1]+['--checksum','--dry-run','--itemize-changes']+argv[1:],text=True,capture_output=True,check=True,timeout=1800)
    assert not check.stdout.strip(), 'Receiver content differs after rsync: '+check.stdout
    assert all(sha(p)==v for p,v in files.items()),'Source changed during archive'
    save(receipt,{'transferred_at':datetime.now(timezone.utc).isoformat(),'destination':'nkuliulab-e2:/ifs1/User/dengwei/igem/md/gpr2-autodl/','manifest':str(manifest.relative_to(b)),'manifest_sha256':sha(manifest),'rsync_receiver_checksum_comparison':'PASS','independent_sha256_verification':'PENDING_AGENT_E2_READ','end_ps':data['end_ps']})
   save(out/'status.json',{'pid':os.getpid(),'observed_at':datetime.now(timezone.utc).isoformat(),'state':'IDLE','closed_manifests_seen':len(manifests)})
  except Exception as exc:
   save(out/'status.json',{'pid':os.getpid(),'observed_at':datetime.now(timezone.utc).isoformat(),'state':'ERROR','error':str(exc)})
   raise
  if (out/'STOP').exists():return
  time.sleep(60)
if __name__=='__main__':main()
