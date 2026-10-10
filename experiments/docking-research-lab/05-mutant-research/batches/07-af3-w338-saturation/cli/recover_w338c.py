"""User-run preservation of failed model_0 and explicit selection of model_1."""
import argparse, json, math
from pathlib import Path
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from scipy.spatial import cKDTree
from model_selection import digest
from prepare_received import AA, require
ROOT=Path(__file__).resolve().parents[4]
BATCH=ROOT/'outputs/batches/07-af3-w338-saturation'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check-only',action='store_true')
    a=p.parse_args()
    receipt=BATCH/'manifests/received-af3.json'
    job=next(j for j in json.loads(receipt.read_text())['jobs'] if j['alias']=='07_w338c')
    model=job['models'][1]; cif=ROOT/model['path']
    require(digest(cif)==model['sha256'],'CIF changed')
    fasta=ROOT/job['expected_fasta']; require(digest(fasta)==job['fasta_sha256'],'FASTA changed')
    seq=''.join(x.strip() for x in fasta.read_text().splitlines() if not x.startswith('>'))
    data=MMCIF2Dict(str(cif)); atoms={}; residues={}
    for i,element in enumerate(data['_atom_site.type_symbol']):
        if element in ('H','D'): continue
        key=(data['_atom_site.auth_asym_id'][i],int(data['_atom_site.auth_seq_id'][i]),data['_atom_site.label_atom_id'][i])
        require(key not in atoms,'Duplicate atom')
        xyz=tuple(float(data['_atom_site.Cartn_'+v][i]) for v in 'xyz')
        require(all(math.isfinite(v) for v in xyz),'Nonfinite coordinate')
        atoms[key]=xyz; residues[key[:2]]=AA[data['_atom_site.label_comp_id'][i]]
    require(set(residues)=={('A',i) for i in range(1,407)},'Full-length residue inventory differs')
    require(''.join(residues['A',i] for i in range(1,407))==seq and seq[337]=='C','W338C sequence differs')
    keys=list(atoms); coords=list(atoms.values())
    clashes=[(keys[i],keys[j],math.dist(coords[i],coords[j])) for i,j in cKDTree(coords).query_pairs(1.8)
             if keys[i][0]!=keys[j][0] or abs(keys[i][1]-keys[j][1])>1]
    require(not clashes,f'Nonadjacent-residue heavy atoms within 1.8 A: {clashes}')
    distance=math.dist(atoms['A',181,'NH1'],atoms['A',345,'NH1'])
    old=BATCH/'run-01/07_w338c'
    saved=BATCH/'diagnostics/07_w338c-failed-model0'
    selection=BATCH/'manifests/w338c-model-selection.json'
    require(old.is_dir() and not saved.exists() and not selection.exists(),'Recovery already staged or unexpected paths; inspect without overwriting')
    require(not (old/'preparation_validation.json').exists(),'Completed preparation must not be replaced')
    require(not (old/'ascr3').exists() and not (old/'ascr18').exists(),'Docking configuration already exists')
    diagnostic=json.loads((BATCH/'diagnostics/w338c-preparation-issue.json').read_text())
    for name,h in diagnostic['files'].items(): require(digest(Path(name))==h,f'Failure evidence changed: {name}')
    require('Expected 2 paddings' in (old/'preparation.log').read_text(),'Unexpected failure reason')
    files={str(f.relative_to(old)):digest(f) for f in old.rglob('*') if f.is_file()}
    report={'alias':job['alias'],'selected_model':1,'receipt_sha256':digest(receipt),'cif':model,
            'reason':'model_0 ARG181 NH1 / ARG345 NH1 1.5568 A overlap and Meeko inter-residue bond failure; model_1 selected before docking by geometry QC, not docking score',
            'qc':{'full_length_residues':406,'sequence_verified':True,'NH1_NH1_distance_A':distance,
                  'nonadjacent_heavy_atom_pairs_within_1_8_A':0,'scope':'screen excludes same and adjacent residues; not a full geometry validation'},
            'preserved_failure':{'old_directory':str(old),'new_directory':str(saved),'files':files,
                                 'note':'Original report bytes preserved; embedded old absolute paths describe the original location.'}}
    print(f'RECOVERY PREFLIGHT PASS: W338C model_1; 406 aa; NH1-NH1={distance:.4f} A; close pairs=0',flush=True)
    if a.check_only: return
    old.rename(saved)
    try:
        with selection.open('x') as f: f.write(json.dumps(report,indent=2)+'\n')
    except Exception:
        # No scientific stage has started; restore the directory on write failure.
        saved.rename(old)
        raise
    print('RECOVERY STAGED: 07_w338c -> AF model_1; model_0 failure preserved; other 19 receptors unchanged')

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,KeyError) as exc: raise SystemExit(f'STOP: {exc}')
