#!/usr/bin/env python3
"""Own-candidate parameterization and neutral input assembly, no MD."""
import argparse,hashlib,importlib.util,json,os,pty,re,select,shutil,subprocess,sys,time
from pathlib import Path

def need(ok,message):
 if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--case',required=True);a=ap.parse_args();b=a.bundle.resolve();src=b/'compute/cases'/a.case
 need(a.case in ('v368r_ascr3_lid_rebuilt_own_pose_v1','native_wt_ascr3_lid_rebuilt_own_pose_v1'),'Wrong own-lid case')
 meta=json.loads((src/'case.json').read_text());ev=json.loads((src/'evidence/candidate_manifest.json').read_text());candidate=src/meta['candidate_receptor']
 need(meta['new_lid'] and not meta['allowed_old_checkpoint_continuation'],'Invalid branch')
 need(sha(candidate)==ev['receptor_sha256'] and sha(src/'pose.sdf')==ev['ligand_sha256'] and ev['geometric_screen']['geometric_screen_pass'],'Static own-source review changed')
 rec=b/'operator_records/new_lid_inputs_v1'/a.case;rec.mkdir(parents=True,exist_ok=False)
 shutil.copytree(b/'compute/forcefields/ascr3.ff',rec/'ascr3.ff')
 source=candidate.read_text();lines=[]
 for l in source.splitlines():
  if l.startswith(('ATOM  ','HETATM')) and l[17:20]=='HIS':l=l[:17]+'HSD'+l[20:]
  lines.append(l)
 (rec/'candidate_hsd.pdb').write_text('\n'.join(lines)+'\n')
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1');gmx='/opt/drylab/gromacs-2025.4/bin.AVX2_256/gmx_mpi'
 need(sha(Path(gmx))=='90a2a9be92d37b236e0772a91df7eef1ac7fe24c4522d2994f6519f6835f6bd7','Actual A binary changed')
 cmd=[gmx,'pdb2gmx','-f','candidate_hsd.pdb','-o','protein.gro','-p','protein.top','-ff','ascr3','-water','tip3p','-ignh','-ter']
 master,slave=pty.openpty();p=subprocess.Popen(cmd,cwd=rec,stdin=slave,stdout=slave,stderr=slave,env=env);os.close(slave)
 transcript='';selections=[];start=time.monotonic();handled=set()
 with (rec/'pdb2gmx.console.txt').open('x') as log:
  try:
   while p.poll() is None:
    need(time.monotonic()-start<60,'pdb2gmx interactive timeout; preserve transcript')
    ready,_,_=select.select([master],[],[],.25)
    if ready:
     try:chunk=os.read(master,65536).decode(errors='replace')
     except OSError:break
     transcript+=chunk;log.write(chunk);log.flush()
    for kind,label in (('start','NH3+'),('end','COO-')):
     if kind in handled:continue
     matches=list(re.finditer(r'Select '+kind+r' terminus type.*?(?:\n|\r)',transcript,re.I))
     if not matches:continue
     tail=transcript[matches[-1].end():]
     choices=re.findall(r'^\s*(\d+)\s*:\s*(\S.*?)\s*$',tail,re.M)
     pick=[i for i,x in choices if x.strip()==label]
     # Wait for the full terminal menu to be emitted, then select by its label.
     if len(pick)==1 and 'None' in tail:
      os.write(master,(pick[0]+'\n').encode());selections.append({'menu':kind,'label':label,'actual_menu_number':int(pick[0]),'menu_text':tail});handled.add(kind)
   rc=p.wait(timeout=10);need(rc==0 and handled=={'start','end'},'pdb2gmx failed or terminal choices not verified')
  finally:
   if p.poll() is None:p.terminate();p.wait(timeout=10)
   os.close(master)
 (rec/'selections.json').write_text(json.dumps({'argv':cmd,'selections':selections,'only_residue_name_mapping':'HIS -> HSD, same neutral delta tautomer as original PROA','candidate_sha256':sha(candidate)},indent=2)+'\n')
 work=b/'runs'/a.case/'rep1_codex_v1'
 def run(args,name,stdin=None,cwd=rec,allow_failure=False):
  with (rec/(name+'.stdout.txt')).open('x') as so,(rec/(name+'.stderr.txt')).open('x') as se:r=subprocess.run(list(map(str,args)),input=stdin,text=True,cwd=cwd,env=env,stdout=so,stderr=se,timeout=180)
  need(allow_failure or r.returncode==0,name+' failed; inspect evidence');return r.returncode
 run([sys.executable,'-E',b/'compute/scripts/assemble_new_lid_dry.py','--case-dir',src,'--protein-gro',rec/'protein.gro','--protein-top',rec/'protein.top','--output',work],'assembly')
 helper=b/'compute/scripts/twf154_preheat_support.py'
 run([sys.executable,'-E',helper,'setup'],'mdp_setup',cwd=work)
 run([gmx,'solvate','-cp','dry.gro','-cs','spc216.gro','-o','solvated.gro','-p','topol.top'],'solvate',cwd=work)
 # Helper expects the original log location, without suppressing grompp diagnostics.
 cmd=[gmx,'grompp','-f','genion.mdp','-c','solvated.gro','-p','topol.top','-o','genion.tpr']
 with (work/'genion.grompp.log').open('x') as f:r=subprocess.run(cmd,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 if r.returncode:
  run([sys.executable,'-E',helper,'warning_gate'],'preion_warning_gate',cwd=work)
  run(cmd+['-maxwarn','1'],'accepted_preion_compilation',cwd=work)
 run([sys.executable,'-E',helper,'ions'],'ion_counts',cwd=work)
 counts=json.loads((work/'ion_counts.json').read_text())
 run([gmx,'genion','-s','genion.tpr','-o','ionized.gro','-p','topol.top','-pname','POT','-nname','CLA','-np',counts['POT'],'-nn',counts['CLA'],'-seed','8428368'],'genion','SOL\n',work)
 run([sys.executable,'-E',helper,'index'],'index',cwd=work)
 run([gmx,'grompp','-f','em.mdp','-c','ionized.gro','-r','ionized.gro','-p','topol.top','-n','index.ndx','-o','em.tpr','-po','em.mdout.mdp','-pp','em.processed.top'],'em_compile',cwd=work)
 text=(rec/'em_compile.stdout.txt').read_text()+(rec/'em_compile.stderr.txt').read_text();need(not re.search(r'WARNING\s+\d+|Fatal error',text),'Neutral EM compilation warning')
 (work/'new_input_ready.json').write_text(json.dumps({'case_id':a.case,'candidate_sha256':sha(candidate),'own_pose_sha256':sha(src/'pose.sdf'),'assembly':json.loads((work/'assembly_check.json').read_text()),'atom_count':int((work/'ionized.gro').read_text().splitlines()[1]),'em_tpr_sha256':sha(work/'em.tpr'),'preparation_ready':False,'production_ready':False,'next':'Own full-system EM with original force/geometry gate, heat, hold and NPT; never old raw CPT'},indent=2)+'\n')
 print(a.case,'own neutral EM input compiled; no MD started')
if __name__=='__main__':main()
