# Gpr3 WT/R167Y + ASCR3 matched-pair package status

> Date: 2026-07-17
>
> Last audited: 2026-07-20
>
> Source: local runnable-input gate
> `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/terminal_status.tsv`
> plus the completed AutoDL result package
> `experiments/md-simulation/results/gpr3-r167y-ascr3/README.md`, backed by the
> external append-only `logs/production/rep1/run_state_events.tsv`, timestamped
> completion/postprocess attempts, the 91-row production archive manifest, and
> the 55-file analysis manifest; together with the E2 WT resource preflight
> `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260720_e2_wt_resource_blocker/terminal_status.tsv`.
>
> As of: R167Y production ended normally at
> `2026-07-20T18:13:57+08:00`; the completion gate passed at
> `2026-07-20T10:16:40Z`, postprocess passed at
> `2026-07-20T10:17:37Z`, and the recovered production/analysis manifests were
> revalidated locally on 2026-07-20. WT E2 resource state was verified at
> `2026-07-20T12:33:25+08:00`.
>
> Allowed use: local WT/R167Y runnable-input readiness plus the accepted
> R167Y preproduction/benchmark, 200 ns `TERMINAL_NORMAL`, canonical
> postprocess, and seven-driver single-rep exploratory analysis, plus the dated
> E2 WT resource-blocker decision. This view does not establish WT completion,
> a replicated WT/R167Y genotype comparison, or a categorical pose-stability
> conclusion.
>
> Update trigger: a production/archive identity change, new R167Y replicate,
> E2 WT resource recheck, WT execution evidence, or matched-analysis result.
>
> Status: local gate `LOCAL_RUNNABLE_INPUT_GATE_PASS`; R167Y AutoDL 200 ns rep1
> is `TERMINAL_NORMAL`, postprocess is `PASS`, and the shared seven-driver
> analysis is complete with evidence level `single_rep_exploratory_only`; WT
> E2 stage remains `BLOCKED_E2_GPU_BUSY`. The historical input-promotion HOLD
> was resolved with a versioned 42-row manifest and additive promotion.
> Accepted attempt3 completed geometry repair, standard EM,
> step6.1-step6.6, the 100 ps benchmark, checkpoint-resume, production,
> completion finalization, postprocess, and analysis. The production archive
> validates `91/91 PASS`; the canonical analysis/content validator returned
> 45 PASS checks and its checksum manifest validates `55/55 PASS`. The WT arm
> reuses the receptor-only base from CHARMM-GUI job
> `7628627163`; the matched R167Y receptor-membrane
> base from job `8426884163` has been received and intake-audited. Both arms now
> have transformed ASCR3, reviewed clash/POPC decisions, pair-specific final
> coordinates/topologies/indexes, and zero-warning final `grompp` evidence.
>
> Scope: package-local material checkpoint for the Gpr3 WT/R167Y matched MD
> input gate.
>
> 2026-07-30 docking input boundary: the ASCR3 starting pose was selected from a
> now-withdrawn docking release. The accepted R167Y terminal state and package
> provenance are unchanged, but allowed interpretation is limited to this actual
> historical starting pose and single-rep exploratory evidence. This package
> does not validate the frame-repaired candidate ranking or define a future
> shortlist.

## Current Contents

This directory contains the primary matched R167Y receptor upload, retained
independent-AF3/PPM sensitivity bodies, package-local ligand topology
materials, a promoted single-pose ASCR3 docking SDF, and a standalone 46-atom
ASCR3 coordinate in the independent docking-receptor frame. The returned
matched R167Y receptor-membrane base is preserved as an ignored byte-identical
archive plus extracted local payload; its compact intake status and manifest
are Git-visible. The matched receptor method and coordinate audit are in
`receptor/matched_backbone_status.md`. The local runnable-input evidence at
`experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/`
records the unique docking-receptor provenance, receptor transform, shared
46-atom ligand, pair-specific assembly, final validators, and warning reviews.

The first E2 WT execution attempt stopped at the read-only resource preflight.
At `2026-07-20T12:33:25+08:00`, two other users' Python jobs occupied the A100
with 66,637 MiB of 81,920 MiB in use. No remote run root was created and no
input, preproduction, benchmark, or production stage started. Evidence is in
`experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260720_e2_wt_resource_blocker/`.

