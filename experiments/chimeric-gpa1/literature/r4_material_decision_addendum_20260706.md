# R4 Material Decision Addendum

> Date: 2026-07-06
>
> Status: R4 material/boundary record; execution requires separate approval.
>
> Scope: single R4 material-boundary addendum for the 2026-07-05/06 source/material gate.

## Source-Faithful Update

Routing contract: `docs/INDEX.md` owns current project routing. This addendum is
the single R4 material-boundary record for the 2026-07-05/06 source/material
gate. Supporting R4 files point here for the R4 boundary and keep current status,
phase order, and future-action instructions in `docs/INDEX.md` or dated decision
records.

This addendum records R4 as screening/design-only at the material gate. Build,
E2, candidate-transfer, or dry-build planning would require a separate dated
decision record with the missing evidence named below.

The 2026-07-05 decision remains true in its narrow sense:

- the current material set keeps R4 dry-build planning at no-go;
- `chctrl` CG topology, contact file, backmapped AA output, and candidate-transfer package remain missing evidence;
- R4 remains a screening/design-only material record for atomistic `chctrl`.

The 2026-07-06 R4-only pass sharpened supporting evidence while leaving the
build decision and active project route unchanged:

| Gap row | New artifact | Source-faithful result |
|---|---|---|
| R4-GAP-01 | `r4_direct_gpcr_galpha_cg_recheck_20260706.md` and `.tsv` | Direct GPCR-Galpha / Ste2-Gpa1 CG workflow was rechecked at metadata/title-screen level and no retained direct workflow was found. Boundary unchanged. |
| R4-GAP-03 | `r4_cg_to_aa_route_screen_20260706.md` | CG2AT is now the best current CG-to-AA route candidate because the official source documents Martini-to-atomistic conversion and contains Martini 3 fragment database entries. Local install and `chctrl` testing remain pending evidence. |
| R4-GAP-06 | `r4_local_toolchain_inventory_20260706.tsv` | Yang tutorial materials are present as zipped source attachments; local PATH does not contain `martinize2`, `vermouth`, `cg2at`, `backward`, `initram.sh`, `gmx`, `insane.py`, or `create_goVirt*`. |
| R4-GAP-05 | `r4_chctrl_contact_map_feasibility_20260706.md` and `r4_chctrl_contact_anchor_spec_20260706.tsv` | Existing `chctrl` atomistic anchors are now converted into a future contact-map requirement: chain identity, alpha5/eCT anchors, Ste2 clusters, intra/interchain separation, epsilon labels, required output classes, and stop conditions. No contact map has been generated. |
| R4-GAP-04 | `r4_chctrl_payload_policy_20260706.md` and `r4_chctrl_payload_inventory_20260706.tsv` | Exact full-system `chctrl` payloads can be cited only through tracked pointer/checksum policy unless a later explicit archive route is approved. Large raw payloads remain ignored and are not copied into git. |

## Project Interpretation

The earlier fallback phrase belongs to a single 2026-07-05 session record. The
durable R4 boundary is the material no-go plus the evidence rows in this
addendum.

For R4 evidence records, the corrected boundary is:

```text
R4 dry-build remains no-go -> R4 stays screening/design-only -> future validation requires a new dated decision record and INDEX coordination
```

R4 files store source/material/tool-validation evidence. Shared routers and
daily logs are edited only when the hunk is isolated and source-backed.

## R4 Material Decision

| Question | 2026-07-06 answer |
|---|---|
| Can R4 now write a local dry-build planning package? | Current answer: no-go. Tool validation, actual `chctrl` contact files, and tested CG-to-AA conversion are still absent. |
| Does the 2026-07-06 pass create an active R4 route? | Current route remains in `docs/INDEX.md`; this pass records source/tool/payload/contact evidence. |
| Where are non-executable validation-design notes recorded? | `r4_tool_validation_plan_20260706.md` as supporting validation-design evidence. |
| Which R4 rows remain unresolved? | R4-GAP-02 OLIVES method-body acquisition, CG2AT official/example smoke-object pointer acquisition, exact Go/contact-map source pinning, and local executable validation environment definition. R4-GAP-01 has been rechecked and retained no direct workflow. |

## Supporting Validation Scope

`r4_tool_validation_plan_20260706.md` is a supporting non-executable
validation-design sketch. This addendum records what the 2026-07-06 pass changed
in the R4 material boundary; route authority remains with `docs/INDEX.md` and
dated decision records.

Source-pin result is now tracked in:

```text
experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv
```

It sharpens the material decision: CG2AT and vermouth-martinize have source pins
suitable for a future approved validation phase; Backward is only a fallback
branch-head pin; GoContactMap/ContactMapGenerator, local GROMACS, and OLIVES
remain unresolved rows. The 2026-07-06 recheck keeps source acquisition narrowed
to those named unresolved rows.

No-execution smoke design is now tracked in:

```text
experiments/chimeric-gpa1/literature/r4_non_chctrl_smoke_design_20260706.md
```

It uses the Yang2024 beta2AR tutorial archive as the first non-`chctrl` file-shape object and leaves a separate CG2AT official/example object as pending.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_cg_to_aa_route_screen_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_local_toolchain_inventory_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_map_feasibility_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_anchor_spec_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_policy_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_inventory_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_material_matrix_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_non_chctrl_smoke_design_20260706.md`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_non_chctrl_smoke_design_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
- Historical/supporting R4 route files point here for the R4 material-boundary record and may point to `r4_tool_validation_plan_20260706.md` for protocol-design evidence.
- Shared router/log files use this file as a route pointer and keep detailed material-boundary content here.
