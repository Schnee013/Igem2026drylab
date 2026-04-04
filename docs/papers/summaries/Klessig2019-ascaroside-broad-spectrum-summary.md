# Klessig et al. 2019 — 文献总结

> **完整标题**: Nematode ascaroside enhances resistance in a broad spectrum of plant-pathogen systems
> **期刊**: Journal of Phytopathology
> **DOI**: 10.1111/jph.12795
> **作者**: Daniel F. Klessig, Murli Manohar, Shine Baby, Aline Koch, Wiseborn B. Danquah, Emily Luna, Hee-Jin Park, Judith M. Kolkman, B. Gillian Turgeon, Rebecca Nelson, Jan E. Leach, Valerie M. Williamson, Karl-Heinz Kogel, Aardra Kachroo, Frank C. Schroeder
> **发表年份**: 2019

## 核心发现

1. **ascr#18 (ascaroside) 可在多种作物上诱导广谱抗病性**：在 8 个 plant-pathogen 系统中的 7 个中，ascr#18 提供了 partial 到 strong 的保护作用，覆盖 viruses、bacteria、fungi、oomycetes 和 nematodes 五大类病原体。

2. **作用机制是激活植物先天免疫 (innate immunity)**：ascr#18 被植物识别后，激活以下防御通路：
   - Mitogen-activated protein kinases (MAPK) 通路
   - Salicylic acid (SA) 和 jasmonic acid (JA) 介导的 defence signalling
   - Defence gene expression 上调

3. **极低浓度即有效**：nanomolar 到 low micromolar 浓度 (0.01-10 uM) 即可提供保护，具体最佳浓度因作物-病原体系统而异。

4. **ascr#18 是线虫分泌的进化保守信号分子**：属于 ascaroside 家族，是 plant-parasitic nematodes 分泌的主要 ascaroside，本质上是线虫的 pheromone，但被植物识别为 MAMP (microbe-associated molecular pattern) 类似物。

5. **唯一失败案例**：玉米对 *Setosphaeria turcica* (northern corn leaf blight) 的抗性未被 ascr#18 增强。

## 实验方法

### 作物与病原体系统

**4 种主要作物 + 4 种此前已测试的作物**（共 8 种植物、16 个 plant-pathogen/pest 系统）：

| 作物 | 病原体 | 类型 | 接种方式 |
|------|--------|------|---------|
| Soybean (*Glycine max*) | Soybean Mosaic Virus (SMV-G5) | Biotrophic virus | 叶片 rub-inoculation |
| Soybean | *Pseudomonas syringae* pv. *glycinea* | Hemi-biotrophic bacterium | 叶片 infiltration |
| Soybean | *Phytophthora sojae* (race R1) | Hemi-biotrophic oomycete | 茎部 mycelium 接种 |
| Rice (*Oryza sativa*) | *Xanthomonas oryzae* pv. *oryzae* PXO86 | Biotrophic bacterium | 剪叶浸泡法 |
| Wheat (*Triticum aestivum*) | *Zymoseptoria tritici* | Hemi-biotrophic fungus | 喷雾接种 |
| Maize (*Zea mays*) | *Cochliobolus heterostrophus* C4 | Necrotrophic fungus | 喷雾接种 |
| Maize | *Setosphaeria turcica* | Hemi-biotrophic fungus | 喷雾接种 |
| Tomato (*Solanum lycopersicum*) | *Meloidogyne hapla* VW9 (root-knot nematode) | Biotrophic nematode | 根部 J2 juveniles 接种 |

### ascr#18 施用方式
- **叶面喷施 (foliar spray)**：大多数作物系统，病原体接种前 24-48 hr 喷施
- **根部浸泡 (root dipping)**：番茄-线虫系统，接种前 48 hr 浸泡
- **浓度范围**：0.001-10 uM，配制在含 surfactant (Silwet L-77 或 Tween 20) 的溶液中

### 检测指标
- **病毒**：immunoblotting (SMV coat protein-specific antibodies) 检测病毒积累
- **细菌**：colony forming units (CFU) 计数，lesion length 测量
- **真菌**：lesion area/number 测量，qRT-PCR 定量真菌 DNA
- **Oomycete**：plant survival rate
- **线虫**：eggs per plant 计数

### 统计方法
- Two-way ANOVA + Tukey's HSD（大豆系统）
- One-way ANOVA（玉米系统）
- *t* test（小麦系统）

## 关键数据

### Table 1 汇总：ascr#18 在不同 pathosystem 中的效果

