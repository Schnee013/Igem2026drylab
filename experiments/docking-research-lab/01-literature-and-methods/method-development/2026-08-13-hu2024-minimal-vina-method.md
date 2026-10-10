# Hu2024 最小 Vina 方法记录

> 用途：为一次 GprC WT–ascr#18 复现和后续 Gpr2/Gpr3 WT 对接提供文献基准。
>
> 状态：0A 文献调研记录（含跨受体结构比较）；0B 审查已记录，0C 项目运行协议已冻结于 `MINIMAL_VINA_ROADMAP.md` 和 `config/minimal_vina.yaml`。
> 原则：只记录会影响输入、运行参数或结果验收的信息。

## Findings

### 最小结论

Hu2024 使用 AlphaFold DB 的受体模型，截取 GPCR 跨膜部分，经 ADFR Suite 制备受体；配体经 Avogadro 构建、Orca B3LYP/def2-TZVP 优化和 ADFR Suite 制备。Vina 使用 40 Å 立方搜索框、受体质心作为中心、`exhaustiveness=200`、`spacing=0.1 Å`，并分析前 5 个 pose。[S1, Methods: Modelling and docking]

这些信息足以定义文献基准，但不足以直接生成唯一命令：原文没有给出 GprC 的具体 TM 截取范围、质心所基于的精确原子集合、`seed`、`num_modes` 及若干 Vina 参数。[S1, Methods: Modelling and docking]

### 文献方法表

| 环节 | Hu2024 原文信息 | 对本项目的最小作用 | 置信度 |
|---|---|---|---|
| WT 受体 | GprC 模型来自 AlphaFold Protein Structure Database；TM 区域 pLDDT > 0.85 | 核对 GprC 模型身份和 TM 区结构质量 | high |
| 受体范围 | 对预测 GPCR 的 transmembrane portions 进行对接准备 | 只使用可追溯且统一定义的 TM 区域 | high |
| TM 边界 | 原文提到用 Phyre2 和 TMHMM 2.0 预测 TM，但未给出用于 docking 的具体残基范围 | 0B 必须核对仓库实际截取范围 | high |
| 受体制备 | ADFR Suite `prepare_receptor` | 优先复用同工具生成且来源清楚的 PDBQT | high |
| 配体构建 | Avogadro 构建 | 核对现有 ascr#18 是否来自相同或等价化学结构 | high |
| 配体优化 | Orca，B3LYP/def2-TZVP | 优先复用已完成且可追溯的优化结构，避免重复量化计算 | high |
| 配体柔性 | ADFR `prepare_ligand` 默认设置；ascarylose 环外单键可旋转；文中报告 7–11 DOF | 核对 ascr#18 PDBQT 的可旋转键定义 | high |
| 配体电荷 | Gasteiger charge model | WT 与突变体统一使用同一 prepared ligand | high |
| Vina 版本 | Reporting Summary 记录 AutoDock Vina 1.2.3 | 复现时记录实际版本；版本差异需要在结果中注明 | high |
| 搜索框 | 40 Å 立方体，中心为 receptor centre of mass | 0B 核对中心究竟由哪一份 receptor/TM 输入计算 | high |
| 搜索参数 | `exhaustiveness=200`；`spacing=0.1 Å` | 作为 GprC 验证任务的文献基准 | high |
| pose 分析 | 使用前 5 个 binding poses；扩展数据报告最佳 pose 分数 | 保存至少前 5 个 pose，并同时检查最佳分数与 pose 位置 | high |
| 接触残基 | 对 20 个 pose 中距配体 3.5 Å 内的受体残基进行汇总 | 可作为 GprC 复现的简单接触检查，不要求先建立复杂 IFP | high |

### GprC–ascr#18 最小验收参照

| 检查项 | 文献参照 | 用法 |
|---|---|---|
| 最佳 Vina 分数 | −8.29 kcal/mol | 仅用于核对量级和明显输入错误，不设为单独通过条件 |
| 口袋方向 | 胞外侧的经典正构口袋 | 代表 pose 应位于胞外侧跨膜口袋 |
| 参与区域 | 主要涉及 TM2、TM3、TM5、TM6、TM7；GprC 的 ECL2 参与接触 | 用于人工检查 pose 是否落在合理区域 |
| 残基比较 | 原文用 Ballesteros–Weinstein 编号，并汇总 3.5 Å 接触残基 | 只在编号映射可追溯时比较；不根据 BW 编号猜绝对序号 |
| 解释边界 | 论文提醒缺失 loop dynamics 和 induced fit 会影响结果 | 优先比较 pose 集合和相对排序，避免把单个分数解释为真实亲和力 |

