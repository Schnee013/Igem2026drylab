---
direction: P0-molecular-docking
status: reanalysis
priority: P0
chassis_dependent: false
last_updated: 2026-04-27
---

# P0: 受体-配体分子对接与 In Silico 突变扫描

> 来源: PRD v3 §3.1 | iGEM 评审定位: 直接支撑湿实验设计
>
> **2026-04-27 校准**：本方向从“计算完成”退回 **reanalysis**。Gpr2 旧 Ala/Sat 数据存在 grid/offset 污染，已于 2026-04-23 用 3D offset 重跑；Gpr3 旧 pose 存在 TM-POPC groove 污染，方案 F（ECL2 manual box=20 Å）几何 PASS 且 Ala/Sat 结果已生成。旧 `ratio_channel_report.md` 早于 Gpr3 F 全量结果，不能作为最终湿实验 Top 配对权威；下一步是合并 Gpr3 F 结果、重跑 ratio/IFP 并刷新湿实验交接。详见 [2026-04-23 日志](../logs/2026-04-23.md) 与 [INDEX](../INDEX.md)。

## 解决什么问题

核心问题：**如何改造 Gpr2/3/GprC 受体，使其对 ascr#18（PPN 富集标志物，Choe 2012 / Manosalva 2015）和 ascr#3（自由生活线虫标志物）具有差异化选择性？** 属于双通道比值型设计（`docs/prd/overview-v4.md` §双靶标判别逻辑）。突变按 sel_mut 双向分类为 Channel A（ascr#18 偏好）/ Channel B（ascr#3 偏好）/ neutral，跨受体配对形成传感器对。注意：2026-04-14 版完整分析 [`ratio_channel_report.md`](../../experiments/docking-repro/analysis/ratio_channel_report.md) 是历史基线，当前等待 Gpr3 方案 F 结果合并刷新。

文献（Hu2024、Kuo2024）已给出 WT 受体的结合亲和力排名。干实验的真正价值在于**预测增强选择性的突变位点**，为湿实验组的定点突变设计提供计算依据。

**iGEM 价值（DBTL cycle）**:
- **Design**: 本方向产出 → 推荐突变位点（ΔΔG_selectivity < -0.5 kcal/mol）
- **Build**: 湿实验组据此设计定点突变实验
- **Test**: 湿实验实测突变体结合活性
- **Learn**: 实验结果反馈回模型，校准对接预测准确度

## 方法路线

1. 从 AlphaFold DB 获取 Gpr3/Gpr2/GprC WT 预测结构
2. 使用 AutoDock Vina **单阶段对接**（box=40Å, spacing=0.1Å, exh=200, seed=42，匹配 Hu2024 参数）建立 WT 基线
3. **ProLIF IFP 分析**结合口袋关键残基（验证 Hu2024 已知位点，发现新接触残基；IFP 交叉验证排除无效残基）
4. **In silico 突变扫描（核心新增）**：
   - **AlphaFold 3 Server** 预测突变体全长结构 → annotation-based TM 域提取 → ADFR 准备 PDBQT
   - 重对接计算 ΔΔG_selectivity = ΔΔG(ascr18) − ΔΔG(ascr3)
   - Channel A/B 双通道分类 + 跨受体配对推荐 → 供湿实验组验证

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
- [~] **双通道全谱排名**：2026-04-14 版 122 突变体已生成，但 Gpr2/Gpr3 修复后需刷新；旧 [ratio_channel_report.md](../../experiments/docking-repro/analysis/ratio_channel_report.md) 暂作历史基线，不作最终权威
- [x] **Channel A 候选**（14 条无 caveat）+ **Channel B 候选**（11 条无 caveat）— 3σ 阈值 = ±0.477
- [ ] **跨受体配对推荐刷新**：旧 Top 3（M327A/V138T 等）受 Gpr2/Gpr3 旧数据影响；待 Gpr3 F 合并后重算
- [x] IFP 热图可视化（[ifp_heatmap_all_receptors.png](../../experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png)）
- [x] Channel A Top 6 mutant IFP 分析（[ifp_analysis_mutants/](../../experiments/docking-repro/results/ifp_analysis_mutants/)）
- [x] 可视化素材（Channel A Top 6 complex PDB + PyMOL scene 脚本；见 [analysis/pymol_top6/](../../experiments/docking-repro/analysis/pymol_top6/)）— 渲染交付 PI 的 PNG/PSE 待补
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
- **计算节点**: Windows 7500F（通过 Tailscale SSH 远程调用）
- **关键技术修复**:
  - ICL3 截断 + TM 螺旋质心（修复 GprC grid box 偏移 18.1Å）
  - Annotation-based TM 域提取（UniProt + DeepTMHMM 交叉验证）
  - ascr18 PDBQT freeze_terminal_torsions bug 修复（15→26 原子）
