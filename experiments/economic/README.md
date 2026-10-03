# P2 Economic Benefit Models

Last updated: 2026-10-04

This folder holds two complementary implementations for the P2 early-detection
economic benefit model:

- the original framework-only public MVP; and
- a literature-backed demonstration for Spanish protected tomato and southern
  root-knot nematode (*Meloidogyne incognita*).

## What Is Implemented

- Deterministic cost-accounting MVP runner.
- Yield-loss rules:
  - piecewise density -> percent-normal-yield tables;
  - linear density -> yield-loss approximations;
  - threshold-only skeleton rows when no yield-loss function is ready.
- Intervention-effect sweep for break-even early-detection program cost.
- CSV output suitable for HP discussion and later plotting.

## What Is Not Yet Fixed

- Biosensor unit cost.
- Biosensor deployment density.
- Field sensitivity/specificity.
- Local lab delay and local lab price.
- Product price, application labor, resistant-seed premium, and rotation opportunity cost.
- Final soybean-SCN density-yield curve.

These remain HP/wet-lab or full-text extraction inputs for generalization beyond
the fixed Spanish demonstration. Do not present either implementation as a
field prescription or a universally calibrated ROI model.

## Run

### Public framework MVP

```bash
python3 src/modeling/economic/run_mvp.py \
  --config experiments/economic/configs/public_mvp_framework.json \
  --out experiments/economic/results/public_mvp_framework_results.csv
```

### Spanish protected-tomato demonstration

```bash
python3 src/modeling/economic/eco_model.py
```

The command reads the tracked example configuration and density input, then
writes TXT, JSON, Chinese HTML, and English HTML reports to
`experiments/economic/results/eco_model/`. It does not open a browser by
default. Pass `--open` only when the Chinese HTML report should be opened after
generation.

Useful variants:

```bash
python3 src/modeling/economic/eco_model.py 100 --no-report
python3 -m src.modeling.economic.eco_model_pkg.cli --help
```

## Current Inputs

- `experiments/economic/configs/public_mvp_framework.json`
- `experiments/economic/configs/eco_model_example_model.json`
- `experiments/economic/configs/eco_model_example_input.json`
- Source matrix: `docs/papers/p2-economic-benefit/stage2-model-parameters.csv`

## Current Output

- `experiments/economic/results/public_mvp_framework_results.csv`
- `experiments/economic/results/public_mvp_framework_summary.md`
- Regenerable bilingual demonstration reports:
  `experiments/economic/results/eco_model/`

## Validation

The current framework validation is documented in:

- `docs/modeling/P2-economic-benefit-validation.md`

Run the automated arithmetic and guardrail checks with:

```bash
python3 -m unittest tests.modeling.test_economic_model -v
python3 -m unittest tests.modeling.test_eco_model -v
```

The tests validate UC IPM public tomato-RKN arithmetic, piecewise interpolation,
PCN normalized structure, threshold-only SCN guardrails, and cost-accounting
identities. They do not validate final biosensor ROI.

The demonstration tests additionally validate the Seinhorst density-loss
function, treatment thresholds, economic accounting, configuration guardrails,
and parity between the Chinese and English report structures. The demonstration
uses only the Python standard library.
