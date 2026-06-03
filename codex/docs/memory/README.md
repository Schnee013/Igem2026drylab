# Drylab project memory

This directory stores repo-scoped project memory for `/Users/roy/Documents/drylab`.
It is a timestamped routing, warning, and handoff layer. It is not an authority
for scientific facts, project status, methods, results, or decisions.

Authoritative facts live in `docs/INDEX.md`, `docs/logs/`, domain docs, code,
configs, result files, paper summaries, and data outputs. Verify factual claims
there before making strong claims.

Codex native global memory and Claude Code private memory should only keep
durable user preferences and a pointer back to `docs/DOCMAP.md`. Do not
duplicate drylab scientific conclusions or project state into agent-native
memory.

## Files

- `current-state.md`: timestamped latest snapshot, historical timeline, and source pointers.
- `execution-discipline.md`: reusable workflow, evidence, claim, and code-change discipline.
- `pitfalls.md`: drylab-specific scientific/documentation traps and guardrails.
- `plan-index.md`: relevant Claude plan files and their current interpretation.
- `references.md`: people / external-contact reference notes.

Repo-owned execution plans live in `codex/docs/plans/`. Memory files may point
to those plans but should not duplicate their content.

## Loading rule

Use this README only when the `docs/DOCMAP.md` task profile or the user's
request specifically needs repo-scoped memory, handoff context, or recurring
pitfall routing. Then read only the memory files relevant to the task. Do not
bulk-load all memory files by default.

## Maintenance rule

Update memory only for durable state changes or recurring guardrails that affect
future sessions. Ordinary tasks should update the daily log, not force a memory
rewrite.

`current-state.md` must keep this fixed structure:

- `last_reviewed`
- `latest_snapshot`
- `state_timeline`
- `source_pointers`

`latest_snapshot` should contain only 5-8 current summary bullets, each with a
log or domain-doc pointer. Timeline entries older than the latest snapshot must
be marked historical and must not be read as current state.

Keep memory concise and pointer-based. Move stable project facts into the
appropriate `docs/` source when they become authoritative; keep memory as an
index and warning layer.

## Migration source

This layer is distilled from selected Claude memory files now archived under `/Users/roy/.claude/projects/-Users-roy-Documents-drylab/memory_legacy_2026-05-12/`. Do not copy those files wholesale; many contain stale state. Preserve rules and source pointers, not historical conclusions.
