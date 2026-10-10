#!/usr/bin/env python3
"""Validate real predecessor/backup evidence; --refresh adds read-only live probes.

Default plan-only: no writes or external commands. Never starts MD or grompp.
The reviewed v2.3 driver and all scientific files remain unchanged.
"""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
CASE = 'native_wt_ascr18'
WORK_REL = 'runs/native_wt_ascr18/rep1_npt01_attempt02'
TARGETS = ('npt03', 'npt04', 'npt05')
MANIFEST_MEMBER = 'RECOVERY_SHA256.json'
QUALIFICATION_SHA = 'a7d02375652f594ad3d1649ebc11661fdabb5ece052df83578fbd27b26334d02'
GPU_UUID = 'GPU-0d5d6691-0983-c849-a06a-f7e2dd9b526f'
FROZEN_SHA = {
    'prepare_equilibration.py': 'a765ed0af887479b92dbae8215f7416c70941c0e30289c46bb8dc8354b7b4cb1',
    'run_stage_v3_locked.py': 'c38ccbd32a6a38f62185935a0da774d7fe9eb4749ee3ca5191c20b880b1c0aae',
    'import_verified_npt01.py': 'b3d5afe6e5ed07b7bb09805c4ff6ab0724a4383cd0024e57ac70567a9212816d',
    'refresh_native_wt_npt02_gate.py': '96d593a40aed73303f48c2ecbce6f2002994673ed29bdef0d72b07df00113fe1',
}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(stream):
    value = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        value.update(block)
    return value.hexdigest()


def sha(path):
    with Path(path).open('rb') as stream:
        return digest(stream)


def hash_value(value):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value), 'Explicit lowercase SHA256 required')
    return value


def safe_path(path, directory=False):
    path = Path(path).absolute()
    require('..' not in path.parts, 'Parent path traversal is forbidden')
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'Symlink evidence/path forbidden')
    require(path.is_dir() if directory else path.is_file(), 'Missing regular evidence: ' + str(path))
    if not directory:
        require(stat.S_ISREG(path.stat().st_mode), 'Nonregular evidence forbidden')
    return path.resolve(strict=True)


def read_json(path):
    return json.loads(safe_path(path).read_text())


def reference(base, row):
    require(isinstance(row, dict), 'Evidence reference must be an object')
    path = Path(row['path'])
    path = safe_path(path if path.is_absolute() else base / path)
    require(sha(path) == hash_value(row['sha256']), 'Pinned evidence changed: ' + str(path))
    return path


