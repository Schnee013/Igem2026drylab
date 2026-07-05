# Chimeric Route-Family Selection After R1-Z Downgrade

> Date: 2026-07-04
>
> Scope: chimeric Gpa1 MD compute-triage route selection after reduced `chctrl` R1-Z evidence.
>
> Status: local route-selection memo only. This file is not an E2 approval package and does not reopen Ch-1/Ch-2/Ch-4 production.

## Trigger

R1 job `8305210188` proved that the reduced `chctrl` package can build through CHARMM-GUI step6 and run a 100 ps short production test on E2, but the setup is Z-only:

- reduced `chctrl`: `257130` atoms;
- current chctrl reference: `263906` atoms;
- delta: `-6776` atoms (`-2.57%`);
- `PROA`, `PROB`, and `POPC=389` are unchanged.

This is not enough to solve the current E2 compute constraint. Public atom-count comparison also does not show that the protein fraction is abnormal for an explicit-solvent GPCR-Galpha membrane system.

## Selection

The next chimeric route family should not be more Z-only R1 shaving.

Selected local workstream:

1. **R4 coarse-grained / multiscale source gate** as the next route family to investigate for meaningful compute reduction.
2. **Full-object throughput baseline planning** as a companion scheduling/performance work item, not a system-reduction route.

Interpretation boundary:

- R4 can only be `screening_only` unless a later workflow includes successful atomistic backmapping and comparison against `chctrl`.
- Full-object throughput tuning can preserve the full-system evidence class, but it does not reduce atom count and cannot by itself solve the biological-system-size problem.

## Routes Not Selected As Primary Next Step

| Route | Current handling | Reason |
|---|---|---|
| R1 tight full-system rebuild | Keep job `8305210188` as exploratory chctrl build/run evidence; pause Z-only reduction as the primary path | Current atom-count benefit is only `-2.57%`; no source-backed numeric padding rule exists. |
| R2 layered restraints | Keep as a possible stabilization or early-screening protocol | It does not reduce per-ns atom cost and needs force-constant / release-schedule source extraction before any E2 test. |
| R3 interface-only subsystem | Keep as supporting-mechanism-only unless a new source-backed decision upgrades it | It removes membrane/domain context and is likely geometry-restraint dominated. |
| Direct candidate transfer | Blocked | Ch-1/Ch-2/Ch-4 cannot inherit the exploratory R1-Z setup, and no new candidate route has passed `chctrl` gates. |

## Immediate Local Tasks

1. Screen `experiments/chimeric-gpa1/literature/research_runs/system_reduction_20260703/martini_gpcr_gprotein/` for actual GPCR or GPCR-G protein coarse-grained examples, not generic Martini papers.
2. Add R4-specific "supports / does not support" notes to `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`.
3. Define a `chctrl`-first R4 object contract: retained complex, CG model choice, elastic-network or structure-bias choice, backmapping requirement, and comparison metrics against existing `chctrl` evidence.
4. If E2 is needed later, write a new approval package with remote directory, upload command, environment, commands, GPU/CPU/thread settings, expected duration, logs, stop conditions, download command, and cleanup rule.

2026-07-04 update: tasks 1-2 have an initial extraction pass in `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`. Follow-up targeted citation-chasing is recorded in `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`; the later targeted pass added Cevheroglu et al. 2017 as a Ste2p-Gpa1p interface seed, but still did not find a direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG source. Task 3 remains a source-gate/design task and does not authorize a build.

## Current Blockers

- No direct GPCR-Galpha-specific CG source has been extracted yet. The first local screen is recorded in `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`.
- The 2026-07-04 directed R4 run validated but returned mostly generic CG records and recorded an OpenAlex 429 warning. This is recorded in `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`.
- The targeted GPCR-Galpha citation chase found a final DOI for the P0038 GPCR-lipid record and captured Mohanty et al. 2025 plus Cevheroglu et al. 2017 as Ste2p-Gpa1p interface sources, but none supports a CG build route.
- R4 parameterization and backmapping choices are undefined.
- R5-derived metric-dependency files listed in older startup prompts are absent from the repo; the current exploration plan says those files were removed and any metric dependency table must be recreated from current scripts, selection config, preprocessing logs, and run evidence.
- No additional E2 command is approved by this memo.

## References / 所引

- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/padding_rule.md`
- `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `codex/docs/plans/chimeric-gpa1-system-reduction-exploration.md`
- `docs/decisions/005-md-compute-triage-after-chctrl.md`
- `environments/e2-md-gromacs.md`

## Referenced by / 被引

- `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P3-chimeric-gprotein.md`
- `docs/logs/2026-07-04.md`
