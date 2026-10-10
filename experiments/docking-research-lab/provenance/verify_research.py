"""Read-only integrity checks for the reorganized delivery; Python standard library only."""
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def check(root, source_root=None):
    errors = []
    stats = {}
    cached = {}

    def digest(path):
        if path not in cached:
            cached[path] = sha256(path)
        return cached[path]

    manifest = root / 'provenance/checksums.sha256'
    expected_paths = set()
    for line in manifest.read_text().splitlines():
        expected, relative = line.split('  ', 1)
        path = root / relative
        expected_paths.add(relative)
        if not path.is_file():
            errors.append('Missing delivery file: ' + relative)
        elif digest(path) != expected:
            errors.append('Changed delivery file: ' + relative)
    stats['delivery_files_checked'] = len(expected_paths)
    actual_paths = {
        str(p.relative_to(root)) for p in root.rglob('*')
        if p.is_file() and not any(x in {'.git', '.delivery-local', '__pycache__'}
                                   for x in p.relative_to(root).parts)
        and p.name != '.DS_Store'
    }
    extras = actual_paths - expected_paths - {'provenance/checksums.sha256'}
    errors.extend('Unlisted delivery file: ' + p for p in sorted(extras))

    sources = check_sources(root)
    errors.extend(sources['errors'])
    stats.update(sources['checks'])

    generated = json.loads((root / 'provenance/generated-files.json').read_text())
    changed = json.loads((root / 'provenance/documentation-changes.json').read_text())
    docs = sorted({p for p in generated if p.endswith('.md')} |
                  {r['destination'] for r in changed})
    checked_links = 0
    for relative in docs:
        path = root / relative
        if not path.exists():
            errors.append('Missing document: ' + relative)
            continue
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for target in re.findall(r'\]\(([^)\n]+)\)', text):
            target = unquote(target.split('#', 1)[0])
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            checked_links += 1
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()):
                errors.append('Link escapes delivery: ' + relative + ' -> ' + target)
            elif not resolved.exists():
                errors.append('Broken link: ' + relative + ' -> ' + target)
    stats['reading_documents_checked'] = len(docs)
    stats['local_links_checked'] = checked_links

    if source_root is not None:
        with (root / 'provenance/file-map.csv').open(newline='') as handle:
            mapping = {r['source']: r for r in csv.DictReader(handle)}
        for relative, row in mapping.items():
            path = source_root / relative
            if not path.is_file() or sha256(path) != row['sha256']:
                errors.append('Original source changed or missing: ' + relative)
        stats['original_source_files_checked'] = len(mapping)
    return {'status': 'PASS' if not errors else 'FAIL', 'checks': stats, 'errors': errors}



def check_sources(root):
    errors = []
    stats = {}
    cached = {}

    def digest(path):
        if path not in cached:
            cached[path] = sha256(path)
        return cached[path]

    with (root / 'provenance/file-map.csv').open(newline='') as handle:
        mapping = {r['source']: r for r in csv.DictReader(handle)}
    indirect_receptors = set()
    for relative in [
        '05-mutant-research/analysis/04-07-single-mutants/data/single-mutants.json',
        '05-mutant-research/analysis/data/combination-mutants.json',
    ]:
        data = json.loads((root / relative).read_text())
        sources = data['source_sha256']
        for old_path, expected in sources.items():
            row = mapping.get(old_path)
            if not row:
                errors.append('Unmapped analysis source: ' + old_path)
                continue
            path = root / row['destination']
            if not path.is_file() or digest(path) != expected:
                errors.append('Analysis source mismatch: ' + old_path)
            if path.is_file() and old_path.endswith('/top1_contacts/ifp/metadata.json'):
                metadata = json.loads(path.read_text())
                receptor = path.parents[3] / 'receptor.json'
                indirect_receptors.add(str(receptor.relative_to(root)))
                if not receptor.is_file() or digest(receptor) != metadata['receptor_sha256']:
                    errors.append('Contact receptor source mismatch: ' + str(receptor.relative_to(root)))
        stats[Path(relative).stem + '_source_hashes_checked'] = len(sources)
    stats['indirect_contact_receptors_checked'] = len(indirect_receptors)

    batch_root = root / '05-mutant-research/batches'
    counts = {}
    for folder in sorted(batch_root.iterdir()):
        if folder.is_dir():
            poses = list((folder / 'run-01').glob('*/ascr*/poses.pdbqt'))
            counts[folder.name[:2]] = len(poses)
    expected_counts = dict(zip(['01', '02', '03', '04', '05', '06', '07', '08'],
                               [6, 6, 16, 38, 116, 14, 40, 36]))
    if counts != expected_counts:
        errors.append('Batch counts differ: ' + repr(counts))
    stats['batch_docking_outputs'] = counts

    python_files = set((root / 'shared/scripts').glob('*.py'))
    python_files.update((root / '05-mutant-research').rglob('*.py'))
    python_files.add(Path(__file__).resolve())
    for path in sorted(python_files):
        try:
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            errors.append('Python syntax: ' + str(path) + ': ' + str(exc))
    stats['python_files_parsed'] = len(python_files)

    return {'status': 'PASS' if not errors else 'FAIL', 'checks': stats, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-root', type=Path,
                        help='Optional additional check that original source files are unchanged.')
    args = parser.parse_args()
    result = check(args.root.resolve(), args.source_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
