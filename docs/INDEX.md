# iGEM DryLab 干实验 — 项目索引

## 项目概述

- **一句话**: 构建基于 GPCR 生物传感器的植物寄生线虫田间早期检测系统的干实验（计算建模）模块
- **当前阶段**: 文档体系搭建 + 底盘决策等待中
- **主要卡点**: 底盘选择未确定（等 PI 确认真菌物种和遗传操作工具）
- **目标**: iGEM Wiki freeze 约 2026-09 底
- **详细背景**: [项目全貌](prd/overview.md)

---

## 建模方向状态

| 优先级 | 方向 | 底盘相关 | 状态 | 文档 |
|--------|------|---------|------|------|
| **P0** | 受体-配体分子对接 | 否 | in_progress | [P0-molecular-docking.md](modeling/P0-molecular-docking.md) |
| **P0** | 信号通路 ODE 建模 | **是** | not_started | [P0-signal-pathway-ode.md](modeling/P0-signal-pathway-ode.md) |
| **P1** | 土壤 ascaroside 扩散模型 | 否 | not_started | [P1-soil-diffusion.md](modeling/P1-soil-diffusion.md) |
| **P1** | 标志物→线虫丰度贝叶斯推断 | 否 | not_started | [P1-bayesian-inference.md](modeling/P1-bayesian-inference.md) |
| **P2** | 早期检测经济效益模型 | 否 | not_started | [P2-economic-benefit.md](modeling/P2-economic-benefit.md) |
| **P2** | 化学杀线虫剂剂量-响应 | 否 | not_started | [P2-dose-response.md](modeling/P2-dose-response.md) |
| **P2** | 生物防治 Lotka-Volterra | 仅丝状真菌 | not_started | [P2-biocontrol-lv.md](modeling/P2-biocontrol-lv.md) |
| **P3** | 嵌合 Gpa1 同源性建模 | 仅酵母 | not_started | [P3-chimeric-gprotein.md](modeling/P3-chimeric-gprotein.md) |

---

## 阻塞性待确认事项

- [ ] **[阻塞] PI 真菌物种确认**: 实验室做的"真菌"是哪个物种？→ 直接决定底盘选择（[决策树](prd/chassis-decision.md)）
- [ ] **[阻塞] 遗传操作工具确认**: 转化方法、选择标记、CRISPR 是否已建立？
- [ ] **[阻塞] PI 底盘倾向性**: 酵母 vs 丝状真菌有无明确偏好？
- [ ] **[重要] 转录组数据检索**: GEO/SRA 中 *A. oligospora*/*A. flagrans* ascaroside RNA-seq 数据？
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
| 项目全貌 | §1 信号链路、团队、受体、文献 | [overview.md](prd/overview.md) |
| 干实验总策略 | §2 方向评估、痛点调研、防治决策 | [dry-lab-strategy.md](prd/dry-lab-strategy.md) |
| 底盘决策分析 | §2C-2D 酵母vs真菌、决策树、行动项 | [chassis-decision.md](prd/chassis-decision.md) |
| 学习路线图 | §4+§6 学习资源、硬件、工具 | [roadmap.md](learning/roadmap.md) |

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

- **2026-04-04**: v2 pipeline production 对接完成（exh=200，9 对）；Kuo2024 排名验证 PASS；GprC 绝对值差 ~2 kcal/mol（方法差异）
- **2026-04-04**: docking-repro pipeline 代码完成（ADFR+Orca+两阶段对接）；待在 Windows 安装 ADFR Suite + Orca 后运行
- **2026-04-03**: 文献总结完成 16 篇（3 批并行处理），覆盖核心对接、信号通路、酵母底盘、嵌合 G protein 全链路
- **2026-04-03**: papers/ 目录重组（pdf/ + summaries/），37 个 PDF 全部规范命名；文献矩阵勘误 5 处（作者错误、虚构条目、PDF 错配）
- **2026-04-03**: 文献全面调研完成（6 Tier, 257→47 筛选），产出文献矩阵和搜索日志；发现关键新文献 Mukherjee et al. 2025 PNAS

---

## 待办

- [ ] 问 PI 确认真菌物种、遗传工具、底盘倾向（本周内）
- [ ] 检索 GEO/SRA 转录组数据
- [ ] 与 HP 组沟通经济效益模型需求
- [x] §3.1 数据源验证 + 受体 PDB 下载（完成）
- [x] §3.1 配体 SDF 下载 + 工具环境搭建（完成，conda `docking` 环境已配置）
- [x] 文献 PDF 管理 + 16 篇核心文献总结（完成）
- [ ] §3.1 分子对接 pipeline 编写（下一步）
- [ ] 开始 §3.5c 经济效益模型（收集作物损失函数文献）
- [ ] 第 4 周前确定主线底盘
