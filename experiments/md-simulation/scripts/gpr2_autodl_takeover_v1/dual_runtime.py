#!/usr/bin/env python3
"""Shared checks for the authorized two-worker, six-thread production configuration."""
import csv,fcntl,hashlib,importlib.util,json,math,os,re,shutil,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
GMX='/opt/drylab/gromacs-2025.4/bin.AVX2_256/gmx_mpi'
GMX_SHA='90a2a9be92d37b236e0772a91df7eef1ac7fe24c4522d2994f6519f6835f6bd7'
GPU='GPU-0d5d6691-0983-c849-a06a-f7e2dd9b526f'
CORES=[[52,53,54,55,56,57],[58,59,60,61,62,63]]
CASES={'native_wt_ascr18':{'work':'runs/native_wt_ascr18/rep1_npt01_attempt02','records':'operator_records/codex_takeover_v1','module':'wt_controller_v1_5.py','atoms':145776},'raw_n84v_ascr18':{'work':'runs/raw_n84v_ascr18/rep1_codex_v1','records':'operator_records/n84v_production_v1','module':'n84v_controller.py','atoms':146032}}
def now():return datetime.now(timezone.utc).isoformat()
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):
 p=Path(p);tmp=Path(str(p)+'.tmp');tmp.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');tmp.replace(p)
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def env(slot):return dict(os.environ,OMP_NUM_THREADS='6',OPENBLAS_NUM_THREADS='1',OMP_PLACES=','.join('{'+str(c)+'}' for c in CORES[slot]),OMP_PROC_BIND='close')
def load_core(b):
 q=module(b/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py','qualified_original');return q,q.load_validators(b)
class SixCore:
 def __init__(self,core):self.core=core
 def __getattr__(self,k):return getattr(self.core,k)
 def runtime_parameters_check(self,tpr,log):
  c=self.core;keys=('fourier-nx','fourier-ny','fourier-nz','pme-order','ewald-rtol','rcoulomb');expected={k:c.scalar(tpr,k) for k in keys}
  need(expected=={k:c.scalar(log,k) for k in keys},'Actual case PME/electrostatics differ')
  need(all(expected[k]>0 and expected[k].is_integer() for k in keys[:4]) and expected['rcoulomb']==1.2 and expected['ewald-rtol']==1e-5,'Original force settings differ')
  widths=re.findall(r'Using a Gaussian width \(1/beta\) of ([-+\d.eE]+) nm for Ewald',log);need(len(widths)==1 and abs(float(widths[0])-.384195)<.000001,'Ewald beta differs')
  for text in ('-notunepme','Using 1 MPI process','Using 6 OpenMP threads','PP task will update and constrain coordinates on the GPU','PME tasks will do all aspects on the GPU','Using GPU 8x4 nonbonded short-range kernels','PP tasks will do (non-perturbed) short-ranged and most bonded interactions on the GPU'):
   need(text in log,'Six-thread backend missing: '+text)
  need(not re.search(r'PME tuning|timed with pme grid|Optimal PME grid',log,re.I),'PME tuning forbidden')
  lines=[l.strip() for l in log.splitlines() if 'outer list:' in l];need(lines and all(re.search(r'updated every\s+200 steps',l) for l in lines),'Actual nstlist is not 200')
  return {'threads':6,'nstlist':200,'ranks':1,'pme_grid':[int(expected[k]) for k in keys[:3]],'pme_order':int(expected['pme-order']),'inverse_beta_nm':float(widths[0]),'offload':'NB/PME/bonded/update GPU, original CPU CMAP retained','pme_tuning':False,'active_neighbor_list_lines':lines}
def children(pid):
 result=set();todo=[pid]
 while todo:
  p=todo.pop()
  try:cs=list(map(int,Path(f'/proc/{p}/task/{p}/children').read_text().split()))
  except FileNotFoundError:continue
  result.update(cs);todo+=cs
 return result
def live(b,allowed_supervisors=()):
 need(sha(GMX)==GMX_SHA,'Pinned executable changed');allowed=set().union(*(children(p) for p in allowed_supervisors)) if allowed_supervisors else set();actual=[]
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try:cmd=p.read_bytes().split(b'\0')
  except (FileNotFoundError,ProcessLookupError):continue
  if len(cmd)>1 and cmd[1]==b'mdrun':
   pid=int(p.parent.name);need(pid in allowed and cmd[0].decode()==GMX,'Unowned MD process present');actual.append(pid)
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,driver_version,memory.total,memory.used','--format=csv,noheader,nounits'],text=True).strip();row=next(csv.reader([gpu]));need(row[0].strip()==GPU and 'RTX 5090' in row[1],'GPU identity changed')
 gpu_apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).strip();gpids=[int(x) for x in gpu_apps.splitlines() if x.strip()]
 # A sibling can start mdrun between the /proc scan and the GPU query. Bind a new
 # observed PID to its actual owned supervisor and command before accepting it.
 refreshed=set().union(*(children(p) for p in allowed_supervisors)) if allowed_supervisors else set()
 for pid in gpids:
  need(pid in allowed|refreshed,'Unowned GPU process present')
  try:cmd=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
  except FileNotFoundError:need(pid in actual,'Unknown exited GPU PID');continue
  need(cmd[0].decode()==GMX and cmd[1:2]==[b'mdrun'],'Owned GPU process has unexpected executable')
  if pid not in actual:actual.append(pid)
 quota=Path('/sys/fs/cgroup/cpu.max').read_text().split();need(quota[0]=='max' or int(quota[0])/int(quota[1])>=14,'CPU quota below14')
 mem=Path('/sys/fs/cgroup/memory.max').read_text().strip();need(mem=='max' or int(mem)>=32*1024**3,'Memory reserve below32GiB')
 need(set(sum(CORES,[]))<=os.sched_getaffinity(0),'Selected CPU affinity unavailable')
 topology=subprocess.check_output(['lscpu','-p=CPU,CORE,SOCKET,NODE'],text=True);top={int(x.split(',')[0]):tuple(map(int,x.split(',')[1:])) for x in topology.splitlines() if not x.startswith('#')};chosen=[top[x] for x in sum(CORES,[])];need(len(set((x[0],x[1]) for x in chosen))==12 and all(x[2]==1 for x in chosen),'Not12distinct NUMA1physical cores')
 free=shutil.disk_usage(b).free;need(free>=10_000_000_000,'Two-worker disk reserve below10GB')
 return {'utc':now(),'binary_sha256':sha(GMX),'gpu':gpu,'owned_mdruns':actual,'gpu_pids':gpids,'cpu_quota':quota,'physical_cores':CORES,'memory_limit':mem,'free_bytes':free,'pass':True}
def affinity(pid,slot):
 masks=[]
 for p in Path(f'/proc/{pid}/task').glob('*'):
  try:masks.append(sorted(os.sched_getaffinity(int(p.name))))
  except ProcessLookupError:pass
 single={m[0] for m in masks if len(m)==1};need(single==set(CORES[slot]),'Actual six-thread physical-core binding differs');return masks
