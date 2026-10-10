#!/usr/bin/env python3
"""Export a Meeko ligand PDBQT pose to prepared SDF for Maestro LID."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Any

from atomic_publish import publish_staged_file
from docking_tool_result import ToolArtifact, write_tool_result
from external_process import run_external

from export_receptor_pdbqt_to_pdb import (
    COORDINATE_TOLERANCE_ANGSTROM,
    pdbqt_atom_records,
    pdbqt_element,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Recover a prepared ligand .sdf from .pdbqt using its Meeko "
            "structure metadata."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python src/export_ligand_pdbqt_to_sdf.py --input ligand.pdbqt "
            "--output ligand.sdf --meeko-python /path/to/python\n\n"
            "The explicit --meeko-python must provide both Meeko and RDKit."
        ),
    )
    parser.add_argument(
        "--input", required=True, type=Path, help="source ligand .pdbqt"
    )
    parser.add_argument("--output", required=True, type=Path, help="target ligand .sdf")
    parser.add_argument(
        "--meeko-python",
        required=True,
        type=Path,
        help="Python executable with Meeko and RDKit installed",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="replace an existing output file"
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _validate_paths(source: Path, target: Path, overwrite: bool) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"input file not found: {source}")
    if source.suffix.lower() != ".pdbqt":
        raise ValueError("input filename must end in .pdbqt")
    if target.suffix.lower() not in {".sdf", ".sd"}:
        raise ValueError("output filename must end in .sdf or .sd")
    if target.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {target} (use --overwrite)")


def _match_coordinate_inventory(
    source_atoms: list[tuple[str, tuple[float, float, float]]],
    target_atoms: list[tuple[str, tuple[float, float, float]]],
) -> float:
    """Match a coordinate-bearing element inventory independent of atom ordering."""
    unmatched = list(target_atoms)
    maximum_delta = 0.0
    for element, coord in source_atoms:
        compatible = [
            (math.dist(coord, target_coord), index)
            for index, (target_element, target_coord) in enumerate(unmatched)
            if target_element == element
        ]
        if not compatible:
            raise RuntimeError(f"ligand recovery lost a serialized {element} atom")
        delta, match_index = min(compatible)
        maximum_delta = max(maximum_delta, delta)
        unmatched.pop(match_index)
    return maximum_delta


def _external_python_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for variable in ("PYTHONHOME", "PYTHONPATH", "PYTHONEXECUTABLE"):
        environment.pop(variable, None)
    return environment


def _meeko_runner(meeko_python: Path) -> list[str]:
    """Validate the explicit Python executable that provides Meeko/RDKit."""
    executable = meeko_python.expanduser().resolve()
    if not executable.is_file():
        raise FileNotFoundError(f"Meeko Python executable not found: {executable}")
    probe = "import meeko; assert meeko.__version__"
    try:
        result = run_external(
            [str(executable), "-c", probe],
            text=True,
            timeout=30,
            env=_external_python_environment(),
            forward_stdout=False,
            forward_stderr=False,
        )
    except (OSError, TimeoutExpired) as error:
        raise RuntimeError(
            f"Meeko Python probe failed for {executable}: {type(error).__name__}"
        ) from error
    if result.returncode == 0:
        return [str(executable)]
    raise RuntimeError(
        "Meeko is required for strict ligand PDBQT→SDF recovery. "
        f"The explicit --meeko-python does not import Meeko: {executable}"
    )


def _meeko_export_program() -> str:
    return r'''from pathlib import Path
import sys
from meeko import PDBQTMolecule, RDKitMolCreate
source, target = map(Path, sys.argv[1:3])
pdbqt = PDBQTMolecule.from_file(str(source), skip_typing=True)
sdf, failures = RDKitMolCreate.write_sd_string(pdbqt)
if failures or not sdf.strip():
    raise RuntimeError(f"Meeko failed to recover molecule indices: {failures}")
target.write_text(sdf, encoding="utf-8")
'''


def _meeko_inspect_program() -> str:
    return r'''import json, sys
from rdkit import Chem
supplier = Chem.SDMolSupplier(sys.argv[1], removeHs=False, sanitize=True, strictParsing=True)
molecules = list(supplier)
if len(molecules) != 1 or molecules[0] is None:
    raise RuntimeError(f"expected exactly one valid SDF record, got {len(molecules)}")
mol = molecules[0]
conf = mol.GetConformer()
atoms = []
for index, atom in enumerate(mol.GetAtoms()):
    point = conf.GetAtomPosition(index)
    atoms.append({"element": atom.GetSymbol(), "coord": [point.x, point.y, point.z]})
print(json.dumps({
    "atom_count": mol.GetNumAtoms(),
    "heavy_atom_count": mol.GetNumHeavyAtoms(),
    "formal_charge": Chem.GetFormalCharge(mol),
    "canonical_isomeric_smiles": Chem.MolToSmiles(Chem.RemoveHs(mol), isomericSmiles=True),
    "atoms": atoms,
}, separators=(",", ":")))
'''


def convert_ligand_pdbqt_to_sdf(
    source: Path, target: Path, *, meeko_python: Path
) -> dict[str, Any]:
    """Recover chemistry with Meeko metadata and verify serialized pose coordinates."""
    text = source.read_text(encoding="utf-8")
    required_metadata = ("REMARK SMILES ", "REMARK SMILES IDX ")
    missing = [item.strip() for item in required_metadata if item not in text]
    if missing:
        raise ValueError(
            "strict ligand recovery is impossible; missing Meeko metadata: "
            + ", ".join(missing)
        )
    source_records = pdbqt_atom_records(source)
    runner = _meeko_runner(meeko_python)
    export = run_external(
        [*runner, "-c", _meeko_export_program(), str(source), str(target)],
        text=True,
        timeout=120,
        env=_external_python_environment(),
        forward_stdout=False,
        forward_stderr=False,
    )
    if export.returncode != 0:
        raise RuntimeError(f"Meeko PDBQT→SDF recovery failed: {export.stderr.strip()}")
    inspect = run_external(
        [*runner, "-c", _meeko_inspect_program(), str(target)],
        text=True,
        timeout=120,
        env=_external_python_environment(),
        forward_stdout=False,
        forward_stderr=False,
    )
    if inspect.returncode != 0:
        raise RuntimeError(f"recovered SDF validation failed: {inspect.stderr.strip()}")
    report = json.loads(inspect.stdout)

    source_elements = [
        pdbqt_element(record["autodock_type"], record["name"])
        for record in source_records
    ]
    source_atoms = [
        (element, record["coord"])
        for element, record in zip(source_elements, source_records, strict=True)
    ]
    source_heavy = [atom for atom in source_atoms if atom[0] != "H"]
    sdf_atoms = [
        (atom["element"], tuple(atom["coord"])) for atom in report["atoms"]
    ]
    sdf_heavy = [atom for atom in sdf_atoms if atom[0] != "H"]
    if len(source_heavy) != len(sdf_heavy):
        raise RuntimeError(
            "ligand recovery changed the heavy-atom count: "
            f"{len(source_heavy)} != {len(sdf_heavy)}"
        )
    if sorted(element for element, _ in source_heavy) != sorted(
        element for element, _ in sdf_heavy
    ):
        raise RuntimeError("ligand recovery changed the heavy-atom element inventory")

    maximum_heavy_delta = _match_coordinate_inventory(source_heavy, sdf_heavy)
    maximum_serialized_delta = _match_coordinate_inventory(source_atoms, sdf_atoms)
    if maximum_serialized_delta > COORDINATE_TOLERANCE_ANGSTROM:
        raise RuntimeError(
            "ligand recovery changed serialized atom coordinates: "
            f"max_delta={maximum_serialized_delta:.6f} Å"
        )
    return {
        "converted": True,
        "source_format": "pdbqt",
        "target_format": "sdf",
        "source_atom_count": len(source_records),
        "source_heavy_atom_count": len(source_heavy),
        "sdf_atom_count": report["atom_count"],
        "sdf_heavy_atom_count": report["heavy_atom_count"],
        "formal_charge": report["formal_charge"],
        "canonical_isomeric_smiles": report["canonical_isomeric_smiles"],
        "max_heavy_atom_coordinate_delta_angstrom": maximum_heavy_delta,
        "max_serialized_atom_coordinate_delta_angstrom": maximum_serialized_delta,
        "serialized_atoms_coordinate_preserved": True,
        "chemistry_recovered_from_meeko_metadata": True,
        "reconstructed_hydrogen_count": report["atom_count"] - len(source_records),
        "lossless_scope": (
            "serialized atom coordinates plus Meeko-encoded bond orders, formal "
            "charges, and stereochemistry; missing pre-PDBQT hydrogen coordinates "
            "are chemically reconstructed"
        ),
    }


def export_ligand(
    source: Path, target: Path, *, meeko_python: Path, overwrite: bool = False
) -> dict[str, Any]:
    source = source.expanduser().resolve()
    target = target.expanduser().resolve()
    _validate_paths(source, target, overwrite)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
        report = convert_ligand_pdbqt_to_sdf(
            source, temporary_path, meeko_python=meeko_python
        )
        publish_staged_file(temporary_path, target, overwrite=overwrite)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    return {
        **{key: value for key, value in report.items() if key != "temporary"},
        "source": str(source),
        "output": str(target),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = export_ligand(
            args.input,
            args.output,
            meeko_python=args.meeko_python,
            overwrite=args.overwrite,
        )
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    write_tool_result([ToolArtifact(args.output, "导出的配体 SDF")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
