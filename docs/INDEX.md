# iGEM DryLab 干实验 — 项目索引

> 最后校准：2026-05-20。本文是项目路由表，不承载详细结果数值；需要结论时请沿链接读取领域文档、日志和原始结果文件。

## 项目概述

- **一句话**: 构建基于 GPCR 生物传感器的植物寄生线虫田间早期检测系统的干实验（计算建模）模块
- **当前阶段**: 底盘已锁定酵母-STE2；嵌合 Gpa1 已完成 AF3 全量筛选并进入 MD 验证；chctrl 阳性对照 3/3 production MD 已完成，Ch-1/2/4 暂停等待 chctrl 本地分析结论；docking-repro 已完成 Gpr2/Gpr3 修复后的 ratio/IFP/湿实验 handoff 刷新；ODE 继续并行但 Kd/calibration 仍等待单独文献审查。
- **主要卡点**: chctrl MD 本地分析尚未产出；docking 首批构建容量/湿实验执行安排待确认；显色级联方案 TBD（报告基因/整合位点/GAL4 放大）；HP 经济效益模型需求未对齐。
- **目标**: iGEM Wiki freeze 约 2026-09 底
- **详细背景**: [项目全貌 v4](prd/overview-v4.md)

---

## 建模方向状态

| 优先级 | 方向 | 底盘相关 | 当前状态 | 文档 |
|--------|------|---------|----------|------|
| **P0** | 受体-配体分子对接 | 否 | **refreshed_handoff**：Gpr2 3D offset、Gpr3 方案 F、Gpr3 supplemental docking、266 条 merged ratio、Top 候选 IFP 与湿实验交接均已刷新 | [P0-molecular-docking.md](modeling/P0-molecular-docking.md) |
| **P0** | MD 模拟（突变体稳定性 + 嵌合 Gpa1 验证） | 否/酵母触发 | **in_progress**：WT holo Phase 3 已完成；chimeric chctrl 3/3 production 完成，当前转本地分析；Ch-1/2/4 暂停 | [P0-md-simulation.md](modeling/P0-md-simulation.md) |
| **P0** | 信号通路 ODE 建模（酵母 STE2） | 已锁定酵母 | in_progress：模型框架与参数源继续整理；Top 候选标签已刷新，Kd/calibration 仍等待单独文献审查 | [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) |
| **P0** | 嵌合 Gpa1 同源性建模 | 酵母触发 | **MD_validation**：42 个 AF3 jobs + Top 3 选择完成；AoGpa2 序列核查通过；MD 验证进行中 | [P3-chimeric-gprotein.md](modeling/P3-chimeric-gprotein.md) |
| **P1** | 土壤 ascaroside 扩散模型 | 否 | not_started | [P1-soil-diffusion.md](modeling/P1-soil-diffusion.md) |
| **P1** | 标志物→线虫丰度贝叶斯推断 | 否 | not_started | [P1-bayesian-inference.md](modeling/P1-bayesian-inference.md) |
| **P2** | 早期检测经济效益模型 | 否 | not_started | [P2-economic-benefit.md](modeling/P2-economic-benefit.md) |
| **P2** | 化学杀线虫剂剂量-响应 | 否 | not_started | [P2-dose-response.md](modeling/P2-dose-response.md) |
| ~~P2~~ | ~~生物防治 Lotka-Volterra~~ | 仅丝状真菌 | **archived** | [P2-biocontrol-lv.md](modeling/P2-biocontrol-lv.md) |

---

## 阻塞性待确认事项

> 2026-04-11 底盘 4 项阻塞全部解除（PI 确认酵母-STE2 主线，详见 [决策 003](decisions/003-chassis-yeast-ste2-integration.md)）。

- [ ] **[阻塞] chctrl MD 阳性对照分析**：下载/处理 chctrl 3 条轨迹，跑 RMSD、α5 iRMSD、H-bond、COM distance、RMSF 等第一批指标；结论决定 Ch-1/2/4 是否重启。
- [ ] **[质量门] 预注册 operational cutoff 来源审查**：所有用于 go/no-go 的项目预注册阈值、技术栈选择、几何定义和数值判据必须补齐 DOI / 标题 / 原文方法段落 / 官方工具文档等 exact pointer；没有 exact pointer 的文献引用暂不承认，统一标记为待查验或项目 operational heuristic。
- [ ] **[待确认] docking 首批构建容量/交接执行**：刷新后的 handoff 已落地，当前首选 `Gpr2_R59C + Gpr3_R167Y`；下一步需湿实验组确认首批构建容量和读出设计。
- [ ] **[阻塞] 显色级联方案**：报告基因 / 整合位点 / 拷贝数目标 / 是否 GAL4 放大 → 与通路工程组讨论。
- [ ] **[重要] HP 组沟通**: 经济效益模型需要哪些定量论据？

---

## 当前优先入口

1. **chimeric MD 分析** — 从 [2026-04-26 日志](logs/2026-04-26.md) 接续 chctrl 本地分析与 Ch-1/2/4 重启决策。
2. **docking-repro 湿实验交接** — 当前权威候选见 [wet-lab-handoff-P0-docking.md](modeling/wet-lab-handoff-P0-docking.md)；证据链从 [2026-05-19 日志](logs/2026-05-19.md) 与 [ratio_channel_report.md](../experiments/docking-repro/analysis/ratio_channel_report.md) 读取。
3. **ODE 并行推进** — 用 [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) 维护通路结构；候选标签可引用新版 docking handoff，但 Kd/calibration 仍等待单独文献审查。
4. **湿实验/显色级联讨论** — 需要结合 [overview-v4.md](prd/overview-v4.md)、[决策 003](decisions/003-chassis-yeast-ste2-integration.md) 与 ODE 需求。

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

