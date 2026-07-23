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

## Phase 1: normalized engineering scenario suite

`configs/stage1_scenario_scan.json` is the human-readable Phase-1 suite. It
uses the Phase-0 config as a base, then explicitly expands three bounded,
uncalibrated scan families:

- normalized ligand dose × normalized receptor half activation;
- effective Gpr--G protein coupling × output-layer leak; and
- 1/2/4-copy engineering scenarios × reporter gain × observation window.

Run the suite and its compact three-panel summary from the repository root:

```powershell
python src/modeling/ode/run_scenario_scans.py
python src/modeling/ode/plot_scenario_scan.py
```

The commands write `results/stage1_scenario_scan/`. Its README identifies the
config snapshot, complete time-courses, scenario manifest, final-time summary,
and figure. Run the ODE contracts without requiring `pytest`:

```powershell
python -m unittest tests.modeling.test_ode_minimal_solver tests.modeling.test_ode_scenario_scans -v
```

Every Phase-1 numeric setting and output remains `scenario_prior`. The suite
does not use docking scores as kinetic inputs and cannot establish a real ascr
concentration, experimental detection limit, or final copy-number choice.
