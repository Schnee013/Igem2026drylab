"""User-run Meeko preparation with manifest-based sequence and heavy-atom checks."""
from model_selection import load_manifest, model_note
import argparse, hashlib, importlib.metadata, json, math, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BATCH=ROOT/'outputs/batches/08-af3-double-mutants'
EXPECTED=set(range(22,164)) | set(range(179,407))
AA=dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),'ARNDCQEGHILKMFPSTWYV'))

def require(ok,msg):
    if not ok: raise ValueError(msg)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def atoms(path):
    result={}
    for line in path.read_text().splitlines():
        require(not line.startswith('HETATM'),f'Unexpected HETATM: {path}')
        if not line.startswith('ATOM  '): continue
        key=(line[21],int(line[22:26]),line[26],line[12:16].strip())
        if key[3].lstrip('0123456789').startswith(('H','D')): continue
        require(line[16]==' ' and key not in result,f'Alternate/duplicate atom: {path} {key}')
        require(all(math.isfinite(float(line[a:b])) for a,b in [(30,38),(38,46),(46,54)]),'Nonfinite coordinates')
        result[key]=line
    return result

def validate_inventory(path,seq):
    found=atoms(path)
    require({k[:3] for k in found}=={('A',n,' ') for n in EXPECTED},f'Residue inventory mismatch: {path}')
    for k,line in found.items(): require(AA[line[17:20]]==seq[k[1]-1],f'Sequence mismatch: {path} {k}')
    return found

def validate_output(source,path,seq):
    current=validate_inventory(path,seq)
    require(set(current)==set(source),f'Heavy atom inventory changed: {path}')
    terminal={('A',406,' ','O'),('A',406,' ','OXT')}
    for k,line in current.items():
        require(line[17:20]==source[k][17:20],f'Residue name changed: {k}')
        if k in terminal and terminal<=set(source):
            require({current[t][30:54] for t in terminal}=={source[t][30:54] for t in terminal},'Terminal oxygen geometry changed')
        else: require(line[30:54]==source[k][30:54],f'Heavy atom moved: {path} {k}')
        if path.suffix=='.pdbqt':
            require(math.isfinite(float(line[70:76])) and bool(line[77:].strip()),f'Invalid charge/type: {k}')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group',help='all-mutants, variant ID or 08_ alias')
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--resume',action='store_true',help='Skip only completed jobs whose validation hashes still match')
    parser.add_argument('--exclude',action='append',default=[],help='Explicitly defer a variant ID or alias; repeat as needed')
    a=parser.parse_args()
    m=load_manifest(BATCH)
    jobs=[j for j in m['jobs'] if (a.group=='all-mutants' and j['id']!='baseline') or a.group in (j['id'],j['alias'])]
    require(bool(jobs),'Unknown group')
    known={v for j in jobs for v in (j['id'],j['alias'])}
    require(set(a.exclude)<=known,'Unknown excluded variant')
    deferred=[j for j in jobs if j['id'] in a.exclude or j['alias'] in a.exclude]
    jobs=[j for j in jobs if j not in deferred]
    for j in deferred: print(f'DEFERRED: {j["alias"]}; explicitly excluded, outputs preserved',flush=True)
    versions={name:importlib.metadata.version(name) for name in ['meeko','rdkit']}
    print('Environment:',json.dumps(versions),flush=True)
    pending=[]
    for j in jobs:
        d=BATCH/'run-01'/j['alias']; prov=json.loads((d/'alignment_provenance.json').read_text())
        for name,h in prov['files'].items(): require(digest(Path(name))==h,f'Alignment file changed: {name}')
        fasta=ROOT/j['expected_fasta']; require(digest(fasta)==j['fasta_sha256'],'FASTA changed')
        seq=''.join(x.strip() for x in fasta.read_text().splitlines() if not x.startswith('>'))
        require(len(seq)==406,'Expected full-length FASTA')
        validate_inventory(d/'input.pdb',seq)
        if a.resume and (d/'preparation_validation.json').is_file():
            report=json.loads((d/'preparation_validation.json').read_text())
            require(report['alias']==j['alias'] and report['residues']==370 and report['sequence_verified'] and report['heavy_atom_coordinates_preserved'] and report['charge_model']=='gasteiger','Invalid completion report')
            for path,h in report['files'].items(): require(digest(Path(path))==h,f'Completed output changed: {path}')
            original=validate_inventory(d/'input.pdb',seq)
            for name in ['receptor.pdbqt','prepared.pdb']: validate_output(original,d/name,seq)
            print(f'SKIP VERIFIED: {j["alias"]}',flush=True)
            continue
        pending.append(j)
        for name in ['receptor.pdbqt','receptor.json','prepared.pdb','preparation.log','preparation_validation.json']:
            require(not (d/name).exists(),f'Refusing to overwrite: {d/name}')
    jobs=pending
    print(f'PREFLIGHT PASS: {len(jobs)} preparation jobs',flush=True)
    if a.check_only: return
    for j in jobs:
        d=BATCH/'run-01'/j['alias']; fasta=ROOT/j['expected_fasta']
        seq=''.join(x.strip() for x in fasta.read_text().splitlines() if not x.startswith('>'))
        source=validate_inventory(d/'input.pdb',seq)
        cmd=[sys.executable,str(ROOT/'vina/src/prepare_receptor_pdbqt.py'),
             '--receptor-pdb',str(d/'input.pdb'),'--output-pdbqt',str(d/'receptor.pdbqt'),
             '--meeko-executable',sys.executable,'--charge-model','gasteiger',
             '--meeko-arg=-j',f'--meeko-arg={d / "receptor.json"}',
             '--meeko-arg=--write_pdb',f'--meeko-arg={d / "prepared.pdb"}']
        with (d/'preparation.log').open('x') as log:
            result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
        require(result.returncode==0,f'Meeko failed; inspect {d / "preparation.log"}')
        for name in ['receptor.pdbqt','prepared.pdb']: validate_output(source,d/name,seq)
        from meeko import Polymer
        polymer=Polymer.from_json((d/'receptor.json').read_text())
        require(set(polymer.get_valid_monomers())=={f'A:{n}' for n in EXPECTED},'Meeko JSON residue inventory mismatch')
        report={'alias':j['alias'],'residues':370,'heavy_atoms':len(source),'sequence_verified':True,
                'heavy_atom_coordinates_preserved':True,'terminal_oxygen_name_swap_allowed':True,
                'charge_model':'gasteiger','versions':versions,'command':cmd,'af_model':j['selected_model'],
                'files':{str(p):digest(p) for p in [fasta,d/'input.pdb',d/'receptor.pdbqt',d/'receptor.json',d/'prepared.pdb',d/'preparation.log']}}
        if (d/'af_model_selection.json').exists():
            report['files'][str(d/'af_model_selection.json')]=digest(d/'af_model_selection.json')
            report['files'][str(ROOT/j['models'][j['selected_model']]['path'])]=digest(ROOT/j['models'][j['selected_model']]['path'])
        (d/'preparation_validation.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f'PREPARE PASS: {j["alias"]}; 370 residues; sequence, numbering and heavy-atom coordinates verified',flush=True)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,KeyError,importlib.metadata.PackageNotFoundError) as exc: raise SystemExit(f'STOP: {exc}')
