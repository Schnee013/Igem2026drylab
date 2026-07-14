# E2 MD Archive Router

This directory is the Git-visible checksum and recovery contract for MD payload
bodies whose complete manifest scope is stored on E2. Payload bodies are not
repo-owned inputs and are not kept in the Git worktree.

## Archive Authority

| Archive | E2 root | Expected manifest | Current integrity |
|---|---|---|---|
| Gpr2 WT + ASCR18 200 ns rep1 | `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705` | [48-row manifest](gpr2-wt-ascr18_200ns-rep1_20260705_archive.sha256) | `48/48 PASS` |
| Gpr2 WT + ASCR18 100 ps benchmark | `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_short_benchmark_20260705` | [40-row corrected manifest](gpr2-wt-ascr18_100ps-benchmark_20260705_archive.sha256) | `40/40 PASS` |
| `chimeric-ste2-gpa1-wt` Phase C3 | `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs` | [42-row manifest](chimeric-ste2-gpa1-wt_phase-c3_20260529_archive.sha256) | `42/42 PASS` |
| `chimeric-gpr3-aogpa2-c37` Phase C3 | `/ifs1/User/dengwei/igem/md-simulation/chimeric-gpr3-aogpa2-c37/gromacs` | [42-row manifest](chimeric-gpr3-aogpa2-c37_phase-c3_20260529_archive.sha256) | `42/42 PASS` |
| `chimeric-gpr3-aogpa2-c15` Phase C3 | `/ifs1/User/dengwei/igem/md-simulation/chimeric-gpr3-aogpa2-c15/gromacs` | [42-row manifest](chimeric-gpr3-aogpa2-c15_phase-c3_20260529_archive.sha256) | `42/42 PASS` |
| `chimeric-gpr2-aogpa2-c10` Phase C3 | `/ifs1/User/dengwei/igem/md-simulation/chimeric-gpr2-aogpa2-c10/gromacs` | [42-row manifest](chimeric-gpr2-aogpa2-c10_phase-c3_20260529_archive.sha256) | `42/42 PASS` |
| `chimeric-ste2-gpa1-wt` smoke | `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep1` | [11-row manifest](chimeric-ste2-gpa1-wt_smoke_20260529_archive.sha256) | `11/11 PASS` |
| `chimeric-gpr3-aogpa2-c37` smoke | `/ifs1/User/dengwei/igem/md-simulation/chimeric-gpr3-aogpa2-c37/gromacs/prod_rep1` | [11-row manifest](chimeric-gpr3-aogpa2-c37_smoke_20260529_archive.sha256) | `11/11 PASS` |
| `chimeric-gpr3-aogpa2-c15` smoke | `/ifs1/User/dengwei/igem/md-simulation/chimeric-gpr3-aogpa2-c15/gromacs/prod_rep1` | [11-row manifest](chimeric-gpr3-aogpa2-c15_smoke_20260529_archive.sha256) | `11/11 PASS` |
| `chimeric-gpr2-aogpa2-c10` smoke | `/ifs1/User/dengwei/igem/md-simulation/chimeric-gpr2-aogpa2-c10/gromacs/prod_rep1` | [11-row manifest](chimeric-gpr2-aogpa2-c10_smoke_20260529_archive.sha256) | `11/11 PASS` |

The package-level metadata and manifest digests are in
[payload_manifest.tsv](payload_manifest.tsv). Phase-C3 source manifests and
the seven-row smoke payload manifests are retained beside the authoritative
archive manifests as compact provenance.

The Gpr2 final archive has two distinct integrity statements: the historical
2026-07-12 local mirror was `45/48 PARTIAL`, while the current E2 canonical
archive validates `48/48 PASS`. The historical preproduction snapshot remains
`11/14 HOLD` in its system-local gate and is outside this router. The corrected
40-row short-benchmark manifest is the expected-list authority; the manifest
resident on E2 is stale and self-referential.

Archive integrity does not change scientific interpretation. Phase-C3 EM/LINCS
caveats remain in their existing evidence sources, and smoke archives are not
production-completion evidence. None of these PASS results clears a mutant GPR
provenance HOLD or makes a CHARMM-GUI package runnable.

## External Restore Layout

Choose a payload root outside the Git worktree:

```bash
export DRYLAB_PAYLOAD_ROOT=/absolute/path/outside/drylab
```

Restore Gpr2 final contents using the unchanged E2 run-root layout under:

```text
$DRYLAB_PAYLOAD_ROOT/experiments/md-simulation/results/gpr2-wt-ascr18/
├── logs/
├── production/
└── processed/rep1/
```

The analysis drivers continue to write canonical outputs under the repo
`result_dir/analysis/`, while `DRYLAB_PAYLOAD_ROOT` or the direct package-level
`CHIMERIC_MD_PAYLOAD_ROOT` redirects their `processed/repN` inputs.

Restore Phase-C3 payloads under:

```text
$DRYLAB_PAYLOAD_ROOT/experiments/md-simulation/systems/<system>/gromacs/
```

Set `SYSTEM_PAYLOAD_ROOT` directly or let the E2 sync scripts derive it from
`DRYLAB_PAYLOAD_ROOT`. Production/smoke pulls use `RESULT_PAYLOAD_ROOT` or the
same shared root and restore under
`$RESULT_PAYLOAD_ROOT/<system>/raw/repN/`. The sync scripts reject destinations
inside the Git worktree.

Validate a restored archive from its restored E2-root-equivalent directory:

```bash
sha256sum -c /absolute/path/to/archive-router/<expected-manifest>.sha256
```

## References / 所引

- `docs/ops/payload-tracking-policy.md`
- `docs/ops/md-gromacs-operational-pitfalls.md`
- `experiments/md-simulation/scripts/e2_sync_chimeric_inputs.sh`
- `experiments/md-simulation/scripts/e2_sync_chimeric_phase3_outputs.sh`
- `experiments/md-simulation/scripts/e2_sync_chimeric_results.sh`
- `experiments/md-simulation/results/gpr2-wt-ascr18/payload_manifest.tsv`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/README.md`
