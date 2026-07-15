# R4 Historical Gap Register

> Date: 2026-07-06
>
> Status: historical supporting gap register; execution requires separate approval.
>
> Scope: recorded source/material gaps for the chimeric Gpa1 R4 coarse-grained / multiscale route after the 2026-07-05 local material decision.
>
> Routing contract: this file is a supporting gap register consumed by
> `r4_material_decision_addendum_20260706.md`.

## Why This File Exists

The 2026-07-05 R4 local material decision stopped a local dry-build planning package. This file preserves the concrete missing-material rows that explain the remaining buildability gate.

The source-backed R4 state captured when this register was written was:

- R4 has a `chctrl`-first design-only object contract.
- R4 still requires a reproducible local dry-build package before build planning.
- The missing materials are now concrete: direct GPCR-Galpha or Ste2-Gpa1 CG workflow evidence, a Martini 3-compatible CG-to-AA route for membrane protein complexes, a durable `chctrl` full-system input payload policy, an actual `chctrl` contact-map generation policy, and a local version/source inventory for the CG toolchain.

This file is a supporting historical register consumed by the material addendum.

## Working Rule

Within this register, "reopen R4" was a historical label for evidence-gap
classification. Execution, shared-router edits, and production-file work require
separate routed approval.

If a future session revisits any row, it must start from `docs/INDEX.md` and
write a new dated R4-local artifact instead of continuing this register in
place. Router files or shared daily logs should only be updated after
coordination.

## Source-Faithful Supporting State

| Topic | Current repo record | Boundary read |
|---|---|---|
| R4 method vocabulary | Yang2024 SI/tutorial, GoMartini3, OliGoMers, Lopez2022, Aydin2025 are extracted in `r4_cg_method_extraction_20260704.md`. | Enough vocabulary for object contracts, not enough for a build. |
| Direct GPCR-Galpha CG source | `r4_gpcr_galpha_citation_chasing_20260704.md` and `r4_direct_gpcr_galpha_cg_source_chase_20260705.md` did not retain a usable direct workflow. | Recheck stays narrow and source-targeted. |
| Object contract | `r4_chctrl_object_contract_20260705.md` defines `chctrl` object, contact-policy arms, CG-to-AA validation gate, and comparable atomistic metrics. | Supporting design anchor. |
| Local material decision | `r4_local_dry_build_decision_package_20260705.md` records the R4 dry-build no-go. | A new dated material-boundary review would be required if one of the concrete missing materials changes. |
| Material matrix | `r4_local_dry_build_material_matrix_20260705.tsv` names input anchors, interface anchors, toolchain vocabulary, membrane/ion caveats, and CG-to-AA gaps. | Use it as historical row source for this register. |

## Recorded Gap Rows

| ID | Gap | Evidence check description | Recorded/possible output | Boundary criterion |
|---|---|---|---|---|
| R4-GAP-01 | Direct GPCR-Galpha / Ste2-Gpa1 CG workflow | Run a narrow source recheck for direct GPCR-Galpha, Ste2-Gpa1, mini-G/Galpha, or receptor-G protein Martini/coarse-grained workflows. Keep DOI/title/source/access and reject receptor-only or generic protein papers. | `r4_direct_gpcr_galpha_cg_recheck_YYYYMMDD.tsv` plus a short memo if any retained source exists. | At least one source names object, membrane setup, receptor-effector contact policy, and validation route. |
| R4-GAP-02 | OLIVES method body | Acquire article/SI/code or an accessible official/preprint copy for DOI `10.1021/acs.jctc.4c00553`; extract only method fields that affect structure-bias choice. | OLIVES subsection update or `r4_olives_method_extraction_YYYYMMDD.md`. | Method body names contact definition, parameters, Martini 3 compatibility, and limitations. |
| R4-GAP-03 | Martini 3-compatible CG-to-AA route | Identify and extract a concrete route such as CG2AT, Backward, or sinceCG only from official docs, papers, or source repositories. Check membrane-protein examples, Martini 3 support, stereochemistry/periodicity checks, and interface preservation. | `r4_cg_to_aa_route_screen_YYYYMMDD.md` and optional TSV. | A route can be named with version/source, Martini 3 scope, protein/membrane compatibility, and validation checks. |
| R4-GAP-04 | Durable `chctrl` full-system payload policy | Decide how exact full-system `chctrl` inputs would be referenced or archived without copying ignored raw binaries blindly into git. Include checksum, location, size, and acceptable pointer/archive form. | `r4_chctrl_payload_policy_YYYYMMDD.md`. | A later dry-build plan can cite an exact durable full-system input without depending on an unstaged local-only path. |
| R4-GAP-05 | Actual `chctrl` contact-map feasibility | Convert the object-contract anchors into a contact-map feasibility spec: required atomistic input, receptor/Galpha chains, contact generator, inclusion/exclusion of interchain contacts, epsilon scan labels, and validation metrics. Topology/build file generation requires a separate phase. | `r4_chctrl_contact_map_feasibility_YYYYMMDD.md` and optional contact-anchor TSV. | A future dry-build plan can state what contact files must exist and how they will be checked against atomistic anchors. |
| R4-GAP-06 | Local tool/source inventory | Record whether required tools are source-only, locally present, or need manual install later: martinize2/vermouth, Martini 3 files, Go/contact-map generator, `insane.py`, CG-to-AA route, analysis tooling. Installation requires separate approval. | `r4_local_toolchain_inventory_YYYYMMDD.tsv`. | The difference between "paper vocabulary" and "locally executable toolchain" is explicit. |

