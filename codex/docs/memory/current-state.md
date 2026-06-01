# Current drylab state memory

> 生成日期：2026-06-01
> Purpose: Codex project memory entry for current state. This file is pointer-based and does not replace `docs/INDEX.md`, domain docs, logs, or raw results.
> Read rule: use this file to find the relevant source logs, modeling docs, plans, and result files; verify conclusions in those sources.

## 1. chimeric MD：统一环境 clean-start rerun 是当前最高优先级

**当前状态（2026-06-01）**：chimeric MD 决策已更新为用统一 GROMACS 2025.4 MPI-CUDA 环境 clean-start 重跑 chctrl + Ch-1/Ch-2/Ch-4。E2 是 primary；旧 Slurm RTX 5090 仅作为 validated secondary candidate。E2 推荐环境/preflight、四体系输入同步和 rep1 smoke gate 已完成；`chimeric-ste2-gpa1-wt` rep1 full production 已在 2026-05-30 02:14 CST checkpoint 后按用户要求中断并保留 canonical `prod_rep1/prod.cpt`。same-GPU 2-job benchmark 显示最佳并发总吞吐低于单 job，当前不推荐 E2 同卡并行 production；rep1 已在 tmux `e2_chctrl_rep1_resume_20260530` 用 `-cpi prod.cpt -append` 单 job 恢复。2026-06-01 新增 100-150 ns full-system early stability gate，500 ns/replicate 仍是最终目标，局部口袋/interface-only MD 不替代当前 rerun。Slurm read-only preflight/resource gate 已通过，但用户环境没有 conda/mamba/micromamba，当前 blocked before same-pin env validation。以 `docs/logs/2026-05-30.md`、`docs/logs/2026-06-01.md`、`docs/INDEX.md`、`docs/modeling/P0-md-simulation.md`、`environments/md-production-sites.md`、`codex/docs/plans/e2-chimeric-md-restart.md` 和 `codex/docs/plans/chimeric-md-unified-rerun-sites.md` 为当前路由。

**历史状态指针**：旧 Slurm/chctrl production 和 selection audit 只作历史证据/方法参考，不再作为当前 baseline 接受状态。旧 selection audit 报告仍在 `/Users/roy/Documents/drylab/experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`；old Slurm production logs 在 `/Users/roy/Documents/drylab/experiments/md-simulation/results/chimeric-ste2-gpa1-wt/raw/rep{1,2,3}/prod.log`。

**当前待办（2026-06-01）**：监控 E2 tmux `e2_chctrl_rep1_resume_20260530` 中的 chctrl rep1 single-job production；到 100-150 ns early gate 时按 `codex/docs/plans/e2-chimeric-md-restart.md` 暂停/同步/分析/决定继续或归档；完成后用 `RESULTS_RUN_ID=20260529_e2_rerun` 同步回本地并做 `prod.log` 正常终止、`prod.cpt/gro/xtc/edr/tpr`、checksum 和 `gmx check` 校验。Slurm 下一步需要先解决用户目录 conda-family package manager 或另行批准异路径构建；未完成 same-pin env validation 前不启动 smoke、benchmark 或 production。当前不要再做 E2 同卡 full-production 并发。

- Chimeric MD current status is routed through INDEX, the MD direction doc, the active execution plans, and recent logs. Do not infer run state, targets, or continue/stop advice from memory alone. Pointers: [docs/INDEX.md](../../../docs/INDEX.md), [docs/modeling/P0-md-simulation.md](../../../docs/modeling/P0-md-simulation.md), [codex/docs/plans/e2-chimeric-md-restart.md](../plans/e2-chimeric-md-restart.md), [docs/logs/](../../../docs/logs/).
- Remote-compute and MD site policy is indexed in the environment docs and site plans. Do not infer server, job, checkpoint, or scheduler state from memory alone. Pointers: [environments/md-production-sites.md](../../../environments/md-production-sites.md), [environments/e2-md-gromacs.md](../../../environments/e2-md-gromacs.md), [codex/docs/plans/chimeric-md-unified-rerun-sites.md](../plans/chimeric-md-unified-rerun-sites.md), [docs/ops/](../../../docs/ops/).
- Docking candidate and wet-lab handoff status must be read from the current docking direction doc, handoff, ratio outputs, and logs. Do not use historical Top sets or memory summaries as recommendations. Pointers: [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md), [docs/modeling/wet-lab-handoff-P0-docking.md](../../../docs/modeling/wet-lab-handoff-P0-docking.md), [docs/logs/](../../../docs/logs/).
- ODE and reporter claims route through the ODE direction doc, reporter decision, and current INDEX/log pointers. Do not convert docking scores into calibrated ODE inputs from memory. Pointers: [docs/modeling/P0-signal-pathway-ode.md](../../../docs/modeling/P0-signal-pathway-ode.md), [docs/decisions/004-reporter-output-architecture.md](../../../docs/decisions/004-reporter-output-architecture.md), [docs/INDEX.md](../../../docs/INDEX.md).
- P2 economic-model status and parameter readiness route through the P2 direction doc, evidence dossier, validation notes, and HP/local-parameter logs. Do not state final ROI or calibrated local economics from memory. Pointers: [docs/modeling/P2-economic-benefit.md](../../../docs/modeling/P2-economic-benefit.md), [docs/papers/p2-economic-benefit/README.md](../../../docs/papers/p2-economic-benefit/README.md), [docs/logs/](../../../docs/logs/).

