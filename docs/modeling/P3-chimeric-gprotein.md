---
direction: P3-chimeric-gprotein
status: in_progress
priority: P0
chassis_dependent: true
last_updated: 2026-04-13
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
| Conklin et al. 1993 | C 端 3 aa 替换切换 Gαq→Gαi 特异性 | 3–5 | **奠基性**：最小替换单元 + β-turn 结构 |
| Brown et al. 2000 | 10 种嵌合 Gpa1，C 端 5 aa 替换 | 5 | 酵母中系统比较，Gαi/o 最佳 |
| Hara et al. 2012 | C 端 4/31–37/44 aa 替换 gustducin 序列 | 4–37 | 酵母中 37 aa ✓ / 44 aa ✗ 边界 |
| Ueda et al. 2003 | G16/gust 5/11/23/37/44 aa 长度滴定 | 37–44 | **唯一系统长度对比**：仅 37+ aa 功能化 |
| Medici et al. 1997 | Ste2-Gpa1/Gsα 共价融合 | ~108 | 融合绕过 C 端识别需求 |
| Velazhahan et al. 2021 | Ste2 + mini-Gpa1 cryo-EM (PDB 7AD3) | — | AF3 基准：首个 Class D GPCR 实验结构 |
| Lengger & Jensen 2020（综述） | 综述 C 端 5 aa 作为标准替换 | 5 (综述) | 酵母 GPCR biosensor 工程化 |
| Mukherjee et al. 2025 | 真菌 GPCR 在酵母筛选 | 实测 | 提供与本项目最近的体系类比 |
| Fan & Yuan 2024 | GPCR + GAL4 级联放大 | — | 下游 ODE 模型参数源 |

## 方法路线

### Step 1：序列比对 + C 端边界识别

1. 提取 Gpa1（P08539）C 端 30 残基序列作为基线
2. 提取候选 Gα 序列：
   - *A. oligospora* **Gpa2**（NCBI TGJ64397.1, Class III Gα, 与 Gpr2/Gpr3 偶联, cAMP-PKA 通路; Kuo 2024 + Chen 2022）
   - *A. flagrans* **GasA**（UniProt A0A436ZRX2, Group I Gα, 与 GprC 偶联, MAPK 通路; Hu 2024）
3. **MUSCLE 多序列比对**：Gpa1 + 候选真菌 Gα + 已知 Hara2012/Medici1997 模板
4. 标记保守 motif 与替换边界候选

### Step 2：三档嫁接方案

参考文献中不同长度的实验结果，生成 **3 个嵌合候选**：

| 方案 | 替换 C 端残基数 | 模板依据 |
|---|---|---|
| Chimera-5 | 最末 5 残基 | Conklin1993 (3 aa 最小) + Brown2000 (5 aa 系统验证) |
| Chimera-10 | 最末 10 残基 | 项目设计：介于 5 aa 与 α5 helix 全长之间的中间档 |
| Chimera-15 | 最末 15 残基 | 项目设计：覆盖 α5 helix 更多区域，但仍低于 Ueda2003 的 23→37 aa 功能阈值 |
| Chimera-25 | 最末 25 残基 | 覆盖完整 α5 helix + eCT；测试 α5 完整替换是否足够（Ueda2003 gust23 失败，C25 略长） |
| Chimera-37 | 最末 37 残基 | β6 + α5 + eCT；匹配 Ueda2003/Hara2012 双重验证的功能阈值（≥37 aa） |

