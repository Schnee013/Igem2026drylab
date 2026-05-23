# P2 Economic Benefit Stage 3 Benchmark Extraction

Date: 2026-05-23

Scope: full-text and method extraction for the next reliability layer of the P2
early-detection economic-benefit model. This document records external
benchmarks that can support model structure. It does not claim local ROI for the
project biosensor.

## Stage 3 Conclusion Boundary

Stage 3 strengthens the model's evidence base in three ways:

- PCN: Koehler et al. provides a usable external method and local-parameter
  benchmark for a PCN decision-support tool, including viable eggs/g soil,
  yield-loss slope, annual decline, cultivar determinacy, spring rainfall, and
  rotation logic.
- VOI: USDA ERS ERR-18 provides the cleanest worked method benchmark for early
  warning: information value is the difference between expected outcomes without
  information and expected outcomes with a signal.
- Density-yield: Mukhtar and Kayani 2020 provides a new full-text cucumber-RKN
  inoculum-to-fruit-yield-loss table. Barker et al. 1976 supports tomato-RKN
  reasonableness and environmental sensitivity.

Stage 3 does not change the current deterministic MVP. It is still valid only
for deterministic cost accounting and the UC IPM tomato-RKN public example. It
still cannot support a claim that the biosensor has validated positive ROI in a
target region.

## Benchmark Overview

| tier | source | role | current use |
|---|---|---|---|
| must_read | Koehler et al. 2021/2022, `10.1163/15685411-bja10138` | PCN method benchmark | enhanced PCN module design and local parameter check |
| must_read | USDA ERS ERR-18, 2006 | VOI method benchmark | future probabilistic information-value layer |
| must_read | Mukhtar and Kayani 2020, `10.1590/1678-4499.20190359` | cucumber-RKN density-yield benchmark | new scenario evidence after field conversion assumptions |
| must_read | Barker, Shoemaker, Nelson 1976, PMID `19308228` | tomato-RKN reasonableness check | external support for UC IPM table plausibility |
| strong_candidate | Contina et al. 2019, `10.1094/pdis-04-19-0717-re` | Idaho PCN predictive-risk model | candidate after legal full-text access |
| strong_candidate | Isik, Hudson, Coble 2005, `10.1016/j.jenvman.2005.01.024` | peer-reviewed site-specific information economics | secondary VOI/adoption benchmark after full-text access |
| strong_candidate | Kayani, Mukhtar, Hussain 2017, `10.1016/j.cropro.2016.09.007` | cucumber-RKN density and plant-age timing | preferred timing-value benchmark after legal full-text access |
| strong_candidate | Kayani, Mukhtar, Hussain 2018, `10.17582/journal.pjz/2018.50.3.897.902` | cucumber-RKN density and plant-age timing | triangulation after legal full-text access |
| strong_candidate | Heydari, Tanha Maafi, Pourjam 2012, `10.1163/156854111x614511` | soybean-SCN yield-loss candidate | SCN remains non-monetized until function extraction |
| pending_verification | Been/Schomaker 1998, `10.18174/194231` | PCN management and NemaDecide background | metadata/year conflict remains; extract only after legal full text and metadata check |
| background | EPPO, AHDB, USDA APHIS, UC IPM | official/extension context | threshold, severe-loss, and existing MVP baselines |

The structured source table is
`docs/papers/p2-economic-benefit/stage3-benchmark-evidence.csv`.

## 3A: PCN / NemaDecide Benchmark

### Selected Benchmark

The selected Stage 3 PCN benchmark is Koehler et al. 2021/2022:

- Title: Improving a pest management tool for scenario analysis of economic
  populations of `Globodera pallida`
- Authors: Ann-Kristin Koehler; Christopher A. Bell; Matthew A. Back; Peter E.
  Urwin; Howard J. Atkinson
- DOI: `10.1163/15685411-bja10138`
- Source type: peer-reviewed article; OA PDF retrieved from White Rose

This paper improves an AHDB-style PCN scenario tool and discusses NemaDecide as
an existing comparator. It is not a complete NemaDecide worked example, so the
benchmark status is: external tool method benchmark plus local parameter
validation, not complete NemaDecide reproduction.

### Extracted Model Inputs

The PCN tool input structure is directly relevant to an enhanced P2 potato
module:

| model input | extracted meaning | model alignment |
|---|---|---|
| `Pi` | viable eggs/g soil before planting | maps to density input |
| soil type | user-supplied agronomic condition | later scenario field |
| rotation length | years between potato crops | later multi-season layer |
| maximum yield without PCN | counterfactual yield | economic revenue baseline |
| cultivar tolerance/resistance or determinacy | crop response modifier | later scenario field |
| chemical control percentage | treatment effect modifier | later intervention module |
| annual decline rate | dormant population decline between host crops | later long-run PCN module |

Important extracted values:

- Pre-plant densities analyzed for the revised linear loss relation were in the
  limited range up to about 20 viable eggs/g soil.
