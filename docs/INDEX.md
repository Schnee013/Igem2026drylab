# iGEM DryLab 干实验 — 项目索引

> 最后校准：2026-07-06。本文是项目路由表，不承载详细结果数值；需要结论时请沿链接读取领域文档、日志和原始结果文件。

## 项目概述

- **一句话**: 构建基于 GPCR 生物传感器的植物寄生线虫田间早期检测系统的干实验（计算建模）模块
- **当前阶段**: 底盘已锁定酵母-STE2；docking-repro 已完成刷新交接；旧 Slurm 上 chimeric Gpa1 control/chctrl 组 3 reps MD 已完成，E2 路线已有 chctrl rep1 early-gate 证据和 R1 reduced-chctrl exploratory step6/100 ps short-production 证据；R1 Z-only 因 atom-count 降幅过小降级为证据点，候选体系 production 仍暂停；mutant GPR 前测分两条证据线：`Gpr2_WT + ASCR18` 100 ps 资源基线已完成，200 ns rep1 目前只有 2026-07-06 launch-gate/started 证据、尚无 completion archive；`Gpr2_R59C + ASCR18` 与 `Gpr3_R167Y + ASCR3` 已到 CHARMM-GUI operator/request + return-intake 门禁，仍缺 returned output、final ligand insertion、topology、index 和 warning review。
- **主要卡点**: E2 是当前主要可用算力且属于共享服务器，后续 MD 必须降低 A100 占用。R1 reduced `chctrl` 已能完成 step6 和 100 ps short production，但 `120 A` XY / `20 A` water 的 Z-only 缩减只有 `-2.57%` atom-count delta，不足以解决算力问题，且不是 candidate-transfer rule；mutant GPR 已越过 design/PPM/submission-preflight 层，当前卡在 CHARMM-GUI output 回收、system-local intake/validator manifest、receptor-frame ligand insertion/alignment、final topology/index/warning review，以及 `Gpr2_WT + ASCR18` rep1 completion archive。docking 构建容量、reporter 实现参数和 HP 本地参数仍待湿实验/HP 确认。
- **目标**: iGEM Wiki freeze 约 2026-09 底
- **详细背景**: [项目全貌 v4](prd/overview-v4.md)

---

## 建模方向状态

| 优先级 | 方向 | 底盘相关 | 当前状态 | 文档 |
|--------|------|---------|----------|------|
| **P0** | 受体-配体分子对接 | 否 | **refreshed_handoff**：Gpr2 3D offset、Gpr3 方案 F、Gpr3 supplemental docking、266 条 merged ratio、Top 候选 IFP 与湿实验交接均已刷新 | [P0-molecular-docking.md](modeling/P0-molecular-docking.md) |
| **P0** | MD 模拟（突变体稳定性 + 嵌合 Gpa1 验证） | 否/酵母触发 | **compute_triage**：旧 Slurm control/chctrl 3 reps 为历史完成证据，E2 有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据；R1 Z-only 已降级为省算力不足；候选体系 full MD 暂停；mutant GPR 有 WT short benchmark 和 WT rep1 launch-gate 证据，两个 mutant system 已到 CHARMM-GUI 手工提交/回传接收门禁，但还不是 runnable package，full-production 决策未完成 | [P0-md-simulation.md](modeling/P0-md-simulation.md) |
| **P0** | 信号通路 ODE 建模（酵母 STE2） | 已锁定酵母 | in_progress：文献证据、参数状态、湿实验校准需求已整理；reporter 架构已确认；尚无 `src/modeling/ode/` solver、config 或 plots | [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) |
| **P0** | 嵌合 Gpa1 同源性建模 | 酵母触发 | **MD_validation_paused_compute_triage**：42 个 AF3 jobs + Top 3 选择完成；AoGpa2 序列核查通过；旧 Slurm control/chctrl 组 3 reps 完成，E2 有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据；R1 Z-only 不作为候选迁移规则，候选体系验证暂停 | [P3-chimeric-gprotein.md](modeling/P3-chimeric-gprotein.md) |
| **P1** | 土壤 ascaroside 扩散模型 | 否 | not_started | [P1-soil-diffusion.md](modeling/P1-soil-diffusion.md) |
| **P1** | 标志物→线虫丰度贝叶斯推断 | 否 | not_started | [P1-bayesian-inference.md](modeling/P1-bayesian-inference.md) |
| **P2** | 早期检测经济效益模型 | 否 | **framework_mvp_validated_arithmetic + stage3_benchmarks_extracted**：deterministic cost-accounting MVP 已落地并验证公开示例算术；最终 ROI 仍待 HP/湿实验/本地参数校准 | [P2-economic-benefit.md](modeling/P2-economic-benefit.md) |
| **P2** | 化学杀线虫剂剂量-响应 | 否 | not_started | [P2-dose-response.md](modeling/P2-dose-response.md) |
| ~~P2~~ | ~~生物防治 Lotka-Volterra~~ | 仅丝状真菌 | **archived** | [P2-biocontrol-lv.md](modeling/P2-biocontrol-lv.md) |

