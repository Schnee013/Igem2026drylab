# Gpr2、Gpr3、GprC 与 ascr#3 / ascr#18 的已发表证据

## Findings

### Bottom Line

截至 2026-08-11，没有找到任何已发表论文用纯化受体结合实验（如放射性/竞争结合、SPR、ITC、MST）、定量解离常数（Kd）或受体–配体实验结构，直接证明 Gpr2、Gpr3 或 GprC 与 ascr#3、ascr#18 的物理结合。因此，严格表述应是“论文支持该受体感知/响应某蛔苷素，并存在计算对接所预测的结合构象”，而不是“已经实验证明直接结合”。

两篇 2024 年 *Nature Microbiology* 原始研究提供了目前最关键的证据：

- **Gpr2 和 Gpr3** 属于 *Arthrobotrys oligospora*，论文对 **ascr#3 和 ascr#7** 做了受体相关的遗传学、细胞生物学和计算分析；**没有测试 Gpr2/Gpr3–ascr#18 配对**。
- **GprC** 属于 *Arthrobotrys flagrans*（旧名 *Duddingtonia flagrans*）。论文用 **ascr#18** 得到了 GprC 依赖的细胞响应，并对 **ascr#1、#2、#3、#5、#18** 全部进行了计算对接；其中 ascr#3 和 ascr#18 的预测结合能最优且非常接近。
- 因而，就项目选定的六个组合而言，证据排序是：**GprC–ascr#18 最强；Gpr2–ascr#3 与 Gpr3–ascr#3 次之；GprC–ascr#3 只有计算对接和非配体特异的结合口袋功能证据；Gpr2–ascr#18 与 Gpr3–ascr#18 尚无已发表配对证据。**

### Published Literature Status

- 检索范围：PubMed/PMC、Nature 和通用学术网页索引可检出的已发表期刊论文；用受体全名、物种名、ascr#3、ascr#18、ascr#7、ascaroside、binding、docking 等组合检索。
- 核心证据来自 [Kuo et al., 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11724650/) 与 [Hu et al., 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/) 两篇原始研究。
- 2023 年以前的研究证明蛔苷素可以诱导捕食线虫真菌形成陷阱，但没有把信号分配给 Gpr2、Gpr3 或 GprC。
- 检索到的学位论文、新闻、厂商页面、ResearchGate 转载、预印本和仅有搜索摘要而不可核实的材料均未用于最终受体–配体结论。

### Receptor–Ligand Claims

| 受体（物种） | 已发表论文支持的蛔苷素 | 证据层级 | 对 ascr#3 的判断 | 对 ascr#18 的判断 | 置信度与限制 |
|---|---|---|---|---|---|
| Gpr2（*A. oligospora* TWF154） | ascr#3、ascr#7 | 敲除降低诱捕环形成；过表达增强响应；ascr#7 诱导受体内吞；计算对接 | **支持为候选配体/被 Gpr2 感知**；预测 ΔG = −6.99 kcal/mol | **未测试，不能声称结合** | 中高；有功能与计算证据，无直接物理结合 |
| Gpr3（*A. oligospora* TWF154） | ascr#3、ascr#7 | 敲除降低诱捕环形成；过表达增强响应；ascr#7 诱导受体内吞；计算对接 | **支持为候选配体/被 Gpr3 感知**；预测 ΔG = −7.05 kcal/mol | **未测试，不能声称结合** | 中高；有功能与计算证据，无直接物理结合 |
| GprC（*A. flagrans*） | ascr#18（功能响应 + 对接）；ascr#1、#2、#3、#5（对接候选） | ascr#18 引发的 *artA* 启动子抑制依赖 GprC；结合口袋突变影响受体功能；五种蛔苷素均有计算对接 | **只支持计算候选结合**；预测 ΔG = −8.31 kcal/mol | **支持 GprC 依赖的感知/响应和计算候选结合**；预测 ΔG = −8.29 kcal/mol | ascr#18 为中高；ascr#3 为中低；均无直接物理结合 |

### Evidence Strength for the Six Project Pairs