- **状态**: **reanalysis**（2026-04-27）。早期 32 alanine + 90 saturation 结果已形成历史基线；Gpr2 3D offset 与 Gpr3 方案 F 修复后需重算 ratio/IFP/湿实验推荐

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

## 当前 reanalysis 状态（2026-04-27）

- **Gpr2**：3D offset WT/Ala/Sat 重跑完成；旧 Gpr2 结果不再作为权威。2026-04-23 版 ratio 已纳入 Gpr2 修复，但仍混用旧 Gpr3/GprC 数据。
- **Gpr3**：旧 pose 确认偏向 TM-POPC groove；方案 F 使用 ECL2 manual box center `[0.42, 7.16, -17.11]`、box=20 Å，WT pose 几何全线 PASS；Gpr3 F Ala/Sat 结果文件已生成。
- **当前阻塞**：合并 Gpr3 F Ala/Sat 到全量 mutagenesis JSON，重跑 `ratio_channel_analysis.py`，再刷新 `ratio_channel_report.md` / `ratio_pairings.csv` / IFP 与湿实验交接。
- **使用纪律**：本节以下 2026-04-14 “结果概览”是历史结果，不能直接作为最终推荐；如需候选优先级，先查 [INDEX](../INDEX.md) 与最新日志。

## 历史结果概览（2026-04-14，双通道分析；待刷新）

历史双通道全谱排名见 [ratio_channel_report.md](../../experiments/docking-repro/analysis/ratio_channel_report.md)（2026-04-14 版历史报告，Alanine 32 + Saturation 90 = 122 条合并；待 Gpr3 F 合并后刷新）。IFP 热图见 [ifp_heatmap_all_receptors.png](../../experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png)。

122 条按 sel_mut 全谱排列，Channel A（sel_mut < −0.477，ascr#18 偏好，14 条无 caveat + 1 条 GprC-ala caveat）和 Channel B（sel_mut > +0.477，ascr#3 偏好，11 条无 caveat + 3 条 GprC-ala caveat），跨受体配对排名 Top 1：Gpr2_M327A + Gpr3_V138T（D=−2.433，balance=0.572）。

### Pipeline 验证