---

## 阻塞性待确认事项

> 2026-04-11 底盘 4 项阻塞全部解除（PI 确认酵母-STE2 主线，详见 [决策 003](decisions/003-chassis-yeast-ste2-integration.md)）。

- [ ] **[门禁] MD 算力收缩与排程**：按 [决策 005](decisions/005-md-compute-triage-after-chctrl.md)，chimeric 候选体系 full-production 暂停；先调研减少体系大小或更强 restraint 的省算力 protocol。E2 是共享服务器，后续 MD 必须先做资源估算/短程 benchmark，不得长期独占 A100。
- [ ] **[门禁] mutant GPR MD 前测**：`Gpr2_WT + ASCR18` E2 短时资源基线已完成；2026-07-06 已把后续队列收缩为 staged funnel：先完成并归档 `Gpr2_WT + ASCR18` 200 ns rep1，再推进 `Gpr2_R59C + ASCR18` package gate、smoke/benchmark 和 200 ns rep1，完成 Gpr2 WT/mut matched analysis 后再启动 `Gpr3_WT + ASCR3` / `Gpr3_R167Y + ASCR3` matched pair；rep1 稳定时暂停 rep2/3，待最终 candidate 保留后补齐。
- [ ] **[质量门] 预注册 operational cutoff 来源审查**：所有用于 go/no-go 的项目预注册阈值、技术栈选择、几何定义和数值判据必须补齐 DOI / 标题 / 原文方法段落 / 官方工具文档等 exact pointer；没有 exact pointer 的文献引用暂不承认，统一标记为待查验或项目 operational heuristic。
- [ ] **[待确认] docking 首批构建容量/交接执行**：刷新后的 handoff 已落地，当前首选 `Gpr2_R59C + Gpr3_R167Y`；下一步需湿实验组确认首批构建容量和读出设计。
- [ ] **[待确认] reporter 输出实现参数**：架构已确认（sTF -> GAL 多拷贝放大 -> 色素显色），但具体色素、整合位点、实际拷贝数、输出增益和 time-course 参数仍需通路工程组/湿实验校准。
- [ ] **[重要] HP 组沟通**: 回收经济模型的本地参数：传感器单次成本、部署密度、检测性能、当地 lab 成本/周期、施药/轮作/抗性品种成本、作物价格与农户支付意愿。

---

## 当前优先入口

1. **MD 算力收缩与 mutant GPR 前测** — 决策见 [决策 005](decisions/005-md-compute-triage-after-chctrl.md)；WT 资源基线见 [2026-07-05 日志](logs/2026-07-05.md) 和 `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`；WT 200 ns rep1 只有 launch gate/started 证据，见 `experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260706_rep1_launch/README.md`。mutant GPR local input gate 见 `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`、`experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/material_matrix.tsv` 和 `decision_package.md`；CHARMM-GUI operator/return 协调用 `codex/docs/plans/igem2026-drylab-material-return-board-20260706.md`、`codex/docs/plans/igem2026-drylab-outbound-requests-20260706.md` 和 `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md`。下一步是回收两个体系的 CHARMM-GUI output，填 intake/manifest 后完成 ASCR18/ASCR3 final coordinate、topology、index 和 warning review；方法边界见 [P0-md-simulation.md](modeling/P0-md-simulation.md)。
2. **chimeric Gpa1 省算力方案调研** — 候选体系 production 仍暂停；R1-Z 对照与路线选择历史见 `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md` 和 `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`。旧 E2/unified rerun 计划保留为历史脚本参考，不是当前 full-production 启动指令。
3. **docking-repro 湿实验交接** — 当前权威候选见 [wet-lab-handoff-P0-docking.md](modeling/wet-lab-handoff-P0-docking.md)；证据链从 [2026-05-19 日志](logs/2026-05-19.md) 与 [ratio_channel_report.md](../experiments/docking-repro/analysis/ratio_channel_report.md) 读取。
4. **ODE 并行推进** — 用 [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) 维护通路结构、参数状态和 reporter 输出接口；候选标签可引用新版 docking handoff，但 Kd/calibration 仍等待文献/湿实验校准，尚未进入 solver 实现。
5. **早期检测经济效益模型 HP 参数回收** — 文献/参数入口见 [early-detection economic-benefit dossier](papers/p2-economic-benefit/README.md)，问卷见 [P2-economic-benefit-hp-questionnaire.md](modeling/P2-economic-benefit-hp-questionnaire.md)；当前只能做公开示例和 break-even 结构。
6. **湿实验/reporter 输出参数讨论** — 需要结合 [overview-v4.md](prd/overview-v4.md)、[决策 003](decisions/003-chassis-yeast-ste2-integration.md)、[决策 004](decisions/004-reporter-output-architecture.md) 与 ODE 需求。

