---
direction: P1-soil-diffusion
status: not_started
priority: P1
chassis_dependent: false
last_updated: 2026-04-03
---

# P1: 土壤中 ascaroside 扩散-检测模型

> 来源: PRD v3 §3.3 | iGEM 评审定位: 增强叙事完整性，支撑 Proposed Implementation

## 解决什么问题

如果试纸放在田间土壤中，ascarosides 从线虫分泌到接触试纸需要多久？检测有效半径是多少？这直接决定产品部署方案（试纸间距、出结果时间）的合理性。

**iGEM 价值**: 为 Integrated Human Practices 提供定量论据（"为什么试纸间距应该是 X cm"）。

## 方法路线

1. 建立 ascaroside 在土壤多孔介质中的扩散方程（Fick 定律 + 吸附项）
2. 考虑土壤含水量、有机质含量等参数
3. 模拟不同线虫密度下，试纸周围的 ascr 浓度分布随时间的变化
4. 结合 [P0-signal-pathway-ode](P0-signal-pathway-ode.md) 的灵敏度极限，计算检测有效半径

## 工具栈

| 工具 | 用途 |
|------|------|
| Python (NumPy, SciPy) | PDE 求解（有限差分法） |
| FEniCS | 如需 3D 有限元求解 |
| Matplotlib | 浓度场可视化 |

## 参数与数据来源

| 参数 | 典型值范围 | 来源 |
|------|-----------|------|
| ascaroside 分子扩散系数 | ~10⁻⁶ cm²/s（小有机分子量级） | 文献估算或 Stokes-Einstein |
| 土壤孔隙度 | 0.3-0.6 | 土壤科学文献 |
| 土壤含水量 | 0.1-0.4 (v/v) | 可变参数 |
| 有机质吸附系数 (Kd) | 待查 | 类似疏水性小分子文献 |
| 线虫 ascr 分泌速率 | 待确认（见 PRD §2.2 瓶颈） | 文献可能缺乏精确值 |

**注意**: 分泌速率数据可能不可获取。建模策略应为参数化/敏感性分析框架（"如果分泌速率在 X-Y 范围内，检测有效距离如何变化"），而非追求单一精确映射。

## 产出定义

- [ ] 检测有效距离 vs 线虫密度的关系图
- [ ] 最优试纸间距建议（基于不同土壤类型）
- [ ] 从部署试纸到出结果的时间预测
- [ ] 参数敏感性分析报告
- [ ] 产出文件位置: `experiments/diffusion/`

## 代码与实验关联

- **代码路径**: `src/modeling/diffusion/`
- **产出路径**: `experiments/diffusion/`
- **湿实验对接**:
  - 本方向产出 → HP 组：产品部署方案的定量支撑
  - 本方向产出 → 通路工程组：对传感器灵敏度的最低要求

## 学习成本与依赖

- **难度**: ★★★★☆（偏难，但方程本身不复杂，主要是 PDE 数值求解）
- **前置知识**: 偏微分方程基础、有限差分法
- **学习资源**: 见 [学习路线图 阶段四](../learning/roadmap.md)
- **预计时间**: 2-3 周

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §3.3 提取初始内容 | 文档体系搭建 |

## 进展记录

（暂无）

## 与其他方向的依赖关系

- **输出到**:
  - [P1-bayesian-inference](P1-bayesian-inference.md): 扩散模型作为正向模型的一部分
  - HP 组 Proposed Implementation: 部署方案定量论据
- **依赖于**:
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 传感器灵敏度极限（检测阈值）
