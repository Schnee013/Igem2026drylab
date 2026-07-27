# Gpr3 R167Y matched-backbone preparation status

> Date: 2026-07-17
>
> Status: `READY_FOR_MATCHED_CHARMM_GUI_SUBMISSION`
>
> Scope: receptor-coordinate preparation only. This is not a runnable
> receptor-membrane-ligand package and is not MD stability evidence.

## Primary design

The primary WT/R167Y comparison now uses one receptor backbone and one membrane
orientation:

- canonical backbone and orientation:
  `experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb`;
- WT receptor/membrane base: CHARMM-GUI job `7628627163`, specifically the
  receptor-only `systems/Gpr3_WT/gromacs/step5_input.*` and `topol.top` layer;
- mutant upload:
  `receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`;
- shared builder settings:
  `receptor/charmm_gui_submission/settings.tsv`.

No new PPM submission is needed for the matched mutant because the mutation was
constructed directly in the already PPM-oriented WT coordinate frame. The
independent-AF3/PPM input remains a sensitivity route and must not be submitted
as the primary matched mutant.

## Mutation and local geometry minimization

1. PyMOL `3.1.0` Mutagenesis Wizard replaced chain A residue 167 `ARG` with
   `TYR`.
2. All WT backbone coordinates (`N`, `CA`, `C`, and `O`; 1,604 atoms) were
   restored exactly before minimization.
3. A local CHARMM36m steepest-descent EM was run with GROMACS
   `2025.2-conda_forge`. All backbone atoms and all atoms outside the 5 A
   neighborhood were frozen. Only sidechains in residues
   `160,161,163-172,306,313,336` were allowed to relax.
4. EM converged in 27 steps to `Fmax=828.92987 kJ mol^-1 nm^-1`, below the
   `1,000 kJ mol^-1 nm^-1` stopping criterion. Relative to the exact-backbone
   post-mutation structure, 87 local sidechain heavy atoms moved, with maximum
   displacement `0.529 A`.
5. Only minimized heavy-atom coordinates were transferred to the upload PDB.
   The receptor backbone remains coordinate-identical to the WT source.

This local EM is a clash/geometry cleanup, not membrane equilibration and not a
claim about the biological R167Y conformational ensemble. The returned
receptor/membrane package must still undergo the standard CHARMM-GUI
minimization and six-step restraint-release equilibration.

The promoted generator and complete accepted GROMACS log are routed through
`receptor/matched_backbone_evidence/README.md`. Runtime binary and temporary
working bodies remain outside Git.

## Coordinate audit

| Field | WT source | Matched R167Y upload |
|---|---:|---:|
| Residues | 401 | 401 |
| Protein ATOM records | 3,157 | 3,158 |
| Residue 167 | ARG | TYR |
| HETATM records | 0 | 0 |
| X/Y/Z span (A) | 85.908 / 45.101 / 139.305 | 85.908 / 45.101 / 139.305 |
| SHA256 | `3b7294ce3bf9549ece343123c274aaa422f7650f5f626125c8d256cc9a70192a` | `6b79e0353379eb9bce9bf7d28b896e64e6b74e7b8bd3e5e888ce3222382c4d0f` |

The matched mutant therefore uses the same `90 A` XY setting as the accepted WT
job. The earlier `115 A` requirement belonged to the laterally extended,
independently predicted AF3 mutant and does not carry over to this matched
backbone.

## Ligand boundary

CHARMM-GUI receives the receptor only. Do not upload ASCR3 in Membrane Builder.
The current standalone `ASCR3_pose_completed.gro` is in the independent docking
receptor frame and must not be inserted unchanged. After the matched
receptor/membrane return is received, align the selected ASCR3 pose through the
docking-receptor-to-matched-WT receptor transform, then perform receptor/POPC
clash, topology count, package-local index, and warning gates.

## Sensitivity route retained

The following file remains the checksum-validated independent-AF3/PPM input:

`receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb`

Its SHA256 is
`6ff4497787bef8105dd0db378667df67833531b536161a94ebc18da96f5c3c63`.
It is retained for provenance and possible starting-structure sensitivity
analysis, not for the primary WT/R167Y matched comparison.

## References / 所引

- `experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.gro`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/topol.top`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_evidence/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/INDEX.md`
- `docs/logs/2026-07-17.md`
