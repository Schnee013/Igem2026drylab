# Gpr3 WT/R167Y + ASCR3 local runnable-input gate

> Date: 2026-07-17
>
> Terminal status: `PASS` for both local runnable-input arms. Remote
> qualification, transfer, preproduction, benchmark, and production remain
> unauthorized and were not run.

## Outcome

The selected-pose manifest resolves the docking receptor uniquely to
`experiments/docking-repro/results/ifp_analysis_mutants/receptors/Gpr3_R167Y_tm.pdb`
(SHA256 `0d071090099179aae47672862e1c01ccb29cf797701da5ca23592d1964439034`).
A unique 988-atom common-backbone mapping gave receptor RMSD `0.809728 A`.
Across six recorded reasonable selections, the maximum ligand-coordinate
difference was `0.065634 A`, below the recorded operational decision limit.

The transform was applied rigidly to all 46 canonical ASCR3 atoms. Both arms
consume the byte-identical shared base-frame GRO with SHA256
`db5b3e1aaffffa2d8006cd413ef025864d759ca46aa0c1f0dc46ed7ffa459a1c`.
The independent R167Y base bridge differs from the shared WT bridge by ligand
RMSD `0.013060 A` and maximum delta `0.013639 A`.
Post-genion extraction confirms that both final coordinates retain the same
ordered 46 ligand name/XYZ tuples with zero coordinate delta; the audit is
`shared/final_ligand_identity.tsv`.

Clash classification remains explicitly
`OPERATIONAL_CRITERION_PENDING_SOURCE_REVIEW`. For this local input-sanity
gate, the complete pair-specific inventories were reviewed: WT removes POPC
residues `407,514`; R167Y removes POPC residue `408`. No protein contact
crossed the recorded severe-overlap cutoff. These are assembly decisions, not
scientific interaction claims.

| Arm | Final atoms | POPC | POT | CLA | TIP3 | SYSTEM index | Final warnings |
|---|---:|---:|---:|---:|---:|---:|---:|
| WT | 139757 | 201 | 98 | 100 | 35422 | 139757 | 0 |
| R167Y | 139708 | 202 | 97 | 98 | 35363 | 139708 | 0 |

`genion` appended the replacement POT as a final molecule block. The final
topologies preserve that row order, while the validator aggregates repeated
moltype rows for count comparison and independently validates coordinate block
order. Package-local `index_final.ndx` files were regenerated from the
post-genion coordinates.

Initial charge-state `grompp` found exactly one reviewed warning per arm: the
ASCR3-containing pre-genion system had charge `-1`. That warning was accepted
only to create `genion.tpr`, with `-maxwarn 1`. After one POT replacement per
arm, final `grompp` used no `-maxwarn`, exited `0`, and produced zero warnings.
The executable identity is recorded in `gromacs_binary_identity.txt`.

Failed attempts are intentionally retained: the first preparation directory
records the 9-value GRO box parser stop, and each arm's
`validation/final_input/` records the initial incorrect post-genion topology
row-normalization assumption. The corrected validators are under
`validation/final_input_attempt2/`.

## Evidence entry points

- Shared transform and ligand: `shared/`
- WT final package and audit: `wt/final_manifest.tsv`
- R167Y final package and audit: `r167y/final_manifest.tsv`
- Overall terminal decision: `terminal_status.tsv`
- GROMACS environment: `gromacs_binary_identity.txt`
- Commands and validation outcomes: `commands_and_results.tsv`

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/manifest.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro`
- `experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.gro`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/topol.top`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_manifest.tsv`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/logs/2026-07-17.md`
- `docs/INDEX.md`
