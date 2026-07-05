# R4 Direct GPCR-Galpha CG Source Chase

> Date: 2026-07-05
>
> Scope: Pass 1 source-chase output for the R4 `chctrl`-first coarse-grained / multiscale route.
>
> Status: action-planning memo. This file decides what to read next; it is not a build protocol.

## Project Question

The useful question after Yang2024 and Sahoo2023 is no longer "is Martini generally relevant?". It is:

Can we find enough GPCR-Galpha / protein-complex CG practice to write a `chctrl`-first R4 object contract within the iGEM2026 drylab timeline?

Current answer: **one focused extraction pass is still worth doing, but the next work is method-source acquisition, not `chctrl` build.**

## What Was Searched

Local metadata runs checked during this pass:

| Run | Purpose | Result for R4 |
|---|---|---|
| `research_runs/system_reduction_20260705/r4_direct_gpcr_galpha_cg_20260705/` | direct GPCR-Galpha / GPCR-G protein CG or multiscale workflows | 25 verified records; top hits were generic Martini protocol, GPCR Dock, PDB structure records, or receptor-only/background. No direct route was retained. OpenAlex recorded HTTP 503. |
| `research_runs/system_reduction_20260705/r4_ste2_gpa1_cg_20260705/` | Ste2/Gpa1 + CG/Martini query | 0 records; Crossref 429, OpenAlex 503, and empty-result caveat. Treat as a retry/manual-search item, not proof of absence. |
| `research_runs/system_reduction_20260705/r4_martini_complex_interface_bias_20260705/` | Martini protein-complex, Go-like, OLIVES, interchain/contact-bias methods | 25 verified records; useful seed is OLIVES final/preprint plus possible Go-Martini protein-complex leads; many automatic hits are PDB/non-project noise. OpenAlex recorded HTTP 503. |
| `research_runs/system_reduction_20260705/r4_martini_backmapping_revalidation_20260705/` | Martini backmapping / atomistic revalidation | 0 records in the API run; Crossref rate-limit/empty-result caveat. Manual DOI seed queue is still needed. |
| `research_runs/system_reduction_20260705/r4_gomartini_olives_oligomers_20260705/` | narrow GoMartini / OLIVES / OliGoMers metadata check | 40 verified Crossref records; no provider failures; reinforces OLIVES as a must-read seed but still needs manual DOI seed handling for GoMartini3 and OliGoMers. |

Manual DOI metadata checked during this pass:

- `10.1038/s41467-025-58719-0` — "GōMartini 3: From large conformational changes in proteins to environmental bias corrections" (*Nature Communications*, 2025).
- `10.1021/acs.jctc.4c00677` — "Martini 3 OliGo̅mers: A Scalable Approach for Multimers and Fibrils in GROMACS" (*Journal of Chemical Theory and Computation*, 2024).
- `10.1021/acs.jctc.4c00553` — "OLIVES: A Go̅-like Model for Stabilizing Protein Structure via Hydrogen Bonding Native Contacts in the Martini 3 Coarse-Grained Force Field" (*Journal of Chemical Theory and Computation*, 2024).
- `10.1021/acs.jpcb.4c08622` — "Enhanced Exploration of Protein Conformational Space through Integration of Ultra-Coarse-Grained Models to Multiscale Workflows" (*Journal of Physical Chemistry B*, 2025).
- `10.1021/acs.jctc.2c00168` — "Asynchronous Reciprocal Coupling of Martini 2.2 Coarse-Grained and CHARMM36 All-Atom Simulations in an Automated Multiscale Framework" (*Journal of Chemical Theory and Computation*, 2022).

The seed table for the next extraction pass is:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv
```

## Meaning for This Project

Yang2024 now has a clear role: it gives R4 the vocabulary for a state-pair, Go-contact, Martini 3, membrane/water/ion, topology-switching workflow. Its project value is not "we can build `chctrl` now"; its value is that it tells us exactly what the next sources must resolve.

The missing pieces are practical:

1. **Interface/contact policy**: whether receptor-Galpha interchain contacts should be biased, excluded, weakened, or allowed to drift in a CG model.
2. **Protein-complex bias choice**: GoMartini3 vs OLIVES vs OliGoMers vs elastic-network style stabilization.
3. **Backmapping/revalidation**: how a cheap CG screen returns to atomistic `chctrl` metrics instead of becoming a disconnected coarse-grained story.
4. **Timeline triage**: if the next method-source extraction cannot answer 1-3, R4 should stop before local build planning and drylab effort should move to mutant GPR pretests, ODE/reporter, or HP/economic model deliverables.

## Recommended Action Lane

Use **R4-B focused extraction** for the next pass:

- no direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG workflow has been found in the current metadata pass;
- enough protein-complex and structure-bias method seeds exist to do one short extraction pass;
- the output should be an R4 object-contract decision, not a build.

Decision after the next pass:

| If the extraction finds... | Then do... |
|---|---|
| clear interchain/contact policy plus a backmapping/revalidation path | draft a `chctrl`-first R4 object contract |
| method support but no receptor-Galpha policy | keep R4 as design-only and do not build |
| only generic protein/receptor-only support | park R4 for 2026 and move MD work toward mutant GPR pretests |
| provider/access blocks remain dominant | write a short manual acquisition queue and stop broad scraping |

## Next Extraction Queue

Read in this order:

1. `GoMartini3_2025` (`10.1038/s41467-025-58719-0`) — extract how the updated GoMartini method handles protein conformational transitions, environmental bias corrections, and limitations.
2. `OLIVES_2024` (`10.1021/acs.jctc.4c00553`) — extract whether OLIVES changes the need for quaternary structure bias and whether it handles protein-complex contact choices better than ordinary GoMartini.
3. `OliGoMers_2024` (`10.1021/acs.jctc.4c00677`) — extract multimer/interchain handling and whether its GROMACS workflow offers a practical object-contract pattern.
4. `Lopez2022_CG_AA_Coupling` (`10.1021/acs.jctc.2c00168`) and `Aydin2025_UCG_Multiscale` (`10.1021/acs.jpcb.4c08622`) — extract only the CG-to-AA bridge and revalidation logic.
5. `Mohanty2025_Ste2_Gpa1` (`10.7554/eLife.106397`) and existing `Cevheroglu2017` notes — use only for Ste2/Gpa1 interface context if object-contract drafting starts.

Stop condition: after these sources, write a one-page R4 decision package. Do not start a `chctrl` build plan unless that package can name the simulated object, structure-bias model, receptor-Galpha contact policy, backmapping/revalidation gate, and comparison metrics.

## References / 所引

- `codex/docs/plans/chimeric-gpa1-r4-new-source-acquisition-plan.md`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260705/r4_direct_gpcr_galpha_cg_20260705/run_summary.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260705/r4_ste2_gpa1_cg_20260705/run_summary.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260705/r4_martini_complex_interface_bias_20260705/run_summary.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260705/r4_martini_backmapping_revalidation_20260705/run_summary.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260705/r4_gomartini_olives_oligomers_20260705/run_summary.md`
- `docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `docs/logs/2026-07-05.md`
