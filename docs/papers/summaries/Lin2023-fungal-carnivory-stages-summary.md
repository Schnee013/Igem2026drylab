# Lin et al. 2023 — 文献总结

> **完整标题**: Key processes required for the different stages of fungal carnivory by a nematode-trapping fungus
> **期刊**: PLoS Biology, 21(11): e3002400
> **DOI**: https://doi.org/10.1371/journal.pbio.3002400
> **发表日期**: 2023-11-21
> **作者**: Hung-Che Lin†, Guillermo Vidal-Diez de Ulzurrun†, Sheng-An Chen†, Ching-Ting Yang, Rebecca J. Tay, Tomoyo Iizuka, Tsung-Yu Huang, Chih-Yen Kuo, A. Pedro Gonçalves, Siou-Ying Lin, Yu-Chu Chang, Jason E. Stajich, Erich M. Schwarz, Yen-Ping Hsueh
> **通讯作者**: Yen-Ping Hsueh（ping hsueh@gate.sinica.edu.tw）
> **机构**: Institute of Molecular Biology, Academia Sinica, Taipei（主）；台湾国防医学中心；台北医学大学；University of California, Riverside；Cornell University
> **数据**: NCBI GEO GSE233568

---

## 核心发现（5–10 bullets，含数据）

- **时间课程转录组揭示高度动态的应答**：将 *A. oligospora* 暴露于 *C. elegans* 后，在 2、4、10、24、48 hpe（hours post-exposure）共 6 个时间点取样，鉴定出 2,693 个差异表达基因（q < 0.01，|beta| > 1）；其中 159 个基因在所有时间点持续上调，318 个持续下调，为核心捕食必需基因候选。

- **早期阶段（2–10 hpe）：核糖体生物合成与 DNA 复制上调驱动陷阱形态发生**：GO 富集显示"structural constituent of ribosome"（GO:0003735）、"rRNA processing"（GO:0006364）、"nucleolus"（GO:0005730）为 2–10 hpe 最显著富集项。陷阱细胞核数（平均 10 个）显著多于营养菌丝（平均 2 个）。雷帕霉素（rapamycin，4 µg/ml）抑制 TOR 后陷阱数量显著减少、线虫存活率提高；羟基脲（HU，200 mM）抑制 DNA 复制后陷阱数量也显著减少。

- **分泌组大规模激活**：*A. oligospora* 预测分泌蛋白组（secretome）共 1,084 个，其中 549 个（50.6%）在 *C. elegans* 暴露后差异表达。进一步预测出 417 个效应蛋白（effectors），其中 209 个（50.1%）差异表达，且在 4–10 hpe 时多数上调。

- **t-SNARE 蛋白 Sso2 对陷阱功能不可或缺**：*sso2* 缺失突变体陷阱数量与野生型相当（无显著差异），但 70% 的线虫能逃脱 *sso2* 陷阱，而野生型几乎为 0% 逃脱率（p < 0.0001）。表明蛋白分泌对线虫黏附功能至关重要。

- **DUF3129 基因家族（TEP 家族）在 NTF 中显著扩张**：*A. oligospora* 基因组含 27 个 DUF3129 域蛋白基因，其中 15 个在 10 hpe 时表达峰值最高。扫描 2,504 个真菌基因组发现约 99% 的物种含少于 5 个 DUF3129 基因，而多数 NTF 物种含超过 20 个，且基因扩张主要发生在 Ascomycete NTF 进化枝内。作者将这类富集于陷阱的 DUF3129 蛋白命名为 **Trap Enriched Proteins（TEPs）**。

- **TEP1 蛋白定位于陷阱表面，对线虫黏附必需**：TEP1-GFP 活体成像显示 EYR41_003105（TEP1）蛋白从菌丝流向陷阱并定位于陷阱细胞表面。*tep1* 突变体中，仅 10% 的线虫在接触 10 分钟内被捕获（野生型接近立即捕获）；TEP1 互补菌株恢复捕获效率，而 *tep4*、*tep5* 缺失无明显影响。TEP 蛋白 C 端具高度无序区（IDR），可能形成液-液相分离（LLPS）凝聚体参与黏附。

