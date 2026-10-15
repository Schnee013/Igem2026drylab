"""Run configurable constant-input scenarios with the six-state model."""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import sys
import scipy
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.modeling.ode.literature_core import (
    LiteratureCoreModel, ROOT, PROJECT_PATH, SOURCE_PATH, STATES, RECONSTRUCTED,
)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parameters',type=Path,default=PROJECT_PATH)
    parser.add_argument('--source',type=Path,default=SOURCE_PATH)
    parser.add_argument('--ligand',type=float,nargs='+',default=[0,.1,1,10])
    parser.add_argument('--hours',type=float,default=8)
    parser.add_argument('--output',type=Path,default=ROOT/'temp/ode-literature-core')
    args=parser.parse_args()
    if not np.isfinite(args.hours) or args.hours<=0:
        parser.error('--hours must be finite and positive')
    model=LiteratureCoreModel(args.parameters,args.source)
    for ligand in args.ligand:
        model.drive(ligand)
    # Atomically reserve a fresh directory before producing run evidence.
    try:
        args.output.mkdir(parents=True,exist_ok=False)
    except FileExistsError:
        parser.error('--output already exists; choose a new directory for each run')
    end=args.hours*3600
    times=np.unique(np.r_[0,np.geomspace(end*1e-8,end,200),np.linspace(0,end,201)])
    rows=[]
    for ligand in args.ligand:
        sol=model.solve(ligand,times)
        expanded=model.reconstruct(sol.y)
        if not np.isfinite(expanded).all() or expanded.min() < -1e-8:
            raise RuntimeError('Nonphysical trajectory; output not saved')
        rows.extend([ligand,time,*expanded[:,i],expanded[7,i]/model.pools[3]] for i,time in enumerate(times))
    with (args.output/'timecourses.csv').open('w') as f:
        writer=csv.writer(f)
        writer.writerow(['ligand_normalized','time_s',*RECONSTRUCTED,'MAPK_fraction'])
        writer.writerows(rows)
    identity_paths=[Path(__file__),ROOT/'src/modeling/ode/literature_core.py',model.parameters_path,model.source_path]
    record={'observed_at':datetime.now(timezone.utc).isoformat(),'status':'TERMINAL_NORMAL',
            'environment':{'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__},
            'model_states':STATES,'hours':args.hours,'ligand_normalized':args.ligand,
            'resolved_endpoint_parameters':model.parameters,'fixed_source_rates':model.rates,
            'fixed_source_pools_uM':model.pools.tolist(),
            'sha256':{(str(p.resolve().relative_to(ROOT)) if p.resolve().is_relative_to(ROOT) else p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in identity_paths},
            'result_sha256':hashlib.sha256((args.output/'timecourses.csv').read_bytes()).hexdigest(),
            'interpretation':'Uncalibrated prototype. Literature transfer and both endpoints assumed.'}
    (args.output/'run.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    events=args.output/'run_state_events.tsv'
    if not events.exists():
        events.write_text('observed_at\tstate\tsource\tdetail\n')
    with events.open('a') as f:
        f.write(f"{record['observed_at']}\tTERMINAL_NORMAL\trun.json\tconstant-input scenarios completed\n")
    print(json.dumps({'status':record['status'],'output':str(args.output),'rows':len(rows)}))


if __name__=='__main__':
    main()
