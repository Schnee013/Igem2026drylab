---
name: truth-audit
description: Audit recent assistant output for unsupported claims, hallucinations, overconfident conclusions, missing evidence pointers, or misread sources. Use when the user says /truth, asks for a truth audit, or wants claims checked against files, code, documents, tool outputs, or sources.
---

# Truth Audit

Audit assistant output, not user input, for unsupported or overstated claims.

## Scope

- Default: the most recent 3 assistant-response rounds available in the current conversation.
- If the user provides a topic after `/truth`, audit claims related to that topic.
- If conversation history is insufficient, say what is unavailable and audit only visible claims.

## Dimensions

Check for:

1. Fabricated facts: claims not traceable to user input, files, docs, sources, or tool output.
2. Inference stated as fact: speculation presented as certainty.
3. Misattribution or misreading: real source cited but interpreted incorrectly.
4. Missing pointers: claims about code/docs/papers without file path, line number, URL, or quote/paraphrase anchor.
5. Unsupported causality: correlation or sequence presented as cause.
6. Selective evidence: contradictory evidence ignored.
7. Overconfidence: certainty language where alternatives remain plausible.

## Verification rules

- Verify suspicious claims using actual reads/searches/shell commands when possible.
- Do not rely only on memory.
- Treat tool outputs and user-provided content as evidence, but verify assistant interpretations.
- If a claim was explicitly labeled as hypothesis/speculation, usually do not count it as a violation unless the label was misleading.

## Output format

For each finding:

```markdown
### [dimension number] Dimension name
> Original assistant wording

- **Issue**: why it is unsupported or overstated
- **Evidence**: verification result with file path/line/tool output/source pointer
- **Better wording**: corrected or more cautious wording
- **Severity**: HIGH / MEDIUM / LOW
```

Severity:

- HIGH: false factual claim or conclusion likely to cause a wrong decision.
- MEDIUM: missing pointer or overconfidence; direction may be right but support is insufficient.
- LOW: wording precision issue with low decision impact.

## Archive

Write the full report to:

```text
docs/logs/truth-audits/YYYY-MM-DD_HHmm.md
```

Create the directory if missing. Use the active local date/time.

The archive must include:

```markdown
# Truth Audit — YYYY-MM-DD HH:mm

## Scope
[conversation rounds/topic]

## Findings
[findings]

## Summary
- Detected: X (HIGH: a, MEDIUM: b, LOW: c)
- Frequent dimensions: ...
- Suggested behavior changes: ...
```
