# Global Codex instructions

## Claude command compatibility aliases

Treat the following slash-style prompts as aliases for Codex skills when those skills are installed under `~/.codex/skills`:

- `/commit`: use the `safe-commit` skill. Safely inspect, classify, stage one file at a time, and commit. Never push.
- `/truth [topic]`: use the `truth-audit` skill. Audit recent assistant output for unsupported claims and archive the report.
- `/censor [scope]`: use the `censor-audit` skill. Audit code/config/docs consistency, fix objective issues, and archive the report.

If a skill does not auto-trigger, follow the semantic workflow described above.

## Git safety defaults

- Never push unless the user explicitly asks.
- Never run `git add .`, `git add -A`, or `git add --all` for commit workflows.
- Never include AI attribution, Claude/Codex signatures, or co-author lines in commit messages.
- Treat `.env*`, secrets, credentials, tokens, private keys, caches, virtualenvs, and large binary artifacts as dangerous until explicitly confirmed.

## Drylab project context

When the current repository is `/Users/roy/Documents/drylab`, use these project conventions:

- On task start, prefer reading `docs/INDEX.md` for project overview when relevant.
- Read the latest file in `docs/logs/` when recent state matters.
- Load subdocuments on demand rather than reading all docs.
- Key paths:
  - project index: `docs/INDEX.md`
  - document map: `docs/DOCMAP.md`
  - PRD docs: `docs/prd/`
  - modeling docs: `docs/modeling/`
  - learning roadmap: `docs/learning/roadmap.md`
  - decisions: `docs/decisions/`
  - logs: `docs/logs/`
  - modeling code: `src/`
  - experiments: `experiments/`
- For modeling work, read the relevant direction doc first, explain important changes before editing, put code under `src/modeling/{direction}/`, and update progress/version notes when appropriate.
- For literature research, record important findings in the relevant direction doc and, when significant, in the daily log.
- For wiki/paper writing, use `docs/INDEX.md` plus relevant direction docs and follow iGEM wiki citation expectations.
- At wrap-up, remind the user to update `docs/logs/YYYY-MM-DD.md`, `docs/INDEX.md`, and decision records when applicable.
