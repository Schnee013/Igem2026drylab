---
name: drylab-project
description: Drylab repository startup and operating discipline for /Users/roy/Documents/drylab. Use when Codex works in this repository on non-trivial project tasks, scientific/modeling status, documentation, code changes, logs, memory recovery, docking, MD simulation, ODE, chimeric Gpa1, wet-lab handoff, or project planning.
---

# Drylab Project

Use this skill as the entry discipline for `/Users/roy/Documents/drylab`. It is a loader and routing guide, not an authority for scientific facts.

## Startup

For any non-trivial drylab task:

1. Read `docs/DOCMAP.md` first.
2. Read `docs/INDEX.md` unless the task is purely local/mechanical and the exact scope is already specified.
3. Read `codex/docs/memory/README.md`.
4. Read only the memory files relevant to the task. Do not bulk-load all memory by default.
5. If recent state matters, read the latest relevant `docs/logs/YYYY-MM-DD.md` file and the relevant domain doc under `docs/modeling/`, `docs/prd/`, `docs/ops/`, `docs/papers/`, or `docs/decisions/`.

Treat memory, old plans, and session imports as indexes. Verify facts against source docs, logs, configs, code, paper summaries, or result files before making strong claims.

## Source Routing

- Document governance and source-of-truth rules: `docs/DOCMAP.md`.
- Current project routing, blockers, and active todos: `docs/INDEX.md`.
- Codex memory router: `codex/docs/memory/README.md`.
- Current state pointers: `codex/docs/memory/current-state.md`.
- Evidence and workflow discipline: `codex/docs/memory/execution-discipline.md`.
- Pitfalls and active guardrails: `codex/docs/memory/pitfalls.md`.
- Historical Claude plans: use `codex/docs/memory/plan-index.md` as an index only; calibrate against current docs and logs.

## Evidence Discipline

- Do not present memory-derived claims as verified facts.
- Completion/status words such as done, fixed, verified, passed, confirmed, unresolved, submitted, deployed, or merged require source-backed verification.
- Scientific cutoffs, thresholds, geometry definitions, and go/no-go criteria require exact pointers. If a value is project-defined, label it as an operational heuristic.
- Before quoting paths, command names, script names, section references, metric names, result files, or numeric conclusions, verify them with file reads or search.
- Avoid universal or superlative wording unless the relevant set has been enumerated.

## Change Discipline

- Keep edits scoped to the requested task and established repository patterns.
- If modifying `src/` or `scripts/`, update `docs/logs/YYYY-MM-DD.md` in the same session. If the change affects cross-session understanding, also update the relevant pointer-style memory under `codex/docs/memory/`.
- If adding or moving durable project files, update `docs/DOCMAP.md` when the documented directory structure or governance changes.
- For long or decision-relevant drylab workflows, pause before downloads, remote jobs, large analyses, restart/continue decisions, broad edits, or scientific status judgments. Present verified facts, missing information, options, risks, and a recommended next step.

## Active Guardrails

- Do not treat stale docking Top candidates as wet-lab recommendations until Gpr3 F follow-up, ratio refresh, and IFP refresh are complete.
- Do not restart Ch-1/Ch-2/Ch-4 chimeric MD automatically from memory alone. Use current chctrl analysis reports and ask for a decision when results remain caveated.
- Windows 7500F is deprecated for new compute. Use Slurm docs for current compute; consult Windows archive docs only for historical files.
- On Mac, run docking-repro work in the `docking` conda environment unless a task-specific doc says otherwise.

