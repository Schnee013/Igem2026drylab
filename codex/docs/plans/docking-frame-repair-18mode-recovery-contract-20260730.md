# Docking frame repair 18-mode recovery contract

> Status: `executed_fail_stop_at_geometry`
>
> Scope: repair the technical-completion, pose-population and CPU/provenance
> contracts, then run one new eight-unique-job recovery smoke. This plan does
> not authorize the remaining 320 docking jobs, ratio/IFP ranking, candidate
> selection, wetlab handoff, commit or push.
>
> Current project status remains authoritative in `docs/INDEX.md`. The v3/v4
> terminal manifests remain immutable historical run-state authorities; the R1
> terminal is the current smoke authority.

## Execution outcome

The user approved R1 through completion of the new eight-job smoke. The
implementation and run preserved the frozen receptor, ligand, box, seed,
spacing, exhaustiveness, Vina version and output/search parameters while
adding maximum-20 semantics, explicit CPU8 and full invocation identity.

The current archived run is
`temp/docking_frame_repair_20260730_e2_smoke_r1_v5/`, run identity
`950639bdc788bf23a3cacc61d57dfa130ea05872f3d64663f87b88e567f6bce8`.
All 8/8 docking jobs and 8/8 IFP reports completed. The two Gpr3 R167Y jobs
returned 18 poses and passed the corrected technical and pose-population
contracts. The terminal geometry result is nevertheless
`fail_stop_before_full`: only 3/8 jobs passed the frozen complete-distribution
gate.

Five failures were recorded as follows:

| Job | Passing poses | Frozen minimum | MODEL 1 |
|---|---:|---:|---|
| Gpr2 WT / ascr18 | 17 | 19 | pass |
| Gpr2 WT / ascr3 | 17 | 18 | pass |
| Gpr2 R59C / ascr18 | 18 | 19 | pass |
| Gpr3 R167Y / ascr18 | 12 | 15 | pass |
| Gpr3 R167Y / ascr3 | 9 | 15 | fail |

The terminal identity is
`abbcad305e305004c328b75c7be9c82b4981d0ee60286e90a093c49c9b1f3c3f`.
`run_state_events.tsv` records `TERMINAL_ABNORMAL`; no full job plan was
created and the remaining 320 jobs were not started. Because both Gpr2 WT
baselines failed only the complete-distribution count while MODEL 1 passed,
the next decision must follow a separate WT-calibration/toolchain/geometry-gate
audit. This plan does not authorize such a rerun or any threshold change.

## Decision summary

Recommend **R1: preserve the scientific search parameters and correct the
technical contract**.

- Keep receptor frame, box, ligand, Vina 1.2.6, seed 42, spacing,
  exhaustiveness 200, `num_modes=20`, `energy_range=3.0`,
  `min_rmsd=1.0` and `max_evals=0` unchanged.
- Interpret `num_modes=20` as `requested_max_modes=20`, not as a guaranteed
  exact output count.
- Separate Vina technical completion from pose-population comparability and
  from the downstream geometry gate.
- Pass `--cpu 8` explicitly and bind the complete invocation to the job
  identity. Do not infer CPU from an environment variable.
- Use a new run identity and rerun all eight unique smoke jobs. Do not mutate,
  merge or retroactively promote v3/v4 attempts.

R1 requires explicit user approval before code changes or a new E2 run.

## Verified cause

### Vina completed normally

The three 18-mode attempts contain a complete Vina result table and a
well-formed PDBQT with consecutive `MODEL 1` through `MODEL 18`. The runner
returns from Vina only after process return code zero and a non-empty affinity
table. The recorded exception is raised later by
`docking_manifest.pose_evidence()` because it currently requires
`actual_modes == expected_modes`.

Relevant implementation:

- `src/modeling/docking-repro/dock.py`
- `src/modeling/docking-repro/docking_manifest.py`
- `src/modeling/docking-repro/run_frame_repair_docking.py`

### `num_modes` is a maximum

AutoDock Vina v1.2.6 defines `--num_modes` as the “maximum number of binding
modes to generate”. Search results are RMSD-deduplicated, and output is also
bounded by `energy_range`; therefore fewer than the requested maximum is a
valid successful output.

Official source pointers:

- <https://github.com/ccsb-scripps/AutoDock-Vina/blob/v1.2.6/src/main/main.cpp#L236-L242>
- <https://github.com/ccsb-scripps/AutoDock-Vina/blob/v1.2.6/src/lib/parallel_mc.cpp#L51-L73>
- <https://github.com/ccsb-scripps/AutoDock-Vina/blob/v1.2.6/src/lib/vina.cpp#L557-L615>
- <https://github.com/ccsb-scripps/AutoDock-Vina/blob/v1.2.6/src/lib/vina.cpp#L858-L914>

### The 18-mode outputs were not energy-range truncation

