# ODE PR #1 Post-Recovery Content Integration Plan

> Created: 2026-07-27. Execution checkpoint updated: 2026-07-28.
>
> Status: `LOCAL_RECONSTRUCTION_COMPLETE_AWAITING_REMOTE_GATE`.
>
> Scope: after the user-designated non-ODE recovery work has passed review and
> merged, take that canonical branch as a new initial snapshot, audit what ODE
> work is already present, and reconstruct only the missing or defective ODE
> increment from old PR #1. On 2026-07-28 the user clarified that ODE is the
> product of this task, not an additional prerequisite merge.
>
> Execution boundary: the trigger gate has passed for local reconstruction.
> Push, PR creation, closing old PR #1, and merge-to-main remain separate remote
> gates.
>
> Status authority: this plan does not maintain live project state. At
> execution time, current status comes from the then-current `docs/INDEX.md`,
> domain documents, code, tests, configs, result artifacts, and merged-PR
> evidence.

## 1. Requirements Summary

1. Do not start until all user-designated non-ODE prerequisite recovery
   branches have passed review and their merge commits are ancestors of the
   canonical target branch. ODE itself is reconstructed by this plan.
2. Define the post-merge canonical target tip as `BASE_SHA`; do not use the
   current dirty primary worktree or a historical pre-rewrite branch as the
   integration base.
3. Audit the post-merge tree before reconstructing anything. If the required
   ODE content and fixes are already present, stop with a zero-delta report
   instead of creating a duplicate PR.
4. Recover content, not old branch history:
   - use `135010c` only as a source for the minimum Phase 0 dependency closure;
   - use `4be3b2c` as the source for Phase 0 visualization logic;
   - use `c39bb3d` as the source for Phase 1 scan logic;
   - do not replay broad merge commit `05eb79a`.
5. Preserve the scientific boundary: all uncalibrated outputs remain
   `scenario_prior`; no docking score becomes `Kd`, `EC50`, `kon/koff`, a real
   detection limit, or a final construct recommendation.
6. Reconcile project documents semantically against the post-merge files.
   Never replace the full `docs/INDEX.md` or another current document with the
   old PR version.
7. Preserve the user's primary dirty worktree. All implementation occurs in a
   separate clean worktree and stages explicit paths only.

### 1.1 2026-07-28 execution checkpoint

| Item | Verified value |
|---|---|
| Canonical target | `origin/main` |
| `BASE_SHA` | `e6a8be4e5f0d586f9a8ee9defeda9f83a5ef0763` |
| Isolated branch | `codex/ode-pr1-content-integration` |
| Isolated worktree | `/Users/roy/Documents/drylab/.omx/worktrees/ode-pr1-content-integration` |
| Gap audit | real delta: `BASE_SHA` has no `src/modeling/ode/`, ODE configs/tests, or ODE result package |
| Recovery method | focused content extraction/reimplementation; no cherry-pick and no replay of `05eb79a` |
| Remote boundary | local implementation only; no push or PR creation authorized yet |

## 2. Planning Context, Not The Future Initial Snapshot

The following values were verified while writing this plan and are historical
planning context only:

| Ref or file | 2026-07-27 observation | Allowed use |
|---|---|---|
| `origin/main` | `a71f501ce90163ccbd2b593baf63e1c5f73d9150` | Explain why a future snapshot is required; not an execution base after later merges |
| old PR #1 head | `c39bb3d604a41cdaeff7d7a38d698e3bdb85494b` | Recover candidate ODE content and reproduce old review findings |
| local historical tip | `3208818d737a9f29f987a48079f8a31f0f91add9` | Historical/current-local evidence router only; not a shared-history integration base |
| `docs/INDEX.md:29,57,164-168` | ODE is still routed as lacking solver/config/plots in this checkout | Identify the future project-level status delta; re-open after merges |
| `docs/modeling/P0-signal-pathway-ode.md:36-55` | Current checkout describes preparation work and missing implementation | Identify the future domain-document delta; re-open after merges |
| `docs/ops/payload-tracking-policy.md:15-58` | Generated payload bodies are external by default; compact contracts and reviewed summaries are trackable | Classify Phase 1 time-course output at execution time |