| 项目配对 | 细胞/遗传功能证据 | 计算对接 | 直接物理结合 | 最稳妥结论 |
|---|---|---|---|---|
| Gpr2–ascr#3 | 有：敲除减弱、过表达增强 | 有 | 无 | 有较强的“感知/候选结合”依据 |
| Gpr2–ascr#18 | 无 | 无（已发表论文中未做） | 无 | 当前无配对证据 |
| Gpr3–ascr#3 | 有：敲除减弱、过表达增强 | 有 | 无 | 有较强的“感知/候选结合”依据 |
| Gpr3–ascr#18 | 无 | 无（已发表论文中未做） | 无 | 当前无配对证据 |
| GprC–ascr#3 | 无配体特异的湿实验 | 有 | 无 | 计算候选；不能写成实验验证结合 |
| GprC–ascr#18 | 有：*artA* 报告基因响应依赖 GprC | 有 | 无 | 六个组合中证据最强，但仍非直接结合证明 |

### Detailed Interpretation

#### Gpr2 和 Gpr3：ascr#3 / ascr#7

Kuo et al. 删除 *gpr2* 或 *gpr3* 后，ascr#3 和 ascr#7 诱导的陷阱数量均从野生型约 30–40 个/cm² 降到约 20 个/cm²；双突变没有比单突变更严重，提示二者非冗余且还存在其他蛔苷素受体。反向证据是 GPR2 或 GPR3 过表达均增强 ascr#3 与 ascr#7 诱导的陷阱形成。论文还观察到 ascr#7 暴露后 Gpr2–GFP 和 Gpr3–GFP 从细胞膜内吞至液泡，这是较接近配体激活的细胞证据。

需要注意：论文图 2 标题写成“ascr#3 和 ascr#7 触发 Gpr2/Gpr3 内吞”，但正文和图注描述的定位实验实际只使用了 **ascr#7**。因此不能把“ascr#3 诱导内吞”作为独立实验事实；ascr#3 的湿实验支持主要来自敲除与过表达后的陷阱表型。

计算方面，SwissDock 给出 Gpr2–ascr#3、Gpr2–ascr#7 的预测 ΔG 分别为 −6.99、−7.07 kcal/mol；Gpr3–ascr#3、Gpr3–ascr#7 分别为 −7.05、−6.41 kcal/mol。它们是模型评分，不是实验测得的结合自由能或 Kd。

#### GprC：ascr#18 与其他计算候选

Hu et al. 在野生型 *A. flagrans* 中观察到线虫或 ascr#18 会使 *artA* 启动子报告信号消失；在 Δ*gprC* 和 Δ*gasA* 中，该报告信号不再响应线虫或 ascr#18。这把 **ascr#18 的细胞响应明确连接到 GprC–GasA 通路**，但读出位于信号通路下游，不能单独排除共受体或间接机制。

该研究还将 ascr#1、#2、#3、#5、#18 对接到 GprC 模型。最佳预测结合能依次为 −7.26、−6.90、−8.31、−6.62、−8.29 kcal/mol；ascr#3 与 ascr#18 是五者中最优的两个。N2.57A、R6.45A、S2.41A 等突变破坏受体功能，且模型将其中部分残基置于预测正构口袋附近，为“GprC 存在蛔苷素结合口袋”提供功能支持，但这些突变实验不是用每一种蛔苷素逐一测定，不能据此证明五种配体都直接结合。

### Practical Implications

1. 如果项目要用“已有论文实验证据”筛选 docking 组合，优先级应为：**GprC–ascr#18 > Gpr2–ascr#3 ≈ Gpr3–ascr#3 > GprC–ascr#3**。
2. **Gpr2–ascr#18 和 Gpr3–ascr#18 应标为探索性/新假说组合**，不应在项目文本中写成已有文献支持。
3. 如果最终目标是声称“直接结合”，最低限度应补做受体依赖的剂量–反应与配体竞争；更强证据是纯化/膜制备结合实验获得 Kd，或用突变体证明 ascr#3/ascr#18 特异地依赖预测口袋残基。
4. 由于 Gpr2/Gpr3 与 GprC 来自两个不同 *Arthrobotrys* 物种，跨受体的配体谱差异可能同时反映物种、菌株、实验体系和受体本身，不能只归因于受体结构。

