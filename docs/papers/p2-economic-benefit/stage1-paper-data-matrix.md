# P2 Early-Detection Economic Benefit: Stage 1 Paper/Data Matrix

Date: 2026-05-21
Durable location: `docs/papers/p2-economic-benefit/stage1-paper-data-matrix.md`
Temporary run source: `tmp_papers/p2_economic_benefit_20260521/stage1_paper_data_matrix.md`
Scope: metadata/source discovery for a Python economic model. This is not model code and not final full-text numeric calibration.

Project boundary: current chassis is yeast STE2 + GPCR biosensor. The economic model quantifies "early detection + timely intervention" against "no detection / late discovery". Docking rankings, docking Delta G, ODE Kd, and unverified wet-lab assumptions are not fixed economic inputs; they remain optional scenario/detection-threshold interfaces.

## Research Plan And Keyword Groups

1. Build three crop scenarios first: soybean + soybean cyst nematode, potato + potato cyst nematodes, and tomato/cucumber + root-knot nematodes. These cover field crop, tuber/regulatory pest, and high-value vegetable cases.
2. For each scenario, screen for density-to-damage functions, damage thresholds, economic thresholds, diagnostic cost/delay, management cost/effect, and commodity price/yield data.
3. Prioritize API metadata from Crossref/OpenAlex/Semantic Scholar/PubMed, then fill official/extension/statistical gaps from USDA, FAO, EPPO, APHIS, AHDB, UC IPM, and university diagnostic labs.
4. Treat source strength explicitly: peer-reviewed for functions and efficacy, official/extension for thresholds and lab/management practice, official statistics for prices/yields, industry pages only as low-tier adoption/cost precedent.
5. After this stage, do full-text/table extraction only for `must_read` and selected `strong_candidate` records.

Keyword groups:
- SCN: `Heterodera glycines soybean yield loss egg density economic threshold eggs 100 cc soil`, `SCN resistant variety crop rotation yield`, `SCN soil sample egg count fee turnaround`.
- PCN: `Globodera pallida rostochiensis potato yield loss eggs g soil Seinhorst threshold`, `PCN grower guide nematicide rotation resistant variety`, `pale cyst nematode APHIS economic impact`.
- RKN vegetables: `Meloidogyne incognita tomato cucumber yield loss initial population density J2 500 cm3 soil`, `root-knot nematode tomato UC IPM yield loss table`, `cucumber plant age inoculum density`.
- Diagnostics/value: `plant parasitic nematode diagnostic qPCR morphology cost turnaround`, `rapid field plant disease diagnostic value of information`, `site-specific information pesticide threshold adoption`.
- Management/cost: `abamectin fosthiazate fluopyram fluazaindolizine nematicide label rate`, `resistant cultivar rotation cover crop biological control nematode yield`, `USDA NASS ERS FAOSTAT soybean potato tomato price yield cost`.

## Evidence Matrix

