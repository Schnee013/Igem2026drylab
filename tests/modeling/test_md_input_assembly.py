"""Regression tests for generic ligand assembly and local input contracts."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "experiments/md-simulation/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import assemble_complex as assembly
import validate_md_run_contract as validator


def atom(resnum: int, resname: str, atomname: str, atomnum: int):
    return {
        "resnum": resnum,
        "resname": resname,
        "atomname": atomname,
        "atomnum": atomnum,
        "x": 0.01 * atomnum,
        "y": 0.02 * atomnum,
        "z": 0.03 * atomnum,
    }


def write_itp(path: Path, moltype: str, atom_names: list[str]) -> None:
    lines = [
        "[ moleculetype ]\n",
        f"{moltype} 3\n",
        "\n",
        "[ atoms ]\n",
    ]
    for index, name in enumerate(atom_names, 1):
        lines.append(
            f"{index} CT {1} {moltype} {name} {index} 0.0 12.0\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


class MdInputAssemblyTests(unittest.TestCase):
    def make_fixture(self, temporary: Path) -> dict[str, Path]:
        base = temporary / "base"
        toppar = base / "toppar"
        toppar.mkdir(parents=True)
        (toppar / "forcefield.itp").write_text("", encoding="utf-8")
        write_itp(toppar / "PROA.itp", "PROA", ["N"])
        write_itp(toppar / "POPC.itp", "POPC", ["C1", "C2"])
        write_itp(toppar / "POT.itp", "POT", ["POT"])
        write_itp(toppar / "CLA.itp", "CLA", ["CLA"])
        write_itp(toppar / "TIP3.itp", "TIP3", ["OH2", "H1", "H2"])
        base_topology = """#include "toppar/forcefield.itp"
#include "toppar/PROA.itp"
#include "toppar/POPC.itp"
#include "toppar/POT.itp"
#include "toppar/CLA.itp"
#include "toppar/TIP3.itp"

[ system ]
synthetic

