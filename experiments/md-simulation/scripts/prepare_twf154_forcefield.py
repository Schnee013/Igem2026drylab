#!/usr/bin/env python3
"""Keep the complete CHARMM36m port and use the exact ligand CGenFF fragment.

Only matching CGenFF type definitions are replaced, including their complete
Fourier series. Protein/lipid types are never eligible for replacement.
"""
from collections import Counter
import json
from pathlib import Path
import re
import shutil

SIZES={'atomtypes':1,'bondtypes':2,'pairtypes':2,'angletypes':3,'dihedraltypes':4}


def key(section,line):
    f=line.split(';')[0].split()
    if not f or section not in SIZES or f[0].startswith(('#','[')):return None
    n=SIZES[section];types=tuple(f[:n]);types=min(types,types[::-1])
    return (section,types,'' if section=='atomtypes' else f[n])


def prepare(source,fragment,out,protected_types):
    definitions=set();section='';base_atoms={}
    for line in (source/'ffnonbonded.itp').read_text().splitlines():
        if line.strip().startswith('['):section=line.strip().strip('[] ')
        k=key(section,line)
        if k and section=='atomtypes':base_atoms[k[1][0]]=line.split(';')[0].split()
    section=''
    for line in fragment.read_text().splitlines():
        if line.strip().startswith('['):section=line.strip().strip('[] ')
        k=key(section,line)
        if k:
            if section=='atomtypes':
                f=line.split(';')[0].split();b=base_atoms[f[0]]
                # Defaults charges are unused: molecular charges are explicit.
                assert all(abs(float(f[i])-float(b[i]))<1e-7 for i in [1,2,5,6]),(f,b)
                continue
            assert all(t=='X' or t not in protected_types for t in k[1]), k
            assert any(t.startswith(('CG','OG','HG')) for t in k[1]),k
            definitions.add(k)
    shutil.copytree(source,out)
    counts=Counter();removed=[]
    for p in out.glob('*.itp'):
        lines=[];section=''
        for no,line in enumerate(p.read_text().splitlines(),1):
            if line.strip().startswith('['):section=line.strip().strip('[] ')
            k=key(section,line)
            if k in definitions:
                counts[section]+=1;removed.append({'file':p.name,'line':no,'value':line});continue
            lines.append(line)
        p.write_text('\n'.join(lines)+'\n')
    (out/'ligand_parameter_replacement.json').write_text(json.dumps({'source':str(source),
       'fragment':str(fragment),'removed_counts':dict(counts),'removed_original_rows':removed,
       'rule':'Full fragment overrides matching CGenFF type definitions only; no protein or lipid types modified'},indent=2))
    return dict(counts)
