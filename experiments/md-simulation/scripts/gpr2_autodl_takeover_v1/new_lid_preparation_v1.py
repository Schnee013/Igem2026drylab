#!/usr/bin/env python3
"""Own new-lid EM, original 50+75ps preheat, and five NPT stages; never production."""
import argparse, fcntl, json, math, os, re, shutil, subprocess, sys
from pathlib import Path
import dual_runtime as d
import prepare_existing_npt as core

CASES=('v368r_ascr3_lid_rebuilt_own_pose_v1','native_wt_ascr3_lid_rebuilt_own_pose_v1')
STAGES=[('em',0.,0.),('heat',0.,50.),('hold',50.,125.)]+core.STAGES

def sources(b,case,receipt):
    w=b/'runs'/case/'rep1_codex_v1';src=b/'compute/cases'/case
    meta=d.read(src/'case.json');ready=d.read(w/'new_input_ready.json')
    d.need(case in CASES and meta['new_lid'] and not meta['allowed_old_checkpoint_continuation'],'Wrong own branch')
    order=d.read(b/'WORK_ORDER.json');d.need(case in order['cases'] and order['reps']==[1] and order['production_scope_authorized'],'Scope differs')
    d.need(ready['case_id']==case and ready['candidate_sha256']==d.sha(src/meta['candidate_receptor']) and ready['own_pose_sha256']==d.sha(src/'pose.sdf'),'Own candidate/pose changed')
    d.need(ready['em_tpr_sha256']==d.sha(w/'em.tpr') and ready['assembly']['ligand_and_lipid_coordinates_unchanged'],'Own compiled neutral state changed')
    recovery=d.read(receipt);manifest=b/'operator_records/closed_input_archive_v1/manifest.json'
    d.need(recovery['all_match'] and recovery['manifest_sha256']==d.sha(manifest),'Independent own new-input E2 recovery absent')
    archived={e['relative_path']:e for e in d.read(manifest)['files']}
    names=['new_input_ready.json','assembly_check.json','input_contract.json','ionized.gro','index.ndx','topol.top','em.tpr','em.mdp','heat.mdp','hold.mdp','em.mdout.mdp','em.processed.top']
    paths=[w/n for n in names]+[p for folder in ('toppar','ff') for p in (w/folder).rglob('*') if p.is_file()]
    evidence={}
    for p in paths:
        rel=str(p.relative_to(b));d.need(not p.is_symlink() and d.sha(p)==archived[rel]['sha256'],'Prepared file differs from verified E2 input: '+rel);evidence[rel]=d.sha(p)
    frozen={e['path']:e for e in d.read(b/'MANIFEST.json')['files']}
    for p in [src/'case.json',src/meta['candidate_receptor'],src/'pose.sdf',b/'compute/scripts/twf154_preheat_support.py',b/'compute/scripts/check_twf154_snapshot.py',b/'compute/configs/ligand_geometry_contract.json']+[b/'compute/mdp'/(name+'.mdp') for name,_,_ in core.STAGES]:
        rel=str(p.relative_to(b));d.need(d.sha(p)==frozen[rel]['sha256'],'Frozen source changed');evidence[rel]=d.sha(p)
    ids,_,_=core.read_gro(w/'ionized.gro');d.need(len(ids)==ready['atom_count'],'Atom count changed');core.index_check(w/'index.ndx',ids)
    return {'case_id':case,'atom_count':len(ids),'source_sha256':evidence,'recovery':{'path':str(receipt),'sha256':d.sha(receipt)},'scope':'own new-lid preparation only','production_ready':False}

def run(args,out,name,cwd,stdin=None):
    core.write(out/(name+'.command.json'),{'argv':list(map(str,args)),'cwd':str(cwd),'at':d.now()})
    return core.command(args,out/(name+'.log'),cwd,stdin)

def thermal_preheat(text,start,end,hold):
    legends={int(i)+1:n for i,n in re.findall(r'@\s+s(\d+)\s+legend\s+"([^"]+)"',text)}
    rows=[list(map(float,l.split())) for l in text.splitlines() if l.strip() and not l.lstrip().startswith(('#','@'))]
    required={'Potential','Temperature','T-SOLU','T-MEMB','T-SOLV'}
    d.need(set(legends.values())==required and len(rows)==round((end-start)/.5)+1,'Preheat energy fields/cadence count differs')
    d.need(all(len(r)==6 and all(math.isfinite(v) for v in r) and abs(r[0]-(start+i*.5))<.001 for i,r in enumerate(rows)),'Preheat finite original0.5ps grid failed')
    window=[r for r in rows if r[0]>=end-20];means={name:sum(r[i] for r in window)/len(window) for i,name in legends.items()}
    d.need(all(r[i]>0 for r in rows for i,n in legends.items() if n.startswith('T')),'Nonpositive temperature')
    if hold:d.need(all(abs(means[n]-303.15)<10 for n in required if n.startswith('T')),'Own final preheat temperature screen failed')
    return {'last20ps_means':means,'heat_ramp_scope':'Heat verifies original annealing settings, finite energies and structural integrity; the303K mean screen is applied to hold only.'}

