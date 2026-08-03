"""Focused local tests for the docking multi-mutant Phase 2 contract."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "src/modeling/docking-repro"
sys.path.insert(0, str(MODULE_DIR))

from multi_mutant import (  # noqa: E402
    CycleValidationError,
    MutationValidationError,
    apply_mutations,
    build_genotype_fasta,
    canonicalize_mutations,
    compute_cycle_contrasts,
    join_cycle_results,
    make_genotype_id,
    normalize_genotype,
    validate_cycle,
    write_genotype_fasta,
)


WT_SEQUENCE = "ACDEFGHIKLMNPQRSTVWY"
MUT_A = {"position": 2, "wt": "C", "mut": "V"}
MUT_B = {"position": 8, "wt": "I", "mut": "A"}


def synthetic_cycle() -> dict:
    contract = {
        "receptor": "SyntheticR",
        "parent": "parent-01",
        "ligands": ["target", "offtarget"],
        "grid": {"center": [1.0, 2.0, 3.0], "size": [40.0, 40.0, 40.0]},
        "seeds": [11, 22],
        "conformers": ["conf-1", "conf-2"],
    }
    return {
        "cycle_id": "synthetic-cycle-01",
        "allowed_use": "schema_and_test_only",
        "genotypes": {
            "WT": {**contract, "mutations": []},
            "A": {**contract, "mutations": [MUT_A]},
            "B": {**contract, "mutations": [MUT_B]},
            "AB": {**contract, "mutations": [MUT_B, MUT_A]},
        },
    }


def synthetic_results(cycle: dict) -> list[dict]:
    normalized = validate_cycle(cycle)
    rows = []
    for role, arm in normalized["genotypes"].items():
        for ligand_index, ligand in enumerate(arm["ligands"]):
            for conformer_index, conformer in enumerate(arm["conformers"]):
                for seed_index, seed in enumerate(arm["seeds"]):
                    rows.append(
                        {
                            "receptor": arm["receptor"],
                            "genotype_id": arm["genotype_id"],
                            "mutations": copy.deepcopy(arm["mutations"]),
                            "label": f"do-not-parse-{role}",
                            "parent": arm["parent"],
                            "ligand_id": ligand,
                            "receptor_conformer_id": conformer,
                            "vina_seed": seed,
                            "vina_score": float(
                                len(role)
                                + ligand_index
                                + conformer_index
                                + seed_index
                            ),
                        }
                    )
    return rows


class DockingMultiMutantTests(unittest.TestCase):
    def test_mutation_order_is_canonical_and_genotype_id_is_stable(self) -> None:
        ordered = canonicalize_mutations([MUT_B, MUT_A], sequence=WT_SEQUENCE)
        self.assertEqual(ordered, [MUT_A, MUT_B])
        self.assertEqual(
            make_genotype_id(
                "SyntheticR", [MUT_B, MUT_A], sequence=WT_SEQUENCE
            ),
            make_genotype_id(
                "SyntheticR", [MUT_A, MUT_B], sequence=WT_SEQUENCE
            ),
        )
        self.assertEqual(
            make_genotype_id(
                "SyntheticR", [MUT_B, MUT_A], sequence=WT_SEQUENCE
            ),
            "SyntheticR_C2V_I8A",
        )

    def test_single_and_double_mutant_fasta(self) -> None:
        single = build_genotype_fasta("SyntheticR", WT_SEQUENCE, [MUT_A])
        double = build_genotype_fasta(
            "SyntheticR", WT_SEQUENCE, [MUT_B, MUT_A]
        )
        self.assertEqual(single["sequence"], "AVDEFGHIKLMNPQRSTVWY")
        self.assertEqual(double["sequence"], "AVDEFGHAKLMNPQRSTVWY")
        self.assertEqual(single["sequence_length"], len(WT_SEQUENCE))
        self.assertTrue(double["fasta"].startswith(">SyntheticR_C2V_I8A\n"))

        with tempfile.TemporaryDirectory() as directory:
            path, payload = write_genotype_fasta(
                "SyntheticR", WT_SEQUENCE, [MUT_B, MUT_A], Path(directory)
            )
            self.assertEqual(path.read_text(encoding="utf-8"), payload["fasta"])
            with self.assertRaises(FileExistsError):
                write_genotype_fasta(
                    "SyntheticR", WT_SEQUENCE, [MUT_A, MUT_B], Path(directory)
                )

    def test_wt_identity_succeeds_and_fails_closed(self) -> None:
        self.assertEqual(
            canonicalize_mutations([MUT_A], sequence=WT_SEQUENCE),
            [MUT_A],
        )
        with self.assertRaisesRegex(
            MutationValidationError, "WT identity mismatch"
        ):
            canonicalize_mutations(
                [{"position": 2, "wt": "D", "mut": "V"}],
                sequence=WT_SEQUENCE,
            )

    def test_duplicate_and_conflicting_positions_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            MutationValidationError, "duplicate mutation position"
        ):
            canonicalize_mutations([MUT_A, MUT_A])
        with self.assertRaisesRegex(
            MutationValidationError, "conflicting mutations"
        ):
            canonicalize_mutations(
                [MUT_A, {"position": 2, "wt": "C", "mut": "A"}]
            )

    def test_out_of_range_and_illegal_residues_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            MutationValidationError, "outside sequence length"
        ):
            canonicalize_mutations(
                [{"position": 21, "wt": "A", "mut": "V"}],
                sequence=WT_SEQUENCE,
            )
        invalid_mutations = [
            {"position": "2", "wt": "C", "mut": "V"},
            {"position": 0, "wt": "C", "mut": "V"},
            {"position": 2, "wt": "C"},
            {"position": 2, "wt": "X", "mut": "V"},
            {"position": 2, "wt": "C", "mut": "B"},
            {"position": 2, "wt": "", "mut": "V"},
            {"position": 2, "wt": "C", "mut": "C"},
        ]
        for mutation in invalid_mutations:
            with self.subTest(mutation=mutation):
                with self.assertRaises(MutationValidationError):
                    canonicalize_mutations([mutation], sequence=WT_SEQUENCE)

    def test_undeclared_residues_remain_identical(self) -> None:
        mutated = apply_mutations(WT_SEQUENCE, [MUT_A, MUT_B])
        declared = {MUT_A["position"], MUT_B["position"]}
        for position, (before, after) in enumerate(
            zip(WT_SEQUENCE, mutated), start=1
        ):
            if position not in declared:
                self.assertEqual(before, after)

    def test_legacy_single_mutation_schema_remains_readable(self) -> None:
        legacy = {
            "receptor": "SyntheticR",
            "mutation": "C2V",
            "wt_residue": "C",
            "mut_residue": "V",
            "residue_num": 2,
            "historical_score": -1.0,
        }
        normalized = normalize_genotype(legacy, sequence=WT_SEQUENCE)
        self.assertEqual(normalized["genotype_id"], "SyntheticR_C2V")
        self.assertEqual(normalized["mutations"], [MUT_A])
        self.assertNotIn("historical_score", normalized)

    def test_complete_cycle_is_canonical(self) -> None:
        cycle = validate_cycle(synthetic_cycle())
        self.assertEqual(
            set(cycle["genotypes"]), {"WT", "A", "B", "AB"}
        )
        self.assertEqual(cycle["genotypes"]["AB"]["mutations"], [MUT_A, MUT_B])
        self.assertEqual(
            cycle["genotypes"]["AB"]["genotype_id"],
            "SyntheticR_C2V_I8A",
        )

    def test_missing_cycle_arm_is_rejected(self) -> None:
        cycle = synthetic_cycle()
        del cycle["genotypes"]["B"]
        with self.assertRaisesRegex(CycleValidationError, "missing=.*B"):
            validate_cycle(cycle)

    def test_ab_must_equal_union_and_sites_must_differ(self) -> None:
        wrong_union = synthetic_cycle()
        wrong_union["genotypes"]["AB"]["mutations"] = [MUT_A]
        with self.assertRaisesRegex(CycleValidationError, "canonical union"):
            validate_cycle(wrong_union)

        same_site = synthetic_cycle()
        same_site_mutation = {"position": 2, "wt": "C", "mut": "A"}
        same_site["genotypes"]["B"]["mutations"] = [same_site_mutation]
        same_site["genotypes"]["AB"]["mutations"] = [MUT_A]
        with self.assertRaisesRegex(CycleValidationError, "different positions"):
            validate_cycle(same_site)

    def test_all_cycle_contract_fields_must_match(self) -> None:
        mutations = {
            "receptor": "OtherR",
            "parent": "parent-02",
            "ligands": ["target", "other"],
            "grid": {"center": [0.0, 0.0, 0.0]},
            "seeds": [11],
            "conformers": ["conf-9"],
        }
        for field, value in mutations.items():
            cycle = synthetic_cycle()
            cycle["genotypes"]["AB"][field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    CycleValidationError, f"inconsistent {field}"
                ):
                    validate_cycle(cycle)

    def test_missing_matched_seed_or_conformer_rejects_calculation(self) -> None:
        cycle = synthetic_cycle()
        rows = synthetic_results(cycle)
        rows = [
            row
            for row in rows
            if not (
                row["genotype_id"] == "SyntheticR_C2V_I8A"
                and row["ligand_id"] == "offtarget"
                and row["receptor_conformer_id"] == "conf-2"
                and row["vina_seed"] == 22
            )
        ]
        with self.assertRaisesRegex(
            CycleValidationError, "matched seed/conformer coverage is incomplete"
        ):
            compute_cycle_contrasts(cycle, rows)

    def test_result_join_uses_structured_identity_not_label_parsing(self) -> None:
        cycle = synthetic_cycle()
        rows = synthetic_results(cycle)
        for index, row in enumerate(rows):
            row["label"] = f"arbitrary-label-{index}"
        joined = join_cycle_results(cycle, rows)
        contrasts = compute_cycle_contrasts(cycle, rows)
        self.assertEqual(len(joined), 4)
        self.assertEqual(len(contrasts), 4)
        self.assertTrue(
            all(
                set(item["arms"]) == {"WT", "A", "B", "AB"}
                for item in joined
            )
        )

        legacy_only = copy.deepcopy(rows[0])
        legacy_only.pop("mutations")
        legacy_only["mutation"] = "C2V"
        with self.assertRaisesRegex(
            CycleValidationError, "structured mutations"
        ):
            join_cycle_results(cycle, [legacy_only])

        missing_id = copy.deepcopy(rows[0])
        missing_id.pop("genotype_id")
        with self.assertRaisesRegex(CycleValidationError, "genotype_id"):
            join_cycle_results(cycle, [missing_id])

    def test_runtime_schema_and_template_are_parseable_placeholders(self) -> None:
        schema_path = (
            ROOT
            / "experiments/docking-repro/multi-mutant/schemas/genotype.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "docking-genotype-v1")
        template = (
            ROOT
            / "experiments/docking-repro/multi-mutant/configs/"
            "candidate_cycle.template.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn("allowed_use: schema_and_test_only", template)
        self.assertIn("SyntheticR", template)
        self.assertNotIn("R59C", template)
        self.assertNotIn("R167Y", template)


if __name__ == "__main__":
    unittest.main()
