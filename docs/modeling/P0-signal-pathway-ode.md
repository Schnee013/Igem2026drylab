---
direction: P0-signal-pathway-ode
status: in_progress
priority: P0
chassis_dependent: true
last_updated: 2026-05-23
---

# P0: 信号通路 ODE 建模（酵母 STE2）

> 来源: PRD v3 §3.2 | iGEM 评审定位: 直接支撑湿实验设计
>
> **底盘已锁定**: *S. cerevisiae* + 内源 STE2 通路 + 嵌合 Gpa1 + **基因组单拷贝整合**（2026-04-11，PI 确认）。详见 [决策 003](../decisions/003-chassis-yeast-ste2-integration.md) / [overview-v4](../prd/overview-v4.md)。
>
> 本方向走**完整酵母 STE2 ODE 模型**，参数源 Shaw 2019 / Kofahl 2004 / Yi 2003 / Brown 2000 / Ladds 2005 / Lengger 2020-2022 / Fan 2024 / Fan & Yuan 2023。丝状真菌 ODE 表格（下方）保留为**历史备选 / 已不激活**。
>
> **2026-05-20 输入接口校准**：P0 docking 线已提供刷新后的候选标签、双通道方向和相对排序；ODE 不直接使用 Vina ΔG 换算 Kd。配体结合/激活参数先作为文献校准或参数扫描变量，待 Hu2024/Kuo2024/酵母 GPCR 文献与后续湿实验剂量响应确认后再固定。

## 解决什么问题

信号链路的定量预测:
- 系统能检测的最低 ascr 浓度是多少？
- 放大倍数如何选择？
- 背景泄漏对假阳性的影响？

**iGEM 价值**: 预测放大回路参数范围 → 湿实验据此选择 GAL4 promoter 强度 → 测量实际输出 → 用数据校准模型 → 完成 DBTL cycle。

## 通路结构（已锁定酵母）

