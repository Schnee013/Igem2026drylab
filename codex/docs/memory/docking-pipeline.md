# Docking pipeline memory

> Source: distilled from Claude `project_docking_pipeline.md`, current `docs/INDEX.md`, `docs/modeling/P0-molecular-docking.md`, and recent logs. Verify current claims against sources before use.

## Current interpretation

- Active pipeline: `docking-repro`, not the archived early v2 docking pipeline.
- Current status: reanalysis. Gpr2 3D offset rerun completed; Gpr3 scheme F used ECL2 manual box and passed geometry, but the result is not final for wet-lab recommendation.
- Current blocking task: refresh Gpr3 F follow-up, ratio, IFP, and wet-lab handoff before treating Top pairs as authoritative.
- User-specified follow-up: Gpr3 F conclusion is not ideal; additional AF3 predictions for more IFP-related sites are needed. Batch JSON files exist at:
  - `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_01.json`
  - `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_02.json`

## Source pointers

- Direction doc: `/Users/roy/Documents/drylab/docs/modeling/P0-molecular-docking.md`
- Current router: `/Users/roy/Documents/drylab/docs/INDEX.md`
- Gpr2/Gpr3 repair log: `/Users/roy/Documents/drylab/docs/logs/2026-04-23.md`
- Current Codex state: `/Users/roy/Documents/drylab/codex/docs/memory/current-state.md`
- Historical ratio report: `/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_channel_report.md` — use as history only until refreshed.
- Ratio script: `/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_channel_analysis.py`

## Guardrails

- Do not copy ΔG/sel/D values from memory. Read the JSON/CSV/report that is current for the specific analysis.
- Do not treat old Gpr3 V138-series IFP as mechanism evidence after scheme F changed pose geometry.
- Do not update wet-lab Top recommendations until refreshed ratio and IFP outputs exist.
