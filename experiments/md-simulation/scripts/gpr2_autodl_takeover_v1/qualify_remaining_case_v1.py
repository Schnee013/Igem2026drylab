#!/usr/bin/env python3
"""Own remaining-case six-thread force, new-start and native restart qualification; zero formal credit."""
import argparse,fcntl,json,math,os,re,shutil,subprocess,sys,time
from pathlib import Path
import remaining_runtime_v1 as d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--case',choices=list(d.CASES),required=True);ap.add_argument('--slot',type=int,choices=[0,1],required=True);a=ap.parse_args();b=a.bundle.resolve();code=b/'operator_records/codex_takeover_v1';out=b/d.CASES[a.case]['qualifier'];created=False
 q,(addon,core,oldcode)=d.load_core(b);six=d.SixCore(core);procs=[];locks=[];beg=time.monotonic()
 try:
  for p in (b/'operator_records/codex_scheduler.lock',b/'operator_records/equilibration_prep_v2_2_2/serial.lock'):
   f=p.open('a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  w=b/d.CASES[a.case]['work'];done=d.read(w/'preparation_complete.json')
  d.need(done['case_id']==a.case and done['preparation_pass'] and done['final_time_ps']==2750,'Own preparation incomplete')
  d.need((w/'source_preflight.json').is_file() and (w/'production.tpr').is_file(),'Own compiled production missing')
  out.mkdir(exist_ok=False);created=True
  d.save(out/'live_preflight.json',d.live(b))
  d.need(d.sha(b/'operator_records/multiframe_probe_v3.py')=='620d94739eea4ba710eb9a326e231fd5fc37dbd1b5630cde1b445d8c30e16ce9','Original TRR helper changed')
  helper=d.module(b/'operator_records/multiframe_probe_v3.py','trr_helper');nr=d.read(oldcode/'numerical_preparation_qualification_v3.json')
  historic=b/'operator_records/multiframe_v3_20261006T000827Z_59280_58e06be2/force_comparisons.json';d.need(d.sha(historic)==nr['evidence']['force_comparisons.json']['sha256'],'Reviewed force reference changed')
  def values(x):
   if isinstance(x,dict):
    for k,v in x.items():
     if k=='relative_rms' and isinstance(v,(int,float)):yield v
     else:yield from values(v)
   elif isinstance(x,list):
    for v in x:yield from values(v)
  force_scale=max(values(d.read(historic)));potential_scale=max(abs(x) for x in nr['reviewed_numeric_findings']['cpu8_minus_cpu4_potential_kj_mol_at_0_10_20ps'])
  cases=[]
  def run(args,work,name,stdin=None,env=None):
   d.need(time.monotonic()-beg<1500,'Qualification exceeded25min; no unbounded retries')
   with (work/(name+'.stdout.txt')).open('x') as so,(work/(name+'.stderr.txt')).open('x') as se:
    p=subprocess.Popen(list(map(str,args)),cwd=work,env=env or dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'),stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,stdout=so,stderr=se);procs.append(p)
    try:p.communicate(stdin.encode() if stdin else None,timeout=120)
    except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=15);raise
   d.need(p.returncode==0,name+' failed');stdout=(work/(name+'.stdout.txt')).read_text();stderr=(work/(name+'.stderr.txt')).read_text();core.issue_scan(stdout+'\n'+stderr,name);return stdout
  for slot,case in [(a.slot,a.case)]:
   cfg=d.CASES[case];w=b/cfg['work'];z=out/'probe';z.mkdir();c=d.case_validator(case)
   review=d.read(w/'source_preflight.json');done=d.read(w/'preparation_complete.json')
   d.need(review['case_id']==case and review['production_tpr_sha256']==d.sha(w/'production.tpr'),'Own compiled production identity differs')
   d.need(done['case_id']==case and done['preparation_pass'] and done['final_time_ps']==2750 and review['preparation_evidence']['box_density_settled'] and review['structure']['pass'],'Own preparation/source purpose not accepted')
   for name,h in review['source_sha256'].items():d.need(d.sha(b/name)==h,'Own accepted preparation evidence changed')
   d.need(not list(w.glob(case+'_rep1_production*.log')),'Formal production exists; inspect and continue it instead of probing again')
   d.need(d.sha(w/'production.mdp')=='c19c76f41c5cd0ef3523f438a5bb84927989b2e195271dcd2f6f8d7bd03e8d6f','Original production MDP changed')
   d.save(out/'source_review.json',{'source_preflight_sha256':d.sha(w/'source_preflight.json'),'preparation_complete_sha256':d.sha(w/'preparation_complete.json'),'case_id':case,'production_ready':False})
   # Hard links reuse immutable inputs and give the existing archiver real files.
   for name in ('npt05.gro','input_contract.json','ionized.gro','em.processed.top','production.tpr'):os.link(w/name,z/name)
   orig=run([d.GMX,'dump','-s',w/'production.tpr'],z,'production_dump');start=0.;cp=None
   for key,value in {'natoms':cfg['atoms'],'tinit':0,'init-step':0,'dt':.002,'nsteps':50000000,'nstxout-compressed':5000,'nstenergy':500,'nstlog':5000}.items():d.need(core.scalar(orig,key)==value,'Own production clock/atoms/output mismatch: '+key)
   run([d.GMX,'convert-tpr','-s',w/'production.tpr','-nsteps',round(start/.002)+20000,'-o',z/'smoke.tpr'],z,'length_only')
   smoke=run([d.GMX,'dump','-s',z/'smoke.tpr'],z,'smoke_dump');d.need(q.normalized_dump(smoke)==q.normalized_dump(orig),'Own diagnostic TPR changed beyond length')
   cases.append(dict(case=case,cfg=cfg,slot=slot,w=w,z=z,c=c,orig=orig,start=start,source=cp,checks=[]))
  def zero_test(item,source,label):
   z=item['z'];nt=item['cfg']['atoms'];state=run([d.GMX,'dump','-cp',source],z,label+'_cpt');x=core.dump_vectors(state,'x',nt);v=core.dump_vectors(state,'v',nt);box=core.dump_vectors(state,'box',3)
   gro=z/(label+'.gro');ident=(item['w']/'npt05.gro').read_text().splitlines();d.need(all(abs(box[i][j])<1e-8 for i in range(3) for j in range(3) if i!=j),'Diagnostic box shear')
   with gro.open('x') as f:
    f.write('Own complete CPT diagnostic text view\n'+str(nt)+'\n')
    for line,xx,vv in zip(ident[2:-1],x,v):f.write(line[:20]+''.join(f'{a:8.3f}' for a in xx)+''.join(f'{a:8.4f}' for a in vv)+'\n')
    f.write(''.join(f'{box[i][i]:10.5f}' for i in range(3))+'\n')
   orig=item['orig'];changes={'nsteps':'0','nstxout':'1','nstvout':'1','nstfout':'1','nstenergy':'1','nstcalcenergy':'1','nstlog':'1','ld-seed':str(int(core.scalar(orig,'ld-seed')))}
   for axis in 'xyz':changes['fourier-n'+axis]=str(int(core.scalar(orig,'fourier-n'+axis)))
   mdp=z/(label+'.mdp');mdp.write_text(helper.amend_mdp((item['w']/'production.mdp').read_text(),changes));top=item['w']/'production.processed.top'
   if not top.exists():top=item['w']/'production_processed.top'
   run([d.GMX,'grompp','-f',mdp,'-c',gro,'-t',source,'-p',top,'-n',item['w']/'index.ndx','-o',z/(label+'.tpr'),'-po',z/(label+'.mdout.mdp')],z,label+'_compile')
   diag=run([d.GMX,'dump','-s',z/(label+'.tpr')],z,label+'_dump')
   # Explicit identical PME dimensions cause grompp to store spacing0. Check the
   # actual dimensions, order, Ewald tolerance/cutoff and runtime beta separately.
   ignored=('nstxout','nstvout','nstfout','nstenergy','nstcalcenergy','nstlog','fourierspacing')
   def norm(t):return '\n'.join(l for l in q.scientific_prefix(t).splitlines() if not any(re.match(r'^\s*'+k+r'\s*=',l) for k in ignored))
   d.need(norm(diag)==norm(orig),'Own force/topology/coupling changed')
   for k in ('fourier-nx','fourier-ny','fourier-nz','pme-order','ewald-rtol','rcoulomb'):d.need(core.scalar(diag,k)==core.scalar(orig,k),'Actual PME differs: '+k)
   d.need(core.scalar(diag,'fourierspacing')==0 and core.scalar(orig,'fourierspacing')==.12,'Unexpected compiler-spacing representation')
   for field,count in (('x',nt),('v',nt),('box',3)):
    left=core.dump_vectors(diag,field,count);right=core.dump_vectors(state,field,count);d.need(all(abs(a-b)<=1e-7+1e-5*max(abs(a),abs(b)) for xx,yy in zip(left,right) for a,b in zip(xx,yy)),'Own state differs: '+field)
   common=[d.GMX,'mdrun','-s',z/(label+'.tpr'),'-pin','off','-notunepme','-nb','gpu','-pme','gpu','-bonded','gpu','-update','gpu','-maxh','.02']
   energies=[];frames=[]
   for backend,threads,nstlist,env in [('baseline',8,100,dict(os.environ,OMP_NUM_THREADS='8',OPENBLAS_NUM_THREADS='1')),('candidate',6,200,d.env(item['slot']))]:
    prefix=label+'_'+backend;run([*common,'-deffnm',prefix,'-ntomp',threads,'-nstlist',nstlist],z,prefix,env=env);log=(z/(prefix+'.log')).read_text()
    (core if threads==8 else six).runtime_parameters_check(orig,log)
    fr=list(helper.trr_frames(z/(prefix+'.trr'),nt));d.need(len(fr)==1,'Single diagnostic force frame required');frames.append(fr[0])
    run([d.GMX,'energy','-f',z/(prefix+'.edr'),'-o',z/(prefix+'.energy.xvg'),'-dp'],z,prefix+'_energy','Potential\nPressure\nTemperature\n0\n')
    rows=[list(map(float,l.split())) for l in (z/(prefix+'.energy.xvg')).read_text().splitlines() if l.strip() and not l.lstrip().startswith(('#','@'))];d.need(len(rows)==1 and all(math.isfinite(x) for x in rows[0]),'Nonfinite/ambiguous energy');legends={int(i):name for i,name in re.findall(r'@\s+s(\d+)\s+legend\s+"([^"]+)"',(z/(prefix+'.energy.xvg')).read_text())};d.need(set(legends)==set(range(3)) and set(legends.values())=={'Potential','Temperature','Pressure'},'Energy column identity missing');energies.append({legends[i]:rows[0][i+1] for i in range(3)})
   info=d.read(item['w']/'input_contract.json');lg=d.read(b/'compute/configs/ligand_geometry_contract.json')[info['pose_mapping']];groups={'system':(0,nt),'protein':(0,info['atoms']),'ligand':(info['atoms'],info['atoms']+len(lg['atom_names']))};comparison=helper.force_compare(frames[0],frames[1],groups);delta={name:energies[1][name]-energies[0][name] for name in energies[0]}
   d.save(z/(label+'.comparison.json'),{'force':comparison,'energy_names_from_xvg_legend':True,'candidate_minus_baseline':delta,'baseline':energies[0],'candidate':energies[1],'force_empirical_max':force_scale,'potential_empirical_max':potential_scale,'compiler_spacing_note':'Explicit identical PME grid stores spacing0; real dimensions/order/beta/tolerance and matched state separately verified'})
   d.need(all(v<=force_scale for v in values(comparison)),'Force difference outside prior reviewed empirical range');d.need(abs(delta['Potential'])<=potential_scale,'Potential discrepancy outside prior reviewed empirical range')
   item['checks'].append({'frame':label,'source_sha256':d.sha(source),'force':comparison,'energy_delta':delta})
  for item in cases:zero_test(item,item['source'] or item['w']/'npt05.cpt','start_state')
  for phase in ('first','restart'):
   active=[]
   for item in cases:
    z=item['z'];args=[d.GMX,'mdrun','-s',z/'smoke.tpr','-deffnm',phase,'-cpo',phase+'.cpt','-ntomp','6','-nstlist','200','-pin','off','-notunepme','-nb','gpu','-pme','gpu','-bonded','gpu','-update','gpu','-cpt','1','-maxh','.05']
    cp=item['source'] if phase=='first' else z/'first.cpt'
    if cp:args+=['-cpi',cp,'-noappend']
    if phase=='first':args+=['-nsteps','10000']
    f=(z/(phase+'.console.txt')).open('x');p=subprocess.Popen(list(map(str,args)),cwd=z,env=d.env(item['slot']),stdout=f,stderr=subprocess.STDOUT);procs.append(p);active.append((item,p,f))
   t=time.monotonic();bound=set()
   while any(p.poll() is None for _,p,_ in active):
    d.need(time.monotonic()-t<150,'Own simultaneous restart timeout')
    for item,p,f in active:
     core.issue_scan((item['z']/(phase+'.console.txt')).read_text(),phase)
     logs=list(item['z'].glob(phase+'*.log'));started=len(logs)==1 and re.search(r'Step\s+Time\s*\n\s*\d+',logs[0].read_text())
     if started and p.poll() is None and item['slot'] not in bound:d.save(item['z']/(phase+'.affinity.json'),d.affinity(p.pid,item['slot']));bound.add(item['slot'])
    time.sleep(.2)
   d.need(len(bound)==len(cases),'Actual own six-thread physical-core binding missing')
   for item,p,f in active:
    f.close();d.need(p.returncode==0,'Own simultaneous MD failed');z=item['z'];c=item['c'];c.PREFIX=phase;validation=z/('validation_'+phase);validation.mkdir()
    start=item['start']+(0 if phase=='first' else 20);accepted=c.validate_closed(b,z,validation,six,d.GMX,start,item['orig'],set())
    d.need(abs(accepted['end_ps']-(item['start']+(20 if phase=='first' else 40)))<.001,'Wrong own restart endpoint')
    if phase=='restart':
     text=next(z.glob('restart*.log')).read_text();d.need('Reading checkpoint file '+str(z/'first.cpt') in text,'Not own first checkpoint');d.need(d.sha(z/'first.cpt')==d.read(z/'validation_first/closed_segment.json')['checkpoint']['sha256'],'Restart source changed')
    item['checks'].append({'phase':phase,'end_ps':accepted['end_ps'],'validation_sha256':d.sha(validation/'closed_segment.json')})
  for item in cases:zero_test(item,item['z']/'restart.cpt','after_restart')
  evidence={str(p.relative_to(out)):d.sha(p) for p in sorted(out.rglob('*')) if p.is_file() and not p.is_symlink()}
  result={'status':'PASS_OWN_SIX_THREAD_FORCE_START_RESTART','finished_at':d.now(),'cases':{i['case']:{'production_tpr_sha256':d.sha(i['w']/'production.tpr'),'formal_source_start_ps':i['start'],'formal_source_cpt_sha256':d.sha(i['source']) if i['source'] else None,'checks':i['checks']} for i in cases},'configuration':{'threads_per_worker':6,'nstlist':200,'cores':d.CORES,'mps':False},'source_review_paths':[str(i['w']/'source_preflight.json') for i in cases], 'case_id':a.case, 'slot':a.slot, 'shared_parallel_basis':'Previously measured ordinary two-task GPU configuration; this own-case qualification establishes its independent force/runtime/start/restart. First formal dual segments still require actual runtime, structure and thermodynamic closure.','evidence_sha256':evidence,'production_credit_ns':0,'limits':'Empirical same-state force/energy scale and own source/restart checks; no NVE, absolute energy accuracy or long-time convergence claim.','elapsed_seconds':time.monotonic()-beg}
  d.save(out/'qualification.json',result);d.save(out/'status.json',{'state':'QUALIFIED','at':d.now()})
  archived=out/'segment_001';archived.mkdir();files=[p for p in out.rglob('*') if p.is_file() and p.suffix not in ('.pyc','.lock')]
  d.save(archived/'closed_segment.json',{'case_id':a.case,'stage':'own_six_thread_qualification','stage_kind':'qualification','production_credit_ns':0,'start_ps':0,'end_ps':40,'pass':True,'files':[{'path':str(p),'sha256':d.sha(p)} for p in files]})
  print(json.dumps({'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'case':a.case}))
 except Exception as exc:
  if created:d.save(out/'status.json',{'state':'HOLD','at':d.now(),'error':str(exc)})
  raise
 finally:
  for p in procs:
   if p.poll() is None:p.terminate()
  for p in procs:
   if p.poll() is None:
    try:p.wait(timeout=15)
    except subprocess.TimeoutExpired:p.kill()
  for f in locks:fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main()
