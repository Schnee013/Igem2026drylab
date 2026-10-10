import concurrent.futures as cf
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import zipfile

root = Path('/private/tmp/gpr2-own-lid-20261005/downloads')
size = 1532921712
chunk = 4 * 1024 * 1024
url = 'https://west.rosettacommons.org/pyrosetta/quarterly/release/pyrosetta-2026.29%2Breleasequarterly.80a0635615-cp312-cp312-macosx_12_0_arm64.whl'
env = os.environ.copy()
if env.get('AGENT_PROXY_URL'):
    for k in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'):
        env[k] = env['AGENT_PROXY_URL']
    env['NO_PROXY'] = env.get('AGENT_NO_PROXY', '')
started = time.monotonic()

def get(i):
    first, last = i*chunk, min((i+1)*chunk, size)-1
    part = root/f'part_{i:04d}'
    header = root/f'part_{i:04d}.headers'
    if part.exists() and part.stat().st_size == last-first+1:
        return part.stat().st_size
    for attempt in range(3):
        if time.monotonic()-started > 1800:
            raise TimeoutError('Bounded download exceeded 30 minutes')
        r = subprocess.run(['curl','-fsSL','--connect-timeout','20','--max-time','120',
            '--range',f'{first}-{last}','-D',str(header),'-o',str(part),url],
            env=env,capture_output=True,text=True)
        h = header.read_text().lower() if header.exists() else ''
        if r.returncode == 0 and part.stat().st_size == last-first+1 and f'content-range: bytes {first}-{last}/{size}' in h:
            return last-first+1
    raise RuntimeError(f'Chunk {i} failed after 3 bounded attempts')

done=0
last_report=0
with cf.ThreadPoolExecutor(max_workers=16) as pool:
    fs=[pool.submit(get,i) for i in range((size+chunk-1)//chunk)]
    for f in cf.as_completed(fs):
        done += f.result()
        elapsed=time.monotonic()-started
        if elapsed-last_report>20 or done==size:
            progress=dict(bytes=done,total_bytes=size,percent=round(100*done/size,2),elapsed_s=round(elapsed,1),MiB_s=round(done/1024**2/elapsed,2))
            (root/'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
            print(json.dumps(progress),flush=True)
            last_report=elapsed
wheel=root/'pyrosetta-2026.29+releasequarterly.80a0635615-cp312-cp312-macosx_12_0_arm64.whl'
h=hashlib.sha256()
with wheel.open('wb') as w:
    for i in range((size+chunk-1)//chunk):
        data=(root/f'part_{i:04d}').read_bytes()
        w.write(data);h.update(data)
with zipfile.ZipFile(wheel) as z:
    bad=z.testzip()
assert bad is None, bad
(root/'download_manifest.json').write_text(json.dumps(dict(url=url,size_bytes=size,sha256=h.hexdigest(),zip_crc_verified=True),indent=2)+'\n')
print(json.dumps(dict(completed=True,wheel=str(wheel),sha256=h.hexdigest())),flush=True)
