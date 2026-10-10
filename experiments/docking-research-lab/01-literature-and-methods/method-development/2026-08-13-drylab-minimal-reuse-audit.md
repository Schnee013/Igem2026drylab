# Drylab 最小复用审查（0B）

> 用途：从 `/Users/yangruoxi/Igem2026drylab` 提取适合当前简化 Vina 路线的方法与文件。
> 当前路线来源：本项目的 `MINIMAL_VINA_ROADMAP.md` 和 Hu2024 方法记录。
> 原则：WT 二维接触分析负责产生突变候选；首轮只处理少量显式单点突变。
> 状态：0B-1 方法级取舍、0B-2 文件迁移审查和 0B-3 缺失功能审查均已记录。尚未迁移文件或运行计算。

## 0B-1 审查问题

旧仓库的 docking-repro 主线同时包含 WT 复现、预设残基丙氨酸扫描、饱和扫描、162 个突变体批量运行、frame repair、geometry gate 和双通道面板排名。当前项目只需要支持以下证据链：

```text
WT 双配体对接
  → WT 二维接触分析
  → 共同/差异残基
  → 少量显式 Ala 突变（必要时再对一个位点做饱和突变）
  → AF3 突变体结构
  → 同协议双配体对接
  → WT 归一化选择性排序
```

因此，本步骤按“保留、改造、弃用、延后”判断旧仓库的方法，而不沿用旧候选或旧批量任务规模。

## 方法级取舍表

