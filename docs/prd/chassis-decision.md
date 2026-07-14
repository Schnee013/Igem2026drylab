# 底盘选择历史决策 Hub

> 来源: PRD v3 §2C, §2D | 最后更新: 2026-04-17
>
> 本文件只记录底盘选择的历史决策、决策依据和后续权威指针。它不维护当前项目状态、方向进展、候选列表或运行结果。当前现状看 [docs/INDEX.md](../INDEX.md)；具体经过看 [docs/logs/](../logs/)。

## 最终决策（2026-04-11）

| 项 | 决定 |
|---|------|
| 底盘 | *Saccharomyces cerevisiae*（酿酒酵母） |
| 通路 | STE2 pheromone pathway（异源 Gpr 接入内源 MAPK） |
| G 蛋白 | 嵌合 Gpa1（C 端嫁接真菌来源 Gα C 端，模板 Hara 2012 / Medici 1997） |
| 拷贝数策略 | 基因组整合；不使用 CEN/2μ 质粒作为默认路线 |
| 输出架构 | sTF -> GAL 多拷贝放大 -> 色素显色；详见 [决策 004](../decisions/004-reporter-output-architecture.md) |

权威记录：

- [决策 003: chassis-yeast-ste2-integration](../decisions/003-chassis-yeast-ste2-integration.md)
- [决策 004: reporter-output-architecture](../decisions/004-reporter-output-architecture.md)
- 当前项目全貌：[overview-v4.md](overview-v4.md)

## 决策依据

1. **PI 确认**：2026-04-11 与 PI 当面讨论后锁定酵母主线。
2. **真菌底盘工具风险**：Kuo 2024 / Hu 2024 提示 *A. oligospora*、*A. flagrans* 原生表达体系遗传操作繁琐，CRISPR 工具未稳定建立，周转较慢。
3. **酵母 GPCR 工程模板更完整**：Lengger 2020、Mukherjee 2025、Hara 2012 / Medici 1997、Fan & Yuan 2024 等支持酵母 GPCR、嵌合 Gpa1 和 GAL 输出放大的工程路线。
4. **基因组整合降低输出层漂移**：避免 CEN/2μ 质粒拷贝数波动影响下游输出解释。

## 决策影响边界

- P3 嵌合 Gpa1 同源建模升为核心干实验路线；当前进展和 MD 验证状态看 [P3-chimeric-gprotein.md](../modeling/P3-chimeric-gprotein.md)、[P0-md-simulation.md](../modeling/P0-md-simulation.md) 和 [docs/INDEX.md](../INDEX.md)。
- P0 ODE 走酵母 STE2/MAPK/reporter 输出接口；参数状态和实现边界看 [P0-signal-pathway-ode.md](../modeling/P0-signal-pathway-ode.md)。
- P2 生物防治 LV 只属于丝状真菌路线下的历史备选；当前 P2 经济模型看 [P2-economic-benefit.md](../modeling/P2-economic-benefit.md)。
- docking 候选、MD 运行状态和 reporter 参数的当前入口分别是 [P0 docking MD candidate-system shortlist](../modeling/P0-docking-md-candidate-shortlist.md)、[P0-md-simulation.md](../modeling/P0-md-simulation.md)、[P0-signal-pathway-ode.md](../modeling/P0-signal-pathway-ode.md)、[docs/INDEX.md](../INDEX.md) 和最新日志。

## 历史分析边界

以下内容是 2026-04-03 至 2026-04-10 阶段的方案比较摘要，用于解释酵母路线选择。当前状态和行动清单入口为 [docs/INDEX.md](../INDEX.md)、领域文档和最新日志。

### 当时的核心问题

项目成败关键是：Gpr 受体能否在底盘生物中正确折叠、定位到细胞膜，并与下游 G 蛋白功能性偶联。

### 酵母路线的当时判断

- 优势：GPCR 工程、pheromone pathway 参数、遗传操作、iGEM 叙事和产品化路径更成熟。
- 风险：异源真菌 GPCR 的膜定位与 G 蛋白偶联需要计算和湿实验共同验证。
- 缓解：分子对接、嵌合 Gpa1 设计、MD 稳定性验证和 ODE/reporter 建模分层推进。

### 丝状真菌路线的当时判断

- 优势：Gpr 受体在原生或近缘底盘中表达时，折叠和偶联风险较低。
- 风险：遗传操作、定量通路参数、响应启动子和产品化路径都更不确定。
- 结论：2026-04-11 PI 确认后，酵母-STE2 为当前主线，丝状真菌路线保留为历史备选。

