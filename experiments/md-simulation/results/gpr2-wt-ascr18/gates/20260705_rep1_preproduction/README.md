# Gpr2 WT + ASCR18 Rep1 Preproduction Gate Evidence

> Date: 2026-07-05
>
> Remote run root: `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705`

## Decision

Status: historical preproduction gate snapshot.

The local static pre-production audit passed, and the E2 `grompp` warning gate passed for the 200 ns rep1 input. The E2 shared GPU gate failed immediately before `mdrun`, so the script stopped before production.

The later launch and completion evidence supersedes this retry state. Current rep1 evidence is under `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/`, processed trajectory evidence is under `processed/rep1/`, and chctrl metric outputs are under `analysis/`.

## Gate Results

| Gate | Result | Evidence |
|---|---|---|
| Local static input consistency | Pass | `grompp_gpr2_wt_ascr18_rep1_200ns.log`; `gpr2_wt_ascr18_rep1_200ns_out.mdp` |
| Repaired index | Pass | E2 `grompp` command used `input/gromacs/index.fixed.ndx`; see `grompp_gpr2_wt_ascr18_rep1_200ns.log` |
| E2 `grompp` | Pass | `grompp_gpr2_wt_ascr18_rep1_200ns.log` |
| Warning gate | Pass | `grompp_warning_gate.txt`: exactly 11 accepted `cgenff_ASCR18.itp` duplicate type-9 warnings |
| E2 GPU gate | Fail | `gpu_busy_before_mdrun.log`: active compute apps `none`, GPU state `[(23.0, 0.0)]` |
| Production `mdrun` | Not started | `production_rep1_summary.tsv`: `status = gpu_busy_before_mdrun` |

`grompp` also confirms that velocities were taken from the equilibrated `step6.6.gro`, matching the production continuation strategy rather than the benchmark-only velocity regeneration strategy.

## Files

- `gmx_version.log`: E2 GROMACS environment evidence.
- `grompp_gpr2_wt_ascr18_rep1_200ns.log`: full preprocessing log.
- `grompp_warning_gate.txt`: parsed warning-gate decision.
- `gpr2_wt_ascr18_rep1_200ns.mdp`: generated 200 ns production MDP.
- `gpr2_wt_ascr18_rep1_200ns_out.mdp`: `grompp` output MDP.
- `nvidia_smi_before.log`: initial GPU snapshot.
- `nvidia_smi_compute_apps_before_mdrun.csv`: compute-app snapshot before `mdrun`.
- `nvidia_smi_gpu_state_before_mdrun.csv`: utilization and memory snapshot before `mdrun`.
- `gpu_busy_before_mdrun.log`: blocker record.
- `production_rep1_summary.tsv`: terminal status summary.
- `manifest_sha256.txt`: local checksum manifest for this text evidence package.

## Integrity Hold

This historical snapshot is not checksum-clean as of the local-only 2026-07-12
review. `sha256sum -c manifest_sha256.txt` validates 11 of 14 entries and reports
three mismatches:

- `gmx_version.log`
- `gpr2_wt_ascr18_rep1_200ns_out.mdp`
- `nvidia_smi_before.log`

The repository does not establish whether these bodies were replaced during a
later retry, incompletely copied, or paired with stale manifest entries. The
expected checksums are therefore preserved rather than replaced with hashes of
the currently present bodies. Keep this gate package on integrity hold until
the recorded E2 run root is checked against the original 2026-07-05 snapshot.
The later successful launch and final production evidence do not retroactively
repair this historical snapshot.

## Follow-up Evidence

The accepted launch gate is recorded in `../20260706_rep1_launch/`. The completed 200 ns production archive and sanity checks are recorded in `../../raw/rep1/`.

## References / 所引

- `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260706_rep1_launch/README.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/grompp_gpr2_wt_ascr18_rep1_200ns.log`

## Referenced by / 被引

- `experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260706_rep1_launch/README.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/`
- `experiments/md-simulation/results/gpr2-wt-ascr18/payload_manifest.tsv`