| bucket | topic_bucket | title | authors | year | DOI/URL | source_type | crop | nematode species | parameter/data extracted | model_use | quality_tier | verification_status | notes |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|---|
| must_read | general damage model | Nematode population dynamics, threshold levels and estimation of crop losses | FAO chapter | n.d. | https://www.fao.org/4/V9978E/v9978e07.htm | official technical | multi-crop | PPN broadly | Seinhorst damage-function framing, threshold concept, density-dependent multiplication | mathematical structure for yield-loss submodel | high | verified_url | Good model-language bridge; not crop-specific calibration. |
| must_read | general PPN ranking | Top 10 plant-parasitic nematodes in molecular plant pathology | Jones et al. | 2013 | 10.1111/mpp.12057 | peer-reviewed review | multi-crop | Meloidogyne, Heterodera, Globodera | priority pest justification | Wiki/background and crop-scenario rationale | high | verified_metadata | Use for why RKN/cyst nematodes are central. |
| must_read | global PPN threats | Current Nematode Threats to World Agriculture | Nicol, Turner, Coyne, den Nijs, Hockland, Tahna Maafi | 2011 | 10.1007/978-94-007-0434-3_2 | peer-reviewed chapter | multi-crop | PPN broadly | global crop threat framing and quarantine/management context | background and scenario selection | high | verified_metadata | Good for global/China narrative, not direct local price. |
| must_read | SCN early detection / thresholds | Soybean cyst nematode management guide | Chen, Kurle, Malvick, Potter, Orf / UMN Extension | 2021 reviewed | https://extension.umn.edu/soybean-pest-management/soybean-cyst-nematode-management-guide | extension | soybean | Heterodera glycines | early detection importance; eggs/100cc reporting; 200-10,000 eggs/100cc resistant-variety range; >=10,000 eggs/100cc nonhost recommendation; <200 low damage | soybean decision thresholds and scenario rules | high | verified_url | Directly model-ready as threshold bands; extension guidance, not raw trial curve. |
| must_read | SCN sample uncertainty | How to interpret SCN soil test results | Tylka / Iowa State Extension | n.d. | https://crops.extension.iastate.edu/encyclopedia/how-interpret-scn-soil-test-results | extension | soybean | Heterodera glycines | results in eggs/cysts per 100cc or 250cc; 100-300% sample variability; <12,000 eggs/100cc rotation + resistant soybean guidance | false-negative/sampling-error module and uncertainty ranges | high | verified_url | Strong for Bayesian observation-error layer. |
| must_read | SCN diagnostic cost | Soybean Cyst Nematode Sample Submission | Iowa State PIDC | 2026 current page | https://yardandgarden.extension.iastate.edu/pidc/soybean-cyst-nematode-sample-submission | university lab | soybean | Heterodera glycines | SCN egg count $30 in-state / $35 out-of-state; 10-20 locations per 10-20 acres | diagnostic-cost baseline | high | verified_url | U.S. fee benchmark; not China/local cost. |
| must_read | SCN diagnostic cost | Nematode Soil Sample Submission Form | University of Minnesota SROC | form current online | https://apps.extension.umn.edu/agriculture/crop-diseases/soybean/docs/soybean-cyst-nematode-submission-form.pdf | university lab form | soybean | Heterodera glycines | SCN egg $21; juvenile $35; about 20 subsamples, max 10 acres; eggs/100 cm3 reported | low-cost lab benchmark and sampling-density benchmark | high | verified_url | Form says prices subject to change. |
| must_read | SCN loss narrative | Soybean Cyst Nematode | Iowa State Extension | n.d. | https://crops.extension.iastate.edu/encyclopedia/soybean-cyst-nematode | extension | soybean | Heterodera glycines | U.S. losses estimated about $1.5B; up to 50%+ yield reduction; many infestations undiscovered for years | "late discovery" loss scenario | medium-high | verified_url | Use as narrative/upper-bound context, not exact field curve. |
| must_read | SCN density-yield paper | Yield loss caused by soybean cyst nematode, Heterodera glycines, in Iran | Hajihassani et al. | 2012 | 10.1163/156854111x614511 | peer-reviewed | soybean | Heterodera glycines | candidate density-to-yield-loss relationship | soybean yield-loss curve extraction | high | verified_metadata | Full text/table extraction needed. |
| strong_candidate | SCN management | Soybean cyst nematode resistant cultivar rotation system impacts nematode population density, virulence, and yield | Acharya et al. | 2022 | 10.1016/j.cropro.2021.105864 | peer-reviewed | soybean | Heterodera glycines | resistant-cultivar rotation effects on density, virulence, yield | intervention-effect range | high | verified_metadata | Full text needed for effect sizes. |
| strong_candidate | SCN seed treatment | Seed Treatments for Management of Soybean Cyst Nematode, Heterodera glycines, in Mid-Atlantic Soybean Production | Grabau et al. | 2023 | 10.2478/jofnem-2023-0026 | peer-reviewed | soybean | Heterodera glycines | seed-treatment yield/density effect candidate | intervention cost/effect scenario | medium-high | verified_metadata | Needs cost pairing from product/budget sources. |
| strong_candidate | SCN qPCR | Developing a Real-Time PCR Assay for Direct Identification and Quantification of Soybean Cyst Nematode... | Yan et al. | 2021 | 10.1094/pdis-01-21-0129-re | peer-reviewed diagnostic | soybean | Heterodera glycines | qPCR direct quantification from soil | comparator for lab molecular detection | high | verified_metadata | Use for sensitivity/specificity/LOD after full text. |
| must_read | tomato RKN yield table | Root-Knot Nematode / Tomato / Pest Management Guidelines | UC IPM | current page | https://ipm.ucanr.edu/agriculture/tomato/root-knot-nematodes/ | extension | processing tomato | Meloidogyne spp. | San Joaquin sandy-loam table: spring J2/kg vs percent normal yield; example economics with $54/ton | tomato MVP loss function and net-return example | high | verified_url | Most directly model-ready tomato table. |
| must_read | tomato RKN classic function | Relationships of initial population densities of Meloidogyne incognita and M. hapla to yield of tomato | Barker, Shoemaker, Nelson | 1976 | https://pubmed.ncbi.nlm.nih.gov/19308228/ | peer-reviewed | tomato | M. incognita, M. hapla | thresholds 500-1,000 eggs+larvae/500 cm3 at mountain site; as low as 20/500 cm3 caused damage at coastal plain; max losses 20-85% by site/species | tomato/yield-loss calibration and environment sensitivity | high | verified_url_no_doi | No DOI found in API; PMID/PMCID recorded. |
| must_read | cucumber RKN density | Effects of southern root knot nematode population densities and plant age on growth and yield parameters of cucumber | Kayani, Mukhtar, Hussain | 2017 | 10.1016/j.cropro.2016.09.007 | peer-reviewed | cucumber | Meloidogyne incognita | 500-8000 J2 inoculum; earlier exposure causes higher yield/growth reduction | cucumber scenario, early-detection-time advantage | high | verified_metadata | Strong bridge for "earlier vs later exposure" value. |
| strong_candidate | cucumber RKN density | Interaction between Nematode Inoculum Density and Plant Age on Growth and Yield of Cucumber... | Mukhtar et al. | 2018 | 10.17582/journal.pjz/2018.50.3.897.902 | peer-reviewed | cucumber | Meloidogyne incognita | inoculum density x plant-age growth/yield effects | replicate/triangulate cucumber function | medium | verified_metadata | Screen after Kayani 2017. |
| strong_candidate | cucurbit RKN pathogenicity | Initial Population Density and its Effect on the Pathogenic Potential and Population Growth of the Root Knot Nematode Meloidogyne incognita in Four Species of Cucurbits | Chandra, Sao, Gautam, Poddar | 2010 | 10.3923/ajppaj.2010.1.15; https://scialert.net/fulltext/?doi=ajppaj.2010.1.15 | peer-reviewed | cucurbits | Meloidogyne incognita | initial density and host response | generalized cucurbit density response | medium | verified_metadata | Crossref date is 2009-12-15; journal citation is Asian Journal of Plant Pathology 4(1):1-15, 2010. |
| strong_candidate | eggplant qPCR/yield | Development of a direct quantitative detection method for M. incognita and M. hapla in andosol... | Uehara et al. | 2013 | 10.3725/jjn.43.21 | peer-reviewed | eggplant | M. incognita, M. hapla | qPCR quantification plus initial population vs yield | diagnostic + density-yield bridge | high | probable | Useful if tomato/cucumber data insufficient. |
| background | RKN compendium | Root-knot nematode in tomato | CABI | 2020 | 10.1079/pwkb.20207800110 | expert datasheet | tomato | Meloidogyne spp. | biology/management background | Wiki background and host scope | medium | verified_metadata | Use for narrative, not numeric calibration unless tables exist. |
| must_read | PCN regulatory impact | Pale Cyst Nematode | USDA APHIS | 2025 | https://www.aphis.usda.gov/plant-pests-diseases/pcn | official government | potato/tomato/eggplant | Globodera pallida | dormant viable up to 30 years; cyst 300-500 eggs; unchecked yield reduction 20-70% | potato late-detection upper-bound and quarantine narrative | high | verified_url | Official source; not a density curve. |
| must_read | PCN thresholds | Globodera pallida datasheet | EPPO | 2022 update | https://gd.eppo.int/taxon/HETDPA/datasheet | official/regulatory datasheet | potato | Globodera pallida | approx 2 t/ha lost per 20 eggs/g soil; damage threshold as low as 1-2 eggs/g; up to 80% loss | potato density-to-loss and threshold bands | high | verified_url | Very model-relevant; cite as regulatory datasheet. |
| must_read | PCN grower guide | PCN Grower Guide | AHDB | 2018 | https://potatoes.ahdb.org.uk/knowledge-library/pcn-grower-guide | levy-board/industry-extension | potato | G. pallida, G. rostochiensis | trial losses 1-35% at 10-20 eggs/g soil; management options | potato scenario calibration and grower practice | high | verified_url | Good UK grower-facing evidence. |
| must_read | PCN risk model | A Predictive Risk Model Analysis of the Potato Cyst Nematode Globodera pallida in Idaho | Contina et al. | 2019 | 10.1094/pdis-04-19-0717-re | peer-reviewed | potato | Globodera pallida | predictive risk model for Idaho PCN | potato scenario and regulatory-risk structure | high | probable | Full text needed for equations/parameters. |
| strong_candidate | PCN yield study | Impact of Globodera ellingtonae on yield of potato | Ingham et al. | 2019 | 10.21307/jofnem-2019-073 | peer-reviewed | potato | Globodera ellingtonae | field/potato yield impact of cyst nematode | alternative PCN-like density/yield evidence | medium-high | probable | Species differs from G. pallida/rostochiensis. |
| strong_candidate | PCN management model | Improving a pest management tool for scenario analysis of economic populations of Globodera pallida | Koehler, Bell, Back, Urwin, Atkinson | 2021 | 10.1163/15685411-bja10138 | peer-reviewed | potato | Globodera pallida | scenario analysis tool for economic populations | enhanced model / decision-tool inspiration | high | verified_metadata | Important for enhanced version. |
| strong_candidate | PCN abamectin efficacy | Abamectin Efficacy on the Potato Cyst Nematode Globodera pallida | Sasanelli et al. | 2020 | 10.3390/plants9010012 | peer-reviewed | potato | Globodera pallida | LD50, LD99.9, reductions in eggs/J2/cyst/g soil, comparison with fosthiazate, estimated yield-loss effect | intervention efficacy ranges | high | verified_url | Pot/greenhouse predictor; not field cost. |
| strong_candidate | nematicide label | Salibro label | U.S. EPA / Corteva | 2023 | https://www3.epa.gov/pesticides/chem_search/ppls/000352-00932-20230906.pdf | official pesticide label | carrot, cucurbits, tomato/fruiting veg, potato | root-knot, lesion, sting, stubby-root | U.S. label rates and restrictions: tomato 30.7-61.4 fl oz/ac; cucurbits 15.3-23 fl oz/ac; potato subgroup 15.4-61.4 fl oz/ac | treatment-cost conversion once product price obtained | high | verified_url | Label rate only; price must come from distributor/HP/local market. |
| strong_candidate | fluopyram label/industry | Velum Prime | Bayer CropScience UK/FR/ES/US pages | current pages | https://cropscience.bayer.co.uk/our-products/insecticides/velum-prime/ | industry + label links | potato, carrot, tomato/cucumber depending region | PCN/RKN | fluopyram active 400 g/L; application windows; some industry yield/profit claims | management option, lower-tier ROI precedent | medium | verified_url | Use label/rate only; treat profit claims as industry estimates. |
| must_read | diagnostic fee/delay | Agronomic Services - Nematode Assay | North Carolina Department of Agriculture | 2026 fee page | https://www.ncagr.gov/divisions/agronomic-services/nematode-assay | official state lab | many crops | PPN broadly | predictive/diagnostic $10 in-state, $20 out-of-state; molecular $40/$50; turnaround 2 weeks Oct-Nov, 4-8 weeks Dec-Feb | lab cost and delay baseline | high | verified_url | Excellent for "lab delay" parameter. |
| must_read | diagnostic fee/delay | Nematode Diagnostics Lab | Penn State | 2026 page | https://plantpath.psu.edu/about/facilities/nematode-diagnostics-lab | university lab | many crops | PPN broadly | soil species ID $29.34; ID+counts $47.89; morphology; no molecular analysis; results 4-5 days after receipt | lab cost and turnaround benchmark | high | verified_url | Good fast-lab comparator. |
| strong_candidate | diagnostic fee | Services & Fees | University of Minnesota Plant Disease Clinic | 2026 page | https://pdc.umn.edu/services-fees | university lab | commercial crops | PPN broadly | nematode analysis $50; molecular diagnostics $100 minimum | diagnostic cost range | high | verified_url | General commercial crop lab cost. |
| strong_candidate | extraction/time | Testing Services | Cornell Plant Disease Diagnostic Clinic | current page | https://plantclinic.cornell.edu/services/ | university lab | many crops | PPN broadly | nematode extraction by 5-day pie plate or 1-day sugar flotation; most diagnostics within one week | method-turnaround detail | high | verified_url | Good for delay mechanics. |
| strong_candidate | HTS diagnostic standards | Guidelines for reliable use of high throughput sequencing technologies to detect plant pathogens and pests | EPPO/Euphresco? | 2022 | 10.5281/zenodo.6637519 | technical guideline | plant pests | broad | HTS diagnostic reliability framework | diagnostic-quality benchmark | medium | probable | Background for molecular validation, not economics. |
| must_read | economic VOI precedent | The Value of Plant Disease Early-Warning Systems: USDA's Soybean Rust Coordinated Framework | Roberts, Schimmelpfennig, Ashley, Livingston, Ash, Vasavada | 2006 | https://ageconsearch.umn.edu/record/7208 | USDA ERS report | soybean | soybean rust pathogen | cost of early-warning framework; information value depends on forecast accuracy | value-of-information structure for early detection | high | verified_search_metadata | Open failed, but metadata and abstract found; retrieve PDF later. |
| strong_candidate | site-specific information | The value of site-specific information and the environment: Technology adoption and pesticide use under uncertainty | Isik, Hudson, Coble | 2005 | 10.1016/j.jenvman.2005.01.024 | peer-reviewed economics | cotton example | pest populations broadly | option-value framework, economic thresholds over field subunits, adoption under uncertainty | enhanced model/adoption framing | high | verified_url | Not nematode-specific but method-relevant. |
| strong_candidate | biosecurity economics | Approaches for estimating benefits and costs of interventions in plant biosecurity across invasion phases | Welsh et al. | 2021 | 10.1002/eap.2319 | peer-reviewed / USDA page | plant biosecurity | invasive pests | cost accounting vs partial equilibrium vs CGE; intervention stage framing | model-scope selection and caveats | high | verified_url | Use for why MVP should be cost accounting, not full equilibrium. |
| background | onsite diagnostics | Sowing seeds for the future: the need for on-site plant diagnostics | Cassedy et al. | 2020 | 10.1016/j.biotechadv.2019.02.014 | peer-reviewed review | plant disease | broad | point-of-use diagnostics rationale, targeted treatment vs blanket treatment | biosensor precedent/background | medium | verified_search_metadata | Full text metadata should be rechecked via Crossref. |
| background | diagnostic network value | What's the Value in Finding No disease? >$7.2M/year in the SPDN | Harmon / NPDN | 2024 | https://www.npdn.org/newsletter/2024/05/whats_value_finding_no_disease_72myear_spdn | diagnostic network article | multi-crop | plant pathogens/pests | "no pathogen found" avoided-treatment savings example; $1,000 commercial spray cost assumption | communication example, not hard parameter | low-medium | verified_url | Treat as illustrative estimate, not peer-reviewed. |
| must_read | soybean costs | Commodity Costs and Returns | USDA ERS | 2025 docs | https://www.ers.usda.gov/data-products/commodity-costs-and-returns/documentation/ | official statistics | soybean | n/a | annual U.S. soybean production costs/returns by commodity/region | crop cost baseline | high | verified_url | Use API/download for model input; survey-year reliability caveat. |
| must_read | crop production/prices | QuickStats API | USDA NASS | current | https://quickstats.nass.usda.gov/api | official statistics/API | soybean, potato, tomato | n/a | official aggregate production, yield, price, value data | yield and price input source | high | verified_url | Use queries per crop/state/year. |
| must_read | vegetables/potatoes prices | Vegetables and Pulses Data | USDA ERS | current | https://www.ers.usda.gov/topics/crops/vegetables-and-pulses/data/ | official statistics | potato, tomato | n/a | annual supply, production, imports, season-average prices for vegetables and potatoes | potato/tomato price series | high | verified_url | Better for U.S. vegetable price than generic commodity page. |
| must_read | global/China crop data | FAOSTAT crop production / producer prices | FAO | current | https://www.fao.org/statistics/en | official statistics | soybean, potato, tomato/cucumber | n/a | production, harvested area, yields, producer prices by country | China/global scenario inputs | high | verified_url | Pull latest available via FAOSTAT; flag FAO estimates where used. |
| background | classic global loss | A world perspective on nematology: the role of the society | Sasser and Freckman | 1987 | no DOI found; reference URL: https://pubmed.ncbi.nlm.nih.gov/24204279/ | book/chapter | multi-crop | PPN broadly | classic global crop-loss estimates | background only | medium | verified_reference_only | Bibliography verified from PubMed reference list: in Veech and Dickson, eds., Vistas on Nematology, Society of Nematologists, pp. 7-14. Use only as background. |
| pending_verification | SCN thesis candidates | Precision agriculture / pH / SCN density / yield Iowa theses | Iowa State repository records | unknown | 10.31274/rtd-180813-11437 and related | thesis/dissertation | soybean | Heterodera glycines | spatial density-yield relations | possible advanced spatial model | medium | pending_verification | API tier over-promoted; exact years/authors need verification. |
| strong_candidate | PCN dissertation | Quantitative studies on the management of potato cyst nematodes (Globodera spp) in The Netherlands | Been and Schomaker | 1998 | 10.18174/194231; https://research.wur.nl/en/publications/quantitative-studies-on-the-management-of-potato-cyst-nematodes-g | dissertation | potato | Globodera spp. | quantitative PCN management, sampling error, stochastic management and yield-loss risk | enhanced potato model | medium-high | verified_url | WUR thesis record verified; useful for enhanced potato model, but keep separate from peer-reviewed article evidence. |
| pending_verification | China/local costs | Chinese lab/field diagnostic, pesticide, crop-price sources | TBD | TBD | pending | official/local/HP | soybean, potato, tomato/cucumber | target local PPN | local cost, willingness-to-pay, product price | China-facing scenario | high need | pending_verification | Need HP interviews or Chinese official/extension equivalents. |

