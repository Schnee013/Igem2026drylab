# Manohar et al. 2020 — 文献总结

> **完整标题**: Plant metabolism of nematode pheromones mediates plant-nematode interactions
> **期刊**: *Nature Communications* 11:208 (2020)
> **DOI**: https://doi.org/10.1038/s41467-019-14104-2
> **作者**: Murli Manohar, Francisco Tenjo-Castano, Shiyan Chen, Ying K. Zhang, Anshu Kumari, Valerie M. Williamson, Xiaohong Wang, Daniel F. Klessig, Frank C. Schroeder
> **机构**: Boyce Thompson Institute; Cornell University (Dept. Chemistry and Chemical Biology; Plant Pathology and Plant-Microbe Biology); UC Davis (Dept. Plant Pathology); USDA-ARS, Ithaca, NY
> **注**: 第一作者 Manohar 即文件名中的 "Dong" 标记所对应的通讯组（Schroeder/Klessig lab）；论文发表名义第一作者为 Manohar

---

## 核心发现（5-10 bullets，含数据）

- **植物主动代谢 ascr#18**：*Arabidopsis*、番茄、小麦根部暴露于 1 µM ascr#18（11-碳侧链）24 h 后，通过 LC-MS 检测到 ascr#10（9-碳）、ascr#1（7-碳）、ascr#9（5-碳）三种侧链缩短的衍生物显著积累，说明植物利用 peroxisomal β-oxidation 将 ascr#18 逐步截短（每轮去除 2 个碳），该代谢途径在单子叶和双子叶植物中保守。
- **¹³C 标记追踪确认代谢流**：用 ¹³C₂-标记的 ascr#18 处理番茄，LC-MS 检测到相应的 ¹³C₂-ascr#9（m/z 249.1254），但 ascr#18 和 ascr#9 的未标记峰未移位，证实 ascr#9 确为 ascr#18 的 β-oxidation 产物，而非内源性积累。
- **ascr#18 被快速消耗，ascr#9 持续积累**：以 1 µM ascr#18 处理 *Arabidopsis* 叶片后追踪 96 h，ascr#18 在 0.5–3 h 内迅速下降，ascr#9 在 1–12 h 达到峰值后缓慢下降，显示代谢动力学具有时间分辨特征。
- **关键酶为过氧化物酶体 acyl-CoA 氧化酶 ACX1/ACX5**：*acx1 acx5* 双突变体几乎完全丧失将 ascr#18 转化为 ascr#9 的能力；ACX1 和 ACX5 在 ascr#10→ascr#9 步骤上功能冗余，ascr#18→ascr#10 的第一步可能还涉及其他 acyl-CoA 氧化酶。
- **代谢产物 ascr#9 介导线虫驱避**：ascr#9 是植物分泌的最主要根系 ascr#18 代谢产物；50 nM ascr#9 可显著减少根结线虫（*Meloidogyne incognita*）J2 幼虫接触根尖（p = 0.014）；ascr#18 单独处理 wt 时有效，但 *acx1 acx5* 突变体对线虫的驱避效果显著减弱。
- **ascr#18/ascr#9 混合物协同驱虫**：定量趋向性实验（6 cm Petri dish）显示，ascr#18（10 nM）+ ascr#9（100 nM）混合物的 attraction index 为 −0.61（p = 0.0026），驱避效果强于单一化合物，表明植物产生的多种 ascaroside 组合具有增效驱虫效果。
- **该防御机制独立于经典 PTI 信号通路**：ascr#18 处理可诱导 JA（PDF1.2、AOS、LOX2）和 SA（PR-1、PR-4）信号标记基因上调，但在 *acx1 acx5* 突变体中这些基因的诱导基本正常，说明 β-oxidation 代谢不是激活经典防御信号通路所必需，而是独立的"化学信号编辑"防御层。
- **对细菌病原体的抗性不依赖 ACX1/ACX5**：用 *Pseudomonas syringae* pv. *tomato* DC3000 感染实验显示，ascr#18 预处理在 wt 和 *acx1 acx5* 中均提供相似的保护，进一步确认 β-oxidation 代谢产物与细菌抗性无关。
- **根分泌物富含 ascr#9**：HPLC-MS 分析 *Arabidopsis* 和番茄根的分泌物，发现 ascr#9 是最主要的分泌型 ascr#18 代谢产物，ascr#10 最少；连续 48 h 追踪显示根系分泌的 ascr 持续积累，提示稳定的代谢-分泌通量。

