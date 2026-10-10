# Vina 对接总体最小路线

> 状态：当前执行入口（可随项目进展完善）
>
> 适用对象：没有分子对接和计算生物学基础的本科生团队
>
> 核心原则：每一阶段先完成最小验证，通过后再增加计算量。

## 目标

使用 Hu et al. (2024) 的 GprC–ascr#18 对接方法作为基准，以尽可能少的计算完成：

1. Gpr2/Gpr3 WT 与 ascr#3、ascr#18 的对接和关键残基选点；
2. 少量差异残基的单点突变对接；
3. 突变体对两种配体的相对选择性排序。

## 总体路线

```text
第 0 步：Hu2024 方法调研与一次 GprC–ascr#18 验证
                         ↓
第 1 步：4 个 WT 对接与二维接触分析选点
                         ↓
第 2 步：最多 4 个 Ala 突变体的双配体对接
                         ↓
第 3 步：简单选择性排序
                         ↓
第 4 步：最多 2 个最终候选的重复复核
```

首轮预计规模：

- GprC 方法验证：1 个 Vina 任务；
- WT 选点：2 个受体 × 2 个配体，共 4 个 Vina 任务；
- 突变筛选：最多 4 个突变体 × 2 个配体，共 8 个 Vina 任务；
- AF3：最多 4 个单点突变体；
- 首轮合计：最多 13 个 Vina 任务和 4 个 AF3 任务。

饱和突变和多 seed 计算由前一阶段结果触发，不列入首轮默认任务。

## 第 0 步：Hu2024 方法基准

### 0A. 调研原文方法

从 Hu2024 正文、Methods、Reporting Summary、图注和扩展数据中提取并逐项记录：

- GprC WT 结构来源和版本；
- 受体是否截取跨膜区，以及 box 中心所用结构；
- ascr#18 的构建、几何优化、质子化和电荷；
- 受体和配体 PDBQT 的制备方法；
- Vina 版本、box、spacing、exhaustiveness 和其他运行参数；
- pose 生成、筛选和分析规则；
- 文献报告的分数、口袋位置和关键接触残基；
- 原文未明确、需要本项目自行决定的参数。

文献值与项目选择必须分栏记录，避免把仓库中的既有实现误写成原文方法。

### 0B. 审查 Drylab 可复用内容

将 `/Users/yangruoxi/Igem2026drylab` 中与 Vina 有关的文件分类为：

1. 可直接复用；
2. 需要少量适配；
3. 仅作方法参考；
4. 当前缺失，需要新增。

优先审查：

- GprC/ascr#18 输入及来源记录；
- WT Vina 对接脚本；
- ProLIF IFP 和二维接触图脚本；
- AF3 结果处理、CIF/PDB 转换和 TM 提取脚本；
- 突变身份核验及突变体到 WT 坐标框的结构对齐；
- PDBQT 制备、环境检查和结果记录方法。

当前项目的新候选必须来自本路线产生的 WT 接触分析和突变结果。

### 0C. 冻结最小方法

0C 的执行配置为 [`config/minimal_vina.yaml`](config/minimal_vina.yaml)。下表是团队实际执行时使用的一页方法摘要。

