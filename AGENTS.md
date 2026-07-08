# Drylab agent project instructions

Use the global `drylab-project` skill for this repository.

Slash aliases:
- `/commit` -> global `safe-commit` workflow
- `/truth [topic]` -> global `truth-audit` workflow
- `/censor [scope]` -> global `censor-audit` workflow

Core rule: project memory is an index. Source-backed claims come from source docs, logs, configs, code, paper summaries, or data outputs.

For non-trivial drylab work, use `docs/DOCMAP.md` as the entry and context-loading authority. `docs/INDEX.md` is the current-state router; `codex/docs/memory/` is a pointer, warning, and handoff layer only.

Payload/Git tracking rule: load `docs/ops/payload-tracking-policy.md` only when the task classifies generated/runtime/archive payloads, manifests, checksums, `.gitignore`, Git tracking, or `/commit` staging risk. Ordinary status, literature, modeling, and MD interpretation tasks use the DOCMAP route without this policy.
