#!/usr/bin/env python3
"""Assemble a reviewed ligand into a receptor/membrane GROMACS package.

The source package is never edited.  A new output directory is copied from the
source package, the reviewed ligand and topology inputs are installed there,
and the final coordinate/topology/index audits are written beside the package.

The assembly contract carries every system-specific expected value.  This
module intentionally has no ASCR18, Gpr2, POPC-residue, atom-count, ion-count,
or water-count defaults.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


PROTEIN_RESNAMES = {
    "ALA",
    "ARG",
    "ASN",
    "ASP",
    "CYS",
    "GLN",
    "GLU",
    "GLY",
    "HIS",
    "HSD",
    "HSE",
    "HSP",
    "HID",
    "HIE",
    "HIP",
    "ILE",
    "LEU",
    "LYS",
    "MET",
    "PHE",
    "PRO",
    "SER",
    "THR",
    "TRP",
    "TYR",
    "VAL",
}

REQUIRED_CONTRACT_FIELDS = {
    "contract_id",
    "arm",
    "ligand_moltype",
    "ligand_atom_count",
    "ligand_atom_names",
    "base_gro_sha256",
    "base_topology_sha256",
    "ligand_gro_sha256",
    "expected_base_molecule_counts",
    "expected_remove_popc_resids",
    "expected_final_molecule_counts",
    "expected_final_atom_count",
    "required_index_groups",
    "expected_index_group_counts",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_tsv(path: Path, header: Iterable[str], rows: Iterable[Iterable[Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def parse_gro(path: Path) -> tuple[str, list[dict[str, Any]], str]:
    """Parse a position-only GRO file with strict atom-count checks."""
    with path.open(encoding="utf-8") as handle:
        title = handle.readline().rstrip("\n")
        count_line = handle.readline()
        if not count_line:
            raise ValueError(f"missing atom-count line: {path}")
        atom_count = int(count_line.strip())
        atoms: list[dict[str, Any]] = []
        for index in range(atom_count):
            line = handle.readline()
            if len(line) < 44:
                raise ValueError(f"short GRO atom line {index + 1}: {path}")
            atoms.append(
                {
                    "resnum": int(line[0:5]),
                    "resname": line[5:10].strip(),
                    "atomname": line[10:15].strip(),
                    "atomnum": int(line[15:20]),
                    "x": float(line[20:28]),
                    "y": float(line[28:36]),
                    "z": float(line[36:44]),
                }
            )
        box_line = handle.readline()
        if not box_line.strip():
            raise ValueError(f"missing GRO box line: {path}")
        trailing = [line for line in handle if line.strip()]
        if trailing:
            raise ValueError(f"unexpected non-empty trailing GRO lines: {path}")
    return title, atoms, box_line


def write_gro(
    path: Path,
    title: str,
    atoms: list[dict[str, Any]],
    box_line: str,
) -> None:
    """Write GRO atom numbers with GROMACS' five-column modulo convention."""
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"{title}\n")
        handle.write(f"{len(atoms):5d}\n")
        for index, atom in enumerate(atoms, 1):
            atom_number = index % 100000
            handle.write(
                f"{atom['resnum'] % 100000:5d}{atom['resname']:<5.5s}"
                f"{atom['atomname']:>5.5s}{atom_number:5d}"
                f"{atom['x']:8.3f}{atom['y']:8.3f}{atom['z']:8.3f}\n"
            )
        handle.write(box_line if box_line.endswith("\n") else f"{box_line}\n")


def parse_itp_atoms(path: Path, expected_moltype: str | None = None) -> list[str]:
    """Return atom names from one ITP and optionally verify its moleculetype."""
    section = ""
    moltype: str | None = None
    atoms: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r"\[\s*([^\]]+?)\s*\]", line)
        if match:
            section = match.group(1).strip().lower()
            continue
        if line.startswith("#"):
            continue
        fields = line.split()
        if section == "moleculetype" and moltype is None:
            moltype = fields[0]
        elif section == "atoms":
            if len(fields) < 5:
                raise ValueError(f"malformed [ atoms ] row in {path}: {raw}")
            atoms.append(fields[4])
    if expected_moltype is not None and moltype != expected_moltype:
        raise ValueError(
            f"ligand moleculetype mismatch: expected {expected_moltype}, found {moltype}"
        )
    if not atoms:
        raise ValueError(f"no [ atoms ] entries in {path}")
    return atoms


