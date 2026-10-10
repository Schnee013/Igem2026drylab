#!/usr/bin/env python3
"""Bounded geometry refinement of one own-parent candidate with fixed own pose.

Adds an explicit ligand steric obstacle and a stronger Ramachandran preference.
Weights/floors are modelling heuristics; scores are not binding energies.
"""
import argparse
import json
import math
from pathlib import Path
import time

import numpy as np
import pyrosetta
from pyrosetta import rosetta as R

from sample_disulfide_lid import (GeometryGate, angle, dihedral, event,
    export_source_atoms, pose_atoms, read_pdb, sha, write_json)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',required=True,type=Path)
    ap.add_argument('--candidate',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    cfg=json.loads(args.config.read_text())
    assert len(cfg['ligands'])==1
    out=args.output;out.mkdir(parents=True,exist_ok=False)
    write_json(out/'config.json',cfg)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    write_json(out/'source_checksums.json',{str(p):sha(p) for p in [args.candidate,args.config,Path(cfg['receptor']),*[Path(v) for v in cfg['ligands'].values()]]})
    gate=GeometryGate(cfg)
    pyrosetta.init(f'-constant_seed -jran {cfg["seed"]} -ex1 -ex2aro -mute all')
    p=pyrosetta.pose_from_pdb(str(args.candidate))
    initial=gate.evaluate(pose_atoms(p,gate))
    assert initial['outside_max_displacement_A']<1e-6
    atom=lambda r,n:R.core.id.AtomID(p.residue(r).atom_index(n),r)
    C,F,S=R.core.scoring.constraints,R.core.scoring.func,R.core.scoring
    score=pyrosetta.create_score_function('ref2015_cart')
    for st in [S.atom_pair_constraint,S.angle_constraint,S.dihedral_constraint,S.coordinate_constraint]:score.set_weight(st,1.0)
    score.set_weight(S.rama_prepro,3.0)
    for u,v in gate.lid_bonds:
        if u[1]==v[1]=='SG':continue
        target=float(np.linalg.norm(gate.ref[u]['xyz']-gate.ref[v]['xyz']))
        p.add_constraint(C.AtomPairConstraint(atom(*u),atom(*v),F.HarmonicFunc(target,.02)))
    for u,v,w in gate.lid_angles:
        target=math.radians(angle(gate.ref[u]['xyz'],gate.ref[v]['xyz'],gate.ref[w]['xyz']))
        p.add_constraint(C.AngleConstraint(atom(*u),atom(*v),atom(*w),F.HarmonicFunc(target,math.radians(3))))
    for r in range(gate.start-1,gate.end+1):
        p.add_constraint(C.DihedralConstraint(atom(r,'CA'),atom(r,'C'),atom(r+1,'N'),atom(r+1,'CA'),F.CircularHarmonicFunc(math.pi,math.radians(5))))
    a,b=cfg['disulfide']
    p.add_constraint(C.AtomPairConstraint(atom(a,'SG'),atom(b,'SG'),F.HarmonicFunc(2.03,.04)))
    for ids in [(atom(a,'CB'),atom(a,'SG'),atom(b,'SG')),(atom(a,'SG'),atom(b,'SG'),atom(b,'CB'))]:
        p.add_constraint(C.AngleConstraint(*ids,F.HarmonicFunc(math.radians(104),math.radians(5))))
    chir=1 if initial['disulfide']['chi3_deg']>0 else -1
    p.add_constraint(C.DihedralConstraint(atom(a,'CB'),atom(a,'SG'),atom(b,'SG'),atom(b,'CB'),F.CircularHarmonicFunc(chir*math.pi/2,math.radians(5))))
    # Ligand atoms are fixed targets only; no receptor or ligand source is moved.
    lig_x,lig_r=next(iter(gate.ligands.values()))
    for i,k in enumerate(gate.keys):
        if not gate.lid[i]:continue
        for x,rad in zip(lig_x,lig_r):
            p.add_constraint(C.CoordinateConstraint(atom(*k),atom(1,'CA'),R.numeric.xyzVector_double_t(*map(float,x)),
                C.BoundFunc(float(gate.radii[i]+rad-.5),1000.0,.1,'fixed_own_ligand_obstacle')))
    mm=R.core.kinematics.MoveMap();mm.set_bb(False);mm.set_chi(False);mm.set_jump(False)
    for r in range(gate.start,gate.end+1):mm.set_bb(r,True);mm.set_chi(r,True)
    minimizer=R.protocols.minimization_packing.MinMover(mm,score,'lbfgs_armijo_nonmonotone',.001,True)
    minimizer.cartesian(True);minimizer.max_iter(1000)
    details=[];seen=set();started=time.monotonic()
    event(out,'RUNNING_VERIFIED','source_checksums.json','Own candidate loaded; fixed exterior verified; bounded local refinement')
    for round_id in range(3):
        aa=pose_atoms(p,gate);x=np.array([aa[k]['xyz'] for k in gate.keys]);lid_ids=np.where(gate.lid)[0]
        dist=np.linalg.norm(x[lid_ids,None]-x[None,:],axis=2)
        lower=gate.radii[lid_ids,None]+gate.radii[None,:]-.5
        near=(dist<lower+.2)&~gate.exclude[lid_ids]
        for row,j in zip(*np.where(near)):
            i=lid_ids[row]
            pair=tuple(sorted((int(i),int(j))))
            if pair in seen:continue
            seen.add(pair)
            p.add_constraint(C.AtomPairConstraint(atom(*gate.keys[i]),atom(*gate.keys[j]),C.BoundFunc(float(lower[row,j]),1000.0,.05,'local_protein_steric_floor')))
        minimizer.apply(p)
        geometry=gate.evaluate(pose_atoms(p,gate));assert geometry['outside_max_displacement_A']<1e-6
        score(p)
        rama={str(r):float(p.energies().residue_total_energies(r)[S.rama_prepro]) for r in range(gate.start,gate.end+1)}
        file=out/f'candidate_{round_id+1:04d}.pdb';export_source_atoms(p,gate,cfg['receptor'],file)
        written=gate.evaluate(read_pdb(file))
        details.append(dict(round=round_id+1,path=str(file),sha256=sha(file),geometry=written,lid_rama_prepro_REU=rama,
            max_rama_prepro_REU=max(rama.values()),geometry_screen_pass=written['geometric_screen_pass'],elapsed_s=time.monotonic()-started))
        write_json(out/'refinement.json',dict(source_candidate=str(args.candidate),initial_geometry=initial,
            rama_prepro_weight=3.0,protein_and_ligand_steric_floor='sum of van der Waals radii minus 0.5 A; modelling heuristic',rounds=details,
            production_ready=False,interpretation='Candidate geometry refinement only; no binding energy or final structure acceptance'))
        event(out,'RUNNING_VERIFIED','refinement.json',f'Refinement round {round_id+1}/3 completed')
        print(json.dumps(dict(round=round_id+1,geometric_screen_pass=written['geometric_screen_pass'],max_rama=max(rama.values()))),flush=True)
    event(out,'TERMINAL_NORMAL','refinement.json','Bounded refinement completed; independent topology/visual review still required')


if __name__=='__main__':
    main()
