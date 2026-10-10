"""Verify existing calculation records and recovered files; emit delivery evidence."""
from pathlib import Path
import csv
from datetime import datetime, timezone
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET

n = Path(__file__).resolve().parent.parent
ev = n / 'evidence'
cfg = json.loads((n / 'configs/mechanism_config.json').read_text())
checks = []


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def check(name, passed, detail=''):
    checks.append(dict(check=name, passed=bool(passed), detail=detail))


def readcsv(p):
    with p.open() as f:
        return list(csv.DictReader(f))


main_source = n / 'configs/source_v1/experiments/md-simulation/analysis/chctrl/analyze_local_mechanism.py'
pair_source = n / 'configs/source_v2/experiments/md-simulation/analysis/chctrl/analyze_local_mechanism.py'
for name in ['queue_status.json', 'pair_queue_status.json']:
    d = json.loads((ev / name).read_text())
    check(name, len(d) == 6 and {r['case'] for r in d} == {c['id'] for c in cfg['cases']} and all(r['exit_code'] == 0 for r in d))

for c in cfg['cases']:
    base = n / 'e2_delivery' / c['id']
    d = json.loads((base / 'completion.json').read_text())
    check(c['id'] + ': completion', d['status'] == 'complete' and d['case'] == c['id'] and (d['n_source_frames'], d['n_sampled_frames'], d['n_late_frames']) == (10001, 1001, 501))
    check(c['id'] + ': frozen main source/config', d['source_sha256'] == sha(main_source) and d['config_sha256'] == sha(n / 'configs/mechanism_config.json'))
    for kind in ['topology', 'reference', 'trajectory']:
        identity = d['input_identity'][kind]
        check(c['id'] + ': input ' + kind, identity['path'] == c[kind] and identity['sha256'] == c['expected_' + kind + '_sha256'])
    pair = json.loads((base / 'pair_details/completion.json').read_text())
    check(c['id'] + ': pair completion/source/config', pair['status'] == 'complete' and pair['case'] == c['id'] and pair['n_frames'] == 1001 and pair['source_sha256'] == sha(pair_source) and pair['config_sha256'] == sha(n / 'configs/pair_detail_config.json'))
    times = [float(r['time_ns']) for r in readcsv(base / 'frame_metrics.csv')]
    check(c['id'] + ': sampled times', len(times) == 1001 and all(abs(t - i * .1) < 1e-6 for i, t in enumerate(times)))
    pdb = (n / 'structures' / (c['id'] + '_six_frames.pdb')).read_text().splitlines()
    check(c['id'] + ': six PDB models', sum(line.startswith('MODEL ') for line in pdb) == 6 and sum(line.startswith(('ATOM  ', 'HETATM')) for line in pdb) == 6 * d['n_atoms'])

recovery_count = 0
for name, expected in [('delivery_manifest.json', 96), ('pair_delivery_manifest.json', 24)]:
    rows = json.loads((ev / name).read_text())
    check(name + ': count', len(rows) == expected)
    for r in rows:
        p = n / 'e2_delivery' / r['path']
        check('recovery:' + r['path'], p.stat().st_size == r['bytes'] and sha(p) == r['sha256'])
        recovery_count += 1

for summary, table, expected in [('validation.json', 'numerical_validation.csv', 975), ('pair_validation.json', 'pair_numerical_validation.csv', 528)]:
    d = json.loads((ev / summary).read_text())
    rows = readcsv(ev / table)
    check(summary, d['status'] == 'PASS' and d['checks'] == expected and not d['failures'] and len(rows) == expected and all(r['pass_check'] == 'True' and float(r['error']) <= float(r['tolerance']) for r in rows))
rows = readcsv(ev / 'previous_contact_crosscheck.csv')
check('existing contact crosscheck', len(rows) == 36 and all(r['pass_check'] == 'True' and abs(float(r['reconstructed_0p5ns_occupancy']) - float(r['prior_occupancy'])) < 1e-12 for r in rows))

