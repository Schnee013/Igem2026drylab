"""Recover this task's small delivery snapshot on E2 and check every packaged file."""
from pathlib import Path
import hashlib
import json
import tarfile
from datetime import datetime, timezone

root = Path('/ifs1/User/dengwei/igem/md/gpr2-autodl/analysis/_mechanism_20261010')
dest = root / 'delivery'
dest.mkdir(exist_ok=True)
with tarfile.open(root / 'human_delivery.tar.gz') as t:
    for member in t.getmembers():
        resolved = (dest / member.name).resolve()
        if not resolved.is_relative_to(dest.resolve()) or not member.isfile():
            raise ValueError('Unexpected archive member: ' + member.name)
    t.extractall(dest, filter='data')

cfg = json.loads((dest / 'configs/mechanism_config.json').read_text())
(dest / 'e2_delivery').mkdir(exist_ok=True)
for c in cfg['cases']:
    p = dest / 'e2_delivery' / c['id']
    if p.is_symlink():
        assert p.resolve() == Path(c['output']).resolve()
    elif p.exists():
        raise ValueError('Existing non-link case delivery path: ' + str(p))
    else:
        p.symlink_to(c['output'], target_is_directory=True)

expected = json.loads((dest / 'evidence/human_delivery_manifest.json').read_text())
failures = []
for r in expected['files']:
    p = dest / r['path']
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != r['sha256'] or p.stat().st_size != r['bytes']:
        failures.append(r['path'])
result = dict(status='PASS' if not failures else 'FAIL', created_utc=datetime.now(timezone.utc).isoformat(), files=len(expected['files']), failures=failures, destination=str(dest), snapshot_manifest_sha256=hashlib.sha256((dest / 'evidence/human_delivery_manifest.json').read_bytes()).hexdigest(), note='Final acceptance and local_artifacts.tsv are synchronization metadata, sent after this receipt and excluded from the snapshot manifest.')
(root / 'delivery_upload_verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
if failures:
    raise SystemExit(1)
