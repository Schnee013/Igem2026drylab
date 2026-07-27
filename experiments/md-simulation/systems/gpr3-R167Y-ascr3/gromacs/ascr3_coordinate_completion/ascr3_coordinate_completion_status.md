# ASCR3 Coordinate Completion Status

> Date: 2026-07-17
>
> Last audited: 2026-07-17
>
> Scope: Gpr3 WT/R167Y + ASCR3 matched-pair package-local ligand coordinate
> layer.
>
> Status: the exact 46-atom GRO remains the repo-owned canonical standalone
> ligand coordinate in the independent docking-receptor frame. The audited
> transform and pair assembly have now been completed without changing this
> canonical body; derived matched-frame coordinates and both runnable-input
> arms are recorded under the 2026-07-17 local gate evidence.

## Result

| Field | Value |
|---|---|
| Molecule from topology | `ASCR3` |
| Final atom count | `46` |
| Final heavy atom count | `21` |
| Total charge from topology atom charges | `-1.000` |
| Docking first-pose atoms / bonds | `24` / `24` |
| Template atoms / bonds | `46` / `46` |
| Heavy-atom graph mappings enumerated | `2` |
| Selected mapping rank | `1` |
| Diagnostic rigid-template heavy-atom fit RMSD | `2.9557 A` |
| Diagnostic rigid-template maximum heavy-atom fit delta | `6.0769 A` |
| Completed heavy-atom pose delta | `0.0000 A` |
| Docking score record | `VINA RESULT:    -5.715      0.000      0.000` |
| Local derived PDB view | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.pdb` |
| Canonical GRO input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro` |
| Mapping table | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_heavy_atom_mapping.tsv` |
| Mapping alternatives | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_heavy_atom_mapping_alternatives.tsv` |
| Coordinate source table | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_sources.tsv` |
| Ownership/recovery manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_manifest.tsv` |

## Method

The historical completion script parsed the first molecule in the docking SDF, parsed the deprotonated ASCR3 template SDF and `ligandrm.pdb`, enumerated heavy-atom graph isomorphisms while ignoring hydrogen completeness and bond-order differences, and chose the graph mapping with the lowest rigid heavy-atom fit RMSD as a diagnostic mapping. The selected first molecule is now promoted as `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf`; MD package consumers should use that system-local SDF rather than the `results/**/tmp/` multi-pose run output. The 46-atom coordinate uses the mapped docking heavy-atom coordinates exactly, copies docking polar hydrogens for `O3` and `O4`, and generates the remaining hydrogens from package-local ASCR3 topology connectivity and local heavy-atom geometry. This preserves the selected docking pose heavy atoms while making the output compatible with the 46-atom ASCR3 topology order.

The rigid-template fit is retained only as a diagnostic because the CHARMM-GUI template conformer and the docking conformer differ. The selected rigid fit has RMSD `2.9557 A` and maximum heavy-atom delta `6.0769 A`; the 46-atom coordinate preserves docking heavy-atom positions rather than replacing them with rigidly transformed template heavy atoms.

The standalone GRO uses residue name `ASCR3` and is the accepted exact body for downstream package assembly. The standalone PDB uses residue field `AS3` because fixed-width PDB residue names are three characters; it is retained locally as a derived inspection view and is not required for recovery or assembly. Topology authority remains `ASCR3.itp` plus the package assembly checks.

## Matched-Frame Boundary

The primary comparison uses the PPM-oriented Gpr3 WT backbone and a
coordinate-identical matched R167Y backbone. The selected ASCR3 pose was
generated against an independently predicted R167Y docking receptor, so the
canonical GRO was not copied unchanged into either matched package. With the
matched R167Y CHARMM-GUI return present, the local gate completed:

1. fit the docking receptor to the PPM-oriented matched WT receptor using the
   accepted receptor alignment selection;
2. apply that same rigid transform to all 46 ASCR3 atoms;
3. insert the transformed ligand separately into the WT and R167Y
   receptor/membrane bases;
