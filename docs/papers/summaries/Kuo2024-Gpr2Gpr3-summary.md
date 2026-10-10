---
paper_id: Kuo2024
document_role: corrected concise summary
source: Kuo et al. 2024 version of record and the linked detailed evidence audit
as_of: 2026-08-11
allowed_use: quick orientation; use the detailed evidence audit for exact values, source locations, and evidence boundaries
update_trigger: correction to the version of record or update of the detailed evidence audit
---

# Kuo et al. (2024) — Gpr2/Gpr3 校正版摘要

> **按需查看详细证据**：[Kuo2024-Gpr2Gpr3-detailed-evidence.md](../Kuo2024-Gpr2Gpr3-detailed-evidence.md)
>
> 详细稿逐项列出正文、Methods、主图、Extended Data、官方 Source Data、Supplementary Tables 和透明审稿文件的证据位置、原始均值及推论边界。本页只保留经过校正的主线结论。

**论文**：Kuo, C.-Y. et al. *The nematode-trapping fungus Arthrobotrys oligospora detects prey pheromones via G protein-coupled receptors*. *Nature Microbiology* 9, 1738–1751 (2024).

**DOI**：<https://doi.org/10.1038/s41564-024-01679-w>

**研究菌株**：*Arthrobotrys oligospora* TWF154

---

## 一句话结论

遗传表型、过表达、受体定位和下游信号结果共同支持：*A. oligospora* 的 yeast-Gpr1-like / carbon-receptor-family GPCR **Gpr2 和 Gpr3 参与 ascr#3/#7 响应**。但论文没有直接测量受体–配体结合，AlphaFold + SwissDock 结果也未经口袋突变或生化实验验证，因此“Gpr2/Gpr3 直接结合 ascr#3/#7”仍是合理模型，而不是已经闭合的机制事实。

---

## 1. Ascaroside 只是活体线虫信号的一部分

- `daf-22` 线虫不能合成已知有生物活性的 ascaroside，但仍能诱导约 WT **75.82%** 的捕陷器；即均值下降约 **24%**，不是“下降 75%”。
- 单一合成 ascr#3 或 ascr#7 足以诱导捕陷器，但诱导量远低于活体线虫。
- 因此不能把 Gpr2/Gpr3 表述为真菌感知活体线虫的唯一受体；论文后半部分的 Pth11-like Gin 受体提供了另一组上游输入。

---

## 2. GPR2/GPR3 的来源及转录变化

作者从 TWF154 基因组中鉴定出 83 个典型 7-TM GPCR 候选，其中 3 个归入 carbon receptor family：

| 基因 | TWF154 位点 |
|---|---|
| GPR1 | `EYR41_004122` |
| GPR2 | `EYR41_005010` |
| GPR3 | `EYR41_007055` |

Gpr1 与酵母葡萄糖受体 Gpr1 的序列最相近；Gpr2/Gpr3 是另外两个旁系同源物。“GPR”是基因命名前缀，最好不要把所有 GPR 泛称为一个“受 ascr 调控的家族”。

RNA-seq 的诱导条件是**活体 *C. elegans***，不是纯 ascr#3/#7。官方 Source Data 中的平均 TPM 为：

| hpe | 0 | 2 | 4 | 10 | 24 | 48 |
|---:|---:|---:|---:|---:|---:|---:|
| GPR2 | 12.79 | 13.43 | 14.74 | 4.02 | 3.92 | 6.33 |
| GPR3 | 10.95 | 121.37 | 58.78 | 106.11 | 118.43 | 76.97 |

准确解释是：GPR2 在 10 h 明显下降，但 4.02 TPM 不是“消失”；GPR3 在 2–48 h 持续高于基线，但并非单调上升。该结果说明两者的**转录动力学不同**，不能单独推出 Gpr3 的蛋白水平、信号贡献或功能重要性高于 Gpr2。

---

## 3. 删除突变：Fig. 2b–c