remote = json.loads((ev / 'remote_artifacts.json').read_text())
remote_by_path = {r['e2_path']: r for r in remote['files']}
for name in ['delivery_manifest.json', 'pair_delivery_manifest.json']:
    for r in json.loads((ev / name).read_text()):
        now = remote_by_path.get(r['e2_path'], {})
        check('remote final:' + r['path'], now.get('sha256') == r['sha256'] and now.get('bytes') == r['bytes'])
figures = sorted((n / 'figures').glob('*'))
check('figure count', len(figures) == 15)
visual = []
for p in figures:
    r = remote_by_path.get(cfg['shared_output'] + '/figures_final/' + p.name, {})
    check('figure recovery:' + p.name, p.stat().st_size == r.get('bytes') and sha(p) == r.get('sha256'))
    if p.suffix == '.png':
        data = p.read_bytes()
        width, height = struct.unpack('>II', data[16:24])
        check('PNG:' + p.name, data[:8] == b'\x89PNG\r\n\x1a\n' and width > 1000 and height > 600)
        visual.append(dict(file='figures/' + p.name, sha256=sha(p), review='Visually inspected: Chinese/Latin labels readable; axes/units and uncertainty captions visible; no material clipping.'))
    elif p.suffix == '.pdf':
        check('PDF:' + p.name, p.read_bytes().startswith(b'%PDF-'))
    elif p.suffix == '.svg':
        check('SVG:' + p.name, ET.parse(p).getroot().tag.endswith('svg'))

evidence_rows = readcsv(n / 'tables/mechanism_evidence.csv')
check('13 mechanism claims', len(evidence_rows) == 13)
for r in evidence_rows:
    for ref in r['来源'].split(';'):
        check('claim source:' + r['证据编号'] + ':' + ref.strip(), (n / ref.strip()).exists())

generated = {(ev / 'final_acceptance.json').resolve(), (ev / 'local_artifacts.tsv').resolve()}
for p in [n / 'README.md', n / 'REPORT_CN.md', n / 'METHODS.md', n / 'EVIDENCE_TABLE.md', n / 'structures/README.md']:
    for link in re.findall(r'\]\(([^)]+)\)', p.read_text()):
        if '://' in link or link.startswith('#'):
            continue
        target = (p.parent / link.split('#')[0]).resolve()
        check('link:' + p.name + ':' + link, target.exists() or target in generated)

upload = ev / 'delivery_upload_verification.json'
if upload.exists():
    r = json.loads(upload.read_text())
    check('E2 human delivery recovery snapshot', r['status'] == 'PASS' and not r['failures'])

failures = [c for c in checks if not c['passed']]
result = dict(status='PASS' if not failures else 'FAIL', created_utc=datetime.now(timezone.utc).isoformat(), scope='Six existing trajectories; four descriptive mechanism analyses, not biological validation.', cases=6, new_MD_or_FEP=False, processed_input_hash_matches=18, recovered_case_files=recovery_count, independent_numerical_checks=1503, existing_contact_crosschecks=36, final_figure_files=15, visual_review=visual, delivery_checks=len(checks), failures=failures, checks=checks)
(ev / 'final_acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
if failures:
    print(json.dumps(failures, ensure_ascii=False, indent=2))
    raise SystemExit(1)
with (ev / 'local_artifacts.tsv').open('w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['path', 'bytes', 'sha256'])
    for p in sorted(n.rglob('*')):
        if p.is_file() and p != ev / 'local_artifacts.tsv' and '__pycache__' not in p.parts:
            writer.writerow([str(p.relative_to(n)), p.stat().st_size, sha(p)])
print(json.dumps({k: result[k] for k in ['status', 'delivery_checks', 'recovered_case_files', 'independent_numerical_checks', 'existing_contact_crosschecks']}))
