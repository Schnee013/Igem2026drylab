# R1 Tight Full-System Rebuild Chctrl Prototype Notes

> Date: 2026-07-04
>
> Status: CHARMM-GUI exploratory `chctrl` GROMACS input package extracted; local static checks complete; user-approved E2 step6 minimization/equilibration and 100 ps short production test completed for chctrl only. Post-comparison review downgraded this Z-only instantiation as insufficient for compute saving. No Ch-1/Ch-2/Ch-4 action has been run.

## Scope

This prototype root is only for `chimeric-ste2-gpa1-wt` / `chctrl`.

Route 1 retains the full receptor-Galpha protein complex, POPC membrane, explicit water, ions, and full-system box/energy evidence. Allowed reduction is limited to avoidable box, membrane, and solvent padding produced by a reproducible full-system rebuild.

## Builder Input Now Present

The CHARMM-GUI archive supplied by the user has been moved under this prototype root and its `gromacs/` package has been extracted here:

```text
source_archives/charmm_gui_8305210188_xy120_w20_download.tgz
gromacs/
```

Archive checksum:

```text
486963899f9522767492e87aead931ddd8398755d08d950bf1d1d9913918745e
```

The archive root is `charmm-gui-8305210188/`. The extracted GROMACS package contains `topol.top`, `index.ndx`, `toppar/`, `step5_input.gro`, `step5_input.pdb`, `step5_input.psf`, `step6.0_minimization.mdp`, `step6.1` through `step6.6` equilibration MDPs, and `step7_production.mdp`.

This is a CHARMM-GUI generated input package. Equilibration and short-production outputs are stored under the separate result root:

```text
experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/
```

## CHARMM-GUI Job Record

Job ID: `8305210188`.

Recorded manual settings and observations:

- `Length of X and Y = 120 A`.
- `Water thickness = 20.0 A`.
- `110 A` and `115 A` XY attempts produced CHARMM-GUI protein-extent warnings and were abandoned.
- `120 A` avoided the protein-extent warning in this manual pass.
- User-reported Step 4 checks: no protein surface penetration and no lipid ring penetration.
- The package is therefore a Z-only exploratory water/ion reduction attempt; XY membrane reduction remains a separate, unproven route.

Because `padding_rule.md` remains `exploratory`, candidate transfer and `candidate_replacement` status require a new source-backed rule.

## Public Atom-Count Comparison And Compute-Saving Interpretation

The public/local atom-count comparison is recorded in:

```text
experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md
```

Conclusion:

- The reduced `chctrl` protein fraction remains within the expected range for an explicit-solvent membrane-protein complex.
- This job is Z-only because XY remains `120 A` and POPC remains `389`.
- The atom-count delta is only `-6776` atoms (`-2.57%`); compute-saving success requires a stronger source-backed reduction.
- Further Z-only water-thickness shaving is paused as the primary route unless a new source-backed rationale is added.
- Candidate transfer remains blocked.

## Local Static Validation

Static validation summary:

```text
local_static_validation.tsv
```

Key facts:

- Local `command -v gmx` returned no path; local `grompp` is unavailable.
- Prototype initial atom count from `gromacs/step5_input.gro`: `257130`.
- Baseline chctrl reference atom count from current `step6.6.gro`: `263906`.
- Atom-count delta: `-6776` atoms (`-2.57%`).
- Topology molecule delta vs baseline: `PROA=1`, `PROB=1`, and `POPC=389` are unchanged; `TIP3` decreases from `65687` to `63433`; `POT` and `CLA` decrease from `177/177` to `170/170`.
- Topology atom sum from `topol.top` and `toppar/*.itp`: `257130`, matching `step5_input.gro`.
- Required index groups parse: `SOLU=14365`, `MEMB=52126`, `SOLV=190639`, `SOLU_MEMB=66491`, `SYSTEM=257130`.
- Production MDP core settings match the current chctrl production MDP for `integrator`, `dt`, `nsteps`, `tc_grps`, `pcoupl`, `pcoupltype`, `constraints`, and `comm_grps`.

Initial-box comparison must be interpreted carefully:

- Historical current `step5_input.gro`: `12.02529 x 12.02529 x 19.28350 nm`.
- Prototype `step5_input.gro`: `12.02529 x 12.02529 x 18.78350 nm`.
- Historical current `step6.6.gro`: `11.74841 x 11.74841 x 18.63860 nm`.

