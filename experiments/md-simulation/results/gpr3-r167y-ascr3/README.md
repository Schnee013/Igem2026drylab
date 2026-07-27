# Gpr3 R167Y + ASCR3 rep1 result-package recovery contract

## Scope and status

This directory is the Git-visible recovery and analysis entry for the
validator-accepted `Gpr3_R167Y + ASCR3` 200 ns production rep1 on the AutoDL
clone.

| Stage | Verified result | Evidence |
|---|---|---|
| Physical production | `TERMINAL_NORMAL`; 139,708 XTC atoms; 2,001 frames; final step 100,000,000 and time 200,000 ps | external `logs/production/rep1/run_state_events.tsv` and completion attempt |
| Completion gate | `PASS`; completed `2026-07-20T10:16:40Z`; empty issue scan; performance `264.134 ns/day` | external `logs/production/rep1/completion_attempt3_20260720T101630Z/` |
| Production archive | `91/91 PASS` | [Git-visible production manifest](../../archive-router/gpr3-r167y-ascr3_200ns-rep1_20260720_archive.sha256) |
| Postprocess | `PASS`; 6,356 atoms; 2,001 frames ending at 200,000 ps; `SOLU=6356`, `PROA_BACKBONE=1603` | external `processed/rep1/postprocess_attempt3_20260720T101730Z/` |
| Seven-driver analysis | seven shared `chctrl` drivers exited `0`; 45 canonical output/content checks and 55 analysis checksums passed | `analysis/run_logs/analysis_attempt3_20260720T101900Z/` and [metric report](analysis/gpr3_r167y_ascr3_rep1_chctrl_metric_analysis_20260720.md) |

The final state is production complete, postprocess complete, and single-rep
analysis complete. The scientific evidence level remains
`single_rep_exploratory_only`; this package does not establish a replicated
WT/R167Y genotype conclusion.

## Recovery route

The production, run evidence, sanity output, and processed analysis inputs were
restored outside the Git worktree at:

```text
/Users/roy/Documents/drylab-payloads/experiments/md-simulation/results/gpr3-r167y-ascr3/
├── logs/production/rep1/
├── processed/rep1/
├── production/rep1/
└── sanity/production/rep1/
```

The AutoDL run-root authority was:

```text
/root/autodl-tmp/igem/md-simulation/gpr3_r167y_ascr3_rep1_20260717
```

Validate the restored production archive from the external result root:

```bash
sha256sum -c /absolute/path/to/drylab/experiments/md-simulation/archive-router/gpr3-r167y-ascr3_200ns-rep1_20260720_archive.sha256
```

For local analysis, set:

```bash
export CHIMERIC_MD_CONFIG=experiments/md-simulation/results/gpr3-r167y-ascr3/chimeric_systems.gpr3_r167y_ascr3_rep1.json
export CHIMERIC_MD_REPS=1
export CHIMERIC_MD_PAYLOAD_ROOT=/Users/roy/Documents/drylab-payloads/experiments/md-simulation/results/gpr3-r167y-ascr3
```

The direct analysis inputs are:

- `processed/rep1/prod_protein.xtc`: SHA256 `1ebe62179c568c697bcc24c7e898aa6af60c53188d91dca00ac9fc2d9a85d40a`
- `processed/rep1/protein_ref.pdb`: SHA256 `0da0a5961f07abf89c20ead561bf1770bfbc08b8436125d9eedc4c1956783423`

## Producer and consumer chain

AutoDL GROMACS 2025.4 produced the 200 ns full-system trajectory. The
source-first postprocess script consumed the production TPR/XTC and created the
6,356-atom `SOLU` trajectory and reference. The configured shared seven-driver
family consumed those processed inputs and wrote canonical CSV, PNG, Markdown,
and run-evidence outputs under `analysis/`.

The first BSA invocation used base Python and failed because `mdtraj` was not
installed there. No dependency was installed. The same shared driver was rerun
with the existing `chimeric` environment and exited `0`; both the failed attempt
and successful recovery logs are retained.

## Tracking classification

- Track in Git: this README, `payload_manifest.tsv`, analysis config, canonical
  analysis outputs, scripts, tests, and the archive-router manifest.
- Keep outside Git: raw TPR/CPT/GRO/XTC/EDR, processed trajectory bodies, full
  runtime logs, and machine/runtime snapshots.

## References / 所引

- [Archive router](../../archive-router/README.md)
- [Payload tracking policy](../../../../docs/ops/payload-tracking-policy.md)
- [MD operational guardrails](../../../../docs/ops/md-gromacs-operational-pitfalls.md)
- [System package status](../../systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md)
- [Single-rep metric report](analysis/gpr3_r167y_ascr3_rep1_chctrl_metric_analysis_20260720.md)
- `payload_manifest.tsv`

## Referenced by / 被引

- [Project index](../../../../docs/INDEX.md)
- [MD modeling route](../../../../docs/modeling/P0-md-simulation.md)
- [2026-07-20 log](../../../../docs/logs/2026-07-20.md)
- [System package status](../../systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md)
