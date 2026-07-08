# Drylab agent project instructions

Use the global `drylab-project` skill for this repository.

Slash aliases:
- `/commit` -> global `safe-commit` workflow
- `/truth [topic]` -> global `truth-audit` workflow
- `/censor [scope]` -> global `censor-audit` workflow

Core rule: project memory is an index, not an authority. Verify facts against source docs, logs, configs, code, paper summaries, or data outputs before making strong claims.

For non-trivial drylab work, use `docs/DOCMAP.md` as the entry and context-loading authority. `docs/INDEX.md` is the current-state router; `codex/docs/memory/` is a pointer, warning, and handoff layer only.
