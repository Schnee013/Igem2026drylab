# IFP and salt-bridge memory

> Source: distilled from Claude `project_ifp_salt_bridge_limitation.md`, `feedback_mechanism_claim_requires_channel.md`, and current docking reanalysis state.

## Core lesson

ProLIF Anionic/Cationic channels were not “disabled”. In the PDBQT → SDF workflow, formal charges were missing, so salt-bridge SMARTS could not match charged atoms. The failure mode was input chemistry, not a disabled interaction channel.

## Current interpretation

- The pipeline was later fixed by injecting ligand/receptor formal charges via pH 7.4 templates and receptor charge correction.
- A positive static IFP salt-bridge geometry is not thermodynamic proof. It means the pose satisfies geometric/contact criteria, not that electrostatics drive binding.
- After Gpr3 scheme F changed the Gpr3 pose geometry, old Gpr3 V138R/groove IFP results are not valid mechanism evidence for the new extracellular ECL2 pose.

## Source pointers

- Current docking doc: `/Users/roy/Documents/drylab/docs/modeling/P0-molecular-docking.md`
- MD doc for dynamic validation: `/Users/roy/Documents/drylab/docs/modeling/P0-md-simulation.md`
- Gpr3 F repair log: `/Users/roy/Documents/drylab/docs/logs/2026-04-23.md`
- IFP historical outputs: `/Users/roy/Documents/drylab/experiments/docking-repro/results/ifp_analysis_mutants/`

## Guardrails

- Before writing “salt bridge”, “hydrogen bond”, “π interaction”, or similar mechanism claims, inspect the actual interaction-channel outputs.
- For Gpr3 mechanism claims after scheme F, use refreshed F-pose IFP/AF3/ratio outputs, not pre-F groove outputs.
- For stronger mechanistic claims, prefer MD distance/occupancy/lifetime evidence over static docking IFP alone.
