# 补充 MSA 对 ASCR3 / ASCR18 识别与配体区分残基的证据评估

日期：2026-08-26  
分析对象：DAF-37、Gpr2、Gpr3、GprC、SRBC-64 五个目标受体  
主结论对象：当前被视为生物学有效的 docking construct；Gpr2、Gpr3 使用 deltaN，另外三个受体使用 WT  
配套数据：[残基映射证据表](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/residue_mapping_evidence.csv)与[带 MSA 注释的完整 ProLIF 配对矩阵](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/prolif_ligand_discrimination_matrix_all_msa_annotated.csv)

## Findings

### 结论先行

补充 MSA 确实增加了证据，但增加的是“这些残基是否可能处在可比较的位置”以及“该位置受到多强的序列约束”，不是“该残基已经被证明决定配体选择性”。

最有价值的新结果有三点：

1. **ASCR3 没有得到一个可称为五受体保守功能残基的位点。**唯一的既有 ASCR3 区分候选是 GprC N56 的 `HBAcceptor`：五个模型中两种配体都可接触该位点，但 ASCR3 在 3/5 个配对模型中更高，中位配对差为 +0.222。五受体 MSA 对这个位置的对应关系和氨基酸保守性都较弱，而且算法敏感；受体内 A3M 中 N56 的 exact/class 比例也只有 0.441/0.471。文献中的 N2.53A（由序列和突变引物固定为全长 N56）对总受体功能没有可检测影响。因此，N56 更适合被称为**GprC 的 ASCR3-vs-ASCR18 差异性突变位点**，不适合被称为五受体共同、功能必需的 ASCR3 残基。

2. **ASCR18 得到了一个三受体层面的高可信 TM6 芳香核心。**Gpr2 W338、Gpr3 W306、GprC W388 同时满足：位于两套拓扑预测的 TM6；MAFFT 和 MUSCLE 都把三者放到同一列；三者两两之间的 US-align 映射在 25/25 个模型组合中一致；三者各自都映到 c7xmsA:226；受体内 A3M exact 比例分别为 0.992、0.966、0.971。三个位点也都在原有 ASCR18 区分候选中。这个组合支持“ASCR18 倾向由 TM6 芳香侧链提供疏水稳定”的机制假说。它目前只对 Gpr2/Gpr3/GprC 可靠，尚不能扩展为五受体共同残基。

3. **MSA 能帮助区分‘共享核心’和‘受体特异调节位点’，但不能单独证明同一受体如何区分两个配体。**Gpr3 Y172、GprC W155/W157、SRBC-64 F161 等候选仍有清楚的受体内 ASCR18 偏好，但跨五受体映射较弱或 construct 不可比，应作为受体特异假说处理。真正的配体区分证据仍需同一受体、同一表达背景下分别测 ASCR3 和 ASCR18 的突变效应。

### 当前最简机制模型

| 层次 | ASCR3 | ASCR18 | MSA 增加的证据 | 当前解释 |
|---|---|---|---|---|
| 共享 GPCR 结构框架 | 进入正构口袋的可能性 | 进入正构口袋的可能性 | 拓扑、结构与 c7xmsA fold anchor 支持大体可比的跨膜框架 | 只说明结构位置可比，不说明配体亲和力 |
| 候选稳定作用 | GprC N56 的方向性氢键受体接触 | Gpr2 W338、Gpr3 W306、GprC W388 的芳香/疏水接触 | N56 映射和保守性弱；TM6 W 簇有多方法一致证据 | ASCR3 可能依赖局部极性几何；ASCR18 更可能利用 TM6 芳香侧链 |
| 受体特异修饰 | 当前没有第二个达到既有阈值的 ASCR3 位点 | Gpr3 Y172、GprC R174、W155/W157、SRBC-64 F161 等 | 多数位置跨受体不稳定，或落入 deltaN 删除区 | 可能塑造单个受体内的 ASCR18 偏好，不应称为五受体保守核心 |
| 因果证据 | 无 ASCR3-vs-ASCR18 残基突变比较 | 无 ASCR3-vs-ASCR18 残基突变比较 | MSA 不提供因果性 | 需要双配体、同批突变实验 |

### ASCR3：N56 值得测，但理由是“区分”，不是“保守必需”