```
异源 Gpr 受体（Gpr2/Gpr3/GprC，单拷贝整合，P0-docking 刷新候选之一）
    │ ascr#18 / ascr#3 结合（Kd/EC50 为文献校准或参数扫描变量）
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

> **GAL4 正反馈警告**：Fan et al. 2024 的 GAL4 级联放大方案与 Fan & Yuan 2023 的 GAL regulon 输出层均在不同构建背景下定量验证。在本项目单拷贝整合下，正反馈增益可能弱于文献值，需在 ODE 中作为**拷贝数变量**显式建模并做敏感性分析。

## 历史备选（已不激活）

> 2026-04-11 底盘锁定酵母后，丝状真菌方案不再使用。下表保留为历史记录。

| 维度 | 酵母方案（策略 B，**已选**） | ~~丝状真菌方案（策略 A）~~ |
|------|-------------------|---------------------|
| 通路结构 | Gpr → 嵌合 Gpa1 → Ste11/Ste7/Fus3 MAPK → 报告基因 | ~~Gpr → 内源 Gα → MAPK/PKA → 内源响应启动子~~ |
| 参数可获取性 | ★★★★★ | ★★☆☆☆ |
| 建模可行性 | 高: 详细定量 ODE | 低: 粗粒度 Hill 函数 |
| 关键参考 | Shaw 2019 / Fan 2024 / Fan & Yuan 2023 / Ladds 2005 | ~~Hu 2024（间接推断）~~ |

## 方法路线

1. 将信号通路拆解为生化反应网络（Gpr → Gpa1 → MAPK → Ste12 → pFUS1 → 报告基因）
2. 用质量作用定律和 Hill 函数建立 ODE 模型，**显式包含拷贝数变量** N（基线 N=1）
3. 参数从文献获取或设为先验（Shaw 2019 / Kofahl 2004 / Yi 2003 / Brown 2000 / Ladds 2005 / Lengger 2020-2022 / Fan 2024 / Fan & Yuan 2023）
4. **拷贝数敏感性分析**：N=1（基线）/ N=2（异源单倍体复制）/ N=4（双 cassette 整合），评估线性度与动态范围
5. 灵敏度分析：哪些参数对最终输出影响最大？
6. 优化下游显色级联接口（参数 TBD，待报告基因方案确定后回填）
7. **与 P0-docking 联动**：读取刷新后的候选标签、Channel A/B 方向、D/balance 和相对排序；不要把 Vina ΔG 直接换算成 Kd。ODE 中的配体结合/激活参数用文献校准范围、湿实验剂量响应或敏感性扫描定义。

## ODE 输入接口（2026-05-20）

P0 docking 当前能提供：

- 候选集合与优先级：首选 `Gpr2_R59C + Gpr3_R167Y`；B 端备选 `Gpr3_V138M/R167P/R167C`；A 端备选 `Gpr2_R59F/R59T`；`GprC_Q411S` 仅作探索性备选并保留 GprC caveat。
- 每个候选的双通道方向：Channel A 偏 ascr#18，Channel B 偏 ascr#3。
- 相对排序证据：`sel_mut`、D、balance、IFP 接触差异，用于设定模型场景和优先级。
- WT Gpr2 / WT Gpr3 baseline 标签，用于湿实验和模型校准对照。

P0 docking 当前不能直接提供：

- 真实 Kd、kon/koff、EC50、Emax 或受体激活效率。
- Vina ΔG 到 Kd 的可直接套用换算因子。
- 异源 Gpr 与嵌合 Gpa1 在酵母中的偶联效率。

ODE 当前应这样消费 docking 输出：

1. 用 docking handoff 选定 receptor-ligand 场景集合，而不是生成固定 Kd 表。
2. 对每个 receptor-ligand pair 设置待校准参数：`K_L`/EC50-like half activation、ligand efficacy、basal activity、最大输出比例。
3. 用文献或湿实验剂量响应给这些参数设定先验范围；文献不足时做 log-scale 参数扫描。
4. 在报告中明确区分“docking 排名假设”和“ODE 数值参数假设”。

## 参数证据矩阵与校准计划（2026-05-23）

本节来自 API-first 二阶段抽取文件：`tmp_papers/ode_api_refresh_20260521/stage2_value_extraction_matrix.md`。它是 ODE 准备证据包，不是最终参数表。

状态标签：

- `fixed from source`：可固定模型结构、变量定义、方法或来源内定义，不代表可迁移所有数值。
- `literature prior`：可作为先验范围、情景倍率或工程边界，进入敏感性分析。
- `scenario prior`：文献不足时的操作性扫描范围，必须标注为假设。
- `wet-lab required`：必须由本项目 dose-response、time-course、表达/定位或偶联实验校准。
- `do-not-use`：不得进入 ODE 数值参数。

| 问题 | 参数/模块 | 主要来源 | 当前状态 | ODE 使用方式 |
|------|-----------|----------|----------|--------------|
| 酵母 GPCR-MAPK 通路拓扑是否可先固定？ | GPCR → Gpa1/Gbetagamma → Ste20/Ste11/Ste7/Fus3 → Ste12/reporter | Shaw 2019 `10.1016/j.cell.2019.02.023`; Kofahl 2004 `10.1002/yea.1122`; Yi 2003 `10.1073/pnas.1834247100` | `fixed from source` for topology; rate constants `manual pending` | 先固定模块顺序和状态变量类别；SBML/补充表未抽完前不固定具体速率 |
| Gpr2/Gpr3/GprC 配体结合和激活强度能否由文献固定？ | `Kd`, `kon`, `koff`, EC50/Kc, Emax, Hill | Hu 2024 `10.1038/s41564-024-01731-9`; Kuo 2024 `10.1038/s41564-024-01679-w` | `wet-lab required`; docking constants `do-not-use` | Hu/Kuo 支持受体身份、机制和 native 条件，不提供可迁移 wet `Kd/EC50`；本项目只能先扫参 |
| 异源 Gpr 与嵌合 Gpa1 偶联如何处理？ | 偶联效率、basal leak、G protein cycle | Brown 2000 `10.1002/(SICI)1097-0061(20000115)16:1<11::AID-YEA497>3.0.CO;2-K`; Ladds 2005 `10.1016/j.tibtech.2005.05.007`; Lengger 2020 `10.1093/femsyr/foz087`; Lengger 2022 `10.1021/acssensors.1c02061`; Tehseen 2014 `10.1371/journal.pone.0111429` | `literature prior`; project coupling `wet-lab required` | 用作偶联效率和 basal leak 的宽先验；Gpr2/Gpr3 与项目 chimeric Gpa1 必须实测 |
| reporter / promoter / GAL4 放大能否迁移？ | reporter gain、pFUS1/GAL4/sTF 输出、LOD/LOQ、T50、copy-number effect | Fan 2024 `10.1016/j.bios.2024.116058`; Fan & Yuan 2023 `10.1016/j.crmeth.2023.100647`; Miettinen 2022 `10.1038/s41467-022-31357-6`; Shaw 2019 | `literature prior`; single-copy gain `wet-lab required` | 用作输出层结构和增益/时间尺度先验；单拷贝整合下必须重新标定 |
| 缺少 binding 参数时如何建模？ | log-scale scan、profile likelihood、sloppy sensitivity | Simpson & Maclaren 2023 `10.1371/journal.pcbi.1011515`; Gutenkunst 2007 `10.1371/journal.pcbi.0030189`; Raue 2009 `10.1093/bioinformatics/btp358` | `literature prior` for method | 第一版只输出参数接口、扫描范围和可识别性计划；数据到位后做 profile likelihood |
| docking 刷新结果如何进入 ODE？ | candidate label、Channel A/B、relative rank、IFP clue | `ratio_channel_report.md`; `ratio_pairings.csv`; `wet-lab-handoff-P0-docking.md`; 2026-05-19/20 logs | constants `do-not-use`; labels/ranking usable | 只定义场景集合和优先级；严禁把 Vina Delta G 换算为 `Kd/EC50` |

### 建议扫描范围（非定论）

| 参数 | 初始建议 | 状态 | 替换条件 |
|------|----------|------|----------|
| `K_L` / EC50-like ligand half activation | 主扫描 `1e-9` 到 `1e-3` M；压力测试 `1e-12` 到 `1e-2` M | `scenario prior` | 本项目 dose-response 给出 EC50/Kc 后替换 |
| Hill coefficient | `0.5` 到 `3` | `scenario prior` | 本项目剂量响应拟合后替换 |
| ligand efficacy / Gpr-Gpa1 coupling efficiency | 归一化 `1e-3` 到 `1` | `scenario prior` | chimeric Gpa1 functional coupling 数据后替换 |
| basal leak | 归一化 `1e-4` 到 `0.2` | `scenario prior` | no-ligand reporter 和阴性对照后替换 |
| reporter amplification gain | `1` 到 `100`，按 pFUS1 direct 或 GAL4/sTF 方案分情景 | `scenario prior` | reporter 构型、copy number 和 time-course 数据后替换 |

### 湿实验需求表

| 对象/决定 | 必测数据 | 进入 ODE 的用途 | 状态 |
|-----------|----------|----------------|------|
| WT Gpr2、WT Gpr3、`Gpr2_R59C`、`Gpr3_R167Y` | ascr#18 与 ascr#3 dose-response；无配体、低 nM、uM、mM 点 | EC50/Kc、Emax、Hill、basal leak、A/B 通道分离 | `wet-lab required` |
| 备选突变：`Gpr3_V138M/R167P/R167C`、`Gpr2_R59F/R59T`、探索性 `GprC_Q411S` | 同一 dose-response panel | 验证 docking 场景标签和相对优先级 | `wet-lab required` |
| reporter 方案：pFUS1 直连、GAL4/sTF、荧光、lacZ、NanoLuc 或显色模块 | reporter-specific dose-response、basal、dynamic range | 输出层 gain、噪声、最大输出和降解/稀释项 | `wet-lab required` |
| 底盘编辑：`Δsst2`、`Δbar1`、Gpa1 过表达、GAL4 feedback | 每项对应阴性/阳性对照 | 区分灵敏度提升、leak 和生长/报告伪影 | `wet-lab required` |
| time-course | 早期 MAPK/reporter 激活和 2-8 h 稳态输出 | 响应时间、reporter production/degradation/dilution | `wet-lab required` |
| 表达/定位与偶联 | 受体膜定位/表达；chimeric Gpa1 coupling 功能读出 | 区分 trafficking failure、ligand activation failure 和 coupling failure | `wet-lab required` |

### 建模建议

- 可固定：酵母 pheromone/MAPK 拓扑、状态变量类别、reporter 方程形式、LOD/LOQ/Hill fitting 定义，以及 docking 刷新后的候选标签集合。
- 可作为文献先验：异源 GPCR-Gpa1 偶联效率量级、basal leak 风险、reporter/GAL4 放大和时间尺度。
- 只能作为 scenario prior：Gpr-ascr 半激活浓度、efficacy、Hill、basal leak、reporter gain 的项目数值。
- 必须等待湿实验：每个 mutant/ascr pair 的 `Kd/kon/koff/EC50/Kc/Emax/Hill`、表达/定位、chimeric Gpa1 coupling、单拷贝 reporter gain。
- 禁用：Vina 或 SwissDock Delta G 到 `Kd/EC50` 的直接换算，旧 `Gpr2_M327A + Gpr3_V138T` Top 说法，以及未刷新 IFP 机制解释。

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
| 异源 Gpr 配体结合/激活参数 | [P0-molecular-docking](P0-molecular-docking.md) 提供候选标签与相对排序；Kd/EC50/efficacy 需文献或湿实验校准 | 不直接由 Vina ΔG 换算；先做参数范围/敏感性扫描 |
| 嵌合 Gpa1 GTPase 速率 | Shaw 2019 / Hara 2012 | 假设 C 端 5/10/15 嵌合不显著影响 GTPase 域速率（待 MD 验证） |
| Gβγ 释放 / Sst2 RGS | Shaw 2019 *Cell* | |
| MAPK 级联动力学（Ste20/Ste11/Ste7/Fus3） | Shaw 2019 + Ladds 2005 | |
| Ste12 转录激活动力学 | Lengger 2020 综述 | |
| pFUS1 启动子强度 | Fan 2024 / Fan & Yuan 2023 + 酵母系统综述 | |
| GAL4 正反馈参数（若使用） | Fan 2024 / Fan & Yuan 2023 | **拷贝数敏感**：单拷贝下增益需重新评估 |
| 拷贝数 N | 干变量 | 基线 1，做 1/2/4 灵敏度 |

### ~~丝状真菌方案参数~~（已不激活）

> 历史备选，不再使用。原表保留：

| 参数 | 来源 | 可获取性 |
|------|------|---------|
| ~~Gpr-Gα 偶联速率~~ | ~~Hu 2024（间接推断）~~ | ★★☆☆☆ |
| ~~MAPK/PKA 动力学~~ | ~~几乎无文献值~~ | ★☆☆☆☆ |

## 产出定义

- [ ] 系统剂量-响应曲线（ascr 浓度 vs 报告基因输出，覆盖 refreshed docking handoff 候选场景）
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
| 2026-04-11 | **v2.0** | status not_started → in_progress；锁定酵母 STE2 路径；新增基因组单拷贝整合基线 + 拷贝数敏感性分析；丝状真菌表保留为历史；与 P0-docking 双通道分析联动 | 底盘决策落地（[决策 003](../decisions/003-chassis-yeast-ste2-integration.md)） |
| 2026-05-20 | **v2.1** | 修正 docking→ODE 输入接口：docking 只提供候选标签/方向/排序，Kd/EC50/efficacy 进入文献校准或参数扫描门控 | docking-repro full refresh 完成，但 Vina ΔG 不可直接换算 Kd |
| 2026-05-23 | **v2.2** | 新增参数证据矩阵与校准计划；按 `fixed from source` / `literature prior` / `scenario prior` / `wet-lab required` / `do-not-use` 标注 ODE 参数状态 | API-first ODE 文献二阶段抽取完成，进入建模准备但不生成定论参数表 |

## 进展记录

（暂无）

## 与其他方向的依赖关系

- **输出到**:
  - [P1-soil-diffusion](P1-soil-diffusion.md): 灵敏度极限 → 检测有效距离计算
  - [P1-bayesian-inference](P1-bayesian-inference.md): 剂量-响应曲线 → 正向模型组件
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): refreshed handoff 候选标签、Channel A/B 方向、相对排序和 WT baseline；Kd/EC50/efficacy 需文献或湿实验校准，不由 Vina ΔG 直接换算
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 嵌合 Gpa1 偶联效率 → ODE 中 Gpr-Gpa1 偶联速率
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发本方向激活