- Yield-loss response is approximately linear over that limited range and varies
  roughly from about 0.2% to 2.0% yield loss per viable egg/g soil depending on
  cultivar determinacy and spring rainfall.
- The regression form is:
  `% yield loss per viable egg/g soil = b0 + b1 * determinacy + b2 * rainfall_mm`.
- Coefficients extracted from the paper:
  - `b0 = 0.02894`
  - `b1 = -0.00465`
  - `b2 = -0.00004237`
  - adjusted `R2 = 0.352`
- Field-level annual decline rate:
  - mean `20.4 +/- 1.4%`
  - field range about `4.0-39.7%` per year
- Cyst viable egg equation:
  - viable eggs/cyst = `1333.2 * cyst_area_mm2 - 52.829`

### Reliability Boundary

Koehler et al. is useful because it independently supports a density-driven PCN
loss structure and shows which modifiers matter. It also limits the model:

- It warns that multi-rotation predictions can compound error and create false
  precision.
- Its revised loss relationship is for `G. pallida`, UK potato contexts, and a
  limited `Pi` range.
- It does not provide a clean row-by-row worked example that can be copied into
  the current automated unit tests.

Therefore, Stage 3 should not add a new PCN ROI test yet. The next PCN code step
should wait until one complete worked example is extracted from Koehler
supplement, Contina full text, Been/Schomaker, AHDB calculator documentation, or
another legal source.

## 3B: VOI Method Benchmark

### Selected Benchmark

The selected Stage 3 VOI benchmark is:

- Title: The Value of Plant Disease Early-Warning Systems: A Case Study of
  USDA's Soybean Rust Coordinated Framework
- Authors: Michael J. Roberts; David Schimmelpfennig; Elizabeth Ashley; Michael
  Livingston; with Mark Ash and Utpal Vasavada
- Year: 2006
- Source type: USDA ERS official economic report

The report is not nematode-specific, but it is directly relevant to this
project's core economic claim: early warning is valuable when it changes a
farmer's decision before avoidable damage is locked in.

### Extracted VOI Structure

The minimum enhanced P2 VOI structure should be:

```text
VOI = E[cost_without_information] - E[cost_with_information]
```

or equivalently, in profit form:

```text
VOI = E[profit_with_information] - E[profit_without_information]
```

USDA ERS models three actions:

- preventive treatment;
- monitoring plus curative treatment;
- no management.

Without an information signal, the farmer chooses the strategy with the highest
expected value under prior infection probability `P`.

With an information signal:

- `b` is infection probability after a high-risk signal;
- `g` is infection probability after a low-risk signal;
- `a` is probability of receiving a high-risk signal;
- `P = a*b + (1-a)*g`.

The report also defines an information-quality parameter `f`:

- `b = f(1-P) + P`
- `g = P(1-f)`
- in the report's simplifying construction, `a = P`

Worked numeric check from the report:

- Corn Belt representative farm, `P = 0.60`, `f = 0.8`
- expected value without information: `92,366`
- expected value with information: `97,098`
- information value: `4,731/farm`, or `6.38/acre`

The report also estimates that the 2005 framework increased soybean producer
profits by `$11-$299 million`, or `$0.16-$4.12/acre`, against reported framework
costs of `$2.6M` to almost `$5M`.

### Model Boundary

This VOI layer should be added later as a probabilistic enhancement, not merged
into the current deterministic MVP. For the biosensor case, `f`, sensitivity,
specificity, prior infestation risk, sampling error, detection interval, and
response actions must be supplied by wet-lab/P1/HP evidence before the VOI layer
is calibrated.

## 3C: SCN / Cucumber / RKN Density-Yield Functions

### New Density-Yield Benchmark: Cucumber-RKN

The strongest new full-text density-yield benchmark extracted in Stage 3 is:

- Title: Comparison of the damaging effects of `Meloidogyne incognita` on a
  resistant and susceptible cultivar of cucumber
- Authors: Tariq Mukhtar; Muhammad Zameer Kayani
- Year: 2020
- DOI: `10.1590/1678-4499.20190359`
- Source type: peer-reviewed open-access article, Bragantia / SciELO

Methods relevant to modeling:

- `M. incognita` was isolated from cucumber roots and maintained on tomato
  Money Maker.
- Plants were inoculated ten days after emergence.
- Inoculum levels were freshly hatched J2 at `250`, `500`, `1000`, `2000`,
  `4000`, and `8000` per plant/pot.
- Greenhouse temperature was `25 +/- 2 C`.
- The methods describe five replications per inoculum level and one repeat of
  the experiment; table footnotes report means of ten replicates after pooling.

Extracted fruit-yield-loss table:

| inoculum level | Mirage susceptible: % fruit-yield decrease | Long Green resistant: % fruit-yield decrease |
|---:|---:|---:|
| 250 | 3.7 +/- 0.43 | 0.7 +/- 0.13 |
| 500 | 5.2 +/- 0.67 | 1.1 +/- 0.32 |
| 1000 | 11.3 +/- 1.32 | 3.4 +/- 0.45 |
| 2000 | 13.9 +/- 1.43 | 6.3 +/- 0.66 |
| 4000 | 24.8 +/- 1.93 | 7.9 +/- 0.75 |
| 8000 | 40.6 +/- 2.23 | 11.4 +/- 1.24 |

