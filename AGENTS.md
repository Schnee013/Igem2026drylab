# Drylab agent project instructions

Core rule: agent/native memory is an index. Source-backed claims come from source docs, logs, configs, code, paper summaries, or data outputs.

For non-trivial drylab work, use `docs/DOCMAP.md` as the entry and context-loading authority. `docs/INDEX.md` is the current-state router.

Completion gate: before declaring a non-trivial task complete, compare its verified outcome with `docs/INDEX.md`. If project-level status, priority, blockers, or active entrypoints changed, update INDEX in the same task. In the final handoff, state whether INDEX was updated or why no project-level field changed.

Decision gate: before downloads, remote jobs, broad edits, restart/continue decisions, or decision-relevant scientific conclusions, present verified facts, unknowns, options, risks, and a recommended next step; obtain confirmation when the route, authority, cost, or irreversible state would change.
