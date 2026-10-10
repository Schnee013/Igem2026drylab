# Gpr2/Gpr3 pocket alignment

## 目标

比较 *Arthrobotrys oligospora* TWF154 的 Gpr2/Gpr3 与 GprC、SRBC-64 的跨膜结构和胞外候选口袋，判断 Gpr2/Gpr3 是否支持 GprC/SRBC-64 型 ascaroside 结合口袋。

本任务只建立结构和口袋相似性证据，不证明受体与 ascaroside 直接结合。配体准备、新 docking、分子动力学和突变设计不属于本任务。

## 目录入口

- 根输入清单：`input_manifest.tsv`
- 分析定义：`definitions/tm_ranges.tsv`、`definitions/reference_pocket_residues.tsv`
- 操作指南：`docs/PYMOL_POCKET_COMPARISON.md`
- 汇总结果：`results/alignment_summary.tsv`

## 正式比较组

### 第一层：核心口袋比较

1. TWF154 Gpr2 ↔ GprC
2. TWF154 Gpr2 ↔ SRBC-64
3. TWF154 Gpr3 ↔ GprC
4. TWF154 Gpr3 ↔ SRBC-64

### 第二层：菌株敏感性检查

5. TWF154 Gpr2 ↔ ATCC Gpr2
6. TWF154 Gpr3 ↔ ATCC Gpr3

ATCC 结构只用于判断数据库模型能否代表 TWF154；TWF154 是主分析对象。

## 主模型选择

- TWF154 Gpr2/Gpr3：使用仓库已有 ColabFold AlphaFold2 模型。
- ATCC Gpr2/Gpr3、GprC：使用对应 AlphaFold DB 模型。
- SRBC-64：使用与 Hu 实验 N2 背景一致的 G5ECV4/NP_740807.1/Y39G10AR.22 序列和 AFDB v6 模型；Hu2024 未报告历史模型 accession，此差距保留在来源记录中。
- 现有 TWF154 AlphaFold 3 模型不进入主流程，也不重新运行 AF3 Server。

选择 AF2 作为主模型，是为了使目标受体与主要参考受体尽量使用同代结构预测方法。不得根据最终口袋是否“符合预期”挑选结构模型。

## 已有输入

权威输入采用统一命名：`来源或菌株_受体_accession.fasta` 与 `来源或菌株_受体_accession_模型版本.pdb`。后续程序只读取 `input_manifest.tsv` 列出的六对文件。

### TWF154 Gpr2

- 序列：`../swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/Gpr2_TGJ68930.1.fasta`
- AF2：`../swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/Gpr2_TGJ68930.1_AF2_rank1_unrelaxed.pdb`
- AF3 备用集合：`../swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/fold_gpr2_tgj68930_1_af3.zip`

### TWF154 Gpr3

- 序列：`../swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/Gpr3_TGJ67963.1.fasta`
- AF2：`../swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/Gpr3_TGJ67963.1_AF2_rank1_unrelaxed.pdb`
- AF3 备用集合：`../swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/fold_gpr3_tgj67963_1_af3.zip`

### ATCC Gpr2/Gpr3 与 GprC

现有原始结构位于 Drylab：

- `/Users/yangruoxi/Igem2026drylab/experiments/docking/receptors/Gpr2_G1X9E2.pdb`
- `/Users/yangruoxi/Igem2026drylab/experiments/docking/receptors/Gpr3_G1XJN1.pdb`
- `/Users/yangruoxi/Igem2026drylab/experiments/docking/receptors/GprC_A0A437AGY2.pdb`

本任务以本节列出的三份原始 AFDB PDB 为权威输入，并核对 accession、序列长度、来源和文件校验值。`prepared/receptors/*_tm.pdb` 属于其原任务的衍生文件。

### SRBC-64

本任务冻结 N2 标准 SRBC-64：G5ECV4/NP_740807.1/Y39G10AR.22，289 aa；主结构为 `AF-G5ECV4-F1-model_v6.pdb`。Hu2024 未给出其历史 AFDB accession 或版本，因此该输入用于身份匹配的 N2 口袋参照，不能标成 Hu 原始坐标文件。

## 配体处理

结构 alignment 本身不需要配体。本仓库虽已有 ascr#3/ascr#18 及旧 docking pose，但这些文件不复制到本任务，也不参与第一轮口袋判断。

参考口袋首先由 Hu2024 报告的 GprC/SRBC-64 跨膜区域、Ballesteros–Weinstein 位置和接触残基定义。alignment 完成后，旧 docking pose 只能在独立任务中作为交叉检查，不能反向决定本任务的口袋位置。

## 五步流程

### 第1步：冻结和收集受体输入

工作：

1. 收集六个受体的序列与主结构模型。
2. 固定 N2 SRBC-64 的 accession 和 AlphaFold DB 模型，并记录 Hu2024 历史模型的来源差距。
3. 为每个输入记录物种、菌株、accession、序列长度、结构来源、文件路径或 URL、获取日期和 SHA256。
4. 将用于分析的原始副本保存于 `inputs/`，原文件保持不变。

产出：

- `inputs/sequences/`
- `inputs/structures/`
- `input_manifest.tsv`

完成条件：六个选定受体身份唯一、序列与结构一致、来源可追溯，未解决的来源差距已记录。

### 第2步：确定 TM 范围和参考口袋

工作：

