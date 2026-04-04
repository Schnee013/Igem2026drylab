# Miettinen et al. 2022 — 文献总结

> **完整标题**: A GPCR-based yeast biosensor for biomedical, biotechnological, and point-of-use cannabinoid determination
> **期刊**: Nature Communications, 13:3664
> **DOI**: https://doi.org/10.1038/s41467-022-31357-6
> **类型**: Research Article
> **作者**: Karel Miettinen, Nattawat Leelahakorn, Aldo Almeida, Yong Zhao, Lukas R. Hansen, Iben E. Nikolajsen, Jens B. Andersen, Michael Givskov, Dan Staerk, Søren Bak & Sotirios C. Kampranis (University of Copenhagen, Denmark)

## 核心发现

- 利用 *S. cerevisiae* 的 pheromone signalling pathway，将 human CB₂ receptor 偶联至 yeast MAPK cascade，构建了一个 **modular whole-cell cannabinoid biosensor**，具备高灵敏度和广泛的实际应用场景
- Biosensor 采用 **五模块设计**（Receptor, Adaptor, Signal processing, Actuator, Reporter），通过模块化替换可适配不同 GPCR 和不同输出模式（fluorescence, colorimetric, luminescence）
- 开发了三种 reporter 系统：**ZsGREEN fluorescence**、**betalain colorimetric**（betacyanin 可用肉眼直接观察）、**NanoLuc luminescence**（最高灵敏度，EC₅₀ = 1.39 nM）
- 通过三个 case study 验证了实际应用能力：(1) 1600 化合物库的 high-throughput screening 发现新 CB₂ agonist 和 antagonist；(2) 54 种植物提取物的 bioprospecting 发现了新 phytocannabinoid **dugesialactone**；(3) 便携式设备检测唾液/尿液/血清中的 cannabinoid
- 该技术平台可扩展至任何有对应 GPCR 的 ligand 检测，为 point-of-care diagnostics 和 drug discovery 提供了低成本、高通量的解决方案

## 实验方法

### 1. Chassis strain 构建（KM111）

- 基于 *S. cerevisiae* AM254 strain 进行多基因敲除，构建 biosensor 底盘菌株 KM111
- **敲除基因**：
  - **STE3**：native a-pheromone receptor（腾出位置给 heterologous GPCR）
  - **GPA1**：native Ga subunit（替换为 chimeric Ga）
  - **STE12**：pheromone response master regulator（由外源 module 提供可调控表达）
  - **SST2**：Gpa1 的 negative regulator（GTPase-activating protein），敲除后增强信号
  - **FAR1**：cell cycle arrest inducer，敲除后消除 pheromone-induced growth arrest

### 2. 初始 biosensor 构建（KM202）

- 在 X-3 locus 整合四个基因：
  - **CNR2**（human CB₂ receptor）under P_CCW12（强组成型启动子），fused with 3×HA-tag
  - **GPA1/Gai1** chimera（Gpa1 C-terminal 5 AA 替换为 human Gai1 序列）under P_PGK1
  - **STE12** under P_RET2（中等强度组成型启动子）
  - **ZsGREEN** reporter under P_FIG1（pheromone responsive promoter）

### 3. 优化 biosensor（KM203）

- 在 CB₂ N-terminal 融合 **MFaSS**（mating factor a secretion signal），提高 receptor 的 plasma membrane localization 和总蛋白水平
- 使用强组成型启动子 **P_CCW12** 驱动 MFaSS-CB₂ 表达
- 优化后 EC₅₀ 从 15 nM（KM202）降至 **4.64 nM**（KM203），灵敏度提升 3.2 倍

### 4. 三种 Reporter 系统

| Reporter strain | 输出类型 | Reporter 基因 | EC₅₀ (CP55940) | LOD | SNR |
|----------------|---------|-------------|----------------|-----|-----|
| KM203 | Fluorescence (ZsGREEN) | ZsGREEN under P_FIG1 | 4.64 nM | 10 pM | 20.1:1 |
| KM205 (betalain) | Colorimetric (O-da-betacyanin) | MjDOD + BvCYP76AD5 under P_FIG1, 补充 L-DOPA + O-dianisidine | 7.05 nM | 63 pM | 26.3 |
| KM206 | Luminescence (NanoLuc) | NanoLuc under P_FIG1 | 1.39 nM | 10 pM | 687:1 |

### 5. Null control strain（KM207）

- 用 A₁ₐ adenosine receptor 替换 CB₂，检测 off-target effect
- 所有 control curve 以 1 mM adenosine 为 fixed background，验证 hit 的 CB₂ specificity

### 6. High-throughput screening workflow

