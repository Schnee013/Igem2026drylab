---
artifact: P0-ode-phase2a-analysis-contract
status: active-contract
priority: P0
last_updated: 2026-07-29
source_base_commit: 36599402fd091f616520e9b7415d3b30aefd5781
---

# P0 ODE Phase 2A：敏感性与实验接口分析合同

## 当前交付

Phase 2A 固定 Phase 2 的分析对象、参数空间、输出指标、实验接口和进入门槛。
本合同基于团队 `main@36599402fd091f616520e9b7415d3b30aefd5781` 的归一化 Phase 0/1 实现，支持后续局部敏感性、
Morris screening、重点参数交互分析和 calibration-readiness 审计。

当前证据等级为 `scenario_prior`。本合同给出的范围是可复现的筛选范围；项目参数
升级为 calibrated 需要同一底盘、构建、ligand、读出和时间设计下的可追溯数据。

## 权威来源与更新条件

| 内容 | 当前来源 |
|---|---|
| 方程执行行为 | [`minimal_solver.py`](../../src/modeling/ode/minimal_solver.py) |
| 18 个参数、当前值和证据状态 | [`P0-ode-lumped-parameter-register.md`](P0-ode-lumped-parameter-register.md) |
| Phase 0 基线值 | [`minimal_normalized_scenario.json`](../../experiments/ode-model/configs/minimal_normalized_scenario.json) |
| 已接受的 Phase 1 工程范围 | [`stage1_scenario_scan.json`](../../experiments/ode-model/configs/stage1_scenario_scan.json) |
| Phase 2A 机器合同 | [`phase2a_analysis_contract.json`](../../experiments/ode-model/configs/phase2a_analysis_contract.json) |

以下任一变化会触发本合同复核：

- solver 方程、字段或验证约束改变；
- 基线配置或参数登记改变；
- 项目实验提供有单位的 dose-response、time-course 或模块读出；
- reporter 构建、实际 copy number 或显色方案被锁定；
- 参数筛选显示当前范围无法覆盖响应转折区。

## 基线模型

Phase 2A 使用当前三状态集总模型 `M0`：

```text
R_active = b_R + E_R * Hill(L; K_R, n_R)

dG/dt = k_couple * R_active * (1 - G) - k_deact * G

dM/dt = k_mapk_on * G * (1 - M) - k_mapk_off * M

TF = b_TF + E_TF * Hill(M; K_TF, n_TF)

Prod = leak_out + N * gain_out * TF / (K_out + TF)

dC/dt = k_color_prod * Prod - k_color_loss * C
```

`G`、`M`、`C` 是动态状态；`R_active`、`TF`、`Prod` 是代数接口。动态 sTF
候选模型 `M1` 使用

```text
dS/dt = (TF_infinity(M) - S) / tau_sTF
```

作为最小扩展定义。`M1` 的启用门槛是：`M0` 的筛选结果显示 sTF 模块对目标输出
具有高影响，且计划中的早期 time-course 与中间读出能区分 sTF 延迟和色素动力学。

## 参数空间设计

参数空间见
[`phase2a_parameter_space.csv`](../../experiments/ode-model/configs/phase2a_parameter_space.csv)。

设计规则：

1. 18 个内部字段全部登记；外部 ligand、观察时长和输出点数作为实验上下文。
2. `copy_number` 是离散工程设计变量。Phase 2B 在 `N=1/2/4` 条件下分层运行，
   不把 copy number 连续化。
3. Phase 1 已接受的范围直接沿用：
   - `K_R = 0.01–100`；
   - `k_couple = 0.05–1.2 h^-1`；
   - `leak_out = 0–0.08`；
   - `gain_out = 0.1–1.0`；
   - `N = 1/2/4`。
4. 领域文档已给出的 Hill 范围使用 `0.5–3`。
5. 其余正速率和半响应参数先使用相对基线 `0.1×–10×` 的 log-uniform
   诊断范围；这些行标记为 `provisional_diagnostic_multiplier`。
6. 归一化 basal/efficacy 使用有界 uniform 范围，并保证
   `b_R + E_R <= 1`、`b_TF + E_TF <= 1`。

Phase 2B 报告必须同时保存具体范围版本和基线提交，敏感性排序只在对应范围合同内
成立。

## 分析上下文

第一轮筛选使用三种输入上下文：

