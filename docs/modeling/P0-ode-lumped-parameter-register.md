---
artifact: P0-ode-lumped-parameter-register
status: active
priority: P0
last_updated: 2026-08-10
---

# P0 ODE Phase 0/1：lumped 方程与参数状态/缺口登记表

> 本表是当前 Phase 0 最小求解器和 Phase 1 归一化工程情景扫描的参数登记入口。Phase 0 给出单一 time-course；Phase 1 只在显式 `scenario_prior` 网格中扫描剂量/半响应、偶联/泄漏、copy/gain/观察时间。两者都不构成真实浓度、亲和力、动力学常数、检测限或最优构型预测。参数范围、潜在可观测量和证据缺口以 [Phase 2A 机器合同](../../experiments/ode-model/configs/phase2a_analysis_contract.json) 为准；领域解释和文献边界回到 [P0 信号通路 ODE](P0-signal-pathway-ode.md)。

## 一页结论

- **3 个动态状态**：`G_on`、`M`（lumped MAPK）和 `C`（色素信号）。
- **3 个代数接口**：`R_active`、`TF`、`Prod`；每一时刻由上游状态直接计算，不单独积分。
- **18 个内部可配置参数**：受体 4、G protein 2、MAPK 2、转录/sTF 4、GAL 输出 4、色素 2。
- **3 个外部控制量**：归一化 ligand、模拟时长、输出点数；它们不属于生物动力学参数。
- **3 个初始条件**在代码中固定为零，`G_total=M_total=1` 是归一化容量尺度，均不计入 18 个参数。
- 18 个当前数值全部来自 [最小情景配置](../../experiments/ode-model/configs/minimal_normalized_scenario.json)。其中 6 项的项目状态是 `scenario_prior`，12 项是 `wet-lab required`。后一个现有标签表示项目证据缺口；它不指定测量方案，也不要求逐参数独立测量。对应数值只是可运行占位值，不是项目已测数。
- [Phase 1 suite](../../experiments/ode-model/configs/stage1_scenario_scan.json) 不增加新的生物学定值，而是对现有字段建立可复现情景网格。当前网格为 143 个情景：74 个 ligand 情景、69 个一对一无 ligand 对照和 23,023 条完整 time-course 记录。
- Phase 1 紧凑结果、输入快照和外部 time-course checksum 合同见 [结果包](../../experiments/ode-model/results/stage1_scenario_scan/README.md)。requested 轴值与 effective solver 输入分开记录；control 的 effective ligand 恒为 `0.0`。

| 对象 | 数量 | 当前实现 | 校准处理 |
|---|---:|---|---|
| 动态状态 | 3 | `G_on`, `M`, `C` | 由求解器计算 |
| 代数接口 | 3 | `R_active`, `TF`, `Prod` | 函数形式固定；参数多数待校准 |
| 内部可配置参数 | 18 | 六个方程模块 | 按下表状态使用 |
| 外部控制量 | 3 | `ligand_normalized`, `duration_hours`, `output_points` | 模拟情景与数值输出条件，不作拟合常数 |
| 初始条件 | 3 | `G_on(0)=M(0)=C(0)=0` | Phase 0 设计假设；有基线数据后可改 |
| 隐含容量 | 2 | `G_total=M_total=1` | 归一化尺度，不表示真实分子总量 |

## 方程骨架：逐项读法

令 `L` 为归一化 ligand 输入，`G=G_on`，`M=mapk_active`，`C=color_signal`。当前代码实现为：

```text
R_active = b_R + E_R * L^n_R / (K_R^n_R + L^n_R)

dG/dt = k_couple * R_active * (1 - G) - k_deact * G

dM/dt = k_mapk_on * G * (1 - M) - k_mapk_off * M

TF = b_TF + E_TF * M^n_TF / (K_TF^n_TF + M^n_TF)

Prod = leak_out + N * gain_out * TF / (K_out + TF)

dC/dt = k_color_prod * Prod - k_color_loss * C
```

| 对象或项 | 数学角色 | 生物学解释 | 当前单一输入情景中的行为 |
|---|---|---|---|
| `R_active` | 代数接口 | ligand 触发异源 Gpr 的有效活性 | `L` 在 8 h 内不变，故 `R_active` 也不变 |
| `k_couple * R_active * (1-G)` | `G` 正项 | 未激活 G protein 池被受体信号转化 | `(1-G)` 防止归一化活性超过 1 |
| `k_deact * G` | `G` 负项 | G protein 失活/恢复的有效过程 | 未拆成完整 GTPase 反应网络 |
| `k_mapk_on * G * (1-M)` | `M` 正项 | G protein/Gβγ 有效信号推动 MAPK 活化 | Ste20/Ste11/Ste7/Fus3 压缩成一个节点 |
| `k_mapk_off * M` | `M` 负项 | MAPK 去磷酸化或恢复 | 不代表单一已测磷酸酶速率 |
| `TF` | 代数接口 | MAPK 到 Ste12/sTF 的转录输入—输出关系 | 尚未拆分转录、翻译和延迟 |
| `Prod` | 代数接口 | sTF 经 GAL 输出层形成的有效 reporter 生产速率 | 显式保留 copy、gain、leak 和饱和性 |
| `k_color_prod * Prod - k_color_loss * C` | `C` 方程 | 显色产生与降解、稀释或衰减 | 显色成熟延迟尚未单独建模 |