### GprC、SRBC-64 与 DAF-37 的结构比较

Hu2024 用这三个低序列相似性的 ascaroside GPCR 比较“合理口袋应该在哪里、由哪些结构区域组成”。这些受体在绝对序列上不必相同，因此应优先比较 TM 相对位置和口袋几何。[S1, Results pp. 1758–1759; Fig. 5]

| 特征 | GprC | SRBC-64 | DAF-37 | 对 docking 判读的意义 |
|---|---|---|---|---|
| 整体相似性 | 与 SRBC-64 的 TM2/TM3 形状及 ECL2 长度更接近 | 与 GprC 更接近 | TM2/TM3 更长、倾斜更明显 | 不要求不同受体具有相同绝对坐标；比较受体内部的相对口袋位置 |
| 典型结合区 | 胞外正构口袋 | 胞外正构口袋 | 胞外正构口袋，但几何不同 | 胞内侧或远离正构腔的 pose 优先判为可疑 |
| 参与的 TM | TM2、TM3、TM5、TM6、TM7 | TM2、TM3、TM5、TM6、TM7 | TM2、TM3、TM5、TM6、TM7 | TM1、TM4 在文中未参与配体结合，可作为异常 pose 的提示 |
| ECL2 | 较短，参与 ascaroside 接触 | 较短，参与接触 | 更长，20 个汇总 pose 中无 ECL2 接触 | GprC/Gpr2/Gpr3 的 ECL2 应保留并检查，但 ECL2 接触不是所有受体都必须具有 |
| 保守锚点 | D2.50；TM6 常见 Pro | D2.50；TM6 常见 Pro | D2.50；TM6 对应位置为 Trp | 用于 TM/BW 对齐和结构核对，不自动等同于配体接触或突变候选 |
| 口袋共同化学特征 | ECL2 芳香残基、TM2 极性/碱性残基 | 同类特征 | 部分同类位置 | 跨受体迁移时比较“化学性质+相对位置”，不强求相同氨基酸 |

### Hu2024 汇总的口袋接触位置

下表来自 Extended Data Table 3，是多个 ascaroside pose 的 `3.5 Å` 接触并集，不是 ascr#3 或 ascr#18 的单独接触表。[S1, Extended Data Table 3]

| 区域 | GprC | SRBC-64 | DAF-37 |
|---|---|---|---|
| TM2 | N2.53, N2.57, S2.60, R2.63 | Y2.53, V2.57, N2.60, K2.61 | L2.53, Y2.61 |
| TM3 | N3.28, Q3.33, V3.36 | I3.29, T3.32, I3.33, C3.37, R3.39 | S3.32, H3.33, Q3.36 |
| TM5 | T5.39, H5.40, R5.44 | W5.39, R5.42, D5.43, Q5.46, Y5.47 | T5.42, N5.43, M5.46, V5.47 |
| TM6 | W6.48, R6.55* | I6.43, S6.47, S6.51 | N6.48, L6.54, T6.55 |
| TM7 | Q7.39, T7.42, Q7.43 | I7.32, K7.35, H7.36 | R7.35, I7.38, N7.39, A7.42, N7.45 |
| ECL2 / Loop4-5 | W45.52, W45.54 | F45.48 | 无 |

`*` 论文内部编号存在冲突：正文、Figure 4 和 Extended Data Table 2 将突变写为 `R6.45A`，Figure 5 接触图和 Extended Data Table 3 将接触精氨酸写为 `R6.55`。本项目使用绝对残基前必须通过序列和结构重新核对。

### R-motif、S-motif 与功能突变

| 位点/特征 | 文献证据 | 应如何用于 docking |
|---|---|---|
| GprC N2.53 | 更靠胞内；Ala 突变未影响受体功能 | 可作为口袋方向的阴性对照，不能因它靠近某个 pose 就认定 pose 合理 |
| GprC N2.57 | 更靠胞外；Ala 突变导致功能丧失 | 合理 pose 应接近同一胞外口袋区域 |
| SRBC-64 N2.60 | Ala 突变影响功能 | 支持 TM2 胞外端是跨受体可比的口袋锚点 |
| R-motif | 三个受体均存在；只有 GprC 的 Arg 指向口袋并与功能/预测分数相关 | motif 存在不等于直接结合；必须检查侧链方向和实际接触 |
| S-motif / S2.41 | GprC 和 SRBC-64 具有；远离结合位点，但 GprC 突变影响功能 | 这是信号/构象完整性保护位点，不适合作为仅凭接触差异挑选的首轮突变位点 |
| D2.50 | 三个受体均具有的高度保守 TM2 残基 | 主要用于 TM 对齐和结构合理性检查，首轮默认保留 |

