#!/usr/bin/env python3
"""Manifest-driven full-length FASTA preparation; run by the user. Standard library only."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MANIFEST = ROOT / 'outputs/batches/05-af3-saturation-combinations/manifests/saturation-singles.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_fasta(path):
    records = {}
    name = None
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            name = line[1:].split()[0]
            require(name not in records, f'Duplicate header in {path}: {name}')
            records[name] = ''
        else:
            require(name is not None, f'Missing FASTA header: {path}')
            records[name] += line
    require(bool(records), f'Empty FASTA: {path}')
    return records


def single(path):
    records = read_fasta(path)
    require(len(records) == 1, f'Expected one sequence: {path}')
    return next(iter(records.values()))


def check_sources(m):
    wt = single(ROOT / m['source_fasta'])
    require(len(wt) == 406 and set(wt) <= set(m['alphabet']), 'Invalid WT length/alphabet')
    require(sha(wt.encode()) == m['source_sequence_sha256'], 'WT sequence hash changed')
    expected_ids = {'baseline'} | {
        f'{old}{pos}{aa}' for pos, old in [(84, 'N'), (110, 'V'), (368, 'V')]
        for aa in m['alphabet'] if aa != old
    }
    rows = m['variants']
    require(len(rows) == 58 and {r['id'] for r in rows} == expected_ids, 'Incorrect design coverage')
    require(sum(r['new_af_required'] for r in rows) == 48, 'Expected 48 new AF jobs')
    require(len({r['af_job_name'] for r in rows}) == 58, 'Duplicate AF job names')
    for r in rows:
        require(r['af_job_name'] == 'gpr2_b05_fl_' + r['id'].lower(), 'Invalid AF job name')
        if r['id'] != 'baseline':
            pos = r['position']
            require((pos, r['from']) in [(84, 'N'), (110, 'V'), (368, 'V')], 'Unexpected site')
            require(wt[pos-1] == r['from'], f'WT residue mismatch: {r["id"]}')
            require(r['to'] in m['alphabet'] and r['to'] != r['from'], 'Invalid substitution')
            require(r['id'] == f'{r["from"]}{pos}{r["to"]}', 'ID/substitution mismatch')
        source = r['historical_source']
        require(r['new_af_required'] == (source is None), 'AF/reuse flag mismatch')
        if source:
            check_mapping(source)
            old = single(ROOT / source['paths']['fasta'])
            diffs = [(i+1, a, b) for i, (a, b) in enumerate(zip(wt, old)) if a != b]
            require(len(old) == 406 and diffs == [(r['position'], r['from'], r['to'])],
                    f'Historical FASTA mismatch: {r["id"]}')
    for source in m['historical_wt'].values():
        check_mapping(source)
        require(single(ROOT / source['paths']['fasta']) == wt, 'Historical WT mismatch')
    print('SOURCE PASS: WT 406 aa; N84/V110/V368; 58 designs; 10 reuse FASTAs; 2 historical WTs')
    print('Historical CIF/job files: existence and hashes checked; CIF sequence validation remains pending.')
    return wt


def check_mapping(source):
    for key, rel in source['paths'].items():
        require(sha((ROOT / rel).read_bytes()) == source['file_sha256'][key], f'Historical file changed: {rel}')


def sequences(m, wt):
    result = {}
    for r in m['variants']:
        s = list(wt)
        if r['position'] is not None:
            s[r['position']-1] = r['to']
        result[r['id']] = ''.join(s)
    return result


def fasta(name, seq):
    return f'>{name}\n' + '\n'.join(seq[i:i+70] for i in range(0, len(seq), 70)) + '\n'


def submission_table(m):
    lines = ['variant_id\taf_job_name\tfasta_path']
    lines += [f'{r["id"]}\t{r["af_job_name"]}\tindividual/{r["id"]}.fasta'
              for r in m['variants'] if r['new_af_required']]
    return '\n'.join(lines) + '\n'


def validate(m, wt, out):
    expected = sequences(m, wt)
    names = {r['id']: r['af_job_name'] for r in m['variants']}
    require({p.name for p in (out / 'individual').iterdir()} == {f'{v}.fasta' for v in expected},
            'Individual FASTA file set mismatch')
    for name, seq in expected.items():
        require(read_fasta(out / 'individual' / f'{name}.fasta') == {names[name]: seq}, f'FASTA mismatch: {name}')
    require(read_fasta(out / 'all_58.fasta') == {names[n]: s for n, s in expected.items()}, 'Combined FASTA mismatch')
    new = {r['id']: expected[r['id']] for r in m['variants'] if r['new_af_required']}
    require(read_fasta(out / 'new_af_48.fasta') == {names[n]: s for n, s in new.items()}, 'New-AF FASTA mismatch')
    require((out / 'submission_ids.txt').read_text().splitlines() == list(new), 'Submission list mismatch')
    require((out / 'submission_jobs.tsv').read_text() == submission_table(m), 'Job mapping mismatch')
    require(len(set(expected.values())) == 58, 'Duplicate sequences')
    receipt = json.loads((out / 'checksums.json').read_text())
    require(receipt['manifest_sha256'] == sha(MANIFEST.read_bytes()), 'Manifest changed since generation')
    actual_files = {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p.name != 'checksums.json'}
    require(actual_files == set(receipt['files']), 'Output file inventory changed')
    for rel, digest in receipt['files'].items():
        require(sha((out / rel).read_bytes()) == digest, f'Output hash mismatch: {rel}')
    print('FASTA PASS: 57 single mutants + baseline; 406 aa each; exact mutation differences; 48 new AF jobs')
    print(f'Output: {out}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['check', 'generate', 'validate'])
    args = parser.parse_args()
    m = json.loads(MANIFEST.read_text())
    wt = check_sources(m)
    out = (ROOT / 'vina/inputs/receptors/fasta' / Path(__file__).resolve().parents[1].name)
    if args.stage == 'check':
        return
    if args.stage == 'generate':
        require(not out.exists(), f'Refusing to overwrite existing directory: {out}')
        seqs = sequences(m, wt)
        names = {r['id']: r['af_job_name'] for r in m['variants']}
        (out / 'individual').mkdir(parents=True, exist_ok=False)
        for name, seq in seqs.items():
            (out / 'individual' / f'{name}.fasta').write_text(fasta(names[name], seq))
        (out / 'all_58.fasta').write_text(''.join(fasta(names[n], s) for n, s in seqs.items()))
        new = [r['id'] for r in m['variants'] if r['new_af_required']]
        (out / 'new_af_48.fasta').write_text(''.join(fasta(names[n], seqs[n]) for n in new))
        (out / 'submission_ids.txt').write_text('\n'.join(new) + '\n')
        (out / 'submission_jobs.tsv').write_text(submission_table(m))
        receipt = {'manifest_sha256': sha(MANIFEST.read_bytes()), 'files': {
            str(p.relative_to(out)): sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()
        }}
        (out / 'checksums.json').write_text(json.dumps(receipt, indent=2) + '\n')
    validate(m, wt, out)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        raise SystemExit(f'STOP: {exc}')