No claim in this section may be copied forward as a post-merge current fact
without re-verification.

## 3. Trigger Gate And Future `BASE_SHA`

### 3.1 Required merge ledger

At execution time, first create a ledger in the current dated log with one row
per user-designated prerequisite:

| Required recovery | PR / branch | Reviewed verdict | Merge commit | Ancestor of target? |
|---|---|---|---|---|
| GPR3 recovery | fill from live repository/GitHub evidence | must be accepted | exact SHA | PASS required |
| Other user-designated recovery branches | enumerate explicitly | must be accepted | exact SHA | PASS required |

ODE is deliberately absent from this prerequisite ledger after the user's
2026-07-28 clarification. Its replacement branch is the output governed by
this plan.

Do not interpret “等” as permission to choose an arbitrary branch. The
execution log must enumerate the exact prerequisites from merged repository
evidence or a current user-provided list.

### 3.2 Snapshot procedure

After the ledger is complete:

1. Query the live remote target and fetch without modifying the primary
   worktree:

   ```bash
   git ls-remote origin refs/heads/main
   git fetch --prune origin
   ```

2. Set `BASE_SHA` to the exact canonical target tip after the prerequisite
   merges:

   ```bash
   git rev-parse origin/main
   ```

3. Verify every prerequisite merge:

   ```bash
   git merge-base --is-ancestor "$RECOVERY_MERGE_SHA" "$BASE_SHA"
   ```

   Repeat this check after assigning `RECOVERY_MERGE_SHA` to each exact merge
   SHA in the ledger.

4. Record in the dated log:
   - `BASE_SHA`;
   - remote URL and target branch;
   - prerequisite merge SHAs;
   - initial tracked/untracked/staged status of the primary worktree;
   - current ODE file inventory;
   - current ODE status text from `docs/INDEX.md`;
   - current domain status from
     `docs/modeling/P0-signal-pathway-ode.md`;
   - current payload policy identity.

### 3.3 Trigger stop conditions

Stop without implementation when any of the following is true:

- a designated recovery PR is still open, rejected, superseded without a clear
  replacement, or not an ancestor of the canonical target;
- the canonical target branch is ambiguous;
- the live remote tip changes during snapshot creation;
- another independently owned ODE replacement branch appears and overlaps
  this plan;
- the post-merge files cannot be read without using an uncommitted user
  modification as authority.

## 4. Post-Merge Gap Audit

Before creating a change branch, classify the post-merge tree against the
acceptance criteria in this plan.

### 4.1 Inventory

Inspect at minimum:

- `src/modeling/ode/`
- `tests/modeling/test_ode_minimal_solver.py`
- `tests/modeling/test_ode_scenario_scans.py`
- `experiments/ode-model/`
- `docs/modeling/P0-signal-pathway-ode.md`
- `docs/modeling/P0-ode-lumped-parameter-register.md`
- `docs/INDEX.md`
- the current dated logs and any merged ODE recovery log
- `codex/docs/plans/`

For each expected artifact, classify it as:

- `PRESENT_VALID`;
- `PRESENT_NEEDS_FIX`;
- `MISSING`;
- `STALE_DOC_ONLY`;
- `SUPERSEDED_BY_MERGED_IMPLEMENTATION`;
- `OUT_OF_SCOPE`.

### 4.2 Old-commit equivalence

Use tree/diff/patch evidence, not subjects alone:

```bash
git diff --name-status "$BASE_SHA"..135010c -- \
  src/modeling/ode tests/modeling experiments/ode-model \
  docs/modeling/P0-signal-pathway-ode.md \
  docs/modeling/P0-ode-lumped-parameter-register.md
git diff --name-status "$BASE_SHA"..4be3b2c -- \
  src/modeling/ode experiments/ode-model
git diff --name-status "$BASE_SHA"..c39bb3d -- \
  src/modeling/ode tests/modeling experiments/ode-model \
  docs/modeling/P0-signal-pathway-ode.md
git log --cherry-pick --left-right --oneline "$BASE_SHA"...c39bb3d
```

When patch identity is ambiguous, compare file bodies or stable semantic
contracts. Do not use commit ancestry alone to conclude that content is
missing.

