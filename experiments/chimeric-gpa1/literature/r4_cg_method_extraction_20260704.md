# R4 Coarse-Grained / Multiscale Method Extraction

> Date: 2026-07-04
>
> Last updated: 2026-07-05
>
> Scope: local source-gate extraction for the chimeric Gpa1 R4 route family after the R1-Z downgrade.
>
> Status: `screening_only`; build, E2 approval, and candidate-transfer actions
> require later routed approval.

## Question

At this historical extraction point, could the chimeric compute-reduction route
move from R1 Z-only box shaving to a coarse-grained or multiscale
`chctrl`-first route?

Pass outcome: **source-gate/design evidence only**. A buildable R4 route still
requires direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha coarse-grained route
evidence and a later material-boundary approval.

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
- Its allowed use here is R4 design vocabulary for a membrane GPCR-effector analog.
- Galpha-specific interface validation, Ste2-Gpa1 interpretation, and chimeric alpha5/eCT transfer require separate source evidence.

### GPCR / ligand and GPCR / lipid CG examples

P0034, "Protein-ligand binding with the coarse-grained Martini model" (DOI `10.1038/s41467-020-17437-5`), supports coarse-grained Martini sampling of protein-ligand interactions and includes GPCR-family examples such as A2AR and beta2AR in the abstract/method context. It also uses backmapping to inspect atomistic detail.

P0038, "Human class B1 GPCR modulation by plasma membrane lipids" (DOI `10.1101/2024.12.19.629375`), supports coarse-grained simulations of active and inactive class B1 GPCRs in complex plasma membranes with provenance-managed setup.

P0057, "Vibrational energy landscapes and energy flow in GPCRs..." (DOI `10.1039/d5cp02918j`), supports all-atom versus coarse-grained comparison for GPCR energy-flow analysis.

Project implication:

- These support R4 as a plausible screening route for whole-receptor/lipid or GPCR-local dynamics questions.
- Atomistic receptor-Galpha interface evidence remains the required comparison layer.
- Any R4 route needs atomistic backmapping or atomistic comparison before it can inform final chimeric interpretation.

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
- Direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha route use requires a separate source.
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
- Transfer to a GPCR-Galpha object requires evidence beyond this beta2AR receptor-only deactivation tutorial, including Galpha or Ste2-Gpa1 complex handling, chimeric Galpha context, interchain receptor-Galpha Go-contact policy, backmapping, and atomistic comparison gates.
- Any future R4 `chctrl` object contract would still need to specify whether receptor-Galpha quaternary contacts are included in the Go map, excluded, weakly biased, or left free, and how interface drift is rejected against existing atomistic `chctrl` evidence.
- The source limitations remain active: two known states are required; default contact-map construction may be non-optimal; high-energy switching can produce improper pathways; switching residence time prevents quantitative free-energy/kinetics claims; slow surrounding molecules may lag protein transitions; Martini 3 coverage gaps can matter for missing chemical groups.

### P0040: Martini 3 TM-dimer quaternary-bias analog

Sahoo et al. 2023, "Transmembrane dimers of type 1 receptors..." (DOI `10.1016/j.str.2023.03.014`), was extracted from the user-supplied full text on 2026-07-05.

Captured method details:

- Project role: quaternary-bias analog for 11 single-pass/type 1 receptor TM-region dimers; GPCR-Galpha use requires separate evidence.
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
- Buildable `chctrl` routing, direct GPCR-Galpha CG replacement, and full receptor-Galpha dimensions require separate source-backed evidence.

### GoMartini3_2025: updated Martini 3 structure-bias method source

Souza et al. 2025, "GōMartini 3: From large conformational changes in proteins to environmental bias corrections" (DOI `10.1038/s41467-025-58719-0`), was extracted from the Nature Communications HTML and Supporting Information PDF on 2026-07-05.

Source-faithful details:

