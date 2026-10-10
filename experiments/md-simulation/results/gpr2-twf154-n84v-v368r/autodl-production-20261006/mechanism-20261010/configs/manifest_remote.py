"""Hash only this analysis's E2 outputs, configuration, source and final figures."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

root = Path('/ifs1/User/dengwei/igem/md/gpr2-autodl/analysis/_mechanism_20261010')
cfg = json.loads((root / 'mechanism_config.json').read_text())
paths = set()
for c in cfg['cases']:
    paths.update(p for p in Path(c['output']).rglob('*') if p.is_file())
for sub in ['source', 'source_v2', 'figures_final']:
    paths.update(p for p in (root / sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for p in root.iterdir():
    if p.is_file() and p.suffix in {'.json', '.py', '.log'} and p.name not in {'remote_artifacts.json', 'delivery_upload_verification.json'}:
        paths.add(p)
rows = []
for p in sorted(paths):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    rows.append(dict(e2_path=str(p), bytes=p.stat().st_size, sha256=h.hexdigest()))
result = dict(created_utc=datetime.now(timezone.utc).isoformat(), scope='This analysis only; original trajectories are identified by input_identity.json, not rehashed here.', files=rows)
(root / 'remote_artifacts.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(files=len(rows), bytes=sum(r['bytes'] for r in rows))))
