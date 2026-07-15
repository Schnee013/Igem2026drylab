# R4 chctrl Design-Only Object Contract

> Date: 2026-07-05
>
> Status: `design_only_object_contract`
>
> Scope: `chctrl`-first coarse-grained / multiscale design contract for the chimeric Gpa1 compute-triage route.
>
> This contract is design-only. GROMACS commands, E2 approval, build protocol, and Ch-1/Ch-2/Ch-4 candidate-transfer decisions each require separate current work orders and evidence gates.

## Project Use

This file records the design-only contract produced by the R4 source pass: what
an R4 `chctrl` coarse-grained object would have to be if the lane is reopened.

The useful outcome is a named object, a named receptor-Galpha contact policy, and a named route for returning any CG result to atomistic `chctrl` interpretation. Current use is design evidence; execution requires those fields to be satisfied later in a dry-build plan.

## Source-Backed Design Vocabulary

| Field | Source-backed vocabulary | Project use |
|---|---|---|
| State-pair / Go-Martini workflow | Yang2024 SI/tutorial: Martini 3, state-specific topology, `martinize2`, OV/rCSU contacts, `create_goVirt*`, POPC/water/ion examples, relaxation before topology switching | Vocabulary only; beta2AR receptor-only tutorial cannot be copied as a `chctrl` build |
| Protein-complex Go contact policy | GoMartini3_2025: contact maps, `Martinize2 -go`, epsilon tuning, inter-protein contacts, chain/model uniqueness | Forces R4 to name receptor-Galpha interchain contacts explicitly |
| Interchain overbias risk | OliGoMers_2024: separate intra/intermolecular Go contacts, `epsilon_intra` / `epsilon_inter`, AA RMSF/RMSD/native-contact comparison, overstrong interchain bias risk | Supplies the practical weak/interchain-bias design language |
| CG-to-AA bridge | Lopez2022: selected CG snapshots, conversion, stereochemistry checks, AA relaxation/short production, loss-of-interface warning | Treats CG as snapshot generation until atomistic checks pass |
| Optional future workflow | Aydin2025: cheap UCG conformer generation, UCG-to-Martini backmapping, GROMACS validation loop | Future language only; too heavy for immediate chimeric route |
| Ste2/Gpa1 biology context | Mohanty2025 and Cevheroglu2017 in repo records | Interface context only; not a CG route source |

## Simulated Object

The R4 object is:

```text
complete chctrl Ste2-Gpa1 membrane complex at coarse-grained resolution
```

Required object fields for any later dry-build plan:

| Field | Contract |
|---|---|
| Positive-control identity | `chctrl` only: Ste2 receptor plus WT yeast Gpa1/Galpha positive control |
| Chain identity | Preserve current atomistic audit mapping: `PROA` = Gpa1-WT, `PROB` = Ste2 |
| Protein scope | Full receptor-Galpha complex; receptor-only beta2AR and interface-only subsystems are separate evidence classes |
| Membrane scope | Full membrane/solvent/ion context retained at CG resolution; Yang beta2AR box/lipid counts and Sahoo TM-dimer box dimensions require separate transfer decisions |
| Candidate scope | `chctrl` only; Ch-1/Ch-2/Ch-4 and mutant/candidate applications require separate contracts |
| Starting atomistic anchor | Existing `chctrl` structure/trajectory records and selection audit; exact input snapshot must be chosen in a later dry-build plan |

## State and Structure-Bias Policy

Yang2024 switching setup is vocabulary evidence only. A future R4 review must
choose an explicit state-bias design for `chctrl`; a source-backed Ste2-Gpa1 CG
state-pair route remains a required gate.

For a later dry-build plan, use one of these design arms:

| Arm | Meaning | Use |
|---|---|---|
| `R4B-intra-only` | Apply structure bias within each protein chain only; receptor-Galpha interchain contacts are left free | Negative/control arm for interface drift |
| `R4B-weak-interchain` | Include a restricted receptor-Galpha interchain contact set with separately tracked `epsilon_inter` scan | Primary design arm if R4 continues |
| `R4B-strong-interchain-diagnostic` | Deliberately stronger interchain bias | Diagnostic for overfrozen interfaces only; not an interpretive route |

Required structure-bias fields:

- Martini protein model version and source.
- Contact generator and contact-map source.
- Contact distance range and graph/sequence-distance exclusion rule.
- Separate intra-chain and receptor-Galpha interchain contact files or tables.
- Separate `epsilon_intra` and `epsilon_inter` values or scan levels.
- Chain/model uniqueness policy so receptor and Galpha contacts cannot be accidentally shared across molecule types.
- Explicit statement of whether receptor-Galpha contacts are included, excluded, weakened, or diagnostic-only.

## Receptor-Galpha Contact Policy

The contact policy must be derived from current `chctrl` atomistic selections and then checked after CG-to-AA conversion. It cannot be invented from Yang2024 beta2AR.

Atomistic selection anchors already available in the repo:

| Selection anchor | Source in repo | Use in R4 |
|---|---|---|
| Gpa1 alpha5/eCT | `PROA` residues `448-472` in selection audit | Primary Galpha interface contact anchor |
| Gpa1 last5 | `PROA` residues `468-472` in selection audit | C-terminal proximity / gross orientation anchor |
| Ste2 interface clusters | `PROB` ranges `69:84`, `145:160`, `222:251`, `288:304` in selection audit | Receptor-side contact clusters; `145:160` should stay broader-interface, not alpha5-only |
| Existing atomistic contact set | selection audit frame-0 and snapshot metrics | Initial contact retention comparison, with frame-0 caveat preserved |
| Existing chctrl early gate | 2026-06-02 rep1 early-gate report | Short-horizon atomistic comparison target |

Primary R4 contact-policy draft:

1. Keep all intra-protein structure bias explicit and chain-specific.
2. Generate a receptor-Galpha interchain contact candidate set from the atomistic `chctrl` interface anchors above.
3. Split interchain contacts from intrachain contacts.
4. Use `R4B-intra-only` and `R4B-weak-interchain` as design comparison arms if a dry-build plan is ever written.
5. Treat any strong interchain bias as diagnostic for overfreezing; project interpretation requires successful CG-to-AA validation and atomistic comparison.

Failure modes to record before any build decision:

| Failure mode | Meaning |
|---|---|
| Interface drift | `R4B-intra-only` loses receptor-Galpha orientation or alpha5/eCT contact before atomistic comparison |
| Overfrozen interface | `R4B-weak-interchain` or stronger bias suppresses real interface rearrangement and becomes a geometry clamp |
| Contact-map ambiguity | OV/rCSU or equivalent contact generation yields receptor-Galpha contacts that do not map cleanly to current atomistic selections |
| Chain/model collision | Go contacts are accidentally applied to the wrong molecule type or shared across molecules |

## CG-to-AA Validation Gate

R4 output is only interpretable if selected CG snapshots can return to atomistic checks.

Required validation gate for any later build plan:

| Gate | Required check |
|---|---|
| Snapshot selection | Select CG snapshots by receptor-Galpha orientation, alpha5/eCT displacement, contact retention, membrane embedding, and absence of gross periodic artifacts |
| Conversion sanity | Reject failed stereochemistry, bad periodicity, chain breaks, residue/chain identity mismatch, and obvious membrane/protein overlap |
| AA relaxation | Run only after a separate approved plan defines the local or remote environment; this contract does not provide commands |
| Interface-loss check | Confirm that favorable receptor-Galpha contacts are not lost during conversion/relaxation |
| Atomistic comparison | Recompute the existing `chctrl` metrics on backmapped/relaxed AA snapshots before any project interpretation |

CG-only outputs can rank or triage conformers. Chimeric Galpha interface-stability validation requires CG-to-AA conversion, AA relaxation, and atomistic metric recomputation.

## Comparable Atomistic Metrics

Any later R4 dry-build or analysis plan must reconnect to the existing atomistic `chctrl` metric family instead of introducing a separate CG-only story.

| Metric family | Atomistic comparison target | Current caveat |
|---|---|---|
| alpha5/eCT iRMSD | P0 §4.4 metric and selection audit alpha5 reproduction/alternative fits | Project operational bands, not literature thresholds |
| BSA/SASA | FreeSASA-style interface BSA/SASA after CG-to-AA conversion | Existing 20% retention cutoff remains heuristic |
| Contact persistence | Heavy-atom contact map against current atomistic contact sets | Frame-0 contact set sensitivity must be preserved |
| H-bond occupancy | MDAnalysis-style geometry on AA structures | Reporting threshold remains heuristic |
| COM/orientation | Ste2 interface clusters versus Gpa1 C-terminal/alpha5 region | Descriptive gross-separation metric, not a universal cutoff |
| RMSF | Gpa1 alpha5/eCT and future chimera junction regions | `chctrl` has no junction threshold; candidate use would require a later decision |
| Membrane/system sanity | membrane embedding, water/ion sanity, periodicity, compactness | Must use full-system evidence if a build ever occurs |
| Optional MM-PBSA | AA-only, qualitative ranking at most | Not meaningful on raw CG output |

## Conditional Go / No-Go For Later R4 Work

At the time this contract was written, R4 could only advance to a local
dry-build planning document if that next document could name:

- exact input atomistic snapshot(s);
- exact Martini/protein-bias toolchain and versions;
- exact receptor-Galpha interchain-contact generation policy;
- exact dry-build checks for chain identity, topology includes, contact-map assignment, membrane/ion sanity, and metric recomputation;
- exact stop condition before any E2 or candidate work.

The local material decision is recorded at
`experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md`.
It records supporting design evidence only; R4 dry-build planning requires the later material-boundary decision.

2026-07-06 route cleanup: this object contract supplies supporting design
evidence. The R4 material boundary is recorded in
`r4_material_decision_addendum_20260706.md`; `r4_tool_validation_plan_20260706.md`
supplies validation-design evidence. Current project routing starts from
`docs/INDEX.md`.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P3-chimeric-gprotein.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/chctrl_phase_C5_batch1_summary.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`
- `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/early_gate_report.md`
- `docs/logs/2026-07-05.md`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-md-simulation.md`
- `docs/modeling/P3-chimeric-gprotein.md`
- `experiments/chimeric-gpa1/literature/r4_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- `codex/docs/plans/chimeric-gpa1-r4-local-dry-build-material-plan.md`
- `docs/logs/2026-07-05.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
- `experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md`