| 宿主 | 病原体 | Protection level | 最佳浓度 |
|------|--------|-----------------|---------|
| Soybean | Soybean Mosaic Virus | **S** (strong) | 10 uM |
| Soybean | *P. syringae* pv. *glycinea* | **MS** (moderately strong) | 10 uM |
| Soybean | *Phytophthora sojae* | **S** (strong) | 10 uM |
| Rice | *X. oryzae* pv. *oryzae* | **W** (weak) | 0.1 uM |
| Maize | *C. heterostrophus* | **M** (modest) | 0.1 uM |
| Maize | *Setosphaeria turcica* | **None** | N/A |
| Wheat | *Zymoseptoria tritici* | **M** (modest) | 0.1 uM |
| Tomato | *Meloidogyne hapla* | **M** (modest) | 0.01 uM |

**注**：加上 Manosalva et al. 2015 的数据，ascr#18 在 16 个 plant-pathogen/pest 系统的 15 个中增强了抗性。

### 关键定量结果

- **Soybean vs. SMV**：5 uM 和 10 uM 处理后，uninoculated systemic leaves 中几乎检测不到病毒积累
- **Soybean vs. *P. syringae***：10 uM ascr#18 使细菌生长降低约 **10 倍** (4 dpi)
- **Soybean vs. *P. sojae***：mock 组 8 dpi 存活率仅 65%，10 uM ascr#18 处理组存活率提升至 **83%**（提升 50%）
- **Rice vs. *X. oryzae***：0.1 uM ascr#18 使 lesion length 从 mock 的 8.08 cm 降至 **3.31 cm**（降低约 59%）
- **Wheat vs. *Z. tritici***：0.1 uM 和 1 uM ascr#18 使 infection area 降低约 **25%**，fungal DNA 降低约 **60-80%**
- **Maize vs. *C. heterostrophus***：0.1 uM ascr#18 显著降低 lesion number
- **Tomato vs. *M. hapla***：0.01 uM ascr#18 使 nematode eggs/plant 从约 55,000 降至约 **25,000**（降低约 55%）

### 浓度依赖性特征
- 大豆系统：高浓度 (10 uM) 效果最佳
- 水稻/小麦/玉米：低浓度 (0.1 uM) 效果最佳
- 番茄/马铃薯（此前数据）：极低浓度 (0.01 uM) 即达最佳效果
- 浓度最佳值 **高度依赖于植物种类和病原体类型**

## 与项目的关系

### Human Practices (HP) narrative 关联

1. **生物防治与可持续农业**：ascr#18 作为天然线虫信号分子，能以极低浓度（nanomolar 级别）诱导广谱植物抗性，可作为传统化学农药的 environmentally friendly 替代方案。这为 iGEM 项目提供了强有力的 real-world application 故事线——利用线虫自身的化学信号来保护作物，而非使用合成杀虫剂。

2. **经济效益模型支撑**：
   - 全球线虫造成的作物损失超过 **$150 billion/year**
   - 大豆全球年产量约 **3.4 亿吨**（2017/2018 数据）
   - ascr#18 有效浓度极低 (nanomolar-low micromolar)，意味着极少量化合物即可处理大面积农田，**成本效益比极高**
   - 覆盖大豆、水稻、小麦、玉米四大主粮，市场覆盖面广

3. **与线虫检测的关系**：本文强调 ascr#18 是 plant-parasitic nematodes 分泌的主要 ascaroside。若我们的项目开发基于 ascaroside 的线虫检测系统，则检测到的信号分子本身就具有 **双重价值**——既能指示线虫存在（诊断），又暗示了潜在的生物防治策略（治疗）。这构成了 "detect-and-protect" 的完整叙事。

4. **Receptor-mediated 识别**：论文指出 ascarosides 不具有 amphiphilic 或 detergent-like 性质（区别于 rhamnolipids），其在极低浓度即能激活免疫的特征 strongly suggest receptor-mediated recognition。这与我们项目中可能涉及的 GPCR-based biosensor 设计形成概念上的呼应。

### 对项目设计的启示
- ascr#18 的 **broad-spectrum** 特性验证了 ascaroside 作为通用线虫标志物的合理性
- 不同作物对 ascr#18 的响应浓度不同，提示 **biosensor 的灵敏度需求因应用场景而异**
- 该研究使用的 plant-pathogen systems 可作为未来 **功能验证** 的参考体系

## 关键引用

- **Manosalva et al. (2015)** *Nature Communications* 6:7795 — ascr#18 诱导植物防御的原始发现，测试了 barley、potato、tomato、Arabidopsis 等 4 种植物
- **Ludewig et al. (2013)** *PNAS* 110:5522-5527 — ascaroside 在 *C. elegans* 中的 pheromone sensing 功能
- **Pungaliya et al. (2009)** *PNAS* 106:7708-7713 — ascaroside 调控线虫发育和行为的早期发现
- **Zipfel (2014)** *Trends in Immunology* 35:345-351 — 植物 pattern-recognition receptors 综述
- **Singh et al. (2015)** — 线虫每年造成 $150 billion 作物损失的数据来源
