---
direction: P0-molecular-docking
status: geometry_gate_v3_seed44_holdout_fail_stop_full_blocked
priority: P0
chassis_dependent: false
last_updated: 2026-07-31
---

# P0: 受体-配体分子对接与 In Silico 突变扫描

**五受体结构、对接与残基比较材料**：见 [final-docking 研究入口](final-docking/README.md)。
输入、代码、Vina/ProLIF 输出和报告分别位于既有 Docking 分类下；
Gpr2 TWF154 的结构与姿态连接到六组 MD 的输入来源。
以下撤回和恢复门禁描述旧 mutant frame-repair 批次，不代表五受体材料的新实验状态。

> 来源: PRD v3 §3.1 | iGEM 评审定位: 候选体系生成与 MD 验证前证据
>
> **2026-07-31 撤回与恢复门禁**：AF3 mutant 在 docking 前未刚体叠合到 WT docking frame，却复用了 WT frame 的绝对搜索框。受影响的 Gpr2/Gpr3 mutant score、ratio、IFP、排名和旧湿实验交付均已撤回；当前无 active shortlist 或 wetlab handoff。seed 42 + 43 WT evidence 已用于冻结 `docking-geometry-gate-v3`，随后独立 seed-44 8-job holdout 的 docking、IFP 和 geometry 全部技术完成，但 `Gpr3/R167Y` 两臂未通过冻结门，终态为 `TERMINAL_ABNORMAL / fail_stop_before_full`。不得用 holdout 结果放宽门；328-job full-run 未启动。

## 解决什么问题

核心问题：**如何改造 Gpr2/Gpr3 受体，使其对 ascr#18（PPN 富集标志物，Choe 2012 / Manosalva 2015）和 ascr#3（自由生活线虫标志物）具有差异化选择性？** 属于双通道比值型设计（`docs/prd/overview-v4.md` §双靶标判别逻辑）。旧 `ratio_channel_report.md` 只保留为 2026-05-20 历史快照；修复后的活跃候选宇宙限定为 Gpr2/Gpr3，需由新全量结果重建。

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
   - **AlphaFold 3 Server** 预测突变体全长结构 → annotation-based TM 域提取 → 用固定七 TM/147 Cα 将完整 mutant 刚体叠合到对应 WT docking frame → 仅从对齐后 PDB 用锁定版 ADFR 生成 PDBQT
   - 重对接计算 ΔΔG_selectivity = ΔΔG(ascr18) − ΔΔG(ascr3)
   - Channel A/B 双通道分类 + 跨受体配对优先级 → 形成 MD 验证候选体系清单

## 工具栈