| 方法模块 | 旧仓库实现与证据 | 决定 | 当前项目中的最小用法 |
|---|---|---|---|
| 原始受体和配体身份记录 | AlphaFold DB 受体、PubChem SDF 及化学标识符已经整理 | **保留** | 作为输入来源线索；0B-2 核对具体文件、来源记录和 SHA256 |
| 基于注释的受体区域提取 | `extract_tm_domain_by_annotation` 按 TM 注释保留 TM1–7、ECL1–3，并截去 ICL3 主体 | **改造** | 使用 0C 冻结的统一残基范围；保留 ECL2；每个受体的 WT 与突变体使用相同规则 |
| 基于 pLDDT 连续高分区自动猜测 TM 范围 | `extract_tm_domain` 会按阈值和连续片段自动确定首尾边界，失败时可能退回全长 | **弃用** | 受体范围必须显式、可核对，不能由本次运行自动变化 |
| ADFR 受体制备 | `prepare_receptor_adfr` 可清理受体并调用 `prepare_receptor` 生成 PDBQT | **改造** | 保留 ADFR 转换和原子数核对；删除旧目录复用和“已存在即跳过”假设 |
| Orca + ADFR 配体制备 | B3LYP/def2-TZVP 优化、ADFR `prepare_ligand`、Gasteiger/可旋转键准备与 Hu2024 路线一致 | **改造** | 保留化学结构、收敛、净电荷、原子数和 DOF 核对；同一 prepared ligand 用于 WT 和突变体 |
| 按 11 DOF 上限自动冻结末端扭转键 | `freeze_terminal_torsions` 把论文四种配体的 7–11 DOF 汇总范围当作单个配体上限 | **弃用** | 先记录 ADFR 实际生成的可旋转键，再根据 ascr#3/ascr#18 化学结构人工核对；不为追求范围自动改写 PDBQT |
| Hu2024 单阶段 Vina | `dock_pair_singlestage` 支持 40 Å、0.1 Å、`exhaustiveness=200`，并保存命令、stdout、stderr 和 poses | **改造** | 保留单次运行核心和运行记录；参数统一从一份小配置读取 |
| 两阶段 Vina | 先 40 Å 粗搜，再围绕最佳 pose 使用 20 Å 精修 | **弃用** | 当前文献基准和后续比较统一使用单阶段方法 |
| 受体特定手动 box、偏移和缩小 box | 旧配置为 Gpr2/Gpr3 加入手动中心、膜法线偏移或 20 Å box | **弃用** | WT 与突变体采用同一套已冻结 box 规则；口袋合理性通过 pose 检查判断 |
| 受体质心 box 计算 | `compute_box_center_of_mass` 支持全原子质量加权质心，也支持仅使用 TM 螺旋原子 | **改造** | 0C 只选择一种原子集合并固定；所有可比较任务复用同一规则 |
| WT 矩阵运行 | `run_wt_singlestage.py` 能按指定受体和配体运行单阶段 Vina | **改造** | 只支持当前任务明确列出的 receptor–ligand 对；移除 ascr#1/ascr#7、旧验证分支和受体特定 box 逻辑 |
| ProLIF 相互作用识别 | `run_ifp_analysis.py` 已包含 PDBQT→SDF、配体价态修复、受体电荷处理及 ProLIF 指纹 | **改造** | 分析每组前 5 个 pose，保留残基、相互作用类型和逐 pose 证据 |
| 残基接触频率 | 旧实现把同一残基的多种 interaction count 相加，高频值可能大于实际 pose 数 | **改造** | 每个 pose 中某残基只计一次“出现”；频率为出现 pose 数除以实际分析 pose 数 |
| 共同/差异残基判断 | 旧实现已计算 shared、ascr#18-only、ascr#3-only，但把 ascr#18-only 硬编码为保护、ascr#3-only 硬编码为突变候选 | **改造** | 对称输出“共同、ascr#3差异、ascr#18差异”；候选方向由目标选择性决定，共同高频接触默认保留 |
| ProLIF LigNetwork 二维图 | `plot_ifp_2d_diagram.py` 可生成交互式 HTML | **延后** | 先用接触 CSV 完成选点；需要汇报或复核最终候选时再生成二维图 |
| 用预设口袋残基做全量丙氨酸扫描以发现热点 | `config.yaml` 的 `scan_residues` 来自文献位点和旧 PLIP/IFP 并集，`run_mutagenesis_alanine.py` 批量扫描这些位点 | **弃用** | 突变候选只来自本项目新生成的 WT 双配体共同/差异接触表 |
| 对已冻结候选做显式 Ala 突变 | `make_alanine_scan_mutations` 能核对 WT 身份并把指定残基变为 Ala | **改造** | 输入改为本项目冻结的少量显式候选列表，不再读取旧 `scan_residues` |
| 饱和突变枚举 | `make_saturation_scan_mutations` 能在指定位点枚举氨基酸，但旧 runner 硬编码 Channel A 位点并默认批量展开 | **延后** | Ala 结果触发后，最多选择一个位点；届时只保留显式位点枚举函数 |
| 突变体 FASTA 生成 | 旧代码使用全长受体序列生成 Ala 或饱和突变 FASTA | **改造** | 只接受显式突变标签，核对 WT 残基、序列长度及除目标位点外的序列一致性 |
| AF3 模型选择、CIF→PDB、统一受体范围 | 旧代码可按 `ranking_score` 选模型并进行格式转换和受体区域提取 | **改造** | 只处理冻结的少量突变体；记录所选模型和置信度，并使用与 WT 相同的受体范围 |
| 突变身份核验和 mutant→WT 刚体对齐 | `frame_alignment.py` 可核对唯一目标突变、排除额外序列差异，并用固定七 TM Cα 做 Kabsch 对齐 | **保留** | 作为突变体进入 Vina 前的必需检查；核验或对齐失败即停止该突变体 |
| 162/328 任务批量 runner、frame manifest、geometry gate 和终态聚合 | 这些模块服务于旧仓库的大规模修复、远程运行和特定 pose 分布门 | **弃用** | 当前项目只运行少量显式任务，保存最小输入、参数、命令、日志和结果即可 |
| 旧 ratio/channel/面板排名 | `ratio_ranking.py` 使用突变体原始 `ΔG18−ΔG3`、Channel A/B、跨受体配对和七成员面板规则 | **弃用** | 不迁移旧通道分类、阈值、配对和面板规则 |
| WT 归一化选择性公式 | `mutagenesis.py` 已实现 `ΔΔG18−ΔΔG3` | **保留公式** | 用当前 WT 和突变体同协议结果计算；0B-3 决定用小脚本还是结果表公式实现 |
| 多 seed 复核 | 旧仓库支持多 seed，但默认规模和旧候选绑定 | **延后** | 首轮排序后最多复核两个最终候选，并同时重跑对应 WT |
| 多突变体/双突变 cycle | 旧仓库存在多突变 schema 和 WT/A/B/AB cycle | **弃用** | 当前路线只处理单点突变 |

