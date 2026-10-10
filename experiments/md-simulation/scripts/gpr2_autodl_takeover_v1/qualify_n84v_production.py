#!/usr/bin/env python3
"""Own N84V new-start/restart prerequisite only; no production release or MD by default.

Execute only after the original NPT05 has passed and its final drift screen is
settled. Uses the existing qualified runtime and frozen source validators.
The new production TPR is immutable. The diagnostic TPR differs only in nsteps.
"""
import argparse
from contextlib import ExitStack
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
import subprocess
import sys

sys.dont_write_bytecode = True
CASE = 'raw_n84v_ascr18'
WORK_REL = 'runs/raw_n84v_ascr18/rep1_codex_v1'
ADDON_REL = 'operator_records/equilibration_prep_next_gate_v1_1/refresh_native_wt_later_gate.py'
# Filled from the unchanged, already-reviewed addon when packaging.
ADDON_SHA = '8b03a17c6abbaa45e76dcb463f6039c11ae20dbb20e92bd79752d1f7f52eed3b'
MDP_SHA = 'c19c76f41c5cd0ef3523f438a5bb84927989b2e195271dcd2f6f8d7bd03e8d6f'
NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def load_validators(bundle):
    path = bundle / ADDON_REL
    require(sha(path) == ADDON_SHA, 'Reviewed later-gate addon changed')
    spec = importlib.util.spec_from_file_location('wt_existing_gate', path)
    addon = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(addon)
    core, code = addon.load_core(bundle)
    return addon, core, code


def validate_inputs(bundle,work,core):
    require(work==bundle/WORK_REL,'Wrong own N84V zero-start directory')
    report=json.loads((work/'source_preflight.json').read_text())
    require(report['case_id']==CASE and report['source_preparation_ps']==2750 and report['production_clock_ps']==[0,100000],'Wrong preflight source purpose')
    require(report['structure']['pass'] is True and report['preparation_evidence']['box_density_settled'] is True,'Own prepared geometry or drift failed')
    for name,digest in report['source_sha256'].items():require(sha(bundle/name)==digest,'Immutable own source changed')
    require(report['production_tpr_sha256']==sha(work/'production.tpr'),'Production TPR changed')
    require(sha(work/'production.tpr')==sha(bundle/'compute/cases'/CASE/'zero_start_100ns/production.tpr'),'Not frozen own production input')
    require(sha(work/'production.mdp')==MDP_SHA,'Original production MDP changed')
    for pattern in ('raw_n84v_ascr18_rep1_production*.log','raw_n84v_ascr18_rep1_production*.cpt','production.log','production.cpt'):
        require(not list(work.glob(pattern)),'Production already exists; do not rerun qualifier')
    return report