---

## 策略文档

| 文档 | 内容 | 链接 |
|------|------|------|
| 项目全貌 v4 | 锁定酵母-STE2 后的核心信号链路、团队、受体、文献 | [overview-v4.md](prd/overview-v4.md) |
| 干实验总策略 | §2 方向评估、痛点调研、防治决策 | [dry-lab-strategy.md](prd/dry-lab-strategy.md) |
| 底盘决策（已定） | §最终决策：策略 B 酵母-STE2-基因组整合 | [chassis-decision.md](prd/chassis-decision.md) |
| 决策 003 | 底盘选择技术决策记录 | [003-chassis-yeast-ste2-integration.md](decisions/003-chassis-yeast-ste2-integration.md) |
| 学习路线图 | §4+§6 学习资源、硬件、工具 | [roadmap.md](learning/roadmap.md) |

## 湿实验交接

> 注意：P0 docking 交接已刷新；不要复用 2026-04-14 版旧 Top 候选或把 Vina ΔG 直接转换为 Kd。

| 文档 | 内容 | 链接 |
|------|------|------|
| P0 分子对接交接（权威源，已刷新） | Top 候选、双通道全谱排名、底盘上下文、计算局限性 | [wet-lab-handoff-P0-docking.md](modeling/wet-lab-handoff-P0-docking.md) |
| P0 分子对接交接（飞书扁平版，已刷新） | 同上内容，飞书云文档/多维表格粘贴版 | [wet-lab-handoff-P0-docking-feishu.md](modeling/wet-lab-handoff-P0-docking-feishu.md) |

## 运维参考

- **当前服务器入口**：新服务器/远程计算任务默认使用 [NKULiulab E2 共享云服务器](ops/nkuliulab-e2-cloud-server.md)。2026-06-26 后 chimeric 候选 full-production 暂停，旧 Slurm secondary route 只保留为历史/未来备选指针；任何新的 MD production 都必须先做资源估算和短程 benchmark。
- **GROMACS / MD 操作踩坑索引**：[md-gromacs-operational-pitfalls.md](ops/md-gromacs-operational-pitfalls.md)（服务器中立；新任务仍先读 E2 手册）
- **[已归档] Slurm GPU 集群**：[slurm-md-server.md](ops/archives/slurm-md-server.md)（仅用于追溯旧 MD/Slurm 运行记录；2026-05-30 chimeric secondary route 已于 2026-06-26 降级为历史/未来备选指针，相关脚本和 gate 见 `environments/md-production-sites.md` 和 `experiments/md-simulation/scripts/slurm_*`）
- **[已归档] Sunlab 历史文件查询服务器**：[sunlab-historical-server.md](ops/archives/sunlab-historical-server.md)（`10.40.4.2`，本机 alias `drylab-10-40-4-2`；仅用于查询历史文件，不是当前活跃计算入口）
- **[已归档] HBU SGE 集群**：[hbu-sge-cluster.md](ops/archives/hbu-sge-cluster.md)（仅用于追溯旧 HBU SGE 调研/投递记录）
- **[已弃用] Windows SSH 操作指南**：[ssh-windows-compute.md](ops/archives/ssh-windows-compute.md)（Windows 7500F 节点停用；部分 docking 结构文件仍存于该节点，需访问时参考此文档）

## 文献

> **读取策略**: 需要某篇文献时，先查矩阵确认编号，再只读取对应的 `summaries/` 文件。**不要批量读取所有总结，不要直接读 PDF**。

