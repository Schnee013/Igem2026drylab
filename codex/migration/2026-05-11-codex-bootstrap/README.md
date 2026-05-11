# Codex bootstrap migration archive

This directory preserves the temporary Codex migration snapshot that previously
lived under `temp/codex-migration/`.

It is provenance only. Do not treat files here as active runtime configuration
or project authority.

## Current status

- `global/AGENTS.md` was considered during the Codex setup recovery and is
  superseded by the active global/project instructions.
- `skills/drylab-project`, `skills/truth-audit`, and
  `skills/censor-audit` match the currently installed global skill sources as
  of the migration audit.
- `skills/safe-commit` is older than the currently installed global
  `safe-commit` skill, which now supports layered commits for mixed worktrees.
- `agents/openai.yaml` files were migration scaffolds for Codex skill metadata;
  use the installed versions under `~/.codex/skills/` as the active runtime
  source.

## Usage

Use this archive only when auditing how Claude-era command workflows were
translated into Codex skills and project instructions. For normal drylab work,
follow `AGENTS.md`, `docs/DOCMAP.md`, `docs/INDEX.md`, and
`codex/docs/memory/README.md`.
