"""Canonical multi-mutation genotype, FASTA, and double-mutant cycle contracts.

This module is intentionally independent of the withdrawn legacy mutant
ranking pipeline. It provides local schema and validation preparation only; it
does not select candidates or start structure prediction or docking.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


GENOTYPE_SCHEMA = "docking-genotype-v1"
CYCLE_SCHEMA = "docking-double-mutant-cycle-v1"
CANONICAL_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")
REQUIRED_CYCLE_ARMS = ("WT", "A", "B", "AB")
_MUTATION_LABEL = re.compile(r"([A-Z])([1-9][0-9]*)([A-Z])")
_RECEPTOR_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*")


class MutationValidationError(ValueError):
    """Raised when a mutation or genotype violates the canonical contract."""


class CycleValidationError(ValueError):
    """Raised when a WT/A/B/AB cycle or its matched results are incomplete."""


def _require_nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MutationValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _canonical_residue(value: Any, field: str) -> str:
    residue = _require_nonempty_text(value, field).upper()
    if len(residue) != 1 or residue not in CANONICAL_AMINO_ACIDS:
        raise MutationValidationError(
            f"{field} must be one canonical amino-acid letter"
        )
    return residue


def normalize_sequence(sequence: str) -> str:
    """Normalize a FASTA-like sequence and reject noncanonical residues."""

    if not isinstance(sequence, str):
        raise MutationValidationError("sequence must be a string")
    normalized = "".join(sequence.split()).upper()
    if not normalized:
        raise MutationValidationError("sequence must not be empty")
    invalid = sorted(set(normalized) - CANONICAL_AMINO_ACIDS)
    if invalid:
        raise MutationValidationError(
            f"sequence contains noncanonical residues: {','.join(invalid)}"
        )
    return normalized


def canonicalize_mutations(
    mutations: Sequence[Mapping[str, Any]],
    *,
    sequence: str | None = None,
) -> list[dict[str, Any]]:
    """Validate and sort structured mutations by residue number.

    An empty list is valid and represents WT. Duplicate entries at a position
    fail even if they are identical; different entries at one position are
    reported as a conflict.
    """

    if isinstance(mutations, (str, bytes)) or not isinstance(mutations, Sequence):
        raise MutationValidationError("mutations must be a structured list")

    reference = normalize_sequence(sequence) if sequence is not None else None
    canonical: list[dict[str, Any]] = []
    seen: dict[int, dict[str, Any]] = {}

    for index, raw in enumerate(mutations):
        if not isinstance(raw, Mapping):
            raise MutationValidationError(f"mutations[{index}] must be an object")

        position = raw.get("position")
        if isinstance(position, bool) or not isinstance(position, int) or position < 1:
            raise MutationValidationError(
                f"mutations[{index}].position must be a positive integer"
            )
        wt = _canonical_residue(raw.get("wt"), f"mutations[{index}].wt")
        mut = _canonical_residue(raw.get("mut"), f"mutations[{index}].mut")
        if wt == mut:
            raise MutationValidationError(
                f"mutation at position {position} is a WT identity, not a mutation"
            )

        record = {"position": position, "wt": wt, "mut": mut}
        if position in seen:
            if seen[position] == record:
                raise MutationValidationError(
                    f"duplicate mutation position: {position}"
                )
            raise MutationValidationError(
                f"conflicting mutations at position: {position}"
            )
        seen[position] = record

        if reference is not None:
            if position > len(reference):
                raise MutationValidationError(
                    f"mutation position {position} is outside sequence length "
                    f"{len(reference)}"
                )
            actual_wt = reference[position - 1]
            if actual_wt != wt:
                raise MutationValidationError(
                    f"WT identity mismatch at position {position}: "
                    f"declared {wt}, sequence has {actual_wt}"
                )

        canonical.append(record)

    canonical.sort(key=lambda mutation: mutation["position"])
    return canonical


def make_genotype_id(
    receptor: str,
    mutations: Sequence[Mapping[str, Any]],
    *,
    sequence: str | None = None,
) -> str:
    """Build an input-order-independent genotype identifier."""

    receptor_id = _require_nonempty_text(receptor, "receptor")
    if not _RECEPTOR_ID.fullmatch(receptor_id):
        raise MutationValidationError(
            "receptor may contain only letters, digits, dots, and hyphens"
        )
    canonical = canonicalize_mutations(mutations, sequence=sequence)
    if not canonical:
        return f"{receptor_id}_WT"
    suffix = "_".join(
        f"{mutation['wt']}{mutation['position']}{mutation['mut']}"
        for mutation in canonical
    )
    return f"{receptor_id}_{suffix}"


def normalize_genotype(
    record: Mapping[str, Any],
    *,
    sequence: str | None = None,
) -> dict[str, Any]:
    """Read canonical genotypes and the historical single-mutation schema.

    Historical rows are accepted read-only through ``mutation`` plus the
    optional ``wt_residue``, ``mut_residue``, and ``residue_num`` fields. New
    multi-mutant result joins must still provide structured ``mutations``.
    """

    if not isinstance(record, Mapping):
        raise MutationValidationError("genotype record must be an object")
    supplied_schema = record.get("schema")
    if supplied_schema is not None and supplied_schema != GENOTYPE_SCHEMA:
        raise MutationValidationError(
            f"unsupported genotype schema: {supplied_schema}"
        )
    receptor = _require_nonempty_text(record.get("receptor"), "receptor")

    if "mutations" in record:
        raw_mutations = record["mutations"]
        if isinstance(raw_mutations, (str, bytes)) or not isinstance(
            raw_mutations, Sequence
        ):
            raise MutationValidationError("mutations must be a structured list")
        canonical = canonicalize_mutations(raw_mutations, sequence=sequence)
    else:
        label = _require_nonempty_text(record.get("mutation"), "mutation").upper()
        if label == "WT":
            canonical = []
        else:
            match = _MUTATION_LABEL.fullmatch(label)
            if match is None:
                raise MutationValidationError(
                    "legacy mutation must be one unambiguous single-mutation label"
                )
            wt, position_text, mut = match.groups()
            position = int(position_text)
            legacy_checks = {
                "wt_residue": wt,
                "mut_residue": mut,
                "residue_num": position,
            }
            for field, expected in legacy_checks.items():
                if field in record and record[field] != expected:
                    raise MutationValidationError(
                        f"legacy {field} disagrees with mutation label {label}"
                    )
            canonical = canonicalize_mutations(
                [{"position": position, "wt": wt, "mut": mut}],
                sequence=sequence,
            )

    genotype_id = make_genotype_id(receptor, canonical, sequence=sequence)
    supplied_id = record.get("genotype_id")
    if supplied_id is not None and supplied_id != genotype_id:
        raise MutationValidationError(
            f"genotype_id mismatch: expected {genotype_id}, got {supplied_id}"
        )
    return {
        "schema": GENOTYPE_SCHEMA,
        "genotype_id": genotype_id,
        "receptor": receptor,
        "mutations": canonical,
    }


def apply_mutations(
    sequence: str,
    mutations: Sequence[Mapping[str, Any]],
) -> str:
    """Apply only declared mutations and verify full sequence identity."""

    reference = normalize_sequence(sequence)
    canonical = canonicalize_mutations(mutations, sequence=reference)
    output = list(reference)
    declared_positions = {mutation["position"] for mutation in canonical}
    for mutation in canonical:
        output[mutation["position"] - 1] = mutation["mut"]
    mutated = "".join(output)

    if len(mutated) != len(reference):
        raise AssertionError("mutation application changed sequence length")
    for position, (before, after) in enumerate(zip(reference, mutated), start=1):
        if position in declared_positions:
            expected = next(
                mutation["mut"]
                for mutation in canonical
                if mutation["position"] == position
            )
            if after != expected:
                raise AssertionError(
                    f"declared mutation was not applied at position {position}"
                )
        elif before != after:
            raise AssertionError(
                f"undeclared residue changed at position {position}"
            )
    return mutated


def build_genotype_fasta(
    receptor: str,
    sequence: str,
    mutations: Sequence[Mapping[str, Any]],
    *,
    line_width: int = 80,
) -> dict[str, Any]:
    """Return a canonical genotype plus its identity-checked FASTA payload."""

    if isinstance(line_width, bool) or not isinstance(line_width, int) or line_width < 1:
        raise MutationValidationError("line_width must be a positive integer")
    reference = normalize_sequence(sequence)
    genotype = normalize_genotype(
        {"receptor": receptor, "mutations": mutations},
        sequence=reference,
    )
    mutated = apply_mutations(reference, genotype["mutations"])
    lines = [
        mutated[offset : offset + line_width]
        for offset in range(0, len(mutated), line_width)
    ]
    return {
        **genotype,
        "sequence": mutated,
        "sequence_length": len(mutated),
        "fasta": f">{genotype['genotype_id']}\n" + "\n".join(lines) + "\n",
    }


def write_genotype_fasta(
    receptor: str,
    sequence: str,
    mutations: Sequence[Mapping[str, Any]],
    output_dir: Path,
    *,
    overwrite: bool = False,
) -> tuple[Path, dict[str, Any]]:
    """Write one canonical FASTA without overwriting an existing file by default."""

    payload = build_genotype_fasta(receptor, sequence, mutations)
    output_path = Path(output_dir) / f"{payload['genotype_id']}.fasta"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing FASTA: {output_path}")
    output_path.write_text(payload["fasta"], encoding="utf-8")
    return output_path, payload


def _validate_arm_contract(role: str, arm: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(arm, Mapping):
        raise CycleValidationError(f"cycle arm {role} must be an object")
    try:
        genotype = normalize_genotype(arm)
    except MutationValidationError as exc:
        raise CycleValidationError(f"invalid {role} genotype: {exc}") from exc

    parent = arm.get("parent")
    if not isinstance(parent, str) or not parent.strip():
        raise CycleValidationError(f"cycle arm {role} requires parent")

    ligands = arm.get("ligands")
    if isinstance(ligands, (str, bytes)) or not isinstance(ligands, Sequence):
        raise CycleValidationError(f"cycle arm {role} requires a ligand list")
    normalized_ligands = [
        ligand.strip()
        for ligand in ligands
        if isinstance(ligand, str) and ligand.strip()
    ]
    if len(normalized_ligands) != 2 or len(set(normalized_ligands)) != 2:
        raise CycleValidationError(
            f"cycle arm {role} requires exactly two distinct ligands"
        )

    grid = arm.get("grid")
    if not isinstance(grid, Mapping) or not grid:
        raise CycleValidationError(f"cycle arm {role} requires a non-empty grid")

    seeds = arm.get("seeds")
    if isinstance(seeds, (str, bytes)) or not isinstance(seeds, Sequence):
        raise CycleValidationError(f"cycle arm {role} requires a seed list")
    if (
        not seeds
        or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise CycleValidationError(
            f"cycle arm {role} seeds must be unique integers"
        )

    conformers = arm.get("conformers")
    if isinstance(conformers, (str, bytes)) or not isinstance(conformers, Sequence):
        raise CycleValidationError(f"cycle arm {role} requires a conformer list")
    normalized_conformers = [
        conformer.strip()
        for conformer in conformers
        if isinstance(conformer, str) and conformer.strip()
    ]
    if (
        not normalized_conformers
        or len(normalized_conformers) != len(conformers)
        or len(set(normalized_conformers)) != len(normalized_conformers)
    ):
        raise CycleValidationError(
            f"cycle arm {role} conformers must be unique non-empty strings"
        )

    return {
        **genotype,
        "parent": parent.strip(),
        "ligands": normalized_ligands,
        "grid": dict(grid),
        "seeds": list(seeds),
        "conformers": normalized_conformers,
    }


def validate_cycle(cycle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a complete, matched WT/A/B/AB double-mutant cycle."""

    if not isinstance(cycle, Mapping):
        raise CycleValidationError("cycle must be an object")
    supplied_schema = cycle.get("schema")
    if supplied_schema is not None and supplied_schema != CYCLE_SCHEMA:
        raise CycleValidationError(
            f"unsupported cycle schema: {supplied_schema}"
        )
    cycle_id = cycle.get("cycle_id")
    if not isinstance(cycle_id, str) or not cycle_id.strip():
        raise CycleValidationError("cycle_id must be a non-empty string")
    arms = cycle.get("genotypes")
    if not isinstance(arms, Mapping):
        raise CycleValidationError("cycle genotypes must be an object")
    missing = sorted(set(REQUIRED_CYCLE_ARMS) - set(arms))
    extra = sorted(set(arms) - set(REQUIRED_CYCLE_ARMS))
    if missing or extra:
        raise CycleValidationError(
            f"cycle arms mismatch: missing={missing}, extra={extra}"
        )

    normalized = {
        role: _validate_arm_contract(role, arms[role])
        for role in REQUIRED_CYCLE_ARMS
    }
    reference = normalized["WT"]
    contract_fields = ("receptor", "parent", "ligands", "grid", "seeds", "conformers")
    for role in REQUIRED_CYCLE_ARMS[1:]:
        for field in contract_fields:
            if normalized[role][field] != reference[field]:
                raise CycleValidationError(
                    f"cycle arm {role} has inconsistent {field}"
                )

    if reference["mutations"]:
        raise CycleValidationError("WT arm must not contain mutations")
    if len(normalized["A"]["mutations"]) != 1:
        raise CycleValidationError("A arm must contain exactly one mutation")
    if len(normalized["B"]["mutations"]) != 1:
        raise CycleValidationError("B arm must contain exactly one mutation")
    mutation_a = normalized["A"]["mutations"][0]
    mutation_b = normalized["B"]["mutations"][0]
    if mutation_a["position"] == mutation_b["position"]:
        raise CycleValidationError("A and B must mutate different positions")

    expected_ab = canonicalize_mutations([mutation_a, mutation_b])
    if normalized["AB"]["mutations"] != expected_ab:
        raise CycleValidationError(
            "AB mutations must equal the canonical union of A and B"
        )

    output = dict(cycle)
    output["schema"] = CYCLE_SCHEMA
    output["cycle_id"] = cycle_id.strip()
    output["genotypes"] = normalized
    return output