- **文献调研入口**: [文献矩阵](papers/literature-matrix.md)（当前本地记录：58 篇 PDF / 59 篇已总结，详见矩阵头部）
- **早期检测经济效益模型文献/数据源包**: [early-detection economic-benefit](papers/p2-economic-benefit/README.md)（Stage 1/2 paper/data matrix、参数表、source evidence；Stage 3 external benchmark extraction）
- **组员使用说明**: [papers/README.md](papers/README.md)
- INDEX 不再维护完整已总结清单，避免与矩阵重复和漂移；请以 `papers/literature-matrix.md` 为文献路由权威。

## 归档

| 文件 | 说明 | 位置 |
|------|------|------|
| PRD v3 原始文件 | 已拆分到 prd/ 各子文档 | [archive/iGEM_DryLab_PRD_v3.md](archive/iGEM_DryLab_PRD_v3.md) |
| Claude Code Skill 指南 | 项目管理参考 | [archive/claude-code-skill-guide.md](archive/claude-code-skill-guide.md) |

---

## 最近进展

- **2026-07-06**: 记录 GPR MD 体系数量与采样队列决策，并新增 `Gpr2_WT + ASCR18` 200 ns rep1 launch-gate 证据；该证据只说明 `mdrun` 已在 2026-07-06T11:03:57+08:00 启动，尚不是 completion archive。详见 [2026-07-06 日志](logs/2026-07-06.md)、`experiments/md-simulation/results/gpr2-wt-ascr18/gates/20260706_rep1_launch/README.md` 和 `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/decision_package.md`。
- **2026-07-06**: mutant GPR CHARMM-GUI operator packet、return intake 模板、submission preflight、return validator、material-return board 和 outbound request pack 已形成；下一步是手工提交/回收两个 CHARMM-GUI output，并填 system-local intake/manifest。详见 `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md`。
- **2026-07-06**: `Gpr3_R167Y + ASCR3` standalone ASCR3 46-atom ligand coordinate layer 与 mutant GPR MD metric pre-registration 已形成；仍需 CHARMM-GUI receptor/membrane output 后再做 receptor-frame insertion、clash sanity、topology/index/warning。详见 `experiments/md-simulation/systems/gpr3-R167Y-ascr3/gromacs/ascr3_coordinate_completion/ascr3_coordinate_completion_status.md` 和 `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/mutant_gpr_md_metric_preregistration_20260706.md`。
- **2026-07-05/06**: `Gpr2_WT + ASCR18` 100 ps short benchmark 已完成；mutant GPR 两体系已完成 AF3 sanity、package design、ligand topology scaffold、clean receptor、PPM output 和 CHARMM-GUI manual submission package，但仍不是 runnable package。详见 [2026-07-05 日志](logs/2026-07-05.md)、[2026-07-06 日志](logs/2026-07-06.md) 和 `experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/decision_package.md`。
- **2026-07-04**: R1 reduced `chctrl` exploratory prototype 在 E2 完成 CHARMM-GUI step6 minimization/equilibration 和 100 ps short production，记录 atom count、产出速率、GPU utilization、energy sanity 与 checksum；padding rule 仍为 `exploratory`，不是 candidate-transfer rule。详见 [2026-07-04 日志](logs/2026-07-04.md) 与结果 README。
- **2026-07-04**: 公开 atom-count 对照和本地拓扑计数显示 R1 `120 A` XY / `20 A` water 实例为 Z-only 缩减，atom-count 降幅不足以解决 E2 算力紧缺；该实例保留为 chctrl build/run evidence point，不迁移候选。详见 [2026-07-04 日志](logs/2026-07-04.md) 与 `r1_z_only_public_atom_count_comparison.md`。
- **2026-06-26**: 记录 MD 算力收缩决策：旧 Slurm chimeric control/chctrl 组 3 reps 已完成，但 E2 路线只有 chctrl rep1 证据；候选体系 full MD 因算力不足暂停；下一步为 chimeric 省算力方案调研，并先从 `Gpr2_R59C` / `Gpr3_R167Y` 启动 mutant GPR MD 的体系大小核查和算力测试。详见 [决策 005](decisions/005-md-compute-triage-after-chctrl.md) 与 [2026-06-26 日志](logs/2026-06-26.md)。
- **2026-06-02**: E2 chctrl rep1 通过 full-system early stability gate；该路线后来被 2026-06-26 算力收缩决策暂停为历史执行路线。报告见 `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/early_gate_report.md`。
- **2026-06-01**: chimeric MD 新增 tiered validation protocol；当时定义为早期门禁通过后继续到 final production，局部口袋/interface-only MD 不作为等价替代。2026-06-26 后该 protocol 作为历史执行背景和未来方案参考，不再直接触发 chimeric candidate production。
- **2026-05-30**: chimeric MD 记录 checkpoint/benchmark 结果，并新增 E2 primary + Slurm RTX 5090 gated secondary 的统一 rerun 站点矩阵；详细数值和命令回 `docs/logs/2026-05-30.md`、`environments/` 和 `codex/docs/plans/`。
- **2026-05-25**: reporter 输出架构按用户确认和实验方案附件更新为 `异源 Gpr2/3 -> 嵌合 Gpa1 -> MAPK 级联 -> sTF -> GAL 多拷贝放大 -> 色素显色`；ODE/经济效益模型缺口说明和总览图填充文案已同步到路由文档，未新增 ODE solver 或经济模型代码。
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
- [x] 记录算力收缩决策：chimeric 候选体系 full-production 暂停，旧 E2/unified rerun 计划不再作为直接启动指令 → [决策 005](decisions/005-md-compute-triage-after-chctrl.md)
- [x] 完成 `Gpr2_WT + ASCR18` E2 100 ps 短时 MD 资源基线，用于后续 mutant GPR 输入门禁和排程估算 → `experiments/md-simulation/results/gpr2-wt-ascr18/e2_short_benchmark/20260705_gpr2_wt_ascr18_short/README.md`
- [ ] 若重启 R1，必须先给出非 Z-only 的 source-backed 物理依据和预期 atom-count benefit；在此之前不迁移到 Ch-1/Ch-2/Ch-4
- [ ] 归档 `Gpr2_WT + ASCR18` 200 ns rep1 的 final raw/result/sanity/checksum package；当前 repo 只有 launch-gate/started 证据，不能写成 rep1 完成。
- [ ] 继续 mutant input gate：先回收 `Gpr2_R59C + ASCR18` / `Gpr3_R167Y + ASCR3` CHARMM-GUI output，填 intake/manifest，完成 final coordinate/topology/index/warning review；任一体系先完整时再写对应 single-system smoke/benchmark 计划。
- [ ] Gpr2 WT/mut matched analysis 完成后，再推进 `Gpr3_WT + ASCR3` / `Gpr3_R167Y + ASCR3` matched pair；rep1 稳定时暂停 rep2/3，待最终 candidate 保留后补齐。

