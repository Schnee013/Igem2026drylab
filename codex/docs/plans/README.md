# Drylab Project Plans

This directory stores repo-owned execution plans and next-session handoffs for
`/Users/roy/Documents/drylab`.

Plans here are project-local replacements for private assistant plan paths such
as `/Users/roy/.claude/plans/`. They should be usable by Codex, Claude, or a
human reader without depending on tool-private storage.

## Role

- Use this directory for decision-complete execution plans, handoff prompts,
  and current-session plans that need to survive across tools.
- Keep `codex/docs/memory/` short and pointer-based; memory may point here but
  should not duplicate plan content.
- Treat plans as execution guidance, not final scientific evidence. Verify
  status claims against `docs/`, logs, configs, code, and result files before
  acting.

## Current Plans

- [e2-chimeric-md-restart.md](e2-chimeric-md-restart.md) —
  NKULiulab E2 primary-site restart route for chctrl + Ch-1/Ch-2/Ch-4 chimeric MD,
  with clean-start provenance, input/smoke/production gates, and system-configured
  analysis selections.
- [chimeric-md-unified-rerun-sites.md](chimeric-md-unified-rerun-sites.md) —
  current site-integration plan for one unified rerun provenance across E2 primary
  and a Slurm RTX 5090 validated secondary site.
- [docking-repro-full-refresh-slurm.md](docking-repro-full-refresh-slurm.md) —
  historical 2026-05-19 docking-repro full refresh plan that used old Slurm;
  read as executed provenance only, not as a current server entry.
- [ode-v01-task-outline-2026-07-13.md](ode-v01-task-outline-2026-07-13.md) —
  proposed ODE v0.1 staged plan through Wiki-freeze preparation; personal
  assignees must be supplied by the team before execution begins.
- [ode-weekly-plan-2026-07-13.md](ode-weekly-plan-2026-07-13.md) —
  proposed 2026-07-13 to 2026-07-19 ODE understanding-and-minimum-solver plan,
  assigned to named first-week owners.