1. **2.1** 为六个正式结构输入以及 DAF-37/DAF-38 补充参照分别运行 DeepTMHMM。
2. **2.2** 将八次 DeepTMHMM 1.0.57 的完整原始结果按受体保存于 `topology/raw/`。
3. **2.3** 从各自的 `TMRs.gff3` 提取并冻结 TM1–TM7、膜内外方向和信号肽范围，写入 `definitions/tm_ranges.tsv`。ATCC 与 TWF154 保留各自的直接预测结果。
4. **2.4** 将目视质控合并到第 3 步首次叠合：确认七条 TM 大致构成连续螺旋束，并确认胞外方向和 ECL2。该检查不生成独立分析文件，也不覆盖 2.3 的原始预测边界。
5. **2.5** 将 Hu2024 的 GprC/SRBC-64 参考口袋位置映射为绝对残基号，并为每个位点记录已验证、暂定或未解决状态。

DAF-37/DAF-38 用于补充比较七跨膜拓扑；正式 alignment 仍采用“正式比较组”中的六组。

产出：

- `topology/raw/`
- `definitions/tm_ranges.tsv`
- `definitions/reference_pocket_residues.tsv`

完成条件：八个受体均有可追溯的 DeepTMHMM 原始结果与 TM1–TM7 范围；GprC/SRBC-64 参考口袋的绝对编号及未解决项均有明确记录。结构连续性在首次正式叠合时完成目视质控。

### 第3步：执行六组 TM-core alignment

每组使用同一工具和同一规则：

1. 只用预先定义的七条 TM 的 Cα 原子进行结构拟合。
2. 保存旋转和平移变换。
3. 将变换应用到完整受体，用于观察 ECL2 和胞外口袋。
4. 记录 TM-score、TM-core Cα RMSD 和对齐残基数。

不另外计算全蛋白 RMSD，也不使用长胞内环或低置信尾部优化拟合。不得根据候选口袋残基重新调整结构，使口袋被强制重合。

产出：

- `alignments/` 下六组叠合结构和原始输出
- `results/alignment_summary.tsv`
- 可复现的 alignment 脚本或命令记录

完成条件：六组均使用相同流程完成，叠合结构、原始输出和汇总指标一致可复查。

### 第4步：最小口袋分析

每组只回答以下问题：

1. 候选区域是否位于胞外侧七条 TM 束内部？
2. 是否主要由 TM2、TM3、TM5、TM6 和 TM7 包围？
3. GprC/SRBC-64 参考口袋投影到 Gpr2/Gpr3 后，是否存在明显封闭、偏移或空间冲突？
4. 对应空间位置的残基化学类型是否大体相似：极性、带电、芳香或疏水？
5. Gpr2 的 7 个、Gpr3 的 6 个 ATCC–TWF154 差异位点位于口袋、靠近口袋还是远离口袋？
6. 关键判断是否落在 AlphaFold 明显低置信区域？

本轮不运行 fpocket、POVME、电势计算、新 docking 或配体转移，也不将单一侧链旋转角解释为可靠差异。

产出：

- `pocket_mapping.tsv`
- `strain_variant_mapping.tsv`
- Gpr2 参考叠合图
- Gpr3 参考叠合图
- Gpr2 菌株叠合图
- Gpr3 菌株叠合图

完成条件：每个目标受体都有口袋位置、参与 TM、残基化学、菌株差异和结构置信度五方面的记录。

### 第5步：综合判断

分别回答：

1. TWF154 Gpr2 是否支持 GprC/SRBC-64 型胞外口袋？
2. TWF154 Gpr3 是否支持？
3. Gpr2 与 Gpr3 的结果是否一致？
4. ATCC 模型是否可代表 TWF154 的候选口袋？
5. 哪些结论受 AlphaFold 局部置信度限制？

每个目标受体只使用以下结论等级：

- 支持；
- 部分支持；
- 不支持；
- 结构置信度不足，无法判断。

产出：

- 一页左右的 `alignment_conclusion.md`

## AF3 备用检查触发条件

AF3 不属于主流程。只有出现以下情况时，才使用现有 TWF154 AF3 model 0–4 检查口袋位置是否稳定：

- AF2 候选口袋局部置信度明显不足；
- 结论依赖低置信 loop 或单一侧链方向；
- ATCC 与 TWF154 的结果发生无法由序列差异解释的冲突；
- 主比较只能得到临界或相互矛盾的结论。

启用 AF3 时，不新增正式比较组，不挑选最符合预期的模型，只报告五个模型是否保留共同的口袋位置。

## 最小交付

1. 一份可追溯的输入清单；
2. 六组 TM-core alignment 结构和原始输出；
3. 一份 alignment 指标汇总；
4. 两份口袋和菌株差异残基表；
5. 四张结构图；
6. 一页左右的综合结论。

## 明确排除

- 配体重新准备；
- AF3 Server 重跑；
- 新 docking 或旧 pose 重选；
- SRBC-66 或其他受体扩展；
- 多种 alignment 软件交叉扫描；
- 复杂口袋体积、电势或黑箱相似度评分；
- 分子动力学；
- 突变设计和功能结论。

## 文献入口

- Hu et al. (2024), *GprC of the nematode-trapping fungus Arthrobotrys flagrans activates mitochondria and reprograms fungal cells for nematode hunting*: <https://doi.org/10.1038/s41564-024-01731-9>
- Kuo et al. (2024), *The nematode-trapping fungus Arthrobotrys oligospora detects prey pheromones via G protein-coupled receptors*: <https://doi.org/10.1038/s41564-024-01679-w>
- 本仓库 Hu2024 方法记录：`../research/2026-08-13-hu2024-minimal-vina-method.md`
