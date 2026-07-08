# R4 Tool Validation Design Notes

> Date: 2026-07-06
>
> Status: supporting R4 validation-design evidence.
>
> Scope: source/version and low-risk tool-validation planning for the R4 `chctrl` coarse-grained / multiscale route.

## Purpose

Routing contract: `docs/INDEX.md` owns current project routing, and
`r4_material_decision_addendum_20260706.md` records the R4 material boundary.
This file preserves non-executable validation-design notes that could
be reused only if a new dated decision record reopens R4 through `docs/INDEX.md`.
Other R4 files use `r4_material_decision_addendum_20260706.md` for current
material-boundary status.

The 2026-07-06 gap pass sharpened what would be required to change the R4 source/material gate. The immediate problem is no longer "is Martini 3 relevant?" The immediate problem is:

```text
Can the needed R4 tools and source files be pinned and validated before touching any exact chctrl payload?
```

This record preserves possible R4 validation design as screening/design-only
evidence.

## Approval Gates

- Tool installation requires separate approval.
- `chctrl` CG system, Go contact map, topology, backmapped AA structure, and production command generation require a later approved phase.
- Remote access and production-file work require separate route approval.
- Shared `docs/INDEX.md` or daily-log edits require explicit coordination.

## Evidence Block A: Source Pinning Manifest

The source-pin manifest has been created:

```text
experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv
```

Minimum rows:

| Tool/source | Required fields | Current seed |
|---|---|---|
| CG2AT | source URL, release/tag or commit, install channel, required Python/GROMACS, Martini 3 fragment directories, force-field target directories | `r4_cg_to_aa_route_screen_20260706.md` |
| martinize2/vermouth | source URL, release/tag or commit, Go/contact flags, compatibility with Martini 3 and contact-map input | `r4_local_toolchain_inventory_20260706.tsv` |
| Go/contact-map generator | exact generator name, source URL, OV/rCSU or equivalent contact definition, contact range, graph-distance rule, multichain behavior | `r4_chctrl_contact_map_feasibility_20260706.md` |
| Yang tutorial archive | zip checksum, contained scripts/MDPs/topologies, extracted file names if used later, no repo explosion by default | `source_files.sha256`; `source_attachments/README.md` |
| Backward/sinceCG fallback | source URL or paper pointer, Martini scope, force-field scope, known limitations | `r4_cg_to_aa_route_screen_20260706.md`; `r4_cg_method_extraction_20260704.md` |

Recorded criterion: the manifest separates source-pinned candidates from locally executable tools. A missing local executable is acceptable here if it is explicitly marked.

2026-07-06 result: this source-pointer block records CG2AT, vermouth-martinize, Backward, Yang tutorial archive members, and unresolved rows for GoContactMap/ContactMapGenerator, GROMACS local environment, OLIVES, and direct GPCR-Galpha CG workflow. Tool installation or execution requires a later approved validation phase.

## Evidence Block B: Non-chctrl Smoke Design

Before any `chctrl` payload is touched, define a smoke design from official/example material.

The smoke-design spec has been written:

```text
experiments/chimeric-gpa1/literature/r4_non_chctrl_smoke_design_20260706.md
```

Required design fields:

| Field | Required content |
|---|---|
| Example object | Official CG2AT or martinize2/Go example object, not `chctrl`. |
| Input file class | Exact file type and source checksum or official example pointer. |
| Expected output class | What files should be produced if a future approved install is used. |
| Validation check | Small checks such as residue count, chain count, fragment selection, topology includes, stereochemistry sanity, or known example comparison. |
| Stop condition | Abort before `chctrl` if official/example behavior is not reproducible. |

This block is design evidence only. Actual installation or execution is a separate approval decision.

2026-07-06 result: this no-execution design block uses the Yang2024 beta2AR tutorial archive as Smoke Object A and leaves CG2AT official/example acquisition as `source_pending_for_example_object`.

## Evidence Block C: chctrl Readiness Without Build

Use existing R4 payload/contact files only for read-only readiness checks:

| Readiness item | Required evidence |
|---|---|
| Payload checksum gate | Match `r4_chctrl_payload_inventory_20260706.tsv` before any future use. |
| Chain identity gate | Reconfirm `PROA = Gpa1-WT` and `PROB = Ste2` from selection-audit authority before mapping contact classes. |
| Contact class gate | Keep alpha5/eCT, last5, Ste2 clusters, broader 145-160 contacts, and frame-0 contact set separate. |
| Tool-input compatibility | Record whether the chosen future tool expects PDB, GRO, top, contact-map, or CG topology input. |
| Output generation gate | Contact maps, topology includes, CG coordinates, and AA conversions require a later approved phase. |

Recorded criterion: a future dry-build plan would have to state what input hashes and tool-source pins it requires, but this file still cannot claim those outputs exist.

## Evidence Block D: Direct Workflow Recheck

R4-GAP-01 was retained as a narrow source-recheck evidence row only.

Output target:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_YYYYMMDD.tsv
```

Keep a source only if it names at least three of these four fields:

| Required field | Why it matters |
|---|---|
| Object | GPCR-Galpha, Ste2-Gpa1, mini-G/Galpha, or receptor-G protein complex, not receptor-only. |
| Membrane setup | Lipid/water/ion or membrane model details. |
| Receptor-effector contact policy | Interchain treatment, restraints, Go contacts, elastic network, or equivalent. |
| Validation route | Backmapping, atomistic comparison, experimental comparison, or interface metric. |

Reject generic protein CG, receptor-only Go examples, and atomistic-only GPCR papers for this row.

2026-07-06 result: this metadata/title-screen recheck is recorded in:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.md
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.tsv
```

No source met the retention rule. Screened near-misses were atomistic mini-G/G-protein MD, GPCR-ligand MM/CG, GPCR-beta-arrestin analogs, receptor-lipid CG, receptor dimer/oligomer CG, and Ste2 structure seeds. The mini-G/Galpha Crossref/OpenAlex run had provider caveats, so PubMed exact probes were recorded as supplemental screening rather than exhaustive absence proof.

## Evidence Block E: OLIVES Manual Acquisition

R4-GAP-02 remains a manual-acquisition evidence gap. Boundary changes require a
new material review.

If a readable OLIVES article, SI, code, or official preprint becomes available, extract only:

- contact definition;
- Martini 3 compatibility;
- parameter choices;
- whether hydrogen-bond native contacts can help or harm receptor-Galpha interchain interpretation;
- limitations and examples.

Output target:

```text
experiments/chimeric-gpa1/literature/r4_olives_method_extraction_YYYYMMDD.md
```

## Non-Executable Reopen Conditions

These conditions are classification-only labels for a future R4 material-boundary
review:

| Result | Boundary implication |
|---|---|
| Source pins plus official/example smoke design are concrete, and direct workflow source is still absent | A new material addendum would be required before any approved install/run work. |
| Direct GPCR-Galpha or Ste2-Gpa1 CG workflow is retained | Method extraction and the material boundary would need to be rewritten around that source before any tool install. |
| Source pins remain weak or conflicting | R4 remains appendix/source-gate evidence with only specific manual-acquisition gaps. |
| Any step requires production files or E2 | The work requires a separate route. |

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_cg_to_aa_route_screen_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_local_toolchain_inventory_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_policy_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_inventory_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_map_feasibility_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_anchor_spec_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_non_chctrl_smoke_design_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.tsv`

## Referenced by / 被引

- Potential future R4-only output after the direct-workflow recheck evidence block: `r4_olives_method_extraction_YYYYMMDD.md` if OLIVES becomes accessible, or CG2AT official/example pointer acquisition for Smoke Object B, only if `docs/INDEX.md` reopens this lane.
- Historical/supporting R4 files may point here for validation-design evidence; the R4 material boundary is recorded in `r4_material_decision_addendum_20260706.md`.
- Shared router/log files use this file as supporting validation-design evidence and keep conditional protocol details here.