## Model-Ready Parameter Table Draft

| parameter | meaning | unit | candidate value/range | source | reliability | HP/wet-lab confirmation? |
|---|---|---|---|---|---|---|
| crop_scenario | modeled crop/nematode pair | categorical | soybean-SCN; potato-PCN; tomato/cucumber-RKN | project scope + matrix | high | HP choose priority geography/crop |
| area | modeled field area | ha or acre | configurable; sample sources often use 10 acres or 10-20 acres per SCN sample | UMN/ISU sampling guidance | medium | HP/local farm size |
| baseline_yield | no-nematode expected yield | t/ha or bu/ac | pull from USDA NASS / FAOSTAT by crop-region-year | USDA NASS, FAOSTAT | high if official | HP select target region |
| crop_price | farmgate/producer price | USD/t or local currency/t | pull from USDA ERS/NASS or FAOSTAT producer prices | USDA ERS/NASS, FAOSTAT | high | HP select market/local price |
| scn_low_threshold | SCN low/damaging boundary | eggs/100 cc soil | <200 eggs/100cc = low/limited damage context | UMN Extension | medium-high | local extension validation |
| scn_resistant_band | SCN management band | eggs/100 cc soil | 200-10,000 eggs/100cc: resistant varieties recommended | UMN Extension | medium-high | agronomist validation |
| scn_high_threshold | SCN high management threshold | eggs/100 cc soil | >=10,000 eggs/100cc: nonhost crop one or more years; significant loss even with resistant variety | UMN Extension | high for scenario band | local validation |
| scn_sample_error | field sampling variability | multiplier | 100-300% variation between samples from same area is possible | Iowa State Extension | medium-high | local sampling design |
| scn_lab_cost | lab SCN egg count | USD/sample | $21-$35/sample from UMN/ISU examples | UMN SROC, Iowa State PIDC | high for U.S. examples | local lab/China cost |
| broad_nematode_lab_cost | general nematode analysis | USD/sample | $10-$50 morphology/count; molecular $40-$100+ depending lab | NCDA, Penn State, UMN PDC | high for U.S. examples | local lab/China cost |
| lab_turnaround | current lab delay | days/weeks | 4-5 days after receipt to 2 weeks; seasonally 4-8 weeks in NC winter | Penn State, NCDA, Cornell | medium-high | target lab confirmation |
| pcn_damage_threshold | PCN damage threshold | eggs/g soil | as low as 1-2 eggs/g soil | EPPO | high | local PCN species/cultivar |
| pcn_loss_slope | potato yield loss approximation | t/ha per eggs/g | approx 2 t/ha lost per 20 eggs/g soil | EPPO citing Brown 1969 | medium | full-text check and cultivar fit |
| pcn_trial_loss_band | PCN trial loss band | % yield | 1-35% at 10-20 eggs/g soil | AHDB | high for UK guide | region/cultivar check |
| pcn_upper_loss | uncontrolled PCN severe loss | % yield | 20-70% APHIS for G. pallida; up to 80% in EPPO/AHDB contexts | USDA APHIS, EPPO | medium-high | scenario only |
| tomato_rkn_yield_table | tomato yield as function of J2 | % normal yield | spring 0-25 J2/kg = 100%; 200 J2/kg = 88%; 500 J2/kg = 72%; 1000 J2/kg = 53% in UC IPM table | UC IPM | high for San Joaquin sandy loam | local soil/crop fit |
| tomato_rkn_threshold | tomato RKN classic threshold | eggs+larvae/500 cm3 soil | 500-1,000 at NC mountain site; as low as 20 at coastal plain | Barker et al. 1976 PubMed | medium-high | environment-specific |
| cucumber_rkn_inoculum | cucumber RKN exposure range | J2/plant or pot inoculum | 500-8,000 freshly hatched J2; earlier infection worsens reductions | Kayani et al. 2017 | high for experimental relation | field conversion needed |
| intervention_efficacy | reduction in density/loss from intervention | % or relative risk | crop-specific; PCN abamectin pot data: strong egg/J2/cyst reduction at 18-36 ug/mL; tomato/cucumber use label/trial ranges | Sasanelli et al. 2020; label/trial papers | medium | local product/regulatory fit |
| intervention_cost | cost of treatment | USD/ha | not fixed; compute from product rate x market price + application labor | EPA/label rates + distributor/HP | low until priced | yes |
| detection_unit_cost | biosensor per-test cost | USD/test | TBD | team estimate | unknown | yes, wet-lab/prototype |
| deployment_density | tests per ha | tests/ha | TBD; enhanced by P1 diffusion radius/spacing | P1 diffusion interface | unknown | yes |
| early_time_gain | time gained vs late discovery | days/weeks | crop-specific; currently evidence supports pre-plant/fall sampling vs symptom-based discovery, but exact days TBD | UMN/UC IPM/Kayani | medium-low | HP/agronomist interviews |
| sensitivity_specificity | field sensor diagnostic performance | probability | TBD; do scenario sweep | wet-lab/ODE/P1 Bayesian interface | unknown | yes |
| false_negative_cost | expected cost of missed infestation | USD/ha | derived from loss_function x crop value | model output | depends | yes via performance assumptions |
| farmer_wtp | willingness to pay / adoption threshold | USD/test or USD/ha | TBD | HP interviews | unknown | yes |

