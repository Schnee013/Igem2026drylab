#!/usr/bin/env python3
"""Read-only snapshot of the first production pair, including its 100 ns closure.

After both cases close, the successor's actual stage requires separate review.
This script never dispatches, stops, retries, or changes acceptance records.
"""
import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle', type=Path, required=True)
    b = ap.parse_args().bundle.resolve()
    code = b / 'operator_records/codex_takeover_v1'
    sys.path.insert(0, str(code))
    import dual_runtime as d

    status = d.read(b / 'operator_records/dual_dispatch_v1/status.json')
    queue = d.read(b / 'operator_records/six_case_successor_v1_1/status.json')
    queue_proc = Path('/proc') / str(queue['pid']) / 'cmdline'
    queue_alive = queue_proc.exists() and b'six_case_successor_v1_1.py' in queue_proc.read_bytes()
    d.need(queue_alive or queue['state'] == 'ALL_DISPATCH_FINISHED_AGENT_RECOVERY_REQUIRED',
           'Successor not active or normally finished; inspect its actual state')
    d.need(queue['state'] != 'QUEUE_HOLD', 'Successor held; preserve evidence and inspect')
    if queue['state'] == 'WAITING_CURRENT_PAIR_CLOSURE':
        d.need(not d.children(queue['pid']), 'Waiting successor unexpectedly has children')
    supervisors = [v['supervisor_pid'] for v in status.get('workers', {}).values()]
    if queue_alive:
        supervisors.append(queue['pid'])
    live = d.live(b, supervisors)
    _, (_, core, _) = d.load_core(b)
    cases = {}
    for case, cfg in d.CASES.items():
        work = b / cfg['work']
        cp = work / (case + '_rep1_production.cpt')
        dump = subprocess.check_output([d.GMX, 'dump', '-cp', str(cp)], text=True,
                                      stderr=subprocess.DEVNULL,
                                      env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'))
        checkpoint = {'time_ps': core.scalar(dump, 't'), 'step': core.scalar(dump, 'step'),
                      'atoms': core.scalar(dump, '#atoms'),
                      'age_seconds': time.time() - cp.stat().st_mtime}
        d.need(checkpoint['atoms'] == cfg['atoms'] and
               abs(checkpoint['time_ps'] - checkpoint['step'] * .002) < .001,
               'Checkpoint identity/clock differs: ' + case)
        state = status['cases'][case]
        if state['state'] == 'COMPLETE_PENDING_RECOVERY':
            tpr_sha = d.sha(work / 'production.tpr')
            paths = sorted((b / cfg['records']).glob('segment_*/closed_segment.json'))
            d.need(bool(paths), 'Complete case has no actual closed parts: ' + case)
            end = 0
            for path in paths:
                closed = d.read(path)
                d.need(closed['case_id'] == case and closed['pass'] is True and
                       closed['start_ps'] == end and closed['end_ps'] > end and
                       closed['production_tpr_sha256'] == tpr_sha,
                       'Completed case history is discontinuous or differs: ' + case)
                end = closed['end_ps']
            d.need(end == state['closed_ps'] == checkpoint['time_ps'] == 100000 and
                   checkpoint['step'] == 50000000 and
                   d.sha(cp) == closed['checkpoint']['sha256'] == d.sha(closed['checkpoint']['path']),
                   'Completed case lacks matching 100 ns final checkpoint: ' + case)
            d.need(case not in status.get('workers', {}), 'Completed case still registered as active')
            for pid in live['owned_mdruns']:
                cmd = (Path('/proc') / str(pid) / 'cmdline').read_bytes()
                d.need((case + '_rep1_production').encode() not in cmd,
                       'Completed case still has an MD process: ' + case)
            cases[case] = {'phase': 'COMPLETE_100NS_PENDING_RECOVERY_REVIEW',
                           'checkpoint': checkpoint, 'closed_parts': len(paths),
                           'final_closed_record': str(paths[-1]),
                           'final_closed_record_sha256': d.sha(paths[-1])}
        else:
            v = d.read(work / 'live_status.json')
            d.need(v['process_alive'] and v['issue'] is None and
                   v['pid'] in live['owned_mdruns'] and checkpoint['age_seconds'] < 420,
                   'Active case requires live process/fresh checkpoint: ' + case)
            v.update(phase='PRODUCING', checkpoint=checkpoint,
                     xtc_bytes=Path(v['log']).with_suffix('.xtc').stat().st_size)
            cases[case] = v
    locks = {}
    for path in (b / 'operator_records/codex_scheduler.lock',
                 b / 'operator_records/equilibration_prep_v2_2_2/serial.lock'):
        with path.open('r') as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                locks[str(path)] = True
            else:
                fcntl.flock(f, fcntl.LOCK_UN)
                locks[str(path)] = False
    if any(v['phase'] == 'PRODUCING' for v in cases.values()):
        d.need(all(locks.values()), 'Active first-pair production must retain both dispatch locks')
    archive = d.read(b / 'operator_records/e2_archive_v1/status.json')
    archive_proc = Path('/proc') / str(archive['pid']) / 'cmdline'
    d.need(archive['state'] != 'ERROR' and archive_proc.exists() and
           b'archive_closed_v1_' in archive_proc.read_bytes(), 'Archive process absent or failed')
    all_closed = all(v['phase'] == 'COMPLETE_100NS_PENDING_RECOVERY_REVIEW' for v in cases.values())
    print(json.dumps({'observed_at': d.now(), 'live': live, 'cases': cases,
                      'locks_held': locks, 'archive': archive, 'successor': queue,
                      'successor_process_alive': queue_alive,
                      'cpu_stat': Path('/sys/fs/cgroup/cpu.stat').read_text(),
                      'first_pair_complete': all_closed,
                      'requires_successor_stage_review': all_closed,
                      'independent_E2_recovery_verified_by_this_snapshot': False,
                      'all_six_complete': False}, indent=2))


if __name__ == '__main__':
    main()