| context | `ligand_normalized` | 用途 |
|---|---:|---|
| `no_ligand` | 0 | 背景与假阳性风险 |
| `transition_reference` | 1 | 当前归一化半响应附近 |
| `high_input` | 1000 | 高输入/接近饱和的压力情景 |

每个输入上下文在 `N=1/2/4` 三个 copy strata 下运行。正输入情景同时生成
逐参数匹配的 no-ligand control，唯一改变字段为 `input.ligand_normalized=0`。
时间网格沿用 0–8 h、161 点，保证 2 h、4 h 和 8 h 输出可直接比较。

## 输出指标

输出定义见
[`phase2a_output_metrics.csv`](../../experiments/ode-model/configs/phase2a_output_metrics.csv)。

第一轮主要指标：

- 2/4/8 h color；
- 0–8 h color AUC；
- 8 h matched-control background；
- 8 h ligand-control delta；
- 8 h ligand/control ratio；
- `time_to_half_final_color`。

模块诊断指标在 1 h 读取 `G`、`M`、`TF` 和 `Prod`，用于定位敏感性在哪一层
产生。`time_to_readout_threshold` 已登记为校准接口；它需要湿实验读出阈值、
噪声模型和判读规则后才能启用。

## 参数—观测量—实验接口

逐参数接口见
[`phase2a_experiment_matrix.csv`](../../experiments/ode-model/configs/phase2a_experiment_matrix.csv)。

四类最小实验模块为：

| 模块 | 主要观测 | 主要约束参数 |
|---|---|---|
| receptor dose-response | matched reporter、OD/growth、无 ligand 与多剂量 | `b_R`, `E_R`, `K_R`, `n_R` |
| coupling/MAPK time-course | chimeric Gpa1 功能偶联、早期 MAPK proxy、step-on/off | `k_couple`, `k_deact`, `k_mapk_on`, `k_mapk_off` |
| sTF/GAL transfer assay | 受控上游激活、中间 reporter、copy-confirmed 构建 | `b_TF`, `E_TF`, `K_TF`, `n_TF`, `N`, `leak_out`, `gain_out`, `K_out` |
| color production/shutoff | constitutive/controlled production、显色 time-course、OD | `k_color_prod`, `k_color_loss` |

仅有最终颜色时，`N × gain_out`、`gain_out × k_color_prod`、上游 basal 与
`leak_out`、sTF 延迟与色素动力学会形成参数组合。Phase 2C 的实验设计审计需要
逐步加入 early pathway、sTF/GAL 和 color readout，检查每一类数据能拆开哪些组合。

## Phase 2B 执行顺序

进入 Phase 2B 前，先完成本阶段的固定复核流程：

1. 团队仓库以可追溯 commit 固定可执行模型、配置、测试和分析合同；
2. personal learning workspace 保存带来源 commit 和 checksum 的只读快照；
3. 对参数空间、输出、实验矩阵、假设和模型升级条件完成个人理解与复现；
4. 形成区分“合同事实、个人解释、未决问题、建议变更”的理解报告；
5. 仅把团队复核接受的结论写回本仓库的合同、决策记录或实施计划；
6. 理解报告已复核、涉及合同的未决变更已处理后，才进入 Phase 2B。

团队仓库中的冻结合同保持项目权威；personal workspace 用于独立理解和复现，
不在未评审的情况下改变团队合同。

通过上述门槛后，Phase 2B 按以下顺序执行：

1. 对 17 个连续不确定字段运行局部归一化敏感性，检查方向、数值稳定性和
   time-dependent sensitivity。
2. 在三个 ligand context 和三个 copy strata 下运行 Morris screening。
3. 根据 `mu_star`、`sigma`、不同输出和不同时间的一致性选择重点参数。
4. 为高影响交互补少量二维图；优先候选为：
   - `K_TF × n_TF`；
   - `b_R × leak_out`；
   - `k_mapk_off × k_color_loss`。
5. 全局方差分解的进入门槛是重点参数集合、范围和独立性假设完成复核。

## Phase 2A 完成门槛

- 18 个内部参数与当前基线配置逐项一致；
- 17 个连续字段和 1 个离散设计变量分类明确；
- 每个参数都有观测量、最小实验、关键对照和替换条件；
- 输出指标具有唯一 ID、计算定义和启用状态；
- 机器合同中的路径、数量和来源提交通过自动测试；
- 项目 INDEX、ODE 领域文档和当日日志指向本合同。

验证命令：

```bash
python -m unittest tests.modeling.test_ode_phase2a_contract -v
```
