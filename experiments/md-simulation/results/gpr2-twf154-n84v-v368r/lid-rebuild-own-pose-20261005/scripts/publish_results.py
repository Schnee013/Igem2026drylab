from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import shutil
import sys

import numpy as np

ROOT = Path('/Users/roy/Documents/drylab')
TMP = Path('/private/tmp/gpr2-own-lid-20261005')
BASE = ROOT/'experiments/md-simulation/results/gpr2-twf154-n84v-v368r'
OUT = BASE/'lid-rebuild-own-pose-20261005'
SEL = BASE/'input-selection-20261005'
SCRIPTS = ROOT/'experiments/md-simulation/scripts'
sys.path.insert(0, str(SCRIPTS))
from sample_disulfide_lid import read_pdb

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

now = datetime.now(timezone.utc).isoformat()
cases = [('v368r_ascr3_lid_rebuilt_own_pose_v1', 'refine_v368r02', 12),
         ('native_wt_ascr3_lid_rebuilt_own_pose_v1', 'refine_wt24', 24)]
for dirname in ['inputs', 'runs', 'logs']:
    shutil.copytree(TMP/dirname, OUT/dirname, dirs_exist_ok=True)
for dirname in ['refine_v368r', 'refine_wt', 'refine_v368r02', 'refine_wt02', 'refine_wt24', 'wt_disulfide_first']:
    shutil.copytree(TMP/dirname, OUT/'supplemental'/dirname, dirs_exist_ok=True)
for name in ['sample_disulfide_lid.py', 'run_twf154_own_lid_parallel.py',
             'refine_twf154_own_lid.py', 'sample_twf154_own_lid.py',
             'check_twf154_own_lid_candidates.py']:
    shutil.copy2(SCRIPTS/name, OUT/'scripts'/name)
for name in ['download_pyrosetta.py', 'download_dependencies.py']:
    shutil.copy2(TMP/name, OUT/'environment'/name)