| 项目 | 冻结选择 | 来源或理由 |
|---|---|---|
| 任务范围 | 先做 GprC–ascr#18 验证；通过后做 Gpr2/Gpr3 × ascr#3/ascr#18 四组 WT | 最小路线 |
| 原始受体 | AlphaFold DB：GprC `A0A437AGY2`、Gpr2 `G1X9E2`、Gpr3 `G1XJN1`；复制后核对配置中的 SHA256 | Hu2024 + 0B 输入审查 |
| 受体范围 | GprC `10–197, 369–432`；Gpr2 `25–211, 322–382`；Gpr3 `12–201, 290–347`；均保留 ECL2 和 ICL3 两端 5 aa | 旧仓库的 UniProt/DeepTMHMM 注释；项目选择 |
| 受体准备 | chain A 标准残基；ADFR 加氢并清理水、非标准残基、孤对电子和非极性氢 | Hu2024 + ADFR 方法 |
| 配体状态 | ascr#3、ascr#18 均使用中性羧酸形式；每种配体只优化和制备一次，随后供全部 WT/突变体复用 | 原文未报告质子化；采用与原始 SDF 和旧复现一致的单一状态以控制任务量 |
| 配体优化与准备 | Orca 5.0.1，B3LYP/def2-TZVP，`Opt TightOpt`，电荷 0、单重态；ADFR 加氢、Gasteiger 电荷和重原子单键柔性 | Hu2024；DOF 必须通过化学键和 PDBQT 一致性检查 |
| 软件 | Python 3.11、Vina 1.2.7、ADFRsuite 1.0 rc1（含 ADFR v1.2）、Open Babel 3.1.1、Orca 5.0.1；运行前记录实际版本 | Python 3.11 沿用旧仓库已验证环境；Vina 使用当前官方版本；Orca 与论文一致 |
| 搜索框 | 截取后 WT 受体 PDB 的全原子质量加权质心；`40 × 40 × 40 Å`；spacing `0.1 Å`；offset 为 0 | Hu2024 的受体质心和搜索参数；项目明确原子集合 |
| 突变体搜索框 | 突变体对齐到对应 WT 后，直接复用 WT 已保存的数值中心和 box | 保证 WT/突变体可比 |
| Vina 参数 | rigid receptor；Vina scoring；`exhaustiveness=200`、seed `44`、CPU `4`、`num_modes=5`、`energy_range=5 kcal/mol`、`min_rmsd=1 Å`、`max_evals=0` | 前两项来自 Hu2024；其余为项目冻结值；5 个 mode 对应 top-5 分析 |
| 接触分析 | 分析 top-5；同一残基每个 pose 最多计一次；至少 `3/5` 为高频；一侧 `≥3/5` 且另一侧 `≤1/5` 才记为差异 | 避免旧脚本重复累计相互作用类型，并减少边缘候选 |
| 选点 | shared 高频残基保留；D2.50、S2.41 首轮保护；R-motif 需核对侧链方向和绝对残基号；每个受体最多 2 个差异位点 | Hu2024 结构/功能证据 + 首轮计算上限 |
| 人工 pose 验收 | 代表 pose 位于胞外正构口袋，主要由 TM2/3/5/6/7 包围；记录 ECL2；胞内侧、膜暴露沟槽或 TM1/TM4 主导的 pose 判为可疑 | Hu2024 跨受体口袋比较 |
| GprC 验证 | 必须有可追溯运行记录和结构合理的 top poses；`−8.29 kcal/mol` 只作分数参照 | Hu2024 Extended Data Table 2 |
| 分数用途 | 只做同协议相对排序；直接结合、亲和力和功能结论使用独立证据 | 科学解释边界 |

接触分组固定为：

- `shared`：两种配体均为 `≥3/5`；
- `ascr3_only`：ascr#3 为 `≥3/5`，ascr#18 为 `≤1/5`；
- `ascr18_only`：ascr#18 为 `≥3/5`，ascr#3 为 `≤1/5`；
- `ambiguous`：其余情况，首轮不进入突变候选。

当前计算机尚未发现可调用的 Vina、Open Babel、ADFR 或 Orca。配置状态为“方法已冻结”；执行资格需要通过工具版本、输入哈希、受体截取结果和配体 PDBQT 柔性检查。