- ProLIF 证据：GprC `ASN56.A–HBAcceptor` 为 moderate discriminator；5/5 模型有可比较数据，ASCR3 在 3/5 模型中频率更高，中位配对差 +0.222。
- 五目标全长 MSA：MAFFT 对应列为 N65/M73/L59/N56/M54，exact 和同化学类别均为 2/5；MUSCLE 对应列为 L82/M73/L59/N56/gap，exact 和同类别均为 1/5。两个算法对 DAF-37、SRBC-64 的对应关系不一致。
- 受体内序列约束：GprC 的过滤 A3M 在该位置覆盖 34 条序列，N exact 为 15/34（0.441），同化学类别为 16/34（0.471），不属于强约束位点。
- 结构映射：US-align 能稳定给出 GprC N56 对 DAF-37 L81、Gpr2 M73、Gpr3 L59、SRBC-64 Y56 的结构对应位置，但这些氨基酸并不保守；“结构上可对应”与“化学功能保守”是两件事。
- 文献证据：[GprC 研究](https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/)在 Par18 报告 N2.53A 对总受体功能无影响；突变引物和 D2.50=D53 将 N2.53 固定为全长 N56。这降低了“总功能必需残基”的优先级，却没有排除它只改变 ASCR3/ASCR18 相对偏好的可能。

因此，N56A 实验的判别力很高：如果 N56A 保留总体表达与一般受体功能，却选择性降低 ASCR3 相对 ASCR18 的响应，它会直接支持配体区分；如果两种配体都不变，则现有 ProLIF 差异更可能是 pose 几何波动。

### ASCR18：TM6 芳香核心是补充 MSA 后最强的新线索

Gpr2 W338、Gpr3 W306、GprC W388 的证据相互独立且方向一致：

- **受体内配体区分：**Gpr2 W338–Hydrophobic 为 5/5 模型支持、5/5 偏向 ASCR18、中位差 +0.222；Gpr3 W306–Hydrophobic 为 4/5 支持、3/5 偏向 ASCR18、中位差 +0.222；GprC W388–VdWContact 为 5/5 支持、4/5 偏向 ASCR18、中位差 +0.333，W388–Hydrophobic 为 5/5 支持、3/5 偏向 ASCR18、中位差 +0.333。`VdWContact` 只代表接触，不能解释为结合力。
- **五目标直接 MSA：**三者都位于 MAFFT 列 485 和 MUSCLE 列 477。MAFFT 还把 DAF-37 W301 和 SRBC-64 F235 放入该列，得到 4/5 exact、5/5 aromatic；MUSCLE 只加入 DAF-37 W301，SRBC-64 为 gap，得到 4/4 available exact/aromatic。
- **受体内 A3M：**Gpr2 W338、Gpr3 W306、GprC W388 的 exact 比例分别为 0.992、0.966、0.971；GprC 的 aromatic class 为 1.000。这里衡量的是各受体自身同源序列中的约束，不进入“五目标受体保守性”的 5 个分母。
- **不依赖 c7xmsA 的结构映射：**以三者中任一位点为查询，US-align 都在 25/25 个相关模型组合中把另外两个受体映到对应 W。这个证据支持 Gpr2/Gpr3/GprC 三者的位置同源性假说。
- **c7xmsA fold anchor：**三个位点分别独立映到 c7xmsA:226，提供第二条折叠框架线索。五个受体对 c7xmsA 的序列一致性只有 9–19%，因此 c7 只作结构锚点，不能单独决定同源残基。
- **边界：**对 DAF-37 和 SRBC-64，US-align 从这组三个 W 查询得到的结构对应分别是 N299 与 S228，而不是直接 MSA 给出的 W301 与 F235；MUSCLE 也没有把 SRBC-64 F235放入该列。因此，五受体共同的 TM6 芳香残基仍是未解决假说。

### 其他同一受体区分候选的定位

