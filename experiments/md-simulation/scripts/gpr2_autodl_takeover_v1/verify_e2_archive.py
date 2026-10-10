#!/usr/bin/env python3
"""Independently read E2 archive bytes and retain a compact local SHA256 receipt."""
import argparse,json,subprocess
from pathlib import Path
REMOTE=r'''
from pathlib import Path
import hashlib,json,datetime
root=Path('/ifs1/User/dengwei/igem/md/gpr2-autodl')
receipts=[]
for m in sorted(root.glob('operator_records/e2_archive_v1/*.manifest.json')):
 data=json.loads(m.read_text());bad=[];checked=0;total=0
 for entry in data['files']:
  p=(root/entry['relative_path']).resolve()
  if not p.is_relative_to(root) or not p.is_file():bad.append({'file':entry['relative_path'],'error':'missing/unsafe'});continue
  with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  if digest!=entry['sha256'] or p.stat().st_size!=entry['bytes']:bad.append({'file':entry['relative_path'],'error':'identity mismatch'})
  else:checked+=1;total+=entry['bytes']
 receipts.append({'manifest':str(m.relative_to(root)),'manifest_sha256':hashlib.sha256(m.read_bytes()).hexdigest(),'case_id':data['case_id'],'stage_kind':data.get('stage_kind','production'),'production_credit_ns':data.get('production_credit_ns',(data['end_ps']-data['start_ps'])/1000),'start_ps':data['start_ps'],'end_ps':data['end_ps'],'files_matched':checked,'expected_files':len(data['files']),'bytes_matched':total,'failures':bad,'all_match':not bad})
print(json.dumps({'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'destination':'nkuliulab-e2:/ifs1/User/dengwei/igem/md/gpr2-autodl/','method':'independent receiver-side SHA256 of every manifest entry','segments':receipts,'all_match':bool(receipts) and all(r['all_match'] for r in receipts)},indent=2))
'''
def main():
 import shlex
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 r=subprocess.run(['ssh','-o','BatchMode=yes','nkuliulab-e2','python3 -c '+shlex.quote(REMOTE)],text=True,capture_output=True,check=True,timeout=1200)
 data=json.loads(r.stdout);a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
 print(json.dumps({'receipt':str(a.output),'segments':len(data['segments']),'all_match':data['all_match']}))
if __name__=='__main__':main()