### 4.3 Zero-delta outcome

If the post-merge tree already satisfies every acceptance criterion:

1. run the complete verification suite in Section 9;
2. record `NO_CONTENT_DELTA_REQUIRED`;
3. update no source or project document merely to manufacture a PR;
4. report that old PR #1 is superseded by the merged recovery work.

## 5. Isolated Reconstruction Workspace

Only when the gap audit finds a real delta:

1. Create a new clean worktree and branch from `BASE_SHA`, using a branch such
   as `codex/ode-pr1-content-integration`.
2. Verify the new worktree is clean before edits.
3. Keep the primary worktree unchanged.
4. Never run `git add .`, `git add -A`, `git clean`, `git reset --hard`, or a
   force-push.
5. Treat the old commits as read-only sources. Restore or reimplement only the
   exact missing paths.

If the target branch advances after the worktree is created, stop before the
documentation phase and establish a new snapshot/reconciliation point.

## 6. Content Recovery Matrix

This matrix defines the default treatment. The post-merge gap audit may reduce
the work but must not broaden it without a new decision.

### 6.1 Phase 0 source from `135010c`

Recover only when missing or invalid:

- `src/modeling/ode/__init__.py`
- `src/modeling/ode/minimal_solver.py`
- `src/modeling/ode/run_minimal_solver.py`
- `tests/modeling/test_ode_minimal_solver.py`
- `experiments/ode-model/configs/minimal_normalized_scenario.json`
- `docs/modeling/P0-ode-lumped-parameter-register.md`

Regenerate from accepted code/config instead of copying old generated bytes:

- `experiments/ode-model/results/minimal_normalized_timecourse.csv`
- `experiments/ode-model/results/minimal_normalized_timecourse.png`

Do not import from `135010c` as whole-file replacements:

- `docs/INDEX.md`
- `codex/docs/memory/current-state.md`
- old plan status projections
- old project-wide status text

### 6.2 Phase 0 visualization from `4be3b2c`

Recover or semantically reproduce:

- `src/modeling/ode/plot_minimal_timecourse.py`

Generate the PNG from the newly accepted CSV. The old PNG is comparison
evidence, not the accepted output body.

### 6.3 Phase 1 source from `c39bb3d`

Recover only when missing or invalid:

- `src/modeling/ode/run_scenario_scans.py`
- `src/modeling/ode/plot_scenario_scan.py`
- `tests/modeling/test_ode_scenario_scans.py`
- `experiments/ode-model/configs/stage1_scenario_scan.json`
- the compact result-package contracts described in Section 8

Do not accept `c39bb3d` unchanged. All applicable repairs in Section 7 are
mandatory even if the main numerical run succeeds.

### 6.4 Documentation defaults

- `experiments/ode-model/README.md`: semantic merge/rewrite.
- `docs/modeling/P0-signal-pathway-ode.md`: semantic merge.
- `docs/INDEX.md`: minimal ODE-only status projection after validation.
- `docs/DOCMAP.md`: no change unless a new authority location, directory role,
  or conflict-resolution rule is introduced.
- existing dated logs: do not overwrite. Add the verified reconstruction to
  the execution-date log; append to a historical log only when preserving a
  precisely verified historical event is necessary.
- `ode-four-stage-workbook.md`: omit by default. If a current consumer requires
  it, rewrite it in a separate documentation change so it no longer claims
  that solver/CSV/plots are absent.
- `ode-weekly-plan-2026-07-13.md`: do not restore as a current plan.
- `codex/docs/memory/current-state.md`: do not restore.

## 7. Mandatory Phase 1 Repairs

### 7.1 Control identity contract

For every no-ligand control:

- the effective solver input must be `ligand_normalized = 0.0`;
- the manifest must not present the paired non-zero ligand as the effective
  input;
- pairing information must remain recoverable.

Preferred schema:

- `requested_axis_values_json`: the scan design point used for pairing;
- `effective_axis_values_json`: values actually applied to the solver;
- `control_for_scenario_id`: the paired ligand scenario;
- `scenario_role`: `ligand` or `no_ligand_control`.

Acceptance checks:

- all no-ligand rows have effective ligand `0.0`;
- all ligand rows have an effective ligand matching their generated config;
- every control points to exactly one ligand scenario;
- a pair differs only in the intended ligand input and identity fields.

### 7.2 Self-contained configuration snapshot

The result package must include the exact suite config and exact base config
used for the run. A copied result directory must rerun without consulting the
source config directory.

Accepted designs:

1. `scan_suite_config_snapshot.json` references a colocated
   `base_config_snapshot.json`; or
2. one resolved run-bundle JSON embeds both configs.

The package must record:

- schema version;
- source paths as provenance only;
- hashes of both input configs;
- solver/runner identity;
- Python, SciPy, NumPy, and Matplotlib versions;
- generation command;
- scenario count and time-course row count.

### 7.3 Strict configuration validation

Add regression-tested validation so that:

- `output_points` is an integer, is not a boolean, and is at least `2`;
- fractional values such as `2.9` are rejected rather than truncated;
- `NaN`, positive/negative infinity, and non-numeric values are rejected in
  every numeric config field;
- copy-number fields are positive integers when they represent discrete copy
  scenarios;
- rates, times, gains, and normalized inputs obey their documented
  non-negative/positive bounds;
- unknown or missing required fields fail closed.

### 7.4 Result identity and determinism

- Scenario IDs must be unique.
- `scenario_manifest.csv`, `final_metrics.csv`, and time-course payload rows
  must reference the same scenario set.
- Re-running from the accepted snapshot must reproduce the same numeric CSV
  contents or an explicitly documented tolerance-based equivalence.
- Plot generation must consume the accepted CSVs and must not recompute hidden
  model values.

## 8. Result And Payload Contract

Re-evaluate the then-current payload policy before generating results. Under
the 2026-07-27 policy, the default classification is:

| Artifact | Default Git treatment | Reason |
|---|---|---|
| Phase 0 CSV and PNG | track after regeneration and review | compact reviewed result |
| Phase 1 suite/base config snapshots | track | canonical run inputs/provenance |
| `scenario_manifest.csv` | track | scenario identity contract |
| `final_metrics.csv` | track | compact reviewed analysis |
| `run_metadata.json` | track | compact provenance and boundary |
| Phase 1 summary PNG | track after regeneration and review | compact reviewed summary |
| full `timecourses.csv` (~6.6 MB in the old run) | external by default | operation-produced full payload body |
| `payload_manifest.tsv` for full time-course | track | checksum, bytes, storage, producer, consumer, recovery route |

For an external full time-course:

1. use the schema at
   `docs/ops/templates/payload_manifest.schema.tsv`;
2. record exact bytes and SHA256;
3. record an explicit non-worktree storage location;
4. record the command and accepted config snapshot required to regenerate it;
5. change README/metadata language so the missing Git body is not falsely
   declared to be a tracked file inside the package.

Tracking the full time-course body requires an explicit promotion decision
under the then-current policy.

Expected old-grid invariants, applicable only if the merged configuration has
not intentionally changed:

- `143` total scenarios;
- `23,023` time-course data rows;
- `74` ligand scenarios;
- `69` matched no-ligand controls.

Any intentional grid change must be separately explained and must update tests,
metadata, README, and the dated log together. An unexplained count difference
is a blocker.

The earlier planning value `30 controls` was not the total control count. It
described only the dose-scan controls affected by the old
`axis_values_json` requested/effective identity conflict. Direct suite
expansion proves the full unchanged grid contains 69 controls.

## 9. Verification Plan

### 9.1 Unit and contract tests

Run the accepted repository commands, including at minimum:

```bash
python -m unittest \
  tests.modeling.test_ode_minimal_solver \
  tests.modeling.test_ode_scenario_scans -v
```

Required regression coverage:

- valid Phase 0 simulation;
- valid Phase 1 suite expansion;
- control effective-input identity;
- one-to-one control pairing;
- fractional `output_points` rejection;
- `NaN`/infinity rejection;
- unknown/missing-field rejection;
- snapshot-only replay;
- scenario/metric/time-course identity consistency.

### 9.2 Isolated result regeneration