| 工具 | 用途 | 安装 |
|------|------|------|
| AlphaFold DB | WT 结构获取 | 浏览器 |
| **AlphaFold 3 Server** | 突变体结构预测 | alphafoldserver.com（免费） |
| AutoDock Vina | 分子对接 | E2 conda package 锁定 1.2.6 |
| ADFR Suite | 受体/配体 PDBQT 准备（Hu2024 方法） | E2 锁定 ADFRsuite 1.1dev build 100，并记录 installer 与 executable SHA256 |
| OpenBabel | 配体/格式检查 | E2 conda package 锁定 3.1.1；CLI 内嵌版本字符串 3.1.0 仅保留为非权威输出 |
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
- [ ] **双通道全谱重建**：旧 266 条 merged snapshot 受 mutant frame 缺陷影响；待 162 个 Gpr2/Gpr3 mutant × 两配体及 4 个 WT baseline 全量重跑后重建
- [ ] **Channel A/B 候选重建**：公式和排序方向须在查看新分数前冻结并测试；当前无 active 候选
- [ ] **MD/wetlab shortlist 重建**：旧候选清单已撤回；不足 7 对或不能满足预冻结多样性规则时不得凑数
- [x] IFP 热图可视化（[ifp_heatmap_all_receptors.png](../../experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png)）
- [ ] Mutant IFP 全量重建（旧 [ifp_analysis_mutants_gpr3_f_full_20260520_0854/](../../experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/) 仅为撤回历史快照）
- [x] 可视化素材（历史 Channel A complex PDB + PyMOL scene 脚本；见 [analysis/pymol_top6/](../../experiments/docking-repro/analysis/pymol_top6/)）— 仅作历史样式材料；未来按修复后 shortlist 独立重建 PNG/PML
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
- **产出路径**: `experiments/docking-repro/`；目录治理和清理边界见 [docking-repro directory contract](../../experiments/docking-repro/README.md)
- **工具链**: ADFR Suite + Orca DFT B3LYP/def2-TZVP + **单阶段对接**（40Å/0.1/exh=200） + **AF3 突变体结构预测** + **ProLIF IFP 分析**
- **远程计算入口**: 历史刷新曾使用 Slurm GPU 集群；新服务器/远程计算任务统一先读 [NKULiulab E2 共享云服务器使用规范](../ops/nkuliulab-e2-cloud-server.md)，Windows 7500F 和 Slurm 仅作历史 artifact / 旧运行记录参考
- **关键技术修复**:
  - ICL3 截断 + TM 螺旋质心（修复 GprC grid box 偏移 18.1Å）
  - Annotation-based TM 域提取（UniProt + DeepTMHMM 交叉验证）
  - ascr18 PDBQT freeze_terminal_torsions bug 修复（15→26 原子）
- **状态**: **geometry_gate_v3_seed44_holdout_fail_stop_full_blocked**（2026-07-31）。当前无 active ratio/IFP/shortlist/handoff；新门已在 holdout 前冻结，seed-44 独立 holdout 8/8 docking、IFP 和 geometry 技术完成，但 `Gpr3/R167Y-ascr18` 为 14/16、`Gpr3/R167Y-ascr3` 为 11/18 且后者 MODEL 1 失败。失败终态已固化，full-run 未启动；详见[重校准决策包](../../codex/docs/plans/docking-geometry-gate-recalibration-decision-20260730.md)

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

## 当前权威指针（2026-07-31 seed-44 holdout fail-stop）

