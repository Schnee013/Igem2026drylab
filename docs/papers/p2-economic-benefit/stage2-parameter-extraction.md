# P2 Early-Detection Economic Benefit: Stage 2 Parameter Extraction

Date: 2026-05-21
Durable location: `docs/papers/p2-economic-benefit/stage2-parameter-extraction.md`
Temporary run source: `tmp_papers/p2_economic_benefit_20260521/stage2_parameter_extraction.md`

Scope: convert the Stage 1 paper/data matrix into model-usable candidate parameters for the later Python economic model. This stage does not implement model code. It also does not treat docking Delta G, ODE Kd, or unverified wet-lab assumptions as fixed economic inputs; those remain scenario or interface variables only.

Primary Stage 1 artifact: `docs/papers/p2-economic-benefit/stage1-paper-data-matrix.md`

## Stage 2 Boundaries

- Use directly extracted values only when the source is a verified official/extension page, lab fee page, pesticide label, or a peer-reviewed paper with accessible metadata and clear parameter statement.
- Treat peer-reviewed density-yield papers as high-priority but not fully calibrated unless their tables/equations have been extracted from full text.
- Keep China/local scenarios open. U.S./EU/UK sources are strong for method and parameter priors, but HP/local interviews must supply region-specific cost, price, availability, and adoption values.
- Keep the economic model independent. P1 diffusion, P1 Bayesian inference, P2 dose-response, and P0 ODE can enhance deployment density, density posterior, intervention effect, and detection threshold, but they are not required for the MVP.

## Key Extraction Result

The strongest MVP path is deterministic cost accounting with three crop scenarios:

1. soybean + soybean cyst nematode (SCN, `Heterodera glycines`);
2. processing tomato or cucumber + root-knot nematode (RKN, mainly `Meloidogyne incognita`);
3. potato + potato cyst nematode (PCN, `Globodera pallida` / `G. rostochiensis`).

Among these, tomato-RKN and potato-PCN currently have the most directly numeric density-to-loss parameters from extension/regulatory sources. Soybean-SCN has strong threshold and diagnostic-cost evidence, but the density-to-yield-loss curve still needs full-text extraction from peer-reviewed papers such as Hajihassani et al. 2012.

## Directly Model-Ready Parameters

### Cross-Scenario Inputs

| parameter_id | candidate value | unit | source type | model use | status |
|---|---:|---|---|---|---|
| baseline_yield | pull by crop-region-year | t/ha, bu/ac, tons/ac | official statistics | expected yield without nematode damage | model-ready data source |
| crop_price | pull by crop-region-year | USD/t, USD/bu, local currency/t | official statistics | crop value calculation | model-ready data source |
| lab_test_cost_general | 10-50 | USD/sample | official/university lab | comparator cost for current diagnostics | directly extracted |
| molecular_test_cost_general | 40-100+ | USD/sample | official/university lab | qPCR/molecular comparator | directly extracted |
| lab_turnaround_fast | 4-7 | days after receipt | university lab | current best-case delay | directly extracted |
| lab_turnaround_slow | 14-56 | days | official lab | peak-season / off-season delay | directly extracted |
| field_area_per_lab_sample | 10-20 acres | acre/sample | extension/lab guidance | sampling cost multiplier | directly extracted |
| subsamples_per_lab_sample | 10-20 or about 20 | subsamples/sample | extension/lab guidance | sampling labor proxy | directly extracted |
| sensor_unit_cost | TBD | USD/test | team/HP | proposed product cost | HP/wet-lab required |
| sensor_tests_per_ha | TBD | tests/ha | P1 diffusion + HP | deployment density | HP/P1 required |
| sensor_sensitivity_specificity | TBD | probability | wet-lab/P1 Bayesian | false negative / false positive economics | wet-lab required |

### Soybean + SCN

