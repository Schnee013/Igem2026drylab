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

- [chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md](chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md) —
  historical Route 1 chctrl-first plan for a tight full-system rebuild; keep as
  provenance for storage, source gates, padding-rule requirements, and E2
  approval boundaries. Current launch decisions start from `docs/INDEX.md`.
- [chimeric-gpa1-system-reduction-exploration.md](chimeric-gpa1-system-reduction-exploration.md) —
  historical exploration plan for reducing or restraining chimeric Gpa1 MD
  systems after the 2026-06-26 compute-triage decision. It records literature
  search, system inventory, protocol matrix, and benchmark gate design, but
  current project routing belongs to `docs/INDEX.md`.
- [chimeric-gpa1-r4-new-source-acquisition-plan.md](chimeric-gpa1-r4-new-source-acquisition-plan.md) —
  archived R4 source-acquisition provenance after Yang2024/Sahoo2023 extraction.
  Current routing starts from `docs/INDEX.md`.
- [chimeric-gpa1-r4-local-dry-build-material-plan.md](chimeric-gpa1-r4-local-dry-build-material-plan.md) —
  archived/decisioned local-only R4 material provenance after the object
  contract. Detailed no-go rationale lives in
  `r4_local_dry_build_decision_package_20260705.md`; current routing starts from
  `docs/INDEX.md`.
- [mutant-gpr-md-input-gate-plan-20260705.md](mutant-gpr-md-input-gate-plan-20260705.md) —
  active local-only mutant GPR input-gate plan. CHARMM-GUI manual submission is
  intentionally reduced to each system's upload PDB plus `settings.tsv`, using
  `docs/ops/charmm-gui-membrane-builder.md` as the reusable operating guide.
  Smoke/benchmark planning starts after at least one system has concrete final
  coordinate, topology, index, and warning-review files.
- [autodl-gpr3-r167y-md-plan-20260717.md](autodl-gpr3-r167y-md-plan-20260717.md) —
  plan-only AutoDL qualification and `Gpr3_R167Y + ASCR3` production rep1
  execution contract. It defines live-check, exact-pin, transfer, benchmark,
  production/resume, postprocess, archive, cost, confounding, and fallback
  gates.
- [e2-chimeric-md-restart.md](e2-chimeric-md-restart.md) —
  paused/historical NKULiulab E2 restart route for chctrl + Ch-1/Ch-2/Ch-4
  chimeric MD; keep as script inventory and provenance reference. Current launch
  decisions start from `docs/INDEX.md`.
- [chimeric-md-unified-rerun-sites.md](chimeric-md-unified-rerun-sites.md) —
  paused/historical site-integration plan for one unified rerun provenance across
  E2 primary and a Slurm RTX 5090 validated secondary site.
- [docking-repro-full-refresh-slurm.md](docking-repro-full-refresh-slurm.md) —
  historical 2026-05-19 docking-repro full refresh plan that used old Slurm;
  read as executed provenance. Current server entries are routed through
  `docs/INDEX.md` and `docs/ops/`.
