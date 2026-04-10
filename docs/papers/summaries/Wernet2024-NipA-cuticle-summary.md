# Wernet et al. 2024 — 文献总结

> **完整标题**: The cysteine-rich virulence factor NipA of *Arthrobotrys flagrans* interferes with cuticle integrity of *Caenorhabditis elegans*
> **期刊**: *Nature Communications*, 2024, 15:5795
> **DOI**: https://doi.org/10.1038/s41467-024-50096-4
> **作者**: Jennifer Emser, Nicole Wernet, Birgit Hetzer, Elke Wohlmann & Reinhard Fischer
> **机构**: Institute for Applied Biosciences, Department of Microbiology, Karlsruhe Institute of Technology (KIT) – South Campus; Max Rubner-Institut (MRI) – Federal Research Institute of Nutrition and Food, Karlsruhe 76131, Germany
> **通讯作者**: reinhard.fischer@KIT.edu

---

## 核心发现（5–10 bullets，含数据）

- **NipA（nematode induced protein A）** 是 *A. flagrans* 在侵染位点分泌的小分子分泌蛋白（SSP，small-secreted protein），含 16 aa 信号肽和 EGF-like 结构域，全长 133 aa，含 13 个半胱氨酸（12 个可能形成二硫键）
- **nipA 缺失突变体**（Δ*nipA*）穿透 *C. elegans* 的时间显著延长：WT 均值 64.38 min vs. Δ*nipA* 均值 77.53 min（*p* < 0.0001；*n* = 45），说明 NipA 在侵染早期促进穿透
- NipA **在侵染位点积聚**，定位于捕陷器内缘（inner rim）和侵染球（infection bulb）；CyrA-GFP（胞外基质蛋白）定位在侵染球内，两者在位置上形成互补；NipA 在侵染 *C. elegans* 体内不可见，提示其靶点位于胞外基质（ECM）
- **异源表达实验**：在 *C. elegans* 表皮细胞异源表达 *nipA*（使用 *col-19* 启动子）导致成虫出现**水疱（blisters）**，表型在野生型 N2 和 GS2478（coelomocyte 缺陷）背景中均重现；无信号肽的 NipA 变体（NipA^ΔSP^）不形成水疱，说明分泌（胞外化）是致疱的前提
- **水疱形成位于角质层内**：共表达 *mScarlet*（胞外标记）和 *nipA* 的表皮细胞，水疱破裂后荧光液体渗出但线虫不受进一步伤害；Cryo-SEM 显示水疱局限于无 alae 和 annuli 的区域，止于外阴，提示水疱发生于特定角质层组分缺失的部位（medial layer 无液态填充层）
- **关键半胱氨酸 Cys-23**（未配对半胱氨酸，AlphaFold 预测）对水疱形成必不可少：将 Cys-23 替换为 Ala 的转基因线虫不形成水疱
- **全基因组转录组分析**（RNA-seq，*col-19p::nipA* vs. *col-19p::mScarlet* 对照）：238 个差异表达基因（DEG）——73 个上调、53 个下调（|fold change| ≥ 2）；在两个 *nipA* 表达数据集中共享 229 个 DEG
  - 下调基因：富集**胶原蛋白**（collagen）和 **C-type lectin** 相关基因（ECM 组分）；*bli-6* 显著下调（fold change −2.4，*p* = 3.5 × 10⁻⁹）
  - 上调基因：富集**病原体压力反应**和**解毒**通路（含 C-type lectin）；String-DB 网络揭示 IRG-4（CUBL-domain）等免疫基因高度互联
- NipA 在 *C. elegans* 体内**被运输至 coelomocyte（体腔细胞）液泡**，使用 *eft-3* 泛启动子表达时可见，提示线虫自身通过内吞清除胞外 NipA；在 GS2478 背景中信号仍保留于 coelomocyte 位置但较弱
- VAB-10A（表皮中连接基底膜与角质层的中间丝相关蛋白）定位在 *nipA* 表达线虫中**不受影响**，说明水疱不是由表皮细胞膜破裂所致，角质层结构性完整性受损是原发事件

---

## 实验方法（表格）

