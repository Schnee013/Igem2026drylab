"""User-run minimum-pose ProLIF analysis for the 36 mutant docking runs."""
from model_selection import load_manifest, model_note
import argparse, csv, importlib.metadata, json, subprocess, sys
from configure_received import ROOT,BATCH,verify_report,require,digest
INTERACTIONS=['Anionic','CationPi','Cationic','HBAcceptor','HBDonor','Hydrophobic','PiCation','PiStacking','VdWContact']

def validate(folder):
    out=folder/'top1_contacts'; sel=json.loads((out/'selection.json').read_text())
    dock=verify_report(folder/'docking_validation.json')
    require(sel['analyzed_pose_count']==1 and sel['selected_original_mode']==dock['selected_model'] and sel['vina_score_kcal_mol']==dock['lowest_score'],'Pose selection mismatch')
    require(sel['source_sha256']==digest(folder/'poses.pdbqt'),'Pose hash mismatch')
    meta=json.loads((out/'ifp/metadata.json').read_text())
    require(meta['prolif_version']=='2.1.0' and meta['n_poses']==1 and meta['vicinity_cutoff_A']==6.0 and meta['interactions']==INTERACTIONS,'ProLIF parameters changed')
    require(meta['receptor_sha256']==digest(folder.parent/'receptor.json') and meta['sdf_sha256']==digest(out/'top1.sdf'),'Contact input hash mismatch')
    with (out/'contact_residues.csv').open() as f: rows=list(csv.DictReader(f))
    require(len(rows)==sel['unique_contact_residues'] and len({r['original_number'] for r in rows})==len(rows),'Contact residue count mismatch')
    return sel

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--check-only',action='store_true'); a=p.parse_args()
    require(importlib.metadata.version('prolif')=='2.1.0','Expected ProLIF 2.1.0')
    m=load_manifest(BATCH); tasks=[]
    for j in m['jobs']:
        if j['id']=='baseline': continue
        d=BATCH/'run-01'/j['alias']; verify_report(d/'preparation_validation.json')
        for lig in ['ascr3','ascr18']:
            folder=d/lig; verify_report(folder/'docking_validation.json')
            require(not (folder/'top1_contacts').exists(),f'Refusing existing output: {folder / "top1_contacts"}')
            require(not (folder/'top1_contacts.log').exists(),f'Existing contact log: {folder}')
            tasks.append(folder)
    require(len(tasks)==36,'Expected 36 tasks')
    print('PREFLIGHT PASS: 36 mutant contact tasks; ProLIF 2.1.0; one minimum-score pose each',flush=True)
    if a.check_only: return
    helper=ROOT/'outputs/batches/03-af3-single-alanine/cli/top1_contacts.py'
    for folder in tasks:
        print(f'START: {folder.parent.name} {folder.name}',flush=True)
        with (folder/'top1_contacts.log').open('x') as log:
            proc=subprocess.run([sys.executable,str(helper),'--run-dir',str(folder)],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
        require(proc.returncode==0,f'Contact analysis failed; inspect {folder / "top1_contacts.log"}')
        sel=validate(folder)
        out=folder/'top1_contacts'
        report={'analyzed_pose_count':1,'selected_model':sel['selected_original_mode'],'unique_contact_residues':sel['unique_contact_residues'],
                'files':{str(path):digest(path) for path in sorted(out.rglob('*')) if path.is_file()}}
        (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f'CONTACTS PASS: {folder.parent.name} {folder.name}; MODEL={sel["selected_original_mode"]}; residues={sel["unique_contact_residues"]}',flush=True)
    print('BATCH PASS: 36 mutant minimum-pose contact analyses completed',flush=True)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,KeyError) as exc: raise SystemExit(f'STOP: {exc}')
