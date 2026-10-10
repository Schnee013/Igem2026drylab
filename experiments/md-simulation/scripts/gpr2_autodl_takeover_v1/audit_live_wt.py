#!/usr/bin/env python3
"""Read-only checkpoint/energy/structure sample of the currently running WT part."""
import argparse,json,math,os,shutil,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
import importlib.util

def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);a=ap.parse_args();b=a.bundle.resolve();r=b/'operator_records/codex_takeover_v1';w=b/'runs/native_wt_ascr18/rep1_npt01_attempt02'
 os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
 c=module(r/'wt_controller_v1_5.py','controller');q=module(b/'operator_records/production_transition_plan_v1/qualify_wt_production_restart.py','q');_,core,_=q.load_validators(b);gmx=core.VERIFIED_GMX
 status=c.read(r/'controller_status.json');c.require(status['state']=='SUPERVISING','No active WT segment')
 live=c.read(w/'live_status.json');c.require(live['process_alive'] and live['issue'] is None,'Supervisor reports unhealthy process')
 cmd=Path(f"/proc/{live['pid']}/cmdline").read_bytes().split(b'\0');c.require(cmd[0].decode()==gmx and cmd[1]==b'mdrun','Actual process identity differs')
 observed=datetime.fromisoformat(live['observed_at']).timestamp();c.require(time.time()-observed<90,'Stale supervisor state')
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=r/f"segment_{status['segment']:03d}"/('live_audit_'+stamp);out.mkdir()
 try:
  source=w/'native_wt_ascr18_rep1_production.cpt';age=time.time()-source.stat().st_mtime;c.require(age<420,'Checkpoint older than seven minutes')
  cp=out/'captured.cpt';shutil.copy2(source,cp);c.require(c.sha(cp)==c.sha(source),'Checkpoint changed during copy; resample without modifying MD')
  text=c.command([gmx,'dump','-cp',cp],out,'checkpoint')[0];end=core.scalar(text,'t');step=core.scalar(text,'step');nt=145776
  c.require(core.scalar(text,'#atoms')==nt and abs(end-step*.002)<.001 and status['start_ps']<end<=100000,'Wrong or nonadvancing checkpoint')
  log=Path(live['log']);logtext=log.read_text();(out/'captured.log').write_text(logtext);core.issue_scan(logtext,'Live production log')
  original=(b/'operator_records/wt_production_start_restart_20261006T0400Z/production_tpr_dump.stdout.txt').read_text();core.runtime_parameters_check(original,logtext)
  c.require(c.sha(w/'production.tpr')==c.read(r/'initial_review.json')['production_tpr_sha256'],'Production input changed')
  x=core.dump_vectors(text,'x',nt);v=core.dump_vectors(text,'v',nt);box=core.dump_vectors(text,'box',3);identity=(w/'npt05.gro').read_text().splitlines()
  c.require(all(abs(box[i][j])<1e-8 for i in range(3) for j in range(3) if i!=j),'Box shear')
  gro=out/'captured.gro'
  with gro.open('x') as f:
   f.write('CPT validation view only; continuation uses native CPT\n145776\n')
   for line,xx,vv in zip(identity[2:-1],x,v):f.write(line[:20]+''.join(f'{z:8.3f}' for z in xx)+''.join(f'{z:8.4f}' for z in vv)+'\n')
   f.write(''.join(f'{box[i][i]:10.5f}' for i in range(3))+'\n')
  core.state_match(text,gro)
  c.command([sys.executable,'-E',b/'compute/scripts/check_twf154_snapshot.py',w,gro,b/'compute/configs/ligand_geometry_contract.json',out/'structure.json','--allow-box-change'],out,'structure')
  c.require(c.read(out/'structure.json')['pass'] is True,'Live sampled structure failed')
  edr=out/'captured.edr';shutil.copy2(log.with_suffix('.edr'),edr);end_grid=math.floor(end);start_grid=end_grid-500
  c.require(start_grid>=math.ceil(status['start_ps']),'Less than a 500 ps current-part sample')
  c.command([gmx,'energy','-f',edr,'-b',start_grid,'-e',end_grid,'-o',out/'thermo.xvg'],out,'energy','\n'.join(core.THERMO)+'\n0\n')
  thermo=core.thermo_report((out/'thermo.xvg').read_text(),start_grid,end_grid)
  report={'observed_at':datetime.now(timezone.utc).isoformat(),'case_id':'native_wt_ascr18','segment':status['segment'],'pid':live['pid'],'checkpoint_ps':end,'checkpoint_age_seconds':age,'checkpoint_sha256':c.sha(cp),'log_observed_ps':live['time_ps'],'structure_pass':True,'thermo':thermo,'cpu_stat':Path('/sys/fs/cgroup/cpu.stat').read_text(),'disk_free_bytes':shutil.disk_usage(b).free,'pass':True,'scope':'Live read-only sample; not closed-segment acceptance or additional production credit'}
  c.save(out/'audit.json',report);print(json.dumps({'audit':str(out/'audit.json'),'checkpoint_ps':end,'pass':True}))
 except Exception as exc:
  c.save(out/'audit_failure.json',{'at':datetime.now(timezone.utc).isoformat(),'error':str(exc),'action':'Agent must classify sampling race versus genuine runtime/structure fault; this reader never restarts MD.'});raise
if __name__=='__main__':main()