def _result_identity(
    row: Mapping[str, Any],
    role_by_genotype: Mapping[str, str],
    cycle: Mapping[str, Any],
) -> tuple[str, str, str, int]:
    if "genotype_id" not in row or "mutations" not in row:
        raise CycleValidationError(
            "new cycle results require genotype_id and structured mutations; "
            "legacy labels are read-only"
        )
    try:
        genotype = normalize_genotype(row)
    except MutationValidationError as exc:
        raise CycleValidationError(f"invalid structured result genotype: {exc}") from exc
    genotype_id = genotype["genotype_id"]
    role = role_by_genotype.get(genotype_id)
    if role is None:
        raise CycleValidationError(f"unexpected result genotype_id: {genotype_id}")
    expected = cycle["genotypes"][role]
    if genotype["mutations"] != expected["mutations"]:
        raise CycleValidationError(
            f"result mutations disagree with cycle arm {role}"
        )

    ligand = row.get("ligand_id")
    conformer = row.get("receptor_conformer_id")
    seed = row.get("vina_seed")
    parent = row.get("parent")
    if ligand not in expected["ligands"]:
        raise CycleValidationError(f"unexpected ligand_id for {role}: {ligand}")
    if conformer not in expected["conformers"]:
        raise CycleValidationError(
            f"unexpected receptor_conformer_id for {role}: {conformer}"
        )
    if isinstance(seed, bool) or not isinstance(seed, int) or seed not in expected["seeds"]:
        raise CycleValidationError(f"unexpected vina_seed for {role}: {seed}")
    if parent != expected["parent"]:
        raise CycleValidationError(f"inconsistent parent in result for {role}")
    return role, ligand, conformer, seed


