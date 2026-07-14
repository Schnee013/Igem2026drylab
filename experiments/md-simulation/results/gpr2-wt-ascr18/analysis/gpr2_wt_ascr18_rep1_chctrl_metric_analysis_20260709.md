# Gpr2 WT + ASCR18 rep1 chctrl-metric analysis

> Original analysis cleanrun: 2026-07-09 00:24-00:31 +0800; shared-driver semantic-contract regeneration: 2026-07-12 +0800 from the same local processed rep1 inputs.
> Scope: reuse the existing chctrl rep1 metric-family drivers on `Gpr2_WT + ASCR18` 200 ns rep1. This is a single WT holo replicate, not a 3-replicate statistical conclusion.

## Completion and sanity

- E2 production did not stop from interruption: `mdrun` started at `2026-07-06T11:03:57+08:00` and finished normally at `2026-07-08 17:10:18 +0800`.
- Final log step/time: `100000000 / 200000 ps`; performance line: `88.717 ns/day`.
- Full XTC check: 132478 atoms, 2001 frames, 100 ps spacing, final frame 200000 ps.
- EDR check: 100001 energy frames, 2 ps spacing, final energy frame 200000 ps.
- Issue scan only matched CUDA/GROMACS environment metadata lines; no fatal error, LINCS warning, NaN, killed/OOM, or segmentation evidence was found in the archived scan.
- GPU sampler shows shared-resource overlap during the run: max observed GPU memory `60518 MiB`, with 1156 samples above 10000 MiB. This supports delayed throughput, not an interrupted MD.

## Reuse route

- Existing chctrl drivers were reused from `experiments/md-simulation/analysis/chctrl/` with `CHIMERIC_MD_CONFIG=experiments/md-simulation/results/gpr2-wt-ascr18/chimeric_systems.gpr2_wt_ascr18_rep1.json` and `CHIMERIC_MD_REPS=1`.
- E2-side GROMACS 2025.4 generated `processed/rep1/protein_ref.pdb` and `processed/rep1/prod_protein.xtc` from the `SOLU` group. Here `SOLU` means Gpr2 receptor plus ASCR18 ligand.
- The `selection_rmsd/` output directory is the generic chctrl-family RMSD slot. In this GPR receptor-ligand context, it means ASCR18 heavy-atom RMSD after Gpr2/SOLU backbone fitting.
- H-bond, BSA, and contacts are Gpr2-ASCR18 receptor-ligand measurements. COM distance uses configured Gpr2 readout-residue clusters.
- The GPR config deliberately defines no ligand-RMSD, BSA-retention, contact-retention, or H-bond occupancy interpretation cutoff. Those outputs are descriptive and must not inherit the chctrl alpha5/interface operational heuristics.

## Metric summary

| metric | result | interpretation |
|---|---:|---|
| Gpr2 backbone RMSD after 100 ns | 12.6186 A mean; 13.1302 A at 200 ns | Frame-0-referenced receptor displacement; inspect structures before treating this single rep as a stable baseline. |
| Gpr2 CA Rg after 100 ns | 27.711 A mean | Compactness trace available in `convergence/rg_summary.csv`. |
| ASCR18 heavy-atom RMSD after 100 ns | 5.63561 A mean; 11.7193 A max | Descriptive frame-0-referenced displacement; no ligand-specific interpretation threshold is configured. |
| ASCR18 to all readout COM | 35.4901 A mean; 36.0808 A at 200 ns | Descriptive COM series for the configured readout cluster; no categorical cutoff is configured. |
| ASCR18 to primary readout COM | 38.9451 A mean | Primary residues: 59,119,122,138. |
| ASCR18 to secondary readout COM | 34.6327 A mean | Secondary residues: 115,134,143–148,150–151. |
| Top H-bond occupancy | 0.399002 | A:ARG345:NH2-H:HH21 -> B:ASCR407:O6; geometry 3.0 A / 150 deg; stride 5 |
| BSA after 100 ns | 639.593 A^2 mean; fraction 0.745909 | Descriptive relative to frame 0; no GPR-specific retention threshold is configured. |
| Initial contact persistence after 100 ns | 0.425062 retained fraction | 16.0 initial residue contacts at 4.0 A; top contact occupancy 0.977556; no GPR-specific retention threshold is configured. |
| RMSF | 406.0 CA rows | Baseline RMSF generated; no region-specific RMSF interpretation threshold is configured. |

## Bottom line

This rep completed normally and the chctrl metric-family analysis is complete. Relative to the frame-0 reference, the single rep yields the receptor-backbone and ASCR18 heavy-atom displacement values reported above, together with lower late-window BSA fraction and initial-contact retention values. Because no GPR-specific cutoff is configured, these numbers are structural-inspection triggers rather than a categorical classification. Do not use this rep alone as a stable or unstable WT holo conclusion, or as a matched-mutant baseline, before structural inspection and matched analysis.

## References / 所引

- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/final_mdrun_markers.txt`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/final_step_time.txt`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/sanity_rep1_xtc_check.log`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/sanity_rep1_edr_check.log`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/mdrun_issue_scan.log`
- `experiments/md-simulation/results/gpr2-wt-ascr18/raw/rep1/logs/nvidia_smi_mdrun_sampler.csv`
- `experiments/md-simulation/results/gpr2-wt-ascr18/processed/rep1/processing_summary.tsv`
- `experiments/md-simulation/results/gpr2-wt-ascr18/chimeric_systems.gpr2_wt_ascr18_rep1.json`
- `experiments/md-simulation/analysis/chctrl/analyze_convergence.py`
- `experiments/md-simulation/analysis/chctrl/analyze_selection_rmsd.py`
- `experiments/md-simulation/analysis/chctrl/analyze_hbond.py`
- `experiments/md-simulation/analysis/chctrl/analyze_com_distance.py`
- `experiments/md-simulation/analysis/chctrl/analyze_rmsf.py`
- `experiments/md-simulation/analysis/chctrl/analyze_bsa.py`
- `experiments/md-simulation/analysis/chctrl/analyze_contacts.py`

## Referenced by / 被引

- `docs/logs/2026-07-09.md`.
- `docs/INDEX.md`.
- `docs/modeling/P0-md-simulation.md`.
