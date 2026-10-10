---
paper_id: Kuo2024
document_role: source-backed detailed evidence audit
source: Kuo et al. 2024 version of record, Extended Data, publisher Source Data, Supplementary Tables, and transparent peer-review file
as_of: 2026-08-11
allowed_use: interpret the Kuo2024 Gpr2/Gpr3 evidence, audit figure claims, and delimit docking reproducibility and direct-binding claims
update_trigger: correction to the version of record, newly released receptor-ligand binding data, or a new audit of the publisher files
---

# Kuo et al. (2024) 详细证据审读：Gpr2/Gpr3、ascr#3/#7 与证据边界

> **对应摘要**：[Kuo2024-Gpr2Gpr3-summary.md](summaries/Kuo2024-Gpr2Gpr3-summary.md)
>
> **论文**：Kuo, C.-Y. et al. *The nematode-trapping fungus Arthrobotrys oligospora detects prey pheromones via G protein-coupled receptors*. *Nature Microbiology* 9, 1738–1751 (2024).
>
> **DOI**：<https://doi.org/10.1038/s41564-024-01679-w>

## 1. 先给结论

这篇论文较有力地支持以下命题：

1. *A. oligospora* 的 Gpr2 和 Gpr3 **参与**合成单一 ascr#3、ascr#7 所诱导的捕陷器形成；
2. ascr#7 暴露后，Gpr2–GFP 和 Gpr3–GFP 出现与 GPCR 内吞相符的膜到液泡重定位；
3. 提高 GPR2 或 GPR3 表达量会增强 ascr#3/#7 诱导的捕陷器形成；
4. Gpr2/Gpr3 在异源酵母 co-IP 中与 *A. oligospora* Gpa2 互作，且两种受体缺失都会削弱线虫诱导后的 cAMP 增加；
5. AlphaFold + TM-align + SwissDock 给出了结构相似性和候选结合姿势。

但论文**没有证明**以下更强命题：

1. 没有生化或生物物理实验显示 ascr#3/#7 与 Gpr2/Gpr3 直接结合；
2. 没有测得实验性结合常数、动力学常数或实验自由能；论文中的 ΔG 是对接预测值；
3. 没有对 Y166、Y168 或 Gpr3 口袋残基进行突变验证；
4. 没有证明 ascr#3 会触发 Gpr2/Gpr3 内吞，因为 Fig. 2d 只做了 ascr#7；
5. 没有提供足以逐文件、逐姿势严格复现 docking 的完整输入和输出。

因此最稳妥的总括是：**遗传学、表型、定位和下游信号证据共同支持 Gpr2/Gpr3 是 ascaroside 响应所需的上游组成部分；“它们是直接结合 ascr#3/#7 的受体”仍是高度合理但未被直接结合实验闭合的模型。**

---

## 2. 本次使用的证据与边界

### 2.1 直接核查的官方材料

