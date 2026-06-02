# Current drylab state memory

Purpose: timestamped project-state index for new sessions. This file summarizes
where the current state is, but it does not make facts authoritative. Verify
status, results, thresholds, and next actions in the linked logs, domain docs,
plans, code, and result files.

## last_reviewed

- Reviewed at: 2026-06-02
- Current-state authority: [docs/INDEX.md](../../../docs/INDEX.md)
- Detailed chronology authority: [docs/logs/](../../../docs/logs/)

## latest_snapshot

- Chimeric MD is the highest-priority active route. `chimeric-ste2-gpa1-wt` rep1 passed the 194.8 ns full-system early stability gate on 2026-06-02 and should continue the same live `mdrun` to the 500 ns final target unless later evidence changes that route. Pointers: [docs/INDEX.md](../../../docs/INDEX.md), [docs/logs/2026-06-02.md](../../../docs/logs/2026-06-02.md), [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md).
- E2 remains the primary route for the current chimeric rerun; Slurm RTX 5090 is only a gated secondary candidate, not a fallback to old Slurm production provenance. Pointers: [environments/md-production-sites.md](../../../environments/md-production-sites.md), [environments/e2-md-gromacs.md](../../../environments/e2-md-gromacs.md), [codex/docs/plans/chimeric-md-unified-rerun-sites.md](../plans/chimeric-md-unified-rerun-sites.md), [docs/logs/2026-05-30.md](../../../docs/logs/2026-05-30.md).
- Docking-repro has a refreshed 2026-05-20 handoff. Use the current wet-lab handoff and ratio release for candidates; do not revive the 2026-04-14 historical Top set as a recommendation. Pointers: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md), [docs/modeling/wet-lab-handoff-P0-docking.md](../../../docs/modeling/wet-lab-handoff-P0-docking.md), [docs/logs/2026-05-19.md](../../../docs/logs/2026-05-19.md).
- ODE remains a parameter/evidence and reporter-interface track until a solver/config/plot implementation exists. Do not convert docking scores into `Kd` or calibrated ODE inputs. Pointers: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md), [docs/INDEX.md](../../../docs/INDEX.md).
- Reporter output architecture is sTF to GAL multi-copy amplification to color output; specific pigment, integration site, actual copy number, gain, and time-course parameters still require wet-lab/ODE calibration. Pointers: [docs/decisions/004-reporter-output-architecture.md](../../../docs/decisions/004-reporter-output-architecture.md), [docs/INDEX.md](../../../docs/INDEX.md).
- P2 economic modeling can explain deterministic cost-accounting and break-even structure, but final ROI depends on HP/wet-lab/local parameter recovery. Pointers: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md), [docs/papers/p2-economic-benefit/README.md](../../../docs/papers/p2-economic-benefit/README.md), [docs/logs/2026-05-23.md](../../../docs/logs/2026-05-23.md).

## state_timeline

- 2026-06-02 current snapshot: chctrl rep1 early stability gate passed at the isolated 194.8 ns snapshot; same trajectory should continue to 500 ns final production target. Source: [docs/logs/2026-06-02.md](../../../docs/logs/2026-06-02.md).
- 2026-06-01 historical: tiered validation protocol introduced; 100-150 ns is an early full-system gate, not a replacement for final production. Source: [docs/logs/2026-06-01.md](../../../docs/logs/2026-06-01.md).
- 2026-05-30 historical: checkpoint-gated interruption, same-GPU benchmark, single-job resume route, and Slurm secondary-site gate were recorded. Source: [docs/logs/2026-05-30.md](../../../docs/logs/2026-05-30.md).
- 2026-05-20 historical: docking-repro handoff refresh became the current candidate route; older ratio/Top materials became historical context. Sources: [docs/logs/2026-05-19.md](../../../docs/logs/2026-05-19.md), [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md).
- 2026-04-11 historical: yeast-STE2 chassis decision set the strategic baseline; later implementation status must be read from INDEX/logs/domain docs, not from the decision analysis itself. Sources: [docs/decisions/003-chassis-yeast-ste2-integration.md](../../../docs/decisions/003-chassis-yeast-ste2-integration.md), [docs/prd/chassis-decision.md](../../../docs/prd/chassis-decision.md).

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
