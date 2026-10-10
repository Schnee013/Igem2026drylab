#!/usr/bin/env python3
"""Read-only coordinate/provenance audit; no MD, rebuilding or geometry acceptance.

Requires Python 3 and NumPy. All coordinates are compared in angstroms. Fit only
the protein backbone outside lid 164:178; apply that SAME rigid transform to the
lid and ligand. A ligand-only fit would conceal replacement of a docking pose.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

AA = dict(zip(
    'ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),
    'ARNDCQEGHILKMFPSTWYV'))
AA.update(HSD='H', HSE='H', HSP='H')
LID = set(range(164, 179))
PARENTS = {
    'n84v': 'sources/n84v/af3_original/raw_model0.pdb',
    'v368r': 'sources/v368r/af3_original/raw_model0.pdb',
    'wt': 'sources/native_wt/full_length.pdb',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdb(path):
    atoms = []
    for line in path.read_text().splitlines():
        if line.startswith('ATOM  '):
            atoms.append(dict(resid=int(line[22:26]), resname=line[17:20].strip(),
                              name=line[12:16].strip(),
                              xyz=[float(line[i:i+8]) for i in (30, 38, 46)]))
    return atoms


def gro(path):
    lines = path.read_text().splitlines()
    n = int(lines[1])
    assert len(lines) >= n + 3
    return [dict(resid=int(s[:5]), resname=s[5:10].strip(), name=s[10:15].strip(),
                 xyz=[10*float(s[i:i+8]) for i in (20, 28, 36)]) for s in lines[2:n+2]]


def itp(path):
    sections = {}
    section = None
    for line in path.read_text().splitlines():
        line = line.split(';')[0].strip()
        if line.startswith('['):
            section = line.strip('[] ').lower()
        elif line and not line.startswith('#') and section:
            sections.setdefault(section, []).append(line.split())
    return sections


def sdf(path):
    lines = path.read_text().splitlines()
    assert 'V2000' in lines[3]
    n, nb = int(lines[3][:3]), int(lines[3][3:6])
    xyz = np.array([[float(s[i:i+10]) for i in (0, 10, 20)] for s in lines[4:n+4]])
    elements = [s[31:34].strip() for s in lines[4:n+4]]
    edges = {tuple(sorted((int(s[:3])-1, int(s[3:6])-1))) for s in lines[n+4:n+4+nb]}
    return xyz, elements, edges


def sequence(atoms):
    ca = [a for a in atoms if a['name'] == 'CA']
    assert [a['resid'] for a in ca] == list(range(1, 407))
    return ''.join(AA[a['resname']] for a in ca)


def key(a, aliases=False):
    name = a['name']
    if aliases:
        if a['resname'] == 'ILE' and name == 'CD1':
            name = 'CD'
        if a['resid'] == 406:
            name = {'O': 'OT1', 'OXT': 'OT2'}.get(name, name)
    return a['resid'], name


def indexed(atoms, aliases=False):
    d = {key(a, aliases): a for a in atoms}
    assert len(d) == len(atoms), 'Duplicate protein atom keys'
    return d


def xyz(atoms):
    return np.array([a['xyz'] for a in atoms])


def fit(a, b):
    ac, bc = a.mean(axis=0), b.mean(axis=0)
    u, _, vt = np.linalg.svd((a-ac).T @ (b-bc))
    rot = u @ np.diag([1., 1., np.linalg.det(u @ vt)]) @ vt
    assert abs(np.linalg.det(rot) - 1) < 1e-8
    return rot, bc - ac @ rot


def stats(dist):
    return {'n': len(dist), 'rmsd_A': float(np.sqrt(np.mean(dist**2))),
            'max_A': float(np.max(dist))}


def backbone_keys(a, b):
    # Terminal O/OT1 has preparation changes: exclude explicitly, not silently.
    return sorted(k for k in a.keys() & b.keys()
                  if k[0] not in LID and k[1] in {'N', 'CA', 'C', 'O'})


def aligned_stats(a, b, keys, rot, trans):
    ax = xyz([a[k] for k in keys]) @ rot + trans
    bx = xyz([b[k] for k in keys])
    return stats(np.linalg.norm(ax-bx, axis=1))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--retained', required=True, type=Path)
    p.add_argument('--selection', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    root, sel, out = args.retained.absolute(), args.selection.absolute(), args.output.absolute()
    manifest = json.loads((root/'manifest.json').read_text())
    expected_hashes = {x['path']: x.get('sha256') for x in manifest['files']}
    file_records = {}

    def evidence(path, expected=None):
        path = Path(os.path.abspath(path))
        digest = sha(path)
        try:
            rel = str(path.relative_to(root))
            expected = expected or expected_hashes.get(rel)
        except ValueError:
            rel = str(path)
        if expected:
            assert digest == expected, f'Hash mismatch: {path}'
        file_records[str(path)] = dict(path=str(path), resolved_path=str(path.resolve()),
                                      sha256=digest, expected_sha256=expected,
                                      manifest_or_explicit_hash_match=(digest == expected) if expected else None)
        return str(path)

    wtseq = ''.join(s.strip() for s in (root/'sources/WT_sequence.fasta').read_text().splitlines()
                    if not s.startswith('>'))
    evidence(root/'sources/WT_sequence.fasta')
    parent_atoms = {g: pdb(root/path) for g, path in PARENTS.items()}
    for path in PARENTS.values():
        evidence(root/path)
    old_cases = json.loads((root/'cases.json').read_text())['cases']
    current = {c['comparison_case']: c for c in json.loads((sel/'selection.json').read_text())['cases']}
    evidence(root/'cases.json')
    evidence(root/'manifest.json')
    evidence(sel/'selection.json')
    results = []
    tolerance = 0.02  # File identity heuristic allowing GRO 0.001 nm rounding; not a geometry cutoff.
    for case in old_cases:
        cid = case['case']
        meta = case['selected_preparation']
        genotype, ligand = meta['genotype'], meta['ligand']
        source_group = 'native_wt' if genotype == 'wt' else genotype
        pose = root/f'sources/{source_group}/{ligand}/top1.sdf'
        prep = root/case['input']
        contract_path = prep/'input_contract.json'
        contract = json.loads(contract_path.read_text())
        protein_count = int(contract['atoms'])
        ligand_path = prep/f'toppar/{ligand.upper()}.itp'
        ligand_top = itp(ligand_path)
        ligand_count = len(ligand_top['atoms'])
        protein_top = itp(prep/'toppar/PROA.itp')
        dry = gro(prep/'dry.gro')
        # Protein and ligand occupy known molecule blocks. Residue IDs are reused
        # by POPC, so selecting all residue 407 or all residues <=406 is unsafe.
        protein = dry[:protein_count]
        placed_ligand = dry[protein_count:protein_count+ligand_count]
        assert [(a['resid'], a['name']) for a in protein] == [(int(a[2]), a[4]) for a in protein_top['atoms']]
        assert [a['name'] for a in placed_ligand] == [a[4] for a in ligand_top['atoms']]
        assert all(a['resname'] == ligand.upper()[:5] and a['resid'] == 407 for a in placed_ligand)
        expected_seq = list(wtseq)
        if genotype == 'n84v':
            expected_seq[83] = 'V'
        elif genotype == 'v368r':
            expected_seq[367] = 'R'
        assert sequence(protein) == sequence(parent_atoms[genotype]) == ''.join(expected_seq)
        # Parents are moved into their documented docking frame BEFORE the fit.
        parent = [dict(a) for a in parent_atoms[genotype]]
        alignment_path = None
        if genotype != 'wt':
            alignment_path = root/f'sources/{genotype}/docking_receptor/alignment.json'
            al = json.loads(alignment_path.read_text())
            x = xyz(parent) @ np.array(al['rotation_matrix']) + np.array(al['translation_vector'])
            for a, coords in zip(parent, x):
                a['xyz'] = coords.tolist()
            evidence(alignment_path)
        dock_path = root/(f'sources/{genotype}/docking_receptor/input.pdb' if genotype != 'wt'
                          else 'sources/native_wt/deltaN_docking_receptor.pdb')
        dock_atoms = indexed(pdb(dock_path))
        full_atoms = indexed(parent)
        assert set(dock_atoms).issubset(full_atoms)
        removed_residues = {k[0] for k in full_atoms} - {k[0] for k in dock_atoms}
        assert removed_residues == set(range(1, 22)) | LID
        dock_keys = sorted(dock_atoms)
        frame_stats = aligned_stats(full_atoms, dock_atoms, dock_keys, np.eye(3), np.zeros(3))
        assert frame_stats['max_A'] < 0.002, 'Parent does not reconstruct the documented docking receptor frame'
        evidence(dock_path)
        a, b = indexed(parent, True), indexed(protein)
        backbone = backbone_keys(a, b)
        assert len(backbone) == 1563
        rot, trans = fit(xyz([a[k] for k in backbone]), xyz([b[k] for k in backbone]))
        lid = sorted(k for k in a if k[0] in LID and k[1] in {'N', 'CA', 'C', 'O'})
        assert len(lid) == 60
        terminal = [(406, 'OT1'), (406, 'OT2')]
        assert set(a).issubset(b)
        heavy = sorted(k for k in a if k not in terminal)
        protein_stats = aligned_stats(a, b, heavy, rot, trans)
        lid_stats = aligned_stats(a, b, lid, rot, trans)
        backbone_stats = aligned_stats(a, b, backbone, rot, trans)
        assert protein_stats['max_A'] < tolerance and lid_stats['max_A'] < tolerance
        terminal_delta = {str(k): aligned_stats(a, b, [k], rot, trans)['max_A'] for k in terminal}
        cross = {}
        for donor, atoms in parent_atoms.items():
            da = indexed(atoms, True)
            keys = backbone_keys(da, b)
            rr, tt = fit(xyz([da[k] for k in keys]), xyz([b[k] for k in keys]))
            cross[donor] = aligned_stats(da, b, keys, rr, tt)['rmsd_A']
        lx, le, edges = sdf(pose)
        placed = xyz(placed_ligand)
        de = [a['name'][0] for a in placed_ligand]
        assert len(lx) == ligand_count and set(de) <= {'C', 'O', 'H'}
        distance = np.linalg.norm((lx @ rot + trans)[:, None, :] - placed[None, :, :], axis=2)
        distance[np.array(le)[:, None] != np.array(de)[None, :]] = np.inf
        mapping = np.argmin(distance, axis=1)
        assert len(set(mapping)) == len(mapping), 'Pose atom map is not one-to-one'
        deviations = distance[np.arange(len(lx)), mapping]
        assert max(deviations) < tolerance
        mapped_edges = {tuple(sorted((int(mapping[i]), int(mapping[j])))) for i, j in edges}
        topology_edges = {tuple(sorted((int(row[0])-1, int(row[1])-1))) for row in ligand_top['bonds']}
        assert mapped_edges == topology_edges, 'Ligand bond graph differs after atom mapping'
        for path in (contract_path, prep/'dry.gro', prep/'toppar/PROA.itp', ligand_path, pose):
            evidence(path)
        preheat = root/case['preheat']
        evidence(preheat/'dry.gro')
        assert sha(preheat/'dry.gro') == sha(prep/'dry.gro')
        em = preheat/meta['em_source']
        hold = root/case['heating_files']['hold.gro']
        evidence(em, meta['em_sha256'])
        evidence(hold, meta['final_gro_sha256'])
        for endpoint in (em, hold):
            rows = gro(endpoint)
            assert [(q['resid'], q['resname'], q['name']) for q in rows[:protein_count+ligand_count]] == [
                (q['resid'], q['resname'], q['name']) for q in dry[:protein_count+ligand_count]]
            assert sequence(rows[:protein_count]) == ''.join(expected_seq)
        chosen = current[cid]
        selected_info = dict(selected_case_id=chosen['selected_case_id'],
                             status='EXISTING_INPUT_PROVENANCE_MATCHED_NOT_GEOMETRY_ACCEPTED')
        if chosen.get('selection_contract'):
            cp = sel/chosen['selection_contract']
            cc = json.loads(cp.read_text())
            evidence(cp)
            for part in ('receptor_parent', 'ligand_pose'):
                evidence(sel/cc[part]['path'], cc[part]['sha256'])
            assert (sel/cc['receptor_parent']['path']).resolve() == (root/PARENTS[genotype]).resolve()
            assert (sel/cc['ligand_pose']['path']).resolve() == pose.resolve()
            if genotype != 'wt':
                fc = cc['coordinate_frame_contract']['receptor_to_ligand_frame']
                evidence(sel/fc['path'], fc['sha256'])
                assert (sel/fc['path']).resolve() == alignment_path.resolve()
            assert cc['coordinate_status'] == 'NOT_GENERATED' and cc['accepted_receptor_path'] is None
            planned = {k: dict(path=str(sel/v), exists=(sel/v).exists()) for k, v in cc['planned_coordinate_files'].items()}
            assert not any(v['exists'] for v in planned.values())
            selected_info.update(status='NOT_GENERATED_CANNOT_AUDIT_NEW_LID', contract=str(cp), planned_files=planned)
        results.append(dict(case=cid, selected=selected_info, parent=str(root/PARENTS[genotype]),
            pose=str(pose), docking_alignment=str(alignment_path) if alignment_path else 'already aligned WT parent',
            docking_receptor=str(dock_path), docking_frame_shared_atom_match=frame_stats,
            docking_deleted_residues=sorted(removed_residues),
            dry=str(prep/'dry.gro'), selected_em=str(em), preheat_endpoint=str(hold),
            protein_atoms_with_H=protein_count, receptor_residues=406,
            sequence_differences_from_WT=[f'{w}{i+1}{v}' for i, (w,v) in enumerate(zip(wtseq,expected_seq)) if w != v],
            outside_lid_backbone=backbone_stats, lid_backbone_same_transform=lid_stats,
            parent_heavy_except_terminal_oxygens=protein_stats,
            terminal_oxygen_displacements_A=terminal_delta,
            terminal_note='Local C-terminal oxygen changes; consistent with terminal topology preparation. Original pdb2gmx log not retained here.',
            donor_control_outside_lid_rmsd_A=cross,
            ligand_all_atoms=stats(deviations), ligand_heavy=stats(deviations[np.array(le) != 'H']),
            ligand_bond_graph_matches=True,
            sdf_atom_1based_to_itp_atom_1based=[int(i)+1 for i in mapping],
            ligand_relative_pose_fit='protein-derived transform only; no independent ligand fit',
            transform_docking_to_dry=dict(rotation=rot.tolist(), translation_A=trans.tolist())))
    repair = json.loads((root/'provenance/trp174_orientation_repair.json').read_text())
    before_path = root/'data/preheat/native_wt_ascr18/attempt6_trp174_orientation/ionized.gro'
    after_path = before_path.parent/'sidechain_repaired.gro'
    evidence(root/'provenance/trp174_orientation_repair.json')
    evidence(before_path, repair['source_sha256'])
    evidence(after_path, repair['selected']['candidate_sha256'])
    before, after = gro(before_path), gro(after_path)
    assert len(before) == len(after)
    assert [(a['resid'],a['resname'],a['name']) for a in before] == [(a['resid'],a['resname'],a['name']) for a in after]
    changed = np.where(np.any(xyz(before) != xyz(after), axis=1))[0]
    changes = [dict(index_1based=int(i)+1, resid=before[i]['resid'], name=before[i]['name']) for i in changed]
    assert len(changed) == 17 and all(q['resid'] == 174 for q in changes)
    assert {q['name'] for q in changes} == set(repair['selected']['changed_atom_names'])
    assert not {q['name'] for q in changes} & {'N','HN','H','CA','HA','C','O','CB'}
    assert len(before) - len(changed) == repair['selected']['unchanged_atoms']
    result = dict(as_of=datetime.now(timezone.utc).isoformat(),
        scope='Original six input provenance, current selection availability, direct WT repair diff. Not geometry or production readiness acceptance.',
        runtime=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()),
        rounding_match_tolerance_A=tolerance, tolerance_use='file identity operational heuristic, not scientific go/no-go cutoff',
        retained_root=str(root), selection_root=str(sel), cases=results,
        wt_ascr18_repair_direct_diff=dict(before=str(before_path), after=str(after_path), total_atoms=len(before),
            changed_count=len(changed), changed_heavy_count=sum(not x['name'].startswith('H') for x in changes),
            unchanged_count=len(before)-len(changed), changes=changes, backbone_and_ligand_unchanged=True),
        all_six_selected_coordinates_ready=False, all_original_six_provenance_checks_passed=True,
        evidence_files=list(file_records.values()), script_sha256=sha(Path(__file__)))
    out.mkdir(parents=True, exist_ok=True)
    (out/'audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    with (out/'per_case.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['comparison_case','selected_case_id','selected_status','parent','pose','dry','selected_em','preheat_endpoint',
                    'residues','outside_lid_backbone_rmsd_A','lid_backbone_rmsd_A','ligand_heavy_rmsd_A',
                    'ligand_max_A','bond_graph_matches','terminal_OT1_delta_A','terminal_OT2_delta_A'])
        for c in results:
            w.writerow([c['case'],c['selected']['selected_case_id'],c['selected']['status'],c['parent'],c['pose'],c['dry'],
                c['selected_em'],c['preheat_endpoint'],c['receptor_residues'],c['outside_lid_backbone']['rmsd_A'],
                c['lid_backbone_same_transform']['rmsd_A'],c['ligand_heavy']['rmsd_A'],c['ligand_all_atoms']['max_A'],
                c['ligand_bond_graph_matches'],*c['terminal_oxygen_displacements_A'].values()])
    print(json.dumps(dict(original_cases_checked=len(results), existing_selected=4, selected_new_coordinates_missing=2,
                          evidence_files=len(file_records), wt_repair_changed_atoms=len(changed), output=str(out)),ensure_ascii=False))


if __name__ == '__main__':
    main()
