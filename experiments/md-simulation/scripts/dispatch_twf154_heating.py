#!/usr/bin/env python3
"""One-shot bounded heating dispatcher for the already authorized 12 cases."""
from datetime import datetime,timezone
import argparse
import json
from pathlib import Path
import subprocess
import time


def run(cmd,**kwargs):return subprocess.run(cmd,text=True,**kwargs)


def active(root):
    jobs=[]
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:
            cwd=(proc/'cwd').resolve();cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
        except (OSError,UnicodeDecodeError):continue
        fields=cmd.split()
        heating_runner=len(fields)>1 and fields[0].endswith('bash') and ('run_twf154_heating_v' in fields[1] or ('run_twf154_preheat_case_v' in fields[1] and 'heat_gpu' in fields))
        if str(cwd).startswith(str(root/'runs')+'/') and (' mdrun ' in cmd or heating_runner):
            jobs.append({'pid':int(proc.name),'cwd':str(cwd),'gpu':'-nb gpu' in cmd or heating_runner,
                         'role':'heating_runner' if heating_runner else 'mdrun'})
    return jobs


def main():
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();r=a.root.resolve()
    cases=[f'{state}_{genotype}_{ligand}' for genotype,ligand in [('n84v','ascr18'),('v368r','ascr3'),('n84v','ascr3'),('v368r','ascr18'),('wt','ascr18'),('wt','ascr3')] for state in ['rebuilt','raw']]
    launched=set();inspected={};started=time.time()
    while time.time()-started<12*3600:
        jobs=active(r)
        # Reserve a slot during grompp / phase transitions as well as mdrun.
        ngpu=len({Path(j['cwd']).relative_to(r/'runs').parts[0] for j in jobs if j['gpu']});status={};pending=[]
        for name in cases:
            c=r/'runs'/name
            if (c/'hold.gro').exists() or (c/'heating_v4/hold.gro').exists():status[name]='heating_output_present';continue
            if (c/'heat.tpr').exists() or (c/'heating_v4').exists() or name in launched:status[name]='heating_launched';continue
            source=None
            for emdir in [c/'attempt5_frozen_ligand',c/'attempt4_ligand_constraints',c/'attempt2_double',c]:
                em=emdir/'em.gro';gate=emdir/'em_gate.json'
                if not em.exists() or not gate.exists():continue
                try:force=json.loads(gate.read_text()).get('fmax_kj_mol_nm',float('inf'))
                except (ValueError,OSError):continue
                if not 0<=force<=1000:continue
                key=(str(em),em.stat().st_mtime_ns)
                if key not in inspected:
                    out=emdir/'em_snapshot_qc_v5.json'
                    with (emdir/'snapshot_qc_v5.log').open('w') as h:
                        result=run(['python3',str(r/'scripts/check_twf154_snapshot_v5.py'),str(c),str(em),str(r/'inputs/ligand_geometry_contract_v2.json'),str(out)],stdout=h,stderr=subprocess.STDOUT)
                    inspected[key]=result.returncode==0
                if inspected[key]:source=str(em.relative_to(c));break
            status[name]='EM_ready' if source else 'await_valid_EM'
            if source:pending.append((name,source))
        report={'time_utc':datetime.now(timezone.utc).isoformat(),'cases':status,'active_jobs':jobs,'max_gpu_heatings':4,'launched_by_dispatcher':sorted(launched)}
        tmp=r/'logs/heating_dispatch_status.tmp';tmp.write_text(json.dumps(report,indent=2));tmp.replace(r/'logs/heating_dispatch_status.json')
        if all(v=='heating_output_present' for v in status.values()):break
        if ngpu<4 and pending:
            free=int(run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],capture_output=True,check=True).stdout.splitlines()[0])
            if free>=2560:
                name,source=pending[0];log=r/'logs'/f'{name}_automatic_heat_dispatch.log'
                # Fixed internal identifiers and paths contain no shell metacharacters.
                command=f'bash {r}/scripts/run_twf154_heating_v8.sh {r} {name} {source} > {log} 2>&1'
                run(['tmux','new-session','-d','-s',f'twf154_{name}_autoheat',command],check=True);launched.add(name)
        time.sleep(45)


if __name__=='__main__':main()
