"""Cross-check shared comparison tables against their frame contact records."""
import csv
import json
import math
import sys
from pathlib import Path

base = Path(sys.argv[1])
folder = base / 'comparison/ligand_paths'
def read(path):
    return list(csv.DictReader(path.open()))
paths = read(folder / 'centroid_path.csv')
occupancy = read(folder / 'residue_contact_occupancy.csv')
metadata = json.loads((folder / 'run_metadata.json').read_text())
checks, summary = [], []
def check(arm, name, passed, detail):
    checks.append({'arm': arm, 'check': name, 'status': 'PASS' if passed else 'FAIL', 'detail': detail})
    if not passed:
        raise ValueError(f'{arm}: {name}: {detail}')
for arm, inputs in metadata['arms'].items():
    frame = [r for r in paths if r['arm'] == arm]
    late = [r for r in frame if float(r['time_ns']) >= 50]
    early = [r for r in frame if float(r['time_ns']) < 50]
    check(arm, 'grid_and_windows', len(frame) == 201 and len(late) == 101 and len(early) == 100 and
          all(abs(float(r['time_ns']) - i * .5) < 1e-8 for i, r in enumerate(frame)), '0-100 ns at 0.5 ns')
    numerical = ['x_A', 'y_A', 'z_A', 'fit_rmsd_A', 'minimum_receptor_ligand_distance_A',
                 'centroid_displacement_from_arm_initial_in_common_frame_A']
    check(arm, 'finite', all(math.isfinite(float(r[k])) for r in frame for k in numerical), str(numerical))
    first = frame[0]
    check(arm, 'centroid_displacement_reproduction', all(abs(math.sqrt(sum((float(r[k])-float(first[k]))**2
          for k in ['x_A', 'y_A', 'z_A'])) - float(r[numerical[-1]])) < 1e-6 for r in frame), 'distance from stored common-frame initial centroid')
    sets = [set(r['contact_residues'].split(';')) - {''} for r in frame]
    check(arm, 'dynamic_contact_count', all(len(s) == int(r['contacting_receptor_residues'])
          for s, r in zip(sets, frame)), 'distinct residue contact tokens per frame')
    contacts = [r for r in occupancy if r['arm'] == arm]
    check(arm, 'occupancy_residue_coverage', {r['receptor_resname']+r['receptor_resid'] for r in contacts} ==
          set().union(*sets), 'all residues ever observed in the sampled frame records')
    check(arm, 'dynamic_occupancy_reproduction', all(
          abs(sum((r['receptor_resname']+r['receptor_resid']) in s for s in sets[:100])/100 - float(r['early_occupancy'])) < 1e-10 and
          abs(sum((r['receptor_resname']+r['receptor_resid']) in s for s in sets[100:])/101 - float(r['late_occupancy'])) < 1e-10 and
          (r['initial_contact'] == 'True') == ((r['receptor_resname']+r['receptor_resid']) in sets[0]) for r in contacts), 'early denominator 100; late denominator 101; initial flags')
    canonical = base / 'e2_delivery' / inputs['system'] / 'analysis/contacts'
    persistence = read(canonical / 'contact_persistence.csv')
    check(arm, 'shared_initial_contacts_cross_driver', len(persistence) == 201 and all(
          int(r['initial_contacts']) == len(sets[0]) and int(r['retained_contacts']) == len(s & sets[0])
          and abs(float(r['time_ns'])-float(f['time_ns'])) < 1e-8 for r, s, f in zip(persistence, sets, frame)), 'seven-driver persistence vs independent path contact records')
    initial = read(canonical / 'initial_contact_occupancy.csv')
    check(arm, 'initial_occupancies_cross_driver', len(initial) == len(sets[0]) and all(
          abs(sum((r['receptor_resname']+r['receptor_resid']) in s for s in sets[100:])/101 - float(r['occupancy'])) < 1e-10
          for r in initial), 'same 101 sampled late frames')
    summary.append({'arm': arm, 'case_id': inputs['system'], 'window_start_ns': 50, 'window_end_ns': 100,
                    'n_samples': 101, 'centroid_displacement_mean_A': sum(float(r[numerical[-1]]) for r in late)/101,
                    'dynamic_contact_residues_mean': sum(int(r['contacting_receptor_residues']) for r in late)/101,
                    'minimum_distance_min_A': min(float(r['minimum_receptor_ligand_distance_A']) for r in late),
                    'minimum_distance_max_A': max(float(r['minimum_receptor_ligand_distance_A']) for r in late)})
for target, rows, delimiter in [('evidence/ligand_path_validation.tsv', checks, '\t'),
                                ('comparison/ligand_path_primary_summary.csv', summary, ',')]:
    with (base / target).open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)
print('ligand_path_checks', len(checks), 'PASS', sum(r['status']=='PASS' for r in checks))
