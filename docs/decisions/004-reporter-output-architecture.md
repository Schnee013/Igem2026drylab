# 决策 004：Reporter 输出架构 — sTF + GAL 多拷贝放大 + 色素显色

- **日期**: 2026-05-25
- **状态**: 架构已确认，参数待校准
- **关联方向**:
  - [overview-v4](../prd/overview-v4.md)
  - [P0-signal-pathway-ode](../modeling/P0-signal-pathway-ode.md)
  - [P2-economic-benefit](../modeling/P2-economic-benefit.md)
  - [决策 003](003-chassis-yeast-ste2-integration.md)

## 背景

[决策 003](003-chassis-yeast-ste2-integration.md) 锁定了酿酒酵母 + STE2 通路 + 嵌合 Gpa1 + 基因组整合，但显色输出不在当时决策范围内。后续用户确认实验方案附件中的 reporter 路径，应把项目总览、ODE 接口和缺口说明从“显色级联 TBD”更新为“架构已确认、参数待校准”。

## 决定

采用以下 reporter 输出架构：

```
异源 Gpr2/3 -> 嵌合 Gpa1 -> MAPK 级联 -> sTF -> GAL 多拷贝放大 -> 色素显色
```

这里的 sTF 指 Ste12 PRD-Gal4DBD 类融合转录因子输出层；GAL 多拷贝放大作为下游 reporter 增益模块进入 ODE 的 copy-number/gain/leakage 扫参。

## 仍未决定

- 具体色素 reporter 类型：Betaxanthin、Lycopene 或其他显色/荧光读出。
- 整合位点与构建方式：HO、URA3、TRP1、多位点整合或其他湿实验实现。
- 实际 copy number：1/2/4 copy 或其他构型；“多拷贝放大”不等同于已经决定使用 2μ 质粒或固定拷贝数。
- 输出层定量参数：reporter gain、basal leak、Kc/EC50-like、Hill、Emax、显色时间、noise floor。
- 产品化读出条件：冻干酵母试纸、液体培养或琼脂板的最终判读流程。

## 后果

1. **ODE 建模**：sTF -> GAL 多拷贝放大 -> 色素显色作为输出层拓扑进入 P0 ODE；具体数值仍标记为 `wet-lab required` 或 `scenario prior`。
2. **文档状态**：`overview-v4.md` 和 `INDEX.md` 不再把整个显色级联写成 TBD；只保留具体色素、整合位点、实际拷贝数和输出层参数待校准。
3. **总览图填充**：ODE 中间框建议写“ODE Solver / 剂量响应 + 拷贝数 + 泄漏扫参”；ODE 输出椭圆写“检测限 / 动态范围 / 放大倍数建议”；经济效益输出椭圆写“ROI / break-even 曲线 / HP 参数回收清单”。
4. **证据边界**：不把 Fan 2024 的 CaSte2/GAL 参数直接迁移为本项目 Gpr-ascr 参数；不把 docking Delta G 或 ODE 未校准参数作为 wet-lab 或经济模型定论输入。

## 与决策 003 的关系

本记录只补充 reporter 输出架构。决策 003 仍是底盘、STE2 通路、嵌合 Gpa1 和基因组整合基线的权威记录；本记录不回改 2026-04-11 的历史决策内容。