方程、字段名和验证条件以 [最小求解器](../../src/modeling/ode/minimal_solver.py) 为准；本表仅解释参数及证据边界。

## 来源键

| 键 | 当前数值来源或可用于替换的证据 |
|---|---|
| `C0` | [最小情景配置](../../experiments/ode-model/configs/minimal_normalized_scenario.json)：唯一的当前数值来源；顶层强制标为 `scenario_prior`。 |
| `E1` | [P0 ODE 文档](P0-signal-pathway-ode.md) 的 Stage 3 checkpoint：Shaw 2019、Kofahl 2004、Yi 2003 可固定通路拓扑/变量类别；未完成单位和 kinetic-law 映射的速率值仍为 `do-not-use`。 |
| `E2` | [Phase 2A 参数空间](../../experiments/ode-model/configs/phase2a_parameter_space.csv) 与 [P0 ODE 文档](P0-signal-pathway-ode.md) 的证据 checkpoint：规定分析范围、潜在可观测量和证据缺口，不提供本项目定值。 |
| `E3` | Brown 2000、Ladds 2005、Lengger 2020/2022 等异源 GPCR—酵母偶联先例：只能作 `literature prior`，不迁移为 Gpr—嵌合 Gpa1 常数。exact pointer 见 `E2`。 |
| `E4` | Fan 2024、Fan C & Yuan 2023、Miettinen 2022、Shaw 2019 的 reporter/GAL 先例：只支持函数形式、工程先验和潜在可观测量类别；不迁移其特定系统拟合值。exact pointer 见 [P0 ODE 文档](P0-signal-pathway-ode.md)。 |
| `D1` | [决策 003](../decisions/003-chassis-yeast-ste2-integration.md)：基因组单拷贝整合是底盘基线。 |
| `D2` | [决策 004](../decisions/004-reporter-output-architecture.md)：`sTF -> GAL 多拷贝放大 -> 色素显色` 拓扑已确认，实际 copy/gain/leak/色素参数待校准。 |

## 18 个内部可配置参数

“当前值”是 `C0` 中本次 smoke scenario 使用的无量纲数或有效速率，并非文献给出的项目常数。“项目状态”回答该参数现在能否作为项目数值固定。

| 模块 | 符号（config 字段） | 当前值 / 单位 | 项目状态 | 当前值来源 | 潜在可观测量与当前证据缺口 |
|---|---|---:|---|---|---|
| 受体 | `b_R` (`basal_activity`) | 0.02，无量纲 | `scenario_prior` | `C0` | 受体通路背景；当前项目证据不能把受体背景与下游背景分开。 |
| 受体 | `E_R` (`efficacy`) | 0.78，无量纲 | `scenario_prior` | `C0` | 受体通路响应幅度；当前项目证据不能把受体贡献与下游增益分开。 |
| 受体 | `K_R` (`half_activation_normalized`) | 1.0，归一化 ligand | `scenario_prior` | `C0` | ligand 响应转折位置；归一化 ligand 尚未映射到项目响应尺度。 |
| 受体 | `n_R` (`hill_coefficient`) | 1.5，无量纲 | `scenario_prior` | `C0` | ligand 响应转折形状；当前缺少支持参数级解释的转折区证据。 |
| G protein | `k_couple` (`coupling_rate_per_hour`) | 1.2 h⁻¹ | `wet-lab required` | `C0` 占位值 | 早期受体到通路动力学；与受体 efficacy 和 MAPK 激活混杂。 |
| G protein | `k_deact` (`deactivation_rate_per_hour`) | 0.45 h⁻¹ | `wet-lab required` | `C0` 占位值 | 早期通路恢复动力学；与下游恢复和读出损失混杂。 |
| lumped MAPK | `k_mapk_on` (`activation_rate_per_hour`) | 1.0 h⁻¹ | `scenario_prior` | `C0` | MAPK 层上升动力学；与上游偶联混杂。 |
| lumped MAPK | `k_mapk_off` (`deactivation_rate_per_hour`) | 0.3 h⁻¹ | `scenario_prior` | `C0` | MAPK 层恢复动力学；与上游恢复和下游持续性混杂。 |
| sTF | `b_TF` (`basal_activity`) | 0.01，无量纲 | `wet-lab required` | `C0` 占位值 | 转录层背景；与受体背景和输出层背景混杂。 |
| sTF | `E_TF` (`efficacy`) | 0.85，无量纲 | `wet-lab required` | `C0` 占位值 | 转录层响应幅度；与上游激活和输出增益混杂。 |
| sTF | `K_TF` (`half_activation`) | 0.25，无量纲 M | `wet-lab required` | `C0` 占位值 | MAPK 到转录层的转折位置；上游活性尺度与转录响应尚未联合观测。 |
| sTF | `n_TF` (`hill_coefficient`) | 2.0，无量纲 | `wet-lab required` | `C0` 占位值 | MAPK 到转录层的转折形状；当前缺少支持参数级解释的转折区证据。 |
| GAL | `N` (`copy_number`) | 1，离散有效 copy | 基线 `fixed from source`；输出效应 `wet-lab required` | `C0`；基线设计 `D1` | 构建 copy-number 身份；1/2/4 是分析分层，项目构建身份仍待团队确认。 |
| GAL | `leak_out` (`leak_rate`) | 0.005，有效产率 | `wet-lab required` | `C0` 占位值 | 输出层背景；与上游 basal signaling 混杂。 |
| GAL | `gain_out` (`gain_rate`) | 0.4，有效产率 | `wet-lab required` | `C0` 占位值 | 输出层响应幅度；与 copy number、转录 efficacy 和色素生成混杂。 |
| GAL | `K_out` (`half_activation`) | 0.25，无量纲 TF | `wet-lab required` | `C0` 占位值 | 转录到输出层的转折位置；转录输入尺度与输出响应尚未联合观测。 |
| 色素 | `k_color_prod` (`production_rate_per_hour`) | 1.0 h⁻¹ | `wet-lab required` | `C0` 占位值 | 读出上升动力学；与输出增益和成熟过程混杂。 |
| 色素 | `k_color_loss` (`loss_rate_per_hour`) | 0.12 h⁻¹ | `wet-lab required` | `C0` 占位值 | 读出持续动力学；与降解、稀释和生长混杂。 |

