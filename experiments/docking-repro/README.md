# docking-repro historical directory contract

This directory is a read-only historical record of the docking reproduction and
mutant-scan work completed in April-May 2026. It preserves the method, result,
and provenance files needed to interpret the historical analysis and the
starting coordinates used by completed MD systems.

Current project routing is maintained in `docs/INDEX.md`. Historical method
and evidence boundaries are maintained in
`docs/modeling/P0-molecular-docking.md`.

## Retained tree

The following roots are retained as historical evidence:

| Root | Historical role |
|---|---|
| `analysis/` | Ratio, spectrum, release, and visualization artifacts |
| `logs/` | Runtime logs retained by the historical experiment tree |
| `mutagenesis/` | Historical mutation inventories, structures, and preparation evidence |
| `prepared/` | Prepared historical receptor and ligand inputs |
| `results/` | Docking and IFP result bodies |
| `slurm/` | Historical Slurm execution material |
| `temp/docking-results/` | Historical docking delivery copy outside this directory |

The directory keeps the April-May source/result lineage intact. Runtime
reproducibility requires independent environment validation.

## Historical analysis pointers

| Role | Path |
|---|---|
| Ratio report | `experiments/docking-repro/analysis/ratio_channel_report.md` |
| Pair ranking | `experiments/docking-repro/analysis/ratio_pairings.csv` |
| Full spectrum | `experiments/docking-repro/analysis/ratio_spectrum.csv` |
| Versioned 2026-05-20 release | `experiments/docking-repro/analysis/releases/gpr3_f_full_20260520_0854/` |
| Mutant IFP output | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/` |
| Historical MD selection snapshot | `docs/modeling/P0-docking-md-candidate-shortlist.md` |

## Promoted MD pose inputs

Completed MD packages own the exact pose bodies they consumed. The docking
paths below provide provenance for those promoted system-local inputs.

| System | Promoted pose input | Historical docking source |
|---|---|---|
| `Gpr2_R59C + ASCR18` | `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/Gpr2_R59C_ascr18_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr2_R59C_ascr18_poses.sdf` |
| `Gpr3_R167Y + ASCR3` | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf` |

The `tmp/` directories under retained IFP result roots are provenance for
these historical promotions. MD package consumers use the system-local ligand
files as their coordinate authority.

## Historical result-root boundaries

| Path class | Allowed use |
|---|---|
| `results/wt_singlestage*` | Trace WT redock and pose-geometry method work |
| `results/ifp_analysis*` | Trace IFP snapshots from different historical stages |
| `analysis/pymol_top6/` | Historical visualization material |
| `analysis/pymol_gpr3_review/` | Historical Gpr3 pose-review helpers |
| `mutagenesis/af3_downloads/` | Preserve AF3 structure and request provenance used by historical work |
| `mutagenesis/archive/` | Preserve voided or retired mutagenesis evidence |

## Evidence limits

- Historical Vina scores and ratio outputs support within-workflow ranking only.
- Static IFP outputs support interaction hypotheses.
- Binding constants, activation parameters, and functional conclusions require
  independent evidence.
- Result files remain the numerical authority; this README only defines
  directory ownership and allowed use.

## References / 所引

- `docs/modeling/P0-molecular-docking.md`
- `docs/modeling/P0-docking-md-candidate-shortlist.md`
- `experiments/docking-repro/analysis/ratio_channel_report.md`
- `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/README.md`
- `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/README.md`

## Referenced by / 被引

- `docs/modeling/P0-molecular-docking.md`
