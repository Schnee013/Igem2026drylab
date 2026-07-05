# Chimeric System Reduction Protocol Matrix

> Created: 2026-07-03
>
> Scope: first draft for `codex/docs/plans/chimeric-gpa1-system-reduction-exploration.md`.
>
> Execution boundary: no E2 run is approved by this file. Any remote `grompp`, smoke, benchmark, or production command requires explicit approval with command, run directory, expected duration, and resource profile.
>
> E2 output boundary: any future E2-produced GROMACS binary outputs must be checked, converted, preprocessed, and evidence-analyzed with the recorded E2 GROMACS environment for that run. Current authority: `environments/e2-md-gromacs.md`.

## Inventory-Derived Starting Point

The four prepared systems show that candidate overhead is mainly solvent and membrane size, not protein atoms:

| Candidate vs chctrl | Total atom delta | Water atom delta | Lipid atom delta | Protein atom delta | Initial implication |
|---|---:|---:|---:|---:|---|
| Ch-1 `chimeric-gpr3-aogpa2-c37` | +65,022 | +45,435 | +19,966 | -468 | Route 1 should target avoidable water/XY membrane padding first. |
| Ch-2 `chimeric-gpr3-aogpa2-c15` | +102,111 | +82,581 | +19,832 | -459 | Route 1 has larger possible savings, but Ch-2 carries an EM caveat. |
| Ch-4 `chimeric-gpr2-aogpa2-c10` | +107,020 | +87,390 | +19,832 | -381 | Route 1 has larger possible savings, but Ch-4 has early EM LINCS-warning provenance. |

The seven current interface metrics mostly consume protein-only selections after trajectory preprocessing, but physical sanity checks still require membrane, solvent, ions, box, temperature, and pressure traces. Therefore, deleting membrane/solvent context can only create screening or mechanism-support evidence unless a later decision changes the evidence role.

## Universal Prototype Rule

All reduction or restraint routes must be prototyped on `chctrl` first. The first benchmark object is the reduced or restrained `chctrl` variant, not Ch-1/Ch-2/Ch-4.

Rationale: `chctrl` is the positive-control system with existing control evidence, so it can be compared against existing E2 chctrl rep1 early-gate evidence and historical control boundaries before any rule is transferred to candidates. Only after a `chctrl` build, smoke test, short benchmark, and physical sanity gate pass may the identical reduction/restraint rule be applied to Ch-1/Ch-2/Ch-4. Candidate application must preserve the same route definition; candidate-specific tuning would create a new route and require a new benchmark.

## Route Hypotheses

| Route ID | Working hypothesis | Immediate falsifier / downgrade trigger |
|---|---|---|
| R1-tight-full-rebuild | The candidate systems may contain avoidable membrane and water padding; keeping the complete protein-membrane-solvent object while tightening box/padding could lower cost only if XY/membrane or substantial solvent counts fall without changing the evidence class. Current `chctrl` job `8305210188` is Z-only and does not show enough atom-count reduction to solve compute pressure. | `chctrl` reduced rebuild shows PBC image artifacts, Galpha dehydration, membrane distortion, pressure-coupling instability, metric drift inconsistent with existing control evidence, or atom-count reduction too small to matter operationally. |
| R2-layered-restraints-full-system | Early instability or noisy relaxation may be dominated by distal scaffold motions rather than the interface itself; layered restraints could focus early screening on the receptor-Galpha interface. | Restraints artificially preserve contacts, require route-specific force tuning, fail release, or do not reduce failed relaxation/early-screening time on `chctrl`. |
| R3-interface-only-subsystem | Local interface chemistry may be testable in a small capped subsystem, providing mechanistic support for alpha5/eCT or chimeric-junction contacts. | Loss of membrane/domain context makes geometry restraint-dominated or results cannot be mapped back to full-system metrics. |
| R4-coarse-grained-multiscale | A CG whole-complex model may cheaply triage large-scale stability and sampling before atomistic confirmation. | CG parameterization or elastic-network choices erase alpha5/chimeric-junction contact detail, or backmapped atomistic structures fail comparison to `chctrl`. |

