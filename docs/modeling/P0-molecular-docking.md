---
direction: P0-molecular-docking
status: completed
priority: P0
chassis_dependent: false
last_updated: 2026-04-10
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
- **Learn**: 实验结果反馈回模型，校准对接预测准确度

## 方法路线

1. 从 AlphaFold DB 获取 Gpr3/Gpr2/GprC WT 预测结构
2. 使用 AutoDock Vina **单阶段对接**（box=40Å, spacing=0.1Å, exh=200, seed=42，匹配 Hu2024 参数）建立 WT 基线
3. **ProLIF IFP 分析**结合口袋关键残基（验证 Hu2024 已知位点，发现新接触残基；IFP 交叉验证排除无效残基）
4. **In silico 突变扫描（核心新增）**：
   - **AlphaFold 3 Server** 预测突变体全长结构 → annotation-based TM 域提取 → ADFR 准备 PDBQT
   - 重对接计算 ΔΔG_selectivity = ΔΔG(ascr18) − ΔΔG(ascr3)
   - Tier 1-4 分层推荐 → 供湿实验组验证

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
- [x] **ΔΔG_selectivity 排名表**（32 突变体 alanine scan 完成，2026-04-10）
- [x] **Tier 1-4 推荐表**（见 [tier_recommendations_20260410.md](../../experiments/docking-repro/mutagenesis/tier_recommendations_20260410.md)）
- [x] **推荐突变位点**: Gpr2 M327A（Tier 1, ΔΔG_sel=−0.99）、Gpr2 R59A（−0.52）、Gpr3 I141A（−0.79）
- [x] IFP 热图可视化（[ifp_heatmap_all_receptors.png](../../experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png)）
- [ ] 可视化图（PyMOL 渲染 WT vs 最优突变体结合构象对比）

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
- **状态**: **计算完成**（2026-04-10）。32 突变体 alanine scan + Tier 1-4 推荐表 + IFP 热图

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

## 最终结果概览（2026-04-10）

完整推荐表见 [tier_recommendations_20260410.md](../../experiments/docking-repro/mutagenesis/tier_recommendations_20260410.md)。IFP 热图见 [ifp_heatmap_all_receptors.png](../../experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png)。

### Pipeline 验证

Hu2024 阳性对照（GprC N60A、R395A、S44A——ascr18 结合必需残基）全部落入 **Tier 4**（削弱选择性），与文献一致。**Pipeline 通过验证。**

WT 基线复现：GprC ascr18 **ΔG = −8.235 kcal/mol**（Hu2024: −8.29，**Δ = 0.05 kcal/mol**）。

### Tier 1：强选择性增强（3 个）— 首选湿实验验证

| 受体 | 突变 | ΔG(18) | ΔG(3) | ΔΔG_sel | 机制 |
|------|------|--------|-------|---------|------|
| Gpr2 | **M327A** | −6.74 | −5.35 | **−0.99** | ascr18 几乎不受影响（ΔΔG=+0.09），ascr3 大幅削弱（+1.08） |
| Gpr3 | **I141A** | −5.19 | −4.60 | **−0.79** | 双配体亲和均下降，ascr3 损失更大 |
| Gpr2 | **R59A** | −6.53 | −5.60 | **−0.52** | ascr3 比 ascr18 更依赖 R59 |

ΔΔG_sel 阈值 = −0.48（3σ，噪声 SD=0.159 来自 5-seed 方差评估）。

### Tier 2：中度选择性增强（2 个）

| 受体 | 突变 | ΔΔG_sel |
|------|------|---------|
| Gpr3 | **F170A** | −0.36 |
| Gpr3 | **V138A** | −0.26 |

### Tier 3-4 汇总

- **Tier 3（中性）**: 6 个突变，ΔΔG_sel 在噪声范围内
- **Tier 4（削弱选择性，不推荐）**: 21 个突变，含全部 GprC 口袋残基和 Hu2024 阳性对照

### 关键洞察

1. **GprC 不适合 alanine 工程化选择性**: 14 个突变中 13 个为 Tier 4，口袋残基对 ascr18/ascr3 均至关重要
2. **Gpr2 M327A 最强信号**: MET327 是 IFP 全场最高频接触残基（51 次），但对 ascr3 结合贡献远超 ascr18。mutant ΔG(18)=−6.74 仍保持合理亲和力（≈WT −6.83），**湿实验优先级最高**
3. **Gpr3 WT 偏好 ascr3**（ΔG_sel=+0.20），I141A 可扭转为 ascr18 偏好
4. **v2 旧结论已被修正**: Orca DFT 配体几何 + ICL3 截断 + BW 映射修正后，Y200A/Y378A 从 Tier 1 降为 Tier 4，M327A 成为新的首选

## 方法学局限性

| 局限性 | 影响 | 缓解 |
|--------|------|------|
| 单 seed Vina 噪声（SD=0.159） | ΔΔG_sel < 0.48 不可信 | Tier 划分以 3σ 为阈值；5-seed 方差已量化 |
| 刚性受体 | 构象选择限于 AF3 单预测 | 单点突变对骨架影响 <0.1Å（TM helix 域内） |
| AF3 预测精度 | pLDDT>90 区域可信，loop 区不确定 | 仅在 TM helix 域内对接；annotation-based TM 提取 |
| Vina 评分精度（±1 kcal/mol） | 绝对值不精确 | 仅用排名，不用绝对值；Tier 1 全部 >3σ |

## 方法学迭代记录

P0 对接方法经历三次重大迭代，每次修正了前一阶段的系统性偏差：

| 阶段 | 时间 | 关键变更 | 修正了什么 |
|------|------|---------|-----------|
| v2（MMFF） | 04-03~04 | OpenBabel + RDKit MMFF + spacing=0.25Å | 初始探索，验证 Kuo2024 排名 |
| docking-repro v1 | 04-05~06 | ADFR + Orca DFT + 两阶段对接 | 配体几何（MMFF→DFT）；发现协议不匹配 |
| docking-repro v2 | 04-07~10 | **单阶段**（匹配 Hu2024）+ **ICL3 截断** + **TM 螺旋质心** + **BW 映射修正** + **ProLIF IFP** | GprC grid box 偏移 18.1Å；ascr18 PDBQT 截断（15→26 原子）；BW→序列映射错误；v2 PLIP 残基无效（Gpr3 全部替换） |

最终方法（docking-repro v2）的 GprC ascr18 ΔG 与 Hu2024 仅差 0.05 kcal/mol，Hu2024 阳性对照全部通过验证。

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
| 2026-04-10 | **v3.0** | 32 突变体全量 alanine scan 完成；Tier 1-4 推荐表；Gpr2 IFP 验证（9/9 PASS）；**本文档更新至 Wiki 初版** | P0 计算阶段完成，进入输出阶段 |

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
| 2026-04-10 | **P0 计算阶段完成**: 32 突变体 + Tier 推荐表 | Tier 1: M327A(−0.99) / I141A(−0.79) / R59A(−0.52)；Hu2024 阳性对照全部 Tier 4 ✅ |

## 与其他方向的依赖关系

- **输出到**:
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 结合亲和力参数（Kd）→ ODE 模型输入
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 结合口袋结构信息 → 嵌合设计参考
- **依赖于**: 无（本方向可独立启动）