def load_core(bundle):
    code = bundle / 'operator_records/equilibration_prep_v2_3'
    for name, value in FROZEN_SHA.items():
        require(sha(safe_path(code / name)) == value, 'Frozen v2.3 source changed: ' + name)
    spec = importlib.util.spec_from_file_location('_nativewt_frozen_v23', code / 'prepare_equilibration.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, code


def check_acceptances(core, bundle, work, stage, binding):
    plan = core.verify_sources(bundle, CASE)
    inputs = read_json(work / 'preparation_inputs.json')
    expected = core.fixed_expected_hashes(bundle, plan)
    require(inputs.get('case_id') == CASE and inputs.get('source_sha256') == plan['source_sha256'] and inputs.get('fixed_files_sha256') == expected, 'Original source/input identity differs')
    core.validate_manifest(work, expected, set(expected))
    initial = read_json(work / 'initial_complete.json')
    require(initial.get('case_id') == CASE and type(initial.get('replicate')) is int and initial['replicate'] == 1, 'Initial identity differs')
    core.validate_manifest(work, initial.get('evidence_sha256'), core.INITIAL_EVIDENCE)
    prior = core.previous_stage(stage)
    require(sha(work / f'{prior}.validated.json') == hash_value(binding['predecessor_validation_sha256']), 'Predecessor acceptance pin differs')
    require(sha(work / f'controlled_stop_after_{prior}.json') == hash_value(binding['predecessor_controlled_stop_sha256']), 'Predecessor controlled-stop pin differs')
    evidence = [work / 'preparation_inputs.json', work / 'initial_complete.json']
    for name, start, end in core.STAGES:
        if name == stage:
            break
        path = work / f'{name}.validated.json'
        accepted = read_json(path)
        require(accepted.get('case_id') == CASE and type(accepted.get('replicate')) is int and accepted['replicate'] == 1 and accepted.get('stage') == name and accepted.get('start_ps') == start and accepted.get('end_ps') == end and accepted.get('pass_stage') is True and accepted.get('production_ready') is False and accepted.get('version') == core.VERSION, 'Saved stage identity/acceptance differs: ' + name)
        core.validate_manifest(work, accepted.get('output_sha256'), core.stage_output_names(name))
        if name == 'npt01':
            core.validate_npt01_import(work, accepted)
        tpr = (work / f'{name}.tpr.dump.txt').read_text()
        runtime = core.runtime_parameters_check(tpr, (work / f'{name}.log').read_text())
        require(read_json(work / f'{name}.runtime.json') == runtime, 'Saved runtime differs: ' + name)
        thermo = core.thermo_report((work / f'{name}.thermo.xvg').read_text(), start, end)
        require(all(accepted.get(k) == v for k, v in thermo.items()), 'Saved thermo differs: ' + name)
        trajectory = core.trajectory_check((work / f'{name}.xtc.check.txt').read_text(), start, end, plan['atom_count'], tpr)
        require(accepted.get('trajectory') == trajectory, 'Saved trajectory differs: ' + name)
        evidence.append(path)
        if name != 'npt01':
            stop_path = work / f'controlled_stop_after_{name}.json'
            stop = read_json(stop_path)
            wanted = dict(case_id=CASE, replicate=1, version=core.VERSION, stage=name, end_ps=end, stage_validated=True, preparation_complete=False, production_ready=False, stage_validation_sha256=sha(path))
            require(stop == wanted and type(stop.get('replicate')) is int and stop.get('stage_validated') is True and stop.get('preparation_complete') is False and stop.get('production_ready') is False, 'Controlled-stop proof differs: ' + name)
            evidence.append(stop_path)
    return plan, evidence


def member_name(name):
    require(isinstance(name, str) and name and '\\' not in name and ':' not in name and '\x00' not in name, 'Unsafe archive member')
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts and path.as_posix() == name, 'Unsafe archive member')
    return path


def check_library_receipt(raw, row, receipt_sha, association=None):
    """Validate unchanged direct or prepared-helper output; never invent a receipt."""
    prepared = 'results' in raw
    if prepared:
        require('structuredContent' not in raw and raw.get('isError', False) is False and isinstance(raw['results'], list) and len(raw['results']) == 1, 'Exactly one unambiguous prepared-upload result required')
        result = raw['results'][0]
        require(isinstance(result, dict) and result.get('purpose') == 'create_library_file' and result.get('status') == 'succeeded' and result.get('local_metadata_applied') is True, 'Prepared Library finalization did not succeed')
        require(isinstance(result.get('file_id'), str) and re.fullmatch('file_[A-Za-z0-9]+', result['file_id']), 'Prepared upload file identity missing')
        local = result.get('local_path')
        require(isinstance(local, str) and Path(local).is_absolute() and '..' not in Path(local).parts and Path(local).name == row['file_name'], 'Prepared upload local source identity differs')
        require(isinstance(association, dict) and association.get('purpose') == 'actual_prepared_upload_local_identity_verification', 'Pinned actual upload association required')
        require(association.get('upload_result_sha256') == receipt_sha and association.get('raw_upload_output_sha256') == receipt_sha and association.get('local_path') == local, 'Upload association receipt/path differs')
        require(association.get('sha256') == row['sha256'] and type(association.get('bytes')) is int and association['bytes'] == row['file_size_bytes'], 'Upload association archive hash/bytes differ')
        require(association.get('library_file_id') == row['library_file_id'] and type(association.get('current_version_number')) is int and association['current_version_number'] == row['current_version_number'], 'Upload association Library identity differs')
        require(association.get('xattrs') == {'user.library-file-version': str(row['current_version_number']), 'user.library-file-id': row['library_file_id']} and association.get('xattrs_verified') is True and association.get('file_unchanged_after_upload') is True and association.get('library_download_roundtrip_performed') is False, 'Actual unchanged-file/xattr upload verification required; no roundtrip claim')
        fields = ('file_name', 'library_file_id', 'current_version_number')
    else:
        result = raw.get('structuredContent', {})
        require(raw.get('isError') is False and result.get('operation') == 'create_library_file' and result.get('status') == 'succeeded', 'Library finalization did not succeed')
        fields = ('file_name', 'file_size_bytes', 'library_file_id', 'current_version_number')
    for field in fields:
        require(result.get(field) == row[field], 'Library finalization identity differs: ' + field)
    if prepared:
        require(type(result.get('current_version_number')) is int, 'Prepared upload version must be an integer')