## 取舍后的最小方法链

旧仓库可提供的核心能力被压缩为六个模块：

1. 受体和配体输入制备；
2. 单阶段 Vina 运行及最小运行记录；
3. WT 前 5 个 pose 的 ProLIF 接触分析；
4. 从新接触表生成少量显式突变；
5. AF3 结构处理、突变身份核验和 mutant→WT 对齐；
6. WT 归一化选择性计算。

其中第 3 项产生候选，第 4 项只执行已经冻结的候选。丙氨酸突变是候选验证方式，饱和突变是条件触发的后续扩展。

## 必须保留的科学检查

- WT 和突变体采用相同的受体范围、配体 PDBQT、box 和 Vina 参数；
- WT 接触分析使用前 5 个 pose，并保留逐 pose 证据；
- 共同高频接触残基默认保留；候选来自两配体差异接触；
- D2.50、S2.41 等保守结构或信号位点默认不进入首轮突变；R-motif 需先核对侧链方向和绝对残基号；
- 代表 pose 应位于胞外正构口袋，主要由 TM2、TM3、TM5、TM6、TM7 包围，并记录 ECL2 是否参与；
- Vina 分数只用于同一协议内的相对排序。

## 0B-2 文件级迁移审查

### 源快照和迁移方式

- Drylab 源版本：Git commit `329aee077e5de74287bf9c442aa645ecf07152af`；下列 docking 代码、原始输入、测试和环境文件相对该 commit 无本地修改。
- 当前项目尚无可执行 docking 目录。下文的目标路径是 0B-2 的迁移规划，未创建目录或文件。
- 原始输入按文件复制；代码按函数提取并精简。旧脚本中的项目路径、批量循环、旧候选、旧阈值和旧报告逻辑不随函数迁入。

### 可直接迁移的原始输入

| Drylab 源文件 | 身份 | SHA256 | 拟迁入位置 | 迁移条件 |
|---|---|---|---|---|
| `experiments/docking/receptors/GprC_A0A437AGY2.pdb` | AlphaFold monomer v2.0；A0A437AGY2；538 aa 模型 | `270871e91f8af0ebbd0d283e8ec3fab269ccc41687c4cf632093c2dcbc6a820d` | `inputs/receptors/GprC_A0A437AGY2.pdb` | 复制后复核 accession、长度和 SHA256 |
| `experiments/docking/receptors/Gpr2_G1X9E2.pdb` | AlphaFold monomer v2.0；G1X9E2 | `0801e8e3c746ec1089ccfdcdb2c4d6dfa67710b3c01a1a3510897a278de946df` | `inputs/receptors/Gpr2_G1X9E2.pdb` | 复制后复核 accession、长度和 SHA256 |
| `experiments/docking/receptors/Gpr3_G1XJN1.pdb` | AlphaFold monomer v2.0；G1XJN1 | `cbca769fd582bd837bfe3984cf7ca9d72fc7bad3c541095ce7f016107f5b643a` | `inputs/receptors/Gpr3_G1XJN1.pdb` | 复制后复核 accession、长度和 SHA256 |
| `experiments/docking/ligands/ascr18_CID71514784.sdf` | PubChem CID 71514784；3D SDF | `d0f46ab82153c12541d7908b68a7f2c84467138b4df9fb5a43d46b1731749faa` | `inputs/ligands/ascr18_CID71514784.sdf` | 复制后核对 CID、立体化学、净电荷和 SHA256 |
| `experiments/docking/ligands/ascr3_CID16066476.sdf` | PubChem CID 16066476；3D SDF | `cf3969daa490879ac4cc0fc225b657d00b3c21f568558e4c90a4ca7c85a588c0` | `inputs/ligands/ascr3_CID16066476.sdf` | 复制后核对 CID、立体化学、净电荷和 SHA256 |

