---
direction: P0-signal-pathway-ode
status: in_progress
priority: P0
chassis_dependent: true
last_updated: 2026-04-11
---

# P0: 信号通路 ODE 建模（酵母 STE2）

> 来源: PRD v3 §3.2 | iGEM 评审定位: 直接支撑湿实验设计
>
> **底盘已锁定**: *S. cerevisiae* + 内源 STE2 通路 + 嵌合 Gpa1 + **基因组单拷贝整合**（2026-04-11，PI 确认）。详见 [决策 003](../decisions/003-chassis-yeast-ste2-integration.md) / [overview-v4](../prd/overview-v4.md)。
>
> 本方向走**完整酵母 STE2 ODE 模型**，参数源 Shaw 2019 / Fan & Yuan 2024 / Ladds 2005。丝状真菌 ODE 表格（下方）保留为**历史备选 / 已不激活**。

## 解决什么问题

信号链路的定量预测:
- 系统能检测的最低 ascr 浓度是多少？
- 放大倍数如何选择？
- 背景泄漏对假阳性的影响？

**iGEM 价值**: 预测放大回路参数范围 → 湿实验据此选择 GAL4 promoter 强度 → 测量实际输出 → 用数据校准模型 → 完成 DBTL cycle。

## 通路结构（已锁定酵母）

```
异源 Gpr 受体（Gpr2/Gpr3/GprC，单拷贝整合，Top 6 突变体之一）
    │ ascr#18 / ascr#3 结合（Kd 来自 P0-docking Tier v2）
    ▼
嵌合 Gpa1（C 端嫁接真菌 Gα C 端，由 P0-chimeric-gprotein 提供 5/10/15 三档候选）
    │ GTP 结合 → Gβγ 释放
    ▼
Ste20 → Ste11 → Ste7 → Fus3 (MAPK 级联)
    │ 磷酸化
    ▼
Ste12（转录因子）
    │ 结合 pFUS1（或下游显色级联启动子，TBD）
    ▼
报告基因（lacZ / 颜色蛋白 / GAL4 间接放大，TBD）
```

**基线假设**：所有可调元件按**基因组单拷贝**整合于同一位点；不使用 CEN/2μ 质粒（避免拷贝数漂移破坏下游线性度）。

> **GAL4 正反馈警告**：Fan & Yuan 2024 的 GAL4 级联放大方案在多拷贝质粒下定量验证。在单拷贝整合下，正反馈增益可能弱于文献值，需在 ODE 中作为**拷贝数变量**显式建模并做敏感性分析。

## 历史备选（已不激活）

> 2026-04-11 底盘锁定酵母后，丝状真菌方案不再使用。下表保留为历史记录。

| 维度 | 酵母方案（策略 B，**已选**） | ~~丝状真菌方案（策略 A）~~ |
|------|-------------------|---------------------|
| 通路结构 | Gpr → 嵌合 Gpa1 → Ste11/Ste7/Fus3 MAPK → 报告基因 | ~~Gpr → 内源 Gα → MAPK/PKA → 内源响应启动子~~ |
| 参数可获取性 | ★★★★★ | ★★☆☆☆ |
| 建模可行性 | 高: 详细定量 ODE | 低: 粗粒度 Hill 函数 |
| 关键参考 | Shaw 2019 / Fan & Yuan 2024 / Ladds 2005 | ~~Hu 2024（间接推断）~~ |

## 方法路线

1. 将信号通路拆解为生化反应网络（Gpr → Gpa1 → MAPK → Ste12 → pFUS1 → 报告基因）
2. 用质量作用定律和 Hill 函数建立 ODE 模型，**显式包含拷贝数变量** N（基线 N=1）
3. 参数从文献获取（Shaw 2019 / Fan & Yuan 2024 / Ladds 2005 + Lengger 2020 综述补充）
4. **拷贝数敏感性分析**：N=1（基线）/ N=2（异源单倍体复制）/ N=4（双 cassette 整合），评估线性度与动态范围
5. 灵敏度分析：哪些参数对最终输出影响最大？
6. 优化下游显色级联接口（参数 TBD，待报告基因方案确定后回填）
7. **与 P0-docking 联动**：Top 6 突变体的 Vina ΔG → Kd 换算（用 Hu2024 / Kuo2024 实验值校准换算因子）→ 作为受体输入参数

