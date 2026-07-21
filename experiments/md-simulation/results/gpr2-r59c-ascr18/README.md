# Gpr2 R59C + ASCR18 rep1 result-package recovery contract

## Scope and status

This directory is the Git-visible recovery and analysis entry for the
validator-accepted `Gpr2_R59C + ASCR18` 200 ns production rep1 on E2.

| Stage | Verified result | Evidence |
|---|---|---|
| Physical production | `finished`; 130,638 atoms; XTC 2,001 frames and EDR 100,001 frames, both ending at 200,000 ps | external `logs/production/gmx_check_production_{xtc,edr}.log`; GROMACS main-log completion/performance markers |
| Audit finalization | `TERMINAL_NORMAL`; finished `2026-07-19T21:39:21+08:00`; finalizer exit `0`; production archive `43/43 PASS` | external `logs/production/run_state_events.tsv`, derived `terminal_status.tsv`, `finalizer_exit_code.tsv`, and `production_archive.sha256` |
| Postprocess | `finished 2026-07-19T21:41:09+08:00`; 6,438 atoms; 2,001 frames ending at 200,000 ps | external `processed/rep1/terminal_status.tsv`, `gmx_check_protein.txt`, and `SHA256SUMS_processed_rep1.txt` |
| Final archive | `55/55 PASS` | [Git-visible final manifest](../../archive-router/gpr2-r59c-ascr18_200ns-rep1_20260716_archive.sha256) |
| Seven-driver analysis | seven shared `chctrl` drivers exited `0` | `analysis/run_logs/` and [R59C metric report](analysis/gpr2_r59c_ascr18_rep1_chctrl_metric_analysis_20260719.md) |
| Matched comparison | WT/R59C same-contract single-rep comparison complete | [matched report](analysis/gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md) |
| Ligand-path / dynamic-pocket triage | complete; descriptive only; WT/R59C starting contact regions differ | [ligand-path report](analysis/gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md) and `analysis/ligand_path/` |

The finalizer's execution surface is process/file/endpoint/marker/issue
validation plus summary, archive, and terminal-status promotion.

The ligand-path report identifies `ILE122/ILE126/THR133/GLN134/PHE137` as the
R59C rep1 dynamic-contact region and `ILE122` as the first docking/MD
cross-evidence validation site. It does not promote any residue to a best
mutation.

## Recovery route

The compact processed payload and necessary run evidence were restored outside
the Git worktree at:

```text
/Users/roy/Documents/drylab-payloads/experiments/md-simulation/results/gpr2-r59c-ascr18/
├── final_archive.sha256
├── production_archive.sha256
├── logs/production/
└── processed/rep1/
```

The E2 archive authority remains:

```text
/ifs1/User/dengwei/igem/md-simulation/gpr2_r59c_ascr18_rep1_20260716
```

Validate the full E2 run-root layout with:

```bash
sha256sum -c /absolute/path/to/drylab/experiments/md-simulation/archive-router/gpr2-r59c-ascr18_200ns-rep1_20260716_archive.sha256
```

For local analysis, set:

```bash
export CHIMERIC_MD_CONFIG=experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json
export CHIMERIC_MD_REPS=1
export CHIMERIC_MD_PAYLOAD_ROOT=/Users/roy/Documents/drylab-payloads/experiments/md-simulation/results/gpr2-r59c-ascr18
```

The two direct analysis inputs are:

- `processed/rep1/prod_protein.xtc`: SHA256 `be38397e82abc3db630ca4c6cf3cadfce6f5e9edbf2b93fe9138a15443962438`
- `processed/rep1/protein_ref.pdb`: SHA256 `86834a671ec0d22661b48f52e54792a5845d31d88d2606f01f990f4189d76f96`

## Producer and consumer chain

E2 GROMACS 2025.4 produced the 200 ns full-system trajectory. The canonical
postprocess script used the production TPR/XTC and package-local index to create
the 6,438-atom `SOLU` trajectory and reference. The configured shared driver
family consumed those processed files and wrote canonical analysis outputs
under `analysis/` in this repository. The shared ligand-path driver consumed
the same validated processed inputs.

## Tracking classification

- Track in Git: this README, `payload_manifest.tsv`, analysis config, canonical
  CSV/PNG/Markdown outputs, scripts, tests, and the archive-router manifest.
- Keep in E2 or external storage: raw TPR/CPT/GRO/XTC/EDR, processed trajectory
  bodies, full runtime logs, and machine/runtime snapshots.

## References / 所引

- [Archive router](../../archive-router/README.md)
- [Payload tracking policy](../../../../docs/ops/payload-tracking-policy.md)
- [MD operational guardrails](../../../../docs/ops/md-gromacs-operational-pitfalls.md)
- [System package status](../../systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md)
- [R59C metric report](analysis/gpr2_r59c_ascr18_rep1_chctrl_metric_analysis_20260719.md)
- [WT/R59C matched report](analysis/gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md)
- [Ligand-path and dynamic-pocket triage](analysis/gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md)
- `payload_manifest.tsv`

## Referenced by / 被引

- [Project index](../../../../docs/INDEX.md)
- [MD modeling route](../../../../docs/modeling/P0-md-simulation.md)
- [2026-07-19 log](../../../../docs/logs/2026-07-19.md)
- [System package status](../../systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md)
