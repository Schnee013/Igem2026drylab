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

- No Codex lifecycle hook is enabled by this repository.
- `commit-msg.sh` is a Git hook template installed with `install.sh`; it is not
  a Codex lifecycle hook.

If adding a Codex lifecycle hook that writes to stdout, follow the Codex hook
JSON contract for that event.
