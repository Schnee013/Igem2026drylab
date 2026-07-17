# Gpr2_R59C + ASCR18 package status

> Date: 2026-07-16
>
> Last audited: 2026-07-16
>
> Status: `RUNNING_PRODUCTION_REP1_ON_E2`. The receptor-frame ASCR18 insertion,
> clash review, final topology/index, 11-warning gate, EM, step6.1-step6.6, and
> 100 ps benchmark have passed on E2. The resulting 130,638-atom holo system
> contains one 406-residue Gpr2_R59C receptor, one 54-atom ASCR18, 200 POPC,
> 88 POT, 100 CLA, and 32,404 TIP3. Its 200 ns rep1 started at
> `2026-07-16T15:48:19+08:00`; the first parseable checkpoint was written at
> `2026-07-16T16:18:26+08:00`.
>
> Scope: package-local material checkpoint for the mutant GPR MD input gate.

## Current Contents

This directory contains the package-local source/provenance chain and the
Git-visible scripts/config used to complete the system. Large generated
GROMACS bodies remain local/ignored or under the E2 run root
`/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716`.
The returned CHARMM-GUI package was ligand-free, but that was an intermediate
base: the accepted E2 package now contains ASCR18 and has passed the runnable
gate. The current task is to preserve the active production run, then generate
chctrl-compatible processed inputs and matched WT/R59C analysis outputs.

Generated package-local files:

- [x] `ligand/Gpr2_R59C_ascr18_pose1.sdf`
- [x] `ligand/README.md`
- [x] `ligand/manifest.tsv`

- [x] `receptor/clean_receptor.pdb`
- [x] `receptor/clean_receptor_status.md`

- [x] `receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb`
- [x] `receptor/ppm_submission/README.md`
- [x] `receptor/ppm_submission/manifest.tsv`
- [x] `receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_raw.pdb`
- [x] `receptor/ppm_submission/output/Gpr2R59CASCR18_ppm2_output_clean.pdb`
- [x] `receptor/ppm_submission/output/ppm_output_manifest.tsv`
- [x] `receptor/ppm_submission/output/ppm_output_status.md`
- [x] `receptor/ppm_submission/output/20260715_current_input_rerun/Gpr2R59CASCR18_ppm2_output_raw.pdb` (local-only payload)
- [x] `receptor/ppm_submission/output/20260715_current_input_rerun/Gpr2R59CASCR18_ppm2_output_clean.pdb` (local-only payload)
- [x] `receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_manifest.tsv`
- [x] `receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md`

- [x] `receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb`
- [x] `receptor/charmm_gui_submission/settings.tsv`

- [x] `gromacs/ASCR18.itp`
- [x] `gromacs/toppar/cgenff_ASCR18.itp`
- [x] `gromacs/posre_ASCR18.itp`
- [x] `gromacs/charmm_gui_return_manifest.tsv`
- [x] `gromacs/charmm_gui_return_status.md`
- [x] `gromacs/charmm_gui_returned/charmm-gui-8417129094.tgz` (local-only byte-identical archive)
- [x] `gromacs/charmm_gui_returned/charmm-gui-8417129094/` (local-only payload)
- [x] `gromacs/ascr18_receptor_frame/ASCR18_receptor_frame.gro`
- [x] `gromacs/ascr18_receptor_frame/ASCR18_receptor_frame.pdb`
- [x] `gromacs/ascr18_receptor_frame/assembly_decision.tsv`
- [x] `gromacs/ascr18_receptor_frame/clash_audit.tsv`
- [x] `gromacs/ascr18_receptor_frame/receptor_alignment.tsv`

Run and analysis contracts:

- [x] `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_preproduction.sh`
- [x] `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_production.sh`
- [x] `experiments/md-simulation/scripts/e2_postprocess_gpr2_r59c_ascr18_rep1.sh`
- [x] `experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json`

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

