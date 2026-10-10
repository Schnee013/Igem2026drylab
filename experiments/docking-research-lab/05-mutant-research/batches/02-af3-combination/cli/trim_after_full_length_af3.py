"""Validate a full-length AF3 prediction, then remove docking-only flexible segments."""
import argparse
import hashlib
import json
from pathlib import Path

AA = dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(), 'ARNDCQEGHILKMFPSTWYV'))
ORIGINAL = list(range(22, 164)) + list(range(179, 407))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-pdb', type=Path, required=True)
    p.add_argument('--expected-fasta', type=Path, required=True)
    p.add_argument('--job-request', type=Path, required=True)
    p.add_argument('--output-pdb', type=Path, required=True)
    p.add_argument('--report-json', type=Path, required=True)
    a = p.parse_args()
    expected = ''.join(x.strip() for x in a.expected_fasta.read_text().splitlines() if not x.startswith('>'))
    assert len(expected) == 406, 'AF3 prediction requires the full-length 406-aa sequence'
    request = json.loads(a.job_request.read_text())
    assert isinstance(request, list) and len(request) == 1
    job = request[0]
    assert len(job['sequences']) == 1
    protein = job['sequences'][0]['proteinChain']
    assert protein['count'] == 1
    assert protein['sequence'] == expected, 'AF3 job sequence differs from expected full-length 406-aa sequence. Re-predict the full-length protein before proceeding.'
    residues, atoms, lines = {}, set(), []
    for line in a.input_pdb.read_text().splitlines():
        if line.startswith('HETATM'):
            raise ValueError('Unexpected HETATM in single-protein AF3 model')
        if not line.startswith('ATOM  '):
            continue
        assert line[21] == 'A' and line[26] == ' ' and line[16] == ' '
        number = int(line[22:26]); name = line[17:20]
        assert 1 <= number <= 406
        if number in residues:
            assert residues[number] == name
        residues[number] = name
        key = (number, line[12:16]); assert key not in atoms; atoms.add(key)
        if number in ORIGINAL:
            lines.append(line)
    assert set(residues) == set(range(1, 407))
    assert ''.join(AA[residues[n]] for n in range(1, 407)) == expected
    for out in (a.output_pdb, a.report_json):
        assert not out.exists(), f'Refusing to overwrite: {out}'
        out.parent.mkdir(parents=True, exist_ok=True)
    a.output_pdb.write_text('\n'.join(lines) + '\nEND\n')
    report = {
        'job_name': job['name'], 'model_seeds': job.get('modelSeeds'),
        'prediction_residue_count': 406, 'docking_residue_count': 370,
        'deleted_original_ranges': [[1,21],[164,178]],
        'retained_coordinate_changes': False, 'renumbered': False,
        'mapping': [{'af3_number': n, 'original_number': n} for n in ORIGINAL],
        'files': {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in (a.input_pdb, a.expected_fasta, a.job_request, a.output_pdb)},
    }
    a.report_json.write_text(json.dumps(report, indent=2) + '\n')
    print('Full-length sequence verified; removed 1-21,164-178 after prediction; original numbering and retained coordinates unchanged:', a.output_pdb)


if __name__ == '__main__':
    main()