## state_timeline

Do not read this timeline as current state. It only preserves dated routing
pointers for cross-session recovery.

- 2026-06-02: chimeric MD gate/status evidence was logged; read the log and INDEX before making any run-state claim. Source: [docs/logs/2026-06-02.md](../../../docs/logs/2026-06-02.md).
- 2026-06-01: validation protocol and gate semantics were recorded; read the log and active plans before applying criteria. Source: [docs/logs/2026-06-01.md](../../../docs/logs/2026-06-01.md).
- 2026-05-30: E2/secondary-site routing and interruption evidence were recorded; read environment docs, plans, and logs before giving execution advice. Source: [docs/logs/2026-05-30.md](../../../docs/logs/2026-05-30.md).
- 2026-05-19/20: docking-repro handoff refresh became the current candidate route; read the handoff and docking direction doc for candidate claims. Sources: [docs/logs/2026-05-19.md](../../../docs/logs/2026-05-19.md), [docs/modeling/P0-molecular-docking.md](../../../docs/modeling/P0-molecular-docking.md).
- 2026-04-11: yeast-STE2 chassis decision set the strategic baseline; later implementation status must be read from INDEX/logs/domain docs. Sources: [docs/decisions/003-chassis-yeast-ste2-integration.md](../../../docs/decisions/003-chassis-yeast-ste2-integration.md), [docs/prd/chassis-decision.md](../../../docs/prd/chassis-decision.md).

## source_pointers

- `/Users/roy/Documents/drylab/docs/logs/2026-04-26.md` — 旧 Slurm/chctrl 状态核查的历史指针，不作为当前 rerun 状态。
- `/Users/roy/Documents/drylab/docs/logs/2026-05-30.md` — E2 checkpoint-gated benchmark、single-job resume、Slurm RTX 5090 secondary candidate preflight。
- `/Users/roy/Documents/drylab/docs/logs/2026-06-01.md` — full-system early stability gate 方法学决策。
- `/Users/roy/Documents/drylab/docs/modeling/P0-md-simulation.md` — MD phase 定义、chimeric C1-C5 状态、7 项分析指标。
- `/Users/roy/Documents/drylab/docs/INDEX.md` — 当前优先入口与阻塞项。

## 2. docking-repro：Gpr2/Gpr3 修复后的结果刷新已完成，进入湿实验交接执行

**当前状态**：2026-05-20 已完成 repo-owned full refresh plan 的 Phase 1-7：Gpr2 3D offset、Gpr3 方案 F、Gpr3 supplemental docking、266 条 merged ratio、8 个 Top 候选 IFP 与湿实验 handoff 均已刷新。当前首选候选见 handoff；不要从本 memory 复制数值结论。

**已完成补充任务（用户 2026-04-27 指定）**：Gpr3 F 更多 IFP 相关位点的 supplemental AF3/docking 已纳入刷新。原 batch JSON 输入为：

- `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_01.json`
- `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_02.json`

**Plan 指针**：