def run(args, out, name, stdin=None, timeout=300):
    argv = [str(a) for a in args]
    save(out / (name + '.command.json'), {'argv': argv, 'cwd': str(out), 'started_at': datetime.now(timezone.utc).isoformat()})
    with (out / (name + '.stdout.txt')).open('x') as stdout, (out / (name + '.stderr.txt')).open('x') as stderr:
        proc = subprocess.Popen(argv, cwd=out, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL, stdout=stdout, stderr=stderr, env=dict(os.environ, OMP_NUM_THREADS='8', OPENBLAS_NUM_THREADS='1'))
        try:
            proc.communicate(stdin.encode() if stdin is not None else None, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            raise RuntimeError(name + ': exceeded bounded time; preserve partial outputs and inspect checkpoint')
    require(proc.returncode == 0, name + ': subprocess failed; inspect original stdout/stderr')
    return (out / (name + '.stdout.txt')).read_text(), (out / (name + '.stderr.txt')).read_text()


def normalized_dump(text):
    rows = text.splitlines()
    require(rows and rows[0].endswith('.tpr:'), 'Unknown TPR dump header')
    return re.sub(r'^\s*nsteps\s*=.*$', 'nsteps = LENGTH_ONLY', '\n'.join(rows[1:]), flags=re.M)


def scientific_prefix(text):
    require(text.count('\nbox (3x3):') == 1, 'Unknown scientific/state TPR boundary')
    head = text.split('\nbox (3x3):', 1)[0]
    lines = head.splitlines()
    require(lines[0].endswith('.tpr:'), 'Unknown TPR header')
    # Clock/seed change for the original new stage; neighbor/PME dimensions are
    # grompp-derived from this stage's own box. All force/coupling/topology fields
    # and every group assignment remain covered by the exact comparison.
    omitted = ('tinit','nsteps','ld-seed','rlist','fourier-nx','fourier-ny','fourier-nz')
    return '\n'.join(line for line in lines[1:] if not any(re.match(r'^\s*'+key+r'\s*=',line) for key in omitted))


def verify_production_tpr(core,text,checkpoint,work):
    require(sha(work/'production.tpr')==json.loads((work/'source_preflight.json').read_text())['production_tpr_sha256'],'Frozen TPR identity changed')
    for key,value in {'natoms':146032,'tinit':0,'init-step':0,'dt':.002,'nsteps':50000000,'nstxout':0,'nstvout':0,'nstfout':0,'nstxout-compressed':5000,'nstenergy':500,'nstlog':5000}.items():require(core.scalar(text,key)==value,'Original production field mismatch: '+key)
    require(core.scalar(checkpoint,'#atoms')==146032 and core.scalar(checkpoint,'t')==2750,'Not the own accepted preparation CPT')
    core.state_match(text,work/'npt05.gro');core.state_match(checkpoint,work/'npt05.gro')
    errors={}
    for field,count in (('x',146032),('v',146032),('box',3)):
        left=core.dump_vectors(text,field,count);right=core.dump_vectors(checkpoint,field,count)
        require(all(abs(a-b)<=1e-7+1e-5*max(abs(a),abs(b)) for x,y in zip(left,right) for a,b in zip(x,y)),'Source state differs: '+field)
        errors[field]=max(abs(a-b) for x,y in zip(left,right) for a,b in zip(x,y))
    return errors


def one(out, pattern):
    paths = list(out.glob(pattern))
    require(len(paths) == 1, 'Expected exactly one file: ' + pattern)
    return paths[0]


def validate_xtc(core, text, start, end):
    expected = round((end-start)/10) + 1
    frames = re.findall(r'(?:Reading|Last)\s+frame\s+(\d+)\s+time\s+(' + NUMBER + ')', text)
    require(frames and int(frames[0][0]) == 0 and abs(float(frames[0][1])-start) < .001 and int(frames[-1][0])+1 == expected and abs(float(frames[-1][1])-end) < .001, 'Diagnostic XTC endpoint/frame count differs')
    require(all(int(i)<expected and abs(float(t)-(start+10*int(i))) < .001 for i,t in frames), 'Wrong diagnostic XTC schedule')
    counts = re.findall(r'#\s*Atoms\s+(\d+)',text)
    require(counts and all(int(n)==146032 for n in counts), 'Wrong XTC atom count')
    for key in ('Step','Time','Coords','Box'):
        rows = re.findall(r'^\s*'+key+r'\s+(\d+)\s+('+NUMBER+r')\s*$',text,re.M)
        require(len(rows)==1 and int(rows[0][0])==expected and abs(float(rows[0][1])-10)<.001, 'Wrong XTC ' + key + ' summary')
    require(not re.search(r'WARNING|Fatal error|Incomplete frame|Number of atoms at|Timesteps at',text,re.I), 'XTC issue')
    core.issue_scan(text, 'Diagnostic XTC')
    return {'first_ps':start, 'last_ps':end, 'frames':expected, 'atoms':146032}


def validate_segment(bundle, work, out, core, gmx, prefix, start, end, tpr_dump):
    logfile = one(out, prefix + '*.log')
    text = logfile.read_text()
    core.issue_scan(text+'\n'+(out/('run_'+prefix+'.stdout.txt')).read_text()+'\n'+(out/('run_'+prefix+'.stderr.txt')).read_text(), prefix)
    require('Finished mdrun' in text, 'Missing normal MD closure')
    runtime = core.runtime_parameters_check(tpr_dump, text)
    times = re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+('+NUMBER+')', text)
    require(times and int(times[0][0]) == round(start/.002) and abs(float(times[0][1])-start) < .001, 'Diagnostic initial step/time differs')
    require(times and int(times[-1][0]) == round(end/.002) and abs(float(times[-1][1])-end) < .001, 'Diagnostic ended early or wrong clock')
    cpt, _ = run([gmx,'dump','-cp',out/(prefix+'.cpt')], out, prefix+'.checkpoint_dump')
    require(core.scalar(cpt,'#atoms')==146032 and core.scalar(cpt,'step')==round(end/.002) and core.scalar(cpt,'t')==end, 'Diagnostic CPT endpoint differs')
    core.state_match(cpt, one(out,prefix+'*.gro'))
    check = run([gmx,'check','-f',one(out,prefix+'*.xtc')],out,prefix+'.xtc_check')
    trajectory = validate_xtc(core, '\n'.join(check), start, end)
    check = run([gmx,'check','-e',one(out,prefix+'*.edr')],out,prefix+'.edr_check')
    core.issue_scan('\n'.join(check),'Diagnostic EDR')
    require(not re.search(r'WARNING|Incomplete|Timesteps at','\n'.join(check),re.I),'EDR issue')
    run([gmx,'energy','-f',one(out,prefix+'*.edr'),'-o',out/(prefix+'.thermo.xvg')],out,prefix+'.energy','\n'.join(core.THERMO)+'\n0\n')
    thermo = core.thermo_report((out/(prefix+'.thermo.xvg')).read_text(),start,end)
    run([sys.executable,'-E',bundle/'compute/scripts/check_twf154_snapshot.py',work,one(out,prefix+'*.gro'),bundle/'compute/configs/ligand_geometry_contract.json',out/(prefix+'.structure.json'),'--allow-box-change'],out,prefix+'.structure')
    require(json.loads((out/(prefix+'.structure.json')).read_text())['pass'] is True,'Diagnostic structure screen failed')
    return {'runtime':runtime,'trajectory':trajectory,'thermo':thermo}


def thermo_endpoint(text, last):
    names = {int(i)+1:name for i,name in re.findall(r'@\s+s(\d+)\s+legend\s+"([^"]+)"',text)}
    rows = [list(map(float,line.split())) for line in text.splitlines() if line.strip() and not line.lstrip().startswith(('#','@'))]
    row = rows[-1] if last else rows[0]
    require(abs(row[0]-20)<.001 and all(math.isfinite(v) for v in row), 'Missing finite thermo restart seam')
    return {name:row[i] for i,name in names.items()}


def fresh_enough(live):
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(live['utc'])).total_seconds()
    require(0<=age<=900, 'Live preflight older than 15 minutes; stop and refresh before MD')