Compare initial boxes only against initial boxes; the historical post-equilibration `step6.6.gro` is a pressure-relaxed state.

## E2 Step6 And Short Production Evidence

User-approved Package B ran on E2 from `step6.0_minimization` through `step6.6_equilibration`.

Evidence:

- Remote directory: `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704`
- E2 GROMACS command: `/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi`
- GROMACS: `2025.4-conda_forge`, Open MPI `5.0.8`, CUDA support.
- Final step6.6 files exist in the result root under `work/`: `.gro`, `.cpt`, `.tpr`, `.edr`, `.xtc`.
- Final step6.6 atom count: `257130`.
- `step6.6_equilibration` performance: `39.920 ns/day`, `0.601 hour/ns`.
- Step6.6 energy summary: temperature `303.201 K`, pressure `0.704 bar`, density `1028.91 kg/m^3`.

Caveat:

- `mdrun_step6.0_minimization.log` contains `86` `LINCS WARNING` matches, but minimization converged to `Fmax < 1000` in `4523` steps.
- Local text scan found no LINCS/fatal/CUDA/nan matches in step6.1-step6.6 equilibration logs.

User-approved Package C ran a short production test from Package B outputs:

- Output prefix: `production_smoke/r1_chctrl_short_prod`
- Override: `-nsteps 50000`
- Nominal duration: `100 ps`
- Final atom count: `257130`
- Performance: `74.362 ns/day`, `0.323 hour/ns`
- GPU sampling: 25 samples; average all-sample utilization `84.36%`; average nonzero utilization `91.70%`; max utilization `99%`; max memory `575 MiB`
- Short production energy summary: temperature `303.192 K`, pressure `7.549 bar`, density `1029.21 kg/m^3`
- Local text scan found no LINCS/fatal/CUDA/nan matches in the short production `mdrun` log.

## Current Build Conclusion

The chctrl-only exploratory prototype can be built through CHARMM-GUI step6 and reached the 100 ps short-production endpoint on E2.

The current conclusion is limited:

- Generated reduced GROMACS input files exist under the prototype root.
- Static file/topology/index/MDP checks are internally consistent.
- Authoritative E2 build/equilibration and short-production evidence exists in the result root.
- E2/result-root evidence is the authority for `grompp`/run behavior; local GROMACS was unavailable for evidence generation.
- The padding rule remains `exploratory`; source-backed numeric padding requires a separate rule.
- Post-comparison interpretation downgrades this Z-only instance as insufficient for the compute-saving goal.
- The historical post-agreement route-family selection is superseded as a current instruction by later R4 material-boundary records; current R4 and next local-workstream ownership starts from those records and `docs/INDEX.md`.
- Long-run physical sanity, metric comparability, and candidate transfer remain blocked.

## E2 Output Analysis Boundary

If a future approved E2 run produces reduced-`chctrl` GROMACS binary outputs, those `.tpr`, `.cpt`, `.edr`, `.trr`, `.xtc`, and any `gmx`-processed evidence outputs must be checked, converted, preprocessed, and evidence-analyzed with the recorded E2 GROMACS environment for that run.

Current E2 environment authority: `environments/e2-md-gromacs.md`.

Current authoritative E2 command unless run-specific provenance says otherwise:

```text
/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
```

Evidence generation for E2-produced binary outputs uses the recorded E2 GROMACS environment for that run. Local or Python analysis is acceptable after E2-side preprocessing produces documented, synced, checksummed analysis inputs.

## Inputs And Evidence

References / 所引:

- `codex/docs/plans/chimeric-gpa1-system-reduction-exploration.md`
- `codex/docs/plans/chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md`
- `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md`
- `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/padding_rule.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/source_pointers.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_reduced_chctrl_build_request.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/command_plan.md`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/source_archives/charmm_gui_8305210188_xy120_w20_download.tgz`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/local_static_validation.tsv`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/README.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/source_pointers.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/local_download.sha256`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step5_input.gro`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step6.6.gro`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/topol.top`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/index.ndx`
- `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step7_production.mdp`
- `environments/e2-md-gromacs.md`

Referenced by / 被引:

- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/source_pointers.md`
- `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/command_plan.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/README.md`
- Next consumer: reduced `chctrl` physical-sanity and metric-comparability review before any candidate transfer.
