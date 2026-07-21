# Gpr2 WT/R59C + ASCR18 rep1 ligand-path and dynamic-pocket triage

> Analysis date: 2026-07-19 +0800.
>
> Allowed use: descriptive structural triage of the two completed 200 ns rep1
> trajectories, identification of candidate dynamic-contact regions, and design
> of the next controlled comparison. This report does not establish a unique
> binding pocket, a mutation-causal effect, or a best mutation.

## Question and analysis contract

The analysis asks whether ASCR18 remains near its initial pose, moves to another
receptor-contact region, or shows a sustained detachment trend. Both processed
trajectories were refitted to the WT frame-0 receptor reference with an
equal-weight Kabsch fit on receptor backbone outside residues `250–310`. Direct
contacts use a `4.0 A` receptor-heavy-atom to ligand-heavy-atom cutoff. Early
and late windows are `0–<100 ns` and `100–200 ns`.

The shared driver records the full centroid path, per-residue early/late contact
occupancy, representative frames, input checksums, and three plots under
`ligand_path/`. The processed trajectories already use the accepted
protein/ligand, PBC-corrected analysis route. Smooth, bounded centroid traces
and continuing receptor contacts do not show the discontinuous jumps expected
from an uncorrected periodic-boundary artifact.

The two arms were independently constructed and start with ASCR18 in clearly
different receptor-contact regions:

- WT frame 0: residues `14–17`, `168–181`, and `345–364`.
- R59C frame 0: residues `119`, `122`, `134`, `137`, and `144–149`.

Absolute WT/R59C pocket positions therefore combine starting-pose/construction
differences with any genotype-dependent behavior. They are not a clean
same-pocket mutation comparison.

## Observed ligand movement

| After-100 ns metric | WT rep1 | R59C rep1 | Descriptive reading |
|---|---:|---:|---|
| Ligand-centroid displacement from that arm's frame 0, mean A | 5.518 | 9.824 | R59C explores farther from its own starting position. |
| Direct-contact receptor residues per frame, mean | 8.020 | 3.544 | R59C retains a sparser contact shell. |
| Minimum receptor-ligand distance, mean A | 2.632 | 3.184 | R59C remains near the receptor but with looser direct proximity. |
| Final centroid displacement, A | 4.721 | 8.716 | Both end away from frame 0; R59C remains farther. |

R59C does not show evidence of sustained complete receptor detachment: direct
contacts persist through the trajectory and five receptor residues are within
`4.0 A` in the final frame. Some frames have no `4.0 A` contact, so the current
evidence supports a mobile, sparsely contacted receptor-associated pose rather
than a tightly retained initial pose.

## R59C dynamic-contact region

| Residue | Early occupancy | Late occupancy | Role supported by this rep1 |
|---|---:|---:|---|
| `GLN134` | 88.2% | 93.9% | Strong persistent dynamic anchor candidate. |
| `PHE137` | 78.8% | 88.6% | Strong persistent dynamic anchor candidate. |
| `THR133` | 36.1% | 57.3% | Contact gained during movement; path/gate candidate. |
| `ILE126` | 35.0% | 47.8% | Contact gained during movement; path/gate candidate. |
| `ILE122` | 45.7% | 34.7% | Moderate persistent contact and docking/MD cross-evidence candidate. |
| `VAL119` | 3.0% | 0.0% | Initial/docking contact not retained; last contact at 6.8 ns. |

Residue `59` is absent from the `4.0 A` direct-contact table. In this trajectory,
R59C is therefore not supported as a residue that directly holds ASCR18. Any
R59C effect would more plausibly act indirectly through pocket shape,
side-chain packing, or a longer-range conformational network.

The refreshed docking handoff reports stronger local ASCR18 than ASCR3 contacts
at `VAL119/ILE122`. Dynamic MD separates those two signals: `VAL119` is lost
early, whereas `ILE122` remains intermittently contacted through 200 ns.
`ILE122` is consequently the current first cross-evidence site for validation,
not a demonstrated best mutation site. `GLN134/PHE137` have stronger MD
occupancy, but the present evidence does not show that they are
ASCR18-selective rather than general pocket anchors.

## Can this identify a more reliable pocket?

It can identify a **candidate dynamic binding region** more reliably than one
static docking pose by showing where the ligand repeatedly stays and which
contacts survive over time. For R59C rep1, that region is centered on
`ILE122/ILE126/THR133/GLN134/PHE137`, with `GLN134/PHE137` as the strongest
late-window anchors.

