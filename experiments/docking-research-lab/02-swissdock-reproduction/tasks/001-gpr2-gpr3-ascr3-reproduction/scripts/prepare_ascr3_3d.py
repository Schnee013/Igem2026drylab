#!/usr/bin/env python3
"""Generate one deterministic 3D ascr#3 conformer from the ChemSpider MOL."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors


EXPECTED_FORMULA = "C15H26O6"
EXPECTED_CHIRAL_CENTERS = 5
DEFAULT_SEED = 20260811


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def infer_alkene_stereo_from_2d(mol: Chem.Mol) -> str:
    """Preserve the E/Z geometry drawn in the ChemSpider 2D coordinates."""
    cc_double_bonds = [
        bond
        for bond in mol.GetBonds()
        if bond.GetBondType() == Chem.BondType.DOUBLE
        and bond.GetBeginAtom().GetAtomicNum() == 6
        and bond.GetEndAtom().GetAtomicNum() == 6
    ]
    if len(cc_double_bonds) != 1:
        fail(f"expected one C=C bond, found {len(cc_double_bonds)}")

    bond = cc_double_bonds[0]
    if bond.GetStereo() in (Chem.BondStereo.STEREOE, Chem.BondStereo.STEREOZ):
        return "E" if bond.GetStereo() == Chem.BondStereo.STEREOE else "Z"

    begin = bond.GetBeginAtom()
    end = bond.GetEndAtom()
    begin_subs = [
        atom
        for atom in begin.GetNeighbors()
        if atom.GetIdx() != end.GetIdx() and atom.GetAtomicNum() != 1
    ]
    end_subs = [
        atom
        for atom in end.GetNeighbors()
        if atom.GetIdx() != begin.GetIdx() and atom.GetAtomicNum() != 1
    ]
    if len(begin_subs) != 1 or len(end_subs) != 1:
        fail("could not identify the two heavy-atom substituents around C=C")

    conf = mol.GetConformer()
    p_begin = conf.GetAtomPosition(begin.GetIdx())
    p_end = conf.GetAtomPosition(end.GetIdx())
    p_sub1 = conf.GetAtomPosition(begin_subs[0].GetIdx())
    p_sub2 = conf.GetAtomPosition(end_subs[0].GetIdx())

    dx = p_end.x - p_begin.x
    dy = p_end.y - p_begin.y
    cross1 = dx * (p_sub1.y - p_begin.y) - dy * (p_sub1.x - p_begin.x)
    cross2 = dx * (p_sub2.y - p_end.y) - dy * (p_sub2.x - p_end.x)
    if math.isclose(cross1 * cross2, 0.0, abs_tol=1e-8):
        fail("C=C geometry is degenerate in the source 2D coordinates")

    geometry = "E" if cross1 * cross2 < 0 else "Z"
    bond.SetStereoAtoms(begin_subs[0].GetIdx(), end_subs[0].GetIdx())
    bond.SetStereo(
        Chem.BondStereo.STEREOE if geometry == "E" else Chem.BondStereo.STEREOZ
    )
    return geometry


def assigned_chiral_centers(mol: Chem.Mol) -> list[tuple[int, str]]:
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    return Chem.FindMolChiralCenters(
        mol, includeUnassigned=True, useLegacyImplementation=False
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_mol", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    input_path = args.input_mol.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not input_path.is_file():
        fail(f"input file not found: {input_path}")

    source = Chem.MolFromMolFile(
        str(input_path), sanitize=True, removeHs=False, strictParsing=True
    )
    if source is None:
        fail("RDKit could not parse the ChemSpider MOL")

    formula = rdMolDescriptors.CalcMolFormula(source)
    if formula != EXPECTED_FORMULA:
        fail(f"expected formula {EXPECTED_FORMULA}, found {formula}")
    if source.GetNumHeavyAtoms() != 21 or source.GetNumAtoms() != 47:
        fail(
            "expected 21 heavy atoms and 47 total atoms, found "
            f"{source.GetNumHeavyAtoms()} and {source.GetNumAtoms()}"
        )

    centers_before = assigned_chiral_centers(source)
    if len(centers_before) != EXPECTED_CHIRAL_CENTERS or any(
        label == "?" for _, label in centers_before
    ):
        fail(f"expected five assigned chiral centers, found {centers_before}")

    alkene_geometry = infer_alkene_stereo_from_2d(source)
    source_smiles = Chem.MolToSmiles(Chem.RemoveHs(source), isomericSmiles=True)

    mol3d = Chem.AddHs(Chem.RemoveHs(source))
    params = AllChem.ETKDGv3()
    params.randomSeed = args.seed
    params.enforceChirality = True
    params.useSmallRingTorsions = True
    embed_status = AllChem.EmbedMolecule(mol3d, params)
    if embed_status != 0:
        params.useRandomCoords = True
        embed_status = AllChem.EmbedMolecule(mol3d, params)
    if embed_status != 0:
        fail("3D embedding failed")

    if AllChem.MMFFHasAllMoleculeParams(mol3d):
        force_field_name = "MMFF94s"
        properties = AllChem.MMFFGetMoleculeProperties(mol3d, mmffVariant="MMFF94s")
        force_field = AllChem.MMFFGetMoleculeForceField(mol3d, properties)
    else:
        force_field_name = "UFF"
        force_field = AllChem.UFFGetMoleculeForceField(mol3d)
    optimization_status = force_field.Minimize(maxIts=500)
    energy = force_field.CalcEnergy()

    Chem.AssignStereochemistryFrom3D(mol3d, replaceExistingTags=True)
    Chem.AssignStereochemistry(mol3d, cleanIt=True, force=True)
    centers_after = assigned_chiral_centers(mol3d)
    output_smiles = Chem.MolToSmiles(Chem.RemoveHs(mol3d), isomericSmiles=True)
    if source_smiles != output_smiles:
        fail(
            "stereochemical identity changed during 3D generation:\n"
            f"source: {source_smiles}\noutput: {output_smiles}"
        )
    if len(centers_after) != EXPECTED_CHIRAL_CENTERS or any(
        label == "?" for _, label in centers_after
    ):
        fail(f"3D output does not retain five assigned centers: {centers_after}")

    conf = mol3d.GetConformer()
    z_values = [conf.GetAtomPosition(i).z for i in range(mol3d.GetNumAtoms())]
    z_span = max(z_values) - min(z_values)
    if not conf.Is3D() or z_span < 0.5:
        fail("output coordinates are not genuinely three-dimensional")

    mol3d.SetProp("_Name", "ascr3_ChemSpider_17226059_3D")
    mol3d.SetProp("SOURCE", "ChemSpider ID 17226059")
    mol3d.SetProp("PREPARATION", f"ETKDGv3 + {force_field_name}; seed {args.seed}")
    mol3d.SetProp("ISOMERIC_SMILES", output_smiles)

    sdf_path = output_dir / "ascr3_ChemSpider_17226059_3D.sdf"
    mol_path = output_dir / "ascr3_ChemSpider_17226059_3D.mol"
    report_path = output_dir / "ascr3-preparation-report.json"

    writer = Chem.SDWriter(str(sdf_path))
    writer.write(mol3d)
    writer.close()
    Chem.MolToMolFile(mol3d, str(mol_path))

    report = {
        "source_file": input_path.name,
        "source_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "source": "ChemSpider ID 17226059",
        "rdkit_version": Chem.rdBase.rdkitVersion,
        "formula": rdMolDescriptors.CalcMolFormula(mol3d),
        "formal_charge": Chem.GetFormalCharge(mol3d),
        "heavy_atoms": mol3d.GetNumHeavyAtoms(),
        "total_atoms_with_hydrogens": mol3d.GetNumAtoms(),
        "assigned_chiral_centers": centers_after,
        "alkene_geometry_from_source_2d": alkene_geometry,
        "isomeric_smiles": output_smiles,
        "embedding": "ETKDGv3",
        "random_seed": args.seed,
        "force_field": force_field_name,
        "optimization_converged": optimization_status == 0,
        "final_force_field_energy": energy,
        "z_coordinate_span_angstrom": z_span,
        "protonation_policy": "neutral form exactly as downloaded from ChemSpider",
        "outputs": [sdf_path.name, mol_path.name],
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("PASS: ascr#3 identity and stereochemistry retained")
    print(f"Formula: {report['formula']}; formal charge: {report['formal_charge']}")
    print(f"Chiral centers: {len(centers_after)} assigned; alkene: {alkene_geometry}")
    print(f"3D z-span: {z_span:.2f} A; force field: {force_field_name}")
    print(f"Output: {sdf_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