Regression equations reported for fruit yield:

- Mirage: `y = 7.0257x - 8.0067`, `R2 = 0.886`
- Long Green: `y = 2.1943x - 2.5467`, `R2 = 0.9661`

Important limitation: the regression `x` appears to be an inoculum-level
category/index, not field density in J2/kg soil. This source can support a
cucumber greenhouse scenario and relative resistant-vs-susceptible comparison,
but it must not be directly treated as a field soil density function without a
conversion assumption.

### Tomato-RKN Reasonableness Check

Barker, Shoemaker, and Nelson 1976 remains an external reasonableness check for
the UC IPM tomato-RKN table:

- Title: Relationships of initial population densities of `Meloidogyne
  incognita` and `M. hapla` to yield of tomato
- Authors: K. R. Barker; P. B. Shoemaker; L. A. Nelson
- Year: 1976
- PMID: `19308228`; PMCID: `PMC2620177`
- Source type: peer-reviewed article

Extracted relevance:

- Microplots were `80 x 100 cm`.
- Initial population density was reported as eggs and larvae per `500 cm3` soil,
  and in a second experiment up to `25,000/50 cm3` soil.
- Mountain sandy-loam site losses were about `20-30%` at `0-12,500/500 cm3`.
- Coastal-plain site losses were much more severe: `M. incognita` suppressed
  yield up to `85%`, and `M. hapla` up to `50%`.
- Approximate threshold densities were `500-1000` eggs and larvae/`500 cm3` at
  the mountain site, but as low as `20 larvae/500 cm3` at the coastal-plain site.

This supports the idea that tomato-RKN yield loss is strongly environment- and
site-dependent. It does not replace the current UC IPM golden baseline because
UC IPM provides the direct table and economic values used in the automated
MVP tests.

### SCN Status

The Stage 3 SCN candidate should be recorded as:

- Title: Yield loss caused by soybean cyst nematode, `Heterodera glycines`, in
  Iran
- Authors: Ramin Heydari; Zahra Tanha Maafi; Ebrahim Pourjam
- DOI: `10.1163/156854111x614511`
- Source type: peer-reviewed article

The original plan referred to this as Hajihassani et al. 2012. Current metadata
verification points instead to Heydari, Tanha Maafi, and Pourjam. Until full
text is legally retrieved and the density-yield function is extracted, SCN stays
threshold-only and non-monetized in the P2 model.

## Impact On Model Structure

### Current MVP

No change. The current MVP remains deterministic cost accounting:

```text
gross_loss = baseline_yield * market_price * yield_loss_fraction
avoided_loss = gross_loss * intervention_effect
net_benefit = avoided_loss - early_program_cost
roi = net_benefit / early_program_cost
```

It is validated only against the UC IPM tomato-RKN public arithmetic baseline
and internal guardrails.

### Enhanced Version

Add only after the relevant benchmark is complete enough for implementation:

- PCN module with `Pi`, cultivar determinacy/tolerance, spring rainfall, annual
  decline, rotation length, and chemical control effect.
- VOI module with prior risk, signal quality, sensitivity/specificity or
  equivalent forecast-quality parameter, and strategy-dependent expected costs.
- Additional density-yield functions for cucumber-RKN and later SCN, but only
  with explicit unit conversions and field/local crop economics.

### Wiki Demonstration Version

Use Stage 3 qualitatively:

- show that PCN decision tools already use egg density, cultivar response,
  rainfall, rotation, and chemical control;
- show that early-warning economics has a published expected-value framework;
- show cucumber/tomato RKN density-response examples, while clearly labeling
  greenhouse vs field and extension vs peer-reviewed evidence.

## Do Not Claim

- Do not claim the biosensor has validated local ROI.
- Do not use docking Delta G, ODE Kd, or unverified wet-lab assumptions as
  economic constants.
- Do not monetize SCN until a full density-yield function is extracted.
- Do not treat Koehler/AHDB/NemaDecide long-rotation outputs as high-precision
  forecasts without error propagation.
- Do not convert cucumber pot inoculum directly to field J2/kg soil without
  stating assumptions.

## Next Steps

1. Obtain legal full text or institutional access for Contina 2019, Kayani 2017,
   Kayani/Mukhtar/Hussain 2018, Isik/Hudson/Coble 2005, and Heydari/Tanha
   Maafi/Pourjam 2012.
2. Search Koehler supplementary data and AHDB calculator documentation for one
   complete PCN worked example that can become an automated test.
3. When P1 Bayesian or wet-lab detection performance data exists, implement VOI
   as a separate probabilistic layer rather than altering deterministic MVP
   accounting.
4. When HP parameters return, create local calibration configs for sensor cost,
   deployment density, crop price/yield, intervention cost/effect, and farmer
   willingness to pay.