- 使用 Opentrons OT-2 液体处理机器人 + 384-well plate format
- Colorimetric strain KM205 用于 agonist screen（不需 cell lysis，16 h 孵育后直接读色）
- Luminescence strain KM206 用于 antagonist screen（需要精确定量，加 luciferin 后读取）
- 筛选 1600 化合物，Z' score 分别为 0.87（agonist）和 0.61（antagonist），assay quality excellent

### 7. Bioprospecting workflow

- 71 种甲醇提取物 → biosensor 初筛 → HPLC 分级 → biosensor 复筛 → NMR 结构鉴定
- 发现 *Ratibida columnifera*（根部）和 *Eschscholzia californica*（果实）含 CB₂ agonist
- 通过 bioactivity-guided fractionation 从 *R. columnifera* 鉴定出 sesquiterpene lactone **dugesialactone**（EC₅₀ = 2 μM）

### 8. Portable biosensor device

- **Colorimetric 便携设备**（KM205）：bar-coded sample holder，肉眼或手机拍照判读，LOD for THC = 100 nM
- **Luminometric 便携设备**（KM206）：手机 + macro lens + adaptor ring 组装，读取 NanoLuc blue channel intensity，LOD for THC = 100 nM, 11-OH-THC = 100 nM, JWH-018 = 10 nM
- 在模拟人体样本（urine, saliva, serum + THC spiked）中成功检测 cannabinoid

## 关键数据

### Biosensor 性能对比

| 化合物 | KM203 (Fluorescence) EC₅₀ | KM203 LOD | KM206 (Luminescence) EC₅₀ | KM206 LOD |
|-------|---------------------------|-----------|---------------------------|-----------|
| CP55940 | 4.64 ± 0.44 nM | 10 pM | 1.39 ± 0.07 nM | 10 pM |
| THC | 1.2 μM | 32 nM | 5.18 ± 0.98 μM | 100 nM |
| JWH-018 | 169 ± 27 nM | 1 nM | 176 ± 24 nM | 10 nM |
| 11-OH-THC | — | — | 3.11 ± 0.28 μM | 100 nM |

### 天然 cannabinoid 对 KM206 的响应

| 化合物 | EC₅₀ / IC₅₀ | 作用类型 |
|-------|-------------|---------|
| CBC (cannabichromene) | 11.4 ± 2.84 μM | Agonist (medium-low potency) |
| THCA | 10.02 ± 2.13 μM | Agonist (medium-low potency) |
| CBD | IC₅₀ = 10.84 ± 0.73 μM | Inhibitor |
| CBDA | IC₅₀ = 4.05 ± 2.17 μM | Inhibitor |
| CBG | IC₅₀ = 25.75 ± 1.41 μM | Inhibitor |
| CBGA | IC₅₀ = 8.36 ± 0.87 μM | Inhibitor |

### HTS 筛选结果

| 类型 | 发现数量 | 代表性 hit | EC₅₀ / IC₅₀ |
|-----|--------|----------|------------|
| Agonist | 2 (AGO1, AGO2) | AGO1 | 389 ± 61 nM |
| | | AGO2 | 1.5 ± 0.22 μM |
| Antagonist | 7 candidates, 2 validated | ANT2 | IC₅₀ = 28 ± 2.9 μM |
| | | ANT5 | IC₅₀ = 710 ± 73 nM |

### Chimeric G protein 设计

- **Gpa1/Gai1 chimera**：yeast Gpa1 的 C-terminal 5 amino acids 替换为 human **Gai1** 对应序列
- 这一设计使 CB₂（natively coupling to Gi/o family）能够有效偶联至 yeast mating pathway MAPK cascade
- 优化后的 EC₅₀ 与 mammalian cell-based assay 的 equilibrium binding constant（K_D = 3.6 nM for CP55940）高度吻合，证明 coupling efficiency 接近完美

### 关键工程参数

| 参数 | 优化前 (KM202) | 优化后 (KM203) | 提升倍数 |
|-----|-------------|-------------|--------|
| EC₅₀ (CP55940) | 15 ± 1.53 nM | 4.64 ± 0.44 nM | 3.2× |
| LOD (CP55940) | 56 pM | 10 pM | 5.6× |
| SNR max | 17.7:1 | 20.1:1 | 1.1× |
| 最佳温度 | 25°C | 25°C | — |
| T₅₀ (响应时间) | — | 4.6 h (30°C) | — |

## 与项目的关系

### Yeast GPCR biosensor 设计的直接参考

- 本文是 **yeast whole-cell GPCR biosensor 从概念到实际应用的完整工程案例**，提供了从 chassis 构建、receptor 表达优化、chimeric G protein 设计、reporter 系统选择到便携设备开发的全流程参考
- 其 modular five-module architecture（Receptor → Adaptor → Signal processing → Actuator → Reporter）可直接套用于项目中线虫/真菌 GPCR biosensor 的设计框架