## Economic Model Structure Recommendation

### MVP: deterministic cost-accounting model

Purpose: fastest HP / Proposed Implementation deliverable.

Inputs:
- crop scenario, area, baseline yield, crop price;
- nematode density category or measured density;
- yield-loss function/table;
- lab or biosensor test cost;
- intervention option and cost/effect.

Equations:
- `loss_no_detection = baseline_yield * price * yield_loss_late(density_late)`
- `loss_early = test_cost + intervention_cost + baseline_yield * price * yield_loss_after_intervention(density_early, efficacy)`
- `net_benefit = loss_no_detection - loss_early`
- `ROI = net_benefit / (test_cost + intervention_cost)`

Outputs:
- break-even test cost;
- break-even intervention efficacy;
- ROI heatmap over density x crop price;
- 2-3 crop case tables.

### Enhanced: probabilistic decision model

Purpose: link with P1/P2 technical models without making P2 dependent on them.

Enhancements:
- density posterior from P1 Bayesian model instead of fixed density;
- sensor sensitivity/specificity and sampling-error model;
- field deployment grid from P1 diffusion radius;
- intervention dose/effect from P2 dose-response;
- Monte Carlo over crop price, yield, test cost, efficacy, and false negatives;
- decision rule: monitor / rotate / resistant variety / chemical / nonhost year.