[ molecules ]
PROA 1
POPC 2
POT 1
CLA 1
TIP3 2
"""
        (base / "topol.top").write_text(base_topology, encoding="utf-8")
        base_atoms = [
            atom(1, "ALA", "N", 1),
            atom(2, "POPC", "C1", 2),
            atom(2, "POPC", "C2", 3),
            atom(3, "POPC", "C1", 4),
            atom(3, "POPC", "C2", 5),
            atom(4, "POT", "POT", 6),
            atom(5, "CLA", "CLA", 7),
            atom(6, "TIP3", "OH2", 8),
            atom(6, "TIP3", "H1", 9),
            atom(6, "TIP3", "H2", 10),
            atom(7, "TIP3", "OH2", 11),
            atom(7, "TIP3", "H1", 12),
            atom(7, "TIP3", "H2", 13),
        ]
        assembly.write_gro(
            base / "step5_input.gro",
            "synthetic non-Gpr2 receptor membrane base",
            base_atoms,
            "5.00000 5.00000 5.00000\n",
        )

        ligand_gro = temporary / "ASCR3.gro"
        ligand_atoms = [
            atom(1, "ASCR3", "O1", 1),
            atom(1, "ASCR3", "C1", 2),
        ]
        assembly.write_gro(
            ligand_gro,
            "synthetic ASCR3",
            ligand_atoms,
            "0.00000 0.00000 0.00000\n",
        )
        ligand_itp = temporary / "ASCR3.itp"
        cgenff = temporary / "cgenff_ASCR3.itp"
        posre = temporary / "posre_ASCR3.itp"
        write_itp(ligand_itp, "ASCR3", ["O1", "C1"])
        cgenff.write_text("[ atomtypes ]\n", encoding="utf-8")
        posre.write_text("[ position_restraints ]\n", encoding="utf-8")
        return {
            "base": base,
            "ligand_gro": ligand_gro,
            "ligand_itp": ligand_itp,
            "cgenff": cgenff,
            "posre": posre,
        }

    def contract_and_review(
        self,
        temporary: Path,
        fixture: dict[str, Path],
        arm: str,
        remove: list[int],
    ) -> tuple[Path, Path, dict]:
        review = temporary / f"{arm}_review.tsv"
        if remove:
            rows = [
                (
                    arm,
                    resid,
                    "remove",
                    "ACCEPTED_FOR_TEST",
                    "synthetic reviewed overlap",
                )
                for resid in remove
            ]
        else:
            rows = [
                (
                    arm,
                    "NONE",
                    "retain_all",
                    "ACCEPTED_FOR_TEST",
                    "synthetic reviewed retain-all decision",
                )
            ]
        assembly.write_tsv(
            review,
            [
                "arm",
                "popc_resid",
                "proposed_action",
                "review_status",
                "review_note",
            ],
            rows,
        )
        popc_count = 2 - len(remove)
        membrane_atoms = popc_count * 2
        final_atom_count = 13 - len(remove) * 2 + 2
        group_counts = {
            "PROA": 1,
            "ASCR3": 2,
            "SOLU": 3,
            "MEMB": membrane_atoms,
            "SOLV": 8,
            "SOLU_MEMB": 3 + membrane_atoms,
            "SYSTEM": final_atom_count,
            "TIP3": 6,
        }
        contract = {
            "contract_id": f"synthetic-{arm}",
            "arm": arm,
            "ligand_moltype": "ASCR3",
            "ligand_atom_count": 2,
            "ligand_atom_names": ["O1", "C1"],
            "base_gro_sha256": assembly.sha256(
                fixture["base"] / "step5_input.gro"
            ),
            "base_topology_sha256": assembly.sha256(
                fixture["base"] / "topol.top"
            ),
            "ligand_gro_sha256": assembly.sha256(fixture["ligand_gro"]),
            "expected_base_molecule_counts": {
                "PROA": 1,
                "POPC": 2,
                "POT": 1,
                "CLA": 1,
                "TIP3": 2,
            },
            "expected_remove_popc_resids": remove,
            "expected_final_molecule_counts": {
                "PROA": 1,
                "ASCR3": 1,
                "POPC": popc_count,
                "POT": 1,
                "CLA": 1,
                "TIP3": 2,
            },
            "expected_final_atom_count": final_atom_count,
            "required_index_groups": list(group_counts),
            "expected_index_group_counts": group_counts,
        }
        contract_path = temporary / f"{arm}_contract.json"
        contract_path.write_text(
            json.dumps(contract, indent=2) + "\n", encoding="utf-8"
        )
        return contract_path, review, contract

    def run_assembly(
        self,
        fixture: dict[str, Path],
        output: Path,
        contract: Path,
        review: Path,
    ) -> None:
        assembly.assemble(
            work_dir=fixture["base"],
            output_dir=output,
            ligand_gro=fixture["ligand_gro"],
            ligand_moltype="ASCR3",
            ligand_itp=fixture["ligand_itp"],
            cgenff_itp=fixture["cgenff"],
            posre_itp=fixture["posre"],
            remove_popc_from=review,
            expected_contract=contract,
        )

    def test_variable_width_index_handles_more_than_99999_atoms(self) -> None:
        atoms = [atom(index, "TIP3", "OH2", index) for index in range(1, 100002)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.ndx"
            groups = {"SYSTEM": list(range(1, len(atoms) + 1))}
            assembly.write_index(groups, path)
            parsed = validator.parse_index(path)
        self.assertEqual(parsed["SYSTEM"][-2:], [100000, 100001])

    def test_ascr3_includes_molecule_entry_and_non_gpr2_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            fixture = self.make_fixture(temporary)
            contract_path, review, contract = self.contract_and_review(
                temporary, fixture, "wt", [2]
            )
            output = temporary / "wt_output"
            self.run_assembly(fixture, output, contract_path, review)

            topology = (output / "topol.top").read_text(encoding="utf-8")
            self.assertEqual(topology.count('#include "ASCR3.itp"'), 1)
            self.assertEqual(topology.count('#include "toppar/cgenff_ASCR3.itp"'), 1)
            self.assertEqual(topology.count('#include "posre_ASCR3.itp"'), 1)
            self.assertIn("ASCR3", dict(assembly.parse_topology_molecules(output / "topol.top")))
            self.assertEqual(
                len(assembly.parse_gro(output / "step5_complex.gro")[1]),
                contract["expected_final_atom_count"],
            )

    def test_duplicate_include_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "topol.top"
            path.write_text(
                '#include "toppar/forcefield.itp"\n'
                '#include "toppar/PROA.itp"\n'
                '#include "ASCR3.itp"\n'
                "[ molecules ]\nPROA 1\nPOPC 1\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate ligand include"):
                assembly.modify_topology(
                    path,
                    ligand_moltype="ASCR3",
                    ligand_include="ASCR3.itp",
                    cgenff_include="toppar/cgenff_ASCR3.itp",
                    posre_include="posre_ASCR3.itp",
                    popc_removed=0,
                )

    def test_empty_required_group_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            atoms = [atom(1, "ALA", "N", 1), atom(2, "ASCR3", "O1", 2)]
            with self.assertRaisesRegex(ValueError, "required index groups are empty"):
                assembly.build_index(
                    atoms,
                    Path(directory) / "index.ndx",
                    ligand_moltype="ASCR3",
                    required_groups=["PROA", "ASCR3", "MEMB"],
                )

    def test_overwrite_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            fixture = self.make_fixture(temporary)
            contract, review, _ = self.contract_and_review(
                temporary, fixture, "wt", [2]
            )
            output = temporary / "already_exists"
            output.mkdir()
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                self.run_assembly(fixture, output, contract, review)

    def test_pair_specific_wt_and_r167y_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            for arm, remove in (("wt", [2]), ("r167y", [])):
                with self.subTest(arm=arm):
                    arm_root = temporary / arm
                    arm_root.mkdir()
                    fixture = self.make_fixture(arm_root)
                    contract_path, review, contract = self.contract_and_review(
                        arm_root, fixture, arm, remove
                    )
                    output = arm_root / "output"
                    self.run_assembly(
                        fixture, output, contract_path, review
                    )
                    final_counts = dict(
                        assembly.parse_topology_molecules(output / "topol.top")
                    )
                    self.assertEqual(
                        final_counts,
                        contract["expected_final_molecule_counts"],
                    )

    def test_input_validator_accepts_assembled_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            fixture = self.make_fixture(temporary)
            assembly_contract, review, expected = self.contract_and_review(
                temporary, fixture, "wt", [2]
            )
            output = temporary / "package"
            self.run_assembly(
                fixture, output, assembly_contract, review
            )
            files = {
                "coordinate": str(output / "step5_complex.gro"),
                "topology": str(output / "topol.top"),
                "index": str(output / "index.ndx"),
                "ligand_itp": str(output / "ASCR3.itp"),
            }
            input_contract = {
                "contract_id": "synthetic-input-wt",
                "arm": "wt",
                "gate": "input",
                "files": files,
                "expected": {
                    "coordinate_atom_count": expected["expected_final_atom_count"],
                    "molecule_counts": expected["expected_final_molecule_counts"],
                    "ligand_moltype": "ASCR3",
                    "ligand_atom_count": 2,
                    "ligand_atom_names": ["O1", "C1"],
                    "required_index_groups": expected["required_index_groups"],
                    "index_group_counts": expected["expected_index_group_counts"],
                    "checksums": {
                        name: assembly.sha256(Path(path))
                        for name, path in files.items()
                    },
                },
            }
            contract_path = temporary / "input_contract.json"
            contract_path.write_text(
                json.dumps(input_contract, indent=2) + "\n",
                encoding="utf-8",
            )
            validation = temporary / "validation"
            validation.mkdir()
            validator.validate_input(contract_path, input_contract, validation)
            summary = (validation / "input_summary.tsv").read_text(
                encoding="utf-8"
            )
            self.assertTrue(all(line.endswith("\tPASS") for line in summary.splitlines()[1:]))

    def test_genion_appended_ion_block_keeps_coordinate_order_and_aggregates(self) -> None:
        topology_rows = [("POT", 1), ("TIP3", 1), ("POT", 1)]
        atoms = [
            atom(1, "POT", "POT", 1),
            atom(2, "TIP3", "OH2", 2),
            atom(2, "TIP3", "H1", 3),
            atom(2, "TIP3", "H2", 4),
            atom(3, "POT", "POT", 5),
        ]
        counts = assembly.topology_molecule_counts(topology_rows)
        self.assertEqual(counts, {"POT": 2, "TIP3": 1})
        audit = validator.validate_coordinate_blocks(
            atoms,
            topology_rows,
            {"POT": ["POT"], "TIP3": ["OH2", "H1", "H2"]},
        )
        self.assertEqual([row[0] for row in audit], ["POT", "TIP3", "POT"])

    def test_warning_inventory_normalizes_blocks(self) -> None:
        text = """WARNING 1 [file topol.top, line 10]:
  first warning body