| 方法 | 具体内容 |
|------|---------|
| 基因缺失 | CRISPR/HR，*nipA* ORF 替换为潮霉素抗性盒（hph），Southern blot 和 PCR 验证 |
| 荧光蛋白融合 | NipA-mCherry / NipA-GFP（C 端融合，使用 *A. nidulans laccase* 分泌系统 LccC 验证分泌活性）；CyrA-mCherry（胞外基质）；Lifeact-GFP（肌动蛋白）|
| 分泌活性检测 | Laccase C 端融合（NipA-LccC）：含/不含信号肽的 ABTS 氧化试验；颜色变化指示分泌 |
| 线虫捕获计时 | 捕陷器诱导后共培养，共聚焦显微镜每 9 min 记录 1 次，持续 11 h；t₀ = 捕陷器接触，t_end = CyrA-mCherry 首次在线虫体内出现 |
| 异源表达 | *C. elegans* 表皮：*col-19*(p)::*nipA* / *dpy-7*(p)::*nipA*；泛表达：*eft-3*(p)::*nipA*；长期观察（20 天，50 µM FUDR，90 只同期化成虫） |
| RNA-seq | TRIZOL 法提取，*col-19*(p)::*mScarlet*、*col-19*(p)::*nipA*::*mScarlet* 及 N2 对照；WormCat GO 分析（fold change ≥/≤ ±2） |
| Cryo-SEM | 25 µm LNA 薄板上的 *A. flagrans* 与线虫共培养 24 h 后 Cryo-SEM 成像 |
| 水疱针刺实验 | 27G 注射针穿刺水疱，观察荧光液体渗出及后续损伤 |
| Cys-23 突变 | *col-19*(p)::*nipA^Cys23Ala^* 染色体外阵列表达，孵育在含 50 µM FUDR 的 NGM 板 |
| VAB-10A::GFP | CRISPR 敲入 *vab-10a::GFP*，与 *col-19*(p)::*nipA* 共表达 |

---

## 关键数据（分小节）

### 穿透时间（*A. flagrans* 进入 *C. elegans*）

| 菌株 | 样本量 | 均值 ± SD（min） | 统计显著性 |
|------|--------|-----------------|-----------|
| WT | 45 | 64.38 ± 9.92 | — |
| Δ*nipA* | 45 | 77.53 ± 14.07 | *p* < 0.0001（vs. WT） |
| *nipA*-GFP（回补） | 26 | 63.81 ± 10.39 | *p* = 0.879（ns，vs. WT） |
| NipA^Cys23Ala^-GFP | 21 | 83.48 ± 13.61 | *p* < 0.0001（vs. WT） |

### 转录组差异表达基因（nipA vs. mScarlet，fold change ≥ 2）

| 方向 | 数量 | 主要功能类别 |
|------|------|------------|
| 上调 | 73 | 病原体压力反应、解毒（UDP-葡萄糖醛酸转移酶 UGT）、C-type lectin |
| 下调 | 53 | 胶原蛋白（collagen）、C-type lectin ECM 组分 |
| 两数据集共享 | 229 | — |

*bli-6*（胶原）显著下调，fold change = −2.4（*p* = 3.5 × 10⁻⁹）

### NipA 结构特征（AlphaFold 预测）

- 16 aa 信号肽（SP）+ EGF-like 结构域（残基 16–133）
- 13 个 Cys 残基：12 个预测形成胞内二硫键，第 23 位（N 端，SP 后）预测为**游离半胱氨酸**（unpaired）
- pLDDT 在 EGF-like 结构域区域较高，SP 区域较低（典型 SSP 特征）

---

## 与项目的关系

本文来自 Fischer 实验室（*A. flagrans* GprC 研究同一实验室，参见 Hu2024-GprC），研究对象为同一真菌物种 *A. flagrans* 与 *C. elegans* 的互作。

**直接关联点：**
1. **Fisher 实验室背景**：NipA 和 GprC 均来自 *A. flagrans* 侵染 *C. elegans* 的系统，有助于理解 ascaroside 感知（GprC）与侵染执行（NipA 等 SSP）在同一真菌中的功能分工
2. **线虫角质层**：本文揭示 NipA 靶向 *C. elegans* 角质层 ECM，干扰胶原蛋白表达（*bli-6* 下调），使真菌更容易穿透；这补充了 GprC 通过 ascaroside 感应启动捕陷器形成的上游信号机制
3. **研究范围限制**：NipA 是 SSP 毒力因子，与本项目 GprC/Gpr2/Gpr3 等 ascaroside 受体的 GPCR 对接研究属于不同层次（侵染执行 vs. 化学感应），不直接用于对接或 IFP 分析
4. **信号通路背景**：*C. elegans* 角质层完整性基因（collagen、C-type lectin）的下调表达提示真菌侵染涉及多重机制，ascaroside 诱导的 GprC 信号可能与 NipA 等效应蛋白协同作用

---

## 关键引用（3–8条）

1. **Emser J et al. (2024)** — 本文（NipA 及 *A. flagrans* SSP 毒力因子表征的第一手数据）
2. **Hu X et al. (2024)** *Nat Microbiol* — GprC 作为 ascaroside GPCR 感应 *C. elegans*，同一 Fischer 实验室，功能机制互补
3. **Kuo CJ et al. (2024)** — *A. oligospora* Gpr2/Gpr3 ascaroside 受体（本项目核心对象，与 GprC 的跨物种比较背景）
4. **Wernet N et al. (文内引用 ref ~12)** — CyrA 作为胞外基质蛋白标记（捕陷器捕获阶段）
5. **Bhatt S et al. / GS2478 背景文献（文内引用）** — coelomocyte 缺陷株 GS2478 的使用背景
6. **WormCat 工具（文内引用 ref ~16）** — *C. elegans* 转录组 GO 分析平台，用于 DEG 功能分类
7. **String-DB 文献（文内引用）** — 蛋白互作网络构建，用于揭示 NipA 调控基因集中的核心节点（IRG-4 等）
