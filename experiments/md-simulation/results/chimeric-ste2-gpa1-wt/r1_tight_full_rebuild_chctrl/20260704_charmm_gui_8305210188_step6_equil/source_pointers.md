# Source Pointers

## Planning And Prototype

| Path | Role |
|---|---|
| `codex/docs/plans/chimeric-gpa1-system-reduction-exploration.md` | Parent reduction exploration plan and chctrl-first gate sequence. |
| `codex/docs/plans/chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md` | Route 1 chctrl tight full-system rebuild plan. |
| `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/command_plan.md` | E2 Package B/C approval package and command record. |
| `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/padding_rule.md` | Current `exploratory` padding rule boundary. |
| `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md` | Public/local atom-count comparison and post-run decision that the current Z-only R1 instantiation is not a compute-saving solution. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/route.json` | Prototype metadata and current gate status. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/build_notes.md` | Human-readable prototype build notes and caveats. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/source_files.sha256` | Checksums for prototype inputs, metadata, and selected result pointers. |

## E2 Result Evidence

| Path | Role |
|---|---|
| `README.md` | Result summary, evidence boundary, and key performance/sanity facts. |
| `logs/gmx_version.log` | Package B E2 GROMACS provenance and corrected sanity timestamps. |
| `logs/gmx_version_production_short.log` | Package C E2 GROMACS provenance. |
| `logs/grompp_step6.*.log` | Package B `grompp` logs with `-maxwarn 0`. |
| `logs/mdrun_step6.*.log` | Package B minimization/equilibration logs and performance lines. |
| `logs/sanity_gmx_dump_step6.6_tpr.log` | E2-side `gmx dump -s` check for final step6.6 `.tpr`. |
| `logs/sanity_gmx_check.log` | E2-side final step6.6 `.xtc` and `.edr` readability checks. |
| `logs/sanity_energy.log` | E2-side final step6.6 energy summary. |
| `logs/grompp_r1_chctrl_short_prod.log` | Package C short-production `grompp` log. |
| `logs/mdrun_r1_chctrl_short_prod.log` | Package C short-production `mdrun` log and performance line. |
| `logs/nvidia_smi_production_short.csv` | Package C GPU utilization samples. |
| `logs/production_short_summary.tsv` | Short production summary emitted on E2. |
| `logs/sanity_short_prod_tpr_dump.log` | E2-side `gmx dump -s` check for short production `.tpr`. |
| `logs/sanity_short_prod_check.log` | E2-side short production `.xtc` and `.edr` readability checks plus `.gro` existence record. |
| `logs/sanity_short_prod_energy.log` | E2-side short production energy summary. |
| `work/step6.6_equilibration.*` | Package B final equilibration outputs. |
| `production_smoke/r1_chctrl_short_prod.*` | Package C short production outputs. |
| `local_download.sha256` | Local checksum manifest after download. |
| `logs/manifest_sha256.txt` | E2-side checksum manifest after Package B. |
| `logs/manifest_sha256_after_production_short.txt` | E2-side checksum manifest after Package C. |

## Ops And Environment

| Path | Role |
|---|---|
| `environments/e2-md-gromacs.md` | Authority for E2 GROMACS command and rule that E2 binary outputs must be processed with the recorded E2 environment. |
| `docs/ops/nkuliulab-e2-cloud-server.md` | E2 shared-server resource, tmux, directory, and cleanup guardrails. |
| `docs/ops/md-gromacs-operational-pitfalls.md` | GROMACS/MD operational pitfalls; relevant here for `.tpr`/trajectory version and output handling. |

## Interpretation Boundary

This result root is chctrl-only. It records build/equilibration and short-production evidence for the exploratory reduced `chctrl` prototype. It is not a compute-saving success claim, not a candidate action, and does not approve Ch-1, Ch-2, or Ch-4 rebuilding, benchmarking, or production.
