#!/usr/bin/env python3
"""Reconstructed v2 after workspace loss; not recovered original bytes.
Default plan-only. Three selected 125 ps preheats only; never production.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

VERSION = 'prepared_v2_3'
VERIFIED_GMX = '/opt/drylab/gromacs-2025.4/bin.AVX2_256/gmx_mpi'
VERIFIED_GMX_SHA256 = '90a2a9be92d37b236e0772a91df7eef1ac7fe24c4522d2994f6519f6835f6bd7'
NPT01_BACKUP_RECEIPT_SHA256 = '51ceac6559ed533e5617fe2ee73c8215253965093521abc47cd343fa09fce5c8'
CASES = ('raw_n84v_ascr3', 'raw_v368r_ascr18', 'native_wt_ascr18')
STAGES = [('npt01',125.,250.),('npt02',250.,750.),('npt03',750.,1250.),('npt04',1250.,1750.),('npt05',1750.,2750.)]
THERMO = ('Temperature','T-SOLU','T-MEMB','T-SOLV','Potential','Density','Box-X','Box-Y','Box-Z','Pressure')
NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
GATES = ('numerical_compatibility','source_identity','structure_purpose','resources','storage_and_recovery')
INITIAL_EVIDENCE = ('gromacs_identity.txt','source_hold.tpr.dump.txt','source_hold.tpr.dump.txt.stderr.txt','start.cpt.dump.txt','start.cpt.dump.txt.stderr.txt','em.audit.tpr','em.audit.mdout.mdp','em.processed.top','em.audit.grompp.log','start.structure.json','start.structure.log','original_bond_contract.json')


def require(ok, message):
    if not ok: raise RuntimeError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def write(path, value):
    with Path(path).open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False); f.write('\n')


def mdp(text):
    out={}
    for raw in text.splitlines():
        line=raw.split(';',1)[0].strip()
        if '=' not in line: continue
        key,value=line.split('=',1); key=key.strip().lower().replace('_','-')
        require(key not in out,f'Duplicate MDP key {key}'); out[key]=value.strip()
    return out


def same_mdp_value(a,b):
    def token(v):
        try:return float(v)
        except ValueError:return v.lower()
    return [token(v) for v in a.split()]==[token(v) for v in b.split()]


def read_gro(path):
    lines=Path(path).read_text().splitlines(); n=int(lines[1])
    require(len(lines)==n+3,f'GRO atom count: {path}')
    ids=[(int(l[:5]),l[5:10].strip(),l[10:15].strip()) for l in lines[2:-1]]
    xyz=[tuple(float(l[i:i+8]) for i in (20,28,36)) for l in lines[2:-1]]
    box=list(map(float,lines[-1].split()))
    require(len(box)==3 and all(math.isfinite(v) and v>0 for v in box),'Orthorhombic positive box required')
    require(all(math.isfinite(v) for pos in xyz for v in pos),'Non-finite GRO')
    return ids,xyz,box


def index_check(path,atoms):
    groups={}; key=None
    for raw in Path(path).read_text().splitlines():
        line=raw.split(';',1)[0].strip()
        if not line:continue
        if line.startswith('['):
            key=line.strip('[] '); require(key not in groups,'Duplicate index group'); groups[key]=[]
        else:
            require(key is not None,'Index values before header'); groups[key].extend(map(int,line.split()))
    expected={k:[] for k in ('System','SOLU','MEMB','SOLV')}
    for i,(_,res,_) in enumerate(atoms,1):
        expected['System'].append(i)
        expected['MEMB' if res=='POPC' else 'SOLV' if res in ('SOL','POT','CLA') else 'SOLU'].append(i)
    for k,v in expected.items():require(v and groups.get(k)==v,f'Index membership/order {k}')
    return {k:len(v) for k,v in expected.items()}


def verify_sources(bundle,case):
    require(case in CASES,'Only the three selected existing preheats')
    source=bundle/'compute/cases'/case; prepared=source/'prepared'
    meta=json.loads((source/'case.json').read_text())
    require(meta['case_id']==case and not meta['new_lid'] and meta['state']=='PREHEATED_125_PS_NPT_RELEASE_REQUIRED','Wrong branch')
    order=json.loads((bundle/'WORK_ORDER.json').read_text())
    require(case in order['cases'] and order['reps']==[1] and order['production_scope_authorized'] is True,'Work order mismatch')
    ff=bundle/'compute/forcefields'/(meta['ligand']+'.ff')
    files=[source/'case.json',bundle/'WORK_ORDER.json',bundle/'compute/configs/ligand_geometry_contract.json']
    files += [p for d in (prepared,ff,bundle/'compute/mdp',bundle/'compute/scripts') for p in d.rglob('*') if p.is_file() and p.suffix!='.pyc']
    manifest={r['path']:r for r in json.loads((bundle/'MANIFEST.json').read_text())['files']}; digests={}
    for p in sorted(files):
        rel=p.relative_to(bundle).as_posix(); require(rel in manifest and not p.is_symlink(),f'Unexpected source {rel}')
        row=manifest[rel]; digest=sha(p)
        require(digest==row['sha256'] and p.stat().st_size==row['bytes'],f'Changed source {rel}'); digests[rel]=digest
    info=json.loads((prepared/'input_contract.json').read_text())
    require(info['id']==case and info['lid_position_restraints'] is False,'Wrong contract/lid restraints')
    atoms,_,_=read_gro(prepared/'hold.gro'); reference,_,_=read_gro(prepared/'ionized.gro')
    require(atoms==reference,'Hold/reference atom identity or order mismatch')
    groups=index_check(prepared/'index.ndx',atoms)
    section=''; protein=[]; posres=[]
    for raw in (prepared/'toppar/PROA.itp').read_text().splitlines():
        line=raw.split(';',1)[0].strip()
        if line.startswith('['):section=line.strip('[] ')
        elif line and not line.startswith('#'):
            f=line.split()
            if section=='atoms':protein.append((int(f[2]),f[3],f[4]))
            elif section=='position_restraints':posres.append(int(f[0]))
    require(len(protein)==info['atoms'] and protein==atoms[:info['atoms']],'PROA identity/order mismatch')
    require(not any(164<=protein[i-1][0]<=178 for i in posres),'Unexpected lid position restraint')
    for name,start,end in STAGES:
        d=mdp((bundle/f'compute/mdp/{name}.mdp').read_text())
        require(float(d['tinit'])==start and int(d.get('init-step',0))==0,f'{name} start clock')
        require(abs(float(d['dt'])*int(d['nsteps'])-(end-start))<1e-8,f'{name} duration')
        require(d['gen-vel']=='no' and d['continuation']=='yes',f'{name} velocity settings')
        require(bool(d.get('define'))==(name!='npt05'),f'{name} restraints')
    return {'version':VERSION,'case_id':case,'source_dir':str(prepared),'forcefield_dir':str(ff),
            'source_sha256':digests,'atom_count':len(atoms),'index_counts':groups,
            'wt_w174_repair_preserved_by_prepared_branch':case=='native_wt_ascr18',
            'schedule_ps':[{'stage':n,'start':s,'end':e} for n,s,e in STAGES],
            'max_drift_extensions':4,'extension_ps':1000,'max_preparation_end_ps':6750,
            'mode':'PLAN_ONLY','numerical_compatibility':'NOT_ESTABLISHED_HERE','production_ready':False}



def checked_workdir(bundle,root):
    bundle=bundle.resolve(); root=root.resolve()
    require(not root.is_relative_to((bundle/'compute').resolve()),'Never write inside original compute inputs')
    return root


def fixed_expected_hashes(bundle,plan):
    source=Path(plan['source_dir']); result={}
    for name in ('ionized.gro','input_contract.json','index.ndx','selected_em.gro','em.mdp'):
        result[name]=sha(source/name)
    for old,new in (('hold.gro','start.gro'),('hold.cpt','start.cpt'),('hold.tpr','source_hold.tpr')):
        result[new]=sha(source/old)
    for src,dest in ((source/'toppar','toppar'),(Path(plan['forcefield_dir']),'ff')):
        for p in src.rglob('*'):
            if p.is_file():result[(Path(dest)/p.relative_to(src)).as_posix()]=sha(p)
    text,count=re.subn(r'^#include "[^"\n]*forcefield\.itp"$','#include "ff/forcefield.itp"',(source/'topol.top').read_text(),flags=re.M)
    require(count==1,'Exactly one forcefield include must be rewritten')
    result['topol.top']=hashlib.sha256(text.encode()).hexdigest()
    for name,_,_ in STAGES:result[f'{name}.mdp']=sha(bundle/f'compute/mdp/{name}.mdp')
    return result


def fixed_input_names(plan):
    source=Path(plan['source_dir']); bundle=source.parents[3]
    return set(fixed_expected_hashes(bundle,plan))


def stage_output_names(name):
    suffixes=('mdp','tpr','mdout.mdp','processed.top','tpr.dump.txt','tpr.dump.txt.stderr.txt','log','cpt','gro','xtc','edr',
              'cpt.dump.txt','cpt.dump.txt.stderr.txt','runtime.json','structure.json','structure.log','xtc.check.txt','edr.check.txt','thermo.xvg','energy.log')
    return {f'{name}.{s}' for s in suffixes}|{f'audit.{name}.{s}' for s in ('grompp.log','supervisor.log','supervisor_tpr.dump.txt','supervisor_tpr.dump.txt.stderr.txt','gate.json')}


def validate_manifest(root,manifest,required):
    require(isinstance(manifest,dict) and bool(manifest),'Missing/nonempty artifact manifest required')
    missing=set(required)-set(manifest)
    require(not missing,f'Missing mandatory artifact hashes: {sorted(missing)}')
    for rel,digest in manifest.items():
        p=Path(rel)
        require(not p.is_absolute() and '..' not in p.parts and p.as_posix()==rel,'Unsafe artifact path')
        target=root/p
        require(target.resolve().is_relative_to(root.resolve()) and not target.is_symlink(),'Artifact symlink/outside work directory')
        require(isinstance(digest,str) and re.fullmatch(r'[0-9a-f]{64}',digest) is not None,'Invalid SHA256 in manifest')
        require(target.is_file() and sha(target)==digest,f'Changed validated artifact {rel}')


def preflight_new_outputs(root,patterns,allowed=()):
    allow=set(allowed); existing=[]
    for pattern in patterns:
        existing.extend(p.name for p in root.glob(pattern) if p.name not in allow)
    require(not existing,f'Generated output already exists; preserve and inspect: {sorted(set(existing))}')


def validate_npt01_import(root,result):
    require(result.get('case_id')=='native_wt_ascr18' and result.get('replicate')==1 and result.get('stage')=='npt01' and result.get('pass_stage') is True,'Original nativeWT rep1 NPT01 acceptance required')
    manifest=result.get('output_sha256')
    validate_manifest(root,manifest,stage_output_names('npt01')|{'audit.npt01.import.json'})
    record=root/'audit.npt01.import.json';data=json.loads(record.read_text())
    require(result.get('import_record')==record.name and result.get('import_record_sha256')==sha(record),'Saved NPT01 import record differs')
    require(data.get('case_id')=='native_wt_ascr18' and data.get('replicate')==1 and data.get('stage')=='npt01' and data.get('existing_files_overwritten') is False and data.get('md_started') is False,'Invalid NPT01 import provenance')
    require(data.get('backup_receipt_sha256')==NPT01_BACKUP_RECEIPT_SHA256,'Verified original NPT01 full-backup receipt missing')
    for field in ('revalidation_report','revalidation_manifest'):
        require(manifest.get(data.get(field))==data.get(field+'_sha256') and isinstance(data.get(field+'_sha256'),str),'Imported validation does not bind read-only audit evidence')
    report=json.loads((root/data['revalidation_report']).read_text())
    require(report.get('revalidation_pass') is True and report.get('original_outputs_unchanged') is True and report.get('md_rerun') is False and report.get('simulation_end_ps')==250,'Independent completed-NPT01 audit did not pass')
    for suffix in ('tpr','cpt','gro','xtc','edr'):
        require(report.get('completed_'+suffix+'_sha256')==manifest.get('npt01.'+suffix),'Imported core state differs from independently verified NPT01')


def materialize(bundle,root,plan):
    root=checked_workdir(bundle,root)
    require(not root.exists(),f'Refusing overwrite {root}')
    source=Path(plan['source_dir']); root.mkdir(parents=True)
    for name in ('ionized.gro','input_contract.json','index.ndx','selected_em.gro','em.mdp'):
        shutil.copy2(source/name,root/name)
    for old,new in (('hold.gro','start.gro'),('hold.cpt','start.cpt'),('hold.tpr','source_hold.tpr')):
        shutil.copy2(source/old,root/new)
    shutil.copytree(source/'toppar',root/'toppar'); shutil.copytree(plan['forcefield_dir'],root/'ff')
    original=(source/'topol.top').read_text()
    text,n=re.subn(r'^#include "[^"\n]*forcefield\.itp"$','#include "ff/forcefield.itp"',original,flags=re.M)
    require(n==1,'Exactly one forcefield include must be rewritten'); (root/'topol.top').write_text(text)
    for name,_,_ in STAGES:shutil.copy2(bundle/f'compute/mdp/{name}.mdp',root/f'{name}.mdp')
    record=dict(plan,mode='MATERIALIZED_ONLY',path_rewrite={'old_topol_sha256':sha(source/'topol.top'),'new_topol_sha256':sha(root/'topol.top'),'only_change':'forcefield include -> ff/forcefield.itp'})
    record['fixed_files_sha256']={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}
    expected=fixed_expected_hashes(bundle,plan)
    require(record['fixed_files_sha256']==expected,'Copied inputs differ from authoritative source or allowed rewrite')
    write(root/'preparation_inputs.json',record)


def gate_check(path,plan,gmx):
    require(path is not None and path.is_file(),'Evidence-backed preparation gate required; no GROMACS invocation allowed')
    gate=json.loads(path.read_text())
    require(gate.get('case_id')==plan['case_id'] and gate.get('replicate')==1,'Gate case/replicate mismatch')
    sourcekey=f"compute/cases/{plan['case_id']}/prepared/hold.cpt"
    require(gate.get('source_hold_cpt_sha256')==plan['source_sha256'][sourcekey],'Gate source checkpoint mismatch')
    for key in GATES:
        require(gate.get('checks',{}).get(key) is True,f'Closed preparation gate: {key}')
        refs=gate.get('evidence',{}).get(key); require(isinstance(refs,list) and refs,f'Missing {key} evidence')
        for row in refs:
            p=Path(row['path']); p=p if p.is_absolute() else path.parent/p
            require(p.is_file() and sha(p)==row['sha256'],f'Missing/changed evidence {key}')
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(gate['live_verified_at'])).total_seconds()
    require(0<=age<=900,'Refresh resource/storage evidence within 15 minutes before a new stage')
    runtime=gate['runtime']; actual=gmx.resolve(strict=True)
    require(str(actual)==runtime['gmx_realpath'] and sha(actual)==runtime['gmx_sha256'],'Runtime binary identity mismatch')
    require(runtime['offload']=='gpu' and type(runtime['threads']) is int and runtime['threads']==8 and runtime.get('pme_tuning') is False,'Only reviewed GPU full-offload/8 threads/no PME tuning is qualified')
    require(runtime.get('pme_grid_policy')=='case_original_grompp_grid','No cross-case PME grid override allowed')
    require(runtime['gmx_realpath']==VERIFIED_GMX and runtime['gmx_sha256']==VERIFIED_GMX_SHA256,'Runtime not the live-verified A binary')
    allowed=gate.get('allowed_stages')
    require(isinstance(allowed,list) and allowed and set(allowed)<=set(allowed_stage_clocks()),'Explicit bounded preparation-stage scope required')
    return runtime


def command(args,logfile,cwd,stdin=None):
    argv=[str(x) for x in args]
    if len(argv)>1 and argv[1]=='dump':
        # Numerical dumps must remain pure stdout. GROMACS reminders/errors are
        # independently preserved, never filtered or inserted into vector data.
        stderr_path=logfile.with_name(logfile.name+'.stderr.txt')
        require(not logfile.exists() and not stderr_path.exists(),'Dump capture output already exists; preserve and inspect')
        with logfile.open('x') as log, stderr_path.open('x') as err:
            subprocess.run(argv,input=stdin,text=True,cwd=cwd,stdout=log,stderr=err,check=True)
    else:
        with logfile.open('x') as log:
            subprocess.run(argv,input=stdin,text=True,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    return logfile.read_text(errors='replace')


def issue_scan(text,context):
    bad=[line for line in text.splitlines() if re.search(r'LINCS WARNING|cannot be settled|Fatal error|\bnan\b|\binf\b',line,re.I)
         and not re.fullmatch(r'\s*epsilon-rf\s*=\s*inf\s*',line)]
    require(not bad,f'{context}: {bad[:3]}')


def scalar(text,key):
    values=re.findall(r'^\s*'+re.escape(key)+r'\s*=\s*('+NUMBER+r')\s*$',text,re.M)
    require(len(values)==1,f'Expected one {key} in GROMACS dump; inspect raw output')
    value=float(values[0]); require(math.isfinite(value),f'Non-finite {key}'); return value


def dump_vectors(text,name,count):
    """TPR braced rvecs and GROMACS 2025.4 CPT flat real arrays; no zero fill."""
    braced=re.findall(r'^\s*'+re.escape(name)+r'\[\s*(\d+)\s*\]\s*=\s*\{([^}]+)\}',text,re.M)
    flat=re.findall(r'^\s*'+re.escape(name)+r'\[\s*(\d+)\s*\]\s*=\s*([^\s{},]+)\s*$',text,re.M)
    require(not (braced and flat),f'Mixed {name} dump formats')
    if braced:
        require(len(braced)==count,f'Missing or incomplete {name} vectors in state dump; inspect exact format')
        values=[]
        for expected,(index,row) in enumerate(braced):
            pos=list(map(float,row.split(',')))
            require(int(index)==expected and len(pos)==3 and all(math.isfinite(v) for v in pos),f'Invalid/non-finite {name} vector/order')
            values.append(pos)
        return values
    require(len(flat)==count*3,f'Missing or incomplete {name} vectors in state dump; inspect exact format')
    values=[]
    for expected,(index,row) in enumerate(flat):
        value=float(row)
        require(int(index)==expected and math.isfinite(value),f'Invalid/non-finite {name} scalar/order')
        values.append(value)
    return [values[i:i+3] for i in range(0,len(values),3)]


def coordinates_match(text,gro_path):
    _,xyz,box=read_gro(gro_path); values=dump_vectors(text,'x',len(xyz)); worst=0.
    for pos,ref in zip(values,xyz):
        worst=max(worst,*(abs((a-b)-round((a-b)/L)*L) for a,b,L in zip(pos,ref,box)))
    require(worst<.00061,f'CPT/TPR vs GRO differs beyond PBC and text rounding: {worst} nm'); return worst


def state_match(text,gro_path):
    """Printed x/v/box vs GRO only; not bitwise thermostat/barostat/RNG continuity."""
    maximum_coordinate_error=coordinates_match(text,gro_path)
    ids,_,box=read_gro(gro_path)
    matrix=dump_vectors(text,'box',3)
    for i,row in enumerate(matrix):
        for j,value in enumerate(row):
            if i==j:
                require(value>0 and abs(value-box[i])<=.0000051+abs(value)*.000005,'State/GRO box differs beyond text rounding')
            else:require(abs(value)<=1e-8,'Non-orthorhombic state box cannot use this preparation checker')
    velocity=dump_vectors(text,'v',len(ids)); lines=Path(gro_path).read_text().splitlines()[2:-1]
    maximum_velocity_error=0.
    for row,pos in zip(lines,velocity):
        require(len(row)>=68,'GRO velocities absent; cannot verify checkpoint continuity')
        gro_v=[float(row[i:i+8]) for i in (44,52,60)]
        require(all(math.isfinite(v) for v in gro_v),'Non-finite GRO velocity')
        for a,b in zip(pos,gro_v):
            error=abs(a-b);maximum_velocity_error=max(maximum_velocity_error,error)
            require(error<=.000051+max(abs(a),abs(b))*.000005,'State/GRO velocity differs beyond text rounding')
    return {'maximum_coordinate_error_nm':maximum_coordinate_error,'maximum_velocity_error_nm_ps':maximum_velocity_error,
            'box_and_velocity_finite_and_matched':True,'scope':'Text-precision coordinate/velocity/box check only; not full ensemble or RNG state continuity'}


def dump_tpr(gmx,root,stem,natoms,start,end,reference=None):
    text=command([gmx,'dump','-s',root/f'{stem}.tpr'],root/f'{stem}.tpr.dump.txt',root)
    require(scalar(text,'natoms')==natoms,'TPR atom count')
    tinit,dt,initial,steps=[scalar(text,k) for k in ('tinit','dt','init-step','nsteps')]
    require(abs(tinit+dt*initial-start)<1e-6 and abs(tinit+dt*(initial+steps)-end)<1e-6,'TPR start/end clock mismatch')
    if reference is not None:state_match(text,reference)
    return int(initial+steps)


def checkpoint_check(gmx,root,stem,natoms,time_ps,step=None):
    text=command([gmx,'dump','-cp',root/f'{stem}.cpt'],root/f'{stem}.cpt.dump.txt',root)
    require(scalar(text,'#atoms')==natoms,'Checkpoint atom count')
    require(abs(scalar(text,'t')-time_ps)<1e-5,'Checkpoint time mismatch')
    actual=int(scalar(text,'step'))
    if step is not None:require(actual==step,'Checkpoint step mismatch')
    state_match(text,root/f'{stem}.gro'); return actual


def snapshot(bundle,root,stem):
    output=root/f'{stem}.structure.json'
    command([sys.executable,'-E',bundle/'compute/scripts/check_twf154_snapshot.py',root,root/f'{stem}.gro',bundle/'compute/configs/ligand_geometry_contract.json',output,'--allow-box-change'],root/f'{stem}.structure.log',root)
    require(json.loads(output.read_text())['pass'] is True,'Snapshot gate failed')


def thermo_report(text,start,end):
    legends={}; rows=[]
    for line in text.splitlines():
        match=re.match(r'\s*@\s+s(\d+)\s+legend\s+"([^"]+)"',line)
        if match:legends[int(match[1])+1]=match[2]
        if line.strip() and not line.lstrip().startswith(('#','@')):rows.append(list(map(float,line.split())))
    require(len(rows)>10 and all(len(r)==11 for r in rows),'Thermo row/column count')
    require(all(math.isfinite(v) for r in rows for v in r),'Non-finite thermo')
    require(set(legends)==set(range(1,11)) and set(legends.values())==set(THERMO),'Missing/ambiguous thermo terms')
    require(abs(rows[0][0]-start)<.001 and abs(rows[-1][0]-end)<.001,'EDR endpoint mismatch')
    require(all(abs(b[0]-a[0]-1)<.001 for a,b in zip(rows,rows[1:])),'EDR missing or non-original 1 ps cadence')
    for name in ('Density','Box-X','Box-Y','Box-Z'):
        col=next(i for i,v in legends.items() if v==name); require(all(r[col]>0 for r in rows),f'Nonpositive {name}')
    window=[r for r in rows if r[0]>=max(start,end-500)-1e-6]
    series={name:[r[i] for r in window] for i,name in legends.items()}; avg=lambda a:sum(a)/len(a)
    for name in THERMO[:4]:require(abs(avg(series[name])-303.15)<10,f'Temperature group outside original screen: {name}')
    series['Area-XY']=[x*y for x,y in zip(series['Box-X'],series['Box-Y'])]; drift={}
    for name in ('Density','Area-XY','Box-Z'):
        values=series[name]; half=len(values)//2; drift[name]=abs(avg(values[-half:])-avg(values[:half]))/avg(values)
    return {'thermodynamic_means':{k:avg(v) for k,v in series.items()},'drift_window_start_ps':window[0][0],
            'drift_window_end_ps':window[-1][0],'half_window_fractional_change':drift,
            'box_density_settled':end-start>=500 and all(v<.02 for v in drift.values()),
            'scope':'Preparation drift screen only, not binding or thermodynamic convergence'}


def trajectory_check(text,start,end,natoms,tpr_text):
    dt=scalar(tpr_text,'dt'); initial=scalar(tpr_text,'init-step')
    steps=scalar(tpr_text,'nsteps'); stride=scalar(tpr_text,'nstxout-compressed')
    require(dt>0 and initial==0 and steps>0 and steps.is_integer() and stride>0 and stride.is_integer(),'Invalid original compressed-output schedule')
    require(abs(scalar(tpr_text,'tinit')-start)<1e-6 and abs(start+dt*steps-end)<1e-6,'XTC TPR segment clock mismatch')
    expected=int(steps)//int(stride)+1; interval=dt*stride
    last=start+(expected-1)*interval
    frames=re.findall(r'(?:Reading|Last)\s+frame\s+(\d+)\s+time\s+('+NUMBER+r')',text)
    require(frames and int(frames[0][0])==0 and abs(float(frames[0][1])-start)<.001 and abs(float(frames[-1][1])-last)<.001,'XTC scheduled endpoint missing/wrong')
    require(all(int(i)<expected and abs(float(t)-(start+int(i)*interval))<.001 for i,t in frames),'XTC timestamp differs from original output schedule')
    counts=re.findall(r'#\s*Atoms\s+(\d+)',text); require(counts and all(int(v)==natoms for v in counts),'XTC atom count mismatch')
    require(int(frames[-1][0])+1==expected,'XTC frame count mismatch')
    for key in ('Step','Time','Coords','Box'):
        rows=re.findall(r'^\s*'+key+r'\s+(\d+)\s+('+NUMBER+r')\s*$',text,re.M)
        require(len(rows)==1 and int(rows[0][0])==expected and abs(float(rows[0][1])-interval)<.001,f'XTC {key} summary differs from original output schedule')
    require(not re.search(r'WARNING|Fatal error|Incomplete frame|Number of atoms at',text,re.I),'XTC check warning')
    issue_scan(text,'XTC check')
    require(not re.search(r'Timesteps at',text,re.I),'Unexpected XTC cadence change')
    return {'first_ps':float(frames[0][1]),'last_ps':float(frames[-1][1]),'frames':expected}




def allowed_stage_clocks():
    result={name:(start,end,.001 if name=='npt01' else .002) for name,start,end in STAGES}
    result.update({f'npt_extend{i+1:02d}':(2750.+i*1000,3750.+i*1000,.002) for i in range(4)})
    return result


def validate_launch_tpr(text,prefix,expected_end,natoms,reference):
    require(prefix in allowed_stage_clocks(),'Supervisor is preparation-only')
    start,end,dt=allowed_stage_clocks()[prefix]
    require(expected_end==end,'Supervisor endpoint differs from allowed stage clock')
    require(scalar(text,'natoms')==natoms,'Supervisor TPR atom count differs from selected case')
    require(scalar(text,'dt')==dt and scalar(text,'tinit')==start and scalar(text,'init-step')==0 and scalar(text,'nsteps')==round((end-start)/dt),'Supervisor TPR is not the bounded original preparation stage')
    state_match(text,reference)


def previous_stage(prefix):
    names=['start']+[name for name,_,_ in STAGES]+[f'npt_extend{i+1:02d}' for i in range(4)]
    require(prefix in names[1:],'Invalid preparation stage prefix')
    return names[names.index(prefix)-1]


def active_list_lines(text):
    found=False; lines=[]
    for line in text.splitlines():
        if 'Using a dual 8x4 pair-list setup' in line:found=True;continue
        if found:
            if 'equivalent classical' in line:break
            if 'outer list:' in line or 'inner list:' in line:lines.append(line)
            elif lines:break
    return lines


def runtime_parameters_check(tpr_text,log_text):
    """Verify each case's own compiled PME, not another case's Fourier grid."""
    keys=('fourier-nx','fourier-ny','fourier-nz','pme-order','ewald-rtol','rcoulomb')
    expected={key:scalar(tpr_text,key) for key in keys}
    observed={key:scalar(log_text,key) for key in keys}
    require(expected==observed,'Actual PME/electrostatic parameters differ from this case TPR')
    require(all(expected[key]>0 and expected[key].is_integer() for key in keys[:4]),'Invalid compiled PME grid/order')
    require(expected['rcoulomb']==1.2 and expected['ewald-rtol']==1e-5,'Original qualified Ewald/cutoff settings changed; review before continuing')
    widths=re.findall(r'Using a Gaussian width \(1/beta\) of ('+NUMBER+r') nm for Ewald',log_text)
    require(len(widths)==1 and abs(float(widths[0])-.384195)<=.000001,'Inverse beta differs from reviewed original electrostatics')
    for required in ('-notunepme','Using 1 MPI process','Using 8 OpenMP threads','PP task will update and constrain coordinates on the GPU','PME tasks will do all aspects on the GPU','Using GPU 8x4 nonbonded short-range kernels'):
        require(required in log_text,f'Reviewed backend not confirmed: {required}')
    require('PP tasks will do (non-perturbed) short-ranged and most bonded interactions on the GPU' in log_text,'Reviewed bonded/NB GPU backend not confirmed')
    require(not re.search(r'PME tuning|timed with pme grid|Optimal PME grid',log_text,re.I),'Unexpected PME tuning in runtime')
    return {'pme_grid':[int(expected[k]) for k in keys[:3]],'pme_order':int(expected['pme-order']),
            'rcoulomb_nm':expected['rcoulomb'],'ewald_rtol':expected['ewald-rtol'],'inverse_beta_nm':float(widths[0]),
            'grid_policy':'case_original_grompp_grid','pme_tuning':False,'ranks':1,'threads':8,
            'offload':'NB/PME/bonded/update GPU; CMAP CPU fallback retained','production_ready':False,
            'active_neighbor_list_lines':active_list_lines(log_text),'neighbor_list_adaptation_lines':[line for line in log_text.splitlines() if 'Changing nstlist' in line]}


def initialize(bundle,root,plan,gmx):
    preflight_new_outputs(root,('initial_checks.json','initial_complete.json',*INITIAL_EVIDENCE,'em.audit*','start.structure*'))
    write(root/'initial_checks.json',{'state':'CHECKING','version':VERSION,'production_ready':False})
    version=command([gmx,'--version'],root/'gromacs_identity.txt',root)
    for pattern in (r'GROMACS version:\s+2025\.4',r'Precision:\s+mixed',r'MPI library:\s+MPI\s*$',r'OpenMP support:\s+enabled',r'CUDA runtime:\s+12\.9'):
        require(re.search(pattern,version,re.M),'Expected A runtime not found')
    dump_tpr(gmx,root,'source_hold',plan['atom_count'],50.,125.)
    checkpoint_check(gmx,root,'start',plan['atom_count'],125.,75000)
    # Preprocess only: never rerun EM from pre-repair ionized.gro.
    text=command([gmx,'grompp','-f','em.mdp','-c','ionized.gro','-r','ionized.gro','-p','topol.top','-n','index.ndx','-o','em.audit.tpr','-po','em.audit.mdout.mdp','-pp','em.processed.top'],root/'em.audit.grompp.log',root)
    require(not re.search(r'WARNING\s+\d+',text),'Neutral topology grompp warning')
    snapshot(bundle,root,'start')
    evidence={n:sha(root/n) for n in INITIAL_EVIDENCE}
    validate_manifest(root,evidence,INITIAL_EVIDENCE)
    write(root/'initial_complete.json',{'case_id':plan['case_id'],'replicate':1,'version':VERSION,'production_ready':False,'evidence_sha256':evidence})


def execute(bundle,root,plan,gate,gmx,maxh,stop_after=None):
    require(plan.get('case_id')=='native_wt_ascr18','v2.3 adapter is restricted to the original nativeWT rep1 continuation')
    require(stop_after in {n for n,_,_ in STAGES[1:]},'Continuation requires explicit --stop-after npt02, npt03, npt04, or npt05; never rerun NPT01')
    root=checked_workdir(bundle,root)
    require(root.is_dir(),'Continuation requires the existing completed rep1 workdir')
    require(gate is not None and gate.is_file(),'Fresh single-stage continuation gate required')
    require(json.loads(gate.read_text()).get('allowed_stages')==[stop_after],'Gate must authorize exactly the requested stop stage')
    for prior,_,_ in STAGES[:[n for n,_,_ in STAGES].index(stop_after)]:
        require((root/f'{prior}.validated.json').is_file(),f'Previous stage not validated: {prior}; no first-stage rerun')
    gmx=gmx.resolve()
    gate_check(gate,plan,gmx)  # Must precede any external program or materialization.
    if not root.exists():materialize(bundle,root,plan)
    inputs=json.loads((root/'preparation_inputs.json').read_text())
    require(inputs['source_sha256']==plan['source_sha256'],'Materialized source plan changed')
    require(inputs.get('case_id')==plan['case_id'],'Materialized case identity mismatch')
    expected=fixed_expected_hashes(bundle,plan)
    validate_manifest(root,inputs.get('fixed_files_sha256'),set(expected))
    require(inputs['fixed_files_sha256']==expected,'Fixed-input hashes differ from authoritative source')
    with (root/'equilibration.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        require(not (root/'initial_checks.json').exists() or (root/'initial_complete.json').exists(),'Incomplete initial validation; preserve and inspect')
        if not (root/'initial_complete.json').exists():initialize(bundle,root,plan,gmx)
        initial=json.loads((root/'initial_complete.json').read_text())
        require(initial.get('case_id')==plan['case_id'] and initial.get('replicate')==1,'Initial validation identity mismatch')
        validate_manifest(root,initial.get('evidence_sha256'),INITIAL_EVIDENCE)
        previous='start'; results=[]
        def stage(name,start,end,extension=False):
            nonlocal previous
            validated=root/f'{name}.validated.json'
            if validated.exists():
                result=json.loads(validated.read_text())
                require(result.get('pass_stage') is True and result.get('case_id')==plan['case_id'] and result.get('replicate')==1 and result.get('stage')==name and result.get('start_ps')==start and result.get('end_ps')==end,'Saved stage identity mismatch')
                validate_manifest(root,result.get('output_sha256'),stage_output_names(name))
                if name=='npt01':validate_npt01_import(root,result)
                expected_runtime=runtime_parameters_check((root/f'{name}.tpr.dump.txt').read_text(),(root/f'{name}.log').read_text())
                require(json.loads((root/f'{name}.runtime.json').read_text())==expected_runtime,'Saved runtime summary differs from verified TPR/log')
                verified_thermo=thermo_report((root/f'{name}.thermo.xvg').read_text(),start,end)
                require(all(result.get(k)==v for k,v in verified_thermo.items()),'Saved thermo summary differs from actual verified series')
                verified_trajectory=trajectory_check((root/f'{name}.xtc.check.txt').read_text(),start,end,plan['atom_count'],(root/f'{name}.tpr.dump.txt').read_text())
                require(result.get('trajectory')==verified_trajectory,'Saved trajectory summary differs from actual original output schedule')
                previous=name; results.append(result); return result
            require(not (root/f'{name}.tpr').exists(),f'{name} incomplete: no blind rerun; validate/continue checkpoint explicitly')
            preflight_new_outputs(root,(name+'*','audit.'+name+'.*'),() if extension else (name+'.mdp',))
            runtime=gate_check(gate,plan,gmx)
            require(name in json.loads(gate.read_text())['allowed_stages'],f'Stage outside reviewed gate scope: {name}')
            require(shutil.disk_usage(root).free>=5e9,'Below 5 GB preparation reserve')
            if extension:
                template=(bundle/'compute/mdp/npt05.mdp').read_text()
                text,count=re.subn(r'^tinit\s*=.*$',f'tinit = {start:g}',template,flags=re.M); require(count==1,'Extension time rewrite')
                with (root/f'{name}.mdp').open('x') as f:f.write(text)
            args=[gmx,'grompp','-f',f'{name}.mdp','-c',f'{previous}.gro','-t',f'{previous}.cpt']
            if name in ('npt01','npt02','npt03','npt04'):args+=['-r','start.gro']
            args+=['-p','topol.top','-n','index.ndx','-o',f'{name}.tpr','-po',f'{name}.mdout.mdp','-pp',f'{name}.processed.top']
            # Prefix audit.* avoids run_stage.py's prefix*.log output guard.
            text=command(args,root/f'audit.{name}.grompp.log',root)
            require(not re.search(r'WARNING\s+\d+',text),'Final grompp warning; no maxwarn')
            original=mdp((root/f'{name}.mdp').read_text()); actual=mdp((root/f'{name}.mdout.mdp').read_text())
            for key,value in original.items():require(same_mdp_value(actual.get(key,''),value),f'MDP readback changed {key}')
            if name=='npt05' or extension:
                require(not re.search(r'^\s*\[\s*(position_restraints|dihedral_restraints)\s*\]',(root/f'{name}.processed.top').read_text(),re.M),'Unrestrained phase contains restraints')
            final_step=dump_tpr(gmx,root,name,plan['atom_count'],start,end,root/f'{previous}.gro')
            runtime=gate_check(gate,plan,gmx)
            require(name in json.loads(gate.read_text())['allowed_stages'],f'Stage outside current gate scope: {name}')
            shutil.copy2(gate,root/f'audit.{name}.gate.json')
            command([sys.executable,Path(__file__).resolve().parent/'run_stage_v3_locked.py','--case',plan['case_id'],'--stage','npt','--workdir',root,'--tpr',root/f'{name}.tpr','--prefix',name,'--gmx',gmx,'--threads',runtime['threads'],'--offload',runtime['offload'],'--maxh',maxh,'--expected-end-ps',end,'--min-free-gb',5,'--gate',gate],root/f'audit.{name}.supervisor.log',root)
            text=(root/f'{name}.log').read_text(); issue_scan(text,name); require('Finished mdrun' in text,'No normal closure')
            runtime_record=runtime_parameters_check((root/f'{name}.tpr.dump.txt').read_text(),text)
            write(root/f'{name}.runtime.json',runtime_record)
            times=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+('+NUMBER+r')',text)
            require(times and int(times[-1][0])==final_step and abs(float(times[-1][1])-end)<.001,'Segment ended early; do not advance')
            checkpoint_check(gmx,root,name,plan['atom_count'],end,final_step); snapshot(bundle,root,name)
            check=command([gmx,'check','-f',root/f'{name}.xtc'],root/f'{name}.xtc.check.txt',root)
            trajectory=trajectory_check(check,start,end,plan['atom_count'],(root/f'{name}.tpr.dump.txt').read_text())
            check=command([gmx,'check','-e',root/f'{name}.edr'],root/f'{name}.edr.check.txt',root)
            issue_scan(check,'EDR check'); require(not re.search(r'WARNING|Incomplete|Timesteps at',check,re.I),'EDR check warning')
            command([gmx,'energy','-f',root/f'{name}.edr','-o',root/f'{name}.thermo.xvg'],root/f'{name}.energy.log',root,'\n'.join(THERMO)+'\n0\n')
            result=thermo_report((root/f'{name}.thermo.xvg').read_text(),start,end)
            result.update(case_id=plan['case_id'],replicate=1,version=VERSION,stage=name,start_ps=start,end_ps=end,trajectory=trajectory,pass_stage=True,production_ready=False)
            result['output_sha256']={p.name:sha(p) for p in list(root.glob(name+'*'))+list(root.glob('audit.'+name+'.*')) if p.is_file()}
            validate_manifest(root,result['output_sha256'],stage_output_names(name))
            write(validated,result); previous=name; results.append(result); return result
        for name,start,end in STAGES:
            result=stage(name,start,end)
            if stop_after==name:
                paused={'case_id':plan['case_id'],'replicate':1,'version':VERSION,'stage':name,'end_ps':end,'stage_validated':True,'preparation_complete':False,'production_ready':False,'stage_validation_sha256':sha(root/f'{name}.validated.json')}
                destination=root/f'controlled_stop_after_{name}.json'
                if destination.exists():require(json.loads(destination.read_text())==paused,'Changed saved controlled stop')
                else:write(destination,paused)
                return paused
        for i in range(4):
            if result['box_density_settled']:break
            start=result['end_ps']; result=stage(f'npt_extend{i+1:02d}',start,start+1000.,True)
        require(result['box_density_settled'],'Still drifting after four 1 ns extensions; stop and inspect')
        complete={'version':VERSION,'case_id':plan['case_id'],'replicate':1,'preparation_pass':True,'final_prefix':previous,'final_time_ps':result['end_ps'],
                  'final_gro_sha256':sha(root/f'{previous}.gro'),'final_cpt_sha256':sha(root/f'{previous}.cpt'),
                  'validated_stages':[r['stage'] for r in results],'production_ready':False,'next':'Separate numerical/restart/resource/storage/source gates; no production TPR or production run'}
        path=root/'preparation_complete.json'
        if path.exists():require(json.loads(path.read_text())==complete,'Changed saved completion')
        else:write(path,complete)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parents[2]); p.add_argument('--case',choices=CASES,required=True)
    modes=p.add_mutually_exclusive_group(); modes.add_argument('--materialize',action='store_true'); modes.add_argument('--execute',action='store_true')
    p.add_argument('--workdir',type=Path); p.add_argument('--gate',type=Path); p.add_argument('--gmx',type=Path,default=Path(VERIFIED_GMX))
    p.add_argument('--stop-after',choices=[n for n,_,_ in STAGES],help='Validate this full original stage, then stop without starting the next stage')
    p.add_argument('--maxh',type=float,default=12.); p.add_argument('--plan-output',type=Path)
    a=p.parse_args(); bundle=a.bundle.resolve(); plan=verify_sources(bundle,a.case)
    root=checked_workdir(bundle,a.workdir if a.workdir else bundle/'runs'/a.case/'rep1')
    require(0<a.maxh<=12,'maxh outside supervisor bounds'); plan['workdir']=str(root)
    if a.plan_output:write(a.plan_output,plan)
    if a.materialize:materialize(bundle,root,plan); plan['mode']='MATERIALIZED_ONLY'
    if a.execute:
        # Share the original global serial lock while old and new drivers coexist.
        with (bundle/'operator_records/equilibration_prep_v2_2_2/serial.lock').open('a') as serial:
            fcntl.flock(serial,fcntl.LOCK_EX|fcntl.LOCK_NB)
            stopped=execute(bundle,root,plan,a.gate.resolve() if a.gate else None,a.gmx.resolve(),a.maxh,a.stop_after)
        plan['mode']='PREPARATION_STAGE_VALIDATED' if stopped else 'PREPARATION_COMPLETE_PRODUCTION_BLOCKED'
        if stopped:plan['controlled_stop']=stopped
    print(json.dumps(plan,ensure_ascii=False,indent=2))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(f'STOP: {exc}',file=sys.stderr); raise SystemExit(1)