def parse_topology_molecules(path: Path) -> list[tuple[str, int]]:
    section = ""
    rows: list[tuple[str, int]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r"\[\s*([^\]]+?)\s*\]", line)
        if match:
            section = match.group(1).strip().lower()
            continue
        if line.startswith("#"):
            continue
        if section == "molecules":
            fields = line.split()
            if len(fields) != 2:
                raise ValueError(f"malformed [ molecules ] row in {path}: {raw}")
            rows.append((fields[0], int(fields[1])))
    if not rows:
        raise ValueError(f"no [ molecules ] entries in {path}")
    return rows


def topology_molecule_counts(rows: Iterable[tuple[str, int]]) -> Counter[str]:
    """Aggregate molecule counts while preserving rows for coordinate-order checks."""
    counts: Counter[str] = Counter()
    for name, count in rows:
        counts[name] += count
    return counts


def topology_includes(path: Path) -> list[str]:
    includes = []
    pattern = re.compile(r'^\s*#include\s+"([^"]+)"')
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            includes.append(match.group(1))
    return includes


def coordinate_molecule_counts(atoms: list[dict[str, Any]]) -> Counter[str]:
    """Count molecules from contiguous residue blocks plus one protein chain."""
    counts: Counter[str] = Counter()
    protein_seen = False
    prior: tuple[int, str] | None = None
    for atom in atoms:
        key = (atom["resnum"], atom["resname"])
        if key == prior:
            continue
        prior = key
        if atom["resname"] in PROTEIN_RESNAMES:
            if not protein_seen:
                counts["PROA"] += 1
                protein_seen = True
        else:
            counts[atom["resname"]] += 1
    return counts


def write_index(groups: dict[str, list[int]], path: Path) -> None:
    """Write variable-width, whitespace-separated GROMACS index values."""
    with path.open("w", encoding="utf-8") as handle:
        for name, values in groups.items():
            handle.write(f"[ {name} ]\n")
            for offset in range(0, len(values), 15):
                handle.write(" ".join(str(value) for value in values[offset : offset + 15]))
                handle.write("\n")
            handle.write("\n")


def build_index(
    atoms: list[dict[str, Any]],
    path: Path,
    *,
    ligand_moltype: str,
    required_groups: Iterable[str],
) -> dict[str, list[int]]:
    protein: list[int] = []
    ligand: list[int] = []
    membrane: list[int] = []
    solvent: list[int] = []
    tip3: list[int] = []
    solvent_names = {"POT", "CLA", "TIP3", "SOL", "NA", "K"}

    for atom_index, atom in enumerate(atoms, 1):
        residue = atom["resname"]
        if residue in PROTEIN_RESNAMES:
            protein.append(atom_index)
        elif residue == ligand_moltype:
            ligand.append(atom_index)
        elif residue == "POPC":
            membrane.append(atom_index)
        elif residue in solvent_names:
            solvent.append(atom_index)
        else:
            raise ValueError(f"unclassified residue in final coordinate: {residue}")
        if residue in {"TIP3", "SOL"}:
            tip3.append(atom_index)

    groups = {
        "PROA": protein,
        ligand_moltype: ligand,
        "SOLU": protein + ligand,
        "MEMB": membrane,
        "SOLV": solvent,
        "SOLU_MEMB": protein + ligand + membrane,
        "SYSTEM": list(range(1, len(atoms) + 1)),
        "TIP3": tip3,
    }
    missing = [name for name in required_groups if name not in groups]
    if missing:
        raise ValueError(f"required index group definitions missing: {missing}")
    empty = [name for name in required_groups if not groups[name]]
    if empty:
        raise ValueError(f"required index groups are empty: {empty}")
    write_index(groups, path)
    return groups


