# Letia et al. 2025 — 文献总结

> **完整标题**: Ascaroside#18 Promotes Plant Defence by Repressing Auxin Signalling
> **期刊**: *Physiologia Plantarum*, 2025; 177:e70386
> **DOI**: https://doi.org/10.1111/ppl.70386
> **作者**: Sharon Letia, Sabarna Bhattacharyya, Badou Mendy, Ute C. Vothknecht, Stephan H. von Reuss, Masaki Inada, Florian M. W. Grundler, M. Shamim Hasan
> **机构**: INRES - Molecular Phytomedicine, University of Bonn（德国）; Plant Cell Biology, University of Bonn; Laboratory for Bioanalytical Chemistry, University of Neuchâtel（瑞士）; Department of Biotechnology and Life Science, Tokyo University of Agriculture and Technology（日本）
> **接受日期**: 2025年6月17日（Open Access）

---

## 核心发现（5-10 bullets，含数据）

- **ascr#18 诱导广谱病原体抗性，但不触发经典 PTI 响应**：三种浓度（0.001、0.01、1 µM）的 ascr#18 预处理均未引发 ROS burst（相对于 flg22 阳性对照），也未导致 flg22 典型的生长抑制，表明其防御机制为非经典 PTI 途径。

- **ascr#18 显著降低胞囊线虫（*Heterodera schachtii*，CN）侵染**：三种浓度预处理均使雌性数量（females/plant）显著降低（mock 约 17，1 µM ascr#18 约 10，*p* < 0.0001）；总线虫数（males + females）同样显著减少；雌虫体积和 syncytia 面积均约缩小 40–50%（14 dpi）。

- **抗性独立于过氧化物酶体 β-氧化途径**：在 *acx1acx5* 双突变体（peroxisomal β-oxidation 缺失，无法将 ascr#18 代谢转化为 ascr#9）中，ascr#18 处理仍保持显著抗性，说明 ascr#9（nematode repellent）不是 ascr#18 抗性的唯一贡献者，存在独立的防御机制。

- **RNA-Seq 揭示 auxin 转运与信号通路基因强烈下调**：ascr#18 处理的拟南芥根中，FDR < 0.05 下共获得 114 个 DEG，其中 49 个下调、65 个上调；下调基因富集于"auxin 激活信号通路"和"response to auxin"GO terms（fold enrichment > 40）；经典防御基因无显著变化。

- **四个关键 auxin 基因被 ascr#18 显著下调**：*AUX1*（auxin influx carrier）、*GH3.6*（auxin 氨基酸结合酶）、*IAA27*（auxin-responsive gene）、*SAUR69*（小 auxin 上调 RNA）均在 RT-qPCR 中证实下调（*p* < 0.01），且此下调与已知 ascr#18 受体 *NILR1* 无关（*nilr1* 突变体中同样下调）。

- **ascr#18 对 auxin 的抑制在线虫侵染期间持续存在**：在 *H. schachtii* 侵染后 3 dpi 的取食位点，ascr#18 预处理组的 *AUX1* 和 *IAA27* 表达仍显著低于对照（*p* < 0.05），表明抑制作用在侵染条件下持续。

- **ascr#18 通过抑制 AUX1 蛋白破坏早期 syncytia 中的 auxin 内流**：proAUX1::AUX1-YFP 荧光成像显示，ascr#18 处理后未感染根及感染位点（3 dpi）的 AUX1-YFP 荧光信号均显著降低，说明 ascr#18 在空间上阻断了 syncytia 发育早期的 auxin 内流。

- **auxin 可用性降低损害 syncytia 发育**：DR5::GUS 报告系分析显示，ascr#18 处理的幼嫩 syncytia（3 dpi）中 auxin 信号（GUS 染色）显著弱于对照，导致更小的 syncytia 和更小的成年雌虫，从而降低线虫繁殖成功率。

---

## 实验方法（表格）

