#!/usr/bin/env python3
"""Seven bounded WT performance probes; never count probes as production."""
import argparse,fcntl,hashlib,importlib.util,json,math,os,re,shutil,signal,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
 t=Path(str(p)+'.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def mod(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def stop(procs):
 for p in procs:
  if p.poll() is None:p.send_signal(signal.SIGTERM)
 deadline=time.monotonic()+30
 while any(p.poll() is None for p in procs) and time.monotonic()<deadline:time.sleep(1)
 for p in procs:
  if p.poll() is None:p.kill()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();records=b/'operator_records/codex_takeover_v1';out=b/'operator_records/performance_windows_v1';out.mkdir(exist_ok=False)
 lock=(b/'operator_records/codex_scheduler.lock').open('a')
 save(out/'status.json',{'state':'WAITING_VALIDATED_PRODUCTION_BOUNDARY','at':now()})
 fcntl.flock(lock,fcntl.LOCK_EX)
 serial=(b/'operator_records/equilibration_prep_v2_2_2/serial.lock').open('a');fcntl.flock(serial,fcntl.LOCK_EX|fcntl.LOCK_NB)
 status=json.loads((records/'controller_status.json').read_text());need(status['state']=='VALIDATED_BOUNDARY_PAUSED_DISPATCH','Controller did not pause at accepted boundary')
 work=b/'runs/native_wt_ascr18/rep1_npt01_attempt02';c=mod(records/'wt_controller_v1_5.py','ctl');q=mod(b/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py','q');_,core,_=q.load_validators(b);gmx=core.VERIFIED_GMX
 latest=sorted(records.glob('segment_*/closed_segment.json'))[-1];accepted=json.loads(latest.read_text());need(sha(work/'native_wt_ascr18_rep1_production.cpt')==accepted['checkpoint']['sha256'],'Not a consistent accepted production CPT')
 shutil.copy2(work/'production.tpr',out/'production.tpr');shutil.copy2(accepted['checkpoint']['path'],out/'start.cpt')
 source={'tpr_sha256':sha(out/'production.tpr'),'checkpoint_sha256':sha(out/'start.cpt'),'source_closed_manifest':str(latest),'source_closed_manifest_sha256':sha(latest),'start_ps':accepted['end_ps'],'production_credit_ns':0}
 save(out/'source.json',source)
 # Visible cgroup allocation is a time quota, not exclusive ownership of cores.
 cpuinfo=subprocess.check_output(['lscpu','-p=CPU,CORE,SOCKET,NODE'],text=True);(out/'lscpu.txt').write_text(cpuinfo)
 topo=subprocess.check_output(['nvidia-smi','topo','-m'],text=True);(out/'gpu_topology.txt').write_text(topo)
 allowed=os.sched_getaffinity(0);cores=[];seen=set()
 for l in cpuinfo.splitlines():
  if l.startswith('#'):continue
  cpu,coreid,socket,node=map(int,l.split(','))
  if cpu in allowed and node==1 and (socket,coreid) not in seen:cores.append(cpu);seen.add((socket,coreid))
 need(len(cores)>=12 and re.search(r'GPU0.*\b1\s+N/A',topo),'Current GPU NUMA relation differs; review before pinning')
 quota=Path('/sys/fs/cgroup/cpu.max').read_text().split();need(quota[0]=='max' or int(quota[0])/int(quota[1])>=14,'Insufficient visible CPU quota')
 save(out/'resources.json',{'at':now(),'cpus_selected':cores[:12],'allowed':sorted(allowed),'cpu_max':quota,'cpu_stat':Path('/sys/fs/cgroup/cpu.stat').read_text(),'independent_physical_cores_verified':True})
 tpr=(b/'operator_records/wt_production_start_restart_20261006T0400Z/production_tpr_dump.stdout.txt').read_text()
 start_clock=time.monotonic();deadline=start_clock+3600;results=[];allprocs=[];mps=False
 envbase=dict(os.environ,OPENBLAS_NUM_THREADS='1');mpsenv={};pin=lambda ids:'{'+','.join(map(str,ids))+'}'
 def window(name,threads,nstlist,bound,mps_on=False,repeat_of=None):
  nonlocal allprocs
  need(time.monotonic()+470<deadline,'Insufficient time for a full stable window; no extension')
  d=out/name;d.mkdir();procs=[];handles=[];samples=[];beg=time.monotonic();cpu_start=Path('/sys/fs/cgroup/cpu.stat').read_text()
  for i in range(len(bound)):
   w=d/f'worker{i+1}';w.mkdir();shutil.copy2(out/'production.tpr',w/'production.tpr');shutil.copy2(out/'start.cpt',w/'input.cpt')
   env=dict(envbase,OMP_NUM_THREADS=str(threads));env.update(mpsenv if mps_on else {})
   for k in ('OMP_PLACES','OMP_PROC_BIND','CUDA_MPS_ACTIVE_THREAD_PERCENTAGE','GMX_CUDA_GRAPH'):env.pop(k,None)
   if bound[i]:env.update(OMP_PLACES=','.join('{'+str(x)+'}' for x in bound[i]),OMP_PROC_BIND='close')
   cmd=[gmx,'mdrun','-s','production.tpr','-cpi','input.cpt','-noappend','-deffnm','probe','-cpo','probe.cpt','-ntomp',str(threads),'-pin','off','-notunepme','-nb','gpu','-pme','gpu','-bonded','gpu','-update','gpu','-nstlist',str(nstlist),'-nsteps','5000000','-maxh','.119','-cpt','2']
   save(w/'command.json',{'argv':cmd,'env_overrides':{k:env.get(k) for k in ('OMP_NUM_THREADS','OMP_PLACES','OMP_PROC_BIND','CUDA_MPS_PIPE_DIRECTORY')},'input':source,'started_at':now()})
   f=(w/'console.txt').open('x');handles.append(f);p=subprocess.Popen(cmd,cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT);procs.append(p);allprocs=procs
  save(out/'status.json',{'state':'PERFORMANCE_WINDOW','window':name,'at':now(),'pids':[p.pid for p in procs],'elapsed_seconds':time.monotonic()-start_clock})
  mps_clients=False
  while any(p.poll() is None for p in procs):
   elapsed=time.monotonic()-beg;point={'elapsed':elapsed,'wall':now(),'steps':[],'affinity':[]}
   need(time.monotonic()<deadline-30,'Hard 60 minute deadline approaching')
   for i,p in enumerate(procs):
    w=d/f'worker{i+1}';logs=list(w.glob('probe*.log'));text=logs[0].read_text() if len(logs)==1 else '';console=(w/'console.txt').read_text();core.issue_scan(text+'\n'+console,name)
    steps=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+([-+\d.eE]+)',text);point['steps'].append(float(steps[-1][1]) if steps else None)
    if steps:
     need('Using '+str(threads)+' OpenMP threads' in text,'Thread count differs')
     need('Reading checkpoint file' in text and 'input.cpt' in text,'Probe did not read own isolated source CPT')
    aff=[]
    for task in Path(f'/proc/{p.pid}/task').glob('*'):
     try:aff.append({'tid':int(task.name),'cpus':sorted(os.sched_getaffinity(int(task.name)))})
     except ProcessLookupError:pass
    point['affinity'].append(aff)
    if bound[i] and elapsed>30 and p.poll() is None:
     singleton={tuple(x['cpus']) for x in aff if len(x['cpus'])==1}
     need(len(singleton)>=threads and all(x[0] in bound[i] for x in singleton),'OpenMP physical-core binding not realized')
   point['gpu']=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,power.draw,clocks.sm,memory.used','--format=csv,noheader'],text=True,capture_output=True,timeout=10).stdout.strip()
   point['cpu_stat']=Path('/sys/fs/cgroup/cpu.stat').read_text()
   if mps_on and elapsed>30 and not mps_clients:
    servers=subprocess.run(['nvidia-cuda-mps-control'],input='get_server_list\n',text=True,capture_output=True,env=dict(envbase,**mpsenv),timeout=10)
    ids=re.findall(r'^\s*(\d+)\s*$',servers.stdout,re.M);clients=''
    for sid in ids:clients+=subprocess.run(['nvidia-cuda-mps-control'],input='get_client_list '+sid+'\n',text=True,capture_output=True,env=dict(envbase,**mpsenv),timeout=10).stdout
    (d/'mps_clients.txt').write_text(servers.stdout+'\n'+clients);need(all(re.search(r'\b'+str(p.pid)+r'\b',clients) for p in procs),'MPS clients not confirmed');mps_clients=True
   with (d/'samples.jsonl').open('a') as f:f.write(json.dumps(point)+'\n')
   if elapsed>=60 and all(x is not None for x in point['steps']) and all(p.poll() is None for p in procs):samples.append(point)
   need(elapsed<480,'Window exceeded bounded maxh allowance')
   time.sleep(5)
  for f in handles:f.close()
  need(all(p.returncode==0 for p in procs),'Probe exited abnormally')
  need(len(samples)>2 and samples[-1]['elapsed']-samples[0]['elapsed']>=300,'Less than 5 minutes common stable time')
  sec=samples[-1]['elapsed']-samples[0]['elapsed'];speeds=[(v-u)/1000/sec*86400 for u,v in zip(samples[0]['steps'],samples[-1]['steps'])]
  # Split common window measures within-window variability without inventing replicas.
  mid=samples[len(samples)//2];half=[]
  for u,v in ((samples[0],mid),(mid,samples[-1])):half.append(sum(y-x for x,y in zip(u['steps'],v['steps']))/1000/(v['elapsed']-u['elapsed'])*86400)
  validations=[]
  for i in range(len(procs)):
   w=d/f'worker{i+1}';log=list(w.glob('probe*.log'))[0];txt=log.read_text();core.issue_scan(txt,name);need('Finished mdrun' in txt,'Probe lacked normal closure')
   # Reuse production checks while explicitly accommodating the tested thread count.
   if threads==8:core.runtime_parameters_check(tpr,txt)
   else:
    keys=('fourier-nx','fourier-ny','fourier-nz','pme-order','ewald-rtol','rcoulomb')
    need(all(core.scalar(tpr,k)==core.scalar(txt,k) for k in keys),'Probe PME parameters differ')
    for literal in ('-notunepme','Using 1 MPI process','Using 6 OpenMP threads','PP task will update and constrain coordinates on the GPU','PME tasks will do all aspects on the GPU','Using GPU 8x4 nonbonded short-range kernels','PP tasks will do (non-perturbed) short-ranged and most bonded interactions on the GPU'):
     need(literal in txt,'Six-thread runtime changed: '+literal)
    need(not re.search(r'PME tuning|timed with pme grid|Optimal PME grid',txt,re.I),'Unexpected PME tuning')
    widths=re.findall(r'Using a Gaussian width \(1/beta\) of ([-+\d.eE]+) nm for Ewald',txt)
    need(len(widths)==1 and abs(float(widths[0])-.384195)<=.000001,'Probe inverse beta changed')
   ec=c.command([gmx,'dump','-cp',w/'probe.cpt'],w,'checkpoint')[0];end=core.scalar(ec,'t');need(end>source['start_ps'] and core.scalar(ec,'#atoms')==145776,'Invalid probe checkpoint')
   c.command([gmx,'energy','-f',list(w.glob('probe*.edr'))[0],'-o',w/'thermo.xvg'],w,'energy','\n'.join(core.THERMO)+'\n0\n')
   raw=(w/'thermo.xvg').read_text();rows=[list(map(float,l.split())) for l in raw.splitlines() if l.strip() and not l.lstrip().startswith(('#','@'))];need(all(len(r)==11 and all(math.isfinite(x) for x in r) for r in rows),'Invalid probe energies')
   reg=[r for r in rows if abs(r[0]-round(r[0]))<.001];clean='\n'.join([l for l in raw.splitlines() if l.lstrip().startswith(('#','@'))]+[' '.join(map(str,r)) for r in reg]);thermo=core.thermo_report(clean,reg[0][0],reg[-1][0])
   validations.append({'checkpoint_sha256':sha(w/'probe.cpt'),'end_ps':end,'thermo':thermo,'actual_neighbor_lines':core.active_list_lines(txt)})
  need(sha(out/'production.tpr')==source['tpr_sha256'] and sha(out/'start.cpt')==source['checkpoint_sha256'],'Common source changed')
  r={'window':name,'threads_per_worker':threads,'nstlist_requested':nstlist,'bound_cores':bound,'mps':mps_on,'mps_clients_confirmed':mps_clients,'common_seconds':sec,'per_worker_ns_day':speeds,'aggregate_ns_day':sum(speeds),'half_window_aggregate_ns_day':half,'repeat_of':repeat_of,'validations':validations,'cpu_stat_before':cpu_start,'finished_at':now(),'production_credit_ns':0,'candidate_qualified_for_production':False}
  save(d/'result.json',r);results.append(r);save(out/'results.json',results);return r
 try:
  r1=window('01_single_100',8,100,[None]);r2=window('02_single_200',8,200,[None]);best=max((r1,r2),key=lambda r:r['aggregate_ns_day']);ns=best['nstlist_requested']
  r3=window('03_single_affinity',8,ns,[cores[:8]]);best=max((best,r3),key=lambda r:r['aggregate_ns_day']);r4=window('04_single_repeat',8,best['nstlist_requested'],best['bound_cores'],repeat_of=best['window']);ns=best['nstlist_requested']
  r5=window('05_dual_plain',6,ns,[cores[:6],cores[6:12]])
  pipe=out/'mps_pipe';logs=out/'mps_logs';pipe.mkdir(mode=0o700);logs.mkdir(mode=0o700);mpsenv={'CUDA_MPS_PIPE_DIRECTORY':str(pipe),'CUDA_MPS_LOG_DIRECTORY':str(logs),'CUDA_VISIBLE_DEVICES':'0'}
  mp=subprocess.run(['nvidia-cuda-mps-control','-d'],env=dict(envbase,**mpsenv),text=True,capture_output=True,timeout=10);(out/'mps_start.txt').write_text(mp.stdout+'\n'+mp.stderr)
  if mp.returncode==0:
   mps=True;r6=window('06_dual_mps',6,ns,[cores[:6],cores[6:12]],True)
   candidate=max((r5,r6),key=lambda r:r['aggregate_ns_day'])
  else:candidate=r5;save(out/'mps_unavailable.json',{'returncode':mp.returncode,'message':mp.stderr})
  if candidate['aggregate_ns_day']>=1.05*min(best['aggregate_ns_day'],r4['aggregate_ns_day']):window('07_dual_repeat',6,ns,[cores[:6],cores[6:12]],candidate['mps'],candidate['window'])
  save(out/'status.json',{'state':'WINDOWS_COMPLETE_QUALIFICATION_PENDING','at':now(),'elapsed_seconds':time.monotonic()-start_clock,'elapsed_cost_yuan':(time.monotonic()-start_clock)*2.88/3600,'decision':'Keep verified production baseline pending correctness and restart qualification; probes not production'})
 except Exception as exc:
  stop(allprocs);save(out/'status.json',{'state':'STOPPED_REVIEW_REQUIRED','at':now(),'error':str(exc),'elapsed_seconds':time.monotonic()-start_clock})
 finally:
  stop(allprocs)
  if mps:subprocess.run(['nvidia-cuda-mps-control'],input='quit\n',text=True,capture_output=True,env=dict(envbase,**mpsenv),timeout=10)
  need(sha(out/'production.tpr')==source['tpr_sha256'] and sha(out/'start.cpt')==source['checkpoint_sha256'],'Source changed; do not resume')
  (records/'pause_dispatch').unlink(missing_ok=True)
  fcntl.flock(serial,fcntl.LOCK_UN);fcntl.flock(lock,fcntl.LOCK_UN)
  with (out/'production_resume.console.txt').open('x') as f:
   p=subprocess.Popen([sys.executable,'-E',str(records/'wt_controller_v1_5.py'),'--bundle',str(b),'--records',str(records),'--receipt',str(records/'INITIAL_RECOVERY_RECEIPT.json'),'--execute'],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=envbase)
  save(out/'production_resume.json',{'at':now(),'controller_pid':p.pid,'configuration':'original verified baseline; no automatic candidate adoption'})
if __name__=='__main__':main()