这些文件只作为原始输入。受体截取文件、PDBQT、Orca 输出和 docking poses 均由本项目重新生成。

### 可提取的代码文件

以下 Drylab 路径均相对于 `src/modeling/docking-repro/`。

| Drylab 源文件 | 可用部分 | 不带入的旧逻辑 | 拟迁入模块 | 主要依赖 | 时机 |
|---|---|---|---|---|---|
| `utils.py` | `load_config`、`generate_run_id`、`setup_logging`、最小文件存在检查 | 旧目录自动创建、latest 覆写和旧结果子目录约定 | 作为函数参考；最小预检直接放入对应脚本 | PyYAML、stdlib | 首轮 |
| `prepare_receptor.py` | `_clean_pdb`、`extract_tm_domain_by_annotation`、`prepare_receptor_adfr` | pLDDT 自动截取、批量遍历、已存在文件自动复用 | `scripts/prepare_inputs.py` | Biopython、ADFR Suite | 首轮 |
| `prepare_ligand.py` | 初始3D生成、Orca输入/收敛检查、XYZ→PDB、`prepare_ligand_adfr`、`count_dofs` | Windows MPI PATH、批量配体循环、`freeze_terminal_torsions`、重复的 `method_from_inp` | `scripts/prepare_inputs.py` | RDKit、Orca、ADFR Suite | 首轮 |
| `grid_box.py` | `GridBox`、原子质量表、`compute_box_center_of_mass` | blind box、残基质心、自动 BW 推断 | `scripts/run_vina.py` | NumPy | 首轮；原子集合由 0C 冻结 |
| `dock.py` | `DockingResult`、`_parse_vina_output`、`_run_vina`、单阶段运行骨架和命令/stdout/stderr记录 | 两阶段对接、手动中心、受体特定 offset/box、完整矩阵函数 | `scripts/run_vina.py` | Vina CLI、stdlib | 首轮 |
| `run_wt_singlestage.py` | CLI 参数、输入预检、receptor×ligand 小循环的组织方式 | ascr#1/ascr#7、旧验证表、硬编码文件名、受体特定 box 分支 | `scripts/run_vina.py` 的参考 | 上一行模块 | 首轮；不整文件复制 |
| `run_ifp_analysis.py` | `add_hydrogens`、`pdbqt_to_sdf`、`fix_sdf_valence`、`fix_receptor_charges`、pose-set pocket、`analyze_pair`、交互类型列表 | top-20 默认值、ascr#1/ascr#7、旧 GprC PASS/MISS、旧接触频率和单向候选标签 | `scripts/analyze_contacts.py` | Open Babel、RDKit、NumPy、pandas、MDAnalysis、ProLIF | WT选点阶段 |
| `plot_ifp_2d_diagram.py` | `LigNetwork` 绘图调用和 HTML 输出方式 | 旧结果路径、旧临时文件、重复指纹计算和页面装饰 | `scripts/analyze_contacts.py` 的可选绘图部分 | ProLIF | 延后到需要二维图时 |
| `mutagenesis.py` | `_get_residue_wt`、`make_explicit_mutations`、`make_alanine_scan_mutations`、`make_saturation_scan_mutations`、WT归一化公式 | `_get_scan_residues`、`run_mutagenesis`、旧目录、两阶段分支、旧阈值和自动报告 | `scripts/prepare_mutants.py`；公式进入 `scripts/rank_selectivity.py` | stdlib | 位点冻结后；公式在排序阶段 |
| `generate_mutant_fastas.py` | `_read_sequence_from_pdb` 和单点序列替换 | 从 `config.scan_residues` 批量生成、默认全扫描和旧目录 | `scripts/prepare_mutants.py` | stdlib | 位点冻结后 |
| `process_af3_structures.py` | `find_best_model` 及 ranking/pTM 记录 | 扫描全部下载目录、旧 job 命名过滤和批量复制 | `scripts/prepare_mutants.py` | stdlib | AF3返回后 |
| `cif_to_pdb.py` | `convert_one` | 批量 glob、旧目录和 overwrite 行为 | `scripts/prepare_mutants.py` | Biopython | AF3返回后 |
| `extract_mutant_tm.py` | 对“突变体与 WT 使用相同注释截取函数”的调用顺序 | pLDDT fallback、批量 glob 和旧目录 | 不单独迁移；复用 `prepare_inputs.py` 的受体截取函数 | Biopython | AF3返回后 |
| `frame_alignment.py` | `parse_atoms`、`validate_mutation_identity`、`select_tm_ca`、`kabsch_transform`、`apply_transform_to_pdb`、`align_mutant_to_wt` 和对齐摘要 | 162突变体清单、固定147 Cα数量假设、旧 run-root/终态绑定 | `scripts/prepare_mutants.py` | NumPy | 突变体制备阶段；必需 |
| `tests/modeling/test_docking_frame_repair.py` | Kabsch round-trip、突变身份检查、对齐后 RMSD 和输入篡改失败样例 | 162突变体库存、旧真实结果路径和 frame-run manifest | `tests/test_core_logic.py` 的测试来源 | pytest、NumPy | 与 alignment 迁移同时 |

