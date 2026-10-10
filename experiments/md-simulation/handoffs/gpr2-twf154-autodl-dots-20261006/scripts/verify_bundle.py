#!/usr/bin/env python3
"""Validate the exact exported payload, not MD scientific readiness."""
import argparse
import hashlib
import json
from pathlib import Path
import re

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    a=ap.parse_args();root=a.root.resolve()
    manifest=json.loads((root/'MANIFEST.json').read_text())
    errors=[]
    for row in manifest['files']:
        p=root/row['path']
        if not p.is_file() or p.is_symlink():errors.append('Missing/symlink: '+row['path']);continue
        if p.stat().st_size!=row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('Changed: '+row['path'])
    for p in (root/'compute').rglob('*'):
        if p.is_symlink():errors.append('Symlink: '+str(p))
        if p.is_file() and p.suffix in ['.top','.itp']:
            for name in re.findall(r'^\s*#include\s+["<]([^">]+)',p.read_text(),re.M):
                q=p.parent/name
                if Path(name).is_absolute() or not q.is_file():errors.append(f'Unresolved include: {p.relative_to(root)} -> {name}')
    order=json.loads((root/'WORK_ORDER.json').read_text())
    assert len(order['cases'])==6 and order['production_ns_per_rep']==100 and order['reps']==[1]
    assert not list((root/'compute').rglob('production.cpt')), 'Historical progress CPT is not a valid migration package'
    assert not list((root/'compute').rglob('*.xtc')) and not list((root/'compute').rglob('*.trr'))
    result={'integrity_pass':not errors,'checked_files':len(manifest['files']),'errors':errors,'production_readiness':'NOT_CLAIMED; follow WORK_ORDER and RUNBOOK'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
