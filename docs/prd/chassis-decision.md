# 底盘选择历史决策 Hub

> 来源: PRD v3 §2C, §2D | 最后更新: 2026-06-02
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
- docking 候选、MD 运行状态和 reporter 参数不要从本文件读取；分别回到 docking handoff、MD 文档、ODE 文档和最新日志。

## 历史分析边界

以下内容是 2026-04-03 至 2026-04-10 阶段的方案比较摘要，只用于解释为什么选择酵母路线；不作为当前状态或行动清单。

### 当时的核心问题

项目成败关键是：Gpr 受体能否在底盘生物中正确折叠、定位到细胞膜，并与下游 G 蛋白功能性偶联。

### 酵母路线的当时判断

- 优势：GPCR 工程、pheromone pathway 参数、遗传操作、iGEM 叙事和产品化路径更成熟。
- 风险：异源真菌 GPCR 的膜定位与 G 蛋白偶联需要计算和湿实验共同验证。
- 缓解：分子对接、嵌合 Gpa1 设计、MD 稳定性验证和 ODE/reporter 建模分层推进。

### 丝状真菌路线的当时判断

- 优势：Gpr 受体在原生或近缘底盘中表达时，折叠和偶联风险较低。
- 风险：遗传操作、定量通路参数、响应启动子和产品化路径都更不确定。
- 结论：在 2026-04-11 PI 确认后，丝状真菌路线不再作为主线。

## 历史阻塞项结论

| 历史问题 | 2026-04-11 后结论 |
|---|---|
| 实验室真菌物种是否决定底盘 | 不再作为主线选择阻塞；酵母主线已定 |
| 真菌遗传操作工具是否足够成熟 | 不作为当前默认路线 |
| PI 底盘倾向 | 已确认酵母-STE2 |
| 转录组数据是否用于丝状真菌启动子选择 | 丝状真菌路线停用后失效 |

## 使用纪律

- 引用底盘选择时，优先引用 [决策 003](../decisions/003-chassis-yeast-ste2-integration.md)。
- 引用输出架构时，优先引用 [决策 004](../decisions/004-reporter-output-architecture.md)。
- 需要“现在做到了哪一步”时，不读本文件；读 [docs/INDEX.md](../INDEX.md) 和相关日志。
- 本文件后续只在底盘决策解释发生变化时更新；普通进展不写入这里。
