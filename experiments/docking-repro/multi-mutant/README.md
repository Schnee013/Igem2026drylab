# Multi-mutant docking local contract

> Status: `phase2_local_schema_test_ready_blocked_by_frame_repair`
>
> Source: `src/modeling/docking-repro/multi_mutant.py` and
> `tests/modeling/test_docking_multi_mutant.py`.
>
> As of: `2026-07-30`
>
> Allowed use: local schema, FASTA, cycle-validation, and synthetic test
> preparation only.
>
> Update trigger: repaired single-mutant release, candidate freeze, or any
> genotype/cycle contract change.

This directory is the minimal Phase 2 scaffold for canonical multi-mutation
inputs. It is not a candidate release and contains no real AB genotype.

## Contract

- `mutations` is a structured list of `{position, wt, mut}` objects.
- Mutation order is canonicalized by residue number.
- `genotype_id` is derived from receptor plus canonical mutations.
- New results must carry both `genotype_id` and structured `mutations`.
- Historical single-mutation rows remain readable through a read-only
  compatibility adapter; historical result files are not rewritten.
- A cycle is valid only with matched `WT / A / B / AB` arms and identical
  receptor, parent, ligand, grid, seed, and conformer contracts.

The runtime validator and FASTA generator are implemented in
`src/modeling/docking-repro/multi_mutant.py`. The template under `configs/`
uses synthetic placeholders and must not be promoted to a real
`candidate_cycles.yaml`.

## Stop gate

Do not create a real candidate cycle. R1 corrected the maximum-20 and explicit
CPU8 contracts. The seed-44 independent eight-job holdout completed docking,
IFP, and geometry, but both Gpr3/R167Y arms failed the frozen gate and the run
stopped before full. The repaired 328-job/6560-pose single-mutant rerun has not
started. A passing smoke, run-local score/pose/ratio/IFP, and an audited repaired
shortlist must all exist first.

## References / 所引

- `docs/modeling/multi-mutant-docking/README.md`
- `codex/docs/plans/multi-mutant-docking-execution-plan-20260730.md`
- `codex/docs/plans/docking-frame-repair-18mode-recovery-contract-20260730.md`
- `src/modeling/docking-repro/multi_mutant.py`
- `tests/modeling/test_docking_multi_mutant.py`

## Referenced by / 被引

- `docs/modeling/multi-mutant-docking/README.md`
- `codex/docs/plans/multi-mutant-docking-execution-plan-20260730.md`
- `docs/logs/2026-07-30.md`
