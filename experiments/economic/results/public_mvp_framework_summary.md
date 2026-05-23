# Public MVP Framework Run Summary

Date: 2026-05-21

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/modeling/economic/run_mvp.py \
  --config experiments/economic/configs/public_mvp_framework.json \
  --out experiments/economic/results/public_mvp_framework_results.csv
```

Output: `experiments/economic/results/public_mvp_framework_results.csv`

## What The Run Shows

This is a framework smoke run, not a final ROI claim.

## Comparator Baseline

The comparator is a late-discovery / no-early-field-detection scenario. In the
current MVP, that baseline is represented as gross revenue loss at the configured
nematode density:

`gross_loss = baseline_yield_per_area * crop_price_per_yield_unit * yield_loss_fraction`

The early-detection side is not yet calibrated to the real biosensor. Instead,
the run sweeps placeholder early-program costs and placeholder intervention
effects:

- `early_program_cost_per_area`: stand-in for sensor deployment, sampling, and
  timely intervention cost;
- `intervention_effect`: fraction of late-scenario revenue loss avoided by early
  detection plus timely intervention;
- `break_even_early_program_cost_per_area`: the maximum early-program cost that
  would still break even for that intervention effect.

This baseline is valid for checking model arithmetic and evidence plumbing
because all monetary tomato values are traceable to the UC IPM public example.
It is not valid as a final project benefit claim until HP/local values replace
the public example yield, price, intervention cost, deployment density, and
sensor performance.

### Tomato-RKN public example

Source basis: UC IPM tomato root-knot nematode spring J2/kg soil table.

Configured example:

- density: 500 spring J2/kg soil
- normal yield at that density: 72%
- yield loss fraction: 28%
- source example yield: 30 source tons/acre
- source example price: 54 USD/source ton
- gross late-scenario revenue loss: 453.6 USD/acre

Break-even early-program cost per acre under the intervention-effect sweep:

| intervention effect | break-even early-program cost |
|---:|---:|
| 25% avoided loss | 113.4 USD/acre |
| 50% avoided loss | 226.8 USD/acre |
| 75% avoided loss | 340.2 USD/acre |

Interpretation: before HP data, this is the most defensible public demonstration of the cost-accounting structure. Replace yield, price, intervention cost, sensor cost, and deployment density before making project-specific ROI claims.

### Potato-PCN normalized example

Source basis: EPPO Globodera pallida datasheet parameter, approximately 2 t/ha lost per 20 eggs/g soil.

Configured example:

- density: 20 eggs/g soil
- normalized yield-loss fraction: 4.4444%
- currency: normalized

Interpretation: this confirms the framework can consume the EPPO-style linear density-loss approximation. It is not a local potato ROI result until target-region yield and price are supplied.

### Soybean-SCN threshold skeleton

Source basis: UMN Extension SCN threshold bands.

Configured example:

- density: 10000 eggs/100 cc soil
- rule type: threshold-only
- monetary output: intentionally blank

Interpretation: SCN has threshold/action evidence, sampling-error evidence, and lab-cost evidence, but still needs a full density-yield curve before soybean ROI can be calculated.

## Current Blockers For Final ROI

- biosensor unit cost;
- tests per hectare / deployment spacing;
- field sensitivity and specificity;
- local crop price and baseline yield;
- local lab cost and delay;
- intervention cost and effect in the chosen region;
- farmer willingness to pay;
- SCN/RKN/PCN full-text table extraction for stronger crop-specific calibration.
