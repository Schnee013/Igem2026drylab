# Drylab Codex pitfalls

> Frozen historical snapshot. Retained for traceability; not an active
> guardrail source. Re-enter through `docs/DOCMAP.md` and verify all current
> claims against repository authorities.

> Distilled from selected Claude feedback memories. These were historical
> guardrails, not final evidence.

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
- A positive static IFP salt-bridge geometry is not thermodynamic proof. It means the pose satisfies contact criteria, not that electrostatics drive binding.
- ProLIF Anionic/Cationic channels were not disabled in the old PDBQT workflow; formal charges were missing after PDBQT-to-SDF conversion, so SMARTS matching failed on charged atoms.
- After Gpr3 scheme F changed pose geometry, old Gpr3 V138R/groove IFP outputs are historical mechanism context only. Use refreshed F-pose IFP/AF3/ratio outputs for current Gpr3 mechanism claims.
- AoGpa2 `TGJ64397.1` identity and chimeric donor choices should not be rolled back from memory alone; use `docs/logs/True_Gpr2_or_not.md`, `docs/modeling/P3-chimeric-gprotein.md`, and current MD docs.

## External-communication pitfalls

- For documents sent to external people, verify the full project fact chain: species/roles via PRD, numeric progress via logs/docs, topology/structure via modeling docs.
- Avoid “directly transferable”, “essentially identical”, or similar absolute similarity claims unless the same paragraph lists the important differences.

## Active project guardrails

- Do not treat the 2026-04 historical docking Top set as wet-lab recommendations. Use the refreshed handoff and current ratio release.
- Current chimeric MD rerun is an approved clean-start scope for chctrl + Ch-1/Ch-2/Ch-4. Do not launch a site or replicate from memory alone; follow `environments/md-production-sites.md`, current logs, and the gate scripts.
- New server/remote-compute work defaults to NKULiulab E2 and must read `docs/ops/nkuliulab-e2-cloud-server.md` first. The approved exception is the current chimeric MD Slurm RTX 5090 validated secondary route, which must use `environments/md-production-sites.md` and new `slurm_*` gate scripts. Windows 7500F, HBU SGE, and archived Slurm guides remain historical unless explicitly used as pointers.
- For GROMACS / MD operational pitfalls that are not server-specific, use `docs/ops/md-gromacs-operational-pitfalls.md`; do not use the archived Slurm guide as the default execution entry.
- On Mac, run docking-repro scripts in the `docking` conda environment; do not install docking dependencies into base.