- **当前状态权威**：[INDEX](../INDEX.md) 和本文件。
- **目录治理与历史边界**：[docking-repro directory contract](../../experiments/docking-repro/README.md)。
- **撤回快照**：`temp/withdrawn/docking_wetlab_handoff_20260729.snapshot/`；原路径只保留撤回 tombstone。
- **本地对齐前置 run**：`temp/docking_frame_repair_20260730_local_frame_v2/`，run identity `1e1c07f3553ae0f26c44f5163ac75cd88f20a478af524269c19efea31ed3c52a`。162/162 mutant aligned PDB 与 2 个 WT identity-frame manifest 已完成；该 run 只作对齐前置证据，不是当前 smoke/result root。
- **历史 E2 R1 smoke run（冻结新门前）**：`temp/docking_frame_repair_20260730_e2_smoke_r1_v5/`，run identity `950639bdc788bf23a3cacc61d57dfa130ea05872f3d64663f87b88e567f6bce8`。终态原始权威为 `terminal/smoke_terminal.json`，terminal identity `abbcad305e305004c328b75c7be9c82b4981d0ee60286e90a093c49c9b1f3c3f`，状态 `fail_stop_before_full` / `TERMINAL_ABNORMAL`。v3/v4 保持不可变历史 fail-stop。
- **E2 WT calibration run**：`temp/docking_frame_repair_20260731_e2_wt_calibration_seed43_r3/` 复用同一 source frame/environment，固定 seed 43，只运行 Gpr2/Gpr3 WT × ascr18/ascr3 四项。4/4 docking 正常完成并各返回 20 poses，4/4 IFP 与 4/4 历史门诊断完成；`RUN_FILES.sha256` 的 59/59 条目在远端和本地均通过。旧门诊断为 Gpr2 两臂失败、Gpr3 两臂通过；new gate 保持 `not_frozen`。详细数值与资源审计见 [2026-07-31 日志](../logs/2026-07-31.md)。
- **冻结门**：`experiments/docking-repro/geometry-gates/20260731_seed42_seed43_wt_v1/geometry_gate.json` 只使用 seed 42 + 43 WT evidence，artifact SHA256 `7b74b8335c18eeb2548d32dbe0b5cdf823f34dc2bf22f09061c8a750afb62d8d`，gate identity `5b59c1d36b3b5e89e0c67ed9846c2b76b48bf1ca5ce8af9873a8562565740924`。其 allowed use 仅为独立 holdout，以及仅在 holdout 通过后进入绑定的 full matrix。
- **seed-44 独立 holdout**：当前权威 run 为 `temp/docking_frame_repair_20260731_e2_full_seed44_r1/`，run identity `4496efeedc527d870fff06c5e61b49ef811b0c27045b739846e4471a97c0af69`。8/8 docking、IFP、geometry 技术完成；Gpr2 四项和 Gpr3 WT 两项通过，Gpr3 R167Y–ascr18 为 14/16，R167Y–ascr3 为 11/18 且 MODEL 1 失败。terminal identity `43967837a7473c1a422df31e87924e727b1d9a54a1fe933f1252712bb7b5bbfa`，状态 `TERMINAL_ABNORMAL / fail_stop_before_full`。1,089/1,089 远端与本地 checksum 通过；full plan 和剩余 320 jobs 均未启动。
- **PyMOL 人工审查入口与结论**：`tmp/wt_calibration_seed43_pose_review.ipynb` 可列出每条 WT arm 的全部 pose，并把指定 `pose_index` 真正抽取为单一 ligand state；当前 pose 的 4 Å pocket、逐原子 ProLIF interaction table 和分类虚线均与其他 pose 隔离。用户已确认四条 WT arm 的 MODEL 1 / pose 1 结合位置目视合理，本次 visual-review gate 完成；这不等于 20 个 pose 已逐一选优，也不会自动冻结 geometry gate。全部 poses 叠加模式不生成误导性的 union pocket；虚线只表示 ProLIF 几何相互作用分类，不是测得的力或共价键。Gpr2/ascr18 pose 11 仍是当前报告明确定位的胞内侧错误 pose，详见 [2026-07-31 日志](../logs/2026-07-31.md)。
- **历史 R1 smoke 范围（冻结新门前）**：8 个唯一 jobs 均一次完成且没有重试。6 个 job 返回 20 poses，Gpr3 R167Y–ascr#18/ascr#3 各返回 18 poses；maximum-20 validator 正确接受两者，四类绝对 pose-population 下限和全部 job provenance 均通过。8/8 IFP 完成，旧 geometry 门仅 3/8 job 通过，未创建 full job plan、未启动剩余 320 jobs。
- **历史 R1 geometry 终态（冻结新门前）**：通过者为 Gpr2 R59C–ascr#3、Gpr3 WT–ascr#18 和 Gpr3 WT–ascr#3。失败者的“合格 poses / 预冻结下限”为 Gpr2 WT–ascr#18 17/19、Gpr2 WT–ascr#3 17/18、Gpr2 R59C–ascr#18 18/19、Gpr3 R167Y–ascr#18 12/15、Gpr3 R167Y–ascr#3 9/15；后者 MODEL 1 的膜绝对高度 107.520 Å，低于冻结的 108.5 Å 下限。其余四个失败 job 的 MODEL 1 均通过。
- **geometry transfer 审计**：两项 Gpr2 WT baseline 的 MODEL 1 均通过。ascr18 的两个 pose 仅越过旧高度边界 0.033/0.053 Å，另一个 pose 位于约 31.2 Å 外的错误高度簇；ascr3 当前有 3 个错误高度簇 pose，而历史单次 calibration 只有 2 个。Gpr2 旧门来自 Slurm Vina 1.2.5 单次 ensemble 的零 margin 极值和实际合格数；Gpr3 旧 Windows calibration 缺少完整工具链身份。历史/current WT receptor PDBQT 规范化后相同，ligand PDBQT 哈希也相同，因此输入替换不是差异来源。结论是旧门不能直接充当 E2/Vina 1.2.6 跨工具链 hard gate；详见[重校准决策包](../../codex/docs/plans/docking-geometry-gate-recalibration-decision-20260730.md)。
- **解释边界**：seed-44 holdout 只支持“技术链完成、冻结 geometry gate 失败并停止”。不得把 mutant geometry 差异解释为生物学效应，不得根据 holdout 调低阈值，也不得绕过失败终态启动 full-run。
- **18/20 成因审计**：Vina v1.2.6 的 `num_modes` 是最大输出数；RMSD 去重后少于 20 属合法输出。三次 18-mode 输出均有完整表和连续 MODEL，能量跨度仅 1.118/1.192 kcal/mol，不是 `energy_range=3.0` 截断。R167Y–ascr18 在 v3 CPU8 和 v4 两次尝试的 pose SHA256 均为 `1ac5be6c79be7bd85b6bf1f5cd33c7ef440dd61eac3a16152b0d394999e23e69`，原合同重试无恢复价值。
- **v4 CPU 边界**：v4 九条 Vina 命令全部缺少 `--cpu 8`，且 CPU 未进入 job plan、environment compute record 或 job identity；因此 v4 只支持 18-mode 可重复性和终态审计，不能晋升为 production smoke。
- **历史 R1 已执行恢复合同**：[18-mode recovery contract](../../codex/docs/plans/docking-frame-repair-18mode-recovery-contract-20260730.md)。R1 已将 20 解释为 maximum，沿用当时的绝对 `min_passing_modes`，显式传 CPU8 并绑定完整 invocation；执行结果是技术链通过、旧 geometry 门 fail-stop。
- **E2 工具链**：Vina conda 1.2.6、OpenBabel conda 3.1.1、ADFRsuite 1.1dev build 100；精确 package lock 为 `environments/e2-docking-frame-repair.lock.yml`。4 个 smoke receptor PDBQT 的共同重原子坐标差均为 0.0 Å。
- **归档完整性**：R1 run 的 `RUN_FILES.sha256` 列出 608 个远端文件，manifest SHA256 为 `1f5773d92a9d9abbcd63b2cf9599a03fca3694aca048bf9bbbbafec3d26dfd4b`；本地 608/608 校验通过，目录另含该 manifest 本身。
- **本地验证**：截至 2026-07-31，WT-calibration、frame-repair 和 multi-mutant unittest 合计 38/38 通过；新 runner/finalizer syntax、launch shell、notebook JSON/路径/pose count、逐原子 ProLIF sidecar identity 和本机 PyMOL 单-pose 抽取均通过。当前 `docking` conda 环境没有 pytest，未修改环境；详细经过见 [2026-07-31 日志](../logs/2026-07-31.md)。
- **旧分析边界**：`ratio_channel_report.md`、2026-05-20 release、旧 IFP roots 和 [MD 前候选体系清单](P0-docking-md-candidate-shortlist.md) 均为历史证据，不是 current 坐标、排名或候选权威。
- **当前使用边界**：seed-44 holdout score/pose/IFP 只支持本次技术与几何门审计；不得用于 ratio、排名或候选。新的恢复决策、通过的独立 holdout、全量重跑和候选审计全部完成前，不得发布候选或生成新湿实验交付。