| 候选 | 原有配体区分信号 | 补充映射结果 | 现在最合适的定位 |
|---|---|---|---|
| GprC R174–VdWContact | ASCR18；5/5 支持、4/5 偏好、中位差 +0.333 | MAFFT 仅 1/5 exact；MUSCLE 3/5；结构映射与直接 MSA 对其他受体不一致 | 有文献总功能突变重合，优先做 GprC 内部验证；不能称跨受体保守选择性位点 |
| Gpr3 Y172–Hydrophobic / VdWContact | Hydrophobic 5/5 支持、5/5 偏好、中位差 +0.333；另有 VdWContact 信号 | MAFFT 1/5 exact、MUSCLE 2/5；A3M exact 0.216，class 0.564 | 较强的 Gpr3 特异 ASCR18 假说 |
| GprC W155/W157 | 两者均为 ASCR18 候选，W155 同时有 Hydrophobic 与 VdWContact | 全长 MSA 中的 Gpr2/Gpr3 对应位点落入 deltaN 删除区；construct-aware 分母只有 3 个可用受体 | 只在 GprC 内解释；不能用 Gpr2/Gpr3 deltaN docking 作跨受体支持 |
| SRBC-64 F161–Hydrophobic | ASCR18；5/5 支持、4/5 偏好、中位差 +0.222 | 两套 MSA 仅覆盖 2 个受体；结构对应不稳定；A3M exact 0.486 | SRBC-64 特异假说，优先级低于三受体 TM6 W 簇 |
| Gpr2 Y168 | 不在当前 ProLIF 矩阵或候选中 | 文献只预测其接触 ascr#3/ascr#7；该位点在当前 deltaN construct 中不存在 | 文献参考位点，不能用于当前 ASCR3/ASCR18 deltaN 结论 |

### 推荐突变与实验顺序

建议所有突变在同一批次分别测 ASCR3 与 ASCR18，并至少配套受体表达量/定位和一个一般功能读出。只测单一配体，无法判断“配体选择性改变”还是“受体整体失活”。

1. **GprC N56A，同时加入 N60A。**N56A 是 ASCR3-vs-ASCR18 差异检验；N60A 是文献中会导致总功能丧失的阳性突变对照。预期最有信息量的结果是 N56A 选择性改变 ASCR3/ASCR18 响应比，而 N60A 同时削弱总体响应。
2. **GprC R174K 与 R174A。**R174A 测试去除正电荷和侧链体积的综合效应；R174K 尽量保留正电性，用于区分电荷作用与整体结构/表达崩溃。该位点的 ProLIF 候选轨道是接触型 `VdWContact`，不能预设盐桥或亲和力机制。
3. **Gpr2 W338F、Gpr3 W306F、GprC W388F。**先以 W→F 保留芳香性、减小侧链，直接检验三受体共享的 TM6 芳香核心是否更偏向稳定 ASCR18；若有选择性效应，再考虑更激进的 W→A。
4. **Gpr3 Y172F 与 Y172A。**Y→F 保留芳香环但去除羟基，Y→A 同时去除芳香性，可区分极性与疏水/堆积贡献。
5. **GprC W155F、W157F 及 W155F/W157F 双突变。**只作为 GprC 内部位点测试，不作 Gpr2/Gpr3 deltaN 的同源位点比较。
6. **SRBC-64 F161Y 与 F161A。**用于检验 SRBC-64 特异的芳香侧链假说；由于跨受体映射证据较弱，排在后面。

若资源只允许先做一组，建议从 **GprC N56A + N60A，并双配体同测** 开始；它最直接回答“同一受体是否利用不同残基区分 ASCR3 与 ASCR18”。若资源允许做跨受体验证，则第二组优先做三受体的 TM6 W→F。

## Gaps and Conflicts

