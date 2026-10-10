#!/usr/bin/env python3
"""Validate archived segments and orchestrate the shared GPR analysis drivers.

All input and deployment paths come from a batch config. This runner computes
no scientific metrics; those belong to the shared chctrl driver family.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

import MDAnalysis as mda
from MDAnalysis.lib.formats.libmdaxdr import XTCFile
import numpy as np
import pandas as pd


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def identity(path):
    path = Path(path)
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha256(path)}


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def command(args, log, stdin=None, env=None):
    args = list(map(str, args))
    write_json(str(log) + '.command.json', {'argv': args, 'stdin': stdin,
               'observed_at': datetime.now(timezone.utc).isoformat()})
    with Path(log).open('w') as stream:
        p = subprocess.run(args, input=stdin, text=True, stdout=stream,
                           stderr=subprocess.STDOUT, env=env)
    Path(str(log) + '.exit').write_text(str(p.returncode) + '\n')
    if p.returncode:
        raise RuntimeError(f'command exit {p.returncode}: {log}')


def map_source(path, root):
    text = str(path)
    marker = '/gpr2-twf154-dots-20261006/'
    if marker in text:
        return root / text.split(marker, 1)[1]
    mapped = Path(text)
    if not mapped.is_relative_to(root):
        raise ValueError(f'unmapped source: {path}')
    return mapped


def read_xtc(path, atoms):
    times, first, last = [], None, None
    # Low-level XDR API never writes offsets/lock files beside raw trajectories.
    with XTCFile(str(path), 'r') as stream:
        for frame in stream:
            if len(frame.x) != atoms or not np.isfinite(frame.x).all():
                raise ValueError(f'XTC atom/finite-coordinate mismatch: {path}')
            times.append(float(frame.time))
            if first is None:
                first = frame.x.copy()
            last = frame.x.copy()
    values = np.array(times)
    if not len(values) or np.any(np.diff(values) <= 0):
        raise ValueError(f'empty or non-increasing XTC: {path}')
    if not np.allclose(values / 10, np.round(values / 10), atol=0.00001):
        raise ValueError(f'non-10ps grid: {path}')
    return values, first, last


def validate_segments(batch, case, out):
    root = Path(batch['input_root'])
    run = root / case['run_dir']
    tpr = run / 'production.tpr'
    contract = json.loads((run / 'input_contract.json').read_text())
    if contract['id'] != case['id'] or contract['genotype'] != case['genotype'] or contract['ligand'] != case['ligand']:
        raise ValueError('input contract identity mismatch')
    if contract['production_ns'] != 100 or contract['replicate'] != 1:
        raise ValueError('input contract time/replicate mismatch')
    topology = mda.Universe(str(tpr))
    if len(topology.atoms) != case['full_atoms']:
        raise ValueError('full TPR atom count mismatch')
    protein = topology.select_atoms('protein')
    ligand_segments = [s for s in topology.segments if s.segid.endswith('_' + case['ligand'].upper())]
    if len(ligand_segments) != 1:
        raise ValueError('ligand molecule segment identity mismatch')
    ligand = ligand_segments[0].atoms
    if len(protein) != contract['atoms'] or len(ligand.residues) != 1:
        raise ValueError('protein/ligand topology identity mismatch')
    solution = protein | ligand
    if not np.array_equal(solution.indices, np.arange(len(solution))):
        raise ValueError('SOLU is not a source-order contiguous prefix')
    if protein.residues[83].resname != {'wt':'ASN','n84v':'VAL','v368r':'ASN'}[case['genotype']]:
        raise ValueError('residue84 genotype mapping mismatch')
    if protein.residues[367].resname != {'wt':'VAL','n84v':'VAL','v368r':'ARG'}[case['genotype']]:
        raise ValueError('residue368 genotype mapping mismatch')
    pd.DataFrame({'source_index_1based': solution.indices + 1, 'processed_index_1based': np.arange(len(solution)) + 1,
                  'resid':solution.resids,'resname':solution.resnames,'name':solution.names,'segid':solution.segids}).to_csv(out / 'atom_mapping.csv', index=False)
    coverage = json.loads(Path(batch['coverage_certificate']).read_text())
    if not coverage['all_six_complete'] or not coverage['cases'][case['id']]['complete_100ns']:
        raise ValueError('retained coverage certificate does not close this case')
    archive_rows = {}
    evidence = [identity(batch['coverage_certificate'])]
    for item in coverage['verified_manifests']:
        if item['case_id'] != case['id']:
            continue
        path = root / item['manifest']
        if sha256(path) != item['manifest_sha256']:
            raise ValueError(f'archive manifest identity changed: {path}')
        evidence.append(identity(path))
        for row in json.loads(path.read_text())['files']:
            archive_rows.setdefault(str(root / row['relative_path']), []).append(row)
    tpr_hash = sha256(tpr)
    records = []
    for path in (root / case['record_dir']).glob('segment_*/closed_segment.json'):
        data = json.loads(path.read_text())
        records.append((float(data['start_ps']), float(data['end_ps']), path, data))
    records.sort(key=lambda row: row[:2])
    if len(records) != case['segments'] or records[0][0] != 0 or records[-1][1] != 100000:
        raise ValueError('closed segment count/endpoints mismatch')
    rows, source_paths, all_times, duplicate_rows = [], [], [], []
    previous_end = 0.0
    previous_time, previous_x = None, None
    for number, (start, end, path, data) in enumerate(records, 1):
        if data['case_id'] != case['id'] or not data['pass'] or abs(start - previous_end) > 0.01:
            raise ValueError(f'closed segment identity/continuity failure: {path}')
        if data['production_tpr_sha256'] != tpr_hash:
            raise ValueError(f'closed segment TPR mismatch: {path}')
        current_sha = sha256(path)
        if not any(r['sha256'] == current_sha and r['bytes'] == path.stat().st_size for r in archive_rows.get(str(path), [])):
            raise ValueError(f'closed record does not match verified archive: {path}')
        evidence.append(identity(path))
        xtc_entries = [entry for entry in data['files'] if entry['path'].endswith('.xtc')]
        if len(xtc_entries) != 1:
            raise ValueError('formal segment must identify exactly one XTC')
        entry = xtc_entries[0]
        xtc = map_source(entry['path'], root)
        if not xtc.is_relative_to(run) or not xtc.exists():
            raise ValueError(f'wrong-case/nonexistent XTC: {xtc}')
        matching = [r for r in archive_rows.get(str(xtc), []) if r['sha256'] == entry['sha256'] and r['bytes'] == xtc.stat().st_size]
        if not matching:
            raise ValueError(f'XTC identity/size inconsistent with retained SHA proof: {xtc}')
        times, first, last = read_xtc(xtc, case['full_atoms'])
        recorded = data['trajectory']
        if len(times) != recorded['frames'] or times[0] != recorded['first_ps'] or times[-1] != recorded['last_ps']:
            raise ValueError(f'current XTC time metadata differs from closed record: {xtc}')
        if previous_time is not None and times[0] == previous_time:
            delta_nm = float(np.max(np.abs(first - previous_x)))
            duplicate_rows.append({'time_ps':times[0],'max_coordinate_difference_nm':delta_nm})
            if times[0] not in case['legal_duplicate_ps'] or delta_nm > 0.005:
                raise ValueError(f'unverified duplicate boundary: {duplicate_rows[-1]}')
        source_paths.append(xtc)
        all_times.extend(times)
        rows.append({'order':number, 'closed_record':str(path), 'start_ps':start,'end_ps':end,
                     'trajectory':str(xtc),'first_ps':times[0],'last_ps':times[-1],'stored_frames':len(times),
                     'bytes':xtc.stat().st_size,'retained_source_sha256':entry['sha256'],
                     'current_check':'size + complete time grid + atom/finite coordinates; prior independent SHA reused'})
        previous_end, previous_time, previous_x = end, times[-1], last
    unique = np.unique(all_times)
    if not np.array_equal(unique, np.arange(0, 100001, 10)):
        raise ValueError('raw union does not cover every 0-100000ps grid point')
    if sorted(row['time_ps'] for row in duplicate_rows) != case['legal_duplicate_ps']:
        raise ValueError('duplicate boundary list does not match certified exceptions')
    pd.DataFrame(rows).to_csv(out / 'formal_segments.csv', index=False)
    with (out / 'source_index.ndx').open('w') as stream:
        for name, atoms in [('PROA',protein),('LIGAND',ligand),('SOLU',solution)]:
            stream.write(f'[ {name} ]\n')
            indices = atoms.indices + 1
            for i in range(0,len(indices),15):
                stream.write(' '.join(map(str,indices[i:i+15])) + '\n')
    result = {'status':'PASS','case_id':case['id'],'input_contract':contract,'topology':identity(tpr),
              'full_atoms':len(topology.atoms),'protein_atoms':len(protein),'protein_residues':len(protein.residues),
              'ligand_atoms':len(ligand),'ligand_heavy_atoms':len(ligand.select_atoms('not name H*')),
              'solution_atoms':len(solution),'fit_atoms':len(protein.select_atoms('backbone')),
              'receptor_segids':list(set(protein.segids)), 'ligand_segids':list(set(ligand.segids)),
              'stored_frames':len(all_times),'unique_frames':len(unique),'duplicates':duplicate_rows,
              'source_integrity':'Retained independent per-file E2 SHA receipts; current manifest/closed-record/TPR SHA and XTC byte/time/atom checks',
              'evidence':evidence, 'observed_at':datetime.now(timezone.utc).isoformat()}
    write_json(out / 'input_validation.json',result)
    (out / 'input_contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    return result, source_paths


def processed_gate(case, base, inputs):
    processed = base / 'processed/rep1'
    out = base / 'evidence'
    source = mda.Universe(inputs['topology']['path'])
    expected = source.atoms[:inputs['solution_atoms']]
    u = mda.Universe(str(processed / 'protein_ref.pdb'), str(processed / 'prod_protein.xtc'))
    topology = mda.Universe(str(processed / 'solution.tpr'))
    for field in ['names','resids','resnames']:
        if not np.array_equal(getattr(expected,field),getattr(topology.atoms,field)):
            raise ValueError(f'reduced TPR/source atom-order mapping failed: {field}')
        if field != 'resnames' and not np.array_equal(getattr(expected,field),getattr(u.atoms,field)):
            raise ValueError(f'processed/source atom-order mapping failed: {field}')
    pdb_expected_resnames = expected.resnames.copy()
    # GROMACS PDB serializes residue names in a four-character field. Require
    # exact protein names and the observed deterministic ligand truncation.
    pdb_expected_resnames[inputs['protein_atoms']:] = [str(name)[:4] for name in expected.resnames[inputs['protein_atoms']:]]
    if not np.array_equal(pdb_expected_resnames, u.atoms.resnames):
        raise ValueError('PDB residue-name serialization mapping failed')
    receptor = u.select_atoms('protein')
    ligand = u.atoms[inputs['protein_atoms']:inputs['solution_atoms']]
    bonds = topology.bonds.indices
    heavy = np.array([not str(name).startswith('H') for name in topology.atoms.names])
    heavy_bonds = bonds[heavy[bonds[:,0]] & heavy[bonds[:,1]]]
    ca = receptor.select_atoms('name CA')
    if len(receptor) != inputs['protein_atoms'] or len(ligand) != inputs['ligand_atoms']:
        raise ValueError('processed selection count mismatch')
    times, rows = [], []
    prev_ligand_com = None
    maximum_jump, maximum_bond, maximum_ca = 0.0,0.0,0.0
    for ts in u.trajectory:
        times.append(float(ts.time))
        pos = u.atoms.positions
        if not np.isfinite(pos).all():
            raise ValueError('nonfinite processed coordinates')
        bond_max = float(np.linalg.norm(pos[heavy_bonds[:,0]]-pos[heavy_bonds[:,1]],axis=1).max())
        ca_max = float(np.linalg.norm(np.diff(ca.positions,axis=0),axis=1).max())
        lc = ligand.center_of_mass() - receptor.center_of_mass()
        jump = 0.0 if prev_ligand_com is None else float(np.linalg.norm(lc-prev_ligand_com))
        maximum_jump,maximum_bond,maximum_ca = max(maximum_jump,jump),max(maximum_bond,bond_max),max(maximum_ca,ca_max)
        prev_ligand_com = lc.copy()
        if ts.frame % 50 == 0:
            rows.append({'time_ns':ts.time/1000,'ligand_relative_com_x_A':lc[0],'ligand_relative_com_y_A':lc[1],
                         'ligand_relative_com_z_A':lc[2],'heavy_bond_max_A':bond_max,'adjacent_CA_max_A':ca_max,
                         'ligand_relative_com_step_A':jump})
    if not np.array_equal(times,np.arange(0,100001,10)):
        raise ValueError('processed trajectory grid mismatch')
    if maximum_bond > 3.0 or maximum_ca > 4.5 or maximum_jump > 10.0:
        raise ValueError(f'PBC continuity screen failed: bond={maximum_bond}, CA={maximum_ca}, jump={maximum_jump}')
    result={'status':'PASS','frames':len(times),'first_ps':times[0],'last_ps':times[-1],
            'processed_atoms':len(u.atoms),'protein_atoms':len(receptor),'ligand_atoms':len(ligand),
            'heavy_bond_max_A':maximum_bond,'adjacent_CA_max_A':maximum_ca,'max_ligand_relative_com_10ps_step_A':maximum_jump,
            'screen_limits':{'heavy_bond_A':3.0,'adjacent_CA_A':4.5,'relative_COM_step_A':10.0},
            'screen_scope':'Numerical atom mapping and PBC discontinuity screens; not pose-stability classification',
            'source_order_and_names_resids_resnames':'PASS',
            'pdb_ligand_resname_serialization':{'source_TPR':str(expected.resnames[-1]),'PDB':str(u.atoms.resnames[-1]),'rule':'exact first four characters; all other atom identities checked'}}
    write_json(out/'processed_validation.json',result)
    pd.DataFrame(rows).to_csv(out/'pbc_sanity.csv',index=False)
    import matplotlib.pyplot as plt
    df=pd.DataFrame(rows)
    fig,axes=plt.subplots(2,1,figsize=(8,6),sharex=True)
    for coord in ['x','y','z']:
        axes[0].plot(df.time_ns,df[f'ligand_relative_com_{coord}_A'],label=coord)
    axes[0].set_ylabel('Ligand relative COM (A)');axes[0].legend()
    axes[1].plot(df.time_ns,df.heavy_bond_max_A,label='heavy bond')
    axes[1].plot(df.time_ns,df.adjacent_CA_max_A,label='adjacent CA')
    axes[1].set_ylabel('Maximum distance (A)');axes[1].set_xlabel('Time (ns)');axes[1].legend()
    fig.suptitle(case['id']);fig.tight_layout();fig.savefig(out/'pbc_sanity.png',dpi=160);plt.close(fig)
    # All metrics use full receptor interface; COM uses the own initial-contact
    # cluster. Its identities and comparability caveat are retained in config.
    from MDAnalysis.lib.distances import distance_array
    u.trajectory[0]
    rh = receptor.select_atoms('not name H*')
    lh = ligand.select_atoms('not name H*')
    distances = distance_array(rh.positions,lh.positions)
    pocket = sorted(set(map(int,rh.resids[np.any(distances<=4.0,axis=1)])))
    if not pocket:
        raise ValueError('no frame0 4A receptor-ligand contact cluster')
    receptor_selection='protein'
    ligand_selection=f"index {inputs['protein_atoms']}:{inputs['solution_atoms']-1}"
    ligand_heavy_selection=f'({ligand_selection}) and not name H*'
    system={'label':case['label'],'result_dir':str(base),'interaction_partner_role':'ligand',
            'backbone_selection':'protein and backbone','ca_selection':'protein and name CA',
            'summary_window_ns':[50,100],'occupancy_window_ns':[50,100],'rmsf_window_ns':[50,100],
            'selection_rmsd_label':case['ligand'].upper()+' heavy-atom RMSD',
            'selection_rmsd_selection_label':'ligand heavy atoms','selection_rmsd_selection':ligand_heavy_selection,
            'com_target_label':'ligand heavy atoms','plot_segids':list(set(receptor.segids)),
            'receptor':{'name':'Gpr2 '+case['genotype'].upper(),'selection':receptor_selection,
                        'interface_selection':receptor_selection,'interface_clusters':{
                          'own_initial_4A_contacts':'protein and resid '+' '.join(map(str,pocket)),
                          'whole_receptor':'protein'}},
            'galpha':{'name':case['ligand'].upper(),'selection':ligand_selection,
                      'alpha5_selection':ligand_heavy_selection,'ect_selection':ligand_heavy_selection,
                      'core_backbone_selection':ligand_heavy_selection},'junction_rmsf_regions':{},
            'initial_contact_resids':pocket,'input_provenance':inputs['input_contract'],
            'interpretation_boundary':'single_rep_exploratory_only; different parent/lid/pose; no mutation causality/affinity ranking/mechanistic proof'}
    config={'default':case['id'],'systems':{case['id']:system}}
    write_json(base/'system_config.json',config)
    write_json(out/'selection_audit.json',{'receptor_atoms':len(receptor),'receptor_residues':len(receptor.residues),
        'fit_atoms':len(receptor.select_atoms('backbone')),'ligand_atoms':len(ligand),'ligand_heavy_atoms':len(lh),
        'own_initial_contact_resids':pocket,'whole_receptor_com':'same residue set across cases',
        'own_contact_com_caveat':'Different own frame0 residue clusters; use as within-case motion, not matched pocket comparison'})
    return base/'system_config.json'


def run_case(batch,case,mode):
    base=Path(batch['output_root'])/case['id'];out=base/'evidence'
    out.mkdir(parents=True,exist_ok=True)
    state=base/'run_state_events.tsv'
    if not state.exists():
        state.write_text('observed_at\tstate\tsource\tdetail\n')
    def event(status,detail):
        with state.open('a') as s:
            s.write(f'{datetime.now(timezone.utc).isoformat()}\t{status}\t{__file__}\t{detail}\n')
        print(case['id'],status,detail,flush=True)
    try:
        event('RUNNING_VERIFIED','current input validation or verified derived inputs')
        if mode not in ['metrics', 'resume_metrics']:
            inputs,files=validate_segments(batch,case,out)
            if mode=='preflight':
                event('INPUT_VALIDATED','formal segments current time/atom checks and retained SHA evidence PASS')
                return
            merged=base/'merged_full.xtc'
            if merged.exists():
                raise FileExistsError(f'refuse overwrite: {merged}')
            command([batch['gmx'],'trjcat','-f',*files,'-o',merged,'-tu','ps'],out/'merge.log')
            times,_,_=read_xtc(merged,case['full_atoms'])
            if not np.array_equal(times,np.arange(0,100001,10)):
                raise ValueError('merged XTC is not the exact unique 10001-frame grid')
            gate={'status':'PASS','frames':len(times),'unique_frames':len(times),'first_ps':times[0],
                  'last_ps':times[-1],'missing_grid_points':0,'topology':inputs['topology'],
                  'trajectory':identity(merged),'evidence':inputs['evidence']}
            write_json(out/'merged_validation.json',gate)
            env=os.environ.copy();env.update({'RUN_ROOT':str(base),'GMX_CMD':batch['gmx'],'PREFIX':'production',
                'PROD_DIR':str(base),'PROD_LOG_DIR':str(out),'OUT_DIR':str(base/'processed/rep1'),
                'TPR_INPUT':inputs['topology']['path'],'XTC_INPUT':str(merged),
                'PYTHON_CMD':sys.executable,'INDEX_FILE':str(out/'source_index.ndx'),
                'EXPECTED_SOLUTION_ATOMS':str(inputs['solution_atoms']),'EXPECTED_FIT_ATOMS':str(inputs['fit_atoms']),
                'EXPECTED_FRAMES':'10001','EXPECTED_FINAL_TIME_PS':'100000',
                'PRODUCTION_GATE_MODE':'verified_segments','SOURCE_VALIDATION_JSON':str(out/'merged_validation.json'),
                'PBC_ROUTE':'whole_nojump','ATTEMPT_ID':batch['run_id']})
            event('RUNNING_VERIFIED','merged exact grid PASS; PBC processing')
            command(['bash',Path(batch['source_root'])/'experiments/md-simulation/scripts/postprocess_gpr_md_rep.sh'],out/'postprocess.log',env=env)
            config=processed_gate(case,base,inputs)
            event('POSTPROCESS_VALIDATED','processed mapping/grid/bond/COM sanity PASS')
        else:
            if mode == 'resume_metrics':
                inputs=json.loads((out/'input_validation.json').read_text())
                if sha256(inputs['topology']['path']) != inputs['topology']['sha256']:
                    raise ValueError('source TPR identity changed before recovery')
                config=processed_gate(case,base,inputs)
                event('POSTPROCESS_VALIDATED','recovered PDB serialization mapping; grid/bond/COM sanity PASS')
            else:
                if json.loads((out/'processed_validation.json').read_text())['status']!='PASS':
                    raise ValueError('missing processed validation')
                config=base/'system_config.json'
        if mode=='process':
            return
        env=os.environ.copy();env.update({'CHIMERIC_MD_CONFIG':str(config),'CHIMERIC_MD_REPS':'1',
                                         'CHIMERIC_MD_PAYLOAD_ROOT':str(base)})
        drivers={'convergence':[],'selection_rmsd':[],'hbond':['--step','50'],'com_distance':[],
                 'rmsf':[],'bsa':['--stride','50','--n-sphere-points','240'],'contacts':['--stride','50','--cutoff','4.0']}
        failures=[]
        for name,extra in drivers.items():
            try:
                event('RUNNING_VERIFIED',f'shared metric {name}; reps=1')
                command([sys.executable,Path(batch['source_root'])/f'experiments/md-simulation/analysis/chctrl/analyze_{name}.py',*extra],out/f'{name}.log',env=env)
            except Exception as exc:
                failures.append(str(exc))
        if failures:
            raise RuntimeError('; '.join(failures))
        write_json(out/'driver_completion.json',{'status':'PASS','drivers':list(drivers),'replicate_selector':'1',
                   'summary_window_ns':[50,100],'sparse_sample_spacing_ns':0.5,
                   'finished_at':datetime.now(timezone.utc).isoformat()})
        event('TERMINAL_NORMAL','seven shared drivers exited0; content acceptance remains separate')
    except Exception as exc:
        traceback.print_exc()
        write_json(out/f'failure_{mode}.json',{'status':'HOLD','error':str(exc),'observed_at':datetime.now(timezone.utc).isoformat()})
        event('TERMINAL_ABNORMAL',str(exc))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--batch-config',type=Path,required=True)
    parser.add_argument('--case',action='append')
    parser.add_argument('--mode',choices=['all','preflight','process','metrics','resume_metrics','recover_queue'],default='all')
    args=parser.parse_args()
    batch=json.loads(args.batch_config.read_text())
    os.chdir(batch['source_root'])
    for case in batch['cases']:
        if args.case is None or case['id'] in args.case:
            if args.mode == 'recover_queue':
                failure=Path(batch['output_root'])/case['id']/'evidence/failure_all.json'
                deadline=time.monotonic()+7200
                while not failure.exists() and time.monotonic()<deadline:
                    time.sleep(15)
                if not failure.exists():
                    print(case['id'],'HOLD: original processing not closed by timeout',flush=True)
                    continue
                if json.loads(failure.read_text())['error'] != 'processed/source atom-order mapping failed: resnames':
                    print(case['id'],'HOLD: original failure is not PDB name serialization; keep affected case stopped',flush=True)
                    continue
                run_case(batch,case,'resume_metrics')
            else:
                run_case(batch,case,args.mode)


if __name__=='__main__':
    main()
