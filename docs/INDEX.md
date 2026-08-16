# iGEM DryLab 干实验 — 项目索引

> 最后校准：项目全表 2026-07-31；ODE 条目 2026-08-16。本文是项目路由表；详细结果数值沿链接回到领域文档、日志和原始结果文件。
>
> Source: system-local `PACKAGE_STATUS.md`、直接 gate/run artifacts、领域权威文件。
>
> As of: 项目全表 `2026-07-31`，ODE 条目 `2026-08-16`；运行状态使用其条目内的独立核验时间，超过新鲜度边界后不继续视为当前状态。
>
> Allowed use: 项目级状态投影、优先级、阻塞项和活跃入口。
>
> Update trigger: 上游事实改变项目级状态、优先级、阻塞项或活跃入口。

## 项目概述

- **一句话**: 构建基于 GPCR 生物传感器的植物寄生线虫田间早期检测系统的干实验（计算建模）模块
- **当前阶段**: 底盘已锁定酵母-STE2；docking-repro 旧 Gpr2/Gpr3 ratio、IFP、排名和湿实验交付已因 AF3 mutant frame 缺陷撤回。seed 42 + 43 WT evidence 已用于冻结 `docking-geometry-gate-v3`；随后 seed-44 独立 8-job holdout 的 docking、IFP 和 geometry 全部技术完成，但 `Gpr3/R167Y` 两臂未通过冻结门，当前状态为 `geometry_gate_v3_seed44_holdout_fail_stop_full_blocked`。不存在 active shortlist 或 wetlab handoff。既有 R59C/R167Y MD 仅支持各自旧起始 pose 的单重复探索性描述，不能验证修复后的候选排名。其他 MD/ODE/底盘方向状态沿各自权威入口读取。
- **主要卡点**: seed-44 run `4496efeedc527d870fff06c5e61b49ef811b0c27045b739846e4471a97c0af69` 已形成 `TERMINAL_ABNORMAL / fail_stop_before_full`：Gpr3/R167Y-ascr18 为 14/16，R167Y-ascr3 为 11/18 且 MODEL 1 失败。冻结门不得按 holdout 结果放宽；328-job full-run 未启动。任何改门、新 holdout 或绕过门进入剩余 320 jobs 都是新的决策与授权。方法与证据见[重校准决策包](../codex/docs/plans/docking-geometry-gate-recalibration-decision-20260730.md)和[2026-07-31 日志](logs/2026-07-31.md)。MD、reporter 和 HP 的其他卡点沿对应方向文档读取。
- **目标**: iGEM Wiki freeze 约 2026-09 底
- **详细背景**: [项目全貌 v4](prd/overview-v4.md)

---

## 建模方向状态

| 优先级 | 方向 | 底盘相关 | 当前状态 | 文档 |
|--------|------|---------|----------|------|
| **P0** | 受体-配体分子对接 | 否 | **geometry_gate_v3_seed44_holdout_fail_stop_full_blocked**：新门已从 seed 42 + 43 WT evidence 冻结；seed-44 独立 holdout 8/8 技术完成，但 Gpr3/R167Y 两臂 geometry 失败，终态阻止 full-run | [P0-molecular-docking.md](modeling/P0-molecular-docking.md) |
| **P0（探索）** | 双/多突变 docking | 否 | **phase2_local_schema_test_ready_blocked_by_frame_repair（2026-07-30）**：canonical genotype、multi-mutation FASTA、旧单突变只读兼容、WT/A/B/AB validator 和 synthetic focused tests 已完成；仍须等共同 frame 修复、单突变全量重跑和 active shortlist 重建后才能冻结真实 AB，当前未生成双突变结构或启动计算 | [multi-mutant-docking/README.md](modeling/multi-mutant-docking/README.md) |
| **P0** | MD 模拟（突变体稳定性 + 嵌合 Gpa1 验证） | 否/酵母触发 | **compute_triage + gpr2_wt_r59c_rep1_analyzed + gpr3_r167y_rep1_analyzed**：旧 Slurm control/chctrl 3 reps 为历史完成证据，E2 有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据；R1 Z-only 已降级为省算力不足；chimeric 候选 full MD 暂停；Gpr2 WT/R59C 200 ns rep1、七 driver、matched single-rep 和 ligand-path triage 已完成；Gpr3 R167Y AutoDL 200 ns rep1、postprocess 和共享七 driver 已完成，当前为 single-rep exploratory，WT arm 尚无 production completion | [P0-md-simulation.md](modeling/P0-md-simulation.md) |
| **P0** | 信号通路 ODE 建模（酵母 STE2） | 已锁定酵母 | **phase2b_runners_verified_result_package_pending**：Phase 0/1 可执行原型、Phase 2A 分析合同及 Phase 2B 局部敏感性、Morris、Sobol、重点曲面 runner/config/test 已验证；完整长运行结果尚缺仓库内紧凑结果包与恢复指针，候选冻结和项目校准仍待证据接纳 | [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) |
| **P0** | 嵌合 Gpa1 同源性建模 | 酵母触发 | **MD_validation_paused_compute_triage**：42 个 AF3 jobs + Top 3 选择完成；AoGpa2 序列核查通过；旧 Slurm control/chctrl 组 3 reps 完成，E2 有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据；候选迁移规则仍需非 Z-only 的 source-backed 物理依据，候选体系验证暂停 | [P3-chimeric-gprotein.md](modeling/P3-chimeric-gprotein.md) |
| **P1** | 土壤 ascaroside 扩散模型 | 否 | not_started | [P1-soil-diffusion.md](modeling/P1-soil-diffusion.md) |
| **P1** | 标志物→线虫丰度贝叶斯推断 | 否 | not_started | [P1-bayesian-inference.md](modeling/P1-bayesian-inference.md) |
| **P2** | 早期检测经济效益模型 | 否 | **framework_mvp_validated_arithmetic + stage3_benchmarks_extracted**：deterministic cost-accounting MVP 已落地并验证公开示例算术；最终 ROI 仍待 HP/湿实验/本地参数校准 | [P2-economic-benefit.md](modeling/P2-economic-benefit.md) |
| **P2** | 化学杀线虫剂剂量-响应 | 否 | not_started | [P2-dose-response.md](modeling/P2-dose-response.md) |
| ~~P2~~ | ~~生物防治 Lotka-Volterra~~ | 仅丝状真菌 | **archived** | [P2-biocontrol-lv.md](modeling/P2-biocontrol-lv.md) |