Outputs:
- expected value of information;
- probability net benefit > 0;
- false-negative loss curve;
- adoption threshold under different test prices.

### Wiki display version

Purpose: clear narrative, not overfitted economics.

Use three panels:
1. Problem: late symptoms hide yield loss and delay management.
2. Model: early field test changes the decision before the damage threshold is crossed.
3. Result: crop-specific break-even plots showing when the biosensor pays for itself.

Keep formulas simple; link a supplementary table for source provenance. Label all uncertain prototype inputs as scenario variables.

## Source-Type Labels

- Peer-reviewed / academic: Jones 2013, Nicol 2011, Barker 1976, Kayani 2017, Sasanelli 2020, Contina 2019, Koehler 2021, SCN/PCN/RKN API-discovered articles; Been and Schomaker 1998 is a verified dissertation, not peer-reviewed article evidence.
- Official statistics / government / regulatory: USDA ERS, USDA NASS, FAOSTAT, USDA APHIS, EPPO, EPA labels, NCDA lab.
- Extension / university diagnostic: UMN, Iowa State, Penn State, Cornell, UC IPM, AHDB grower guide.
- Industry / estimates: Bayer product pages, NPDN newsletter savings estimate, distributor product prices if later used.

## Parameter Gaps Requiring HP / Wet-Lab / Team Input

- biosensor material cost, manufacturing cost, packaging, shelf life, and per-test labor time;
- field deployment density and sampling pattern for the proposed product, ideally linked to P1 diffusion radius;
- field sensor sensitivity, specificity, LOD, false-negative behavior, and whether "no color" is actionable;
- true turnaround-time advantage against local labs, not only U.S. examples;
- target region and crop priority, especially China/global framing;
- local crop price, yield, farm size, pesticide availability, product price, and application labor cost;
- farmer willingness to pay and adoption constraints;
- whether the product is meant for pre-plant soil screening, in-season scouting, or repeated monitoring;
- local regulatory constraints for living yeast biosensor deployment and sample handling;
- accepted intervention actions after positive detection: resistant variety, rotation, chemical, bio-control, or expert consultation.

## Immediate Next Stage

1. Full-text/table extraction for the 10-12 `must_read` crop-function sources.
2. Query USDA NASS/ERS and FAOSTAT for the selected crop-region-year price/yield series.
3. Add local China-facing official/extension/market sources if HP needs China scenarios.
4. Convert the parameter table into a CSV/JSON config for `src/modeling/economic/` only after the source matrix is accepted.
