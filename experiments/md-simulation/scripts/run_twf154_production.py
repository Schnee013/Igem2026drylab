#!/usr/bin/env python3
"""Continue the two authorized full-length rep1 systems through NPT into 100 ns.

Uses prepared structures/checkpoints and the existing CHARMM-style NPT schedule.
It checks numerical/structural preparation, never selects for ligand retention.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from twf154_preheat_support import COMMON


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def event(root, state, detail, source='runner.log'):
    p=root/'run_state_events.tsv'
    if not p.exists(): p.write_text('observed_at\tstate\tsource\tdetail\n')
    with p.open('a') as h: h.write(f'{datetime.now(timezone.utc).isoformat()}\t{state}\t{source}\t{detail}\n')
    (root/'current_state.json').write_text(json.dumps({'as_of_utc':datetime.now(timezone.utc).isoformat(),
         'state':state,'detail':detail,'source':source},indent=2))


def mdp(dt, duration, start, restraint=None):
    s=COMMON
    if restraint:
        bb,sc,lip,lig,dih=restraint
        s+=f'define = -DPOSRES -DPOSRES_FC_BB={bb} -DPOSRES_FC_SC={sc} -DPOSRES_FC_LIPID={lip} -DPOSRES_FC_LIG={lig} -DDIHRES -DDIHRES_FC={dih}\nrefcoord_scaling = all\n'
    s+=f'integrator = md\ndt = {dt}\nnsteps = {round(duration/dt)}\ntinit = {start}\n'
    s+='continuation = yes\ngen_vel = no\nconstraints = h-bonds\nconstraint_algorithm = LINCS\nlincs_order = 4\nlincs_iter = 2\n'
    s+='tcoupl = v-rescale\ntc_grps = SOLU MEMB SOLV\ntau_t = 1 1 1\nref_t = 303.15 303.15 303.15\n'
    s+='pcoupl = C-rescale\npcoupltype = semiisotropic\ntau_p = 5\ncompressibility = 4.5e-5 4.5e-5\nref_p = 1 1\n'
    s+='nstcomm = 100\ncomm_mode = linear\ncomm_grps = System\nnstxout = 0\nnstvout = 0\nnstfout = 0\n'
    s+=f'nstxout-compressed = {round(10/dt)}\nnstenergy = {round(1/dt)}\nnstlog = {round(10/dt)}\nnstcalcenergy = 100\n'
    return s


def command(args, log, data=None):
    with log.open('w') as h:
        subprocess.run([str(x) for x in args],input=data,text=True,stdout=h,stderr=subprocess.STDOUT,check=True)


def stage_check(root, prefix, end, cfg, source):
    text=(root/f'{prefix}.log').read_text()
    assert 'Finished mdrun' in text
    problems=[l for l in text.splitlines() if re.search(r'LINCS WARNING|cannot be settled|Fatal error|\bnan\b|\binf\b',l,re.I)
              and not re.fullmatch(r'\s*epsilon-rf\s*=\s*inf\s*',l)]
    assert not problems, problems
    steps=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+([\d.]+)',text)
    assert steps and abs(float(steps[-1][1])-end)<.001
    command(['python3',cfg['snapshot_checker'],source,root/f'{prefix}.gro',cfg['geometry_contract'],
             root/f'{prefix}_structure.json','--allow-box-change'],root/f'{prefix}_structure.log')
    command([cfg['gmx'],'energy','-f',root/f'{prefix}.edr','-b',max(end-500,0),'-o',root/f'{prefix}_thermo.xvg'],
            root/f'{prefix}_thermo.log','Temperature\nT-SOLU\nT-MEMB\nT-SOLV\nPotential\nDensity\nBox-X\nBox-Y\nBox-Z\nPressure\n0\n')
    lines=(root/f'{prefix}_thermo.xvg').read_text().splitlines()
    legends={}
    for line in lines:
        match=re.search(r'@ s(\d+) legend "([^"]+)"',line)
        if match:legends[int(match[1])+1]=match[2]
    rows=[list(map(float,l.split())) for l in lines if l and not l.startswith(('#','@'))]
    assert len(rows)>10 and all(math.isfinite(x) for row in rows for x in row)
    series={name:[r[i] for r in rows] for i,name in legends.items()}
    avg=lambda x:sum(x)/len(x)
    for name in ['Temperature','T-SOLU','T-MEMB','T-SOLV']:
        assert abs(avg(series[name])-303.15)<10, (name,avg(series[name]))
    series['Area-XY']=[x*y for x,y in zip(series['Box-X'],series['Box-Y'])]
    drift={}
    for name in ['Density','Area-XY','Box-Z']:
        values=series[name];n=len(values)//2
        drift[name]=abs(avg(values[-n:])-avg(values[:n]))/avg(values)
    result={'stage':prefix,'end_ps':end,'thermodynamic_means':{k:avg(v) for k,v in series.items()},
            'last500ps_half_window_fractional_change':drift,'box_density_settled':all(v<.02 for v in drift.values()),
            'scope':'Numerical preparation and short-window box/density drift screen, not thermodynamic or binding convergence'}
    (root/f'{prefix}_summary.json').write_text(json.dumps(result,indent=2))
    return result


def run(cfg, case):
    assert case in ['raw_n84v_ascr18','raw_v368r_ascr3'] and cfg['production_ns']==100
    root=Path(cfg['root'])/case/'rep1';root.mkdir(parents=True,exist_ok=True)
    lock=(root/'runner.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (root/'npt01.tpr').exists(), 'Existing simulation requires explicit checkpoint continuation, not overwrite'
    native=Path(cfg['native_wt_root'])/'results/preheat_status.json'
    event(root,'UNRESOLVED','Waiting for both independent WT preheats to finish')
    deadline=time.time()+48*3600
    while True:
        if native.exists():
            data=json.loads(native.read_text())
            if {x['case'] for x in data['cases']}=={'native_wt_ascr18','native_wt_ascr3'} and data['passed']==2:
                break
        assert time.time()<deadline, 'WT preheat dependency did not finish within 48h'
        time.sleep(45)
    source=Path(cfg['preheat_root'])/'runs'/case;selected=source/'heating_v4'
    manifest=json.loads((Path(cfg['preheat_root'])/'results/selected_run_manifest.json').read_text())
    evidence=next(x for x in manifest['cases'] if x['case']==case)
    assert sha(selected/'hold.gro')==evidence['final_gro_sha256']
    command(['python3',cfg['snapshot_checker'],source,selected/'hold.gro',cfg['geometry_contract'],root/'starting_structure.json'],root/'starting_structure.log')
    shutil.copytree(source/'toppar',root/'toppar')
    (root/'topol.top').write_text((source/'topol.top').read_text().replace('../ff/',str(Path(cfg['preheat_root'])/'inputs/membrane05/ff')+'/'))
    for name in ['index.ndx','input_contract.json']:
        shutil.copy2(source/name,root/name)
    shutil.copy2(selected/'hold.gro',root/'start.gro');shutil.copy2(selected/'hold.cpt',root/'start.cpt')
    (root/'config.json').write_text(json.dumps(cfg,indent=2))
    (root/'input_manifest.json').write_text(json.dumps({'case':case,'preheat':evidence,
        'independent_wt_preheat_sha256':sha(native),'source_hold_cpt_sha256':sha(selected/'hold.cpt'),
        'source_hold_gro_sha256':sha(selected/'hold.gro'),'production_ns':100,
        'schedule':'NPT 125+500+500+500 ps restraint taper; then 1000 ps unrestrained; at most four 1000 ps preparation extensions',
        'shared_backbone':False,'production_position_or_dihedral_restraints':False},indent=2))
    free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])
    assert free>=2048, 'Insufficient GPU memory for a new run; inspect resource state before retrying'
    command([cfg['gmx'],'--version'],root/'gromacs_identity.txt')
    os.chdir(root)
    previous='start';clock=125
    stages=[('npt01',.001,125,(1000,500,400,100,200)),('npt02',.002,500,(500,200,200,50,200)),
            ('npt03',.002,500,(200,50,40,10,100)),('npt04',.002,500,(50,0,0,0,0)),
            ('npt05',.002,1000,None)]
    args=['-ntomp',str(cfg['threads']),'-pin','off','-nb','gpu','-pme','gpu','-bonded','cpu','-update','cpu','-cpt','10']
    def stage(name,dt,duration,restraint):
        nonlocal previous,clock
        (root/f'{name}.mdp').write_text(mdp(dt,duration,clock,restraint))
        extra=['-r','start.gro'] if restraint else []
        command([cfg['gmx'],'grompp','-f',f'{name}.mdp','-c',f'{previous}.gro','-t',f'{previous}.cpt',*extra,
                 '-p','topol.top','-n','index.ndx','-o',f'{name}.tpr','-po',f'{name}_mdout.mdp','-pp',f'{name}_processed.top'],root/f'{name}_grompp.log')
        event(root,'RUNNING_VERIFIED',f'{name}: NPT {duration} ps; restraints {restraint}',f'{name}.tpr')
        command([cfg['gmx'],'mdrun','-deffnm',name,*args],root/f'{name}_mdrun.log')
        clock+=duration;previous=name
        return stage_check(root,name,clock,cfg,source)
    for s in stages: result=stage(*s)
    for i in range(4):
        if result['box_density_settled']:break
        result=stage(f'npt_extend{i+1:02d}',.002,1000,None)
    assert result['box_density_settled'], 'Box/density still drifting; preserve preparation and inspect before production'
    (root/'production.mdp').write_text(mdp(.002,100000,0,None))
    command([cfg['gmx'],'grompp','-f','production.mdp','-c',f'{previous}.gro','-t',f'{previous}.cpt','-p','topol.top',
             '-n','index.ndx','-o','production.tpr','-po','production_mdout.mdp','-pp','production_processed.top'],root/'production_grompp.log')
    processed=(root/'production_processed.top').read_text()
    assert not re.search(r'^\s*\[\s*(position_restraints|dihedral_restraints)\s*\]',processed,re.M)
    event(root,'RUNNING_VERIFIED','100 ns production starts; full-length, no position/dihedral restraints; rep1','production.tpr')
    command([cfg['gmx'],'mdrun','-deffnm','production',*args],root/'production_mdrun.log')
    text=(root/'production.log').read_text()
    assert 'Finished mdrun' in text and re.search(r'50000000\s+100000\.000',text)
    event(root,'TERMINAL_NORMAL','100 ns production completed; trajectory analysis remains','production.log')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('case');a=p.parse_args()
    cfg=json.loads(a.config.read_text());os.environ.update(OMP_NUM_THREADS=str(cfg['threads']),OPENBLAS_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='0')
    target=Path(cfg['root'])/a.case/'rep1'
    try:run(cfg,a.case)
    except Exception as exc:
        if target.exists():event(target,'TERMINAL_ABNORMAL',str(exc))
        raise