## Gaps and Conflicts

- 未找到 Gpr2/Gpr3 对 ascr#18 的已发表受体特异性测试。
- 未找到 GprC 对 ascr#3 的配体特异性湿实验；目前是计算对接候选。
- 三种受体均没有直接结合常数、竞争结合、热力学结合或受体–配体实验结构。
- Gpr2/Gpr3 论文的图 2 标题比正文实验范围更宽：标题包含 ascr#3 和 ascr#7，实际成像内吞实验只报告 ascr#7；本报告按正文和图注收窄结论。
- [Huang et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10536950/) 证明 ascr#18 能诱导 *A. oligospora* 陷阱并与氨产生协同，但没有测试 Gpr2 或 Gpr3，因此不能把这篇论文转换成 Gpr2/Gpr3–ascr#18 证据。
- “没有找到”是截至检索日的文献检索结果，不是逻辑上的绝对不存在；未公开数据、无法索引的非英文期刊或检索日之后发表的论文不在结论范围内。

## Research Objective

- Decision/use: 为捕食线虫真菌受体–蛔苷素 docking 和后续实验选择提供可引用证据，并防止把间接响应误写成直接结合。
- Target question: Gpr2、Gpr3、GprC 是否有已发表证据支持与 ascr#3、ascr#18 结合；每个受体还支持哪些编号的蛔苷素。
- Source scope: 截至 2026-08-11 可检出的已发表期刊论文；核心结论优先使用原始研究全文。
- Exclusions: 学位论文、预印本、新闻稿、百科、厂商页面、ResearchGate 转载和未发表材料不作为结论证据。
- Access date: 2026-08-11.

## Verified Source Ledger

| ID | Source | URL | Authority | Access | Relevance | Status |
|----|--------|-----|-----------|--------|-----------|--------|
| S1 | Kuo et al. (2024), “The nematode-trapping fungus *Arthrobotrys oligospora* detects prey pheromones via G protein-coupled receptors”, *Nature Microbiology* 9:1738–1751, DOI 10.1038/s41564-024-01679-w | https://pmc.ncbi.nlm.nih.gov/articles/PMC11724650/ | primary | 2026-08-11，全文可检视 | Gpr2/Gpr3 与 ascr#3/#7 的核心来源 | used |
| S2 | Hu et al. (2024), “GprC of the nematode-trapping fungus *Arthrobotrys flagrans* activates mitochondria and reprograms fungal cells for nematode hunting”, *Nature Microbiology* 9:1752–1763, DOI 10.1038/s41564-024-01731-9 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/ | primary | 2026-08-11，全文可检视 | GprC、ascr#18 功能响应与五种蛔苷素 docking | used |
| S3 | Huang et al. (2023), “Ammonia and Nematode Ascaroside Are Synergistic in Trap Formation in *Arthrobotrys oligospora*”, *Pathogens* 12:1114, DOI 10.3390/pathogens12091114 | https://pmc.ncbi.nlm.nih.gov/articles/PMC10536950/ | primary | 2026-08-11，全文/摘要可检视 | ascr#18 可诱导 *A. oligospora*，但不提供受体归属 | used for scope limitation |
| S4 | Hsueh et al. (2013), “Nematode-trapping fungi eavesdrop on nematode pheromones”, *Current Biology* 23:83–86, DOI 10.1016/j.cub.2012.11.035 | https://pmc.ncbi.nlm.nih.gov/articles/PMC4047969/ | primary | 2026-08-11，全文可检视 | 早期蛔苷素诱导谱；未鉴定受体 | used for historical context |

## Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|-------------------|-----------|---------|------------------|------------|---------|
| Gpr2 参与感知 ascr#3 和 ascr#7 | S1 | Results “GPCRs from the carbon receptor family sense ascarosides”, paragraph 1; Fig. 2a,b | Δ*gpr2* 对两种配体形成的陷阱均少于 WT | high | 表型仍保留，说明还有其他受体；不是直接结合 |
| Gpr3 参与感知 ascr#3 和 ascr#7 | S1 | 同上 | Δ*gpr3* 对两种配体形成的陷阱均少于 WT | high | 同上 |
| Gpr2/Gpr3 过表达增强 ascr#3/#7 响应 | S1 | Results paragraph 3; Fig. 3a | 两种过表达株对两种配体产生更多陷阱 | high | 下游表型，不能单独证明物理结合 |
| ascr#7 触发 Gpr2/Gpr3 内吞 | S1 | Results paragraph 2; Fig. 2d and caption | 两种 GFP 融合受体在 ascr#7 暴露后从膜进入液泡 | high | 成像只用了 ascr#7；不能外推为 ascr#3 的内吞实验 |
| Gpr2 与 Gpr3 可计算对接 ascr#3/#7 | S1 | Results paragraph 4; Fig. 3d; Extended Data Fig. 6 | Gpr2：−6.99/−7.07；Gpr3：−7.05/−6.41 kcal/mol | medium | 预测 ΔG，不是实验值；Gpr3 无强氢键预测 |
| ascr#18 的 *artA* 报告响应依赖 GprC | S2 | Results “GprC–GasA signalling controls gene expression…”, paragraph 1; Fig. 3a | WT 在 ascr#18 后丢失 *artA* 报告信号；Δ*gprC* 不响应 | high | 下游报告信号，不能排除间接感知机制 |
| GprC 可计算对接 ascr#1/#2/#3/#5/#18 | S2 | Results “A. flagrans GprC…share the ascaroside-binding site”; Fig. 5; Extended Data Table 2 | 五种预测能量为 −7.26/−6.90/−8.31/−6.62/−8.29 kcal/mol | medium | 不是实测亲和力；论文亦明确警告避免过度解释 docking |
| GprC 预测正构口袋对功能重要 | S2 | Results paragraphs 4–5; Fig. 4b, Fig. 5; Extended Data Table 2 | N2.57A、R6.45A、S2.41A 等突变影响功能，R6.45A 降低预测亲和力 | medium | 突变表型不是逐配体结合试验 |
| ascr#18 能诱导 *A. oligospora* 陷阱，但未归属 Gpr2/Gpr3 | S3 | Abstract; Results/Fig. 1 | ascr#18 与氨协同增加陷阱 | high | 不能作为任何特定受体的证据 |
| *A. oligospora* 对多种蛔苷素响应，#1/#3/#7 较强 | S4 | Results and Discussion; Fig. 2 | 十种蛔苷素测试中，C7/C9 侧链的 #1/#3/#7 诱导最强 | high | 2013 年未鉴定 Gpr2/Gpr3；不能据此扩张其配体谱 |
| Gpr2/Gpr3 论文未报告受体–配体直接物理结合测定 | S1 | 全文 Results、Methods 与图表审计 | 使用遗传学、成像、co-IP 和 docking；未报告受体–配体直接结合实验 | high | 仅限已检视全文 |
| GprC 论文未报告受体–配体直接物理结合测定 | S2 | 全文 Results、Methods 与图表审计 | 使用报告基因、突变和 docking；未报告受体–配体直接结合实验 | high | 仅限已检视全文 |

## Audit Notes

- 每个最终受体–配体结论均映射到 Evidence Table 中至少一行。
- 已核对两篇核心论文的正文、图注和方法；搜索摘要仅用于发现文献，不作为证据。
- 对接能统一标为计算预测，不称为实测“结合亲和力”。
- 早期真菌整体响应与受体特异响应分开呈现，未把不同物种的结果合并外推。
- 时效范围：以 2026-08-11 为检索截止日；精确检索未发现 2024 年两篇核心论文之后新增的 Gpr2/Gpr3/GprC–ascr#3/#18 直接结合原始研究。
- 结构验证：已运行 `evidence_lint.py`；并人工核对来源 ID、证据指针、结论强度与限制条件。
