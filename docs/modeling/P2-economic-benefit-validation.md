# P2 Economic Benefit Framework Validation

Date: 2026-05-23

Scope: validation of the deterministic cost-accounting framework for the P2
early-detection economic-benefit model. This validates arithmetic, source-value
plumbing, and guardrails against unsupported ROI claims. It does not calibrate
local economics.

## Validation Claim

The current MVP is reliable for these limited claims:

- It can reproduce public UC IPM tomato-RKN partial-budget arithmetic.
- It correctly converts density-to-percent-normal-yield tables into revenue
  loss.
- It correctly calculates avoided loss, break-even early-program cost, net
  benefit, and ROI for configured scenario sweeps.
- It intentionally refuses to monetize threshold-only soybean-SCN rows until a
  density-yield function is extracted.

The current MVP is not yet reliable for these claims:

- final ROI for the project biosensor;
- local China or target-region economics;
- true field value of early detection under sampling error and sensor
  sensitivity/specificity;
- calibrated intervention efficacy for a specific nematicide, resistant variety,
  rotation, or biocontrol workflow.

Those require HP, wet-lab, local market, and additional full-text benchmark
inputs.

## Source Baselines

| baseline | source | source type | validation use | current status |
|---|---|---|---|---|
| UC IPM tomato-RKN yield table | UC IPM Tomato Root-Knot Nematode Pest Management Guidelines | extension | golden arithmetic and piecewise table validation | implemented in tests |
| UC IPM tomato example economics | same UC IPM page: 30 tons/acre and 54 USD/ton example values plus the table point 200 spring J2/kg soil -> 88% normal yield | extension | computed golden arithmetic baseline: 30 * 54 * 12% = 194.40 USD/acre | implemented in tests |
| Current tomato 500 J2/kg public scenario | same UC IPM table plus configured 500 J2/kg point | extension-derived scenario | framework smoke scenario and break-even sweep | implemented in tests |
| EPPO PCN loss slope | EPPO Globodera pallida datasheet citing about 2 t/ha lost per 20 eggs/g soil | official/regulatory datasheet | normalized linear density-loss structure check | implemented as structural test only |
| UMN/ISU SCN threshold guidance | UMN Extension and Iowa State Extension | extension | threshold-only decision skeleton and no-monetization guardrail | implemented as guardrail test |
| NemaDecide / PCN decision-support literature | Koehler et al. 2021/2022; Contina et al. 2019; Been and Schomaker 1998; related PCN tools | peer-reviewed / dissertation / decision-support precedent | external benchmark for enhanced PCN decision model | Koehler method/local-parameter benchmark extracted; complete worked example still pending |
| Soybean rust early-warning / site-specific information economics | USDA ERS soybean rust framework; Isik et al. 2005 | official report / peer-reviewed economics | value-of-information structure benchmark | USDA ERS method and numeric examples extracted; Isik full text pending |
| Cucumber-RKN density-yield table | Mukhtar and Kayani 2020 Bragantia | peer-reviewed OA | additional density-yield benchmark for later cucumber scenario | full table extracted; field-unit conversion pending |
| Tomato-RKN classic microplot study | Barker, Shoemaker, Nelson 1976 | peer-reviewed | external reasonableness check for UC IPM tomato-RKN table | full-text abstract/method values extracted; not replacing UC IPM golden baseline |

## Automated Tests

Command:

```bash
python3 -m unittest tests.modeling.test_economic_model -v
```

Current result:

```text
Ran 14 tests in 0.001s
OK
```

Coverage:

| test area | what it checks |
|---|---|
| UC IPM table points | 0, 25, 50, 200, 500, and 1000 spring J2/kg soil map to the configured percent-normal-yield values |
| interpolation | between-table values are linearly interpolated |
| endpoint clamp | values outside the UC IPM table range are clamped rather than extrapolated |
| UC IPM 200 J2/kg golden baseline | computed from UC IPM table/example values: `30 * 54 * 0.12 = 194.40 USD/acre`; 50% avoided loss gives 97.20 USD/acre break-even early-program cost |
| tomato 500 J2/kg public example | `30 * 54 * 0.28 = 453.60 USD/acre`; 25/50/75% avoided-loss break-even costs are 113.40/226.80/340.20 USD/acre |
| accounting identities | monetized rows satisfy residual loss, break-even, net benefit, and ROI identities |
| intervention-effect clamp | out-of-range intervention effects are clamped to 0-1 |
| zero early cost | net benefit can be computed, but ROI is left blank to avoid division by zero |
| PCN normalized slope | EPPO-style 2 t/ha per 20 eggs/g structure maps to configured 4.4444% normalized loss |
| loss cap | linear loss rules respect `max_loss_fraction` |
| invalid rules | empty piecewise tables and nonpositive linear density increments are rejected |
| SCN threshold-only guardrail | soybean-SCN rows do not emit monetary loss, net benefit, or ROI |
| config coverage | public config still emits 21 rows across tomato-RKN, potato-PCN, and soybean-SCN |

## Output Reproducibility Check

Command:

```bash
python3 src/modeling/economic/run_mvp.py \
  --config experiments/economic/configs/public_mvp_framework.json \
  --out /private/tmp/p2_public_mvp_framework_results_validation.csv
```

Then:

```bash
cmp -s experiments/economic/results/public_mvp_framework_results.csv \
  /private/tmp/p2_public_mvp_framework_results_validation.csv
```

Result: the regenerated public MVP output matches the committed CSV exactly.

## Interpretation

This validation is enough to say:

> The deterministic cost-accounting framework and the UC IPM public example are
> arithmetically reproducible.

It is not enough to say:

> The biosensor has a validated positive ROI in the target deployment region.

The validated baseline is a public extension example for processing tomato in a
specific UC IPM context. It should remain a framework benchmark until local
yield, price, sensor cost, deployment density, sensor performance, and
intervention cost/effect are supplied.

## Stage 3 External Benchmark Extraction

Stage 3 added external evidence for the next reliability layer:

- PCN / NemaDecide: Koehler et al. 2021/2022 supports a PCN decision-support
  structure using `Pi` viable eggs/g soil, maximum yield without PCN, cultivar
  response, chemical control, annual decline, rotation length, determinacy, and
  spring rainfall. It is a method/local-parameter benchmark, not a complete
  NemaDecide reproduction.
- VOI: USDA ERS ERR-18 supports defining the enhanced information layer as
  `E[cost_without_information] - E[cost_with_information]` or the equivalent
  expected-profit difference. Its Appendix provides worked values for signal
  quality and prior infection probability.
- Density-yield: Mukhtar and Kayani 2020 provides a cucumber-RKN greenhouse
  inoculum-to-fruit-yield-loss table; Barker et al. 1976 provides tomato-RKN
  environmental-sensitivity checks.

These benchmarks are documented in
`docs/papers/p2-economic-benefit/stage3-benchmark-extraction.md` and
`docs/papers/p2-economic-benefit/stage3-benchmark-evidence.csv`.

No new code, public config, or automated tests were added from Stage 3 because
the newly extracted material does not yet provide a complete, legal, row-by-row
external worked example comparable to the current UC IPM tomato-RKN golden
baseline. The current automated test suite remains a deterministic MVP
validation suite, not a calibrated probabilistic VOI or PCN decision-tool
validation suite.

## Remaining Benchmark Work

1. Find one complete legal PCN worked example from Koehler supplementary data,
   AHDB calculator documentation, Contina 2019 full text, or Been/Schomaker.
2. Implement a separate VOI layer only after detection-performance and sampling
   uncertainty parameters exist.
3. Extract soybean-SCN full density-yield functions before monetizing soybean
   rows.
4. Add tests for false positives, false negatives, repeated testing, and
   sampling error only after wet-lab/P1 Bayesian parameters exist.
