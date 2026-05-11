---
name: censor-audit
description: Audit and fix objective inconsistencies across code, configuration, paths, imports, documentation, and dependencies. Use when the user says /censor, asks for a consistency audit, wants recent changes checked, or requests code/config/docs linkage verification and repair.
---

# Censor Audit

Audit code/config/docs consistency and fix objective issues with minimal changes.

## Scope

- Default: files modified or added in recent work plus their direct dependency files.
- If the user provides a topic/path after `/censor`, audit that directory/topic and related code/config/docs.

## Dimensions

Check these categories:

1. Argument passing: call signatures, order, count, required params.
2. Missing branches: `None`, empty collections, boundary values, missing fallback/defaults.
3. Unused returns: function results computed but not consumed.
4. Description/implementation mismatch: docstrings/comments/names promise behavior not implemented.
5. Dead config: config fields defined but unread or ineffective.
6. Old logic residue: deprecated paths still reachable, stale fallbacks, impossible branches.
7. Missing paths: hard-coded or configured paths do not exist.
8. Stale path references after move/delete/rename across code, docs, logs, ignore rules, and memory-like files.
9. New config not wired into code.
10. Removed/renamed config still referenced.
11. API contract breakage across callers.
12. Broken imports or stale `sys.path` assumptions.
13. Dead functions/classes/constants with no in-repo usage, unless public API status is plausible.
14. Unused imports.

## Verification rules

- Every finding needs tool-backed evidence.
- Path issues: verify with `ls`, `find`, or equivalent.
- Signature issues: read definitions and all relevant call sites.
- Config issues: grep/search keys across relevant code.
- Dead-code issues: search symbol usage across the repo and be conservative.
- Do not critique strategic decisions; only objective consistency/correctness.

## Fixing rules

- Fix discovered objective issues directly when safe.
- Use minimal diffs; do not perform opportunistic refactors.
- Prefer updating stale references over moving target files.
- If a user decision is required, mark `[NEEDS_USER_INPUT]` with concrete options.

## Output format

For each finding:

```markdown
### [dimension number] Dimension name
**File**: `path/to/file.py:line`
**Issue**: concrete description
**Evidence**: verification result with path/line/search output
**Fix**: concrete change made or proposed
**Status**: [FIXED] / [WONTFIX: reason] / [NEEDS_USER_INPUT]
**Severity**: CRITICAL / HIGH / MEDIUM / LOW
```

Severity:

- CRITICAL: inevitable runtime error such as ImportError, KeyError, FileNotFoundError, wrong arg count.
- HIGH: logic error or silent wrong result.
- MEDIUM: consistency issue with limited immediate runtime impact.
- LOW: hygiene issue.

## Archive

Write the full report to:

```text
docs/logs/censor-audits/YYYY-MM-DD_HHmm.md
```

Create the directory if missing. Include scope, findings, and summary:

```markdown
## Summary
- Detected: X (CRITICAL: a, HIGH: b, MEDIUM: c, LOW: d)
- Fixed: Y
- Needs confirmation: Z
- Frequent dimensions: ...
- High-risk files: ...
- Prevention suggestions: ...
```
