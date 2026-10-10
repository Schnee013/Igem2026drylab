# Vina 工作区说明

## 当前状态

本目录是后续 Vina 工作的统一入口。两个原始压缩包已原样保存，工作副本已解压：

```text
vina/
├── original_archives/       # 原始 zip 与 SHA256
├── inputs/                  # 结构、序列、拓扑、配体
├── src/                     # 命令行工具与 PyQt GUI 源码
└── tasks/
    └── 001_wt_vs_low_confidence_segment_removed/
```

当前可直接使用 `docking` Conda 环境运行大部分命令行工具。GUI 需要 PyQt6，当前环境尚未安装。源码已通过 Python 3.11 语法编译检查。

这套文件是“输入数据 + 对接前后处理工具”，尚缺少三个执行环节：

1. 按指定残基范围构建受体删减版本；
2. 实际调用 AutoDock Vina 并完整保存命令、日志和 pose；
3. 用 ProLIF 汇总 WT 与删减组的逐 pose 接触。

因此，现有文件适合建立可追溯流程；端到端运行需要在本目录补充小型脚本或使用显式命令。

## 与当前研究进度的衔接

当前项目已经完成以下基础工作：

- TWF154 Gpr2/Gpr3 与 GprC、SRBC-64 的 7TM 结构比对；
- Gpr2/Gpr3 跨膜范围与候选胞外口袋的人工检查入口；
- ATCC Gpr2/Gpr3 × ascr#3/ascr#18 的一批全长 WT Vina 结果；
- 一份冻结的最小 Vina 参数方案，当前停在 Meeko/RDKit 与 ADFR/ORCA 两条制备路线的选择门。

新压缩包补齐了 TWF154 的完整 AF2/AF3 模型集合、DeepTMHMM/Phyre2 拓扑、两种配体电荷状态，以及结构准备和结果汇总工具。它最适合支持下一项配对敏感性实验：

```text
同一受体模型 + 同一配体状态 + 同一固定搜索框 + 同一 Vina 参数
                    │
            ┌───────┴────────┐
            │                │
         全长 WT       删除低置信片段
            │                │
            └──── pose、分数、接触与位置比较 ────┘
```

“删除低置信片段”应作为结构不确定性敏感性对照解释。它不是天然存在的生物学突变体，也不能单靠更优 Vina 分数证明真实结合更强。

## 输入文件怎么用

### 1. 配体

`inputs/ligands/` 为 ascr#3 和 ascr#18 各提供两种形式：

| 目录 | 形式 | 文件记录的总形式电荷 | 适用方式 |
|---|---|---:|---|
| `original/` | 中性羧酸 | 0 | 延续当前最小 Hu2024 方法方案 |
| `deprotonated-minus1/` | 羧酸根 | −1 | 延续当前 ATCC r3 的去质子化配体方案 |

WT 与删减组必须使用同一份 prepared ligand PDBQT。两种电荷状态属于两套独立协议；选择一种后，应把源 SDF 的 SHA256、Meeko 参数、输出 PDBQT 的 SHA256 和扭转键信息一起冻结。

可先用以下工具检查 SDF 中实际记录的原子、电荷、键和立体信息：

```bash
conda run -n docking python vina/src/report_ligand_chemistry.py \
  --ligand-sdf <selected.sdf> --format text
```

### 2. 受体 AF2 模型

`inputs/receptors/af2/` 包含：

- TWF154 Gpr2：一套 10 个 ColabFold AF2-pTM 模型及分数 JSON；
- TWF154 Gpr3：一套 10 个 ColabFold AF2-pTM 模型及分数 JSON；
- GprC、SRBC-64、DAF-37 的 AlphaFold DB PDB。

当前 `alignment/` 主流程使用的 TWF154 AF2 模型与新包内 rank 1 并非同一组坐标。两组模型序列长度相同，但全长 TM-align 结果为：

| 受体 | 新包 rank 1 vs 当前 alignment 主模型 |
|---|---|
| Gpr2 | TM-score 0.850；aligned RMSD 2.62 Å |
| Gpr3 | TM-score 0.879；aligned RMSD 2.16 Å |

下一轮对接必须先冻结一种模型来源。若目标是让 Vina 结果直接承接现有口袋比对，优先使用 `alignment/inputs/structures/` 中已经进入主分析的模型；若目标是评估新包这套预测，则 WT 与删减组都从新包同一个模型派生，并单独记录模型来源。

### 3. 受体 AF3 模型

`inputs/receptors/af3/original_cif/` 保存 AF3 原始 CIF、full-data JSON、summary confidence JSON 和 job request；`inputs/receptors/af3/pdb/` 保存相应的 PDB 转换结果。

AF3 summary 中的 `ranking_score` 可用于同一 AF3 job 内排序。结构局部置信度应从对应 CIF/PDB 的逐残基值复核；summary 中的 `fraction_disordered` 是全局摘要，不能定位需要删除的残基。