| 方法 | 详情 |
|------|------|
| 植物材料 | *Arabidopsis thaliana* Col-0, *nilr1* 突变体, *acx1acx5* 双突变体; 12 日龄幼苗 |
| 线虫侵染 | *Heterodera schachtii* 二龄幼虫（J2s）；70–80 条/植株；感染后 12 dpi（雌雄计数）/ 14 dpi（体积测量）|
| ascr#18 处理浓度 | 0.001、0.01、1 µM；24 h 预处理 |
| ROS burst 测定 | 发光素酶法（luminol-based assay），90 min 时程，Col-0 叶片盘 |
| 生长抑制测定 | 5 日龄幼苗转入含 ascr#18 或 flg22 培养基，7 dpi 测鲜重 |
| RNA-Seq | 12 日龄根，6 h ascr#18 处理后提取 RNA；NGS Core Facility（Illumina）；cutadapt 去接头；HISAT2 比对 *A. thaliana* 参考基因组（TAIR10） |
| 差异表达分析 | EdgeR 包，FDR < 0.05；GO enrichment 用 featureCounts + clusterProfiler |
| RT-qPCR | Quick-RNA Miniprep；高容量 cDNA 反转录试剂盒；SsoAdvanced Universal SYBR Green；内参 *UBQ10* / 18S rRNA |
| 荧光显微镜 | proAUX1::AUX1-YFP 转基因系；Leica SP5 激光共聚焦显微镜；100 µm scale bar；3 dpi 收样 |
| Syncytia 位点取样 | 侵染后 3 dpi，沿根取 ≤0.2 cm 含侵染位点段，液氮速冻，Applied Biosystems 提取 RNA |
| GUS 染色 | DR5::GUS 报告系；3 dpi syncytia；组织化学染色后光镜观察 |
| 统计 | GraphPad Prism v10.4.0；one-way ANOVA + Tukey's post hoc；*p* < 0.05 |

---

## 关键数据（分小节）

### 线虫侵染抗性（图 1）

| 指标 | Mock | 1 µM ascr#18 | 0.01 µM | 0.001 µM |
|------|------|-------------|---------|----------|
| 雌性数/植株（12 dpi） | ~17 | ~10* | ~12* | ~14 |
| 总线虫数/植株 | ~27 | ~16* | ~17* | ~20* |
| 雌虫面积（mm²，14 dpi） | ~0.16 | ~0.09* | ~0.10* | ~0.09* |
| Syncytia 面积（mm²） | ~0.11 | ~0.08* | ~0.08* | ~0.08* |

*表示 *p* < 0.05 vs. Mock（ANOVA + Tukey）

### PTI 响应（图 2）

- ROS burst：ascr#18（三浓度）与 Mock 无显著差异；flg22 总 RLU 约 350,000，ascr#18 各组 < 50,000（*p* < 0.0001 flg22 vs. 其余）
- 生长抑制：flg22 组鲜重约 25 mg（严重抑制）；ascr#18 各组与 Mock（约 150 mg）无显著差异

### β-氧化独立性（图 3，*acx1acx5*）

- 三种浓度 ascr#18 在 *acx1acx5* 背景下仍显著降低雌性数和总线虫数（*p* < 0.0002）
- 雌虫和 syncytia 面积同样显著减小，与 Col-0 表型一致

### RNA-Seq 差异表达（图 4）

- 114 个 DEG（FDR < 0.05）：49 个下调，65 个上调
- 下调 GO terms 富集：auxin-activated signalling（fold enrichment ~60）、response to auxin（~40）
- 仅 1 个 PTI 相关基因 *PR4* 上调；*NILR1* 无显著变化

### Auxin 基因下调（图 4D，5）

| 基因 | 功能 | 下调程度（LogFC，RNA-Seq） |
|------|------|--------------------------|
| *AUX1* | Auxin influx carrier | ~−1.4 |
| *GH3.6* | IAA-氨基酸结合酶（auxin 结合） | ~−0.8 |
| *IAA27* | Aux/IAA 转录抑制子 | ~−1.1 |
| *SAUR69* | 早期 auxin 响应基因 | ~−1.2 |