## 历史阻塞项结论

| 历史问题 | 2026-04-11 后结论 |
|---|---|
| 实验室真菌物种是否决定底盘 | 酵母主线已定 |
| 真菌遗传操作工具是否足够成熟 | 历史备选判断；酵母主线已定 |
| PI 底盘倾向 | 已确认酵母-STE2 |
| 转录组数据是否用于丝状真菌启动子选择 | 丝状真菌路线停用后失效 |

**决策后关键进展（2026-04-11 → 04-17，细节见各指针文档）**：

- **分子对接**：122 突变体完成 + IFP 验证 + Top 6 锁定 → [P0-molecular-docking](../modeling/P0-molecular-docking.md)
- **嵌合 Gpa1**：AF3 42 jobs 全量完成，Top 3 候选选定；GprC MTS 风险（98.41% 线粒体靶向）已识别，GprC-WT 备选路线不启动 → [P3-chimeric-gprotein](../modeling/P3-chimeric-gprotein.md)
- **MD 模拟**：突变体 Phase 3 完成、Phase 4 进行中；Chimeric Phase C1-C5 已规划未启动 → [P0-md-simulation](../modeling/P0-md-simulation.md)
- **双受体策略具体化**：Gpr2/3 突变体 + AoGpa2 chimeric Gpa1（统一工程路线）
- **开放风险**：异源 GPCR 在酵母的膜定位验证仍为湿实验开放问题，干实验不产出此类数据

> 完整决策上下文与历史选项对比：[决策 003: chassis-yeast-ste2-integration](../decisions/003-chassis-yeast-ste2-integration.md)。
>
> 以下"核心技术挑战 / 酵母方案 / 丝状真菌方案 / 决策树 / 阻塞性待确认项"小节保留为**历史分析**，记录 2026-04-03 ~ 04-10 阶段的备选评估。

## 核心技术挑战

**所有下游工程（显色输出、放大回路、产品化）都是有解的工程问题。** 整个项目成败的决定性环节是:

> **Gpr 受体能否在底盘生物中正确折叠、定位到细胞膜、并与下游 G 蛋白功能性偶联？**

这一个问题，决定了底盘选择的全部逻辑。

## 酵母方案的逻辑链

```
优势链:
  酵母 GPCR 工程极其成熟 (Ste2/Ste3 pathway)
  → pheromone pathway 每个节点都有定量参数
  → 建模数据充足
  → 遗传操作快速（2-3 天周转）
  → iGEM 社区熟悉，评审友好
  → 冻干酵母试纸产品化路径清晰

核心风险:
  Gpr2/3/GprC 来自丝状真菌
  → 七跨膜结构与酵母内源 GPCR 差异大
  → 异源表达后能否正确插膜？→ 仍为开放问题（GprC 另有 MTS 风险，详见下方进展）
  → 能否与嵌合 Gpa1 偶联？→ AF3 已给出计算证据，MD 验证进行中
  → 这是整个方案的"0 或 1"风险点
  
缓解措施（已部分兑现）:
  → 分子对接 122 突变体完成 → [P0-molecular-docking](../modeling/P0-molecular-docking.md)
  → 嵌合 Gpa1 AF3 42 jobs 完成，Top 3 已选定 → [P3-chimeric-gprotein](../modeling/P3-chimeric-gprotein.md)
  → MD 验证 Phase 4 进行中 → [P0-md-simulation](../modeling/P0-md-simulation.md)
```

## 丝状真菌方案的逻辑链

```
优势链:
  Gpr 受体在 A. oligospora / A. flagrans 中原生表达
  → 折叠、膜定位、G蛋白偶联全部已知可行
  → "0 或 1"风险直接消除
  → 叙事强大: "用线虫天敌来检测线虫"
  → 如果实验室有操作基础 → 巨大竞争优势

核心风险:
  1. 遗传操作成熟度远低于酵母（CRISPR 不如酵母稳健，周期 1-2 周 vs 2-3 天）
  2. 通路参数匮乏，ODE 建模困难（只能做粗粒度 Hill 函数近似）
  3. 响应型启动子未知（需 RNA-seq 数据或文献推测）
  4. 产品化路径不清晰（不像酵母容易冻干成试纸）
```

## 决策树