当前结构比对把 AF3 作为备用检查。若继续这一分析口径，AF3 用于检查口袋和低置信片段在五个模型之间是否稳定，而不是挑选最符合预期 pose 的模型。

### 4. 序列与拓扑

`inputs/receptors/fasta/` 用于核对受体身份、长度和残基编号。`inputs/receptors/topology/deepTMHMM/` 与 `topology/phyre2/` 用于确认 7TM、胞内外方向和长环边界。

DeepTMHMM 对 TWF154 的主要范围是：

| 受体 | TM5 | ICL3 | TM6 | ICL3 平均 pLDDT（新包 AF2 rank 1） | 7TM 平均 pLDDT |
|---|---:|---:|---:|---:|---:|
| Gpr2 | 182–201 | 202–325 | 326–346 | 37.77 | 92.03 |
| Gpr3 | 169–189 | 190–294 | 295–315 | 58.90 | 93.55 |

这些数值支持把长 ICL3 作为当前“低置信片段”的首要候选。正式删减边界仍需结合目标受体、PyMOL 空间位置和保留的 TM5/TM6 flank 冻结。当前最小方案中的参考删减方式为：

| 受体 | 保留范围 | 实际删除主体 |
|---|---|---|
| GprC | 10–197、369–432 | 198–368 |
| Gpr2 | 25–211、322–382 | 212–321 |
| Gpr3 | 12–201、290–347 | 202–289 |

这套范围保留 7TM、胞外环和 ICL3 两端少量 flank。若本轮使用 TWF154 Gpr2/Gpr3，应先将这些参考范围与本包 DeepTMHMM 边界、实际 PDB 编号逐项核对。

## `src/` 工具的作用

### 结构、置信度与拓扑

| 文件 | 作用 | 本任务中的位置 |
|---|---|---|
| `cif_to_pdb.py` | AF3 CIF 单个或批量转 PDB | AF3 输入整理 |
| `report_af_confidence.py` | 读取受支持的 AF/ColabFold JSON，汇总全序列及指定区域置信度 | 模型与删减范围复核 |
| `parse_tm_topology.py` | 解析显式拓扑区段 | 拓扑工具底层模块 |
| `make_tm_topology_review_pml.py` | 生成 PyMOL 拓扑复核脚本 | 目视检查 TM、环区与胞外方向 |
| `make_tm_review_pml.py` | PyMOL TM 显示的公共逻辑 | 供其他复核工具调用 |

### 几何与膜定位

| 文件 | 作用 | 本任务中的位置 |
|---|---|---|
| `run_geometry_validation.py` | 调用显式指定的外部几何检查器并保存原始结果、日志和摘要 | 可选受体质控 |
| `summarize_geometry_validation.py` | 从外部检查 JSON 提取指定指标 | 可选受体质控 |
| `run_restrained_minimization.py` | 调用外部最小化程序，要求用户显式提供力场、约束与参数 | 可选结构优化 |
| `compare_raw_relaxed.py` | 比较优化前后坐标、RMSD 和位移 | 优化影响复核 |
| `make_raw_relaxed_review_pml.py` | 生成优化前后 PyMOL 对照 | 优化影响复核 |
| `extract_ppm_protein_pdb.py` | 从 PPM 输出去除 DUM 记录并提取蛋白链 | 使用 PPM 时的整理步骤 |
| `make_ppm_review_pml.py` | 生成 PPM 膜平面与受体复核视图 | 检查胞外/胞内方向 |

### 化学检查与 PDBQT 准备

| 文件 | 作用 | 本任务中的位置 |
|---|---|---|
| `report_receptor_chemistry.py` | 报告 PDB 中残基、HETATM、水和可电离位点等可观察信息 | 准备前检查 |
| `report_ligand_chemistry.py` | 报告 SDF 原子、电荷、键、氢和立体信息 | 配体状态冻结 |
| `prepare_receptor_pdbqt.py` | 调用 Meeko 准备受体 PDBQT | WT 与删减受体准备 |
| `prepare_ligand_pdbqt.py` | 调用 Meeko 准备配体 PDBQT，可联动显式原子映射检查 | 配体准备 |
| `check_sdf_pdbqt_mapping.py` | 按外部提供的 atom-map JSON 核对 SDF→PDBQT 映射 | 高严格度配体验收 |

压缩包没有提供配体 atom-map JSON。当前可以使用 `prepare_ligand_pdbqt.py` 的 preparation-only 模式；若要启用严格映射门，需要另行生成并人工核对 atom-map。

### Vina 配置与结果

| 文件 | 作用 | 限制 |
|---|---|---|
| `define_vina_box.py` | 把人工指定的中心、尺寸、exhaustiveness、num_modes、energy_range 和 seed 写入配置 | 不计算 box 中心，也不实际运行 Vina；不写 CPU、spacing、min_rmsd、max_evals |
| `summarize_vina_results.py` | 从 Vina 1.x 日志提取 mode、affinity、RMSD 和版本，写 JSON | 机械汇总，不判断 pose 是否合理 |