---

## 阻塞性待确认事项

> 2026-04-11 底盘 4 项阻塞全部解除（PI 确认酵母-STE2 主线，详见 [决策 003](decisions/003-chassis-yeast-ste2-integration.md)）。

- [ ] **[门禁] MD 算力收缩与排程**：按 [决策 005](decisions/005-md-compute-triage-after-chctrl.md)，chimeric 候选体系 full-production 暂停；先调研减少体系大小或更强 restraint 的省算力 protocol。E2 是共享服务器，后续 MD 必须先做资源估算/短程 benchmark，不得长期独占 A100。
- [ ] **[门禁] mutant GPR MD 前测**：`Gpr2_WT + ASCR18` 与 `Gpr2_R59C + ASCR18` 的 200 ns rep1、共享七 driver、WT/R59C matched single-rep comparison 和 ligand-path triage 已完成；当前只支持 matched single-rep exploratory/triage，不使用 alpha5 的 3/5 A operational band 对 ligand pose 分级，也没有预注册 ligand RMSD cutoff。两臂起始 receptor/pose 不同，复制和 same-starting-system 控制仍是 genotype inference 前置条件；既有结果仅描述旧起始 pose，不能验证 repaired ranking。Gpr3 WT/R167Y + ASCR3 双臂已通过本地 runnable-input gate；R167Y arm 的 200 ns rep1、completion finalization、postprocess 和共享七 driver 已完成，当前只支持 single-rep exploratory 描述。WT arm 尚无运行完成证据；未来最佳突变和新 MD 输入必须等待 frame-repaired 全量候选。
- [ ] **[质量门] 预注册 operational cutoff 来源审查**：所有用于 go/no-go 的项目预注册阈值、技术栈选择、几何定义和数值判据必须补齐 DOI / 标题 / 原文方法段落 / 官方工具文档等 exact pointer；没有 exact pointer 的文献引用暂不承认，统一标记为待查验或项目 operational heuristic。
- [ ] **[门禁] docking frame 纠错与候选重建**：旧 shortlist 已撤回。maximum-20、显式 CPU8、WT calibration、MODEL 1 目视和新门冻结均已完成；seed-44 独立 holdout 8/8 技术完成但 Gpr3/R167Y 两臂未通过冻结门，已 `fail_stop_before_full`。不得按 holdout 结果调低门；当前不存在可发送的 docking 湿实验候选。
- [ ] **[待确认] reporter 输出实现参数**：架构已确认（sTF -> GAL 多拷贝放大 -> 色素显色），但具体色素、整合位点、实际拷贝数、输出增益和 time-course 参数仍需通路工程组/湿实验校准。
- [ ] **[证据门] ODE Phase 2B 结果接纳**：runner、配置、测试和设计预检已具备；候选冻结需要仓库内紧凑结果包绑定完整局部敏感性、Morris、Sobol、重点曲面的来源哈希、输出校验和、生成命令、软件身份和恢复入口。
- [ ] **[重要] HP 组沟通**: 回收经济模型的本地参数：传感器单次成本、部署密度、检测性能、当地 lab 成本/周期、施药/轮作/抗性品种成本、作物价格与农户支付意愿。

---

## 当前优先入口

