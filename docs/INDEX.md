# iGEM DryLab 干实验 — 项目索引

> 最后校准：2026-07-04。本文是项目路由表，不承载详细结果数值；需要结论时请沿链接读取领域文档、日志和原始结果文件。

## 项目概述

- **一句话**: 构建基于 GPCR 生物传感器的植物寄生线虫田间早期检测系统的干实验（计算建模）模块
- **当前阶段**: 底盘已锁定酵母-STE2；docking-repro 已完成刷新交接；旧 Slurm 上 chimeric Gpa1 control/chctrl 组 3 reps MD 已完成，E2 路线已有 chctrl rep1 early-gate 证据和 R1 reduced-chctrl exploratory step6/100 ps short-production 证据；R1 Z-only 方案因 atom-count 降幅过小已降级为证据点而非省算力主路线，候选体系 production 仍暂停；MD 主线转为 R4 coarse-grained/multiscale source gate + full-object throughput baseline planning，R4 首轮方法提取和 GPCR-Galpha 定向追引支持继续 source gate 但尚未找到直接 GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG source；同时推进 mutant GPR MD 前置核查；ODE、reporter 和早期检测经济效益模型并行维护参数/校准需求。
- **主要卡点**: E2 是当前主要可用算力且属于共享服务器，后续 MD 必须降低 A100 占用。R1 reduced `chctrl` 已能完成 step6 和 100 ps short production，但 `120 A` XY / `20 A` water 的 Z-only 缩减只有 `-2.57%` atom-count delta，不足以解决算力问题，且不是 candidate-transfer rule；mutant GPR MD 先从 `Gpr2_R59C` / `Gpr3_R167Y` 做体系大小核查和短程算力测试。docking 构建容量、reporter 实现参数和 HP 本地参数仍待湿实验/HP 确认。详细证据见下方“当前优先入口”和对应领域文档、日志、结果文件。
- **目标**: iGEM Wiki freeze 约 2026-09 底
- **详细背景**: [项目全貌 v4](prd/overview-v4.md)

---

## 建模方向状态

| 优先级 | 方向 | 底盘相关 | 当前状态 | 文档 |
|--------|------|---------|----------|------|
| **P0** | 受体-配体分子对接 | 否 | **refreshed_handoff**：Gpr2 3D offset、Gpr3 方案 F、Gpr3 supplemental docking、266 条 merged ratio、Top 候选 IFP 与湿实验交接均已刷新 | [P0-molecular-docking.md](modeling/P0-molecular-docking.md) |
| **P0** | MD 模拟（突变体稳定性 + 嵌合 Gpa1 验证） | 否/酵母触发 | **compute_triage**：旧 Slurm control/chctrl 3 reps 为历史完成证据，E2 有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据；R1 Z-only 已降级为省算力不足；候选体系 full MD 暂停；当前 chimeric 路线进入 R4 coarse-grained/multiscale source gate，full-object throughput baseline 只作排程/性能配套；mutant GPR 仍需体系大小核查/算力测试 | [P0-md-simulation.md](modeling/P0-md-simulation.md) |
| **P0** | 信号通路 ODE 建模（酵母 STE2） | 已锁定酵母 | in_progress：文献证据、参数状态、湿实验校准需求已整理；reporter 架构已确认；尚无 `src/modeling/ode/` solver、config 或 plots | [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) |
| **P0** | 嵌合 Gpa1 同源性建模 | 酵母触发 | **MD_validation_paused_compute_triage**：42 个 AF3 jobs + Top 3 选择完成；AoGpa2 序列核查通过；旧 Slurm control/chctrl 组 3 reps 完成，E2 有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据；R1 Z-only 不作为候选迁移规则，候选体系验证暂停；下一步只做 R4 source gate / chctrl-first route design | [P3-chimeric-gprotein.md](modeling/P3-chimeric-gprotein.md) |
| **P1** | 土壤 ascaroside 扩散模型 | 否 | not_started | [P1-soil-diffusion.md](modeling/P1-soil-diffusion.md) |
| **P1** | 标志物→线虫丰度贝叶斯推断 | 否 | not_started | [P1-bayesian-inference.md](modeling/P1-bayesian-inference.md) |
| **P2** | 早期检测经济效益模型 | 否 | **framework_mvp_validated_arithmetic + stage3_benchmarks_extracted**：deterministic cost-accounting MVP 已落地并验证公开示例算术；最终 ROI 仍待 HP/湿实验/本地参数校准 | [P2-economic-benefit.md](modeling/P2-economic-benefit.md) |
| **P2** | 化学杀线虫剂剂量-响应 | 否 | not_started | [P2-dose-response.md](modeling/P2-dose-response.md) |
| ~~P2~~ | ~~生物防治 Lotka-Volterra~~ | 仅丝状真菌 | **archived** | [P2-biocontrol-lv.md](modeling/P2-biocontrol-lv.md) |

