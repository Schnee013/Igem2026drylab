#!/usr/bin/env python3
"""Add the archived WT-lid case at a normally validated V368R-lid boundary."""
import argparse, fcntl, os, shutil, signal, subprocess, sys, time
from pathlib import Path
import remaining_runtime_v1 as d


def command(pid):
    try:
        return [x for x in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0') if x]
    except FileNotFoundError:
        return []


def own_sources(b, require_archive=True):
    result = {}
    for slot, case in enumerate(d.BATCHES['lid']):
        cfg = d.CASES[case]; w = b / cfg['work']; qp = b / cfg['qualifier']
        q = d.read(qp / 'qualification.json'); s = d.read(w / 'source_preflight.json')
        d.need(q['case_id'] == case and q['slot'] == slot and q['status'] == 'PASS_OWN_SIX_THREAD_FORCE_START_RESTART', 'Own qualification absent')
        d.need(s['case_id'] == case and s['structure']['pass'] and s['preparation_evidence']['box_density_settled'], 'Own source not accepted')
        d.need(d.sha(w / 'production.tpr') == s['production_tpr_sha256'] == q['cases'][case]['production_tpr_sha256'], 'Own TPR differs')
        for name, digest in q['evidence_sha256'].items():
            d.need(d.sha(qp / name) == digest, 'Qualification evidence changed')
        for name, digest in s['source_sha256'].items():
            d.need(d.sha(b / name) == digest, 'Source evidence changed')
        receipt = b / 'operator_records/e2_archive_v1' / (qp.name + '_segment_001.transfer.json')
        if not receipt.exists() and not require_archive:
            result[case] = {'qualification_sha256': d.sha(qp / 'qualification.json'), 'production_tpr_sha256': d.sha(w / 'production.tpr'), 'archive_pending': True}
            continue
        rr = d.read(receipt)
        d.need(rr['rsync_receiver_checksum_comparison'] == 'PASS' and d.sha(b / rr['manifest']) == rr['manifest_sha256'], 'Own archive not complete')
        manifest = d.read(b / rr['manifest'])
        d.need(any(x['relative_path'] == str((qp / 'qualification.json').relative_to(b)) and x['sha256'] == d.sha(qp / 'qualification.json') for x in manifest['files']), 'Qualification not in archive')
        result[case] = {'qualification_sha256': d.sha(qp / 'qualification.json'), 'production_tpr_sha256': d.sha(w / 'production.tpr'), 'archive_receipt_sha256': d.sha(receipt)}
    return result


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--bundle', type=Path, required=True)
    ap.add_argument('--old-controller', type=int, required=True); ap.add_argument('--old-queue', type=int, required=True)
    ap.add_argument('--check-only', action='store_true'); a = ap.parse_args()
    b = a.bundle.resolve(); code = b / 'operator_records/codex_takeover_v1'
    batch = b / 'operator_records/remaining_dual_lid_v1'
    queue = b / 'operator_records/lid_recovery_successor_v1'
    out = b / 'operator_records/lid_pair_recovery_v1'
    d.need(str(code / 'remaining_dual_controller_v1.py').encode() in command(a.old_controller), 'Old controller identity differs')
    d.need(str(code / 'lid_recovery_successor_v1.py').encode() in command(a.old_queue), 'Old queue identity differs')
    before = d.read(batch / 'status.json'); vcase, wcase = d.BATCHES['lid']
    d.need(before['pid'] == a.old_controller and set(before['cases']) == {vcase} and before['state'] == 'PRODUCING', 'Unexpected active batch')
    d.need(d.read(queue / 'status.json')['child_pid'] == a.old_controller, 'Old parent chain differs')
    d.live(b, [a.old_controller])
    sources = own_sources(b, require_archive=False)
    d.need(not list((b / d.CASES[wcase]['work']).glob(wcase + '_rep1_production*.log')), 'WT formal work already exists')
    pinned = {p.name: d.sha(p) for p in code.glob('*.py')}
    if a.check_only:
        print(__import__('json').dumps({'own_source_and_qualification_pass': True, 'archive_ready': not any(x.get('archive_pending') for x in sources.values()), 'sources': sources, 'old_controller': a.old_controller, 'old_queue': a.old_queue})); return
    out.mkdir(exist_ok=True); lock = (out / 'handoff.lock').open('a'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    d.need(not (out / 'preflight.json').exists(), 'One-shot handoff already initialized')
    d.save(out / 'preflight.json', {'at': d.now(), 'sources': sources, 'pinned_code': pinned, 'old_controller': a.old_controller, 'old_queue': a.old_queue, 'initial_batch': before, 'scope': 'Wait for ordinary accepted boundary; never signal MD or change its finite segment'})
    frozen = False; child = None
    def state(label, **kw):
        d.save(out / 'status.json', {'pid': os.getpid(), 'at': d.now(), 'state': label, **kw})
    def interrupted(signum, frame):
        raise RuntimeError('Boundary handoff interrupted; preserve healthy MD')
    signal.signal(signal.SIGTERM, interrupted); signal.signal(signal.SIGINT, interrupted)
    try:
        archive_deadline = time.monotonic() + 7200
        receipts = [b / 'operator_records/e2_archive_v1' / (Path(d.CASES[c]['qualifier']).name + '_segment_001.transfer.json') for c in d.BATCHES['lid']]
        while not all(p.exists() for p in receipts):
            ar = d.read(b / 'operator_records/e2_archive_v1/status.json')
            d.need(ar['state'] != 'ERROR' and b'archive_closed_v1_3.py' in b' '.join(command(ar['pid'])), 'Archive failed again; no further automatic recovery')
            d.need(time.monotonic() < archive_deadline, 'Qualification archive not ready within120min; no new submission')
            state('WAITING_OWN_QUALIFICATION_ARCHIVE', archive=ar, old_controller=a.old_controller)
            time.sleep(30)
        d.save(out / 'archived_sources.json', own_sources(b))
        state('WAITING_NORMAL_VALIDATED_BOUNDARY', old_controller=a.old_controller, old_queue=a.old_queue)
        deadline = time.monotonic() + 5400
        record = b / d.CASES[vcase]['records']; initial_end = before['cases'][vcase]['closed_ps']
        while True:
            d.need(time.monotonic() < deadline, 'No normal boundary within90min; leave healthy worker unchanged')
            d.need(str(code / 'remaining_dual_controller_v1.py').encode() in command(a.old_controller), 'Old controller exited unexpectedly')
            ar = d.read(b / 'operator_records/e2_archive_v1/status.json')
            d.need(ar['state'] != 'ERROR' and b'archive_closed_v1_3.py' in b' '.join(command(ar['pid'])), 'Archive failed again; no additional automatic recovery')
            current = d.read(record / 'controller_status.json')
            if current['state'] == 'DUAL_VALIDATED_BOUNDARY' and current['production_ps'] > initial_end:
                os.kill(a.old_controller, signal.SIGSTOP); frozen = True
                # A next worker may have started between observing the boundary and STOP.
                # If so, resume only the controller and wait for the next natural boundary.
                descendants = d.children(a.old_controller)
                busy = any(command(p) and any(x in b' '.join(command(p)) for x in (b'mdrun', b'run_stage_remaining_dual_v1.py')) for p in descendants)
                pending = [p for p in record.glob('segment_*') if p.is_dir() and not (p / 'closed_segment.json').exists()]
                if busy or pending:
                    os.kill(a.old_controller, signal.SIGCONT); frozen = False; time.sleep(.2); continue
                history = sorted(record.glob('segment_*/closed_segment.json')); previous = 0.
                for p in history:
                    item = d.read(p)
                    d.need(item['pass'] and item['case_id'] == vcase and item['start_ps'] == previous, 'History continuity failed')
                    previous = item['end_ps']
                last = d.read(history[-1]); cp = b / d.CASES[vcase]['work'] / (vcase + '_rep1_production.cpt')
                d.need(previous == current['production_ps'] and d.sha(cp) == last['checkpoint']['sha256'], 'Actual accepted boundary CPT differs')
                d.need(not d.live(b, [a.old_controller])['owned_mdruns'], 'A healthy MD is still active; leave it unchanged')
                saved = out / 'old_dispatch'; saved.mkdir()
                for label, directory in [('batch', batch), ('queue', queue)]:
                    for p in directory.glob('*.json'):
                        shutil.copy2(p, saved / (label + '_' + p.name))
                state('RETIRING_IDLE_DISPATCHER', boundary_ps=previous, boundary_sha256=d.sha(history[-1]))
                os.kill(a.old_controller, signal.SIGTERM); os.kill(a.old_controller, signal.SIGCONT); frozen = False
                stop_deadline = time.monotonic() + 30
                while command(a.old_controller) or command(a.old_queue):
                    d.need(time.monotonic() < stop_deadline, 'Old dispatch did not exit; no new submission')
                    time.sleep(.2)
                break
            time.sleep(.2)
        # The unchanged controller revalidates all closed files and all own gates itself.
        own_sources(b); d.live(b)
        for name, digest in pinned.items():
            d.need(d.sha(code / name) == digest, 'Pinned code changed during wait')
        for label, directory in [('batch', batch), ('queue', queue)]:
            shutil.copy2(directory / 'status.json', saved / (label + '_retired_status.json'))
        with (out / 'pair.console.txt').open('x') as f:
            child = subprocess.Popen([sys.executable, '-E', str(code / 'remaining_dual_controller_v1.py'), '--bundle', str(b), '--batch', 'lid', '--cases', *d.BATCHES['lid']], stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT, start_new_session=True, env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'))
            state('RUNNING_RECOVERED_PAIR', child_pid=child.pid, continued_from_ps=previous, new_case_start_ps=0)
            rc = child.wait()
        final = d.read(batch / 'status.json')
        d.need(rc == 0 and final['state'] == 'BATCH_CLOSED', 'Recovered pair stopped abnormally; inspect without retry')
        state('PAIR_CLOSED_AGENT_RECOVERY_REQUIRED', cases=final['cases'], six_case_completion=False)
    except Exception as exc:
        if frozen and command(a.old_controller):
            os.kill(a.old_controller, signal.SIGCONT)
        state('HANDOFF_HOLD', error=str(exc), new_controller_pid=child.pid if child else None)
        raise


if __name__ == '__main__':
    main()