## 工具栈

| 工具 | 用途 |
|------|------|
| Python (SciPy, NumPy, Matplotlib) | ODE 求解与可视化 |
| COPASI | 反应网络建模 GUI（快速原型） |
| PySB | Python 代码构建生化模型 |
| BioCRNpyler + AutoReduce | 从详细反应到简化 ODE 的自动化 |

## 参数与数据来源

### 酵母方案参数（已锁定，文献充足）

| 参数 | 来源 | 备注 |
|------|------|------|
| 异源 Gpr 配体结合 Kd | [P0-molecular-docking](P0-molecular-docking.md) Tier v2 + Hu2024/Kuo2024 实验值校准 | Top 6 突变体单独参数 |
| 嵌合 Gpa1 GTPase 速率 | Shaw 2019 / Hara 2012 | 假设 C 端 5/10/15 嵌合不显著影响 GTPase 域速率（待 MD 验证） |
| Gβγ 释放 / Sst2 RGS | Shaw 2019 *Cell* | |
| MAPK 级联动力学（Ste20/Ste11/Ste7/Fus3） | Shaw 2019 + Ladds 2005 | |
| Ste12 转录激活动力学 | Lengger 2020 综述 | |
| pFUS1 启动子强度 | Fan & Yuan 2024 + 酵母系统综述 | |
| GAL4 正反馈参数（若使用） | Fan & Yuan 2024 | **拷贝数敏感**：单拷贝下增益需重新评估 |
| 拷贝数 N | 干变量 | 基线 1，做 1/2/4 灵敏度 |

### ~~丝状真菌方案参数~~（已不激活）

> 历史备选，不再使用。原表保留：

| 参数 | 来源 | 可获取性 |
|------|------|---------|
| ~~Gpr-Gα 偶联速率~~ | ~~Hu 2024（间接推断）~~ | ★★☆☆☆ |
| ~~MAPK/PKA 动力学~~ | ~~几乎无文献值~~ | ★☆☆☆☆ |

## 产出定义

- [ ] 系统剂量-响应曲线（ascr 浓度 vs 报告基因输出，覆盖 Top 6 受体突变体）
- [ ] 灵敏度极限预测（最低可检测浓度）
- [ ] 放大倍数优化建议
- [ ] **拷贝数敏感性分析（1/2/4 copy 对比）** —— 基线整合策略下的核心交付
- [ ] 参数灵敏度分析报告（哪些参数的不确定性主导输出）
- [ ] 与湿实验的 model-experiment feedback loop 对照表
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
| 2026-04-11 | **v2.0** | status not_started → in_progress；锁定酵母 STE2 路径；新增基因组单拷贝整合基线 + 拷贝数敏感性分析；丝状真菌表保留为历史；与 P0-docking Tier v2 联动 | 底盘决策落地（[决策 003](../decisions/003-chassis-yeast-ste2-integration.md)） |

## 进展记录

（暂无）

## 与其他方向的依赖关系

- **输出到**:
  - [P1-soil-diffusion](P1-soil-diffusion.md): 灵敏度极限 → 检测有效距离计算
  - [P1-bayesian-inference](P1-bayesian-inference.md): 剂量-响应曲线 → 正向模型组件
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): Top 6 突变体的 Kd → ODE 输入参数（Vina ΔG → Kd 换算需用 Hu2024/Kuo2024 实验值校准）
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 嵌合 Gpa1 偶联效率 → ODE 中 Gpr-Gpa1 偶联速率
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发本方向激活
