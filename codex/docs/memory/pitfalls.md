# Drylab Codex pitfalls

> Distilled from selected Claude feedback memories. These are active guardrails, not final evidence.

## Source-of-truth pitfalls

- Memory is not evidence. Verify claims against `docs/`, logs, configs, code, result files, paper summaries, or data outputs.
- Do not treat old Claude plan files as current state. Use them as historical plans and calibrate against `docs/INDEX.md` and recent logs.
- Log/memory should not duplicate plan details. If a plan contains workflow steps, log the event and point to the plan section instead of copying the plan body.

## Scientific/documentation pitfalls

- When writing `docs/modeling/**` or `docs/prd/**` and citing literature classifications such as positive/negative controls, loss-of-function, or gain-of-function, read the relevant `docs/papers/summaries/*.md` section and cite the summary line/pointer. Do not flatten remembered classifications.
- Mechanism claims such as salt bridge, hydrogen bond, π interaction, or hydrophobic enrichment require source interaction-channel evidence. Check the actual CSV/JSON interaction fields before writing the mechanism.
- Historical JSON/CSV artifacts used as baselines require provenance checks: input identity, code version, config, and whether the artifact predates a known fix.
- Project architecture claims involving chassis, heterologous expression, signal chain, engineered organism, or “expressed in/on” must be checked against `docs/prd/overview-v4.md` and `docs/prd/chassis-decision.md`.
- Paper summaries must stay faithful to the paper. Do not add project pipeline results, IFP comparisons, or ΔG comparisons to `docs/papers/summaries/`.
- Saturation-scan outliers are not class rules. Before saying “basic residues”, “acidic residues”, etc. drive an effect, check same-class consistency across the saturation set.

## External-communication pitfalls

- For documents sent to external people, verify the full project fact chain: species/roles via PRD, numeric progress via logs/docs, topology/structure via modeling docs.
- Avoid “directly transferable”, “essentially identical”, or similar absolute similarity claims unless the same paragraph lists the important differences.

## Active project guardrails

- Do not treat stale docking Top candidates as wet-lab recommendations until Gpr3 F follow-up, ratio refresh, and IFP refresh are complete.
- Do not restart Ch-1/Ch-2/Ch-4 chimeric MD until chctrl local analysis has been reviewed.
- Windows 7500F is deprecated for new compute. Only consult Windows rules when accessing historical docking files still on that node; prefer `docs/ops/archives/ssh-windows-compute.md` as the source.
- On Mac, run docking-repro scripts in the `docking` conda environment; do not install docking dependencies into base.
