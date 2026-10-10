"""Verify GitHub-only content, or the complete delivery restored from Feishu files."""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--mode', choices=['github', 'full'], default='github')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.mode == 'full':
        spec = importlib.util.spec_from_file_location('delivery_research', root / 'provenance/verify_research.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.check(root)
    else:
        attachments = {r['path']: r for r in csv.DictReader((root / 'provenance/feishu-files.csv').open())}
        expected = {line.split('  ', 1)[1]: line.split('  ', 1)[0]
                    for line in (root / 'provenance/checksums.sha256').read_text().splitlines()}
        errors = []
        for rel, row in attachments.items():
            if expected.get(rel) != row['sha256']:
                errors.append('Attachment manifest mismatch: ' + rel)
        checked = 0
        deferred = 0
        for rel, digest in expected.items():
            path = root / rel
            if not path.is_file():
                if rel in attachments:
                    deferred += 1
                else:
                    errors.append('Missing GitHub file: ' + rel)
            elif sha256(path) != digest:
                errors.append('Changed file: ' + rel)
            else:
                checked += 1
        actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()
                  and p.name != '.DS_Store'
                  and not any(x in {'.git', '.delivery-local', '__pycache__'} for x in p.relative_to(root).parts)}
        extras = actual - set(expected) - {'provenance/checksums.sha256'}
        errors.extend('Unlisted file: ' + rel for rel in sorted(extras))
        result = {'status': 'PASS' if not errors else 'FAIL', 'mode': 'github',
                  'checked_files': checked, 'expected_feishu_files_not_restored': deferred,
                  'scientific_source_audit': 'Run --mode full after restoring all attachments',
                  'errors': errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
