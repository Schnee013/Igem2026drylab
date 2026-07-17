# Gpr3 WT/R167Y + ASCR3 matched-pair package status

> Date: 2026-07-17
>
> Last audited: 2026-07-17
>
> Status: `RETURN_RECEIVED_MATCHED_BACKBONE_BASE_ONLY`. The WT arm reuses the
> receptor-only base from CHARMM-GUI job `7628627163`; the matched R167Y
> receptor-membrane base from job `8426884163` has been received and
> intake-audited. The independent-AF3/PPM mutant is retained as sensitivity
> evidence only. Neither ASCR3 arm is runnable until receptor-frame ligand
> alignment/insertion, topology, index, and warning gates are complete.
>
> Scope: package-local material checkpoint for the Gpr3 WT/R167Y matched MD
> input gate.

## Current Contents

This directory contains the primary matched R167Y receptor upload, retained
independent-AF3/PPM sensitivity bodies, package-local ligand topology
materials, a promoted single-pose ASCR3 docking SDF, and a standalone 46-atom
ASCR3 coordinate in the independent docking-receptor frame. The returned
matched R167Y receptor-membrane base is preserved as an ignored byte-identical
archive plus extracted local payload; its compact intake status and manifest
are Git-visible. The matched receptor method and coordinate audit are in
`receptor/matched_backbone_status.md`. The selected-pose SDF remains the docking
orientation source, but its completed GRO must be transformed through the
docking-receptor-to-matched-WT alignment before insertion; it cannot be copied
unchanged into the returned matched package.

Generated package-local files:

- [x] `receptor/clean_receptor.pdb`
- [x] `receptor/clean_receptor_status.md`
- [x] `receptor/matched_backbone_status.md`

- [x] `receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb`
- [x] `receptor/ppm_submission/README.md`
- [x] `receptor/ppm_submission/manifest.tsv`
- [x] `receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb`
- [x] `receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb`
- [x] `receptor/ppm_submission/output/ppm_output_manifest.tsv`
- [x] `receptor/ppm_submission/output/ppm_output_status.md`
- [x] `receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_manifest.tsv`
- [x] `receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md`

- [x] `receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb`
- [x] `receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`
- [x] `receptor/charmm_gui_submission/settings.tsv`

- [x] `ligand/Gpr3_R167Y_ascr3_pose1.sdf`
- [x] `ligand/README.md`
- [x] `ligand/manifest.tsv`

- [x] `gromacs/ASCR3.itp`
- [x] `gromacs/toppar/cgenff_ASCR3.itp`
- [x] `gromacs/posre_ASCR3.itp`
- [x] `gromacs/charmm_gui_return_manifest.tsv`
- [x] `gromacs/charmm_gui_return_status.md`
- [x] `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone.tgz` (local-only byte-identical matched-backbone archive; not independent AF3)
- [x] `gromacs/charmm_gui_returned/charmm-gui-8426884163-gpr3-r167y-matched-backbone/` (local-only matched-backbone payload)
- [x] `gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.pdb`
- [x] `gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro`
- [x] `gromacs/ascr3_coordinate_completion/ascr3_heavy_atom_mapping.tsv`
- [x] `gromacs/ascr3_coordinate_completion/ascr3_heavy_atom_mapping_alternatives.tsv`
- [x] `gromacs/ascr3_coordinate_completion/ascr3_coordinate_sources.tsv`
- [x] `gromacs/ascr3_coordinate_completion/ascr3_coordinate_manifest.tsv`
- [x] `gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`

Ligand facts checked from `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp`:

| Field | Value |
|---|---|
| Molecule | `ASCR3` |
| Atom count | `46` |
| Heavy atom count used for posre | `21` |
| Total charge from atom charges | `-1.000` |
| Expected atom count | `46` |
| Expected heavy atom count | `21` |
| Expected total charge | `-1.000` |