| Job/attempt | Modes | Best affinity | Last affinity | Difference |
|---|---:|---:|---:|---:|
| Gpr3 R167Y-ascr18 attempt 1 | 18 | -6.953 | -5.835 | 1.118 kcal/mol |
| Gpr3 R167Y-ascr18 attempt 2 | 18 | -6.953 | -5.835 | 1.118 kcal/mol |
| Gpr3 R167Y-ascr3 attempt 1 | 18 | -7.097 | -5.905 | 1.192 kcal/mol |

All differences are below the frozen 3.0 kcal/mol range. Increasing
`energy_range` does not address these observed outputs.

### Same-contract retry has no recovery value

Gpr3 R167Y-ascr18 is byte-identical across v3 CPU8, v4 attempt 1 and v4
attempt 2:

`1ac5be6c79be7bd85b6bf1f5cd33c7ef440dd61eac3a16152b0d394999e23e69`

The seven v3/v4 jobs shared by both runs also have byte-identical pose files.
No attempt may be appended or merged to manufacture 20 modes.

### v4 has an independent CPU-contract defect

Every v4 Vina command omitted `--cpu 8`; v3 commands included it. The current
runner only appends `--cpu` when the unbound `VINA_CPU` environment variable is
present. CPU is absent from the v4 job plan, environment compute record and job
identity. The v4 stderr warning about low exhaustiveness is consistent with
Vina auto-detecting more CPUs than the 200 search tasks can use.

Consequently v4 supports auditing the deterministic 18-mode behavior, but it
cannot be promoted as a resource-bounded production smoke.

## R1 technical contract

### 1. Invocation and identity

The canonical config and every job identity must bind:

- Vina executable SHA256, package version and package build;
- receptor and ligand hashes;
- box center and dimensions;
- spacing, exhaustiveness and seed;
- `requested_max_modes=20`;
- `energy_range=3.0`;
- `min_rmsd=1.0`;
- `max_evals=0`;
- `cpu=8`.

The runner must pass all four output/search controls and `--cpu 8` explicitly.
Missing or different command flags fail closed before Vina starts. Invocation
flags must be present in the job plan rather than existing only in per-attempt
command JSON.

### 2. Vina technical completion

A Vina attempt is technically complete only when:

1. return code is zero;
2. the pose file exists and has `1 <= actual_modes <= requested_max_modes`;
3. MODEL numbers are consecutive from 1;
4. MODEL 1 exists;
5. stdout affinities and PDBQT affinities/counts agree;
6. all pose bodies and invocation artifacts have recorded hashes.

Fewer than 20 modes is not by itself a technical failure. Zero modes, more
than 20 modes, missing/gapped models, affinity disagreement or an incomplete
file remains a technical failure.

Every attempt, including failed attempts, must preserve return code, elapsed
time, stdout, stderr, command and any pose evidence.

### 3. Pose-population comparability

Do not invent a new fractional cutoff. Reuse the absolute, pre-mutant
`min_passing_modes` values already frozen in `config.yaml`:

| Receptor / ligand | Minimum returned modes needed to be comparable | Frozen geometry `min_passing_modes` |
|---|---:|---:|
| Gpr2 / ascr18 | 19 | 19 |
| Gpr2 / ascr3 | 18 | 18 |
| Gpr3 / ascr18 | 15 | 15 |
| Gpr3 / ascr3 | 15 | 15 |

If a technically complete attempt returns fewer modes than this absolute
minimum, record `non_comparable_pose_population` and stop the smoke. Do not
retry with a new seed or change the threshold.

### 4. Geometry and IFP

For every technically complete, population-comparable job:

- audit all actually returned modes;
- require MODEL 1 to pass the existing frame, search-volume, membrane,
  central-pocket, receptor-contact and provenance gates;
- require the absolute number of passing modes to meet the frozen
  receptor/ligand `min_passing_modes`;
- do not rescale 15/20, 18/20 or 19/20 thresholds to the returned-mode count;
- bind score, MODEL 1 pose body, full pose set, geometry and IFP by hashes.

## Recovery execution

### Phase 1 — local implementation

**Inputs**

- Current frame-repair source and config.
- v3/v4 immutable archives.
- Frozen geometry calibration report.

**Outputs**

- Updated config terminology and CPU/search controls.
- Updated pose evidence, job identity, runner and geometry adapter.
- Focused regression tests.

**Validators**

- Accept well-formed 18-of-20 technical output.
- Reject 0, 21, gapped, unclosed or affinity-mismatched outputs.
- Enforce the four absolute population minima.
- Require explicit `--cpu 8` and prove CPU/search controls alter job identity.
- Preserve return code and elapsed time for a forced post-Vina validator
  failure.
- Reject v3/v4 manifests under the new schema without mutating them.

**Stop conditions**

