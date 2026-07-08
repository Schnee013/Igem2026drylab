# R4 Local Dry-Build Material Decision Package

> Date: 2026-07-05
>
> Status: local material decision.
>
> Scope: post-object-contract R4 `chctrl` material check for the iGEM2026 drylab compute-triage route.

## Decision

R4 local dry-build planning package status: no-go with the current material set.

R4 has enough material to stay useful as a design-only method appendix, but the
local material pack still needs a reproducible `chctrl` CG dry-build route before
build planning. For the R4-only line, this is a stop condition for dry-build
planning.

2026-07-06 route cleanup: the dry-build no-go above remains active. The R4
material boundary is recorded in `r4_material_decision_addendum_20260706.md`;
current route status starts from `docs/INDEX.md`.

## Material Check

| Field | Current status | Decision read |
|---|---|---|
| Exact input snapshot | A full-system `chctrl` `step5_input.pdb` exists locally under ignored raw paths, and protein-only selection-audit snapshots exist locally under ignored `snapshots/*.pdb`. | Input can be named locally, but the durable payload/archive policy is not solved. Protein-only snapshots are validation anchors, not full-system build inputs. |
| Chain and interface identity | Selection audit supports `PROA = Gpa1-WT`, `PROB = Ste2`, Gpa1 alpha5/eCT `448-472`, and Ste2 clusters `69:84`, `145:160`, `222:251`, `288:304`. | Pass for contact-policy design. |
| Toolchain/source vocabulary | Yang2024 tutorial zip names Martini 3 v3.0.0 files, `create_goVirt*`, `insane.py`, MDPs, and prepared beta2AR topologies; GoMartini3/OliGoMers name `martinize2`/Go/contact-policy fields. | Source-level pass; execution gate is a local executable/version-pinned toolchain plus a generated `chctrl` contact map. |
| Receptor-Galpha contact policy | The object contract can define `R4B-intra-only`, `R4B-weak-interchain`, and `R4B-strong-interchain-diagnostic`. | Pass as a design policy; fail as an execution package because no actual `chctrl` Go/contact file exists. |
| Membrane/ion setup | Yang beta2AR POPC/water/ion examples and local AA full-system `chctrl` inputs exist. | Transfer to a `chctrl` CG setup requires a named CG membrane/ion conversion rule. |
| CG-to-AA validation | Lopez2022, Sahoo2023, and Aydin2025 provide validation vocabulary: selected snapshots, conversion checks, AA relaxation, stereochemistry/periodicity/interface-loss filters, and atomistic metric recomputation. | Build planning requires a local Backward/CG2AT/sinceCG route or an extracted Martini 3 Ste2-Gpa1 / GPCR-Galpha backmapping workflow. |

The material matrix is:

```text
experiments/chimeric-gpa1/literature/r4_local_dry_build_material_matrix_20260705.tsv
```

## Why This Still Helps The Project

This pass turns the R4 material question into two concrete missing materials: an
executable CG-to-AA route and a durable full-system input payload policy.

Current R4 value at this gate:

- it gave the project a vocabulary for future CG object contracts;
- it forced receptor-Galpha interchain contact policy to be explicit;
- it identified the exact missing pieces before any build/run work could waste time;
- it gives a clear stop condition instead of leaving R4 as an open-ended literature loop.

## Boundary After Decision

For R4 work, use `r4_material_decision_addendum_20260706.md` for the R4 material
boundary and `r4_tool_validation_plan_20260706.md` for non-executable
validation-design notes. For global drylab priorities, use `docs/INDEX.md`.

Only two future material changes would justify revisiting this no-go decision:

- a concrete, accessible Martini 3 compatible CG-to-AA/backmapping route for membrane protein complexes;
- or a direct GPCR-Galpha / Ste2-Gpa1 CG workflow that names object, contact policy, membrane setup, and atomistic revalidation.

The 2026-07-06 gap pass now records CG2AT as a concrete CG-to-AA route candidate, a payload pointer policy, a contact-map feasibility spec, and a local toolchain inventory. That supports conditional tool/source validation design; `chctrl` build planning still requires an approved validation phase and named build inputs.

## References / 所引

- `codex/docs/plans/chimeric-gpa1-r4-local-dry-build-material-plan.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_material_matrix_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md`
- `docs/papers/summaries/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer-summary.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/exported_snapshots.csv`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/chctrl_phase_C5_batch1_batch2_summary.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/early_gate_report.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/README.md`

## Referenced by / 被引

- `docs/logs/2026-07-05.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P3-chimeric-gprotein.md`
- `codex/docs/plans/README.md`
- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