def execute(bundle, work, out, addon, core, code):
    require(not out.exists() and out.is_relative_to(bundle/'operator_records') and not out.is_relative_to(Path(__file__).resolve().parent), 'Use a new separate operator_records output directory')
    out.mkdir(parents=True, exist_ok=False)
    gmx, numeric, live = addon.fresh_resources(core, code, bundle, out)
    save(out/'live_preflight.json',live)
    original = work/'production.tpr'
    original_sha = sha(original)
    source_cpt_sha = sha(work/'npt05.cpt')
    prod_dump,_ = run([gmx,'dump','-s',original],out,'production_tpr_dump')
    cpt_dump,_ = run([gmx,'dump','-cp',work/'npt05.cpt'],out,'npt05_checkpoint_dump')
    state = verify_production_tpr(core,prod_dump,cpt_dump,work)
    run([gmx,'convert-tpr','-s',original,'-nsteps','15000','-o',out/'smoke.tpr'],out,'length_only_tpr')
    smoke_dump,_ = run([gmx,'dump','-s',out/'smoke.tpr'],out,'smoke_tpr_dump')
    require(core.scalar(smoke_dump,'nsteps')==15000 and normalized_dump(prod_dump)==normalized_dump(smoke_dump),'Diagnostic TPR changed more than length')
    smoke_sha = sha(out/'smoke.tpr')
    common = [gmx,'mdrun','-s',out/'smoke.tpr','-ntomp','8','-pin','off','-notunepme','-nb','gpu','-pme','gpu','-bonded','gpu','-update','gpu','-cpt','5','-maxh','0.05']
    fresh_enough(live)
    run([*common,'-deffnm','segment0','-nsteps','10000','-cpo','segment0.cpt'],out,'run_segment0')
    first = validate_segment(bundle,work,out,core,gmx,'segment0',0.,20.,smoke_dump)
    snapshot=out/'accepted_20ps.cpt'
    shutil.copyfile(out/'segment0.cpt',snapshot)
    snapshot_sha=sha(snapshot)
    require(shutil.disk_usage(out).free>=5_000_000_000,'Below 5 GB reserve before diagnostic restart')
    # NO -nsteps on continuation: smoke.tpr already owns the absolute 15000 endpoint.
    require(snapshot.is_file() and sha(snapshot)==snapshot_sha and sha(out/'smoke.tpr')==smoke_sha, 'Missing/changed restart checkpoint or TPR')
    fresh_enough(live)
    stdout,stderr=run([*common,'-deffnm','restart','-cpi',snapshot,'-noappend','-cpo','restart.cpt'],out,'run_restart')
    require(re.search(r'continuing from step\s+10000\s*,\s*20(?:\.0*)?\s+ps',stdout+'\n'+stderr+'\n'+one(out,'restart*.log').read_text(),re.I),'Restart did not confirm own 20 ps checkpoint')
    second=validate_segment(bundle,work,out,core,gmx,'restart',20.,30.,smoke_dump)
    # Compare the common XTC seam without changing diagnostic output settings.
    for prefix in ('segment0','restart'):
        run([gmx,'trjconv','-s',out/'smoke.tpr','-f',one(out,prefix+'*.xtc'),'-dump','20','-o',out/(prefix+'.seam.gro')],out,prefix+'.seam','0\n')
    left=core.read_gro(out/'segment0.seam.gro');right=core.read_gro(out/'restart.seam.gro')
    require(left==right,'20 ps restart seam differs at XTC/GRO text precision')
    before=thermo_endpoint((out/'segment0.thermo.xvg').read_text(),True)
    after=thermo_endpoint((out/'restart.thermo.xvg').read_text(),False)
    seam_delta={name:after[name]-before[name] for name in before}
    require(sha(original)==original_sha and sha(work/'npt05.cpt')==source_cpt_sha and sha(out/'smoke.tpr')==smoke_sha and sha(snapshot)==snapshot_sha,'Immutable source/diagnostic state changed')
    result={'status':'PASS_NEW_START_AND_CPT_RESTART_ONLY','case_id':CASE,'replicate':1,'production_tpr_sha256':original_sha,'production_mdp_sha256':MDP_SHA,'source_npt05_cpt_sha256':source_cpt_sha,'smoke_tpr_sha256':smoke_sha,'only_tpr_change':'nsteps: 50000000 -> 15000; all other dump fields identical','source_x_v_box_dump_precision_max_errors':state,'first_segment':first,'restart_segment':second,'restart_checkpoint_sha256':snapshot_sha,'xtc_restart_seam_20ps_equal_at_text_precision':True,'thermo_restart_minus_original_at_20ps':seam_delta,'thermo_seam_review':'Report differences for scientific review; no new absolute-energy or pressure-equality threshold is invented','restart_test':True,'production_release':False,'numerical_compatibility':'Requires documented N84V-specific synthesis of existing numerical review, own NPT evidence and this result; not automatically granted','production_progress_ns':0,'diagnostic_trajectory_not_for_production':True,'new_cpu_gpu_matrix_performed':False,'finished_at':datetime.now(timezone.utc).isoformat()}
    result['source_provenance']={str(p):sha(p) for p in (Path(__file__).resolve(),bundle/ADDON_REL,code/'prepare_equilibration.py',work/'source_preflight.json',work/'npt05.structure.json')}
    result['evidence_sha256']={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    save(out/'qualification_result.json',result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--workdir',type=Path,required=True)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    bundle=args.bundle.absolute();work=args.workdir.absolute()
    require('..' not in bundle.parts and '..' not in work.parts and not any(p.is_symlink() for p in (bundle,*bundle.parents,work,*work.parents)), 'Unsafe source path')
    require(work==bundle/WORK_REL,'Wrong own N84V rep1 workdir')
    addon,core,code=load_validators(bundle)
    if not args.execute:
        print(json.dumps({'mode':'PLAN_ONLY','case_id':CASE,'workdir':str(work),'required_completed_stage':'Original NPT05 1750–2750 ps, own final <2% drift screen','required_production_files':['production.mdp','production.mdout.mdp','production.processed.top','production.tpr','audit.production.grompp.log'],'diagnostic_intervals_ps':[[0,20],[20,30]],'production_release':False,'writes_or_external_commands':False},indent=2))
        return
    require(args.out is not None,'--execute requires a new --out')
    out=args.out.absolute()
    require('..' not in out.parts and not any(p.is_symlink() for p in (out,*out.parents)),'Unsafe diagnostic output path')
    with ExitStack() as stack:
        for path in (bundle/'operator_records/codex_scheduler.lock',bundle/'operator_records/equilibration_prep_v2_2_2/serial.lock',work/'equilibration.lock',work/'stage.lock'):
            stream=stack.enter_context(path.open('a'))
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        validate_inputs(bundle,work,core)
        result=execute(bundle,work,out,addon,core,code)
    print(json.dumps({k:result[k] for k in ('status','production_tpr_sha256','restart_test','production_release','production_progress_ns')},indent=2))


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        raise SystemExit('STOP: '+str(exc))