### Fig. 2b 的基因型和表型

Fig. 2b 从左到右为 `WT`、`gpr1`、`gpr2`、`gpr3`、`gpr2gpr3`。第五组确实是 **gpr2gpr3 双敲**。

官方 Source Data 的均值（traps cm⁻²）：

| 基因型 | ascr#3 | ascr#7 |
|---|---:|---:|
| WT | 33.78 | 43.87 |
| `gpr1` | 40.14 | 51.83 |
| `gpr2` | 24.00 | 19.60 |
| `gpr3` | 22.48 | 17.06 |
| `gpr2gpr3` | 19.19 | 14.83 |

- `gpr2` 和 `gpr3` 单敲对 ascr#3/#7 的响应均显著下降。
- 双敲仍有响应，且相较两个单敲均未显著进一步降低。
- 这支持 Gpr2/Gpr3 均参与该响应，但不能仅凭这些数据判定二者的精确协作机制。
- 论文没有展示 GPR2/GPR3 的同位基因回补株，因此删除表型缺少回补闭环。

### Fig. 2c 的活体线虫结果

`gpr2gpr3` 在活体线虫条件下均值为 454.77，WT 为 570.18，WT vs `gpr2gpr3` 的 P = 0.272，**不显著**。图中约 0.01 的 P 值对应 WT vs `gpr1`，且 `gpr1` 的均值是升高。

所以旧表述“gpr2gpr3 对活体线虫显著减少（P = 0.01）”错误，应删除。

---

## 4. GFP 重定位：Fig. 2d

- Gpr2–GFP、Gpr3–GFP 在 *A. oligospora* 中由包含各自内源上游区的构建表达。
- Fig. 2d 只展示 **1 mM ascr#7** 处理后的 0、2、10 h；没有展示 ascr#3。
- ascr#7 后信号增强，并出现与“由膜向液泡内化”相符的分布变化。
- 图像来自 3 次独立重复，但论文没有提供内吞比例或荧光强度定量。

因此可说“ascr#7 触发了与 Gpr2/Gpr3 内吞相符的重定位”，不能说“Fig. 2d 证明 ascr#3/#7 都触发内吞”，更不能把内吞当作直接结合证明。透明审稿中审稿人也明确指出该结果与配体识别一致，但不是证明。

---

## 5. 过表达：Fig. 3a

作者用 *Aspergillus nidulans gpdA* 强组成型启动子驱动 GPR2 或 GPR3。官方 Source Data：

| 条件 | WT | GPR2-OE | GPR3-OE |
|---|---:|---:|---:|
| ascr#3，traps cm⁻² | 23.79 | 39.10（1.64×） | 51.53（2.17×） |
| ascr#7，traps cm⁻² | 20.01 | 40.95（2.05×） | 38.87（1.94×） |

两种过表达株在两个配体条件下都显著高于各自 WT。GPR3 的增幅只在 ascr#3 下更大；ascr#7 下 GPR2 的均值和倍数反而略高。论文也没有做 GPR2-OE vs GPR3-OE 的直接统计比较，不能笼统说“Gpr3 的提升更大”。

---

## 6. 结构比较和 docking：Fig. 3、Extended Data Fig. 5–6

### 图和结论要分开定位

| 内容 | 位置 |
|---|---|
| Gpr2 vs Gpr3 预测结构比较 | 主文 p.1741；Extended Data Fig. 5a |
| Gpr2 vs SRBC-66 预测结构比较 | 主文 p.1741；Fig. 3c |
| Gpr3 vs SRBC-66 预测结构比较 | 主文 p.1741；Extended Data Fig. 5b |
| Gpr2–ascr#3/#7 docking | Fig. 3d |
| Gpr3–ascr#3/#7 docking | Extended Data Fig. 6 |

主文 p.1741 写明上述三组结构比较的 TM-score 都约为 0.7；Extended Data Fig. 5 图注自身只给出 `0.5 < TM-score < 1.00` 的相似折叠解释。它们比较的是 **AlphaFold 预测结构**，不是实验解析结构。

