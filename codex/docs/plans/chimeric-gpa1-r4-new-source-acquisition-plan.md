# Chimeric Gpa1 R4 New-Source Acquisition Plan

> Date: 2026-07-05
>
> Status: active literature-acquisition and next-action plan for R4.
>
> Purpose: turn the Yang2024/Sahoo2023 method read into a concrete next pass that can decide what R4 should do for the iGEM2026 drylab MD route.

## Working Question

Can R4 become a useful `chctrl`-first coarse-grained screening workflow for the chimeric Gpa1 project in the iGEM2026 timeline?

The next pass should not repeat generic Martini reading. It should look for the missing project-useful materials:

1. direct or near-direct GPCR-Galpha coarse-grained workflows;
2. receptor-Galpha or Ste2-Gpa1 interface preservation methods;
3. Martini protein-complex quaternary-bias practice;
4. backmapping and atomistic revalidation routes that could connect a cheap screen back to the existing atomistic `chctrl` story;
5. enough negative search information to decide whether R4 is worth more time before Wiki freeze.

## Decision Target

At the end of this plan, write one short decision package that chooses one of these actions:

- **Draft R4 object contract**: enough material exists to write a `chctrl`-first CG screening object contract, but not to build yet.
- **Prepare local dry-build plan**: enough material exists to design local files and checks for `chctrl`, still without E2 launch.
- **Park R4 for 2026**: direct sources are too weak for the project timeline; keep Yang2024/Sahoo2023 as background and move MD effort toward mutant GPR pretests or other drylab outputs.

## Status Update: 2026-07-05 Pass 1

Pass 1 metadata/source-chasing has produced its first memo and seed table:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv
```

Current action lane: **R4-B focused extraction**.

Meaning for the drylab workflow: keep R4 alive for one short method-source extraction pass, but spend that pass on the exact missing object-contract fields:

- receptor-Galpha or protein-complex interchain/contact-bias policy;
- GoMartini3 / OLIVES / OliGoMers structure-bias choice;
- CG-to-AA backmapping or atomistic revalidation path;
- final decision on object-contract draft versus parking R4 for 2026.

The next useful work is not another broad Martini search. It is method extraction from the seed table above, then a one-page R4 decision package.

## Source Targets

### A. Direct GPCR-Galpha / Ste2-Gpa1 CG Sources

Goal: find papers, tutorials, preprints, supplementary methods, or public workflows that actually simulate a GPCR with a G protein or yeast Ste2/Gpa1-like complex at CG or multiscale resolution.

Search strings:

- `"Martini" "GPCR" "G protein"`
- `"coarse-grained" "GPCR" "G protein complex"`
- `"Martini 3" "GPCR" "Galpha"`
- `"Ste2" "Gpa1" "coarse-grained"`
- `"Ste2" "Gpa1" "Martini"`
- `"mini-Gs" "Martini" "GPCR"`
- `"G protein alpha5" "coarse-grained"`
- `"GPCR-G protein" "backmapping" "Martini"`

Search locations:

- PubMed / Europe PMC
- Crossref and OpenAlex metadata
- Semantic Scholar only when rate limits allow
- GPCRmd, GPCRdb, GPCRsignal, and related method/reference pages
- Martini community tutorials, GitHub examples, and supplementary archives linked from papers

Output:

- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- optional seed table: `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`

### B. Interface Preservation and Quaternary-Bias Methods

Goal: decide how a future R4 object would handle receptor-Galpha interchain contacts instead of leaving that choice implicit.

Questions to answer:

- In Martini protein-complex work, when are interchain contacts included in Go/elastic/OLIVES-like bias?
- Are quaternary contacts biased, excluded, weakened, or validated by replicate exchange between states?
- How do papers detect that a protein-protein interface is artificially frozen versus physically retained?
- Are there examples where CG complex results are only used for ranking or path generation before atomistic validation?

Search strings:

- `"GoMartini" "protein complex" interface`
- `"Martini 3" "protein complex" "elastic network" interface`
- `"OLIVES" "Martini" "protein complex"`
- `"coarse-grained" "protein-protein interface" "Martini"`
- `"quaternary structure" "Martini 3" "protein complex"`
- `"Go-like" "interchain contacts" "Martini"`

Output:

- add a section to `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- add rows or update notes in `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`

### C. Backmapping and Atomistic Revalidation

Goal: define how a cheap CG screen would connect back to atomistic interpretation.

Questions to answer:

- Which backmapping workflow is most commonly paired with Martini 3 membrane proteins?
- How much atomistic relaxation is normally required before measuring interface geometry?
- Which comparison metrics survive CG-to-AA conversion: alpha5/eCT contacts, BSA, COM distance, TM packing, membrane embedding, junction RMSF?
- Is there an example of GPCR or protein-complex CG ranking followed by atomistic refinement?

Search strings:

- `"Martini" "backward" "membrane protein" "GPCR"`
- `"CG2AT" "Martini" "GPCR"`
- `"backmapping" "coarse-grained" "protein-protein interface"`
- `"coarse-grained screening" "atomistic refinement" "GPCR"`
- `"Martini 3" "backmapping" "protein complex"`

Output:

- a short validation-gate draft under the R4 method extraction memo;
- if strong enough, a separate `r4_cg_backmapping_validation_notes_20260705.md`.

### D. Ste2-Gpa1 Biology Bridge

Goal: make sure any R4 design stays connected to the actual yeast sensor chassis instead of becoming a generic beta2AR exercise.

Materials to chase:

- Ste2-Gpa1 precoupling and interface papers already surfaced in repo records;
- papers on Gpa1 N-terminus, C-terminus, alpha5/eCT coupling, and yeast G protein membrane localization;
- any structure or model that constrains the Ste2 intracellular face and Gpa1 contact geometry.

Output:

- update `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`;
- add only project-useful bridge notes, not a full yeast signaling review.

### E. Timeline Triage

Goal: keep this work pointed at iGEM2026 deliverables.

After the searches above, classify R4 into one of four lanes:

| Lane | Meaning | Next project action |
|---|---|---|
| R4-A | direct GPCR-Galpha CG workflow found | write object contract and decide whether local dry-build planning is worth it |
| R4-B | no direct workflow, but enough protein-complex/interface CG practice | object-contract draft only; do not build until the receptor-Galpha contact policy is explicit |
| R4-C | only generic receptor-only or protein-only method support | keep as background, shift MD effort to mutant GPR pretests and other drylab outputs |
| R4-D | source search remains inconclusive because access/rate-limit blocks retrieval | make a short manual-acquisition queue and stop before another broad metadata scrape |

## Execution Sequence

### Pass 1: Metadata and Seed Search

- Run the query families in A-C.
- Save query strings and top hits, including null results for direct GPCR-Galpha terms.
- Deduplicate by DOI/title.
- Mark each hit as direct, close analog, method-only, background-only, or reject.

Target output: source chase memo plus seed table.

### Pass 2: Full-Text and Supplement Triage

- Prioritize 6-10 items that can actually change the R4 action lane.
- For each, collect DOI, PDF/supplement pointer if available, method location, and why it matters.
- Do not spend time summarizing papers that cannot affect R4 action.

Target output: updated literature matrix rows and a short ranked reading queue.

### Pass 3: Project Translation

- Convert the useful materials into R4 object-contract fields:
  - simulated object;
  - force field and tool versions;
  - membrane/ion/water setup;
  - receptor-Galpha contact policy;
  - state-pair or starting-structure policy;
  - backmapping/revalidation policy;
  - metrics that can be compared with atomistic `chctrl`.
- Keep source-faithful notes in literature files and project translation in the R4 extraction memo.

Target output: object-contract draft section or a clear decision to park R4.

### Pass 4: Next Drylab Action

Write a one-page decision package:

- what was found;
- which lane R4 is in;
- whether the next drylab action is R4 object-contract drafting, local dry-build planning, mutant GPR MD pretest, ODE/reporter work, or HP/economic model work;
- what the next session should open first.

## Immediate Next Session Prompt

Use this as the next working instruction:

```text
Continue /Users/roy/Documents/drylab iGEM2026 drylab goal. Use drylab-project, read AGENTS.md and docs/DOCMAP.md, then follow codex/docs/plans/chimeric-gpa1-r4-new-source-acquisition-plan.md plus experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md. Do not SSH, do not run E2, do not build chctrl or candidates. Start from experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv and extract GoMartini3, OLIVES, OliGoMers, then Lopez2022/Aydin2025 validation bridge. The output should be an R4 decision package: draft object contract, keep design-only, park R4 for 2026, or write a manual acquisition queue.
```

## References / 所引

- `docs/INDEX.md`
- `codex/docs/plans/chimeric-gpa1-system-reduction-exploration.md`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md`
- `docs/logs/2026-07-05.md`

## Referenced by / 被引

- `codex/docs/plans/README.md`
- `docs/INDEX.md`
- `docs/logs/2026-07-05.md`
