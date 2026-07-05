# R4 Coarse-Grained / Multiscale Method Extraction

> Date: 2026-07-04
>
> Last updated: 2026-07-05
>
> Scope: local source-gate extraction for the chimeric Gpa1 R4 route family after the R1-Z downgrade.
>
> Status: `screening_only`; this memo is not a build protocol, not an E2 approval package, and not a candidate-transfer rule.

## Question

Can the next chimeric compute-reduction route move from R1 Z-only box shaving to a coarse-grained or multiscale `chctrl`-first route?

The answer after this pass is: **not yet as a buildable route**. The sources support continued R4 source-gate work, but they do not yet support a direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha coarse-grained replacement route.

## Inputs Read

- Existing R4 screen: `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- Existing run: `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260703/martini_gpcr_gprotein/`
- New directed run: `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_direct_gpcr_gprotein_cg/`
- Follow-up citation chase: `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- Additional targeted runs: `r4_targeted_active_gpcr_galpha_martini_20260704/`, `r4_targeted_ste2_gpa1_martini_20260704/`, and `r4_targeted_minig_engineered_galpha_martini_20260704/`
- Literature matrix: `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- Route-family memo: `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`
- Martini 3 protein tutorial: `https://cgmartini.nl/docs/tutorials/Martini3/ProteinsI/`
- Nature Communications article pages for DOI `10.1038/s41467-025-59842-8` and DOI `10.1038/s41467-020-17437-5`
- Crossref DOI metadata for the records listed below
- User-supplied full-text PDFs for DOI `10.1021/acs.jctc.3c01222` and DOI `10.1016/j.str.2023.03.014`, archived under `docs/papers/pdf/`
- User-supplied Yang and Song 2024 supplementary PDF and tutorial zip, archived under `experiments/chimeric-gpa1/literature/source_attachments/`; method-relevant details from the SI PDF and tutorial archive were extracted on 2026-07-05.
- Markdown transcriptions and paper summaries for Yang and Song 2024 and Sahoo et al. 2023

## Extracted Support

### Martini protein modeling

The Martini 3 protein tutorial supports a general protein-CG workflow with mapping and required protein structure bias. It identifies structure-bias options including elastic networks, GoMartini, and OLIVES, and notes that the choice affects tertiary and quaternary stabilization.

Project implication:

- R4 cannot be defined by "use Martini" alone.
- A `chctrl` R4 object contract must specify the protein structure-bias model, especially how receptor-Galpha quaternary contacts are stabilized or left free.
- Different bias choices are different routes and must not be mixed across `chctrl` and candidates.

### GPCR-effector membrane analog

P0051, "Lipids modulate the dynamics of GPCR:beta-arrestin interaction" (DOI `10.1038/s41467-025-59842-8`), is a close GPCR-effector/membrane analog. Its methods page records a Martini 3 coarse-grained workflow using GROMACS, martinize2, an elastic-network cutoff, INSANE membrane/water/ion setup, CHARMM-GUI-derived equilibration scripts, and long CG sampling.

Project implication:

- This supports that a GPCR-effector complex in a membrane can be treated with a Martini-style CG workflow.
- It does **not** support Galpha-specific interface validation, Ste2-Gpa1, or chimeric alpha5/eCT transfer.
- It is an analog source for R4 design vocabulary, not a candidate-replacement source.

### GPCR / ligand and GPCR / lipid CG examples

P0034, "Protein-ligand binding with the coarse-grained Martini model" (DOI `10.1038/s41467-020-17437-5`), supports coarse-grained Martini sampling of protein-ligand interactions and includes GPCR-family examples such as A2AR and beta2AR in the abstract/method context. It also uses backmapping to inspect atomistic detail.

P0038, "Human class B1 GPCR modulation by plasma membrane lipids" (DOI `10.1101/2024.12.19.629375`), supports coarse-grained simulations of active and inactive class B1 GPCRs in complex plasma membranes with provenance-managed setup.

P0057, "Vibrational energy landscapes and energy flow in GPCRs..." (DOI `10.1039/d5cp02918j`), supports all-atom versus coarse-grained comparison for GPCR energy-flow analysis.

Project implication:

- These support R4 as a plausible screening route for whole-receptor/lipid or GPCR-local dynamics questions.
- They do not support replacing atomistic receptor-Galpha interface evidence.
- They strengthen the requirement that any R4 route needs atomistic backmapping or atomistic comparison before it can inform final chimeric interpretation.

