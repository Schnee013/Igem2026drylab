---
direction: P2-dose-response
status: not_started
priority: P2
chassis_dependent: false
last_updated: 2026-04-03
---

# P2: 化学杀线虫剂剂量-响应模型

> 来源: PRD v3 §3.5a + §2B | iGEM 评审定位: 完成"检测→建议施药浓度"的定量链
>
> **决策结论 (§2B.3)**: 推荐辅助方向，与经济效益模型并行。

## 解决什么问题

提供"检测到什么信号 → 建议施多少药"的定量链路。建立常用杀线虫剂的剂量-响应模型，与密度推断串联，形成从传感器信号到施药建议的完整决策链。

## 方法路线

1. 从文献收集 2-3 种常用杀线虫剂对目标线虫的 LC50/EC50 数据:
   - 阿维菌素 (Avermectin)
   - 噻唑膦 (Fosthiazate)
   - 氟吡菌酰胺 (Fluopyram)
   - 目标物种: *M. incognita* / *H. glycines*
2. 建立 Hill / log-logistic 剂量-响应模型
3. 与 [P1-bayesian-inference](P1-bayesian-inference.md) 串联:
   传感器信号 → 线虫密度后验分布 → 推荐施药浓度范围

## 工具栈

| 工具 | 用途 |
|------|------|
| Python (SciPy `curve_fit`) | 剂量-响应曲线拟合 |
| R (`drc` 包) | 专业剂量-响应分析（备选） |
| Matplotlib | 可视化 |

## 参数与数据来源

| 数据 | 来源 | 可获取性 |
|------|------|---------|
| 阿维菌素 LC50/EC50 对 *M. incognita* | 农药毒理学文献 | ★★★★★ |
| 噻唑膦 LC50/EC50 | 同上 | ★★★★☆ |
| 氟吡菌酰胺 LC50/EC50 | 同上 | ★★★★☆ |
| Hill 系数 (n) | 文献拟合或自行拟合 | ★★★☆☆ |

## 产出定义

- [ ] 2-3 种杀线虫剂的剂量-响应曲线
- [ ] LC50/EC50 参数汇总表
- [ ] "检测信号 → 推荐施药浓度范围"的决策链图
- [ ] 产出文件位置: `experiments/dose-response/`

## 代码与实验关联

- **代码路径**: `src/modeling/dose-response/`
- **产出路径**: `experiments/dose-response/`
- **对接**:
  - 本方向产出 → Proposed Implementation: 具体施药建议
  - 串联 [P1-bayesian-inference](P1-bayesian-inference.md): 密度估计 → 施药浓度

## 学习成本与依赖

- **难度**: ★☆☆☆☆（最简单，纯数据拟合）
- **前置知识**: SciPy curve_fit 基础
- **预计时间**: 1 周

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|------|------|---------|---------|
| 2026-04-03 | v1.0 | 从 PRD v3 §3.5a 提取初始内容 | 文档体系搭建 |

## 进展记录

（暂无）

## 与其他方向的依赖关系

- **输出到**:
  - Proposed Implementation: 施药建议
  - iGEM wiki: 防治闭环量化论证
- **依赖于**:
  - [P1-bayesian-inference](P1-bayesian-inference.md)（可选）: 密度后验 → 施药浓度范围
  - 基本可独立运行（仅需文献 LC50 数据）
