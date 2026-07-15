# Gpr2 WT + ASCR18 Result-Package Recovery Contract

## Scope And Status

This file is the Git-visible recovery entry for the `Gpr2_WT + ASCR18` E2
short benchmark and 200 ns rep1 result packages. Operation-produced payload
bodies stay on E2 or in an explicitly configured external payload root; they
are not repo-owned inputs and are not kept in the Git worktree.

| Package | Current authority | Boundary |
|---|---|---|
| 100 ps short benchmark | E2 canonical archive `40/40 PASS` | Operational resource baseline only. |
| 2026-07-05 preproduction snapshot | `11/14 HOLD` | Historical snapshot; three preserved checksum mismatches remain unresolved. |
| 200 ns rep1 final archive | E2 canonical archive `48/48 PASS` | Archive integrity only; scientific caveats remain unchanged. |

The historical 2026-07-12 local mirror state remains `45/48 PARTIAL`; it is
not the current archive authority. The Git-visible archive checksums and E2
roots are maintained in [the archive router](../../archive-router/README.md).

## Recovery Route

Choose a payload root outside the Git worktree:

```bash
export DRYLAB_PAYLOAD_ROOT=/absolute/path/outside/drylab
```

Restore the E2 final run-root layout unchanged under:

```text
$DRYLAB_PAYLOAD_ROOT/experiments/md-simulation/results/gpr2-wt-ascr18/
├── logs/
├── production/
└── processed/rep1/
```

From that package root, validate the restored final archive against the
Git-visible router manifest:

```bash
sha256sum -c /absolute/path/to/drylab/experiments/md-simulation/archive-router/gpr2-wt-ascr18_200ns-rep1_20260705_archive.sha256
```

For the short benchmark, restore the E2 benchmark root outside the repository
and validate it with
`gpr2-wt-ascr18_100ps-benchmark_20260705_archive.sha256` from the same router.
The corrected Git-visible expected list is authoritative; the manifest
resident on E2 is stale and self-referential.

## Producer And Consumer Chain

The 200 ns `gmx_mpi mdrun` produced the raw production trajectory. The recorded
GROMACS 2025.4 processing commands used the production TPR/XTC and the E2
`input/gromacs/index.fixed.ndx` to create:

- `processed/rep1/prod_protein.xtc`
- `processed/rep1/protein_ref.pdb`

These two files are the direct inputs consumed by the configured chctrl driver
family. Set `DRYLAB_PAYLOAD_ROOT` as above, or set
`CHIMERIC_MD_PAYLOAD_ROOT` directly to this external package root. Analysis
outputs continue to be written under the repo-owned `result_dir/analysis/`.

Exact processing logs and the repaired index remain E2 payloads. If that
processing chain cannot be restored, regenerated inputs constitute a new
provenance chain rather than an exact restoration.

## Tracking Classification

- `README.md`, `payload_manifest.tsv`, analysis outputs, configs, scripts, and
  tests: repo-owned contracts or canonical results; track in Git.
- `experiments/md-simulation/archive-router/`: Git-visible checksum and recovery
  authority for the E2 archives; track in Git.
- Raw/processed trajectories, copied runtime inputs, short-production bodies,
  full logs, machine snapshots, warning/summary bodies, and convenience
  checksums covered by the archive manifest: operation payloads; keep on E2 or
  in an external payload root, not in the Git worktree.

Archive integrity does not clear either mutant GPR checksum-provenance HOLD,
does not change the `11/14 HOLD` snapshot, and does not make any CHARMM-GUI
package runnable.

## References / 所引

- [Archive router](../../archive-router/README.md)
- [Payload tracking policy](../../../../docs/ops/payload-tracking-policy.md)
- [MD operational guardrails](../../../../docs/ops/md-gromacs-operational-pitfalls.md)
- [200 ns analysis summary](analysis/gpr2_wt_ascr18_rep1_chctrl_metric_analysis_20260709.md)
- [Short benchmark contract](e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md)
- [Preproduction HOLD](gates/20260705_rep1_preproduction/README.md)

## Referenced by / 被引

- [Project index](../../../../docs/INDEX.md)
- [MD modeling route](../../../../docs/modeling/P0-md-simulation.md)
- `payload_manifest.tsv`
- `chimeric_systems.gpr2_wt_ascr18_rep1.json`
