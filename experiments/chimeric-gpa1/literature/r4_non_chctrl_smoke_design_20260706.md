# R4 Non-chctrl Smoke Design

> Date: 2026-07-06
>
> Status: supporting smoke-design spec; no tool execution.
>
> Scope: define low-risk, non-`chctrl` validation checks that a future approved
> R4 validation decision would need before touching exact `chctrl`
> payloads.

## Purpose

This file preserves a possible staged gate for future R4 tool validation. The
first smoke object should be an official/example object. Tool installation,
source extraction, command-interface, and file-shape failures should stay in a
temporary validation surface before any project `chctrl` payload is touched.

No commands are authorized by this file.

## Smoke Object A: Yang2024 beta2AR Go-Martini Tutorial

Use the archived tutorial zip only as an example object and file-shape source.

```text
experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-tutorial.zip
```

SHA-256:

```text
f6790c8e7d79fe24be8eb410288a59bf82e9629d54753873b1381d8f3168228e
```

### Input File Classes

| File class | Archive members | Smoke use |
|---|---|---|
| Atomistic state inputs | `template/3SN6_clean.pdb`, `template/2RH1_clean.pdb`, `prepared/3SN6_clean.pdb`, `prepared/2RH1_clean.pdb` | Confirm receptor-only example structure file class and residue/chain assumptions before any future martinize2 test. |
| Contact maps | `template/3SN6_clean.map`, `template/2RH1_clean.map`, `prepared/3SN6_clean.map`, `prepared/2RH1_clean.map` | Confirm expected contact-map file class for Yang-style `create_goVirt*` scripts. |
| Force-field includes | `template/Martini3_FF/*`, `prepared/Martini3_FF/*` | Confirm Martini 3 include names used by tutorial examples. |
| Script examples | `create_goVirt.py`, `create_goVirt_for_multimer.py`, `insane.py` in `template/` and `prepared/` | Confirm file presence and command-interface assumptions only after temporary extraction in an approved validation phase. |
| Prepared topology examples | `prepared/ActiveITP/*`, `prepared/InactiveITP/*`, `prepared/system.top`, `prepared/system_Active.top`, `prepared/system_Inactive.top` | Confirm output file classes expected from Go virtual-site generation and topology switching. |
| MDP examples | `em.mdp`, `npt.mdp`, `md_relax.mdp`, `md.mdp` in `template/` and `prepared/` | Confirm schedule vocabulary and parameter fields; `chctrl` transfer requires a separate method decision. |

### Expected Output Classes For A Future Approved Smoke Run

If a later phase explicitly approves temporary extraction and local tool execution, the smoke run would be expected to demonstrate only file-shape reproducibility:

| Output class | Required check |
|---|---|
| CG protein PDB | Produced from tutorial input by the chosen martinize2/vermouth pin; receptor-only counts and chain identity recorded. |
| Topology include files | `GO_VIRT`/virtual-site definitions, Go LJ table, exclusions, and protein ITP include structure are present and parseable as text. |
| System topology | Includes Martini 3 force-field files, protein ITP, POPC/water/ion components, and active/inactive topology switching fields. |
| Temporary output path | Smoke output path must be under `/private/tmp` or another explicit temporary validation path before any project `chctrl` result tree is used. |

### Stop Conditions

Stop before `chctrl` if any of these are true:

| Stop condition | Reason |
|---|---|
| Tutorial archive checksum mismatch | Source object cannot be trusted. |
| martinize2/vermouth pin differs from manifest without explanation | Tool behavior is not reproducible. |
| Contact-map format cannot be consumed by the selected route | A future `chctrl` contact map would be speculative. |
| Go virtual-site or exclusion output is not auditable as text | R4 cannot track contact policy. |
| Temporary smoke output cannot be deleted/recreated cleanly | Later `chctrl` validation would risk hidden state. |

## Smoke Object B: CG2AT Official Example

CG2AT is the source-level CG-to-AA candidate. The next CG2AT gate is an
official example input/output pointer suitable for a smoke run.

Recorded status:

```text
source_pending_for_example_object
```

Required before any CG2AT execution:

| Required item | Why |
|---|---|
| Official/example CG input pointer | Prevents using `chctrl` as the first test object. |
| Exact CG2AT tag or commit | Future behavior must be pinned. |
| Fragment directory choice | Martini 3 fragment family must be explicit. |
| Atomistic force-field target | AA comparison force-field must be explicit. |
| Expected output file classes | Needed for checks before any `chctrl` conversion. |

## Conditional chctrl Readiness Gate After Smoke

A passing official/example smoke run would support tool/file-shape validation
only. `chctrl` readiness checks would still require a future R4
material-boundary review.

Before touching `chctrl`, any future approved phase would still need to
re-check:

- payload checksum from `r4_chctrl_payload_inventory_20260706.tsv`;
- chain identity and residue anchors from the selection audit;
- source-pinned contact generator;
- separate intra/interchain contact classes;
- CG-to-AA route and post-conversion atomistic metric map.

## Evidence Classification

```text
phase_b_smoke_design_written_no_execution
```

This no-execution design preserves two conditional validation-design branches:

1. R4-GAP-01 direct GPCR-Galpha / Ste2-Gpa1 CG source recheck; or
2. CG2AT official/example pointer acquisition for Smoke Object B.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv`
- `experiments/chimeric-gpa1/literature/source_attachments/README.md`
- `experiments/chimeric-gpa1/literature/source_files.sha256`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_cg_to_aa_route_screen_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_policy_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_inventory_20260706.tsv`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
- Potential future material-boundary review only if `docs/INDEX.md` reopens R4.