def check_backup(core, work, base, binding):
    archive = reference(base, binding['backup_archive'])
    manifest = reference(base, binding['member_manifest'])
    recovery = reference(base, binding['recovery_record'])
    require(all(not p.is_relative_to(work) for p in (archive, manifest, recovery)), 'Backup/proof must stay outside the run workdir')
    size = binding['backup_archive']['bytes']
    require(type(size) is int and size > 0 and archive.stat().st_size == size, 'Full backup byte count differs')
    members = read_json(manifest)
    require(isinstance(members, dict) and members and MANIFEST_MEMBER not in members, 'Full-workdir member map required')
    actual = set()
    for p in work.rglob('*'):
        require(not p.is_symlink(), 'Workdir contains a symlink')
        if p.is_file():
            safe_path(p)
            actual.add(p.relative_to(work).as_posix())
        else:
            require(p.is_dir(), 'Workdir contains a nonregular entry')
    require(set(members) == actual, 'Backup manifest is not the complete current workdir')
    core.validate_manifest(work, members, actual)
    with zipfile.ZipFile(archive) as zipped:
        infos = zipped.infolist()
        names = [i.filename for i in infos]
        require(len(names) == len(set(names)) == len({n.casefold() for n in names}), 'Duplicate/case-colliding archive members')
        require(set(names) == set(members) | {MANIFEST_MEMBER}, 'Full archive membership differs')
        for info in infos:
            rel = member_name(info.filename)
            require(info.orig_filename == info.filename and not info.is_dir() and not info.flag_bits & 1 and stat.S_IFMT(info.external_attr >> 16) in (0, stat.S_IFREG), 'Nonregular/encrypted archive member')
            expected_path = manifest if info.filename == MANIFEST_MEMBER else work / rel
            require(info.file_size == expected_path.stat().st_size, 'Archive member byte count differs')
            expected_hash = sha(manifest) if info.filename == MANIFEST_MEMBER else members[info.filename]
            with zipped.open(info) as stream:
                require(digest(stream) == expected_hash, 'Archive member hash differs: ' + info.filename)
    saved = binding['library_files']
    require(isinstance(saved, list) and len(saved) == 1, 'Exactly one actual full-ZIP Library receipt required; multipart is unsupported')
    artifacts = []
    receipts = []
    ids = set()
    for row in saved:
        receipt = reference(base, row['receipt'])
        raw = read_json(receipt)
        require(isinstance(row['library_file_id'], str) and re.fullmatch('libfile_[A-Za-z0-9]+', row['library_file_id']) and row['library_file_id'] not in ids, 'Missing/duplicate Library identity')
        ids.add(row['library_file_id'])
        require(type(row['file_size_bytes']) is int and row['file_size_bytes'] > 0 and type(row['current_version_number']) is int and row['current_version_number'] >= 0, 'Invalid Library size/version')
        require(Path(row['file_name']).name == row['file_name'] and row['file_name'], 'Invalid Library filename')
        association = None
        if 'results' in raw:
            association_path = reference(base, row['upload_association'])
            association = read_json(association_path)
            receipts.append(association_path)
        check_library_receipt(raw, row, sha(receipt), association)
        artifacts.append({'file_name': row['file_name'], 'bytes': row['file_size_bytes'], 'sha256': hash_value(row['sha256'])})
        receipts.append(receipt)
    require(len({x['file_name'] for x in artifacts}) == len(artifacts), 'Duplicate Library artifact filename')
    proof = read_json(recovery)
    require(proof.get('status') == 'verified' and proof.get('case_id') == CASE and type(proof.get('replicate')) is int and proof['replicate'] == 1 and proof.get('stage') == core.previous_stage(binding['target_stage']), 'Wrong predecessor recovery proof')
    require(proof.get('archive_sha256') == sha(archive) and proof.get('archive_bytes') == size and proof.get('member_manifest_sha256') == sha(manifest), 'Recovery proof names another archive/member map')
    require(proof.get('original_archive_byte_for_byte_equal') is True and type(proof.get('original_evidence_files_byte_for_byte_equal')) is int and proof['original_evidence_files_byte_for_byte_equal'] == len(members) and proof.get('path_safety_verified') is True and proof.get('existing_files_overwritten') is False, 'Actual full recovery/byte-comparison proof required')
    require(proof.get('library_artifacts') == artifacts, 'Recovery proof does not bind these persisted Library artifacts')
    require(type(proof.get('library_download_roundtrip_performed')) is bool, 'Explicit truthful Library roundtrip boolean required')
    require(isinstance(proof.get('verification_scope'), str) and proof['verification_scope'].strip(), 'Recovery verification scope required')
    require(artifacts[0] == {'file_name': archive.name, 'bytes': size, 'sha256': sha(archive)}, 'Single Library artifact must be the exact full archive')
    return [archive, manifest, recovery, *receipts]


