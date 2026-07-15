# drylab Claude Code compatibility

This repository is managed with agent-neutral project rules so Claude Code and
Codex read the same source of truth.

## Startup

For any non-trivial drylab task:

1. Read `docs/DOCMAP.md` first.
2. Read `docs/INDEX.md` unless the task is purely local/mechanical and the exact file or scope is already specified.
3. Read `codex/docs/memory/README.md`, then only task-relevant project memory files.

## Core Rules

- Project memory under `codex/docs/memory/` is an index, not an authority.
- Verify facts against source docs, logs, configs, code, paper summaries, or result files before making strong claims.
- If modifying `src/` or `scripts/`, update `docs/logs/YYYY-MM-DD.md` in the same session.
- If adding or moving durable project files, update `docs/DOCMAP.md` and any affected `docs/INDEX.md` pointers.

## References

- Codex entrypoint: `AGENTS.md`
- Document governance: `docs/DOCMAP.md`
- Current project router: `docs/INDEX.md`
- Repo-scoped project memory: `codex/docs/memory/README.md`
