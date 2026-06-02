# iGEM DryLab 干实验 — 项目索引

> 最后校准：2026-06-02。本文是项目路由表，不承载详细结果数值；需要结论时请沿链接读取领域文档、日志和原始结果文件。

## 项目概述

- **一句话**: 构建基于 GPCR 生物传感器的植物寄生线虫田间早期检测系统的干实验（计算建模）模块
- **当前阶段**: 底盘已锁定酵母-STE2；嵌合 Gpa1 已完成 AF3 全量筛选并进入 MD 验证；当前决策为 E2 primary + Slurm RTX 5090 validated secondary 的统一 clean-start rerun 体系，范围为 chctrl + Ch-1/Ch-2/Ch-4；docking-repro 已完成 Gpr2/Gpr3 修复后的 ratio/IFP/湿实验 handoff 刷新；ODE 继续并行但当前仍是文献证据、参数状态和湿实验校准需求整理，尚未写 solver/config/plots；reporter 输出架构已确认为 sTF -> GAL 多拷贝放大 -> 色素显色。
- **主要卡点**: E2 chimeric rerun 已通过推荐 GROMACS 2025.4 MPI-CUDA 环境安装/preflight、四体系输入同步与 rep1 smoke；chctrl rep1 full production 已在 2026-05-30 02:14 CST checkpoint 后按用户要求中断并完成 same-GPU benchmark，benchmark 显示最佳并发总吞吐低于单 job；rep1 已从 `prod.cpt` 以单 job 恢复运行，并在 2026-06-02 的 194.8 ns isolated snapshot 上通过 full-system early stability gate，当前建议继续同一 `mdrun` 到 500 ns final target；Slurm RTX 5090 read-only preflight 显示 node3/RTX5090 可调度、目标 env 无残留，但用户环境没有 conda/mamba/micromamba，因此 Slurm blocked before same-pin env validation，不进入 smoke/benchmark/production；docking 首批构建容量/湿实验执行安排待确认；reporter 架构已确认但具体色素、整合位点、实际拷贝数和输出层参数仍待湿实验/ODE 校准；HP 经济模型的本地成本/部署/支付意愿参数仍待回收。
- **目标**: iGEM Wiki freeze 约 2026-09 底
- **详细背景**: [项目全貌 v4](prd/overview-v4.md)

---

## 建模方向状态

| 优先级 | 方向 | 底盘相关 | 当前状态 | 文档 |
|--------|------|---------|----------|------|
| **P0** | 受体-配体分子对接 | 否 | **refreshed_handoff**：Gpr2 3D offset、Gpr3 方案 F、Gpr3 supplemental docking、266 条 merged ratio、Top 候选 IFP 与湿实验交接均已刷新 | [P0-molecular-docking.md](modeling/P0-molecular-docking.md) |
| **P0** | MD 模拟（突变体稳定性 + 嵌合 Gpa1 验证） | 否/酵母触发 | **in_progress**：WT holo Phase 3 已完成；chimeric 线转统一环境 clean-start rerun，E2 primary，Slurm RTX 5090 仅在验证后作为 secondary | [P0-md-simulation.md](modeling/P0-md-simulation.md) |
| **P0** | 信号通路 ODE 建模（酵母 STE2） | 已锁定酵母 | in_progress：文献证据、参数状态、湿实验校准需求已整理；reporter 架构已确认；尚无 `src/modeling/ode/` solver、config 或 plots | [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) |
| **P0** | 嵌合 Gpa1 同源性建模 | 酵母触发 | **MD_validation**：42 个 AF3 jobs + Top 3 选择完成；AoGpa2 序列核查通过；MD 验证进行中 | [P3-chimeric-gprotein.md](modeling/P3-chimeric-gprotein.md) |
| **P1** | 土壤 ascaroside 扩散模型 | 否 | not_started | [P1-soil-diffusion.md](modeling/P1-soil-diffusion.md) |
| **P1** | 标志物→线虫丰度贝叶斯推断 | 否 | not_started | [P1-bayesian-inference.md](modeling/P1-bayesian-inference.md) |
| **P2** | 早期检测经济效益模型 | 否 | **framework_mvp_validated_arithmetic + stage3_benchmarks_extracted**：deterministic cost-accounting MVP 已落地并验证公开示例算术；最终 ROI 仍待 HP/湿实验/本地参数校准 | [P2-economic-benefit.md](modeling/P2-economic-benefit.md) |
| **P2** | 化学杀线虫剂剂量-响应 | 否 | not_started | [P2-dose-response.md](modeling/P2-dose-response.md) |
| ~~P2~~ | ~~生物防治 Lotka-Volterra~~ | 仅丝状真菌 | **archived** | [P2-biocontrol-lv.md](modeling/P2-biocontrol-lv.md) |