4. run pair-specific protein/POPC clash, topology molecule-count, index, and
   `grompp` warning gates.

The unique docking receptor, 988-atom alignment, rigid transforms, six-selection
sensitivity audit, shared transformed ligand, and pair-specific outputs are
indexed by
`experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`.
The shared base-frame ligand contains 46 atoms and has SHA256
`db5b3e1aaffffa2d8006cd413ef025864d759ca46aa0c1f0dc46ed7ffa459a1c`.

The WT arm reuses the receptor-only `systems/Gpr3_WT/gromacs/step5_input.*` and
`topol.top` layer from CHARMM-GUI job `7628627163`; the later ASCR18-containing
WT `step6.6.gro` is outside this matched ASCR3 assembly route.

## Ownership And Recovery Contract

- `ASCR3_pose_completed.gro` is a small intended repo-owned canonical input, not an
  expendable operation payload. Its exact bytes are required by the next
  receptor-frame insertion step, while the historical one-off producer is no
  longer retained.
- `ascr3_coordinate_sources.tsv` and the mapping tables are intended Git-tracked compact
  provenance and validator evidence. They explain the coordinate source but do
  not replace the accepted GRO body.
- `ASCR3_pose_completed.pdb` remains a local-only derived view; a future PDB
  may be regenerated from the canonical coordinates without preserving its
  current byte hash.
- Once the intended repo-owned files are committed, recovery is a Git checkout of `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro`, followed by SHA256 verification against `ascr3_coordinate_manifest.tsv`.

## Input Checksums

| Input | SHA256 |
|---|---|
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf` | `ccbd49e840b25c142c1cfcdd7f5247267c8b5099c48d0193427626554803d006` |
| Historical multi-pose source: `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf` | `60cf0012c6f06a147ddf8497e39eee09b177fea5ce8b75b3d27de1680b18ba4d` |
| `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/ascr3_deprotonated.sdf` | `9ff3834a6af8c6552aefb36b65388832b0559774df2cdca5c0bb573ba389851f` |
| `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/ligandrm.pdb` | `e6c9cf8f9a82b779b9c46de34b23f818afefef93e11dcaa37ef60b348542e6ad` |
| `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/upload.crd` | `7749b1c6e969906c755e331c4328a4c2470e80ea3e6eace304e99b38b55c8ee9` |
| `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp` | `ad121770ebf2896be7b0db73de6fc6ecd7dfe6af85cff4fc63c8137432aef20d` |

## Output Checksums

| Output | SHA256 |
|---|---|
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_heavy_atom_mapping.tsv` | `08798d6f7ba26860e3982cafcd4351d1bbdb44edffaff87ef43c30e299b4e0ca` |
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_heavy_atom_mapping_alternatives.tsv` | `85295ea76850c41060d6b827a2c9f20b28e7ffc910282b797c9e0d3bf5e3d96a` |
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_sources.tsv` | `d7d96de0049b41b6aec868fcdf06371de6aa44da47d121ec5049b198b1531492` |
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.pdb` | `a2a146b067577e500aebd6ecfea77634377ece8e2e1d96b92826767f1a3e2f62` |
| `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro` | `06e1e2925b28444aa5a8dec285c0cc52e4372eb415507661ab50244078112448` |
| `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/shared/ASCR3_shared_base_frame.gro` | `db5b3e1aaffffa2d8006cd413ef025864d759ca46aa0c1f0dc46ed7ffa459a1c` |

## Still Missing

- No local coordinate-completion or runnable-input item remains missing.
- Remote qualification, transfer, preproduction, benchmark, and production are
  separate gates requiring independent authorization.

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_manifest.tsv`
- `experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.gro`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/topol.top`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/manifest.tsv`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/ligandrm.pdb`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/ascr3_deprotonated.sdf`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/upload.crd`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_status.md`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/shared/rigid_transforms.tsv`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
- `docs/logs/2026-07-17.md`
