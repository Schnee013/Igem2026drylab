# Current drylab state memory

> 生成日期：2026-06-01
> Purpose: Codex project memory entry for current state. This file is pointer-based and does not replace `docs/INDEX.md`, domain docs, logs, or raw results.
> Read rule: use this file to find the relevant source logs, modeling docs, plans, and result files; verify conclusions in those sources.

## 1. chimeric MD：统一环境 clean-start rerun 是当前最高优先级

- Reviewed at: 2026-06-26
- Current-state authority: [docs/INDEX.md](../../../docs/INDEX.md)
- Detailed chronology authority: [docs/logs/](../../../docs/logs/)

**历史状态指针**：旧 Slurm/chctrl production 和 selection audit 只作历史证据/方法参考，不再作为当前 baseline 接受状态。旧 selection audit 报告仍在 `/Users/roy/Documents/drylab/experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`；old Slurm production logs 在 `/Users/roy/Documents/drylab/experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw/rep{1,2,3}/prod.log`。

- MD current status is routed through INDEX, the MD direction doc, decision 005, and recent logs. As of the latest pointer, old Slurm has the chimeric control/chctrl 3-replicate completion record, E2 has chctrl rep1 evidence only, chimeric candidate full-production is paused for compute triage, and mutant GPR MD should begin with system-size/resource tests from the current handoff candidates; verify details in sources before acting. Pointers: [docs/INDEX.md](../../../docs/INDEX.md), [docs/decisions/005-md-compute-triage-after-chctrl.md](../../../docs/decisions/005-md-compute-triage-after-chctrl.md), [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md), [docs/logs/2026-06-26.md](../../../docs/logs/2026-06-26.md).
- Remote-compute and MD site policy is indexed in the environment docs and site plans. The old chimeric E2/unified rerun route is now a paused/historical execution route unless reopened by a new decision; do not infer server, job, checkpoint, or scheduler state from memory alone. Pointers: [environments/md-production-sites.md](../../../environments/md-production-sites.md), [environments/e2-md-gromacs.md](../../../environments/e2-md-gromacs.md), [codex/docs/plans/e2-chimeric-md-restart.md](../plans/e2-chimeric-md-restart.md), [codex/docs/plans/chimeric-md-unified-rerun-sites.md](../plans/chimeric-md-unified-rerun-sites.md), [docs/ops/](../../../docs/ops/).
- Docking candidate and wet-lab handoff status must be read from the current docking direction doc, handoff, ratio outputs, and logs. Do not use historical Top sets or memory summaries as recommendations. Pointers: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md), [docs/modeling/wet-lab-handoff-P0-docking.md](../../../docs/modeling/wet-lab-handoff-P0-docking.md), [docs/logs/](../../../docs/logs/).
- ODE and reporter claims route through the ODE direction doc, reporter decision, and current INDEX/log pointers. Do not convert docking scores into calibrated ODE inputs from memory. Pointers: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md), [docs/decisions/004-reporter-output-architecture.md](../../../docs/decisions/004-reporter-output-architecture.md), [docs/INDEX.md](../../../docs/INDEX.md).
- Early-detection economic-model status and parameter readiness route through the direction doc, evidence dossier, validation notes, and HP/local-parameter logs. Do not state final ROI or calibrated local economics from memory. Pointers: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md), [docs/papers/p2-economic-benefit/README.md](../../../docs/papers/p2-economic-benefit/README.md), [docs/logs/](../../../docs/logs/).

## state_timeline

Do not read this timeline as current state. It only preserves dated routing
pointers for cross-session recovery.

- 2026-06-26: MD compute triage decision recorded; chimeric candidate full-production paused and mutant GPR MD starts with system-size/resource tests from current handoff candidates. Sources: [docs/decisions/005-md-compute-triage-after-chctrl.md](../../../docs/decisions/005-md-compute-triage-after-chctrl.md), [docs/logs/2026-06-26.md](../../../docs/logs/2026-06-26.md).
- 2026-06-02: chimeric MD gate/status evidence was logged; this route was later paused by the 2026-06-26 compute triage decision. Source: [docs/logs/2026-06-02.md](../../../docs/logs/2026-06-02.md).
- 2026-06-01: validation protocol and gate semantics were recorded; read the log and active plans before applying criteria. Source: [docs/logs/2026-06-01.md](../../../docs/logs/2026-06-01.md).
- 2026-05-30: E2/secondary-site routing and interruption evidence were recorded; read environment docs, plans, and logs before giving execution advice. Source: [docs/logs/2026-05-30.md](../../../docs/logs/2026-05-30.md).
- 2026-05-19/20: docking-repro handoff refresh became the current candidate route; read the handoff and docking direction doc for candidate claims. Sources: [docs/logs/2026-05-19.md](../../../docs/logs/2026-05-19.md), [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md).
- 2026-04-11: yeast-STE2 chassis decision set the strategic baseline; later implementation status must be read from INDEX/logs/domain docs. Sources: [docs/decisions/003-chassis-yeast-ste2-integration.md](../../../docs/decisions/003-chassis-yeast-ste2-integration.md), [docs/prd/chassis-decision.md](../../../docs/prd/chassis-decision.md).

## source_pointers

- Current router: [docs/INDEX.md](../../../docs/INDEX.md)
- Document governance: [docs/DOCMAP.md](../../../docs/DOCMAP.md)
- MD compute triage decision: [docs/decisions/005-md-compute-triage-after-chctrl.md](../../../docs/decisions/005-md-compute-triage-after-chctrl.md)
- Chimeric MD execution gate: [codex/docs/plans/e2-chimeric-md-restart.md](../plans/e2-chimeric-md-restart.md)
- Chimeric site matrix: [environments/md-production-sites.md](../../../environments/md-production-sites.md)
- MD direction doc: [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md)
- Docking direction doc: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md)
- Current docking handoff: [docs/modeling/wet-lab-handoff-P0-docking.md](../../../docs/modeling/wet-lab-handoff-P0-docking.md)
- ODE direction doc: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md)
- Early-detection economic benefit direction doc: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md)
