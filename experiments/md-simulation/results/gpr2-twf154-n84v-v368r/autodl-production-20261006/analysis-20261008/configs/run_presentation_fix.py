"""Rerun the shared comparison after a figure-label fix; require identical tables."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path('/ifs1/User/dengwei/igem/md/gpr2-autodl/analysis')
spec = json.loads((root / '_shared/comparison_commands.json').read_text())
folder = root / '_comparison/ligand_paths'
def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.glob('*.csv'))}
before = hashes()
command = spec['commands'][2]['argv']
with (root / '_shared/evidence/presentation_fix_driver.log').open('w') as log:
    result = subprocess.run(command, cwd=spec['cwd'], stdout=log,
                            stderr=subprocess.STDOUT, check=False)
after = hashes()
record = {'status': 'PASS' if result.returncode == 0 and before == after else 'FAIL',
          'driver_returncode': result.returncode, 'command': command,
          'reason': 'Generic ligand title and configured six-arm figure order',
          'before_csv_sha256': before, 'after_csv_sha256': after,
          'driver_sha256': hashlib.sha256(Path(command[1]).read_bytes()).hexdigest()}
(root / '_shared/evidence/presentation_fix.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
if record['status'] != 'PASS':
    raise SystemExit(1)
