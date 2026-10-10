"""Helpers for the user-run model-0 deltaN alanine experiment. Never runs Vina."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

GROUPS = {
    'baseline': {},
    'N84A_L90A_R345A': {84: 'ASN', 90: 'LEU', 345: 'ARG'},
    'V110A_R181A_W338A_V368A': {110: 'VAL', 181: 'ARG', 338: 'TRP', 368: 'VAL'},
}
EXPECTED = set(range(22, 164)) | set(range(179, 407))
INTERACTIONS = ['Anionic', 'CationPi', 'Cationic', 'HBAcceptor', 'HBDonor',
                'Hydrophobic', 'PiCation', 'PiStacking', 'VdWContact']


def atoms(path):
    result = {}
    for line in path.read_text().splitlines():
        if not line.startswith('ATOM  '):
            continue
        key = (line[21], int(line[22:26]), line[26], line[12:16].strip())
        if line[76:78].strip() in ('H', 'D', 'HD', 'HS') or key[3].lstrip('0123456789').startswith(('H', 'D')):
            continue
        assert line[16] == ' ', 'Resolve alternate locations first'
        assert key not in result, f'Duplicate atom: {key}'
        result[key] = line
    return result


def build(source, out):
    original = atoms(source)
    assert {(k[0], k[1], k[2]) for k in original} == {('A', n, ' ') for n in EXPECTED}
    for mutations in GROUPS.values():
        for n, name in mutations.items():
            assert original[('A', n, ' ', 'CA')][17:20] == name
            assert {k[3] for k in original if k[1] == n} >= {'N', 'CA', 'C', 'O', 'CB'}
    for group, mutations in GROUPS.items():
        folder = out / group
        folder.mkdir(parents=True, exist_ok=True)
        destination = folder / 'input.pdb'
        assert not destination.exists(), f'Already exists: {destination}'
        lines = []
        for key, line in original.items():
            if key[1] in mutations:
                if key[3] not in {'N', 'CA', 'C', 'O', 'CB', 'OXT'}:
                    continue
                line = line[:17] + 'ALA' + line[20:]
            lines.append(line)
        destination.write_text('\n'.join(lines) + '\nEND\n')
        validate(source, destination, group)
    (out / 'construction.json').write_text(json.dumps({
        'source': str(source.resolve()),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'method': 'Fixed heavy-atom coordinates; alanine retains N CA C O CB; all groups rehydrogenated by Meeko; no relaxation',
        'groups': GROUPS,
    }, indent=2) + '\n')


def validate(source, prepared, group):
    original, current = atoms(source), atoms(prepared)
    mutations = GROUPS[group]
    expected = {k for k in original if k[1] not in mutations or k[3] in {'N', 'CA', 'C', 'O', 'CB', 'OXT'}}
    assert set(current) == expected, f'Atom/residue inventory changed: {prepared}'
    for key, line in current.items():
        name = 'ALA' if key[1] in mutations else original[key][17:20]
        assert line[17:20] == name, (key, name)
        if key[1] == 406 and key[3] in {'O', 'OXT'}:
            terminal = [('A', 406, ' ', atom) for atom in ('O', 'OXT')]
            assert {current[k][30:54] for k in terminal} == {original[k][30:54] for k in terminal}, 'Terminal oxygen geometry changed'
        else:
            assert line[30:54] == original[key][30:54], f'Heavy atom moved: {key}'
    print('Validated:', group, prepared, '370 residues; original numbering and retained coordinates')


def contacts(receptor_json, sdf, out):
    from meeko import Polymer
    from rdkit import Chem
    import prolif as plf
    polymer = Polymer.from_json(receptor_json.read_text())
    assert len(polymer.get_valid_monomers()) == 370
    # Preserve Meeko's per-residue chemical templates and explicit hydrogen coordinates.
    # No extra inter-residue bonds are inferred from spatial proximity.
    mol = Chem.Mol()
    for resid, monomer in polymer.get_valid_monomers().items():
        chain, number = resid.split(':')
        for i, atom in enumerate(monomer.rdkit_mol.GetAtoms()):
            info = Chem.AtomPDBResidueInfo()
            info.SetName(monomer.atom_names[i].rjust(4))
            info.SetResidueName(monomer.input_resname)
            info.SetResidueNumber(int(number))
            info.SetChainId(chain)
            atom.SetMonomerInfo(info)
        mol = Chem.CombineMols(mol, monomer.rdkit_mol)
    Chem.SanitizeMol(mol)
    protein = plf.Molecule.from_rdkit(mol)
    molecules = list(Chem.SDMolSupplier(str(sdf), removeHs=False))
    assert molecules and all(m is not None for m in molecules), 'Invalid SDF pose'
    assert all(Chem.GetFormalCharge(m) == -1 for m in molecules), 'Unexpected ligand charge'
    fp = plf.Fingerprint(interactions=INTERACTIONS, vicinity_cutoff=6.0)
    fp.run_from_iterable([plf.Molecule.from_rdkit(m) for m in molecules], protein, n_jobs=1)
    df = fp.to_dataframe()
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / 'ifp_presence.csv')
    union = df.T.groupby(level='protein').any().T
    union.to_csv(out / 'residue_presence.csv')
    with (out / 'residue_counts.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['residue', 'poses_with_any_contact', 'n_poses', 'frequency'])
        for residue in union:
            count = int(union[residue].sum())
            writer.writerow([residue, count, len(molecules), count / len(molecules)])
    (out / 'metadata.json').write_text(json.dumps({
        'prolif_version': plf.__version__, 'n_poses': len(molecules),
        'interactions': INTERACTIONS, 'vicinity_cutoff_A': 6.0,
        'receptor_json': str(receptor_json.resolve()), 'poses_sdf': str(sdf.resolve()),
        'receptor_sha256': hashlib.sha256(receptor_json.read_bytes()).hexdigest(),
        'sdf_sha256': hashlib.sha256(sdf.read_bytes()).hexdigest(),
    }, indent=2) + '\n')


def compare(out):
    scores = {}
    for group in GROUPS:
        for ligand in ('ascr3', 'ascr18'):
            p = out / group / ligand / 'poses.pdbqt'
            values = [float(x) for x in re.findall(r'^REMARK VINA RESULT:\s+([-\d.]+)', p.read_text(), re.M)]
            assert values, f'No scores: {p}'
            scores[group, ligand] = (min(values), len(values))
    with (out / 'score_comparison.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['group', 'ligand', 'best_score_kcal_mol', 'n_poses', 'mutant_minus_baseline'])
        for (group, ligand), (score, n) in scores.items():
            writer.writerow([group, ligand, score, n, round(score - scores['baseline', ligand][0], 4)])
    for group in GROUPS:
        folder = out / group
        # Each ligand's Vina modes are separate PyMOL states; advance states to review all.
        commands = [
            'reinitialize', f'load "{(folder / "prepared.pdb").resolve()}", receptor',
            f'load "{(folder / "ascr3/poses.pdbqt").resolve()}", ascr3',
            f'load "{(folder / "ascr18/poses.pdbqt").resolve()}", ascr18',
            'hide everything', 'show cartoon, receptor', 'color gray70, receptor',
            'show sticks, ascr3 or ascr18', 'color cyan, ascr3', 'color orange, ascr18',
            'select sites, receptor and chain A and resi 84+90+110+181+338+345+368',
            'show sticks, sites', 'hide everything, hydro', 'set all_states, off',
            'frame 1', 'zoom ascr3 or ascr18, 8',
        ]
        (folder / 'review.pml').write_text('\n'.join(commands) + '\n')


def compare_contacts(out):
    tables, sizes = {}, {}
    for group in GROUPS:
        for ligand in ('ascr3', 'ascr18'):
            folder = out / group / ligand / 'ifp'
            sizes[group, ligand] = json.loads((folder / 'metadata.json').read_text())['n_poses']
            table = {}
            for row in csv.DictReader((folder / 'residue_counts.csv').open()):
                match = re.fullmatch(r'[A-Z]+(\d+)\.A', row['residue'])
                assert match, row['residue']
                table[int(match[1])] = int(row['poses_with_any_contact'])
            tables[group, ligand] = table
    with (out / 'contact_comparison.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['group', 'original_residue_number', 'n_ascr3', 'n_ascr18',
                         'ascr3_count', 'ascr18_count', 'ascr18_minus_ascr3_count',
                         'ascr3_frequency_change_vs_baseline', 'ascr18_frequency_change_vs_baseline'])
        for group in GROUPS:
            for number in sorted(EXPECTED):
                a, b = [tables[group, lig].get(number, 0) for lig in ('ascr3', 'ascr18')]
                changes = [tables[group, lig].get(number, 0) / sizes[group, lig]
                           - tables['baseline', lig].get(number, 0) / sizes['baseline', lig]
                           for lig in ('ascr3', 'ascr18')]
                writer.writerow([group, number, sizes[group, 'ascr3'], sizes[group, 'ascr18'], a, b, b-a, *changes])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    p = subs.add_parser('build'); p.add_argument('source', type=Path); p.add_argument('out', type=Path)
    p = subs.add_parser('validate'); p.add_argument('source', type=Path); p.add_argument('prepared', type=Path); p.add_argument('group', choices=GROUPS)
    p = subs.add_parser('contacts'); p.add_argument('receptor_json', type=Path); p.add_argument('sdf', type=Path); p.add_argument('out', type=Path)
    p = subs.add_parser('compare'); p.add_argument('out', type=Path)
    p = subs.add_parser('compare_contacts'); p.add_argument('out', type=Path)
    args = vars(parser.parse_args()); action = args.pop('action'); globals()[action](**args)