def load_contract(path: Path) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - set(contract))
    if missing:
        raise ValueError(f"expected-contract missing fields: {missing}")
    if not isinstance(contract["ligand_atom_names"], list):
        raise ValueError("ligand_atom_names must be a list")
    return contract


def load_reviewed_popc(path: Path, arm: str) -> list[int]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {
            "arm",
            "popc_resid",
            "proposed_action",
            "review_status",
            "review_note",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"reviewed POPC TSV missing columns: {sorted(required)}")
        rows = list(reader)
    if not rows:
        raise ValueError("reviewed POPC TSV is empty")
    remove: list[int] = []
    accepted_rows = 0
    for row in rows:
        if row["arm"] != arm:
            raise ValueError(f"POPC review arm mismatch: {row['arm']} != {arm}")
        if not row["review_status"].startswith("ACCEPTED"):
            raise ValueError(f"POPC decision is not reviewed: {row}")
        accepted_rows += 1
        if row["proposed_action"] == "remove":
            remove.append(int(row["popc_resid"]))
        elif row["proposed_action"] not in {"retain", "retain_all"}:
            raise ValueError(f"unknown POPC action: {row['proposed_action']}")
    if accepted_rows == 0:
        raise ValueError("reviewed POPC TSV contains no accepted rows")
    if len(remove) != len(set(remove)):
        raise ValueError("duplicate POPC residue in reviewed removal list")
    return sorted(remove)


def modify_topology(
    path: Path,
    *,
    ligand_moltype: str,
    ligand_include: str,
    cgenff_include: str,
    posre_include: str,
    popc_removed: int,
) -> None:
    includes = topology_includes(path)
    duplicates = sorted({value for value in includes if includes.count(value) > 1})
    if duplicates:
        raise ValueError(f"source topology already has duplicate includes: {duplicates}")
    requested = [ligand_include, cgenff_include, posre_include]
    preexisting = [value for value in requested if value in includes]
    if preexisting:
        raise ValueError(f"refusing duplicate ligand include insertion: {preexisting}")

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    forcefield_anchor = sum(
        '#include "toppar/forcefield.itp"' in line for line in lines
    )
    protein_anchor = sum('#include "toppar/PROA.itp"' in line for line in lines)
    if forcefield_anchor != 1 or protein_anchor != 1:
        raise ValueError(
            "topology include anchors are not unique: "
            f"forcefield={forcefield_anchor}, PROA={protein_anchor}"
        )

    output: list[str] = []
    in_molecules = False
    ligand_written = False
    popc_written = False
    for raw in lines:
        stripped = raw.strip()
        output.append(raw)
        if stripped == '#include "toppar/forcefield.itp"':
            output.append(f'#include "{cgenff_include}"\n')
        elif stripped == '#include "toppar/PROA.itp"':
            output.append(f'#include "{ligand_include}"\n')
            output.append("#ifdef POSRES\n")
            output.append(f'#include "{posre_include}"\n')
            output.append("#endif\n")

        if stripped == "[ molecules ]":
            in_molecules = True
            continue
        if in_molecules and stripped and not stripped.startswith((";", "#", "[")):
            fields = stripped.split()
            if len(fields) == 2 and fields[0] == "PROA" and not ligand_written:
                output.append(f"{ligand_moltype:<8s}\t{1:12d}\n")
                ligand_written = True
            elif len(fields) == 2 and fields[0] == "POPC":
                old_count = int(fields[1])
                new_count = old_count - popc_removed
                if new_count < 0:
                    raise ValueError("reviewed POPC removal exceeds topology count")
                output[-1] = f"{'POPC':<8s}\t{new_count:12d}\n"
                popc_written = True

    if not ligand_written or not popc_written:
        raise ValueError(
            f"failed to update [ molecules ]: ligand={ligand_written}, POPC={popc_written}"
        )
    path.write_text("".join(output), encoding="utf-8")


