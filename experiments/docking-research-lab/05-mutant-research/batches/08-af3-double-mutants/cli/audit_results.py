"""Read-only final audit of the 36 double-mutant docking/contact results."""
from model_selection import load_manifest
from configure_received import BATCH,verify_report,require
from contacts_received import validate

def main():
    count=0
    for j in load_manifest(BATCH)['jobs']:
        d=BATCH/'run-01'/j['alias']
        verify_report(d/'alignment_provenance.json')
        verify_report(d/'preparation_validation.json')
        for ligand in ['ascr3','ascr18']:
            folder=d/ligand
            verify_report(folder/'config_provenance.json')
            r=verify_report(folder/'docking_validation.json')
            s=validate(folder)
            verify_report(folder/'top1_contacts/validation.json')
            print(f"{j['alias']} {ligand}: score={r['lowest_score']:.3f}; MODEL={s['selected_original_mode']}; residues={s['unique_contact_residues']}")
            count+=1
    require(count==36,'Expected 36 results')
    print('FINAL AUDIT PASS: 18 double mutants; 36 docking results; 36 minimum-pose contact analyses; hashes verified')
if __name__=='__main__':
    try: main()
    except (ValueError,OSError,KeyError) as exc: raise SystemExit(f'STOP: {exc}')
