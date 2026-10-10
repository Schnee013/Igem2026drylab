"""User-run rigid alignment to the shared reference, followed by PyMOL review files."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BATCH=ROOT/'outputs/batches/06-af3-supplement-singles'
REF=ROOT/'projects-done/inputs&outputs-deltaNlid/inputs/receptors/af3/pdb/gpr2_twf154_wt/deltaN_aligned/gpr2_twf154_wt_model_0_deltaN1-21_deltaN164-178_aligned.pdb'
RANGES='30-50,62-83,101-126,144-163,182-201,326-346,358-380'

def require(ok,msg):
    if not ok: raise ValueError(msg)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group',help='baseline, all-mutants, variant ID or 06_ alias')
    parser.add_argument('--check-only',action='store_true')
    a=parser.parse_args()
    m=json.loads((BATCH/'manifests/received-af3.json').read_text())
    jobs=[j for j in m['jobs'] if (a.group=='all-mutants' and j['id']!='baseline') or a.group in (j['id'],j['alias'])]
    require(bool(jobs),'Unknown group')
    require(REF.is_file(),f'Missing reference: {REF}')
    for j in jobs:
        d=BATCH/'run-01'/j['alias']; report=json.loads((d/'trimming.json').read_text())
        require(report['docking_residue_count']==370 and report['deleted_original_ranges']==[[1,21],[164,178]],'Unexpected trimming')
        require(not report['renumbered'] and not report['retained_coordinate_changes'],'Unexpected coordinate/numbering changes')
        for path,h in report['files'].items(): require(digest(Path(path))==h,f'Input changed: {path}')
        for name in ['input.pdb','alignment.json','alignment_review.pml','alignment_provenance.json']:
            require(not (d/name).exists(),f'Refusing to overwrite: {d/name}')
    print(f'PREFLIGHT PASS: {len(jobs)} alignment jobs',flush=True)
    if a.check_only: return
    for j in jobs:
        d=BATCH/'run-01'/j['alias']
        subprocess.run([sys.executable,str(ROOT/'vina/src/align_pdb_to_reference.py'),
            '--moving-pdb',str(d/'trimmed.pdb'),'--reference-pdb',str(REF),
            '--moving-chain','A','--reference-chain','A','--moving-ranges',RANGES,'--reference-ranges',RANGES,
            '--output-pdb',str(d/'input.pdb'),'--report-json',str(d/'alignment.json')],check=True)
        report=json.loads((d/'alignment.json').read_text())
        pml=['reinitialize',f'load "{REF}", reference',f'load "{d / "input.pdb"}", current',
             'hide everything','show cartoon, reference or current','color gray70, reference','color cyan, current',
             'select target_sites, current and chain A and resi 106+181+338',
             'show sticks, target_sites','color yellow, target_sites',
             'label target_sites and name CA, "%s%s" % (resn,resi)',
             'set cartoon_transparency, 0.45, reference','zoom current','deselect']
        (d/'alignment_review.pml').write_text('\n'.join(pml)+'\n')
        provenance={'alias':j['alias'],'files':{str(p):digest(p) for p in [REF,d/'trimmed.pdb',d/'input.pdb',d/'alignment.json']}}
        (d/'alignment_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
        print(f'ALIGN PASS: {j["alias"]}; CA={report["matched_ca_count"]}; RMSD={report["ca_rmsd_after_angstrom"]:.3f} A',flush=True)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc: raise SystemExit(f'STOP: {exc}')
