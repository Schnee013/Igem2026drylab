# Gpr2/3-ascr#3 reproduction

## 当前状态

- 阶段：C — SwissDock 复现
- 已确认 Gpr2（TGJ68930.1，406 aa）与 Gpr3（TGJ67963.1，401 aa）的 FASTA；两份 ColabFold AlphaFold2-ptm 结果均已验收。
- 已确认配体为 ChemSpider 17226059（ascr#3，C15H26O6）；中性 3D 输入已生成并通过身份、立体化学和坐标验收。
- Gpr2 与 Gpr3 的 AC 原始结果均已保存。Gpr2 的两个作业虽然提交 SMILES 不同，但 SwissDock 最终都按净电荷 0 的中性羧酸参数化；两者 top1 位置不同，暴露出初始构象/采样与排序敏感性。

## 目标

最小化复现 Kuo et al. (2024) 中的两个 WT SwissDock 任务：

1. Gpr2 WT–ascr#3
2. Gpr3 WT–ascr#3

最终获得两个来源清楚、选择依据明确的代表 pose，并完成三维位置审查、二维接触图和接触残基表。这是 Docking Lab 的第一项基础工作。

## 任务范围

本任务限定为 Kuo 2024、WT Gpr2/Gpr3、ascr#3 和 SwissDock 文献复现。其他受体、配体、突变和计算方法由后续独立任务处理。

## 最小化原则

- 只提交两个 WT docking 作业。
- 每个受体只选择一个有明确依据的代表 pose。
- 以复现方法、口袋位置和接触位点为目标；不要求预测分数与论文完全相同。
- 原文缺失的信息记录为未知，不通过复杂推测补齐。
- 只有技术失败才重复提交；不做参数扫描、多 seed 或自动化扩建。
- 使用本科生团队能够解释、复查和展示的方法。

## 阶段 A：文献带读

### 工作

- 阅读 Kuo 2024 中与 Gpr2/Gpr3–ascr#3 docking 直接相关的正文、图注、Methods 和补充材料。
- 提取 receptor、ligand、SwissDock 设置、输出字段、pose/cluster 选择规则和文献接触位点。
- 将原文明确事实与待确认信息分开记录。

### 产出

- `literature/Kuo2024-reading-notes.md`
- 一份可直接指导阶段 B 的最小方法提取表。

### 完成条件

能够回答：使用什么输入、如何提交 SwissDock、如何选择代表 pose、用什么信息判断是否复现。

## 阶段 B：冻结最小复现条件

### 工作

- 确认 Gpr2/Gpr3 WT 结构文件及来源。
- 确认 ascr#3 化学结构、立体化学和来源。
- 确认 SwissDock 当前提交方式。
- 在查看 docking 结果前写下代表 pose 的选择规则。

### 产出

- `inputs/receptors/`：两个 WT receptor 输入。
- `inputs/ligand/`：一个 ascr#3 输入。
- 本文件中的最终输入来源、提交设置和 pose 选择规则。

### 完成条件

两个作业的输入身份清楚，可以独立提交；pose 选择规则已经冻结。

### 已冻结条件（2026-08-11）

