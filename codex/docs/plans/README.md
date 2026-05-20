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

- [docking-repro-full-refresh-slurm.md](docking-repro-full-refresh-slurm.md) —
  docking-repro full refresh on Slurm; ODE pipeline explicitly parked until
  literature review settles Kd/calibration strategy.