### 预测分值和图示残基

| 受体–配体 | 预测 ΔG（kcal mol⁻¹） | 图中具名残基 |
|---|---:|---|
| Gpr2–ascr#3 | −6.99 | Y166、Y168；正文只点名 Y168 |
| Gpr2–ascr#7 | −7.07 | Y168 |
| SRBC-66–ascr#3 | −7.47 | N161 |
| Gpr3–ascr#3 | −7.05 | 未列出 |
| Gpr3–ascr#7 | −6.41 | 未列出 |

Gpr3 docking 并不在主 Fig. 3d，而在 Extended Data Fig. 6；该图没有列出 Gpr3 的具名接触残基，正文称其未预测到强氢键。Y166/Y168 只属于 Gpr2–ascr 图示，N161 属于线虫受体 SRBC-66。

这些 ΔG 是 SwissDock 预测分值，不是实验测得的结合自由能；分值相近也不能用于给 Gpr2/Gpr3 的生物学重要性排序。Y166/Y168 均未做定点突变、表达/定位控制或结合验证，必须称为“预测/图示残基”，不能称为“确认的关键结合残基”。

### 方法报告到什么程度

论文 Methods 报告了：

- 受体使用 AlphaFold 预测；
- ascr#3/#7 化学结构文件来自 ChemSpider；
- 使用 SwissDock web service；
- 使用 default parameters；
- 搜索整个 target protein；
- 用 TM-align 做结构比对。

因此“完全没有 docking 参数”不准确。但严格复现仍缺少：实际输入坐标和校验值、AlphaFold/SwissDock 版本或运行身份、受体与配体的质子化/电荷/构象等预处理、ChemSpider record ID、全部 pose/cluster 输出、展示姿势的选择规则、完整接触残基与距离表，以及对不同模型和设置的稳健性分析。

最合适的结论是：**现有信息允许近似重跑，但不足以严格复现论文所用输入、姿势和残基网络；docking 未经实验验证、稳健性未知、证据权重低，适合生成候选口袋假设，不足以证明直接结合。**

---

## 7. 配体与受体分别来自哪里、如何处理

### 配体

| 场景 | 来源与处理 |
|---|---|
| 捕陷器表型 | ascr#3/#7 按 Zhang et al. 2017 化学合成；每板在菌丝尖端边界约 2 mm 处加入 5 μl、1 mM 单一 ascr，2 d 后计数 |
| GFP 定位 | 使用 1 mM ascr#7；观察 0、2、10 h；未做 ascr#3 成像 |
| docking | 使用 ChemSpider 的 ascr#3/#7 chemical structure files；具体记录号、原始文件和预处理未报告 |

论文 Methods 没有给出合成批次、分析纯度、NMR/HPLC 质控、溶剂和储存细节，所以宜写“化学合成的单一 ascr”，不宜自行补成“高纯度配体”。

### 受体

| 场景 | 来源与处理 |
|---|---|
| 基因来源 | TWF154 的 GPR2（`EYR41_005010`）和 GPR3（`EYR41_007055`） |
| 删除株 | 在 NHEJ-deficient `ku70` 衍生背景 TWF1697 中，以抗性盒替换目标基因；PEG 介导真菌原生质体转化；PCR + Southern blot 验证 |
| 过表达 | *A. nidulans gpdA* 强组成型启动子驱动 |
| GFP | 在真菌中使用包含约 2 kb 内源上游区的 GPCR–GFP 构建 |
| co-IP | *A. oligospora* 受体/Gα cDNA 在 *S. cerevisiae* YDX4 中由 PGK 启动子异源表达 |
| docking | Gpr2/Gpr3/SRBC-66 的 AlphaFold 预测模型；没有实验结构，也未公开实际 docking 坐标文件 |

真菌基因删除使用的是 **PEG 原生质体转化**；电穿孔用于酵母转化。二者不能混写。