Generate into a new temporary or external result root, never over an accepted
package before comparison:

1. run Phase 0 solver;
2. render Phase 0 figure;
3. run Phase 1 suite;
4. render Phase 1 summary;
5. rerun from the copied self-contained snapshot;
6. compare numeric outputs, counts, schema, IDs, and hashes/tolerances;
7. generate the payload manifest for any external full time-course.

### 9.3 Static and repository checks

```bash
python -m compileall src/modeling/ode tests/modeling
python3 scripts/check_payload_tracking_policy.py
git ls-files -ci --exclude-standard
git diff --check
```

Also verify:

- no secrets, credentials, environment files, caches, or unrelated payloads
  are staged;
- the diff contains only the allowed ODE paths and explicitly reviewed
  documentation/log paths;
- no generated output predates its accepted code/config;
- every README path and reproduction command resolves from repository root.

### 9.4 Documentation consistency

Search the final tree for stale claims such as:

- “尚无 solver”;
- “未写 ODE solver”;
- “尚无 config/CSV/plots”;
- “下一阶段才创建 solver”;
- any claim that the uncalibrated model determines a real detection limit or
  optimal construct.

For `docs/INDEX.md`:

- compare against `BASE_SHA`;
- permit only the verified ODE status, entrypoint, todo, and concise recent
  progress delta;
- prove that MD, docking, GPR3, P2, server, blocker, and other project fields
  are not regressed.

For `docs/DOCMAP.md`:

- expect no diff by default;
- if a diff exists, require a newly introduced authority/route contract and an
  explicit reason in the dated log.

## 10. Documentation Update Contract

After code and result verification, update in this order:

1. operation facts and validation evidence in the execution-date log;
2. detailed model status and limitations in
   `docs/modeling/P0-signal-pathway-ode.md`;
3. parameter-source and replacement rules in
   `docs/modeling/P0-ode-lumped-parameter-register.md`, if changed;
4. reproduction and payload contract in
   `experiments/ode-model/README.md`;
5. project-level projection in `docs/INDEX.md`.

Expected INDEX meaning when Phase 0/1 pass:

> A runnable normalized Phase 0 solver and Phase 1 engineering scenario suite
> have been validated. All numeric outputs remain `scenario_prior`; formal
> sensitivity/identifiability analysis, detailed pathway kinetics, and wet-lab
> calibration remain incomplete.

Do not mark the overall ODE direction complete.

## 11. Commit And PR Structure

When a real delta exists, prepare up to three focused commits:

1. `feat(ode): add normalized Phase 0 solver and config`
   - Phase 0 source/config/tests;
   - regenerated compact Phase 0 result.
2. `feat(ode): add reproducible Phase 1 scenario scans`
   - Phase 1 source/config/tests;
   - all mandatory repairs;
   - compact result package and payload manifest.
3. `docs(ode): reconcile validated prototype status`
   - domain documentation;
   - current dated log;
   - minimal `docs/INDEX.md` delta;
   - no `docs/DOCMAP.md` change unless its separate gate is met.

Rules:

- stage explicit paths only;
- use the `safe-commit` workflow for each commit;
- reference old PR #1 and source commits `135010c`, `4be3b2c`, and
  `c39bb3d` in commit/PR provenance without adding co-author or AI attribution;
- omit any empty commit group;
- do not squash away the distinction between executable evidence and
  documentation unless review requests a simpler history.

Before remote delivery, produce a review handoff containing:

- `BASE_SHA`;
- branch head;
- commit list;
- changed-file allowlist;
- verification commands and results;
- payload location/checksum boundary;
- remaining scientific limitations;
- explicit review focus on control identity, snapshot replay, and INDEX
  non-regression.

Push, creation of a replacement PR, closing old PR #1, and final merge occur
only at their separately confirmed remote gates.

## 12. Acceptance Criteria

The task is ready for review only when all applicable criteria pass:

- [x] Every designated recovery merge is an ancestor of recorded `BASE_SHA`.
- [x] Primary dirty worktree beginning/end snapshots are unchanged.
- [x] Post-merge gap audit is recorded and proves why a new delta is needed.
- [x] No broad old merge commit is replayed.
- [x] Phase 0 solver/config/runner/tests are present and runnable.
- [x] Phase 0 CSV and PNG are regenerated from accepted code/config.
- [x] Phase 1 suite expands deterministically.
- [x] All no-ligand controls use effective ligand `0.0` and have unambiguous
      pairing metadata.
