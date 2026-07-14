---
direction: P0-molecular-docking
status: refreshed_shortlist
priority: P0
chassis_dependent: false
last_updated: 2026-07-09
---

# P0: 受体-配体分子对接与 In Silico 突变扫描

> 来源: PRD v3 §3.1 | iGEM 评审定位: 候选体系生成与 MD 验证前证据
>
> **2026-07-09 口径校准**：Gpr2 3D offset、Gpr3 方案 F、Gpr3 supplemental docking、ratio refresh、Top 候选 IFP 和 MD 前候选体系清单均已刷新。当前 MD 输入主线为 `Gpr2_R59C + ASCR18` 与 `Gpr3_R167Y + ASCR3`，候选组合与备选见 [MD 前候选体系清单](P0-docking-md-candidate-shortlist.md)。证据指针见 [2026-05-19 日志](../logs/2026-05-19.md)。

## 解决什么问题

核心问题：**如何改造 Gpr2/3/GprC 受体，使其对 ascr#18（PPN 富集标志物，Choe 2012 / Manosalva 2015）和 ascr#3（自由生活线虫标志物）具有差异化选择性？** 属于双通道比值型设计（`docs/prd/overview-v4.md` §双靶标判别逻辑）。突变按 sel_mut 双向分类为 Channel A（ascr#18 偏好）/ Channel B（ascr#3 偏好）/ neutral，跨受体配对形成传感器对。当前完整分析见 [`ratio_channel_report.md`](../../experiments/docking-repro/analysis/ratio_channel_report.md)。

文献（Hu2024、Kuo2024）已给出 WT 受体的结合亲和力排名。本方向的直接产出是**MD candidate-system shortlist**：候选标签、Channel A/B 方向、相对排序、关键结合残基和 IFP 机制线索。下一道 gate 由 MD 验证结合姿态稳定性、关键接触持续性和受体局部构象合理性。

**iGEM 价值（DBTL cycle）**:
- **Design**: 本方向产出候选体系清单、双通道方向、相对排序和机制线索。
- **Build**: MD input gate 将 shortlist 转成可审计 receptor-ligand package。
- **Test**: MD 验证 pose stability、contact occupancy/lifetime 和 receptor local conformation。
- **Learn**: MD 证据与后续 dose-response 数据共同更新候选置信度。

## 方法路线

1. 从 AlphaFold DB 获取 Gpr3/Gpr2/GprC WT 预测结构
2. 使用 AutoDock Vina **单阶段对接**（box=40Å, spacing=0.1Å, exh=200, seed=42，匹配 Hu2024 参数）建立 WT 基线
3. **ProLIF IFP 分析**结合口袋关键残基（验证 Hu2024 已知位点，发现新接触残基；IFP 交叉验证排除无效残基）
4. **In silico 突变扫描（核心新增）**：
   - **AlphaFold 3 Server** 预测突变体全长结构 → annotation-based TM 域提取 → ADFR 准备 PDBQT
   - 重对接计算 ΔΔG_selectivity = ΔΔG(ascr18) − ΔΔG(ascr3)
   - Channel A/B 双通道分类 + 跨受体配对优先级 → 形成 MD 验证候选体系清单

## 工具栈

| 工具 | 用途 | 安装 |
|------|------|------|
| AlphaFold DB | WT 结构获取 | 浏览器 |
| **AlphaFold 3 Server** | 突变体结构预测 | alphafoldserver.com（免费） |
| AutoDock Vina v1.2.7 | 分子对接 | 独立可执行文件 |
| ADFR Suite | 受体/配体 PDBQT 准备（Hu2024 方法） | Windows GUI 安装 |
| Orca 6.1.1 | 配体 DFT 几何优化（B3LYP/def2-TZVP） | Windows，学术免费 |
| **ProLIF** | 蛋白-配体 IFP 分析（Bouysset & Fiorucci 2021） | `pip install prolif` |
| PyMOL | 分子可视化 | 教育版免费申请 |

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