Extended Data Table 2 中，GprC 对 ascr#3 的 WT、N2.53A、N2.57A、R6.45A 最佳分数依次为 `−8.31`、`−7.91`、`−7.57`、`−6.69 kcal/mol`；SRBC-64 N2.60A 对 ascr#3 只从 `−7.61` 变为 `−7.45 kcal/mol`，但实验功能受到影响。[S1, Extended Data Table 2; Fig. 4b] 这说明 Vina 分数适合排序和发现明显变化，不能覆盖信号传导或远端功能位点。

### 对本项目 docking 结果分析的最小规则

1. **先判口袋位置**：代表 pose 位于胞外正构腔，并主要由 TM2、TM3、TM5、TM6、TM7 包围；胞内侧、膜外沟槽或以 TM1/TM4 为主的 pose 降级处理。
2. **再判结构接触**：为每个 pose 标注参与的 TM、ECL2 和 BW 相对位置；优先比较化学类型和空间位置，不直接搬用其他受体的绝对残基号。
3. **最后做两配体差异**：共同高频接触残基保留；ascr#3/ascr#18 的差异接触残基才进入 Ala 候选池。
4. **设置保护位点**：D2.50、S2.41 及其他保守结构/信号位点默认不进入首轮突变；R-motif 需人工检查侧链方向后再决定。
5. **分数只作同协议排序**：接触几何、口袋位置和重复方向必须与分数一起判断；功能结论需要独立实验。

Hu2024 的 SRBC-64/DAF-37 比较只作为判读参照，不增加本项目的对接任务数。

### 0C 必须解决的最小缺口

1. GprC 的 AlphaFold DB accession、下载版本和文件 checksum；
2. 用于 docking 的 TM 绝对残基范围，以及 ECL2 是否完整保留；
3. 40 Å box 中心由全长结构还是截取后的 TM 结构计算；
4. ascr#18 的质子化状态、净电荷和现有 PDBQT 的可旋转键数；
5. 实际使用的 ADFR Suite 与 Vina 版本；
6. 原文未给出的 `seed`、`num_modes`、`energy_range`、`min_rmsd` 和 CPU 设置；
7. `spacing=0.1 Å` 与 40 Å box 在所选 Vina 版本中的实际运行方式。

0B 已提供现有输入和代码的核对结果；0C 将项目选择冻结成一页方法表。0A 不补猜参数。

## Gaps and Conflicts

- 主文没有提供代码仓库或完整 Vina 命令。
- 主文未明确 TM 截取的绝对残基范围，也未说明 box 质心采用的具体原子集合。
- 主文没有说明 `seed`、重复次数、`num_modes`、`energy_range`、`min_rmsd`、CPU 数和受体质子化细节。
- 文中 “7–11 DOF for the four ascarosides” 不能直接证明 ascr#18 的确切 DOF；应从最终 PDBQT 核对。
- pLDDT > 0.85 是 TM 区域质量描述，不是原文声明的 TM 截取阈值。
- 图 5 和正文的口袋/接触结论汇总多个 ascaroside pose；它们可用于 GprC–ascr#18 的区域级检查，不能假定每个列出的残基都必须接触 ascr#18。
- GprC 的同一精氨酸在正文/突变表中标为 R6.45，在接触图/Extended Data Table 3 中标为 R6.55；绝对残基映射必须单独核验。
- Extended Data Table 3 说明 GprC 和 SRBC-64 的 TM7 `.50` 锚点不能清楚定义，因此 TM7 的 BW 编号只能作为近似结构参照。
- 嵌合受体结果支持 S/R motif 与功能的关系，但嵌合模型中的 pose 不直接证明 WT Gpr2/Gpr3 的结合方式。

## Research Objective

- Decision/use: 冻结对后续 GprC–ascr#18 复现和 Gpr2/Gpr3 WT 对接有直接作用的 Hu2024 文献基准。
- Target question: Hu2024 明确报告了哪些 Vina 参数、跨受体口袋特征、motif、关键残基和 pose 验收信息；哪些关键执行参数仍未说明？
- Source scope: Hu2024 正式论文、Methods、Reporting Summary、Figures 4–5 与 Extended Data Tables 2–3。
- Exclusions: 与最小 Vina 复现无直接作用的实验方法和生物学结果。
- Access date: 2026-08-14。

## Verified Source Ledger

