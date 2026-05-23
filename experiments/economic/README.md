# P2 Economic Benefit Framework

Date: 2026-05-21

This folder holds the first framework-only implementation for the P2 early-detection economic benefit model.

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

These remain HP/wet-lab or full-text extraction inputs. Do not present ROI values as final project claims until those values are filled.

## Run

```bash
python3 src/modeling/economic/run_mvp.py \
  --config experiments/economic/configs/public_mvp_framework.json \
  --out experiments/economic/results/public_mvp_framework_results.csv
```

## Current Inputs

- `experiments/economic/configs/public_mvp_framework.json`
- Source matrix: `docs/papers/p2-economic-benefit/stage2-model-parameters.csv`

## Current Output

- `experiments/economic/results/public_mvp_framework_results.csv`
- `experiments/economic/results/public_mvp_framework_summary.md`