### P0047: Switching Go-Martini method source

Yang and Song 2024, "Switching Go-Martini..." (DOI `10.1021/acs.jctc.3c01222`), was extracted from the user-supplied full text on 2026-07-05.

Captured method details:

- Martini 3 version 3.0.0 with GROMACS 2020.x or 2021.x.
- Protein CG models generated with `martinize2.py` / `vermouth-martinize`.
- Go-like additional Lennard-Jones interactions generated from OV and rCSU contacts through `create_goVirt.py`; multimer case uses an author-modified `create_goVirt_for_multimer.py`.
- Reported Go-like contact distance cutoff: 3-11 A; dissociation energy epsilon = 12.0 kJ/mol.
- General protocol: minimization, NPT equilibration with CG protein BB position restraints of 10 kJ/mol/A^2, then production at 1 atm and 310.15 K; 11 A electrostatics and van der Waals cutoffs; reaction-field electrostatics with epsilon_r = 15.
- Switching protocol: systems first oscillate under State A topology; before full switching, a 1000 steps x 0.002 ps relaxation under State B topology is performed; production then proceeds under State B topology.
- Membrane examples include beta2AR in POPC and ATP8A1-CDC50a in an asymmetric POPC/POPS membrane, generated with `insane.py` and 150 mM NaCl.

Project implication:

- This source supports a specific R4 design vocabulary for Martini 3 plus Go-like structure bias in explicit water/lipid systems.
- It does not support a direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha replacement route.
- A future R4 `chctrl` object contract would need to define the two state structures, the receptor-Galpha quaternary contact-bias policy, backmapping or atomistic comparison, and failure criteria for interface drift.
- The authors state important limitations: switching manually controls state residence time, so the method cannot quantify free-energy landscapes or kinetics; high-energy switching can allow improper pathways; large surrounding molecules may lag behind protein transitions.

Supplementary PDF and tutorial archive extraction on 2026-07-05:

Source-faithful details:

- The Supporting Information PDF has 11 pages. Table S1 records common CG settings: Verlet cutoff scheme, reaction-field electrostatics, `epsilon_r = 15`, electrostatic and van der Waals cutoffs of 11 A, V-rescale temperature coupling with `tau_t = 1.0 ps` and `ref_t = 310.15 K`, Parrinello-Rahman pressure coupling with `tau_p = 12.0 ps`, and transition relaxation of `1000` steps at `0.002 ps`.
- Table S1 records system schedules: minimization steps of 5000/5000/15000/15000 for GlnBP/AdK/beta2AR/ATP8A1-CDC50a; equilibration of 1/1/2/10 ns; production of `300 x 3 ns`, `100 x 2 ns`, `500 x 2 ns`, and `200, 800 ns`; repeats of 50/70/40/50.
- Table S2 records pathway outcomes: GlnBP open-closed pathway 50/50; AdK NMP-closing 48, LID-closing 7, middle 15; beta2AR normal 39 and abnormal 1; ATP8A1-CDC50a main 36, middle 5, incomplete 9.
- The tutorial uses beta2AR active/inactive structures (`3SN6`, `2RH1`) as the worked GPCR example. It instructs removal of water and small molecules, Modeller repair for the 3SN6 missing loop and M96T/M98T mutations, missing-side-chain addition for 2RH1, and trimming both proteins to residues 30-230 and 265-341.
- The tutorial generates state-specific Martini/Go models with `martinize2`, using `-ff martini3001`, `-govs-include`, state-specific `-govs-moltype` values (`Active`/`Inactive`), `-p backbone`, DSSP assignment, automatic cysteine handling, and `-scfix`.
- The tutorial sends each atomistic state to the OV/rCSU contact-map server and then runs the modified `create_goVirt_for_multimer.py` with `--go_eps 12` and `--Natoms 681`. The script defaults record a lower/upper contact distance cutoff of 0.3/1.1 nm, a sequence-distance exclusion of 4, and symmetric OV+rCSU contact retention. It writes virtual-site bead definitions, Go LJ tables, Go exclusions, and VMD-only harmonic Go-bond files.
- The prepared beta2AR CG PDB contains 681 Martini beads plus CA-like virtual Go sites through atom 959. The prepared state topologies define `GO_VIRT`, include state-specific Martini 3 force-field and protein ITP files, and include `Active_exclusions_VirtGoSites.itp` or `Inactive_exclusions_VirtGoSites.itp`.
- The tutorial inserts active beta2AR into a POPC membrane with `python2 insane.py -f Protein_Active_cg.pdb -box 8,8,10 -l POPC -o ions.gro -salt 0.15 -charge auto -center -sol W`. The tutorial explicitly warns that ion names and counts require manual correction because virtual atoms without charges are also counted by `insane.py`.
- The prepared topology records one receptor molecule, 77 + 79 POPC lipids, 2970 Martini waters, 31 `NA`, and 33 `CL`, with index groups for Protein, Membrane, and Solvent.
- The tutorial MDP files differ from the compact SI schedule in one operational detail: `npt.mdp` in the archive uses `nsteps = 1000000` at `dt = 0.020 ps` (20 ns), while SI Table S1 lists beta2AR equilibration as 2 ns. This memo preserves that as a source discrepancy instead of reconciling it silently.
- Tutorial MDP details: `em.mdp` uses steepest descent with `nsteps = 15000`; `npt.mdp` uses `define = -DPOSRES`, `dt = 0.020 ps`, Berendsen semi-isotropic pressure coupling, and topology position restraints of 1000/1000/1000; `md_relax.mdp` uses `dt = 0.002 ps`, `nsteps = 1000`, Parrinello-Rahman semi-isotropic pressure coupling, and no velocity generation; `md.mdp` uses `dt = 0.020 ps`, `nsteps = 25000000` (500 ns), Parrinello-Rahman semi-isotropic pressure coupling, and no velocity generation.
- The tutorial run order is active-state minimization, active-state NPT equilibration, active-state production, short inactive-topology relaxation from `md1.gro`, then inactive-topology production appended after relaxation. Trajectory post-processing concatenates `md1`/`md2`, fixes periodicity, centers the protein, removes rotation/translation, and uses VMD for viewing/analysis.

