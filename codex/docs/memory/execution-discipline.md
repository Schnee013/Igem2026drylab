# Execution discipline

> Frozen historical snapshot. Retained for traceability; not an active policy
> source. Current repository governance starts at `AGENTS.md` and
> `docs/DOCMAP.md`.

> Distilled from Claude feedback memories: `feedback_memory_not_terminal_source.md`, `feedback_completion_claim.md`, `feedback_read_before_quoting.md`, `feedback_universal_quantifier.md`, `feedback_math_derivation_verify.md`, `feedback_grep_all_callers.md`, and recent Codex latency incident.

## Short path for simple tasks

- For simple file-editing or configuration tasks, use the shortest safe execution path: inspect only the necessary file, apply the minimal edit, and run one focused verification. Do not spend extra model-side planning time on straightforward edits.
- If a task is small and well-scoped, do not expand it into broader audits, refactors, or documentation cleanup unless the user explicitly asks.
- When a delay occurs, distinguish tool/runtime latency from model-side delay. Report the observable timeline instead of guessing.

## Collaboration gates for long drylab workflows

- For long or branching drylab workflows, do not run ahead silently. Before downloads, remote jobs, large analyses, restart/continue decisions, broad edits, or scientific status judgments, pause and show a short decision card.
- Decision card format: current goal; verified facts; missing information; viable options; risks/tradeoffs; recommended next step; explicit question asking whether to continue.
- When an unexpected technical fork appears, pause before changing route unless the change is clearly local, reversible, and low-cost. Explain the fork and ask for confirmation.
- When results are borderline or decision-relevant, do not proceed to the downstream action automatically. Summarize the evidence and ask the user to choose the next step.
- Do not expose hidden chain-of-thought. Provide concise rationale, evidence pointers, and decision options instead.

## Evidence discipline

- Memory is an index, not evidence. Treat memory as a pointer to sources, not as a verified fact.
- Before using memory-derived claims about classifications, mechanisms, numeric results, or pipeline status, verify against source docs, logs, configs, code, CSV/JSON outputs, paper summaries, or data files.
- “I previously confirmed this” is not evidence across sessions. Re-read the source when the claim matters.
- Scientific cutoffs, thresholds, geometry definitions, and go/no-go criteria must carry explicit source pointers. If a value is literature-derived, cite the paper/tool documentation and the exact method context. If it is project-derived, label it as an operational heuristic and record who/what decision introduced it. Do not present heuristic thresholds as authoritative literature cutoffs.

## Log writing discipline

- Human-maintained drylab logs under `docs/logs/` are process authority and should be written in Chinese by default, with professional, rigorous, and auditable wording.
- Preserve commands, paths, code symbols, error messages, tool output, paper titles, and other literal evidence in their original form; explain their context in Chinese instead of translating literals.
- If an old log is language-normalized, treat it as an expression-only edit: do not change facts, timestamps, numeric values, paths, or source pointers.

## Claim discipline

- Completion/status claims such as “done”, “fixed”, “verified”, “passed”, “confirmed”, or “unresolved” require source-backed verification.
- For positive claims, decompose the claim into sublayers and verify each layer. If only a subset was checked, state the subset precisely.
- For negative/open claims, grep recent logs and relevant audit directories before saying the issue remains unresolved.
- For third-party operations such as “submitted”, “deployed”, “sent”, or “merged”, require explicit user/tool evidence. Do not infer external system state from indirect wording.

## Quoting and reference discipline

- Before quoting or writing project paths, code symbols, CLI commands, script names, section numbers, metric names, or column labels, verify with Read/Glob/Grep.
- Section references like “§N” require reading the target section content, not just grepping the heading.
- Universal or superlative wording such as “all”, “every”, “none”, “only”, “best”, “strongest”, or “highest” requires enumerating the full relevant set. If not enumerated, use exact counts or scoped wording.
- Mathematical/statistical derivations must be recalculated step by step before being written into docs or teaching material.

## Code-change discipline

- When changing a function signature or adding behavior-affecting parameters, grep all callers and update each intentionally. Do not rely on default fallback behavior to silently preserve old paths.
- Runner logs must use timestamped run IDs; fixed log names are not acceptable for repeatable scientific workflows.
- Script comments/docstrings should describe dependencies and invocation. Full workflow narratives belong in plans/docs/logs, with scripts pointing to those sources.
