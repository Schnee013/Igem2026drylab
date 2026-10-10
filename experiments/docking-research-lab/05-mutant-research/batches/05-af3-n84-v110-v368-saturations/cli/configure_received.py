"""User-run generation and validation of 116 Vina configurations; never starts Vina."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BATCH=ROOT/'outputs/batches/05-af3-saturation-combinations'
LIGANDS=ROOT/'projects-done/inputs&outputs-deltaNlid/inputs/ligands/deprotonated-minus1/pdbqt'
PARAMS={'center_x':20,'center_y':-20,'center_z':5,'size_x':26,'size_y':26,'size_z':26,'exhaustiveness':8,'num_modes':9,'energy_range':3,'seed':1919}

def require(ok,msg):
    if not ok: raise ValueError(msg)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_report(path):
    report=json.loads(path.read_text())
    for name,h in report['files'].items(): require(digest(Path(name))==h,f'File changed: {name}')
    return report

def validate_config(path,receptor,ligand):
    values={}
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        k,v=line.split('=',1); k=k.strip(); require(k not in values,f'Duplicate config key: {k}'); values[k]=v.strip()
    require(set(values)==set(PARAMS)|{'receptor','ligand'},f'Config key mismatch: {path}')
    require(values['receptor']==str(receptor) and values['ligand']==str(ligand),f'Input path mismatch: {path}')
    for k,v in PARAMS.items(): require(float(values[k])==v,f'Parameter mismatch: {path} {k}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['check','generate','validate'])
    a=p.parse_args()
    m=json.loads((BATCH/'manifests/received-af3.json').read_text())
    tasks=[]
    for j in m['jobs']:
        d=BATCH/'run-01'/j['alias']
        verify_report(d/'alignment_provenance.json')
        r=verify_report(d/'preparation_validation.json')
        require(r['residues']==370 and r['sequence_verified'] and r['heavy_atom_coordinates_preserved'],'Preparation validation failed')
        for ligand in ['ascr3','ascr18']:
            source=LIGANDS/f'{ligand}_deprotonated.pdbqt'
            require(source.is_file() and source.stat().st_size>0,f'Missing ligand: {source}')
            folder=d/ligand
            if a.stage!='validate': require(not folder.exists(),f'Refusing existing directory: {folder}')
            tasks.append((j['alias'],ligand,folder,d/'receptor.pdbqt',source))
    require(len(tasks)==116,'Expected 116 tasks')
    print('PREFLIGHT PASS: 58 receptors, 2 ligands, 116 configurations',flush=True)
    if a.stage=='check': return
    for alias,ligand,folder,receptor,source in tasks:
        conf=folder/'vina.conf'; receipt=folder/'config_provenance.json'
        if a.stage=='generate':
            folder.mkdir(exist_ok=False)
            cmd=[sys.executable,str(ROOT/'vina/src/define_vina_box.py'),'--receptor',str(receptor),'--ligand',str(source),'--output',str(conf)]
            for key,value in PARAMS.items(): cmd.extend(['--'+key.replace('_','-'),str(value)])
            subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
            validate_config(conf,receptor,source)
            report={'alias':alias,'ligand':ligand,'parameters':PARAMS,'runtime_parameters':{'spacing':0.375,'min_rmsd':1,'max_evals':0},'files':{str(p):digest(p) for p in [receptor,source,conf]}}
            receipt.write_text(json.dumps(report,indent=2)+'\n')
        else:
            verify_report(receipt)
            validate_config(conf,receptor,source)
    print('CONFIG PASS: 116 configurations; absolute input paths, frozen parameters and hashes verified')

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as exc: raise SystemExit(f'STOP: {exc}')