- [x] 受体-配体结合能排名表（3 受体 × 3 配体 = 9 组）—— WT 单阶段完成（2026-04-07）
- [x] 结合口袋关键残基列表（ProLIF IFP 分析完成，Gpr2/3/GprC 各受体高频接触残基已确认）
- [x] **双通道全谱排名刷新**：2026-05-20 版 266 条合并记录已生成；当前权威为 [ratio_channel_report.md](../../experiments/docking-repro/analysis/ratio_channel_report.md)
- [x] **Channel A/B 候选刷新**：Channel A 无 caveat 36 条；Channel B 无 caveat 13 条；3σ 阈值 = ±0.477
- [x] **MD candidate-system shortlist 刷新**：当前 Top 1 组合为 Gpr2_R59C + Gpr3_R167Y；对应 MD 输入主线为 `Gpr2_R59C + ASCR18` 与 `Gpr3_R167Y + ASCR3`，详见 [MD 前候选体系清单](P0-docking-md-candidate-shortlist.md)
- [x] IFP 热图可视化（[ifp_heatmap_all_receptors.png](../../experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png)）
- [x] Refreshed Top mutant IFP 分析（[ifp_analysis_mutants_gpr3_f_full_20260520_0854/](../../experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/)）
- [x] 可视化素材（历史 Channel A complex PDB + PyMOL scene 脚本；见 [analysis/pymol_top6/](../../experiments/docking-repro/analysis/pymol_top6/)）— 若候选讨论需要，按当前 shortlist 另行渲染 PNG/PSE
- [ ] V138R 盐桥假说 MD 实证 → 转交 [P0-md-simulation](P0-md-simulation.md)

## 方法变体

本方向存在两条并行的方法线：

### v2（早期探索，已归档）
- **代码路径**: `src/modeling/docking/`
- **产出路径**: `experiments/docking/`
- **工具链**: OpenBabel 受体准备 + RDKit MMFF 配体优化 + Meeko PDBQT + spacing=0.25Å
- **状态**: 已归档。production 结果（2026-04-04）验证了 Kuo2024 排名，但发现方法偏差后已被 docking-repro 取代

### docking-repro（当前主线，Hu2024 精确复现 + 突变扫描）
- **代码路径**: `src/modeling/docking-repro/`
- **产出路径**: `experiments/docking-repro/`
- **工具链**: ADFR Suite + Orca DFT B3LYP/def2-TZVP + **单阶段对接**（40Å/0.1/exh=200） + **AF3 突变体结构预测** + **ProLIF IFP 分析**
- **远程计算入口**: 历史刷新曾使用 Slurm GPU 集群；新服务器/远程计算任务统一先读 [NKULiulab E2 共享云服务器使用规范](../ops/nkuliulab-e2-cloud-server.md)，Windows 7500F 和 Slurm 仅作历史 artifact / 旧运行记录参考
- **关键技术修复**:
  - ICL3 截断 + TM 螺旋质心（修复 GprC grid box 偏移 18.1Å）
  - Annotation-based TM 域提取（UniProt + DeepTMHMM 交叉验证）
  - ascr18 PDBQT freeze_terminal_torsions bug 修复（15→26 原子）
- **状态**: **refreshed_shortlist**（2026-07-09 口径校准）。Gpr2/Gpr3 修复后 ratio/IFP/MD 前候选体系清单已刷新；ODE Kd/calibration 仍按单独文献计划暂停

**共享数据**: 两条线共用同一份原始 PDB/SDF（通过 symlink），不重复存储。

## 代码与实验关联

- **受体 PDB**: `experiments/docking/receptors/` （Gpr2_G1X9E2.pdb, Gpr3_G1XJN1.pdb, GprC_A0A437AGY2.pdb）
- **配体 SDF**: `experiments/docking/ligands/` （ascr18_CID71514784.sdf, ascr3_CID16066476.sdf, ascr7_CID86289656.sdf）
- **下游 gate**:
  - 本方向产出 → MD input gate：候选标签、Channel A/B 方向、相对排序、关键结合残基和 IFP 机制线索。
  - MD gate → 本方向：pose stability、关键接触持续性和 receptor local conformation 证据，用于更新候选置信度。
  - 后续 dose-response 数据 → 本方向：binding / activation calibration 证据，用于校准对接排序和 ODE 参数。