## Route Matrix

| Route ID | Exact system object | Retained / deleted / restrained selections | MDP or build changes | Expected evidence class | Expected compute benefit | Main build risks | Required source support | Benchmark command plan |
|---|---|---|---|---|---|---|---|---|
| R1-tight-full-rebuild | Intact receptor-Galpha complex in explicit POPC, water, and ions; rebuild reduced `chctrl` first, then apply the same accepted padding rule to candidates only after `chctrl` passes | Retain all protein atoms, POPC, explicit solvent, ions; reduce avoidable XY/Z padding only if no protein-image artifact; no deletion of Galpha domains | Rebuild with CHARMM-GUI or a scripted equivalent; keep semi-isotropic pressure coupling and CHARMM-family force-field consistency; regenerate `topol.top`, `index.ndx`, `step6.6.gro`, `step6.6.tpr`, checksums | `candidate_replacement` only after new source-backed decision and `chctrl` benchmark; current Z-only instantiation is exploratory evidence only | Current Z-only instantiation is insufficient (`-6776` atoms / `-2.57%`); meaningful savings would require XY/membrane-footprint reduction or a different route | PBC image interaction, insufficient Galpha hydration, distorted membrane relaxation, broken pressure coupling assumptions, and low operational benefit if only Z water changes | S02/S03/S06/S09/S11 plus CHARMM-GUI or builder documentation for padding/defaults; no current source gives a project-specific minimum box | User-approved E2 Package B/C completed for exploratory reduced `chctrl`: step6 equilibration and 100 ps short production evidence are in `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/`. Public atom-count comparison and the Z-only downgrade are in `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md`. Any next E2 step or candidate action requires a new approval package. |
| R2-layered-restraints-full-system | Current full atom-count `chctrl` system first; later candidates only if `chctrl` restraint behavior is physically sane under the same restraint rule | Free or weakly restrained: receptor intracellular loops, Galpha alpha5/eCT, chimeric junction, nearby interface residues. Moderate restraints: receptor TM scaffold and Galpha Ras-like scaffold outside immediate interface. Strong temporary restraints, if any, limited to equilibration and released before interpretation | Add source-backed position/distance restraint files and route-specific MDP includes; preserve atom count and production physics; version generated restraint selections | `screening_only` or stabilization protocol unless a later decision upgrades it; not an atom-count reduction | Does not reduce per-ns cost; may reduce failed relaxation or required early-screening time | Artificially preserving an unstable interface; force constants/release schedule becoming hidden assumptions; selection mismatch across systems | S07/S08/S09/S10/S12/S13 plus direct/close GPCR-Galpha sources S01/S03 for evidence boundaries; force constants still pending extraction | STOP before E2. Build a route-specific `chctrl` restraint file and run `grompp` only after source extraction and approval. Benchmark order: `chctrl` smoke -> `chctrl` short benchmark -> candidate smoke only if `chctrl` passes under the unchanged rule. |
| R3-interface-only-subsystem | Extracted `chctrl` receptor intracellular interface fragments plus Galpha alpha5/eCT, with caps/restraints; candidate fragments only after `chctrl` subsystem behavior is interpretable | Delete membrane, most receptor scaffold, Galpha domains outside local interface, water/ions as appropriate to a local subsystem | New topology/build workflow required; not a simple modification of current CHARMM-GUI systems | `supporting_mechanism_only` unless a later source-backed decision upgrades it | Large atom-count reduction possible | Geometry becomes restraint-dominated; loss of membrane and domain context; false-positive stability | No direct support yet; requires literature specifically validating local interface subsystem for GPCR-Galpha questions | Not built in this phase. If revived, build `chctrl` subsystem first and compare only mechanism-level observables before candidate extraction. |
| R4-coarse-grained-multiscale | Martini or comparable CG `chctrl` GPCR-Galpha complex first, with optional atomistic backmapping; candidate CG only after `chctrl` CG/backmapped behavior is acceptable | Retain whole complex at CG resolution; atomistic details removed during CG phase | Separate CG parameterization, elastic-network/structure-bias decision, backmapping workflow | `screening_only` unless atomistic backmapping and comparison succeed | Potentially large sampling-speed gain | Alpha5/chimeric junction contacts may not survive CG; backmapping drift | S15, S18, and S19 support continued source-gate/design work; Mohanty 2025 and Cevheroglu 2017 are interface seeds only; direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG source still missing; P0047/P0040 full methods pending | Not built in this phase. If revived, run `chctrl` CG/backmapping benchmark first; candidate CG is blocked until `chctrl` comparison passes. |

