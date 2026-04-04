# Mukherjee (Schiesaro) et al. 2025 — 文献总结

> **完整标题**: A yeast mating platform for multiplex screening of fungal GPCR–ligand interactions
> **作者**: Giovanni Schiesaro, Melani Mariscal, Mathias Jönsson, Ricardo Tenente, Mathies Brinks Sørensen, Marcus Wäneskog, María Victoria Aguilar-Pontes, Agustina Undabarrena, Marcus Deichmann, Emma E. Hoch-Schneider, Viji Kandasamy, Thomas M. Frimurer, Antonio Di Pietro, Line Katrine Harder Clemmensen, Michael Krogh Jensen, and Emil Damgaard Jensen
> **期刊**: PNAS (2025), Vol. 122, No. 43, e2521198122
> **DOI**: https://doi.org/10.1073/pnas.2521198122
> **发表日期**: 2025年10月24日
> **物种**: *Saccharomyces cerevisiae*（底盘）; *Fusarium oxysporum*, *F. graminearum*, *Beauveria bassiana*, *Botrytis cinerea*, *Candida albicans*, *Hypocrea jecorina*, *Metarhizium oryzae*, *Neurospora crassa*（真菌 GPCR 来源）

---

## 核心发现

1. **建立了 Yeast Mating Platform (YeMaP)**：利用酿酒酵母 mating pathway 研究真菌 GPCR 与 pheromone 之间的相互作用。将酵母内源 Ste2 GPCR 替换为异源真菌 Ste2-like GPCR，配合 alpha pheromone 分泌，通过 diploid 形成（交配成功）作为 readout。
2. **One-on-One mating matrix 验证特异性**：8 种真菌 GPCR × 8 种 cognate pheromone 的交叉组合显示，species-specific pheromone–GPCR 配对产生最高 diploid frequency，证明系统具有高特异性。但也观察到一些 cross-reactivity，例如 *Bb*.Ste2 对 *Fo* 和 *Hj* pheromone 有响应。
3. **高通量 pheromone library 筛选**：构建了编码 8,000 个 pheromone peptide 变体的 alpha pheromone library（YPL1），筛选出增强型 agonist：
   - **A4 peptide**（含 Ala5 substitution）：对 *Fo*.Ste2 的 EC₅₀ 比天然 *Fo* pheromone 低 13 倍（A4_EC₅₀ = 2.31 × 10⁻⁹ M vs *Fo*_EC₅₀ = 2.92 × 10⁻⁸ M），需要的 pheromone 量减少 57 倍即可达到相同效果
   - **A5 peptide**：EC₅₀ = 5.16 × 10⁻¹⁰ M
4. **发现 pheromone antagonist**：来自 *Cordyceps militaris* 和 *Beauveria asiatica* 的 alpha pheromone（命名为 *Cm*）对 *Bb*.Ste2 和 *Fo*.Ste2 有 antagonistic 效果（IC₅₀ ≈ 1 μM），可抑制 diploid 形成。
5. **环境因子影响 GPCR 信号网络**：通过 Library-on-Library 方法（Cre-Lox barcode 系统 + qPCR 定量），发现 pH、nitrogen source、plant peroxidase（HRP）等环境因子显著影响不同 GPCR–pheromone 的通信强度：
   - *Fo*.Ste2–*Fo* pheromone 信号在所有条件下最为稳健
   - *Fg*.Ste2 信号在 unbuffered media 或 pH = 7 时显著减弱
   - HRP 存在时 *Fo* 系统维持通信但 *Fg* 系统失效
6. **外源 pheromone 补充可干扰真菌 consortia 内通信**：在 *Fo*, *Fg*, *Bb*, *Hj* 四种 GPCR 组成的 consortia 中，添加 *Cm* pheromone 可减少 *Fo*.Ste2 diploid 2 倍并增加 *Bb*.Ste2 diploid 8.7 倍；添加 A4 peptide 增加 *Bb*.Ste2 diploid 12.1 倍。
7. **体内验证**：在 *F. oxysporum* 中进行 in vivo 实验：
   - *Fo* pheromone 和 A4 peptide 均能触发 *F. oxysporum* germ tube 的 hyphal chemotropism（趋化）
   - *Fo* 和 A4 pheromone 可逆转 germ tube 对 tomato root exudate 的趋向性
   - 外源 pheromone 处理显著减少真菌对 tomato root 的侵入（fungal biomass 降低）
   - 但 50 天长期感染实验中 plant survival 无显著差异

---

## 实验方法

### YeMaP 系统设计

