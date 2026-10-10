"""Hash finalized derived outputs; never access raw runs/operator_records."""
import csv
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
target = root / '_shared/evidence/e2_artifacts.tsv'
target.parent.mkdir(parents=True, exist_ok=True)
rows = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or path == target:
        continue
    relative = path.relative_to(root).as_posix()
    if relative in {'_shared/evidence/artifact_hash.log',
                    '_shared/evidence/artifact_hash.exit'}:
        continue  # This process writes these after the immutable snapshot.
    if any(part in {'__pycache__', '.pytest_cache'} for part in path.parts):
        continue
    if 'offsets' in path.name or path.suffix in {'.lock', '.pyc'}:
        continue
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    rows.append({'absolute_path': str(path), 'relative_path': relative,
                 'bytes': path.stat().st_size, 'sha256': digest.hexdigest(),
                 'retained_on_e2': 'true' if path.suffix == '.xtc' else 'false'})
with target.open('w') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)
print('hashed_files', len(rows), 'bytes', sum(row['bytes'] for row in rows),
      'retained_trajectories', sum(row['retained_on_e2'] == 'true' for row in rows))