def join_cycle_results(
    cycle: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Join results by structured genotype identity and enforce matched coverage."""

    normalized_cycle = validate_cycle(cycle)
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise CycleValidationError("result rows must be a list")
    arms = normalized_cycle["genotypes"]
    role_by_genotype = {
        arm["genotype_id"]: role for role, arm in arms.items()
    }
    indexed: dict[tuple[str, str, str, int], Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise CycleValidationError("each result row must be an object")
        key = _result_identity(row, role_by_genotype, normalized_cycle)
        if key in indexed:
            raise CycleValidationError(f"duplicate matched result row: {key}")
        indexed[key] = row

    contract = arms["WT"]
    missing: list[tuple[str, str, str, int]] = []
    for role in REQUIRED_CYCLE_ARMS:
        for ligand in contract["ligands"]:
            for conformer in contract["conformers"]:
                for seed in contract["seeds"]:
                    key = (role, ligand, conformer, seed)
                    if key not in indexed:
                        missing.append(key)
    if missing:
        preview = ", ".join(str(key) for key in missing[:4])
        raise CycleValidationError(
            f"matched seed/conformer coverage is incomplete; missing {preview}"
        )

    joined: list[dict[str, Any]] = []
    for conformer in contract["conformers"]:
        for seed in contract["seeds"]:
            joined.append(
                {
                    "cycle_id": normalized_cycle["cycle_id"],
                    "parent": contract["parent"],
                    "receptor_conformer_id": conformer,
                    "vina_seed": seed,
                    "arms": {
                        role: {
                            ligand: indexed[(role, ligand, conformer, seed)]
                            for ligand in contract["ligands"]
                        }
                        for role in REQUIRED_CYCLE_ARMS
                    },
                }
            )
    return joined


def compute_cycle_contrasts(
    cycle: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    *,
    score_field: str = "vina_score",
) -> list[dict[str, Any]]:
    """Compute matched double-mutant contrasts after complete coverage checks."""

    normalized_cycle = validate_cycle(cycle)
    ligands = normalized_cycle["genotypes"]["WT"]["ligands"]
    joined = join_cycle_results(normalized_cycle, rows)
    contrasts: list[dict[str, Any]] = []
    for matched in joined:
        selectivity: dict[str, float] = {}
        for role in REQUIRED_CYCLE_ARMS:
            values: list[float] = []
            for ligand in ligands:
                value = matched["arms"][role][ligand].get(score_field)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(float(value))
                ):
                    raise CycleValidationError(
                        f"{role}/{ligand} has invalid {score_field}"
                    )
                values.append(float(value))
            selectivity[role] = values[0] - values[1]
        epsilon = (
            selectivity["AB"]
            - selectivity["A"]
            - selectivity["B"]
            + selectivity["WT"]
        )
        contrasts.append(
            {
                "cycle_id": matched["cycle_id"],
                "parent": matched["parent"],
                "receptor_conformer_id": matched["receptor_conformer_id"],
                "vina_seed": matched["vina_seed"],
                "ligand_order": list(ligands),
                "selectivity_by_arm": selectivity,
                "epsilon_selectivity_score": epsilon,
            }
        )
    return contrasts


def canonical_json(value: Mapping[str, Any]) -> str:
    """Return stable JSON for manifests or local schema snapshots."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
