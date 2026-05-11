# Chimeric Gpa1 memory

> Source: distilled from Claude `project_chimeric_gpa1.md`, current `P3-chimeric-gprotein.md`, `P0-md-simulation.md`, and recent logs. Verify current state against source docs/logs.

## Stable decisions

- Chimeric Gpa1 is P0 after yeast-STE2 chassis decision.
- Gpr2/Gpr3 use AoGpa2 as the cognate Gα source; GprC uses AfGasA.
- AoGpa2 `TGJ64397.1` identity has been checked against Kuo2024 primers/NCBI sequence and should not be rolled back without new concrete accession/CDS evidence.
- Chimeric Gpa1 C-terminal donor sequence must come from the receptor’s native-coupled Gα unless explicitly changing the biological hypothesis.

## Current interpretation

- AF3 full screen completed; Top candidates selected; current reliability depends on MD validation.
- chctrl production MD is complete and is the current analysis priority.
- Ch-1/Ch-2/Ch-4 are paused until chctrl local analysis is reviewed.

## Source pointers

- Direction doc: `/Users/roy/Documents/drylab/docs/modeling/P3-chimeric-gprotein.md`
- MD direction doc: `/Users/roy/Documents/drylab/docs/modeling/P0-md-simulation.md`
- AoGpa2 identity check: `/Users/roy/Documents/drylab/docs/logs/True_Gpr2_or_not.md`
- chimeric MD current log: `/Users/roy/Documents/drylab/docs/logs/2026-04-26.md`
- AF3 ranking: `/Users/roy/Documents/drylab/experiments/chimeric-gpa1/analysis/ranking_summary.md`
- Current Codex state: `/Users/roy/Documents/drylab/codex/docs/memory/current-state.md`
- Historical plans:
  - `/Users/roy/.claude/plans/mac-pbc-memory-memory-imperative-moon.md`
  - `/Users/roy/.claude/plans/chimeric-md-execution.md`
  - `/Users/roy/.claude/plans/docking-md-chimeric-md-md-wt-gpr-chimer-nifty-falcon.md`

## Guardrails

- Do not restart Ch-1/Ch-2/Ch-4 until chctrl metrics are reviewed.
- Do not use memory atom counts, job IDs, box sizes, or EM Fmax values directly; read logs/source outputs.
- Treat 7AD3 as a validation/reference structure unless current docs explicitly say otherwise.
