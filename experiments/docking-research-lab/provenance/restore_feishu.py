"""Restore the exact Feishu attachments into this delivery without overwriting changed files."""
import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def restore(root, archive_dir):
    rows = list(csv.DictReader((root / 'provenance/feishu-files.csv').open()))
    archives = json.loads((root / 'provenance/feishu-archives.json').read_text())['archives']
    by_archive = {}
    for row in rows:
        rel = PurePosixPath(row['path'])
        if rel.is_absolute() or '..' in rel.parts or '\\' in row['path']:
            raise ValueError('Unsafe attachment path: ' + row['path'])
        target = root / row['path']
        if target.is_symlink() or not target.resolve().is_relative_to(root):
            raise ValueError('Destination escapes delivery or is a symlink: ' + row['path'])
        if target.exists() and (not target.is_file() or sha256(target) != row['sha256']):
            raise ValueError('Existing file differs; preserved without overwrite: ' + row['path'])
        by_archive.setdefault(row['archive'], {})[row['path']] = row
    # Preflight every archive before creating any output.
    for arc in archives:
        path = archive_dir / arc['name']
        if not path.is_file() or sha256(path) != arc['sha256']:
            raise ValueError('Missing or changed archive: ' + arc['name'])
        with zipfile.ZipFile(path) as z:
            expected = by_archive[arc['name']]
            if len(z.namelist()) != len(expected) or set(z.namelist()) != set(expected):
                raise ValueError('Unexpected archive members: ' + arc['name'])
            for info in z.infolist():
                if info.file_size != int(expected[info.filename]['bytes']):
                    raise ValueError('Unexpected member size: ' + info.filename)
    restored = skipped = 0
    for arc in archives:
        with zipfile.ZipFile(archive_dir / arc['name']) as z:
            for rel, row in by_archive[arc['name']].items():
                target = root / rel
                if target.exists():
                    skipped += 1
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.restore-', delete=False) as out:
                        temporary = Path(out.name)
                        with z.open(rel) as source:
                            shutil.copyfileobj(source, out)
                    if sha256(temporary) != row['sha256']:
                        raise ValueError('Restored hash mismatch: ' + rel)
                    # Exclusive creation avoids overwriting a file created since preflight.
                    with target.open('xb') as out, temporary.open('rb') as source:
                        shutil.copyfileobj(source, out)
                    restored += 1
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
    print(json.dumps({'status': 'PASS', 'restored': restored, 'already_present_and_identical': skipped}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives', type=Path, required=True, help='Folder containing all five downloaded ZIP files')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        restore(args.root.resolve(), args.archives.resolve())
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        raise SystemExit('STOP: ' + str(exc))


if __name__ == '__main__':
    main()
