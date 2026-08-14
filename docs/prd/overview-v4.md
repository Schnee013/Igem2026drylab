# 项目全貌（v4）

> 来源: 在 v3（[archive/overview-v3.md](archive/overview-v3.md)）基础上，根据 2026-04-11 PI 确认底盘策略落地 | 最后更新: 2026-08-14

## 一句话描述

构建一个**基于 GPCR 生物传感器**的植物寄生线虫田间早期检测系统：线虫分泌特征性蛔苷素（ascarosides）→ 捕食性真菌来源的 Gpr 受体异源表达于**酿酒酵母（*S. cerevisiae*）**膜上 → 经**改造的 STE2 通路 + 嵌合 Gpa1**接入内源 MAPK 级联 → sTF 接入 GAL 多拷贝放大 → 色素显色 → 肉眼可见的田间显色判读 → 防治建议闭环。

> **底盘决策状态**: 已锁定 *S. cerevisiae* + STE2 通路（2026-04-11，PI 确认）。详见 [底盘决策 §最终决策](chassis-decision.md#最终决策2026-04-11) 与 [决策 003](../decisions/003-chassis-yeast-ste2-integration.md)。

## 核心信号链路（方案 A 单一路径）

```
土壤中有害线虫 (PPNs)
    │ 分泌
    ▼
ascr#18 / ascr#3（特征比例）
    │ 配体结合
    ▼
Gpr2 / Gpr3 / GprC（来自 A. oligospora / A. flagrans）
    │ 异源表达
    ▼
酿酒酵母细胞膜 (S. cerevisiae)
    │ 偶联
    ▼
嵌合 Gpa1（C 端嫁接真菌 Gα C 端，模板 Hara2012 / Medici1997）
    │ 激活
    ▼
内源 STE2 通路：Ste11 → Ste7 → Fus3 (MAPK) → 转录因子 Ste12
    │ 启动
    ▼
sTF（Ste12 PRD-Gal4DBD 类融合转录因子）
    │ 接入 GAL 多拷贝放大
    ▼
色素显色 reporter 输出
    │ 上游底盘/受体/通路元件以基因组整合为基线；输出层实际拷贝数作为 ODE 变量校准
    ▼
田间可视化判读（试纸 / 冻干酵母 / 其他形态待定）
    │
    ▼
防治建议闭环（剂量-响应 + 经济效益模型）
```

## 双靶标判别逻辑

- **ascr#18**: 在植物寄生线虫（PPNs）中占绝对优势
- **ascr#3**: 在自由生活线虫中占主导
- 通过改造 Gpr 受体获得对 ascr#3 / ascr#18 的差异化特异性，由两个传感器（不同 Gpr 突变体）输出的显色比例判别有害线虫
- 04-11 干实验曾产出 6 个 Top 候选位点；2026-05 docking 选择及其后续 MD 输入关系作为历史证据保留，见 [2026-05 MD 输入选择快照](../modeling/P0-docking-md-candidate-shortlist.md)。

## 团队组织

| 组别 | 核心目标 | 关键任务 |
|------|---------|---------|
| 核心感应组 | 靶标表征与受体决策 | ascr#3/#18 定量、Gpr 受体筛选与评估、受体特异性改造方案 |
| 通路工程组 | 偶联适配与信号增益 | 酵母 STE2 改造、嵌合 Gpa1 设计与构建、级联放大回路、显色输出与产品化 |
| 背景调研组 | 叙事与社会影响 | 危害与经济学分析、技术痛点对比、防治联动、安全性 |

## 关键受体信息

| 受体 | UniProt | 来源物种 | 结构状态 | AlphaFold DB |
|------|---------|---------|---------|-------------|
| Gpr3 | G1XJN1 | *A. oligospora* | AlphaFold 预测，已验证 | [AF-G1XJN1-F1](https://alphafold.ebi.ac.uk/entry/AF-G1XJN1-F1) |
| Gpr2 | G1X9E2 | *A. oligospora* | AlphaFold 预测，已验证 | [AF-G1X9E2-F1](https://alphafold.ebi.ac.uk/entry/AF-G1X9E2-F1) |
| GprC | A0A437AGY2 | *A. flagrans* | AlphaFold 预测，已验证 | [AF-A0A437AGY2-F1](https://alphafold.ebi.ac.uk/entry/AF-A0A437AGY2-F1) |

## Reporter 输出架构（已确认，参数待校准）

2026-05-25 按用户确认和实验方案附件，reporter 输出架构更新为：

```
异源 Gpr2/3 -> 嵌合 Gpa1 -> MAPK 级联 -> sTF -> GAL 多拷贝放大 -> 色素显色
```

这只确认输出层拓扑，不等同于已经固定所有湿实验参数。仍待校准子问题：

| 子问题 | 候选方向 | 决定时机 |
|---|---|---|
| 色素 reporter 类型 | Betaxanthin / Lycopene / amilCP / lacZ / GFP | 由表达量、显色时间、稳定性和底盘负担决定 |
| 整合位点 | HO / URA3 / TRP1 / 多位点级联 | 取决于报告基因数量与实际 copy-number 目标 |
| GAL 输出层实际拷贝数 | 1/2/4 copy 或其他湿实验实现 | 由 Fus3-Ste12/sTF 通量预算、背景泄漏和显色强度共同决定 |
| 输出层参数 | reporter gain、basal leak、Kc/EC50-like、Hill、Emax、显色时间 | 由 dose-response、time-course 和无配体阴性对照校准 |
| 读出形态 | 冻干酵母试纸 / 液体培养 / 琼脂板 | 与产品化路线一并决定 |

> **干实验对 reporter 输出层的处理**：P0 信号通路 ODE 建模应把 sTF -> GAL 多拷贝放大 -> 色素显色作为输出层结构，但具体数值仍是 `wet-lab required`。当前不应把 Fan 2024 的 CaSte2/GAL 参数、docking Delta G 或未验证湿实验假设直接写成本项目定论参数。

## 总览图填充建议

当前总览图中的空白应填“当前可交付物/缺口”，而不是暗示最终模型已经完成：

| 图中位置 | 建议文案 | 含义 |
|---|---|---|
| ODE 中间空白框 | ODE Solver / 剂量响应 + 拷贝数 + 泄漏扫参 | 下一阶段要实现的动态预测组件 |
| ODE 底部输出椭圆 | 检测限 / 动态范围 / 放大倍数建议 | ODE 完整后给湿实验的设计建议 |
| 经济效益底部输出椭圆 | ROI / break-even 曲线 / HP 参数回收清单 | P2 当前 MVP 能输出的经济讨论材料，最终 ROI 仍待校准 |

## 核心参考文献

| 文献 | 内容 |
|------|------|
| Kuo et al. (2024) *Nature Microbiology* | Gpr2/Gpr3 感知线虫信息素 |
| Hu et al. (2024) *Nature Microbiology* | GprC 激活线粒体并重编程真菌细胞 |
| Lengger & Jensen (2020) *FEMS Yeast Research* | 酵母 GPCR 信号工程综述 |
| Mukherjee et al. (2025) | 酵母底盘筛选真菌 GPCR |
| Hara et al. (2012) | 嵌合 Gpa1 C 末端设计模板 |
| Medici et al. (1997) | 嵌合 Gpa1-Gsα 融合 |
| Fan & Yuan (2024) *Biosensors and Bioelectronics* | GPCR + GAL4 级联放大酵母传感器 |
| Shaw et al. (2019) *Cell* | 酵母 GPCR 信号通路模块化调控模型 |
| Ladds et al. (2005) | 酵母 GPCR 异源表达综述 |

## iGEM 评审策略

详见 [干实验总策略](dry-lab-strategy.md) §4 部分。核心要求：**Model 与湿实验之间有实际互动**（model-experiment feedback loop），需完成至少一个 Design-Build-Test-Learn cycle。

## 变更记录

| 版本 | 日期 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| v3 | 2026-04-03 | 初版，底盘待定（方案 A/B 并列） | PRD v3 §1 提取 |
| v4 | 2026-04-11 | 锁定酵母-STE2 主线；明确嵌合 Gpa1 + 基因组整合；显色级联标 TBD；P3 升 P0；P2-biocontrol-lv 失效 | PI 确认底盘 |
| v4.1 | 2026-05-25 | 更新 reporter 输出架构为 sTF -> GAL 多拷贝放大 -> 色素显色；补总览图填充建议 | 用户确认实验方案附件中的 reporter 路径 |
