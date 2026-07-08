# R4 Decision Package: Chimeric Gpa1 CG Source Gate

> Date: 2026-07-05
>
> Lane: `R4-B design_only_object_contract_draft`
>
> Status: decision package. Build planning requires a later material-boundary approval.

## Project Meaning

The new Yang2024 SI/tutorial plus GoMartini3/OliGoMers/Lopez/Aydin pass changes R4 from "generic Martini may be relevant" into a concrete design question:

Can we write a `chctrl`-first coarse-grained object contract that explicitly controls receptor-Galpha interchain contacts and then returns selected CG snapshots to atomistic interpretation?

Answer recorded on 2026-07-05: **proceed as a design-only object-contract
draft. Build/run routing requires a later material-boundary approval.**

This was useful for iGEM2026 drylab because it prevented another broad Martini
search loop. The follow-up artifact from this decision was one design document.
The historical single-session fallback was to park R4 for 2026 and move global
drylab effort to other priorities through `docs/INDEX.md` if that document left
the simulated object, contact policy, or validation bridge unnamed.

## What The New Sources Add

| Source | Project-useful contribution | Use in R4 |
|---|---|---|
| Yang2024 SI/tutorial | worked Martini 3 + switching Go beta2AR setup, MDP/topology/contact-map vocabulary | receptor-only workflow vocabulary |
| GoMartini3_2025 | `Martinize2 -go`, contact maps, epsilon tuning, inter-protein contacts, chain/model uniqueness | contact-policy vocabulary |
| OliGoMers_2024 | separate intra/intermolecular Go contacts, `epsilon_intra` / `epsilon_inter`, AA RMSF/RMSD/native-contact comparison, overbias warning | practical receptor-Galpha interchain policy analog |
| Lopez2022 | selected CG snapshots, CG-to-AA conversion, stereochemistry checks, short AA relaxation/production, loss-of-interface warning | validation bridge vocabulary |
| Aydin2025 | cheap UCG conformer generation, UCG-to-Martini ML backmapping, GROMACS validation | optional future workflow idea, not immediate route |
| OLIVES_2024 | likely relevant hydrogen-bond native-contact bias method | manual acquisition; not used in this decision |

## Object-Contract Scope

The follow-up object contract has been written at `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`. It contains only a design contract:

1. Simulated object: intact `chctrl` receptor-Galpha membrane complex at CG resolution.
2. Structure-bias model: Martini 3 with explicit Go/contact-bias choice; compare GoMartini3/OliGoMers style handling, leave OLIVES as a manual-acquisition check.
3. Receptor-Galpha contact policy: define included/excluded/weak interchain contacts and an `epsilon_inter` scan; record overfrozen-interface and interface-drift failure modes.
4. Validation bridge: select CG snapshots, backmap/relax to atomistic resolution, fail bad stereochemistry/periodicity/interface-loss cases, then measure atomistic geometry.
5. Comparable metrics: alpha5/eCT contact retention, receptor-Galpha COM/orientation, BSA/SASA, interface residue contacts/H-bonds, junction RMSF, receptor/Galpha RMSD, membrane embedding, and conversion sanity.

This contract contains design requirements only; build commands, E2 commands,
Ch-1/Ch-2/Ch-4 work, and candidate replacement language require later routed
approval.

## Boundary After Decision

The design-only `chctrl` R4 object contract has now been written at `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`.

The follow-up local-only material plan has also been executed. Its decision package is `experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md`.

Historical single-session fallback after that decision: R4 dry-build planning
stays at no-go with the current material set. R4 remains design-only/future
appendix evidence.

2026-07-06 route cleanup: the durable R4 material boundary is
`r4_material_decision_addendum_20260706.md`; `r4_tool_validation_plan_20260706.md`
supplies validation-design evidence. Current project routing starts from
`docs/INDEX.md`.

## References / 所引

- `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.tsv`
- `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `docs/papers/summaries/Yang2024-Switching-Go-Martini-summary.md`
- `docs/logs/2026-07-05.md`
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11391574/fullTextXML`
- `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12105037/fullTextXML`
- `https://doi.org/10.1021/acs.jctc.2c00168`
- `https://doi.org/10.1021/acs.jctc.4c00553`

## Referenced by / 被引

- `docs/logs/2026-07-05.md`
- `experiments/chimeric-gpa1/literature/r4_chctrl_object_contract_20260705.md`
- historical router/domain updates after object-contract drafting:
  `docs/INDEX.md`, `docs/modeling/P0-md-simulation.md`,
  `docs/modeling/P3-chimeric-gprotein.md`
- `codex/docs/plans/chimeric-gpa1-r4-local-dry-build-material-plan.md`
- `experiments/chimeric-gpa1/literature/r4_local_dry_build_decision_package_20260705.md`
- `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`