- `/Users/roy/Documents/drylab/codex/docs/plans/docking-repro-full-refresh-slurm.md` — repo-owned full refresh plan；Phase 1-7 执行证据见 2026-05-19 日志和结果文件。
- `/Users/roy/.claude/plans/gpr3-1-2-cozy-bengio.md` — Gpr3 pose 质量审查、方案 F、全量重跑与后续 ratio/IFP 刷新框架。
- `/Users/roy/.claude/plans/charmmgui-membrane-builder-gpr2-icl-vin-whimsical-ripple.md` — Gpr2 grid/offset 污染核查与重跑决策。
- `/Users/roy/.claude/plans/tidy-yawning-twilight.md` — 比值型双通道 docking 数据分析框架。
- `/Users/roy/.claude/plans/virtual-wobbling-peach.md`、`/Users/roy/.claude/plans/greedy-nibbling-shannon.md` — ProLIF/IFP 通道与盐桥检测修复背景。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/logs/2026-04-23.md` — Gpr2 重跑完成、Gpr3 box/offset/F 方案审查与 PASS 记录。
- `/Users/roy/Documents/drylab/docs/logs/2026-04-27.md` — INDEX 与 P0 docking 状态校准；明确旧 wet-lab handoff 不可直接下发。
- `/Users/roy/Documents/drylab/docs/logs/2026-05-19.md` — full refresh Phase 1-7 执行记录和校验指针。
- `/Users/roy/Documents/drylab/docs/modeling/P0-molecular-docking.md` — docking-repro 当前 `refreshed_handoff` 状态与使用纪律。
- `/Users/roy/Documents/drylab/docs/modeling/wet-lab-handoff-P0-docking.md` — 当前湿实验候选权威交接。
- `/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_channel_report.md` — 当前 266 条 merged ratio 报告。
- `/Users/roy/Documents/drylab/experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/` — 当前 refreshed Top 候选 IFP 输出。

## 3. 嵌合 Gpa1：AF3 全量筛选完成，当前进入 MD validation

**当前状态**：嵌合 Gpa1 设计与 AF3 全量筛选已完成，Top 3 候选已选；AoGpa2 `TGJ64397.1` 身份核查支持其为 Kuo2024 GPA2 构建对应序列，Gpr2/Gpr3 → AoGpa2 设计暂不回滚。当前可靠性主要等待 chimeric MD 验证。

**Plan 指针**：

- `/Users/roy/.claude/plans/lively-spinning-newt.md` — Chimeric Gpa1 MD 路线规划与文献/技术栈背景。
- `/Users/roy/.claude/plans/dreamy-shimmying-harp.md` — Chimeric MD 前置调研、Gpr2-AoGpa2 偶联缺口与体系选择重评估。
- `/Users/roy/.claude/plans/chimeric-md-execution.md` — Chimeric Gpa1 MD 执行计划。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/logs/True_Gpr2_or_not.md` — AoGpa2 `TGJ64397.1` / GPA2 身份核查。
- `/Users/roy/Documents/drylab/docs/logs/2026-04-26.md` — 旧 Slurm/chimeric MD 状态核查的历史指针。
- `/Users/roy/Documents/drylab/docs/logs/2026-05-30.md` 与 `/Users/roy/Documents/drylab/docs/logs/2026-06-01.md` — 当前统一 rerun 路线和 early stability gate。
- `/Users/roy/Documents/drylab/docs/modeling/P3-chimeric-gprotein.md` — 嵌合 Gpa1 方向权威文档，当前 `MD_validation`。
- `/Users/roy/Documents/drylab/experiments/chimeric-gpa1/analysis/ranking_summary.md` — AF3 Top 候选选择结果。

## 4. ODE / 显色级联：并行推进，但关键输入等待 docking 与湿实验方案

**当前状态**：底盘已锁定酵母 STE2 + 嵌合 Gpa1 + 基因组单拷贝整合；ODE 可继续整理模型框架和参数源。Docking Top 候选标签已刷新，但 Kd/calibration 仍需等待单独文献审查，不能把 docking ΔG 直接转换为 Kd。显色级联方案仍 TBD。P2 经济效益模型已进入 `framework_mvp`，但本地成本、部署密度、检测性能和支付意愿仍待 HP/湿实验回收。

**Plan 指针**：

- `/Users/roy/.claude/plans/playful-watching-raccoon.md` — 底盘决策落地、饱和突变审查、MD 补充的项目级转向背景。
- `/Users/roy/.claude/plans/functional-sauteeing-sunrise.md` — docking 教学/交接材料背景；与湿实验沟通材料有关。
- 注：未在 `/Users/roy/.claude/plans` 中确认到专门的 ODE 执行 plan；ODE 当前以项目文档为权威。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/modeling/P0-signal-pathway-ode.md` — STE2 ODE 模型方向文档。
- `/Users/roy/Documents/drylab/docs/prd/overview-v4.md` — 酵母-STE2 当前项目全貌与显色级联 TBD。
- `/Users/roy/Documents/drylab/docs/decisions/003-chassis-yeast-ste2-integration.md` — 底盘决策权威记录。
- `/Users/roy/Documents/drylab/docs/logs/2026-04-27.md` — 当前 INDEX 校准与待办。

## 5. P2 经济效益模型：framework MVP 已有，最终 ROI 等 HP/本地参数

**当前状态**：P2 早期检测经济效益模型已经有 Stage 1/2 文献/参数矩阵和 deterministic cost-accounting MVP。当前结果只能解释框架与 break-even 结构，不能作为最终 ROI。不要把 docking Delta G、ODE Kd 或未验证 wet-lab 假设当作经济确定输入。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/modeling/P2-economic-benefit.md` — P2 方向权威状态、示例分析边界和依赖。
- `/Users/roy/Documents/drylab/docs/papers/p2-economic-benefit/README.md` — P2 文献/数据源包入口。
- `/Users/roy/Documents/drylab/docs/modeling/P2-economic-benefit-hp-questionnaire.md` — HP 参数回收问卷。
- `/Users/roy/Documents/drylab/experiments/economic/README.md` — MVP 代码、配置和输出路径。
- `/Users/roy/Documents/drylab/docs/logs/2026-05-23.md` — P2 长期资料迁移与路由更新记录。