- **底盘**：*S. cerevisiae* CEN.PK2-1C 和 BY4741（EUROSCARF）
- **核心改造**：将酵母内源 *STE2* GPCR 替换为异源真菌 Ste2-like GPCR（*STE2* homologs from *Ca*, *Fg*, *Fo*, *Bb*, *Bc*, *Hj*, *Mo*, *Nc*），保留酵母内源 G protein（Gpa1）和下游 mating pathway
- **Readout**：MAT**a** 细胞表达异源 GPCR，MATα 细胞分泌异源 alpha pheromone → 共培养后通过 diploid 形成频率定量互作强度
- **最优 mating type 配置**：异源 GPCR 表达在 MATα 细胞（替换内源 *STE2*），alpha pheromone 从 inducible *MFA2* promoter 驱动表达 → 比 constitutive *TDH3* promoter 产生更高 diploid frequency

### Pheromone Library（YPL1）

- 基于 *Fo* alpha pheromone 的 WCXXXGQPCW 骨架，保留 Gly6-Gln7 essential residues
- 在 position 3, 4, 5 进行 saturation mutagenesis（any amino acid）
- 共 8,000 peptide variants（= 262,144 nucleotide variants）
- 通过 state-of-the-art yeast transformation 导入 1.8 × 10⁶ 细胞，6.9× library coverage
- 筛选流程：Day 1 共培养 → Day 2 选择 diploid → Day 3 DNA 提取 → Day 5 NGS 测序

### Library-on-Library（Multiplex）

- 引入 **Cre-Lox barcode 系统**：每个 haploid 细胞含一个 unique barcode flanked by conserved region 和 Lox site
- 成功 mating 后两个 barcode 通过 Cre-Lox recombination 合并到同一染色体
- 通过 qPCR 比较 barcode pair 的 Ct 值定量 diploid abundance
- 可在单管中同时检测 4 种 GPCR × 4 种 pheromone + controls 的所有组合

### Biosensor 对比实验

- 使用 yEGFP reporter 的传统 biosensor assay 与 YeMaP 平行比较
- YeMaP 提供更高分辨率（能区分 on/off vs. partial activation），但 GPCR signaling 并不总与 mating efficiency 相关

### In vivo 验证

- *F. oxysporum* f. sp. *lycopersici* 4287（Fol4287）
- Chemotropism assay：germ tube 在 water agar 中对 pheromone 梯度的定向生长
- Tomato root infection：2 周龄 *Solanum lycopersicum* cv. Moneymaker 幼苗
- Fungal biomass 通过 qPCR（*Fol4287 actin* gene）定量
- Plant survival 通过 Kaplan-Meier 分析（50 天）

### 分子克隆

- Gene blocks（IDT）经 codon optimization for *S. cerevisiae*
- CRISPR/Cas9 介导的基因组整合（EasyClone site）
- USER cloning + MAD cloning strategy

---

## 关键数据