The package-local SDF contains only the selected first docking pose (`MODEL=1`, `VINA RESULT=-5.698`), not the full 20-pose IFP conversion. It is the ligand-coordinate provenance source; the completed receptor-frame 54-atom coordinate is now recorded under `gromacs/ascr18_receptor_frame/` and was consumed by the E2 assembly.

## Source Pointers

| Layer | Path |
|---|---|
| Receptor source | `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_model_0.cif` |
| AF3 job request | `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_job_request.json` |
| Ligand pose source | `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/Gpr2_R59C_ascr18_pose1.sdf` |
| Ligand pose manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/manifest.tsv` |
| Ligand topology source | `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/ASCR18.itp` |
| CGenFF source | `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/charmm36.itp` |
| Clean receptor PDB | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor.pdb` |
| Clean receptor PDB status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/clean_receptor_status.md` |
| PPM submission package | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md` |
| Current PPM rerun status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md` |
| Current PPM output clean PDB | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/Gpr2R59CASCR18_ppm2_output_clean.pdb` |
| PPM output status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md` |
| PPM submission input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/Gpr2R59CASCR18_ppm2_input.pdb` |
| CHARMM-GUI upload input | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` |
| CHARMM-GUI settings | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv` |
| CHARMM-GUI return intake | `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_status.md` |
| CHARMM-GUI return manifest | `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_manifest.tsv` |
| Current input-gate route | `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md` |
| E2 run root | `/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716` |
| Rep1 analysis config | `experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json` |

## Still Missing

- [x] clean receptor PDB converted from selected AF3 CIF
- [x] PPM 2.0 submission input/provenance package
- [x] PPM 2.0 oriented receptor PDB
- [x] CHARMM-GUI upload PDB and settings
- [x] system-local canonical ASCR18 first-pose SDF and ownership/recovery manifest
- [x] historical-to-current PPM input and clean/upload checksum migration superseded by the versioned 2026-07-15 current-input rerun
- [x] CHARMM-GUI Membrane Builder receptor-membrane output package received and intake-audited (job `8417129094`; ASCR18 absent by design at this stage)
- [x] ligand coordinate insertion/completion aligned to the final receptor package
- [x] `step6.6.gro` final coordinate generated on E2 after EM and step6.1-step6.6
- [x] `topol_phase3.top` molecule counts checked on E2
- [x] package-local `index.fixed.ndx` regenerated from final coordinates on E2
- [x] system-specific production `grompp` gate accepted exactly 11 identified duplicate type-9 ASCR18 dihedral warnings
- [ ] 200 ns rep1 terminal state, final trajectory/energy sanity, and production archive checksum
- [ ] chctrl-compatible `processed/rep1/` and seven-driver analysis
- [ ] WT/R59C single-rep matched comparison

## Next Action

Do not relaunch or overwrite the active production body. Monitor the E2 run to
its 200 ns terminal state; use checkpoint resume only after a non-normal stop,
with a valid TPR/CPT, no active `gmx_mpi`, and the shared-GPU idle gate. After
normal completion, run the package postprocess script, restore the compact
processed payload outside the Git worktree, reuse the shared chctrl seven-driver
family with the rep1 config, and write the WT/R59C matched comparison.

## References / 所引

- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_model_0.cif`
- `experiments/docking-repro/mutagenesis/af3_downloads/gpr2_r59c/fold_gpr2_r59c_job_request.json`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/Gpr2_R59C_ascr18_pose1.sdf`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/manifest.tsv`
- `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/ASCR18.itp`
- `experiments/md-simulation/parameters/ascr18/deprotonated/charmm-gui-7629292909/gromacs/charmm36.itp`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/settings.tsv`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/README.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_manifest.tsv`
- `docs/ops/charmm-gui-membrane-builder.md`
- `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_preproduction.sh`
- `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_production.sh`
- `experiments/md-simulation/scripts/e2_postprocess_gpr2_r59c_ascr18_rep1.sh`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json`
- `docs/logs/2026-07-16.md`

## Referenced by / 被引

- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
- `docs/logs/2026-07-15.md`