RT-qPCR 在 *nilr1* 背景下三个基因（AUX1、GH3.6、SAUR69）仍显著下调，IAA27 在 *nilr1* 中 p = 0.003（图 5）。

### Syncytia 中 AUX1-YFP 荧光（图 7）

- ascr#18 处理 + 未感染：根中 AUX1-YFP 荧光强度显著低于 Mock/Ui
- ascr#18 处理 + 感染（3 dpi）：感染位点 AUX1-YFP 信号进一步显著降低

---

## 与项目的关系

本文直接阐明 ascr#18（iGEM 2026 干实验核心配体）在植物免疫中的分子作用机制。关键相关性如下：

1. **ascr#18 生物活性机制背景**：本文提供了 ascr#18 作为 NAMP（nematode-associated molecular pattern）触发广谱抗性的最新机制——通过下调 auxin 转运与信号通路（非经典 PTI），为理解 ascr#18 为何能激活植物防御提供了分子层面的解释。

2. **受体-配体关系**：文中提到 ascr#18 被 NILR1（leucine-rich repeat receptor）识别，但 auxin 信号抑制独立于 NILR1，暗示 ascr#18 还通过其他受体或下游途径发挥作用。这与干实验建模中 GprC/Gpr2/Gpr3 作为 ascr#18 候选受体的研究视角互补——本文提供了 ascr#18 感知的植物侧机制背景。

3. **防御机制的有效浓度范围**：0.001–1 µM 范围内均有效，这对 ascr#18 应用浓度的合理性判断有参考价值。

4. **与 GprC 相关性**：GprC 在线虫中感知 ascr#18，本文则从植物角度揭示 ascr#18 如何削弱线虫取食位点（syncytia）发育，二者从不同物种侧面共同描述 ascr#18 在寄主-线虫互作中的核心地位。

---

## 关键引用（8条）

1. **Mendy et al. 2017** — 鉴定 NILR1 为 ascr#18 的受体（PRR），首次报告 ascr#18 触发 PTI 类防御，为本文的独立机制发现提供对照背景。*EMBO J* 36:2528–2639.

2. **Manohar et al. 2020** — 阐明拟南芥通过 peroxisomal β-oxidation 将 ascr#18 代谢为 ascr#9（repellent）；本文证明此代谢途径非 ascr#18 抗性的唯一途径。*New Phytologist* 223:1811–1824.

3. **Huang et al. 2023** — 报告 NILR1 功能损失影响 PTI 响应；本文利用 *nilr1* 突变体证实 auxin 抑制独立于 NILR1。*Plant Cell* 35:3519–1529.

4. **Navarro et al. 2006** — 首次证明 PAMP flg22 通过 miR393 降解 auxin 受体 mRNA（GH3-like、IAA12、IAA17），是 PTI 通过 auxin 途径调控免疫的经典文献，为本文机制提供概念框架。*Science* 312:436–439.

5. **Kyndt et al. 2016** — 证明 AUX1 主导的 auxin 内流对 gall 形成（根结线虫）至关重要，为本文 syncytia 中 AUX1 被 ascr#18 抑制的功能意义提供实验依据。*J Exp Bot* 67:13:3833–3843.

6. **Goverse et al. 2000** — 证明外源 auxin 施用促进 syncytia 发育；本文通过 DR5::GUS 降低印证 auxin 可用性下降损害 syncytia 发展。*Mol Plant Microbe Interact* 13:1089–1099.

7. **Gutierrez et al. 2009** — 证明 Meloidogyne incognita 促进 auxin 生物合成以操控取食位点；与本文 ascr#18 反向抑制 auxin 的新型防御机制形成对比。*Plant Physiology* 150:1:315–326.

8. **Wang et al. 2007** — 水杨酸通过抑制 auxin 信号途径阻止植物生长，揭示 SA-auxin 拮抗在免疫中的作用，是本文讨论 auxin 作为 susceptibility factor 的概念依据。*Current Biology* 17:20:1784–1790.