## 学习成本与依赖

- **难度**: ★★☆☆☆（有 Python 基础，工具有完善教程）
- **前置知识**: 蛋白质结构基础、配体-受体概念
- **学习资源**: 见 [学习路线图 阶段二](../learning/roadmap.md)
- **预计时间**: 1-2 周完成学习 + 首次对接

## 当前权威指针（2026-05-20 refresh）

- **当前候选清单**：[MD 前候选体系清单](P0-docking-md-candidate-shortlist.md)。
- **当前分析报告**：[ratio_channel_report.md](../../experiments/docking-repro/analysis/ratio_channel_report.md)；versioned release 见 `experiments/docking-repro/analysis/releases/gpr3_f_full_20260520_0854/`。
- **执行证据**：[2026-05-19 日志](../logs/2026-05-19.md)；路线校准见 [2026-05-20 日志](../logs/2026-05-20.md)。
- **当前使用边界**：候选标签、Channel A/B 方向、相对排序、关键结合残基和 IFP 机制线索可进入 MD candidate-system shortlist；Vina score 只支持排序，`Kd`、`EC50` 和 ODE 校准参数需要独立 binding/calibration 证据。

## 历史结果边界（2026-04 阶段）

2026-04-11 至 2026-04-14 的饱和扫描、双通道重读、静态 IFP 和候选集合是历史阶段结果，详见 [2026-04-11 日志](../logs/2026-04-11.md)、[2026-04-13 日志](../logs/2026-04-13.md) 和 [2026-04-14 日志](../logs/2026-04-14.md)。当前候选清单使用 2026-05-20 refreshed ratio/IFP 结果。

历史阶段留下的稳定教训：

- GprC alanine scan 的阴性对照假阳性说明“WT 基线重现”和“突变扫描残基分辨力”是两个问题；GprC 单点候选需要 refreshed ranking、IFP 和后续 gate 证据共同支持优先级。
- Saturation outlier 保留为单点异常证据；氨基酸类别规律需要同类替换一致性检查后再写入机制解释。
- ProLIF Anionic/Cationic 通道保持启用；旧失败模式来自 PDBQT-to-SDF 缺形式电荷。静态 IFP 的盐桥几何接触属于机制线索，热力学驱动需要 MD 或独立 binding evidence 支撑。
- Gpr3 pose geometry 后续改为方案 F，因此旧 Gpr3 groove-pose IFP 只能作为历史机制背景。

## 机制与 MD 边界

静态 docking/IFP 可以提出机制假说；动态稳定性、盐桥持续性、配体驻留和构象选择由 [P0-md-simulation.md](P0-md-simulation.md) 维护。当前 MD gate 聚焦：

- ARG138-羧基距离、盐桥占比和 contact lifetime。
- F170E/ECL2 相关 pose drift 与入口路径。
- 当前 refreshed 候选进入 MD 时，体系定义使用 2026-05-20 refreshed 候选集合；通过 MD gate 后，再进入更高置信度的湿实验候选构建讨论。

## 方法学局限性

| 局限性 | 影响 | 缓解 |
|--------|------|------|
| 单 seed Vina 噪声（SD=0.159） | |sel_mut| < 0.477 不可信 | Channel A/B 划分以 3σ 为阈值；5-seed 方差已量化 |
| 刚性受体 | 构象选择限于 AF3 单预测 | 单点突变对骨架影响 <0.1Å（TM helix 域内） |
| AF3 预测精度 | pLDDT>90 区域可信，loop 区不确定 | 仅在 TM helix 域内对接；annotation-based TM 提取 |
| Vina 评分精度（±1 kcal/mol） | 绝对值不精确 | 仅用排名，不用绝对值；Channel A/B 全部 >3σ |
| 静态对接提供空间富集证据 | V138R / F170E 机制需要动态证据 | 转交 [P0-md-simulation](P0-md-simulation.md)：MD 时间序列测距 + 盐桥占比 |
| ~~仅 Ala 扫描，无饱和扫描~~ | ~~04-10 之前局限~~ | **2026-04-11 解除**：5 个 Channel A 核心位点已完成 18 AA 全谱扫描（90 突变） |

