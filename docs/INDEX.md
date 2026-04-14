# iGEM DryLab 干实验 — 项目索引

## 项目概述

- **一句话**: 构建基于 GPCR 生物传感器的植物寄生线虫田间早期检测系统的干实验（计算建模）模块
- **当前阶段**: P0 对接 completed；底盘锁定酵母-STE2；**P0 执行顺序 = ① 嵌合 Gpa1（阻塞湿实验）→ ② ODE（并行）→ ③ MD（最后，等 CHARMM-GUI + PI 服务器）**
- **主要卡点**: 显色级联方案 TBD（报告基因/整合位点/GAL4 放大）；嵌合 Gpa1 设计尚未启动（直接阻塞湿实验构建）
- **目标**: iGEM Wiki freeze 约 2026-09 底
- **详细背景**: [项目全貌 v4](prd/overview-v4.md)

---

## 建模方向状态

| 优先级 | 方向 | 底盘相关 | 状态 | 文档 |
|--------|------|---------|------|------|
| **P0** | 受体-配体分子对接 | 否 | completed | [P0-molecular-docking.md](modeling/P0-molecular-docking.md) |
| **P0** | MD 模拟（V138R 盐桥实证 + Top 6 稳定性） | 否 | learning | [P0-md-simulation.md](modeling/P0-md-simulation.md) |
| **P0** | 信号通路 ODE 建模（酵母 STE2） | 已锁定酵母 | in_progress | [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) |
| **P0** | 嵌合 Gpa1 同源性建模 | 酵母触发 | in_progress | [P3-chimeric-gprotein.md](modeling/P3-chimeric-gprotein.md) |
| **P1** | 土壤 ascaroside 扩散模型 | 否 | not_started | [P1-soil-diffusion.md](modeling/P1-soil-diffusion.md) |
| **P1** | 标志物→线虫丰度贝叶斯推断 | 否 | not_started | [P1-bayesian-inference.md](modeling/P1-bayesian-inference.md) |
| **P2** | 早期检测经济效益模型 | 否 | not_started | [P2-economic-benefit.md](modeling/P2-economic-benefit.md) |
| **P2** | 化学杀线虫剂剂量-响应 | 否 | not_started | [P2-dose-response.md](modeling/P2-dose-response.md) |
| ~~P2~~ | ~~生物防治 Lotka-Volterra~~ | 仅丝状真菌 | **archived** | [P2-biocontrol-lv.md](modeling/P2-biocontrol-lv.md) |

---

## 阻塞性待确认事项

> 2026-04-11 底盘 4 项阻塞全部解除（PI 确认酵母-STE2 主线，详见 [决策 003](decisions/003-chassis-yeast-ste2-integration.md)）。

- [ ] **[阻塞] 显色级联方案**：报告基因 / 整合位点 / 拷贝数目标 / 是否 GAL4 放大 → 与通路工程组讨论
- [ ] **[阻塞] 嵌合 Gpa1 设计**：湿实验不知道用哪个嵌合方案，无法开始构建 → **立即启动**
- [ ] **[重要] MD 算力方案**：PI 课题组服务器配置确认（CPU/GPU/RAM）；排在嵌合 Gpa1 之后
- [ ] **[重要] HP 组沟通**: 经济效益模型需要哪些定量论据？

---

## 立即可开始的工作（底盘无关）

1. **§3.1 分子对接** — 受体-配体结合分析
2. **§3.3 土壤扩散模型** — 检测有效距离预测
3. **§3.5c 经济效益模型** — 早期检测的成本-收益分析
4. **学习路线图阶段一** — ODE 建模基础 + 分子对接入门

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

| 文档 | 内容 | 链接 |
|------|------|------|
| P0 分子对接交接（权威源） | Top 6 候选、双通道全谱排名、底盘上下文、计算局限性 | [wet-lab-handoff-P0-docking.md](modeling/wet-lab-handoff-P0-docking.md) |
| P0 分子对接交接（飞书扁平版） | 同上内容，飞书云文档/多维表格粘贴版 | [wet-lab-handoff-P0-docking-feishu.md](modeling/wet-lab-handoff-P0-docking-feishu.md) |

## 运维参考

| 文档 | 内容 | 链接 |
|------|------|------|
| Windows SSH 操作指南 | Mac→Win SSH 正确调用方式、踩坑快查表、bat 模板 | [ssh-windows-compute.md](ops/ssh-windows-compute.md) |

## 文献

> **读取策略**: 需要某篇文献时，先查矩阵确认编号，再只读取对应的 `summaries/` 文件。**不要批量读取所有总结，不要直接读 PDF**。

**文献调研**: [文献矩阵](papers/literature-matrix.md) (47 条目, 6 Tiers) | [搜索日志](papers/search-log.md)

### 已总结文献（17 篇）