**结论更新（2026-04-12）**：先前 "4/4 Hu2024 对照 |ΔΔG_sel| 全部显著 → Pipeline 通过验证" 的表述**错误地把 N56A（阴性对照）当成阳性对照**。按 Hu2024 原文（[Hu2024-GprC-summary.md:143-145](../papers/summaries/Hu2024-GprC-summary.md#L143)）真实角色重新核对后：

- **真阳性对照（3 个，预期方向一致偏移）**：N60A (N2.57, +0.396 = 2.5σ)、R395A (R6.45, +0.370 = 2.3σ)、S44A (S2.41, +1.032 = 6.5σ)——ΔΔG_sel 方向全部一致且 > 2σ ✓（注：N60A/R395A 未过 Channel 分类的 3σ 阈值，但方向一致性为阳性对照验证的核心判据）
- **真阴性对照（1 个，预期 |ΔΔG_sel| 在噪声内）**：N56A (N2.53，Hu2024 "无功能影响")——**实际 |ΔΔG_sel| 大幅偏移 ❌**，ΔΔG_sel = +1.139 (7.2σ)，ΔΔG(ascr18) = +2.696，**扰动幅度大于任何阳性对照**（N60A +0.396、R395A +0.370、S44A +1.032）
- **GprC 整体分辨力**：14 个 scan 残基中 **13 个** |ΔΔG_sel| > 2σ（唯一例外 L377A ΔΔG_sel = +0.04 在噪声内），Channel A/B 无 caveat 候选**全部来自 Gpr2/Gpr3**

**因此 "Pipeline 通过验证" 的论断不成立**。可以确认的是：
1. Vina alanine scan 在 GprC 上对**阴性对照给出了最强的假阳性**之一，现有 3σ 阈值**不能可靠区分 GprC 的功能性残基**
2. GprC 单点突变不适合作为湿实验候选；本方向的 Channel A/B 无 caveat 候选全部来自 Gpr2/Gpr3 与此一致

根因尚未锁定，存在至少两种不互斥解释、需进一步实验区分：
- (a) **pipeline 普遍假阳性**：单点 Ala 扰动放大打分偏差
- (b) **GprC 口袋几何特异**：口袋浅 / 接触残基密集，任何接触残基的单点替换都破坏结合（此时 sel_mut 显著偏移对接触残基本身是真阳性，但 pipeline 对 "结合必需 vs. 功能中性" 无分辨力）

> 待办：对比 Gpr2/Gpr3 是否有已知阴性对照可测，或对 GprC 重做不同 box/seed 控制。`docs/logs/truth-audits/2026-04-12_0205.md` 记录了本次推翻的完整推导。

WT 基线复现不受影响：GprC ascr18 **ΔG = −8.235 kcal/mol**（Hu2024: −8.29，**Δ = 0.05 kcal/mol**）——绝对 ΔG 的重现性和 alanine scan 的残基分辨力是两个独立问题。

### 双通道分布（122 条）

| 通道 | 含义 | 数量 | sel_mut 区间 |
|------|------|------|--------------|
| Channel A | ascr#18 偏好 | 15 | < −0.477 |
| neutral | 噪声内 | 93 | −0.477 ~ +0.477 |
| Channel B | ascr#3 偏好 | 14 | > +0.477 |

3σ 阈值 = ±0.477（噪声 SD=0.159 来自 5-seed 方差评估）。其中 Channel A 含 1 条 GprC-ala caveat，Channel B 含 3 条 GprC-ala caveat（分辨力存疑，详见 §Pipeline 验证）。

### Channel A: ascr#18 偏好（前 5 / 共 14 条无 caveat）— 按 sel_mut 升序

| # | 受体 | 突变 | 类型 | sel_mut | ΔG(ascr18) | ΔG(ascr3) |
|---|------|------|------|---------|------------|-----------|
| 1 | Gpr2 | **M327A** | Ala | **−1.391** | −6.74 | −5.35 |
| 2 | Gpr2 | **M327D** | Sat | **−1.089** | −6.67 | −5.58 |
| 3 | Gpr2 | **R59F** | Sat | **−0.956** | −6.66 | −5.70 |
| 4 | Gpr2 | **R59A** | Ala | **−0.925** | −6.53 | −5.60 |
| 5 | Gpr3 | **V138R** | Sat | **−0.875** ⭐ | −6.14 | −5.26 |

完整 14 条见 [ratio_channel_report.md §3](../../experiments/docking-repro/analysis/ratio_channel_report.md)。

### Channel B: ascr#3 偏好（前 5 / 共 11 条无 caveat）— 按 sel_mut 降序

| # | 受体 | 突变 | 类型 | sel_mut | ΔG(ascr3) | ΔG(ascr18) |
|---|------|------|------|---------|-----------|------------|
| 1 | Gpr3 | **V138T** | Sat | **+1.042** | −6.05 | −5.01 |
| 2 | Gpr3 | **V138L** | Sat | +0.886 | −5.70 | −4.82 |
| 3 | Gpr2 | **M327G** | Sat | +0.749 | −5.63 | −4.88 |
| 4 | Gpr3 | **V138P** | Sat | +0.736 | −5.50 | −4.77 |
| 5 | Gpr3 | **R175A** | Ala | +0.663 | −5.97 | −5.30 |

完整 11 条见 [ratio_channel_report.md §4](../../experiments/docking-repro/analysis/ratio_channel_report.md)。

### 跨受体配对推荐 Top 3

| # | Channel A | Channel B | D | balance |
|---|-----------|-----------|---|---------|
| 1 | Gpr2_M327A (sel=−1.391) | Gpr3_V138T (sel=+1.042) | −2.433 | 0.572 |
| 2 | Gpr2_M327A (sel=−1.391) | Gpr3_V138L (sel=+0.886) | −2.277 | 0.611 |
| 3 | Gpr2_M327D (sel=−1.089) | Gpr3_V138T (sel=+1.042) | −2.131 | 0.511 |

D = sel_A − sel_B（越负 = 判别力越强）；balance = |sel_A|/(|sel_A|+|sel_B|)（理想=0.5）。完整配对排名见 [ratio_channel_report.md §5](../../experiments/docking-repro/analysis/ratio_channel_report.md)。

> **历史湿实验建议（已冻结，勿直接下发）**：2026-04-14 版曾优先配对 Gpr2_M327A + Gpr3_V138T；该建议需等 Gpr2/Gpr3 修复后重新计算。当前以 [INDEX](../INDEX.md) 的 reanalysis 待办为准。

## 饱和扫描结果与三大新发现

04-11 在 5 个 Channel A 核心位点（Gpr2 M327/R59 + Gpr3 I141/F170/V138）做了 18 AA 全谱饱和扫描（90 突变体 × 2 配体 = 180 次对接），相较 04-10 alanine-only 版有以下重大补充：

### 1. Gpr3 V138R 最重磅发现 ⭐⭐⭐

Gpr3 WT 选择性 sel=+0.195 在 3σ 噪声内（方向轻微偏 ascr3）。V138R 单点突变后翻转到 abs sel=−0.88，**首次穿透 Gpr3 的噪声阈值**，与 Gpr2 WT（−0.40）同量级且更优。ΔG(18)=−6.14 比 WT −5.72 更强，"增强一侧 + 削弱另一侧"双效应。

### 2. Gpr3 F170 酸性残基规则

F170E（sel=−0.50）进入 Channel A，F170D（sel=−0.44）在 neutral 边缘，方向一致（增强 ascr#18 + 削弱 ascr#3）。F170 位于 ECL2，酸性替换的影响可能来自配体进入路径或入口处的静电互补，而非深层口袋重塑。**F170→酸性 + V138→Arg 组合可能叠加**（未验证）。

### 3. Gpr2 M327 同位点两条路径

- **M327A**（−1.39 abs sel）：纯粹"移除 ascr3 专属相互作用"，Ala 去除侧链。
- **M327D**（−1.09 abs sel）：引入羧基，**主动**加强 ascr18 偏好。
- 湿实验取舍：要"保亲和力 + 增强选择性" → M327A；要"激进调节方向性" → M327D。

### 教训：孤峰 vs 类别规律

V138 全 18 谱中 V138R **是孤峰**而非类别规律——同为碱性的 V138K/V138H 与 V138A 基线几乎等价，远不如 V138R 强；V138Y/N/S/I 的 sel_mut 落在 neutral moderate 区间，远不及 V138R。**碱性/正电荷"类别规律"不成立**，更像是 Arg 胍基特异的侧链长度 + 几何取向效应。湿实验不应默认 K/H 作为 R 的等价替代。

> 该教训已写入 memory（feedback_outlier_vs_rule.md）。后续设计推断前应先做同类一致性检查。

## 机制假说（V138R 盐桥）

Gpr3 V138R 的 mutant IFP 最新结果（2026-04-15 电荷注入修复后，数据源 `mutant_contacts.csv`）：

| 配体   | Anionic | Hydrophobic | VdWContact | 总计 |
| ------ | ------: | ----------: | ---------: | ---: |
| ascr18 |       2 |           3 |          9 |   14 |
| ascr3  |   **3** |           3 |          2 |    8 |

**技术说明（修复前）**：ProLIF 的 Anionic/Cationic 在 PDBQT 工作流下结构性失效（PDBQT→SDF 不编码形式电荷，SMARTS 匹配永远为空）。2026-04-15 通过 `fix_sdf_valence(template_smiles)` + `fix_receptor_charges()` 注入 pH 7.4 形式电荷，修复已验证（WT GprC ARG395（暂标 Hu2024 R6.45；BW 编号有争议，见 config.yaml）Anionic=4）。

**结论**：证据不一致——

- **支持假说方向**：VdW 富集 ascr18 远大于 ascr3（9 vs 2），与"ARG138 对较长链配体空间容纳更好"一致
- **与假说方向相反**：Anionic 计数 ascr3（3）> ascr18（2），说明 ascr3 的羧基与 ARG138 在 Vina 选出的 pose 中也满足盐桥几何——Anionic 结果不能作为"选择性支持 ascr18"的证据
- 总体结论：**静态 pose 中两个配体均与 ARG138 有盐桥几何接触，不能从 IFP 区分选择性**
- **不能回答**：盐桥是否热力学驱动（Vina 无静电项，pose 由无电荷世界选出）

**实证路径**：

1. **MD 模拟**测量 ARG138-羧基距离的时间序列与盐桥占比 → 转交 [P0-md-simulation](P0-md-simulation.md)（首选，力场自动分配电荷态 + 显式溶剂 + 动力学采样，能同时回答 pose 稳定性问题）

F170E 反直觉现象（GLU170 本身与 ascr3 接触更多但整体 ΔG(ascr3)=+0.17 上升）也无法用静态对接 + IFP 解释，同样需 MD 实证。

## 方法学局限性

| 局限性 | 影响 | 缓解 |
|--------|------|------|
| 单 seed Vina 噪声（SD=0.159） | |sel_mut| < 0.477 不可信 | Channel A/B 划分以 3σ 为阈值；5-seed 方差已量化 |
| 刚性受体 | 构象选择限于 AF3 单预测 | 单点突变对骨架影响 <0.1Å（TM helix 域内） |
| AF3 预测精度 | pLDDT>90 区域可信，loop 区不确定 | 仅在 TM helix 域内对接；annotation-based TM 提取 |
| Vina 评分精度（±1 kcal/mol） | 绝对值不精确 | 仅用排名，不用绝对值；Channel A/B 全部 >3σ |
| 静态对接无法证明动态相互作用类型（如盐桥） | V138R / F170E 机制仅有空间富集证据 | 转交 [P0-md-simulation](P0-md-simulation.md)：MD 时间序列测距 + 盐桥占比 |
| ~~仅 Ala 扫描，无饱和扫描~~ | ~~04-10 之前局限~~ | **2026-04-11 解除**：5 个 Channel A 核心位点已完成 18 AA 全谱扫描（90 突变） |

## 方法学迭代记录

P0 对接方法经历三次重大迭代，每次修正了前一阶段的系统性偏差：

| 阶段 | 时间 | 关键变更 | 修正了什么 |
|------|------|---------|-----------|
| v2（MMFF） | 04-03~04 | OpenBabel + RDKit MMFF + spacing=0.25Å | 初始探索，验证 Kuo2024 排名 |
| docking-repro v1 | 04-05~06 | ADFR + Orca DFT + 两阶段对接 | 配体几何（MMFF→DFT）；发现协议不匹配 |
| docking-repro v2 | 04-07~10 | **单阶段**（匹配 Hu2024）+ **ICL3 截断** + **TM 螺旋质心** + **BW 映射修正** + **ProLIF IFP** | GprC grid box 偏移 18.1Å；ascr18 PDBQT 截断（15→26 原子）；BW→序列映射错误；v2 PLIP 残基无效（Gpr3 全部替换） |

最终方法（docking-repro v2）的 GprC ascr18 ΔG 与 Hu2024 仅差 0.05 kcal/mol。Hu2024 四个对照的分层验证结果已推翻 "4/4 通过验证" 的表述——详见上文 §Pipeline 验证 的修正（[Hu2024-GprC-summary.md:L143-145](../papers/summaries/Hu2024-GprC-summary.md)）。

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
| 2026-04-06 | v2.3 | Orca DFT 配体全面重跑；发现并清理 MMFF 残留配体；12-bug 审计修复 + preflight_check 机制 | MMFF→Orca 配体几何一致性 |
| 2026-04-07 | v2.4 | 单阶段对接（`dock_pair_singlestage`）取代两阶段；TM 螺旋质心修复 GprC grid box 偏移 18.1Å；ICL3 annotation-based 截断；AF3 替代 FoldX | 方法偏差诊断：ICL3 拉偏质心、ascr18 PDBQT 截断 |
| 2026-04-07~08 | v2.5 | ProLIF IFP 分析；BW→序列映射修正（N2.57=ASN60, S2.41=SER44）；ascr18 PDBQT 修复（15→26 原子）；GprC ascr18 ΔG=−8.235（Hu2024 Δ=0.05） | IFP 交叉验证 + BW 映射纠错 |
| 2026-04-08~09 | v2.6 | 单一权威源重构（4 文件硬编码→config-driven）；全脚本动态路径重构（6 辅助脚本） | DOCMAP §1 原则落地 |
| 2026-04-09 | v2.7 | Gpr3 scan_residues 全量替换为 IFP 残基（v2 PLIP 8 个→IFP 8 个）；Gpr3 alanine scan 完成（I141A ΔΔG_sel=−0.786） | Truth Audit 发现 v2 PLIP 残基全部无效 |
| 2026-04-10 | **v3.0** | 32 突变体全量 alanine scan 完成；双通道分类完成；Gpr2 IFP 验证（9/9 PASS）；**本文档更新至 Wiki 初版** | P0 计算阶段完成，进入输出阶段 |
| 2026-04-11 | **v3.1** | 90 饱和扫描合并 → 双通道全谱排名（122 条）；Channel A Top 6 推荐替换原 3 条；新增"饱和扫描结果与三大新发现""机制假说未实证（V138R 盐桥）"小节；alanine-only 局限性解除；机制实证转交 P0-md-simulation | 饱和扫描完成 + 底盘锁定酵母后湿实验候选审查 |
| 2026-04-12 | v3.2 | §Pipeline 验证重写：N56A 阴性对照假阳性推翻 "4/4 通过验证"；进展记录 04-10 条目修正真阳性/真阴性角色 | Truth Audit 发现阳性/阴性对照混淆 |
| 2026-04-13 | v3.3 | 新增 ratio_channel_report.md 双通道全谱分析 + 跨受体配对排名 | ratio_channel_report.md 完成 |
| 2026-04-14 | **v3.4** | 全文清除单通道分析（Tier 1-4）痕迹，统一为双通道框架（Channel A/B + 跨受体配对）；产出定义、结果概览、Pipeline 验证、饱和扫描叙述全面重写 | PRD 回溯审查，纠正分析框架错误 |
| 2026-04-27 | v3.5 | 状态改为 reanalysis；标记 Gpr2/Gpr3 修复后旧 Top/ratio/湿实验推荐待刷新 | 2026-04-23/24 Gpr2 3D offset 与 Gpr3 方案 F 重跑 |

## 进展记录

| 日期 | 事件 | 关键数据 |
|------|------|---------|
| 2026-04-04 | v2 pipeline production 完成（exh=200，481.7 min） | Gpr2 ascr7=−6.654, ascr3=−6.282; Gpr3 ascr3=−6.284, ascr7=−6.238; GprC ascr18=−6.048, ascr3=−6.445; Kuo2024 排名全部 PASS |
| 2026-04-04 | docking-repro pipeline 代码完成 | mutagenesis.py 支持 alanine/saturation 两种扫描模式 |
| 2026-04-04 | docking-repro Windows 环境：Orca 6.1.1 已安装，ascr18 DFT 优化中 | 21:09 已到第 13 个几何优化 cycle，ascr3/ascr7 待启动 |
| 2026-04-05 | 完整 alanine scan 完成（27/28 突变体，3 受体 × PLIP 残基） | Gpr2 Y200A ΔΔG_sel=+1.12，Y378A=+0.92；GprC 校正后最强 H189A=−0.10；发现协议不匹配需 WT 重对接 |
| 2026-04-06 | Orca DFT 配体完成 + MMFF 残留发现并清理 | ascr18/ascr3/ascr7 全部 Orca B3LYP/def2-TZVP；MMFF 结果全部作废 |
| 2026-04-07 | 方法偏差诊断：ICL3 截断 + 单阶段对接 + TM 螺旋质心 | GprC grid box 偏移 18.1Å 确认为偏差根因；质心修复后 GprC ECL 结合位点入 box |
| 2026-04-07 | ascr18 PDBQT 截断 bug 修复 + GprC 复现 | GprC ascr18: −5.41→**−8.235**（Hu2024: −8.29，Δ=0.05 kcal/mol） |
| 2026-04-07~08 | ProLIF IFP 分析 + BW 映射修正 | N2.57=ASN60 确认；R6.45→ARG395（BW 算术 6.55，与 Hu2024 原文编号存争议） |
| 2026-04-09 | 5-seed 方差基线完成 | Gpr2_ascr18 SD=0.159（最高）；GprC SD<0.03；3σ 阈值=0.48 |
| 2026-04-09 | Gpr3 scan_residues 全量替换（IFP 验证） | v2 PLIP 8 个残基全部无效→IFP 8 个替换；I141A ΔΔG_sel=−0.786 |
| 2026-04-10 | alanine scan 阶段完成: 32 突变体 + 双通道分类 | Channel A 首批候选: M327A(sel=−1.39) / I141A(sel=−0.59) / R59A(sel=−0.92)；Hu2024 真阳性对照（N60A/R395A/S44A，见 [Hu2024-GprC-summary.md:L143-145](../papers/summaries/Hu2024-GprC-summary.md)）ΔΔG_sel 方向一致且 > 2σ ✅；真阴性对照 N56A (N2.53A) 亦显著偏移（假阳性，详见 §Pipeline 验证 2026-04-12 修正） |
| 2026-04-11 | **饱和扫描阶段完成**: 90 突变 + 双通道全谱排名（122 条合并）+ Channel A Top 6 IFP 验证 | Channel A 14 条无 caveat + Channel B 11 条无 caveat；新发现 V138R(sel=−0.88)/M327D(sel=−1.09)/F170E(sel=−0.50)/R59F(sel=−0.96)；ARG138 空间富集（盐桥假说待 MD 实证） |

## 与其他方向的依赖关系

- **输出到**:
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): Top 6 突变体的 Kd（从 ΔG 推算）→ ODE 模型输入
  - [P0-md-simulation](P0-md-simulation.md): Top 6 mutant pose → MD 初始构象；V138R/F170E 机制假说 → MD 实证
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 结合口袋结构信息 → 嵌合设计参考
  - [wet-lab-handoff-P0-docking](wet-lab-handoff-P0-docking.md): Top 6 候选 + 机制说明 → 湿实验交接
- **依赖于**: 无（本方向可独立启动）