1. **MD 算力收缩与 mutant GPR 前测** — 决策见 [决策 005](decisions/005-md-compute-triage-after-chctrl.md)；Gpr2 R59C completion/recovery 入口为 `experiments/md-simulation/results/gpr2-r59c-ascr18/README.md`、`experiments/md-simulation/systems/gpr2-R59C-ascr18/PACKAGE_STATUS.md` 和 [2026-07-19 日志](logs/2026-07-19.md)，分析分别见 `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_r59c_ascr18_rep1_chctrl_metric_analysis_20260719.md`、`experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md` 与 `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md`。Gpr3 R167Y completion、恢复与七 driver 当前入口是 `experiments/md-simulation/results/gpr3-r167y-ascr3/README.md` 和 `experiments/md-simulation/results/gpr3-r167y-ascr3/analysis/gpr3_r167y_ascr3_rep1_chctrl_metric_analysis_20260720.md`；详细 package 视图回 system-local `PACKAGE_STATUS.md`，方法边界见 [P0-md-simulation.md](modeling/P0-md-simulation.md)。
2. **chimeric Gpa1 省算力方案调研** — 候选体系 production 仍暂停；R1-Z 对照与路线选择历史见 `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md` 和 `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`。R4 的唯一当前材料边界见 `experiments/chimeric-gpa1/literature/r4_material_decision_addendum_20260706.md`；`experiments/chimeric-gpa1/literature/r4_tool_validation_plan_20260706.md` 作为非执行 validation-design evidence。任何 full-production 启动都需要新的当前 work order 和审批。
3. **docking-repro frame repair** — 当前状态和方法边界见 [P0 molecular docking](modeling/P0-molecular-docking.md) 与 [docking-repro directory contract](../experiments/docking-repro/README.md)。新门已冻结；seed-44 独立 holdout 归档在 `temp/docking_frame_repair_20260731_e2_full_seed44_r1/`，终态为 `TERMINAL_ABNORMAL / fail_stop_before_full`。下一步是对失败门保持现状，或另行决定新的 geometry 策略与独立验证；当前不得启动剩余 320 jobs。旧 shortlist/ratio/IFP 只保留为带日期的撤回历史证据。
4. **双/多突变 docking（Phase 2 local ready / blocked）** — 方向、证据边界和核心文献见 [multi-mutant-docking/README.md](modeling/multi-mutant-docking/README.md)，执行合同见 [multi-mutant-docking-execution-plan-20260730.md](../codex/docs/plans/multi-mutant-docking-execution-plan-20260730.md)，本地 schema/test 入口见 [multi-mutant local contract](../experiments/docking-repro/multi-mutant/README.md)。当前不从旧 ratio/IFP 组合候选；只有 frame repair 和 repaired single-mutant shortlist 完成后，才冻结少量真实 WT/A/B/AB 周期。
5. **ODE 并行推进** — 可执行入口为 `src/modeling/ode/` 与 `experiments/ode-model/`，分析合同入口为 `experiments/ode-model/configs/phase2a_analysis_contract.json`；参数证据/边界回 [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) 和 [lumped 参数登记表](modeling/P0-ode-lumped-parameter-register.md)。当前只支持归一化 `scenario_prior`；下一门槛是补齐并审查 Phase 2B 紧凑结果包，Kd/calibration、可识别性、拟合和不确定性传播仍未完成。
6. **早期检测经济效益模型 HP 参数回收** — 文献/参数入口见 [early-detection economic-benefit dossier](papers/p2-economic-benefit/README.md)，问卷见 [P2-economic-benefit-hp-questionnaire.md](modeling/P2-economic-benefit-hp-questionnaire.md)；当前只能做公开示例和 break-even 结构。
7. **湿实验/reporter 输出参数讨论** — 需要结合 [overview-v4.md](prd/overview-v4.md)、[决策 003](decisions/003-chassis-yeast-ste2-integration.md)、[决策 004](decisions/004-reporter-output-architecture.md) 与 ODE 需求。

---

## 策略文档

| 文档 | 内容 | 链接 |
|------|------|------|
| 项目全貌 v4 | 锁定酵母-STE2 后的核心信号链路、团队、受体、文献 | [overview-v4.md](prd/overview-v4.md) |
| 干实验总策略 | §2 方向评估、痛点调研、防治决策 | [dry-lab-strategy.md](prd/dry-lab-strategy.md) |
| 底盘决策（已定） | §最终决策：策略 B 酵母-STE2-基因组整合 | [chassis-decision.md](prd/chassis-decision.md) |
| 决策 003 | 底盘选择技术决策记录 | [003-chassis-yeast-ste2-integration.md](decisions/003-chassis-yeast-ste2-integration.md) |
| 学习路线图 | §4+§6 学习资源、硬件、工具 | [roadmap.md](learning/roadmap.md) |

## Docking 候选清单

> 当前不存在 active docking shortlist。2026-05-20 ratio/IFP/shortlist 只保留为已撤回历史证据；新的候选权威必须等待共同 frame、smoke、328-job 全量矩阵和候选审计全部通过后建立。

| 文档 | 内容 | 链接 |
|------|------|------|
| P0 docking MD 前候选体系清单（已撤回） | 旧 Top 候选、ratio/IFP 和 MD 输入身份的历史边界；不得作为当前候选来源 | [已撤回的 MD 前候选体系清单](modeling/P0-docking-md-candidate-shortlist.md) |
| 双/多突变 docking 方向（plan-only / blocked） | frame repair 前置、受限组合、WT/A/B/AB、双配体负向设计、文献和执行入口 | [multi-mutant-docking/README.md](modeling/multi-mutant-docking/README.md) |

## 运维参考

- **GROMACS / MD 必读前置**：[md-gromacs-operational-pitfalls.md](ops/md-gromacs-operational-pitfalls.md)（服务器中立；任何 MD/GROMACS 任务先读）
- **当前服务器入口**：完成上述必读后，新服务器/远程计算任务再读 [NKULiulab E2 共享云服务器](ops/nkuliulab-e2-cloud-server.md)。2026-06-26 后 chimeric 候选 full-production 暂停，旧 Slurm secondary route 只保留为历史/未来备选指针；任何新的 MD production 都必须先做资源估算和短程 benchmark。
- **[已归档] Slurm GPU 集群**：[slurm-md-server.md](ops/archives/slurm-md-server.md)（仅用于追溯旧 MD/Slurm 运行记录；2026-05-30 chimeric secondary route 已于 2026-06-26 降级为历史/未来备选指针，相关脚本和 gate 见 `environments/md-production-sites.md` 和 `experiments/md-simulation/scripts/slurm_*`）
- **2026-07-28**: 从 `BASE_SHA=e6a8be4` 聚焦重建 ODE Phase 0/1 可执行原型并通过 11 个单元/合同测试、编译和 snapshot-only replay；固定网格为 143 scenarios（74 ligand + 69 controls）和 23,023 条完整 time-course data rows。所有输出仍为 `scenario_prior`；完整 time-course 按 payload policy 外置并由 checksum manifest 路由。实现、结果边界与验证证据见 [ODE 领域文档](modeling/P0-signal-pathway-ode.md)、[结果 README](../experiments/ode-model/README.md) 和 [2026-07-28 日志](logs/2026-07-28.md)。
- **[已归档] Sunlab 历史文件查询服务器**：[sunlab-historical-server.md](ops/archives/sunlab-historical-server.md)（`10.40.4.2`，本机 alias `drylab-10-40-4-2`；用途限定为历史文件查询，当前活跃计算入口使用 E2 规范）
- **[已归档] HBU SGE 集群**：[hbu-sge-cluster.md](ops/archives/hbu-sge-cluster.md)（仅用于追溯旧 HBU SGE 调研/投递记录）
- **[已弃用] Windows SSH 操作指南**：[ssh-windows-compute.md](ops/archives/ssh-windows-compute.md)（Windows 7500F 节点停用；部分 docking 结构文件仍存于该节点，需访问时参考此文档）