---

## 阻塞性待确认事项

> 2026-04-11 底盘 4 项阻塞全部解除（PI 确认酵母-STE2 主线，详见 [决策 003](decisions/003-chassis-yeast-ste2-integration.md)）。

- [ ] **[门禁] MD 算力收缩与排程**：按 [决策 005](decisions/005-md-compute-triage-after-chctrl.md)，chimeric 候选体系 full-production 暂停；先调研减少体系大小或更强 restraint 的省算力 protocol。E2 是共享服务器，后续 MD 必须先做资源估算/短程 benchmark，不得长期独占 A100。
- [ ] **[门禁] mutant GPR MD 前测**：从 refreshed docking handoff 的 `Gpr2_R59C`（Channel A）和 `Gpr3_R167Y`（Channel B）开始，先做体系大小核查和算力测试；full production 时长、rep 数和排程需另行确认。
- [ ] **[质量门] 预注册 operational cutoff 来源审查**：所有用于 go/no-go 的项目预注册阈值、技术栈选择、几何定义和数值判据必须补齐 DOI / 标题 / 原文方法段落 / 官方工具文档等 exact pointer；没有 exact pointer 的文献引用暂不承认，统一标记为待查验或项目 operational heuristic。
- [ ] **[待确认] docking 首批构建容量/交接执行**：刷新后的 handoff 已落地，当前首选 `Gpr2_R59C + Gpr3_R167Y`；下一步需湿实验组确认首批构建容量和读出设计。
- [ ] **[待确认] reporter 输出实现参数**：架构已确认（sTF -> GAL 多拷贝放大 -> 色素显色），但具体色素、整合位点、实际拷贝数、输出增益和 time-course 参数仍需通路工程组/湿实验校准。
- [ ] **[重要] HP 组沟通**: 回收经济模型的本地参数：传感器单次成本、部署密度、检测性能、当地 lab 成本/周期、施药/轮作/抗性品种成本、作物价格与农户支付意愿。

---

## 当前优先入口

1. **MD 算力收缩与 mutant GPR 前测** — 决策见 [决策 005](decisions/005-md-compute-triage-after-chctrl.md) 和 [2026-06-26 日志](logs/2026-06-26.md)；方法、phase 和证据边界见 [P0-md-simulation.md](modeling/P0-md-simulation.md)。
2. **chimeric Gpa1 省算力方案调研** — R1 reduced `chctrl` exploratory prototype 已完成 step6 和 100 ps short production，但 Z-only atom-count 降幅不足，已降级为 build/run evidence point；下一 route family 入口为 `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`，R4 首轮方法提取见 `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`，GPCR-Galpha 定向追引见 `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`，下一步资料补充计划见 `codex/docs/plans/chimeric-gpa1-r4-new-source-acquisition-plan.md`。结果入口见 `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/README.md`，Z-only 对照结论见 `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/r1_z_only_public_atom_count_comparison.md`，执行边界见 `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/command_plan.md`。旧 E2/unified rerun 计划保留为历史执行路线和脚本参考，不再作为当前 full-production 启动指令。
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