## 历史结果边界（2026-04 阶段）

2026-04-11 至 2026-05-20 的突变扫描、双通道重读、静态 IFP 和候选集合均保留为历史阶段结果。2026-05-20 refreshed ratio/IFP 也受 mutant frame 缺陷影响，不能再作为当前候选来源。

历史阶段留下的稳定教训：

- GprC alanine scan 的阴性对照假阳性说明“WT 基线重现”和“突变扫描残基分辨力”是两个问题；该线只保留为历史方法证据，不进入本次 Gpr2/Gpr3 repaired candidate universe。
- Saturation outlier 保留为单点异常证据；氨基酸类别规律需要同类替换一致性检查后再写入机制解释。
- ProLIF Anionic/Cationic 通道保持启用；旧失败模式来自 PDBQT-to-SDF 缺形式电荷。静态 IFP 的盐桥几何接触属于机制线索，热力学驱动需要 MD 或独立 binding evidence 支撑。
- Gpr3 pose geometry 后续改为方案 F，因此旧 Gpr3 groove-pose IFP 只能作为历史机制背景。

## 机制与 MD 边界

静态 docking/IFP 可以提出机制假说；动态稳定性、盐桥持续性、配体驻留和构象选择由 [P0-md-simulation.md](P0-md-simulation.md) 维护。当前 MD gate 聚焦：