The promoted SDF first pose has 24 atoms and serves as the traceable
pose/orientation source. The package-local coordinate completion output provides
a 46-atom ASCR3 ligand coordinate in topology atom order in the independent
docking frame. Evidence class: ligand coordinate layer only. The final matched
ligand coordinate waits for receptor alignment and package-frame insertion into
both returned/reused receptor-membrane bases.

## Source Pointers

| Layer | Path |
|---|---|
| Primary receptor backbone/orientation | `experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb` |
| Matched-backbone method and audit | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md` |
| Matched-backbone local-EM reproducibility evidence | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_evidence/README.md` |
| Primary matched R167Y upload | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb` |
| WT receptor/membrane base | `experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.gro` + `topol.top` (CHARMM-GUI job `7628627163`) |
| Independent-AF3 sensitivity source | `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_model_0.cif` |
| Independent-AF3 job request | `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_job_request.json` |
| Ligand pose source | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf` |
| Historical multi-pose docking SDF source | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf` |
| Ligand topology source | `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp` |
| CGenFF source | `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/charmm36.itp` |
| Independent-AF3 clean receptor/status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor.pdb` + `clean_receptor_status.md` |
| Independent-AF3 PPM sensitivity package | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md` |
| Independent-AF3 versioned PPM evidence | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md` |
| Preserved independent-AF3 upload | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` |
| CHARMM-GUI settings | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv` |
| Matched R167Y CHARMM-GUI return intake | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_status.md` |
| Matched R167Y CHARMM-GUI return manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_manifest.tsv` |
| Current input-gate route | `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md` |
| ASCR3 coordinate-completion status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md` |
| ASCR3 coordinate ownership/recovery manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_manifest.tsv` |
| ASCR3 canonical completed ligand GRO | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro` |
| ASCR3 local derived PDB view | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.pdb` |
| Selected ASCR3 docking pose manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/manifest.tsv` |

## Still Missing

- [x] canonical WT receptor backbone in an accepted PPM-oriented frame
- [x] exact-backbone R167Y mutation plus local CHARMM36m geometry EM
- [x] primary matched R167Y CHARMM-GUI upload PDB and shared settings
- [x] WT receptor/membrane base from CHARMM-GUI job `7628627163`
- [x] independent-AF3/PPM chain retained as starting-structure sensitivity evidence
- [x] standalone ASCR3 46-atom ligand coordinate layer in docking-pose spatial frame
- [x] matched R167Y CHARMM-GUI Membrane Builder returned package from job `8426884163`
- [ ] docking-receptor-to-matched-WT transform for the selected ASCR3 pose
- [ ] ASCR3 insertion into both WT and matched-R167Y receptor/membrane frames
- [ ] pair-specific `step6.6.gro` or equivalent final coordinates
- [ ] pair-specific topologies with molecule counts checked
- [ ] package-local indexes regenerated from each final coordinate
- [ ] WT and R167Y system-specific `grompp` warning reviews

## Next Action

Do not resubmit either receptor: the matched R167Y return from job
`8426884163` is present, and the WT arm starts from the receptor-only
`systems/Gpr3_WT/gromacs/step5_input.*` / `topol.top` base from job
`7628627163`, not from its later ASCR18-containing `step6.6.gro`.

Next derive the docking-receptor-to-matched-WT transform, transform the selected
46-atom ASCR3 pose, insert it separately into both receptor/membrane bases, run
protein/POPC clash sanity, prepare pair-specific topologies and indexes, and
write both warning reviews. Smoke/benchmark planning starts only after these
gates have named evidence.

## References / 所引

- `experiments/md-simulation/structures/ppm2/Gpr3_G1XJN1out_clean.pdb`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.gro`
- `experiments/md-simulation/systems/Gpr3_WT/gromacs/topol.top`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/manifest.tsv`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_model_0.cif`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_job_request.json`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/charmm36.itp`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_manifest.tsv`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
- `docs/logs/2026-07-16.md`
- `docs/logs/2026-07-17.md`