def validate_plan(bundle, work, stage, binding_path, binding_sha):
    require(stage in TARGETS, 'Only original NPT03, NPT04, NPT05 are supported')
    bundle = safe_path(bundle, directory=True)
    work = safe_path(work, directory=True)
    require(work == bundle / WORK_REL, 'Only the existing original nativeWT rep1 workdir is supported')
    binding_path = safe_path(binding_path)
    require(not binding_path.is_relative_to(work), 'Binding must be outside workdir')
    require(sha(binding_path) == hash_value(binding_sha), 'Explicit reviewed binding SHA differs')
    binding = read_json(binding_path)
    require(binding.get('version') == 'nativewt_next_gate_v1' and binding.get('case_id') == CASE and type(binding.get('replicate')) is int and binding['replicate'] == 1 and binding.get('target_stage') == stage and binding.get('workdir_relative') == WORK_REL, 'Wrong stage-specific binding identity')
    core, code = load_core(bundle)
    core.preflight_new_outputs(work, (stage + '*', 'audit.' + stage + '.*'), (stage + '.mdp',))
    require(not (work / f'controlled_stop_after_{stage}.json').exists(), 'Target already has a controlled stop; inspect')
    plan, prior = check_acceptances(core, bundle, work, stage, binding)
    backup = check_backup(core, work, binding_path.parent, binding)
    return core, code, plan, binding, [binding_path, *prior], backup


def read_command(args, out, name):
    result = subprocess.run(args, text=True, capture_output=True, check=True, timeout=30)
    for suffix, data in (('stdout', result.stdout), ('stderr', result.stderr)):
        with (out / f'{name}.{suffix}.txt').open('x') as stream:
            stream.write(data)
    return result.stdout


