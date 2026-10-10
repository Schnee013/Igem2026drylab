#!/usr/bin/env python3
"""Restore the exact handoff ZIP from ordinary ZIP attachments; stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parts-dir', type=Path, default=Path('.'))
    ap.add_argument('--manifest', type=Path,
                    default=Path(__file__).resolve().with_name('SPLIT_MANIFEST.json'))
    ap.add_argument('--output-dir', type=Path, default=Path('.'))
    a = ap.parse_args()
    manifest = json.loads(a.manifest.read_text())
    target_info = manifest['original_archive']
    name = target_info['filename']
    if Path(name).name != name:
        raise SystemExit('Invalid archive filename in manifest')
    a.output_dir.mkdir(parents=True, exist_ok=True)
    target = a.output_dir / name
    if target.exists():
        if target.stat().st_size == target_info['bytes'] and digest(target) == target_info['sha256']:
            print(json.dumps({'restored_archive': str(target.resolve()), 'sha256_pass': True,
                              'already_present': True}))
            return
        raise SystemExit('Output already exists with another identity; choose a fresh output directory')

    archives = sorted(a.parts_dir.glob('*.zip'))
    sources = []
    for part in manifest['parts']:
        member = part['member']
        if Path(member).name != member:
            raise SystemExit('Invalid part filename in manifest')
        raw = a.parts_dir / member
        candidates = [('raw', raw)] if raw.is_file() else []
        for zpath in archives:
            try:
                with zipfile.ZipFile(zpath) as z:
                    if member in z.namelist():
                        candidates.append(('zip', zpath))
            except zipfile.BadZipFile:
                continue
        if not candidates:
            raise SystemExit('Missing attachment: ' + part['attachment'])
        # Prefer an extracted raw part; duplicates still have to match the expected hash.
        sources.append((part, candidates[0]))

    pending = None
    try:
        with tempfile.NamedTemporaryFile(dir=a.output_dir, prefix=name + '.', suffix='.assembling',
                                         delete=False) as out:
            pending = Path(out.name)
            combined = hashlib.sha256()
            for part, (kind, location) in sources:
                z = zipfile.ZipFile(location) if kind == 'zip' else None
                stream = z.open(part['member']) if z else location.open('rb')
                h = hashlib.sha256()
                count = 0
                try:
                    with stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            count += len(block)
                            h.update(block)
                            combined.update(block)
                            out.write(block)
                finally:
                    if z:
                        z.close()
                if count != part['bytes'] or h.hexdigest() != part['sha256']:
                    raise SystemExit('Damaged or mismatched part: ' + part['attachment'])
            if out.tell() != target_info['bytes'] or combined.hexdigest() != target_info['sha256']:
                raise SystemExit('Restored archive identity does not match the original')
        # The directory must be dedicated to this restore; never overwrite existing outputs.
        if target.exists():
            raise SystemExit('Output appeared during restoration; choose a fresh output directory')
        pending.rename(target)
        pending = None
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)
    print(json.dumps({'restored_archive': str(target.resolve()), 'bytes': target.stat().st_size,
                      'sha256': digest(target), 'sha256_pass': True}))


if __name__ == '__main__':
    main()
