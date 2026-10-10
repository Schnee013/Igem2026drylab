import hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
b=Path('/root/autodl-tmp/gpr2-twf154-dots-20261006')
out=b/'operator_records/dual_qualification_archive_v1';out.mkdir(exist_ok=False)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
roots=[b/'operator_records/dual_qualification_v1',b/'operator_records/n84v_production_qualifier_v1']
assert json.loads((roots[0]/'dual_production_review.json').read_text())['status']=='ACCEPT_OWN_TWO_CASE_DUAL_PRODUCTION'
files=sorted(p for root in roots for p in root.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix not in ('.lock','.pyc') and 'mps_pipe' not in p.parts)
files += [b/'operator_records/n84v_production_v1/initial_review.json']
entries=[{'relative_path':str(p.relative_to(b)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
manifest=out/'manifest.json';manifest.write_text(json.dumps({'source':'Closed own two-case dual numerical and restart qualification; no formal production credit','production_credit_ns':0,'files':entries},indent=2)+'\n')
listing=out/'files.txt';listing.write_text('\n'.join([e['relative_path'] for e in entries]+[str(manifest.relative_to(b))])+'\n')
ssh='ssh -i /root/.ssh/gpr2_e2_archive -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/root/.ssh/gpr2_e2_known_hosts -p 40042'
args=['rsync','-aR','--omit-dir-times','--partial','--timeout=120','--bwlimit=15000','--files-from='+str(listing),'-e',ssh,str(b)+'/', 'dengwei@e2.tongyuangene.com:./']
with (out/'rsync.log').open('x') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
r=subprocess.run(args[:1]+['--checksum','--dry-run','--itemize-changes']+args[1:],text=True,capture_output=True,check=True,timeout=1800)
assert not r.stdout.strip(),r.stdout
assert all(sha(b/e['relative_path'])==e['sha256'] for e in entries)
receipt={'transferred_at':datetime.now(timezone.utc).isoformat(),'destination':'nkuliulab-e2:/ifs1/User/dengwei/igem/md/gpr2-autodl/','files':len(entries),'bytes':sum(e['bytes'] for e in entries),'manifest_sha256':sha(manifest),'rsync_checksum':'PASS','independent_e2_sha256':'PENDING'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
