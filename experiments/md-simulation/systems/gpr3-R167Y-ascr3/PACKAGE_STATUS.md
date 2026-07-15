# Gpr3_R167Y + ASCR3 package status

> Date: 2026-07-06
>
> Last audited: 2026-07-12
>
> Status: ligand-topology scaffold, current receptor/PPM/CHARMM-GUI handoff
> bodies, and a canonical standalone ASCR3 46-atom GRO are present.
> Historical-to-current PPM input and clean/upload checksum migrations are
> unresolved, so the upload is on provenance hold. Runnable gate also requires
> CHARMM-GUI output, receptor-frame final coordinates, topology, index, and
> warning review.
>
> Scope: package-local material checkpoint for the mutant GPR MD input gate.

## Current Contents

This directory currently contains package-local ligand topology materials, current local receptor/PPM bodies, a DUM-free PPM-oriented receptor PDB copied into the intended Git-tracked CHARMM-GUI handoff location, a local `settings.tsv` parameter guide, and a standalone ASCR3 46-atom ligand coordinate in the docking-pose spatial frame. The GRO is explicitly promoted as the intended repo-owned canonical downstream coordinate because the historical producer is retired; its ownership and recovery contract is in `gromacs/ascr3_coordinate_completion/ascr3_coordinate_manifest.tsv`. The historical and current PPM/input hashes are not interchangeable; the explicit hold is recorded in `receptor/ppm_submission/output/ppm_output_status.md`.

Generated package-local files:

- [x] `receptor/clean_receptor.pdb`
- [x] `receptor/clean_receptor_status.md`

- [x] `receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb`
- [x] `receptor/ppm_submission/README.md`
- [x] `receptor/ppm_submission/manifest.tsv`
- [x] `receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb`
- [x] `receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb`
- [x] `receptor/ppm_submission/output/ppm_output_manifest.tsv`
- [x] `receptor/ppm_submission/output/ppm_output_status.md`

- [x] `receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb`
- [x] `receptor/charmm_gui_submission/settings.tsv`

- [x] `gromacs/ASCR3.itp`
- [x] `gromacs/toppar/cgenff_ASCR3.itp`
- [x] `gromacs/posre_ASCR3.itp`
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

The SDF first pose has 24 atoms and serves as the traceable pose/orientation source. The package-local coordinate completion output now provides a 46-atom ASCR3 ligand coordinate in topology atom order, preserving mapped docking heavy-atom coordinates exactly and using the ASCR3 topology charge source. Evidence class: ligand coordinate layer; receptor/membrane-inserted final system coordinate waits for CHARMM-GUI output and package-frame insertion.

## Source Pointers

| Layer | Path |
|---|---|
| Receptor source | `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_model_0.cif` |
| AF3 job request | `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_job_request.json` |
| Ligand pose source | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf` |
| Ligand topology source | `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp` |
| CGenFF source | `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/charmm36.itp` |
| Clean receptor PDB | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor.pdb` |
| Clean receptor PDB status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/clean_receptor_status.md` |
| PPM submission package | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md` |
| PPM output raw PDB | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_raw.pdb` |
| PPM output clean PDB | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/Gpr3R167YASCR3_ppm2_output_clean.pdb` |
| PPM output manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_manifest.tsv` |
| PPM output status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/ppm_output_status.md` |
| PPM submission input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/Gpr3R167YASCR3_ppm2_input.pdb` |
| CHARMM-GUI upload input | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` |
| CHARMM-GUI settings | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv` |
| Current input-gate route | `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md` |
| ASCR3 coordinate-completion status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md` |
| ASCR3 coordinate ownership/recovery manifest | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_manifest.tsv` |
| ASCR3 canonical completed ligand GRO | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro` |
| ASCR3 local derived PDB view | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.pdb` |

## Still Missing

- [x] clean receptor PDB converted from selected AF3 CIF
- [x] PPM 2.0 submission input/provenance package
- [x] PPM 2.0 oriented receptor PDB
- [x] CHARMM-GUI upload PDB and settings
- [x] standalone ASCR3 46-atom ligand coordinate layer in docking-pose spatial frame
- [ ] historical-to-current PPM input and clean/upload checksum migration resolved or superseded by a versioned rerun
- [ ] CHARMM-GUI Membrane Builder output package
- [ ] ASCR3 receptor-frame alignment/insertion into the final CHARMM-GUI receptor/membrane package
- [ ] `step6.6.gro` or equivalent final coordinate
- [ ] `topol_phase3.top` or equivalent topology with molecule counts checked
- [ ] package-local `index.ndx` regenerated from final coordinates
- [ ] system-specific `grompp_warning_gate.txt` warning review

## Next Action

First reconcile the old-to-current checksum transitions recorded in `receptor/ppm_submission/output/ppm_output_status.md`, or supersede them with a new versioned PPM/cleaning run. Only then submit `receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb` to CHARMM-GUI Membrane Builder using `receptor/charmm_gui_submission/settings.tsv` and `docs/ops/charmm-gui-membrane-builder.md`. After downloading the CHARMM-GUI GROMACS output, archive the output under `gromacs/`, then align/insert the canonical `gromacs/ascr3_coordinate_completion/ASCR3_pose_completed.gro` into the receptor/membrane package, run protein/POPC clash sanity, prepare final topology, regenerate the package-local index, and write the Gpr3_R167Y-specific warning review. Smoke or benchmark planning starts after those gates have named evidence.

## References / 所引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_model_0.cif`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr3_r167y/fold_gpr3_r167y_job_request.json`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/ASCR3.itp`
- `experiments/md-simulation/parameters/ascr3/deprotonated/charmm-gui-7629305001/gromacs/charmm36.itp`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_charmmgui_input.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/README.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
