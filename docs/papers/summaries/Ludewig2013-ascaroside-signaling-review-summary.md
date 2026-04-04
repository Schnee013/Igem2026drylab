# Choe et al. 2012b / Ludewig & Schroeder 2012 — 文献总结

> **完整标题**: Ascaroside signaling in *C. elegans* (综述，引用了 Choe et al. 2012b 的跨物种保守性数据)
> **实际引用的关键论文**: Choe, A., von Reuss, S. H., Kogan, D., Gasser, R. B., Platzer, E. G., Schroeder, F. C., and Sternberg, P. W. (2012b). Ascaroside signaling is widely conserved among nematodes. *Curr. Biol.* 22, 772-780.
> **综述来源**: Ludewig, A. H. and Schroeder, F. C. (2012). Ascaroside signaling in *C. elegans*. WormBook, ed. The *C. elegans* Research Community.
> **DOI (综述)**: 10.1895/wormbook.1.155.1
> **期刊 (Choe 2012b)**: Current Biology

## 核心发现

- **Ascaroside signaling 在线虫门广泛保守**: Choe et al. (2012b) 筛查了 18 个 nematode species 已知的 100 多种 ascarosides，发现其中 **15/18 物种产生可被检测到的 ascarosides**（即 *C. elegans* 中已知的短链 ascarosides）。
- **3 个未检出物种**: 未检测到 *C. elegans* 型 ascarosides 的物种包括猪蛔虫 *Ascaris suum*，以及与之同属的物种（congeneric with *A. lumbricoides*）。但作者指出，*A. suum* 可能仍产生短链 ascarosides，只是丰度低、发育阶段特异性、或结构差异导致未被检出。
- **Ascarosides 构成 modular signaling library**: 不同 ascarosides 通过不同组合和浓度调控 dauer formation、male attraction、hermaphrodite repulsion、aggregation、olfactory plasticity 等多种行为表型。
- **Ascaroside 生物合成通过 peroxisomal beta-oxidation 途径**: 侧链缩短由 ACOX-1、MAOC-1、DHS-28、DAF-22 四步酶完成，来自 very long-chain fatty acid (VLCFA) 前体。
- **Ascaroside profiles 具有物种特异性和性别特异性**: 例如 *C. elegans* 雄性以 ascr#10（饱和）为主，雌雄同体以 ascr#3（alpha,beta-不饱和）为主。

## 实验方法

本综述引用的关键方法包括：

- **NMR spectroscopy + mass spectrometry-based comparative metabolomics**: 用于鉴定 *C. elegans* 中 >100 种 ascarosides（Pungaliya et al., 2009; von Reuss et al., 2012）
- **Activity-guided fractionation**: 分离具有 dauer-inducing 或 male-attracting 活性的组分（Butcher et al., 2007; Srinivasan et al., 2008）
- **LC-MS/MS**: 用于 beta-oxidation mutant 代谢组分析（von Reuss et al., 2012）
- **Behavioral assays**: Chemotaxis assays（雄性吸引、雌雄同体排斥、聚集行为）
- **Genetic analysis**: *daf-22*, *acox-1*, *maoc-1*, *dhs-28* 突变体代谢组比较
- **Cross-species screening** (Choe et al., 2012b): 对 18 个 nematode species 进行 ascaroside profiling

## 关键数据

### Ascaroside 跨物种分布（来自 Choe et al. 2012b）

| 结果 | 详情 |
|------|------|
| 筛查物种数 | 18 nematode species |
| 检出 ascaroside 的物种 | **15/18** species，包括 free-living 和 parasitic nematodes |
| 未检出物种 | *Ascaris suum* 及同属物种（共 3 种）|
| 关键结论 | Ascaroside signaling 在线虫门广泛保守 |

### ascr#18 相关信息

- ascr#18 在 Figure 12 的 *acox-1* 突变体代谢组数据中被明确标注，为 **C11 链长的 (omega-1)-functionalized ascaroside**（saturated 类型）
- 在 Figure 13(a) 的 ascaroside 结构通式中，ascr#18 对应 n=8 的 (omega-1)-oxygenated ascaroside
- ascr#18 在 *acox-1* 突变体中大量积累（因 beta-oxidation 受阻），说明它是 beta-oxidation 途径的中间产物/产品
- **本综述未单独列出 ascr#18 在各物种中的分布**；Choe et al. (2012b) 的原始论文应包含 species-specific ascaroside profiles 的完整数据

### 主要 ascaroside 功能谱