### 只作参考、不进入首轮迁移的文件

| Drylab 文件或目录 | 允许用途 | 处理决定 |
|---|---|---|
| `src/modeling/docking-repro/config.yaml` | 查阅旧字段名、TM 注释线索和曾用参数 | 不整份迁移；0C 另建一份小配置 |
| `environments/mac-docking.yml` | 确认 macOS 可用包名 | 不整份迁移；依赖裁剪后再生成最小环境文件 |
| `environments/mac-docking.lock.yml`、`e2-docking-frame-repair.lock.yml` | 查阅已测试的软件版本 | 不迁移；两份 lock 含大量当前任务无关包和站点路径 |
| `experiments/docking-repro/prepared/receptors/` | 排查历史受体制备差异 | 不迁移为正式输入；GprC PDB/PDBQT 残基范围不一致 |
| `experiments/docking-repro/prepared/ligands/` | 排查历史配体制备差异 | 不迁移为正式输入；配体从原始 SDF 重新制备 |
| `run_mutagenesis_alanine.py`、`run_mutagenesis_saturation.py` | 理解旧任务组织方式 | 不迁移；候选来源和默认规模与当前路线不一致 |
| `run_frame_repair_*.py`、`geometry_gate.py`、终态聚合脚本 | 理解旧坐标缺陷及修复背景 | 不迁移；当前项目仅保留突变身份核验和刚体对齐 |
| `ratio_ranking.py` | 核对为何旧 raw ratio/channel 规则不适用 | 不迁移；WT归一化公式来自 `mutagenesis.py` |
| `multi_mutant.py` 及 multi-mutant 目录 | 无当前用途 | 不迁移；当前路线只处理单点突变 |
| `experiments/docking-repro/results/`、`analysis/`、`mutagenesis/fastas/` | 历史排错和样式参考 | 不作为新候选、输入、分数或排名来源 |

### 拟迁入的最小目标

0B-2 将迁移目标压缩为下列逻辑结构；目录和文件在迁移获批后创建：

```text
config/
└── minimal_vina.yaml           # 0C 冻结的最小方法参数

inputs/
├── receptors/                  # 3 个原始 AlphaFold PDB
└── ligands/                    # ascr#3、ascr#18 原始 SDF

scripts/
├── prepare_inputs.py           # 受体/配体准备
├── run_vina.py                 # COM box + 单阶段 Vina
├── analyze_contacts.py         # top-5 ProLIF、共同/差异残基、可选二维图
├── prepare_mutants.py          # FASTA、AF3处理、截取、身份核验、对齐
└── rank_selectivity.py         # WT归一化选择性表

tests/
└── test_core_logic.py          # 接触计数、排序、身份和坐标对齐测试
```

