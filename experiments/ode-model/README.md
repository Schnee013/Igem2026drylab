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

`configs/phase2a_analysis_contract.json` defines the analysis and evidence-gap
contract on top of the accepted Phase 0/1 baseline. Its companion CSV files
register:

- all 18 internal model fields and their screening ranges;
- 17 continuous uncertainty fields plus the discrete 1/2/4-copy design strata;
- active, diagnostic, and threshold-gated output metrics; and
- a potential-observable class and current evidence gap for every parameter.

The machine-readable rationale and activation gates are recorded in
`configs/phase2a_analysis_contract.json`. The canonical ODE scope and evidence
boundaries remain in
[`docs/modeling/P0-signal-pathway-ode.md`](../../docs/modeling/P0-signal-pathway-ode.md).
Phase 2A establishes the analysis contract. Phase 2B produces model-side
sensitivity results, and Phase 2C evaluates identifiability under candidate
observable classes. Concrete assays, experimental controls, sampling design,
and priorities enter the later DBTL handoff after joint review of those model
outputs and the team-confirmed wet-lab plan, feasibility, cost, and resources.

## Phase 2B: sensitivity and global screening

`configs/phase2b_local_sensitivity.json` defines the first executable Phase 2B
slice. The runner reads the Phase 2A parameter and context contract, computes
scaled local sensitivities `d(output)/d(log(parameter))`, and repeats the
finite difference at a halved step. Parameters on a registered range boundary
use an in-bounds one-sided difference; all others use a central difference. A
configured output-scale floor prevents solver noise around a true zero
sensitivity from being mislabeled as a large relative step difference.

Run the full 17-parameter, five-context baseline-copy analysis from the
repository root:

```bash
python -m src.modeling.ode.local_sensitivity
```

For a small diagnostic slice, filters can be repeated as needed:

```bash
python -m src.modeling.ode.local_sensitivity \
  --parameter-id n_R \
  --ligand-context transition_reference \
  --ligand-context transition_low_diagnostic \
  --ligand-context transition_high_diagnostic \
  --out /tmp/ode-phase2b-nr-slice/sensitivities.csv
```

The CSV keeps all configured time points and `run_metadata.json` records the
input hashes, finite-difference rule, selected dimensions, and interpretation
boundary. These normalized `scenario_prior` derivatives support local numerical
diagnostics. Biological effect calibration and parameter ranking require
project data and their separate analysis gates.

`configs/phase2b_morris_screening.json` defines the next Phase 2B substage.
The dependency-free runner builds deterministic one-at-a-time Morris
trajectories in the normalized unit cube, maps uniform and log-uniform
coordinates through the Phase 2A parameter ranges, and reports elementary
effects plus `mu`, `mu_star`, and `sigma` separately for each metric, ligand
context class, and copy stratum.

Run a small verification slice before expanding to the full contract:

```bash
python -m src.modeling.ode.morris_screening \
  --parameter-id K_R \
  --parameter-id n_R \
  --parameter-id k_couple \
  --ligand-context transition_low_diagnostic \
  --copy-number 1 \
  --metric-id color_8h \
  --trajectory-count 4 \
  --out-dir /tmp/ode-phase2b-morris-slice
```

The slice is valid for verifying sampling, mapping, elementary-effect
bookkeeping, summary statistics, and reproducibility. Phase 2B continues with
full conditional Morris screening, conditional subset Sobol decomposition,
and focused equation-linked two-parameter surfaces.

The 17-parameter `L=0.3`, `N=1`, `color_8h` stability check selected 64
trajectories for conditional screening. Run the registered contexts, copy
strata, and active metrics with:

```bash
python -m src.modeling.ode.morris_screening \
  --trajectory-count 64 \
  --out-dir /tmp/ode-phase2b-morris-full
```

`configs/phase2b_sobol_sensitivity.json` registers the Morris-selected
eight-parameter subset, primary ligand contexts, extreme copy strata, color
metrics, deterministic scrambled-Sobol seed, bootstrap settings, and result
boundary. Running the command without an execution flag validates the contract
and design size only:

```bash
python -m src.modeling.ode.sobol_sensitivity
python -m src.modeling.ode.sobol_sensitivity --second-order
```

The first command validates `N * (D + 2) = 2560` rows per condition for S1/ST;
the second validates `N * (2D + 2) = 9216` rows per condition for S1/ST/S2.
ODE evaluation requires the explicit `--execute-ode` gate and a reviewed output
directory:

```bash
python -m src.modeling.ode.sobol_sensitivity \
  --execute-ode \
  --out-dir /tmp/ode-phase2b-sobol-pilot
```

The resulting indices partition variance within the selected eight-parameter
subset under fixed omitted parameters. The runner writes a sample manifest,
first/total indices with bootstrap intervals, optional second-order indices,
run metadata, and SHA-256 identities.

The first focused surface fixes `transition_reference`, `N=1`, and `color_8h`,
then evaluates a 7 x 7 registered-range grid for `gain_out x K_out`. Validate
the 49-point contract first; ODE execution requires the explicit gate:

```bash
python -m src.modeling.ode.focused_two_parameter_surface
python -m src.modeling.ode.focused_two_parameter_surface \
  --execute-ode \
  --out-dir /tmp/ode-phase2b-gain-by-half-surface
```

The CSV records the response and balanced-grid additive interaction residual;
the PNG shows both surfaces. Their allowed use is the fixed-condition
`scenario_prior` response shape registered in the config.

Run the ODE contracts without requiring `pytest`:

```bash
python -m unittest \
  tests.modeling.test_ode_minimal_solver \
  tests.modeling.test_ode_scenario_scans \
  tests.modeling.test_ode_phase2a_contract \
  tests.modeling.test_ode_local_sensitivity \
  tests.modeling.test_ode_morris_screening \
  tests.modeling.test_ode_sobol_sensitivity \
  tests.modeling.test_ode_focused_two_parameter_surface -v
```