> **文献定位**: 5 aa 在多个系统中验证有效（Conklin1993, Brown2000, Hara2012）。10/15 aa 在已有文献中**无直接先例**——Ueda2003 的长度滴定跳跃为 5→11→23→37 aa，项目 C10/C15 填补了 5–23 aa 区间的空白。Hara2012 和 Ueda2003 均显示 37 aa 是功能化下限（含 β6 sheet），而 23 aa（仅 α5 + eCT）在 Ueda2003 中失败。C25/C37 于 2026-04-13 追加，动因见 [ranking_summary.md §4](../../experiments/chimeric-gpa1/analysis/ranking_summary.md#4-文献支撑解读)。

每方案 × 2 真菌物种 = **10 个嵌合 Gpa1 候选序列**。

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

- [x] Gpa1 + 候选真菌 Gα 多序列比对图（含保守 motif 标注）→ `experiments/chimeric-gpa1/alignment/`
- [x] 10 个嵌合 Gpa1 候选序列（FASTA + 注释）→ `experiments/chimeric-gpa1/chimeras/`（C5/C10/C15 + C25/C37 × 2 供体）
- [x] Batch 1（C5/C10/C15）: 26 jobs AF3 预测完成
- [x] Batch 2（C25/C37）: 16 jobs AF3 预测完成，合并 Batch 1+2 排名 → `experiments/chimeric-gpa1/analysis/ranking_summary.md`
- [x] 全量分析（42 jobs）：GprC×AfGasA 唯一 cognate 特异性配对 (Δ=+0.088)；β6 假设未被支持；Top 3 候选已选定
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
| 2026-04-12 | Phase 0 完成：Gα 偶联关系确认 + 5 条源序列获取 + 实验目录建立 | Gpr2/3→Gpa2(cAMP), GprC→GasA(MAPK) |
| 2026-04-12 | Phase 1+2 完成：MUSCLE+ClustalΩ 比对（C 端一致）+ 6 个嵌合候选生成 + WT 对照 | conda env chimeric; 边界分析→boundary_analysis.md |
| 2026-04-13 | Phase 3+4 完成：AF3 26 jobs 全部预测完成 + parse_af3_results.py 解析 + ranking_summary.md 生成 | cognate avg ipTM=0.41 ≈ cross=0.42，嫁接特异性未体现 |
| 2026-04-13 | 文献修正：Lengger2020 引用纠错（无 5/10/13 比较），新增 Conklin1993/Ueda2003/Velazhahan2021 至文献模板 | Web search 发现 PDB 7AD3 + Ueda 长度滴定 |
| 2026-04-13 | C25/C37 追加设计：generate_chimeras.py 扩展为 5 档，10 个嵌合 FASTA 生成，batch2.json（16 jobs）就绪 | Ueda2003 37 aa 功能阈值 + Batch 1 失败 |
| 2026-04-13 | Pipeline 清理：删除 6 个冗余脚本/manifest，parse_af3_results.py 改为 discover_jobs() 自动扫描 | 简化维护 |
| 2026-04-14 | Batch 2 完成：42 jobs 全量解析 + 逐受体分析 + β6 假设验证 | GprC cognate Δ=+0.088；β6 未按预期生效；Top 3 候选选定 |
| 2026-04-14 | Bug 修复：parse_af3_results.py 3 处 bug (chains→chimera, is_cognate 作用域, Ste2 路径) + downloads/ 命名统一 | Ste2 folder 重命名 → ste2_gpa1_wt_complex |

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|---|---|---|---|
| 2026-04-03 | v1.0 | 占位文件，等待底盘决策 | 文档体系搭建 |
| 2026-04-11 | **v2.0** | priority P3 → P0；status not_started → in_progress；新增文献模板表、五步方法路线、AF3 评分阈值、产出定义 | 底盘决策落地（[决策 003](../decisions/003-chassis-yeast-ste2-integration.md)） |
| 2026-04-12 | **v2.1** | Step 1 Gα 序列已确定：Ao Gpa2 (TGJ64397) + Af GasA (A0A436ZRX2)；偶联关系文献锁定；实验目录 `experiments/chimeric-gpa1/` 建立 | Phase 0 序列获取完成 |
| 2026-04-13 | **v3.0** | 文献模板重写：修正 Lengger2020 错误引用（无 5/10/13 比较），新增 Conklin1993/Ueda2003/Velazhahan2021；Step 2 三档方案归因修正；AF3 Phase 3+4 完成 | AF3 结果解读 + 文献调研 |
| 2026-04-13 | **v3.1** | Step 2 扩展为五档（+C25/C37）；产出定义更新（10 候选 + Batch 1/2 分期）；进展记录补 C25/C37 条目 | Batch 1 cognate≈cross + Ueda2003 长度滴定驱动 |
| 2026-04-14 | **v4.0** | Batch 2 完成 + 42 jobs 全量分析；产出定义更新（全量分析 + Top 3）；§4 逐受体分析 + β6 假设验证写入 ranking_summary.md | Batch 2 AF3 结果到位 |

## 与其他方向的依赖关系

- **输出到**:
  - 通路工程组（嵌合 Gpa1 序列设计 → 湿实验构建）
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md): 嵌合 Gpa1 的偶联效率参数 → ODE 模型输入
  - [P0-md-simulation](P0-md-simulation.md): Top 2-3 嵌合候选 → MD 稳定性验证
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): 结合口袋结构信息（mutant pose 影响嵌合 Gpa1 与受体偶联界面）
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发本方向激活
