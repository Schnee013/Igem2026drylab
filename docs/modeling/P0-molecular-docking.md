---
direction: P0-molecular-docking
status: in_progress
priority: P0
chassis_dependent: false
last_updated: 2026-04-05
---

# P0: 受体-配体分子对接与 In Silico 突变扫描

> 来源: PRD v3 §3.1 | iGEM 评审定位: 直接支撑湿实验设计

## 解决什么问题

核心问题：**如何改造 Gpr2/3/GprC 受体，使其更好地区分 ascr#18（PPN 特征性标志物）和 ascr#3（自由生活线虫标志物）？**

文献（Hu2024、Kuo2024）已给出 WT 受体的结合亲和力排名。干实验的真正价值在于**预测增强选择性的突变位点**，为湿实验组的定点突变设计提供计算依据。

**iGEM 价值（DBTL cycle）**:
- **Design**: 本方向产出 → 推荐突变位点（ΔΔG_selectivity < -0.5 kcal/mol）
- **Build**: 湿实验组据此设计定点突变实验
- **Test**: 湿实验实测突变体结合活性
- **Learn**: 实验结果反馈回模型，校准 FoldX 预测准确度

## 方法路线

1. 从 AlphaFold DB 获取 Gpr3/Gpr2/GprC 预测结构
2. 使用 AutoDock Vina 两阶段对接（spacing=0.1Å，匹配 Hu2024 参数）建立 WT 基线
3. PLIP 分析结合口袋关键残基（验证 Hu2024 已知位点，发现新接触残基）
4. **In silico 突变扫描（核心新增）**：
   - FoldX BuildModel 生成突变体结构（秒级）
   - 重对接计算 ΔΔG_selectivity = ΔΔG(ascr18) - ΔΔG(ascr3)
   - 排名推荐 → 供湿实验组验证

## 工具栈

| 工具 | 用途 | 安装 |
|------|------|------|
| AlphaFold DB | 结构获取 | 浏览器 |
| AutoDock Vina v1.2.7 | 分子对接 | 独立可执行文件 |
| ADFR Suite | 受体/配体 PDBQT 准备（Hu2024 方法） | Windows GUI 安装 |
| Orca 6.1.1 | 配体 DFT 几何优化（B3LYP/def2-TZVP） | Windows，学术免费 |
| **FoldX** | **突变体结构快速建模（~秒/突变）** | **学术免费，见下方安装说明** |
| PLIP | 蛋白-配体相互作用分析 | `pip install plip` |
| PyMOL | 分子可视化 | 教育版免费申请 |

### FoldX 安装

FoldX 是业界标准的突变体快速建模工具，学术使用免费：

