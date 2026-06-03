# Current drylab state memory

Purpose: timestamped project-state index for new sessions. This file summarizes
where the current state is, but it does not make facts authoritative. Verify
status, results, thresholds, and next actions in the linked logs, domain docs,
plans, code, and result files.

## last_reviewed

- Reviewed at: 2026-06-03
- Current-state authority: [docs/INDEX.md](../../../docs/INDEX.md)
- Detailed chronology authority: [docs/logs/](../../../docs/logs/)

## latest_snapshot

- Chimeric MD current status is routed through INDEX, the MD direction doc, the active execution plans, and recent logs. Do not infer run state, targets, or continue/stop advice from memory alone. Pointers: [docs/INDEX.md](../../../docs/INDEX.md), [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md), [codex/docs/plans/e2-chimeric-md-restart.md](../plans/e2-chimeric-md-restart.md), [docs/logs/](../../../docs/logs/).
- Remote-compute and MD site policy is indexed in the environment docs and site plans. Do not infer server, job, checkpoint, or scheduler state from memory alone. Pointers: [environments/md-production-sites.md](../../../environments/md-production-sites.md), [environments/e2-md-gromacs.md](../../../environments/e2-md-gromacs.md), [codex/docs/plans/chimeric-md-unified-rerun-sites.md](../plans/chimeric-md-unified-rerun-sites.md), [docs/ops/](../../../docs/ops/).
- Docking candidate and wet-lab handoff status must be read from the current docking direction doc, handoff, ratio outputs, and logs. Do not use historical Top sets or memory summaries as recommendations. Pointers: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md), [docs/modeling/wet-lab-handoff-P0-docking.md](../../../docs/modeling/wet-lab-handoff-P0-docking.md), [docs/logs/](../../../docs/logs/).
- ODE and reporter claims route through the ODE direction doc, reporter decision, and current INDEX/log pointers. Do not convert docking scores into calibrated ODE inputs from memory. Pointers: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md), [docs/decisions/004-reporter-output-architecture.md](../../../docs/decisions/004-reporter-output-architecture.md), [docs/INDEX.md](../../../docs/INDEX.md).
- P2 economic-model status and parameter readiness route through the P2 direction doc, evidence dossier, validation notes, and HP/local-parameter logs. Do not state final ROI or calibrated local economics from memory. Pointers: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md), [docs/papers/p2-economic-benefit/README.md](../../../docs/papers/p2-economic-benefit/README.md), [docs/logs/](../../../docs/logs/).

## state_timeline

Do not read this timeline as current state. It only preserves dated routing
pointers for cross-session recovery.

- 2026-06-02: chimeric MD gate/status evidence was logged; read the log and INDEX before making any run-state claim. Source: [docs/logs/2026-06-02.md](../../../docs/logs/2026-06-02.md).
- 2026-06-01: validation protocol and gate semantics were recorded; read the log and active plans before applying criteria. Source: [docs/logs/2026-06-01.md](../../../docs/logs/2026-06-01.md).
- 2026-05-30: E2/secondary-site routing and interruption evidence were recorded; read environment docs, plans, and logs before giving execution advice. Source: [docs/logs/2026-05-30.md](../../../docs/logs/2026-05-30.md).
- 2026-05-19/20: docking-repro handoff refresh became the current candidate route; read the handoff and docking direction doc for candidate claims. Sources: [docs/logs/2026-05-19.md](../../../docs/logs/2026-05-19.md), [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md).
- 2026-04-11: yeast-STE2 chassis decision set the strategic baseline; later implementation status must be read from INDEX/logs/domain docs. Sources: [docs/decisions/003-chassis-yeast-ste2-integration.md](../../../docs/decisions/003-chassis-yeast-ste2-integration.md), [docs/prd/chassis-decision.md](../../../docs/prd/chassis-decision.md).

## source_pointers

- Current router: [docs/INDEX.md](../../../docs/INDEX.md)
- Document governance: [docs/DOCMAP.md](../../../docs/DOCMAP.md)
- Chimeric MD execution gate: [codex/docs/plans/e2-chimeric-md-restart.md](../plans/e2-chimeric-md-restart.md)
- Chimeric site matrix: [environments/md-production-sites.md](../../../environments/md-production-sites.md)
- MD direction doc: [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md)
- Docking direction doc: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md)
- Current docking handoff: [docs/modeling/wet-lab-handoff-P0-docking.md](../../../docs/modeling/wet-lab-handoff-P0-docking.md)
- ODE direction doc: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md)
- P2 direction doc: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md)