---

## 阻塞性待确认事项

> 2026-04-11 底盘 4 项阻塞全部解除（PI 确认酵母-STE2 主线，详见 [决策 003](decisions/003-chassis-yeast-ste2-integration.md)）。

- [ ] **[门禁] chimeric MD 统一重跑**：按 `environments/md-production-sites.md`、`environments/e2-md-gromacs.md`、`codex/docs/plans/e2-chimeric-md-restart.md` 和 `codex/docs/plans/chimeric-md-unified-rerun-sites.md`，E2 推荐 GROMACS 环境/preflight、输入同步、rep1 `grompp` + smoke `mdrun` 已完成；chctrl rep1 full production 已在 2026-05-30 02:14 CST checkpoint 后中断并保留 canonical `prod_rep1/prod.cpt`；同卡 2-job benchmark 结果低于单 job，当前不推荐 E2 同卡并行 production；rep1 已在 tmux `e2_chctrl_rep1_resume_20260530` 用 `-cpi prod.cpt -append` 单 job 恢复；2026-06-02 isolated 194.8 ns snapshot 通过 full-system early stability gate（详见 `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/early_gate_report.md`），但不能替代 500 ns final production；Slurm RTX 5090 read-only preflight 通过 scheduler/resource gate，但因无 conda/mamba/micromamba，尚未进入 same-pin env validation、smoke、benchmark 或 production。
- [ ] **[质量门] 预注册 operational cutoff 来源审查**：所有用于 go/no-go 的项目预注册阈值、技术栈选择、几何定义和数值判据必须补齐 DOI / 标题 / 原文方法段落 / 官方工具文档等 exact pointer；没有 exact pointer 的文献引用暂不承认，统一标记为待查验或项目 operational heuristic。
- [ ] **[待确认] docking 首批构建容量/交接执行**：刷新后的 handoff 已落地，当前首选 `Gpr2_R59C + Gpr3_R167Y`；下一步需湿实验组确认首批构建容量和读出设计。
- [ ] **[待确认] reporter 输出实现参数**：架构已确认（sTF -> GAL 多拷贝放大 -> 色素显色），但具体色素、整合位点、实际拷贝数、输出增益和 time-course 参数仍需通路工程组/湿实验校准。
- [ ] **[重要] HP 组沟通**: 回收经济模型的本地参数：传感器单次成本、部署密度、检测性能、当地 lab 成本/周期、施药/轮作/抗性品种成本、作物价格与农户支付意愿。

---

## 当前优先入口

