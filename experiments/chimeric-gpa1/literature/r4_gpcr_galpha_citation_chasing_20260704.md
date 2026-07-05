# R4 GPCR-Galpha CG Citation Chasing

> Date: 2026-07-04
>
> Last updated: 2026-07-05
>
> Scope: targeted metadata and citation-chasing pass for direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha coarse-grained or Martini sources.
>
> Status: `screening_only`; this memo is not a build protocol, not an E2 approval package, and not a candidate-transfer rule.

## Full Text / Supplementary Methods Requested

Primary method papers requested on 2026-07-04 and supplied/read on 2026-07-05:

1. `10.1021/acs.jctc.3c01222` — "Switching Go-Martini for Investigating Protein Conformational Transitions and Associated Protein-Lipid Interactions".
2. `10.1016/j.str.2023.03.014` — "Transmembrane dimers of type 1 receptors sample alternate configurations: MD simulations using coarse grain Martini 3 versus AlphaFold2 Multimer".

Extraction status:

- Yang and Song 2024 is archived at `docs/papers/pdf/Yang2024-Switching-Go-Martini.pdf`, transcribed at `experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md`, and summarized at `docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md`.
- Sahoo et al. 2023 is archived at `docs/papers/pdf/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.pdf`, transcribed at `experiments/chimeric-gpa1/literature/fulltext_md/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.md`, and summarized at `docs/papers/summaries/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer-summary.md`.
- The extraction is incorporated into `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md` and `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`.
- Yang and Song 2024 reports separate supplementary simulation parameters and tutorial files; those supplementary files are not yet locally archived in this pass.

Optional lower-priority papers if accessible:

3. `10.3906/kim-1208-16` — "Exploring Distinct Binding Site Regions of beta2 Adrenergic Receptor via Coarse-Grained Molecular Dynamics Simulations".
4. `10.1080/00268976.2016.1234652` — "A simple coarse-grained model for interacting protein complex".

The first two are still the useful full-method bottlenecks for R4. The optional papers are receptor-only or generic protein-complex CG background; they should not be treated as direct GPCR-Galpha support unless their methods unexpectedly contain transferable checks.

For manual retrieval, prioritize the full article plus supplementary methods / supplementary information, especially tool versions, structure-bias settings, equilibration schedule, backmapping/atomistic comparison, and any membrane-protein complex setup notes.

## Existing Runs Rechecked

- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_query_gpcr_gprotein_cg_crossref/`: validated previously with 60 verified Crossref records; manual screening did not surface a direct GPCR-Galpha CG source.
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_query_heterotrimeric_gprotein_martini_crossref/`: validated previously with 60 verified Crossref records; no direct heterotrimeric G-protein Martini route was extracted.
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_query_receptor_gprotein_complex_martini_crossref/`: validated previously with 60 verified Crossref records; found the beta2AR receptor-only CG paper and a generic protein-complex CG background record.
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_query_galpha_cg_crossref/`: structurally valid run with 0 records and a recorded Crossref SSL/network failure. This is a caveat, not absence evidence.
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_seed_expansion_crossref/`: incomplete interrupted seed expansion; only `request.json` and `search_plan.md` exist, so it is not usable evidence.

## New Targeted Runs

New Crossref/OpenAlex metadata searches were attempted under:

- `r4_targeted_gpcr_gprotein_martini_openalex/`
- `r4_targeted_heterotrimeric_gprotein_martini_openalex/`
- `r4_targeted_minigs_martini_openalex/`
- `r4_targeted_ste2_gpa1_cg_openalex/`

Outcomes:

- `r4_targeted_gpcr_gprotein_martini_openalex/` passed structural validation with 0 records, but both Crossref and OpenAlex recorded HTTP 429 failures.
- The other three directories generated 25 records each, but `validate-run` failed because many usable-tier records lacked a year. They also recorded OpenAlex rate-limit failures.
- Manual inspection of their summaries showed mostly generic Martini/coarse-grained supplementary records and non-GPCR/non-Galpha records. These runs are not usable evidence for an R4 route.

## Additional Targeted Runs After User Request

After the user requested more directed GPCR-Galpha CG citation chasing, three narrower metadata searches were run and validated:

- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_active_gpcr_galpha_martini_20260704/`: 40 verified records; `validate-run` passed; OpenAlex recorded HTTP 429, so this is Crossref-dominated.
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_ste2_gpa1_martini_20260704/`: 40 verified records; `validate-run` passed; OpenAlex recorded HTTP 429, so this is Crossref-dominated.
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_minig_engineered_galpha_martini_20260704/`: 40 verified records; `validate-run` passed; OpenAlex recorded HTTP 429, so this is Crossref-dominated.

