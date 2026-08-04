# ODE model outputs

This directory contains the runnable normalized prototype for the P0 yeast
STE2 pathway ODE. It deliberately separates executable engineering scenarios
from calibrated biological claims.

Every current numeric setting and output remains `scenario_prior`. The model
does not convert docking scores into affinities or kinetic constants and
cannot establish a real ascr concentration, experimental detection limit, or
final construct/copy-number choice.

## Phase 0: one normalized time-course

`configs/minimal_normalized_scenario.json` is the single-input Phase-0
configuration. Run the solver and render its reviewed compact result from the
repository root:

```bash
python -m src.modeling.ode.run_minimal_solver
python -m src.modeling.ode.plot_minimal_timecourse
```

The commands write:

- `results/minimal_normalized_timecourse.csv`
- `results/minimal_normalized_timecourse.png`

The CSV follows one scenario through `G_on`, lumped MAPK, sTF, GAL product
rate, and color signal. The PNG is rendered from that CSV and preserves the
`scenario_prior` label.

## Phase 1: normalized engineering scenario suite

`configs/stage1_scenario_scan.json` uses the Phase-0 config as its base and
expands three bounded, uncalibrated scan families:

- normalized ligand dose × normalized receptor half activation;
- effective Gpr--G protein coupling × output-layer leak; and
- 1/2/4-copy engineering scenarios × reporter gain × observation window.

The compact package is stored in
`results/stage1_scenario_scan/`. The complete time-course body is an external
operation payload and must be written outside the result directory:

```bash
python -m src.modeling.ode.run_scenario_scans \
  --timecourses-out /external/payload/path/timecourses.csv
python -m src.modeling.ode.plot_scenario_scan
```

The compact package contains the scenario manifest, final metrics, suite/base
config snapshots, run metadata, payload checksum/route manifest, and summary
PNG. It does not contain `timecourses.csv`; the tracked
`payload_manifest.tsv` records the external file's bytes, SHA256, storage
location, producer, consumer, and recovery command.

To prove the package is self-contained, rerun from its copied snapshots rather
than the source config directory:

```bash
python -m src.modeling.ode.run_scenario_scans \
  --config experiments/ode-model/results/stage1_scenario_scan/scan_suite_config_snapshot.json \
  --out-dir /tmp/ode-stage1-replay/compact \
  --timecourses-out /tmp/ode-stage1-replay/timecourses.csv
```

The accepted grid expands to 143 scenarios: 74 ligand scenarios and 69
one-to-one no-ligand controls. The complete payload has 23,023 data rows.
Requested scan-axis identity and effective solver input are stored separately,
so every no-ligand control has an effective ligand input of `0.0`.

## Phase 2A: analysis contract

`configs/phase2a_analysis_contract.json` defines the sensitivity and
calibration-readiness analysis interface on top of the accepted Phase 0/1
baseline. Its companion CSV files register:

- all 18 internal model fields and their screening ranges;
- 17 continuous uncertainty fields plus the discrete 1/2/4-copy design strata;
- active, diagnostic, and threshold-gated output metrics; and
- one observation/experiment/replacement route for every parameter.

The machine-readable rationale and activation gates are recorded in
`configs/phase2a_analysis_contract.json`. The canonical ODE scope and evidence
boundaries remain in
[`docs/modeling/P0-signal-pathway-ode.md`](../../docs/modeling/P0-signal-pathway-ode.md).
Phase 2A establishes the contract; local sensitivity and Morris results begin
in Phase 2B.

Run the ODE contracts without requiring `pytest`:

```bash
python -m unittest \
  tests.modeling.test_ode_minimal_solver \
  tests.modeling.test_ode_scenario_scans \
  tests.modeling.test_ode_phase2a_contract -v
```