- ARG138-羧基距离、盐桥占比和 contact lifetime。
- F170E/ECL2 相关 pose drift 与入口路径。
- 已完成的 R59C/R167Y MD 只能描述其实际旧起始 pose 的单重复探索性轨迹，不能验证修复后的候选排名；新候选需在 docking 全量纠错后另行定义。

## 方法学局限性

| 局限性 | 影响 | 缓解 |
|--------|------|------|
| 单 seed Vina 噪声（SD=0.159） | |sel_mut| < 0.477 不可信 | Channel A/B 划分以 3σ 为阈值；5-seed 方差已量化 |
| 刚性受体 | 构象选择限于 AF3 单预测 | 单点突变对骨架影响 <0.1Å（TM helix 域内） |
| AF3 预测精度 | pLDDT>90 区域可信，loop 区不确定；独立 mutant 原始 frame 不可直接与 WT 绝对 box 比较 | 七 TM/147 Cα 刚体叠合；全 162 个 mutant 对齐后 TM RMSD 为 0.236–0.675 Å；完整 receptor 使用同一变换 |
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
| 2026-04-08 ~ 2026-04-14 | ProLIF/BW 映射、PDBQT 截断、双通道框架和 GprC 阴性对照问题被逐步修正 | 该阶段结果保留为历史基线；其候选结论不参与当前冲突裁决 |
| 2026-04-23 ~ 2026-05-20 | Gpr2 3D offset、Gpr3 方案 F、supplemental docking、ratio/IFP/shortlist 刷新 | 历史方法与缺陷快照；mutant frame 未统一，不能作为当前排名或候选 |
| 2026-07-30 | mutant→WT 七 TM 刚体对齐、frame/geometry/provenance validator、E2 锁定工具链、18-mode 审计及 R1 8-job smoke | aligned receptor PDBQT 通过 frame check；maximum-20 与显式 CPU8 技术合同通过，8/8 IFP 完成；5/8 job 未通过预冻结 geometry 分布门，含两项 Gpr2 WT baseline，故终止在 full-run 前并转入 WT calibration/几何门审计 |

日志入口：

- [2026-04-11](../logs/2026-04-11.md) / [2026-04-13](../logs/2026-04-13.md) / [2026-04-14](../logs/2026-04-14.md)：历史双通道阶段和错误修正。
- [2026-04-23](../logs/2026-04-23.md)：Gpr2/Gpr3 repair route。
- [2026-05-19](../logs/2026-05-19.md)：full refresh execution evidence。
- [2026-05-20](../logs/2026-05-20.md)：shortlist 使用边界校准。

## 与其他方向的依赖关系

- **输出到**:
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 候选标签、通道方向、相对排序和校准需求；Vina score 只支持排序，`Kd`/`EC50` 需要独立 calibration 证据。
  - [P0-md-simulation](P0-md-simulation.md): 历史 R59C/R167Y 起始 pose 与单重复探索性轨迹；不得用于验证修复后的排名。
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 受体/口袋背景和候选标签，供工程路线解释。
  - [MD 前候选体系清单](P0-docking-md-candidate-shortlist.md): 已撤回 shortlist 的历史边界。
- **依赖于**: 无（本方向可独立维护；MD 与后续 dose-response 证据用于后续校准）。
