# R1 Z-Only Atom-Count Comparison

> Date: 2026-07-04
>
> Scope: `chimeric-ste2-gpa1-wt` / reduced `chctrl` only.
>
> Decision status: R1 Z-only reduced `chctrl` remains buildable and short-runnable, but is downgraded as a compute-saving route because the observed atom-count reduction is too small to address the current E2 resource constraint.

## Local System Composition

The current R1 exploratory reduced `chctrl` system contains `257130` atoms. Protein atoms are a small fraction of the explicit membrane-solvent system:

| Component | Atoms | Fraction |
|---|---:|---:|
| Protein (`PROA` + `PROB`) | `14365` | `5.59%` |
| POPC | `52126` | `20.27%` |
| Water (`TIP3`) | `190299` | `74.01%` |
| Ions (`POT` + `CLA`) | `340` | `0.13%` |

Source evidence:

- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/local_static_validation.tsv`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/topol.top`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/toppar/PROA.itp`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/toppar/PROB.itp`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/toppar/POPC.itp`

R1 job `8305210188` reduced the baseline atom count from `263906` to `257130`, a delta of `-6776` atoms (`-2.57%`). The molecule-count delta is driven by `TIP3`, `POT`, and `CLA`; `PROA`, `PROB`, and `POPC=389` are unchanged. Therefore this instance is a Z-only water/ion reduction with unchanged XY/membrane footprint.

## Public Case Check

The reduced `chctrl` protein fraction falls within the public comparison range for explicit-solvent membrane systems.

| Case | System class | Public / parsed size | Protein or core fraction interpretation |
|---|---|---:|---|
| NAMD DHFR benchmark | soluble protein + water | `23558` total; parsed `2489` protein atoms and `21069` water atoms from the official input package | Soluble protein is about `10.6%` of total atoms. |
| NAMD ApoA1 benchmark | protein + lipid + water | `92224` total; parsed `6410` protein atoms, `21440` lipid atoms, and `64374` water atoms from the official input package | Protein is about `7.0%` of total atoms, close to the reduced `chctrl` fraction. |
| CB1 receptor MD | single GPCR + POPC + TIP3P + 0.15 M NaCl | reported `90914-94179` total atoms and `190-194` POPC molecules | A single GPCR membrane system already reaches about 91k-94k atoms. |
| hA2AR caffeine MD | single GPCR + mixed membrane + water + ions | reported about `151522-152414` total atoms depending on membrane composition | Single-GPCR near-physiological membranes can be about 150k atoms. |
| 5-HT7:G_s MD | GPCR + heterotrimeric G protein + POPC + TIP3P + ions | reported active/preassembled complex boxes of `131 x 131 x 165 A` and `143 x 143 x 160 A` | Box volume is comparable to reduced `chctrl` (`120.2529 x 120.2529 x 187.835 A`). |

External source pointers:

- NAMD benchmarks: `https://www.ks.uiuc.edu/Research/namd/benchmarks/`
- NAMD DHFR input package: `https://www.ks.uiuc.edu/Research/namd/benchmarks/systems/dhfr_gpu.tar.gz`
- NAMD ApoA1 input package: `https://www.ks.uiuc.edu/Research/namd/benchmarks/systems/apoa1_gpu.tar.gz`
- CB1 toggle-switch MD, DOI `10.1038/s41598-021-01767-5`, EuropePMC XML: `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8595625/fullTextXML`
- hA2AR caffeine MD, DOI `10.1371/journal.pone.0126833`, EuropePMC XML: `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4439127/fullTextXML`
- 5-HT7:G_s MD, DOI `10.1021/acs.jcim.5c01698`, EuropePMC XML: `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12606645/fullTextXML`

## Interpretation

The reduced `chctrl` system has a protein fraction consistent with comparable explicit-solvent membrane systems. It is large because it retains a full GPCR-Galpha complex, POPC membrane, explicit water, ions, and full-system physical sanity evidence.

The current R1 instantiation is still useful as evidence that the `120 A` XY / `20 A` water package can build and run briefly on E2. As a compute-saving route, it only removed `2.57%` of atoms, below the reduction needed for the current E2 constraint.

Further Z water-thickness reduction as the primary solution requires a new source-backed physical rationale. Additional Z shaving is likely to create hydration, pressure, or periodic-image risk before it creates meaningful compute savings.

## Routing Decision

- Keep R1 job `8305210188` as an exploratory chctrl build/run evidence point.
- R1 Z-only remains exploratory evidence rather than a compute-saving success or candidate-transferable replacement.
- Ch-1, Ch-2, and Ch-4 migration requires a new accepted rule.
- Pause further Z-only reduction as the primary route.
- Next route selection should move to either performance/throughput optimization of the full physical object or a clearly re-scoped lower-fidelity model route with its own evidence class.

## References / 所引

- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/local_static_validation.tsv`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/build_notes.md`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/route.json`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/padding_rule.md`
- External source URLs listed above.

## Referenced by / 被引

- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/source_pointers.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/padding_rule.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/command_plan.md`
- `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md`
- `docs/logs/2026-07-04.md`
