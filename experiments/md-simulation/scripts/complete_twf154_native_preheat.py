#!/usr/bin/env python3
"""Finalize two independent WT preheats after their heating runners exit normally."""
import argparse
import json
import hashlib
from pathlib import Path
import subprocess
import time

p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root.resolve()
cases=['native_wt_ascr18','native_wt_ascr3'];deadline=time.time()+24*3600
while time.time()<deadline:
    complete=[]
    for case in cases:
        d=root/'runs'/case/'heating_v4'
        qc=d/'hold_snapshot_qc.json';checksums=d/'output.sha256'
        try:passed=json.loads(qc.read_text())['pass']
        except (OSError,ValueError):passed=False
        event=root/'runs'/case/'run_state_events.tsv'
        last=event.read_text().splitlines()[-1] if event.exists() else ''
        complete.append(passed and checksums.exists() and 'TERMINAL_NORMAL' in last)
    if all(complete):
        subprocess.run(['python3',str(root/'scripts/audit_twf154_heating.py'),str(root)],check=True)
        result=json.loads((root/'results/preheat_status.json').read_text())
        assert result['passed']==2
        selected=[]
        for case in cases:
            c=root/'runs'/case;h=c/'heating_v4';info=json.loads((c/'input_contract.json').read_text())
            emrel=(h/'em_source.txt').read_text().strip();em=c/emrel
            gate=json.loads((em.parent/'em_gate.json').read_text())
            digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
            selected.append({'case':case,'genotype':'wt','ligand':info['ligand'],'lid_input':'native',
                'pose_mapping':info['pose_mapping'],'em_source':emrel,'em_Fmax_kJ_mol_nm':gate['fmax_kj_mol_nm'],
                'em_sha256':digest(em),'heating_directory':str(h),'final_gro_sha256':digest(h/'hold.gro')})
        (root/'results/selected_run_manifest.json').write_text(json.dumps({'as_of_utc':result['as_of_utc'],'cases':selected},indent=2))
        print('Both independent WT preheats finished; source-backed summary is ready.',flush=True)
        break
    time.sleep(45)
else:raise RuntimeError('WT preheat not complete within 24h; inspect rather than promote')