## 文献

> **读取策略**: 需要某篇文献时，先查矩阵确认编号，再按编号读取对应的 `summaries/` 文件；PDF 读取需有具体文献需求。

- **文献调研入口**: [文献矩阵](papers/literature-matrix.md)（当前本地记录：58 篇 PDF / 59 篇已总结，详见矩阵头部）
- **早期检测经济效益模型文献/数据源包**: [early-detection economic-benefit](papers/p2-economic-benefit/README.md)（Stage 1/2 paper/data matrix、参数表、source evidence；Stage 3 external benchmark extraction）
- **组员使用说明**: [papers/README.md](papers/README.md)
- 完整已总结清单由 `papers/literature-matrix.md` 维护；INDEX 只保留文献路由入口。

## 归档

| 文件 | 说明 | 位置 |
|------|------|------|
| PRD v3 原始文件 | 已拆分到 prd/ 各子文档 | [archive/iGEM_DryLab_PRD_v3.md](archive/iGEM_DryLab_PRD_v3.md) |
| Claude Code Skill 指南 | 项目管理参考 | [archive/claude-code-skill-guide.md](archive/claude-code-skill-guide.md) |

---

## 最近进展

- **2026-08-04**: ODE Phase 2A 已固定 18 字段参数空间、主/诊断 ligand contexts、输出指标和参数—实验替换接口；ratio 对零/近零 denominator 输出 NaN + validity/reason，正 ligand 缺失 matched control 时 fail closed。20/20 ODE tests 通过；当前仍无灵敏度排序或校准结论。证据见 [ODE 领域文档](modeling/P0-signal-pathway-ode.md) 与 `experiments/ode-model/configs/phase2a_analysis_contract.json`。
- **2026-07-31**: seed 42 + 43 WT evidence 已冻结 `docking-geometry-gate-v3`；随后 seed-44 独立 holdout 8/8 docking、IFP 和 geometry 技术完成。Gpr2 四项与 Gpr3 WT 两项通过；Gpr3 R167Y-ascr18 为 14/16，R167Y-ascr3 为 11/18 且 MODEL 1 失败。终态 `TERMINAL_ABNORMAL / fail_stop_before_full`，未创建 full plan或启动剩余 320 jobs；1,089/1,089 远端与本地 checksum 通过。证据见 [2026-07-31 日志](logs/2026-07-31.md)。
- **2026-07-30**: R1 8-job E2 smoke 已完成：8/8 docking 与 IFP 技术完成，两个 R167Y job 的 18/20 poses 被正确接受；geometry 仅 3/8 job 通过，五项分布结果为 Gpr2 WT–ascr#18 17/19、WT–ascr#3 17/18、R59C–ascr#18 18/19、Gpr3 R167Y–ascr#18 12/15、R167Y–ascr#3 9/15，后者 MODEL 1 也低于高度门。终态为 `TERMINAL_ABNORMAL` / `fail_stop_before_full`，未建立 full plan 或启动剩余 320 jobs；608 个远端文件已逐项哈希一致归档到 `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/`。证据见 [2026-07-30 日志](logs/2026-07-30.md)。
- **2026-07-30**: 完成 18/20 成因审计：Vina v1.2.6 将 `num_modes` 定义为最大输出数，RMSD 去重后合法返回少于 20；三次 18-mode 输出均正常结束，能量跨度 1.118/1.192 kcal/mol，排除 `energy_range=3.0` 截断。R167Y-ascr18 在 v3/v4 三次 pose SHA256 相同，原合同重试无恢复价值。另确认 v4 全部命令遗漏 `--cpu 8`，CPU 未进入 plan/environment/job identity，因此 v4 不能作为 production smoke。已形成待批准的 [R1 恢复合同](../codex/docs/plans/docking-frame-repair-18mode-recovery-contract-20260730.md)；未改代码、未新跑 E2。
- **2026-07-30**: 获批的 E2 9-attempt recovery smoke 已覆盖冻结的 8 个唯一 job：6 jobs 技术完成且各有 20 poses；Gpr3 R167Y–ascr#18 初次与原合同重试均为 18/20，R167Y–ascr#3 初次为 18/20，形成 6 completed / 2 technical failure / 0 unattempted unique jobs 的 `TERMINAL_ABNORMAL`。未运行 IFP/geometry，未建立 full plan 或启动剩余 320 jobs。远端 573 文件已逐项哈希一致地归档到 `temp/docking_frame_repair_20260730_e2_smoke_9attempt_v4/`。证据见 [2026-07-30 日志](logs/2026-07-30.md)。
- **2026-07-30**: 双/多突变 Phase 2 本地合同已完成：canonical structured mutations/genotype ID、identity-checked FASTA、旧单突变只读兼容、完整 WT/A/B/AB cycle/matched-result validator 和 14 项 synthetic focused tests 已落地；未生成真实 candidate cycle，也未解除 frame/toolchain/smoke 门。证据见 [2026-07-30 日志](logs/2026-07-30.md) 和 [multi-mutant local contract](../experiments/docking-repro/multi-mutant/README.md)。
- **2026-07-27**: 从 checksum 识别的外部 processed inputs 重算并恢复 `Gpr2_R59C + ASCR18` 七 driver、WT/R59C matched single-rep 和 ligand-path canonical evidence；Git 跟踪的 55 行 final manifest 与外部版本字节一致，本机现存 25 项全部 checksum 匹配，其余 30 项仍为 E2-only。当前证据只支持 matched single-rep exploratory/triage；两臂起始 receptor/pose 不同、无预注册 ligand RMSD cutoff，不能形成 population-level genotype conclusion 或“最佳突变”结论。入口见 `experiments/md-simulation/results/gpr2-r59c-ascr18/README.md` 和 [2026-07-19 日志](logs/2026-07-19.md)。
- **2026-07-20**: `Gpr3_R167Y + ASCR3` AutoDL 200 ns rep1 正常完成，completion gate 确认 100,000,000 step / 200,000 ps、同终点 CPT、空 issue scan 与 `TERMINAL_NORMAL`；91-row production archive 回收到仓库外 payload 后 `91/91 PASS`。同环境 GROMACS 2025.4 postprocess 与共享七 driver 均完成，45 项 canonical 检查和 55-file analysis manifest 全部 PASS。当前证据等级为 single-rep exploratory only；结果和恢复入口见 `experiments/md-simulation/results/gpr3-r167y-ascr3/README.md`，详细经过见 [2026-07-20 日志](logs/2026-07-20.md)。
- **2026-07-20**: 修复 `Gpr3_R167Y + ASCR3` attempt3 临时 runtime wrapper 只采 GPU、未写周期正式事件的缺口。新增 source-first heartbeat/supervisor，未来 gate 生成的 launch/resume 命令自动经过 runner；当时 active PID 11020 通过 versioned staging 和独立 tmux 非侵入补挂。60 秒验证窗口连续写入三条 `RUNNING_VERIFIED` 并持续前进，最终周期为 30 分钟、失败重试 5 分钟；production PID/启动标识未改变。证据见 [2026-07-20 日志](logs/2026-07-20.md) 和 periodic-heartbeat package。
- **2026-07-20**: `Gpr3_WT + ASCR3` E2 首次 live resource preflight 确认 Gpr2 production/postprocess 已结束、计划 run root 尚不存在，但 A100 正由两个其他用户的 Python compute jobs 占用；按共享服务器门禁停止，未创建远端目录、未上传输入、未运行 preproduction/benchmark/production。当前终态为 `BLOCKED_E2_GPU_BUSY`，下一门是外部 GPU jobs 结束后的 fresh resource preflight。证据见 [2026-07-20 日志](logs/2026-07-20.md) 和 blocker package。
- **2026-07-19**: 完成 Gpr2 WT/R59C rep1 的 ASCR18 ligand-path 与 `4 A` contact-occupancy 结构复核。两臂起始接触区不同，不能作为同一口袋只改 residue 59 的因果比较；R59C 动态接触区集中在 `ILE122/ILE126/THR133/GLN134/PHE137`，其中 `ILE122` 是 docking/MD 第一交叉验证候选，residue 59 未形成直接接触。最佳突变仍需同起始体系、双配体、多重复与功能实验。证据见 [2026-07-19 日志](logs/2026-07-19.md) 和 ligand-path report。
- **2026-07-19**: `Gpr2_R59C + ASCR18` 200 ns rep1 已由 GROMACS 正常结束标记、XTC/EDR 200,000 ps 终点和空 issue scan 确认物理完成；completed-run finalizer 将 production status 提升为 `finished`，production/final archive 分别通过 `43/43` 与 `55/55` 校验。E2 GROMACS 2025.4 后处理、共享七 driver 和 WT/R59C matched single-rep comparison 全部完成。两条轨迹均有显著 receptor global motion；共同排除并重拟合 250–310 后，R59C 的剩余 backbone RMSD 和 ASCR18 displacement 高于 WT。该结果用于 single-rep exploratory/triage。证据见 [2026-07-19 日志](logs/2026-07-19.md)、system-local `PACKAGE_STATUS.md` 和 matched report。
- **2026-07-19**: `Gpr3_R167Y + ASCR3` AutoDL clone 的历史 input-promotion HOLD 已由 versioned 42-row manifest 和 additive promotion 解除；accepted attempt3 通过 geometry repair、标准 EM、step6.1-step6.6、100 ps benchmark 与 checkpoint-resume。production launch gate 为 `GO`，200 ns rep1 已启动并通过 early-runtime CPT/XTC/EDR、输出增长、GPU、issue-scan 和 provenance gate；当时状态是 `RUNNING_EARLY_GATE_PASS`，不是 200 ns completion。证据见 [2026-07-19 日志](logs/2026-07-19.md) 与 `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260719_autodl_clone_attempt3_running_early_gate_pass/README.md`。
- **2026-07-17**: Gpr3 主比较改为 WT-oriented matched backbone：从已 PPM 定向的 Gpr3 WT receptor 构建 R167Y，保持 1,604 个 `N/CA/C/O` backbone 原子逐原子一致，仅对 5 A 邻域侧链做 CHARMM36m 局部 EM。CHARMM-GUI job `8426884163` 的 matched R167Y receptor-membrane return 已归档并完成 intake audit；WT 复用 job `7628627163` 的 receptor-only base。随后唯一追溯 docking receptor，完成 988-atom transform、共享 46-atom ASCR3、双臂 clash/POPC review、post-genion topology/index/input contracts 和独立零-warning `grompp`；本地 runnable-input gate 双臂 PASS。证据见 [2026-07-17 日志](logs/2026-07-17.md)、system-local `PACKAGE_STATUS.md` 与 `experiments/md-simulation/results/gpr3-matched-ascr3/gates/20260717_runnable_input_attempt2/README.md`。
- **2026-07-16**: `Gpr3R167YASCR3_ppm2_input.pdb` 已提交 PPM 2.0（job key `20260716_092235699_8004174`）；远端 raw output 复核下载与本地归档 byte-identical，DUM-free clean body 与当日 upload contract byte-identical。该 versioned rerun解除独立 AF3 receptor 的 checksum-provenance HOLD；2026-07-17 matched-backbone 决策后，这条链只保留为 starting-structure sensitivity，不再是 primary upload。证据见 [2026-07-16 日志](logs/2026-07-16.md)、[2026-07-17 日志](logs/2026-07-17.md) 和 versioned PPM status。
- **2026-07-16**: `Gpr2_R59C + ASCR18` 已从 receptor-only CHARMM-GUI base 完成 receptor-frame ligand insertion、clash/topology/index gate、EM、step6.1-step6.6 和 100 ps benchmark（130,638 atoms；93.135 ns/day），并于 `15:48:19+08:00` 启动 200 ns rep1。首个 checkpoint 于 `16:18:26+08:00` 写出，GROMACS dump 可解析为 step `894200` / `1788.4 ps`；这是日期限定的 launch/checkpoint 快照，当前状态回 system-local `PACKAGE_STATUS.md`。证据见 [2026-07-16 日志](logs/2026-07-16.md)。
- **2026-07-15**: 以当前 `Gpr2R59CASCR18_ppm2_input.pdb` 重跑 PPM 2.0（job key `20260715_121304156_5202956`），远端 raw output 与复核下载 SHA256 一致；DUM-free clean body 已更新为 CHARMM-GUI upload contract。该版本化链解除 Gpr2 的 checksum-provenance HOLD，但当日尚未 runnable：仍待 CHARMM-GUI 登录、returned output、ASCR18 insertion、topology/index/warning gate。后续 return 状态见 2026-07-16 条目；本次 provenance 证据见 [2026-07-15 日志](logs/2026-07-15.md) 和 versioned PPM status。
- **2026-07-12**: 提交前 payload/分析语义复核完成修复：Gpr2 WT short/processed checksum manifest 移除 self-entry 并补齐 Git-visible recovery contract；历史 preproduction snapshot 保持 `11/14` integrity HOLD，final raw archive 本地为 `45/48`（3 个 runtime byproduct 待恢复）。两个 mutant system 的 PPM/input 与 clean/upload 历史到当前 checksum 迁移均无可证明记录，因此 CHARMM-GUI upload 暂停；Gpr3 的 `ASCR3_pose_completed.gro` 被明确提升为唯一 repo-owned canonical coordinate body。详细证据见 [2026-07-12 日志](logs/2026-07-12.md) 和对应 result/system manifests。
- **2026-07-09**: `Gpr2_WT + ASCR18` 200 ns rep1 在 E2 正常完成（2026-07-08 17:10:18 +0800），raw/sanity/processed 输入已归档到 `experiments/md-simulation/results/gpr2-wt-ascr18/`，并通过 chctrl 七指标 driver family 完成单 rep 分析。结果摘要见 [2026-07-09 日志](logs/2026-07-09.md) 和 `experiments/md-simulation/results/gpr2-wt-ascr18/analysis/gpr2_wt_ascr18_rep1_chctrl_metric_analysis_20260709.md`；该 rep1 当前作为 caveated WT holo triage evidence 使用，高 receptor RMSD 与 ASCR18 heavy-atom displacement 需要结构检查，且 ligand RMSD 暂无预注册分类阈值。
- **2026-07-06**: 记录 GPR MD 体系数量与采样队列决策，并新增 `Gpr2_WT + ASCR18` 200 ns rep1 launch-gate 证据；该证据只说明 `mdrun` 已在 2026-07-06T11:03:57+08:00 启动，尚不是 completion archive。详见 [2026-07-06 日志](logs/2026-07-06.md) 和 `experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260706_rep1_launch/README.md`；后续 completion 状态回 2026-07-09 日志与结果包。
- **2026-07-06**: mutant GPR CHARMM-GUI 当日路由收敛为两个 upload PDB、各自 `settings.tsv` 和既有 Membrane Builder 操作指南；该当日提交/回收动作已被 2026-07-12 checksum-provenance HOLD 取代，当前必须先按 [mutant input-gate plan](../codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md) 解决或版本化取代 checksum migration。
- **2026-07-06**: `Gpr3_R167Y + ASCR3` standalone ASCR3 46-atom ligand coordinate layer 已形成；仍需 CHARMM-GUI receptor/membrane output 后再做 receptor-frame insertion、clash sanity、topology/index/warning。详见 `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md`。
- **2026-07-05/06**: `Gpr2_WT + ASCR18` 100 ps short benchmark 已完成；mutant GPR 两体系已完成 AF3 sanity、package design、ligand topology scaffold、clean receptor、PPM output 和 CHARMM-GUI upload PDB/`settings.tsv`。这只是当日材料边界，现已被 2026-07-12 checksum-provenance HOLD 取代；当前动作与 runnable 条件只看两个 system-local `PACKAGE_STATUS.md` 和 [mutant input-gate plan](../codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md)。
- **2026-07-04**: R1 reduced `chctrl` exploratory prototype 在 E2 完成 CHARMM-GUI step6 minimization/equilibration 和 100 ps short production，记录 atom count、产出速率、GPU utilization、energy sanity 与 checksum；padding rule 仍为 `exploratory`，candidate-transfer 仍待新的 source-backed 规则。详见 [2026-07-04 日志](logs/2026-07-04.md) 与结果 README。
- **2026-07-04**: 公开 atom-count 对照和本地拓扑计数显示 R1 `120 A` XY / `20 A` water 实例为 Z-only 缩减，atom-count 降幅不足以解决 E2 算力紧缺；该实例保留为 chctrl build/run evidence point，候选迁移需新的 source-backed 物理规则。详见 [2026-07-04 日志](logs/2026-07-04.md) 与 `r1_z_only_public_atom_count_comparison.md`。
- **2026-06-26**: 记录 MD 算力收缩决策：旧 Slurm chimeric control/chctrl 组 3 reps 已完成，但 E2 路线只有 chctrl rep1 证据；候选体系 full MD 因算力不足暂停；下一步为 chimeric 省算力方案调研，并先从 `Gpr2_R59C` / `Gpr3_R167Y` 启动 mutant GPR MD 的体系大小核查和算力测试。详见 [决策 005](decisions/005-md-compute-triage-after-chctrl.md) 与 [2026-06-26 日志](logs/2026-06-26.md)。
- **2026-06-02**: E2 chctrl rep1 通过 full-system early stability gate；该路线后来被 2026-06-26 算力收缩决策暂停为历史执行路线。报告见 `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/early_gate_report.md`。
- **2026-06-01**: chimeric MD 新增 tiered validation protocol；当时定义为早期门禁通过后继续到 final production，等价替代仍需要 full-system 证据。2026-06-26 后该 protocol 作为历史执行背景和未来方案参考；chimeric candidate production 由新的当前 work order 触发。
- **2026-05-30**: chimeric MD 记录 checkpoint/benchmark 结果，并新增 E2 primary + Slurm RTX 5090 gated secondary 的统一 rerun 站点矩阵；详细数值和命令回 `docs/logs/2026-05-30.md`、`environments/` 和 `codex/docs/plans/`。
- **2026-05-25**: reporter 输出架构按用户确认和实验方案附件更新为 `异源 Gpr2/3 -> 嵌合 Gpa1 -> MAPK 级联 -> sTF -> GAL 多拷贝放大 -> 色素显色`；ODE/经济效益模型缺口说明和总览图填充文案已同步到路由文档；代码层仍等待 ODE solver 和经济模型实现。
- **2026-05-23**: 早期检测经济效益模型长期资料从 `tmp_papers/` 提升到 `docs/papers/p2-economic-benefit/`；Stage 3 外部 benchmark 抽取已进入 dossier，公开示例算术可验证，但最终 ROI 仍待 HP/湿实验/本地参数。