```
                    实验室做的真菌是什么物种？
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        A. oligospora   Aspergillus    其他丝状真菌
        或 A. flagrans                 
              │             │             │
              ▼             ▼             ▼
        丝状真菌为主线   受体仍需异源表达   受体仍需异源表达
        Gpr 原生表达     和酵母类似风险     和酵母类似风险
        偶联问题消除     但转化慢           但转化慢
              │             │             │
              │             └──────┬──────┘
              │                    │
              │              酵母为主线
              │              丝状真菌为探索线
              │                    │
              ▼                    ▼
        干实验策略 A          干实验策略 B
```

### 策略 A（丝状真菌主线）

- §3.1 分子对接: 仍要做，优化受体特异性
- §3.2 ODE: 粗粒度 Hill 函数模型
- §3.3 扩散: 照常
- §3.5 防治: (c) 经济效益 + (b) 生物防治 LV（叙事耦合）
- **额外**: 转录组挖掘，寻找 ascaroside 响应启动子

### 策略 B（酵母主线）

- §3.1 分子对接: 同上
- §3.2 ODE: 完整详细的 ODE 模型（参数文献丰富）
- §3.3 扩散: 同上
- §3.5 防治: (c) 经济效益 + (a) 剂量-响应
- §3.6 嵌合 Gpa1: **优先级升至 P0**

## 历史阻塞（已全部解除或失效）

> 以下条目在 2026-04-03 ~ 04-10 阶段为决策阻塞项，2026-04-11 PI 确认底盘后全部解除（条目 1-3）或失效（条目 4，丝状真菌路线已不激活）。

| # | 待确认 | 重要性 | 确认方式 |
|---|--------|--------|---------|
| 1 | ~~实验室真菌物种~~ | 直接决定底盘 | 已确认 → 改走酵母 |
| 2 | ~~遗传操作工具~~ | 评估工程可行性 | 已评估 → 真菌底盘工具不成熟 |
| 3 | ~~PI 底盘倾向~~ | 影响湿实验效率 | PI 选定酵母 |
| 4 | ~~转录组数据~~ | 丝状真菌启动子选择 | 失效（不再走丝状真菌路径） |

## 需要查阅的文献

| # | 文献/数据源 | 查什么 | 目的 | 状态 |
|---|-----------|-------|------|------|
| 1 | Hu et al. 2024 | GprC 下游上调基因、启动子候选 | 丝状真菌启动子 | ✅ 已查阅（GprC→GasA 偶联 + MTS 发现） |
| 2 | Kuo et al. 2024 | Gpr2/3 下游 MAPK 磷酸化时序 | 丝状真菌 ODE 参数 | ✅ 已查阅（Gpr2/3→Gpa2 偶联确认） |
| 3 | GEO/SRA 搜索 | *A. oligospora* transcriptome + ascaroside | 响应启动子筛选 | 失效（丝状真菌路线已归档） |
| 4 | 丝状真菌合成生物学工具包文献 | 启动子、终止子、CRISPR 组件 | 工程可行性 | 失效（同上） |
| 5 | iGEM 历史项目中丝状真菌案例 | 有无先例？评审态度？ | 比赛风险 | ✅ 已查阅（零 7-TM GPCR MD 先例） |
| 6 | Fan & Yuan 2024 | 嵌合策略和实验数据 | 酵母方案参考 | ✅ 已查阅（GAL4 级联参考） |

## 关于"并行"的审慎评估

**并行的成本是真实的，收益是不确定的。**

- 6 个月实际可用建模时间约 3-4 个月
- 并行 = 两套通路、两套建模、两套显色优化
- 建议: 除非湿实验 ≥6 人，否则**第 4 周前确定主线**，另一个作为 backup

## 近期行动项（2026-04-03 原始，已全部完成或失效）

- [x] ~~**本周**: 问 PI 真菌物种、遗传工具、底盘倾向~~ → 04-11 已确认酵母
- [x] ~~**本周**: 检索 GEO/SRA 转录组数据~~ → 失效（丝状真菌路线已归档）
- [ ] **本周**: 与 HP 组沟通经济效益模型需求
- [x] ~~**第 2-3 周**: 根据 PI 回复进入策略 A 或 B~~ → 已进入策略 B
- [x] ~~**立即可开始**: §3.1 分子对接、§3.3 扩散模型、§3.5c 经济效益~~ → 对接已完成，详见各方向文档

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §2C-2D 提取 | 文档体系搭建 |
| 2026-04-11 | v2.0 | 追加 §最终决策；阻塞项划线为历史 | PI 确认酵母-STE2 主线 |
| 2026-04-17 | v2.1 | 逻辑链"未知"→当前状态；行动项/文献表标记完成/失效；补决策后进展摘要（指针） | 过时审查 |