每个目标脚本只承载当前路线的一类任务，并使用显式输入和输出。通用函数数量很少，暂不设置单独的公共模块。

### 最小依赖集合

| 类别 | 首轮需要 | 延后或不需要 |
|---|---|---|
| 外部程序 | AutoDock Vina、ADFR Suite、Open Babel；需要重新做配体优化时使用 Orca | 远程调度器、MD 工具链 |
| Python | PyYAML、NumPy、Biopython、RDKit、pandas、MDAnalysis、ProLIF | matplotlib、PLIP、Meeko、ProDy、OpenPyXL、python-docx |

具体版本和安装方式由 0C 冻结；0B-2 只确定代码依赖边界。

### 迁移顺序

1. WT选点所需：5个原始输入、`prepare_inputs.py`、`run_vina.py`、`analyze_contacts.py`；
2. 位点冻结后：`prepare_mutants.py` 和最小 alignment 测试；
3. 突变体双配体结果产生后：`rank_selectivity.py`；
4. 最终候选需要展示时：启用 `analyze_contacts.py` 的二维图输出。

## 0B-3 缺失功能审查

### 审查问题

0B-3 检查 0B-2 规划的每个目标文件能否仅靠提取旧函数完成，并确定最小新增逻辑。判断标准是：脚本只需支持本路线的 1 个 GprC 验证任务、4 个 WT 任务、最多 4 个单点突变体及其双配体任务。

### 必须新增或重写的功能

| 目标文件 | 旧仓库已有基础 | 当前缺口 | 最小实现 | 最早需要阶段 |
|---|---|---|---|---|
| `config/minimal_vina.yaml` | 旧 `config.yaml` 提供字段和参数线索 | 缺少只包含当前受体、两种配体、统一受体范围、box 和 Vina 参数的小配置 | 0C 新写一份短配置；所有脚本只读取这一份 | 0C |
| `scripts/prepare_inputs.py` | 受体清理、按注释截取、Orca 和 ADFR 制备、DOF 计数函数可提取 | 缺少显式单文件 CLI、严格受体范围检查及输入/输出身份记录 | 提取旧函数并写薄封装；记录源文件和输出 SHA256、受体残基范围、配体净电荷与实际 DOF；任何范围或身份不符即停止 | 0D 前 |
| `scripts/run_vina.py` | COM box、单阶段 Vina、分数解析和命令日志可提取 | 旧 runner 绑定旧矩阵和受体特定 box；也没有一个同时适用于 GprC、WT 和突变体的最小入口 | 一个显式 receptor–ligand 命令；WT 首次计算并记录 box，突变体读取对应 WT 的同一 box；保存输入哈希、软件版本、参数、命令、stdout、stderr、全部分数和 poses | 0D 前 |
| `scripts/analyze_contacts.py` | PDBQT→SDF、价态修复、ProLIF 和 LigNetwork 调用可提取 | 旧频率会把同一 pose 中同一残基的多类相互作用重复计数；候选方向被硬编码；缺少可复查的共同/差异结果表 | 重写聚合：先输出逐 pose 接触，再按“残基在该 pose 是否出现”去重计数；对称输出 shared、ascr3_only、ascr18_only；再应用 0C 冻结的频率门槛和保护位点表 | 第 1 步前；GprC 仅需简单接触检查 |
| `scripts/prepare_mutants.py` | 显式/Ala/饱和突变枚举、FASTA、AF3 选模、CIF→PDB、身份核验和 Kabsch 对齐均有可提取函数 | 缺少从本项目冻结候选表到单点突变体输入的一条小流程 | 读取显式候选；生成 FASTA；接收 AF3 结果；核对只有目标位点变化；按 WT 规则截取并对齐；最后调用受体 PDBQT 制备 | 位点冻结后 |
| `scripts/rank_selectivity.py` | `mutagenesis.py` 有正确的 WT 归一化公式 | 旧 `ratio_ranking.py` 使用原始分差和旧 channel/panel 规则；缺少面向当前小规模结果的独立排序脚本 | 新写短脚本：校验 WT/突变体的配体、box 和参数一致，计算两项 ΔΔG 与 `ΔΔGselectivity`，输出两个方向的排序表和人工 pose 检查栏 | 第 3 步 |
| `tests/test_core_logic.py` | 旧 frame repair 测试可裁剪 | 接触去重、对称分组和选择性公式没有与新路线对应的最小回归测试 | 使用小型合成数据测试四件事：同残基每 pose 只计一次、共同/差异分组对称、公式符号正确、突变身份与 Kabsch 对齐失败时停止 | 与对应脚本同时 |

