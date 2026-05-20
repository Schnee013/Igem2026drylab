# Docking pipeline memory

> Source: distilled from Claude `project_docking_pipeline.md`, current `docs/INDEX.md`, `docs/modeling/P0-molecular-docking.md`, and recent logs. Verify current claims against sources before use.

## Current interpretation

- Active pipeline: `docking-repro`, not the archived early v2 docking pipeline.
- Current status: `refreshed_handoff` as of 2026-05-20. Gpr2 3D offset, Gpr3 scheme F, Gpr3 supplemental docking, ratio refresh, Top-candidate IFP, and wet-lab handoff have been refreshed.
- Current handoff task: wet-lab team/PI should confirm first-build capacity and readout design from the refreshed handoff; optional PyMOL PNG/PSE rendering remains a communication artifact, not a ranking blocker.
- Current repo-owned execution plan: `/Users/roy/Documents/drylab/codex/docs/plans/docking-repro-full-refresh-slurm.md` (Phase 1-7 executed; use logs/results below for evidence).
- Completed supplemental AF3 input batches were:
  - `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_01.json`
  - `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_02.json`

## Source pointers

- Direction doc: `/Users/roy/Documents/drylab/docs/modeling/P0-molecular-docking.md`
- Current router: `/Users/roy/Documents/drylab/docs/INDEX.md`
- Gpr2/Gpr3 repair log: `/Users/roy/Documents/drylab/docs/logs/2026-04-23.md`
- Full refresh execution log: `/Users/roy/Documents/drylab/docs/logs/2026-05-19.md`
- Current Codex state: `/Users/roy/Documents/drylab/codex/docs/memory/current-state.md`
- Current ratio report: `/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_channel_report.md`
- Current wet-lab handoff: `/Users/roy/Documents/drylab/docs/modeling/wet-lab-handoff-P0-docking.md`
- Current IFP output: `/Users/roy/Documents/drylab/experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/`
- Ratio script: `/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_channel_analysis.py`

## Guardrails

- Do not copy ΔG/sel/D values from memory. Read the JSON/CSV/report that is current for the specific analysis.
- Do not treat old Gpr3 V138-series IFP as mechanism evidence after scheme F changed pose geometry.
- Do not reuse 2026-04-14 old Top recommendations after the 2026-05-20 refresh.
- Do not convert Vina scores to Kd until the separate ODE/Kd calibration literature review decides the policy.
