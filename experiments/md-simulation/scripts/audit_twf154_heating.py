#!/usr/bin/env python3
"""Audit completed preparation stages and export compact review snapshots."""
from datetime import datetime,timezone
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();r=a.root.resolve()
    out=r/'results';out.mkdir(exist_ok=True);snapshots=out/'snapshots';snapshots.mkdir(exist_ok=True)
    gm='/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi'
    reports=[]
    for case in sorted((r/'runs').iterdir()):
        if not (case/'input_contract.json').exists():continue
        info=json.loads((case/'input_contract.json').read_text());entry={'case':case.name,'status':'not_completed'}
        diagnostic=(case/'heating_rejected_input').exists()
        assert not (diagnostic and (case/'heating_v4').exists())
        stage=case/'heating_rejected_input' if diagnostic else (case/'heating_v4' if (case/'heating_v4').exists() else case)
        if (stage/'hold.gro').exists() and (stage/'hold.edr').exists():
            for args,log,data in [(['energy','-f',str(stage/'hold.edr'),'-b','105','-o',str(stage/'final20ps_groups.xvg')],'final20ps_groups.log','Potential\nTemperature\nT-SOLU\nT-MEMB\nT-SOLV\n0\n'),(['check','-f',str(stage/'hold.xtc')],'hold.check.log',None)]:
                with (stage/log).open('w') as h:subprocess.run([gm,*args],input=data,text=True,stdout=h,stderr=subprocess.STDOUT,check=True)
            qc=stage/'hold_snapshot_qc_v5.json'
            with (stage/'hold_snapshot_qc_v5.log').open('w') as h:
                result=subprocess.run(['python3',str(r/'scripts/check_twf154_snapshot_v5.py'),str(case),str(stage/'hold.gro'),str(r/'inputs/ligand_geometry_contract_v2.json'),str(qc)],stdout=h,stderr=subprocess.STDOUT)
            geometry=json.loads(qc.read_text()) if qc.exists() else {'pass':False,'error':'snapshot checker failed'}
            texts={s:(stage/(s+'.log')).read_text() for s in ['heat','hold']}
            steps=re.findall(r'Step\s+Time\s*\n\s*(\d+)\s+([\d.]+)',texts['hold']);last=float(steps[-1][1]) if steps else None
            # epsilon-rf = inf is a valid input-parameter value, not an energy.
            issues={s:[l for l in re.findall(r'^.*(?:LINCS WARNING|cannot be settled|Fatal error|nan\b|\binf\b).*$',t,re.M|re.I)
                       if not re.fullmatch(r'\s*epsilon-rf\s*=\s*inf\s*',l)] for s,t in texts.items()}
            stats={}
            for line in (stage/'final20ps_groups.log').read_text().splitlines():
                f=line.split()
                if f and f[0] in ['Potential','Temperature','T-SOLU','T-MEMB','T-SOLV'] and len(f)>=5:
                    try:stats[f[0]]={'mean':float(f[1]),'rmsd':float(f[3])}
                    except ValueError:pass
            temperatures=[stats[k]['mean'] for k in ['Temperature','T-SOLU','T-MEMB','T-SOLV'] if k in stats]
            samples=[list(map(float,l.split())) for l in (stage/'final20ps_groups.xvg').read_text().splitlines() if l and not l.startswith(('#','@'))]
            finite_energy=bool(samples) and all(math.isfinite(v) for row in samples for v in row)
            completed=last==125 and all('Finished mdrun' in t for t in texts.values())
            numerical=completed and finite_energy and len(temperatures)==4 and all(abs(t-303.15)<10 for t in temperatures) and not any(issues.values())
            passed=result.returncode==0 and geometry['pass'] and numerical and not diagnostic
            status='preheat_input_rejected' if diagnostic else ('preheat_qc_pass' if passed else 'preheat_qc_failed')
            entry.update({'status':status,'directory':str(stage),'end_ps':last,'heating_completed':completed,'numerical_thermal_checks_pass':numerical,'geometry':geometry,'last20ps_statistics':stats,'runtime_warnings':issues})
            if diagnostic:entry['diagnostic_contract']=json.loads((stage/'diagnostic_contract.json').read_text())
            (stage/'preheat_audit.json').write_text(json.dumps(entry,indent=2))
        # Export only receptor/ligand coordinates; full originals remain immutable in each run.
        for name,path in [('initial',case/'ionized.gro'),('em',case/'em.gro'),('double_em',case/'attempt2_double/em.gro'),('ligand_constrained_em',case/'attempt4_ligand_constraints/em.gro'),('frozen_ligand_em',case/'attempt5_frozen_ligand/em.gro'),('hold',stage/'hold.gro')]:
            if not path.exists():continue
            lines=path.read_text().splitlines();n=int(lines[1]);rows=[]
            for l in lines[2:2+n]:
                res=l[5:10].strip()
                if res in {'SOL','POPC','POT','CLA'}:break
                rows.append({'resnum':int(l[:5]),'resname':res,'atomname':l[10:15].strip(),'xyz_nm':[float(l[i:i+8]) for i in (20,28,36)]})
            (snapshots/f'{case.name}_{name}.json').write_text(json.dumps({'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'box_nm':list(map(float,lines[n+2].split())),'atoms':rows},separators=(',',':')))
        reports.append(entry)
    summary={'as_of_utc':datetime.now(timezone.utc).isoformat(),'cases':reports,'passed':sum(x['status']=='preheat_qc_pass' for x in reports),'completed_heatings':sum(x.get('heating_completed',False) for x in reports),'input_rejected':sum(x['status']=='preheat_input_rejected' for x in reports),'total':len(reports),'production_ns':0}
    tmp=out/'preheat_status.json.tmp';tmp.write_text(json.dumps(summary,indent=2));tmp.replace(out/'preheat_status.json')
    print(json.dumps({'passed':summary['passed'],'total':summary['total'],'cases':[(x['case'],x['status']) for x in reports]}))


if __name__=='__main__':main()
