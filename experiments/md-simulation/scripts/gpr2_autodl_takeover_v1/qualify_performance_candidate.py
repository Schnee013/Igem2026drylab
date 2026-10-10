#!/usr/bin/env python3
"""Use remaining 60-minute window for same-state force and own-CPT checks."""
import argparse,fcntl,hashlib,importlib.util,json,math,os,re,shutil,signal,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone

def mod(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
 t=Path(str(p)+'.tmp');t.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n');t.replace(p)
def now():return datetime.now(timezone.utc).isoformat()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();code=b/'operator_records/codex_takeover_v1';perf=b/'operator_records/performance_windows_v1';out=b/'operator_records/performance_candidate_qualification_v1';out.mkdir(exist_ok=False)
 first=json.loads((perf/'01_single_100/worker1/command.json').read_text())
 deadline=datetime.fromisoformat(first['started_at']).timestamp()+3600
 lock=(b/'operator_records/codex_scheduler.lock').open('a');have=False
 save(out/'status.json',{'state':'WAITING_PERFORMANCE_WINDOWS','deadline_utc':datetime.fromtimestamp(deadline,timezone.utc).isoformat()})
 # The waiting successor may acquire the same mutex between probes and formal dispatch.
 # If a healthy production worker wins it, do not interrupt it for qualification.
 while time.time()<deadline-180:
  state=json.loads((perf/'status.json').read_text())['state']
  if state in ('WINDOWS_COMPLETE_QUALIFICATION_PENDING','STOPPED_REVIEW_REQUIRED'):
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);have=True;break
   except BlockingIOError:pass
  time.sleep(.1)
 if not have:
  save(out/'status.json',{'state':'NOT_QUALIFIED_TIME_OR_HEALTHY_PRODUCTION_LOCK','at':now(),'decision':'keep original verified production configuration'});return
 serial=(b/'operator_records/equilibration_prep_v2_2_2/serial.lock').open('a');fcntl.flock(serial,fcntl.LOCK_EX|fcntl.LOCK_NB)
 procs=[];mps=False;envbase=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1');mpsenv={}
 try:
  need(not any(p.read_bytes().split(b'\0')[1:2]==[b'mdrun'] for p in Path('/proc').glob('[0-9]*/cmdline') if p.exists()),'Active mdrun; do not compete')
  results=json.loads((perf/'results.json').read_text());by={r['window']:r for r in results};pairs=[]
  for r in results:
   if r['repeat_of']:
    original=by[r['repeat_of']];low=min(r['aggregate_ns_day'],original['aggregate_ns_day']);pairs.append((low,r,original))
  need(pairs,'No repeated candidate')
  baseline=by['01_single_100']['aggregate_ns_day'];low,candidate,original=max(pairs,key=lambda x:x[0])
  need(low>=1.05*baseline,'Repeated gain does not meet approximately 5% adoption screen')
  if len(candidate['bound_cores'])==2:
   singles=[r['aggregate_ns_day'] for r in results if len(r['bound_cores'])==1]
   need(low>=1.05*max(singles),'Concurrency advantage does not exceed single-window variation plus 5%')
  save(out/'candidate.json',{'candidate':candidate['window'],'repeat_of':candidate['repeat_of'],'conservative_aggregate_ns_day':low,'comparison_baseline':baseline,'same_input_probe_only':True})
  source=json.loads((perf/'source.json').read_text());work=b/'runs/native_wt_ascr18/rep1_npt01_attempt02';gmx='/opt/drylab/gromacs-2025.4/bin.AVX2_256/gmx_mpi'
  need(sha(Path(gmx))=='90a2a9be92d37b236e0772a91df7eef1ac7fe24c4522d2994f6519f6835f6bd7','Pinned A changed')
  need(sha(perf/'production.tpr')==source['tpr_sha256'] and sha(perf/'start.cpt')==source['checkpoint_sha256'],'Common probe input changed')
  q=mod(b/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py','q');_,core,_=q.load_validators(b)
  need(sha(b/'operator_records/multiframe_probe_v3.py')=='620d94739eea4ba710eb9a326e231fd5fc37dbd1b5630cde1b445d8c30e16ce9','Existing TRR parser identity changed')
  old=mod(b/'operator_records/multiframe_probe_v3.py','existing_trr_helpers')
  def run(cmd,name,cwd=out,stdin=None,env=envbase):
   need(time.time()<deadline-45,'Qualification deadline approaching')
   with (out/(name+'.stdout.txt')).open('x') as so,(out/(name+'.stderr.txt')).open('x') as se:
    p=subprocess.Popen(list(map(str,cmd)),cwd=cwd,env=env,stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,stdout=so,stderr=se);procs.append(p)
    try:p.communicate(stdin.encode() if stdin else None,timeout=max(1,min(90,deadline-time.time()-30)))
    except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=10);raise
   need(p.returncode==0,name+' failed')
   text=(out/(name+'.stdout.txt')).read_text();err=(out/(name+'.stderr.txt')).read_text();core.issue_scan(text+'\n'+err,name);return text,err
  cp=run([gmx,'dump','-cp',perf/'start.cpt'],'source_cpt')[0];nt=145776;xyz=core.dump_vectors(cp,'x',nt);vel=core.dump_vectors(cp,'v',nt);box=core.dump_vectors(cp,'box',3)
  ident=(work/'npt05.gro').read_text().splitlines();gro=out/'source.gro'
  with gro.open('x') as f:
   f.write('Accepted production CPT text view, diagnostics only\n145776\n')
   for line,x,v in zip(ident[2:-1],xyz,vel):f.write(line[:20]+''.join(f'{z:8.3f}' for z in x)+''.join(f'{z:8.4f}' for z in v)+'\n')
   f.write(''.join(f'{box[i][i]:10.5f}' for i in range(3))+'\n')
  orig=(b/'operator_records/wt_production_start_restart_20261006T0400Z/production_tpr_dump.stdout.txt').read_text()
  changes={'nsteps':'0','nstxout':'1','nstvout':'1','nstfout':'1','nstenergy':'1','nstcalcenergy':'1','nstlog':'1','ld-seed':str(int(core.scalar(orig,'ld-seed')))}
  for axis in 'xyz':changes['fourier-n'+axis]=str(int(core.scalar(orig,'fourier-n'+axis)))
  (out/'zero.mdp').write_text(old.amend_mdp((work/'production.mdp').read_text(),changes))
  text,err=run([gmx,'grompp','-f',out/'zero.mdp','-c',gro,'-t',perf/'start.cpt','-p',work/'production.processed.top','-n',work/'index.ndx','-o',out/'zero.tpr','-po',out/'zero.mdout.mdp'],'zero_compile')
  need(not re.search(r'WARNING\s+\d+',text+err),'Diagnostic compilation warning')
  zero=run([gmx,'dump','-s',out/'zero.tpr'],'zero_dump')[0]
  def science(text):
   s=q.scientific_prefix(text)
   return '\n'.join(l for l in s.splitlines() if not any(re.match(r'^\s*'+k+r'\s*=',l) for k in ('nstxout','nstvout','nstfout','nstenergy','nstcalcenergy','nstlog')))
  need(science(zero)==science(orig),'Diagnostic topology/force/coupling changed')
  for field,count in (('x',nt),('v',nt),('box',3)):
   x=core.dump_vectors(zero,field,count);y=core.dump_vectors(cp,field,count);need(all(abs(a-b)<=1e-7+1e-5*max(abs(a),abs(b)) for u,v in zip(x,y) for a,b in zip(u,v)),'Diagnostic state differs: '+field)
  common=[gmx,'mdrun','-pin','off','-notunepme','-nb','gpu','-pme','gpu','-bonded','gpu','-update','gpu','-cpt','1','-maxh','.02']
  run([*common,'-s',out/'zero.tpr','-deffnm','baseline_zero','-ntomp','8','-nstlist','100'],'baseline_zero',env=dict(envbase,OMP_NUM_THREADS='8'))
  if candidate['mps']:
   (out/'mps_pipe').mkdir(mode=0o700);(out/'mps_logs').mkdir(mode=0o700);mpsenv={'CUDA_MPS_PIPE_DIRECTORY':str(out/'mps_pipe'),'CUDA_MPS_LOG_DIRECTORY':str(out/'mps_logs'),'CUDA_VISIBLE_DEVICES':'0'}
   run(['nvidia-cuda-mps-control','-d'],'mps_start',env=dict(envbase,**mpsenv));mps=True
  configs=[]
  for i,ids in enumerate(candidate['bound_cores']):
   env=dict(envbase,OMP_NUM_THREADS=str(candidate['threads_per_worker']),**mpsenv)
   if ids:env.update(OMP_PLACES=','.join('{'+str(x)+'}' for x in ids),OMP_PROC_BIND='close')
   configs.append(env)
  # Same-state force comparison on each candidate worker; no scientific trajectory credit.
  ref=list(old.trr_frames(out/'baseline_zero.trr',nt));need(len(ref)==1,'Expected one zero-step reference force frame')
  comparisons=[]
  info=json.loads((work/'input_contract.json').read_text());cfg=json.loads((b/'compute/configs/ligand_geometry_contract.json').read_text())[info['pose_mapping']];groups={'system':(0,nt),'protein':(0,info['atoms']),'ligand':(info['atoms'],info['atoms']+len(cfg['atom_names']))}
  for i,env in enumerate(configs):
   name=f'candidate{i+1}_zero';run([*common,'-s',out/'zero.tpr','-deffnm',name,'-ntomp',candidate['threads_per_worker'],'-nstlist',candidate['nstlist_requested']],name,env=env)
   fr=list(old.trr_frames(out/(name+'.trr'),nt));need(len(fr)==1,'Expected one candidate force frame');comparisons.append(old.force_compare(ref[0],fr[0],groups))
   run([gmx,'energy','-f',out/(name+'.edr'),'-o',out/(name+'.energy.xvg'),'-dp'],name+'_energy',stdin='Potential\nPressure\nTemperature\n0\n')
  run([gmx,'energy','-f',out/'baseline_zero.edr','-o',out/'baseline_zero.energy.xvg','-dp'],'baseline_energy',stdin='Potential\nPressure\nTemperature\n0\n')
  save(out/'same_state_force_comparisons.json',comparisons)
  # Reuse the previously reviewed cross-backend force-difference scale as a conservative
  # empirical comparison; do not label this a universal physical accuracy tolerance.
  numeric=json.loads((b/'operator_records/equilibration_prep_v2_3/numerical_preparation_qualification_v3.json').read_text())
  forcepath=b/'operator_records/multiframe_v3_20261006T000827Z_59280_58e06be2/force_comparisons.json'
  need(sha(forcepath)==numeric['evidence']['force_comparisons.json']['sha256'],'Historical force evidence changed')
  historical=json.loads(forcepath.read_text())
  def rels(x):
   if isinstance(x,dict):
    for k,v in x.items():
     if k=='relative_rms' and isinstance(v,(int,float)):yield v
     else:yield from rels(v)
   elif isinstance(x,list):
    for v in x:yield from rels(v)
  scale=max(rels(historical));need(all(v<=scale for c in comparisons for v in rels(c)),'Candidate force discrepancy exceeds existing reviewed empirical range; no adoption')
  endstep=round(source['start_ps']/.002)+15000
  run([gmx,'convert-tpr','-s',perf/'production.tpr','-nsteps',endstep,'-o',out/'restart_test.tpr'],'restart_tpr')
  dump=run([gmx,'dump','-s',out/'restart_test.tpr'],'restart_tpr_dump')[0];need(q.normalized_dump(orig)==q.normalized_dump(dump),'Restart diagnostic changed more than length')
  own=[]
  for phase in ('first','restart'):
   active=[]
   for i,env in enumerate(configs):
    name=f'worker{i+1}_{phase}';args=[*common,'-s',out/'restart_test.tpr','-deffnm',name,'-cpo',name+'.cpt','-ntomp',candidate['threads_per_worker'],'-nstlist',candidate['nstlist_requested'],'-noappend','-cpi',perf/'start.cpt' if phase=='first' else out/f'worker{i+1}_first.cpt']
    if phase=='first':args+=['-nsteps','10000']
    f=(out/(name+'.console.txt')).open('x');p=subprocess.Popen(list(map(str,args)),cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT);procs.append(p);active.append((name,p,f))
   observed_clients=not mps;phase_start=time.monotonic()
   while any(p.poll() is None for _,p,_ in active):
    need(time.time()<deadline-30,'Hard performance qualification deadline')
    for name,p,f in active:core.issue_scan((out/(name+'.console.txt')).read_text(),name)
    if mps and not observed_clients and time.monotonic()-phase_start>2:
     e=dict(envbase,**mpsenv);servers=subprocess.run(['nvidia-cuda-mps-control'],input='get_server_list\n',text=True,capture_output=True,env=e,timeout=5).stdout;clients=''
     for sid in re.findall(r'^\s*(\d+)\s*$',servers,re.M):clients+=subprocess.run(['nvidia-cuda-mps-control'],input='get_client_list '+sid+'\n',text=True,capture_output=True,env=e,timeout=5).stdout
     (out/(phase+'_mps_clients.txt')).write_text(servers+'\n'+clients);observed_clients=all(re.search(r'\b'+str(p.pid)+r'\b',clients) for _,p,_ in active)
    time.sleep(.2)
   need(observed_clients,'Own restart workers not observed as MPS clients')
   for name,p,f in active:
    f.close();need(p.returncode==0,name+' restart test failed');log=list(out.glob(name+'*.log'));need(len(log)==1 and 'Finished mdrun' in log[0].read_text(),'Own restart closure missing')
    runtime=old.offload_evidence(log[0].read_text(),True,True,candidate['threads_per_worker']);cp2=run([gmx,'dump','-cp',out/(name+'.cpt')],name+'_cpt')[0]
    target=source['start_ps']+(20 if phase=='first' else 30);need(abs(core.scalar(cp2,'t')-target)<.001 and core.scalar(cp2,'#atoms')==nt,'Own candidate restart endpoint wrong')
    if phase=='restart':
     coords=core.dump_vectors(cp2,'x',nt);vs=core.dump_vectors(cp2,'v',nt);bx=core.dump_vectors(cp2,'box',3);snapshot=out/(name+'.gro')
     need(all(abs(bx[u][v])<1e-8 for u in range(3) for v in range(3) if u!=v),'Unexpected box shear')
     with snapshot.open('x') as f:
      f.write('Candidate CPT validation view; never restart input\n145776\n')
      for line,x,v in zip(ident[2:-1],coords,vs):f.write(line[:20]+''.join(f'{z:8.3f}' for z in x)+''.join(f'{z:8.4f}' for z in v)+'\n')
      f.write(''.join(f'{bx[u][u]:10.5f}' for u in range(3))+'\n')
     run([sys.executable,'-E',b/'compute/scripts/check_twf154_snapshot.py',work,snapshot,b/'compute/configs/ligand_geometry_contract.json',out/(name+'.structure.json'),'--allow-box-change'],name+'_structure')
     need(json.loads((out/(name+'.structure.json')).read_text())['pass'] is True,'Candidate own restart structure failed')
    own.append({'worker_phase':name,'end_ps':target,'runtime':runtime,'checkpoint_sha256':sha(out/(name+'.cpt'))})
  save(out/'qualification.json',{'status':'OWN_WT_FORCE_AND_CPT_RESTART_PASSED','at':now(),'candidate':candidate['window'],'force_comparisons':comparisons,'empirical_reference_max_relative_rms':scale,'own_restarts':own,'same_input_probe_only':True,'production_credit_ns':0,'formal_concurrency_authorized_now':False,'reason':'Only WT has production release; second real case requires own preparation/restart/production review and real-pair throughput confirmation. Keep single WT baseline until those pass.','elapsed_from_first_window_seconds':time.time()-(deadline-3600)})
  save(out/'status.json',{'state':'QUALIFICATION_COMPLETE_WT_PROBE_ONLY','at':now()})
 except Exception as exc:save(out/'status.json',{'state':'NOT_QUALIFIED','at':now(),'error':str(exc),'decision':'keep original verified production configuration'})
 finally:
  for p in procs:
   if p.poll() is None:p.terminate()
  for p in procs:
   if p.poll() is None:
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:p.kill()
  if mps:subprocess.run(['nvidia-cuda-mps-control'],input='quit\n',text=True,capture_output=True,env=dict(envbase,**mpsenv),timeout=10)
  fcntl.flock(serial,fcntl.LOCK_UN);fcntl.flock(lock,fcntl.LOCK_UN)
  # If the original resume already acquired the mutex, leave it healthy.
  try:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_UN)
   with (out/'production_resume.console.txt').open('x') as f:p=subprocess.Popen([sys.executable,'-E',str(code/'wt_controller_v1_5.py'),'--bundle',str(b),'--records',str(code),'--receipt',str(code/'INITIAL_RECOVERY_RECEIPT.json'),'--execute'],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env=envbase)
   save(out/'production_resume.json',{'at':now(),'controller_pid':p.pid,'configuration':'original validated single WT baseline'})
  except BlockingIOError:save(out/'production_resume.json',{'at':now(),'action':'existing healthy scheduler retained'})
if __name__=='__main__':main()
