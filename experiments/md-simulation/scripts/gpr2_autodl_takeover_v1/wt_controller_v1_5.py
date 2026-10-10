#!/usr/bin/env python3
"""Continue the accepted WT rep1 using frozen validators and finite production parts."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
CASE = 'native_wt_ascr18'
PREFIX = CASE + '_rep1_production'
NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
CHECKS = ['source_identity','structure_purpose','preparation','numerical_compatibility','restart_test','resources','storage_and_recovery']

def now(): return datetime.now(timezone.utc).isoformat()
def require(ok, message):
    if not ok: raise RuntimeError(message)
def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def read(path): return json.loads(Path(path).read_text())
def save(path,value):
    with Path(path).open('x') as f: json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def current(path,value):
    tmp=Path(str(path)+'.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');tmp.replace(path)
def ref(path): return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def event(work,state,detail,source):
    p=work/'run_state_events.tsv'
    with p.open('a') as f:
        if p.stat().st_size==0:f.write('observed_at\tstate\tsource\tdetail\n')
        f.write(f'{now()}\t{state}\t{source}\t{detail}\n')

def command(argv,out,name,stdin=None):
    argv=list(map(str,argv));save(out/(name+'.command.json'),{'argv':argv,'started_at':now()})
    with (out/(name+'.stdout.txt')).open('x') as so,(out/(name+'.stderr.txt')).open('x') as se:
        r=subprocess.run(argv,input=stdin,text=True,stdout=so,stderr=se,timeout=180,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    require(r.returncode==0,f'{name} failed: {r.returncode}')
    return (out/(name+'.stdout.txt')).read_text(),(out/(name+'.stderr.txt')).read_text()

def initial_review(bundle,work,out,q,core,receipt):
    plan=q.validate_inputs(bundle,work,core)
    probe=bundle/'operator_records/wt_production_start_restart_20261006T0400Z'
    result=read(probe/'qualification_result.json')
    require(result['status']=='PASS_NEW_START_AND_CPT_RESTART_ONLY' and result['restart_test'] is True,'Own restart not accepted')
    for name,digest in result['evidence_sha256'].items():require(sha(probe/name)==digest,'Changed own restart evidence: '+name)
    require(result['production_tpr_sha256']==sha(work/'production.tpr'),'Production TPR differs from tested start')
    require(result['source_npt05_cpt_sha256']==sha(work/'npt05.cpt'),'Prepared source state changed')
    cp=(probe/'npt05_checkpoint_dump.stdout.txt').read_text();tpr=(probe/'production_tpr_dump.stdout.txt').read_text()
    state=q.verify_production_tpr(core,tpr,cp,work)
    nr=read(bundle/'operator_records/equilibration_prep_v2_3/numerical_preparation_qualification_v3.json')
    require(nr['reviewed_numeric_findings']['hard_runtime_anomalies_found']==[],'Existing numerical review contains unresolved hard runtime anomaly')
    backup=read(receipt);require(backup['off_instance'] is True and len(backup['archives'])==2,'Off-instance receipt missing')
    for a in backup['archives']:require(a['zip_crc_all_members_pass'] and sha(a['remote_path'])==a['sha256'],'Recovery archive identity changed')
    preparation=read(work/'npt05.validated.json');structure=read(work/'npt05.structure.json')
    require(preparation['box_density_settled'] is True and structure['pass'] is True,'Own final preparation failed')
    report={'case_id':CASE,'reviewed_at':now(),'accepted_for':'Bounded 100 ns rep1 exploratory production with periodic structural and thermodynamic checks',
      'preparation':preparation['half_window_fractional_change'],'structure':structure,'production_state_match':state,
      'numerical_synthesis':{'decision':'ACCEPT_THIS_WT_PRODUCTION_RUNTIME',
        'basis':['Existing matched-frame CPU/thread/GPU force and initial virial evidence supports the selected A algorithm path; large absolute potential differences are thread-dependent energy accumulation, not a claim of interchangeable absolute energies.',
                 'All five own WT stages pass the original runtime, structural, endpoint and thermal checks; unrestrained final 500 ps density/XY/Z drift is below the original 2% screen.',
                 'WT production topology and force/coupling settings match its accepted unrestrained NPT05; only the original new-stage clock/length/seed and recorded compiler-derived settings differ.',
                 'Own unchanged-start 20 ps run and CPT continuation to 30 ps pass; seam coordinates, box and temperatures agree; observed potential/pressure differences remain explicitly recorded.'],
        'existing_numeric_observations':nr['reviewed_numeric_findings'],
        'own_restart_seam':result['thermo_restart_minus_original_at_20ps'],
        'limitations':['No universal numerical tolerance, NVE conservation, bitwise trajectory identity or convergence claim.','Do not compare absolute potential values across CPU/GPU/thread paths as binding energies.','Acceptance applies only to this WT input and pinned runtime; other cases need their own preparation/source/restart evidence.']},
      'source_limitations':['Independent WT AF3 mother and own pose; preserve discrete W174 repair branch.','Single replicate and unequal input treatments support exploratory description, not isolated mutation causality.'],
      'evidence':[ref(work/'npt05.validated.json'),ref(work/'npt05.structure.json'),ref(probe/'qualification_result.json'),ref(receipt)],
      'production_tpr_sha256':sha(work/'production.tpr'),'preparation_source_sha256':plan['source_sha256']}
    save(out/'initial_review.json',report)
    return out/'initial_review.json'

def validate_closed(bundle,work,out,core,gmx,start,tpr,old_logs):
    logs=[p for p in work.glob(PREFIX+'*.log') if str(p) not in old_logs]
    require(len(logs)==1,'Ambiguous new closed production log')
    log=logs[0];stem=log.with_suffix('');text=log.read_text();core.issue_scan(text,'Production log')
    require('Finished mdrun' in text,'Production did not close normally')
    core.runtime_parameters_check(tpr,text)
    cpt=work/(PREFIX+'.cpt');cp,_=command([gmx,'dump','-cp',cpt],out,'checkpoint')
    end=core.scalar(cp,'t');step=int(core.scalar(cp,'step'))
    require(core.scalar(cp,'#atoms')==145776 and start<end<=100000 and abs(end-.002*step)<.001,'Invalid or nonadvancing production CPT')
    times=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+('+NUMBER+')',text)
    require(times and int(times[-1][0])==step and abs(float(times[-1][1])-end)<.001,'Final log/CPT clocks differ')
    gro=Path(str(log)[:-4]+'.gro')
    if not gro.exists():
        # maxh closure can save a complete CPT without emitting a final GRO.
        # This text snapshot is solely for structure checking; continuation uses CPT.
        gro=out/'checkpoint_snapshot.gro'
        source=(work/'npt05.gro').read_text().splitlines()
        require(int(source[1])==145776 and len(source)==145779,'Reference atom identities incomplete')
        xyz=core.dump_vectors(cp,'x',145776);vel=core.dump_vectors(cp,'v',145776);box=core.dump_vectors(cp,'box',3)
        require(all(abs(box[i][j])<1e-8 for i in range(3) for j in range(3) if i!=j),'Unexpected box shear')
        with gro.open('x') as f:
            f.write(f'CPT-derived validation snapshot t={end}; never used to restart\n145776\n')
            for line,x,v in zip(source[2:-1],xyz,vel):f.write(line[:20]+''.join(f'{a:8.3f}' for a in x)+''.join(f'{a:8.4f}' for a in v)+'\n')
            f.write(''.join(f'{box[i][i]:10.5f}' for i in range(3))+'\n')
        save(out/'snapshot_provenance.json',{'source_checkpoint':ref(cpt),'identity_reference':ref(work/'npt05.gro'),'derived_snapshot':ref(gro),'purpose':'Text-precision structure validation only; native CPT remains sole restart state'})
    core.state_match(cp,gro)
    xtc=Path(str(log)[:-4]+'.xtc');edr=Path(str(log)[:-4]+'.edr')
    xt='\n'.join(command([gmx,'check','-f',xtc],out,'xtc_check'));core.issue_scan(xt,'XTC')
    frames=re.findall(r'(?:Reading|Last)\s+frame\s+(\d+)\s+time\s+('+NUMBER+')',xt)
    require(frames,'No XTC frames')
    summaries=re.findall(r'^\s*Time\s+(\d+)\s+('+NUMBER+r')\s*$',xt,re.M)
    require(len(summaries)==1 and abs(float(summaries[0][1])-10)<.001,'Missing or invalid full-file XTC count/cadence')
    count=int(summaries[0][0]);first=float(frames[0][1]);last=first+(count-1)*10
    require(int(frames[0][0])==0 and all(0<=int(i)<count for i,t in frames),'Invalid XTC progress indices')
    require(start-.001<=first<=start+10.001 and end-10.001<=last<=end+.001,'XTC saving-grid coverage incomplete')
    require(abs(first/10-round(first/10))<.0001 and abs(last/10-round(last/10))<.0001,'XTC off original 10 ps grid')
    require(count==round((last-first)/10)+1 and all(abs(float(t)-first-10*int(i))<.001 for i,t in frames),'XTC cadence or count gap')
    for key in ('Step','Time','Coords','Box'):
        rows=re.findall(r'^\s*'+key+r'\s+(\d+)\s+('+NUMBER+r')\s*$',xt,re.M)
        require(len(rows)==1 and int(rows[0][0])==count and abs(float(rows[0][1])-10)<.001,'XTC summary mismatch: '+key)
    require(re.search(r'#\s*Atoms\s+145776\b',xt) and not re.search(r'WARNING|Incomplete|Timesteps at',xt,re.I),'XTC integrity issue')
    ec='\n'.join(command([gmx,'check','-e',edr],out,'edr_check'));core.issue_scan(ec,'EDR')
    require(not re.search(r'WARNING|Incomplete',ec,re.I),'EDR integrity issue')
    command([gmx,'energy','-f',edr,'-o',out/'thermo.xvg'],out,'energy','\n'.join(core.THERMO)+'\n0\n')
    raw=(out/'thermo.xvg').read_text();rows=[list(map(float,l.split())) for l in raw.splitlines() if l.strip() and not l.lstrip().startswith(('#','@'))]
    require(rows and start-.001<=rows[0][0]<=start+1.001 and end-1.001<=rows[-1][0]<=end+.001,'EDR grid coverage incomplete')
    require(all(len(r)==11 and all(math.isfinite(v) for v in r) for r in rows),'Incomplete/nonfinite EDR values')
    require(all(a[0]<b[0] for a,b in zip(rows,rows[1:])),'EDR time reversal/duplicates')
    offgrid=[r for r in rows if abs(r[0]-round(r[0]))>.001]
    require(all(abs(r[0]-start)<.001 or abs(r[0]-end)<.001 for r in offgrid),'EDR interior off-grid frame')
    regular=[r for r in rows if abs(r[0]-round(r[0]))<=.001]
    require(regular and abs(regular[0][0]-math.ceil(start-.001))<.001 and abs(regular[-1][0]-math.floor(end+.001))<.001,'Incomplete EDR original saving grid')
    irregular=[(a[0],b[0]-a[0]) for a,b in zip(rows,rows[1:]) if abs(b[0]-a[0]-1)>.001]
    require(all(0<d<1 and (abs(t-start)<.001 or abs(t+d-end)<.001) for t,d in irregular),'EDR interior cadence change')
    notes=re.findall(r"Timesteps at t=("+NUMBER+r") don't match \(("+NUMBER+r"), ("+NUMBER+r")\)",ec)
    require(len(notes)==len(irregular) and all(any(abs(float(t)-x)<.001 and abs(float(v)-d)<.001 for x,d in irregular) for t,u,v in notes),'EDR checker message not explained by exact segment boundary')
    regular_text='\n'.join([l for l in raw.splitlines() if l.lstrip().startswith(('#','@'))]+[' '.join(map(str,r)) for r in regular])
    thermo=core.thermo_report(regular_text,regular[0][0],regular[-1][0])
    thermo['boundary_energy_times_ps']=[r[0] for r in offgrid]
    thermo['finite_rows_including_boundary']=len(rows)
    command([sys.executable,'-E',bundle/'compute/scripts/check_twf154_snapshot.py',work,gro,bundle/'compute/configs/ligand_geometry_contract.json',out/'structure.json','--allow-box-change'],out,'structure')
    require(read(out/'structure.json')['pass'] is True,'Closed production structure failed')
    checkpoint=out/'boundary.cpt';shutil.copy2(cpt,checkpoint);require(sha(checkpoint)==sha(cpt),'Checkpoint changed after closure')
    result={'case_id':CASE,'validated_at':now(),'start_ps':start,'end_ps':end,'step':step,'trajectory':{'first_ps':first,'last_ps':last,'frames':count},'thermo':thermo,'pass':True,'checkpoint':ref(checkpoint),'files':[ref(p) for p in (log,gro,xtc,edr,checkpoint)],'production_tpr_sha256':sha(work/'production.tpr')}
    save(out/'closed_segment.json',result);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--records',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--execute',action='store_true');a=ap.parse_args()
    require(__debug__,'Do not disable validation with optimized Python')
    bundle=a.bundle.resolve();records=a.records.resolve();records.mkdir(parents=True,exist_ok=True)
    lock=(bundle/'operator_records/codex_scheduler.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    work=bundle/'runs/native_wt_ascr18/rep1_npt01_attempt02'
    owner={'pid':os.getpid(),'started_at':now(),'authorization':'User confirmed old operator stopped and no other timers on 2026-10-06; six rep1 x100ns authorized','case':CASE}
    current(records/'controller_status.json',dict(owner,state='REVIEWING'))
    q=module(bundle/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py','existing_qualifier')
    addon,core,code=q.load_validators(bundle);gmx=Path(core.VERIFIED_GMX)
    initial=records/'initial_review.json'
    if not initial.exists():initial=initial_review(bundle,work,records,q,core,a.receipt)
    review=read(initial);require(review['production_tpr_sha256']==sha(work/'production.tpr'),'Reviewed production TPR changed')
    if not a.execute:print(json.dumps({'review':str(initial),'production_started':False}));return
    child=None
    def stop(signum,frame):
        if child is not None and child.poll() is None:child.send_signal(signal.SIGTERM)
        raise RuntimeError('Controller stop requested; child asked to stop gracefully')
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    closed=sorted(records.glob('segment_*/closed_segment.json'));start=read(closed[-1])['end_ps'] if closed else 0.
    if not closed:require(not list(work.glob(PREFIX+'*.log')),'Existing unvalidated production outputs; inspect before restart')
    try:
        while start<100000:
            if (records/'pause_dispatch').exists():
                current(records/'controller_status.json',dict(owner,state='VALIDATED_BOUNDARY_PAUSED_DISPATCH',production_ps=start,reason=(records/'pause_dispatch').read_text()))
                return
            n=len(closed)+1;out=records/f'segment_{n:03d}';out.mkdir(exist_ok=False)
            _,numeric,live=addon.fresh_resources(core,code,bundle,out);save(out/'live_preflight.json',live)
            require(shutil.disk_usage(bundle).free>6e9,'Insufficient next-segment and recovery reserve')
            gate={'case_id':CASE,'replicate':1,'production_ns':100,'tpr_sha256':sha(work/'production.tpr'),'live_verified_at':live['utc'],'checks':{k:True for k in CHECKS},'evidence':{},'continuation_checkpoint':None}
            # The true values above are emitted only after the complete review, source hashes,
            # own restart evidence and fresh resource checks have succeeded.
            for k in CHECKS:gate['evidence'][k]=[ref(initial)]
            gate['evidence']['resources']=[ref(out/'live_preflight.json')]
            gate['evidence']['storage_and_recovery']=[ref(a.receipt),ref(out/'live_preflight.json')]
            gate['evidence']['numerical_compatibility'] += [ref(p) for p in numeric]
            if start:
                previous=read(closed[-1]);cp=work/(PREFIX+'.cpt')
                require(sha(cp)==previous['checkpoint']['sha256'],'Current CPT differs from validated boundary')
                gate['continuation_checkpoint']={**ref(cp),'step':previous['step'],'time_ps':start}
                gate['evidence']['restart_test'].append(ref(closed[-1]))
            save(out/'production_gate.json',gate)
            old_logs={str(p) for p in work.glob(PREFIX+'*.log')}
            cmd=[sys.executable,'-E',str(bundle/'operator_records/codex_takeover_v1/run_stage_production_v1_1.py'),'--case',CASE,'--stage','production','--workdir',str(work),'--tpr',str(work/'production.tpr'),'--prefix',PREFIX,'--gmx',str(gmx),'--threads','8','--offload','gpu','--maxh',str(.20 if n==1 else (.10 if n==3 else 1)),'--expected-end-ps','100000','--min-free-gb','5','--gate',str(out/'production_gate.json')]
            if start:cmd+=['--cpi',str(work/(PREFIX+'.cpt'))]
            current(records/'controller_status.json',dict(owner,state='SUPERVISING',segment=n,start_ps=start,gate=str(out/'production_gate.json')))
            with (out/'supervisor.console.txt').open('x') as f:
                child=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_NUM_THREADS='8',OPENBLAS_NUM_THREADS='1'))
                rc=child.wait()
            require(rc==0,'Segment supervisor failed; no automatic abnormal retry')
            tpr=(bundle/'operator_records/wt_production_start_restart_20261006T0400Z/production_tpr_dump.stdout.txt').read_text()
            result=validate_closed(bundle,work,out,core,gmx,start,tpr,old_logs)
            require(abs(result['start_ps']-start)<.001,'Segment continuity failed')
            closed.append(out/'closed_segment.json');start=result['end_ps']
            with (records/'closed_segments.jsonl').open('a') as f:f.write(json.dumps({'manifest':str(closed[-1]),'sha256':sha(closed[-1]),'end_ps':start})+'\n')
            event(work,'TERMINAL_NORMAL',f'Validated closed segment {n}; production_ps={start}; external recovery pending',str(closed[-1]))
        current(records/'controller_status.json',dict(owner,state='100NS_REACHED_RECOVERY_PENDING',production_ps=start,closed_segments=len(closed)))
    except Exception as exc:
        current(records/'controller_status.json',dict(owner,state='HOLD',error=str(exc),production_ps=start))
        event(work,'TERMINAL_ABNORMAL',str(exc),str(records/'controller_status.json'));raise

if __name__=='__main__':main()