## Historical Handling Note

The 2026-07-06 pass handled R4-GAP-03 and R4-GAP-06 first because CG-to-AA and
toolchain reality were the largest blockers to any future dry-build package. It
also recorded R4-GAP-04 and R4-GAP-05 as payload/contact-map boundary evidence
without generating build files. R4-GAP-01 was later rechecked at metadata/title
level. R4-GAP-02 remains a manual-acquisition gap.

## Historical Classification Labels

Rows were classified using these historical labels at the time. Current
next-action instructions come from routed decision records:

| Classification | Meaning | Boundary implication |
|---|---|---|
| `historical_reopen_for_material_decision` | A row added concrete source/tool/payload information that could have changed the 2026-07-05 material decision. | A new dated material-boundary addendum would have been required. |
| `historical_continue_gap_queue` | A row sharpened the gap but did not close it. | R4 stayed screening/design-only with no production-file work. |
| `historical_appendix_only_with_source_gain` | A row added useful method language but no executable route. | R4 stayed future design evidence only. |

## 2026-07-06 Phase Note

The first R4-only evidence-gap pass produced R4-GAP-03, R4-GAP-04, R4-GAP-05, and R4-GAP-06 artifacts. The decision addendum is:

```text
experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md
```

Supporting R4 validation-design notes:

```text
experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md
```

The rows in this file remain historical/supporting evidence. After the R4-GAP-01
recheck, the recorded unresolved items were R4-GAP-02 OLIVES method-body
acquisition and CG2AT official/example pointer acquisition for Smoke Object B.

## 2026-07-06 R4-GAP-01 Recheck Result

R4-GAP-01 has now been rechecked at metadata/title-screen level:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.md
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.tsv
```

Result:

- Crossref/OpenAlex direct GPCR-Galpha, Ste2-Gpa1, and receptor-G protein complex queries left direct coarse-grained/Martini receptor-Galpha workflow support unresolved.
- The mini-G/Galpha metadata query had provider caveats, so PubMed exact title/abstract probes were used as supplemental screening.
- PubMed surfaced atomistic mini-G/G-protein coupling papers, GPCR-ligand MM/CG, receptor-lipid CG, receptor dimer/oligomer CG, and Ste2 structure seeds, but no retained direct GPCR-Galpha CG workflow.

Classification:

```text
historical_continue_gap_queue
```

The recorded remaining source/material gaps were R4-GAP-02 OLIVES method-body
acquisition and CG2AT official/example pointer acquisition for Smoke Object B.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_material_matrix_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.tsv`
- `docs/logs/2026-07-05.md`
- `docs/logs/2026-07-06.md`
- `docs/INDEX.md`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
- R4-GAP-01 result: `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.md`
- Support relationship: `r4_material_decision_addendum_20260706.md` consumes this file as the gap register; `r4_tool_validation_plan_20260706.md` cites it only for validation-design evidence.