rows = []
summary = []
for case, refinement, source_number in cases:
    cfg = json.loads((TMP/'inputs'/case/'pilot_config.json').read_text())
    parent = read_pdb(cfg['receptor'])
    run = OUT/'runs'/case
    main_checks = json.loads((run/'independent_geometry.json').read_text())
    check_map = {r['name']: r for r in main_checks['rows']}
    raw_results = json.loads((run/'candidates.json').read_text())
    for r in raw_results:
        name = f"candidate_{r['candidate']:04d}"
        atoms = read_pdb(run/(name+'.pdb'))
        assert set(atoms) == set(parent)
        assert all(atoms[k]['resname'] == parent[k]['resname'] for k in parent)
        assert {k[0] for k in atoms} == set(range(1,407))
        exterior = [k for k in parent if not 164 <= k[0] <= 178]
        displacement = max(float(np.linalg.norm(atoms[k]['xyz']-parent[k]['xyz'])) for k in exterior)
        assert displacement == 0.0
        g = r['written_geometry']
        c = check_map[name]
        rows.append(dict(case_id=case, candidate=r['candidate'], geometry_pass=g['geometric_screen_pass'],
                         covalent_cycle_screen_pass=c['covalent_cycle_link_screen_pass'],
                         eligible_for_visual_review=c['eligible_for_visual_review'],
                         max_rama_prepro_REU=max(r['lid_rama_prepro_REU'].values()),
                         lid_backbone_rmsd_A=g['lid_backbone_rmsd_no_fit_A'],
                         outside_max_displacement_A=displacement,
                         sequence_and_heavy_atom_identity_match=True,
                         file=str((run/(name+'.pdb')).relative_to(OUT))))

    refdir = OUT/'supplemental'/refinement
    ref = json.loads((refdir/'refinement.json').read_text())
    r = ref['rounds'][-1]
    c = json.loads((refdir/'independent_geometry.json').read_text())['rows'][-1]
    assert r['round'] == 3 and c['name'] == 'candidate_0003'
    assert c['eligible_for_visual_review']
    dest = OUT/'review_candidates'/case
    dest.mkdir(parents=True, exist_ok=True)
    stem = 'gpr2_twf154_'+case
    receptor = dest/(stem+'_receptor.pdb')
    ligand = dest/(stem+'_ligand.sdf')
    shutil.copy2(refdir/'candidate_0003.pdb', receptor)
    shutil.copy2(TMP/'inputs'/case/'own_pose_top1.sdf', ligand)
    atoms = read_pdb(receptor)
    assert set(atoms) == set(parent)
    assert all(atoms[k]['resname'] == parent[k]['resname'] for k in parent)
    assert {k[0] for k in atoms} == set(range(1,407))
    assert all(np.array_equal(atoms[k]['xyz'],parent[k]['xyz']) for k in parent if not 164 <= k[0] <= 178)
    contract_file = SEL/(stem+'.input.json')
    contract = json.loads(contract_file.read_text())
    original_ligand = (SEL/contract['ligand_pose']['path']).resolve()
    original_parent = (SEL/contract['receptor_parent']['path']).resolve()
    assert sha(original_ligand) == sha(ligand) == contract['ligand_pose']['sha256']
    assert sha(original_parent) == contract['receptor_parent']['sha256']
    item = dict(case_id=case, status='STATIC_SCREEN_PASSED_REVIEW_PENDING', production_ready=False,
        source_candidate_number=source_number, refinement_round=3,
        selection_rule='Among geometry- and cycle-screen passing candidates, choose lowest maximum lid rama_prepro score; retain the final round of the same three-round refinement. No affinity ranking.',
        receptor_path=str(receptor.relative_to(OUT)), receptor_sha256=sha(receptor),
        ligand_path=str(ligand.relative_to(OUT)), ligand_sha256=sha(ligand),
        parent_heavy_atom_count=len(parent), full_length_residues=406,
        sequence_and_heavy_atom_identity_match=True, ligand_file_identical_to_original=True,
        original_parent_sha256_unchanged=True,
        geometric_screen=c['geometry'],
        ss_loop_sugar_linking_numbers=c['ss_loop_sugar_linking_numbers'],
        protein_ring_sugar_links=c['protein_ring_sugar_links'],
        open_lid_artificial_surface_diagnostic=c['open_lid_artificial_surface_diagnostic'],
        lid_rama_prepro_REU=r['lid_rama_prepro_REU'], max_rama_prepro_REU=r['max_rama_prepro_REU'],
        independent_check_path=str((refdir/'independent_geometry.json').relative_to(OUT)),
        pending=['Three-dimensional structural and energetic review', 'Consistent membrane-system topology and minimization/equilibration', 'New production TPR and benchmark'])
    write(dest/'candidate_manifest.json', item)
    summary.append(item)
    contract.update(coordinate_status='CANDIDATES_GENERATED', coordinate_status_observed_at=now,
                    as_of='2026-10-06', allowed_use='Current own-parent input selection and generated review-candidate pointers; not final acceptance or an MD-ready system.',
                    candidate_acceptance_status='STATIC_SCREEN_PASSED_REVIEW_PENDING',
                    candidate_receptor_path='../lid-rebuild-own-pose-20261005/'+item['receptor_path'],
                    candidate_receptor_sha256=item['receptor_sha256'],
                    candidate_ligand_path='../lid-rebuild-own-pose-20261005/'+item['ligand_path'],
                    candidate_ligand_sha256=item['ligand_sha256'],
                    candidate_manifest_path='../lid-rebuild-own-pose-20261005/'+str((dest/'candidate_manifest.json').relative_to(OUT)))
    assert contract['accepted_receptor_path'] is None and contract['production_tpr_path'] is None
    write(contract_file, contract)

with (OUT/'candidate_screening.tsv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t');w.writeheader();w.writerows(rows)
write(OUT/'review_candidates.json', dict(observed_at=now, state='CANDIDATES_GENERATED_REVIEW_PENDING',
      accepted_structures=[], production_ready=False, cases=summary))
write(OUT/'recovery_map.json', dict(observed_at=now, runtime_root=str(TMP), recovered_root=str(OUT),
      identity_preserving_paths=['inputs', 'runs', 'logs'], supplemental_runtime_directories=[x[1] for x in cases],
      note='Runtime JSON retains the original absolute paths as historical evidence; use recovered matching files, not deleted temp paths.'))
manifest_path=OUT/'launch_manifest.json'
manifest=json.loads(manifest_path.read_text())
manifest.update(state='TERMINAL_NORMAL', phase='CANDIDATES_GENERATED_REVIEW_PENDING', observed_at=now,
                evidence='live_status.json, runs/*/summary.json, review_candidates.json', production_ready=False)
write(manifest_path, manifest)
with (OUT/'run_state_events.tsv').open('a') as f:
    f.write(f'{now}\tTERMINAL_NORMAL\treview_candidates.json\tAll 48 first-batch outputs and bounded refinements recovered; two static-screen-passing review candidates; no MD acceptance\n')
print(json.dumps(dict(recovered_first_batch=len(rows), candidates=[dict(case_id=x['case_id'], max_rama=x['max_rama_prepro_REU'], path=x['receptor_path']) for x in summary]), ensure_ascii=False))
