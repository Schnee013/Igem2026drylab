# Gpr2 WT/R59C + ASCR18 rep1 matched comparison

> Analysis date: 2026-07-19 +0800.
>
> Regenerated: 2026-07-27 from checksum-identified WT and R59C processed
> inputs after the shared equal-weight Kabsch correction.
>
> Allowed use: same-site, same-analysis-contract, matched single-rep exploratory/triage comparison. Population-level genotype inference requires biological replication and a matched starting-system design.

## Comparison contract

WT and R59C were analyzed with the same seven shared drivers, receptor/ligand
selections, readout-residue clusters, after-100 ns window, distance units, and
summary statistics. The `250–310` sensitivity calculation uses the exact
algorithm recorded in `docs/logs/2026-07-16.md`: equal-weight Kabsch refitting
on receptor backbone outside residues 250–310, a mean-of-frame CA
squared-displacement contribution, and ASCR18 heavy-atom RMSD/geometric-centroid
shift in that refitted frame.

Each genotype currently has one 200 ns replicate. Their receptor models,
ligand poses, and system-construction chains were generated independently, so
the observed numerical differences combine genotype, starting-structure/pose,
and single-trajectory variation. The comparison therefore supports structural
triage and follow-up design.

## Shared-driver comparison

| Metric | WT rep1 | R59C rep1 | Same-contract observation |
|---|---:|---:|---|
| Receptor backbone RMSD after 100 ns, mean A | 12.6186 | 10.8299 | Large frame-0-referenced global displacement occurs in both runs. |
| Receptor backbone RMSD at 200 ns, A | 13.1302 | 10.3200 | Both remain far from their own frame-0 receptor reference. |
| Receptor CA Rg after 100 ns, mean A | 27.7110 | 27.5663 | Similar late-window compactness means. |
| ASCR18 heavy-atom RMSD after 100 ns, mean A | 5.63647 | 13.0564 | R59C has the larger descriptive ligand displacement. |
| ASCR18 heavy-atom RMSD after 100 ns, max A | 11.7228 | 16.0695 | R59C has the larger maximum. |
| ASCR18 to all readout COM, mean A | 35.4901 | 14.5045 | Different absolute ligand/readout geometry; initial poses are not a common origin. |
| ASCR18 to primary readout COM, mean A | 38.9451 | 11.1957 | Same caveat as the all-readout COM. |
| ASCR18 to secondary readout COM, mean A | 34.6327 | 16.0967 | Same caveat as the all-readout COM. |
| Top H-bond occupancy | 0.399002 | 0.0997506 | WT top pair: ARG345-ASCR407; R59C top pair: THR133-ASCR407. |
| BSA after 100 ns, mean A^2 | 639.593 | 464.338 | R59C has the lower descriptive buried area. |
| BSA fraction of initial, after-100 mean | 0.745909 | 0.673745 | Both lose buried area relative to their own frame 0. |
| Initial residue contacts | 16 | 8 | Starting contact sets differ in size. |
| Initial-contact retained fraction, after-100 mean | 0.425062 | 0.262438 | R59C retains the smaller fraction of its own initial contact set. |
| Top initial-contact occupancy | 0.977556 | 0.917706 | WT ARG345-ASCR407; R59C GLN134-ASCR407. |
| Receptor CA RMSF, all-residue mean A | 4.15417 | 3.26035 | WT has the larger whole-receptor mean RMSF. |
| Residues 250–310 CA RMSF, mean A | 10.8819 | 7.69672 | The same high-motion region is present in both, larger in WT. |
| Other receptor CA RMSF, mean A | 2.96464 | 2.47595 | R59C is lower by this whole-trajectory RMSF summary. |

## Residues 250–310 sensitivity

| Metric, after 100 ns | WT rep1 | R59C rep1 |
|---|---:|---:|
| Backbone RMSD excluding 250–310, no new fit, mean A | 7.20602560 | 6.98678350 |
| Backbone RMSD after refit outside 250–310, mean A | 5.20458295 | 6.18263496 |
| 250–310 share of receptor CA squared displacement, mean-of-frame % | 71.93235196 | 64.60491357 |
| ASCR18 RMSD after receptor refit, mean A | 7.02045497 | 10.50894595 |
| ASCR18 RMSD after receptor refit, max A | 10.49201125 | 12.96041812 |
| ASCR18 heavy-atom geometric-centroid shift after refit, mean A | 5.51767783 | 9.36249449 |

The regenerated values preserve the 2026-07-16 audit interpretation within the
expected numerical tolerance of the corrected alignment implementation.
Residues 250–310 account for most of the receptor CA squared displacement in
both runs. After
that region is excluded from the fit, R59C has the higher remaining backbone
RMSD mean. This separates three observed components: receptor global motion,
the large local contribution from residues 250–310, and ligand displacement
relative to the remaining receptor backbone.

## Matched single-rep conclusion

- The high receptor global motion recorded for WT also appears in R59C.
- Residues 250–310 are a major contributor in both trajectories; their RMSF
  and squared-displacement share are lower in R59C than WT.
- R59C retains more receptor movement outside that region after common refitting
  (`6.18263 A` versus `5.20458 A`).
- ASCR18 displacement remains evident in R59C and is larger than WT by the
  canonical heavy-atom RMSD, refitted sensitivity RMSD, and geometric-centroid
  shift summaries.
- The GPR analysis contract has no preregistered ligand-RMSD stable/unstable
  cutoff. The values therefore remain descriptive structural-triage evidence.
- One replicate per genotype and independently constructed starting systems
  support a matched single-rep exploratory comparison. Population-level or
  mutation-causal effect claims require replicated, starting-system-controlled
  evidence.
- Ligand-path inspection shows that the two arms started from different
  receptor-contact regions. R59C late-window contacts center on
  `ILE122/ILE126/THR133/GLN134/PHE137`; this is dynamic-pocket triage, not proof
  of a shared WT/R59C pocket.

The shared manual Kabsch application was regenerated after correcting the
rotation-matrix orientation for MDAnalysis row-vector coordinates. The
canonical ligand RMSD values changed only slightly and the comparison
conclusion is unchanged.

## References / 所引

- [R59C metric report](gpr2_r59c_ascr18_rep1_chctrl_metric_analysis_20260719.md)
- [WT metric report](../../gpr2-wt-ascr18/analysis/gpr2_wt_ascr18_rep1_chctrl_metric_analysis_20260709.md)
- [Ligand-path and dynamic-pocket triage](gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md)
- `gpr2_wt_r59c_ascr18_rep1_250_310_sensitivity_20260727.csv`
- `rep1_metrics_summary.csv`
- `../../gpr2-wt-ascr18/analysis/rep1_metrics_summary.csv`
- `../chimeric_systems.gpr2_r59c_ascr18_rep1.json`
- `../../gpr2-wt-ascr18/chimeric_systems.gpr2_wt_ascr18_rep1.json`
- `../../../../../docs/logs/2026-07-16.md`

## Referenced by / 被引

- [Result-package recovery contract](../README.md)
- [System package status](../../../systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md)
- [2026-07-19 log](../../../../../docs/logs/2026-07-19.md)
- [MD modeling route](../../../../../docs/modeling/P0-md-simulation.md)
- [Project index](../../../../../docs/INDEX.md)
