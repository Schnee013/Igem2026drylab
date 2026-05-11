# Drylab Codex project instructions

Use the global `drylab-project` skill for this repository.

Slash aliases:
- `/commit` -> global `safe-commit` workflow
- `/truth [topic]` -> global `truth-audit` workflow
- `/censor [scope]` -> global `censor-audit` workflow

Core rule: project memory is an index, not an authority. Verify facts against source docs, logs, configs, code, paper summaries, or data outputs before making strong claims.

Drylab loading rule:
- For any non-trivial drylab task, read `docs/DOCMAP.md` first.
- Then read `docs/INDEX.md` unless the task is purely local/mechanical and the exact file/scope is already specified.
- Use `docs/DOCMAP.md` as the document-governance and source-routing rulebook.
- Use `docs/INDEX.md` as the current project router for direction status, blockers, recent progress, and active todos.

Codex project memory:
- Codex project memory lives under `codex/docs/memory/`.
- For non-trivial drylab tasks, after `docs/DOCMAP.md` and `docs/INDEX.md`, read `codex/docs/memory/README.md`.
- Then read only the memory files relevant to the task; do not bulk-load all memory files by default.
- Treat Codex memory as a routing, handoff, warning, and workflow-discipline layer, not as final evidence.
- Keep memory concise and pointer-based; move authoritative facts into the appropriate `docs/` source.