The R167Y temporary launch wrapper initially sampled GPU state without emitting
periodic formal events. The source-first runner was attached additively without
changing the frozen launch package or restarting `mdrun`; it then maintained
30-minute `RUNNING_VERIFIED` events through step 98,937,000. The launch wrapper
recorded `TERMINAL_NORMAL` at `2026-07-20T18:13:57+08:00`, and the completion
gate independently confirmed step 100,000,000 / 200,000 ps. Historical
heartbeat evidence remains in
`experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260720_autodl_clone_attempt3_periodic_heartbeat/`;
the current completion/postprocess/analysis entry is
`experiments/md-simulation/results/gpr3-r167y-ascr3/README.md`.

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
- [x] `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`
- [x] WT/R167Y `final_manifest.tsv`, `final_input_contract.json`, `final_warning_contract.json`, and `terminal_status.tsv`

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
docking frame. The gate applies the audited docking-receptor-to-matched-WT
transform and then one WT-base bridge to all 46 atoms; both arms consume the
same transformed GRO body (SHA256
`db5b3e1aaffffa2d8006cd413ef025864d759ca46aa0c1f0dc46ed7ffa459a1c`).

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
| Local runnable-input evidence | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md` |
| WT final evidence manifest | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/wt/final_manifest.tsv` |
| R167Y final evidence manifest | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/r167y/final_manifest.tsv` |
| Historical AutoDL clone input-promotion HOLD | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260719_autodl_clone_attempt3_input_promotion_hold/README.md` |
| Historical AutoDL production early gate | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260719_autodl_clone_attempt3_running_early_gate_pass/README.md` |
| Historical AutoDL periodic heartbeat | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260720_autodl_clone_attempt3_periodic_heartbeat/README.md` |
| Completed R167Y result and recovery contract | `experiments/md-simulation/results/gpr3-r167y-ascr3/README.md` |
| R167Y single-rep seven-driver report | `experiments/md-simulation/results/gpr3-r167y-ascr3/analysis/gpr3_r167y_ascr3_rep1_chctrl_metric_analysis_20260720.md` |

## Still Missing

- [x] canonical WT receptor backbone in an accepted PPM-oriented frame
- [x] exact-backbone R167Y mutation plus local CHARMM36m geometry EM
- [x] primary matched R167Y CHARMM-GUI upload PDB and shared settings
- [x] WT receptor/membrane base from CHARMM-GUI job `7628627163`
- [x] independent-AF3/PPM chain retained as starting-structure sensitivity evidence
- [x] standalone ASCR3 46-atom ligand coordinate layer in docking-pose spatial frame
- [x] matched R167Y CHARMM-GUI Membrane Builder returned package from job `8426884163`
- [x] docking-receptor-to-matched-WT transform for the selected ASCR3 pose
- [x] ASCR3 insertion into both WT and matched-R167Y receptor/membrane frames
- [x] pair-specific post-genion final coordinates
- [x] pair-specific topologies with coordinate molecule counts checked
- [x] package-local indexes regenerated from each post-genion final coordinate
- [x] WT and R167Y system-specific `grompp` warning reviews
- [x] clone-host preflight and independent GPU smoke
- [x] reconcile the frozen manifest identity and repeat additive input promotion
- [x] complete R167Y preproduction, 100 ps benchmark, launch, and early-runtime gates
- [x] attach the periodic production heartbeat and route future launch/resume packages through the tested runner
- [x] complete and finalize R167Y 200 ns production rep1
- [x] archive/postprocess the completed trajectory and run the shared analysis gates
- [ ] rerun the E2 WT resource preflight after the foreign GPU jobs finish
- [ ] implement and test generic production/postprocess drivers and remove site-specific assumptions before E2 deployment
- [ ] complete WT E2 environment/input/preproduction/benchmark/production gates

## Next Action

The R167Y AutoDL lane is complete through production, postprocess, and the
single-rep seven-driver analysis. The verified remote check found no
`gmx_mpi` and no tmux server after the local archive had validated, so the
AutoDL instance no longer needs to remain powered on. Further scientific
promotion requires the matched WT arm and replicate design; do not infer a
replicated genotype effect from this rep1 alone.

For the WT E2 lane, wait for the foreign AlphaFold 3 and UNI2 GPU jobs recorded
in the 2026-07-20 blocker package to finish. Then repeat the full 15-minute
resource preflight before any remote write, bundle transfer, or deployment.

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
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/terminal_status.tsv`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260719_autodl_clone_attempt3_input_promotion_hold/README.md`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260719_autodl_clone_attempt3_running_early_gate_pass/README.md`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260720_autodl_clone_attempt3_periodic_heartbeat/README.md`
- `experiments/md-simulation/results/gpr3-r167y-ascr3/README.md`
- `experiments/md-simulation/results/gpr3-r167y-ascr3/analysis/gpr3_r167y_ascr3_rep1_chctrl_metric_analysis_20260720.md`
- `experiments/md-simulation/archive-router/gpr3-r167y-ascr3_200ns-rep1_20260720_archive.sha256`
- `experiments/md-simulation/scripts/run_gpr_md_production_heartbeat.sh`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260720_e2_wt_resource_blocker/README.md`
- `docs/ops/charmm-gui-membrane-builder.md`

## Referenced by / 被引

- `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`
- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-06.md`
- `docs/logs/2026-07-16.md`
- `docs/logs/2026-07-17.md`
- `docs/logs/2026-07-19.md`
- `docs/logs/2026-07-20.md`
