# Mutant GPR MD Input-Gate Plan

> Date: 2026-07-05; cleaned current route: 2026-07-12.
>
> Scope: current local input-gate route for `Gpr2_R59C + ASCR18` and
> `Gpr3_R167Y + ASCR3`.
>
> Status: two system-local CHARMM-GUI upload packages exist. Neither mutant
> system may be submitted yet because the historical-to-current PPM input and
> clean/upload checksum migrations remain on provenance hold. After that hold
> is resolved or superseded by a versioned rerun, runnable status still requires
> CHARMM-GUI returned output, final ligand insertion/alignment, final topology,
> package-local index, and warning review.

## Current Authority

Use these files as the current input-gate authority:

| Layer | Current pointer |
|---|---|
| Candidate source | `docs/modeling/P0-docking-md-candidate-shortlist.md` |
| Gpr2 package status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md` |
| Gpr3 package status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md` |
| Gpr2 CHARMM-GUI upload | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` + `settings.tsv` |
| Gpr3 CHARMM-GUI upload | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` + `settings.tsv` |
| Gpr3 ASCR3 coordinate layer | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md` |
| Reusable CHARMM-GUI guide | `docs/ops/charmm-gui-membrane-builder.md` |
| Current project routing | `docs/INDEX.md` |
| Process history | `docs/logs/2026-07-05.md`, `docs/logs/2026-07-06.md`, `docs/logs/2026-07-09.md` |

The former session-local analysis scaffold is not a current authority source.
System-local status files and output manifests now carry the durable route.

## Next Gate

1. For each system, reconcile the historical-to-current PPM input and
   clean/upload checksum transitions recorded in its
   `receptor/ppm_submission/output/ppm_output_status.md`, or supersede that
   chain with a new versioned PPM/cleaning run.
2. Only after the corresponding provenance hold is cleared, submit that
   system's `receptor/charmm_gui_submission/*_charmmgui_input.pdb` manually
   using its adjacent `settings.tsv` and the reusable Membrane Builder guide.
3. Archive each downloaded CHARMM-GUI GROMACS output under the matching system
   `gromacs/` directory, preserving download source, job/page warnings, and
   checksums.
4. Prepare final ASCR18 or ASCR3 receptor-frame ligand coordinates.
5. Write or update final topology, molecule-count checks, package-local index,
   and system-specific `grompp_warning_gate.txt`.
6. Only after final coordinate/topology/index/warning evidence exists, write a
   single-system smoke/benchmark command plan. If both systems become complete,
   write a dual-system plan.

## Stop Conditions

- Historical-to-current checksum migration is unresolved and no versioned rerun
  supersedes it: keep that system on provenance hold and do not submit it.
- No CHARMM-GUI returned output: do not write a benchmark plan.
- Final ligand coordinate cannot be aligned without unacceptable protein/POPC
  clash: record the clash and stop.
- Topology molecule counts, include paths, or index groups are inconsistent:
  repair the package before writing smoke commands.
- Warning sources are not fully identified: write a warning repair note instead
  of launching E2 work.
- Any E2 action requires a separate current work order and approval.

## References / 所引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P0-docking-md-candidate-shortlist.md`
- `docs/ops/charmm-gui-membrane-builder.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `codex/docs/plans/README.md`