- **晚期阶段（24–48 hpe）：金属蛋白酶等多类蛋白酶上调，驱动消化**：共识别 323 个蛋白酶编码基因，其中 119 个差异表达（包括 15 天冬氨酸、14 半胱氨酸、62 丝氨酸、39 金属、3 苏氨酸蛋白酶）。4 个金属蛋白酶/丝氨酸蛋白酶（Spr1、Spr2、Mcp1、Amp1）在 24 hpe 后表达量最高（Spr1 TPM 约达 3,500）。蛋白酶抑制剂鸡尾酒（PIC）处理显著延缓菌丝在线虫体内的侵殖（12 hpe 时对照组 vs PIC 组差异显著，p < 0.0001）。

- **金属蛋白酶 Mcp1 和 Amp1 缺失导致菌丝体内定殖效率降低**：*mcp1* 和 *amp1* 单敲除突变体均能正常形成陷阱，但线虫体内的定殖百分比显著低于野生型（p < 0.01），说明这两种金属蛋白酶在穿透/消化阶段有功能性作用。

---

## 实验方法（表格）

| 方法 | 详情 |
|------|------|
| RNA-seq | *A. oligospora* TWF154 暴露于 *C. elegans* N2 L4 幼虫，2–3,000 条/皿；2、4、10、24、48 hpe 取样（+对照组），3 个生物学重复；Illumina NextSeq500，76 bp 单端 + 2×75 bp 配对末端；Kallisto 定量，Sleuth 差异分析 |
| 差异表达阈值 | q < 0.01，\|beta\| > 1（log fold change）；Wald 检验；Likelihood ratio test |
| 主成分分析 | PC1 70.0%，PC2 12.3%；同时间点重复聚集良好 |
| 分泌组预测 | SignalP 5.0 + Phobius + TMHMM + WoLFPSort；三个列表整合；最终 1,084 个预测分泌蛋白，913 来自 list A（84.2%）|
| 效应蛋白预测 | EffectorP-fungi 3.0；417 个预测效应蛋白（占分泌组 38.5%）|
| DUF3129 分布 | MycoCosm 2,504 个真菌基因组 BlastP；19 个高质量基因组 OrthoFinder 直系同源分析；IQ-TREE 2 系统发育 |
| 靶向基因敲除 | *ku70* 背景同源重组，潮霉素/G418 抗性标记；PCR 验证 |
| 表型鉴定 | 陷阱数量定量（LNM 平板，*C. elegans* L4 诱导）；线虫逃脱率（50 条线虫捕获实验）；细胞核计数（H2B::mCherry 菌株）|
| 菌丝侵殖可视化 | 胞质 GFP 菌株；Andor Revolution WD 系统 + Nikon Ti-E；XON Ultra 888 EMCCD 相机 |
| HCR in situ 杂交 | 第三代 HCR 方法；LSM980 Airyscan 2 共聚焦；C-Apochromat 63×/1.2 NA 水浸物镜 |
| 蛋白酶抑制实验 | 1× PIC（P2714，Sigma-Aldrich）处理菌体；牛乳平板验证抑制活性 |
| IDR/3D 结构预测 | PONDR VSL2 + PONDR VL3；AlphaFold2 |
| 雷帕霉素/HU 处理 | 4 µg/ml rapamycin 或 200 mM HU 补充到 LNM 培养基 |

---

## 关键数据（分小节）

### 转录组动态

- 差异上调基因数随时间：2 hpe 839、4 hpe 959、10 hpe 1,129、24 hpe 678、48 hpe 622
- 差异下调基因数随时间：2 hpe 1,552、4 hpe 1,471、10 hpe 1,760、24 hpe 1,141、48 hpe 996
- 5 个主要表达簇（soft clustering）：C0（994 基因，核糖体结构组分）、C1（310 基因，丝氨酸蛋白酶活性）、C2（234 基因，跨膜转运）、C3（927 基因，硫酸盐同化）、C4（228 基因，含氮化合物转化/硝酸盐同化）

### 分泌组 / 效应蛋白

| 类别 | 数量 | 占分泌组 % |
|------|------|-----------|
| 分泌组总蛋白 | 1,084 | 100% |
| 预测效应蛋白 | 417 | 38.5% |
| 预测胞质效应蛋白 | 114 | 10.5% |
| 预测非细胞效应蛋白 | 303 | 28.0% |
| 非效应蛋白 | 667 | 61.5% |