## 方法学迭代记录

P0 对接方法经历三次重大迭代，每次修正了前一阶段的系统性偏差：

| 阶段 | 时间 | 关键变更 | 修正了什么 |
|------|------|---------|-----------|
| v2（MMFF） | 04-03~04 | OpenBabel + RDKit MMFF + spacing=0.25Å | 初始探索，验证 Kuo2024 排名 |
| docking-repro v1 | 04-05~06 | ADFR + Orca DFT + 两阶段对接 | 配体几何（MMFF→DFT）；发现协议不匹配 |
| docking-repro v2 | 04-07~10 | **单阶段**（匹配 Hu2024）+ **ICL3 截断** + **TM 螺旋质心** + **BW 映射修正** + **ProLIF IFP** | GprC grid box 偏移 18.1Å；ascr18 PDBQT 截断（15→26 原子）；BW→序列映射错误；v2 PLIP 残基无效（Gpr3 全部替换） |

最终方法（docking-repro v2）的 GprC ascr18 ΔG 与 Hu2024 仅差 0.05 kcal/mol。Hu2024 四个对照的分层验证结果已推翻 "4/4 通过验证" 的表述——详见上文 §Pipeline 验证 的修正（[Hu2024-GprC-summary.md:L143-145](../papers/summaries/Hu2024-GprC-summary.md)）。

## 方法演化摘要

详细版本历史和运行经过以日志为准。本文只保留会影响当前使用边界的方法节点：

| 时间 | 方法节点 | 当前解释 |
|------|---------|---------|
| 2026-04-03 ~ 2026-04-07 | 从早期探索转向 Hu2024 复现路线；改用 ADFR/Orca/单阶段 Vina、ICL3 截断、TM 螺旋质心 | 早期 v2 production 只作方法背景 |
| 2026-04-08 ~ 2026-04-14 | ProLIF/BW 映射、PDBQT 截断、双通道框架和 GprC 阴性对照问题被逐步修正 | 该阶段结果保留为历史基线；当前候选清单使用 2026-05-20 refreshed 结果 |
| 2026-04-23 ~ 2026-05-20 | Gpr2 3D offset、Gpr3 方案 F、supplemental docking、ratio/IFP/shortlist 刷新 | 当前 MD 前候选体系清单使用这一阶段的 shortlist 和结果文件 |

日志入口：

- [2026-04-11](../logs/2026-04-11.md) / [2026-04-13](../logs/2026-04-13.md) / [2026-04-14](../logs/2026-04-14.md)：历史双通道阶段和错误修正。
- [2026-04-23](../logs/2026-04-23.md)：Gpr2/Gpr3 repair route。
- [2026-05-19](../logs/2026-05-19.md)：full refresh execution evidence。
- [2026-05-20](../logs/2026-05-20.md)：shortlist 使用边界校准。

## 与其他方向的依赖关系

- **输出到**:
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 候选标签、通道方向、相对排序和校准需求；Vina score 只支持排序，`Kd`/`EC50` 需要独立 calibration 证据。
  - [P0-md-simulation](P0-md-simulation.md): MD 候选体系、机制线索和初始 pose；进入 MD 时按当前 refreshed 候选重新定义体系。
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 受体/口袋背景和候选标签，供工程路线解释。
  - [MD 前候选体系清单](P0-docking-md-candidate-shortlist.md): 当前 MD 前候选体系清单和计算边界。
- **依赖于**: 无（本方向可独立维护；MD 与后续 dose-response 证据用于后续校准）。
