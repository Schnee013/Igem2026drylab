# Gpr2_R59C + ASCR18 package status

> Date: 2026-07-06
>
> Last audited: 2026-07-12
>
> Status: ligand-topology scaffold and current receptor/PPM/CHARMM-GUI handoff
> bodies are present. Historical-to-current PPM input and clean/upload checksum
> migrations are unresolved, so the upload is on provenance hold. Runnable gate
> also requires CHARMM-GUI output, final coordinates, topology, index, and
> warning review.
>
> Scope: package-local material checkpoint for the mutant GPR MD input gate.

## Current Contents

This directory currently contains package-local ligand topology materials, current local receptor/PPM bodies, a DUM-free PPM-oriented receptor PDB copied into the intended Git-tracked CHARMM-GUI handoff location, and a local `settings.tsv` parameter guide. The historical and current PPM/input hashes are not interchangeable; the explicit hold is recorded in `receptor/ppm_submission/output/ppm_output_status.md`. The runnable gate is provenance resolution, CHARMM-GUI output, final ligand/receptor coordinates, a package-local index, a reviewed `grompp` warning gate, and a smoke/benchmark command plan.

Generated package-local files:

- [x] `receptor/clean_receptor.pdb`
- [x] `receptor/clean_receptor_status.md`

- [x] `receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb`
- [x] `receptor/ppm_submission/README.md`
- [x] `receptor/ppm_submission/manifest.tsv`
- [x] `receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb`
- [x] `receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb`
- [x] `receptor/ppm_submission/output/ppm_output_manifest.tsv`
- [x] `receptor/ppm_submission/output/ppm_output_status.md`

- [x] `receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb`
- [x] `receptor/charmm_gui_submission/settings.tsv`

- [x] `gromacs/ASCR18.itp`
- [x] `gromacs/toppar/cgenff_ASCR18.itp`
- [x] `gromacs/posre_ASCR18.itp`

Ligand facts checked from `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/ASCR18.itp`:

| Field | Value |
|---|---|
| Molecule | `ASCR18` |
| Atom count | `54` |
| Heavy atom count used for posre | `23` |
| Total charge from atom charges | `-1.000` |
| Expected atom count | `54` |
| Expected heavy atom count | `23` |
| Expected total charge | `-1.000` |

The ligand pose source is selected for orientation/provenance; final ASCR18 coordinates still have to be aligned into a CHARMM-GUI membrane package.

## Source Pointers

| Layer | Path |
|---|---|
| Receptor source | `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_model_0.cif` |
| AF3 job request | `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_job_request.json` |
| Ligand pose source | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr2_R59C_ascr18_poses.sdf` |
| Ligand topology source | `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/ASCR18.itp` |
| CGenFF source | `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/charmm36.itp` |
| Clean receptor PDB | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor.pdb` |
| Clean receptor PDB status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor_status.md` |
| PPM submission package | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md` |
| PPM output clean PDB | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb` |
| PPM output status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md` |
| PPM submission input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` |
| CHARMM-GUI upload input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` |
| CHARMM-GUI settings | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv` |
| Current input-gate route | `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md` |

## Still Missing

- [x] clean receptor PDB converted from selected AF3 CIF
- [x] PPM 2.0 submission input/provenance package
- [x] PPM 2.0 oriented receptor PDB
- [x] CHARMM-GUI upload PDB and settings
- [ ] historical-to-current PPM input and clean/upload checksum migration resolved or superseded by a versioned rerun
- [ ] CHARMM-GUI Membrane Builder output package
- [ ] ligand coordinate insertion/completion aligned to the final receptor package
- [ ] `step6.6.gro` or equivalent final coordinate
- [ ] `topol_phase3.top` or equivalent topology with molecule counts checked
- [ ] package-local `index.ndx` regenerated from final coordinates
- [ ] system-specific `grompp_warning_gate.txt` warning review

## Next Action

First reconcile the old-to-current checksum transitions recorded in `receptor/ppm_submission/output/ppm_output_status.md`, or supersede them with a new versioned PPM/cleaning run. Only then submit `receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` to CHARMM-GUI Membrane Builder using `receptor/charmm_gui_submission/settings.tsv` and `docs/ops/charmm-gui-membrane-builder.md`. After downloading the CHARMM-GUI GROMACS output, archive the output under `gromacs/`, then prepare final ASCR18 coordinates, final topology, package-local index, and Gpr2-specific warning review. Smoke or benchmark planning starts after those gates have named evidence.

## References / 所引

- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_model_0.cif`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_job_request.json`
- `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr2_R59C_ascr18_poses.sdf`
- `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/ASCR18.itp`
- `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/charmm36.itp`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
