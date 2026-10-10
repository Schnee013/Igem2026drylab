#!/usr/bin/env python3
"""Small preparation/QC helpers for the authorized TWF154 heating diagnostic."""
import argparse
from collections import defaultdict
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import re


COMMON='''cutoff-scheme = Verlet
nstlist = 20
rlist = 1.2
vdwtype = Cut-off
vdw-modifier = Force-switch
rvdw_switch = 1.0
rvdw = 1.2
coulombtype = PME
rcoulomb = 1.2
pbc = xyz
'''


def setup():
    for stage,bb,sc,lip,lig,dih in [('em',4000,2000,1000,1000,1000),('heat',4000,2000,1000,1000,1000),('hold',1000,500,400,100,400)]:
        text=f'define = -DPOSRES -DPOSRES_FC_BB={bb} -DPOSRES_FC_SC={sc} -DPOSRES_FC_LIPID={lip} -DPOSRES_FC_LIG={lig} -DDIHRES -DDIHRES_FC={dih}\n'+COMMON
        if stage=='em':
            text+='integrator = steep\nemtol = 1000\nemstep = 0.001\nnsteps = 100000\nconstraints = none\nnstenergy = 100\nnstlog = 100\n'
        else:
            text+='integrator = md\ndt = 0.001\nconstraints = h-bonds\nconstraint_algorithm = LINCS\nlincs_order = 4\nlincs_iter = 2\nnstxout-compressed = 1000\nnstenergy = 500\nnstlog = 500\nnstcalcenergy = 100\ntcoupl = v-rescale\ntc_grps = SOLU MEMB SOLV\ntau_t = 1.0 1.0 1.0\nref_t = 303.15 303.15 303.15\npcoupl = no\nnstcomm = 100\ncomm_mode = linear\ncomm_grps = System\n'
            if stage=='heat':
                text+='nsteps = 50000\ngen_vel = yes\ngen_temp = 50\ngen_seed = 8428368\ncontinuation = no\nannealing = single single single\nannealing_npoints = 2 2 2\nannealing_time = 0 50 0 50 0 50\nannealing_temp = 50 303.15 50 303.15 50 303.15\n'
            else:text+='nsteps = 75000\ntinit = 50\ngen_vel = no\ncontinuation = yes\n'
        Path(stage+'.mdp').write_text(text)
    Path('genion.mdp').write_text(COMMON+'integrator = steep\nnsteps = 0\nconstraints = none\n')


def water_count_and_ions():
    text=Path('topol.top').read_text();m=re.findall(r'^SOL\s+(\d+)\s*$',text,re.M);assert len(m)==1
    nw=int(m[0]);info=json.loads(Path('input_contract.json').read_text());charge=round(info['charge'])-1
    pairs=round(nw*0.15/55.5);npot=pairs+max(-charge,0);ncla=pairs+max(charge,0)
    Path('ion_counts.json').write_text(json.dumps({'water_before_ions':nw,'protein_plus_ligand_charge':charge,
       'neutral_salt_pairs':pairs,'POT':npot,'CLA':ncla,'rule':'0.15/55.5 times initial water count, plus counterions'},indent=2))
    print(npot,ncla)


def index():
    ls=Path('ionized.gro').read_text().splitlines();n=int(ls[1]);groups=defaultdict(list)
    for i,line in enumerate(ls[2:n+2],1):
        name=line[5:10].strip();groups['System'].append(i)
        groups['MEMB' if name=='POPC' else 'SOLV' if name in {'SOL','POT','CLA'} else 'SOLU'].append(i)
    with Path('index.ndx').open('w') as h:
        for name,values in groups.items():
            h.write(f'[ {name} ]\n')
            for start in range(0,len(values),15):h.write(' '.join(map(str,values[start:start+15]))+'\n')
    assert all(groups[g] for g in ['SOLU','MEMB','SOLV'])


def event(state,detail):
    p=Path('run_state_events.tsv')
    if not p.exists():p.write_text('time_utc\tstate\tsource\tdetail\n')
    with p.open('a') as f:f.write(f'{datetime.now(timezone.utc).isoformat()}\t{state}\trunner.log\t{detail}\n')


def check_em():
    text=Path('em.log').read_text();matches=re.findall(r'Maximum force\s*=\s*([0-9.eE+-]+)',text)
    assert matches,'No final EM maximum force';force=float(matches[-1]);assert force<=1000,f'EM force too large: {force}'
    assert Path('em.gro').exists()
    ls=Path('em.gro').read_text().splitlines();n=int(ls[1]);box=list(map(float,ls[n+2].split()[:3]));waters=defaultdict(list)
    for line in ls[2:n+2]:
        p=[float(line[i:i+8]) for i in [20,28,36]];assert all(math.isfinite(v) for v in p)
        if line[5:10].strip()=='SOL':waters[int(line[:5])].append(p)
    def distance(a,b):return math.sqrt(sum((v-round(v/L)*L)**2 for v,L in zip([x-y for x,y in zip(a,b)],box)))
    err=0.0
    for p in waters.values():
        assert len(p)==3
        err=max(err,abs(distance(p[0],p[1])-0.09572),abs(distance(p[0],p[2])-0.09572),abs(distance(p[1],p[2])-0.15139))
    assert err<0.003, f'Final water geometry is inconsistent after EM: {err} nm'
    count=json.loads(Path('input_contract.json').read_text())['atoms']
    ref=Path('ionized.gro') if Path('ionized.gro').exists() else Path('../ionized.gro')
    def protein(lines):return {(int(l[:5]),l[10:15].strip()):[float(l[i:i+8]) for i in [20,28,36]] for l in lines[2:2+count]}
    start=protein(ref.read_text().splitlines());end=protein(ls)
    def sub(a,b):return [v-round(v/L)*L for v,L in zip([x-y for x,y in zip(a,b)],box)]
    def volume(m,r,center,names):
        a,b,c=[sub(m[r,k],m[r,center]) for k in names]
        return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
    inversions=[]
    for r in range(1,407):
        if (r,'CB') in start and volume(start,r,'CA',['N','C','CB'])*volume(end,r,'CA',['N','C','CB'])<=0:inversions.append([r,'CA'])
        for names in [['CA','OG1','CG2'],['CA','CG1','CG2']]:
            if all((r,k) in start for k in names) and volume(start,r,'CB',names)*volume(end,r,'CB',names)<=0:inversions.append([r,'CB'])
    ss=distance(end[99,'SG'],end[173,'SG'])
    report={'fmax_kj_mol_nm':force,'finite_coordinates':True,'protein_chirality_inversions':inversions,
            'disulfide_nm':ss,'max_water_distance_error_nm':err,
            'water_geometry_note':'0.003 nm includes GRO coordinate rounding; gross-error screen only',
            'pass':not inversions and 0.19<ss<0.22}
    Path('em_gate.json').write_text(json.dumps(report,indent=2))
    assert report['pass'],report


def check_warning():
    text=Path('genion.grompp.log').read_text();warnings=re.findall(r'WARNING \d+.*?(?=\n\n)',text,re.S)
    assert len(warnings)==1 and 'net charge' in warnings[0],warnings
    assert 'ERROR ' not in text
    Path('genion_warning_contract.json').write_text(json.dumps({'accepted_warning':warnings[0],
          'reason':'Temporary charged pre-ionization system only; final neutral compilation must have zero warnings'},indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode');ap.add_argument('args',nargs='*');a=ap.parse_args()
    {'setup':setup,'ions':water_count_and_ions,'index':index,'em_gate':check_em,'warning_gate':check_warning,
     'event':lambda:event(*a.args)}[a.mode]()
