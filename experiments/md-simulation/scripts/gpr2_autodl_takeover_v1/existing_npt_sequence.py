#!/usr/bin/env python3
"""Validate and execute the missing original NPT stages of one existing preheat."""
import argparse,fcntl,importlib.util,json,os,sys
from pathlib import Path

def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--case',choices=['raw_n84v_ascr3','raw_v368r_ascr18'],required=True);ap.add_argument('--receipt',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();here=Path(__file__).resolve().parent
 os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
 d=module(here/'prepare_existing_npt.py','own_driver');q=module(b/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py','q');addon,core,code=q.load_validators(b)
 plan=d.verify_sources(b,a.case);w=b/'runs'/a.case/'rep1_codex_v1';initial=json.loads((w/'initial_complete.json').read_text());d.validate_manifest(w,initial['evidence_sha256'],core.INITIAL_EVIDENCE)
 recovery=json.loads(a.receipt.read_text());d.require(recovery['off_instance'] and recovery['frozen_bundle_all_files_match'] and recovery['manifest_sha256']==d.sha(b/'MANIFEST.json'),'Own frozen source not recoverable outside instance')
 nr=json.loads((b/'operator_records/equilibration_prep_v2_3/numerical_preparation_qualification_v3.json').read_text());d.require(a.case in nr['scope']['eligible_prepared_cases'],'Existing A-path preparation qualification does not include this case')
 d.require(json.loads((w/'start.structure.json').read_text())['pass'] is True,'Own initial structure failed')
 with (b/'operator_records/codex_scheduler.lock').open('a') as sched,(b/'operator_records/equilibration_prep_v2_2_2/serial.lock').open('a') as serial:
  fcntl.flock(sched,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(serial,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for stage,start,end in d.STAGES:
   if (w/(stage+'.validated.json')).exists():continue
   out=b/'operator_records'/('npt_'+a.case+'_v1')/stage;out.mkdir(parents=True,exist_ok=False)
   gmx,numeric,live=addon.fresh_resources(core,code,b,out)
   d.write(out/'live.json',live)
   facts={'case_id':a.case,'stage':stage,'source_sha256':plan['source_sha256'],'own_initial_structure_sha256':d.sha(w/'start.structure.json'),'initial_complete_sha256':d.sha(w/'initial_complete.json'),'numerical_scope':'Bounded own preparation on the existing qualified A path only; own runtime and end-state validation required. No production acceptance.','source_purpose':'Own full-length raw AF3 mother and own ligand pose; exploratory modeling, not causal or binding-energy proof','production_ready':False}
   if stage!='npt01':
    prior=d.previous_stage(stage);result=json.loads((w/(prior+'.validated.json')).read_text());d.require(result['pass_stage'] and result['case_id']==a.case and result['end_ps']==start,'Own predecessor mismatch');d.validate_manifest(w,result['output_sha256'],d.stage_output_names(prior));facts['previous_stage_sha256']=d.sha(w/(prior+'.validated.json'))
   d.write(out/'stage_review.json',facts)
   refs=lambda ps:[{'path':str(p),'sha256':d.sha(p)} for p in ps]
   evidence={k:refs([out/'stage_review.json']) for k in d.GATES};evidence['resources']=refs([out/'live.json']);evidence['numerical_compatibility']+=refs(numeric);evidence['storage_and_recovery']=refs([a.receipt,out/'live.json'])
   gate={'case_id':a.case,'replicate':1,'allowed_stages':[stage],'source_hold_cpt_sha256':plan['source_sha256'][f'compute/cases/{a.case}/prepared/hold.cpt'],'live_verified_at':live['utc'],'checks':{k:True for k in d.GATES},'evidence':evidence,'runtime':{'gmx_realpath':str(gmx),'gmx_sha256':d.sha(gmx),'offload':'gpu','threads':8,'pme_tuning':False,'pme_grid_policy':'case_original_grompp_grid'}}
   d.write(out/'stage_gate.json',gate)
   d.execute(b,w,plan,out/'stage_gate.json',gmx,.5,stage)
   accepted=json.loads((w/(stage+'.validated.json')).read_text())
   archive=out.parent/f'segment_{[n for n,_,_ in d.STAGES].index(stage)+1:03d}';archive.mkdir()
   files=[{'path':str(w/name),'sha256':digest} for name,digest in accepted['output_sha256'].items()]
   files+=[{'path':str(w/(stage+'.validated.json')),'sha256':d.sha(w/(stage+'.validated.json'))}]
   files+=[{'path':str(p),'sha256':d.sha(p)} for p in out.iterdir() if p.is_file()]
   d.write(archive/'closed_segment.json',{'case_id':a.case,'stage':stage,'stage_kind':'preparation','production_credit_ns':0,'start_ps':start,'end_ps':end,'pass':accepted['pass_stage'],'files':files,'checkpoint':{'path':str(w/(stage+'.cpt')),'sha256':d.sha(w/(stage+'.cpt'))},'source':'actual stage validation, not production progress'})
  last=json.loads((w/'npt05.validated.json').read_text());d.require(last['box_density_settled'],'Own final drift screen failed; review bounded extension before production')
  d.write(w/'preparation_complete.json',{'case_id':a.case,'replicate':1,'preparation_pass':True,'final_prefix':'npt05','final_time_ps':2750,'production_ready':False,'stage_evidence':{n:d.sha(w/(n+'.validated.json')) for n,_,_ in d.STAGES},'next':'Own production compile, start/restart and production review'})
 print(a.case,'all five original NPT stages accepted; production qualification remains')
if __name__=='__main__':main()
