# R4 Direct GPCR-Galpha CG Source Chase

> Date: 2026-07-05
>
> Scope: Pass 1 source-chase output for the R4 `chctrl`-first coarse-grained / multiscale route.
>
> Status: completed source-chase memo. This file records searched and extracted source evidence; build protocol authority requires a later material-boundary approval.

## Project Question

After Yang2024 and Sahoo2023, the useful R4 question is:

Can we find enough GPCR-Galpha / protein-complex CG practice to write a `chctrl`-first R4 object contract within the iGEM2026 drylab timeline?

Answer after the focused extraction pass: **R4 could proceed as a design-only
`chctrl` object-contract draft. `chctrl` build/run work requires a later
material-boundary approval.**

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

The seed table for the historical 2026-07-05 extraction pass is:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv
```

## Meaning for This Project

Yang2024 now has a clear role: it gives R4 the vocabulary for a state-pair,
Go-contact, Martini 3, membrane/water/ion, topology-switching workflow. Its
project value is a precise list of what the next sources must resolve before any
`chctrl` build route.

The missing pieces are practical:

1. **Interface/contact policy**: whether receptor-Galpha interchain contacts should be biased, excluded, weakened, or allowed to drift in a CG model.
2. **Protein-complex bias choice**: GoMartini3 vs OLIVES vs OliGoMers vs elastic-network style stabilization.
3. **Backmapping/revalidation**: how a cheap CG screen returns to atomistic `chctrl` metrics instead of becoming a disconnected coarse-grained story.
4. **Timeline triage**: local build planning requires answers to 1-3; other
   project continuations route through `docs/INDEX.md`, outside this memo.

## Historical Action Lane

The resolved lane after the focused seed pass was **R4-B design-only
object-contract draft**:

- the current metadata pass retained no direct GPCR-Galpha / Ste2-Gpa1 /
  chimeric Galpha CG workflow;
- enough protein-complex and structure-bias method seeds were extracted to write
  a design contract;
- the next historical R4 output from that pass was an object-contract draft;
  build approval requires a later material-boundary decision.

Historical decision rule after this pass:

| If the extraction finds... | Then do... |
|---|---|
| clear interchain/contact policy plus a backmapping/revalidation path | draft a `chctrl`-first R4 object contract |
| method support but no receptor-Galpha policy | keep R4 as design-only and do not build |
| only generic protein/receptor-only support | park R4 for 2026 and select any non-R4 continuation through `docs/INDEX.md`, outside this memo |
| provider/access blocks remain dominant | write a short manual acquisition queue and stop broad scraping |

## Pass 2 Update: GoMartini3 Extracted

`GoMartini3_2025` (`10.1038/s41467-025-58719-0`) was extracted from the Nature Communications article HTML and Supporting Information PDF on 2026-07-05. The method details are incorporated into:

```text
experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md
```

Project-useful result:

- GoMartini3 gives this R4 pass concrete contact-policy vocabulary: OV/rCSU contact maps, `Martinize2 -go`, `-go-eps`, contact distance bounds, graph-distance filtering, non-bonded exclusions for Gō-linked backbone beads, system-specific epsilon calibration, and chain/molecule naming requirements for multi-protein systems.
- Its protein-complex examples explicitly include inter-protein interface contacts, so a future `chctrl` object contract must state whether receptor-Galpha contacts are included, excluded, weakened, or used only for a control design.
- It also warns that many-copy systems can be distorted by shared Gō bonds unless distinct protein models are used. For this project, the useful translation is small-complex chain uniqueness.

Evidence gaps:

- Direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha workflow support is still missing.
- Backmapping/revalidation gate definition still requires a separate source-backed decision.
- R4 `chctrl` build planning requires the current material-boundary gate before execution.

At that point, the remaining queue item was to extract `OLIVES_2024`, then
`OliGoMers_2024`, then the minimal Lopez2022/Aydin2025 CG-to-AA bridge.

## Pass 3 Update: Focused Method Seeds Resolved

The exact seed queue was continued on 2026-07-05 and written back to:

```text
experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md
```

Result:

- `OLIVES_2024` method extraction remains blocked. ACS final article and ChemRxiv preprint landing pages both returned HTTP 403 Cloudflare challenge responses; Crossref metadata was accessible and confirms the DOI, title, and preprint relation. Status: `manual_acquisition`.
- `OliGoMers_2024` was extracted from Europe PMC full-text XML. It provides the current best practical vocabulary for R4 interchain policy: split intra/intermolecular Go contacts, tune separate `epsilon_intra` / `epsilon_inter`, compare against atomistic RMSF/RMSD/native contacts, and avoid overstrong interchain bias that turns interfaces glass-like.
- `Lopez2022_CG_AA_Coupling` was extracted from an OSTI-hosted PDF. It provides the current best CG-to-AA bridge vocabulary: selected CG snapshots, automated conversion, stereochemistry failure checks, AA relaxation, short AA production, on-the-fly RMSD/orientation/distance analyses, and warnings about losing intermolecular contacts during conversion.
- `Aydin2025_UCG_Multiscale` was extracted from Europe PMC full-text XML. It is useful as "cheap UCG proposes Martini starts" workflow language, but it is too ML/training-data heavy to become an immediate iGEM2026 chimeric route.

Decision after this pass:

- The historical lane selected from this pass was **R4-B design-only object-contract draft**.
- `chctrl` build planning requires a later material-boundary approval.
- The `chctrl`-first object-contract draft and local material decision have now been written.
- This source-chase memo supplies evidence to the R4 material boundary and
  supporting design notes. Current routing starts from `../../../docs/INDEX.md`
  and the R4 material-boundary records.

## Historical Extraction Queue

This queue records the source-chase order used by this memo. Current work
orders start from the active R4 material-boundary records:

1. `GoMartini3_2025` (`10.1038/s41467-025-58719-0`) — extracted 2026-07-05; use as contact-policy vocabulary. Direct GPCR-Galpha support requires separate evidence.
2. `OLIVES_2024` (`10.1021/acs.jctc.4c00553`) — `manual_acquisition`; revisit only if article/SI/code becomes accessible.
3. `OliGoMers_2024` (`10.1021/acs.jctc.4c00677`) — extracted 2026-07-05; use for interchain Go policy and overbias-risk vocabulary.
4. `Lopez2022_CG_AA_Coupling` (`10.1021/acs.jctc.2c00168`) and `Aydin2025_UCG_Multiscale` (`10.1021/acs.jpcb.4c08622`) — extracted 2026-07-05; use Lopez as the CG-to-AA bridge and Aydin as optional workflow vocabulary.
5. `Mohanty2025_Ste2_Gpa1` (`10.7554/eLife.106397`) and existing `Cevheroglu2017` notes — use for Ste2/Gpa1 interface context if object-contract drafting starts.

Stop condition reached for the source queue. The one-page decision package and
the design-only `chctrl` object contract have now been written. A `chctrl` build
plan requires a later local dry-build planning package that names exact input
snapshots, toolchain versions, receptor-Galpha contact policy, dry-build checks,
and stop conditions.

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
- `https://www.nature.com/articles/s41467-025-58719-0`
- `https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-58719-0/MediaObjects/41467_2025_58719_MOESM1_ESM.pdf`
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11391574/fullTextXML`
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12105037/fullTextXML`
- `https://doi.org/10.1021/acs.jctc.2c00168`
- `https://doi.org/10.1021/acs.jctc.4c00553`
- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `docs/logs/2026-07-05.md`
- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`
