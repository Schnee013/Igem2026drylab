# Choe et al. 2012 — 文献总结

> **完整标题**: Ascaroside Signaling Is Widely Conserved among Nematodes
> **期刊**: Current Biology 22, 772–780
> **DOI**: 10.1016/j.cub.2012.03.024
> **作者**: Andrea Choe, Stephan H. von Reuss, Dima Kogan, Robin B. Gasser, Edward G. Platzer, Frank C. Schroeder, Paul W. Sternberg

## 核心发现

- Ascaroside 信号传导在线虫门中广泛保守，不仅限于 *C. elegans*。通过 HPLC/MS 筛查 19 个线虫物种（涵盖 free-living 和 parasitic 类型），发现绝大多数物种都产生 ascarosides。
- 不同物种产生 species-specific 的 ascaroside 混合物（blend），其组成和比例因物种、生活史阶段（larval vs. adult）而异。
- Ascaroside 的生物合成模式部分与系统发育（phylogeny）相关，部分与生态位（ecological niche）相关：
  - **Clade-specific 趋势**：Rhabditidae 家族成员多产生 omega-1-functionalization 的 ascarosides；omega-functionalization（如 oscr#9, oscr#10）和 indole ascaroside（icas#9）仅见于 Rhabditidae 的部分成员。
  - **生态位相关**：所有 insect-associated 线虫（*Oscheius tipulae*, *H. bacteriophora*, *Steinernema spp.*, *Pristionchus pacificus*）的 ascaroside blend 中 ascr#9 含量超过 50%，暗示 ascr#9 在 insect-associated 生态中可能有保守功能。
- 不同线虫物种对 ascarosides 表现出 species-specific 的行为响应（retention/avoidance），且存在 gender-specific 差异。
- **跨物种吸引现象**：*C. elegans* 雄虫被 *P. redivivus* 雌虫吸引（因其产生 ascr#3 和 ascr#10），但不被 *S. carpocapsae*、*P. pacificus* 或 *P. strongyloides* 吸引（这些物种不产生或少量产生上述化合物）。
- Ascaroside 信号系统与细菌的 quorum sensing（AHL, acyl homoserine lactones）在结构组织上高度相似：都基于保守的核心骨架 + 物种特异的脂肪酸侧链修饰，构成 modular 的化学语言。
- 有 4 个物种未检出 ascarosides：*Pratylenchus penetrans*、*Ascaris suum*、*Romanomermis* spp.。其中 *Ascaris suum* 已知产生 lipophilic long-chain ascarosides（不溶于水，不在本实验的检测范围内）；*Romanomermis* 属的缺失可能与其独特的脂质代谢有关。

## 实验方法

- **HPLC/MS 筛查**：使用 Agilent 1100 HPLC + Quattro II mass spectrometer（ESI-MS，正/负离子模式），对 19 个线虫物种的 exudate 进行 ascaroside 定性和定量分析。样品与包含 150 种 ascaroside 的 library（来自 *C. elegans* WT 和 mutant）进行比对。
- **Retention assay**：在 5 cm agar plate 的 bacterial lawn 上放置合成 ascarosides（0.6 fmol, pmol, nmol），记录线虫在 conditioned region vs. control region 停留的时间比例，检测 attraction/avoidance 行为。
- **Long-range attraction assay**：10 cm plate，copper cylinder conditioning（hermaphrodites 或 ascaroside），释放 100 只雄虫从中央，测量 chemotaxis index。
- **Phylogenetic tree**：基于 SSU rDNA（small subunit ribosomal DNA）序列，使用 MUSCLE 比对 + PHYLIP 3.68 的 Dnadist/Neighbor + Consense 构建 majority-rule consensus tree。
- **C. elegans 株系内比较**：分析 4 个地理隔离的 WT 株系（N2 Bristol, DL238 Manuka, CB4856 Oahu, JU1527 Orsay）的 ascaroside profile 差异。

## 关键数据

### 各物种 ascaroside 产出概况（Figure 2 heatmap）

