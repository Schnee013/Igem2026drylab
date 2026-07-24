# Gpr3 R167Y + ASCR3 rep1 chctrl-metric analysis

> Analysis date: 2026-07-20 +0800.
>
> Allowed use: single-rep R167Y holo exploratory/triage evidence under the
> shared GPR analysis contract. Replicated genotype inference requires the
> matched WT arm and an expanded replicate design.

## Completion and sanity

- AutoDL production ran from `2026-07-20T00:03:28+08:00` to
  `2026-07-20T18:13:57+08:00`.
- The completion gate is `PASS / TERMINAL_NORMAL`; the final step is
  100,000,000 and the final time is 200,000 ps.
- The performance record is `264.134 ns/day` and `0.091 hour/ns`.
- Full-system XTC contains 139,708 atoms and 2,001 frames through 200,000 ps.
  The checkpoint also resolves to step 100,000,000 / 200,000 ps.
- The completion issue scan is empty and the 91-row production archive
  validates `91/91 PASS`.
- GROMACS 2025.4 postprocess generated 6,356 processed atoms and 2,001 frames
  through 200,000 ps. The index gate returned `SOLU=6356` and
  `PROA_BACKBONE=1603`, both PASS.

## Reuse route

The analysis reused the seven shared drivers under
`experiments/md-simulation/analysis/chctrl/` with:

```bash
export CHIMERIC_MD_CONFIG=experiments/md-simulation/results/gpr3-r167y-ascr3/chimeric_systems.gpr3_r167y_ascr3_rep1.json
export CHIMERIC_MD_REPS=1
export CHIMERIC_MD_PAYLOAD_ROOT=/Users/roy/Documents/drylab-payloads/experiments/md-simulation/results/gpr3-r167y-ascr3
```

Selection audit resolved:

- receptor: `segid A`, 6,310 atoms / 401 residues;
- ligand: `segid B and resname ASCR`, 46 atoms;
- ligand heavy atoms: 21;
- docking-IFP readout cluster: 15 residues / 265 atoms.

All seven final commands exited `0`. The first BSA attempt used base Python and
failed with `ModuleNotFoundError: No module named 'mdtraj'`. No dependency was
installed; rerunning the same shared driver with the existing `chimeric`
environment exited `0`. Both attempts are preserved in the timestamped run
logs.

The canonical output/content validator returned 45 PASS checks. The analysis
manifest covers 55 files and validates `55/55 PASS`; its SHA256 is
`5b3f6d25b4acfa60f72edfc67f9a57bb1368a6edcfdc245912eb54d05da93a7c`.

## Metric summary

Time-series summaries below use `time_ns >= 100`. H-bond occupancy, initial
contact occupancy, and receptor RMSF retain their driver-native
full-trajectory scope.

| Metric | R167Y rep1 result | Direct result |
|---|---:|---|
| Receptor backbone RMSD | 16.6437 A mean; 17.9288 A max | `convergence/rmsd_summary.csv` |
| Receptor CA Rg | 27.1782 A mean | `convergence/rg_summary.csv` |
| ASCR3 heavy-atom RMSD | 7.2131 A mean; 10.7829 A max | `selection_rmsd/selection_rmsd.csv` |
| ASCR3 to docking-IFP cluster COM | 3.7154 A mean | `com_distance/com.csv` |
| Receptor CA RMSF | 3.8528 A mean; 13.5277 A max | `rmsf/rmsf.csv` |
| BSA fraction of initial | 0.9417 mean; 0.7578 minimum | `bsa/bsa.csv` |
| Top H-bond occupancy | 0.4140; `ARG175:NE-H:HE -> ASCR402:O5` | `hbond/hbond_summary.csv` |
| Initial contact persistence | 9 contacts; after-100 mean retained fraction 0.5666 | `contacts/contact_persistence.csv` |
| Top initial contact occupancy | 1.0; `ARG175-ASCR402` | `contacts/initial_contact_occupancy.csv` |

## Interpretation

The run and analysis gates close the R167Y rep1 execution unit. The trajectory
shows substantial receptor global displacement, while ASCR3 remains close in
COM to the configured docking-IFP cluster and retains a mean BSA fraction near
its initial value over the second half. These are descriptive structural
signals, not a categorical pose-stability or genotype call.

No preregistered ligand-RMSD cutoff is present in the GPR config. The current
evidence level is therefore `single_rep_exploratory_only`, with interpretation
boundary `descriptive_only_no_replicated_genotype_conclusion`. A genotype
comparison requires a completed matched WT arm and replicate design under the
same analysis contract.

## References / 所引

- [Result-package recovery contract](../README.md)
- `../chimeric_systems.gpr3_r167y_ascr3_rep1.json`
- `selection_audit.tsv`
- `run_logs/analysis_attempt3_20260720T101900Z/analysis_input_identity.tsv`
- `run_logs/analysis_attempt3_20260720T101900Z/analysis_validation.tsv`
- `run_logs/analysis_attempt3_20260720T101900Z/analysis_summary.tsv`
- `run_logs/analysis_attempt3_20260720T101900Z/analysis_outputs.sha256`
- `convergence/rmsd_summary.csv`
- `convergence/rg_summary.csv`
- `selection_rmsd/selection_rmsd.csv`
- `hbond/hbond_summary.csv`
- `com_distance/com.csv`
- `rmsf/rmsf.csv`
- `bsa/bsa.csv`
- `contacts/contact_persistence.csv`
- `contacts/initial_contact_occupancy.csv`
- `../../../scripts/finalize_gpr_md_production.sh`
- `../../../scripts/postprocess_gpr_md_rep.sh`
- `../../../../../docs/logs/2026-07-20.md`

## Referenced by / 被引

- [System package status](../../../systems/gpr3-R167Y-ascr3/PACKAGE_STATUS.md)
- [2026-07-20 log](../../../../../docs/logs/2026-07-20.md)
- [MD modeling route](../../../../../docs/modeling/P0-md-simulation.md)
- [Project index](../../../../../docs/INDEX.md)
