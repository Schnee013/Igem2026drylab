# Current drylab state memory

> 生成日期：2026-04-27
> Purpose: Codex project memory entry for current state. This file is pointer-based and does not replace `docs/INDEX.md`, domain docs, logs, or raw results.
> Read rule: use this file to find the relevant source logs, modeling docs, plans, and result files; verify conclusions in those sources.

## 1. chimeric MD：chctrl 阳性对照本地分析是当前最高优先级

**当前状态**：`chimeric-ste2-gpa1-wt` / chctrl 的 3 条 production MD 已完成；Ch-1/Ch-2/Ch-4 暂停，等待 chctrl 本地下载、PBC 修正和第一批指标分析后，再决定是否重启或续跑。

**新增待办（2026-04-29）**：chctrl C5 selection audit 已执行，报告：`/Users/roy/Documents/drylab/experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`。结果支持 selection 定义可用于 caveated interpretation，但 chctrl 仍是 “usable with alpha5 caveat”，不是 clean all-metric pass；Ch-1/Ch-2/Ch-4 不自动重启。所有用于 go/no-go 的 operational cutoff 仍必须补齐 DOI / 标题 / 原文方法段落 / 官方工具文档等 exact pointer；没有 exact pointer 的文献引用暂不承认，先标为待查验或 project operational heuristic。

**cutoff-source audit（2026-04-29）**：报告 `.../analysis/cutoff_source_audit.md`。Ste2 interface ranges 已改为 7AD3-derived project structural selection；“Bauer 2022” 未通过 exact-pointer 审查，α5 iRMSD 3/5 Å 与 BSA 20% 均降级为 project operational heuristic；GPCRsignal 支持 interaction frequency 但不支持 >0.50 universal pass；MDAnalysis 支持 H-bond 3.0 Å / 150° 几何但不支持 occupancy >10%。

**GPCR-Gα tech-stack source audit（2026-05-06）**：`docs/modeling/P0-md-tech-stack-research.md §12` 已修订：Ramasamy→Mohanty、Ranganathan→Renault、Jakowiecki→Miszta、Memprot first author/title/DOI 纠正；Tawfeeq 2025 保留为 chimeric Gα 18-aa swap + 4×500 ns 先例，但不再作为 GROMACS/CHARMM36m、empty-only 或 BSA/iRMSD/contact-persistence cutoff 来源；old only-N novelty claims 暂停使用，标为 pending source audit。

**Plan 指针**：

- `/Users/roy/.claude/plans/mac-pbc-memory-memory-imperative-moon.md` — chctrl 本地 MD 分析启动、PBC 修正、批 1/批 2 分析脚本计划。
- `/Users/roy/.claude/plans/docking-md-chimeric-md-md-wt-gpr-chimer-nifty-falcon.md` — 三层验证 MD 规划与 chctrl → Ch-1/2/4 决策链。
- `/Users/roy/.claude/plans/chimeric-md-execution.md` — chimeric Gpa1 MD 总执行计划；状态需以最新日志校准。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/logs/2026-04-26.md` — chctrl 3/3 完成、Ch-1/2/4 暂停、下一步本地分析。
- `/Users/roy/Documents/drylab/docs/modeling/P0-md-simulation.md` — MD phase 定义、chimeric C1-C5 状态、7 项分析指标。
- `/Users/roy/Documents/drylab/docs/INDEX.md` — 当前优先入口与阻塞项。

## 2. docking-repro：Gpr2/Gpr3 修复后的结果刷新仍阻塞湿实验 Top 推荐

**当前状态**：Gpr2 3D offset WT/Ala/Sat 重跑已完成；Gpr3 方案 F 已完成并通过几何约束，但结论不理想，旧 Top/ratio/IFP 不能直接作为最终湿实验推荐。下一步需要合并/刷新结果，并补充 IFP 更多位点所需的 AF3 预测。

**补充任务（用户 2026-04-27 指定）**：Gpr3 F 已完成但结论不理想，需要补充 IFP 更多位点的 AF3 预测；batch JSON 提交文件已生成：

- `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_01.json`
- `/Users/roy/Documents/drylab/experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/af3_batch_gpr3_f_02.json`

**Plan 指针**：

- `/Users/roy/.claude/plans/gpr3-1-2-cozy-bengio.md` — Gpr3 pose 质量审查、方案 F、全量重跑与后续 ratio/IFP 刷新框架。
- `/Users/roy/.claude/plans/charmmgui-membrane-builder-gpr2-icl-vin-whimsical-ripple.md` — Gpr2 grid/offset 污染核查与重跑决策。
- `/Users/roy/.claude/plans/tidy-yawning-twilight.md` — 比值型双通道 docking 数据分析框架。
- `/Users/roy/.claude/plans/virtual-wobbling-peach.md`、`/Users/roy/.claude/plans/greedy-nibbling-shannon.md` — ProLIF/IFP 通道与盐桥检测修复背景。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/logs/2026-04-23.md` — Gpr2 重跑完成、Gpr3 box/offset/F 方案审查与 PASS 记录。
- `/Users/roy/Documents/drylab/docs/logs/2026-04-27.md` — INDEX 与 P0 docking 状态校准；明确旧 wet-lab handoff 不可直接下发。
- `/Users/roy/Documents/drylab/docs/modeling/P0-molecular-docking.md` — docking-repro 当前 `reanalysis` 状态与使用纪律。
- `/Users/roy/Documents/drylab/experiments/docking-repro/analysis/ratio_channel_report.md` — 历史 ratio 报告；刷新前仅作历史基线。

