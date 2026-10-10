"""Read-only checks of all batch08 alignment reports and source hashes."""
from model_selection import load_manifest, model_note
import json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BATCH=ROOT/'outputs/batches/08-af3-double-mutants'

def main():
    m=load_manifest(BATCH); rows=[]
    if len(m['jobs'])!=18:raise ValueError('Expected 18 receptors')
    for j in m['jobs']:
        d=BATCH/'run-01'/j['alias']; r=json.loads((d/'alignment.json').read_text()); p=json.loads((d/'alignment_provenance.json').read_text())
        if r['matched_ca_count']!=153 or r['moving_ranges']!=r['reference_ranges'] or r['moving_ranges']!='30-50,62-83,101-126,144-163,182-201,326-346,358-380':raise ValueError('Alignment selection mismatch')
        for path,h in p['files'].items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=h:raise ValueError(f'Hash changed: {path}')
        rmsd=r['ca_rmsd_after_angstrom']
        if not math.isfinite(rmsd):raise ValueError('Nonfinite RMSD')
        rows.append((rmsd,j['alias']))
    print('ALIGNMENT AUDIT PASS: 18 receptors; 153 matched CA each; all hashes verified')
    for rmsd,alias in sorted(rows,reverse=True):print(f'{alias}: {rmsd:.3f} A')
    print('RMSDs are review priorities, not automatic acceptance thresholds. Review the highest deviations and mutated sites in PyMOL.')
if __name__=='__main__':main()