### 每个脚本的最小输出

| 脚本 | 必须输出 | 本阶段不要求的输出 |
|---|---|---|
| `prepare_inputs.py` | prepared PDB/PDBQT、输入与输出 SHA256、残基范围或配体电荷/DOF 摘要 | 批量准备报告 |
| `run_vina.py` | poses PDBQT、分数表、box、完整参数、命令及 stdout/stderr | 终态聚合和面板报告 |
| `analyze_contacts.py` | 逐 pose 接触表、残基频率表、共同/差异表、候选表 | 首轮不要求精美二维图；最终候选需要展示时再启用 |
| `prepare_mutants.py` | FASTA、AF3 选模记录、身份核验、对齐摘要、prepared mutant PDBQT | 大规模任务清单 |
| `rank_selectivity.py` | 每个突变体的四个原始分数、三项 ΔΔG、两个方向榜单、pose 检查栏 | 自动声称结合或功能改变 |

### 无需另写脚本的功能

- GprC 验证、WT 和突变体对接共用 `run_vina.py`；
- Ala 与以后可能触发的饱和突变共用显式 mutation 输入，不另设批量 runner；
- 多 seed 复核通过更换 `run_vina.py` 的 seed 参数完成；
- 代表 pose 的口袋方向和 PyMOL 检查由团队人工记录；
- 二维图作为 `analyze_contacts.py` 的可选输出，不单独维护绘图脚本。

### 进入实现前由 0C 冻结的项目选择

1. GprC、Gpr2、Gpr3 的绝对受体截取范围及 ECL2 保留范围；
2. 计算 box 质心所用原子集合，以及由 WT 得到的 box 复用规则；
3. ascr#3/ascr#18 的质子化、净电荷、实际 DOF 和是否重做 Orca 优化；
4. Vina/ADFR/Open Babel 版本，以及 seed、`num_modes`、`energy_range`、`min_rmsd` 和 CPU 数；
5. top-5 接触频率门槛、共同/差异定义和保护位点表；
6. GprC 验证与 WT 选点的人工 pose 验收表。

### 0B 最终结论

旧仓库的定位是输入文件和底层函数来源；当前路线由本项目按最小迁移包重新组装。该包由 **1 份配置、5 个脚本、1 个测试文件和 5 个原始输入**组成。真正需要重新实现的核心逻辑只有两处：

1. 基于逐 pose 去重的共同/差异接触与候选生成；
2. 带协议一致性检查的 WT 归一化选择性排序。

其余脚本以提取旧函数、删除旧任务规模和增加显式输入检查为主。0C 已冻结配置和验收规则；下一步按 0D-1 的范围迁移 GprC/ascr#18 输入并完成工具 preflight。

## 审查依据

- 当前路线：`MINIMAL_VINA_ROADMAP.md`；
- 文献基准：`research/2026-08-13-hu2024-minimal-vina-method.md`；
- Drylab 方法权威：`docs/modeling/P0-molecular-docking.md`；
- Drylab 目录边界：`experiments/docking-repro/README.md`；
- Drylab 实现：`src/modeling/docking-repro/` 下的输入制备、Vina、IFP、突变、AF3、frame alignment 和 ranking 模块；
- 审查日期：2026-08-14。