def contract_counter(value: dict[str, Any]) -> Counter[str]:
    return Counter({str(key): int(count) for key, count in value.items()})


def assemble(
    *,
    work_dir: Path,
    output_dir: Path,
    ligand_gro: Path,
    ligand_moltype: str,
    ligand_itp: Path,
    cgenff_itp: Path,
    posre_itp: Path,
    remove_popc_from: Path,
    expected_contract: Path,
) -> None:
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite output directory: {output_dir}")
    required_inputs = [
        work_dir / "step5_input.gro",
        work_dir / "topol.top",
        ligand_gro,
        ligand_itp,
        cgenff_itp,
        posre_itp,
        remove_popc_from,
        expected_contract,
    ]
    missing = [str(path) for path in required_inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"required assembly inputs missing: {missing}")

    contract = load_contract(expected_contract)
    if contract["ligand_moltype"] != ligand_moltype:
        raise ValueError("CLI ligand moltype does not match expected-contract")
    if sha256(work_dir / "step5_input.gro") != contract["base_gro_sha256"]:
        raise ValueError("base GRO checksum does not match expected-contract")
    if sha256(work_dir / "topol.top") != contract["base_topology_sha256"]:
        raise ValueError("base topology checksum does not match expected-contract")
    if sha256(ligand_gro) != contract["ligand_gro_sha256"]:
        raise ValueError("ligand GRO checksum does not match expected-contract")

    _, ligand_atoms, _ = parse_gro(ligand_gro)
    ligand_names = [atom["atomname"] for atom in ligand_atoms]
    itp_names = parse_itp_atoms(ligand_itp, expected_moltype=ligand_moltype)
    if len(ligand_atoms) != int(contract["ligand_atom_count"]):
        raise ValueError("ligand GRO atom count does not match expected-contract")
    if ligand_names != itp_names or ligand_names != contract["ligand_atom_names"]:
        raise ValueError("ligand GRO/ITP/expected-contract atom order mismatch")
    if any(atom["resname"] != ligand_moltype for atom in ligand_atoms):
        raise ValueError("ligand GRO residue name does not match ligand moltype")

    title, base_atoms, box_line = parse_gro(work_dir / "step5_input.gro")
    base_topology_counts = topology_molecule_counts(
        parse_topology_molecules(work_dir / "topol.top")
    )
    expected_base_counts = contract_counter(contract["expected_base_molecule_counts"])
    if base_topology_counts != expected_base_counts:
        raise ValueError(
            f"base topology molecule counts mismatch: {base_topology_counts} "
            f"!= {expected_base_counts}"
        )
    base_coordinate_counts = coordinate_molecule_counts(base_atoms)
    if base_coordinate_counts != expected_base_counts:
        raise ValueError(
            f"base coordinate molecule counts mismatch: {base_coordinate_counts} "
            f"!= {expected_base_counts}"
        )

    remove_popc = load_reviewed_popc(remove_popc_from, contract["arm"])
    if remove_popc != sorted(int(value) for value in contract["expected_remove_popc_resids"]):
        raise ValueError("reviewed POPC removal list does not match expected-contract")

    popc_atoms_by_resid: Counter[int] = Counter(
        atom["resnum"] for atom in base_atoms if atom["resname"] == "POPC"
    )
    absent = [resid for resid in remove_popc if resid not in popc_atoms_by_resid]
    if absent:
        raise ValueError(f"reviewed POPC residues absent from base coordinate: {absent}")
    retained_atoms = [
        atom
        for atom in base_atoms
        if not (atom["resname"] == "POPC" and atom["resnum"] in set(remove_popc))
    ]

    protein_end = 0
    for index, atom in enumerate(retained_atoms):
        if atom["resname"] in PROTEIN_RESNAMES:
            protein_end = index + 1
    if protein_end == 0:
        raise ValueError("no protein atoms found in base coordinate")
    ligand_resnum = retained_atoms[protein_end - 1]["resnum"] + 1
    ligand_copy = [dict(atom, resnum=ligand_resnum) for atom in ligand_atoms]
    assembled = retained_atoms[:protein_end] + ligand_copy + retained_atoms[protein_end:]

    expected_atom_count = int(contract["expected_final_atom_count"])
    if len(assembled) != expected_atom_count:
        raise ValueError(
            f"final atom count mismatch: {len(assembled)} != {expected_atom_count}"
        )
    final_counts = coordinate_molecule_counts(assembled)
    expected_final_counts = contract_counter(contract["expected_final_molecule_counts"])
    if final_counts != expected_final_counts:
        raise ValueError(
            f"final coordinate molecule counts mismatch: {final_counts} "
            f"!= {expected_final_counts}"
        )

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(work_dir, output_dir)
    final_gro = output_dir / "step5_complex.gro"
    final_topology = output_dir / "topol.top"
    final_index = output_dir / "index.ndx"
    ligand_destination = output_dir / ligand_itp.name
    cgenff_destination = output_dir / "toppar" / cgenff_itp.name
    posre_destination = output_dir / posre_itp.name
    for source, destination in (
        (ligand_itp, ligand_destination),
        (cgenff_itp, cgenff_destination),
        (posre_itp, posre_destination),
    ):
        if destination.exists():
            raise FileExistsError(f"refusing to overwrite package include: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    write_gro(
        final_gro,
        f"{title} + {ligand_moltype} ({contract['arm']})",
        assembled,
        box_line,
    )
    modify_topology(
        final_topology,
        ligand_moltype=ligand_moltype,
        ligand_include=ligand_destination.name,
        cgenff_include=f"toppar/{cgenff_destination.name}",
        posre_include=posre_destination.name,
        popc_removed=len(remove_popc),
    )
    topology_counts = topology_molecule_counts(parse_topology_molecules(final_topology))
    if topology_counts != expected_final_counts:
        raise ValueError(
            f"final topology molecule counts mismatch: {topology_counts} "
            f"!= {expected_final_counts}"
        )

    required_groups = [str(value) for value in contract["required_index_groups"]]
    groups = build_index(
        assembled,
        final_index,
        ligand_moltype=ligand_moltype,
        required_groups=required_groups,
    )
    actual_group_counts = {name: len(values) for name, values in groups.items()}
    expected_group_counts = {
        str(name): int(count)
        for name, count in contract["expected_index_group_counts"].items()
    }
    if actual_group_counts != expected_group_counts:
        raise ValueError(
            f"index group counts mismatch: {actual_group_counts} "
            f"!= {expected_group_counts}"
        )

    includes = topology_includes(final_topology)
    duplicate_includes = sorted(
        {include for include in includes if includes.count(include) > 1}
    )
    if duplicate_includes:
        raise ValueError(f"final topology duplicate includes: {duplicate_includes}")

    write_tsv(
        output_dir / "molecule_count_audit.tsv",
        ["molecule", "coordinate_count", "topology_count", "expected_count", "status"],
        [
            (
                molecule,
                final_counts[molecule],
                topology_counts[molecule],
                expected_final_counts[molecule],
                "PASS"
                if final_counts[molecule]
                == topology_counts[molecule]
                == expected_final_counts[molecule]
                else "FAIL",
            )
            for molecule in expected_final_counts
        ],
    )
    write_tsv(
        output_dir / "index_group_counts.tsv",
        ["group", "actual_count", "expected_count", "status"],
        [
            (
                name,
                actual_group_counts[name],
                expected_group_counts[name],
                "PASS"
                if actual_group_counts[name] == expected_group_counts[name]
                else "FAIL",
            )
            for name in actual_group_counts
        ],
    )
    write_tsv(
        output_dir / "include_audit.tsv",
        ["include", "count", "status"],
        [(include, includes.count(include), "PASS") for include in includes],
    )
    manifest_rows = []
    for path, role in (
        (final_gro, "final_coordinate"),
        (final_topology, "final_topology"),
        (final_index, "package_local_index"),
        (ligand_destination, "ligand_itp"),
        (cgenff_destination, "cgenff_itp"),
        (posre_destination, "ligand_posre_itp"),
        (expected_contract, "expected_contract"),
        (remove_popc_from, "reviewed_popc_decision"),
    ):
        manifest_rows.append((role, str(path), path.stat().st_size, sha256(path)))
    write_tsv(
        output_dir / "assembly_manifest.tsv",
        ["role", "path", "bytes", "sha256"],
        manifest_rows,
    )
    write_tsv(
        output_dir / "terminal_status.tsv",
        ["gate", "status", "detail"],
        [
            ("assembly", "PASS", contract["contract_id"]),
            ("final_coordinate", "PASS", str(final_gro)),
            ("topology_molecules", "PASS", json.dumps(dict(final_counts), sort_keys=True)),
            ("package_local_index", "PASS", json.dumps(actual_group_counts, sort_keys=True)),
        ],
    )


