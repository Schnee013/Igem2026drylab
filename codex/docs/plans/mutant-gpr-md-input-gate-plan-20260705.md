# Mutant GPR MD Input-Gate Plan

> Date: 2026-07-05; cleaned current route: 2026-07-12; Gpr2 gate updated:
> 2026-07-16; Gpr3 matched-backbone route updated: 2026-07-17.
>
> Scope: current local input-gate route for `Gpr2_R59C + ASCR18` and
> `Gpr3_R167Y + ASCR3`.
>
> Status: execution-order plan. Live state is not maintained here. Gpr2 package
> detail and runtime freshness are read from its system-local
> `PACKAGE_STATUS.md` and run-local `run_state_events.tsv`; Gpr3 local
> runnable-input state is read from the 2026-07-17 gate `terminal_status.tsv`
> and its system-local `PACKAGE_STATUS.md`.

## Current Authority

Use these files as the current input-gate authority:

| Layer | Current pointer |
|---|---|
| Candidate source | `docs/modeling/P0-docking-md-candidate-shortlist.md` |
| Gpr2 package status | `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md` |
| Gpr3 package status | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md` |
| Gpr2 CHARMM-GUI upload | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/charmm_gui_submission/Gpr2R59CASCR18_charmmgui_input.pdb` + `settings.tsv` |
| Gpr2 current PPM provenance | `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md` |
| Gpr2 CHARMM-GUI return intake | `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_status.md` + `charmm_gui_return_manifest.tsv` |
| Gpr2 E2 preproduction/production contracts | `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_preproduction.sh` + `e2_run_gpr2_r59c_ascr18_production.sh` |
| Gpr2 runtime write authority | `/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716/logs/production/run_state_events.tsv` |
| Gpr2 postprocess/analysis contract | `experiments/md-simulation/scripts/e2_postprocess_gpr2_r59c_ascr18_rep1.sh` + `experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json` |
| Gpr3 matched-backbone method | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md` |
| Gpr3 primary matched R167Y upload | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb` + `settings.tsv` |
| Gpr3 WT receptor/membrane base | `experiments/md-simulation/systems/Gpr3_WT/gromacs/step5_input.*` + `topol.top` from CHARMM-GUI job `7628627163` |
| Gpr3 matched R167Y return intake | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_status.md` + `charmm_gui_return_manifest.tsv` |
| Gpr3 independent-AF3 PPM sensitivity provenance | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md` |
| Gpr3 ASCR3 coordinate layer | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md` |
| Gpr3 local runnable-input evidence | `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md` + `terminal_status.tsv` |
| Reusable CHARMM-GUI guide | `docs/ops/charmm-gui-membrane-builder.md` |
| Current project routing | `docs/INDEX.md` |
| Process history | `docs/logs/2026-07-05.md`, `docs/logs/2026-07-06.md`, `docs/logs/2026-07-09.md`, `docs/logs/2026-07-15.md`, `docs/logs/2026-07-16.md`, `docs/logs/2026-07-17.md` |

The former session-local analysis scaffold is not a current authority source.
System-local status files and output manifests now carry the durable route.

## Next Gate

1. For Gpr2, refresh `run_state_events.tsv` before selecting an action.
   `RUNNING_VERIFIED` preserves the current body; `UNRESOLVED` blocks action;
   `TERMINAL_ABNORMAL` enters the TPR/CPT, process, and shared-GPU resume gate.
2. After `TERMINAL_NORMAL`, verify the 200 ns XTC/EDR final times,
   completion marker, issue scan, energy sanity, production summary, and
   archive checksum; then run the chctrl-compatible postprocess script.
3. Restore the compact processed payload outside the Git worktree, run the
   shared seven-driver family with `CHIMERIC_MD_REPS=1`, and write a
   single-rep WT/R59C matched comparison without inventing a ligand cutoff.
4. For Gpr3, preserve the byte-identical ignored return archive from job
   `8426884163`, both canonical bases, and the local runnable-input evidence.
   Do not resubmit either receptor or route either arm back through input
   assembly without a new versioned contract.
5. Gpr3 is eligible for a separately reviewed remote qualification and
   preproduction plan because both local final coordinate/topology/index/warning
   contracts pass. Do not transfer or run it until Roy independently authorizes
   the environment and execution stage.

## Stop Conditions

- Historical-to-current checksum migration is unresolved and no versioned rerun
  supersedes it: keep only that affected system on provenance hold and do not
  submit it. This no longer applies to Gpr2 or Gpr3 because each now has a
  versioned current-input PPM rerun; preserve the historical records.
- No accepted CHARMM-GUI returned output for the affected system: do not write
  its benchmark plan. This return-intake stop no longer applies to Gpr2 job
  `8417129094` or Gpr3 job `8426884163`; their remaining gates are system
  assembly, validation, or production-stage gates.
- Final ligand coordinate cannot be aligned without unacceptable protein/POPC
  clash: record the clash and stop.
- Topology molecule counts, include paths, or index groups are inconsistent:
  repair the package before writing smoke commands.
- Warning sources are not fully identified: write a warning repair note instead
  of launching E2 work.
- For Gpr2 production, an event older than the freshness window, any
  missing/invalid checkpoint, active-process ambiguity, or busy shared GPU
  blocks automatic resume.

## References / 所引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P0-docking-md-candidate-shortlist.md`
- `docs/ops/charmm-gui-membrane-builder.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/receptor/ppm_submission/output/20260715_current_input_rerun/ppm_output_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_status.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/gromacs/charmm_gui_return_manifest.tsv`
- `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_preproduction.sh`
- `experiments/md-simulation/scripts/e2_run_gpr2_r59c_ascr18_production.sh`
- `experiments/md-simulation/scripts/e2_postprocess_gpr2_r59c_ascr18_rep1.sh`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/matched_backbone_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/charmm_gui_submission/Gpr3R167YASCR3_matched_charmmgui_input.pdb`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_status.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/charmm_gui_return_manifest.tsv`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/terminal_status.tsv`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/receptor/ppm_submission/output/20260716_current_input_rerun/ppm_output_status.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/logs/2026-07-15.md`
- `docs/logs/2026-07-16.md`
- `docs/logs/2026-07-17.md`
- `codex/docs/plans/README.md`