Manual screening of the top metadata again showed mostly generic Martini/coarse-grained records. One useful direct interface seed was found:

- `10.1016/j.bbamem.2017.09.022` — "GPCR-Galpha protein precoupling: Interaction between Ste2p, a yeast GPCR, and Gpa1p, its Galpha protein, is formed before ligand binding via the Ste2p C-terminal domain and the Gpa1p N-terminal domain".

This is direct Ste2p-Gpa1p / GPCR-Galpha interface context, not a Martini/CG route source. It should be read later for biology/interface grounding, not used to justify an R4 build.

## Cevheroglu 2017 Full-Text Extraction

User-supplied PDF read on 2026-07-05 and then archived in repo:

```text
docs/papers/pdf/Cevheroglu2017-Ste2-Gpa1-precoupling.pdf
experiments/chimeric-gpa1/literature/fulltext_md/Cevheroglu2017-Ste2-Gpa1-precoupling.md
experiments/chimeric-gpa1/literature/source_files.sha256
```

Extraction notes:

- The paper tests proximity between Gpa1p N-terminal residues and Ste2p C-terminal residues using BRET, with BiFC/confocal localization as a complementary in vivo interaction readout.
- The BRET constructs place RLuc at Ste2p position 304 and EGFP at Gpa1p N-terminal positions 10, 36, and 67; the BiFC construct uses Gpa1p position 10.
- Reported result: constitutive, position-dependent BRET occurs without alpha-factor; alpha-factor stimulation does not produce a significant BRET increase or decrease. BiFC detects the Ste2p-Gpa1p heterodimer on ER during biosynthesis and on plasma membrane.
- Interpretation for this project: the source supports Ste2p-Gpa1p interface biology and ligand-independent precoupling. It does not contradict C-terminal Galpha chimera logic because the paper itself frames Galpha C-terminus/alpha5 and other regions as known GPCR contact surfaces, and later notes that molecular rearrangement may occur near the Galpha C-terminus.
- Transfer caveat: this is weak background for actual chimeric candidates because those targets use Gpr2/Gpr3/GprC rather than Ste2.
- Project boundary: this is not a Martini/coarse-grained route source, not an MD setup source, not an atom-selection or restraint source, and not a candidate-replacement source.

Design implication:

- Our C-terminal chimera route keeps the yeast Gpa1 N-terminus intact while changing the C-terminal/eCT-alpha5-beta6 region used for receptor-coupling specificity. For Gpr2/Gpr3/GprC candidates, Cevheroglu 2017 should be treated only as a Ste2-Gpa1 control/background note and a reminder not to remove native yeast Gpa1 N-terminal architecture.

A seed list was written at:

```text
experiments/chimeric-gpa1/literature/r4_gpcr_galpha_cg_seed_chase_seeds_20260704.csv
```

The seed expansion run was attempted at:

```text
experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_gpcr_galpha_cg_seed_expansion_20260704/
```

It was interrupted after a long Crossref HTTPS relation lookup stall. Only `request.json` and `search_plan.md` exist, so this directory is not usable evidence.

Two subsequent PubMed E-utilities exact-query attempts were not executed because the sandbox escalation auto-review timed out. This is an operational limitation, not a literature result.

## P0047 / P0040 Full-Text Extraction

User-supplied PDFs read on 2026-07-05 and archived in repo:

```text
docs/papers/pdf/Yang2024-Switching-Go-Martini.pdf
experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md
docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md

docs/papers/pdf/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.pdf
experiments/chimeric-gpa1/literature/fulltext_md/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.md
docs/papers/summaries/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer-summary.md
```

Extraction notes:

- Yang and Song 2024 supports Martini 3 plus switching Go-like structure-bias vocabulary in explicit water/lipid systems. It records `martinize2.py`, OV/rCSU Go contacts, `create_goVirt.py`, `insane.py`, replicate schedules, and explicit limitations around non-quantitative free energy/kinetics and manually controlled switching.
- Sahoo et al. 2023 supports Martini 3 TM-dimer validation vocabulary, including elastic-network secondary-structure stabilization, `insane.py` DMPC setup, 4 x 4 us replicates, Backward/atomistic comparison, and convergence/state-transition checks.
- Neither paper is a direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha CG route source. They do not support `chctrl` build, candidate replacement, Ch-1/Ch-2/Ch-4 action, E2 execution, or compute-saving success claims.