| parameter_id | candidate value | unit | source type | model use | status |
|---|---:|---|---|---|---|
| scn_low_damage_boundary | 200 | eggs/100 cc soil | extension | low-risk threshold band | directly extracted |
| scn_resistant_variety_band | 200-10000 | eggs/100 cc soil | extension | management action band | directly extracted |
| scn_high_nonhost_boundary | >=10000 | eggs/100 cc soil | extension | high-pressure intervention rule | directly extracted |
| scn_nonhost_decline | about 50 | %/year | extension | enhanced rotation population decline | directly extracted |
| scn_high_to_low_rotation_time | about 5 | years | extension | long-run management scenario | directly extracted |
| scn_sample_variability | 100-300 | % variation | extension | observation-error prior | directly extracted |
| scn_lab_egg_count_cost | 21-35 | USD/sample | university lab | lab comparator | directly extracted |
| scn_subsamples | 10-20 or about 20 | locations/sample | university/extension | sampling labor proxy | directly extracted |
| scn_density_yield_function | TBD | yield loss vs eggs/soil | peer-reviewed | yield-loss curve | full-text extraction required |

SCN is strong for "why early screening matters": populations are uneven and can remain unnoticed, test results vary sharply, and management depends on egg-density bands. The current weak point is a model-ready yield-loss curve by eggs/100 cc soil.

### Tomato/Cucumber + RKN

| parameter_id | candidate value | unit | source type | model use | status |
|---|---:|---|---|---|---|
| tomato_rkn_yield_table_spring | 0-25:100; 50:98; 100:95; 150:91; 200:88; 250:85; 300:82; 350:79; 400:77; 450:74; 500:72; 550:69; 600:67; 650:65; 700:63; 750:61; 800:60; 850:58; 900:56; 950:55; 1000:53 | spring J2/kg soil -> % normal yield | extension | direct piecewise yield-loss table | directly extracted |
| tomato_rkn_yield_table_fall | 0-160:100; 310:98; 620:95; 940:91; 1250:88; 1560:85; 1870:82; 2190:79; 2500:77; 2810:74; 3120:72; 3440:69; 3750:67; 4060:65; 4370:63; 4690:61; 5000:60; 5310:58; 5620:56; 5920:55; 6250:53 | fall J2/kg soil -> % normal yield | extension | direct piecewise yield-loss table | directly extracted |
| tomato_rkn_lab_recovery_rate | 10-30 | % recovered | extension | adjust extracted J2 to estimated total J2 | directly extracted |
| tomato_rkn_lab_turnaround | about 14 | days | extension | current lab delay | directly extracted |
| tomato_rkn_sampling_area | <=10 | acre/block | extension | sampling cost multiplier | directly extracted |
| tomato_rkn_subsamples | >=20 | places/block | extension | sampling labor proxy | directly extracted |
| tomato_rkn_example_yield | 30 | tons/acre | extension example | illustrative economics only | scenario/example |
| tomato_rkn_example_price | 54 | USD/ton | extension example | illustrative economics only | scenario/example |
| tomato_rkn_classic_threshold | 20 to 1000 | eggs+larvae/500 cm3 soil | peer-reviewed | environment-sensitive threshold range | metadata verified; full text recommended |
| cucumber_rkn_density_exposure | 500-8000 | J2 inoculum | peer-reviewed | early-vs-late exposure relation | full-text extraction required |

Tomato-RKN is the cleanest MVP crop because UC IPM gives a direct density-to-yield table and an example net-return calculation. Cucumber is still useful for HP narrative because Kayani et al. directly addresses plant age and nematode density, but exact yield-loss percentages need full-text extraction.

### Potato + PCN

