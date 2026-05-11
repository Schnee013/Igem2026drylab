# Codex hook templates

This directory contains project-local hook scripts for drylab.

Codex discovers repo-local hooks from `.codex/hooks.json` only when the project
is trusted and the global feature flag is enabled:

```toml
[features]
codex_hooks = true
```

Before enabling the feature flag, review `~/.codex/hooks.json` as well. Codex
loads matching hooks from active user and project config layers; enabling hooks
for drylab can also activate user-level hooks. Installed Codex plugins can also
bundle hooks; check enabled plugins in `~/.codex/config.toml` when debugging
unexpected hook behavior.

Current default:

- `.codex/hooks.json` enables only `session-end-remind.sh` on `Stop`.
- `session-end-remind.sh` is reminder-only. It returns a JSON `systemMessage`
  and does not block the turn.
- `commit-msg.sh` is a Git hook template installed with `install.sh`; it is not
  a Codex lifecycle hook.

If adding a new Stop hook, return valid JSON on stdout. Plain text stdout is not
valid for Codex Stop hooks.
