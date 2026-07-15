# ODE model outputs

This directory contains inputs and outputs for the P0 yeast STE2 pathway ODE.

The current `configs/minimal_normalized_scenario.json` is a Phase-0,
single-input, normalized `scenario_prior` smoke configuration. Its numeric
values are illustrative interfaces, not calibrated receptor affinities,
kinetic constants, detection limits, or wet-lab recommendations.

Run it from the repository root:

```powershell
python src/modeling/ode/run_minimal_solver.py
```

The command writes `results/minimal_normalized_timecourse.csv`. It contains a
single time-course through `G_on`, lumped MAPK, sTF, GAL product rate, and
color signal. Dose-response, copy-number, leak, and sensitivity scans belong
to the next planned phase and are intentionally not implemented here.
