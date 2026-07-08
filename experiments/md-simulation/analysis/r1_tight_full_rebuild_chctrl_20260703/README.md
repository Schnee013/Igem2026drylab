# R1 Tight Full-System Rebuild Chctrl Design Workspace

> Created: 2026-07-03
>
> Route: `R1-tight-full-rebuild`
>
> System: `chimeric-ste2-gpa1-wt` / `chctrl`
>
> Status: local design workspace plus exploratory prototype metadata. CHARMM-GUI job `8305210188` supplied an extracted chctrl GROMACS input package under the prototype root, and user-approved E2 Packages B/C produced chctrl-only step6 minimization/equilibration plus a 100 ps short production test. Ch-1/Ch-2/Ch-4 action requires a separate candidate-transfer gate.

## Scope

This workspace prepares the chctrl-first Route 1 design for a tighter full-system rebuild. The route keeps the full receptor-Galpha complex, POPC membrane, explicit water, and ions. It may reduce only avoidable box, membrane, and solvent padding after a source-backed padding rule is written.

Candidate transfer to Ch-1/Ch-2/Ch-4 requires the reduced `chctrl` prototype to pass build, smoke, short benchmark, and physical sanity gates.

## Current Files

- `source_pointers.md`: source files and evidence roles.
- `padding_rule.md`: pending padding/build rule form and source-gate status.
- `input_manifest.tsv`: initial manifest for current chctrl inputs and planning sources.
- `current_chctrl_geometry_audit.tsv`: read-only initial geometry and topology audit values.
- `prototype_manifest_template.tsv`: required fields for the future prototype manifest.
- `command_plan.md`: command/approval package and execution record; Package A/B/C were run only after explicit user approval.
- `charmm_gui_reduced_chctrl_build_request.md`: human/manual CHARMM-GUI Membrane Builder checklist for producing the exploratory reduced `chctrl` GROMACS package.
- Prototype root `local_static_validation.tsv`: archive checksum, atom-count delta, topology/index/MDP static checks, and local `gmx` absence.
- `run_logs/`: reserved for future local command logs.

The chctrl-only prototype metadata root now exists at:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/
```

That root currently records route metadata, build notes, checksums, the original CHARMM-GUI archive, an extracted `gromacs/` input package, and `local_static_validation.tsv`. The extracted package contains `step5_input.*`, `topol.top`, `index.ndx`, `toppar/`, and step6/step7 MDPs.

User-approved E2 results are stored separately at:

```text
experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/
```

That result root contains Package B step6 outputs, Package C short production outputs, E2-side sanity logs, GPU sampling, and checksum manifests. The current conclusion is that the exploratory reduced `chctrl` prototype can be built through step6 and can run a short 100 ps production test on E2. Padding-rule acceptance and candidate transfer require separate source-backed and physical-sanity gates.

## Boundary

- Preserve `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/` as the historical/current chctrl system root.
- Write benchmark outputs under a dedicated result directory.
- Use topology/molecule counts and builder records for padding interpretation because current raw `.gro` coordinates cross PBC/box bounds.
- Treat atom-count savings as a post-build evidence claim.
- Use the recorded E2 GROMACS environment for future E2-produced binary evidence, following `environments/e2-md-gromacs.md`.
- Additional remote commands require explicit user approval after a concrete command package is written.
- The current Route 1 rule remains `exploratory`; candidate-transfer status requires a source-backed rule.
- Job `8305210188` is a Z-only exploratory build (`120 A` XY, `20 A` water) with unchanged XY/POPC footprint.
- E2 Packages B/C are chctrl-only evidence. Candidate transfer remains blocked until the same rule passes the remaining physical sanity and interpretation gates.