- The paper presents an enhanced GōMartini model using virtual interaction sites with Martini 3. The virtual sites encode Gō-like Lennard-Jones interactions between native-contact pairs and otherwise do not interact with other beads by default.
- The setup workflow is explicit: obtain an OV/rCSU contact map from the Poma GoContactMap server or the GoMartini `ContactMapGenerator`, then use `Martinize2` to generate CG coordinates and topology from the atomistic reference structure plus the contact map.
- `Martinize2` activates the structure-bias model with `-go`; the contact-map file may be supplied after that flag. Adjustable flags include `-go-eps`, `-go-up`, `-go-low`, `-go-res-dist`, and `-go-moltype`.
- The default potential depth remains `epsilon_LJ = 9.414 kJ/mol`, inherited from the earlier GoMartini implementation. The article also records practical tuning: examples use `epsilon = 12.0 kJ/mol`, `15.0 kJ/mol`, and a benchmark scan from `12` to `27 kJ/mol`.
- Contact-map filtering uses OV/rCSU contacts within a 0.3-1.1 nm reference-structure distance range; the lower bound avoids dense-bead artifacts and the upper bound matches the Martini non-bonded cutoff. The method uses graph-distance filtering, with default `k = 4` in `Martinize2`, and recommends `k = 3` only when loop flexibility is too high.
- Regular Martini non-bonded interactions between backbone beads connected by Gō-like bonds are excluded in GoMartini3, because summing regular Martini and Gō LJ interactions can distort short-contact geometry.
- General CG settings in the article: GROMACS versions 2018.x to 2023.x; Martini updated run parameters; `20 fs` time step; Verlet neighbor search; `1.1 nm` non-bonded cutoff; reaction-field electrostatics with dielectric constant `15`; Parrinello-Rahman pressure coupling with `tau_p = 12.0 ps`; V-rescale temperature coupling with `tau_t = 1.0 ps`.
- Protein models use Martini 3 open-beta or later development versions; folded final-release examples use `Martinize2`; IDP examples use `Polyply`; DSSP assigns secondary structure and `scFix` side-chain dihedral corrections are included.
- The Supporting Information includes a protein-complex nanomechanics example: XMod-Doc:Coh uses Martini 3, PDB `4IU3`, 1036 OV/rCSU contacts total, 59 Coh:Doc interface contacts, `epsilon = 9.414 kJ/mol`, and 100 constant-speed SMD replicas. The RBD:H11-H4 example uses PDB `6ZH9`, 715 total contacts, 26 inter-protein contacts, and `epsilon_LJ = 15.0 kJ/mol`.
- The same SI describes a flexibility-calibration workflow: compare CG RMSF against AA reference simulations, scan epsilon values, and optionally remove selected Gō bonds based on AA contact-frequency maps. For the six benchmark proteins, selected epsilon values differ by system (`11`, `12`, `15`, `18`, `25 kJ/mol`), so GoMartini3 requires system-specific epsilon selection.
- For protein complexes, the discussion states that several studies needed additional interchain Gō-like bonds at protein-protein interfaces, using GoMartini or alternatives such as OLIVES. It also warns that systems with many copies of the same protein are problematic because the same Gō bonds can wrongly affect protein-protein interactions; small oligomers can use unique protein models per monomer, but many-copy systems become impractical.
- Data availability points to Zenodo `10.5281/zenodo.11198318` for system setups, force-field parameters, and GROMACS inputs; code availability points to `vermouth-martinize`, GoContactMap, GoMartini `ContactMapGenerator`, and Polyply IDP tutorial resources.

Project interpretation:

- GoMartini3 is now the clearest source for the missing R4 contact-policy vocabulary. A future R4 object contract must specify atomistic reference structure, contact generator, contact range, graph-distance rule, epsilon strategy, `-go-moltype`/chain uniqueness, and exactly whether receptor-Galpha interface contacts are included.
- The paper gives a practical pattern for small protein complexes: inter-protein interface contacts can be explicitly represented and counted, and different chains may need distinct protein models. That is useful for a `chctrl` design document.
- GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha workflow use would require separate evidence; the protein-complex examples are nanomechanics systems rather than membrane GPCR-effector signaling complexes.
- It moves R4 closer to an object-contract draft by making receptor-Galpha interchain-contact policy a named design field; later OliGoMers/Lopez/Aydin extraction supplies more of that design vocabulary, while direct GPCR-Galpha workflow evidence remains missing.
- For this project, the object-contract implication recorded from this source is:
  receptor-Galpha interchain contacts must be an explicit design choice with a
  failure mode. Leaving them implicit would make any future CG result unusable
  for `chctrl` comparison.