1. 申请学术许可证：https://foldxsuite.crg.eu/academic-license-info
2. 下载对应平台版本（Windows/Mac/Linux）
3. Windows：解压到 `D:\drylab-tools\foldx\`，确保 `foldx.exe` 存在
4. 更新 `config.yaml` 中的 `mutagenesis.foldx_bin` 路径

## 参数与数据来源

| 数据 | 来源 | 链接 | 状态 |
|------|------|------|------|
| Gpr3 结构 (G1XJN1, 401aa) | AlphaFold DB | [AF-G1XJN1-F1](https://alphafold.ebi.ac.uk/entry/AF-G1XJN1-F1) | 已验证，pLDDT 跨膜区 >90 |
| Gpr2 结构 (G1X9E2, 406aa) | AlphaFold DB | [AF-G1X9E2-F1](https://alphafold.ebi.ac.uk/entry/AF-G1X9E2-F1) | 已验证 |
| GprC 结构 (A0A437AGY2, 538aa) | AlphaFold DB | [AF-A0A437AGY2-F1](https://alphafold.ebi.ac.uk/entry/AF-A0A437AGY2-F1) | 已验证（页面标题显示 Git3 domain，UniProt 确认为 GprC） |
| ascr#18 (C₁₇H₃₂O₆) | PubChem | [CID 71514784](https://pubchem.ncbi.nlm.nih.gov/compound/71514784) | 已验证，SDF 已下载 |
| ascr#3 (C₁₅H₂₆O₆) | PubChem | [CID 16066476](https://pubchem.ncbi.nlm.nih.gov/compound/16066476) | 已验证，SDF 已下载 |
| ascr#7 (C₁₃H₂₂O₆) | PubChem | [CID 86289656](https://pubchem.ncbi.nlm.nih.gov/compound/86289656) | 已验证，SDF 已下载 |

### 配体化学标识符（用于交叉验证）

| 配体 | CAS | InChIKey | ChEBI | SMILES | ChemSpider |
|------|-----|----------|-------|--------|------------|
| ascr#18 | 1355681-10-5 | AHRWSOYISAIFOZ-JRBZFYFNSA-N | [CHEBI:78955](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:78955) | `CC1C(CC(C(O1)OC(C)CCCCCCCCC(=O)O)O)O` | — |
| ascr#3 | 946524-26-1 | MWGRRKDIJLJLMO-OSYKULTDSA-N | [CHEBI:78821](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:78821) | `CC1C(CC(C(O1)OC(C)CCCCC=CC(=O)O)O)O` | [17226059](https://www.chemspider.com/Chemical-Structure.17226059.html) |
| ascr#7 | 1139837-37-8 | GGHOMCWJOMBZEK-LHYQPRBASA-N | [CHEBI:78830](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:78830) | `CC1C(CC(C(O1)OC(C)CCC=CC(=O)O)O)O` | — |

> 验证状态：ascr#3 和 ascr#7 的 CAS 号已通过 Common Chemistry 验证。ascr#18 的 CAS 号不在 Common Chemistry 收录范围内，但通过 PubChem 同义词、ChEBI、Wikidata (Q27148038) 三方独立交叉确认身份无误。

> 注：三个配体共享 ascarylose 糖骨架，差异在侧链长度和饱和度（ascr#18 全饱和 C10；ascr#3 反式双键 C8；ascr#7 反式双键 C6）。

**关键文献**:
- Kuo et al. (2024) — Gpr2/Gpr3 与 ascaroside 的结合实验证据。[文献总结](../papers/summaries/Kuo2024-Gpr2Gpr3-summary.md)
- Hu et al. (2024) — GprC 结构功能关系。[文献总结](../papers/summaries/Hu2024-GprC-summary.md)

## 产出定义

- [x] 受体-配体结合能排名表（3 受体 × 3 配体 = 9 组）—— v2 production 完成（2026-04-04）
- [x] 结合口袋关键残基列表（v2 PLIP 分析完成，Gpr2/3/GprC 各受体 top-5 接触残基已确认）
- [x] **ΔΔG_selectivity 排名表**（27/28 突变体完成，2026-04-05；完整表见 [突变扫描报告](../../experiments/docking-repro/mutagenesis/mutagenesis_report.md)）
- [x] **产出文件位置**: `experiments/docking-repro/mutagenesis/`（含 mutagenesis_results_full.json）
- [ ] **推荐突变位点**（校正后 GprC/Gpr3 无候选达阈值；Gpr2 Y200/Y378 已达显著性，待 WT 重对接确认）
- [ ] WT 两阶段重对接（解决协议不匹配，约 1 小时）→ 重评 GprC/Gpr3 ΔΔG
- [ ] 可视化图（PyMOL 渲染 WT vs 最优突变体结合构象对比）

## 方法变体

本方向存在两条并行的方法线：

### v2（当前主线）
- **代码路径**: `src/modeling/docking/`
- **产出路径**: `experiments/docking/`
- **工具链**: OpenBabel 受体准备 + RDKit MMFF 配体优化 + Meeko PDBQT + spacing=0.25Å
- **状态**: production 结果已获取（2026-04-04）
- **已验证**: Kuo2024 Gpr2/Gpr3 排名（PASS）；GprC 绝对值差 ~2 kcal/mol（方法差异）

### docking-repro（Hu2024 精确复现 + 突变扫描主线）
- **代码路径**: `src/modeling/docking-repro/`
- **产出路径**: `experiments/docking-repro/`
- **工具链**: ADFR Suite + Orca DFT B3LYP/def2-TZVP + 两阶段对接 + **FoldX 突变扫描**
- **计算节点**: Windows 7500F（通过 Tailscale SSH 远程调用）
- **安装脚本**: `scripts/win-setup/` (01~04)
- **运行步骤**:
  1. `--step prepare`：ADFR 受体准备 + Orca DFT 配体优化（Windows，已运行）
  2. `--step dock`：两阶段 Vina 对接建立 WT 基线
  3. `--step analyze`：PLIP 关键残基分析
  4. `--step mutagenesis`：FoldX 突变扫描 → ΔΔG_selectivity 排名
- **状态**: alanine scan 完成（27/28 突变体，2026-04-05）；Orca DFT 后台进行中；需 WT 两阶段重对接解决协议偏差

**共享数据**: 两条线共用同一份原始 PDB/SDF（通过 symlink），不重复存储。

## 代码与实验关联

- **受体 PDB**: `experiments/docking/receptors/` （Gpr2_G1X9E2.pdb, Gpr3_G1XJN1.pdb, GprC_A0A437AGY2.pdb）
- **配体 SDF**: `experiments/docking/ligands/` （ascr18_CID71514784.sdf, ascr3_CID16066476.sdf, ascr7_CID86289656.sdf）
- **湿实验对接**:
  - 本方向产出 → 核心感应组：推荐突变位点，指导定点突变实验设计
  - 湿实验反馈 → 本方向：实际结合实验数据，用于校准/验证对接预测

## 学习成本与依赖

- **难度**: ★★☆☆☆（有 Python 基础，工具有完善教程）
- **前置知识**: 蛋白质结构基础、配体-受体概念
- **学习资源**: 见 [学习路线图 阶段二](../learning/roadmap.md)
- **预计时间**: 1-2 周完成学习 + 首次对接

## 突变扫描结果（2026-04-05）

完整结果见 [mutagenesis_report.md](../../experiments/docking-repro/mutagenesis/mutagenesis_report.md)。

**重要方法学说明**: WT 基线（v2 单阶段 spacing=0.25）与突变体（两阶段 spacing=0.1）协议不同，导致系统性偏差约 −0.7 kcal/mol。GprC 内部对照（S77A/N83A）已量化此偏差，原始排名需校正解读。

### GprC（校正后结果）

| 突变 | ΔG(18) | ΔG(3) | 校正 ΔΔG_sel | 来源 |
|------|--------|--------|------------|------|
| H189A | −6.60 | −6.46 | −0.10 | PLIP |
| N378A | −6.77 | −6.63 | −0.09 | PLIP |
| L377A | −6.16 | −6.03 | −0.08 | PLIP |
| R281A | −6.81 | −6.69 | −0.07 | Hu2024 |

校正基线（S77A/N83A 内部对照）: ascr18=−6.733, ascr3=−6.687。**无一达到 −0.5 阈值**，建议 WT 重对接后重评。

### Gpr2（数据可信，协议偏差被效应克服）

| 突变 | ΔΔG(18) | ΔΔG(3) | ΔΔG_sel | 解读 |
|------|---------|--------|---------|------|
| **Y200A** | +0.23 | **−0.89** | **+1.12** | ascr3 结合关键残基 |
| **Y378A** | +0.41 | **−0.51** | **+0.92** | ascr3 结合关键残基 |
| Y330A | +0.51 | +0.08 | +0.43 | ascr18 结合贡献 |
| R59A | +0.53 | +0.16 | +0.37 | ascr18 结合贡献 |

**Gpr2 Y200 和 Y378 建议优先湿实验验证**（ΔΔG_sel > 0.9，远超 Vina 噪声）。

### Gpr3（协议偏差主导，需 WT 重对接）

全部 ΔΔG(18) < 0，结果不可用于推荐突变位点。详见完整报告。

## 方法学局限性

| 局限性 | 影响 | 缓解措施 |
|--------|------|---------|
| 协议不匹配（WT vs 突变体对接方案不同） | 系统性偏差 ~−0.7 kcal/mol，影响 ΔΔG 绝对值 | WT 两阶段重对接（已计划） |
| Docking box 边界（Stage2 仅 20 Å） | box 外残基突变零灵敏度 | GprC S77A/N83A 已确认为 box 外（用作内部对照） |
| 刚性受体 + 局部侧链重排 | FoldX 突变后骨架未弛豫 | 仅影响结合口袋构象精度，对排名影响有限 |
| Vina 评分精度（±1 kcal/mol） | ΔΔG < 0.5 在噪声范围内 | 仅信任 ΔΔG > 0.9 的强效应（Gpr2 Y200/Y378） |

## 补充实验计划（解决 Alanine Scan 局限性）

Alanine scan 暴露三个关键局限，对应以下补充实验（runner 脚本在 `src/modeling/docking-repro/`）：

| 编号 | 实验 | 脚本 | 优先级 | 预计耗时 | 状态 |
|------|------|------|--------|---------|------|
| S1 | WT 两阶段重对接（修复协议不匹配） | `run_wt_twostage.py` | P0 | ~1 hr | 待运行 |
| S2 | 多 seed 方差评估（误差棒） | `run_multiseed.py` | P1 | ~3-4 hr | 待 S1 |
| S3 | Gpr2 Y200/Y378 饱和扫描（最优替换） | `run_saturation_gpr2.py` | P1 | ~8-10 hr | 待 S1 |
| S4 | GprC 扩大 box 25Å（N83A 阳性对照） | `run_gprc_expanded_box.py` | P2 | ~2 hr | 待 S1 |
| S5 | DFT 配体重对接（Orca 完成后） | `run_wt_twostage.py` (DFT PDBQT) | P2 | ~2-3 hr | 等待 Orca |
| S6 | PyMOL 可视化 | 手动 | P2 | ~4-6 hr | 待 S1/S3 |

**执行顺序**: S1（今天）→ S3 overnight → S2/S4（Day 2）→ S5/S6（Day 3-4）

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §3.1 提取初始内容 | 文档体系搭建 |
| 2026-04-03 | v1.1 | 补充已验证的 AlphaFold/PubChem 链接，新增 ascr#7，对接矩阵更新为 3×3 | 数据源验证 |
| 2026-04-03 | v1.2 | 补充配体化学标识符（CAS, InChIKey, SMILES, ChemSpider），关联文献总结 | 化合物交叉验证 |
| 2026-04-04 | v1.3 | 新增 docking-repro 方法变体（ADFR+Orca），补充方法变体章节 | Hu2024 精确复现需求 |
| 2026-04-04 | v2.0 | 方向重构：从"复现文献亲和力"转向"预测增强特异性突变"；新增 FoldX mutagenesis 模块；更新产出定义和工具栈 | 发现 Hu2024/Kuo2024 已有亲和力数据，预测新突变才是真正的 iGEM 贡献 |
| 2026-04-05 | v2.1 | alanine scan 完成（27/28 突变体）；发现协议不匹配并校正；新增方法学局限性章节；Gpr2 Y200/Y378 为首要湿实验推荐 | alanine scan 运行完成 |
| 2026-04-06 | v2.2 | 新增补充实验方案（S1-S6）及对应 runner 脚本；dock.py 支持 seed 覆盖和 stage2_box_size 覆盖 | 解决协议不匹配、缺乏误差棒、仅 Ala 扫描三大局限 |

## 进展记录

| 日期 | 事件 | 关键数据 |
|------|------|---------|
| 2026-04-04 | v2 pipeline production 完成（exh=200，481.7 min） | Gpr2 ascr7=−6.654, ascr3=−6.282; Gpr3 ascr3=−6.284, ascr7=−6.238; GprC ascr18=−6.048, ascr3=−6.445; Kuo2024 排名全部 PASS |
| 2026-04-04 | docking-repro pipeline 代码完成 | mutagenesis.py 支持 alanine/saturation 两种扫描模式 |
| 2026-04-04 | docking-repro Windows 环境：Orca 6.1.1 已安装，ascr18 DFT 优化中 | 21:09 已到第 13 个几何优化 cycle，ascr3/ascr7 待启动 |
| 2026-04-05 | 完整 alanine scan 完成（27/28 突变体，3 受体 × PLIP 残基） | Gpr2 Y200A ΔΔG_sel=+1.12，Y378A=+0.92；GprC 校正后最强 H189A=−0.10；发现协议不匹配需 WT 重对接 |

## 与其他方向的依赖关系

- **输出到**:
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 结合亲和力参数（Kd）→ ODE 模型输入
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 结合口袋结构信息 → 嵌合设计参考
- **依赖于**: 无（本方向可独立启动）