1. **chimeric MD unified rerun** — 站点矩阵见 [md-production-sites.md](../environments/md-production-sites.md)，E2 环境证据见 [e2-md-gromacs.md](../environments/e2-md-gromacs.md)，E2 执行门禁见 [E2 Chimeric MD Restart Plan](../codex/docs/plans/e2-chimeric-md-restart.md)，Slurm secondary gate 见 [Chimeric MD Unified Rerun Sites Plan](../codex/docs/plans/chimeric-md-unified-rerun-sites.md)。
2. **docking-repro 湿实验交接** — 当前权威候选见 [wet-lab-handoff-P0-docking.md](modeling/wet-lab-handoff-P0-docking.md)；证据链从 [2026-05-19 日志](logs/2026-05-19.md) 与 [ratio_channel_report.md](../experiments/docking-repro/analysis/ratio_channel_report.md) 读取。
3. **ODE 并行推进** — 用 [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) 维护通路结构、参数状态和 reporter 输出接口；候选标签可引用新版 docking handoff，但 Kd/calibration 仍等待文献/湿实验校准，尚未进入 solver 实现。
4. **P2 经济模型 HP 参数回收** — 文献/参数入口见 [p2-economic-benefit dossier](papers/p2-economic-benefit/README.md)，问卷见 [P2-economic-benefit-hp-questionnaire.md](modeling/P2-economic-benefit-hp-questionnaire.md)；当前只能做公开示例和 break-even 结构。
5. **湿实验/reporter 输出参数讨论** — 需要结合 [overview-v4.md](prd/overview-v4.md)、[决策 003](decisions/003-chassis-yeast-ste2-integration.md)、[决策 004](decisions/004-reporter-output-architecture.md) 与 ODE 需求。

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

- **当前服务器入口**：新服务器/远程计算任务默认使用 [NKULiulab E2 共享云服务器](ops/nkuliulab-e2-cloud-server.md)；本轮 chimeric MD 允许旧 Slurm 作为已批准的 validated secondary candidate，但必须走 [md-production-sites.md](../environments/md-production-sites.md) 和新的 `slurm_*` gate scripts，不复用旧 Slurm production provenance。
- **GROMACS / MD 操作踩坑索引**：[md-gromacs-operational-pitfalls.md](ops/md-gromacs-operational-pitfalls.md)（服务器中立；新任务仍先读 E2 手册）
- **[已归档] Slurm GPU 集群**：[slurm-md-server.md](ops/archives/slurm-md-server.md)（仅用于追溯旧 MD/Slurm 运行记录；当前 chimeric rerun 的 Slurm secondary route 以 `environments/md-production-sites.md` 和 `experiments/md-simulation/scripts/slurm_*` 为准）
- **[已归档] HBU SGE 集群**：[hbu-sge-cluster.md](ops/archives/hbu-sge-cluster.md)（仅用于追溯旧 HBU SGE 调研/投递记录）
- **[已弃用] Windows SSH 操作指南**：[ssh-windows-compute.md](ops/archives/ssh-windows-compute.md)（Windows 7500F 节点停用；部分 docking 结构文件仍存于该节点，需访问时参考此文档）

## 文献

> **读取策略**: 需要某篇文献时，先查矩阵确认编号，再只读取对应的 `summaries/` 文件。**不要批量读取所有总结，不要直接读 PDF**。

- **文献调研入口**: [文献矩阵](papers/literature-matrix.md)（当前本地记录：58 篇 PDF / 59 篇已总结，详见矩阵头部）
- **P2 经济模型文献/数据源包**: [p2-economic-benefit](papers/p2-economic-benefit/README.md)（Stage 1/2 paper/data matrix、参数表、source evidence；Stage 3 external benchmark extraction）
- **组员使用说明**: [papers/README.md](papers/README.md)
- INDEX 不再维护完整已总结清单，避免与矩阵重复和漂移；请以 `papers/literature-matrix.md` 为文献路由权威。

## 归档

| 文件 | 说明 | 位置 |
|------|------|------|
| PRD v3 原始文件 | 已拆分到 prd/ 各子文档 | [archive/iGEM_DryLab_PRD_v3.md](archive/iGEM_DryLab_PRD_v3.md) |
| Claude Code Skill 指南 | 项目管理参考 | [archive/claude-code-skill-guide.md](archive/claude-code-skill-guide.md) |

---

## 最近进展

