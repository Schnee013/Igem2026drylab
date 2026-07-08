# R4 chctrl Contact-Map Feasibility

> Date: 2026-07-06
>
> Status: R4-GAP-05 feasibility spec.
>
> Scope: convert existing `chctrl` atomistic anchors and R4 object-contract arms into a future contact-map requirement. Generated contact maps, topology files, GROMACS command plans, E2 actions, and candidate-transfer rules require a later approved phase.

## Working Conclusion

This feasibility note records what an eventual `chctrl` Go/contact-map layer
would have to contain if R4 is reopened through `docs/INDEX.md`; actual contact
files remain required evidence.

The practical gain is a narrower evidence checklist for a future phase. Any
future approved R4 tool-validation work would have to prove all of the following
before any dry-build package:

- the atomistic reference input is exact and durable;
- the contact generator is source/version-pinned;
- intrachain and receptor-Galpha interchain contacts are separated;
- receptor-Galpha contacts are traceable back to existing `chctrl` anchors;
- chain/model assignment cannot accidentally apply contacts to the wrong molecule type;
- CG-to-AA comparison can recompute the existing atomistic metric family.

## Current Anchors

The anchor table for this file is:

```text
experiments/chimeric-gpa1/literature/r4_chctrl_contact_anchor_spec_20260706.tsv
```

Source-faithful facts used:

| Field | Current repo fact | Pointer |
|---|---|---|
| Chain identity | `PROA` maps to intended Gpa1-WT; `PROB` maps to intended Ste2. | `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md` |
| Gpa1 alpha5/eCT | `PROA` residues `448-472`; 99 atoms / 25 residues in the selection audit. | `selection_audit_report.md` |
| Gpa1 last5 | `PROA` residues `468-472`; 87 atoms / 5 residues in the selection audit. | `selection_audit_report.md` |
| Ste2 interface cluster 1 | `PROB` residues `69-84`; min distance to Gpa1 alpha5 in `step5_input.pdb` = `3.212 A`. | `ste2_interface_geometry_step5.csv` |
| Ste2 interface cluster 2 | `PROB` residues `145-160`; min distance to all Gpa1 = `2.732 A`, but farther from alpha5; keep as broader-interface cluster. | `ste2_interface_geometry_step5.csv`; `selection_audit_report.md` |
| Ste2 interface cluster 3 | `PROB` residues `222-251`; min distance to Gpa1 alpha5 = `3.641 A`, to last5 = `3.233 A`. | `ste2_interface_geometry_step5.csv` |
| Ste2 interface cluster 4 | `PROB` residues `288-304`; min distance to Gpa1 alpha5 = `2.917 A`, to last5 = `2.683 A`. | `ste2_interface_geometry_step5.csv` |
| Initial contact caveat | Contact persistence is partly sensitive to the frame-0 initial contact set; each replicate has 28 initial contacts in the existing audit. | `selection_audit_report.md` |

## Conditional Contact Files

A future R4 dry-build plan would have to name concrete files for each row below
before it could claim an executable contact-map route.

| Required file class | Minimum content | Why it is needed |
|---|---|---|
| Atomistic reference structure | Exact full-system or protein-complex `chctrl` atomistic input, checksum, chain mapping, and residue numbering. | Contact maps cannot be generated from a vague `chctrl` idea or beta2AR tutorial object. |
| Intrachain contact map for Gpa1 | Contacts internal to `PROA`, with generator parameters and excluded-neighbor rule. | Keeps Galpha fold bias separate from receptor-Galpha interface bias. |
| Intrachain contact map for Ste2 | Contacts internal to `PROB`, with generator parameters and excluded-neighbor rule. | Keeps receptor fold bias separate from interface bias. |
| Interchain candidate contact table | Candidate `PROA`-`PROB` contacts, with residue IDs, bead/atom references, reference distance, source anchor, and generator decision. | The interface must be auditable back to current atomistic anchors. |
| R4B arm assignment table | Per-contact assignment to `intra_only`, `weak_interchain`, or `strong_interchain_diagnostic`. | Prevents accidental use of a strong interface clamp as the interpretive route. |
| Exclusion / nonbonded override table | Explicit exclusions or overrides introduced by Go-like contacts. | GoMartini3 extraction records that regular Martini interactions around Go contacts can require exclusions; this must be auditable. |
| Post-conversion metric map | Mapping from CG/AA output back to alpha5/eCT, Ste2 clusters, BSA/SASA, contact persistence, H-bond, COM/orientation, RMSF, and system sanity metrics. | R4 only helps the project if outputs reconnect to atomistic `chctrl` metrics. |