def fresh_resources(core, code, bundle, out):
    qualification = safe_path(code / 'numerical_preparation_qualification_v3.json')
    require(sha(qualification) == QUALIFICATION_SHA, 'Numerical qualification changed')
    q = read_json(qualification)
    require(q['status'] == 'qualified_prep_only' and q['scope']['first_allowed_case'] == CASE and q['scope']['first_allowed_stage'] == 'npt01', 'No matching bounded preparation qualification')
    numeric = [qualification]
    for name, entry in q['evidence'].items():
        source = bundle / entry['relative_remote_path'] if 'relative_remote_path' in entry else code / 'multiframe_v3_independent_raw_audit.json'
        require(sha(safe_path(source)) == entry['sha256'], 'Numerical evidence absent/changed: ' + name)
        numeric.append(source)
    binary = safe_path(core.VERIFIED_GMX)
    require(str(binary) == core.VERIFIED_GMX and sha(binary) == core.VERIFIED_GMX_SHA256, 'Actual executable differs from A90a2 baseline')
    version = read_command([str(binary), '--version'], out, 'gromacs_version')
    parsed = {k.strip(): v.strip() for k, v in (line.split(':', 1) for line in version.splitlines() if ':' in line)}
    for key, value in q['environment']['same_build_verified_fields'].items():
        require(parsed.get(key) == value, 'Build identity changed: ' + key)
    gpu = read_command(['nvidia-smi', '--query-gpu=index,name,uuid,driver_version,memory.total,memory.used', '--format=csv,noheader,nounits'], out, 'gpu_identity')
    rows = [r.strip().split(',') for r in gpu.strip().splitlines()]
    require(len(rows) == 1 and rows[0][2].strip() == GPU_UUID and 'RTX 5090' in rows[0][1], 'Different GPU; qualification review required')
    require(float(rows[0][5].strip()) < 1024, 'GPU memory not idle enough')
    processes = read_command(['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory', '--format=csv,noheader,nounits'], out, 'gpu_processes')
    require(not processes.strip(), 'Another GPU compute process is present')
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            require(b'mdrun' not in proc.read_bytes().split(b'\0'), 'Another mdrun is present')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    cpu = Path('/sys/fs/cgroup/cpu.max').read_text().strip()
    memory = Path('/sys/fs/cgroup/memory.max').read_text().strip()
    cpuset = Path('/sys/fs/cgroup/cpuset.cpus.effective').read_text().strip()
    cpu_ids = set()
    for part in cpuset.split(','):
        ends = part.split('-')
        cpu_ids.update(range(int(ends[0]), int(ends[-1]) + 1))
    require(len(cpu_ids) >= 8, 'Effective CPU set below eight threads')
    quota, period = cpu.split()
    require(quota == 'max' or float(quota) / float(period) >= 8, 'CPU quota below eight threads')
    require(memory == 'max' or int(memory) >= 16 * 1024**3, 'Memory quota below reserve')
    free = shutil.disk_usage(bundle).free
    require(free >= 5_000_000_000, 'Insufficient preparation disk reserve')
    df = read_command(['df', '-P', str(bundle)], out, 'disk_mount')
    mount = df.strip().splitlines()[-1].split()[-1]
    require(mount != '/' and bundle.is_relative_to(Path(mount).resolve()), 'Data-disk mount not confirmed')
    live = dict(utc=datetime.now(timezone.utc).isoformat(), hostname=socket.gethostname(), binary_realpath=str(binary), binary_sha256=sha(binary), gpu_uuid=GPU_UUID, gpu_processes=[], other_mdruns=[], free_bytes=free, data_mountpoint=mount, case_id=CASE, checks_pass=True)
    live.update({'cpu.max': cpu, 'memory.max': memory, 'cpuset.cpus.effective': cpuset})
    return binary, numeric, live