- **2026-06-02**: E2 chctrl rep1 在 isolated 194.8 ns snapshot 上通过 full-system early stability gate；当前 production 仍在 `e2_chctrl_rep1_resume_20260530` 继续运行，建议不重启、不迁移 checkpoint，继续同一 `mdrun` 到 500 ns final target。报告见 `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/early_gate/20260602_chctrl_rep1_early_gate/early_gate_report.md`。
- **2026-06-01**: chimeric MD 新增 tiered validation protocol：100-150 ns 是 full-system early stability gate，默认 150 ns；通过后从同一 `prod.cpt` 继续到 500 ns final production，局部口袋/interface-only MD 不作为等价替代。
- **2026-05-30**: chimeric MD chctrl rep1 按 checkpoint gate 在 02:14 CST 正常写入 `prod.cpt` 后中断；benchmark 输出显示最佳 same-GPU 2-job 总吞吐低于单 job（详细数值见 `docs/logs/2026-05-30.md` 和远端 `summary.tsv`）；rep1 已从 canonical `prod_rep1/prod.cpt` 单 job 恢复；同日新增 E2 primary + Slurm RTX 5090 validated secondary 的统一 rerun 站点矩阵和 Slurm 专用 gate scripts。
- **2026-05-25**: reporter 输出架构按用户确认和实验方案附件更新为 `异源 Gpr2/3 -> 嵌合 Gpa1 -> MAPK 级联 -> sTF -> GAL 多拷贝放大 -> 色素显色`；ODE/P2 缺口说明和总览图填充文案已同步到路由文档，未新增 ODE solver 或经济模型代码。
- **2026-05-23**: P2 经济模型长期资料从 `tmp_papers/` 提升到 `docs/papers/p2-economic-benefit/`；Stage 3 外部 benchmark 抽取已进入 dossier，公开示例算术可验证，但最终 ROI 仍待 HP/湿实验/本地参数。

---

## 待办

### ① P0 嵌合 Gpa1 + chimeric MD ⭐⭐⭐（当前最高优先级）
- [x] MUSCLE/ClustalΩ 比对 Gpa1 vs Ao Gpa2 / Af GasA（+ gustducin/Gsα 对照）→ `experiments/chimeric-gpa1/alignment/`
- [x] C 端多档嫁接候选生成与 AF3 全量预测（42 jobs）→ `experiments/chimeric-gpa1/analysis/ranking_summary.md`
- [x] Top 3 嵌合候选选定；AoGpa2 `TGJ64397.1` 身份核查通过 → [True_Gpr2_or_not.md](logs/True_Gpr2_or_not.md)
- [x] production site / environment matrix archived → [md-production-sites.md](../environments/md-production-sites.md), [e2-md-gromacs.md](../environments/e2-md-gromacs.md)
- [x] chctrl selection audit：已核验 PROA/PROB、Gpa1 alpha5/eCT residue mapping、Ste2 interface geometry、fit/reference 路线；selection 定义可用于 caveated interpretation，但阈值来源审查仍未完成 → `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`
- [x] 按推荐 pin 创建/选择 E2 GROMACS 生产环境，并保存新的 preflight + conda snapshot
- [x] 对 chctrl + Ch-1/Ch-2/Ch-4 做输入审计/恢复、MDP/index 检查、rep1 `grompp` 和 smoke `mdrun`
- [x] 新增 Slurm RTX 5090 validated secondary 的环境矩阵、计划和专用 gate scripts；read-only preflight/resource gate 通过，但因无 conda-family package manager 阻塞在 same-pin env validation 前，不进入 smoke/benchmark/production
- [ ] 继续监控 chctrl rep1 single-job production：当前在 E2 tmux `e2_chctrl_rep1_resume_20260530` 从 `/ifs1/User/dengwei/igem/md-simulation/chimeric-ste2-gpa1-wt/gromacs/prod_rep1/prod.cpt` 以 `-cpi prod.cpt -append` 恢复；2026-06-02 194.8 ns early gate 已通过，继续同一 `mdrun` 到 500 ns，不重启、不迁移 checkpoint；完成后同步到 E2 rerun 结果子目录并做 `prod.log` 终止、`prod.cpt/gro/xtc/edr/tpr`、checksum 和 `gmx check` 校验；当前不要做同卡 full-production 并发。

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