### OLIVES_2024: access-limited structure-bias seed

Pedersen et al. 2024, "OLIVES: A Go-like Model for Stabilizing Protein Structure via Hydrogen Bonding Native Contacts in the Martini 3 Coarse-Grained Force Field" (DOI `10.1021/acs.jctc.4c00553`), remains an important method seed; full-method extraction is still pending.

Access/status details:

- Crossref metadata confirms the final ACS article, title, DOI, online publication date, and relation to the ChemRxiv preprint DOI `10.26434/chemrxiv-2023-6d61w`.
- Direct `curl -I` checks against the ACS article page and the ChemRxiv article page both returned HTTP 403 Cloudflare challenge pages on 2026-07-05.
- Because no article text, SI, tutorial, code, or source-method body was accessible in this pass, OLIVES is recorded as `manual_acquisition` rather than as an extracted method source.

Project interpretation:

- OLIVES may still matter because it is explicitly about hydrogen-bonding native contacts in Martini 3 protein stabilization.
- R4 source-bias model, contact policy, MDP settings, or validation-gate choices require accessible OLIVES method text before using it as evidence.
- The current decision package can proceed from GoMartini3 plus OliGoMers for a design-only contact-policy draft; OLIVES remains a manual-acquisition row.

### OliGoMers_2024: multimer and interchain Go source

Korshunova et al. 2024, "Martini 3 OliGomers: A Scalable Approach for Multimers and Fibrils in GROMACS" (DOI `10.1021/acs.jctc.4c00677`), was extracted from the Europe PMC full-text XML on 2026-07-05.

Source-faithful details:

- The paper implements Martini 3 plus Go for multimer systems and separates intramolecular and intermolecular Go interactions.
- Default protein generation uses `martinize2` with Martini 3.0.0, DSSP, `-p backbone`, `-scfix`, and `-cys auto`; the default command records `-ff martini3001`.
- Elastic-network controls use force constant `500 kJ mol-1 nm-2`; the default EN command records `-elastic -ef 700.0 -el 0.5 -eu 0.9 -ea 0 -ep 0`.
- Intramolecular Go uses `create_goVirt.py` per chain with an atomistic rCSU contact map, lower cutoff `0.3 nm`, and upper cutoff `1.1 nm`.
- The intra/intermolecular Go model uses a modified `create_goVirt.py` over the whole oligomer; it splits contacts into intra- and intermolecular subsets and assigns separate `epsilon_intra` and `epsilon_inter`.
- The amyloid-beta case uses an in-house `sorted_goVirt.py` / "Snake oil" approach to define intra/intermolecular contacts on a single monomer output, enabling arbitrary monomer counts in the GROMACS topology. This adds up to four virtual sites per backbone bead involved in Go interactions.
- Example systems include aquaporin tetramer in POPC, insulin dimer, and amyloid-beta fibril. The aquaporin CG system was built with `martinize2` and `insane`, `30 x 30 x 15 nm3`, 76,150 regular water beads, 0.15 M NaCl, 2900 POPC, 114,840 total beads, and 996 Go virtual beads.
- CG simulations use GROMACS 2021.X, Martini 3.0.0, `20 fs` time step, 312 K for aquaporin and 310 K for insulin, 1 atm, V-rescale `tau_t = 1.0 ps`, Parrinello-Rahman production pressure coupling `tau_p = 12 ps`, reaction-field electrostatics with relative permittivity 15, and 1.1 nm nonbonded cutoff.
- Proteins are position restrained during equilibration. Production schedules include aquaporin `3` repeats of `5.5 us`, insulin `5 us` with `3` repeats, and solvent scans `5 us` with `8` repeats.
- Analyses include native-contact fractions using MDAnalysis with BB particles and a 0.6 nm cutoff, binding/dimerization traces by minimum intermonomer distance below 0.6 nm, GROMACS/VMD RMSD and RMSF, and comparison of CG RMSF against atomistic RMSF using the last 20-25% of production trajectories.
- For insulin, both `epsilon_intra` and `epsilon_inter` around `15 kJ mol-1` gave AA-like stability; lower values increased fluctuation/dissociation, while values above 15 made the CG-Go model too rigid.
- The paper warns that strong intermolecular Go bias weakens chemical specificity. `epsilon_inter > 10 kJ mol-1` can make interfaces effectively glass-like; `4-10 kJ mol-1` can allow qualitative environment effects; values below `4 kJ mol-1` add little over native Martini BB-BB attraction, which is already about `4.06 kJ mol-1` or less.