- **2026-07-04**: R1 reduced `chctrl` exploratory prototype 在 E2 完成 CHARMM-GUI step6 minimization/equilibration 和 100 ps short production，记录 atom count、产出速率、GPU utilization、energy sanity 与 checksum；padding rule 仍为 `exploratory`，不是 candidate-transfer rule。详见 [2026-07-04 日志](logs/2026-07-04.md) 与结果 README。
- **2026-07-04**: 公开 atom-count 对照和本地拓扑计数显示 R1 `120 A` XY / `20 A` water 实例为 Z-only 缩减，atom-count 降幅不足以解决 E2 算力紧缺；该实例保留为 chctrl build/run evidence point，不迁移候选。详见 [2026-07-04 日志](logs/2026-07-04.md) 与 `r1_z_only_public_atom_count_comparison.md`。
- **2026-07-04**: 用户同意 R1-Z 降级后，route-family selection memo 记录下一步改为 R4 coarse-grained/multiscale source gate；full-object throughput baseline 只作配套排程/性能规划，不是体系缩减路线。详见 `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`。
- **2026-07-04**: R4 首轮方法提取完成：GPCR-effector/GPCR-lipid/GPCR ligand CG 文献支持继续 source gate 和设计 object contract，但未找到直接 GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha CG route source，因此不进入 build/E2/candidate。详见 `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`。
- **2026-07-04**: R4 GPCR-Galpha 定向追引补充完成：P0047/P0040 仍为全文/补充方法瓶颈；P0038 找到 final article DOI；Mohanty 2025 和 Cevheroglu 2017 仅保留为 Ste2p-Gpa1p interface context；仍未找到 direct GPCR-Galpha CG route source。详见 `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`。
- **2026-07-05**: Yang2024 SI/tutorial 与 Sahoo2023 方法提取已补齐；R4 下一步转为定向新资料补充，优先寻找 direct GPCR-Galpha / Ste2-Gpa1 CG workflow、interface-preservation practice 与 backmapping/revalidation route。详见 [2026-07-05 日志](logs/2026-07-05.md) 与 `codex/docs/plans/chimeric-gpa1-r4-new-source-acquisition-plan.md`。
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
- [x] 选择 chimeric 下一 route family：R4 coarse-grained/multiscale 进入 source gate；full-object throughput baseline 只作配套排程/性能规划 → `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md`
- [x] 初筛 R4 GPCR / GPCR-effector / Martini coarse-grained source，并写入 literature matrix 的 supports / does not support 说明 → `experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- [x] R4 首轮方法提取：记录 Martini protein structure-bias、GPCR:beta-arrestin close analog、GPCR ligand/lipid 和 AA/CG comparison 支持边界 → `experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- [x] R4 GPCR-Galpha 定向追引：记录 PubMed/Crossref/OpenAlex 查询、rate-limit caveat、P0038 final DOI 与 Mohanty 2025 / Cevheroglu 2017 interface seed 边界 → `experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
- [x] 补 P0047/Yang2024 SI/tutorial 与 P0040/Sahoo2023 full-method extraction，更新 R4 method extraction 与 literature matrix
- [ ] 执行 R4 新资料补充计划：继续查找 direct GPCR-Galpha / Ste2-Gpa1 / chimeric Galpha coarse-grained source，并把结果转成 R4 action lane 或 2026 时间线内的转向决策
- [ ] 若重启 R1，必须先给出非 Z-only 的 source-backed 物理依据和预期 atom-count benefit；在此之前不迁移到 Ch-1/Ch-2/Ch-4
- [ ] 从 `Gpr2_R59C` / `Gpr3_R167Y` 启动 mutant GPR MD 前测：体系大小核查、资源估算、短程 benchmark
- [ ] benchmark 通过后，再单独决定 mutant GPR full-production 时长、rep 数、是否保留 apo/WT 对照和 E2 排程

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
