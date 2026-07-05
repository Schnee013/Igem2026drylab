# Chimeric Gpa1 System Reduction Exploration Plan

> Date: 2026-07-03
>
> Status: exploration plan, not an execution approval for candidate full-production MD.
>
> Current decision boundary: [Decision 005](../../../docs/decisions/005-md-compute-triage-after-chctrl.md) paused chimeric Gpa1 candidate full-production MD because the available E2 server is shared and the previous full system occupied the A100 too heavily. The next step is protocol research for reduced-compute chimeric MD, not direct continuation of Ch-1/Ch-2/Ch-4 production.

## Purpose

Explore whether the chimeric Gpa1 GPCR-Galpha systems can be reduced or more strongly restrained while preserving a defensible answer to the receptor-Gpa1 interface-stability question.

The plan must answer three questions before any new candidate production route is reopened:

1. Which parts of the current full atomistic membrane system are essential for interpreting receptor-Galpha interface stability?
2. Which reductions or restraints have literature or official-method support, and which are only project heuristics?
3. Which candidate protocol measurably lowers E2 resource use without creating an interpretation that is misleadingly presented as equivalent to full-system MD?

## Source-Backed Starting Boundary

- Current MD priority and stop rule are in [Decision 005](../../../docs/decisions/005-md-compute-triage-after-chctrl.md) and [2026-06-26 log](../../../docs/logs/2026-06-26.md).
- The MD direction document states that old Slurm control/chctrl 3 reps are historical completion evidence, while E2 has only chctrl rep1 evidence; candidate full MD is paused pending a compute-saving protocol. See [P0-md-simulation](../../../docs/modeling/P0-md-simulation.md).
- The chimeric Gpa1 direction document states that AF3 screening and Top 3 selection are complete, but Ch-1/Ch-2/Ch-4 production is paused for compute triage. See [P3-chimeric-gprotein](../../../docs/modeling/P3-chimeric-gprotein.md).
- Old E2 and unified rerun plans are historical execution/provenance references only: [e2-chimeric-md-restart](e2-chimeric-md-restart.md) and [chimeric-md-unified-rerun-sites](chimeric-md-unified-rerun-sites.md).
- E2 use must follow the shared-server rule in [NKULiulab E2 shared server guide](../../../docs/ops/nkuliulab-e2-cloud-server.md): no long A100 occupation without explicit gate approval, and every test must record threads, GPU use, run directory, and logs.
- The 2026-06-27 E2 chctrl rep1 analysis is a one-replicate early-gate snapshot only; it is useful as a control benchmark target but is not E2 3-rep or final-production evidence. See [2026-06-27 log](../../../docs/logs/2026-06-27.md).

## Non-Goals

- Do not launch Ch-1/Ch-2/Ch-4 full-production MD from this plan.
- Do not treat local pocket/interface-only MD as a full-system replacement unless a later source-backed decision explicitly reclassifies its evidence role.
- Do not introduce universal pass/fail cutoffs without exact source pointers. Existing bands such as alpha5 iRMSD, BSA retention, contact retention, and H-bond occupancy remain project operational heuristics unless source-audited.
- Do not use `freezegrps` or hard freezing as a default membrane-production shortcut. If considered at all, it must be justified by official GROMACS behavior and a membrane-specific source audit.

## Workstream A: Professional Material Search

Goal: build a traceable evidence base before choosing any reduction protocol.

### Search Sources

- PubMed / NCBI for primary literature and review leads.
- Google Scholar or institutional search for citation chasing when PubMed misses computational-method papers.
- Crossref / DOI landing pages for metadata verification.
- GPCRdb, GPCRmd, and GPCRsignal for GPCR-G protein dynamics and interface-analysis precedents.
- CHARMM-GUI, GROMACS, PLUMED, MDAnalysis, FreeSASA, Martini, and Memprot.GPCR-ModSim official documentation for method behavior.
- Existing repo anchors first: [chimeric MD literature matrix](../../../experiments/chimeric-gpa1/literature/chimeric_md_literature_matrix.md) and [P0 MD tech-stack research](../../../docs/modeling/P0-md-tech-stack-research.md).

### Query Pack

Run searches in English and preserve exact query strings:

- `"chimeric G alpha" "GPCR" "molecular dynamics"`
- `"G protein selectivity" "chimeric" "molecular dynamics" "alpha5"`
- `"GPCR" "G protein" "interface" "molecular dynamics" "restraints"`
- `"mini-Gs" "GPCR" "molecular dynamics" "CHARMM-GUI" "GROMACS"`
- `"membrane protein" "reduced system" "molecular dynamics" "position restraints"`
- `"flat-bottom restraint" "GPCR" "molecular dynamics"`
- `"Martini 3" "GPCR" "G protein" "complex"`
- `"Ste2" "Gpa1" "molecular dynamics"`
- `"CHARMM-GUI" "protein complex" "membrane" "restraints"`
- `"GROMACS" "position restraints" "membrane protein" "pressure coupling"`

### Inclusion Tiers