软件版本查验来源：[AutoDock Vina 官方 releases](https://github.com/ccsb-scripps/AutoDock-Vina/releases/tag/v1.2.7)、[Vina 参数文档](https://autodock-vina.readthedocs.io/en/stable/vina.html)、[ADFRsuite 官方下载说明](https://ccsb.scripps.edu/adcp/downloads/)；查验日期为 2026-08-14。

下一阶段门：方法来源清楚，输入可追溯，团队成员能够解释每个关键参数。

### 0D. 运行一个验证任务

#### 0D-1 输入迁移与工具 preflight（2026-08-14）

| 检查项 | 结果 |
|---|---|
| GprC 原始受体 | 已迁入 `inputs/receptors/GprC_A0A437AGY2.pdb`；355,022 bytes；538 residues；chain A；SHA256 与配置一致 |
| ascr#18 原始配体 | 已迁入 `inputs/ligands/ascr18_CID71514784.sdf`；7,434 bytes；PubChem CID 71514784；SHA256 与配置一致 |
| 机器 | Apple Silicon `arm64`；macOS 26.6.1；Homebrew 可用 |
| 外部程序 | Vina、Open Babel、ADFR `prepare_receptor`/`prepare_ligand`、Orca 均未安装或未进入 PATH |
| Python | 系统 Python 3.14.4；NumPy 可用；PyYAML、Biopython、RDKit、pandas、MDAnalysis、ProLIF、pytest 缺失 |

输入迁移已验收。执行门仍等待独立 Python 3.11 环境、外部程序和 Python 依赖安装完成并通过版本检查；本步骤未生成 prepared 文件。

#### 0D-2 既有 Miniconda `docking` 环境复用审查（2026-08-14）

| 检查项 | 结果 | 判断 |
|---|---|---|
| 环境位置 | `/Users/yangruoxi/miniconda3/envs/docking` | 可直接通过 `conda run -n docking ...` 调用 |
| Python | 3.11.15，原生 `arm64` | 符合 0C |
| Python 核心包 | PyYAML 6.0.3、NumPy 1.26.4、Biopython 1.87、RDKit 2025.09.5、pandas 3.0.2、MDAnalysis 2.10.0、ProLIF 2.1.0 均可导入 | 可复用；pytest 尚缺 |
| Vina | conda 元数据为 1.2.6，实际 CLI 报告 1.2.5；支持 spacing、seed、CPU、exhaustiveness、num_modes、energy_range、min_rmsd 和 max_evals | 功能可用；版本身份需按实际 CLI 记录，尚未满足 0C 的 1.2.7 |
| Open Babel | conda 元数据为 3.1.1，实际 CLI 报告 3.1.0 | 功能可用；版本身份需按实际 CLI 记录 |
| Meeko | 0.7.1；`mk_prepare_receptor.py` 和 `mk_prepare_ligand.py` 均可启动 | 可作为本机现代 PDBQT 制备工具，但属于对 Hu2024 ADFR 方法的显式替代 |
| ADFR / Orca | `prepare_receptor`、`prepare_ligand`、`orca` 均缺失 | 当前 0C 准备协议尚不能执行 |

现有 `docking` 环境可作为本项目的 Python、Vina、Open Babel、Meeko 和 ProLIF 基础环境，无需重建。它尚未取得 0D 执行资格，原因是准备工具路线未定：

1. **本机最小路线（推荐）**：使用现有 Meeko 0.7.1 替代 ADFR；使用现有中性 PubChem 3D SDF，并以 RDKit MMFF 做轻量几何检查/优化，随后用 GprC–ascr#18 验证决定是否接受这两项方法偏差；
2. **文献准备路线**：在 Linux 环境运行 ADFR，并由团队成员从 ORCA 官方论坛取得 Orca 5.0.1 安装包，再执行 B3LYP/def2-TZVP 优化。

这里需要项目选择。ADFR 官方文档明确提示其 macOS 版本在 Catalina 已无法工作，因此本机 macOS 26.6.1 不视为受支持环境；这是根据官方兼容性说明作出的保守推断。ORCA 官方安装说明要求注册后下载。来源：[Vina/Meeko requirements](https://github.com/ccsb-scripps/AutoDock-Vina/blob/develop/docs/source/docking_requirements.rst)、[ADFRsuite downloads](https://ccsb.scripps.edu/adcp/downloads/)、[ORCA installation](https://www.faccts.de/docs/orca/6.1/manual/contents/quickstartguide/installation.html)。

本次审查未修改 `docking` 环境中的任何包。

只运行 GprC WT–ascr#18：

1. 使用已验收的 GprC/ascr#18 原始输入，按 0C 配置重新制备；
2. 运行一次 Vina；
3. 检查程序是否正常结束；
4. 检查代表 pose 是否位于文献描述的胞外侧跨膜口袋；
5. 比较文献分数和关键接触区域；
6. 保存输入、参数、命令、日志、pose 和简短结论。

下一阶段门：结果同时具有可追溯运行记录和结构上合理的 pose。分数接近文献只能作为辅助判断。

## 第 1 步：WT 对接与选点

只运行以下 4 组：

| 受体 | ascr#3 | ascr#18 |
|---|---:|---:|
| Gpr2 WT | 1 次 | 1 次 |
| Gpr3 WT | 1 次 | 1 次 |

对每个受体完成 ProLIF 二维接触分析，并输出：

- 两种配体的共同接触残基；
- ascr#3 的差异接触残基；
- ascr#18 的差异接触残基；
- 各残基的接触类型、出现频率和代表 pose；
- 建议进入 Ala 突变的位点。

选点上限：每个受体最多 2 个差异残基，两个受体合计最多 4 个。共同高频接触残基默认保留，以降低同时破坏两种配体结合的风险。

下一阶段门：候选位点来自可复查的二维接触证据，并在查看突变结果前冻结。

## 第 2 步：最小 Ala 突变筛选

首轮只做单点 Ala 突变，最多 4 个突变体：

1. 生成突变体 FASTA；
2. 提交 AF3，并选择排名最高且结构可信的模型；
3. 核对序列中只有目标位点发生变化；
4. 提取与 WT 相同的受体区域；
5. 将突变体刚体对齐到对应 WT docking frame；
6. 制备 PDBQT；
7. 使用与 WT 相同的 box 和 Vina 参数分别对接 ascr#3、ascr#18；
8. 保存分数、pose、日志和输入身份。

结构对齐是必需步骤：突变体必须进入对应 WT 的坐标框后才能使用同一搜索框比较。

### 饱和突变触发条件

只有当某个 Ala 突变同时满足以下条件，才考虑对该位点做饱和突变：

- 两种配体的变化存在清楚差异；
- 目标配体仍有结构合理的 pose；
- 结果方向能由接触变化解释；
- 团队确认额外 AF3 和 Vina 计算值得投入。

如果触发，优先只选择 1 个最佳位点设计下一轮。

## 第 3 步：简单选择性排序

对每个突变体计算：

```text
ΔΔG18 = ΔG(mutant, ascr18) - ΔG(WT, ascr18)
ΔΔG3  = ΔG(mutant, ascr3)  - ΔG(WT, ascr3)
ΔΔGselectivity = ΔΔG18 - ΔΔG3
```

输出两个榜单：

- 更偏向 ascr#18 的突变体；
- 更偏向 ascr#3 的突变体。

排序时同时检查：

- 目标配体是否保留合理 pose；
- 非目标配体是否相对减弱；
- WT 与突变体 pose 是否位于可比口袋；
- 接触变化能否解释分数变化。

Vina 分数只用于同一协议内的相对排序。直接结合、真实亲和力和功能效果需要独立证据。

## 第 4 步：最终候选复核

首轮排序后最多选择 2 个突变体：

1. 使用额外 seed 重跑突变体；
2. 使用同一 seed 重跑对应 WT；
3. 检查选择性方向是否一致；
4. 生成 WT/突变体二维接触对比图；
5. 用 PyMOL 人工检查一次口袋和 pose。

复核完成后，再决定是否需要饱和突变或更多重复。

## 后续对话执行规则

后续对话默认从本文件确定当前阶段，并遵循以下顺序：

1. 先报告当前阶段已有输入、证据和缺口；
2. 每次只推进一个最小步骤；
3. 运行计算、提交 AF3 或扩大候选数前先说明任务数和预期产物；
4. 每一阶段通过后再进入下一阶段；
5. 新结果只更新对应阶段，不提前扩展后续工作；
6. 所有运行保存输入、参数、命令、日志、结果和简短结论。

## 当前状态

- 当前阶段：第 0 步，0D-2；
- 0A 文献调研：已记录 Hu2024 方法及 SRBC-64/DAF-37 跨受体结构、motif 和关键残基分析于 [`research/2026-08-13-hu2024-minimal-vina-method.md`](2026-08-13-hu2024-minimal-vina-method.md)；
- 0B Drylab 复用审查：0B-1 方法级取舍、0B-2 文件级迁移审查和 0B-3 缺失功能审查均已记录于 [`research/2026-08-13-drylab-minimal-reuse-audit.md`](2026-08-13-drylab-minimal-reuse-audit.md)；
- 0C 最小方法：已冻结于本文件和 [`config/minimal_vina.yaml`](config/minimal_vina.yaml)；
- 0D-1：GprC/ascr#18 原始输入已迁移并通过哈希核验；工具 preflight 已记录，执行门等待环境安装；
- 0D-2：既有 Miniconda `docking` 环境可部分复用；环境未被修改，ADFR/Orca 准备路线等待项目选择；
- 下一项工作：确认采用本机 Meeko/RDKit 最小路线，或另用 Linux ADFR + Orca 文献准备路线；
- 尚未开始新的 Vina 运行；
- 本文件可在后续获得新证据或批准新计算后更新。