本任务应补充一个 `run_vina.py`，负责固定输入哈希、记录实际 Vina 版本、完整参数、命令、stdout/stderr 和 pose 输出。执行前可先用 `define_vina_box.py` 生成基础配置，再在运行命令中显式补齐冻结参数。

### 导出与相互作用图

| 文件 | 作用 | 条件 |
|---|---|---|
| `export_receptor_pdbqt_to_pdb.py` | 将 prepared receptor PDBQT 导回 PDB | Maestro LID 前处理 |
| `export_ligand_pdbqt_to_sdf.py` | 用 Meeko/RDKit 将 ligand pose 导回 SDF | Maestro LID 前处理 |
| `generate_maestro_lid.py` | 调用 Schrödinger Maestro 生成 LID 图 | 需要本机 Schrödinger/Maestro |

当前源码没有 ProLIF 接触分析工具。WT 与删减组完成后，需要补充 `analyze_contacts.py`，按“同一残基在每个 pose 最多计一次”统计 top poses。

### GUI 与内部模块

| 文件 | 作用 |
|---|---|
| `docking_gui.py` | PyQt6 图形界面，组织上述独立工具 |
| `docking_tool_specs.py` | GUI 工具分组、字段、默认值和输出命名 |
| `docking_tool_result.py` | CLI 与 GUI 之间的结果回执格式 |
| `atomic_publish.py` | 安全发布暂存输出，避免半写入文件 |
| `external_process.py` | 无 shell 展开的外部命令调用 |
| `transient_paths.py` | 临时工作目录选择 |

GUI 是这些 CLI 的表单层，不会自动补齐缺失的科学决策或 Vina runner。当前环境可直接使用 CLI；是否安装 PyQt6 可在流程稳定后决定。

## WT 与低置信片段删减组的推荐执行顺序

### 1. 冻结实验身份

以 `tasks/001_wt_vs_low_confidence_segment_removed/00_decisions/decision_record.template.yaml` 为模板生成 `decision_record.yaml`，并记录：

- 受体：Gpr2、Gpr3、GprC 或其他明确对象；
- 模型来源与具体文件 SHA256；
- 配体与电荷状态；
- WT 定义；
- 删除的绝对残基范围与结构依据；
- 固定 box 数值和确定方式；
- Vina 参数与实际版本。

### 2. 生成两个受体版本

- `WT`：所选原始模型的明确副本；
- `segment_removed`：仅删除冻结范围，保留原始残基编号和其余坐标；
- 生成 residue manifest，证明两者除目标范围外原子坐标一致；
- 在 PyMOL 中确认 7TM、胞外口袋和 ECL2 均保留。

删减范围若碰到任一 DeepTMHMM TM 区段，流程应暂停并重新核对，因为这会改变口袋骨架而非单纯处理低置信环区。

### 3. 准备 PDBQT

WT 与删减受体使用同一 Meeko 版本、charge model 和清理选项。配体只准备一次并供两组复用。

当前环境实测版本：

```text
Python 3.11.15
AutoDock Vina 1.2.5
Open Babel 3.1.0
Meeko 0.7.1
```

这些实际版本与 `MINIMAL_VINA_ROADMAP.md` 中的目标版本存在差异，运行记录应写实际 CLI 版本。跨组比较要求版本和参数一致。

### 4. 冻结共同搜索框

WT 与删减组使用完全相同的数值 box。推荐从稳定的 7TM 核或已经确认的胞外口袋确定中心，再用 PyMOL 检查 box 是否覆盖胞外正构口袋。

当前最小参数参考为：

```text
size = 40 × 40 × 40 Å
spacing = 0.1 Å
exhaustiveness = 200
seed = 44
cpu = 4
num_modes = 5
energy_range = 5 kcal/mol
min_rmsd = 1 Å
max_evals = 0
```

不得分别用 WT 和删减受体的全原子质心生成两个中心，否则组间差异会同时混入 box 位移。低置信 ICL3 可能改变质心，且删减后暴露的胞内疏水腔需要在 pose 复核中单独标记。

### 5. 运行、汇总与人工验收

每组至少保存：

- receptor/ligand 原始与 prepared 文件及 SHA256；
- Vina config、实际命令、软件版本；
- stdout、stderr、pose PDBQT；
- `summarize_vina_results.py` 生成的 JSON；
- top poses 的 PyMOL 位置判定；
- 逐 pose 接触表与残基频率表。

首先比较 pose 是否位于相同的胞外口袋，再比较分数。Vina 分数支持同协议内排序；真实亲和力和结合结论需要独立证据。

## 当前执行门

开始构建受体和运行 Vina 前，需要冻结以下信息：

1. 本轮具体受体与配体；
2. 使用当前 alignment 主模型，还是新包内某个 AF2/AF3 模型；
3. 要删除的绝对残基范围；
4. 使用中性配体协议，还是 −1 配体协议；
5. 共同 box 的数值中心。

这些项目决定实验身份。其余准备、运行和汇总步骤可以在 `vina/tasks/001_wt_vs_low_confidence_segment_removed/` 中继续完成。
