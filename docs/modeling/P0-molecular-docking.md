---
direction: P0-molecular-docking
status: in_progress
priority: P0
chassis_dependent: false
last_updated: 2026-04-04
---

# P0: 受体-配体分子对接与结构分析

> 来源: PRD v3 §3.1 | iGEM 评审定位: 直接支撑湿实验设计

## 解决什么问题

湿实验组需要知道 Gpr2/3/GprC 对 ascr#3、ascr#7、ascr#18 的结合亲和力差异，以及哪些氨基酸残基影响特异性。这是核心感应组（§1.2/§1.3 任务）的直接计算支撑。

**iGEM 价值**: 产出突变位点建议 → 湿实验组据此设计定点突变 → 验证结果反馈回模型 → 完成一个 DBTL cycle。

## 方法路线

1. 从 AlphaFold DB 获取预测结构:
   - Gpr3 (UniProt: G1XJN1)
   - Gpr2 (UniProt: G1X9E2)
   - GprC (UniProt: A0A437AGY2)
2. 使用 AutoDock Vina 进行 ascr#18 / ascr#3 与受体的分子对接
3. 分析结合口袋（binding pocket）关键残基
4. 用计算突变扫描（in silico mutagenesis）预测增强特异性的突变位点

## 工具栈

| 工具 | 用途 | 安装 |
|------|------|------|
| AlphaFold DB / ColabFold | 结构获取/预测 | 浏览器 / Google Colab |
| AutoDock Vina | 分子对接 | `pip install vina` |
| Meeko | 配体/受体 PDBQT 准备 | `pip install meeko` |
| PyMOL | 分子可视化 | 教育版免费申请 |
| PLIP | 蛋白-配体相互作用分析 | `pip install plip` |

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

- [ ] 受体-配体结合能排名表（3 受体 × 3 配体 = 9 组）
- [ ] 结合口袋关键残基列表（每个受体）
- [ ] 推荐突变位点列表（增强 ascr#18 特异性）
- [ ] 可视化图（PyMOL 渲染的结合构象）
- [ ] 产出文件位置: `experiments/docking/`

## 方法变体

本方向存在两条并行的方法线：

### v2（当前主线）
- **代码路径**: `src/modeling/docking/`
- **产出路径**: `experiments/docking/`
- **工具链**: OpenBabel 受体准备 + RDKit MMFF 配体优化 + Meeko PDBQT + spacing=0.25Å
- **状态**: production 结果已获取（2026-04-04）
- **已验证**: Kuo2024 Gpr2/Gpr3 排名（PASS）；GprC 绝对值差 ~2 kcal/mol（方法差异）

### docking-repro（Hu2024 精确复现线）
- **代码路径**: `src/modeling/docking-repro/`
- **产出路径**: `experiments/docking-repro/`
- **工具链**: ADFR Suite 受体/配体准备 + Orca DFT B3LYP/def2-TZVP + 两阶段对接 (spacing=0.1Å)
- **计算节点**: Windows 7500F（通过 Tailscale SSH 远程调用）
- **安装脚本**: `scripts/win-setup/` (01~04)
- **状态**: 代码已写，等待 Windows 安装 ADFR Suite + Orca

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

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §3.1 提取初始内容 | 文档体系搭建 |
| 2026-04-03 | v1.1 | 补充已验证的 AlphaFold/PubChem 链接，新增 ascr#7，对接矩阵更新为 3×3 | 数据源验证 |
| 2026-04-03 | v1.2 | 补充配体化学标识符（CAS, InChIKey, SMILES, ChemSpider），关联文献总结 | 化合物交叉验证 |
| 2026-04-04 | v1.3 | 新增 docking-repro 方法变体（ADFR+Orca），补充方法变体章节 | Hu2024 精确复现需求 |

## 进展记录

| 日期 | 事件 | 关键数据 |
|------|------|---------|
| 2026-04-04 | v2 pipeline production 完成（exh=200） | GprC ascr18=-6.05, ascr3=-6.45; Kuo2024 排名全部 PASS |
| 2026-04-04 | docking-repro pipeline 代码完成 | 等待 Windows 安装 ADFR Suite + Orca |

## 与其他方向的依赖关系

- **输出到**:
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 结合亲和力参数（Kd）→ ODE 模型输入
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 结合口袋结构信息 → 嵌合设计参考
- **依赖于**: 无（本方向可独立启动）