def refresh(bundle, work, stage, out, result):
    core, code, plan, binding, prior, backup = result
    out = Path(out).absolute()
    require('..' not in out.parts and not any(p.is_symlink() for p in (out, *out.parents)), 'Unsafe fresh output path')
    require(out.is_relative_to(bundle / 'operator_records') and not out.is_relative_to(code) and not out.is_relative_to(Path(__file__).resolve().parent), 'Fresh evidence requires a separate operator_records directory')
    require(not out.exists(), 'Refusing to overwrite live evidence')
    out.mkdir(parents=True, exist_ok=False)
    binary, numeric, live = fresh_resources(core, code, bundle, out)
    live['stage'] = stage
    core.write(out / 'case_source_plan.json', plan)
    core.write(out / 'live_preflight.json', live)
    start, end, _ = core.allowed_stage_clocks()[stage]
    storage = dict(bounded_stage_only=f'{CASE}/{stage}:{start:g}->{end:g}ps', free_bytes=live['free_bytes'], minimum_free_bytes=5_000_000_000, predecessor_stage=core.previous_stage(stage), predecessor_validation_sha256=binding['predecessor_validation_sha256'], predecessor_controlled_stop_sha256=binding['predecessor_controlled_stop_sha256'], backup_archive_sha256=binding['backup_archive']['sha256'], member_manifest_sha256=binding['member_manifest']['sha256'], recovery_record_sha256=binding['recovery_record']['sha256'], library_download_roundtrip_performed=read_json(backup[2])['library_download_roundtrip_performed'], this_stage_full_recovery='Pending actual stage completion and verified full backup before progression', delete_unique_outputs=False, production_release=False)
    core.write(out / 'storage_and_recovery.json', storage)
    evidence = lambda p: {'path': str(p), 'sha256': sha(p)}
    gate = dict(version=core.VERSION, case_id=CASE, replicate=1, allowed_stages=[stage], source_hold_cpt_sha256=plan['source_sha256'][f'compute/cases/{CASE}/prepared/hold.cpt'], checks={k: True for k in core.GATES}, evidence={'numerical_compatibility': [evidence(p) for p in numeric], 'source_identity': [evidence(out / 'case_source_plan.json'), *[evidence(p) for p in prior], *[evidence(code / name) for name in FROZEN_SHA], evidence(Path(__file__).resolve())], 'structure_purpose': [evidence(bundle / f'compute/cases/{CASE}/case.json'), evidence(bundle / f'compute/cases/{CASE}/evidence/preheat_audit.json'), evidence(numeric[0])], 'resources': [evidence(out / 'live_preflight.json'), *[evidence(out / f'{n}.stdout.txt') for n in ('gromacs_version', 'gpu_identity', 'gpu_processes', 'disk_mount')]], 'storage_and_recovery': [evidence(out / 'storage_and_recovery.json'), *[evidence(p) for p in backup]]}, live_verified_at=live['utc'], runtime=dict(gmx_realpath=str(binary), gmx_sha256=sha(binary), offload='gpu', threads=8, pme_tuning=False, pme_grid_policy='case_original_grompp_grid'), production_ready=False, note=f'Actual accepted predecessor and full original backup checked. Only original {stage}; no later stage or production.')
    candidate = out / '.candidate.gate.json'
    final = out / f'{CASE}.{stage}.gate.json'
    try:
        core.write(candidate, gate)
        core.gate_check(candidate, plan, binary)
        os.link(candidate, final)
    finally:
        candidate.unlink(missing_ok=True)
    return dict(mode='FRESH_SINGLE_STAGE_GATE', gate=str(final), stage=stage, live_verified_at=live['utc'], md_started=False, production_ready=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--workdir', type=Path, required=True)
    parser.add_argument('--stage', choices=TARGETS, required=True)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--binding-sha256', required=True)
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    require(not args.refresh or args.out is not None, '--refresh requires a new --out directory')
    bundle, work = safe_path(args.bundle, True), safe_path(args.workdir, True)
    require(work == bundle / WORK_REL, 'Only the existing original nativeWT rep1 workdir is supported')
    with ExitStack() as stack:
        if args.refresh:
            for lockpath in (bundle / 'operator_records/equilibration_prep_v2_2_2/serial.lock', work / 'equilibration.lock', work / 'stage.lock'):
                handle = stack.enter_context(safe_path(lockpath).open('r'))
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = validate_plan(bundle, work, args.stage, args.binding, args.binding_sha256)
        if args.refresh:
            report = refresh(bundle, work, args.stage, args.out, result)
        else:
            report = dict(mode='PLAN_ONLY', stage=args.stage, predecessor_stage=result[0].previous_stage(args.stage), evidence_verified=True, live_resources_verified=False, gate_created=False, md_started=False, production_ready=False)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        raise SystemExit('STOP: ' + str(exc))