---

## 实验方法（表格）

| 方法 | 描述 | 关键参数 |
|------|------|---------|
| LC-MS（低分辨率） | 根/叶组织提取物中 ascaroside 代谢产物检测（EIC） | 1 µM ascr#18 处理，24 h |
| HPLC-MS（高分辨率，HRMS） | 根分泌物定量分析（连续 48 h 追踪） | 生长培养基浸根收集 |
| ¹³C 同位素追踪 | 验证 ascr#18→ascr#9 代谢转化 | ¹³C₂-ascr#18，番茄根，LC-MS |
| 时间课程代谢分析 | ascr#18 消耗 & ascr#9 积累动力学 | 处理后 0–96 h，*Arabidopsis* 叶片，n=3 |
| *Arabidopsis* 突变体分析 | acx1, acx5, acx1 acx5, ech2, ibr10 等突变体比较代谢 | 1 µM ascr#18 处理，LC-MS 定量 |
| 根结线虫感染实验 | *M. incognita* J2 接种 *Arabidopsis*，计数根瘤 | ascr#18 预处理 48 h，6 周后计数，n≥15 |
| 幼虫趋向性实验（Pluronic gel） | 在含 Pluronic F-127 gel 的 12-well 板中计数 J2 触碰根尖数量 | n=12 |
| 趋化性双区实验 | 6 cm Petri dish，~100 条 J2 置于中央，计数分布 | ascr 混合物组合，n=12 |
| RNA-Seq 分析 | *Arabidopsis* 根系防御基因表达（ascr#18 处理 24 h） | NCBI-SRA: PRJNA550121 |
| qRT-PCR | 防御相关基因（PR-1, PR-4, FRK1, WRKY53, PDF1.2, AOS, LOX2, PHI1）表达验证 | n≥6 |
| 细菌抗性实验 | *P. syringae* pv. *tomato* DC3000 感染，ascr#18 预处理 | 接种后 3 天细菌计数，n=17 |

---

## 关键数据（分小节）

### ascr#18 代谢产物鉴定

- *Arabidopsis* 根暴露于 1 µM ascr#18 后，检测到 ascr#10（C9 侧链，m/z 303.1813）、ascr#1（C7，m/z 275.1500）、ascr#9（C5，m/z 247.1187），三种物种（*Arabidopsis*、番茄、小麦）均有相同代谢模式。
- ascr#9 为最主要积累产物，峰面积约为 ascr#18 处理组的 3–4 倍（相对于对照），ascr#10 积累量最少。
- ¹³C₂-标记确认 ascr#9 来源于 ascr#18 β-oxidation（非内源），m/z 偏移 +2，对应 ¹³C₂ 标记的 ascr#9（249.1254 vs 247.1187）。

### 代谢动力学

- ascr#18 半衰期约 0.5–3 h（叶片浸润后快速下降）。
- ascr#9 峰值出现在处理后 1–12 h，之后缓慢清除，至 96 h 仍可检测。

### 遗传学证据

- *acx1 acx5* 双突变体中 ascr#18 代谢量极低，ascr#9 不可检出（n.d.），ascr#10 及更短链产物均消失。
- *ech2*、*ibr10* 单突变体及 *acx1* 或 *acx5* 单突变体代谢基本正常，提示 ACX1/ACX5 功能冗余。

### 驱虫活性

- 50 nM ascr#18 预处理 wt：J2 触根数从 ~6 降至 ~3（p < 0.001）；*acx1 acx5*：无显著变化（p > 0.05）。
- 50 nM ascr#9 处理 wt：J2 触根数显著减少（p = 0.014）；*acx1 acx5* 同样无效（符合该突变体缺乏 ascr#9 分泌的预期）。
- ascr#18（10 nM）+ ascr#9（100 nM）混合物 attraction index = −0.61（p = 0.0026），驱避效果最强；1:1 比例（ascr#18/ascr#9 = 1:1）时略弱。
- 1 µM ascr#18 处理不能在 *acx1 acx5* 中提供额外根瘤保护（wt 有显著减少，acx1 acx5 无）。