def runtime(tpr,log,name):
    core.issue_scan(log,name)
    d.need('Finished mdrun' in log and 'Using 1 MPI process' in log and 'Using 8 OpenMP threads' in log,'Own normal eight-thread closure absent')
    d.need('-notunepme' in log and not re.search(r'PME tuning|timed with pme grid|Optimal PME grid',log,re.I),'Unreviewed PME tuning')
    if name.startswith('npt'):return core.runtime_parameters_check(tpr,log)
    for key in ('fourier-nx','fourier-ny','fourier-nz','pme-order','ewald-rtol','rcoulomb'):
        d.need(core.scalar(tpr,key)==core.scalar(log,key),'Own compiled electrostatics changed: '+key)
    if name!='em':
        d.need('PME tasks will do all aspects on the GPU' in log and 'Using GPU 8x4 nonbonded short-range kernels' in log,'Original compat preheat offload absent')
    return {'threads':8,'backend':'CPU EM' if name=='em' else 'GPU NB/PME; CPU bonded/update original preheat','pme_tuning':False}

def execute(b,case,out,plan):
    w=b/'runs'/case/'rep1_codex_v1';code=Path(__file__).resolve().parent
    locks=[]
    for rel in ('operator_records/codex_scheduler.lock','operator_records/equilibration_prep_v2_2_2/serial.lock'):
        f=(b/rel).open('a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
    previous=None
    for index,(name,start,end) in enumerate(STAGES):
        accepted=w/(name+'.new_lid_validated.json')
        if accepted.exists():
            s=d.read(accepted);d.need(s['case_id']==case and s['stage']==name and s['pass'],'Wrong saved stage')
            for p,h in s['files_sha256'].items():d.need(d.sha(p)==h,'Saved stage evidence changed')
            previous=name;continue
        stage=out/name;d.need(not stage.exists(),'Partial stage exists; preserve and inspect instead of rerunning');stage.mkdir()
        for rel,h in plan['source_sha256'].items():d.need(d.sha(b/rel)==h,'Immutable own input changed')
        live=d.live(b);d.save(stage/'live.json',live)
        d.need(not list(w.glob(name+'*.log')) and not (w/(name+'.gro')).exists(),'Existing MD outputs require specific recovery')
        if name!='em':
            if name.startswith('npt'):
                target=w/(name+'.mdp');d.need(not target.exists(),'Unexpected NPT MDP');shutil.copyfile(b/'compute/mdp'/(name+'.mdp'),target)
            cmd=[d.GMX,'grompp','-f',name+'.mdp','-c',previous+'.gro']
            if name!='heat':cmd+=['-t',previous+'.cpt']
            if name in ('heat','hold'):cmd+=['-r','ionized.gro']
            elif name!='npt05':cmd+=['-r','hold.gro']
            cmd+=['-p','topol.top','-n','index.ndx','-o',name+'.tpr','-po',name+'.mdout.mdp','-pp',name+'.processed.top']
            output=run(cmd,stage,'compile',w);d.need(not re.search(r'WARNING\s+\d+|Fatal error',output),'Neutral grompp warning')
        wanted=core.mdp((w/(name+'.mdp')).read_text());actual=core.mdp((w/(name+'.mdout.mdp')).read_text())
        d.need(all(core.same_mdp_value(actual.get(k,''),v) for k,v in wanted.items()),'MDP readback changed')
        if name=='npt05':d.need(not re.search(r'^\s*\[\s*(position_restraints|dihedral_restraints)\s*\]',(w/(name+'.processed.top')).read_text(),re.M),'Restraints in final NPT')
        tpr=run([d.GMX,'dump','-s',w/(name+'.tpr')],stage,'tpr_dump',w)
        d.need(core.scalar(tpr,'natoms')==plan['atom_count'],'Own TPR atom count differs')
        if name!='em':
            dt=core.scalar(tpr,'dt');d.need(core.scalar(tpr,'init-step')==0 and core.scalar(tpr,'tinit')==start and abs(dt*core.scalar(tpr,'nsteps')-(end-start))<1e-6,'Original stage clock changed')
            if name=='heat':core.coordinates_match(tpr,w/'em.gro')
            else:core.state_match(tpr,w/(previous+'.gro'))
        evidence=[{'path':str(out/'source_review.json'),'sha256':d.sha(out/'source_review.json')},{'path':str(stage/'live.json'),'sha256':d.sha(stage/'live.json')}]
        if previous:evidence.append({'path':str(w/(previous+'.new_lid_validated.json')),'sha256':d.sha(w/(previous+'.new_lid_validated.json'))})
        gate=stage/'stage_gate.json';d.save(gate,{'case_id':case,'stage':name,'scope':plan['scope'],'production_ready':False,'tpr_sha256':d.sha(w/(name+'.tpr')),'live_verified_at':live['utc'],'evidence':evidence})
        offload='cpu' if name=='em' else 'compat' if name in ('heat','hold') else 'gpu'
        run([sys.executable,'-E',code/'run_stage_new_lid_v1.py','--case',case,'--stage',name if name in ('em','heat','hold') else 'npt','--workdir',w,'--tpr',w/(name+'.tpr'),'--prefix',name,'--gmx',d.GMX,'--threads','8','--offload',offload,'--maxh','.5','--expected-end-ps',end,'--min-free-gb','10','--gate',gate],stage,'supervisor',w)
        log=(w/(name+'.log')).read_text();rt=runtime(tpr,log,name);result={'case_id':case,'stage':name,'start_ps':start,'end_ps':end,'runtime':rt,'production_ready':False}
        if name=='em':
            run([sys.executable,'-E',b/'compute/scripts/twf154_preheat_support.py','em_gate'],stage,'em_gate',w);d.need(d.read(w/'em_gate.json')['pass'],'Own EM failed');result['energy_minimization']=d.read(w/'em_gate.json')
            d.need(re.search(r'Potential Energy\s*=\s*[-+\d.eE]+',log) is not None,'Final EM energy missing')
        else:
            cp=run([d.GMX,'dump','-cp',w/(name+'.cpt')],stage,'checkpoint',w)
            d.need(core.scalar(cp,'#atoms')==plan['atom_count'] and core.scalar(cp,'t')==end and core.scalar(cp,'step')==round((end-start)/dt),'Actual stage ended early/wrong clock');core.state_match(cp,w/(name+'.gro'))
            check=run([d.GMX,'check','-f',w/(name+'.xtc')],stage,'trajectory',w);result['trajectory']=core.trajectory_check(check,start,end,plan['atom_count'],tpr)
            check=run([d.GMX,'check','-e',w/(name+'.edr')],stage,'edr_check',w);core.issue_scan(check,'EDR');d.need(not re.search(r'WARNING|Incomplete|Timesteps at',check,re.I),'EDR grid problem')
            terms=core.THERMO if name.startswith('npt') else ('Potential','Temperature','T-SOLU','T-MEMB','T-SOLV')
            run([d.GMX,'energy','-f',w/(name+'.edr'),'-o',stage/'thermo.xvg'],stage,'energy',w,'\n'.join(terms)+'\n0\n')
            result['thermo']=core.thermo_report((stage/'thermo.xvg').read_text(),start,end) if name.startswith('npt') else thermal_preheat((stage/'thermo.xvg').read_text(),start,end,name=='hold')
        run([sys.executable,'-E',b/'compute/scripts/check_twf154_snapshot.py',w,w/(name+'.gro'),b/'compute/configs/ligand_geometry_contract.json',stage/'structure.json','--allow-box-change'],stage,'structure',w)
        d.need(d.read(stage/'structure.json')['pass'],'Own full structure failed')
        result['pass']=True;result['accepted_at']=d.now();files=[p for p in stage.iterdir() if p.is_file()]+[p for p in w.glob(name+'.*') if p.is_file()]
        result['files_sha256']={str(p):d.sha(p) for p in files};d.save(accepted,result)
        archive=out/f'segment_{index+1:03d}';archive.mkdir();files.append(accepted)
        d.save(archive/'closed_segment.json',{'case_id':case,'stage':name,'stage_kind':'preparation','production_credit_ns':0,'start_ps':start,'end_ps':end,'pass':True,'files':[{'path':str(p),'sha256':d.sha(p)} for p in files]})
        previous=name
    final=d.read(w/'npt05.new_lid_validated.json');d.need(final['thermo']['box_density_settled'],'Final NPT drift screen failed; no unbounded extension')
    d.save(w/'preparation_complete.json',{'case_id':case,'preparation_pass':True,'production_ready':False,'final_time_ps':2750,'source':'Own new-lid fresh EM→heat→hold→five NPT; no old raw checkpoint','final_validation_sha256':d.sha(w/'npt05.new_lid_validated.json'),'next':'Own zero-clock production TPR, numerical/start/restart qualification, then dual production'})
    for f in locks:fcntl.flock(f,fcntl.LOCK_UN);f.close()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--case',choices=CASES,required=True);ap.add_argument('--recovery-receipt',type=Path,required=True);ap.add_argument('--execute',action='store_true');a=ap.parse_args()
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1');b=a.bundle.resolve();plan=sources(b,a.case,a.recovery_receipt);out=b/'operator_records'/('new_lid_prep_'+a.case+'_v1');out.mkdir(exist_ok=True);review=out/'source_review.json'
    if review.exists():d.need(d.read(review)==plan,'Source review changed')
    else:d.save(review,plan)
    if a.execute:execute(b,a.case,out,plan)
    print(json.dumps({'case':a.case,'source_preflight_pass':True,'executed':a.execute,'production_ready':False}))
if __name__=='__main__':main()