1. **五受体序列距离较远，直接 MSA 对局部位置算法敏感。**MAFFT L-INS-i 与 MUSCLE super5 在 N56、R174、SRBC-64 F161 及部分环区给出不同对应关系。只有两算法、拓扑、结构和/或 profile 证据趋同时，才提高同源位置判断。
2. **TM6 W 簇对 DAF-37、SRBC-64 的序列与结构映射冲突。**MAFFT 提出 DAF-37 W301、SRBC-64 F235；MUSCLE 只支持 DAF-37 W301；从 Gpr2/Gpr3/GprC W 查询的 US-align 则给出 DAF-37 N299、SRBC-64 S228。故三受体结论较强，五受体结论暂不成立。
3. **HHalign 不能被当成每个位点都已映射。**过滤 A3M 的 profile–profile 比较强烈支持 Gpr2–Gpr3，以及 Gpr2/Gpr3–GprC 的整体同源关系；但在 TM6 W 这个具体查询位点，HHR 映射只直接返回 Gpr2 W338↔Gpr3 W306，没有返回 GprC W388。该位点的三受体结论主要来自直接 MSA、拓扑、US-align、A3M 约束和 c7 锚点的交叉支持。
4. **construct 缺失必须与 gap 分开。**Gpr2、Gpr3 使用 deltaN。映射到其删除区的位置被标记为 `NA_construct_absent`，不是“无接触”或“非保守”。GprC W155/W157 对应的 Gpr2/Gpr3 全长位置，以及文献中的 Gpr2 Y168，不能用于当前 deltaN docking 的接触解释。
5. **c7xmsA 是 fold anchor，不是五受体同源性的裁决者。**既有 Phyre2 配对比对概率高，但一致性只有 9–19%；c7 映射与不依赖 c7 的 MSA/结构映射已分开保留。
6. **GprC R 位点存在文献编号冲突。**主文 Par19 与补充突变构建写 `R6.45`，Extended Data Table 3 写 `R6.55`。突变引物把实际全长位点固定为 R174；DeepTMHMM、MEMSAT 和 c7 映射均把 R174 放在当前 TM5-like 区域。因此报告保留原始冲突，并用“全长 R174”作为本项目唯一操作编号，不替文献修正 generic number。
7. **已发表突变测的是总受体/嵌合受体功能，不是 ASCR3-vs-ASCR18 选择性。**[GprC 论文](https://doi.org/10.1038/s41564-024-01731-9)支持 N60、R174、S44 等位点与总功能有关；它没有分别比较这些突变对 ASCR3 和 ASCR18 的响应。[Gpr2/Gpr3 论文](https://doi.org/10.1038/s41564-024-01679-w)实验上研究 ascr#3/ascr#7，Y168 只有 docking 预测；没有 ASCR18 或 Y168 突变。[SRBC-64/66 论文](https://doi.org/10.1126/science.1176331)提供受体级遗传与异源表达证据，没有本项目候选的单残基突变。
8. **ProLIF、MSA 和静态结构都不是亲和力或因果证据。**ProLIF 频率描述给定 docking poses 中的几何接触；MSA 描述位置对应和序列约束；US-align 描述静态折叠对应。它们不能替代正确化学状态下的动力学、结合实验或功能突变。
9. **外部文献没有补上 DAF-37、SRBC-64 F161 或三受体 TM6 W 簇的直接突变证据。**这些仍是由本项目计算证据产生的可检验假说。

## Research Objective

- Decision/use: 为 ASCR3、ASCR18 残基突变实验排序，并判断哪些候选可称为跨受体共享核心、哪些只能称为受体特异配体区分位点。
- Target question: 补充 MSA 是否能为 ASCR3 与 ASCR18 各自的保守功能残基，以及同一受体区分两个配体的残基，提供更多证据？
- Source scope: 五目标受体的全长 FASTA、当前有效 docking constructs、AF3 五模型、现有 A3M、DeepTMHMM/MEMSAT、Phyre2–c7xmsA 比对、ProLIF 源工作簿与派生矩阵，以及可核对的一级文献。五目标“保守”固定只含这五个受体；外部同源序列只作为 A3M 受体内约束。
- Exclusions: 不生成新 docking、MD 或实验数据；不把接触频率解释为能量；不把 c7xmsA 单独当作同源性证明；不把全长序列中落入 deltaN 删除区的位点用于当前 construct 的接触结论。
- Access date: 2026-08-26。

## 方法与证据框架

### 1. 先保留原有“同一受体、五模型配对”统计

没有重新定义候选。原矩阵的 451 个数据行和 65 个原始字段逐值保留；原有 22 个候选的 receptor、construct、residue、interaction、ligand、tier 均保持不变。MSA 注释只增加解释列，不反向改变 ProLIF 候选门槛。

原有门槛是描述性筛选：偏好配体至少在 3/5 个配对模型中频率更高，中位配对差至少 0.20，并满足相应复现度；它不是结合能阈值。

### 2. 将“保守性”拆成七种不可互换的证据

| 证据层 | 计算/来源 | 回答的问题 | 不能回答的问题 |
|---|---|---|---|
| 五目标全长直接 MSA | MAFFT L-INS-i、MUSCLE super5 | 五个指定受体在某列是否 exact/同化学类别；算法是否一致 | 当前 construct 是否实际包含该位点；是否决定配体功能 |
| construct-aware MSA | 将映射到删除区的残基标记 `NA_construct_absent`，按 available 重算 | 在当前五个 biologically valid constructs 中，哪些比较仍有效 | 缺失位点的功能；把缺失当成不保守 |
| 受体内 A3M 约束 | 每个 AF3 unpaired A3M 经 `hhfilter -id 80 -cov 50 -qid 10` | 该受体自己的同源 profile 对这个位置约束多强 | 五目标受体之间是否同源；配体选择性 |
| HHalign profile mapping | 五个过滤 profile 两两比较，共 10 对 | 远缘受体整体 profile 是否支持对应区段 | HHR 未覆盖的具体位置不能视为已映射 |
| US-align 结构映射 | 每对受体 5×5 个 AF3 模型组合，共 25 次；10 对共 250 次 | 某个查询残基在折叠中最稳定对应到哪里 | 动态稳定性、结合能、突变因果 |
| c7xmsA fold anchor | 五个既有 Phyre2 配对比对 | 相对同一已知 GPCR 折叠锚点的位置 | 五受体直接同源性；单独裁决冲突 |
| 文献残基/受体证据 | 一级论文主文、扩展数据与补充突变表 | 已测试的总功能位点、受体级作用或文献 docking 线索 | 未执行的 ASCR3-vs-ASCR18 残基选择性实验 |

### 3. 两种分母同时保留

- **五目标全长口径：**固定分母为 5；gap 仍计入五目标范围，结果写作 exact n/5、chemical class n/5，并保留覆盖数。
- **当前 construct 口径：**五个目标仍是全集，但落入 biologically valid construct 删除区的具体单元写作 `NA_construct_absent`；比例只在 available 单元中计算，并明确写出 n/available。该口径服务于当前 docking 主结论。

## Verified Source Ledger

| ID | Source | URL | Authority | Access | Relevance | Status |
|---|---|---|---|---|---|---|
| S1 | 带 MSA 注释的完整 ProLIF 配对矩阵 | [../../../experiments/docking-repro/analysis/final-docking/msa-prolif/prolif_ligand_discrimination_matrix_all_msa_annotated.csv](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/prolif_ligand_discrimination_matrix_all_msa_annotated.csv) | derived local analysis | 2026-08-26 | 451 个原始配对行及新增映射、约束、文献注释 | used |
| S2 | 残基映射证据表 | [../../../experiments/docking-repro/analysis/final-docking/msa-prolif/residue_mapping_evidence.csv](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/residue_mapping_evidence.csv) | derived local analysis | 2026-08-26 | 211 个 ProLIF residue key 与 2 个文献补充位点的逐残基证据 | used |
| S3 | ProLIF interaction frequency profiles 源工作簿 | [../../../experiments/docking-repro/results/final-docking/prolif/af3/merged/prolif_interaction_frequency_profiles.xlsx](../../../experiments/docking-repro/results/final-docking/prolif/af3/merged/prolif_interaction_frequency_profiles.xlsx) | primary local result | 2026-08-26 | Sources、README 与四个 profile sheets | used |
| S4 | 未经候选阈值截断的 ASCR3/ASCR18 配对矩阵 | [../../../experiments/docking-repro/analysis/final-docking/msa-prolif/sources/prolif-ligand-discrimination-readonly/prolif_ligand_discrimination_matrix_all.csv](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/sources/prolif-ligand-discrimination-readonly/prolif_ligand_discrimination_matrix_all.csv) | derived local result | 2026-08-26 | 原始 451×65 矩阵与配对频率 | used |
| S5 | 原有配体区分候选 | [../../../experiments/docking-repro/analysis/final-docking/msa-prolif/sources/prolif-ligand-discrimination-readonly/prolif_ligand_discrimination_candidates.csv](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/sources/prolif-ligand-discrimination-readonly/prolif_ligand_discrimination_candidates.csv) | derived local result | 2026-08-26 | 22 个候选及原 tier；本轮未重定义 | used |
| S6 | 模块与 source_csv 审计表 | [../../../experiments/docking-repro/analysis/final-docking/msa-prolif/sources/prolif-ligand-discrimination-readonly/prolif_ligand_discrimination_module_audit.csv](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/sources/prolif-ligand-discrimination-readonly/prolif_ligand_discrimination_module_audit.csv) | primary local provenance | 2026-08-26 | 50 个有效模块、construct 与 source_csv 对应 | used |
| S7 | 五受体 FASTA | [../../../experiments/docking-repro/receptors/final-docking/fasta](../../../experiments/docking-repro/receptors/final-docking/fasta) | primary local input | 2026-08-26 | 全长序列、编号与残基身份 | used |
| S8 | AF3 PDB、A3M 与拓扑输入包 | [../../../experiments/docking-repro/receptors/final-docking](../../../experiments/docking-repro/receptors/final-docking)；[../../../experiments/docking-repro/receptors/final-docking/source-archives/af3-msas-and-templates](../../../experiments/docking-repro/receptors/final-docking/source-archives/af3-msas-and-templates) | primary local input | 2026-08-26 | construct presence、结构映射、A3M 约束、DeepTMHMM/MEMSAT | used |
| S9 | 五受体到 c7xmsA 的既有 Phyre2 比对 | [../../../experiments/docking-repro/receptors/final-docking/alignments/phyre2-c7xmsA](../../../experiments/docking-repro/receptors/final-docking/alignments/phyre2-c7xmsA) | primary local input | 2026-08-26 | c7xmsA fold-anchor 映射；独立于五目标直接 MSA 报告 | used |
| S10 | GprC of the nematode-trapping fungus Arthrobotrys flagrans activates mitochondria and reprograms fungal cells for nematode hunting | [PMC11222155](https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/) | primary research article | 2026-08-26 | GprC/SRBC chimera残基突变、功能与 docking；DOI 10.1038/s41564-024-01731-9 | used |
| S11 | The nematode-trapping fungus Arthrobotrys oligospora detects prey pheromones via G protein-coupled receptors | [PMC11724650](https://pmc.ncbi.nlm.nih.gov/articles/PMC11724650/) | primary research article | 2026-08-26 | Gpr2/Gpr3 的 ascr#3/ascr#7 受体级证据与 Y168 docking；DOI 10.1038/s41564-024-01679-w | used |
| S12 | Two chemoreceptors mediate developmental effects of dauer pheromone in C. elegans | [PMC4448937](https://pmc.ncbi.nlm.nih.gov/articles/PMC4448937/) | primary research article | 2026-08-26 | SRBC-64/66 受体级遗传、救援和异源表达；DOI 10.1126/science.1176331 | used |

## Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|---|---|---|---|---|---|
| GprC N56 是唯一达到既有筛选条件的 ASCR3 区分候选 | S1 | `gprc_wt / ASN56.A / HBAcceptor` 行；`candidate_ligand=ASCR3` | 5/5 可比模型，3/5 偏好 ASCR3，中位差 +0.222 | high | 只针对给定 docking poses；不是因果证据 |
| N56 不是五受体强保守位点 | S2 | `gprc_wt / ASN56.A`；MAFFT/MUSCLE、A3M、US-align 字段 | MAFFT exact/class 2/5；MUSCLE 1/5；A3M exact/class 0.441/0.471 | high | 远缘 MSA 算法敏感；结构对应不等于化学保守 |
| N56A 对已发表的总受体功能没有可检测影响 | S10 | Results, Par18；Fig. 4b；补充突变引物 `N2.53A` | 论文将 N2.53A 明确称为 negative mutation；本项目映射到全长 N56 | high | 未分别测试 ASCR3 与 ASCR18，不能排除选择性效应 |
| Gpr2 W338、Gpr3 W306、GprC W388 是同一 TM6 芳香位置的高可信三受体映射簇 | S2 | 三个 residue 行；topology、MAFFT/MUSCLE、US-align、c7 字段 | 三者同列、同为 TM6；两两结构映射 25/25；均映到 c7xmsA:226 | high | 结论限于三受体；HHalign 未在该具体位点返回全部三者 |
| 三个 W 均为 ASCR18 区分候选 | S1 | `TRP338.A–Hydrophobic`、`TRP306.A–Hydrophobic`、`TRP388.A–Hydrophobic/VdWContact` | 三者在各自受体内均达到原候选门槛，配对差方向为 ASCR18 | high | VdWContact 只代表接触；各受体候选强度不完全相同 |
| 受体内同源 profile 对三个 W 的约束很强 | S2 | 三个 W 行的 `a3m_*` 字段 | A3M exact 为 0.992、0.966、0.971 | high | A3M 分母来自各受体外部同源序列，不属于五目标 n=5 |
| DAF-37 W301 与 SRBC-64 F235 是否属于同一 TM6 簇尚有冲突 | S2 | 任一三受体 W 行的 MAFFT、MUSCLE 与 US-align mapping summaries | MAFFT 提出 W301/F235；MUSCLE 只支持 W301；结构映射给 N299/S228 | high | 不宜报告成五受体共同残基 |
| GprC R174 同时有 ASCR18 接触候选和已发表总功能突变线索 | S1 | `gprc_wt / ARG174.A / VdWContact` | 5/5 支持、4/5 偏向 ASCR18、中位差 +0.333 | high | ProLIF 轨道是 contact-only |
| GprC R 位点的实验功能相关性不能直接升级为 ASCR18 选择性 | S10 | Par19、Fig. 4b、Extended Data Table 3、补充突变引物 | R→A 影响总受体功能；本项目由引物固定为全长 R174 | high | 主文 R6.45 与表中 R6.55 冲突；论文没有双配体突变比较 |
| Gpr3 Y172 是强的受体特异 ASCR18 假说 | S1 | `gpr3_twf154_wt / TYR172.A / Hydrophobic` | 5/5 支持、5/5 偏向 ASCR18、中位差 +0.333 | high | 跨五受体 exact 与 A3M exact 较弱 |
| GprC W155/W157 的 Gpr2/Gpr3 全长对应位点不在当前 deltaN construct | S2 | `gprc_wt / TRP155.A`、`TRP157.A` 的 construct-aware members | Gpr2 W172/W174、Gpr3 F158/W160 标为 `NA_construct_absent`；available=3 | high | 不能用当前 Gpr2/Gpr3 docking 支持这些位置的跨受体接触 |
| SRBC-64 F161 是受体特异、映射较弱的 ASCR18 候选 | S1 | `srbc64_wt / PHE161.A / Hydrophobic` | 5/5 支持、4/5 偏向 ASCR18、中位差 +0.222 | high | MSA 仅覆盖 2 个受体；结构映射不稳定；无残基突变文献 |
| Gpr2 Y168 不适用于当前 deltaN ASCR3/ASCR18 结论 | S2 | `gpr2_twf154_wt / TYR168.A` | 不在 ProLIF 矩阵；construct presence=`NA_construct_absent` | high | 仍可作为全长文献编号参考 |
| Gpr2 Y168 只有 ascr#3/ascr#7 的文献 docking 预测 | S11 | Fig. 3d；main text P16 | 论文预测 Y168 接触 ascr#3 与 ascr#7，没有位点突变或 ASCR18 实验 | high | docking 预测不等于功能验证 |
| Gpr2/Gpr3 与 SRBC-64/66 的既有实验主要是受体级证据 | S11 | Fig. 2a–d、Fig. 3a、P13–P16 | 删除/过表达及内吞支持 Gpr2/Gpr3 对 ascr#3/ascr#7 的作用 | high | 不含 ASCR18 或本项目候选的残基级实验 |
| SRBC-64/66 具有受体级遗传与异源表达依据，但没有 F161 证据 | S12 | Fig. 1–4；P3–P10 | 敲除、救援和 HEK293 共表达支持受体级作用 | high | C3 缺陷较 C6/C9/C7 弱；没有本项目候选的单残基突变 |
| ProLIF 频率与输入来源可回溯到源工作簿 | S3 | `Sources`、`README`、四个 profile sheets | 工作簿记录模块来源、pose 数与 ASCR3/ASCR18 interaction-frequency profiles | high | profile 是 docking-pose 几何统计，不是实验测量 |
| 本轮注释以未经候选阈值截断的完整矩阵为底表 | S4 | 全表 451 个数据行、65 列 | 所有残基–interaction 轨道均保留，不只分析 22 个候选 | high | 原矩阵本身是既有 ProLIF 派生结果 |
| 候选定义沿用原 22 行候选表 | S5 | 全表；`candidate_ligand`、`discriminator_tier` | 本轮没有因 MSA 结果新增、删除或改级候选 | high | MSA 只改变候选的生物学解释与实验优先级 |
| 当前有效比较来自 50 个 receptor–ligand–model 模块 | S6 | 第 2–51 行；construct 与 `source_csv` 字段 | Gpr2/Gpr3 只使用 deltaN；其余三个受体使用 WT | high | 模块审计证明输入口径，不证明科学机制 |
| 全长编号与残基身份以五个 FASTA 为准 | S7 | 五个 FASTA 全序列；对应 residue position | 211 个 ProLIF 位点及结构、MSA、c7 查询残基均回查全长序列 | high | 全长存在不等于当前 deltaN construct 存在 |
| construct presence、A3M 约束、拓扑与结构映射来自既有受体输入包 | S8 | 每个受体 5 个有效 PDB；unpaired A3M；DeepTMHMM `TMRs.gff3`；MEMSAT `query.memsat_svm` | 支持 `NA_construct_absent`、TM 区域、profile 约束与 250 次模型组合结构映射 | high | AF3/PDB 与拓扑均为计算输入；不是实验结构 |
| c7xmsA 映射单独作为 GPCR fold anchor | S9 | 五个 `c7xmsA_*.alig.txt`；query/template 对齐块 | 比对概率 99.82–99.97%，一致性 9–19%；三受体 W 均映到 226 | high | 低序列一致性；不能单独建立五受体同源残基 |
| 注释矩阵保留了原始矩阵与候选定义 | S1 | 全表原始 65 字段及 candidate 字段 | 451 个数据行逐值不变；22 个候选 key 与 tier 不变 | high | 这是文件级回归检查，不是科学有效性验证 |
| 所有 ProLIF residue key 均有映射证据行 | S2 | 全表；`in_prolif_matrix`、validation summary | 覆盖 211 个唯一 ProLIF residue key，并加入 Gpr2 Y168、GprC S44 两个文献位点 | high | 文献补充位点不应误计入 ProLIF 矩阵候选 |

## Audit Notes

- **文件结构：**`residue_mapping_evidence.csv` 为 213 个数据行、72 列，导入范围 A1:BT214；`prolif_ligand_discrimination_matrix_all_msa_annotated.csv` 为 451 个数据行、127 列，导入范围 A1:DW452。
- **原矩阵回归：**原 451×65 的字段名、行顺序与全部值逐项不变；本轮只追加注释列。
- **候选回归：**22 个候选的 receptor、construct、residue、interaction、ligand、tier 与原候选表一致。
- **映射覆盖：**211 个 ProLIF residue key 全部进入映射表；另加入 Gpr2 Y168 与 GprC S44 两个文献补充位点。FASTA、PDB、直接 MSA、过滤 A3M 与 c7 查询位点的残基身份检查均通过。
- **construct-aware 检查：**42 个 construct-aware member 单元被标记为 `NA_construct_absent`；Gpr2 Y168 正确落入这一类。所有 available 分母已按实际存在的 construct 重算，没有把删除区当作 gap 或无接触。
- **结构稳健性：**10 个受体对各自比较 25 个 AF3 模型组合；报告使用 modal mapping 与支持次数，不以单一模型作跨受体结论。
- **文献核对：**三个 DOI/PMC 主文均可访问；GprC 的主文、Extended Data、补充突变构建与引物交叉核对。R6.45/R6.55 冲突未被静默修正。
- **证据审计边界：**最终机制性判断都能回指 S1/S2 的候选或映射行；文献功能结论回指 S10–S12。没有把搜索摘要作为证据，没有把 MSA、ProLIF、US-align 或文献 docking 称为亲和力或因果证明。
- **校验哈希：**`residue_mapping_evidence.csv` SHA256 为 `bacd1cfa8eadf9297442c047fe696140c43b1c7558b906bece247be4ffd0331b`；注释矩阵 SHA256 为 `9dee7ffcde14da20cd17efedc1e2f7729b4ed14dfe5ad3d1accc4a667e2b0bbb`。

## 仍需用户最终判断或补充的材料

1. **术语边界：**是否接受把 Gpr2 W338/Gpr3 W306/GprC W388 命名为“三受体共享的 ASCR18 TM6 芳香核心假说”；本报告不建议把它命名为“五受体保守 ASCR18 残基”。
2. **首轮实验范围：**若重点是“同一受体区分两个配体”，优先 GprC N56A+N60A；若重点是“跨受体共享机制”，优先三受体 W→F。两条路径回答的问题不同。
3. **实验构建信息：**开展突变前，建议补充或确认实际表达 construct 的克隆边界、标签、定位/表达检测方式；当前 `NA_construct_absent` 依据的是有效 docking PDB 中的残基存在性与既有 deltaN 目录。
4. **响应读出：**需由用户决定用 trap formation、转录/报告基因、第二信使、异源表达或其他读出。无论选哪种，都应在相同表达背景、相同剂量设计下分别测 ASCR3 与 ASCR18，并保留总体功能与表达/定位对照。
5. **若已有未公开资料：**受体家族人工同源列表、既有点突变、ASCR3/ASCR18 剂量反应、构建表达/定位结果，会直接改变候选排序，尤其可帮助裁决 DAF-37/SRBC-64 的 TM6 对应冲突。
