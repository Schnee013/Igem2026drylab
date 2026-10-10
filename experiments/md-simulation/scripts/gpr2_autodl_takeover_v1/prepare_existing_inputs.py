#!/usr/bin/env python3
"""Materialize only missing input workspaces; no mdrun and no production release."""
import argparse,hashlib,importlib.util,json,os,re,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True

def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve()
 os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
 q=load(b/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py','q');_,core,_=q.load_validators(b);gmx=Path(core.VERIFIED_GMX)
 for case in ('raw_n84v_ascr3','raw_v368r_ascr18'):
  w=b/'runs'/case/'rep1_codex_v1';plan=core.verify_sources(b,case)
  if w.exists():
   core.require((w/'initial_complete.json').exists(),'Existing incomplete workspace; inspect before retry')
   continue
  core.materialize(b,w,plan);core.initialize(b,w,plan,gmx)
  print(case,'verified input and 125 ps preheat; NPT remains',flush=True)
 case='raw_n84v_ascr18';src=b/'compute/cases'/case;w=b/'runs'/case/'rep1_codex_v1'
 core.require(not w.exists(),'N84V production workspace already exists; inspect')
 manifest={v['path']:v for v in json.loads((b/'MANIFEST.json').read_text())['files']}
 files=[p for p in src.rglob('*') if p.is_file()]+[p for p in (b/'compute/forcefields/ascr18.ff').rglob('*') if p.is_file()]
 for p in files:
  entry=manifest[str(p.relative_to(b))];core.require(core.sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes'],'Source identity mismatch')
 meta=json.loads((src/'case.json').read_text());core.require(meta['historical_production_credit_ns']==0 and meta['allowed_old_checkpoint_continuation'] is False,'Not a zero-start branch')
 shutil.copytree(src/'prepared',w);shutil.copytree(b/'compute/forcefields/ascr18.ff',w/'ff')
 old=(w/'topol.top').read_text();new,n=re.subn(r'^#include "[^"\n]*forcefield\.itp"$','#include "ff/forcefield.itp"',old,flags=re.M);core.require(n==1,'Forcefield include ambiguous');(w/'topol.top').write_text(new)
 for p in (src/'zero_start_100ns').iterdir():shutil.copy2(p,w/p.name)
 core.command([gmx,'grompp','-f','em.mdp','-c','ionized.gro','-r','ionized.gro','-p','topol.top','-n','index.ndx','-o','em.audit.tpr','-po','em.audit.mdout.mdp','-pp','em.processed.top'],w/'em.audit.grompp.log',w)
 core.require(not re.search(r'WARNING\s+\d+|Fatal error',(w/'em.audit.grompp.log').read_text()),'Neutral topology preprocessing warning')
 t=core.command([gmx,'dump','-s','production.tpr'],w/'production.tpr.dump.txt',w)
 cp=core.command([gmx,'dump','-cp','npt05.cpt'],w/'npt05.cpt.dump.txt',w)
 for k,v in {'natoms':146032,'tinit':0,'init-step':0,'dt':.002,'nsteps':50000000,'nstxout-compressed':5000,'nstenergy':500,'nstlog':5000}.items():core.require(core.scalar(t,k)==v,'Production TPR mismatch: '+k)
 core.require(core.scalar(cp,'#atoms')==146032 and core.scalar(cp,'t')==2750,'Wrong prepared source')
 core.state_match(t,w/'npt05.gro');core.state_match(cp,w/'npt05.gro')
 for field,count in (('x',146032),('v',146032),('box',3)):
  x=core.dump_vectors(t,field,count);y=core.dump_vectors(cp,field,count)
  core.require(all(abs(a-b)<=1e-7+1e-5*max(abs(a),abs(b)) for u,v in zip(x,y) for a,b in zip(u,v)),'TPR/CPT state mismatch: '+field)
 core.snapshot(b,w,'npt05')
 d=core.mdp((w/'production.mdp').read_text());back=core.mdp((w/'production_mdout.mdp').read_text());core.require(all(core.same_mdp_value(back.get(k,''),v) for k,v in d.items()),'Production mdout differs')
 core.require(not re.search(r'^\s*\[\s*(position_restraints|dihedral_restraints)\s*\]',(w/'production_processed.top').read_text(),re.M),'Production restraints present')
 report={'case_id':case,'source_purpose':'Own raw AF3 and own ascr18 pose, exploratory comparison; no E2 trajectory credit','source_preparation_ps':2750,'production_clock_ps':[0,100000],'preparation_evidence':json.loads((src/'evidence/npt05_summary.json').read_text()),'structure':json.loads((w/'npt05.structure.json').read_text()),'production_tpr_sha256':core.sha(w/'production.tpr'),'source_sha256':{str(p.relative_to(b)):core.sha(p) for p in files},'forcefield_include_rewrite_only':True,'production_ready':False,'remaining':'Own A-runtime new-start and checkpoint restart; fresh production evidence gate'}
 core.write(w/'source_preflight.json',report);print(case,'zero-clock source state and structure verified; own restart remains',flush=True)
if __name__=='__main__':main()