| ID | Source | URL | Authority | Access | Relevance | Status |
|---|---|---|---|---|---|---|
| S1 | [Hu et al. 2024 正式论文](https://doi.org/10.1038/s41564-024-01731-9) | https://doi.org/10.1038/s41564-024-01731-9 | primary | 2026-08-14 | Methods、Figures 4–5、Extended Data Tables 2–3 | used; full text and relevant PDF pages inspected |
| S2 | [Nature Portfolio Reporting Summary](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01731-9/MediaObjects/41564_2024_1731_MOESM2_ESM.pdf) | https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01731-9/MediaObjects/41564_2024_1731_MOESM2_ESM.pdf | primary | 2026-08-13 | 软件与版本信息 | used; 3-page PDF inspected and rendered |

## Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|---|---|---|---|---|---|
| WT GprC 使用 AlphaFold DB 模型，准备其 TM 部分 | S1 | Methods, “Modelling and docking”, pp. 1761–1762 | AlphaFold DB 模型；ADFR `prepare_receptor` 处理 transmembrane portions | high | 未给绝对残基范围 |
| 配体经 Avogadro、Orca B3LYP/def2-TZVP 和 ADFR 准备 | S1 | Methods, “Modelling and docking”, p. 1762 | 报告配体构建、量化优化、可旋转键与 Gasteiger 电荷 | high | 未给 ascr#18 单独 DOF 和质子化状态 |
| Vina 搜索参数为 40 Å、受体质心、exhaustiveness 200、spacing 0.1 Å | S1 | Methods, “Modelling and docking”, p. 1762 | 原文直接给出四个核心搜索参数 | high | 未给其余命令参数 |
| 分析前 5 个 pose，并报告最佳 pose 分数 | S1 | Results p. 1759; Methods p. 1762; Extended Data Table 2 | 每种 ascaroside 分析前五姿态；表 2 为最佳姿态分数 | high | 不代表进行了五次独立重复 |
| GprC–ascr#18 最佳分数为 −8.29 kcal/mol | S1 | Extended Data Table 2 | 表中 GprC/ascr#18 的 best pose affinity | high | 只适合作为复现参照 |
| 接触集合按距 20 个 pose 3.5 Å 的受体残基统计 | S1 | Results p. 1759; Figure 5 legend | 论文用 3.5 Å 距离汇总三个受体的 coordinating residues | high | 汇总多个 ascaroside pose |
| 三个受体的正构口袋主要涉及 TM2/3/5/6/7，TM1/4 未参与 | S1 | Results p. 1759; Fig. 5; Extended Data Table 3 | 三个模型均形成胞外经典正构口袋，五条 TM 提供接触 | high | 来自静态预测结构和 pooled poses |
| GprC/SRBC-64 的 ECL2 参与接触，而 DAF-37 的更长 ECL2 未接触汇总 poses | S1 | Results p. 1759; Fig. 5d–f | ECL2 长度和参与方式构成跨受体差异 | high | 不代表 ECL2 在动态体系中永不接触 |
| N2.57、N2.60、R-motif 与 S-motif 的功能角色不同 | S1 | Fig. 4b; Results p. 1759; Extended Data Table 2 | 胞外 TM2 Asn 和 GprC R-motif 关联口袋；S2.41 远离口袋但对功能重要 | high | 功能效应不能仅由 docking score 解释 |
| GprC R-motif 的 BW 编号在论文内部冲突 | S1 | Results p. 1759; Fig. 4; Fig. 5g; Extended Data Tables 2–3 | 正文/突变表为 R6.45，接触图/表为 R6.55 | high | 应使用经序列/结构核验的绝对残基号 |
| SRBC-64/DAF-37 比较支持使用相对结构位置而非绝对残基身份 | S1 | Results pp. 1758–1759; Fig. 5g–i | 共同特征有限，主要是 ECL2 芳香、TM2 极性/碱性位置和胞外口袋几何 | high | 不能据此假定 Gpr2/Gpr3 具有相同配体谱 |
| 使用 Vina 1.2.3、Avogadro 1.2.0、Orca 5.0.1 | S2 | Reporting Summary, p. 1, “Software and code / Data analysis” | 软件版本列于报告页 | high | ADFR Suite 版本未列出 |

## Audit Notes

- 正式论文的 Methods、Results、Figures 4–5 和 Extended Data Tables 2–3 已交叉核对；PDF 第 6–8、17–18 页已渲染并人工检查。
- Reporting Summary 共 3 页；核验记录包括全文抽取尝试、全部页面渲染和第 1 页人工检查。扫描式表单的文本层不完整，因此版本按页面视觉核验记录。
- 每个执行相关结论均映射到 S1 或 S2；原文缺失参数全部保留为缺口。
- 本文件不把 Drylab 的既有实现当作文献事实；仓库复用审查属于 0B。
