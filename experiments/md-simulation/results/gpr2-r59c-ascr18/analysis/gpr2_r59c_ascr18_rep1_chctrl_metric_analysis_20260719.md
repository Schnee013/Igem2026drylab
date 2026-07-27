# Gpr2 R59C + ASCR18 rep1 chctrl-metric analysis

> Analysis date: 2026-07-19 +0800.
>
> Regenerated: 2026-07-27 from the checksum-identified processed inputs after
> the shared equal-weight Kabsch correction.
>
> Allowed use: single-rep R59C holo exploratory/triage evidence under the shared GPR analysis contract. Replicated genotype inference requires an expanded replicate design.

## Completion and sanity

- E2 production ran from `2026-07-16T15:48:19+08:00` to `2026-07-19T14:46:34+08:00` and contains the GROMACS main-log `Finished mdrun on rank 0` marker.
- The performance record is `67.635 ns/day` and `0.355 hour/ns`.
- Full-system XTC: 130,638 atoms, 2,001 frames, 100 ps spacing, final frame 200,000 ps.
- EDR: 100,001 frames, 2 ps spacing, final frame 200,000 ps.
- The completion issue scan was empty. Production finalization finished with
  exit `0`; the production and final archive validators historically returned
  `43/43 PASS` and `55/55 PASS` on 2026-07-19.
- E2 GROMACS 2025.4 postprocess generated a 6,438-atom processed trajectory with 2,001 frames through 200,000 ps; the processed manifest returned `11/11 PASS`.
- The 2026-07-27 local audit found 25 currently present final-manifest files and
  all 25 matched; the other 30 listed bodies remain E2-only.

## Reuse route

The analysis reused the seven shared drivers under
`experiments/md-simulation/analysis/chctrl/` with:

```bash
export CHIMERIC_MD_CONFIG=experiments/md-simulation/results/gpr2-r59c-ascr18/chimeric_systems.gpr2_r59c_ascr18_rep1.json
export CHIMERIC_MD_REPS=1
export CHIMERIC_MD_PAYLOAD_ROOT=/Users/roy/Documents/drylab-payloads/experiments/md-simulation/results/gpr2-r59c-ascr18
```

All seven commands exited `0` on 2026-07-27. Their canonical CSV and PNG
outputs are retained under `analysis/`; transient run logs are not promoted to
Git.

## Metric summary

Time-series summaries below use `time_ns >= 100`. H-bond occupancy, top initial
contact occupancy, and RMSF retain their driver-native full-trajectory scope.

| Metric | R59C rep1 result | Direct result |
|---|---:|---|
| Receptor backbone RMSD | 10.8299 A mean; 10.3200 A at 200 ns | `convergence/rmsd_summary.csv` |
| Receptor CA Rg | 27.5663 A mean | `convergence/rg_summary.csv` |
| ASCR18 heavy-atom RMSD | 13.0564 A mean; 16.0695 A max | `selection_rmsd/selection_rmsd.csv` |
| ASCR18 to all readout COM | 14.5045 A mean; 14.2380 A at 200 ns | `com_distance/com.csv` |
| ASCR18 to primary readout COM | 11.1957 A mean; 10.4423 A at 200 ns | `com_distance/com.csv` |
| ASCR18 to secondary readout COM | 16.0967 A mean; 16.0186 A at 200 ns | `com_distance/com.csv` |
| Top H-bond occupancy | 0.0997506; `THR133 -> ASCR407:O6` | `hbond/hbond_summary.csv` |
| BSA | 464.338 A^2 mean; fraction of initial 0.673745 | `bsa/bsa.csv` |
| Initial contact persistence | 8 initial contacts; after-100 mean retained fraction 0.262438 | `contacts/contact_persistence.csv` |
| Top initial contact occupancy | 0.917706; `GLN134-ASCR407` | `contacts/initial_contact_occupancy.csv` |
| Receptor CA RMSF | 406 rows; all-residue mean 3.26035 A | `rmsf/rmsf.csv` |

The post-hoc `250–310` sensitivity calculation used the algorithm recorded on
2026-07-16: 1,379 backbone fit atoms outside residues 250–310, 406 receptor CA,
61 regional CA, 23 ligand heavy atoms, and 1,001 after-100 ns frames. R59C
yielded 7.69672 A mean RMSF in residues 250–310 versus 2.47595 A elsewhere;
the maximum was 12.0025 A at residue 276. The same calculation is tabulated in
`gpr2_wt_r59c_ascr18_rep1_250_310_sensitivity_20260727.csv`.

## Interpretation

R59C rep1 shows substantial receptor global displacement together with marked
ASCR18 heavy-atom displacement. Residues 250–310 contribute strongly to the
global movement, while refitting outside that region leaves a 6.18263 A
backbone RMSD mean and a 10.50895 A ligand RMSD mean. The GPR config contains
no preregistered ligand-RMSD stability cutoff, so these values are structural
inspection signals rather than a categorical stable/unstable call.

Validator and driver evidence closes the rep1 analysis unit. Its scientific use
remains single-rep exploratory/triage interpretation; the matched WT/R59C report
provides the direct common-contract comparison and records the starting-system
and replicate limitations.

The shared manual Kabsch application was regenerated after correcting the
rotation-matrix orientation for MDAnalysis row-vector coordinates. The
late-window ligand RMSD changed only slightly; the interpretation above is
unchanged.

## References / 所引

- [Result-package recovery contract](../README.md)
- `../chimeric_systems.gpr2_r59c_ascr18_rep1.json`
- `rep1_metrics_summary.csv`
- `gpr2_wt_r59c_ascr18_rep1_250_310_sensitivity_20260727.csv`
- `convergence/rmsd_summary.csv`
- `convergence/rg_summary.csv`
- `selection_rmsd/selection_rmsd.csv`
- `hbond/hbond_summary.csv`
- `com_distance/com.csv`
- `rmsf/rmsf.csv`
- `bsa/bsa.csv`
- `contacts/contact_persistence.csv`
- `contacts/initial_contact_occupancy.csv`
- `../../../scripts/e2_run_gpr2_r59c_ascr18_production.sh`
- `../../../scripts/e2_postprocess_gpr2_r59c_ascr18_rep1.sh`
- `../../../../../docs/logs/2026-07-16.md`

## Referenced by / 被引

- [WT/R59C matched report](gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md)
- [Ligand-path and dynamic-pocket triage](gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md)
- [System package status](../../../systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md)
- [2026-07-19 log](../../../../../docs/logs/2026-07-19.md)
- [MD modeling route](../../../../../docs/modeling/P0-md-simulation.md)
- [Project index](../../../../../docs/INDEX.md)