### 根系分泌

- HPLC-MS 定量：ascr#9 为最主要根分泌 ascaroside；ascr#10 最少；两者均在 *acx1 acx5* 中检出减少。
- ascr#1 也被检出，但丰度低于 ascr#9。

### 防御信号独立性

- ascr#18 处理（50 nM 和 1000 nM）在 wt 和 *acx1 acx5* 中均上调 JA 标记基因（AOS、LOX2、PDF1.2，p < 0.0001）；两者诱导幅度相当，说明 β-oxidation 不影响 JA/SA 激活。
- WRKY53（SA marker）在 wt 中由 ascr#18 诱导（p = 0.048），*acx1 acx5* 中诱导较弱。

---

## 与项目的关系

本文直接揭示了 **ascr#18 在植物根际的代谢命运**，与 iGEM 2026 干实验的核心问题高度相关：

1. **ascr#18 在土壤/田间的稳定性**：植物根系能在数小时内（半衰期约 0.5–3 h）将 ascr#18 通过 β-oxidation 迅速降解为 ascr#10、ascr#1、ascr#9。这意味着在真实根际环境中，施用的 ascr#18 不会长期以原形存在，其**有效窗口期短**，需在建模中考虑浓度衰减动力学。

2. **代谢产物 ascr#9 的生物活性**：ascr#9（C5 侧链）是 ascr#18 的最主要代谢终产物，同时具有独立的线虫驱避活性。若项目考虑 ascr#18 作为线虫防治信号，则需考量 ascr#9 的驱避贡献可能与 ascr#18 协同或替代。

3. **代谢途径保守性**：番茄和小麦均执行相同的 β-oxidation 代谢，意味着该降解途径在田间作物中普遍存在，ascr#18 的土壤命运不是物种特异的。

4. **量化参考**：1 µM ascr#18 施用后 24 h，根系已积累 ascr#9 至 peak area ~3–4×10⁶（相对单位），为建模降解速率和产物积累曲线提供实验参照。

---

## 关键引用（原文 References）

1. Manosalva, P. et al. Conserved nematode signalling molecules elicit plant defenses and pathogen resistance. *Nat. Commun.* **6**, 7795 (2015). — ascr#18 激活植物免疫的原始报道。
2. Schroeder, F. C. Modular assembly of primary metabolic building blocks. *Chem. Biol.* **22**, 7–16 (2015). — ascaroside 结构多样性的综述。
3. Nugent, J. H. et al. A novel ascaroside controls the parasitic life cycle of the entomopathogenic nematode *Heterorhabditis bacteriophora*. *PLoS Pathog.* **8**, e1002612 (2012). — 寄生线虫 ascaroside 化学通讯。
4. Zhang, Y. K. et al. Intraspecific nematode signals regulate dispersal behavior. *PLoS ONE* **7**, e38735 (2012). — 线虫 ascaroside 种内信号。
5. Kiontke, K. C. et al. A phylogeny and molecular barcodes for *Caenorhabditis*, with numerous recognized taxa. *PLoS ONE* **6**, e22390 (2011). — *C. elegans* 分类背景。
6. Graham, I. A. Seed storage oil mobilization. *Annu. Rev. Plant Biol.* **59**, 115–142 (2008). — 植物 β-oxidation 综述（种子脂肪酸代谢）。
7. Fradin, E. F. & Thomma, B. P. H. J. Physiology and molecular aspects of *Verticillium* wilt diseases caused by *V. dahliae* and *V. albo-atrum*. *Mol. Plant Pathol.* **7**, 71–86 (2006). — 植物-土壤病原体互作背景。
8. Akira, S., Uematsu, S. & Takeuchi, O. Pathogen recognition and innate immunity. *Cell* **124**, 783–801 (2006). — PAMP/PTI 免疫概念框架。