### ② P0 docking-repro 结果刷新 ⭐⭐⭐
- [x] Gpr2 3D offset WT/Ala/Sat 重跑完成；旧 Gpr2 污染结果不再作为权威
- [x] Gpr3 方案 F pose 几何 PASS；Gpr3 F Ala/Sat 产物已生成
- [x] 合并 Gpr3 F Ala/Sat/supplemental 到全量 mutagenesis JSON，重跑 `ratio_channel_analysis.py`
- [x] 对新 Gpr2/Gpr3 F Top 候选重跑/刷新 ProLIF IFP 与机制解释
- [x] 刷新 `wet-lab-handoff-P0-docking*.md`；旧 Top 配对已替换
- [ ] 视 PI/湿实验沟通需要补 PyMOL PNG/PSE 渲染交付物

### ③ P0 信号通路 ODE（并行）
- [ ] ODE v0.1 solver：`src/modeling/ode/` Python 实现 + 参数 config + 模拟输出 CSV/plots
- [ ] reporter 输出层：sTF -> GAL 多拷贝放大 -> 色素显色的 copy-number/gain/leakage 扫参
- [ ] 1/2/4 copy 拷贝数敏感性分析
- [ ] 与 docking 联动：候选标签可引用新版 handoff；Kd/calibration 需等待单独文献审查

### ④ 其他待启动
- [ ] reporter 实现参数讨论（具体色素 / 整合位点 / 实际拷贝数 / 输出增益 / 显色时间）
- [ ] 与 HP 组沟通经济效益模型参数，回填 `experiments/economic/configs/public_mvp_framework.json` 或后续正式 config
- [ ] 土壤扩散、贝叶斯推断、经济效益、剂量-响应等 P1/P2 方向按 Wiki 叙事需要启动
