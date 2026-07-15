# Source Pointers

## Planning And Protocol

| Path | Role |
|---|---|
| `codex/docs/plans/chimeric-gpa1-system-reduction-exploration.md` | Parent exploration plan and route/gate definitions. |
| `codex/docs/plans/chimeric-gpa1-r1-tight-full-rebuild-chctrl-plan.md` | Historical Route 1 chctrl-first plan retained for prototype provenance; current start instructions require a new work order from the active router. |
| `experiments/md-simulation/analysis/chimeric_system_reduction_protocol_matrix.md` | Route matrix, universal prototype rule, and R1 evidence boundary. |
| `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md` | Historical post-R1-Z route-family selection memo; records that R4 source-gate work was selected on 2026-07-04, but later R4 material-boundary records supersede it as a current instruction. |
| `experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md` | Source matrix for R1 support, no-go warnings, and pending extraction queue. |
| `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_reduced_chctrl_build_request.md` | Manual CHARMM-GUI Membrane Builder checklist for the exploratory reduced `chctrl` rebuild. |
| `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md` | Local/public atom-count comparison and routing decision that downgrades the current Z-only R1 instantiation as insufficient for compute saving. |
| `docs/logs/2026-07-03.md` | Work log for system-reduction exploration and R1 planning. |

## Current Chctrl Inputs

| Path | Role |
|---|---|
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step5_input.pdb` | Current CHARMM-GUI-style input structure for chctrl. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step6.6.gro` | Current post-equilibration coordinate source used for inventory. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/topol.top` | Current topology and molecule counts. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/index.ndx` | Current index groups used by production/analysis. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/gromacs/step7_production.mdp` | Current production MDP settings for comparison. |
| `experiments/md-simulation/structures/chimeric/Chctrl_Ste2_Gpa1_WT_submit.pdb` | Protein-only, PPM-oriented chctrl submit PDB for the manual CHARMM-GUI reduced rebuild attempt. |
| `experiments/md-simulation/analysis/chimeric_system_reduction_inventory.tsv` | Four-system atom-count and box inventory. |
| `experiments/md-simulation/analysis/chimeric_systems.json` | Current metric selection definitions. |

## External Method Sources Extracted

| Source | Role |
|---|---|
| Feng et al. 2023, `CHARMM-GUI Membrane Builder: Past, Current, and Future Developments and Applications`, DOI `10.1021/acs.jctc.2c01246`, PMC `PMC10174225` | Supports CHARMM-GUI Membrane Builder as the preferred complete membrane-system rebuild workflow; extracted support is workflow-level, not a Ste2-Gpa1 numeric padding rule. |
| GROMACS 2026.3 pressure-coupling documentation, `https://manual.gromacs.org/current/reference-manual/algorithms/molecular-dynamics.html#pressure-coupling` | Supports Route 1 implementation constraint that membrane systems should preserve interpretable semi-isotropic pressure coupling; does not define minimum padding. |
| GROMACS 2026.3 membrane simulation documentation, `https://manual.gromacs.org/current/how-to/special.html` | Supports treating membrane solvation/embedding as a setup risk requiring full-system checks; does not approve manual water/lipid deletion as a rebuild. |

## Prototype Root

| Path | Role |
|---|---|
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/route.json` | Route metadata and current build conclusion for the chctrl-only prototype. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/build_notes.md` | Human-readable build notes, blocker list, and source/target relationships. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/source_files.sha256` | Checksums for current chctrl input, R1 planning files, prototype metadata, and E2 guardrail files used by the prototype design. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/source_archives/charmm_gui_8305210188_xy120_w20_download.tgz` | Original CHARMM-GUI job `8305210188` download archive for the exploratory `120 A XY / 20 A water` chctrl build. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/` | Extracted CHARMM-GUI GROMACS input package for job `8305210188`; contains `step5_input.*`, `topol.top`, `index.ndx`, `toppar/`, and step6/step7 MDPs. E2 outputs are stored separately under the Package B/C result root. |
| `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/local_static_validation.tsv` | Local static validation summary for archive checksum, atom-count delta, topology/index/MDP checks, and local `gmx` absence. |

## E2 Package A Evidence

| Path | Role |
|---|---|
| `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/run_logs/e2_preflight_20260703_gmx_env/e2_preflight_20260703_gmx_env.log` | User-approved Package A E2 preflight log; verifies E2 `gmx_mpi` environment, GPU visibility, quota, and remote metadata checksums; no `grompp`/`mdrun` was run. |

## E2 Package B/C Evidence

| Path | Role |
|---|---|
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/README.md` | Result summary for user-approved Package B step6 and Package C short production. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/source_pointers.md` | Result-root source pointer map. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/logs/gmx_version.log` | Package B E2 GROMACS provenance. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/logs/gmx_version_production_short.log` | Package C E2 GROMACS provenance. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/logs/mdrun_step6.6_equilibration.log` | Final step6.6 equilibration performance evidence. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/logs/mdrun_r1_chctrl_short_prod.log` | Short production performance evidence. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/logs/nvidia_smi_production_short.csv` | Short production GPU utilization samples. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/logs/sanity_energy.log` | E2-side step6.6 energy summary. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/logs/sanity_short_prod_energy.log` | E2-side short production energy summary. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/local_download.sha256` | Local checksum manifest after downloading Package B/C result files. |

## Benchmark Comparison Inputs

| Path | Role |
|---|---|
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/analysis/e2_ctrl_rep1_slurm_equivalent_analysis_20260627.md` | E2 chctrl rep1 early-gate metric summary and evidence boundary. |
| `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/analysis/early_gate_metrics_summary.csv` | Metric snapshot table for later reduced-chctrl comparison. |

## Ops Guardrails

| Path | Role |
|---|---|
| `docs/ops/nkuliulab-e2-cloud-server.md` | E2 shared-server resource and approval boundary. |
| `docs/ops/md-gromacs-operational-pitfalls.md` | GROMACS/MD operational pitfalls, especially index, output group, and trajectory handling. |
| `environments/e2-md-gromacs.md` | E2 GROMACS environment matrix and hard rule that E2-produced GROMACS binary outputs must be checked, converted, preprocessed, and evidence-analyzed with the recorded E2 GROMACS environment for that run. |
