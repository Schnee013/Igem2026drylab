# Chimeric Gpa1 R1 Tight Full-System Rebuild Chctrl Plan

> Created: 2026-07-03
>
> Status: Route 1 planning artifact. This file is not E2 execution approval.
>
> Parent plan: `codex/docs/plans/chimeric-gpa1-system-reduction-exploration.md`.
>
> Protocol matrix: `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md`.

## Decision For This Session

Route 1 is the active planning route because it keeps the complete receptor-Galpha complex, POPC membrane, explicit water, and ions. The reduction target is avoidable box, membrane, and solvent padding, not deletion of protein domains or conversion to a local subsystem.

The first prototype and benchmark object is reduced `chctrl`. Ch-1/Ch-2/Ch-4 must not be rebuilt or benchmarked until the `chctrl` Route 1 prototype passes build, smoke, short benchmark, and physical sanity gates. Candidate application must reuse the same padding/build rule; candidate-specific tuning is a different route.

## Current Evidence Snapshot

Inventory shows the cost driver is mainly solvent and membrane size rather than protein atoms:

| System | Total atoms | Protein | Lipid | Water | Ions | Box area nm2 | Box volume nm3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| chctrl | 263,906 | 14,365 | 52,126 | 197,061 | 354 | 138.016 | 2572.471 |
| Ch-1 | 328,928 | 13,897 | 72,092 | 242,496 | 443 | 181.495 | 3201.568 |
| Ch-2 | 366,017 | 13,906 | 71,958 | 279,642 | 511 | 184.878 | 3577.767 |
| Ch-4 | 370,926 | 13,984 | 71,958 | 284,451 | 533 | 183.332 | 3622.999 |

Source: `experiments/md-simulation/analysis/chimeric_system_reduction_inventory.tsv`.

Caveat: raw `.gro` z coordinates cross PBC/box bounds, so z padding must not be interpreted until molecule-centered unwrapping or an equivalent structure check is done.

## Route 1 Hypothesis

The prepared candidate systems are expensive because the membrane patch and solvent box are larger than necessary for the intact GPCR-Galpha object. A tighter full-system rebuild may reduce per-ns cost while preserving a stronger evidence class than Route 3/4 because the whole protein-membrane-solvent object remains present.

Immediate downgrade triggers:

- protein-image or Galpha-domain image interaction;
- insufficient hydration around the intracellular Galpha region;
- distorted membrane relaxation or nonphysical pressure-coupling behavior;
- inability to compute the current chctrl interface metrics or system sanity checks;
- metric behavior that is inconsistent with existing chctrl control evidence within its evidence boundary.

## Storage Contract

Do not overwrite current prepared systems or early-gate results.

Route 1 planning and source extraction:

```text
codex/docs/plans/chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md
experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md
experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md
```

Current local design artifacts:

```text
experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/
  README.md
  source_pointers.md
  padding_rule.md
  input_manifest.tsv
  current_chctrl_geometry_audit.tsv
  prototype_manifest_template.tsv
  command_plan.md
  run_logs/
```

Future prototype build root, only after source gate:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/
  route.json
  build_notes.md
  source_files.sha256
  gromacs/
```

Future benchmark result root, only after explicit approval:

```text
experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/<run_id>/
```

Every output directory must include `README.md`, `source_pointers.md`, and checksums for generated or copied files. Large trajectories stay in result roots; docs/logs should point to them instead of duplicating tables.

## Source Gate Tasks

Before choosing any numeric padding rule:

1. Extract exact setup defaults or recommendations from CHARMM-GUI or the chosen builder for membrane protein complexes, including XY membrane margin, z water thickness, ion placement, and any warnings about protein image contacts.
2. Reconfirm GROMACS pressure-coupling constraints relevant to a semi-isotropic membrane system.
3. Record whether the source supports a project-specific minimum, a builder default, or only a general warning.
4. Update `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md` with "supports / does not support" language.
5. Write the selected padding/build rule to `padding_rule.md`; do not encode it only in commands.

If no source-backed numeric rule is available, the first R1 prototype may still be project-exploratory, but it must be labeled `hypothesis` and cannot be promoted to `candidate_replacement`.

## Padding Rule Form

The accepted rule must specify:

- starting structure source;
- builder or scripted workflow;
- force-field family and water model;
- membrane composition;
- XY rule: how membrane patch size is determined from the full receptor-Galpha footprint;
- Z rule: how water thickness and Galpha hydration clearance are determined;
- ion concentration and neutralization rule;
- output groups and whether production XTC is protein-only or full-system;
- MDP settings that must remain unchanged from current production unless explicitly justified.

The rule transfers by logic, not by absolute box dimensions. Candidate systems should use the same rule on their own full receptor-Galpha geometry after the reduced `chctrl` benchmark passes.

## Chctrl Prototype Gate Sequence

### Gate A: Current Geometry Audit

Use the existing `chctrl` input files:

- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step5_input.pdb`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step6.6.gro`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/topol.top`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/index.ndx`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step7_production.mdp`

