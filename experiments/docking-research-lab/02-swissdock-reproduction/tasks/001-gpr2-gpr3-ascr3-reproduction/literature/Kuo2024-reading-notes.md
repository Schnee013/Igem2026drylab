# Kuo 2024 docking 复现笔记

> 只记录复现 Gpr2/Gpr3 WT–ascr#3 所需的信息。

## Research objective

- Decision/use: 为阶段 B 冻结两个 WT docking 的输入与 pose 规则。
- Target question: Kuo 2024 报告了哪些可复现条件，缺少哪些关键条件？
- Source scope: Kuo 2024 docking 正文、Methods、相关图注与其引用的 SwissDock 方法。
- Exclusions: 生物学背景、突变设计、其他 receptor/ligand 和参数扩展。
- Access date: 2026-08-11。

## Findings

### 最小方法提取

| 项目 | 原文可确认内容 | 结论 |
|---|---|---|
| 任务 | *A. oligospora* TWF154 的 Gpr2–ascr#3、Gpr3–ascr#3 | 两个 WT 任务 |
| 受体 | Gpr2、Gpr3 结构由 AlphaFold 预测 | 原文未给 accession、模型版本或结构文件 |
| 配体 | ascr#3 化学结构文件来自 ChemSpider | 原文未给 ChemSpider ID、文件格式、质子化或优化步骤 |
| 对接 | SwissDock，使用默认参数 | 原文 Methods 写作 “SeissDock”，但正文和引用均为 SwissDock |
| 搜索空间 | 默认参数考虑整个靶蛋白 | 属于全蛋白盲对接，不是预先指定口袋 |
| 评分 | 以预测结合自由能 ΔG 比较 pose | 数值仅作为同路线复现参照 |
| pose 选择 | 未报告 cluster、rank 或代表 pose 的选择规则 | 阶段 B 必须在看结果前另行冻结规则 |
| 受体截断 | 未报告 docking 输入被截断 | Gpr2 217–316、Gpr3 212–264 仅在论文图片中因预测为随机卷曲而省略显示，不能据此从输入结构删除 |

### 文献结果锚点

| 受体 | ascr#3 文献 ΔG | 位置/接触信息 | 复现时的用途 |
|---|---:|---|---|
| Gpr2 | −6.99 kcal/mol | 胞外结构域；Y168 被作者列为结合残基 | 检查代表 pose 是否位于胞外区域并接近 Y168 |
| Gpr3 | −7.05 kcal/mol | 作者预测到胞外 docking 区域；未命名具体残基；未预测到强氢键 | 只检查胞外位置，不强求特定氢键或残基 |

### 阶段 A 的直接答案

1. **确切受体文件：不能由论文唯一确定。** 论文只说明使用 AlphaFold 预测结构。
2. **确切 ascr#3 文件：不能由论文唯一确定。** 论文只说明结构文件来自 ChemSpider。
3. **SwissDock 提交方式：**上传受体和配体，使用默认参数，对整个受体做盲对接。
4. **代表 pose 规则：论文未报告。** 后续只能采用事先声明的复现规则，不能声称与作者选择过程完全相同。
5. **合理性锚点：**Gpr2 为胞外区域、Y168 和 −6.99 kcal/mol；Gpr3 为胞外区域和 −7.05 kcal/mol。

## Gaps and conflicts

- Kuo 引用的是 2011 年基于 EADock DSS 的 SwissDock；当前 SwissDock 已改用 Attracting Cavities 或 AutoDock Vina。原文没有记录实际运行日期、服务版本或引擎，因此当前网站结果不能视为算法级完全复现。
- 原文没有给 receptor accession/序列版本、AlphaFold 模型版本、配体唯一标识、输入预处理和 pose/cluster 选择规则。
- 文献给出的 ΔG、Y168 和胞外位置是验证锚点，不足以反推出作者的原始 pose。

## Verified Source Ledger

| ID | Source | URL | Authority | Access | Relevance | Status |
|---|---|---|---|---|---|---|
| S1 | [Kuo et al., 2024, Nature Microbiology](https://doi.org/10.1038/s41564-024-01679-w) | https://doi.org/10.1038/s41564-024-01679-w | primary | 2026-08-11 | docking 结果、图注和 Methods | used |
| S2 | [Grosdidier et al., 2011, SwissDock/EADock DSS](https://doi.org/10.1093/nar/gkr366) | https://doi.org/10.1093/nar/gkr366 | primary | 2026-08-11 | Kuo 引用的 SwissDock 方法 | used |
| S3 | [SwissDock 当前官网](https://www.swissdock.ch/) | https://www.swissdock.ch/ | official | 2026-08-11 | 当前可选引擎和输入界面 | used |

## Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|---|---|---|---|---|---|
| AlphaFold 受体、ChemSpider 配体、SwissDock 默认参数、全蛋白搜索 | S1 | Methods, “The prediction of ascaroside–GPCR docking site…” | 作者明确描述四项条件 | high | 未给唯一输入标识 |
| Gpr2–ascr#3 为 −6.99 kcal/mol、胞外区域、Y168 | S1 | Results；Fig. 3d | 作者报告分数、区域和结合残基 | high | 未给接触距离或 pose 编号 |
| Gpr3–ascr#3 为 −7.05 kcal/mol，未命名残基且无强氢键 | S1 | Results；Extended Data Fig. 6 | 作者报告分数并说明无强氢键 | high | 图注未提供代表 pose 编号 |
| 随机卷曲区仅从图中省略 | S1 | Fig. 3c/d；Extended Data Fig. 6 caption | 图注用词为 omitted from structural display，Methods 同时说明全蛋白搜索 | high | 原始受体文件未公开，不能检查文件内容 |
| Kuo 引用的旧版 SwissDock 基于 EADock DSS | S2 | Title；Methods | 2011 方法原文明确命名 EADock DSS | high | Kuo 未报告实际服务器版本 |
| 当前 SwissDock 提供 Attracting Cavities 与 AutoDock Vina | S3 | Submission page, docking engine buttons | 当前官方界面列出两种引擎 | high | 不能据此确定 Kuo 当年实际部署版本 |
| 原文未报告 exact input 与 pose 选择规则 | S1 | docking 相关 Results、figures、captions、Methods | 全部相关位置均未给 accession、模型版本、配体 ID 或 pose/cluster 规则 | high | “未报告”限于论文及公开补充材料 |

## Audit Notes

- 核对范围：原文 docking 正文、Methods、Fig. 3、Extended Data Figs. 5–6、补充信息和当前 SwissDock 官方说明。
- 补充 PDF 只含 Southern blot；没有 docking 方法，因此未摘录。
- 阶段 A 完成于 2026-08-11；尚未选择输入文件，也尚未提交 docking。
