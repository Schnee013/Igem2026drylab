---
name: safe-commit
description: Safely create a high-quality git commit. Use when the user says /commit, asks to commit current changes, requests a safe commit, or wants staged changes reviewed before committing. Performs file classification, danger-file exclusion, one-by-one staging, conventional commit message selection, and never pushes.
---

# Safe Commit

Create a safe git commit from the current repository state.

## Workflow

1. Inspect context:
   - `git branch --show-current`
   - `git status --short`
   - `git log --oneline -5`
   - `git diff --stat`
   - `git diff --cached --stat`
2. Review relevant diffs before staging. Use `git diff -- <path>` for modified files and inspect untracked text files before deciding.
3. Classify each changed file:
   - **stage**: relevant, complete code/docs/config changes for the current task.
   - **skip**: unrelated, unfinished, generated, temporary, cache, or bulky artifacts.
   - **dangerous**: secrets, credentials, internal agent config, or large binaries; never stage.
4. Dangerous patterns that must not be staged:
   - `.claude/**`
   - `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`
   - `credentials*`, `*secret*`, `*token*`
   - `node_modules/`, `__pycache__/`, `.venv/`
   - binary files larger than 1 MB unless the user explicitly requests them after warning.
5. Show a staging plan table with file, action, and reason. If the user already gave explicit permission to commit, continue; otherwise ask for confirmation when the plan is ambiguous or risky.
6. Stage files one by one with `git add -- <path>`.
   - Never use `git add .`, `git add -A`, or `git add --all`.
7. Generate three concise candidate commit messages following project style from recent commits:
   - Format: `<type>: <description>` where type is `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, or `ci`.
   - First line ≤ 72 characters.
   - Focus on why/intent, not exhaustive file listing.
   - Never include AI signatures, Claude/Codex attribution, or co-author lines.
8. If the user chooses a candidate, use it. If the user does not choose but explicitly asked to commit, choose the best candidate yourself.
9. Run `git commit -m "<message>"` or a safe multi-line equivalent.
10. Confirm success with `git status --short` and `git log --oneline -1`.

## Hard rules

- Never push.
- Never amend unless explicitly requested.
- Never use `--no-verify`.
- Never stage files outside the approved staging plan.
- If there are no committable changes, say so and do not create an empty commit.
