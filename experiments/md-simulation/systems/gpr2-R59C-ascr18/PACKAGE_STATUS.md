# Gpr2_R59C + ASCR18 package status

> Date: 2026-07-16
>
> Last audited: 2026-07-27
>
> Source: dated run-local terminal and archive evidence under
> `/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716`,
> mirrored compactly in the external payload root and routed by the
> [55-row final archive manifest](../../archive-router/gpr2-r59c-ascr18_200ns-rep1_20260716_archive.sha256).
> `run_state_events.tsv` is the runtime write authority. The linked
> validator-promoted terminal records establish the dated rep1 terminal state;
> this document is not a fresh live E2 check.
>
> As of: the terminal and full-archive evidence is dated
> `2026-07-19T23:33:18+08:00`. On 2026-07-27, the Git manifest was
> byte-identical to the external final manifest, and every currently present
> local body matched: `25/25 present`, with the other 30 entries remaining
> E2-only.
>
> Allowed use: detailed package readiness, dated production/postprocess
> terminal state, canonical rep1 analysis routing, and descriptive
> dynamic-pocket triage. Any new run-changing action still requires a live
> check no older than 15 minutes and a current work order.
>
> Update trigger: a new replicate/work order, or a changed run/output checksum
> identity.
>
> Status: `REP1_COMPLETE_ANALYZED_MATCHED`. The 200 ns physical trajectory,
> audit finalization, E2 postprocess, shared seven-driver analysis, and WT/R59C
> matched single-rep comparison completed on 2026-07-19. The ligand-path
> inspection is also complete as exploratory dynamic-pocket triage, with the
> evidence layers separated below.
>
> Scope: package-local readiness, terminal evidence, and canonical result route
> for the Gpr2 R59C mutant GPR MD rep1.

| Stage | Status | Direct evidence |
|---|---|---|
| Physical production completion | `finished`; 130,638 atoms; XTC/EDR both end at 200,000 ps | external `logs/production/gmx_check_production_{xtc,edr}.log`; GROMACS main log |
| Audit finalization | `finished 2026-07-19T21:39:21+08:00`; finalizer exit `0`; production archive `43/43 PASS` | external `logs/production/run_state_events.tsv`, derived `terminal_status.tsv`, `finalizer_exit_code.tsv`, and `production_archive.sha256` |
| Postprocess completion | `finished 2026-07-19T21:41:09+08:00`; 6,438 atoms; 2,001 frames through 200,000 ps; processed manifest `11/11 PASS` | external `processed/rep1/terminal_status.tsv`, `gmx_check_protein.txt`, and `SHA256SUMS_processed_rep1.txt` |
| Seven-driver analysis | complete; seven shared drivers exited `0` | `../../results/gpr2-r59c-ascr18/analysis/run_logs/` and R59C metric report |
| WT/R59C matched single-rep analysis | complete | matched comparison report |
| Ligand-path / dynamic-pocket triage | complete; descriptive only; starting receptor structures and ligand poses differ | ligand-path report and `analysis/ligand_path/` outputs |
| Final archive | historical E2 validator `55/55 PASS` on 2026-07-19; current local audit `25/25 present`, 30 E2-only | archive-router manifest and result-package recovery contract |

## Current Contents

This directory contains the package-local source/provenance chain and the
Git-visible scripts/config used to complete the system. Large generated
GROMACS bodies remain local/ignored or under the E2 run root
`/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716`.
The returned CHARMM-GUI package was a ligand-free intermediate base. The
accepted E2 package contains ASCR18, passed the runnable gate, completed 200 ns,
and produced validated chctrl-compatible inputs plus canonical single-rep and
matched-analysis outputs. The shared ligand-path driver additionally localized
time-resolved ASCR18 movement and direct receptor contacts without assigning a
stable/unstable cutoff or a best mutation.

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

The package-local SDF records the selected first docking pose (`MODEL=1`,
`VINA RESULT=-5.698`) and is the ligand-coordinate provenance source. The
accepted receptor-frame 54-atom coordinate is recorded under
`gromacs/ascr18_receptor_frame/` and was consumed by the E2 assembly.

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
| Runtime state authority | `/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716/logs/production/run_state_events.tsv` |
| Rep1 analysis config | `experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json` |
| Result-package recovery contract | `experiments/md-simulation/results/gpr2-r59c-ascr18/README.md` |
| Result payload manifest | `experiments/md-simulation/results/gpr2-r59c-ascr18/payload_manifest.tsv` |
| Final archive manifest | `experiments/md-simulation/archive-router/gpr2-r59c-ascr18_200ns-rep1_20260716_archive.sha256` |
| R59C seven-driver report | `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_r59c_ascr18_rep1_chctrl_metric_analysis_20260719.md` |
| WT/R59C matched report | `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md` |
| Ligand-path / dynamic-pocket report | `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md` |
| Shared ligand-path driver | `experiments/md-simulation/analysis/chctrl/compare_ligand_paths.py` |

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
- [x] 200 ns rep1 terminal state, final trajectory/energy sanity, and production archive checksum
- [x] chctrl-compatible `processed/rep1/` and seven-driver analysis
- [x] WT/R59C single-rep matched comparison
- [x] WT/R59C ligand-path and dynamic-pocket structural triage

## Next Action

Rep1 has no remaining recovery or analysis action. The current outputs support
matched single-rep exploratory/triage use under the linked reports. WT and R59C
were built from different receptor starting structures and ligand poses, and no
ligand-RMSD cutoff was preregistered; the evidence therefore does not support a
population-level genotype conclusion or a best-mutation claim. `ILE122` is the
first cross-evidence validation site, not a declared best mutation. Any further
replicate or production work requires a new work order, live E2 state check,
resource gate, and explicit authorization.

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
- `experiments/md-simulation/results/gpr2-r59c-ascr18/README.md`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/payload_manifest.tsv`
- `experiments/md-simulation/archive-router/gpr2-r59c-ascr18_200ns-rep1_20260716_archive.sha256`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_r59c_ascr18_rep1_chctrl_metric_analysis_20260719.md`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md`
- `experiments/md-simulation/analysis/chctrl/compare_ligand_paths.py`
- `docs/logs/2026-07-16.md`
- `docs/logs/2026-07-19.md`

## Referenced by / 被引

- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
- `docs/logs/2026-07-15.md`
- `docs/logs/2026-07-19.md`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/README.md`