| 物种 | 生活方式 | 主要 ascarosides | 备注 |
|------|---------|-----------------|------|
| *C. elegans* | free-living, bacteriovore | ascr#1, #3, #5, #7, #9, #10, #12, #14, #18, icas#9, oscr#9, oscr#10, oscr#18 | 最丰富的 ascaroside profile |
| *Caenorhabditis sp. 7* | free-living | 类似 *C. elegans*，额外有 omega-functionalized 产物 | |
| *Panagrellus redivivus* | free-living, bacteriovore | ascr#1, ascr#3, ascr#10（大量） | ascr#3 和 #10 是吸引 *C. elegans* 雄虫的关键 |
| *Pelodera strongyloides* | free-living | ascr#18, ascr#20, ascr#22, ascr#24, ascr#26 | 长链 ascarosides（C12-C15），Clade 9 特征 |
| *H. bacteriophora* | entomopathogenic insect parasite | ascr#18, ascr#22, ascr#24, ascr#26 | 长链为主，ascr#18 也大量存在 |
| *Steinernema glaseri* (adult) | entomopathogenic insect parasite | ascr#9（92.2%）, ascr#11, ascr#12, ascr#10 | ascr#9 占绝对优势 |
| *Steinernema glaseri* (IJ) | entomopathogenic insect parasite | ascr#9, ascr#11, ascr#12, ascr#10 | Dauer/IJ 阶段不产 ascr#1 |
| *S. carpocapsae* | entomopathogenic insect parasite | ascr#9 为主 | |
| *Nippostrongylus brasiliensis* | vertebrate parasite (rat) | ascr#1, ascr#3, ascr#9, ascr#12, ascr#14 | 与 *C. elegans* profile 部分重叠 |
| *Oscheius tipulae* | insect-associated | ascr#9 > 50% | |
| *O. carolinensis* | insect-associated | ascr#9 为主 | |
| *Pristionchus pacificus* | insect-associated (necromenic) | ascr#9 为主 | |
| *Rhabditis sp.* (AF5) | free-living | 含 omega-functionalized ascarosides | |
| *Koernia sp.* | — | 检出 ascarosides | |
| *Pratylenchus penetrans* | plant parasite | **未检出** | 可能产量极低或结构不同 |
| *Ascaris suum* | vertebrate parasite (pig) | **未检出（水溶性）** | 已知产 lipophilic long-chain ascarosides（卵壳层） |
| *Romanomermis* spp. | insect parasite (mermithid) | **未检出** | 独特脂质代谢，可能从未演化出 short-chain ascarosides |

### ascr#18 分布
- ascr#18 在 *C. elegans*、*Pelodera strongyloides*、*H. bacteriophora* 中均有检出，属于较长链的 ascaroside。
- 在 heatmap（Figure 2）中，ascr#18 在 Clade 9 物种（*Pelodera*, *Oscheius*, *Heterorhabditis*）中尤为丰富。
- ascr#18 在 *P. strongyloides*（mixed-stage）和 *H. bacteriophora*（adult）中被 HPLC/MS 明确鉴定（Figure 1C，蓝色标注）。

### 行为学数据（Figure 3）
- ascr#1, ascr#3, ascr#7, ascr#8, ascr#10 在多个物种中表现出 retention activity。
- ascr#3 和 ascr#8 在多物种中有活性，但活性阈值（activity threshold）因物种而异。
- *C. elegans* 雄虫对 pmol 水平的 ascr#10 有 preference，而 *S. glaseri* 和 *P. redivivus* 雄虫仅对 nmol 水平的 ascr#10 有响应。

### C. elegans 株系内变异
- 4 个 WT 株系产生相似的 ascaroside set，但比例有差异：DL238 和 JU1527 产 ascr#1 显著多于 CB4856 和 N2；N2 产更多 omega-oxygenated oscr#9。

## 与项目的关系

### ascr#18 作为 PPN biomarker 的支持证据
- 本文直接证明 ascr#18 不仅存在于 *C. elegans*，也存在于 *Pelodera strongyloides* 和 *Heterorhabditis bacteriophora* 等物种中，说明 ascr#18 的生物合成在线虫中是 conserved 的。
- 虽然本文未检测典型的 plant-parasitic nematodes（PPN）如 *Meloidogyne* 或 *Heterodera* 的 ascr#18，但 *Pratylenchus penetrans*（root-lesion nematode）未检出任何 ascaroside，这可能是检测灵敏度问题而非真正缺失。后续文献（如 Manosalva et al. 2015）已证明 PPN 确实产生 ascarosides 并被植物识别。

### Cross-species conservation 的意义
- Ascaroside biosynthesis 的广泛保守性为将 ascaroside（包括 ascr#18）作为线虫通用 biomarker 提供了理论基础。
- 不同物种产生不同 blend 的特点意味着：通过分析 ascaroside profile（而非单一化合物），有可能实现物种级别的鉴定。
- 本文提出的 "nematode chemical code" 概念，类比细菌 quorum sensing，为基于 pheromone 的线虫防治策略提供了框架。

### 对生物传感器设计的启示
- Species-specific ascaroside blend 意味着 biosensor 需要考虑目标 PPN 的特异性 ascaroside profile，而非仅检测单一化合物。
- 但 ascr#18 在多个 clade 中的广泛分布使其成为"广谱"线虫检测的候选 biomarker。
- 行为学数据表明 ascaroside 浓度阈值因物种而异（fmol-nmol range），这为 biosensor 的灵敏度要求提供了参考。

## 关键引用

- Choe, A., von Reuss, S.H., Kogan, D., Gasser, R.B., Platzer, E.G., Schroeder, F.C., and Sternberg, P.W. (2012). Ascaroside signaling is widely conserved among nematodes. *Current Biology* 22, 772–780.
- 本文引用的关键上下文文献：
  - Srinivasan et al. (2008) Nature 454 — *C. elegans* ascaroside blend 调控 mating 和 dauer
  - von Reuss et al. (2012) JACS 134 — *C. elegans* ascaroside 的 modular biosynthesis
  - Kaplan et al. (2011) PLoS ONE 6 — ascaroside 表达依赖于 diet 和 developmental stage
  - Edison (2009) Curr. Opin. Neurobiol. 19 — ascaroside pheromones 调控多种复杂行为
  - Bartley et al. (1996) J. Nat. Prod. 59 — *Ascaris suum* 的 ascaroside lipid 结构鉴定