## PubMed E-utilities Probes

Because Crossref/OpenAlex were rate-limited, PubMed E-utilities was used as a supplemental metadata probe. The Python urllib attempt failed with an SSL EOF error, so `curl` was used for the same query class.

Query outcomes:

- Broad query for `(GPCR OR G protein-coupled receptor) AND (Galpha OR G alpha OR G protein OR mini-Gs) AND (Martini OR coarse-grained) AND molecular dynamics`: 54 PubMed records. The top returned records were mostly GPCR lipid, activation, ligand, or receptor-only MD/CG papers. Notable entries include the final article for "Human class B1 GPCR modulation by plasma membrane lipids" with DOI `10.1038/s42003-025-09445-2`, and P0057 with DOI `10.1039/d5cp02918j`.
- Exact Galpha/GPCR/Martini-or-CG/MD query: 0 PubMed records.
- Exact heterotrimeric G-protein/Martini-or-CG/MD query: 0 PubMed records.
- `mini-Gs` plus Martini/CG/MD query: 4 PubMed records, including Renault et al. 2019 Mini-G protein MD and A2A/A3 receptor-lipid or receptor-state records. These are not CG-Galpha route sources.
- Ste2/Gpa1 plus Martini/CG/MD query: 1 PubMed record, Mohanty et al. 2025, "Deep learning reveals endogenous sterols as allosteric modulators of the GPCR-Galpha interface" (`10.7554/eLife.106397`). PubMed abstract metadata explicitly mentions Ste2p-Gpa1p and molecular simulations. The repo already downgraded this source to Ste2p-Gpa1p interface/allosteric context, not a full-complex MD protocol and not a CG route source.

## Current Interpretation

This pass found one useful update and one useful reminder:

- The GPCR-lipid record P0038 has a final article DOI, `10.1038/s42003-025-09445-2`; it remains receptor/lipid CG context only.
- Mohanty et al. 2025 is a direct Ste2p-Gpa1p / GPCR-Galpha interface citation seed, but it is already known in the repo and does not support a Martini/CG replacement route.
- Cevheroglu et al. 2017 has now been full-text screened from the user-supplied PDF. It strengthens Ste2p-Gpa1p precoupling/interface context, but transfer to Gpr2/Gpr3/GprC candidates is weak; it remains non-support for R4 buildability.
- Yang and Song 2024 and Sahoo et al. 2023 are now full-text screened. They move P0047/P0040 out of the unread queue, but the extraction still does not define a buildable R4 `chctrl` object contract.

This pass did not find a direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha coarse-grained route source. R4 therefore remains a `screening_only` source gate. The next useful inputs are Yang and Song 2024 supplementary files, if accessible, plus continued direct GPCR-Galpha / Ste2-Gpa1 CG citation chasing.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/chimeric-gpa1/literature/chimeric_md_literature_matrix.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_query_receptor_gprotein_complex_martini_crossref/`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_gpcr_gprotein_martini_openalex/`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_heterotrimeric_gprotein_martini_openalex/`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_minigs_martini_openalex/`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_ste2_gpa1_cg_openalex/`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_active_gpcr_galpha_martini_20260704/`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_ste2_gpa1_martini_20260704/`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_targeted_minig_engineered_galpha_martini_20260704/`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_cg_seed_chase_seeds_20260704.csv`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_gpcr_galpha_cg_seed_expansion_20260704/search_plan.md`
- `docs/papers/pdf/Cevheroglu2017-Ste2-Gpa1-precoupling.pdf`
- `experiments/chimeric-gpa1/literature/fulltext_md/Cevheroglu2017-Ste2-Gpa1-precoupling.md`
- `experiments/chimeric-gpa1/literature/source_files.sha256`
- `docs/papers/pdf/Yang2024-Switching-Go-Martini.pdf`
- `experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md`
- `docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md`
- `docs/papers/pdf/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.pdf`
- `experiments/chimeric-gpa1/literature/fulltext_md/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.md`
- `docs/papers/summaries/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer-summary.md`
- PubMed E-utilities metadata for PMIDs `41507501`, `41090227`, `30940903`, and `41359750`.

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`
- `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md`
- `docs/logs/2026-07-05.md`
- `docs/logs/2026-07-04.md`