Project interpretation:

- This was the strongest extracted source in this record for R4
  receptor-Galpha interchain-contact vocabulary.
- A future `chctrl` CG object contract must decide whether receptor-Galpha interchain contacts are explicitly included, what `epsilon_inter` scan is used, and what counts as overfrozen versus interface drift.
- For a small receptor-Galpha complex, transfer only the separate intra/interchain contact handling and tuning against atomistic metrics; the amyloid "Snake oil" many-copy convenience is outside the project use.
- GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha workflow use and build approval require separate source-backed evidence.

### Lopez2022_CG_AA_Coupling: CG-to-AA validation bridge

Lopez et al. 2022, "Asynchronous Reciprocal Coupling of Martini 2.2 Coarse-Grained and CHARMM36 All-Atom Simulations in an Automated Multiscale Framework" (DOI `10.1021/acs.jctc.2c00168`), was extracted from an OSTI-hosted PDF in `/private/tmp` on 2026-07-05.

Source-faithful details:

- The workflow extends MuMMI by adding CG-to-AA conversion, AA simulations, concurrent analyses, and AA-to-CG feedback. Project transfer role: validation bridge from CG snapshots to AA checks; the molecular example is RAS-RBDCRD on lipid membranes.
- Selected CG snapshots are chosen by RAS tilt, rotation, and CRD-membrane distance; MuMMI analyzes CG snapshots every 2 ns and schedules selected frames for CG-to-AA transformation.
- The Backmapping module retrieves Martini CG ddcMD frames through an MDAnalysis-based tool, calls `sinceCG`, converts GROMACS input to AMBER format using ParmEd, and logs transformation status.
- `sinceCG` is a modified Backward-style Martini 2.2 CG to CHARMM36 AA conversion protocol. It changes mapping files, modified Hamiltonians, stereochemistry controls, and distance-restraint networks to recover protein-protein interactions during equilibration.
- The protocol applies staged energy minimization and short MD with stereochemistry-promoting potentials. Protein geometry is enforced with type-10 distance matrices at `1000 kJ/mol/nm2`, then `10000 kJ/mol/nm2`, followed by restored nonbonded terms and iterative MD relaxation.
- AA simulations use CHARMM36 with CMAP for protein/lipids, TIP3P water, GROMACS 2019.6 for topology construction, ParmEd/gromber conversion to AMBER, and GPU-enabled AMBER18 for production.
- Each AA run is up to `50 ns`, preceded by `0.5 ns` NVT and `2.0 ns` NpT with position restraints on all heavy atoms except water and salt. Production runs on 1 GPU + 1 CPU core at about `14 ns/day` and saves output every `0.1 ns`.
- A test set of about 19,545 AA build attempts from four CG trajectories showed `sinceCG` success of `99.5 +/- 0.1%` versus Backward `86.9 +/- 0.5%`; successful `sinceCG` builds have correct stereochemistry, while successful Backward models averaged `35 +/- 6` stereochemical errors.
- In the full MuMMI run, 10,502 snapshots were selected; 10,324 transformations succeeded on first attempt, 160 on second, 4 on third, and 14 were abandoned after third-attempt failure. The article attributes the 14 abandoned transformations to file-system coordinate delivery failure, giving an implied third-round success rate of 100%.
- Concurrent analyses compute C-alpha RMSD, HVR end-to-end distance, RAS G-domain orientation, CRD-membrane distance, and discard frames with problematic periodic representations when radius of gyration exceeds `0.4 x Z`.
- The discussion warns that CG-to-AA conversion can strain local atomistic geometry, deform proximal atom arrangements, and lose favorable intermolecular interactions without explicit identification/enforcement.
- Generalization requires system-specific changes to MD inputs, queues, order parameters, ML models, peptide-bond assumptions, and the AA distance matrix.