Project interpretation:

- The SI/tutorial extraction refines R4 vocabulary for a future object contract: state-pair provenance and trimming, exact martinize/Go contact generation choices, state-specific topology switching, membrane/ion setup, manual ion/topology repair checks, MDP schedule, and trajectory post-processing.
- The extraction does **not** define a transferable GPCR-Galpha object. The worked example is beta2AR receptor-only deactivation, and the tutorial does not include a Galpha chain, Ste2-Gpa1 complex, chimeric Galpha, interchain receptor-Galpha Go-contact policy, backmapping, or atomistic comparison gate.
- Any future R4 `chctrl` object contract would still need to specify whether receptor-Galpha quaternary contacts are included in the Go map, excluded, weakly biased, or left free, and how interface drift is rejected against existing atomistic `chctrl` evidence.
- The source limitations remain active: two known states are required; default contact-map construction may be non-optimal; high-energy switching can produce improper pathways; switching residence time prevents quantitative free-energy/kinetics claims; slow surrounding molecules may lag protein transitions; Martini 3 coverage gaps can matter for missing chemical groups.

### P0040: Martini 3 TM-dimer quaternary-bias analog

Sahoo et al. 2023, "Transmembrane dimers of type 1 receptors..." (DOI `10.1016/j.str.2023.03.014`), was extracted from the user-supplied full text on 2026-07-05.

Captured method details:

- The systems are 11 single-pass/type 1 receptor TM-region dimers, not GPCRs and not Galpha complexes.
- UniProt-defined TM hydrophobic domains were modeled as ideal alpha helices, with 8-9 N-terminal residues and 10 C-terminal residues added as flanking membrane-proximal context.
- Two identical TM peptides were placed 50 A apart in a DMPC bilayer.
- CG conversion used `martinize2.py` / Martini 3 / `vermouth-martinize` with DSSP secondary-structure assignment.
- Elastic network was used for TM monomer helical secondary-structure stability, with force constant 500 kJ/mol/nm2 and lower/upper cutoffs 0.5/0.9 nm.
- GROMACS 2016.5 and `insane.py` were used; typical systems used 306 DMPC lipids, 4870 CG water molecules, a 100 x 100 x 100 A cubic box, regular Martini water, neutralization, and 0.15 M NaCl.
- Equilibration was 500 ps; production was 4 replicates x 4 us; time step was 20 fs; temperature was 320 K with V-rescale; pressure was 1 bar with Berendsen.
- Extracted CG structures were converted to atomistic representation with the Martini Backward tool / related CG2AT-style workflow for NMR/PREDDIMER/AlphaFold comparison.

