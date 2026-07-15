# Route 1 Padding Rule

> Status: `exploratory`
>
> Current decision: accepted numeric padding rule is still pending source support. Route 1 job `8305210188` remains a chctrl exploratory build/run evidence point; its Z-only atom-count reduction is too small to serve as the main compute-saving route or a candidate-transferable replacement protocol.

## Rule Requirement

The Route 1 rule must keep the full physical object:

- all receptor and Galpha protein atoms;
- POPC membrane;
- explicit water;
- ions;
- semi-isotropic membrane pressure-coupling compatibility.

Allowed reduction:

- avoidable XY membrane/box padding;
- avoidable z solvent padding;
- only through a reproducible full-system rebuild.

Disallowed in Route 1:

- deleting Galpha domains;
- deleting receptor scaffold or membrane context;
- converting to interface-only subsystem;
- adding route-specific restraints;
- hard freezing as a production shortcut;
- candidate-specific tuning before `chctrl` passes.

## Required Fields Before Build

| Field | Status | Notes |
|---|---|---|
| Starting structure source | exploratory | Preferred source is current `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step5_input.pdb` or a documented centered/PPM-oriented derivative. Current `step6.6.gro` remains an inventory/reference file, not a safe source for direct z-padding interpretation because raw coordinates cross PBC/box bounds. |
| Builder/workflow | exploratory | Preferred workflow is CHARMM-GUI Membrane Builder or a scripted equivalent that reproduces complete membrane-system rebuild behavior. Source extraction supports the CHARMM-GUI workflow but not a project-specific minimum padding number. |
| Force-field family | fixed-draft | Preserve CHARMM-family compatibility with the current project stack unless a later source-backed decision changes it. |
| Membrane composition | fixed-draft | POPC, unless a new decision changes the biological object. |
| XY padding/membrane rule | exploratory | Use the full receptor-Galpha complex footprint, not a truncated protein object. CHARMM-GUI source supports determining planar membrane area from protein cross-sectional area along the membrane normal and area per lipid. No fixed XY margin is accepted for this Ste2-Gpa1 object. |
| Z water/hydration rule | exploratory | Rebuild must preserve intracellular Galpha hydration and avoid protein-image artifacts. No source-backed fixed water thickness is accepted for this object. Any numeric water thickness must be recorded as builder/job output or project exploratory input, not a literature minimum. |
| Ion rule | fixed-draft | Keep explicit ions with neutralization and the current project concentration convention (`0.15 M KCl`) unless the actual builder job records a source-backed alternative. |
| Production MDP carryover | fixed-draft | Preserve current production settings unless the rule explicitly justifies a change. |
| Output trajectory groups | fixed-draft | Preserve full-system TPR/EDR/raw trajectory evidence for physical sanity and preserve protein-only processed trajectory compatibility for interface metric recomputation. |
| Candidate-transfer rule | fixed | Apply the same rule logic to candidates only after reduced `chctrl` passes. |

## Source Gate Verdict

The current source matrix supports Route 1 as a plausible full-system rebuild route. A project-specific minimum box or padding rule for this exact Ste2/Gpa1 or chimeric GPCR-Galpha object still requires source extraction.

Therefore:

- `accepted`: no.
- `exploratory`: yes, for a chctrl-only prototype design using a full membrane-protein builder workflow.
- `rejected`: no, because the workflow itself remains physically plausible and source-supported at the builder-behavior level.

Any future reduced `chctrl` build must record the actual builder inputs/outputs, atom-count delta, topology/index/MDP checks, and full-system sanity evidence before it can be benchmarked. `candidate_replacement` status requires build, smoke, short benchmark, and physical sanity gates.

## Current Exploratory Instantiation

CHARMM-GUI job `8305210188` is the current chctrl-only exploratory instantiation:

- requested XY: `120 A`;
- requested water thickness: `20.0 A`;
- source archive: `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/source_archives/charmm_gui_8305210188_xy120_w20_download.tgz`;
- extracted package: `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/`;
- static validation: `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/local_static_validation.tsv`.

Interpretation:

- The job is a Z-only water/ion reduction attempt because `120 A` XY matches the no-warning historical chctrl XY value and POPC remains `389`.
- The atom-count delta is `-6776` atoms (`257130` vs `263906`), driven by lower `TIP3`, `POT`, and `CLA` counts.
- The job remains `exploratory`; source-backed numeric padding and Ch-1/Ch-2/Ch-4 transfer remain pending gates.

## Current E2 Result Boundary

User-approved E2 Packages B/C for job `8305210188` produced chctrl-only step6 minimization/equilibration outputs and a 100 ps short production test. Evidence is stored at:

```text
experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/
```

This upgrades the prototype build/run conclusion for `chctrl`: the exploratory reduced system can be built through step6 and can run a short production test on E2.

The padding rule remains at `exploratory` status. The numeric `120 A` XY / `20.0 A` water setup is a project exploratory instantiation; source-backed minimum padding, accepted-rule status, and candidate-transferable replacement status remain pending.

## Post-Comparison Compute-Saving Verdict

Public atom-count comparison and local topology counts are recorded in:

```text
experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md
```

Verdict:

- The reduced `chctrl` protein atom fraction is within the public comparison range for explicit-solvent membrane-protein complexes.
- R1 job `8305210188` is a Z-only water/ion reduction because XY and POPC count are unchanged.
- The observed `-6776` atom delta (`-2.57%`) is below the reduction needed for the current E2 compute constraint.
- Further Z-only water-thickness shaving is paused as the primary route unless a new source-backed physical rationale is added.
- Candidate transfer remains blocked; Ch-1/Ch-2/Ch-4 require a new accepted rule before migration.
