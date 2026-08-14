# Drylab Project Plans

This directory stores repo-owned execution plans and next-session handoffs for
`/Users/roy/Documents/drylab`.

Plans here are repo-owned durable execution artifacts. They should be usable
by a human or agent without depending on tool-private storage.

## Role

- Use this directory for decision-recorded execution plans, handoff prompts,
  and session plans that need to survive across tools.
- Keep current project status in `docs/INDEX.md`; plans contain execution order
  and source pointers rather than parallel status summaries.
- Plans are execution guidance. Scientific and status claims require verification
  against `docs/`, logs, configs, code, and result files before action.

## Plan Index

Entries below describe each plan's stable scope only. They do not state whether
work is waiting, active, paused, complete, or superseded. Before action, read the
target plan's own boundary and recalibrate it against `docs/INDEX.md` and the
source evidence named by that plan.

- [chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md](chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md) —
  Route 1 chctrl-first tight full-system rebuild contract covering storage,
  source gates, padding-rule requirements, and E2 approval boundaries.
- [chimeric-gpa1-system-reduction-exploration.md](chimeric-gpa1-system-reduction-exploration.md) —
  chimeric Gpa1 MD system-reduction and restraint exploration contract covering
  literature search, system inventory, protocol matrices, and benchmark gates.
- [chimeric-gpa1-r4-new-source-acquisition-plan.md](chimeric-gpa1-r4-new-source-acquisition-plan.md) —
  R4 source-pass provenance covering retained findings, extraction records,
  and evidence boundaries.
- [chimeric-gpa1-r4-local-dry-build-material-plan.md](chimeric-gpa1-r4-local-dry-build-material-plan.md) —
  R4 local material-check record; the detailed no-go rationale is in the
  [material decision](../../../experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md).
- [mutant-gpr-md-input-gate-plan-20260705.md](mutant-gpr-md-input-gate-plan-20260705.md) —
  local mutant GPR input-gate contract covering package inputs, the reusable
  CHARMM-GUI operating guide, assembly, topology, index, and warning gates.
- [autodl-gpr3-r167y-md-plan-20260717.md](autodl-gpr3-r167y-md-plan-20260717.md) —
  AutoDL qualification and `Gpr3_R167Y + ASCR3` production rep1 contract
  covering live checks, exact pinning, transfer, benchmark, production/resume,
  postprocess, archive, cost, confounding, and fallback gates.
- [e2-chimeric-md-restart.md](e2-chimeric-md-restart.md) —
  NKULiulab E2 restart contract for chctrl + Ch-1/Ch-2/Ch-4 chimeric MD,
  including script inventory, resource checks, and launch gates.
- [chimeric-md-unified-rerun-sites.md](chimeric-md-unified-rerun-sites.md) —
  multi-site rerun integration contract covering environment identity,
  benchmark, execution, and provenance across E2 and Slurm routes.
- [docking-repro-full-refresh-slurm.md](docking-repro-full-refresh-slurm.md) —
  Slurm-based docking-repro full-refresh contract covering inputs, execution,
  outputs, validation, and handoff paths.
