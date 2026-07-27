# MD Archive Router

This directory is the Git-visible checksum and recovery contract for MD payload
bodies whose complete manifest scope is stored on E2, AutoDL, or a verified
external mirror. Payload bodies are not repo-owned inputs and are not kept in
the Git worktree.

## Archive Authority

| Archive | Run root | Expected manifest | Integrity evidence |
|---|---|---|---|
| Gpr3 R167Y + ASCR3 200 ns rep1 | `/root/autodl-tmp/igem/md-simulation/gpr3_r167y_ascr3_rep1_20260717` | [91-row production manifest](gpr3-r167y-ascr3_200ns-rep1_20260720_archive.sha256) | `91/91 PASS` from the 2026-07-20 external-mirror validation |
| Gpr2 R59C + ASCR18 200 ns rep1 | `/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716` | [55-row final manifest](gpr2-r59c-ascr18_200ns-rep1_20260716_archive.sha256) | historical E2 `55/55 PASS` on 2026-07-19; current local `25/25` present files match, 30 remain E2-only |
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

The Gpr2 R59C Git manifest is byte-identical to the final manifest copied from
E2. The historical `55/55 PASS` remains a dated 2026-07-19 result. In the
2026-07-27 local audit, all 25 currently restored manifest members match and
the other 30 remain E2-only; this is not a new full-manifest PASS.

The Gpr3 R167Y manifest is byte-identical to the timestamped completion-gate
archive manifest. Its external-mirror validation is dated 2026-07-20.

Archive integrity does not change scientific interpretation. Phase-C3 EM/LINCS
caveats remain in their existing evidence sources, and smoke archives are not
production-completion evidence. Scientific-use boundaries remain in the
system-local status and analysis reports.

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

Restore the compact Gpr2 R59C analysis payload and evidence under:

```text
$DRYLAB_PAYLOAD_ROOT/experiments/md-simulation/results/gpr2-r59c-ascr18/
├── final_archive.sha256
├── production_archive.sha256
├── logs/production/
└── processed/rep1/
```

Restore the Gpr3 R167Y production and processed analysis inputs under:

```text
$DRYLAB_PAYLOAD_ROOT/experiments/md-simulation/results/gpr3-r167y-ascr3/
├── logs/production/rep1/
├── processed/rep1/
├── production/rep1/
└── sanity/production/rep1/
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
- `experiments/md-simulation/results/gpr2-r59c-ascr18/payload_manifest.tsv`
- `experiments/md-simulation/results/gpr3-r167y-ascr3/payload_manifest.tsv`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `experiments/md-simulation/results/gpr2-wt-ascr18/README.md`
- `experiments/md-simulation/results/gpr2-r59c-ascr18/README.md`
- `experiments/md-simulation/results/gpr3-r167y-ascr3/README.md`