- Gpr2 受体：`inputs/receptors/Gpr2_TGJ68930.1_AF2_rank1_unrelaxed.pdb`，全长 406 aa，ColabFold rank 1；保留低置信度 217–316 区段。
- Gpr3 受体：`inputs/receptors/Gpr3_TGJ67963.1_AF2_rank1_unrelaxed.pdb`，全长 401 aa，ColabFold rank 1；保留低置信度 212–264 区段和 C 端尾部。
- 配体来源：ChemSpider ID 17226059，分子式 C15H26O6。
- 配体主文件：`inputs/ligand/ascr3_ChemSpider_17226059_3D.sdf`；保持 ChemSpider 下载的中性形式，以固定 seed 20260811 生成一个 ETKDGv3 构象并用 MMFF94s 最小化。
- SwissDock AC 中性配体输入：`CC@H（原引用 `CCCC/C=C/C(=O` 在源目录未定位）O)O[C@@H]1OC@@H（原引用 `C` 在源目录未定位）C@H（原引用 `O` 在源目录未定位）C[C@H]1O`。AF3 pH 7 去质子化对照以 `extra.rtf` 的 `RESI LIG1 -1.000`、部分电荷总和 −1.0000 和无羧基 O–H 作为拓扑验收条件。
- MOL2 记录：`inputs/ligand/ascr3_ChemSpider_17226059_3D.mol2` 化学身份验收通过，但当前 SwissDock/SwissParam 无法参数化，因此不用于本轮提交。
- 配体验收：5 个手性中心均已定义，烯键为 E，详见 `inputs/ligand/ascr3-preparation-report.json`。
- 服务：旧版 SwissDock 已无法提交，改用当前新版 SwissDock；因此属于方法思路复现，不是 EADock DSS 算法级复现。
- 引擎：Attracting Cavities 2.0；其腔体引导、CHARMM/SwissParam 准备与聚类逻辑在现有选项中更接近旧 EADock DSS，但不是算法级复现。
- 上传格式：受体上传 PDB；配体在网页中粘贴上述 isomeric SMILES。
- Gpr2 搜索空间：以全长 AF2 PDB 的全部原子边界为基础，每侧增加 5 Å；center = `(-11.8, 13.0, 17.0)` Å，size = `(94.3, 81.2, 120.8)` Å。若服务器时间检查拒绝该全蛋白框，再记录技术原因并缩小。
- 若采用 AC：保持新版默认 RIC 1、medium sampling（90°）和 buried cavity prioritization（70）。同一受体–配体的代表 pose 按最低 AC score 选择；SwissParam score 只作为近似结合自由能与 Kuo 数值比较。
- Gpr2 的胞外位置和 Y168、Gpr3 的胞外位置只用于选择后的复现判断，不参与 pose 挑选。
- 若代表 pose 位于低置信度随机卷曲区或受体外表面，保留并报告该结果，不另挑一个更符合预期的 pose。

## 阶段 C：SwissDock 复现

### 工作

- 分别提交 Gpr2 WT–ascr#3 和 Gpr3 WT–ascr#3。
- 保存 SwissDock 原始返回结果和必要的提交记录。
- 按阶段 B 的规则选择每个受体的代表 pose。
- 简单比较文献预测值、复现预测值和 pose 排名。

### 产出

- `runs/gpr2-ascr3/`：Gpr2 原始结果。
- `runs/gpr3-ascr3/`：Gpr3 原始结果。
- `results/gpr2-ascr3/scores/` 和 `results/gpr3-ascr3/scores/`：全部 pose 评分表。
- `results/gpr2-ascr3/poses/` 和 `results/gpr3-ascr3/poses/`：代表 pose 及选择记录。

### 完成条件

两个作业均获得可解析结果，代表 pose 的选择过程能够用原始结果说明。

## 阶段 D：三维可视化与接触图

### 工作

每个受体完成：

- 一张全受体三维位置图；
- 一张结合区域放大图；
- 一张二维接触图；
- 一份简短接触残基表。

重点判断配体是否位于胞外结合区域、是否贴在 TM 束外表面，以及 Gpr2 pose 与文献 Y168 的关系。Gpr3 接触位点按本次代表 pose 如实报告。

### 产出

- `results/gpr2-ascr3/figures/` 和 `results/gpr3-ascr3/figures/`：三维图。
- `results/gpr2-ascr3/contacts/` 和 `results/gpr3-ascr3/contacts/`：二维接触图和残基表。

### 完成条件

两个 WT pose 的空间位置和接触残基均可由图和原始结构复查，并形成一页以内的复现结论。

## 最终最小交付

- 两个 WT SwissDock 原始结果；
- 两个代表 pose；
- 每个受体一张全局图和一张局部图；
- 每个受体一张二维接触图和一份接触残基表；
- 一页以内的复现判断与局限。

## 文献入口

- Kuo et al. (2024), *The nematode-trapping fungus Arthrobotrys oligospora detects prey pheromones via G protein-coupled receptors*：<https://pmc.ncbi.nlm.nih.gov/articles/PMC11724650/>
- [共享证据摘要](../../research/2026-08-11-gpr2-gpr3-gprc-ascaroside-evidence.md)
