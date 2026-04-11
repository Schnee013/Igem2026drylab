# 决策 003：底盘选择 — 酿酒酵母 + STE2 通路 + 嵌合 Gpa1 + 基因组整合

- **日期**: 2026-04-11
- **状态**: 已决定
- **关联方向**:
  - [overview-v4](../prd/overview-v4.md)
  - [chassis-decision §最终决策](../prd/chassis-decision.md#最终决策2026-04-11)
  - [P0-signal-pathway-ode](../modeling/P0-signal-pathway-ode.md)
  - [P3-chimeric-gprotein](../modeling/P3-chimeric-gprotein.md)（升 P0）
  - [P0-md-simulation](../modeling/P0-md-simulation.md)（新建）
  - [P2-biocontrol-lv](../modeling/P2-biocontrol-lv.md)（archived）

## 背景

底盘选择从 2026-04-03 项目启动起就是干实验最关键的阻塞项：

- 决定信号通路 ODE 的复杂度（酵母参数丰富 vs 真菌只能粗粒度 Hill 函数）
- 决定 P3 嵌合 Gpa1 是否需要做（仅酵母路线触发）
- 决定 P2 生物防治 LV 是否值得做（仅丝状真菌路线触发，"用线虫天敌检测线虫"叙事耦合）
- 决定下游显色级联的工程化路径（酵母有冻干产品化先例，丝状真菌产品化路径不清晰）

期间已完成 47 篇文献调研、Kuo2024 / Hu2024 复现对接、`chassis-decision.md` 决策树。详细对比与历史评估见 [chassis-decision.md](../prd/chassis-decision.md)（不在本决策记录中重复）。

2026-04-11 与 PI 当面讨论后，最终方案锁定。

## 选项

1. **策略 A：丝状真菌主线**（*A. oligospora* / *A. flagrans* 原生表达）
2. **策略 B：酿酒酵母主线**（异源表达 + 嵌合 Gpa1 + STE2 通路）

完整选项对比详见 [chassis-decision.md](../prd/chassis-decision.md) §酵母方案的逻辑链 / §丝状真菌方案的逻辑链。本决策记录不复制内容，避免与上游漂移。

## 决定

**采用策略 B**：

| 项 | 决定 |
|---|---|
| 底盘 | *Saccharomyces cerevisiae* |
| 通路 | 内源 STE2 pheromone pathway |
| Gα 改造 | 嵌合 Gpa1（C 端嫁接 *A. oligospora* / *A. flagrans* Gα C 端 5/10/15 残基三档） |
| 拷贝数 | **基因组整合**（不使用 CEN/2μ 质粒） |
| 显色输出 | TBD（不在本决策范围；待报告基因方案确定后补） |

**决策依据**：

1. **PI 一票确认**：2026-04-11 当面讨论。
2. **真菌底盘工具不成熟**：Kuo 2024 / Hu 2024 实验体系周转 1-2 周，CRISPR 工具未稳定建立；即使能跑通也难以在 iGEM 6 个月窗口内迭代。
3. **酵母 GPCR 工程模板齐全**：Lengger 2020 综述、Mukherjee 2025 真菌 GPCR 在酵母筛选、Hara 2012 / Medici 1997 嵌合 Gpa1 设计、Fan & Yuan 2024 GAL4 级联放大共同为酵母路线背书。
4. **基因组整合 vs 质粒**：CEN 拷贝数 1-2、2μ 拷贝数 ~30 但漂移大；下游显色级联放大对线性度敏感，整合保证拷贝数稳定。

## 后果

1. **P3 嵌合 Gpa1 升 P0**：从备选方向变成核心方向，需在 wiki freeze 前完成嵌合方案 + 结构预测 + 稳定性评估。详见 [P3-chimeric-gprotein.md](../modeling/P3-chimeric-gprotein.md)（v2.0）。
2. **P0 信号通路 ODE 走完整酵母路径**：参数源 Shaw 2019 / Fan & Yuan 2024 / Ladds 2005；新增"基因组单拷贝整合"基线假设和 1/2/4 copy 拷贝数敏感性分析。
3. **P2 生物防治 LV 归档**：失去叙事耦合度，文档保留不删除（DOCMAP §8）。
4. **新增 P0-md-simulation**：饱和扫描产出的 V138R 盐桥假说与 F170E 反直觉现象需 MD 实证；嵌合 Gpa1 + Gpr 复合物的稳定性也需 MD 验证。技术栈未预设，首要任务是文献调研。
5. **所有下游模型默认基线**："基因组单拷贝整合"，下游 EC50 / 报告基因表达量等指标均按此假设解读。
6. **显色级联具体方案 TBD**：作为 P0-ODE 的下游接口变量保留，方案确定后回填参数；本次决策不为其建文档。
7. **湿实验交接更新**：[wet-lab-handoff-P0-docking](../modeling/wet-lab-handoff-P0-docking.md) 新增 §7 底盘与通路上下文，明确表达体系与读出方式。

## 不在本决策范围

- 显色报告基因选型（Lycopene / Betalain / amilCP / lacZ / GFP）
- 整合位点（HO / URA3 / TRP1 / 多位点）
- 是否使用 GAL4 间接放大
- 读出形态（试纸 / 液体 / 琼脂板）

以上待与通路工程组讨论后另起决策记录。