- [x] Fractional `output_points`, `NaN`, infinity, invalid discrete copy number,
      and unknown/missing fields fail closed.
- [x] A copied result package can rerun from its own config snapshot.
- [x] Scenario manifest, metrics, and time-course payload use the same unique
      scenario set.
- [x] Old-grid runs produce 143 scenarios, 74 ligand scenarios, 69 controls,
      and 23,023 rows, or an
      approved config change explains and tests the new counts.
- [x] Full time-course tracking follows the then-current payload policy.
- [x] README and metadata describe the real tracked/external result contract.
- [x] `compileall`, ODE unit/contract tests, payload checks, and
      `git diff --check` pass.
- [x] No stale “solver absent” claim remains in an active current-status
      document.
- [x] No uncalibrated result is presented as a real detection limit, kinetic
      constant, or final construct recommendation.
- [x] `docs/INDEX.md` contains only the verified ODE increment and does not
      regress any other project line.
- [x] `docs/DOCMAP.md` is unchanged unless a new route contract genuinely
      requires it.
- [x] Changed files are limited to the reviewed allowlist.

## 13. Risks And Mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| A prerequisite ODE recovery already lands the same work | duplicate implementation or conflicting PR | mandatory post-merge gap audit and zero-delta stop |
| Canonical main changes after snapshot | status/document regression | re-snapshot before documentation and remote delivery |
| Historical branch content is treated as authority | stale INDEX/log/governance overwrite | recover focused code paths; semantic docs merge from `BASE_SHA` |
| Full time-course body is omitted without a contract | irreproducible or misleading result package | external payload manifest by default, or explicit promotion decision |
| Config snapshot still depends on source-tree paths | package-only rerun failure | snapshot-only replay test in an isolated directory |
| Control metadata describes requested rather than effective input | invalid scenario identity and comparisons | separate requested/effective fields and enforce pair contracts |
| Passing tests conceal scientific overclaim | uncalibrated prototype presented as project prediction | keep `scenario_prior` boundary in config, metadata, figures, docs, and tests |
| Existing dated logs collide with recovered work | historical facts overwritten or duplicated | write current reconstruction log; append old logs only with exact verified facts |
| Dirty primary worktree is accidentally mixed into the PR | unrelated user work enters commit | isolated worktree, explicit path staging, beginning/end snapshot comparison |

## 14. Stop Rules During Execution

Stop and report rather than improvising when:

- a required merge or canonical target cannot be proven;
- the post-merge ODE implementation has a different design whose ownership or
  intended replacement relationship is unclear;
- a current project authority conflicts with the old PR and the conflict cannot
  be resolved from repository evidence;
- a validator failure changes the scientific interpretation or result identity;
- the full time-course storage/promotion decision becomes necessary and the
  then-current policy does not resolve it;
- the branch target advances after final verification;
- a push, PR replacement, old-PR closure, or merge action lacks its current
  remote authorization.

## 15. References / 所引

- `AGENTS.md`
- `docs/DOCMAP.md`
- `docs/INDEX.md`
- `docs/modeling/P0-signal-pathway-ode.md`
- `docs/ops/payload-tracking-policy.md`
- `docs/ops/templates/payload_manifest.schema.tsv`
- `codex/docs/plans/README.md`
- old PR #1 source commits:
  - `135010c9ade743e812e34842db103fb736339653`
  - `4be3b2c001a16ac7c21074e7e71539acbb500126`
  - `c39bb3d604a41cdaeff7d7a38d698e3bdb85494b`
- excluded broad merge:
  - `05eb79a06e0f76de03e5860cee6c38535393d459`

## 16. Referenced By / 被引

- `codex/docs/plans/README.md`
- `.omx/plans/ode-pr1-post-recovery-content-integration-20260727.md`
- future execution-date log, after the trigger gate
- future replacement ODE PR handoff, if a real post-merge delta remains