## 外部控制量、初始条件与归一化尺度

这些量影响模拟，却不应被计入“18 个内部生物/工程参数”。

| 类别 | 量 | 当前值 | 来源 | 状态与处理 |
|---|---|---:|---|---|
| 输入 | `L` (`ligand_normalized`) | Phase 0 为 1.0；Phase 1 扫描 0–1000 的归一化轴 | `C0` / Phase 1 suite | 无量纲情景输入，不是 ascr 摩尔浓度，也不是 docking 亲和力；Phase 1 扫描没有把它升级为有单位剂量。 |
| 时间设计 | `duration_hours` | 8.0 h | `C0` | 示意观察窗口；需结合实际显色 time-course 修订。 |
| 数值输出 | `output_points` | 161 | `C0` | 数值采样密度，不是生物学参数。 |
| 初值 | `G_on(0)`、`M(0)`、`C(0)` | 0、0、0 | 求解器 `y0=np.zeros(3)` | Phase 0 清零设计，用于展示 input-induced trajectory；有基线/预激活数据后需显式记录。 |
| 归一化容量 | `G_total`、`M_total` | 1、1 | 方程中的 `(1-G)`、`(1-M)` | 将可激活池限制在 0–1；不是蛋白拷贝数或绝对浓度。 |

## 参数—潜在可观测量—证据缺口

[Phase 2A 参数空间](../../experiments/ode-model/configs/phase2a_parameter_space.csv) 是这一映射的机器可读权威。Phase 2A 只登记潜在可观测量类别和当前证据缺口；Phase 2B 给出模型侧敏感性，Phase 2C 检查参数及参数组合在候选观测类别下的可识别性。具体 assay、实验对照、采样设计和实验优先级在后续 DBTL handoff 中结合团队确认的方案、可行性、成本和资源确定。

## 不可越过的边界

1. docking 的 Vina/SwissDock `ΔG` 只能定义候选情景和相对排序，**不得**转换成 `Kd`、`kon`、`koff`、`EC50`、`K_R` 或 `E_R`。
2. Shaw、Kofahl、Yi 的现有 SBML/文献指针可支持模块结构；未完成 source-table、单位和 kinetic-law 映射的速率数值仍是 `do-not-use`。
3. Fan 2024 的 CaSte2/GAL source-context 拟合行可支持方法和输出层先验，**不得**直接填为 Gpr-ascr 的 `K_R`、`K_out`、Hill、gain 或 `Emax`。
4. 项目校准证据进入配置时，须记录构建、条件、输入单位、观测定义、拟合方法、数据文件和替换日期；只有可追溯证据才能把字段升为 calibrated。具体采集方案由后续 DBTL handoff 确认。

## 相关权威材料

- 方程执行行为：[最小求解器](../../src/modeling/ode/minimal_solver.py)；Phase 0 输入数值：[最小情景配置](../../experiments/ode-model/configs/minimal_normalized_scenario.json)；Phase 1 网格：[扫描 suite](../../experiments/ode-model/configs/stage1_scenario_scan.json)。
- Phase 1 当前结果、复跑方式和外部 payload 边界：[结果包 README](../../experiments/ode-model/results/stage1_scenario_scan/README.md)。
- 文献 exact pointers、扫参边界和证据状态：[P0 信号通路 ODE](P0-signal-pathway-ode.md)。
- 通路范围、当前进度和更宽的参数状态：[P0 信号通路 ODE](P0-signal-pathway-ode.md)。
- 单拷贝基线：[决策 003](../decisions/003-chassis-yeast-ste2-integration.md)；reporter 拓扑：[决策 004](../decisions/004-reporter-output-architecture.md)。