It cannot yet identify a unique true pocket because:

1. WT and R59C started from different ASCR18 contact regions.
2. There is one trajectory per genotype.
3. The current comparison includes ASCR18 but not the matched ASCR3
   selectivity arm.
4. Contact persistence alone does not prove favorable binding free energy or
   receptor signaling competence.

## How to derive a best mutation

A best mutation must optimize the project objective—preferential functional
response to ASCR18—rather than merely maximize one contact. The next evidence
funnel is:

1. **Control the starting system.** Select one credible WT receptor–ASCR18–membrane
   pose, duplicate the complete system, and change only residue 59 for the
   WT/R59C comparison. Keep ligand pose, membrane, water, ions, receptor
   coordinates, and equilibration protocol matched as closely as possible.
2. **Repeat sampling.** Run at least three independent trajectories per arm.
   “Three random seeds” means the same molecular system is simulated three
   times with different randomized initial velocities; it does not mean three
   different mutants. Agreement across repeats reduces the chance that one
   lucky or unlucky trajectory determines the conclusion.
3. **Add the selectivity control.** Apply the same design to ASCR3. A residue
   becomes an ASCR18-selectivity candidate only if its ASCR18 contact/pose
   benefit is reproducible and is not equally gained by ASCR3.
4. **Use a small mechanistic panel.** Start with `ILE122` as the cross-evidence
   site; use an alanine substitution as a loss-of-contact probe and conservative
   hydrophobic substitutions as pocket-volume probes. Use `GLN134/PHE137` as
   anchor controls and `THR133/ILE126` as path/gate controls. Exact substitutions
   should be chosen after matched dual-ligand structural screening rather than
   inferred from occupancy alone.
5. **Reject structurally harmful candidates.** Require preserved receptor
   fold/compactness, acceptable local pocket geometry, and reproducible ligand
   behavior. A mutation that immobilizes ASCR18 while destabilizing the receptor
   is not an improvement.
6. **Confirm experimentally.** Measure ASCR18 and ASCR3 dose-response for each
   construct, including `EC50`, maximum response, basal signal, and
   receptor-expression/membrane-localization controls. The best mutation is the
   one that reproducibly improves the within-receptor ASCR18-versus-ASCR3
   response separation while preserving expression and signaling capacity.

## Current decision

- Dynamic-pocket candidate region: `ILE122/ILE126/THR133/GLN134/PHE137`.
- First cross-evidence validation site: `ILE122`.
- Strongest R59C rep1 dynamic anchors: `GLN134/PHE137`.
- Current interpretation of residue 59: indirect-regulation hypothesis, not a
  direct ASCR18-contact site.
- No best mutation can be declared from the present two single trajectories.
- The next decisive comparison is a same-starting-system, replicated,
  ASCR18/ASCR3 dual-ligand design followed by dose-response and expression
  controls.

## Alignment correction

This analysis exposed a row/column convention error in the shared manual
Kabsch application: `MDAnalysis.analysis.align.rotation_matrix` must be applied
with the transpose to MDAnalysis row-vector coordinates. The common helper and
affected shared consumers were corrected and regression-tested. Regenerating
the canonical ligand RMSD changed the late-window values only slightly and did
not change the WT/R59C qualitative conclusion. The historical 2026-07-09 log is
retained as its dated record; current reports and CSV summaries carry the
corrected values.

## References / 所引

- [Ligand-path metadata](ligand_path/run_metadata.json)
- [Centroid path](ligand_path/centroid_path.csv)
- [Residue contact occupancy](ligand_path/residue_contact_occupancy.csv)
- [Representative frames](ligand_path/representative_frames.csv)
- [Ligand-path run log](ligand_path/run_compare_ligand_paths_20260719.log)
- [WT/R59C matched metric report](gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md)
- [R59C metric report](gpr2_r59c_ascr18_rep1_chctrl_metric_analysis_20260719.md)
- [Docking-to-MD candidate handoff](../../../../../docs/modeling/P0-docking-md-candidate-shortlist.md)
- `../../../analysis/chctrl/compare_ligand_paths.py`
- `../../../../../tests/modeling/test_md_analysis_contracts.py`

## Referenced by / 被引

- [Result-package recovery contract](../README.md)
- [System package status](../../../systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md)
- [2026-07-19 log](../../../../../docs/logs/2026-07-19.md)
- [MD modeling route](../../../../../docs/modeling/P0-md-simulation.md)
- [Project index](../../../../../docs/INDEX.md)
