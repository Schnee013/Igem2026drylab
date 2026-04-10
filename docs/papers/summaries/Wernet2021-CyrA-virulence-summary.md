# Wernet et al. 2021 — 文献总结

> **完整标题**: The small-secreted cysteine-rich protein CyrA is a virulence factor participating in the attack of *Caenorhabditis elegans* by *Duddingtonia flagrans*
> **期刊**: PLoS Pathogens 17(11): e1010028 (2021年11月4日)
> **DOI**: https://doi.org/10.1371/journal.ppat.1010028
> **作者**: Nicole Wernet, Valentin Wernet, Reinhard Fischer
> **机构**: Karlsruhe Institute of Technology (KIT) — South Campus, Institute for Applied Biosciences, Dept. of Microbiology, Karlsruhe, Germany

---

## 核心发现（5-10 bullets，含数据）

- **CyrA 是 *D. flagrans* 基因组编码的 small-secreted protein (SSP)**：155个氨基酸，N端含21 aa信号肽，富含半胱氨酸区域（8个Cys残基），无保守结构域；同源蛋白仅见于另外两种NTF（*A. oligospora*、*M. haptotylum*），不见于非捕食性真菌。

- **cyrA 在捕食互作中被转录诱导**：与 *C. elegans* 共培养24 h后，qRT-PCR显示 cyrA 表达量上调，fold change平均为5.7–18.9（三个生物学重复；P = 0.0342）；荧光素报告基因实验进一步确认诱导主要发生在陷阱（trap）及陷阱内的营养菌丝中，周围营养菌丝中荧光微弱。

- **CyrA 在感染泡（infection bulb）积累，依赖 Golgi 分泌途径**：CyrA-mCherry 在线虫被穿刺进入后立即出现在穿刺点内侧的感染泡。Brefeldin A（BFA，ER→Golgi 转运抑制剂）处理后，感染泡无法积累 CyrA，线虫穿刺被抑制（5小时后大多数陷阱线虫仍无穿刺位点）。

- **外泌体复合物（exocyst complex）对 CyrA 定向转运至感染泡膜至关重要**：敲除 exoA（Exo70同源基因）后，CyrA 无法在感染泡内膜积累，而是停留在外侧膜缘；Δexo70菌株毒力显著下降，L4幼虫麻痹时间由野生型 103 min（SD ± 46）延长至 166 min（SD ± 75；p < 0.0001）。

- **cyrA 缺失（ΔcyrA）菌株毒力减弱**：ΔcyrA 捕获 L3幼虫的麻痹时间从野生型 49 min（SD ± 27）延长至 ~95 min（SD ± 44），回补株（Re）恢复至 62 min（SD ± 39）（p < 0.0001）；捕获 L4幼虫时，野生型 103 min vs ΔcyrA 184 min（SD ± 92）；但菌落形态、产孢量与 WT 无显著差异，说明 CyrA 特异作用于毒力。

- **CyrA 被分泌后在 *C. elegans* 体腔细胞（coelomocytes）积累**：在线虫中异源表达带信号肽的 cyrA（hsp-16.48 热激启动子），CyrA-Scarlet/GFP 积累在头部、中体和尾部两处——与 coelomocytes 位置一致（共定位实验 unc-122(p)::GFP 确认）。cup-8 突变体（coelomocyte 内吞缺陷）中积累信号均匀分布，支持 CyrA 被 coelomocytes 内吞。

- **cyrA 在 *C. elegans* 中异源表达缩短寿命**：在 N2 背景下，col-19 启动子驱动的 cyrA（含 SP）表达导致寿命显著缩短（EV vs. +SP P = 1.2E-06）；coelomocyte 摄取缺陷株 GS2478 中无此效应（P = 0.9），提示 CyrA 的毒性作用通过 coelomocytes 相关信号通路介导。

- **CyrA 定位于陷阱细胞特异囊泡，与已知细胞器（ER、exosome、peroxisome 等）均不共定位**：推测存在一类陷阱特异分泌途径，与哺乳动物神经内分泌细胞的调控分泌颗粒（regulated secretory granules）具有功能相似性。

---

## 实验方法（表格）

| 方法 | 关键细节 |
|------|---------|
| 菌株与培养 | *D. flagrans* CBS 349.94，28°C PDA 或 LNA（KCl, MgSO4, ZnSO4, FeCl3, 琼脂）；同步化 *C. elegans* N2/BAN126 L3/L4幼虫 |
| 陷阱诱导 | 1×10⁴ *D. flagrans* 孢子接种 LNA，添加 ~100 条 *C. elegans*，28°C 暗培养 12–24 h |
| qRT-PCR | Trizol 提取总 RNA；CFX Connect Real-Time PCR；actin 内参；3技术×3生物学重复 |
| 荧光融合蛋白 | cyrA(p)::CyrA-mCherry/GFP；h2b(p)::h2b-mCherry 对照；*A. nidulans* oliC 构成型启动子对照 |
| 转录报告基因 | cyrA 启动子驱动 H2B-mCherry 核定位，荧光激光共聚焦（Zeiss Airyscan LSM 900）观察 |
| 定位分析 | 与 ClaH（clathrin）、BroA（exosome）、RabA（endosome）、GFP-SKL（peroxisome）、GFP-KDEL（ER）、H2B-GFP 共表达比较 |
| BFA处理 | 50 µg/ml BFA 处理 *D. flagrans*，共培养 LNA 玻片，时间间隔拍摄（最长5 h）|
| 基因敲除 | 同源重组替换（hygromycin-B 抗性盒），Southern blot 确认；PstI（cyrA）或 EcoRI（exoA）验证 |
| 毒力实验 | 捕获单虫后长时间间隔拍摄（每2分钟，共12 h），记录从捕获到麻痹时间；Student's t-test 统计 |
| *C. elegans* 异源表达 | cyrA 克隆入 pLZ29；hsp-16.48 或 col-19 启动子；显微注射 5 ng/µL；37°C 1 h 热激诱导 |
| 寿命实验 | 30 条 L4 线虫转入 NGM+150 µM FUdR，20°C 培养；Kaplan-Meier + log-rank test（OASIS）|
| ABTS 分泌实验 | CyrA 信号肽融合 *A. nidulans* LccC（漆酶），LNA+1 mM ABTS，48 h 蓝绿色圈验证信号肽功能 |