## 3. 嵌合 Gpa1：AF3 全量筛选完成，当前进入 MD validation

**当前状态**：嵌合 Gpa1 设计与 AF3 全量筛选已完成，Top 3 候选已选；AoGpa2 `TGJ64397.1` 身份核查支持其为 Kuo2024 GPA2 构建对应序列，Gpr2/Gpr3 → AoGpa2 设计暂不回滚。当前可靠性主要等待 chimeric MD 验证。

**Plan 指针**：

- `/Users/roy/.claude/plans/lively-spinning-newt.md` — Chimeric Gpa1 MD 路线规划与文献/技术栈背景。
- `/Users/roy/.claude/plans/dreamy-shimmying-harp.md` — Chimeric MD 前置调研、Gpr2-AoGpa2 偶联缺口与体系选择重评估。
- `/Users/roy/.claude/plans/chimeric-md-execution.md` — Chimeric Gpa1 MD 执行计划。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/logs/True_Gpr2_or_not.md` — AoGpa2 `TGJ64397.1` / GPA2 身份核查。
- `/Users/roy/Documents/drylab/docs/logs/2026-04-26.md` — chimeric MD 当前运行状态。
- `/Users/roy/Documents/drylab/docs/modeling/P3-chimeric-gprotein.md` — 嵌合 Gpa1 方向权威文档，当前 `MD_validation`。
- `/Users/roy/Documents/drylab/experiments/chimeric-gpa1/analysis/ranking_summary.md` — AF3 Top 候选选择结果。

## 4. ODE / 显色级联：并行推进，但关键输入等待 docking 与湿实验方案

**当前状态**：底盘已锁定酵母 STE2 + 嵌合 Gpa1 + 基因组单拷贝整合；ODE 可继续整理模型框架和参数源，但 Top 候选/Kd 输入需等待 docking-repro 刷新。显色级联方案仍 TBD；HP 经济效益模型需求尚未对齐。

**Plan 指针**：

- `/Users/roy/.claude/plans/playful-watching-raccoon.md` — 底盘决策落地、饱和突变审查、MD 补充的项目级转向背景。
- `/Users/roy/.claude/plans/functional-sauteeing-sunrise.md` — docking 教学/交接材料背景；与湿实验沟通材料有关。
- 注：未在 `/Users/roy/.claude/plans` 中确认到专门的 ODE 执行 plan；ODE 当前以项目文档为权威。

**Log / 文档指针**：

- `/Users/roy/Documents/drylab/docs/modeling/P0-signal-pathway-ode.md` — STE2 ODE 模型方向文档。
- `/Users/roy/Documents/drylab/docs/prd/overview-v4.md` — 酵母-STE2 当前项目全貌与显色级联 TBD。
- `/Users/roy/Documents/drylab/docs/decisions/003-chassis-yeast-ste2-integration.md` — 底盘决策权威记录。
- `/Users/roy/Documents/drylab/docs/logs/2026-04-27.md` — 当前 INDEX 校准与待办。