| Ascaroside | 侧链碳数 | 主要功能 | 活性浓度范围 |
|------------|----------|---------|------------|
| ascr#1 (daumone-1, C7) | 7 | Dauer induction | nM-uM |
| ascr#2 (daumone-2, C6) | 6 | Dauer induction, male attraction | nM-uM |
| ascr#3 (daumone-3, C9) | 9 | Dauer induction, male attraction, hermaphrodite repulsion | pM-nM (attraction), nM-uM (dauer) |
| ascr#5 (C3) | 3 | Dauer induction (synergy) | nM-uM |
| ascr#8 | 含 p-aminobenzoic acid | Dauer induction, male attraction synergist | nM |
| icas#3 (indole ascaroside) | 9 + indole | Hermaphrodite attraction, aggregation | **fM-pM**（极低浓度即有效）|
| ascr#10 (saturated C9) | 9 (saturated) | **Male-produced**, hermaphrodite attraction | 极低量即有效 |
| hbas#3 (p-hydroxybenzoyl) | 含 p-OH-benzoyl | Hermaphrodite attraction | fM |

### 生物合成要点

- **Peroxisomal beta-oxidation 是侧链缩短的核心途径**: ACOX-1 -> MAOC-1 -> DHS-28 -> DAF-22，每轮缩短 2 个碳
- Side-chain oxygenation（omega 或 omega-1 位）发生在 beta-oxidation **之前**
- Ascarylose sugar 的连接可能也在 beta-oxidation 之前
- Indole、p-hydroxybenzoyl 等修饰基团的添加由 tryptophan、tyrosine、isoleucine 等氨基酸代谢供给

### Receptor 系统

- 至少 **3 个 GPCR 家族**参与 ascaroside 感知: srbc-64/srbc-66, srg-36/srg-37, daf-37/daf-38
- 感知神经元: ASK, ASI, ASJ, ADF, ASG, ADL, CEM (male-specific)
- 下游信号通路: TGF-beta (DAF-7), insulin/IGF (DAF-28), serotonin, cGMP

## 与项目的关系

### ascr#18 作为 PPN biomarker 的依据

1. **跨物种保守性**: Choe et al. (2012b) 证明 15/18 nematode species 产生可检测的 ascarosides，包括 free-living 和 parasitic species。这为 ascaroside（包括 ascr#18）作为线虫通用 biomarker 提供了直接证据。
2. **ascr#18 是 beta-oxidation 途径的产物**: 作为 C11 链长的 (omega-1)-oxygenated ascaroside，ascr#18 来自高度保守的 peroxisomal beta-oxidation 途径。该途径在线虫中广泛保守，因此 ascr#18 的产生预期也是保守的。
3. **需要查阅 Choe 2012b 原文确认**: 本综述未逐一列出每个物种产生哪些具体 ascarosides。若要确认 ascr#18 在 plant-parasitic nematodes (PPNs) 中的具体分布，需查阅 Choe et al. (2012b) 原始数据。

### Ascaroside profile 的物种特异性

- 不同物种的 ascaroside profiles 存在差异（species-specific blends），这意味着：
  - 可以通过特定 ascaroside 组合实现 **species-level 鉴定**
  - 但也意味着单一 ascaroside（如 ascr#18）可能不是所有 PPN 的通用 marker
- *Ascaris suum* 等大型寄生线虫未检出短链 ascarosides，可能产生长链 ascaroside lipids（> C29），结构与 *C. elegans* 型 ascarosides 不同

### 选择 ascr#18 作为检测靶标的合理性

- **优势**: 中等链长（C11），处于 beta-oxidation 的中间阶段，可能在多种线虫中稳定产生
- **优势**: (omega-1)-functionalized，是线虫特有的生物合成特征
- **风险**: 需确认目标 PPN species 确实产生 ascr#18（需 Choe 2012b 原始数据或后续文献验证）
- **替代策略**: 若 ascr#18 不够通用，可考虑检测 ascr#18 + ascr#3 + ascr#1 等多种 ascarosides 组合

## 关键引用

| 引用 | 主题 | 重要性 |
|------|------|--------|
| **Choe et al. (2012b)** Curr. Biol. 22, 772-780 | Ascaroside signaling 跨 18 个 nematode species 保守 | **核心**: ascr#18 biomarker 可行性的直接证据 |
| **Choe et al. (2012a)** PNAS 109, 20949-20954 | *Panagrellus redivivus* 的 sex-specific mating pheromones（multiply side chain-hydroxylated ascarosides） | 其他线虫的 ascaroside 变异 |
| von Reuss et al. (2012) JACS | MS-based comparative metabolomics 鉴定 >100 ascarosides | 方法学 + ascaroside 全景 |
| Butcher et al. (2007) Nat. Chem. Biol. 3, 420 | 首次鉴定 dauer pheromone 化学组分 | 奠基性工作 |
| Srinivasan et al. (2008) Nature 454 | Ascarosides 调控 male attraction | 行为功能 |
| Noguez et al. (2012) | *Heterorhabditis bacteriophora* 的 ascaroside ethanolamides | 昆虫病原线虫也产 ascarosides |
| Golden & Riddle (1982) Science 218, 578 | 发现 dauer pheromone | 历史奠基 |
