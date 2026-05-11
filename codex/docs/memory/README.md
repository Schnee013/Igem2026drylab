# Drylab project memory

This directory stores repo-scoped project memory for `/Users/roy/Documents/drylab`.
It is versioned with drylab and is separate from Codex native global memories
under `~/.codex/memories/`.

It is not an authority. Use it as a routing, handoff, warning, and workflow-discipline layer. Verify factual claims against source docs, logs, configs, code, result files, paper summaries, or data outputs before making strong claims.

Codex native global memory and Claude Code private memory should only keep
durable user preferences and entry rules such as "for non-trivial drylab tasks,
read `docs/DOCMAP.md`, `docs/INDEX.md`, then this README." Do not duplicate
scientific conclusions or project state into agent-native memory; point back to
this repo-scoped layer and the authoritative `docs/` sources instead.

## Files

- `current-state.md`: current blockers, active next steps, and source pointers.
- `execution-discipline.md`: reusable workflow, evidence, claim, and code-change discipline.
- `pitfalls.md`: drylab-specific scientific/documentation traps and guardrails.
- `plan-index.md`: relevant Claude plan files and their current interpretation.
- `docking-pipeline.md`: docking-repro source pointers and active caveats.
- `chimeric-gpa1.md`: stable chimeric Gpa1 decisions and source pointers.
- `ifp-salt-bridge.md`: ProLIF/PDBQT salt-bridge limitation and current IFP caveats.
- `references.md`: people / external-contact reference notes.

## Loading rule

For non-trivial drylab tasks, after reading `docs/DOCMAP.md` and `docs/INDEX.md`, read this README and then only the memory files relevant to the task. Do not bulk-load all memory files by default.

## Maintenance rule

Keep memory concise and pointer-based. Move stable project facts into the appropriate `docs/` source when they become authoritative; keep memory as an index and warning layer.

## Migration source

This layer is distilled from selected Claude memory files now archived under `/Users/roy/.claude/projects/-Users-roy-Documents-drylab/memory_legacy_2026-05-12/`. Do not copy those files wholesale; many contain stale state. Preserve rules and source pointers, not historical conclusions.