---

## 待办

### ① P0 MD 算力收缩 + mutant GPR 前测 ⭐⭐⭐（当前最高优先级）
- [x] MUSCLE/ClustalΩ 比对 Gpa1 vs Ao Gpa2 / Af GasA（+ gustducin/Gsα 对照）→ `experiments/chimeric-gpa1/alignment/`
- [x] C 端多档嫁接候选生成与 AF3 全量预测（42 jobs）→ `experiments/chimeric-gpa1/analysis/ranking_summary.md`
- [x] Top 3 嵌合候选选定；AoGpa2 `TGJ64397.1` 身份核查通过 → [True_Gpr2_or_not.md](logs/True_Gpr2_or_not.md)
- [x] production site / environment matrix archived → [md-production-sites.md](../environments/md-production-sites.md), [e2-md-gromacs.md](../environments/e2-md-gromacs.md)
- [x] chctrl selection audit：已核验 PROA/PROB、Gpa1 alpha5/eCT residue mapping、Ste2 interface geometry、fit/reference 路线；selection 定义可用于 caveated interpretation，但阈值来源审查仍未完成 → `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`
- [x] 按推荐 pin 创建/选择 E2 GROMACS 生产环境，并保存新的 preflight + conda snapshot
- [x] 对 chctrl + Ch-1/Ch-2/Ch-4 做输入审计/恢复、MDP/index 检查、rep1 `grompp` 和 smoke `mdrun`
- [x] 新增 Slurm RTX 5090 validated secondary 的环境矩阵、计划和专用 gate scripts；read-only preflight/resource gate 通过，但因无 conda-family package manager 阻塞在 same-pin env validation 前，不进入 smoke/benchmark/production
- [x] 旧 Slurm chimeric control/chctrl 组 3 reps MD 已完成；E2 路线只有 chctrl rep1 证据；结果结论仍需回源审计
- [x] 记录算力收缩决策：chimeric 候选体系 full-production 暂停；当前启动门禁以 [决策 005](decisions/005-md-compute-triage-after-chctrl.md) 为准，旧 E2/unified rerun 计划保留历史执行与脚本指针
- [x] 完成 `Gpr2_WT + ASCR18` E2 100 ps 短时 MD 资源基线，用于后续 mutant GPR 输入门禁和排程估算 → `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`
- [ ] 若重启 R1，必须先给出非 Z-only 的 source-backed 物理依据和预期 atom-count benefit；Ch-1/Ch-2/Ch-4 迁移等待该规则通过。
- [x] 归档 `Gpr2_WT + ASCR18` 200 ns rep1 的 final raw/result/sanity/processed package，并复用 chctrl 七指标 driver family 完成单 rep 分析 → `experiments/md-simulation/results/gpr2-wt-ascr18/analysis/gpr2_wt_ascr18_rep1_chctrl_metric_analysis_20260709.md`
- [x] 完成 `Gpr2_R59C + ASCR18` 200 ns rep1 终态审计、E2 postprocess、共享七 driver 与 WT/R59C matched single-rep comparison → `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_matched_comparison_20260719.md`
- [x] 完成 WT/R59C ASCR18 ligand-path 与 dynamic-pocket triage；`ILE122` 仅为旧起始 pose 下的历史交叉检查线索，不验证 repaired ranking，也不宣布最佳突变 → `experiments/md-simulation/results/gpr2-r59c-ascr18/analysis/gpr2_wt_r59c_ascr18_rep1_ligand_path_pocket_triage_20260719.md`
- [ ] `Gpr3_R167Y + ASCR3` AutoDL 200 ns rep1、completion finalization、postprocess 和共享七 driver 已完成；WT arm 尚无 production completion，matched WT 和后续 replicate 仍需独立排程和 gate。

