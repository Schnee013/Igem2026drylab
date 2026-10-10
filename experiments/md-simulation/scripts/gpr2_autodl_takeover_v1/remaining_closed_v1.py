#!/usr/bin/env python3
"""Same accepted closed-part validation, with each remaining case's own identity/count."""
import math,re,shutil,sys
from pathlib import Path
from wt_controller_v1_5 import command,require,read,save,sha,event,CHECKS,NUMBER,now,ref
def validate_closed(bundle,work,out,core,gmx,start,tpr,old_logs,*,case,natoms,prefix):
    logs=[p for p in work.glob(prefix+'*.log') if str(p) not in old_logs]
    require(len(logs)==1,'Ambiguous new closed production log')
    log=logs[0];stem=log.with_suffix('');text=log.read_text();core.issue_scan(text,'Production log')
    require('Finished mdrun' in text,'Production did not close normally')
    core.runtime_parameters_check(tpr,text)
    cpt=work/(prefix+'.cpt');cp,_=command([gmx,'dump','-cp',cpt],out,'checkpoint')
    end=core.scalar(cp,'t');step=int(core.scalar(cp,'step'))
    require(core.scalar(cp,'#atoms')==natoms and start<end<=100000 and abs(end-.002*step)<.001,'Invalid or nonadvancing production CPT')
    times=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+('+NUMBER+')',text)
    require(times and int(times[-1][0])==step and abs(float(times[-1][1])-end)<.001,'Final log/CPT clocks differ')
    gro=Path(str(log)[:-4]+'.gro')
    if not gro.exists():
        # maxh closure can save a complete CPT without emitting a final GRO.
        # This text snapshot is solely for structure checking; continuation uses CPT.
        gro=out/'checkpoint_snapshot.gro'
        source=(work/'npt05.gro').read_text().splitlines()
        require(int(source[1])==natoms and len(source)==(natoms+3),'Reference atom identities incomplete')
        xyz=core.dump_vectors(cp,'x',natoms);vel=core.dump_vectors(cp,'v',natoms);box=core.dump_vectors(cp,'box',3)
        require(all(abs(box[i][j])<1e-8 for i in range(3) for j in range(3) if i!=j),'Unexpected box shear')
        with gro.open('x') as f:
            f.write(f'CPT-derived validation snapshot t={end}; never used to restart\n{natoms}\n')
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
    require(re.search(r'#\s*Atoms\s+'+str(natoms)+r'\b',xt) and not re.search(r'WARNING|Incomplete|Timesteps at',xt,re.I),'XTC integrity issue')
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
    result={'case_id':case,'validated_at':now(),'start_ps':start,'end_ps':end,'step':step,'trajectory':{'first_ps':first,'last_ps':last,'frames':count},'thermo':thermo,'pass':True,'checkpoint':ref(checkpoint),'files':[ref(p) for p in (log,gro,xtc,edr,checkpoint)],'production_tpr_sha256':sha(work/'production.tpr')}
    save(out/'closed_segment.json',result);return result
