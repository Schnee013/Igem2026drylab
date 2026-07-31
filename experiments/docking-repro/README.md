# docking-repro directory contract

This directory contains historical Hu2024-compatible docking reproduction and
mutant-scan artifacts plus the code used to repair the mutant coordinate-frame
defect. It is an experiment-output tree, not an MD package authority.

## Local execution

On macOS, run docking-repro scripts in the `docking` conda environment. Keep
docking dependencies out of the base environment.

## Current status

Status is `geometry_gate_v3_seed44_holdout_fail_stop_full_blocked`. The
replacement gate was frozen from seed-42 + seed-43 WT evidence before the
independent seed-44 holdout. All eight holdout docking jobs, IFP reports and
geometry reports completed technically, but both Gpr3/R167Y arms failed the
frozen gate; the ascr3 arm also failed MODEL 1 geometry. The run therefore
ended `TERMINAL_ABNORMAL / fail_stop_before_full`. No full plan, remaining
320 jobs, active shortlist, ratio/IFP ranking, or wetlab handoff was created.
Current status is routed through `docs/INDEX.md` and
`docs/modeling/P0-molecular-docking.md`.

The following files are retained only as dated historical evidence:

| Historical role | Path |
|---|---|
| Withdrawn ratio report | `experiments/docking-repro/analysis/ratio_channel_report.md` |
| Withdrawn pair ranking | `experiments/docking-repro/analysis/ratio_pairings.csv` |
| Withdrawn full spectrum | `experiments/docking-repro/analysis/ratio_spectrum.csv` |
| Versioned 2026-05-20 release | `experiments/docking-repro/analysis/releases/gpr3_f_full_20260520_0854/` |
| Withdrawn Top mutant IFP output | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/` |
| Withdrawn MD shortlist document | `docs/modeling/P0-docking-md-candidate-shortlist.md` |

The `tmp/` directories under IFP result roots are run intermediates. They can be
used as provenance for a promoted package input, but MD package files must not
point to them as active coordinate authorities.

## 2026-07-30 frame-repair smoke checkpoint

The local alignment precursor
`temp/docking_frame_repair_20260730_local_frame_v2/` remains evidence for the
162/162 mutant aligned-PDB and two WT identity-frame preparation step. It is not
the current smoke or result root.

The current archived E2 run is
`temp/docking_frame_repair_20260730_e2_smoke_r1_v5/`, run identity
`950639bdc788bf23a3cacc61d57dfa130ea05872f3d64663f87b88e567f6bce8`.
Its machine-readable terminal authority is `terminal/smoke_terminal.json`,
terminal identity
`abbcad305e305004c328b75c7be9c82b4981d0ee60286e90a093c49c9b1f3c3f`;
`run_state_events.tsv` records `TERMINAL_ABNORMAL` /
`fail_stop_before_full`.

All eight unique jobs completed in one attempt with explicit CPU8 and full
invocation identity. Six returned 20 poses; both Gpr3 R167Y jobs returned 18
valid poses and were correctly accepted as technically complete. All eight IFP
reports completed. Geometry passed for three jobs and failed for five:

| Job | Passing poses | Frozen minimum | MODEL 1 |
|---|---:|---:|---|
| Gpr2 WT / ascr18 | 17 | 19 | pass |
| Gpr2 WT / ascr3 | 17 | 18 | pass |
| Gpr2 R59C / ascr18 | 18 | 19 | pass |
| Gpr3 R167Y / ascr18 | 12 | 15 | pass |
| Gpr3 R167Y / ascr3 | 9 | 15 | fail |

The two Gpr2 WT distribution failures mean the run cannot isolate a mutant
effect; the historical WT calibration, locked-toolchain pose distribution and
geometry definition must be audited before any threshold or rerun decision.
No threshold was changed, no full job plan was created, and the remaining 320
jobs were not started. The smoke scores, poses and IFP are audit evidence only,
not a ratio, ranking or candidate source.

`RUN_FILES.sha256` covers 608 remote files and has SHA256
`1f5773d92a9d9abbcd63b2cf9599a03fca3694aca048bf9bbbbafec3d26dfd4b`;
the local archive passed 608/608 checks. The separately authorized earlier v4
run remains immutable historical evidence at
`temp/docking_frame_repair_20260730_e2_smoke_9attempt_v4/`, run identity
`0f86f691a477107b210a35bdf1f863086518cd214355b6712841fae044a5781f`.
Its machine-readable authority is `terminal/smoke_terminal.json`, terminal
identity
`6d5c69afeef74ca01b12d479f3b38efed2770bca90070712d47e618cf9e75140`.
The terminal state is `TERMINAL_ABNORMAL` / `fail_stop_before_full`:

- six jobs completed technically with 20 poses each;
- all eight unique jobs were attempted;
- Gpr3 R167Y-ascr18 returned 18/20 poses in both its initial attempt and one
  bounded same-contract retry;
- Gpr3 R167Y-ascr3 returned 18/20 poses in its initial attempt;
- the archive therefore contains nine attempts across eight unique jobs,
  with two technically failed unique jobs and no unattempted job;
- IFP and pose-geometry evaluation were not run;
- no full job plan was created and the remaining 320 jobs were not started.

The run used the exact E2 package lock in
`environments/e2-docking-frame-repair.lock.yml`: Vina conda 1.2.6, OpenBabel
conda 3.1.1, and ADFRsuite 1.1dev build 100. All four prepared smoke receptor
PDBQT files passed the frame check with a maximum common-heavy-atom coordinate
difference of 0.0 Angstrom.

The 573 remote payload files were archived byte-identically. The local run root
adds `REMOTE_PAYLOAD.sha256`, `ARCHIVE_TREE.sha256`, `ARCHIVE_INTAKE.json`, and
`ARCHIVE_PATH_MAP.tsv`; remote-authored manifests retain their original paths
and bytes. The failed smoke scores and poses are audit evidence only, not a
ratio, ranking, or candidate source. The preceding immutable v3 fail-stop
archive remains at `temp/docking_frame_repair_20260730_e2_smoke_v3/`. Any
further recovery attempt requires authorization under the new contract; do not
change seed, box, energy range, or operational thresholds to force a pass.

## 2026-07-30 18-mode cause audit and proposed recovery

The v4 terminal state remains immutable, but its two 18-of-20 jobs are no longer
interpreted as Vina crashes. Vina 1.2.6 defines `num_modes` as a maximum. The
three affected attempts completed normally with consecutive models; their
best-to-last affinity spans are 1.118 and 1.192 kcal/mol, below the frozen
3.0 kcal/mol energy range. Gpr3 R167Y-ascr18 is byte-identical across v3 CPU8
and both v4 attempts, so a same-contract retry cannot recover two more modes.

The audit also found an independent v4 provenance defect: all nine Vina command
records omit explicit `--cpu 8`, and CPU is absent from the v4 job plan,
environment compute record and job identity. The v4 archive therefore supports
mode-behavior and terminal-state audit only; it cannot be promoted as a
resource-bounded production smoke.

The executed R1 contract is
[`codex/docs/plans/docking-frame-repair-18mode-recovery-contract-20260730.md`](../../codex/docs/plans/docking-frame-repair-18mode-recovery-contract-20260730.md).
It preserves the scientific search parameters, treats 20 as the requested
maximum, keeps the existing absolute geometry `min_passing_modes` values as
pose-population sufficiency limits, and binds explicit CPU8 plus complete
invocation provenance. The new all-eight-job E2 smoke completed the technical
and IFP stages but failed the geometry terminal. The remaining 320 jobs remain
blocked pending a separate WT-calibration and geometry-gate audit.

## 2026-07-31 WT-only calibration checkpoint

The separately authorized run is archived at
`temp/docking_frame_repair_20260731_e2_wt_calibration_seed43_r3/`. It reused the
same frame and locked E2 environment, fixed seed 43, and ran only
Gpr2/Gpr3 WT against ascr18/ascr3:

- 4/4 docking jobs completed normally, each with 20 poses under the
  `1 <= actual_modes <= requested_max_modes(20)` contract;
- 4/4 IFP and 4/4 historical-gate diagnostics completed;
- the historical gate failed both Gpr2 arms and passed both Gpr3 arms, but this
  did not modify or freeze a replacement gate;
- `RUN_FILES.sha256` passed 59/59 locally and remotely;
- no mutant, full plan, remaining 320 jobs, ranking or candidate selection was
  started.

The visual-review entrypoint is
`tmp/wt_calibration_seed43_pose_review.ipynb`. It can load MODEL 1, any chosen
pose, or all poses in PyMOL. The scoped MODEL 1 / pose 1 visual check is
complete; per-pose review remains available for diagnostics. Detailed run
evidence and the next authorization boundary are in
[`docs/logs/2026-07-31.md`](../../docs/logs/2026-07-31.md) and the
[geometry-gate decision package](../../codex/docs/plans/docking-geometry-gate-recalibration-decision-20260730.md).

## 2026-07-31 frozen-gate seed-44 holdout checkpoint

The replacement gate is frozen at
`experiments/docking-repro/geometry-gates/20260731_seed42_seed43_wt_v1/geometry_gate.json`
with gate identity
`5b59c1d36b3b5e89e0c67ed9846c2b76b48bf1ca5ce8af9873a8562565740924`.
The independent holdout is archived at
`temp/docking_frame_repair_20260731_e2_full_seed44_r1/`, run identity
`4496efeedc527d870fff06c5e61b49ef811b0c27045b739846e4471a97c0af69`.

All 8 docking, IFP and geometry records completed. Six arms passed. The frozen
gate rejected Gpr3/R167Y-ascr18 at 14/16 passing poses and
Gpr3/R167Y-ascr3 at 11/18; the latter also failed MODEL 1 geometry. The
machine-readable terminal identity is
`43967837a7473c1a422df31e87924e727b1d9a54a1fe933f1252712bb7b5bbfa`
with `fail_stop_before_full`. `RUN_FILES.sha256` passed 1,089/1,089 both
remotely and after local intake. The gate was not refit, no full plan was
created, and the remaining 320 jobs were not started.

## Multi-mutant local preparation

Phase 2 schema/test preparation is available at
[`multi-mutant/README.md`](multi-mutant/README.md). It contains only the
canonical genotype schema, synthetic cycle template, local FASTA/cycle
validator contract, and tests. It contains no real candidate cycle and does
not change the frame-repair or toolchain gate.

## Historical promoted MD pose inputs

The existing MD packages consumed these promoted system-local pose files. They
remain auditable descriptions of their actual starting poses, but they do not
validate a repaired docking ranking or define a current shortlist:

| System | Promoted pose input | Historical docking source |
|---|---|---|
| `Gpr2_R59C + ASCR18` | `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/Gpr2_R59C_ascr18_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr2_R59C_ascr18_poses.sdf` |
| `Gpr3_R167Y + ASCR3` | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf` |

