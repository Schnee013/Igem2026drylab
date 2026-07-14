# Gpr2 WT + ASCR18 Result-Package Recovery Contract

## Scope And Status

This file is the Git-visible recovery entry for the `Gpr2_WT + ASCR18` E2
short benchmark and 200 ns rep1 result packages. It does not promote raw or
processed trajectory bodies into Git. Those bodies remain operation-produced
payloads in ignored local storage and at the recorded E2 run roots.

Status of the local 2026-07-12 integrity review:

| Package | Result | Boundary |
|---|---|---|
| 100 ps short benchmark | PASS, 40/40 listed files | Manifest self-entry removed; producer fixed to exclude its output manifest. |
| 2026-07-05 preproduction snapshot | HOLD, 11/14 listed files | Three historical bodies do not match the preserved manifest; no source-backed replacement decision is available locally. |
| 200 ns rep1 final archive | PARTIAL, 45/48 listed files available and valid after local path remapping | Three non-analysis runtime byproducts are absent from the local archive. |
| processed rep1 convenience manifest | PASS, 10/10 listed files | Manifest self-entry removed. The final-archive manifest independently covers these same ten processed files. |

The E2 paths below were recorded by the run evidence and were last checked by
the project log on 2026-07-09. Their current availability was not rechecked in
this local-only repair:

- short benchmark: `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_short_benchmark_20260705`
- 200 ns rep1: `/ifs1/User/dengwei/igem/md-simulation/gpr2_wt_ascr18_production_rep1_20260705`

## Recovery Route

1. Confirm the recorded E2 root still exists before treating it as recoverable
   storage.
2. Restore E2 `production/` to local `raw/rep1/production/`, E2 `logs/` to
   local `raw/rep1/logs/`, and E2 `processed/rep1/` to local
   `processed/rep1/`.
3. First authenticate the restored final-archive manifest against the SHA-256
   recorded for it in `payload_manifest.tsv`.
4. From `raw/rep1/`, validate the final logs and production bodies with the
   final-archive manifest rows 1-28 and 39-48. From this result root, validate
   its processed rows 29-38. The manifest uses E2 run-root-relative paths, so
   the split local archive requires these two working-directory mappings.
5. Use the processed convenience manifest from `processed/rep1/` for a direct
   10-file check after restore. It is not a separate recovery dependency: its
   ten rows are derived from final-archive manifest rows 29-38 by replacing the
   `processed/rep1/` path prefix with `./` and excluding the manifest itself.

Validation commands after a complete restore:

```bash
(cd raw/rep1 && sed -n '1,28p;39,48p' logs/manifest_sha256_after_rep1.txt | sha256sum -c -)
sed -n '29,38p' raw/rep1/logs/manifest_sha256_after_rep1.txt | sha256sum -c -
(cd processed/rep1 && sha256sum -c SHA256SUMS_processed_rep1.txt)
```

For the current partial local archive, rows 44-45 and 47 of the final-archive
manifest cannot be checked because these files are absent:

- `production/gpr2_wt_ascr18_rep1_200ns_out.mdp`
- `production/gpr2_wt_ascr18_rep1_200ns_prev.cpt`
- `production/#gpr2_wt_ascr18_rep1_200ns.tpr.1#`

Their expected SHA-256 values remain in the final-archive manifest and in
`payload_manifest.tsv`; their E2 availability is pending verification. They are
not inputs to the current chctrl analysis, but they are required to claim an
exact restoration of the original 48-file archive.

## Producer And Consumer Chain

The 200 ns `gmx_mpi mdrun` produced the raw production trajectory. The recorded
GROMACS 2025.4 processing commands then used the production TPR/XTC and the E2
`input/gromacs/index.fixed.ndx` to create:

- `processed/rep1/prod_protein.xtc`
- `processed/rep1/protein_ref.pdb`

These two processed files are the direct trajectory/topology inputs consumed by
the configured chctrl driver family. Exact processing commands and group
selections remain in the ignored `make_analysis_index.log` and
`trjconv_*.log`; compact route metadata is in `processing_summary.tsv` and the
Git-visible `payload_manifest.tsv`. Regeneration therefore also requires the
recorded E2 repaired index body; if it cannot be restored, use of a newly
generated index must be treated as a new processing provenance chain.

## Tracking Classification

- `README.md` and `payload_manifest.tsv`: workflow and recovery contracts;
  track in Git.
- Short benchmark runner, command plan, compact summaries, warning gate, and
  checksum manifest: repo-visible operational contract/evidence.
- `raw/`, `processed/`, copied `input/gromacs/`, `production_smoke/`, full logs,
  trajectories, checkpoints, energy files, and raw GPU/machine snapshots:
  operation payload bodies; keep local/E2 unless separately promoted.

## References / 所引

- `docs/ops/payload-tracking-policy.md`
- `docs/ops/md-gromacs-operational-pitfalls.md`
- `docs/logs/2026-07-09.md`
- `e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`
- `gates/20260705_rep1_preproduction/README.md`
- `gates/20260706_rep1_launch/README.md`
- `raw/rep1/logs/manifest_sha256_after_rep1.txt`
- `processed/rep1/SHA256SUMS_processed_rep1.txt`
- `processed/rep1/processing_summary.tsv`

## Referenced by / 被引

- `payload_manifest.tsv`
- The current analysis package consumes the two processed rep1 inputs recorded
  here; no exhaustive reverse-link search has been performed.