## Generator Parameters That Must Be Recorded

Use the method vocabulary already extracted into R4 records. Chosen defaults
require a later approved tool-validation phase and a pinned generator.

| Parameter | Required record |
|---|---|
| Generator | GoContactMap, GoMartini `ContactMapGenerator`, Yang-style `create_goVirt*`, OLIVES, or another named source. |
| Protein model tool | `martinize2` / vermouth version and command interface if that route is chosen. |
| Contact definition | OV/rCSU or other method, including atom/bead basis. |
| Distance range | Lower/upper cutoff, for example the 0.3-1.1 nm vocabulary from Yang/GoMartini3 records if selected. |
| Sequence/graph exclusion | Neighbor exclusion or graph-distance rule; must be explicit for each chain. |
| Chain/model uniqueness | How `PROA` and `PROB` get distinct molecule/contact assignments. |
| Epsilon policy | Separate `epsilon_intra` and `epsilon_inter` labels or scans; strong interchain bias must be diagnostic-only. |
| Interchain inclusion decision | For each interface contact class, whether it is excluded, weakly biased, or diagnostic-strong. |
| Output topology includes | Names and checksums of generated Go tables, virtual-site definitions, exclusions, and topology include files. |

## Feasible Design Arms

| Arm | Contact-map requirement | Interpretive use |
|---|---|---|
| `R4B-intra-only` | Generate intrachain Gpa1 and Ste2 contacts only; receptor-Galpha interchain candidate table is recorded but not used as bias. | Tests whether the interface drifts when only each protein fold is stabilized. |
| `R4B-weak-interchain` | Add a restricted `PROA`-`PROB` interchain contact set from atomistic anchors, with separately tracked `epsilon_inter`. | Potential future R4 arm only if a dry-build package is separately justified. |
| `R4B-strong-interchain-diagnostic` | Apply stronger interchain contacts only as a clamp diagnostic. | Used to expose overfrozen-interface behavior; not a route for project interpretation. |

## Contact Classes To Preserve Separately

| Contact class | Definition | Default feasibility read |
|---|---|---|
| alpha5/eCT to Ste2 clusters | `PROA 448-472` against Ste2 `69-84`, `222-251`, `288-304`, and broader `145-160`. | Required candidate interface class for any interchain arm. |
| last5 to Ste2 clusters | `PROA 468-472` against the same Ste2 clusters. | Required gross C-terminal orientation class. |
| broader Gpa1 to Ste2 cluster 145-160 | Gpa1 contacts outside alpha5 may contribute to this range. | Keep separate so it is not mislabeled as alpha5-only. |
| intrachain fold contacts | Contacts within `PROA` and within `PROB`. | Required for every arm but not sufficient for interface interpretation. |
| membrane-facing receptor contacts | Receptor contacts near membrane-facing regions. | Must not be confused with receptor-Galpha contacts; membrane/lipid handling is a separate R4 gap. |

## Stop Conditions

This feasibility record would still block any future dry-build plan if any of
these remain true:

| Stop condition | Reason |
|---|---|
| No durable atomistic input payload | A future contact map must cite an exact reference structure and checksum. |
| No generator/source pin | Contact maps created by different tools or parameters are different R4 routes. |
| No separation of intra/interchain contacts | The project cannot interpret interface drift or overbias if these are mixed. |
| No explicit `PROA`/`PROB` mapping | Chain/model collision would make contacts biologically meaningless. |
| No candidate interchain contact table | The future weak-interchain arm would be handwaved. |
| No CG-to-AA route | CG contact retention alone cannot be used as final `chctrl` validation. |
| No post-conversion atomistic metric map | The output would not reconnect to the existing chimeric MD evidence family. |

## Supporting Boundary Pointers

The contact-map side is specified enough for the R4-GAP-05 evidence row.
R4-GAP-04 is recorded in `r4_chctrl_payload_policy_20260706.md`.

The R4 material boundary and supporting validation-design evidence are recorded in:

```text
experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md
experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md
```

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_reopen_gap_queue_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_material_matrix_20260705.tsv`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_cg_to_aa_route_screen_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_local_toolchain_inventory_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_chctrl_payload_policy_20260706.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/ste2_interface_geometry_step5.csv`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/exported_snapshots.csv`

## Referenced by / 被引

- `experiments/chimeric-gpa1/literature/r4_chctrl_contact_anchor_spec_20260706.tsv`
- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
