# Current drylab state memory

Purpose: timestamped project-state index for new sessions. This file summarizes
where the current state is. Authoritative facts come from the linked logs,
domain docs, plans, code, and result files.

## last_reviewed

- Reviewed at: 2026-07-12
- Current-state authority: [docs/INDEX.md](../../../docs/INDEX.md)
- Detailed chronology authority: [docs/logs/](../../../docs/logs/)

## latest_snapshot

- MD current status is routed through INDEX, the MD direction doc, decision 005, and recent logs. Old Slurm retains the chimeric control/chctrl 3-replicate completion record and chimeric candidate full-production remains paused for compute triage. `Gpr2_WT + ASCR18` now has a completed short benchmark and 200 ns rep1; the latter is single-replicate triage evidence with high receptor RMSD and descriptive ligand displacement, not a ligand-threshold pass/fail result. Both mutant systems have upload materials but remain on checksum-provenance HOLD until the historical-to-current PPM/input migrations are resolved or superseded by versioned reruns. Pointers: [docs/INDEX.md](../../../docs/INDEX.md), [docs/decisions/005-md-compute-triage-after-chctrl.md](../../../docs/decisions/005-md-compute-triage-after-chctrl.md), [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md), [docs/logs/2026-07-12.md](../../../docs/logs/2026-07-12.md).
- Remote-compute and MD site policy is indexed in the environment docs and site plans. The old chimeric E2/unified rerun route is now a paused/historical execution route unless reopened by a new decision; server, job, checkpoint, and scheduler state require current source verification. Pointers: [environments/md-production-sites.md](../../../environments/md-production-sites.md), [environments/e2-md-gromacs.md](../../../environments/e2-md-gromacs.md), [codex/docs/plans/e2-chimeric-md-restart.md](../plans/e2-chimeric-md-restart.md), [codex/docs/plans/chimeric-md-unified-rerun-sites.md](../plans/chimeric-md-unified-rerun-sites.md), [docs/ops/](../../../docs/ops/).
- Docking candidate status must be read from the current docking direction doc, MD candidate-system shortlist, ratio outputs, and logs. Candidate recommendations use current source pointers rather than historical Top sets or memory summaries. Pointers: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md), [docs/modeling/P0-docking-md-candidate-shortlist.md](../../../docs/modeling/P0-docking-md-candidate-shortlist.md), [docs/logs/](../../../docs/logs/).
- ODE and reporter claims route through the ODE direction doc, reporter decision, and current INDEX/log pointers. Calibrated ODE inputs require binding/calibration evidence beyond docking scores. Pointers: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md), [docs/decisions/004-reporter-output-architecture.md](../../../docs/decisions/004-reporter-output-architecture.md), [docs/INDEX.md](../../../docs/INDEX.md).
- Early-detection economic-model status and parameter readiness route through the direction doc, evidence dossier, validation notes, and HP/local-parameter logs. Final ROI and calibrated local economics require those source documents. Pointers: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md), [docs/papers/p2-economic-benefit/README.md](../../../docs/papers/p2-economic-benefit/README.md), [docs/logs/](../../../docs/logs/).

## state_timeline

This timeline is dated routing context for cross-session recovery. Current state
comes from INDEX, current domain docs, logs, plans, code, and result files.

- 2026-07-12: GPR metric semantics and payload/recovery contracts were repaired; unresolved preproduction/raw archive gaps and mutant PPM checksum migrations remain explicit HOLD/PARTIAL states. Sources: [docs/logs/2026-07-12.md](../../../docs/logs/2026-07-12.md), [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md).
- 2026-07-09: `Gpr2_WT + ASCR18` 200 ns rep1 completion and single-replicate analysis were recorded. Sources: [docs/logs/2026-07-09.md](../../../docs/logs/2026-07-09.md), [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md).
- 2026-06-26: MD compute triage decision recorded; chimeric candidate full-production paused and mutant GPR MD starts with system-size/resource tests from current handoff candidates. Sources: [docs/decisions/005-md-compute-triage-after-chctrl.md](../../../docs/decisions/005-md-compute-triage-after-chctrl.md), [docs/logs/2026-06-26.md](../../../docs/logs/2026-06-26.md).
- 2026-06-02: chimeric MD gate/status evidence was logged; this route was later paused by the 2026-06-26 compute triage decision. Source: [docs/logs/2026-06-02.md](../../../docs/logs/2026-06-02.md).
- 2026-06-01: validation protocol and gate semantics were recorded; read the log and active plans before applying criteria. Source: [docs/logs/2026-06-01.md](../../../docs/logs/2026-06-01.md).
- 2026-05-30: E2/secondary-site routing and interruption evidence were recorded; read environment docs, plans, and logs before giving execution advice. Source: [docs/logs/2026-05-30.md](../../../docs/logs/2026-05-30.md).
- 2026-05-19/20: docking-repro shortlist refresh became the current candidate route; read the shortlist and docking direction doc for candidate claims. Sources: [docs/logs/2026-05-19.md](../../../docs/logs/2026-05-19.md), [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md).
- 2026-04-11: yeast-STE2 chassis decision set the strategic baseline; later implementation status must be read from INDEX/logs/domain docs. Sources: [docs/decisions/003-chassis-yeast-ste2-integration.md](../../../docs/decisions/003-chassis-yeast-ste2-integration.md), [docs/prd/chassis-decision.md](../../../docs/prd/chassis-decision.md).

## source_pointers

- Current router: [docs/INDEX.md](../../../docs/INDEX.md)
- Document governance: [docs/DOCMAP.md](../../../docs/DOCMAP.md)
- MD compute triage decision: [docs/decisions/005-md-compute-triage-after-chctrl.md](../../../docs/decisions/005-md-compute-triage-after-chctrl.md)
- Chimeric MD execution gate: [codex/docs/plans/e2-chimeric-md-restart.md](../plans/e2-chimeric-md-restart.md)
- Chimeric site matrix: [environments/md-production-sites.md](../../../environments/md-production-sites.md)
- MD direction doc: [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md)
- Docking direction doc: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md)
- Current docking MD candidate-system shortlist: [docs/modeling/P0-docking-md-candidate-shortlist.md](../../../docs/modeling/P0-docking-md-candidate-shortlist.md)
- ODE direction doc: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md)
- Early-detection economic benefit direction doc: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md)
