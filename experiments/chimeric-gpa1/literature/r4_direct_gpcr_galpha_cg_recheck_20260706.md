# R4 Direct GPCR-Galpha CG Recheck

> Date: 2026-07-06
>
> Status: R4-GAP-01 recheck complete at metadata/title-screen level.
>
> Scope: direct GPCR-Galpha / Ste2-Gpa1 / mini-G-Galpha / receptor-G protein coarse-grained or Martini workflows only. Build, production, E2, and candidate-system work require separate route approval.

## Question

Can the 2026-07-05 R4 no-go be reopened by a direct source that names a receptor-G protein coarse-grained workflow?

For this pass, a retained source had to name at least three of four fields:

| Field | Required content |
|---|---|
| Object | GPCR-Galpha, Ste2-Gpa1, mini-G/Galpha, or receptor-G protein complex. |
| Membrane setup | Lipid/water/ion or explicit membrane model details. |
| Receptor-effector contact policy | Interchain restraints, Go/native contacts, elastic network, contact filtering, or equivalent. |
| Validation route | Backmapping, atomistic comparison, experimental comparison, or interface metric. |

## Search Coverage

Temporary API outputs were written under `/private/tmp/drylab_r4_direct_recheck_20260706/`. The repo-retained screened record is:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.tsv
```

Searches run:

| Scope | Providers | Result |
|---|---|---|
| direct GPCR-Galpha + Martini/CG + membrane | Crossref/OpenAlex | Validated; 43 records; no provider failures. Manual screen retained no direct workflow. |
| Ste2-Gpa1 + Martini/CG/MD | Crossref/OpenAlex | Validated; 40 records; no provider failures. Only Ste2 PDB structure records surfaced as target-like screening-pool items. |
| receptor-G protein complex + Martini/CG + validation | Crossref/OpenAlex | Validated; 80 records; no provider failures. Manual screen found analog/receptor-only classes, not GPCR-Galpha CG. |
| mini-Gs / engineered Galpha + Martini/CG/MD | Crossref/OpenAlex | Combined run hit Crossref HTTP 429; OpenAlex-only run returned 0 records with SSL handshake timeout. Treated as caveat, not absence proof. |
| PubMed GPCR-Galpha + Martini/CG/MD | PubMed E-utilities | 51 title-level records; top records were receptor-lipid CG, receptor AA/CG comparison, GPCR-ligand MM/CG, receptor oligomer CG, or atomistic mini-G/G-protein papers. |
| PubMed Ste2-Gpa1 + Martini/CG/MD | PubMed E-utilities | 0 records. |
| PubMed mini-G + Martini/CG/MD | PubMed E-utilities | 11 title-level records; relevant rows were atomistic Mini-G or engineered G-protein coupling simulations, not Martini/CG workflows. |

## Screened Candidate Classes

No candidate met the retention rule.

| Class | Representative records | Decision |
|---|---|---|
| Direct mini-G object but atomistic MD | A2A receptor/Mini-Gs MD (`10.1038/s41598-019-41980-x`); engineered mini-G histamine receptor GaMD (`10.3390/ijms221810047`) | Useful conceptual analogs, but not CG/Martini workflows. |
| GPCR/ligand MM/CG | Hybrid MM/CG Webserver (`10.3389/fmolb.2020.576689`) | GPCR-ligand only; no receptor-Galpha object or contact policy. |
| GPCR-beta-arrestin analog | beta2AR-beta-arrestin2 (`10.3389/fcell.2021.807913`) | Close GPCR-effector analog, but target object is beta-arrestin, not Galpha. |
| GPCR receptor-lipid CG | class B1 GPCR lipids (`10.1038/s42003-025-09445-2`); serotonin1A PIP CG (`10.1021/acschemneuro.5c00455`) | Receptor-lipid only. |
| GPCR receptor dimer/oligomer CG | CXCR4 dimer (`10.1371/journal.pcbi.1005169`); secretin receptor oligomer (`10.1038/s42003-025-08374-4`) | Receptor-receptor interfaces only. |
| Ste2 structural seeds | PDB 7AD3, 7QB9, 7QA8 | Structural anchors only; no CG method. |

## Result

R4-GAP-01 is now sharpened:

```text
direct GPCR-Galpha / Ste2-Gpa1 CG workflow rechecked -> no retained direct source
```

This exact evidence row left the R4 material boundary unchanged. The remaining
source/material rows are conditional future evidence items:

1. R4-GAP-02: OLIVES method-body acquisition if a readable article, SI, code, or official preprint source becomes available.
2. Smoke Object B: CG2AT official/example input-output pointer acquisition before any approved install/run.
3. A future dated material-boundary review through `docs/INDEX.md`.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_tool_source_pin_manifest_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_non_chctrl_smoke_design_20260706.md`
- PubMed E-utilities title/abstract metadata for PMIDs `33102525`, `30940903`, `34576210`, `41782363`, `41507501`, `41090227`, and `40596640`.

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_recheck_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
- Potential future R4-only artifact, only if `docs/INDEX.md` reopens this lane:
  `r4_olives_method_extraction_YYYYMMDD.md` or a CG2AT official/example pointer
  note for `r4_non_chctrl_smoke_design_20260706.md`.
