"""Restore and verify the selected Docking release using only the Python standard library."""
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from urllib.parse import unquote
import zipfile


def sha256(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def safe_path(root, relative):
    rel = PurePosixPath(relative)
    if not relative or rel.is_absolute() or '..' in rel.parts or '\\' in relative:
        raise ValueError('Unsafe release path: ' + relative)
    path = root.joinpath(*rel.parts)
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('Symlink in release path: ' + relative)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Release path escapes root: ' + relative)
    return path


def load(root):
    release = json.loads((root / 'provenance/lfs-release.json').read_text())
    if release['schema_version'] != 1:
        raise ValueError('Unsupported release schema')
    with safe_path(root, release['restore_manifest']).open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    names = set()
    repo = root.parents[1]
    archive_names = {a['path'] for a in release['archives']}
    for row in rows:
        safe_path(root, row['path'])
        safe_path(repo, row['container'])
        if row['path'] in names:
            raise ValueError('Duplicate restore destination: ' + row['path'])
        names.add(row['path'])
        if row['storage'] not in {'zip', 'repo'}:
            raise ValueError('Unknown storage type: ' + row['storage'])
        if row['storage'] == 'zip':
            safe_path(root, row['member'])
            if row['container'] not in archive_names:
                raise ValueError('Unregistered archive: ' + row['container'])
        if int(row['bytes']) < 0 or not re.fullmatch(r'[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid size or hash: ' + row['path'])
    return release, rows


def check_archives(repo, release):
    for arc in release['archives']:
        path = safe_path(repo, arc['path'])
        if not path.is_file() or path.stat().st_size != arc['bytes'] or sha256(path) != arc['sha256']:
            raise ValueError('Missing or changed LFS archive; run git lfs pull: ' + arc['path'])


def check_git(root, release):
    checked = 0
    for line in safe_path(root, release['git_checksums']).read_text().splitlines():
        digest, relative = line.split('  ', 1)
        path = safe_path(root, relative)
        if not path.is_file() or sha256(path) != digest:
            raise ValueError('Missing or changed Git file: ' + relative)
        checked += 1
    return checked


def restore(root):
    root = root.resolve()
    repo = root.parents[1]
    release, rows = load(root)
    check_git(root, release)
    check_archives(repo, release)
    # Check every destination and source before creating any restored file.
    for row in rows:
        target = safe_path(root, row['path'])
        if target.exists() and (not target.is_file() or sha256(target) != row['sha256']):
            raise ValueError('Existing file differs; preserved without overwrite: ' + row['path'])
        source = safe_path(repo, row['container'])
        if row['storage'] == 'repo':
            if not source.is_file() or source.stat().st_size != int(row['bytes']) or sha256(source) != row['sha256']:
                raise ValueError('Missing or changed canonical source: ' + row['container'])
    by_archive = {}
    for row in rows:
        if row['storage'] == 'zip':
            by_archive.setdefault(row['container'], []).append(row)
    for container, members in by_archive.items():
        with zipfile.ZipFile(safe_path(repo, container)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate ZIP members: ' + container)
            for row in members:
                if archive.getinfo(row['member']).file_size != int(row['bytes']):
                    raise ValueError('ZIP member size differs: ' + row['member'])
    restored = skipped = 0
    opened = {}
    try:
        for row in rows:
            target = safe_path(root, row['path'])
            if target.exists():
                skipped += 1
                continue
            source = safe_path(repo, row['container'])
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.restore-', delete=False) as out:
                    temporary = Path(out.name)
                    if row['storage'] == 'zip':
                        if row['container'] not in opened:
                            opened[row['container']] = zipfile.ZipFile(source)
                        handle = opened[row['container']].open(row['member'])
                    else:
                        handle = source.open('rb')
                    with handle:
                        shutil.copyfileobj(handle, out)
                if temporary.stat().st_size != int(row['bytes']) or sha256(temporary) != row['sha256']:
                    raise ValueError('Restored content differs: ' + row['path'])
                # Atomic exclusive installation; never replace a concurrent write.
                os.link(temporary, target)
                restored += 1
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
    finally:
        for archive in opened.values():
            archive.close()
    return {'status': 'PASS', 'restored': restored, 'already_present_and_identical': skipped}


def check_links(root, release, rows):
    published = {row['path'] for row in rows}
    tracked = set()
    for line in (root / release['git_checksums']).read_text().splitlines():
        tracked.add(line.split('  ', 1)[1])
    with (root / 'provenance/payload_manifest.tsv').open(newline='') as handle:
        historical = {r['path'] for r in csv.DictReader(handle, delimiter='\t')
                      if r['tracked_policy'] == 'historical_local_only'}
    generated = json.loads((root / 'provenance/generated-files.json').read_text())
    changed = json.loads((root / 'provenance/documentation-changes.json').read_text())
    docs = {p for p in generated if p.endswith('.md')} | {r['destination'] for r in changed}
    docs.update({'README.md', 'DATA_DELIVERY.md', 'provenance/README.md',
                 'provenance/PUBLICATION_SCOPE.md', 'provenance/RELEASE_READINESS.md',
                 'provenance/COMMIT_PLAN.md', 'shared/environment/README.md'})
    deferred = set()
    checked = 0
    errors = []
    for relative in sorted(docs):
        path = root / relative
        body = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for target in re.findall(r'\]\(([^)\n]+)\)', body):
            target = unquote(target.split('#', 1)[0]).strip('<>')
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            checked += 1
            resolved = (path.parent / target).resolve()
            if resolved.exists():
                continue
            if resolved.is_relative_to(root):
                rel = str(resolved.relative_to(root))
                historical_match = rel in historical or any(p.startswith(rel + '/') for p in historical)
                published_match = rel in published or rel in tracked or any(p.startswith(rel + '/') for p in published | tracked)
                if historical_match and not published_match:
                    deferred.add(rel)
                    continue
            errors.append('Broken published link: ' + relative + ' -> ' + target)
    return checked, sorted(deferred), errors


def verify(root, mode):
    root = root.resolve()
    release, rows = load(root)
    counts = {'git_files': check_git(root, release)}
    if mode == 'github':
        return {'status': 'PASS', 'mode': mode, 'checks': counts,
                'scope': 'Git content only; restore LFS data and run full for source verification'}
    check_archives(root.parents[1], release)
    for row in rows:
        path = safe_path(root, row['path'])
        if not path.is_file() or path.stat().st_size != int(row['bytes']) or sha256(path) != row['sha256']:
            raise ValueError('Missing or changed restored input: ' + row['path'])
    counts.update(lfs_archives=len(release['archives']), restored_paths=len(rows))
    spec = importlib.util.spec_from_file_location('research_sources', root / 'provenance/verify_research.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    science = module.check_sources(root)
    counts.update(science['checks'])
    links, deferred, errors = check_links(root, release, rows)
    counts['reading_links'] = links
    errors.extend(science['errors'])
    return {'status': 'PASS' if not errors else 'FAIL', 'mode': mode,
            'scope': release['scope'], 'checks': counts,
            'historical_links_outside_release': deferred,
            'scientific_calculations_rerun': False, 'errors': errors}
