#!/usr/bin/env python3
"""Bounded GeneralizedKIC pilot with fixed exterior and independent geometry gates.

Requires NumPy, RDKit and PyRosetta. Runtime inputs/outputs are supplied by JSON.
Produces local modelling candidates, not MD-ready systems or binding energies.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import time

import numpy as np


SIDE_BONDS = {
    "ALA": "CA-CB", "ARG": "CA-CB CB-CG CG-CD CD-NE NE-CZ CZ-NH1 CZ-NH2",
    "ASN": "CA-CB CB-CG CG-OD1 CG-ND2", "ASP": "CA-CB CB-CG CG-OD1 CG-OD2",
    "CYS": "CA-CB CB-SG", "GLN": "CA-CB CB-CG CG-CD CD-OE1 CD-NE2",
    "GLU": "CA-CB CB-CG CG-CD CD-OE1 CD-OE2", "GLY": "",
    "HIS": "CA-CB CB-CG CG-ND1 ND1-CE1 CE1-NE2 NE2-CD2 CD2-CG",
    "ILE": "CA-CB CB-CG1 CB-CG2 CG1-CD1", "LEU": "CA-CB CB-CG CG-CD1 CG-CD2",
    "LYS": "CA-CB CB-CG CG-CD CD-CE CE-NZ", "MET": "CA-CB CB-CG CG-SD SD-CE",
    "PHE": "CA-CB CB-CG CG-CD1 CG-CD2 CD1-CE1 CD2-CE2 CE1-CZ CE2-CZ",
    "PRO": "CA-CB CB-CG CG-CD CD-N", "SER": "CA-CB CB-OG",
    "THR": "CA-CB CB-OG1 CB-CG2",
    "TRP": "CA-CB CB-CG CG-CD1 CG-CD2 CD1-NE1 NE1-CE2 CE2-CD2 CD2-CE3 CE3-CZ3 CZ3-CH2 CH2-CZ2 CZ2-CE2",
    "TYR": "CA-CB CB-CG CG-CD1 CG-CD2 CD1-CE1 CD2-CE2 CE1-CZ CE2-CZ CZ-OH",
    "VAL": "CA-CB CB-CG1 CB-CG2",
}
VDW = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_pdb(path):
    atoms = {}
    for line in Path(path).read_text().splitlines():
        if not line.startswith("ATOM  "):
            continue
        name, element = line[12:16].strip(), line[76:78].strip()
        element = element or name[0]
        if element == "H":
            continue
        if line[16] not in " A" or line[26] != " ":
            raise ValueError("Alternate positions/insertion codes need explicit handling")
        key = (int(line[22:26]), name)
        if key in atoms:
            raise ValueError(f"Duplicate atom or multiple chains at {key}")
        atoms[key] = {"xyz": np.array([float(line[i:i+8]) for i in (30, 38, 46)]),
                      "element": element, "resname": line[17:20], "chain": line[21]}
    if not atoms:
        raise ValueError("Empty protein")
    return atoms


def angle(a, b, c):
    x, y = a-b, c-b
    return math.degrees(math.acos(float(np.clip(np.dot(x, y)/np.linalg.norm(x)/np.linalg.norm(y), -1, 1))))


def dihedral(a, b, c, d):
    axis = c-b
    axis = axis/np.linalg.norm(axis)
    v, w = a-b, d-c
    v, w = v-np.dot(v, axis)*axis, w-np.dot(w, axis)*axis
    return math.degrees(math.atan2(np.dot(np.cross(axis, v), w), np.dot(v, w)))


class GeometryGate:
    def __init__(self, cfg):
        from rdkit import Chem
        self.cfg = cfg
        self.start, self.end = cfg["loop"]
        self.ss1, self.ss2 = cfg["disulfide"]
        self.ref = read_pdb(cfg["receptor"])
        self.keys = list(self.ref)
        self.index = {key: n for n, key in enumerate(self.keys)}
        self.lid = np.array([self.start <= k[0] <= self.end for k in self.keys])
        self.radii = np.array([VDW[self.ref[k]["element"]] for k in self.keys])
        self.ref_xyz = np.array([self.ref[k]["xyz"] for k in self.keys])
        self.bonds = set()
        graph = {k: set() for k in self.keys}

        def bond(a, b):
            if a in graph and b in graph:
                graph[a].add(b)
                graph[b].add(a)
                self.bonds.add(tuple(sorted((a, b))))

        residues = {k[0]: v["resname"] for k, v in self.ref.items()}
        for r, resname in residues.items():
            for pair in ("N-CA CA-C C-O C-OXT " + SIDE_BONDS[resname]).split():
                a, b = pair.split("-")
                bond((r, a), (r, b))
            if r+1 in residues:
                bond((r, "C"), (r+1, "N"))
        bond((self.ss1, "SG"), (self.ss2, "SG"))
        self.lid_bonds = [b for b in sorted(self.bonds) if any(self.start <= k[0] <= self.end for k in b)]
        self.lid_angles = []
        ss_pair = {(self.ss1,"SG"), (self.ss2,"SG")}
        for center, neighbors in graph.items():
            for left, right in combinations(sorted(neighbors),2):
                if not any(self.start <= k[0] <= self.end for k in (left,center,right)):
                    continue
                if {left,center} == ss_pair or {center,right} == ss_pair:
                    continue
                self.lid_angles.append((left,center,right))
        self.exclude = np.zeros((len(self.keys), len(self.keys)), dtype=bool)
        for k in self.keys:
            reached, frontier = {k}, {k}
            for _ in range(3):
                frontier = {v for u in frontier for v in graph[u]} - reached
                reached |= frontier
            for v in reached:
                self.exclude[self.index[k], self.index[v]] = True
        self.ligands = {}
        for name, path in cfg["ligands"].items():
            supplier = Chem.SDMolSupplier(path, removeHs=False, sanitize=True)
            if len(supplier) != 1 or supplier[0] is None:
                raise ValueError(f"Invalid ligand SDF: {path}")
            mol = supplier[0]
            ids = [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() > 1]
            self.ligands[name] = (np.array(mol.GetConformer().GetPositions())[ids],
                                  np.array([VDW[mol.GetAtomWithIdx(i).GetSymbol()] for i in ids]))

    def evaluate(self, atoms):
        if set(atoms) != set(self.ref):
            raise ValueError("Candidate heavy-atom identity changed")
        xyz = np.array([atoms[k]["xyz"] for k in self.keys])
        if not np.isfinite(xyz).all():
            raise ValueError("Nonfinite coordinates")
        p = lambda r, a: xyz[self.index[(r, a)]]
        xyz_lid, rad_lid = xyz[self.lid], self.radii[self.lid]
        all_dist = np.linalg.norm(xyz_lid[:, None]-xyz[None, :], axis=2)
        pair_mask = ~self.exclude[self.lid]
        pair_mask[:, self.lid] &= np.triu(np.ones((self.lid.sum(), self.lid.sum()), dtype=bool), 1)
        overlaps = rad_lid[:, None]+self.radii[None, :]-all_dist
        steric = {"min_nonbonded_heavy_A": float(all_dist[pair_mask].min()),
                  "max_vdw_overlap_A": float(overlaps[pair_mask].max()),
                  "pairs_overlap_gt_0p6_A": int(((overlaps > 0.6) & pair_mask).sum())}
        ligands = {}
        for name, (lig_xyz, lig_rad) in self.ligands.items():
            dist = np.linalg.norm(xyz_lid[:, None]-lig_xyz[None, :], axis=2)
            ov = rad_lid[:, None]+lig_rad[None, :]-dist
            ligands[name] = {"min_heavy_A": float(dist.min()), "max_vdw_overlap_A": float(ov.max()),
                             "pairs_below_2_A": int((dist < 2).sum()),
                             "pairs_overlap_gt_0p6_A": int((ov > 0.6).sum())}
        a, b = self.ss1, self.ss2
        ss = {"SG_SG_A": float(np.linalg.norm(p(a, "SG")-p(b, "SG"))),
              "CB_SG_SG_deg": angle(p(a,"CB"), p(a,"SG"), p(b,"SG")),
              "SG_SG_CB_deg": angle(p(a,"SG"), p(b,"SG"), p(b,"CB")),
              "chi3_deg": dihedral(p(a,"CB"), p(a,"SG"), p(b,"SG"), p(b,"CB"))}
        peptides = [{"res1": r, "CN_A": float(np.linalg.norm(p(r,"C")-p(r+1,"N"))),
                     "CA_C_N_deg": angle(p(r,"CA"), p(r,"C"), p(r+1,"N")),
                     "C_N_CA_deg": angle(p(r,"C"), p(r+1,"N"), p(r+1,"CA")),
                     "omega_deg": dihedral(p(r,"CA"), p(r,"C"), p(r+1,"N"), p(r+1,"CA"))}
                    for r in range(self.start-1, self.end+1)]
        bond_deviations = []
        for u, v in self.lid_bonds:
            if u[1] == v[1] == "SG":
                continue
            distance = float(np.linalg.norm(xyz[self.index[u]]-xyz[self.index[v]]))
            refdist = float(np.linalg.norm(self.ref[u]["xyz"]-self.ref[v]["xyz"]))
            bond_deviations.append(abs(distance-refdist))
        inverted = []
        for r in range(self.start, self.end+1):
            if (r, "CB") not in atoms:
                continue
            def volume(source):
                ca = source[(r,"CA")]["xyz"]
                return np.linalg.det(np.array([source[(r,k)]["xyz"]-ca for k in ("N", "C", "CB")]))
            if volume(atoms)*volume(self.ref) <= 0:
                inverted.append(r)
        outside = float(np.linalg.norm(xyz[~self.lid]-self.ref_xyz[~self.lid], axis=1).max())
        gates = {
            "outside_fixed": outside <= 0.001,
            "local_bond_lengths": max(bond_deviations) <= 0.12,
            "peptide_connections": all(1.25 <= x["CN_A"] <= 1.42 and 105 <= x["CA_C_N_deg"] <= 135
                                       and 110 <= x["C_N_CA_deg"] <= 135 and abs(x["omega_deg"]) >= 150 for x in peptides),
            "disulfide_geometry": 1.95 <= ss["SG_SG_A"] <= 2.12 and 95 <= ss["CB_SG_SG_deg"] <= 115
                                   and 95 <= ss["SG_SG_CB_deg"] <= 115 and 45 <= abs(ss["chi3_deg"]) <= 135,
            "CA_chirality": not inverted,
            "protein_sterics": steric["max_vdw_overlap_A"] <= 0.6,
            "both_ligand_sterics": all(v["max_vdw_overlap_A"] <= 0.6 for v in ligands.values()),
        }
        return {"geometric_screen_pass": all(gates.values()), "gates": gates,
                "outside_max_displacement_A": outside, "max_bond_length_change_A": max(bond_deviations),
                "inverted_CA": inverted, "protein_sterics": steric, "ligands": ligands,
                "disulfide": ss, "peptides": peptides,
                "lid_backbone_rmsd_no_fit_A": float(np.sqrt(np.mean([np.sum((atoms[k]["xyz"]-self.ref[k]["xyz"])**2)
                    for k in self.keys if self.start <= k[0] <= self.end and k[1] in ("N", "CA", "C", "O")])))}


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n")


def event(out, state, source, detail):
    path = out/"run_state_events.tsv"
    if not path.exists():
        path.write_text("observed_at\tstate\tsource\tdetail\n")
    with path.open("a") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()}\t{state}\t{source}\t{detail}\n")


def kic_xml(cfg, mode):
    start, end = cfg["loop"]
    a, b = cfg["disulfide"]
    residues = "".join(f'<AddResidue res_index="{r}"/>' for r in range(start, end+1))
    if mode == "rama":
        pert = '<AddPerturber effect="randomize_backbone_by_rama_prepro">'+''.join(
            f'<AddResidue index="{r}"/>' for r in range(start, end+1))+'</AddPerturber>'
    else:
        pert = '<AddPerturber effect="perturb_dihedral">'+''.join(
            f'<AddAtoms res1="{r}" atom1="{x}" res2="{r}" atom2="{y}"/>'
            for r in range(start, end+1) for x, y in (("N","CA"),("CA","C")))
        pert += f'<AddValue value="{cfg["perturb_degrees"]}"/></AddPerturber>'
    return f'''<ROSETTASCRIPTS><SCOREFXNS>
      <ScoreFunction name="sfxn" weights="ref2015_cart"/>
      </SCOREFXNS><MOVERS>
      <GeneralizedKIC name="kic" closure_attempts="{cfg['closure_attempts']}"
        stop_when_n_solutions_found="5" selector="lowest_energy_selector" selector_scorefunction="sfxn"
        correct_polymer_dependent_atoms="false">
        {residues}
        <SetPivots res1="{start}" atom1="CA" res2="{(start+end)//2}" atom2="CA" res3="{end}" atom3="CA"/>
        {pert}
        <AddFilter type="loop_bump_check"/>
        <AddAtomPairDistanceFilter atom1="SG" res1="{a}" atom2="SG" res2="{b}" distance="3.5" greater_than="false"/>
      </GeneralizedKIC></MOVERS><PROTOCOLS><Add mover="kic"/></PROTOCOLS></ROSETTASCRIPTS>'''


def disulfide_first_xml(cfg, mode):
    start, end = cfg['loop']
    fixed, mobile = cfg['disulfide']
    if not start+3 <= mobile <= end-3:
        raise ValueError('This two-stage pilot requires sufficient residues on both sides of the mobile cysteine')
    def perturb(residues):
        if mode == 'rama':
            return '<AddPerturber effect="randomize_backbone_by_rama_prepro">'+''.join(
                f'<AddResidue index="{r}"/>' for r in residues)+'</AddPerturber>'
        return '<AddPerturber effect="perturb_dihedral">'+''.join(
            f'<AddAtoms res1="{r}" atom1="{x}" res2="{r}" atom2="{y}"/>'
            for r in residues for x,y in (("N","CA"),("CA","C"))
            if not (r==mobile and x=='N'))+f'<AddValue value="{cfg["perturb_degrees"]}"/></AddPerturber>'
    def rama_filters(residues):
        return ''.join(f'<AddFilter type="rama_prepro_check" residue="{r}" rama_cutoff_energy="1.5"/>' for r in residues)
    left_end=mobile-1
    left_mid=(start+left_end)//2
    right_mid=(mobile+end)//2
    right_res=''.join(f'<AddResidue res_index="{r}"/>' for r in [fixed,*range(mobile,end+1)])
    tails=''.join(f'<AddTailResidue res_index="{r}"/>' for r in range(start,mobile))
    # Include the fixed flank so gap geometry can be set by the perturber API.
    # The first pivot remains CA(start); the flank must pass the exterior gate.
    left_res=''.join(f'<AddResidue res_index="{r}"/>' for r in range(start-1,mobile))
    reference=read_pdb(cfg['receptor'])
    xyz=lambda r,n: reference[(r,n)]['xyz']
    gap_distance=float(np.linalg.norm(xyz(start-1,'C')-xyz(start,'N')))
    gap_angle1=angle(xyz(start-1,'CA'),xyz(start-1,'C'),xyz(start,'N'))
    gap_angle2=angle(xyz(start-1,'C'),xyz(start,'N'),xyz(start,'CA'))
    fixed_psi=dihedral(xyz(start-1,'N'),xyz(start-1,'CA'),xyz(start-1,'C'),xyz(start,'N'))
    gap=f'''<AddPerturber effect="set_bondlength"><AddAtoms res1="{start-1}" atom1="C" res2="{start}" atom2="N"/><AddValue value="{gap_distance}"/></AddPerturber>
      <AddPerturber effect="set_bondangle"><AddAtoms res1="{start-1}" atom1="CA" res2="{start-1}" atom2="C" res3="{start}" atom3="N"/><AddValue value="{gap_angle1}"/></AddPerturber>
      <AddPerturber effect="set_bondangle"><AddAtoms res1="{start-1}" atom1="C" res2="{start}" atom2="N" res3="{start}" atom3="CA"/><AddValue value="{gap_angle2}"/></AddPerturber>
      <AddPerturber effect="set_dihedral"><AddAtoms res1="{start-1}" atom1="C" res2="{start}" atom2="N"/><AddValue value="180"/></AddPerturber>'''
    gap+=f'<AddPerturber effect="set_dihedral"><AddAtoms res1="{start-1}" atom1="CA" res2="{start-1}" atom2="C"/><AddValue value="{fixed_psi}"/></AddPerturber>'
    options=f'closure_attempts="{cfg["closure_attempts"]}" stop_when_n_solutions_found="5" selector="lowest_energy_selector" selector_scorefunction="sfxn" correct_polymer_dependent_atoms="false"'
    return f'''<ROSETTASCRIPTS><SCOREFXNS><ScoreFunction name="sfxn" weights="ref2015_cart"/></SCOREFXNS><MOVERS>
    <GeneralizedKIC name="ss" {options}>
      {right_res}{tails}
      <SetPivots res1="{fixed}" atom1="SG" res2="{right_mid}" atom2="CA" res3="{end}" atom3="CA"/>
      <CloseBond res1="{fixed}" atom1="SG" res2="{mobile}" atom2="SG" bondlength="2.03" angle1="104" angle2="104"/>
      {perturb(range(mobile,end+1))}
      <AddPerturber effect="randomize_dihedral">
        <AddAtoms res1="{mobile}" atom1="SG" res2="{mobile}" atom2="CB"/>
        <AddAtoms res1="{mobile}" atom1="CB" res2="{mobile}" atom2="CA"/>
      </AddPerturber>
      <AddFilter type="loop_bump_check"/>{rama_filters([right_mid,end])}
    </GeneralizedKIC>
    <GeneralizedKIC name="left" {options}>
      {left_res}
      <SetPivots res1="{start}" atom1="CA" res2="{left_mid}" atom2="CA" res3="{left_end}" atom3="CA"/>
      {gap}
      {perturb(range(start,mobile))}
      <AddFilter type="loop_bump_check"/>{rama_filters([start,left_mid,left_end])}
    </GeneralizedKIC>
    </MOVERS><PROTOCOLS><Add mover="ss"/><Add mover="left"/></PROTOCOLS></ROSETTASCRIPTS>'''


def pose_atoms(pose, gate):
    atoms = {}
    for (r, name), record in gate.ref.items():
        xyz = pose.residue(r).xyz(name)
        atoms[(r,name)] = {**record, "xyz": np.array([xyz.x, xyz.y, xyz.z])}
    return atoms


def export_source_atoms(pose, gate, source, target):
    lines = ["REMARK 900 LOCAL LID MODELLING CANDIDATE; NOT A VALIDATED MD INPUT",
             f"REMARK 900 RESIDUES {gate.start}-{gate.end} B VALUES SET TO ZERO: NO PREDICTED CONFIDENCE",
             "REMARK 900 EXTERIOR COORDINATES RETAINED FROM SPECIFIED PARENT"]
    for line in Path(source).read_text().splitlines():
        if line.startswith("ATOM  ") and gate.start <= int(line[22:26]) <= gate.end:
            r, name = int(line[22:26]), line[12:16].strip()
            xyz = pose.residue(r).xyz(name)
            line = line[:30]+f"{xyz.x:8.3f}{xyz.y:8.3f}{xyz.z:8.3f}"+line[54:60]+"  0.00"+line[66:]
        lines.append(line)
    Path(target).write_text("\n".join(lines)+"\n")


def run(cfg, out):
    import pyrosetta
    from pyrosetta import rosetta as R
    out.mkdir(parents=True, exist_ok=False)
    event(out,'UNRESOLVED','config.json','Initializing pilot; runtime not yet verified')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    write_json(out/"config.json", cfg)
    write_json(out/"source_checksums.json", {p: sha(p) for p in [cfg["receptor"], cfg["fasta"], *cfg["ligands"].values(), *cfg.get('refine_inputs',[]), __file__]})
    gate = GeometryGate(cfg)
    write_json(out/"baseline_geometry.json", gate.evaluate(gate.ref))
    pyrosetta.init(f'-constant_seed -jran {cfg["seed"]} -ex1 -ex2aro -mute all')
    parent = pyrosetta.pose_from_pdb(cfg["receptor"])
    expected = ''.join(l.strip() for l in Path(cfg["fasta"]).read_text().splitlines() if not l.startswith('>'))
    for position, aa in cfg["parent_mutations"].items():
        i = int(position)-1
        expected = expected[:i]+aa+expected[i+1:]
    assert parent.sequence() == expected, "Parent sequence differs from configured FASTA+mutation"
    assert all(parent.pdb_info().number(i) == i for i in range(1,parent.total_residue()+1)), "Residue numbering mismatch"
    a, b = cfg["disulfide"]
    assert parent.residue(a).is_bonded(parent.residue(b)), "Expected disulfide was not detected"
    imported = gate.evaluate(pose_atoms(parent, gate))
    assert imported["outside_max_displacement_A"] < 1e-6, "Import moved exterior heavy atoms"
    sfxn = pyrosetta.create_score_function('ref2015_cart')
    score_types = R.core.scoring
    sfxn.set_weight(score_types.atom_pair_constraint, 1.0)
    sfxn.set_weight(score_types.angle_constraint, 1.0)
    sfxn.set_weight(score_types.dihedral_constraint, 1.0)
    atom = lambda r, n: R.core.id.AtomID(parent.residue(r).atom_index(n), r)
    C, F = R.core.scoring.constraints, R.core.scoring.func
    parent.add_constraint(C.AtomPairConstraint(atom(a,'SG'), atom(b,'SG'), F.HarmonicFunc(2.03,0.04)))
    for ids in ((atom(a,'CB'),atom(a,'SG'),atom(b,'SG')), (atom(a,'SG'),atom(b,'SG'),atom(b,'CB'))):
        parent.add_constraint(C.AngleConstraint(*ids, F.HarmonicFunc(math.radians(104),math.radians(5))))
    # Preserve local covalent geometry while allowing all backbone phi/psi motion.
    # These terms were added after the smoke test exposed Cartesian bond strain.
    for u, v in gate.lid_bonds:
        if u[1] == v[1] == 'SG':
            continue
        distance = float(np.linalg.norm(gate.ref[u]['xyz']-gate.ref[v]['xyz']))
        parent.add_constraint(C.AtomPairConstraint(atom(*u),atom(*v),F.HarmonicFunc(distance,0.02)))
    for u, v, w in gate.lid_angles:
        target = math.radians(angle(gate.ref[u]['xyz'],gate.ref[v]['xyz'],gate.ref[w]['xyz']))
        parent.add_constraint(C.AngleConstraint(atom(*u),atom(*v),atom(*w),F.HarmonicFunc(target,math.radians(3))))
    for r in range(gate.start-1,gate.end+1):
        parent.add_constraint(C.DihedralConstraint(atom(r,'CA'),atom(r,'C'),atom(r+1,'N'),atom(r+1,'CA'),
                                                   F.CircularHarmonicFunc(math.pi,math.radians(5))))
    mm = R.core.kinematics.MoveMap()
    mm.set_bb(False); mm.set_chi(False); mm.set_jump(False)
    for r in range(gate.start,gate.end+1):
        mm.set_bb(r,True); mm.set_chi(r,True)
    minimizer = R.protocols.minimization_packing.MinMover(mm,sfxn,'lbfgs_armijo_nonmonotone',0.001,True)
    minimizer.cartesian(True)
    minimizer.max_iter(cfg['min_iterations'])
    task = pyrosetta.standard_packer_task(parent)
    task.restrict_to_repacking()
    for r in range(1,parent.total_residue()+1):
        if not gate.start <= r <= gate.end:
            task.nonconst_residue_task(r).prevent_repacking()
    packer = R.protocols.minimization_packing.PackRotamersMover(sfxn,task)
    movers = {}
    for mode in ('local','rama'):
        method=cfg.get('method','peptide_first')
        xml = disulfide_first_xml(cfg,mode) if method=='disulfide_first' else kic_xml(cfg,mode)
        (out/f'kic_{mode}.xml').write_text(xml)
        objects=R.protocols.rosetta_scripts.XmlObjects.create_from_string(xml)
        names=('ss','left') if method=='disulfide_first' else ('kic',)
        movers[mode] = [(name,objects.get_mover(name)) for name in names]
    manifest = {'pyrosetta': pyrosetta.version(), 'seed': cfg['seed'], 'protein_only_score': 'ref2015_cart+disulfide constraints',
                'note': 'Ligands evaluated separately by geometry only; no binding-energy or MD-readiness claim.'}
    write_json(out/'environment.json',manifest)
    baseline_score = float(sfxn(parent))
    write_json(out/'parent_lid_rama_prepro.json',
               {str(r):float(parent.energies().residue_total_energies(r)[score_types.rama_prepro])
                for r in range(gate.start,gate.end+1)})
    rows = []
    rng = np.random.default_rng(cfg['seed']+1)
    started = time.monotonic()
    event(out,'RUNNING_VERIFIED','environment.json','Pilot initialized; no production MD')
    try:
        for i in range(cfg['candidates']):
            stages=[]
            if cfg.get('refine_inputs'):
                mode='refine_only'
                candidate=pyrosetta.pose_from_pdb(cfg['refine_inputs'][i])
                assert candidate.sequence()==expected
                for constraint in parent.constraint_set().get_all_constraints():
                    candidate.add_constraint(constraint)
                cysteine_chi1=float(candidate.chi(1,b))
                successful=True
            else:
                mode = 'local' if i % 2 == 0 else 'rama'
                candidate = parent.clone()
                # Sample the mobile cysteine only; its fixed partner stays put.
                cysteine_chi1 = float(rng.choice([-60., 60., 180.])+rng.normal(0.,10.))
                candidate.set_chi(1,b,cysteine_chi1)
                for phase,mover in movers[mode]:
                    mover.apply(candidate)
                    stages.append({'phase':phase,'move_status':str(mover.get_last_move_status())})
                    if mover.get_last_move_status() != R.protocols.moves.MS_SUCCESS:
                        break
                    phase_geometry=gate.evaluate(pose_atoms(candidate,gate))
                    stages[-1]['geometry']=phase_geometry
                    if phase_geometry['outside_max_displacement_A']>1e-6:
                        raise RuntimeError(f'{phase} moved atoms outside permitted loop')
                successful=mover.get_last_move_status()==R.protocols.moves.MS_SUCCESS
            row = {'candidate': i+1, 'mode':mode, 'sampled_Cys_chi1_deg':cysteine_chi1,
                   'move_status':'success' if successful else 'failed','closure_stages':stages}
            if not successful:
                row['status']='no_closure_solution'
            else:
                pre = gate.evaluate(pose_atoms(candidate,gate))
                row['after_kic_geometry'] = pre
                if pre['outside_max_displacement_A'] > 1e-6:
                    raise RuntimeError('GKIC moved atoms outside permitted loop')
                packer.apply(candidate)
                row['after_packing_geometry'] = gate.evaluate(pose_atoms(candidate,gate))
                minimizer.apply(candidate)
                row['steric_repair_constraints']=[]
                for repair_round in range(cfg.get('steric_repair_rounds',0)):
                    current=pose_atoms(candidate,gate)
                    xyz=np.array([current[k]['xyz'] for k in gate.keys])
                    added=0
                    for u,k in enumerate(gate.keys):
                        if not gate.lid[u]:
                            continue
                        for v,l in enumerate(gate.keys):
                            if gate.exclude[u,v] or (gate.lid[v] and v<=u):
                                continue
                            lower=float(gate.radii[u]+gate.radii[v]-0.5)
                            distance=float(np.linalg.norm(xyz[u]-xyz[v]))
                            if distance>=lower:
                                continue
                            candidate.add_constraint(C.AtomPairConstraint(atom(*k),atom(*l),
                                C.BoundFunc(lower,100.0,0.05,'local_steric_floor')))
                            row['steric_repair_constraints'].append({'round':repair_round+1,'atom1':k,'atom2':l,
                                                                   'initial_A':distance,'lower_A':lower,'width_A':0.05})
                            added+=1
                    if not added:
                        break
                    minimizer.apply(candidate)
                atoms = pose_atoms(candidate,gate)
                check = gate.evaluate(atoms)
                if check['outside_max_displacement_A'] > 1e-6:
                    raise RuntimeError('Refinement moved atoms outside permitted loop')
                row.update(status='geometry_screened', geometry=check, protein_score_REU=float(sfxn(candidate)),
                           parent_protein_score_REU=baseline_score)
                row['lid_rama_prepro_REU'] = {str(r): float(candidate.energies().residue_total_energies(r)[score_types.rama_prepro])
                                              for r in range(gate.start,gate.end+1)}
                file = out/f'candidate_{i+1:04d}.pdb'
                export_source_atoms(candidate,gate,cfg['receptor'],file)
                written = gate.evaluate(read_pdb(file))
                row['written_geometry']=written
                row['output']=str(file)
                row['sha256']=sha(file)
                row['geometric_screen_pass']=check['geometric_screen_pass'] and written['geometric_screen_pass']
            rows.append(row)
            write_json(out/'candidates.json',rows)
            print(json.dumps({'candidate': i+1,'mode':mode,'status':row['status'],
                              'geometric_screen_pass':row.get('geometric_screen_pass',False),
                              'elapsed_s':time.monotonic()-started}),flush=True)
            event(out,'RUNNING_VERIFIED','candidates.json',f'Completed pilot candidate {i+1}/{cfg["candidates"]}')
        summary = {'completed_candidates':len(rows),'closure_successes':sum(r['status']=='geometry_screened' for r in rows),
                   'geometric_screen_passes':sum(r.get('geometric_screen_pass',False) for r in rows),
                   'elapsed_s':time.monotonic()-started,'candidates_sha256':sha(out/'candidates.json'),
                   'production_ready':False,'interpretation':'Bounded local-model pilot; passing geometry still needs energetic and sensitivity review before MD preparation.'}
        write_json(out/'summary.json',summary)
        event(out,'TERMINAL_NORMAL','summary.json',f'Pilot finished; geometry passes={summary["geometric_screen_passes"]}; no MD launched')
    except Exception as e:
        write_json(out/'error.json',{'type':type(e).__name__,'message':str(e),'completed':len(rows)})
        event(out,'TERMINAL_ABNORMAL','error.json',str(e).replace('\t',' ').replace('\n',' '))
        raise


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--geometry-only',action='store_true')
    args=ap.parse_args()
    cfg=json.loads(args.config.read_text())
    if args.geometry_only:
        gate=GeometryGate(cfg)
        write_json(args.output,gate.evaluate(gate.ref))
    else:
        run(cfg,args.output)


if __name__ == '__main__':
    main()