| # | 文献 | 主题 | 总结 |
|---|------|------|------|
| ★ | Kuo 2024 | Gpr2/Gpr3 对接 | [总结](papers/summaries/Kuo2024-Gpr2Gpr3-summary.md) |
| ★ | Hu 2024 | GprC 对接 | [总结](papers/summaries/Hu2024-GprC-summary.md) |
| 1 | Hsueh 2013 | NTF 感知 ascaroside（奠基） | [总结](papers/summaries/Hsueh2013-NTF-eavesdrop-pheromones-summary.md) |
| 2 | Chen 2021 | MAPK 通路 | [总结](papers/summaries/Chen2021-MAPK-prey-sensing-summary.md) |
| 3 | Chen 2022 | cAMP-PKA 通路 | [总结](papers/summaries/Chen2022-cAMP-PKA-trap-morphogenesis-summary.md) |
| 11 | Park 2012 | C. elegans ascaroside 受体 | [总结](papers/summaries/Park2012-SRBC-DAF-receptors-summary.md) |
| 14 | Ludewig 2013 | ascaroside 信号综述 | [总结](papers/summaries/Ludewig2013-ascaroside-signaling-review-summary.md) |
| 17 | Choe 2012 | ascaroside 跨物种保守 | [总结](papers/summaries/Choe2012-ascaroside-conserved-summary.md) |
| 18 | Manosalva 2015 | ascr#18 植物免疫 | [总结](papers/summaries/Manosalva2015-ascaroside-plant-defense-summary.md) |
| 19 | Klessig 2019 | ascr#18 广谱抗性 | [总结](papers/summaries/Klessig2019-ascaroside-broad-spectrum-summary.md) |
| 25 | Zhao 2016 | PPN 产 ascaroside 协调媒介甲虫 | [总结](papers/summaries/Zhao2016-ascaroside-PPN-dispersal-summary.md) |
| 26 | Lengger 2020 | 酵母 GPCR 工程综述 | [总结](papers/summaries/Lengger2020-yeast-GPCR-engineering-summary.md) |
| 27 | Mukherjee 2025 | 酵母底盘筛选真菌 GPCR | [总结](papers/summaries/Mukherjee2025-yeast-mating-fungal-GPCR-summary.md) |
| 31 | Hara 2012 | 嵌合 Gpa1 C-末端设计 | [总结](papers/summaries/Hara2012-chimeric-Gpa1-yeast-summary.md) |
| 32 | Medici 1997 | 嵌合 Gpa1-Gsα 融合 | [总结](papers/summaries/Medici1997-chimeric-Gpa1-Gs-summary.md) |
| 33 | Miettinen 2022 | 酵母 cannabinoid biosensor | [总结](papers/summaries/Miettinen2022-GPCR-yeast-cannabinoid-summary.md) |
| 30 | Ladds 2005 | 酵母 GPCR 异源表达综述 | 待总结 |

## 归档

| 文件 | 说明 | 位置 |
|------|------|------|
| PRD v3 原始文件 | 已拆分到 prd/ 各子文档 | [archive/iGEM_DryLab_PRD_v3.md](archive/iGEM_DryLab_PRD_v3.md) |
| Claude Code Skill 指南 | 项目管理参考 | [archive/claude-code-skill-guide.md](archive/claude-code-skill-guide.md) |

---

## 最近进展

- **2026-04-12**: ① MD 技术栈 7 维度调研全部完成（生产栈 GROMACS+CHARMM36m+CGenFF+CHARMM-GUI+POPC）② 体系 pre-register 8 holo 锁定（修正 7→8：2 WT + Top 6）③ **P0 执行顺序重排：嵌合 Gpa1（阻塞湿实验）→ ODE（并行）→ MD（最后）**——MD 是"锦上添花"不是前置依赖
- **2026-04-11**: ① 双通道全谱排名（122 条）② Top 6 确定 ③ V138R 盐桥假说待 MD 实证 ④ **底盘 = 酵母-STE2，P3→P0**
- **2026-04-10**: GprC×14 + Gpr2×10 alanine scan；双通道分类 v1
- **2026-04-09**: Gpr3 IFP alanine scan；BW 映射修正
- **2026-04-08**: WT 单阶段 GprC_ascr18 复现 Hu2024（Δ=0.05）

---

## 待办

### ① P0 嵌合 Gpa1 ⭐⭐⭐（立即启动，阻塞湿实验）
- [x] MUSCLE 比对 Gpa1 vs Ao Gpa2 / Af GasA（+ gustducin/Gsα 对照）→ `experiments/chimeric-gpa1/alignment/`
- [x] C 端 5/10/15 残基三档嫁接方案 + 6 个候选序列 → `experiments/chimeric-gpa1/chimeras/`
- [ ] AlphaFold 3 预测嵌合复合物（18 组合 + WT 对照）
- [ ] iPAE / 接触界面评分 → 推荐方案 → 湿实验交接
- [ ] MD 稳定性验证（Top 2-3 候选，排在 MD 生产期间）

### ② P0 信号通路 ODE（与 ① 并行）
- [ ] 完整酵母 STE2 ODE 模型（参数源 Shaw2019/Fan&Yuan2024/Ladds2005）
- [ ] 1/2/4 copy 拷贝数敏感性分析
- [ ] 与 P0-docking 联动：Kd 参数从双通道排名获取

### ③ P0 MD 模拟（排在 ① 之后，等 CHARMM-GUI + PI 服务器）
- [x] 技术栈调研 7 维度（GROMACS + CHARMM36m + CGenFF + CHARMM-GUI）
- [x] 体系 pre-register（8 holo 锁定）
- [~] CHARMM-GUI 学术账号（已提交注册）
- [ ] ascaroside ParamChem penalty 扫描（CHARMM-GUI 通过后立即做）
- [ ] V138R + ascr#18 体系 MD（盐桥实证）
- [ ] F170E pose drift 分析
- [ ] Top 6 RMSD/RMSF 汇总

### P0 分子对接（计算完成，进入输出阶段）
- [x] WT 单阶段；[x] Alanine scan；[x] 双通道全谱排名（122 条）；[x] Top 6 IFP
- [ ] **Wiki 写作** + **湿实验交接**（[wet-lab-handoff-P0-docking.md](modeling/wet-lab-handoff-P0-docking.md)）

### 其他待启动
- [ ] 显色级联方案讨论（与通路工程组）
- [ ] 与 HP 组沟通经济效益模型需求
