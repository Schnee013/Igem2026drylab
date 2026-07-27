# Gpr3 R167Y + ASCR3 AutoDL attempt3 production early gate

> Source: run-local machine-readable artifacts under
> `/root/autodl-tmp/igem/md-simulation/gpr3_r167y_ascr3_rep1_20260717/` on
> `autodl-gpr3-clone`.
>
> As of: `2026-07-20T00:41:11+08:00`.
>
> Allowed use: establish that input promotion, preproduction, the 100 ps
> benchmark, the production launch gate, production start, and the early-runtime
> gate passed for `Gpr3_R167Y + ASCR3` production rep1. This does not establish
> 200 ns completion or any scientific trajectory result.
>
> Update trigger: a newer run-state event, checkpoint, terminal mdrun state,
> completion/finalization gate, or provenance identity change.

## Outcome

`Gpr3_R167Y + ASCR3` production rep1 is running on the AutoDL clone. The
accepted preproduction attempt is
`attempt3_geometry_repair_20260719T152123Z`; the launch gate is
`gate_attempt3_gatefix3_20260719T155749Z`; the tmux session is
`gpr3_r167y_ascr3_autodl_rep1_attempt3_20260719T155749Z`.

The accepted early-runtime snapshot is:

- terminal state: `RUNNING_EARLY_GATE_PASS`;
- checkpoint: step `2,743,100`, time `5,486.2 ps`;
- live log: step `3,432,000`, time `6,864 ps`;
- production runtime estimate: `262.295 ns/day`;
- estimated 200 ns wall time/cost: `18.3000 h` / `52.70 CNY`;
- GPU sampler: 76 samples, mean utilization `55.80%`, peak memory `603 MiB`;
- issue count: `0`;
- CPT/XTC/EDR readability, file growth, and frozen provenance: PASS.

The 100 ps benchmark independently measured `234.103 ns/day`, corresponding to
`20.5038 h` / `59.05 CNY` for 200 ns.

## Gate interpretation

`production_launch_gate.tsv` and `production_launch_gate_summary.tsv` are
immutable pre-launch snapshots, so their `mdrun_started=NO` remains expected.
The later `runtime_terminal_status.tsv`, `run_state_events.tsv`, and
`early_gate_summary.tsv` are the current run-state evidence and record
`mdrun_started=YES`.

The prior input-promotion HOLD remains historical evidence. It was superseded
by a versioned 42-row manifest and additive promotion with `41` pre-existing
identical files, `1` new file, `0` conflicts, and `42/42` post-promotion
identity checks. Failed preproduction/gate evidence and attempts 1/2 were not
overwritten.

The AutoDL instance must remain powered on while production is active.

## Payload and recovery

This directory contains compact status, summary, event, and manifest artifacts.
Raw GROMACS logs, checkpoint/trajectory/energy bodies, GPU samples, and full
gate evidence remain under the run root on `autodl-gpr3-clone`.

Primary recovery pointers:

- preproduction accepted attempt:
  `$RUN_ROOT/preproduction/accepted_attempt.tsv`;
- production launch gate:
  `$RUN_ROOT/production/launch_gate.tsv`;
- runtime status:
  `$RUN_ROOT/logs/production/rep1/terminal_status.tsv`;
- early gate:
  `$RUN_ROOT/logs/production/rep1/early_gate_attempt3fix2_20260719T163746Z/`;
- production outputs:
  `$RUN_ROOT/production/rep1/gpr3_r167y_ascr3_rep1_200ns.*`.

## References / 所引

- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`
- `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260719_autodl_clone_attempt3_input_promotion_hold/README.md`
- `experiments/md-simulation/contracts/gpr3-r167y-ascr3/autodl_preproduction_contract.json`
- `experiments/md-simulation/scripts/run_gpr_md_preproduction.sh`
- `experiments/md-simulation/scripts/prepare_gpr_md_production_gate.sh`

## Referenced by / 被引

- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md`
- `docs/INDEX.md`
- `docs/logs/2026-07-19.md`