Project interpretation:

- Lopez2022 supplied the clearest bridge in this R4 record from cheap CG sampling back to atomistic interpretation: selected CG snapshots must be converted, relaxed, checked for stereochemistry/geometry, and measured again at AA resolution.
- Use Lopez2022 as a validation bridge only; Martini 3 build defaults for this project require separate Martini 3 / GPCR-Galpha method evidence.
- It supports an R4 validation requirement: any future CG `chctrl` result should be treated as a snapshot generator until backmapped/relaxed AA structures pass stereochemistry, interface-contact, alpha5/eCT geometry, BSA/contact, membrane embedding, and periodicity sanity checks.

### Aydin2025_UCG_Multiscale: cheap model proposes Martini starts

Aydin et al. 2025, "Enhanced Exploration of Protein Conformational Space through Integration of Ultra-Coarse-Grained Models to Multiscale Workflows" (DOI `10.1021/acs.jpcb.4c08622`), was extracted from the Europe PMC full-text XML on 2026-07-05.

Source-faithful details:

- The paper integrates ultra-coarse-grained (UCG) protein models into MuMMI for RAS-RBDCRD membrane-associated protein complexes.
- UCG sites are selected with essential dynamics coarse graining and parameterized from Martini CG simulations using backbone beads. The interaction model uses heterogeneous elastic network modeling, with selected harmonic interactions converted to Morse potentials to allow larger global motions.
- The implicit membrane model uses a virtual site and Morse-wall interactions to keep protein configurations realistic relative to the membrane. The membrane is not lipid-specific; it is a sampling/orientation aid before Martini CG validation.
- The Martini CG reference system has a `30 nm x 30 nm` plasma membrane patch with 8 lipid types, water, 150 mM NaCl, about 140K CG particles, and RAS-RBDCRD with 320 amino acids. Reported speed is about `1 us/day` with ddcMD on 1 GPU + 1 CPU, and similar with recent GROMACS on 1 GPU + 10 CPUs.
- UCG-to-Martini backmapping uses a multilayer perceptron. Inputs are coordinates for 40 UCG beads plus the upper triangular UCG distance matrix (`n = 900` total input), and outputs are coordinates for 751 Martini CG beads (`n = 2253`) for the 320-aa protein complex.
- The model uses PyTorch, 10% validation, 300 epochs, batch size 128, Adam, and Horovod distributed training across 8 GPUs. Validation RMSD reports lowest `1.2 A` and mean `2.1 A` across all protein beads.
- The MuMMI workflow uses a UCG server/generator, Flux scheduling, GROMACS validation iterations, then CG simulations. Typical GROMACS validation/CG simulations run about `600 ns` in `12 h` on Lassen.
- UCG simulations sample conformers cheaply; generated conformers are validated at Martini CG resolution and then sampled locally. After a UCG-MuMMI iteration, the resulting CG ensemble can retrain/refine the UCG model.

Project interpretation:

- Aydin2025 is useful for the "cheap model proposes Martini starts" concept.
- Immediate chimeric Gpa1 use would require large CG training ensembles and an approved ML/UCG workflow; those prerequisites are absent from the current project record.
- If R4 continues, Aydin2025 should inform language for starting-structure generation and validation loops, while Lopez2022 remains the more relevant CG-to-AA bridge.

## Directed Search Result

The new directed metadata run:

```text
experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260704/r4_direct_gpcr_gprotein_cg/
```

validated successfully, with 40 verified records. It also recorded an OpenAlex HTTP 429 rate-limit warning in `failures.jsonl`.

Manual screening of the top metadata showed that Crossref hits were dominated by generic Martini/coarse-grained protein, peptide, nanopore, DNA, and protein-complex records. The retained evidence set contains no direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha coarse-grained route source.

A supplemental Semantic Scholar title probe for direct GPCR-G protein CG terms failed with SSL/HTTP 429 errors. Evidence status: unresolved search caveat; no absence claim is made from that failed probe.

Follow-up targeted GPCR-Galpha citation chasing is recorded in:

```text
experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md
```