### ② P0 docking-repro frame repair ⭐⭐⭐
- [x] 撤回旧 ratio/IFP/shortlist 和 39-file wetlab handoff；撤回边界持续有效，当前已推进至失败 smoke 的 full-run blocker
- [x] 以固定七 TM/147 Cα 对齐 162/162 个 Gpr2/Gpr3 mutant，并生成隔离 aligned-PDB/frame-manifest run
- [x] 建立 frame、PDBQT、environment、job/pose、geometry、terminal matrix、ratio/IFP 和候选 gate 的本地代码与回归测试
- [x] 在 E2 冻结 Vina conda 1.2.6、OpenBabel conda 3.1.1、ADFRsuite 1.1dev build 100 和新 run identity；4 个 receptor PDBQT 通过 frame check
- [x] 完成并保留 v3/v4 历史失败 smoke；18/20 已确认不是 Vina crash，v4 因缺显式 CPU8 不晋升为 production smoke
- [x] 实施 R1 recovery contract：maximum-20 技术语义、绝对 pose-population 下限、显式 CPU8 和完整 invocation identity；新 8-job docking 与 IFP 8/8 技术完成
- [x] 完成新 8-job geometry 终态：3/8 job 通过，5/8 未达到预冻结分布门；R167Y–ascr#3 的 MODEL 1 也未通过高度门
- [x] 完成历史/current WT calibration、工具链与 geometry gate 的只读审计；确认旧门不能直接作为 E2/Vina 1.2.6 hard gate
- [x] 完成 seed 43 四臂 WT calibration：4/4 docking、IFP 和历史门诊断正常完成，各返回 20 poses；未运行 mutant
- [x] 用 PyMOL notebook 确认四条 WT arm 的 MODEL 1 / pose 1 结合位置合理；该范围不等于全部 ensemble 逐一选优
- [x] 仅以 seed 42 + seed 43 WT evidence 冻结新 geometry gate，并完成独立 seed-44 holdout
- [x] seed-44 holdout 8/8 docking、IFP、geometry 技术完成；Gpr3/R167Y 两臂失败并固化 `fail_stop_before_full`
- [ ] 328-job 全量重跑保持阻塞；未创建 full plan、未启动剩余 320 jobs
- [ ] 从新 run-local score/pose/ratio/IFP 重建候选；通过严格审计后才生成新的 PyMOL/wetlab handoff

