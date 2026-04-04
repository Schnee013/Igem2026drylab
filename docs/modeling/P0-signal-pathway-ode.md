---
direction: P0-signal-pathway-ode
status: not_started
priority: P0
chassis_dependent: true
last_updated: 2026-04-03
---

# P0: 信号通路 ODE 建模

> 来源: PRD v3 §3.2 | iGEM 评审定位: 直接支撑湿实验设计
>
> **底盘依赖**: 建模策略因底盘不同而分为策略 A（丝状真菌）和策略 B（酵母）。详见 [底盘决策分析](../prd/chassis-decision.md)。
>
> **当前建议**: 在底盘确定前，先用酵母方案建模（数据充足），模型框架可在切换时复用。

## 解决什么问题

信号链路的定量预测:
- 系统能检测的最低 ascr 浓度是多少？
- 放大倍数如何选择？
- 背景泄漏对假阳性的影响？

**iGEM 价值**: 预测放大回路参数范围 → 湿实验据此选择 GAL4 promoter 强度 → 测量实际输出 → 用数据校准模型 → 完成 DBTL cycle。

## 双底盘策略对比

| 维度 | 酵母方案（策略 B） | 丝状真菌方案（策略 A） |
|------|-------------------|---------------------|
| 通路结构 | Gpr → 嵌合 Gpa1 → Ste11/Ste7/Fus3 MAPK → GAL4 正反馈 → 报告基因 | Gpr → 内源 Gα → MAPK/PKA → 内源响应启动子 → 报告基因 |
| 参数可获取性 | ★★★★★ | ★★☆☆☆ |
| 建模可行性 | 高: 详细定量 ODE | 低: 粗粒度 Hill 函数近似 |
| 关键参考 | Shaw 2019 *Cell*; Fan & Yuan 2024 | Hu 2024 *Nature Microbiology* |

## 方法路线

1. 将信号通路拆解为生化反应网络
2. 用质量作用定律和 Hill 函数建立 ODE 模型
3. 参数从文献获取（酵母 pheromone pathway 有大量已知参数）
4. 灵敏度分析: 哪些参数对最终输出影响最大？
5. 优化放大回路设计参数

## 工具栈

| 工具 | 用途 |
|------|------|
| Python (SciPy, NumPy, Matplotlib) | ODE 求解与可视化 |
| COPASI | 反应网络建模 GUI（快速原型） |
| PySB | Python 代码构建生化模型 |
| BioCRNpyler + AutoReduce | 从详细反应到简化 ODE 的自动化 |

## 参数与数据来源

### 酵母方案参数（文献充足）

| 参数 | 来源 |
|------|------|
| Ste2/Ste3 配体结合 Kd | 酵母 GPCR 文献 |
| Gpa1 GTPase 速率 | Shaw et al. 2019 |
| MAPK 级联动力学参数 | 多篇酵母信号文献 |
| GAL4 正反馈参数 | Fan & Yuan 2024 |

### 丝状真菌方案参数（稀缺）

| 参数 | 来源 | 可获取性 |
|------|------|---------|
| Gpr-Gα 偶联速率 | Hu 2024（间接推断） | ★★☆☆☆ |
| MAPK/PKA 动力学 | 几乎无文献值 | ★☆☆☆☆ |
| 响应启动子强度 | 需转录组数据 | TBD |

## 产出定义

- [ ] 系统剂量-响应曲线（ascr 浓度 vs 报告基因输出）
- [ ] 灵敏度极限预测（最低可检测浓度）
- [ ] 放大倍数优化建议
- [ ] 参数灵敏度分析报告
- [ ] 产出文件位置: `experiments/ode-model/`

## 代码与实验关联

- **代码路径**: `src/modeling/ode/`
- **产出路径**: `experiments/ode-model/`
- **湿实验对接**:
  - 本方向产出 → 通路工程组: 推荐 GAL4 promoter 强度、放大回路参数
  - 湿实验反馈 → 本方向: 实际剂量-响应数据，校准模型参数

## 学习成本与依赖

- **难度**: ★★☆☆☆（有 Python 基础，主要学 ODE 建模思路）
- **学习资源**: 见 [学习路线图 阶段一 + 阶段三](../learning/roadmap.md)
- **关键参考**: Shaw et al. 2019 *Cell* 中的模型可作为直接起点

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §3.2 提取，含双底盘策略 | 文档体系搭建 |

## 进展记录

（暂无）

## 与其他方向的依赖关系

- **输出到**:
  - [P1-soil-diffusion](P1-soil-diffusion.md): 灵敏度极限 → 检测有效距离计算
  - [P1-bayesian-inference](P1-bayesian-inference.md): 剂量-响应曲线 → 正向模型组件
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): 结合亲和力 Kd → ODE 模型输入参数
  - [底盘决策](../prd/chassis-decision.md): 决定使用策略 A 还是 B