That pass found a final article DOI for the P0038 GPCR-lipid source (`10.1038/s42003-025-09445-2`) and re-surfaced Mohanty et al. 2025 (`10.7554/eLife.106397`) as a direct Ste2p-Gpa1p / GPCR-Galpha interface citation seed already known in the repo. The retained source set still lacks a direct GPCR-Galpha, Ste2-Gpa1, or chimeric Galpha coarse-grained route source.

The subsequent user-requested targeted pass added Cevheroglu, Becker, and Son 2017 (`10.1016/j.bbamem.2017.09.022`) as another direct Ste2p-Gpa1p / GPCR-Galpha interface seed. A later full-text read archived the PDF and Markdown transcription in the repo and bounded the source as Ste2-Gpa1 control/interface background with weak transfer to Gpr2/Gpr3/GprC chimera candidates. R4 method-boundary changes require a coarse-grained/Martini route source. A seed-expansion attempt stalled during Crossref relation lookup and produced only `request.json` plus `search_plan.md`; that interrupted directory is not usable evidence.

## Historical R4 Object Contract Boundary

At this historical extraction point, R4 could continue only as a
`chctrl`-first source-gate/design workstream. A future buildable R4 contract
would have to define:

- intact `chctrl` receptor-Galpha object retained at CG resolution;
- selected Martini generation path and exact tool versions;
- membrane composition and ion/water setup policy;
- structure-bias model: elastic network, GoMartini, OLIVES, or another explicit choice;
- whether receptor-Galpha quaternary contacts are biased, weakly biased, or left free;
- backmapping path and atomistic relaxation requirement;
- comparison targets against existing `chctrl` full-system evidence;
- failure criteria for alpha5/eCT/interface drift, membrane distortion, or backmapping artifacts.

Build, E2, or candidate application requires those fields to become source-backed.

After extracting P0047, its SI/tutorial archive, P0040, GoMartini3_2025,
OliGoMers_2024, Lopez2022, and Aydin2025, the source-gate gap became narrower
but still material: the retained set has no direct GPCR-Galpha / Ste2-Gpa1 /
chimeric Galpha CG workflow and no validated receptor-Galpha interface
preservation gate or buildable `chctrl` object contract. Those sources support a
design-only `chctrl`-first R4 object-contract draft; build or run work requires
the missing route evidence.

## 2026-07-05 New-Source Chase

The follow-up source-acquisition pass is recorded in:

```text
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md
experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv
```

Historical action summary:

- direct GPCR-Galpha / GPCR-G protein CG metadata search retained no usable direct workflow;
- Ste2/Gpa1 CG search remains a retry/manual-search item because the API run returned no records with provider failures;
- GoMartini3 extraction added explicit contact-map, `Martinize2 -go`, epsilon-calibration, interchain-contact, and small-oligomer chain-uniqueness vocabulary;
- OLIVES remains a manual-acquisition item because ACS/ChemRxiv access was blocked by HTTP 403 Cloudflare challenge pages in this pass;
- OliGoMers is extracted as the strongest practical interchain/multimer Go source for the recorded R4 object-contract vocabulary;
- Lopez2022 is now extracted as the most useful CG-to-AA validation bridge; Aydin2025 is extracted as a heavier UCG-to-Martini workflow concept for optional future review.

Historical action lane after this pass: **R4-B design-only object-contract draft**. The one-page decision package, `chctrl`-first object-contract document, and local material decision have now been written. This method memo is historical/supporting evidence; the R4 material boundary is recorded in `r4_material_decision_addendum_20260706.md`.

## Decision

- At this historical extraction point, R4 was selected for source-gate investigation because it was the only route family with plausible large compute-reduction upside.
- This memo supplies method evidence for the R4 material boundary and supporting design notes.
- Current R4 evidence class: `screening_only` / design support.
- Buildable prototype status requires direct route evidence and material-boundary approval.
- Ch-1/Ch-2/Ch-4 action and E2 commands require a separate dated work order.

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
- `https://www.nature.com/articles/s41467-025-58719-0`
- `https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-58719-0/MediaObjects/41467_2025_58719_MOESM1_ESM.pdf`
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11391574/fullTextXML`
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12105037/fullTextXML`
- `https://doi.org/10.1021/acs.jctc.2c00168`
- `https://doi.org/10.1021/acs.jctc.4c00553`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`

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
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`