### Chassis strain 工程策略

- KM111 chassis 的基因敲除策略（STE3, GPA1, STE12, SST2, FAR1）与 Lengger & Jensen 2020 综述中的 Shaw et al. 2019 最优方案高度一致
- **关键差异**：本文额外敲除了 STE12 并以可调控方式重新引入，实现了对 MAPK cascade output 的精细调控
- 本文使用的 AM254 parent strain 被认为有利于 plasma membrane-localized protein 的表达（利于 GPCR 正确 folding 和 trafficking）

### MFaSS leader sequence 的有效性验证

- MFaSS（mating factor a prepro secretion signal）融合到 CB₂ N-terminal 后，显著提升了 receptor 的 membrane localization 和总表达量
- EC₅₀ 改善 3.2 倍，LOD 改善 5.6 倍 —— 这为项目中 fungal GPCR（Gpr2/Gpr3/GprC）的异源表达提供了 **N-terminal leader sequence 策略的直接实验证据**

### Reporter 系统选型指导

| 应用场景 | 推荐 reporter | 理由 |
|--------|-------------|-----|
| 实验室初步验证 | ZsGREEN fluorescence | 简单直接，无需额外底物 |
| High-throughput screening | NanoLuc luminescence | 最高 SNR（687:1），最低 LOD，动态范围宽 |
| 现场快速检测 / portable | Betalain colorimetric | 肉眼可见，无需仪器，适合 point-of-care |
| 需要低背景干扰 | NanoLuc luminescence | 光信号不受样品自荧光/颜色干扰 |

### Betalain reporter 系统的创新性

- 作者引入了来自 *Beta vulgaris*（红甜菜）的 **betalain 生物合成途径**作为 colorimetric reporter，这是一个全新的 reporter 概念：
  - BvCYP76AD1（tyrosine hydroxylase）+ MjDOD（DOPA dioxygenase）+ BvDOPA5GT（glucosyltransferase）
  - 产生可见颜色（红色 betanin、黄色 betaxanthin、深红 O-da-betacyanin），肉眼可辨
- 与传统 beta-galactosidase 或 carotenoid reporter 相比，betalain 响应更快且不需要裂解细胞
- 该策略对项目中开发便携式线虫检测设备具有参考价值

### 对 point-of-care biosensor 开发的启示

- 便携设备的设计理念（bar-coded sample holder、手机拍照读取、calibration curve 内置）可为项目中最终产品形态提供参考
- 实际生物样本检测（urine, saliva, serum）的成功验证证明 yeast biosensor 具备处理复杂基质的能力
- Z' score > 0.5 的 HTS 筛选质量标准可用于评估项目 biosensor 的 assay quality

## 关键引用

- **Shaw, W. M. et al. 2019** — *Cell* 177:782-796. Engineering a model cell for rational tuning of GPCR signaling. **Chassis strain 极致精简的标杆工作（15 gene KO），本文 chassis 设计的直接参考**
- **Brown, A. J. et al. 2000** — *Yeast* 16:11-22. Functional coupling of mammalian receptors to the yeast mating pathway using novel yeast/mammalian G protein alpha-subunit chimeras. **Chimeric Ga 系统测试的经典论文，本文 Gpa1/Gai1 chimera 设计的基础**
- **Ostrov, N. et al. 2017** — *Sci Adv* 3:e1603221. A modular yeast biosensor for low-cost point-of-care pathogen detection. **Modular yeast biosensor 的先驱工作，本文 modular 设计参考**
- **O'Malley, M. A. et al. 2009** — *Protein Sci.* 18:2356-2370. Progress toward heterologous expression of active G-protein-coupled receptors in *Saccharomyces cerevisiae*: Linking cellular stress response with translocation and trafficking. **GPCR 在酵母中异源表达的关键综述**
- **Grewal, P. S. et al. 2018** — *Metab. Eng.* 45:180-188. Bioproduction of a betalain color palette in *Saccharomyces cerevisiae*. **Betalain reporter 在酵母中生产的先驱工作**
- **Nakamura, Y. et al. 2013** — *PLoS ONE* 8:e82237. Bright fluorescence monitoring system utilizing Zoanthus sp. green fluorescent protein (ZsGreen) for GPCR signalling in microbial yeast cells. **ZsGREEN 用于 yeast GPCR signalling 的 reporter 选择依据**
- **Campbell, R. M. et al. 1999** — *Bioorg. Med. Chem. Lett.* 9:2413-2418. Selective A₁-adenosine receptor agonists identified using yeast *Saccharomyces cerevisiae* functional assays. **Adenosine receptor 在酵母中表达的先例，本文 null control strain KM207 的参考**
