#!/usr/bin/env python3
"""Prepare chemistry-safe PoseView inputs from a SwissDock pose."""

from __future__ import annotations

import argparse
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from rdkit.Geometry import Point3D


def read_pose_atoms(path: Path) -> tuple[list[str], list[str], list[Point3D]]:
    names: list[str] = []
    elements: list[str] = []
    coords: list[Point3D] = []
    for line in path.read_text().splitlines():
        if not line.startswith("HETATM"):
            continue
        element = line[76:78].strip()
        if element.upper() == "H":
            continue
        names.append(line[12:16].strip())
        elements.append(element)
        coords.append(
            Point3D(float(line[30:38]), float(line[38:46]), float(line[46:54]))
        )
    if not names:
        raise ValueError(f"No ligand HETATM records found in {path}")
    return names, elements, coords


def build_pose_graph(
    rtf_path: Path, names: list[str], elements: list[str]
) -> Chem.Mol:
    atom_types: dict[str, str] = {}
    bond_pairs: list[tuple[str, str]] = []
    for raw in rtf_path.read_text().splitlines():
        fields = raw.split()
        if not fields:
            continue
        if fields[0] == "ATOM" and len(fields) >= 3:
            atom_types[fields[1]] = fields[2]
        elif fields[0] == "BOND" and len(fields) >= 3:
            tokens = fields[1:]
            if len(tokens) % 2:
                raise ValueError(f"Odd BOND field count in: {raw}")
            bond_pairs.extend(zip(tokens[0::2], tokens[1::2]))

    name_to_idx = {name: idx for idx, name in enumerate(names)}
    rw = Chem.RWMol()
    for name, element in zip(names, elements):
        atom = Chem.Atom(element)
        atom.SetProp("pose_atom_name", name)
        rw.AddAtom(atom)

    for first, second in bond_pairs:
        if first not in name_to_idx or second not in name_to_idx:
            continue
        first_type = atom_types[first]
        second_type = atom_types[second]
        if first_type == second_type == "C=C":
            order = Chem.BondType.DOUBLE
        elif {first_type, second_type} == {"C=O", "O=C"}:
            order = Chem.BondType.DOUBLE
        else:
            order = Chem.BondType.SINGLE
        rw.AddBond(name_to_idx[first], name_to_idx[second], order)

    mol = rw.GetMol()
    Chem.SanitizeMol(mol)
    return mol


def write_protein_only(complex_path: Path, output_path: Path) -> None:
    lines: list[str] = []
    for line in complex_path.read_text().splitlines():
        if line.startswith("HETATM"):
            break
        if line.startswith("END") or line.startswith("TER"):
            continue
        lines.append(line)
    lines.extend(["TER", "END"])
    output_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_sdf", type=Path)
    parser.add_argument("pose_complex_pdb", type=Path)
    parser.add_argument("swissparam_rtf", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    supplier = Chem.SDMolSupplier(str(args.source_sdf), removeHs=False)
    source = supplier[0]
    if source is None:
        raise ValueError(f"Could not read {args.source_sdf}")
    source = Chem.RemoveHs(source)
    Chem.AssignStereochemistry(source, cleanIt=True, force=True)

    pose_names, pose_elements, pose_coords = read_pose_atoms(args.pose_complex_pdb)
    pose_graph = build_pose_graph(args.swissparam_rtf, pose_names, pose_elements)
    match = pose_graph.GetSubstructMatch(source, useChirality=False)
    if len(match) != source.GetNumAtoms():
        raise ValueError("Could not map the source SDF onto the SwissDock pose graph")

    output = Chem.Mol(source)
    output.RemoveAllConformers()
    conformer = Chem.Conformer(output.GetNumAtoms())
    conformer.Set3D(True)
    for source_idx, pose_idx in enumerate(match):
        conformer.SetAtomPosition(source_idx, pose_coords[pose_idx])
    output.AddConformer(conformer, assignId=True)
    output.SetProp("_Name", "Gpr2_ascr3_neutral_AC_top1_pose")
    output.SetProp("SOURCE_CHEMISTRY", "ChemSpider 17226059; neutral ascr#3")
    output.SetProp("POSE_SOURCE", "SwissDock AC top1; Gpr2 AF2")

    sdf_path = args.output_dir / "Gpr2_ascr3_neutral_AC_top1_poseview_ligand.sdf"
    writer = Chem.SDWriter(str(sdf_path))
    writer.write(output)
    writer.close()

    protein_path = args.output_dir / "Gpr2_ascr3_neutral_AC_top1_poseview_protein.pdb"
    write_protein_only(args.pose_complex_pdb, protein_path)

    reloaded = Chem.SDMolSupplier(str(sdf_path), removeHs=False)[0]
    if reloaded is None:
        raise ValueError("Generated SDF could not be reloaded")
    source_smiles = Chem.MolToSmiles(source, isomericSmiles=True)
    output_smiles = Chem.MolToSmiles(reloaded, isomericSmiles=True)
    if source_smiles != output_smiles:
        raise ValueError(f"Stereochemistry changed: {source_smiles} != {output_smiles}")

    max_coordinate_error = 0.0
    out_conf = reloaded.GetConformer()
    for source_idx, pose_idx in enumerate(match):
        delta = out_conf.GetAtomPosition(source_idx) - pose_coords[pose_idx]
        max_coordinate_error = max(max_coordinate_error, delta.Length())
    if max_coordinate_error > 0.001:
        raise ValueError(f"Coordinate mismatch: {max_coordinate_error:.4f} A")

    charge = sum(atom.GetFormalCharge() for atom in reloaded.GetAtoms())
    chiral = Chem.FindMolChiralCenters(reloaded, includeUnassigned=True)
    assigned = sum(label != "?" for _, label in chiral)
    print("PASS: PoseView ligand retains chemistry and docking coordinates")
    print(f"Formula: {rdMolDescriptors.CalcMolFormula(reloaded)}")
    print(f"Molecular weight: {Descriptors.MolWt(reloaded):.3f}")
    print(f"Formal charge: {charge}")
    print(f"Assigned chiral centers: {assigned}/{len(chiral)}")
    print(f"Isomeric SMILES: {output_smiles}")
    print(f"Maximum coordinate error: {max_coordinate_error:.4f} A")
    print(f"Protein: {protein_path}")
    print(f"Ligand: {sdf_path}")


if __name__ == "__main__":
    main()
