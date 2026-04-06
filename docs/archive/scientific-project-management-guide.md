# AI-Assisted Scientific Computing: Project & Documentation Management Guide

> A practical framework for managing computational research projects with Claude Code (or similar AI coding assistants), distilled from real-world use in molecular simulations, bioinformatics pipelines, and ODE modeling workflows.
>
> **Scope**: This guide covers documentation architecture, session continuity, context window management, and remote compute orchestration. It does **not** cover PRD/product management — for that, see Agile-PM-Workflow or similar frameworks.

---

## Table of Contents

1. [Core Philosophy](#1-core-philosophy)
2. [Directory Structure](#2-directory-structure)
3. [The Five-Layer Persistence Architecture](#3-the-five-layer-persistence-architecture)
4. [Key Files and Their Roles](#4-key-files-and-their-roles)
5. [Context Window Economics](#5-context-window-economics)
6. [Daily Logs as Cross-Session Glue](#6-daily-logs-as-cross-session-glue)
7. [Literature Management](#7-literature-management)
8. [Remote Compute Orchestration](#8-remote-compute-orchestration)
9. [Hooks for Enforcement](#9-hooks-for-enforcement)
10. [Anti-Patterns](#10-anti-patterns)
11. [Quick Start Checklist](#11-quick-start-checklist)

---

## 1. Core Philosophy

### The Single-Authority-Source Principle

Every piece of information has exactly **one** authoritative location. All other references are pointers (`see xxx.md`), never copies. This eliminates synchronization overhead and prevents information drift across sessions.

**Why this matters in research**: A typical 6-month research project generates hundreds of sessions. If pipeline status is recorded in 3 places, by session 50 they will contradict each other. The AI assistant will act on whichever it reads first — which may be the stale one.

### Layered Persistence

Not all information needs the same lifetime or loading frequency:

| Lifetime | Example | Where it lives |
|----------|---------|---------------|
| Permanent rules | "Always update the daily log after code changes" | `CLAUDE.md` |
| Project routing | "Which modeling directions exist, their status" | `INDEX.md` |
| Cross-session state | "Pipeline X is running on Node Y since Tuesday" | Memory files |
| Daily narrative | "Today I discovered the grid spacing was wrong" | Daily logs |
| Raw results | ΔG values, benchmark scores, timing data | Result files (JSON/CSV) |

Information flows **downward** (rules → routing → state → narrative → data) but never **upward**. A daily log may reference a result file, but a result file never contains project rules.

---

## 2. Directory Structure

```
project/
├── CLAUDE.md                   # Project-level instructions (auto-loaded)
├── .claude/
│   └── SKILL.md                # Startup sequence + path table + loading strategy
│
├── docs/
│   ├── INDEX.md                # Routing table — the "soul file"
│   ├── DOCMAP.md               # Meta-rules for documentation itself
│   ├── modeling/               # One file per research direction
│   │   ├── P0-direction-a.md   #   Frontmatter: status, priority, dependencies
│   │   ├── P0-direction-b.md
│   │   └── P1-direction-c.md
│   ├── decisions/              # Architecture Decision Records
│   │   └── NNN-title.md
│   ├── ops/                    # Operational runbooks (SSH, environment, tools)
│   │   └── remote-compute.md
│   ├── logs/                   # Daily work logs
│   │   └── YYYY-MM-DD.md
│   └── papers/                 # Literature (matrix + on-demand summaries)
│       ├── literature-matrix.md
│       ├── search-log.md
│       ├── pdf/
│       └── summaries/
│
├── src/                        # Source code (by research direction)
│   └── modeling/
│       └── direction-a/
│
├── experiments/                # Outputs (by research direction)
│   └── direction-a/
│       ├── prepared/           # Pre-processed inputs
│       ├── results/            # Output data (JSON, CSV)
│       └── logs/               # Runtime logs
│
└── scripts/                    # Setup & utility scripts
```

### Naming Conventions

| Item | Pattern | Example |
|------|---------|---------|
| Modeling direction doc | `P{0-3}-{english-slug}.md` | `P0-molecular-docking.md` |
| Decision record | `{NNN}-{short-title}.md` | `002-tool-chain-selection.md` |
| Daily log | `YYYY-MM-DD.md` | `2026-04-06.md` |
| Literature summary | `{Author}{Year}-{Topic}-summary.md` | `Kuo2024-Gpr2Gpr3-summary.md` |
| Runtime log | `run_{script}_{YYYYMMDD}_{HHMMSS}.log` | `run_multiseed_20260406_072954.log` |
| Experiment result | Stored under `experiments/{direction}/results/` | `docking_results.json` |

---

## 3. The Five-Layer Persistence Architecture

```
┌─────────────────────────────────────────────────┐
│  Layer 1: CLAUDE.md  (auto-loaded every session) │
│  Mandatory rules + pointers to authority sources  │
└───────────────────────┬─────────────────────────┘
                        │ points to
┌───────────────────────▼─────────────────────────┐
│  Layer 2: SKILL.md  (auto-loaded every session)  │
│  Startup sequence + path table + loading strategy │
└───────────────────────┬─────────────────────────┘
                        │ reads first
┌───────────────────────▼─────────────────────────┐
│  Layer 3: INDEX.md  (routing table)              │
│  Direction status matrix, blockers, recent ≤5    │
│  progress entries, active TODOs only             │
└───────────────────────┬─────────────────────────┘
                        │ routes to
┌───────────────────────▼─────────────────────────┐
│  Layer 4: Domain docs  (loaded on demand)        │
│  modeling/P*.md, decisions/, ops/, papers/        │
└─────────────────────────────────────────────────┘
                        │ supplemented by
┌───────────────────────▼─────────────────────────┐
│  Layer 5: Memory files  (cross-session state)    │
│  Only what docs/ doesn't cover: behavioral rules,│
│  decision context, pipeline current-state         │
└─────────────────────────────────────────────────┘
```

### What goes where (and what does NOT)

| Layer | File | Should contain | Should NOT contain |
|-------|------|----------------|-------------------|
| Project instructions | `CLAUDE.md` | Mandatory rules + pointers to authoritative docs | Information derivable from other files |
| Entry loader | `.claude/SKILL.md` | Startup sequence, path table, per-task workflows | Rules (→ CLAUDE.md), content (→ docs/) |
| Routing table | `INDEX.md` | Direction status, blockers, ≤5 recent progress, active TODOs | Completed items, detailed result values |
| Meta-rules | `DOCMAP.md` | Naming conventions, directory structure, doc lifecycle | Actual project state |
| Memory | `~/.claude/projects/.../memory/` | Cross-session gotchas and decision context NOT in docs/ | Anything already in docs/ with a full version |
| Daily log | `docs/logs/YYYY-MM-DD.md` | Day's narrative (what, why, pitfalls) | Cross-day status (→ INDEX.md or memory) |

---

## 4. Key Files and Their Roles

### CLAUDE.md — The Rulebook (~40 lines target)

Auto-loaded every session. Keep it **short and directive**:

```markdown
# Project CLAUDE.md

## Background
One-sentence project description.

## Single-Authority-Source Table
[The layering table from Section 3 above]

## Mandatory: Update Docs After Code Changes
After modifying src/ or scripts/, you must:
1. Update daily log docs/logs/YYYY-MM-DD.md
2. Update memory files if cross-session relevant
3. Update DOCMAP.md if files were added/deleted

> This rule exists because: cross-session memory depends on logs + memory.
> Failing to update means the next session loses context.

## Remote Compute
**Read before any SSH operation**: [docs/ops/remote-compute.md](docs/ops/remote-compute.md)

## Directory Conventions
| Path | Purpose |
|------|---------|
| src/modeling/direction-a/ | Direction A pipeline code (authoritative) |
| experiments/direction-a/results/ | Output data |
```

**Key principles**:
- Every rule includes a `why` annotation (rules without rationale get ignored by AI)
- Remote compute details → pointer to ops doc (not inline)
- Directory table resolves ambiguous paths (e.g., when two pipelines share similar names)

### INDEX.md — The Routing Table

The only file the AI reads to decide what to load next:

```markdown
## Project Overview
- **Current stage**: [What's actively happening right now]
- **Main blocker**: [The biggest obstacle]

## Research Direction Status
| Priority | Direction | Status | Doc |
|----------|-----------|--------|-----|
| P0 | Direction A | in_progress | [link] |
| P0 | Direction B | blocked | [link] |
| P1 | Direction C | not_started | [link] |

## Blocking Items
- [ ] [blocking] Item description
- [ ] [important] Item description

## Recent Progress (max 5 entries)
- **YYYY-MM-DD**: One-line summary → [daily log link]

## Active TODOs (no completed items)
- [ ] Task description
```

**Aging rules** (enforce in DOCMAP.md):
- Recent progress: max 5 entries. Older entries are deleted — history lives in daily logs and git.
- Completed `[x]` items: removed on next update. Don't accumulate finished tasks.
- Current stage: re-evaluated every time progress is updated.

### SKILL.md — The Startup Sequence

Defines what the AI loads first and how it navigates:

```markdown
## Startup Sequence
1. Read docs/INDEX.md — understand project state
2. Read latest docs/logs/ entry — understand recent context
3. Load sub-documents on demand based on user request

## On-Demand Loading Strategy
- User mentions a modeling direction → load only that P*.md
- User mentions literature → check literature-matrix.md first, then load specific summaries
- If a loaded doc declares dependencies → ask user if dependent docs should load too
```

### Memory Files — Cross-Session Behavioral Rules

Located at `~/.claude/projects/{project-hash}/memory/`. Use a `MEMORY.md` index + individual files with YAML frontmatter:

```markdown
# MEMORY.md (index, one line per entry, <150 chars each)
- [Remote SSH conventions](feedback_ssh.md) — behavioral rules for SSH compute
- [Pipeline status](project_pipeline.md) — decision context + current runs
```

Each memory file:
```markdown
---
name: Remote SSH Conventions
description: Behavioral rules for SSH to compute nodes (full guide in docs/ops/)
type: feedback
---

1. Merge multiple queries into one SSH connection
2. Never guess filenames — use wildcards + sort by date
3. Long tasks: use run_in_background, not detached processes
4. Check dependency modules synced before uploading new scripts
5. Full guide: docs/ops/remote-compute.md
```

**Memory files should be thin** (~10-20 lines). They store behavioral nudges and decision context that docs/ doesn't cover. If the information has a full authoritative version in docs/, the memory file should only contain a pointer.

---

## 5. Context Window Economics

Research repos contain massive reference material (PDFs, summaries, datasets). Naive loading will exhaust the context window. These patterns keep token usage sustainable:

### Literature Loading Strategy

```
NEVER: Load all summaries/ at once or read PDFs directly
ALWAYS: Check literature-matrix.md first → load only the specific summary needed
LIMIT: Max 2-3 summaries loaded simultaneously
```

The literature matrix serves as a lightweight index:

```markdown
| # | Citation | Topic | Tier | Summary |
|---|----------|-------|------|---------|
| 1 | Author 2024 | Receptor docking | T1 | [link](summaries/Author2024-summary.md) |
```

Most questions can be answered from the matrix's one-line descriptions without loading the full summary.

### On-Demand Document Loading

Don't load everything at session start. Load based on actual need:

```
Session start → CLAUDE.md (auto) → SKILL.md (auto) → INDEX.md
User asks about Direction A → load modeling/P0-direction-a.md
User wants to run SSH task → load ops/remote-compute.md (hook-enforced)
User asks about a paper → check matrix → load one summary
```

### INDEX.md as Token Budget Guard

INDEX.md should contain **just enough metadata to route**, not enough to answer. If the AI can answer the user's question from INDEX.md alone, INDEX.md is too detailed.

---

## 6. Daily Logs as Cross-Session Glue

Daily logs (`docs/logs/YYYY-MM-DD.md`) are the primary mechanism for session continuity. They capture what no other file can: the narrative context of *why* decisions were made.

### Template

```markdown
# YYYY-MM-DD Work Log

## Today's Goals
- [ ] Goal 1
- [ ] Goal 2

## Completed Work

### [Work Item Title]
- What was done
- Key findings / results
- Related files: `path/to/file`

## Pitfalls Encountered
### Pitfall N: [Short Description]
- **Symptom**: What happened
- **Root cause**: Why it happened
- **Fix**: What was done
- **Prevention**: How to avoid in the future

## Next Steps
- [What to do tomorrow]
```

### Pitfall Documentation is Knowledge

The "Pitfalls Encountered" section is the most valuable part of the log for future sessions. Document root causes, not just fixes. These pitfalls should be consolidated into operational runbooks (`docs/ops/`) when patterns recur.

### Log → Ops Doc Promotion Pipeline

```
Day 1: Encounter pitfall, document in daily log
Day 2: Hit similar pitfall, document again
Day 3: Recognize pattern → promote to docs/ops/ runbook
         → add to memory file as behavioral rule
         → optionally create a hook for enforcement
```

---

## 7. Literature Management

### Structure

```
papers/
├── literature-matrix.md      # Lightweight index (one row per paper)
├── search-log.md             # What was searched, when, where
├── pdf/                      # Raw PDFs (gitignored if large)
│   └── Author2024-Topic.pdf
└── summaries/                # AI-readable summaries
    └── Author2024-Topic-summary.md
```

### Literature Matrix

The matrix is the **single entry point** for all literature queries:

```markdown
| # | Citation | Topic | Tier | Status | Summary |
|---|----------|-------|------|--------|---------|
| 1 | Author 2024 | Core method | T1-Core | Summarized | [link] |
| 2 | Author 2023 | Background | T3-Context | Summarized | [link] |
| 3 | Author 2022 | Related | T5-Peripheral | Not needed | — |
```

**Tier system** (adapt to your field):
- T1: Core — directly used in your methods
- T2: Validation — provides benchmarks or comparison data
- T3: Context — cited in introduction/discussion
- T4-T6: Peripheral / archive

### Summary Files

Each summary is a standalone markdown file with structured sections:

```markdown
# Author 2024 — [Paper Title]

## Key Finding
One-paragraph summary relevant to your project.

## Methods Used
- Tool X, version Y
- Parameters: ...

## Data Sources
- Protein: PDB XXXX
- Ligand: PubChem CID NNNN

## Relevance to This Project
How this paper informs your modeling decisions.
```

---

## 8. Remote Compute Orchestration

If your project runs computation on remote nodes (SSH to GPU servers, HPC clusters, cloud VMs), create a dedicated runbook at `docs/ops/remote-compute.md`.

### Runbook Structure

```markdown
# Remote Compute Runbook

## Environment Info
| Item | Value |
|------|-------|
| Host | [IP / hostname] |
| User | [username] |
| Working directory | [path] |
| Conda environment | [path] |
| Tool paths | [list] |
| Log directory | [path] |

## Correct Patterns
[Tested, working command templates with explanations]

## Anti-Patterns
[Commands that look right but fail, with root cause analysis]

## Checking Progress
[One-shot commands to check all running tasks — never guess filenames]

## Pitfall Reference Table
| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| ... | ... | ... |
```

### Key Principles

1. **Root cause analysis over symptom fixes**: Don't just say "use forward slashes." Explain *why* backslashes fail (e.g., double-escape through local shell → SSH → remote shell).

2. **One-shot progress checks**: Combine multiple queries into a single SSH connection. Each SSH has handshake overhead.

3. **Never guess filenames**: Runtime logs are typically timestamped (`run_script_YYYYMMDD_HHMMSS.log`). Use wildcards + sort by modification time to find the latest.

4. **Enforce reading the runbook**: Use a PreToolUse hook (see Section 9) to remind the AI assistant to read the runbook before every SSH command.

---

## 9. Hooks for Enforcement

Written rules are suggestions. Hooks are enforcement. Claude Code supports PreToolUse and PostToolUse hooks that inject context before/after tool execution.

### Pattern 1: Remote Compute Reminder (PreToolUse)

Detect SSH commands and inject a reminder to follow the runbook:

```bash
#!/usr/bin/env bash
# ssh-reminder.sh — PreToolUse hook for Bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if echo "$COMMAND" | grep -qE 'ssh\s+.*YOUR_HOST_PATTERN'; then
  jq -n --arg msg "[SSH Reminder] Read docs/ops/remote-compute.md first. Key rules: 1) Merge queries into one SSH; 2) Use wildcards for log files; 3) Use run_in_background for long tasks." \
    '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":$msg}}'
else
  exit 0
fi
```

Register in `~/.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "/path/to/ssh-reminder.sh"}]
      }
    ]
  }
}
```

### Pattern 2: Doc Update Reminder (PostToolUse)

After editing source code, remind the AI to update the daily log:

```bash
#!/usr/bin/env bash
# doc-reminder.sh — PostToolUse hook for Edit|Write
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

if [[ "$FILE_PATH" == */src/* || "$FILE_PATH" == */scripts/* ]]; then
  TODAY=$(date +%Y-%m-%d)
  jq -n --arg msg "[Doc Update] Source code modified ($(basename "$FILE_PATH")). Update docs/logs/${TODAY}.md and check if memory files need updating." \
    '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":$msg}}'
else
  exit 0
fi
```

Register with `"matcher": "Edit|Write"` and `"async": true`.

---

## 10. Anti-Patterns

### Information Duplication (the #1 enemy)

**Symptom**: The same SSH connection details appear in CLAUDE.md, a memory file, AND the ops runbook. A new pitfall must be updated in 3 places.

**Fix**: Designate one authoritative source (the ops runbook). Other files contain only a one-line pointer: `Full guide: docs/ops/remote-compute.md`.

### INDEX.md as a Knowledge Base

**Symptom**: INDEX.md grows beyond 150 lines. It contains detailed result tables, completed task history, and explanatory paragraphs.

**Fix**: INDEX.md is a routing table, not a wiki. Apply aging rules: max 5 progress entries, no completed tasks, no result values (those live in result files and daily logs).

### Memory Files Duplicating Docs

**Symptom**: A memory file grows to 60+ lines with code examples that also exist in `docs/ops/`.

**Fix**: Memory files store behavioral nudges (~10-20 lines). If the information has a full version in docs/, the memory file should contain only a pointer and a behavioral summary.

### In-Document Version Tracking

**Symptom**: Every modeling doc has a "Version History" table that must be manually maintained alongside daily logs, git history, and INDEX.md progress entries.

**Fix**: Remove in-document version tables. Git log + daily logs provide complete change history. Don't create a third changelog that will inevitably drift.

### Guessing Filenames

**Symptom**: The AI tries to `cat run_results.log` but the actual file is `run_multiseed_20260406_072954.log`. Wasted round-trips to discover the real name.

**Fix**: Document naming conventions in DOCMAP.md. Always use wildcards + sort to find the latest file:
```bash
$log = Get-ChildItem path/run_script_*.log | Sort LastWriteTime -Desc | Select -First 1
```

### Over-Loading at Session Start

**Symptom**: CLAUDE.md + SKILL.md + INDEX.md + latest log + memory files consume 40% of the context window before the user even asks a question.

**Fix**: Keep CLAUDE.md under 50 lines. Keep SKILL.md under 80 lines. INDEX.md should route, not explain. Memory files should be thin behavioral reminders. Load domain docs on demand, not preemptively.

### Methodology Attribution in Working Docs

**Symptom**: DOCMAP.md starts with "Based on Agile-PM-Workflow and Claude Code Skill Guide..." — attribution that helps no one during actual use.

**Fix**: Remove provenance notes from working documents. They consume tokens and provide no actionable guidance. Cite methodologies in an archived guide if lineage matters.

---

## 11. Quick Start Checklist

### Day 1: Foundation (~30 minutes)

- [ ] Create `CLAUDE.md` at project root (use Section 4 template)
- [ ] Create `.claude/SKILL.md` (startup sequence + path table)
- [ ] Create `docs/INDEX.md` (routing table with direction status matrix)
- [ ] Create `docs/DOCMAP.md` (naming conventions + aging rules)
- [ ] Create `docs/logs/` directory, write first daily log
- [ ] Commit and push to git

### Day 2-3: Flesh Out

- [ ] Add `docs/modeling/P*-*.md` files for each research direction
- [ ] Set up `docs/papers/literature-matrix.md` with initial entries
- [ ] If using remote compute: create `docs/ops/remote-compute.md`
- [ ] Initialize memory files in `~/.claude/projects/{project}/memory/`

### Week 1: Add Enforcement

- [ ] Create PostToolUse hook for doc-update reminders
- [ ] If using remote compute: create PreToolUse hook for SSH reminders
- [ ] Register hooks in `~/.claude/settings.json`
- [ ] Review: is every piece of information in exactly one authoritative location?

### Ongoing: Maintenance

- [ ] Apply INDEX.md aging rules at end of each work day
- [ ] Promote recurring pitfalls from daily logs → ops runbooks
- [ ] Review memory files monthly — delete stale entries, slim oversized files
- [ ] Periodically grep for duplicated information across layers

---

## License

This guide is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Adapt freely for your lab, team, or open-source project.