---

## 关键数据

### 表达诱导
- cyrA 与 *C. elegans* 共培养24 h后 fold change：5.7（±0.7）, 7.9（±1.4）, 18.9（±2.6）（3个生物学重复，P = 0.0342）
- 荧光定量（ImageJ）：cyrA(p) 诱导 vs 非诱导 P < 0.0001

### 毒力表型（麻痹时间，均值 ± SD）
| 菌株 | L3幼虫 | L4幼虫 |
|------|--------|--------|
| WT | 49 min (±27) | 103 min (±46) |
| ΔcyrA | ~95 min (±44) | 184 min (±92) |
| Re（回补） | 62 min (±39) | — |
| ΔexoA | — | 166 min (±75) |
| Re(ΔexoA) | — | 108 min (±46) |

### CyrA 分泌时程
- BFA 实验：感染泡积累被完全阻断，5 h 后无穿刺位点
- 正常条件：穿刺约60 min后 CyrA 在感染泡可见（与穿刺时间吻合）

### 寿命实验
- N2 中 cyrA(+SP) 表达：EV vs +SP P = 1.2E-06（显著缩短）
- GS2478（cup-8 突变，coelomocyte 摄取缺陷）：EV vs +SP P = 0.9（无影响）
- EV vs ΔSP（N2）：P = 0.0001（无信号肽也有轻微影响，提示细胞内积累毒性）

---

## 与项目的关系

本文研究对象为 *Duddingtonia flagrans*（NTF），与本项目核心受体所在物种（*Arthrobotrys flagrans*/*A. oligospora*）同属线虫捕食真菌（NTF）。

**直接相关性**：

1. **Fischer 实验室体系**：本文即 Fischer 实验室（KIT）对 *D. flagrans* 的攻击机制研究，属于 iGEM 项目引用的核心实验室背景文献之一。文中多次提及 *A. oligospora* 和 *M. haptotylum* 基因组分析（PHI-base、RNAseq 数据）作为背景对比，证明 cyrA 在 NTF 中高度保守。

2. **NTF 攻击线虫的分子机制**：CyrA 代表了 NTF 中第一个被实验功能验证的 SSP 毒力因子，揭示了 NTF 不仅依赖物理（陷阱）和酶（水解酶）杀虫，还分泌特异蛋白操控宿主。这为理解 ascaroside 感知上游信号（线虫是否通过感知 NTF 的 SSP 或其他分子来调控行为）提供了分子层面背景。

3. **ascaroside 与陷阱诱导的联系**：本文 Introduction 明确指出 NTF 通过感知线虫特异性 ascarosides 来诱导陷阱形成（引文 [18,19]），这与本项目研究 GprC/Gpr2/Gpr3 对 ascaroside 感知的机制直接相关——CyrA 的诱导表达正是 ascaroside 激活下游反应链的结果之一。

4. **局限**：本文不涉及受体（GPCR）或 ascaroside 感知通路，CyrA 的宿主靶点未知，*C. elegans* 中的具体毒性机制（是否干扰免疫信号？）尚待解析。

---

## 关键引用

1. **Youssar L et al. (2019)** *PLoS Genet* — *D. flagrans* 陷阱形成的细胞间通信机制（cyrA上调的背景基础，Ref [15]）

2. **Hsueh YP et al. (2017)** *eLife* — *A. oligospora* 通过模拟 ascaroside 嗅觉线索诱捕线虫，NTF–nematode 化学通信直接证据（Ref [17]）

3. **Hsueh YP et al. (2013)** *PLoS Biol* — NTF 通过线虫信息素（ascaroside）促进陷阱形成（Ref [18]）

4. **Yu X et al. (2021)** *Nat Commun* — ascaroside 直接吸引 *C. elegans* 至 *A. oligospora* 陷阱，线虫行为操控（Ref [19]）

5. **Giraldo MC, Dagdas YF et al. (2013)** *Nat Commun* — *M. oryzae* 两种分泌系统（Golgi依赖与exocyst依赖）的功能区分（Ref [23]，BFA实验概念基础）

6. **Kim S et al. (2020)** *Nat Commun* — 稻瘟病菌两个核效应蛋白通过转录重编程调控宿主免疫（Ref [41]，SSP毒力研究的比较背景）

7. **Fares H, Greenwald I (2001)** *Genetics* — *C. elegans* coelomocyte 内吞缺陷突变 cup-8，胞外蛋白摄取功能（Ref [36]）

8. **Gupta YK et al. (2015)** *Plant Cell* — *M. oryzae* 中 septin 依赖的 exocyst 组装与植物感染（Ref [25]，exocyst 在真菌毒力中的功能类比）