Project implication:

- This source supports R4 validation and risk vocabulary around quaternary state sampling, replicate convergence, and backmapping/comparison.
- It is a cautionary analog: Martini 3 TM-dimer simulations can sample alternate quaternary configurations and interconvert between states, so a receptor-Galpha CG route must define whether such rearrangement is desired, tolerated, or failure.
- It does not support a buildable `chctrl` route, direct GPCR-Galpha CG replacement, or transfer of DMPC peptide-box dimensions to a full receptor-Galpha complex.

## Directed Search Result

The new directed metadata run:

```text
experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_direct_gpcr_gprotein_cg/
```

validated successfully, with 40 verified records. It also recorded an OpenAlex HTTP 429 rate-limit warning in `failures.jsonl`.

Manual screening of the top metadata showed that Crossref hits were dominated by generic Martini/coarse-grained protein, peptide, nanopore, DNA, and protein-complex records. This run did **not** surface a direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha coarse-grained route source.

A supplemental Semantic Scholar title probe for direct GPCR-G protein CG terms failed with SSL/HTTP 429 errors. This is a search caveat, not affirmative evidence that no such paper exists.

Follow-up targeted GPCR-Galpha citation chasing is recorded in:

```text
experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md
```

That pass found a final article DOI for the P0038 GPCR-lipid source (`10.1038/s42003-025-09445-2`) and re-surfaced Mohanty et al. 2025 (`10.7554/eLife.106397`) as a direct Ste2p-Gpa1p / GPCR-Galpha interface citation seed already known in the repo. It still did not find a direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha coarse-grained route source.

The subsequent user-requested targeted pass added Cevheroglu, Becker, and Son 2017 (`10.1016/j.bbamem.2017.09.022`) as another direct Ste2p-Gpa1p / GPCR-Galpha interface seed. A later full-text read archived the PDF and Markdown transcription in the repo and bounded the source as Ste2-Gpa1 control/interface background with weak transfer to Gpr2/Gpr3/GprC chimera candidates. It does not change the R4 method boundary because the record is not a coarse-grained/Martini route source. A seed-expansion attempt stalled during Crossref relation lookup and produced only `request.json` plus `search_plan.md`; that interrupted directory is not usable evidence.

## Current R4 Object Contract Boundary

R4 may continue only as a `chctrl`-first source-gate/design workstream. A future buildable R4 contract must define:

- complete `chctrl` receptor-Galpha object retained at CG resolution;
- selected Martini generation path and exact tool versions;
- membrane composition and ion/water setup policy;
- structure-bias model: elastic network, GoMartini, OLIVES, or another explicit choice;
- whether receptor-Galpha quaternary contacts are biased, weakly biased, or left free;
- backmapping path and atomistic relaxation requirement;
- comparison targets against existing `chctrl` full-system evidence;
- failure criteria for alpha5/eCT/interface drift, membrane distortion, or backmapping artifacts.

Until those are source-backed, R4 cannot move to build, E2, or candidate application.

After extracting P0047, its SI/tutorial archive, and P0040, the remaining source-gate gap is narrower but still material: no direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG workflow has been extracted, and neither paper defines a validated receptor-Galpha interface preservation gate or buildable `chctrl` object contract.

## Decision

- R4 remains the selected next route family for source-gate investigation because it is the only current route family with plausible large compute-reduction upside.
- R4 has **not** passed the source gate for a buildable prototype.
- No Ch-1/Ch-2/Ch-4 action is justified by this extraction.
- No E2 command is approved by this memo.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260703/martini_gpcr_gprotein/run_summary.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_direct_gpcr_gprotein_cg/run_summary.md`
- `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_direct_gpcr_gprotein_cg/failures.jsonl`
- `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `docs/papers/pdf/Yang2024-Switching-Go-Martini.pdf`
- `experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md`
- `experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-supporting-information.pdf`
- `experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-tutorial.zip`
- `docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md`
- `docs/papers/pdf/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.pdf`
- `experiments/chimeric-gpa1/literature/fulltext_md/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.md`
- `docs/papers/summaries/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer-summary.md`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md`
- `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P3-chimeric-gprotein.md`
- `docs/logs/2026-07-05.md`
- `docs/logs/2026-07-04.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