---

## 8. Gpa2、cAMP 与受体二聚证据

- 在异源 *S. cerevisiae* 中，Gpr2/Gpr3 与 Gpa2 共沉淀；Gpr2 与 Gpr3 也共沉淀。
- 这支持受体–Gα 选择性和异源二聚模型，但不证明原生真菌中的直接蛋白接触，也未测试互作是否依赖 ascr。
- 不能凭条带目测断言“Gpr3–Gpa2 更弱”。
- 活体线虫诱导后，WT cAMP 增加，而 `gpr2`、`gpr3` 未出现 WT 式增加；这里的刺激仍是活体线虫，不是纯 ascr。
- 显性活化 GPA2Q208L 只在 `gpr2` 背景产生清晰救援式遗传互作；`gpr3` 背景未显著提高不能简单归因为“Gpr3 与 Gpa2 互作较弱”。

---

## 9. Gin 与 MAPK 主线的必要限定

- Pth11-like Gin 受体参与 ascaroside 以外的活体线虫信号；这与 `gpr2gpr3` 对活体线虫没有显著减少相吻合。
- phospho-p44/42 抗体用于检测 Fus3/Slt2；phospho-p38 抗体用于检测 Hog1。
- Fus3 是 pheromone-response MAPK，Hog1 是 high-osmolarity-glycerol MAPK，Slt2 是 cell-wall-integrity MAPK。旧摘要中 Fus3、Hog1 与抗体的对应关系写反。
- 现有结果更适合表述为 Gpr2/Gpr3/Gin3 可能调节 Hog1 磷酸化动力学，而不是已经证明这些受体直接激活某一 MAPK。

---

## 10. 对“首次提出”的准确说法

Hsueh et al. 2013 已证明 *A. oligospora* 能响应 nematode ascarosides，但没有鉴定上游受体。Kuo2024 的新增贡献是把具体的 carbon-receptor-family GPCR Gpr2/Gpr3 与 ascr#3/#7 响应联系起来，并由作者表述为在非线虫物种中鉴定 ascaroside receptors。

若未另外完成系统优先权检索，建议写：

> Kuo et al. (2024) 首次在这一真菌体系中将具体的 carbon-receptor-family GPCR Gpr2/Gpr3 遗传学地关联到 ascr#3/#7 响应。

不建议写“首次发现 GPR 可以受 ascr 调控”：这会混淆家族范围、受体响应与转录调控，而且绝对的跨物种优先权需要系统检索支持。

---

## 11. 证据分级

| 命题 | 判定 |
|---|---|
| Gpr2/Gpr3 参与 ascr#3/#7 诱导捕陷器形成 | 较强支持：单敲降低 + 过表达增强 |
| ascr#7 触发 Gpr2/Gpr3 内吞 | 支持但未定量 |
| ascr#3 触发 Gpr2/Gpr3 内吞 | Fig. 2d 未显示 |
| Gpr2/Gpr3 与 Gpa2 处于同一信号轴 | 中等至较强支持 |
| Gpr2/Gpr3 在原生真菌中形成异源二聚体 | 未直接证明；只有异源酵母 co-IP |
| Gpr2/Gpr3 直接结合 ascr#3/#7 | 未直接证明 |
| Y166/Y168 是真实关键结合残基 | 未验证 |
| Gpr3 接触残基已经确定 | 不支持 |
| Gpr3 功能上比 Gpr2 更重要 | 不支持 |
| 论文 docking 可严格复现 | 不支持；只能近似重跑 |

---

## 版本记录

| 日期 | 版本 | 说明 |
|---|---|---|
| 2026-04-03 至 2026-04-10 | v1.0–v2.1 | 旧版；包含多处图号、数值、方法和证据强度误读 |
| 2026-08-11 | v3.0 | 依据版本记录正文、Extended Data、官方 Source Data、Supplementary Tables 与透明审稿文件全面校正；新增详细证据指针 |