- Any source/manifest caller remains on exact-20 semantics.
- Any invocation field is absent from identity or job plan.
- Existing frame, box, ratio-source or geometry tests regress.

### Phase 2 — new E2 recovery smoke

This phase requires explicit approval after the local tests pass.

**Inputs**

- One source snapshot and one production-ready E2 environment identity.
- The same four aligned receptors and two ligands.
- Eight unique jobs:
  `Gpr2 WT/R59C × ascr18/ascr3` and
  `Gpr3 WT/R167Y × ascr18/ascr3`.

**Outputs**

- A new run root and run identity.
- Eight terminal job records with complete attempt provenance.
- No reuse or mutation of v3/v4 job manifests.

**Validators**

- Preflight confirms Vina/OpenBabel/ADFR and explicit CPU8 contract.
- 8/8 attempts satisfy technical completion and population comparability.
- Command JSON, job plan and identity agree.

**Stop conditions**

- Toolchain or input drift.
- Missing `--cpu 8`.
- Any technical failure or `non_comparable_pose_population`.

The six completed v3 CPU8 jobs took about 187–248 seconds each. A new serial
CPU8 eight-job docking pass is therefore expected to be on the order of tens
of minutes, but exact recovery timing must come from the new attempt records.

### Phase 3 — smoke geometry/IFP and terminal

Run only after Phase 2 passes.

**Outputs**

- Eight-job geometry and IFP reports.
- A terminal smoke manifest that either authorizes a later full-run decision
  or records an immutable fail-stop.

**Stop conditions**

- MODEL 1 failure.
- Absolute passing-mode count below the frozen threshold.
- Frame, contact, membrane, pocket, search-volume or hash-source mismatch.

Passing this smoke does not itself authorize the remaining 320 jobs.

## Rejected alternatives

### R2 — change search/scoring parameters to force 20 modes

Increasing `energy_range`, changing seed, exhaustiveness, box or `min_rmsd`, or
requesting extra modes and truncating afterward changes the scientific
contract. The current evidence does not justify this route.

### R3 — retain exact-20 completion

Two R167Y ligand arms already return 18 valid modes, and the ascr18 result is
byte-identical under CPU8 and auto-CPU. Exact-20 would keep rejecting valid
Vina output and is not executable for a complete mutant matrix.

Multi-seed pose merging is also rejected because it changes the 328-job,
ratio and pose-distribution definitions.

## Files expected to change after approval

- `src/modeling/docking-repro/config.yaml`
- `src/modeling/docking-repro/dock.py`
- `src/modeling/docking-repro/docking_manifest.py`
- `src/modeling/docking-repro/run_frame_repair_docking.py`
- `src/modeling/docking-repro/preflight_docking_environment.py`
- `src/modeling/docking-repro/evaluate_frame_repair_geometry.py`
- `src/modeling/docking-repro/geometry_gate.py`
- `src/modeling/docking-repro/run_frame_repair_ifp.py`
- `src/modeling/docking-repro/aggregate_frame_repair_terminal.py`
- `src/modeling/docking-repro/finalize_frame_repair_smoke_failure.py`
- `tests/modeling/test_docking_frame_repair.py`
- `tests/modeling/test_docking_frame_repair_unittest.py`

Before editing, re-run the caller inventory for `expected_modes_per_job`,
`pose_evidence()` and `verify_job_manifest()`; no exact-20 caller may remain.

Current status/router files will be updated again only when implementation or a
new run changes their active state.

## Approval record

The completed authorization covered:

1. exact-20 becoming maximum-20 technical semantics;
2. the four frozen absolute pose-population minima;
3. explicit CPU8 plus full invocation identity;
4. a new all-eight-job E2 recovery smoke after local validation;
5. no authorization for the remaining 320 jobs, full ranking or wetlab
   delivery.

All five conditions were followed. A new approval is required before any
geometry-threshold change, further smoke, remaining docking jobs, ranking or
wetlab delivery.

## References / 所引

- `temp/docking_frame_repair_20260730_e2_smoke_v3/`
- `temp/docking_frame_repair_20260730_e2_smoke_9attempt_v4/`
- `temp/docking_frame_repair_20260730_e2_smoke_9attempt_v4/terminal/smoke_terminal.json`
- `temp/docking_frame_repair_20260730_e2_smoke_9attempt_v4/geometry_calibration_report.json`
- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/terminal/smoke_terminal.json`
- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/run_state_events.tsv`
- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/RUN_FILES.sha256`
- `src/modeling/docking-repro/config.yaml`
- `src/modeling/docking-repro/dock.py`
- `src/modeling/docking-repro/docking_manifest.py`
- `src/modeling/docking-repro/run_frame_repair_docking.py`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-molecular-docking.md`
- `experiments/docking-repro/README.md`
- `docs/logs/2026-07-30.md`
