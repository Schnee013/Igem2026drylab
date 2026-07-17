# docking-repro directory contract

This directory contains the current Hu2024-compatible docking reproduction and
mutant-scan result set. It is an experiment-output tree, not an MD package
authority. MD system packages must promote any selected pose they consume into
their own `experiments/md-simulation/systems/<system>/ligand/` directory.

## Current authority

Use these files for the current docking shortlist and interpretation boundary:

| Role | Path |
|---|---|
| Current ratio report | `experiments/docking-repro/analysis/ratio_channel_report.md` |
| Current pair ranking | `experiments/docking-repro/analysis/ratio_pairings.csv` |
| Current full spectrum | `experiments/docking-repro/analysis/ratio_spectrum.csv` |
| Versioned 2026-05-20 release | `experiments/docking-repro/analysis/releases/gpr3_f_full_20260520_0854/` |
| Refreshed Top mutant IFP output | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/` |
| Current MD shortlist document | `docs/modeling/P0-docking-md-candidate-shortlist.md` |

The `tmp/` directories under IFP result roots are run intermediates. They can be
used as provenance for a promoted package input, but MD package files must not
point to them as active coordinate authorities.

## Promoted MD pose inputs

The current MD input packages consume these promoted system-local pose files:

| System | Promoted pose input | Historical docking source |
|---|---|---|
| `Gpr2_R59C + ASCR18` | `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/Gpr2_R59C_ascr18_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr2_R59C_ascr18_poses.sdf` |
| `Gpr3_R167Y + ASCR3` | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf` |

## Historical and one-off result roots

The following roots are retained as historical method or test evidence unless a
separate source-backed archive/delete pass classifies each one:

| Path class | Boundary |
|---|---|
| `results/wt_singlestage*` | WT redock, 3D-offset, and Gpr3 pose-geometry tests from method repair. |
| `results/ifp_analysis*` | IFP snapshots from different method stages; they are not guaranteed to be supersets of one another. |
| `analysis/pymol_top6/` | Historical visualization material; regenerate separately for the current shortlist if needed. |
| `analysis/pymol_gpr3_review/` | Gpr3 pose-review helper scripts. |
| `mutagenesis/af3_downloads/` | AF3 downloaded structures and job request evidence; do not bulk-delete. |
| `mutagenesis/archive/` | Historical voided or retired mutagenesis evidence. |

## Cleanup performed on 2026-07-16

- Removed 168 ignored `.DS_Store` files under `experiments/docking-repro/`.
- Removed empty result placeholder directories:
  - `experiments/docking-repro/results/interactions/`
  - `experiments/docking-repro/results/poses/`
- Removed empty accidental nested directory:
  - `experiments/experiments/`

No docking result bodies, AF3 structures, PDBQT pose sets, IFP outputs, ratio
tables, PyMOL assets, or historical test result JSON files were deleted in this
pass.

## References / 所引

- `docs/modeling/P0-molecular-docking.md`
- `docs/modeling/P0-docking-md-candidate-shortlist.md`
- `experiments/docking-repro/analysis/ratio_channel_report.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/README.md`

## Referenced by / 被引

- `docs/modeling/P0-molecular-docking.md`
