---
direction: P3-chimeric-gprotein
status: in_progress
priority: P0
chassis_dependent: true
last_updated: 2026-04-11
---

# P0: 嵌合 G 蛋白 (Gpa1) 设计的同源性建模

> 来源: PRD v3 §3.6 | iGEM 评审定位: **核心方向**（酵母底盘触发）
>
> **2026-04-11 priority P3 → P0**：底盘决策锁定酵母-STE2 后，嵌合 Gpa1 是异源 Gpr 与内源 Fus3 MAPK 之间唯一的功能桥梁，成败关键。详见 [决策 003](../decisions/003-chassis-yeast-ste2-integration.md) / [chassis-decision §最终决策](../prd/chassis-decision.md#最终决策2026-04-11)。
>
> 文件名仍保留 `P3-chimeric-gprotein.md`（不重命名以避免破坏 git 历史和外部引用），通过 frontmatter `priority: P0` 与本文件头注明实际优先级。

## 解决什么问题

需要将 *A. oligospora* / *A. flagrans* 的 Gα 蛋白 C 端嫁接到酵母 Gpa1（UniProt P08539）上，使得：

1. 嵌合 Gpa1 的 C 端能被异源 Gpr 受体（Gpr2/Gpr3/GprC）正确识别和激活
2. 嵌合 Gpa1 的 N 端（保留酵母原生序列）仍能与酵母内源 Sst2 / Ste18 / Ste4 装配为完整的异源三聚体
3. GTP 结合活性、GAP 调控、Gβγ 释放等关键 G 蛋白功能不被破坏

**核心问题**：C 端替换多少残基？哪个位点边界最优？是否需要中间区域的额外突变补偿？

## 文献模板

| 文献 | 嵌合策略 | 残基数 | 应用 |
|---|---|---|---|
| Hara et al. 2012 | C 端 5 残基替换 | 5 | 多种哺乳动物 GPCR 在酵母重建 |
| Medici et al. 1997 | Gpa1-Gsα 融合 | ~10 | 哺乳动物 β2-AR 信号在酵母重建 |
| Lengger & Jensen 2020（综述） | C 端 5 / 10 / 13 残基比较 | 5/10/13 | 酵母 GPCR biosensor 工程化 |
| Mukherjee et al. 2025 | 真菌 GPCR 在酵母筛选 | 实测 | 提供与本项目最近的体系类比 |
| Fan & Yuan 2024 | GPCR + GAL4 级联放大 | — | 下游 ODE 模型参数源 |

## 方法路线

### Step 1：序列比对 + C 端边界识别

1. 提取 Gpa1（P08539）C 端 30 残基序列作为基线
2. 提取候选 Gα 序列：
   - *A. oligospora* Gα（与 Gpr2/Gpr3 同物种，UniProt 待查）
   - *A. flagrans* Gα（与 GprC 同物种，UniProt 待查）
3. **MUSCLE 多序列比对**：Gpa1 + 候选真菌 Gα + 已知 Hara2012/Medici1997 模板
4. 标记保守 motif 与替换边界候选

### Step 2：三档嫁接方案

参考 Lengger 2020 的实验区间，生成 **3 个嵌合候选**：

| 方案 | 替换 C 端残基数 | 模板依据 |
|---|---|---|
| Chimera-5 | 最末 5 残基 | Hara 2012 最小化方案 |
| Chimera-10 | 最末 10 残基 | Medici 1997 中等方案 |
| Chimera-15 | 最末 15 残基 | Lengger 2020 最大化方案 |

每方案 × 2 真菌物种 = **6 个嵌合 Gpa1 候选序列**。

### Step 3：结构预测

使用 **AlphaFold 3 Server** 预测 4 类复合物：

| 复合物 | 目的 |
|---|---|
| Gpa1-WT 单体 | 基线，确认 AF3 对酵母 Gα 折叠预测可信 |
| 6 个嵌合 Gpa1 单体 | 检查 C 端嫁接是否破坏整体折叠（pLDDT、RMSD vs WT） |
| Gpr2/Gpr3/GprC + 嵌合 Gpa1 复合物（共 18 组合：3 受体 × 6 嵌合） | iPAE / 接触界面分析 → 判断是否能形成生理偶联 |
| Gpa1-WT + Ste2（酵母原生 GPCR）复合物 | 阴性对照（验证 AF3 能复现已知 Gα-Ste2 偶联） |

### Step 4：稳定性 + 偶联评估

| 评估指标 | 工具 | 阈值 |
|---|---|---|
| pLDDT（接触界面） | AF3 输出 | > 70 |
| iPAE（链间预测对齐误差） | AF3 输出 | < 10 Å |
| 接触面残基数 | PyMOL / ChimeraX | > 10 个 |
| 全局 RMSD vs WT 单体 | PyMOL align | < 2 Å（保留 GTPase 域） |
| MD 稳定性（关键候选） | → [P0-md-simulation](P0-md-simulation.md) | RMSD/RMSF + 接触界面持续性 |

### Step 5：与文献模板对比

将干实验产出与 Hara 2012 / Medici 1997 / Fan&Yuan 2024 的实验数据对比，校准 AF3 + iPAE 评分的"通过阈值"。

## 工具栈

| 工具 | 用途 | 安装 |
|---|---|---|
| MUSCLE 5 | 多序列比对 | conda |
| ClustalΩ | 比对交叉验证 | conda |
| AlphaFold 3 Server | 结构预测 | alphafoldserver.com |
| PyMOL | 结构可视化 + RMSD | 教育版 |
| ChimeraX | 接触界面分析 | 免费 |
| BioPython | 序列处理脚本 | conda |
| MD（GROMACS/OpenMM/AMBER） | 稳定性验证 | 待 [P0-md-simulation](P0-md-simulation.md) 调研后选定 |

## 产出定义

- [ ] Gpa1 + 候选真菌 Gα 多序列比对图（含保守 motif 标注）
- [ ] 6 个嵌合 Gpa1 候选序列（FASTA + 注释）
- [ ] 6 个嵌合 Gpa1 + 3 受体 = 18 组复合物 AF3 预测结构（pLDDT/iPAE 表）
- [ ] 推荐嵌合方案（按 iPAE + 接触界面评分排序）
- [ ] MD 稳定性验证（Top 2-3 候选，转 [P0-md-simulation](P0-md-simulation.md)）
- [ ] 与 Hara2012/Medici1997 模板的对比表
- [ ] 嵌合 Gpa1 序列 FASTA + 注释 → 通路工程组（湿实验交接）

## 学习成本与依赖

- **难度**: ★★★☆☆（序列分析 + 结构预测 + 接触界面分析）
- **前置知识**: G 蛋白结构生物学基础、AlphaFold 输出解读、酵母 STE 通路
- **学习资源**: 见 [学习路线图 阶段二](../learning/roadmap.md)（建议补充 G 蛋白章节）
- **预计时间**: 1-2 周完成 6 个候选的 AF3 + 评分；MD 验证另算

## 进展记录

| 日期 | 事件 | 备注 |
|---|---|---|
| 2026-04-11 | priority P3 → P0；方法路线细化（5/10/15 三档 + AF3 评分流程） | 底盘锁定酵母后激活 |

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|---|---|---|---|
| 2026-04-03 | v1.0 | 占位文件，等待底盘决策 | 文档体系搭建 |
| 2026-04-11 | **v2.0** | priority P3 → P0；status not_started → in_progress；新增文献模板表、五步方法路线、AF3 评分阈值、产出定义 | 底盘决策落地（[决策 003](../decisions/003-chassis-yeast-ste2-integration.md)） |

## 与其他方向的依赖关系

- **输出到**:
  - 通路工程组（嵌合 Gpa1 序列设计 → 湿实验构建）
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 嵌合 Gpa1 的偶联效率参数 → ODE 模型输入
  - [P0-md-simulation](P0-md-simulation.md): Top 2-3 嵌合候选 → MD 稳定性验证
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): 结合口袋结构信息（mutant pose 影响嵌合 Gpa1 与受体偶联界面）
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发本方向激活