## Gate Status

| Gate | Current status | Evidence |
|---|---|---|
| Source gate | Partially open | Initial matrix created; R1 has general setup/pressure-coupling support, R2 has candidate restraint-method sources, but force constants/release schedules are not extracted. R4 has method extraction and targeted citation-chasing memos, including interface-context seeds, but no direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG source has been extracted. |
| Build gate | Open for exploratory chctrl | CHARMM-GUI job `8305210188` produced a chctrl GROMACS input package under the R1 prototype root; static atom/topology/index/MDP checks pass in `local_static_validation.tsv`. User-approved E2 Package B completed step6.0 minimization through step6.6 equilibration for chctrl only; result root: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/`. |
| Benchmark gate | Partial chctrl short benchmark | User-approved E2 Package C completed a 100 ps short production test for reduced chctrl only, with performance and GPU utilization recorded in the result root. No Ch-1/Ch-2/Ch-4 benchmark has run. |
| Physical sanity gate | Partial short-run evidence only | E2-side `.tpr`, `.xtc`, `.edr`, `.gro`, and energy checks exist for step6.6 and short production. Step6.0 minimization had LINCS warnings but converged; step6.1-step6.6 and short production logs have no LINCS/fatal/CUDA/nan matches in the local scan. Interface metric recomputation and longer physical-sanity comparison are still pending. |
| Interpretation gate | Chctrl exploratory only; Z-only compute-saving route downgraded | R1 remains exploratory because no source-backed numeric padding rule exists. The chctrl prototype has build/short-run evidence, but the current Z-only instantiation saves only `-6776` atoms (`-2.57%`) and is not a compute-saving success claim or `candidate_replacement`; Ch-1/Ch-2/Ch-4 remain blocked. |

## Active Follow-up

- Route 1 job `8305210188` is retained as exploratory chctrl build/run evidence through `codex/docs/plans/chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md`.
- Current Z-only R1 is paused as the primary compute-saving route. The 2026-07-04 route-family memo selects R4 coarse-grained / multiscale source-gate work as the next meaningful-reduction family to investigate, with full-object throughput baseline planning kept as a companion scheduling/performance work item, not a system-reduction route. R4 method extraction is recorded in `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`; targeted citation chasing is recorded in `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`. These support continued source-gate/design work but not a buildable prototype.
- No separate metric/input dependency reference is maintained by this matrix. Recreate any metric dependency table from current scripts, selection config, preprocessing logs, and run evidence if needed.

## Next Local Steps Before Any E2 Request

1. Use `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md` as the current route-family selection memo.
2. Continue R4 source extraction, especially direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG examples and P0047/P0040 method details.
3. If R1 is revived, require a new source-backed rationale that changes more than Z water thickness and records expected atom-count benefit before any E2 request.
4. Benchmark only the `chctrl` prototype first; do not build or run candidate prototypes until the chosen `chctrl` route passes build, smoke, short benchmark, and interpretation gates.
5. For any next E2 step, write a new approval package with command, run directory, expected wall time, GPU/CPU/thread settings, and stop condition. Completed Package B/C approval does not authorize candidate or long production work.