Audit:

- protein XY footprint and minimum image clearance;
- protein, membrane, and water z extents after a safe PBC/centering route;
- POPC count and approximate leaflet split;
- index groups needed by existing analysis;
- whether current production output is protein-only or full-system.

### Gate B: Rebuild Design

Create only metadata first:

- route ID: `R1-tight-full-rebuild`;
- system: `chimeric-ste2-gpa1-wt`;
- prototype label: `r1_tight_full_rebuild_chctrl`;
- exact retained components: all protein atoms, POPC, explicit solvent, ions;
- deleted components: none except avoidable padding produced by rebuild;
- expected atom-count direction: lower than current `chctrl`, but no exact savings claim until build output exists.

### Gate C: Local Build Checks

Run local checks only if required tools exist. Previous local pass did not find `gmx`, so absence of GROMACS should be recorded instead of worked around silently.

Minimum local checks:

- file existence and checksums;
- topology `[ molecules ]` count agreement;
- index group parseability;
- MDP compatibility review;
- no accidental overwrite of current system files.

### Gate D: E2 Approval Package

Stop before E2. The approval package must include:

- exact remote run directory;
- upload/sync command;
- `grompp` command;
- smoke or benchmark `mdrun` command;
- E2-side output preprocessing and evidence command using the recorded E2 GROMACS environment;
- expected wall time;
- GPU/CPU/thread settings;
- logs and output paths;
- stop condition;
- cleanup rule.

No remote command is approved by this plan.

Any future E2-produced `.tpr`, `.cpt`, `.edr`, `.trr`, `.xtc`, or `gmx`-processed evidence output must be checked, converted, preprocessed, and evidence-analyzed with the recorded E2 GROMACS environment for that run. The current E2 authority is `environments/e2-md-gromacs.md`, with `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` as the current authoritative command unless run-specific provenance says otherwise.

## Benchmark Comparison Targets

Compare reduced `chctrl` only against sources with the correct evidence boundary:

- E2 chctrl rep1 early-gate snapshot:
  `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/analysis/e2_ctrl_rep1_slurm_equivalent_analysis_20260627.md`
- Metric summary:
  `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/analysis/early_gate_metrics_summary.csv`
- Historical Slurm control evidence only if separately audited from source logs/results.

Do not present reduced `chctrl` as 3-replicate validation unless that evidence exists.

## Candidate Transfer Rule

Only after reduced `chctrl` passes:

1. freeze the Route 1 padding/build rule;
2. write a short candidate application note;
3. apply the same rule to one candidate prototype;
4. run only a smoke/short benchmark after explicit approval;
5. create a new decision record before any candidate production route is reopened.

Candidate-specific box tuning, restraint insertion, topology simplification, or protein deletion invalidates direct transfer and becomes a new route.

## Immediate Next Actions

1. Done: create `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/`.
2. Extract CHARMM-GUI or chosen-builder padding/setup defaults into `source_pointers.md` and the literature matrix.
3. Write `padding_rule.md` with an explicit "accepted / exploratory / rejected" status.
4. Done: run the initial current geometry audit locally without changing system files.
5. Draft the E2 approval package only after the local metadata and padding rule are complete.