| 参数 | 数值 |
|------|------|
| *Ca*.Ste2 GPCR–pheromone 最优配置 diploid frequency 优势 | 33 倍（vs 反向配置, P < 0.0001） |
| Pheromone library 大小 | 8,000 peptide variants |
| Library transformation coverage | 6.9× (1.8 × 10⁶ cells) |
| *Fo* pheromone EC₅₀ | 2.92 × 10⁻⁸ M |
| A4 agonist EC₅₀ (for *Fo*.Ste2) | 2.31 × 10⁻⁹ M（13 倍增强） |
| A5 agonist EC₅₀ (for *Fo*.Ste2) | 5.16 × 10⁻¹⁰ M |
| *Bb* pheromone EC₅₀ | 2.45 × 10⁻¹⁰ M |
| *Fo* pheromone EC₅₀ (on *Bb*.Ste2) | 9.58 × 10⁻⁷ M（cross-reactivity, 3,910 倍弱于 *Bb*） |
| *Cm* antagonist IC₅₀ (on *Bc*.Ste2) | ~1 μM |
| Antagonist 需 2,000 倍过量才达到 IC₅₀ | 相对于 agonist |
| *Cm* 对 *Fo*.Ste2 diploid 的抑制 | 0.2 倍（P = 0.001） |
| A4 对 *Bb*.Ste2 diploid 的促进 | 12.1 倍（P = 0.001） |
| *Fo*/*A4* pheromone 对 tomato root fungal biomass 的减少 | 显著减少（P < 0.01） |
| Plant survival (50 d) | 各处理组无显著差异 |

---

## 与项目的关系

本文与 iGEM 项目的 yeast chassis GPCR biosensor 方案高度相关：

### 1. Yeast chassis 设计直接参考

- YeMaP 使用 **CEN.PK2-1C** 和 **BY4741** 作为底盘，直接替换内源 *STE2* 为异源真菌 GPCR → 为项目表达 *A. oligospora* Gpr2/Gpr3 提供成熟的工程化框架
- 关键发现：异源 GPCR 在 MATα 细胞中替换 *STE2*，配合 inducible *MFA2* promoter 驱动 ligand 表达效果最优
- 使用 CRISPR/Cas9 + EasyClone site 进行基因组整合，避免 plasmid loss

### 2. G protein 兼容性

- 本文的真菌 Ste2-like GPCR 能直接与酵母内源 **Gpa1**（Gα subunit）偶联，**无需构建 chimeric G protein** → 这对 Ste2 家族 GPCR 是利好
- 但 Gpr2/Gpr3 属于 **carbon receptor family**（cAMP receptor-like），不属于 Ste2 家族 → 可能需要 chimeric Gα（如 Gpa1-Gpa2 chimera 或 Gpa1-last5aa-of-fungal-Gα）来实现偶联
- GprC（来自 *Trichoderma*）同理，需要评估其 G protein coupling specificity

### 3. Ligand 筛选方法论

- YeMaP 的 **Library-on-Library** 方法可用于筛选 ascaroside 或其他线虫 pheromone 的受体活性 → 如果将 Gpr2/Gpr3 在酵母中功能表达成功，可用类似方法筛选 ascaroside 结构类似物
- 但需注意：ascaroside 是 **小分子糖脂**，不是 peptide pheromone → 不能直接用 alpha pheromone library 筛选，需要换用化学合成 library 或 extract-based screening

### 4. Biosensor vs. Mating readout

- 本文发现 **YeMaP（mating-based）比传统 yEGFP biosensor 分辨率更高**，能检测到 biosensor 无法区分的 GPCR 活性差异
- 但 biosensor assay 更适合简单的 dose-response 检测
- 项目可考虑同时建立两种 readout：**yEGFP/luminescence reporter**（快速定性）+ **mating assay**（高分辨率定量）

### 5. 环境因子考量

- pH、nitrogen source、plant peroxidase 等显著影响 GPCR–ligand 信号 → 设计 biosensor 时需考虑工作环境（土壤 pH、根际分泌物等）
- *Fo*.Ste2 信号在 HRP 存在时保持稳定但 *Fg*.Ste2 失效 → 不同 GPCR 对环境的鲁棒性差异大

### 6. 直接应用前景

- YeMaP 发现的 **A4 synthetic agonist** 能增强 *F. oxysporum* chemotropism → 类似策略可用于设计增强 *A. oligospora* trap formation 的 ascaroside 类似物
- **Antagonist (*Cm* pheromone)** 概念 → 可能存在干扰线虫-真菌通信的 antagonist 分子

---

## 关键引用

| 编号 | 引用 | 相关性 |
|------|------|--------|
| 10 | Vitale et al. (2019) *Nat. Microbiol.* 4, 1443–1449 — Autocrine pheromone signalling in *F. oxysporum* | *Fo* pheromone 系统原始表征 |
| 11 | Turrà et al. (2015) *Nature* 527, 521–524 — *F. oxysporum* senses host plant via pheromone receptor for chemotropism | Ste2 介导的植物根趋化性 |
| 12 | Sridhar et al. (2020) *Sci. Rep.* 10, 10770 — *F. graminearum* Ste2 chemotropism against wheat | Fg.Ste2 功能验证 |
| 14 | Billerbeck et al. (2018) *Nat. Commun.* 9, 5057 — Scalable peptide-GPCR language for multicellular communication | 酵母 GPCR biosensor 工程化先驱 |
| 18 | Lengger et al. (2020) *FEMS Yeast Res.* 20, foz087 — Engineering GPCR signalling in yeast for biotech/medical | 酵母 GPCR 工程综述 |
| 20 | Jensen et al. (2021) *Nat. Commun.* 13, 6201 — Engineered cell differentiation and sexual reproduction in yeast | YeMaP 前期工作 |
| 40 | Shaw et al. (2019) *Cell* 177, 782–796 — Engineering a model cell for rational tuning of GPCR signalling | GPCR 信号调控工程 |
| 41 | Crnkovic et al. (2023) *BioDesign Res.* 5, 0003 — Peptide variant detection by living yeast biosensor via epitope-selective protease | 酵母 biosensor 设计 |

---

## 数据与代码

- NGS 数据和分析代码：[GitHub - Synthetic-Biology-Tools-for-Yeast/Yeast-Mating-Platform](https://github.com/Synthetic-Biology-Tools-for-Yeast/Yeast-Mating-Platform)
- RNA-seq 数据：Gene Expression Omnibus, Accession No. GSE243247