- **Slurm GPU 集群**（当前）：[slurm-md-server.md](ops/slurm-md-server.md)
- **[已弃用] Windows SSH 操作指南**：[ssh-windows-compute.md](ops/archives/ssh-windows-compute.md)（Windows 7500F 节点停用；部分 docking 结构文件仍存于该节点，需访问时参考此文档）

## 文献

> **读取策略**: 需要某篇文献时，先查矩阵确认编号，再只读取对应的 `summaries/` 文件。**不要批量读取所有总结，不要直接读 PDF**。

- **文献调研入口**: [文献矩阵](papers/literature-matrix.md)（当前本地记录：58 篇 PDF / 59 篇已总结，详见矩阵头部）
- **组员使用说明**: [papers/README.md](papers/README.md)
- INDEX 不再维护完整已总结清单，避免与矩阵重复和漂移；请以 `papers/literature-matrix.md` 为文献路由权威。

## 归档

| 文件 | 说明 | 位置 |
|------|------|------|
| PRD v3 原始文件 | 已拆分到 prd/ 各子文档 | [archive/iGEM_DryLab_PRD_v3.md](archive/iGEM_DryLab_PRD_v3.md) |
| Claude Code Skill 指南 | 项目管理参考 | [archive/claude-code-skill-guide.md](archive/claude-code-skill-guide.md) |

---

## 最近进展

- **2026-05-20**: docking-repro full refresh 完成 Phase 1-7：266 条 merged ratio、8 个 Top 候选 IFP、湿实验 handoff 刷新；当前首选 `Gpr2_R59C + Gpr3_R167Y`。
- **2026-04-27**: `True_Gpr2_or_not.md` 核查 Kuo2024 GPA2/GPA3 标签疑问：当前 `TGJ64397.1` 与 GPA2 primers 匹配，Gpr2/Gpr3→AoGpa2 设计暂不回滚；Ch-1/2/4 MD 不因该问题重跑。
- **2026-04-26**: Slurm 队列清空；chctrl Phase C4 production MD 3/3 完成；Ch-1 rep1 中断在约 28 ns 且有 cpt，Ch-2/Ch-4 仅完成 step6.6；决策为先分析 chctrl，再决定是否重启 Ch-1/2/4。
- **2026-04-23/24**: Gpr2 3D offset Ala/Sat 重跑完成并刷新旧 ratio；随后 Gpr3 pose 审查发现旧 groove 污染，方案 F（ECL2 manual box=20 Å）几何 PASS；这些产物已纳入 2026-05-20 full refresh。
- **2026-04-22**: Slurm 新增 QOS=1 导致排队不可接受；取消冲突/排队任务，保留 chctrl rep3；后续 docking/Ch-1 迁移策略调整。

---

## 待办

### ① P0 嵌合 Gpa1 + chimeric MD ⭐⭐⭐（当前最高优先级）
- [x] MUSCLE/ClustalΩ 比对 Gpa1 vs Ao Gpa2 / Af GasA（+ gustducin/Gsα 对照）→ `experiments/chimeric-gpa1/alignment/`
- [x] C 端多档嫁接候选生成与 AF3 全量预测（42 jobs）→ `experiments/chimeric-gpa1/analysis/ranking_summary.md`
- [x] Top 3 嵌合候选选定；AoGpa2 `TGJ64397.1` 身份核查通过 → [True_Gpr2_or_not.md](logs/True_Gpr2_or_not.md)
- [ ] chctrl 3 条 production MD 轨迹本地下载、PBC 修正、第一批指标分析 → [2026-04-26 日志](logs/2026-04-26.md)
- [x] chctrl selection audit：已核验 PROA/PROB、Gpa1 alpha5/eCT residue mapping、Ste2 interface geometry、fit/reference 路线；selection 定义可用于 caveated interpretation，但阈值来源审查仍未完成 → `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/selection_audit_report.md`
- [ ] 审阅 chctrl selection audit 报告后，决定是否接受 chctrl 为“usable with alpha5 caveat”并进入 Ch-1/2/4 续跑/重提决策
- [ ] 根据 chctrl 阳性对照结果决定 Ch-1/2/4 是否续跑/重提，再更新湿实验嵌合方案置信度

### ② P0 docking-repro 结果刷新 ⭐⭐⭐
- [x] Gpr2 3D offset WT/Ala/Sat 重跑完成；旧 Gpr2 污染结果不再作为权威
- [x] Gpr3 方案 F pose 几何 PASS；Gpr3 F Ala/Sat 产物已生成
- [x] 合并 Gpr3 F Ala/Sat/supplemental 到全量 mutagenesis JSON，重跑 `ratio_channel_analysis.py`
- [x] 对新 Gpr2/Gpr3 F Top 候选重跑/刷新 ProLIF IFP 与机制解释
- [x] 刷新 `wet-lab-handoff-P0-docking*.md`；旧 Top 配对已替换
- [ ] 视 PI/湿实验沟通需要补 PyMOL PNG/PSE 渲染交付物

### ③ P0 信号通路 ODE（并行）
- [ ] 完整酵母 STE2 ODE 模型（参数源 Shaw2019/Fan&Yuan2024/Ladds2005 等）
- [ ] 1/2/4 copy 拷贝数敏感性分析
- [ ] 与 docking 联动：候选标签可引用新版 handoff；Kd/calibration 需等待单独文献审查

### ④ 其他待启动
- [ ] 显色级联方案讨论（报告基因 / 整合位点 / 拷贝数 / GAL4 放大）
- [ ] 与 HP 组沟通经济效益模型需求
- [ ] 土壤扩散、贝叶斯推断、经济效益、剂量-响应等 P1/P2 方向按 Wiki 叙事需要启动