| Tier | Include if | Use |
|---|---|---|
| T1 direct | GPCR-Galpha or chimeric/engineered Galpha complex MD | Primary evidence for timescale, restraints, box/membrane design, and analysis metrics |
| T2 close analog | Mini-G, alpha5 peptide, receptor-G protein interface, Ste2-Gpa1, GPCRsignal/GPCRmd methods | Supports interface metric design and interpretation boundaries |
| T3 method | Membrane-protein reduced-system, restraint, multiscale, coarse-grained, or benchmark papers | Supports protocol options, not biology-specific claims |
| T4 official docs | GROMACS/CHARMM-GUI/PLUMED/MDAnalysis/FreeSASA/Martini docs | Supports tool behavior and implementation constraints |

Exclude sources that only make general performance claims without methods, atom counts, restraint definitions, or reproducible setup details.

### Reading Extraction Fields

Create or update `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md` with:

- citation, DOI/PMID/URL, year, source tier
- system class and biological question
- atom count, box dimensions, membrane composition, water/ion padding if reported
- software, force field, timestep, HMR or no-HMR, pressure coupling
- restraint type, restrained selections, force constants, release schedule
- production length, replicate count, discarded equilibration window
- interface metrics and cutoff definitions
- what the paper supports for this project
- what must not be transferred to this project
- exact method-section pointer or official-doc section

## Workstream B: Existing System Inventory

Goal: quantify what currently makes the chimeric systems expensive before proposing reductions.

Inventory the current chctrl and candidate prepared systems:

- `chimeric-ste2-gpa1-wt`
- `chimeric-gpr3-aogpa2-c37`
- `chimeric-gpr3-aogpa2-c15`
- `chimeric-gpr2-aogpa2-c10`

For each system, record:

- total atoms from `step6.6.gro` / `topol.top`
- protein, lipid, water, ion atom counts
- box vectors and approximate water height above and below the protein complex
- lipid count per leaflet if recoverable
- Gromacs `.tpr` size and production MDP settings
- current index groups relevant to `SOLU`, `SOLU_MEMB`, `MEMB`, and receptor/Galpha selections
- any C3 caveats already recorded in old plans, especially Ch-2 EM caveat

Output: `experiments/md-simulation/analysis/chimeric_system_reduction_inventory.tsv`.

## Workstream C: Candidate Reduction Routes

Treat each route as a hypothesis. None is accepted until it passes source, build, benchmark, and interpretation gates.

### Route 1: Tight Full-System Rebuild

Keep the intact GPCR-Galpha complex, membrane, explicit water, and ions, but reduce avoidable padding.

Questions:

- Can CHARMM-GUI or a reproducible local build reduce XY/Z dimensions without protein-image artifacts or insufficient water around intracellular Galpha?
- What minimum membrane and solvent padding is supported by literature or official builder defaults?
- Does the reduced box keep semi-isotropic pressure coupling physically meaningful?

Evidence role if it passes: strongest candidate for replacing the large full system, because the biological object remains intact.

Main risks:

- PBC image interaction with the GPCR-Galpha complex.
- Distorted membrane relaxation if XY dimensions are too tight.
- Changed hydration or ion environment around the intracellular Galpha domain.

### Route 2: Full System With Layered Restraints

Keep the full atom count but apply a source-backed restraint schedule so early screening can focus on interface stability.

Draft layer model:

- free or weakly restrained: receptor intracellular loops, Galpha alpha5/eCT, chimeric junction, nearby receptor-Galpha contact residues
- moderate restraints: receptor transmembrane scaffold and Galpha Ras-like scaffold regions outside the immediate interface
- stronger temporary restraints only during equilibration: distal flexible regions that otherwise dominate relaxation without answering the interface question

Evidence role if it passes: useful as an early screening or stabilization protocol. It may reduce required sampling time, but it will not reduce per-ns cost because atom count remains similar.

Main risks:

- Restraints can artificially preserve an interface that would separate.
- Force constants and release schedule require exact source or official-method justification.
- The protocol must be calibrated against chctrl before candidates.

### Route 3: Interface-Only Atomistic Subsystem

Extract receptor intracellular interface elements and Galpha alpha5/eCT with geometry restraints or capping, then run short atomistic simulations.

Evidence role: supporting mechanism/refinement only unless a later decision upgrades it after literature review. It cannot currently replace full-system MD.

Main risks:

- Removing membrane, receptor scaffold, and Galpha domain context changes the coupling geometry.
- Good behavior in an extracted subsystem can be an artifact of restraints.
- Negative results may still be informative for local clashes but not for full-complex instability.

### Route 4: Coarse-Grained or Multiscale Screening

Evaluate Martini or another coarse-grained/multiscale approach for low-cost screening, then backmap promising systems to atomistic MD if justified.

Evidence role: possible triage layer, not final atomistic interface evidence unless the workflow includes validated atomistic backmapping and comparison.

Main risks:

- Galpha alpha5/interface contacts and chimeric junction details may not survive coarse graining.
- Backmapping adds another uncontrolled source of structural drift.
- Literature support must be GPCR-G protein relevant, not generic membrane-protein-only.

### Retired Route 5: Metric/Input Dependency Triage

