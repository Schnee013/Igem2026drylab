import concurrent.futures as cf
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import time

root=Path('/private/tmp/gpr2-own-lid-20261005/downloads/dependencies');root.mkdir(exist_ok=True)
env=os.environ.copy()
if env.get('AGENT_PROXY_URL'):
    for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY'):env[k]=env['AGENT_PROXY_URL']
    env['NO_PROXY']=env.get('AGENT_NO_PROXY','')
packages=[]
for name,version in [('numpy','2.5.3'),('rdkit','2026.3.6'),('pillow','12.3.0')]:
    meta=root/f'{name}.json'
    subprocess.run(['curl','-fsSL','--connect-timeout','15','--max-time','60',f'https://pypi.org/pypi/{name}/{version}/json','-o',str(meta)],env=env,check=True)
    j=json.loads(meta.read_text())
    wheels=[w for w in j['urls'] if 'cp312-cp312-macosx' in w['filename'] and w['filename'].endswith('arm64.whl')]
    assert wheels,(name,len(wheels))
    wheels.sort(key=lambda w:tuple(map(int,re.search(r'macosx_(\d+)_(\d+)',w['filename']).groups())))
    packages.append(wheels[-1])
tasks=[]
chunk=2*1024*1024
for w in packages:
    d=root/w['filename'].removesuffix('.whl');d.mkdir(exist_ok=True)
    for start in range(0,w['size'],chunk):tasks.append((w,d,start,min(start+chunk,w['size'])-1))
def get(t):
    w,d,start,end=t;p=d/f'{start}.part';h=d/f'{start}.header'
    for _ in range(3):
        r=subprocess.run(['curl','-fsSL','--connect-timeout','15','--max-time','120','--range',f'{start}-{end}',
            '-D',str(h),'-o',str(p),w['url']],env=env,capture_output=True)
        if r.returncode==0 and p.stat().st_size==end-start+1 and f'content-range: bytes {start}-{end}/' in h.read_text().lower():return
    raise RuntimeError(f'Failed dependency chunk {w["filename"]} {start}')
with cf.ThreadPoolExecutor(max_workers=8) as ex:list(ex.map(get,tasks))
for w in packages:
    p=root/w['filename'];d=root/w['filename'].removesuffix('.whl')
    with p.open('wb') as f:
        for start in range(0,w['size'],chunk):f.write((d/f'{start}.part').read_bytes())
    assert hashlib.sha256(p.read_bytes()).hexdigest()==w['digests']['sha256']
    print(json.dumps(dict(file=str(p),sha256=w['digests']['sha256'],verified_against='official PyPI release JSON')),flush=True)
(root/'manifest.json').write_text(json.dumps(packages,indent=2)+'\n')
args=['/private/tmp/gpr2-own-lid-20261005/env/bin/python','-m','pip','install','--no-index','--no-deps',*[str(root/w['filename']) for w in packages]]
subprocess.run(args,check=True)