| parameter_id | candidate value | unit | source type | model use | status |
|---|---:|---|---|---|---|
| pcn_damage_threshold | 1-2 | eggs/g soil | regulatory datasheet | threshold for economic damage | directly extracted |
| pcn_loss_slope | about 2 | t/ha lost per 20 eggs/g soil | regulatory datasheet citing Brown 1969 | linear approximation / sensitivity analysis | directly extracted but should trace original |
| pcn_high_loss_upper | up to 80 | % crop loss | regulatory datasheet | severe scenario cap | directly extracted |
| pcn_uk_trial_loss | 1-35 | % yield loss | levy-board guide | trial-calibrated loss band at 10-20 eggs/g | directly extracted |
| pcn_uk_trial_density | 10-20 | eggs/g soil | levy-board guide | density band paired with loss range | directly extracted |
| pcn_unchecked_loss | 20-70 | % yield loss | USDA APHIS | late/uncontrolled scenario | directly extracted |
| pcn_viable_dormancy | up to 30 | years | USDA APHIS | long-term late-detection risk | directly extracted |
| pcn_eggs_per_cyst | 300-500 | eggs/cyst | USDA APHIS | population growth / narrative | directly extracted |
| pcn_rotation_common | 6-7 | potato-free years | regulatory datasheet | enhanced long-run management | directly extracted |
| pcn_decision_tool_precedent | NemaDecide / economic population scenario tool | n/a | regulatory + peer-reviewed | enhanced model inspiration | verified; implementation later |

Potato-PCN is strong for a Wiki/HP story because early detection affects both yield and regulatory/quarantine risk. The MVP can use EPPO and AHDB values, but the enhanced model should later trace Brown 1969 and extract equations from Contina 2019 and Koehler 2021.

### Intervention Cost And Effect

| parameter_id | candidate value | unit | source type | model use | status |
|---|---:|---|---|---|---|
| fluazaindolizine_tomato_rate_preplant | 30.7-61.4 | fl oz product/acre | EPA label | treatment cost = label rate x product price | directly extracted label rate |
| fluazaindolizine_tomato_rate_inseason | 15.4-30.7 | fl oz product/acre | EPA label | treatment cost scenario | directly extracted label rate |
| fluazaindolizine_potato_rate_preplant | 30.7-61.4 | fl oz product/acre | EPA label | treatment cost = label rate x product price | directly extracted label rate |
| fluazaindolizine_potato_rate_infurrow | 15.4-61.4 | fl oz product/acre | EPA label | treatment cost scenario | directly extracted label rate |
| fluazaindolizine_potato_rate_inseason | 15.4-30.7 | fl oz product/acre | EPA label | treatment cost scenario | directly extracted label rate |
| chemical_product_price | TBD | USD/fl oz or USD/L | distributor/HP/local market | treatment cost | HP/local market required |
| application_labor_cost | TBD | USD/ha | HP/local budget | treatment cost | HP/local market required |
| resistant_seed_premium | TBD | USD/ha or USD/bag | HP/seed budget | soybean/tomato intervention cost | HP/local market required |
| rotation_opportunity_cost | TBD | USD/ha-season | crop budget/HP | nonhost-year cost | HP/local budget required |

Label rates can support cost formulas, but they are not prices. The model should not report nematicide ROI until product price and application cost are sourced for the selected region.

## Parameters Not Yet Model-Ready

| gap | why it matters | recommended next source |
|---|---|---|
| SCN density-to-yield function | needed to convert eggs/100 cc to soybean revenue loss | full text of Hajihassani et al. 2012; Acharya et al. 2022 for management effects |
| Cucumber RKN yield-loss percentages by plant age | needed for "early detection saves time" claim | full text of Kayani et al. 2017 and Mukhtar et al. 2018 |
| PCN equations from risk/economic tools | needed for enhanced model beyond linear slope | Contina et al. 2019; Koehler et al. 2021; Been and Schomaker 1998 dissertation |
| Local crop price/yield/cost | determines ROI magnitude | USDA/FAOSTAT pull for public scenario; HP/local market data for China-facing scenario |
| Biosensor unit economics | core cost in early-detection scenario | HP + wet-lab bill of materials + prototype workflow |
| Deployment density | converts per-test cost to per-ha cost | P1 diffusion radius/spacing + HP user workflow |
| Field diagnostic performance | determines false-negative and false-positive costs | wet-lab validation + P1 Bayesian observation model |
| Regulatory feasibility for living yeast field deployment | affects implementation path and cost | HP/regulatory interviews; local biosafety constraints |

## MVP Parameter Configuration Recommendation

The first Python MVP should load a CSV/JSON config with:

- `scenario_id`: `soybean_scn`, `tomato_rkn`, `potato_pcn`;
- `area_ha`;
- `baseline_yield` and `crop_price`;
- `density_input` in the source unit for each scenario;
- `yield_loss_rule`: threshold band, piecewise table, or linear slope;
- `diagnostic_cost_per_sample`;
- `samples_per_ha` or `field_area_per_sample`;
- `diagnostic_delay_days`;
- `intervention_cost_per_ha`;
- `intervention_effect_on_loss` or `intervention_effect_on_density`;
- `sensor_unit_cost`, `sensor_tests_per_ha`, `sensor_sensitivity`, `sensor_specificity` as scenario variables rather than fixed facts.

For first plots, do not force a single "correct" sensor cost. Use break-even curves:

`break_even_sensor_cost_per_ha = loss_late - intervention_cost - residual_loss_early`

Then divide by `tests_per_ha` only when P1/HP gives deployment density.

## Economic Model Structure Update

### MVP

Use deterministic cost accounting:

`revenue_loss = baseline_yield * crop_price * yield_loss_fraction`

`late_scenario_cost = lab_cost_optional + revenue_loss_late + late_intervention_cost`

`early_scenario_cost = sensor_cost + sampling_labor + early_intervention_cost + residual_revenue_loss`

`net_benefit = late_scenario_cost - early_scenario_cost`

`roi = net_benefit / (sensor_cost + early_intervention_cost)`

Do not include stochastic posterior density or diffusion spacing yet.

### Enhanced Version

Add:

- density posterior from P1 Bayesian inference;
- sampling-error multiplier for lab and sensor;
- field deployment density from P1 soil diffusion;
- intervention efficacy from P2 dose-response;
- Monte Carlo draws over price, yield, density, efficacy, and false-negative rate;
- value-of-information output: `E[cost_without_information] - E[cost_with_information]`.

### Wiki Version

Use three visual examples:

1. Tomato-RKN: direct density-to-yield table and break-even treatment example.
2. Potato-PCN: low egg/g threshold and large severe-loss risk.
3. Soybean-SCN: threshold-band decision tree, showing why cheap repeated screening can be valuable even before exact yield-loss calibration.

Label all prototype inputs as assumptions: sensor cost, detection radius, sensor false-negative rate, and user adoption/payment threshold.

## Source-Type Classification

- Peer-reviewed / academic: Barker et al. 1976; Hajihassani et al. 2012; Kayani et al. 2017; Acharya et al. 2022; Sasanelli et al. 2020; Contina et al. 2019; Koehler et al. 2021; Isik et al. 2005; Welsh et al. 2021. Been and Schomaker 1998 is a verified dissertation, not a peer-reviewed article.
- Official government / regulatory / statistics: FAO, USDA APHIS, USDA ERS, USDA NASS QuickStats, FAOSTAT, EPPO, U.S. EPA label, NCDA.
- Extension / university / levy-board: UMN Extension, Iowa State Extension/PIDC, UMN SROC, Penn State, UC IPM, AHDB, Cornell.
- Industry or estimates: product/vendor pages and newsletter examples. Use only for qualitative precedent or temporary assumptions unless price data can be traced.

## Zotero / Full-Text Note

The Stage 2 extraction did not depend on Zotero full text. Searches through the Zotero MCP for several key papers returned no matching library items, and one query hit an SSL EOF error. Therefore, the peer-reviewed rows marked `full_text_required` remain a manual download/Zotero-import queue rather than extracted full-text evidence.

## Next Stage

1. Extract tables/equations from full texts for Hajihassani 2012, Barker 1976, Kayani 2017, Contina 2019, Koehler 2021, and Sasanelli 2020.
2. Ask HP to select target crop-region scenario and collect local prices, treatment costs, lab turnaround, and willingness-to-pay.
3. Pull a small USDA NASS/ERS/FAOSTAT proof dataset for soybean, potato, and tomato/cucumber prices/yields after the target geography is chosen.
4. Convert `stage2-model-parameters.csv` into a reviewed config only after HP fills the prototype and local-market gaps.