Plan-only note: a fifth workstream was briefly considered to inventory which
existing chimeric MD metrics depend on protein-only processed trajectories and
which require full-system evidence. It is not a simulation-reduction route, not
a build or benchmark gate, and not candidate-validation evidence.

Status: inactive. R5-derived output files were removed because they should not
be reused as an authoritative analysis contract. If metric/input dependencies
are needed later, recreate them from the current analysis scripts, selection
config, preprocessing logs, and run evidence in a new explicitly approved
analysis task.

## Workstream D: Gates

### Gate 1: Source Gate

Each candidate route must have at least:

- one direct or close-analog literature source for the physical idea, or an explicit statement that it is project-only exploratory;
- official documentation for any tool behavior being relied on;
- a written "supports / does not support" note in the literature matrix.

### Gate 2: Build Gate

Before any E2 benchmark:

- local input files must be complete and checksummed;
- `grompp` must pass with warnings justified in a log;
- index groups must match analysis selections;
- route-specific MDP and restraint files must be versioned or generated by a script;
- no result directory may overwrite historical Slurm or E2 evidence.

### Gate 3: Benchmark Gate

Run only short tests with explicit user approval if E2 is required.

Record:

- system ID, route ID, run directory, command, GROMACS build, GPU/CPU/thread settings
- total atoms and output groups
- wall time, ns/day, GPU utilization, GPU memory, CPU utilization
- checkpoint/log/trajectory readability
- comparison against current full-system baseline where available

Default benchmark order:

1. chctrl reduced or restrained prototype smoke test
2. chctrl short benchmark
3. one candidate short smoke test only if chctrl behavior is acceptable

### Gate 4: Physical Sanity Gate

Minimum checks for any prototype:

- no fatal GROMACS errors, LINCS explosions, or unreadable trajectories
- membrane remains intact and protein remains properly embedded
- receptor-Galpha interface does not separate immediately unless the route is rejected
- global RMSD/Rg/box/temperature/pressure are interpretable
- alpha5/eCT iRMSD, BSA, contact persistence, H-bond occupancy, COM distance, and junction RMSF can still be computed from the reduced system or are explicitly marked unavailable

### Gate 5: Interpretation Gate

Classify each route:

- `candidate_replacement`: may replace full-system candidate production after a new decision
- `screening_only`: may rank or reject candidates before full-system confirmation
- `supporting_mechanism_only`: may explain local interface behavior but not validate chimeric coupling
- `reject`: physically unstable, not cheaper, or not interpretable

## Sequence

### Phase 0: Setup and No-Launch Lock

- Confirm no old plan is being used as a current launch instruction.
- Create the literature matrix and inventory output paths.
- Define route IDs before generating any prototype files.

### Phase 1: Literature and Method Search

- Read existing exact anchors: Velazhahan 2021, Tawfeeq 2025, Renault 2019, Memprot.GPCR-ModSim 2024, GPCRsignal 2021, FreeSASA/MDAnalysis docs, and relevant GROMACS/CHARMM-GUI docs.
- Run the query pack and add source-screening notes.
- Produce a short ranked reading memo: direct precedent, close analog, method support, and no-go warnings.

### Phase 2: Current System Inventory

- Quantify atom composition, box dimensions, and index groups for the four prepared systems.
- Identify the largest atom contributors and the minimum atoms required by the current seven interface metrics.
- Produce a route-specific reduction target, but keep all numeric reduction claims marked as estimates until benchmarked.

### Phase 3: Protocol Matrix

For each route, define:

- exact system object being simulated
- retained/deleted/restraint selections
- MDP changes
- expected evidence class
- expected compute benefit
- build risks
- required source support
- benchmark command plan

### Phase 4: chctrl Prototype

- Build at most one or two chctrl prototypes first.
- Run local checks where possible.
- If E2 is needed, stop for explicit approval before any remote benchmark.
- Compare chctrl prototype metrics with the E2 chctrl rep1 early-gate snapshot and old control evidence only within their evidence boundaries.

### Phase 5: Candidate Probe

Only after chctrl passes the build and sanity gates:

- run a short smoke/benchmark on one candidate prototype;
- do not start long production;
- classify whether the route deserves a new decision record.

### Phase 6: Decision Package

Write:

- protocol comparison table
- benchmark table
- source-backed interpretation limits
- recommended route and non-recommended routes
- whether a new decision record is needed to reopen candidate MD

If a route is accepted, create a new decision file under `docs/decisions/` and update `docs/INDEX.md`, `P0-md-simulation.md`, and `P3-chimeric-gprotein.md` only after the decision is source-backed.

## Immediate Next Tasks

1. Create `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`.
2. Create the current-system inventory table from local `step6.6` and topology files.
3. Fill a first protocol matrix with at least Route 1 and Route 2.
4. Stop before any E2 run and ask for explicit approval with a concrete command, run directory, expected duration, and resource profile.

## Completion Definition

This exploration is complete when the project has either:

- a source-backed, benchmarked reduced-compute protocol ready for a new decision record; or
- a documented rejection showing that reduced or restrained protocols are not currently defensible, leaving mutant GPR MD pretesting or other lower-cost MD work as the active path.