## Historical and one-off result roots

The following roots are retained as historical method or test evidence unless a
separate source-backed archive/delete pass classifies each one:

| Path class | Boundary |
|---|---|
| `results/wt_singlestage*` | WT redock, 3D-offset, and Gpr3 pose-geometry tests from method repair. |
| `results/ifp_analysis*` | IFP snapshots from different method stages; they are not guaranteed to be supersets of one another. |
| `analysis/pymol_top6/` | Historical visualization material; regenerate separately only after a frame-repaired shortlist exists. |
| `analysis/pymol_gpr3_review/` | Gpr3 pose-review helper scripts. |
| `mutagenesis/af3_downloads/` | AF3 downloaded structures and job request evidence; do not bulk-delete. |
| `mutagenesis/archive/` | Historical voided or retired mutagenesis evidence. |

## Cleanup performed on 2026-07-16

- Removed 168 ignored `.DS_Store` files under `experiments/docking-repro/`.
- Removed empty result placeholder directories:
  - `experiments/docking-repro/results/interactions/`
  - `experiments/docking-repro/results/poses/`
- Removed empty accidental nested directory:
  - `experiments/experiments/`

No docking result bodies, AF3 structures, PDBQT pose sets, IFP outputs, ratio
tables, PyMOL assets, or historical test result JSON files were deleted in this
pass.

## References / 所引

- `docs/modeling/P0-molecular-docking.md`
- `docs/modeling/P0-docking-md-candidate-shortlist.md`
- `experiments/docking-repro/analysis/ratio_channel_report.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/README.md`
- `codex/docs/plans/docking-frame-repair-18mode-recovery-contract-20260730.md`

## Referenced by / 被引

- `docs/modeling/P0-molecular-docking.md`
- `docs/logs/2026-07-30.md`
- `experiments/docking-repro/multi-mutant/README.md`
