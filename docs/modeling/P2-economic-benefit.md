---
direction: P2-economic-benefit
status: framework_mvp
priority: P2
chassis_dependent: false
last_updated: 2026-05-23
---

# P2: 早期检测经济效益模型

> 来源: PRD v3 §3.5c + §2B | iGEM 评审定位: 完成"检测→预防"闭环，直接支撑 HP 和 Proposed Implementation
>
> **决策结论 (§2B.3)**: 本方向为防治建模的**最高优先**选择。

## 解决什么问题

量化"早期检测省了多少钱"。建立"无检测 vs 早期检测+干预"两种情景的成本-收益对比，为项目叙事提供经济论证。

**为什么是最高优先**: 数据可获取性极好、建模难度极低（纯算术）、对 HP 叙事价值最高、与检测系统耦合度最高。是完成"检测→预防"闭环叙事的最短路径。

## 方法路线

1. 收集作物损失函数数据: 线虫密度 vs 产量损失百分比
   - 经典来源: Sasser & Freckman (1987) 综述 + 后续更新
   - 按作物类型分类（大豆、马铃薯、小麦等）
2. 建立两种情景模型:
   - **情景 A（无检测）**: 农户在症状出现后才发现 → 线虫已建立种群 → 防治成本高、效果差
   - **情景 B（早期检测）**: 使用你们的传感器 → 种植前/早期发现 → 及时干预 → 损失减少
3. 计算各情景成本:
   - 检测试剂成本估算
   - 各防治手段成本（化学/生物/轮作）文献值
   - 作物产量损失的经济价值
4. 产出: ROI 曲线，"每提前 X 天检测可减少 Y% 经济损失"

## 工具栈

| 工具 | 用途 |
|------|------|
| Python (NumPy, Pandas) | 数据处理和计算 |
| Matplotlib / Plotly | 可视化（ROI 曲线、成本对比图） |

## 参数与数据来源

| 参数 | 来源 | 可获取性 |
|------|------|---------|
| 作物损失函数（密度 vs 产量损失%） | Sasser & Freckman 1987; Nicol et al. 2011 | ★★★★★ |
| 化学杀线虫剂成本（$/ha） | 农药市场报告、推广站数据 | ★★★★☆ |
| 生物防治菌剂成本 | 商业产品价格 | ★★★☆☆ |
| 抗性品种种子溢价 | 种子公司数据 | ★★★☆☆ |
| 作物市场价格 | FAO / USDA | ★★★★★ |
| 检测试剂成本估算 | 团队自估（材料成本） | 需团队提供 |

## 产出定义

- [ ] 作物损失函数图（至少 2-3 种主要作物）
- [ ] 成本-收益对比表（无检测 vs 早期检测）
- [ ] ROI 曲线: "每提前 X 天检测可减少 Y% 经济损失"
- [ ] 可用于 HP 组访谈的定量摘要
- [ ] 产出文件位置: `experiments/economic/`

## 代码与实验关联

- **代码路径**: `src/modeling/economic/`
- **产出路径**: `experiments/economic/`
- **HP 组对接**:
  - 本方向产出 → HP 组: 经济论据用于与农业专家、政策制定者访谈
  - 本方向产出 → Proposed Implementation: 量化检测系统的实际价值
  - HP 组反馈 → 本方向: 访谈中获得的真实成本数据可校准模型

## 学习成本与依赖

- **难度**: ★☆☆☆☆（基础算术建模，无需高级数学）
- **前置知识**: 基础 Python、简单的经济学概念
- **预计时间**: 1-2 周（含文献收集）

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-05-23 | v1.2 | 将 P2 文献/参数矩阵从 `tmp_papers/` 提升到 `docs/papers/p2-economic-benefit/`，并补充 HP 问卷路由与示例分析边界 | 长期留存与 DOCMAP 路由规范 |
| 2026-04-03 | v1.0 | 从 PRD v3 §3.5c + §2B 提取初始内容 | 文档体系搭建 |

## 进展记录

### 2026-05-21：Stage 1/2 文献参数矩阵 + MVP 框架

- Stage 1/2 调研产物已提升为长期文档：
  - `docs/papers/p2-economic-benefit/stage1-paper-data-matrix.md`
  - `docs/papers/p2-economic-benefit/stage2-parameter-extraction.md`
  - `docs/papers/p2-economic-benefit/stage2-model-parameters.csv`
  - `docs/papers/p2-economic-benefit/stage2-source-evidence.csv`
  - 原始 API/checkpoint 工作区仍保留在 `tmp_papers/p2_economic_benefit_20260521/`
- 最小 deterministic cost-accounting 框架已落地：
  - 代码：`src/modeling/economic/`
  - 示例配置：`experiments/economic/configs/public_mvp_framework.json`
  - 示例输出：`experiments/economic/results/public_mvp_framework_results.csv`
  - 示例解读：`experiments/economic/results/public_mvp_framework_summary.md`
- HP 参数回收材料：
  - `docs/modeling/P2-economic-benefit-hp-questionnaire.md`
- 当前可用公开参数：
  - tomato-RKN：UC IPM J2/kg soil → % normal yield piecewise table，可直接做 MVP 示例。
  - potato-PCN：EPPO/AHDB/APHIS 阈值与损失范围，可做归一化或占位场景。
  - soybean-SCN：UMN/Iowa 阈值、采样误差和 lab cost 可用，但密度-产量损失函数仍需全文抽取。
- 仍不可作为确定输入：
  - biosensor 单次成本、部署密度、灵敏度/特异性；
  - 当地作物价格、施药成本、人工/设备成本、抗性品种溢价、轮作机会成本；
  - docking Delta G、ODE Kd 或未验证 wet-lab 假设。

### 当前 MVP 示例分析边界

- 基线不是“完全不损失”，而是“没有早期检测/晚发现时，在给定线虫密度下承受的产量收入损失”。
- 早期检测情景暂不使用真实传感器成本；当前用 `early_program_costs_per_area` 做 50/100/200 USD/acre 等占位成本扫参。
- `intervention_effect` 不是某个药剂的确定疗效，而是“早发现+及时干预避免晚发现损失的比例”扫参；正式值需要 HP/湿实验/文献全文回填。
- tomato-RKN 是唯一可直接货币化的公开示例：UC IPM 表给出 500 spring J2/kg soil 对应 72% normal yield，示例产量 30 tons/acre，价格 54 USD/ton，所以晚发现毛损失为 `30 * 54 * 0.28 = 453.6 USD/acre`。
- potato-PCN 目前只是归一化结构验证；soybean-SCN 目前只是阈值决策骨架，二者不能作为本地 ROI 结论。

## 与其他方向的依赖关系

- **输出到**:
  - HP 组 Proposed Implementation（最直接的消费者）
  - iGEM wiki Modeling 页面（经济论证部分）
- **依赖于**:
  - [P1-bayesian-inference](P1-bayesian-inference.md)（可选）: 密度估计的不确定性 → 经济损失的不确定性区间
  - 基本可独立运行，不严格依赖其他建模方向
