# Gpr3 WT + ASCR3 E2 resource preflight blocker

> Observed: 2026-07-20T12:32:51+08:00 to
> 2026-07-20T12:33:25+08:00.
>
> Terminal status: `BLOCKED_E2_GPU_BUSY`.
>
> Scientific role: `SPLIT_SITE_EXPLORATORY`.

## Outcome

The prerequisite Gpr2 workflow is complete: the E2 production status is
`TERMINAL_NORMAL`, and postprocess finished at
`2026-07-19T21:41:09+08:00`.

The E2 resource gate did not pass. No `gmx_mpi` process was active, but two
other users had live GPU compute processes:

| PID | User | Command family | GPU memory (MiB) |
|---:|---|---|---:|
| 118970 | `liht` | AlphaFold 3 Python job | 61330 |
| 122792 | `zhangyuxuan` | UNI2 feature-extraction Python job | 5294 |

The A100 snapshot reported 66,637 MiB used of 81,920 MiB. In accordance with
the shared-E2 resource gate, neither process was preempted or terminated.

The proposed run root
`/ifs1/User/dengwei/igem/md-simulation/gpr3_wt_ascr3_e2_rep1_20260720`
was absent. The exact expected `gmx_mpi` path was executable, but environment
qualification was not started because the resource gate is earlier in the
launch sequence. No run root was created, no input was transferred, and no
preproduction, benchmark, production, resume, or postprocess command ran.

The repo inspection also found `run_gpr_md_preproduction.sh` and
`prepare_gpr_md_production_gate.sh`, but no generic
`run_gpr_md_production.sh` or `postprocess_gpr_md_rep.sh`. The existing
preproduction/production-gate layer still carries AutoDL-specific contract and
price assumptions. This is a later implementation/test gate, not permission to
deploy during the resource blocker.

## Blocker contract

| Field | Value |
|---|---|
| Stage | `e2_resource_preflight` |
| Inspection command exit | `0` |
| Gate exit | `75` |
| Gate decision | `BLOCKED_E2_GPU_BUSY` |
| Remote mutation | none |
| Completed stages | authority restore; dirty-worktree snapshot; Gpr2 terminal/postprocess verification; E2 process/GPU/quota/storage inspection; planned-root absence check |
| Not started | environment snapshot; generic-driver completion; bundle creation/transfer; preproduction; benchmark; production |
| Recommended next action | Wait for both foreign GPU compute processes to finish, rerun the full live resource preflight, then parameterize/test the generic production and postprocess drivers before any E2 deployment |

## Input identity retained for the next attempt

The accepted WT package was not copied or modified. Its current evidence
identity is recorded in `input_identity.tsv`; the accepted local gate remains
`PASS` with 139,757 atoms and final zero-warning `grompp`.

## Scientific-use boundary

If this WT trajectory is later completed on E2, it may support engineering
completeness, WT structural behavior, qualification, and site-sensitivity
description. It cannot by itself form a formal WT/R167Y genotype comparison
with the R167Y trajectory running on AutoDL. A formal matched comparison still
requires a same-site accepted batch for both arms.

## References / 所引

- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/terminal_status.tsv`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/wt/final_manifest.tsv`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/wt/final_input_contract.json`
- `/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716/logs/production/terminal_status.tsv`
- `/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716/processed/rep1/terminal_status.tsv`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `docs/logs/2026-07-20.md`
- `docs/INDEX.md`