### DUF3129 / TEP 家族

- *A. oligospora* 基因组含 27 个 DUF3129 基因，散布于 8 条染色体，无基因组聚集
- 约 40%（11/27）被预测为推定效应蛋白
- 约 99% 的 2,504 个真菌基因组含少于 5 个 DUF3129 基因
- *tep1* 突变体：10 min 内仅 10% 线虫被捕获（WT 接近 100%）；*tep1* TEP1 互补菌株恢复

### 蛋白酶与消化

- 总蛋白酶基因 323 个；差异表达 119 个
- 4 种高表达金属/丝氨酸蛋白酶：Spr1（~3,500 TPM at 48 hpe）、Spr2、Mcp1、Amp1
- PIC 处理：12 hpe 时菌丝侵殖显著受阻（p < 0.0001）
- *mcp1*、*amp1* 单敲除：线虫体内定殖显著降低（p < 0.01）

---

## 与项目的关系

本文以 *A. oligospora* 为模型，系统描绘了 NTF 捕食的三个阶段（感知/陷阱形成/消化）的分子机制，为项目提供以下背景：

1. **感知阶段的信号机制**：文章明确指出线虫 ascarosides 是触发 *A. oligospora* 由腐生转为捕食的关键化学信号（Ref. 9, Hsueh et al. 2013），MAPK/信息素应答通路（Ste12）负责调控感知与陷阱形态发生（Ref. 18, Chen et al. 2021）。本项目研究 GprC（*A. flagrans*）和 Gpr2/Gpr3（*A. oligospora*）对 ascaroside 的感知，正处于该通路最上游的受体层——Lin 2023 提供了感知阶段下游转录应答的完整时间图谱，是受体功能验证的关键叙事背景。

2. **GprC/Gpr2/Gpr3 的功能语境**：本文的转录组数据显示，2–4 hpe（感知启动期）最显著的变化是核糖体生物合成，而非某单一信号通路激活，说明 ascaroside 受体感知信号激活后迅速引发大规模细胞状态转换。项目中的受体即是这一级联的"开关"。

3. **DUF3129/TEP 家族为 NTF 特异扩张基因**，提示 NTF 在受体介导的感知之外，还进化出了陷阱特异的黏附蛋白机制。项目叙事可据此凸显受体感知作为整个捕食行为起始节点的核心地位。

4. **物种关联**：本文聚焦 *A. oligospora*，Gpr2/Gpr3 即为该物种的 ascaroside 受体候选。*A. flagrans*（GprC 所在物种）在本文中也列为 NTF 参照，可作为跨物种比较的背景。

---

## 关键引用（文中编号与内容）

1. **[Ref. 9] Hsueh et al. 2013** — *A. oligospora* 能通过感知线虫 ascarosides（线虫种间信息素，deoxysugar-linked 脂肪酸衍生物）实现嗅探猎物；Curr Biol. PMID: 23246407。

2. **[Ref. 10] Hsueh et al. 2017** — *A. oligospora* 产生挥发性化学物质 methyl 3-methyl-2-butenoate 模拟线虫性信息素和雌雄同体线虫，用于引诱猎物接近；eLife. PMID: 28098585。

3. **[Ref. 18] Chen et al. 2021** — MAPK 信息素应答通路（由 Ste12 调控）是 *A. oligospora* 感知线虫和陷阱形态发生的必要条件；Genetics. PMID: 33724405。

4. **[Ref. 3] Vidal-Diez de Ulzurrun & Hsueh 2018** — NTF 与线虫的捕食者–猎物关系综述；Appl Microbiol Biotechnol. PMID: 29523933。

5. **[Ref. 8] Yang et al. 2020** — *A. oligospora* 捕食行为表现出天然多样性，建立了稳定模型菌株 TWF154；Proc Natl Acad Sci USA. PMID: 32201185。

6. **[Ref. 86] Huang et al. 2017** — DUF3129 基因家族在宿主感染性真菌中受 MAPK/Ste12 调控，跨物种保守机制；Philos Trans R Soc Lond B. PMID: 30967021。

7. **[Ref. 90] Tunlid & Jansson 1991** — NTF 产生的丝氨酸蛋白酶在捕捉后固定和消化线虫中的作用；Appl Environ Microbiol. PMID: 16348563。