### ③ P0 信号通路 ODE（并行）
- [x] 归一化 Phase 0 原型：`src/modeling/ode/` Python solver + 严格参数 config + 模拟 CSV/plot（`scenario_prior`，不是校准 v0.1）
- [x] Phase 1 reporter 工程情景：sTF -> GAL 多拷贝放大 -> 色素显色的 copy-number/gain/leakage 扫参和匹配无 ligand 对照
- [x] 1/2/4 copy 归一化情景比较（不是实际构建优选结论）
- [x] Phase 2A 分析合同：18 字段参数空间、输出指标、主/诊断 contexts、参数—潜在可观测量—证据缺口和 guarded ratio
- [x] Phase 2B runner/config/test：局部时变敏感性、Morris、条件性 Sobol 和重点双参数曲面；当前支持设计预检与 `scenario_prior` 技术诊断
- [ ] Phase 2B 紧凑结果包与正式结果接纳；可识别性、拟合/不确定性传播和逐级 pathway kinetic model
- [ ] 与 docking 联动：WT 场景结构可继续使用；mutant 候选标签/排序/IFP 等待 frame-repaired 全量候选清单，Kd/calibration 需等待单独文献审查

### ④ 其他待启动
- [ ] reporter 实现参数讨论（具体色素 / 整合位点 / 实际拷贝数 / 输出增益 / 显色时间）
- [ ] 与 HP 组沟通经济效益模型参数，回填 `experiments/economic/configs/public_mvp_framework.json` 或后续正式 config
- [ ] 土壤扩散、贝叶斯推断、经济效益、剂量-响应等 P1/P2 方向按 Wiki 叙事需要启动