def rebuild_index(
    gro_path: Path,
    *,
    ligand_moltype: str,
    output_path: Path | None = None,
) -> None:
    _, atoms, _ = parse_gro(gro_path)
    destination = output_path or gro_path.with_name("index.ndx")
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite index: {destination}")
    build_index(
        atoms,
        destination,
        ligand_moltype=ligand_moltype,
        required_groups=[
            "PROA",
            ligand_moltype,
            "SOLU",
            "MEMB",
            "SOLV",
            "SOLU_MEMB",
            "SYSTEM",
            "TIP3",
        ],
    )


def apply_config(args: argparse.Namespace) -> argparse.Namespace:
    if args.config is None:
        return args
    config = json.loads(args.config.read_text(encoding="utf-8"))
    allowed = {
        "work_dir",
        "output_dir",
        "ligand_gro",
        "ligand_moltype",
        "ligand_itp",
        "cgenff_itp",
        "posre_itp",
        "remove_popc_from",
        "expected_contract",
    }
    unknown = sorted(set(config) - allowed)
    if unknown:
        raise ValueError(f"unknown assembly config fields: {unknown}")
    for key, value in config.items():
        if getattr(args, key) is not None:
            raise ValueError(f"{key} provided by both --config and CLI")
        setattr(args, key, Path(value) if key != "ligand_moltype" else value)
    return args


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--ligand-gro", type=Path)
    parser.add_argument("--ligand-moltype")
    parser.add_argument("--ligand-itp", type=Path)
    parser.add_argument("--cgenff-itp", type=Path)
    parser.add_argument("--posre-itp", type=Path)
    parser.add_argument("--remove-popc-from", type=Path)
    parser.add_argument("--expected-contract", type=Path)
    parser.add_argument("--rebuild-index", type=Path)
    parser.add_argument("--index-output", type=Path)
    args = apply_config(parser.parse_args())

    if args.rebuild_index is not None:
        if not args.ligand_moltype:
            parser.error("--rebuild-index requires --ligand-moltype")
        rebuild_index(
            args.rebuild_index,
            ligand_moltype=args.ligand_moltype,
            output_path=args.index_output,
        )
        return

    required = (
        "work_dir",
        "output_dir",
        "ligand_gro",
        "ligand_moltype",
        "ligand_itp",
        "cgenff_itp",
        "posre_itp",
        "remove_popc_from",
        "expected_contract",
    )
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        parser.error(f"missing required assembly arguments: {missing}")
    try:
        assemble(
            work_dir=args.work_dir,
            output_dir=args.output_dir,
            ligand_gro=args.ligand_gro,
            ligand_moltype=args.ligand_moltype,
            ligand_itp=args.ligand_itp,
            cgenff_itp=args.cgenff_itp,
            posre_itp=args.posre_itp,
            remove_popc_from=args.remove_popc_from,
            expected_contract=args.expected_contract,
        )
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