| 材料 | 本次用途 |
|---|---|
| [版本记录正文](https://doi.org/10.1038/s41564-024-01679-w) | 正文、Methods、主图和 Extended Data |
| [Supplementary Information](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM1_ESM.pdf) | Southern blot 和补充图 |
| [透明审稿文件](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM3_ESM.pdf) | 核对作者与审稿人对“内吞是否证明识别”和 docking 局限的原始讨论 |
| [Supplementary Tables 1–4](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM4_ESM.xlsx) | 基因位点、引物、菌株和质粒 |
| [Source Data Fig. 1](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM5_ESM.xlsx) | Fig. 1a、1b、1e 的原始数值 |
| [Source Data Fig. 2](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM6_ESM.xlsx) | Fig. 2b、2c 的基因型标签、重复值和 P 值 |
| [Source Data Fig. 3](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM7_ESM.xlsx) | Fig. 3a 过表达数据 |
| [Source Data Extended Data Fig. 2](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM12_ESM.xlsx) | GPR2/GPR3 的 TPM 时间序列 |

本文中的均值由官方 Source Data 所列生物学重复重新计算，保留两位小数。P 值沿用作者文件中的双尾非配对 Student's *t* 检验；这些 P 值未做多重比较校正。

### 2.2 证据强度用语

| 用语 | 本文中的含义 |
|---|---|
| 证明/直接证明 | 存在直接测量目标关系的实验，不仅是间接表型或计算预测 |
| 支持/提示 | 结果与该机制一致，但仍有其他解释 |
| 预测 | 仅来自 AlphaFold、TM-align 或 docking 等计算分析 |
| 未显示 | 论文及本次核查的官方附件没有对应数据；不等于现实中绝对不存在 |

---

## 3. 三个最容易混淆的定位问题

### 3.1 Fig. 2b 的双敲到底是哪一个？

高分辨率主图与官方 Source Data Fig. 2 完全一致。Fig. 2b 从左到右是：

`WT` → `gpr1` → `gpr2` → `gpr3` → `gpr2gpr3`

因此第五组是 **gpr2gpr3 双敲**，不是 gpr1gpr3。图中没有分隔符，倾斜的小字号容易误读。Fig. 2a 的最后一行同样标为 `gpr2gpr3`。

### 3.2 “Gpr2 与 Gpr3 预测结构相似、TM-score 约 0.7”写在哪里？

精确位置是主文第 1741 页、以 “To understand the molecular interaction...” 开头的段落：

- Gpr2 vs Gpr3：TM-score 约 0.7，指向 **Extended Data Fig. 5a**；
- Gpr2 vs *C. elegans* SRBC-66：TM-score 约 0.7，指向 **Fig. 3c**；
- Gpr3 vs SRBC-66：TM-score 约 0.7，指向 **Extended Data Fig. 5b**。

Extended Data Fig. 5 的图注本身只写了 `0.5 < TM-score < 1.00` 属于相似折叠区间；**“约 0.7”来自主文结果段，不是图中打印的精确数字。**

TM-score 约 0.7 支持全局折叠相似，但不能单独证明配体相同、口袋相同或结合方式相同。

### 3.3 Gpr3 docking 到底在哪？

- 主 Fig. 3b–d 的结构和 docking 主体是 **Gpr2 与 SRBC-66**；
- Gpr3 与 Gpr2/SRBC-66 的结构比较在 **Extended Data Fig. 5**；
- Gpr3–ascr#3/#7 docking 在 **Extended Data Fig. 6**；
- Gpr3 的 −7.05/−6.41 kcal mol⁻¹ 数值写在主文第 1741 页结果段，并由 Extended Data Fig. 6 展示姿势；
- Extended Data Fig. 6 **没有给出具名接触残基**，正文只说未预测到强氢键。

所以，不能把 Gpr3 docking 写成“Fig. 3d 展示了 Gpr3”，也不能把 Gpr3 数值和残基混进 Gpr2 的主图说明中。

---

## 4. 研究问题与总体设计

论文试图回答两个上游问题：

1. *A. oligospora* 通过哪些 GPCR 感知 ascaroside？
2. 它如何感知 ascaroside 以外的线虫信号？

作者组合了以下证据层：

1. **现象层**：活体线虫、`daf-22` 线虫和合成 ascaroside 的捕陷器诱导；
2. **候选发现层**：TWF154 基因组的 GPCR 注释与活体线虫暴露 RNA-seq；
3. **遗传层**：GPR/GIN 删除、GPR 过表达和显性活化 GPA2；
4. **细胞层**：GPCR–GFP 定位与内吞；
5. **通路层**：异源酵母 co-IP、cAMP 和 MAPK 磷酸化；
6. **计算层**：AlphaFold、TM-align 和 SwissDock。

这种组合能把候选受体和生理响应较强地关联起来，但只有计算层触及受体–配体的原子接触，且没有湿实验闭环。

---

## 5. Fig. 1：ascaroside 有贡献，但不是全部线虫信号

### 5.1 `daf-22` 实验的正确解释

`daf-22` 参与 ascaroside 侧链的过氧化物酶体 β-氧化；该突变体不能合成已知具有生物活性的 ascaroside。Fig. 1a 比较由 WT 或 `daf-22` *C. elegans* 诱导的真菌捕陷器数：

| 线虫 | n | 平均 traps cm⁻² | 与 WT 比 |
|---|---:|---:|---:|
| WT | 12 | 747.72 | 100% |
| `daf-22` | 5 | 566.93 | 75.82% |

P = 7.91 × 10⁻³。

正确表述是：`daf-22` 仍诱导约 WT 的 **76%** 捕陷器，即平均下降约 **24%**；不能写成“下降了 75%”。而且不能把该比例机械解释为“ascaroside 贡献恰好 24%”，因为捕陷器计数不是各信号线性相加的直接读数，`daf-22` 也可能改变其他代谢和行为。

### 5.2 单一 ascaroside 足以诱导，但远弱于活体线虫

Fig. 1b Source Data：

| 诱导条件 | n | 平均 traps cm⁻² |
|---|---:|---:|
| 活体 *C. elegans* | 10 | 531.22 |
| ascr#3 | 7 | 31.55 |
| ascr#7 | 7 | 23.40 |

所以 ascr#3/#7 单独处理是充分的诱导输入，但活体线虫还提供大量其他信号。后文 Gin 受体的结果与这一点相呼应。

### 5.3 候选受体来自哪里

- 基因组来源：*A. oligospora* 野生分离株 TWF154，GenBank `SOZJ00000000`；
- 作者先从自动注释的 159 个候选中，经 TMHMM 2.0、Phobius 和人工注释保留 83 个典型 7-TM 候选；
- 69 个归为 Pth11-like GPCR；
- 三个归为 carbon receptor family：
  - GPR1：`EYR41_004122`
  - GPR2：`EYR41_005010`
  - GPR3：`EYR41_007055`
- Gpr1 与酵母葡萄糖受体 Gpr1 的序列最相近；Gpr2/Gpr3 是另外两个旁系同源物。

“GPR”只是基因命名前缀；更准确的家族表述是 **carbon receptor family / yeast Gpr1-like GPCRs**，不应把所有名为 GPR 的受体统称为一个“受 ascr 调控的 GPR 家族”。

---

## 6. Fig. 1e 与 Extended Data Fig. 2：GPR2/GPR3 转录动力学

### 6.1 诱导物是活体线虫，不是纯 ascr

这些 RNA-seq 数据来自暴露于活体 *C. elegans* 的时间序列（GEO `GSE233568`）。因此它们证明的是**线虫暴露后的转录变化**，不能直接证明 GPR2/GPR3 的转录由 ascr#3/#7 调控。

Fig. 1e 显示的是 beta 值，作者说明其近似于 log₂ fold change。Extended Data Fig. 2b 和官方 Source Data 给出平均 TPM（n = 3）：

| 时间（hpe） | 0 | 2 | 4 | 10 | 24 | 48 |
|---|---:|---:|---:|---:|---:|---:|
| GPR2 TPM | 12.79 | 13.43 | 14.74 | 4.02 | 3.92 | 6.33 |
| GPR3 TPM | 10.95 | 121.37 | 58.78 | 106.11 | 118.43 | 76.97 |

对应 Fig. 1e 的 beta 值：

| 时间（hpe） | 2 | 4 | 10 | 24 | 48 |
|---|---:|---:|---:|---:|---:|
| GPR2 beta | 0.157 | 0.221 | −1.038 | −1.080 | −0.619 |
| GPR3 beta | 2.456 | 1.708 | 2.361 | 2.432 | 1.988 |

### 6.2 可以和不可以得出的结论

可以说：

- GPR2 在 2–4 h 维持约 13–15 TPM，10 h 后降至约 4 TPM；
- GPR3 在 2 h 强烈升高，此后虽波动，但 2–48 h 均明显高于 0 h；
- 两者在活体线虫暴露后的转录动力学明显不同；
- GPR3 的转录诱导更强、更持久。

不宜说：

- GPR2 在 10 h “消失”：4.02 TPM 不是零；
- GPR3 一直单调上升：它在 4 h 和 48 h 都回落；
- Gpr3 因而在功能上比 Gpr2 更重要：转录量不等于膜上功能受体量、信号贡献或必要性。

功能数据也没有给出简单的“Gpr3 更重要”排序：两个单敲都降低 ascr 响应；GPR3 过表达只在 ascr#3 条件下增幅更大；显性活化 GPA2 只在 `gpr2` 背景产生清晰遗传互作。

---

## 7. Fig. 2a–c：删除 GPR2/GPR3 后对 ascr 的响应下降

### 7.1 Fig. 2b 的完整定量

| 基因型 | ascr#3：n / 平均 traps cm⁻² | 与 WT 的 P 值 | ascr#7：n / 平均 traps cm⁻² | 与 WT 的 P 值 |
|---|---:|---:|---:|---:|
| WT | 12 / 33.78 | — | 12 / 43.87 | — |
| `gpr1` | 9 / 40.14 | 0.197 | 8 / 51.83 | 0.240 |
| `gpr2` | 9 / 24.00 | 0.0357 | 10 / 19.60 | 7.51 × 10⁻⁴ |
| `gpr3` | 11 / 22.48 | 0.0283 | 11 / 17.06 | 4.31 × 10⁻⁵ |
| `gpr2gpr3` | 15 / 19.19 | 未直接给出 | 15 / 14.83 | 未直接给出 |

双敲与单敲的直接比较：

- ascr#3：`gpr2` vs `gpr2gpr3`, P = 0.149；`gpr3` vs `gpr2gpr3`, P = 0.398；
- ascr#7：`gpr2` vs `gpr2gpr3`, P = 0.136；`gpr3` vs `gpr2gpr3`, P = 0.237。

因此：

1. GPR2 和 GPR3 单敲均使 ascr#3/#7 诱导的捕陷器数下降；
2. 双敲仍保留明显响应，并未降到零；
3. 双敲没有显著重于两个单敲；
4. 数据与两者处于同一功能单元、可能形成复合物以及存在其他 ascr 感知输入相容，但不能仅凭该表型区分这些机制。

作者称两者 “act non-redundantly”，并据残余响应推断还有其他受体。更保守的中文表述是：**Gpr2 和 Gpr3 都不可被另一个完全补偿，但现有遗传数据没有闭合其精确协作机制。**

### 7.2 活体线虫条件下并没有显示 gpr2gpr3 的显著缺陷

Fig. 2c Source Data：

| 基因型 | n | 平均 traps cm⁻² | 与 WT 的 P 值 |
|---|---:|---:|---:|
| WT | 11 | 570.18 | — |
| `gpr1` | 8 | 770.04 | 0.0189 |
| `gpr2` | 8 | 532.19 | 0.636 |
| `gpr3` | 8 | 539.17 | 0.695 |
| `gpr2gpr3` | 4 | 454.77 | 0.272 |

因此不能写“gpr2gpr3 对活体线虫显著减少，P = 0.01”。图中的约 0.01 对应 WT 与 `gpr1` 的比较，而且 `gpr1` 平均值是升高而不是降低。作者正文的准确说法是没有任何 gpr mutant 显示活体线虫诱导的捕陷器**减少缺陷**。

这也说明活体线虫输入远不止 ascr#3/#7。

### 7.3 遗传证据的两个限制

1. 论文没有展示 `gpr2GPR2` 或 `gpr3GPR3` 回补株；Supplementary Table 4 只列出删除株、过表达株、GFP 株和 GPA2Q208L 组合株。因而单敲表型缺少同位基因回补闭环。
2. 捕陷器计数是终点表型，可能受到受体表达、膜运输、下游通路或发育阈值等多层因素影响；它不是直接结合读数。

---

## 8. Fig. 2d：ascr#7 诱导的 GFP 重定位

### 8.1 实验做了什么

- 将 Gpr2 或 Gpr3 的 C 端与 GFP 融合；
- 结果段称其由各自 endogenous promoter 驱动，Methods 说明构建包含约 2 kb 上游区；
- 在 *A. oligospora* 中表达，而不是在酵母中观察定位；
- 用 FM4-64 标记膜系统，用 CellTracker Blue CMAC 标记液泡；
- 只加入 **1 mM ascr#7**，观察 0、2、10 h；
- 图像代表 3 次独立生物学重复，但没有给出内吞比例或荧光强度定量。

### 8.2 图像支持什么

- 0 h：GFP 信号低，主要与膜标记相符；
- 2 h：GFP 表达增强并出现液泡内信号；
- 10 h：捕陷器细胞中信号更强，受体继续呈内部化分布。

这与配体诱导 GPCR 内吞一致，是有价值的细胞生物学支持。

### 8.3 图像不能证明什么

- Fig. 2d **没有 ascr#3 处理**，不能据此说 ascr#3 触发了内吞；
- 没有直接结合测量；
- 没有受体缺失、非响应配体或关键口袋突变对照；
- GFP 总信号同时被诱导，代表性图像不能把“新合成受体增加”和“既有膜受体内吞”完全分离；
- 没有显示内吞对下游信号或捕陷器形成是否必需。

透明审稿文件中，审稿人明确指出：该图“与识别 ascr#3/#7 一致，但不是证明”。作者随后把旧标题 “Gpr2 and Gpr3 recognize ascr#3 and ascr#7” 改成较弱的 “The endocytosis of Gpr2 and Gpr3 is triggered by ascr#3 and ascr#7”。但最终 Fig. 2d 仍只显示 ascr#7，所以对 ascr#3 的内吞主张不能从该面板单独成立。

---

## 9. Fig. 3a：过表达增强 ascr 响应，但“Gpr3 更强”不是普遍结论

作者使用 *Aspergillus nidulans* 强组成型 `gpdA` 启动子驱动 GPR2 或 GPR3。Source Data Fig. 3：

| 条件 | n | 平均 traps cm⁻² | 相对 WT 倍数 | 与 WT 的 P 值 |
|---|---:|---:|---:|---:|
| WT + ascr#3 | 10 | 23.79 | 1.00 | — |
| P<sub>gpdA</sub>::GPR2 + ascr#3 | 11 | 39.10 | 1.64 | 0.0114 |
| P<sub>gpdA</sub>::GPR3 + ascr#3 | 10 | 51.53 | 2.17 | 1.43 × 10⁻⁴ |
| WT + ascr#7 | 7 | 20.01 | 1.00 | — |
| P<sub>gpdA</sub>::GPR2 + ascr#7 | 12 | 40.95 | 2.05 | 0.0117 |
| P<sub>gpdA</sub>::GPR3 + ascr#7 | 10 | 38.87 | 1.94 | 6.96 × 10⁻⁴ |

结论：

- 两个过表达株在两个配体条件下都显著增加捕陷器数；
- GPR3 的平均增幅在 ascr#3 条件下更大；
- ascr#7 条件下 GPR2 的均值和倍数略高；
- 论文没有给出 GPR2-OE 与 GPR3-OE 的直接统计比较，因此不能笼统宣称 “Gpr3 提升显著高于 Gpr2”。

过表达结果支持受体丰度影响响应，但仍不能排除过表达导致的信号阈值、膜稳态或非生理性效应。

---

## 10. Fig. 3b–d 与 Extended Data Fig. 5–6：结构和 docking

### 10.1 结构比较的准确来源

| 比较 | TM-score | 精确来源 |
|---|---:|---|
| Gpr2 vs Gpr3 | 约 0.7 | 主文 p.1741；Extended Data Fig. 5a |
| Gpr2 vs SRBC-66 | 约 0.7 | 主文 p.1741；Fig. 3c |
| Gpr3 vs SRBC-66 | 约 0.7 | 主文 p.1741；Extended Data Fig. 5b |

这些都是 AlphaFold 预测结构之间的 TM-align 比较，不是实验结构比较。

Fig. 3c 图注称 Gpr2 的 217–316 区域因预测为 random coil 而从**结构展示**中省略；Extended Data Fig. 6 称 Gpr3 的 212–264 区域同样从展示中省略。图注没有说明这些区域是否也从 docking 输入坐标中删除，不能把“展示省略”直接写成“对接模型删去了该区域”。

### 10.2 docking 数值与残基必须分图写

| 受体–配体 | 预测 ΔG（kcal mol⁻¹） | 图/文字位置 | 图中具名残基 | 证据边界 |
|---|---:|---|---|---|
| Gpr2–ascr#3 | −6.99 | 主文 p.1741；Fig. 3d | **Y166、Y168** | Fig. 3d 两者均有标签；正文只点名 Y168 |
| Gpr2–ascr#7 | −7.07 | 主文 p.1741；Fig. 3d | **Y168** | 仅为预测 |
| SRBC-66–ascr#3 | −7.47 | 主文 p.1741；Fig. 3d | **N161** | N161 属于 SRBC-66，不属于 Gpr2 |
| Gpr3–ascr#3 | −7.05 | 主文 p.1741；Extended Data Fig. 6a | 未列出 | 正文称未预测到强氢键 |
| Gpr3–ascr#7 | −6.41 | 主文 p.1741；Extended Data Fig. 6b | 未列出 | 正文称未预测到强氢键 |

必须区分：

1. **Y166 的确出现在 Fig. 3d 的 Gpr2–ascr#3 放大图中**；
2. 正文句子只写 “the receptor residues responsible for binding ascr#3 are Y168 and N161 in Gpr2 and SRBC-66, respectively”；
3. 因而“正文只确认 Y168”也不够严谨，因为这里的 “responsible” 仍只是 computational analysis；更准确的说法是“正文只点名 Y168，而图还标了 Y166”；
4. Gpr3 图没有具名接触残基，不能为它补写 Y168 或其他残基。

### 10.3 这些分值不能当作实验亲和力

- 它们是 SwissDock 输出所解释的预测 ΔG，不是通过 ITC、SPR、MST、放射性配体或竞争结合实验得到的实验自由能；
- 分值接近只说明在该模型、该输入和该评分体系下处于相近数量级；
- 不能由 −7.05 vs −6.99 推断 Gpr3 对 ascr#3 在生物学上必然比 Gpr2 更强；
- 未提供不响应配体、诱饵受体或已知阴性组合的最终论文对照。

透明审稿回复中作者曾报告 Gpr2–glucose 预测 ΔG = −6.26，并以此与 ascaroside 比较；该结果没有进入版本记录正文、图或 Source Data，应标为**审稿回复中的补充计算**，不能冒充最终论文正式结果。

---

## 11. Docking 可复现性审核：缺了什么

### 11.1 论文实际报告了什么

Methods 的 “The prediction of ascaroside–GPCR docking site and the protein structure alignment” 明确给出：

1. 工具：SwissDock web service；
2. 受体：由 AlphaFold 预测；
3. 配体结构文件：ascr#3/#7 来自 ChemSpider；
4. 参数：使用 default parameters；
5. 搜索范围：考虑整个 target protein，即全蛋白搜索，可理解为 blind docking；
6. 结构比较：TM-align，TM-score > 0.5 解释为相似折叠。

因此“完全没有 docking 参数”不准确。作者至少给了工具、默认设置和全蛋白搜索范围。

### 11.2 严格复现仍缺少的材料

| 类别 | 未报告/未公开的内容 | 对复现的影响 |
|---|---|---|
| 受体身份 | docking 实际使用的 Gpr2/Gpr3/SRBC-66 坐标文件、文件校验值和模型编号 | 不能确认复跑使用同一坐标 |
| AlphaFold 过程 | AlphaFold 版本、数据库日期、模型类型、模板设置、seed、候选选择、pLDDT/PAE | 不能重建同一预测模型，也无法审计口袋置信度 |
| 受体预处理 | 质子化状态、氢原子、端基、缺失区、侧链修复、电荷、是否最小化 | 会改变姿势和打分 |
| 配体身份 | ChemSpider record ID、原始 MOL/SDF、立体化学、质子化/电荷、构象生成和最小化 | 不能保证配体化学身份与三维构象一致 |
| SwissDock 运行身份 | 服务版本/后端版本、运行日期或 job ID、实际参数回执 | “默认参数”会随服务版本变化，不能确认算法环境 |
| 输出 | 全部 cluster/pose、每个 pose 的分值、坐标文件和服务器结果页 | 不能核对最佳姿势或重新分析相互作用 |
| 选择规则 | 为什么选择展示姿势、cluster/pose 排名规则、是否人工筛选 | 不能排除选择性展示 |
| 相互作用表 | 完整接触残基、距离、氢键/疏水/范德华判据 | 只能看到少量图示标签，不能重建口袋网络 |
| 稳健性 | 多模型、多质子化态、多参数或独立软件的敏感性分析 | 无法判断预测是否对输入和设置稳健 |
| 实验验证 | 直接结合、竞争、剂量反应、口袋突变及表达/定位控制 | 无法把计算姿势升级为已验证机制 |

### 11.3 最合适的可复现性判定

- **可以做近似重跑**：从基因位点重建序列，自行生成 AlphaFold 模型和 ChemSpider 配体，使用当前 SwissDock 默认全蛋白搜索；
- **不能做严格复现**：无法保证获得论文所用的相同输入、相同服务器版本、相同 pose 和相同残基接触；
- 因而“该预测结果不可靠”过强，应该写成：**预测未经实验验证、对输入与参数的稳健性未报告、严格可复现性不足，所以其证据权重较低，适合生成假设，不适合单独证明直接结合或关键残基。**

---

## 12. 配体和受体分别来自哪里、怎么处理

这里必须分开湿实验、成像、异源 co-IP 和计算 docking 四个场景。

### 12.1 配体

| 场景 | 来源 | 处理方式 | 未报告信息 |
|---|---|---|---|
| 捕陷器表型 | ascr#3/#7 按 Zhang et al., *Org. Lett.* 2017 的方法化学合成 | 真菌先在 5 cm LNM 平板 25 °C 培养 3 d；在菌丝尖端边界约 2 mm 处加入 5 μl、1 mM 单一 ascr；2 d 后计数全板捕陷器 | 本文未给出批次、纯度、NMR/HPLC 质控、溶剂和储存细节 |
| GFP 定位 | 同一研究中的 ascr#7 | *A. oligospora* GPCR–GFP 株在 LNM 上生长 3 d；加入 1 mM ascr#7，观察 0/2/10 h | 该段未给出加入体积；没有 ascr#3 成像 |
| docking | ChemSpider 的 ascr#3/#7 chemical structure files | 上传至 SwissDock，默认参数、全蛋白搜索 | 未给 ChemSpider ID、原始文件、立体化学/质子化/构象预处理 |

“纯 ascr#3/#7”最好改成“**化学合成的单一 ascr#3 或 ascr#7 处理**”，因为论文未在 Methods 中给出分析纯度。

### 12.2 受体

| 场景 | 受体来源 | 构建/处理 |
|---|---|---|
| 基因发现 | *A. oligospora* TWF154 基因组 | GPR2 = `EYR41_005010`；GPR3 = `EYR41_007055` |
| 基因删除 | TWF154 的 NHEJ-deficient `ku70` 衍生背景 TWF1697 | 5′/3′ 各约 1.5 kb 同源臂夹抗性盒；PEG 介导真菌原生质体转化；PCR + Southern blot 验证 |
| 过表达 | *A. oligospora* GPR2/GPR3 | 每个 GPCR 连同约 1 kb 下游区克隆至 pUMa1057；由 *A. nidulans gpdA* 强组成型启动子驱动 |
| GFP 定位 | *A. oligospora* GPR2/GPR3 | GPCR 加约 2 kb 上游区，与 GFP 构建并转入 WT 真菌；结果段称由 endogenous promoter 表达 |
| co-IP | *A. oligospora* Gpr2/Gpr3 与 Gpa1/2/3 cDNA | 受体加 3×HA，Gα 加 Myc；pPGK/PGK 启动子；在 *S. cerevisiae* YDX4 中异源表达；抗 HA pull-down 后抗 Myc 检测 |
| 受体二聚 co-IP | *A. oligospora* Gpr2/Gpr3 cDNA | Gpr2–3×HA 与 Gpr3–Myc 在 YDX4 中异源表达 |
| docking | Gpr2、Gpr3，以及 *C. elegans* SRBC-66 | AlphaFold 预测结构；没有实验解析结构或公开的实际 docking PDB 输入 |

注意：

- 真菌基因删除使用的是 **PEG 介导的原生质体转化**；电穿孔用于 *S. cerevisiae* 转化，不能把两者混写；
- 酵母 co-IP 证明的是异源宿主中的蛋白共沉淀，不等于在原生真菌中、配体依赖条件下的相互作用；
- AlphaFold 模型、真菌 GFP 蛋白和酵母 co-IP 构建不是同一种“受体处理”。

---

## 13. Fig. 4：Gpa2/cAMP 证据链的强项和边界

### 13.1 co-IP

作者在 *S. cerevisiae* YDX4 中异源表达：

- Gpr2–3×HA 或 Gpr3–3×HA；
- *A. oligospora* Gpa1–Myc、Gpa2–Myc、Gpa3–Myc；
- 以及 Gpr2–3×HA + Gpr3–Myc。

结果显示 Gpr2/Gpr3 与 Gpa2 共沉淀，而与 Gpa1/Gpa3 不显示同等互作；Gpr2 与 Gpr3 也共沉淀。它支持受体–Gα 选择性和异源二聚模型，但没有：

- 在原生真菌中做相同 co-IP；
- 比较加/不加 ascr 后互作变化；
- 证明直接蛋白–蛋白接触，而不是复合物中的间接共沉淀；
- 定量比较 Gpr2–Gpa2 与 Gpr3–Gpa2 的亲和力。

所以不能根据条带目测写“Gpr3 与 Gpa2 互作更弱”。

### 13.2 cAMP 与遗传互作

- Fig. 4b：活体线虫诱导后 WT 细胞内 cAMP 约增加 2 倍，`gpr2` 和 `gpr3` 均没有出现 WT 式增加；
- Fig. 4c,d：显性活化 GPA2Q208L 在 `gpr2` 背景下提高 ascr#3/#7 诱导的捕陷器数，在 `gpr3` 背景下没有显著效果。

这支持 Gpr2/Gpr3 与 Gpa2–cAMP 轴相关，但要注意：

- cAMP 测量使用活体线虫诱导，不是纯 ascr#3/#7；
- 论文没有直接测量 PKA 酶活；
- `gpr3/GPA2Q208L` 未获救不能简单解释为 “Gpr3 不重要” 或 “Gpr3–Gpa2 互作弱”，也可能提示 Gpr3 还承担复合体、定位或 Gpa2 上游之外的作用。

---

## 14. Gin 受体为何影响对 Gpr2/Gpr3 的解释

论文的第二条主线显示 Pth11-like Gin 受体参与 ascaroside-independent 的线虫感知，尤其 `gin3` 对活体线虫诱导的捕陷器形成影响很大。这解释了：

- 单一 ascr 诱导远弱于活体线虫；
- `gpr2`、`gpr3` 乃至 `gpr2gpr3` 在活体线虫条件下都没有显著降低；
- Gpr2/Gpr3 不能被表述为线虫感知的唯一受体。

MAPK 结果也应准确表述：

- Fus3：pheromone-response MAPK；
- Hog1：high-osmolarity glycerol MAPK；
- Slt2：cell-wall-integrity MAPK；
- phospho-p44/42 抗体检测 Fus3/Slt2，phospho-p38 抗体检测 Hog1；
- 结果更接近 Gpr2/Gpr3/Gin3 可能调节 Hog1 磷酸化动力学，而不是证明它们直接激活 Fus3 或 Slt2。

---

## 15. 对用户三段描述的逐项审核

### 15.1 “首次提出 + 三方面证据 + docking 缺口”

#### “确实是首次提出 gpr（碳源受体家族）可以受 ascr 调控”

**需要改写。**

- 2013 年 Hsueh et al. 已证明 *A. oligospora* 能感知 ascaroside，但没有鉴定具体受体；
- Kuo2024 的贡献是把具体的 carbon-receptor-family GPCR Gpr2/Gpr3 与 ascr#3/#7 响应联系起来；
- 论文摘要称此前 upstream receptors remained unknown，并把本研究描述为在非线虫物种中鉴定 ascaroside receptors；
- 但“绝对首次”是跨文献优先权判断，若未做系统检索，最好写成“**该研究首次在这一真菌体系中将具体的 Gpr2/Gpr3 遗传学地关联到 ascr#3/#7 响应；作者将其表述为对非线虫物种 ascaroside receptors 的鉴定**”；
- “受 ascr 调控”还会混淆转录调控和受体功能。RNA-seq 是活体线虫诱导；更准确是“参与 ascr 响应”。

#### 三方面证据

1. **Fig. 2b 单敲响应下降：正确。** `gpr2`、`gpr3` 对两种单一合成 ascr 的捕陷器计数均显著下降；双敲不归零且不显著重于单敲。
2. **Fig. 2d 内吞：基本正确。** 只展示 ascr#7；与 GPCR 内吞一致，但没有直接结合证明，且只有代表性图像、无内吞定量。透明审稿意见也明确指出“consistent, but not proof”。
3. **Fig. 3a 过表达增强：正确但需限定。** 两个受体对两种配体都增强；GPR3 只在 ascr#3 条件下增幅更大，ascr#7 下 GPR2 略高。

#### “缺少物理结合证据”

**正确。** 删除、过表达、GFP 内吞、cAMP、Gpa2 co-IP 和 docking 都不是直接受体–配体结合实验。

#### “图中只展示少量残基，且无湿实验验证”

**正确。** Gpr2–ascr#3 图标 Y166/Y168，Gpr2–ascr#7 标 Y168；Gpr3 图不列残基；没有完整接触表和残基突变验证。

#### “预测结果不可靠”

**结论过强。** 现有证据足以把 docking 当作候选口袋假设，但不足以把姿势或残基当成已验证机制。应写“未验证、稳健性未知、证据权重低”。

#### “缺少 docking 参数，无法复现”

**部分正确。** 论文报告了 SwissDock、默认参数、全蛋白搜索、AlphaFold 和 ChemSpider；所以不是零参数。缺少的是精确输入、版本、预处理、完整输出和姿势选择规则，导致**无法严格复现，只能近似重跑**。

### 15.2 “GPR2 10 h 接近消失，GPR3 持续激活；不能得出 Gpr3 更重要”

结论方向基本正确，但措辞需改：

- GPR2 10 h 为 4.02 TPM，不是消失；相比 4 h 的 14.74 TPM 明显下降；
- GPR3 在 2–48 h 持续高于 0 h，但并非单调上升；
- 这些是活体线虫暴露后的 RNA-seq，不是纯 ascr 诱导，也不是蛋白量或信号输出；
- 因此不能据此判断 Gpr3 功能上更重要。

### 15.3 “他们用的配体、受体分别来自哪里，怎么处理”

简答：

- 湿实验配体：按 Zhang et al. 2017 化学合成的 ascr#3/#7；表型实验每板局部加入 5 μl 1 mM，2 d 后计数；GFP 只用 1 mM ascr#7；
- docking 配体：ChemSpider 化学结构文件，具体 record ID 和预处理未给；
- 受体基因：*A. oligospora* TWF154 的 GPR2/GPR3；
- 删除：在 `ku70`/TWF1697 背景以 PEG 原生质体转化构建；
- GFP：在真菌中由内源上游区驱动；
- 过表达：*A. nidulans gpdA* 启动子；
- co-IP：受体和 Gα 由 yeast PGK promoter 在 *S. cerevisiae* YDX4 异源表达；
- docking：受体为 AlphaFold 预测结构，不是实验结构。

---

## 16. 建议采用的准确表述

> Kuo et al. (2024) 在 *A. oligospora* 中将 carbon-receptor-family GPCR Gpr2 和 Gpr3 与 ascr#3/#7 响应联系起来。证据包括：`gpr2` 或 `gpr3` 删除均降低单一合成 ascr#3/#7 诱导的捕陷器数；1 mM ascr#7 暴露后 Gpr2–GFP/Gpr3–GFP 出现与膜到液泡内吞一致的重定位；由 *A. nidulans gpdA* 启动子驱动的 GPR2/GPR3 过表达均增强两种 ascr 的捕陷器诱导。GPR3 过表达的增幅只在 ascr#3 条件下高于 GPR2，在 ascr#7 条件下 GPR2 略高。上述结果支持 Gpr2/Gpr3 参与 ascaroside 感知，但不构成直接配体结合证明。
>
> 结构部分使用 AlphaFold、TM-align 与 SwissDock。主 Fig. 3d 只展示 Gpr2 和线虫 SRBC-66；Gpr3 的结构比较和 docking 分别位于 Extended Data Fig. 5、6。Gpr2–ascr#3 图标出 Y166/Y168，Gpr2–ascr#7 标出 Y168；Gpr3 图未列具名接触残基，且所有残基都缺少突变验证。Methods 报告了 SwissDock 默认参数和全蛋白搜索，但未公开实际受体/配体输入文件、版本与预处理、完整 pose/cluster 输出和姿势选择规则，因此只能近似重跑，不能严格复现论文姿势。这些 docking 结果适合作为候选口袋假设，不应被表述为可靠的直接结合证据。
>
> 活体线虫暴露 RNA-seq 显示 GPR2 在 10 h 从 4 h 的 14.74 TPM 降至 4.02 TPM，而 GPR3 在 2–48 h 持续高于基线；这支持两者转录动力学不同，但不能据此判断 Gpr3 在功能上更重要。

---

## 17. 最终证据分级

| 命题 | 判定 | 依据 |
|---|---|---|
| Gpr2/Gpr3 参与 ascr#3/#7 捕陷器响应 | 较强支持 | 单敲下降 + 过表达增强 |
| Gpr2/Gpr3 是唯一 ascr#3/#7 受体 | 不支持 | 双敲仍响应；作者也推断存在其他受体 |
| ascr#7 触发 Gpr2/Gpr3 内吞 | 支持但未定量 | Fig. 2d GFP/FM4-64/CMAC |
| ascr#3 触发 Gpr2/Gpr3 内吞 | 未显示 | Fig. 2d 无 ascr#3 |
| Gpr2/Gpr3 与 Gpa2 处于同一信号轴 | 中等至较强支持 | 异源 co-IP、cAMP、GPA2Q208L 遗传互作 |
| Gpr2/Gpr3 在原生真菌中形成异源二聚体 | 未直接证明 | 只在异源酵母 co-IP 中共沉淀 |
| Gpr2/Gpr3 直接结合 ascr#3/#7 | 未直接证明 | 无实验结合测量；只有间接证据和 docking |
| Y166/Y168 是真实关键结合残基 | 未验证 | 只有 Gpr2 docking 图示，无突变实验 |
| Gpr3 的接触残基已确定 | 不支持 | Extended Data Fig. 6 未列残基 |
| Gpr3 功能上比 Gpr2 更重要 | 不支持 | RNA、删除、过表达和遗传互作不能形成一致排序 |
| 论文 docking 可严格复现 | 不支持 | 缺精确输入、版本、完整输出和选择规则 |

## 18. 参考文献

1. Kuo, C.-Y. et al. *Nature Microbiology* 9, 1738–1751 (2024). <https://doi.org/10.1038/s41564-024-01679-w>
2. Hsueh, Y.-P., Mahanti, P., Schroeder, F. C. & Sternberg, P. W. *Current Biology* 23, 83–86 (2013). <https://doi.org/10.1016/j.cub.2012.11.035>
3. Zhang, Y. K., Sanchez-Ayala, M. A., Sternberg, P. W., Srinivasan, J. & Schroeder, F. C. *Organic Letters* 19, 2837–2840 (2017). <https://doi.org/10.1021/acs.orglett.7b01048>
