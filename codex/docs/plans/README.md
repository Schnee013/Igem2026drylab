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

- [chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md](chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md) —
  active Route 1 chctrl-first plan for a tight full-system rebuild; defines
  storage, source gates, padding-rule requirements, and E2 approval boundaries.
- [chimeric-gpa1-system-reduction-exploration.md](chimeric-gpa1-system-reduction-exploration.md) —
  current exploration plan for reducing or restraining chimeric Gpa1 MD systems,
  including literature search, system inventory, protocol matrix, and benchmark
  gates after the 2026-06-26 compute-triage decision.
- [chimeric-gpa1-r4-new-source-acquisition-plan.md](chimeric-gpa1-r4-new-source-acquisition-plan.md) —
  active R4 follow-up plan after Yang2024/Sahoo2023 extraction; focuses the next
  literature pass on direct GPCR-Galpha / Ste2-Gpa1 CG sources, receptor-Galpha
  interface preservation practice, backmapping/revalidation, and an iGEM2026
  timeline decision.
- [e2-chimeric-md-restart.md](e2-chimeric-md-restart.md) —
  paused/historical NKULiulab E2 restart route for chctrl + Ch-1/Ch-2/Ch-4
  chimeric MD; keep as script inventory and provenance reference, not as a
  current launch instruction.
- [chimeric-md-unified-rerun-sites.md](chimeric-md-unified-rerun-sites.md) —
  paused/historical site-integration plan for one unified rerun provenance across
  E2 primary and a Slurm RTX 5090 validated secondary site.
- [docking-repro-full-refresh-slurm.md](docking-repro-full-refresh-slurm.md) —
  historical 2026-05-19 docking-repro full refresh plan that used old Slurm;
  read as executed provenance only, not as a current server entry.