WARNING 2 [file ASCR3.itp, line 20]:
  second warning
  continued

"""
        warnings = validator.normalize_warning_blocks(text)
        self.assertEqual(len(warnings), 2)
        self.assertEqual(warnings[1]["normalized_text"], "second warning continued")
        self.assertNotEqual(
            warnings[0]["fingerprint_sha256"],
            warnings[1]["fingerprint_sha256"],
        )

    def make_geometry_fixture(
        self,
        temporary: Path,
        *,
        second_x: float,
        bondtype: str = "CTL2 CTL2 1 0.153 186188",
        inline_b0: str = "",
    ) -> tuple[Path, dict]:
        toppar = temporary / "toppar"
        toppar.mkdir()
        forcefield = toppar / "forcefield.itp"
        forcefield.write_text(
            "[ bondtypes ]\n"
            "; i j funct b0 kb\n"
            f"{bondtype}\n",
            encoding="utf-8",
        )
        popc = toppar / "POPC.itp"
        popc.write_text(
            "[ moleculetype ]\n"
            "POPC 3\n"
            "[ atoms ]\n"
            "1 CTL2 1 POPC C1 1 0.0 12.011\n"
            "2 CTL2 1 POPC C2 2 0.0 12.011\n"
            "[ bonds ]\n"
            f"1 2 1{inline_b0}\n",
            encoding="utf-8",
        )
        topology = temporary / "topol.top"
        topology.write_text(
            '#include "toppar/forcefield.itp"\n'
            '#include "toppar/POPC.itp"\n'
            "[ system ]\n"
            "geometry fixture\n"
            "[ molecules ]\n"
            "POPC 1\n",
            encoding="utf-8",
        )
        coordinate = temporary / "coordinate.gro"
        atoms = [
            {
                "resnum": 1,
                "resname": "POPC",
                "atomname": "C1",
                "atomnum": 1,
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
            },
            {
                "resnum": 1,
                "resname": "POPC",
                "atomname": "C2",
                "atomnum": 2,
                "x": second_x,
                "y": 0.0,
                "z": 0.0,
            },
        ]
        assembly.write_gro(
            coordinate,
            "geometry fixture",
            atoms,
            "1.00000 1.00000 1.00000\n",
        )
        contract = {
            "contract_id": "synthetic-geometry",
            "arm": "synthetic",
            "gate": "geometry",
            "files": {
                "coordinate": str(coordinate),
                "topology": str(topology),
                "molecule_itp": str(popc),
                "forcefield_itp": str(forcefield),
            },
            "expected": {
                "coordinate_atom_count": 2,
                "molecule_type": "POPC",
                "molecule_count": 1,
                "bond_deviation_threshold_nm": 0.025,
                "max_outlier_bonds": 0,
                "max_abs_bond_deviation_nm": 0.025,
                "criterion_label": "OPERATIONAL_DIAGNOSTIC_TEST",
                "checksums": {
                    "topology": assembly.sha256(topology),
                    "molecule_itp": assembly.sha256(popc),
                    "forcefield_itp": assembly.sha256(forcefield),
                },
            },
        }
        contract_path = temporary / "geometry_contract.json"
        contract_path.write_text(
            json.dumps(contract, indent=2) + "\n",
            encoding="utf-8",
        )
        return contract_path, contract

    def test_geometry_gate_refuses_malformed_popc_bond(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            contract_path, contract = self.make_geometry_fixture(
                temporary,
                second_x=0.400,
            )
            output = temporary / "geometry_fail"
            output.mkdir()
            with self.assertRaisesRegex(ValueError, "outlier bonds 1 > 0"):
                validator.validate_geometry(
                    contract_path,
                    contract,
                    output,
                )
            outliers = (output / "geometry_bond_outliers.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn("C1\tC2", outliers)
            self.assertIn("0.247000", outliers)

    def test_geometry_gate_accepts_repair_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            contract_path, contract = self.make_geometry_fixture(
                temporary,
                second_x=0.154,
            )
            output = temporary / "geometry_pass"
            output.mkdir()
            validator.validate_geometry(contract_path, contract, output)
            status = (output / "terminal_status.tsv").read_text(encoding="utf-8")
            self.assertIn("geometry\tPASS", status)
            summary = (output / "geometry_summary.tsv").read_text(encoding="utf-8")
            self.assertIn("outlier_bonds\t0", summary)

    def test_geometry_gate_uses_minimum_image_distance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            contract_path, contract = self.make_geometry_fixture(
                temporary,
                second_x=0.990,
                bondtype="CTL2 CTL2 1 0.010 186188",
            )
            output = temporary / "geometry_pbc"
            output.mkdir()
            validator.validate_geometry(contract_path, contract, output)
            summary = (output / "geometry_summary.tsv").read_text(encoding="utf-8")
            self.assertIn("maximum_abs_bond_deviation_nm\t0.000000", summary)

    def test_geometry_gate_prefers_inline_equilibrium_length(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            contract_path, contract = self.make_geometry_fixture(
                temporary,
                second_x=0.200,
                inline_b0=" 0.200 186188",
            )
            output = temporary / "geometry_inline"
            output.mkdir()
            validator.validate_geometry(contract_path, contract, output)
            summary = (output / "geometry_summary.tsv").read_text(encoding="utf-8")
            self.assertIn("maximum_abs_bond_deviation_nm\t0.000000", summary)


if __name__ == "__main__":
    unittest.main()
