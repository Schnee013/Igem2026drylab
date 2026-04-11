---
direction: P0-md-simulation
status: learning
priority: P0
chassis_dependent: false
last_updated: 2026-04-11
---

# P0: MD 模拟（V138R 盐桥实证 + Top 6 稳定性 + 嵌合 Gpa1 验证）

> 来源: 2026-04-11 新建 | iGEM 评审定位: 直接支撑湿实验设计的机制实证
>
> **新方向背景**：[P0-molecular-docking](P0-molecular-docking.md) 已完成 122 突变体对接 + Top 6 IFP 验证，但发现两个**静态对接 + IFP 无法回答的机制问题**：
>
> 1. **V138R 盐桥假说未实证**：mutant IFP 显示 ARG138 对 ascr18 接触 9 次（vs ascr3 仅 2 次）但**全部为 VdWContact**；本轮 ProLIF 未开启 Ionic 通道，盐桥需 MD 时间序列实证。
> 2. **F170E 反直觉**：GLU170 与 ascr3 接触反而比 ascr18 多，但整体 ΔG(ascr3) 上升 —— 静态 pose 无法解释，需 MD 检查 pose drift。
>
> 同时 [P3-chimeric-gprotein](P3-chimeric-gprotein.md)（已升 P0）的嵌合 Gpa1 设计也需要 MD 稳定性验证。
>
> **本方向的边界**：是 docking 与嵌合 Gpa1 的**实证补充**，**不再做新对接**（用户决策：算力全部投入 MD）。

## 解决什么问题

对接 + IFP 给出**静态 pose 与平均接触频率**，无法回答：

1. **相互作用类型**：ARG138-羧基 9 次 VdWContact 是否为伪盐桥（短程范德华接触掩盖了真正的离子键）？
2. **pose 稳定性**：Top 6 mutant 的 pose 在 ns 时间尺度是否保持？还是只是 Vina 全局搜索找到的局部最小值？
3. **动态相互作用持续性**：氢键 / 盐桥 / 疏水 / π-π 在时间序列中的占比？
4. **入口路径与构象选择**：F170E 的 ECL2 取向是否使 ascr3 进入路径偏移？
5. **嵌合 Gpa1 + Gpr 复合物界面稳定性**：AF3 一次性预测的 iPAE 评分是否在 MD 中保持？

## 第一优先级：技术栈调研（不预设软件）

> 本方向**首要任务**是系统性文献调研。**禁止在调研前预设软件、力场、时长**——这是用户在 plan 中明确要求的纪律：技术栈必须由近 3 年 GPCR-配体 MD 模拟主流实践 + 硬件兼容性双重约束选定。

### 调研清单（写入 TODO）

| 维度 | 候选 | 调研问题 |
|---|---|---|
| **MD 软件** | GROMACS / OpenMM / AMBER / NAMD / Desmond | GPCR 膜蛋白使用频率？AMD ROCm/HIP 后端成熟度？教程可用性？iGEM 团队历史使用情况？ |
| **力场** | CHARMM36m / Amber ff19SB / OPLS-AA(GROMOS) | GPCR + 小分子配体体系适用性？哪种与所选 MD 软件搭配最佳？是否支持 ascaroside 这类糖脂？ |
| **膜体系构建** | CHARMM-GUI Membrane Builder / PACKMOL-Memgen / Membed (GROMACS) | 接收 PDB → 出可直接 MD 的体系的工作流？膜组成（POPC vs POPC:POPE 混合）选取依据？ |
| **配体参数化** | GAFF2 / CGenFF / OpenFF | ascarylose 糖骨架 + 长侧链脂肪酸的拓扑生成？哪个工具对环糖支持最好？ |
| **时间尺度惯例** | 50 / 100 / 200 / 500 ns | GPCR + 配体稳定性验证近 3 年文献中的典型时长？复制次数（3× / 5×）？ |
| **盐桥/HBond 分析** | MDAnalysis / mdtraj / PLUMED / VMD | 时间序列盐桥占比的脚本可用性？接触持续时间（contact lifetime）算法？ |
| **自由能 / MM-PBSA** | gmx_MMPBSA / pymbar / alchemlyb | 入门门槛？iGEM 时间窗口是否够？是否能直接给出"WT vs V138R 自由能差"？ |

### 调研产出

完成调研后，**回填到本文档**的"工具栈与参数选型"小节，附**每个选择的文献依据**（年份 + DOI / arXiv / 预印本链接）。**禁止凭印象写入决定**。

### 调研后的技术栈选型（待回填）

> 调研未完成前留空。完成后此处填入：软件 + 力场 + 膜体系工具 + 配体参数化工具 + 时长 + 复制数 + 分析工具，每项一条文献依据。

## 待回答的科学问题

### 问题 1：V138R 盐桥实证（最高优先级）⭐⭐⭐

**体系**：Gpr3 V138R + ascr#18 单复合物（POPC 膜 + 水盒 + 离子）。WT Gpr3 + ascr#18 作为对照。

**核心测量**：
- ARG138 胍基 Nε / NH₁ / NH₂ 三个氢原子与 ascr18 末端羧基 O 的**距离时间序列**
- 盐桥占比（fraction of frames with d < 4 Å 且角度满足）
- ARG138 - ascr18 羧基 **接触持续时间分布**（contact lifetime histogram）
- 与 WT 对照：V138 → ascr18 的接触类型分布（应主要为疏水）

**判定**：
- 盐桥占比 > 30% → 实证盐桥假说，写入 wiki + handoff
- 占比 5-30% → 弱盐桥 / 间歇盐桥，需要更长时间尺度或多复制验证
- 占比 < 5% → 推翻盐桥假说，回到"Arg 胍基特异范德华效应"解释

### 问题 2：F170E pose drift 与 ECL2 取向

**体系**：Gpr3 F170E + ascr#18 vs Gpr3 F170E + ascr#3（双配体对照）。

**核心测量**：
- ascr3 vs ascr18 在 F170E 突变体中的 **pose RMSD 时间序列**（相对 t=0 docking pose）
- GLU170 侧链 χ1 / χ2 角度时间序列
- ascr3 入口路径分析（如有 enhanced sampling 工具）

**判定**：能否解释"GLU170 与 ascr3 接触更多但 ΔG(ascr3) 反而上升"。

### 问题 3：Top 6 mutant binding pose 稳定性

**体系**：Top 6 突变体（Gpr2 M327A/M327D/R59F + Gpr3 V138R/F170E/I141A）+ 各自最佳配体的复合物，WT 对照。

**核心测量**：
- 配体 RMSD（相对初始 docking pose）
- 受体 backbone RMSF（特别是结合口袋残基）
- 关键 HBond 时间序列

**判定**：哪些 Top 6 候选的 docking pose 在 MD 中稳定（→ 湿实验高置信度）；哪些发生大幅 drift（→ 降低优先级或重新解读）。

### 问题 4：嵌合 Gpa1 + Gpr 复合物稳定性（与 [P3-chimeric-gprotein](P3-chimeric-gprotein.md) 联动）

**体系**：P3 输出的 Top 2-3 嵌合 Gpa1 + Gpr 复合物候选。

**核心测量**：
- 链间界面 RMSD
- 接触界面残基持续性
- 嵌合 C 端区域的 RMSF

**判定**：哪个 5/10/15 嵌合方案的 Gpr-Gpa1 偶联界面在 MD 中保持，作为湿实验首选构建。

## 算力资源

### Windows 计算节点（自有，已部署）

| 项 | 配置 |
|---|---|
| CPU | AMD Ryzen 5 7500F（6C/12T） |
| GPU | **AMD Radeon RX 6750 GRE 10 GB** ⚠️ |
| RAM | 16 × 2 GB DDR5 |
| 系统 | Windows 11 + Tailscale SSH（详见 [ops/ssh-windows-compute.md](../ops/ssh-windows-compute.md)） |

**关键约束**：
- AMD 卡 → 必须调研 ROCm/HIP 后端成熟度。已知概况（待调研验证）：
  - GROMACS 有 HIP backend（社区支持，性能不如 CUDA）
  - OpenMM 对 AMD 支持通过 OpenCL，性能有限
  - AMBER 主打 CUDA，AMD 支持差
  - NAMD 通过 OpenCL，但官方文档以 CUDA 为主
- 显存 10 GB → 足以跑中等体系（~150 k 原子的 GPCR + 膜 + 水），**无法**跑超大 REUS / 复制交换
- **软件选型必须与硬件兼容性一起评估，不提前押注 CUDA-only 工具链**

### PI 课题组服务器（即将可用）

- 配置待 PI 确认（CPU/GPU/RAM）
- 作为主力或 backup，待配置确认后更新本节

## 学习资源

**调研清单本身就是学习资源**。完成调研后，在 [learning/roadmap.md](../learning/roadmap.md) 阶段三补充选定工具的入门材料（教程链接 + 关键 paper + 视频课程）。

**禁止**：在技术栈调研完成前预先填入"GROMACS 教程"等条目 —— 这会污染选型独立性。

## 产出定义

### 阶段 0：调研（首要）

- [ ] 完成上述 7 维度的技术栈调研（每维度附 ≥3 条近 3 年文献依据）
- [ ] 在本文档"调研后的技术栈选型"小节回填决定
- [ ] AMD ROCm/HIP 实测（单一小体系如水盒 benchmark）确认所选软件能在硬件上跑通
- [ ] 在 [learning/roadmap.md](../learning/roadmap.md) 阶段三补充入门材料

### 阶段 1：执行（待调研完成后启动）

- [ ] V138R 盐桥占比时间序列图 + 统计（vs WT 对照）
- [ ] F170E pose drift 分析 + GLU170 χ 角时间序列
- [ ] Top 6 mutant 的 RMSD/RMSF 汇总表 + WT 对照
- [ ] 嵌合 Gpa1 + Gpr 复合物界面稳定性报告（与 P3 联动）
- [ ] 产出路径：`experiments/md-simulation/`（待技术栈确定后创建）

## 方法学局限性

> 待技术栈确定后回填。预期需要讨论：
> - 时间尺度局限（ns 级 MD vs μs 级生物学相关时间）
> - 力场对糖脂配体（ascaroside）的精度
> - MM-PBSA 自由能精度（典型 ±2-5 kcal/mol，比 docking 更不确定）
> - 单复制 vs 多复制的统计意义
> - AMD 后端可能的数值精度差异

## 进展记录

| 日期 | 事件 | 备注 |
|---|---|---|
| 2026-04-11 | 方向新建（骨架 + 调研清单） | 底盘锁定酵母后启动；技术栈待调研 |

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|---|---|---|---|
| 2026-04-11 | v1.0 | 新建：方向背景、调研清单、4 个科学问题、AMD 硬件约束 | docking 完成后机制实证 + 嵌合 Gpa1 升 P0 后稳定性验证需求 |

## 与其他方向的依赖关系

- **输出到**:
  - [P0-molecular-docking](P0-molecular-docking.md): V138R 盐桥实证 / F170E 机制 / Top 6 pose 稳定性 → 回填机制结论与置信度
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 嵌合 Gpa1 + Gpr 复合物 MD 验证 → 选定首选嵌合方案
  - [wet-lab-handoff-P0-docking](wet-lab-handoff-P0-docking.md): V138R 盐桥实证为湿实验提供机制背书
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): Top 6 mutant pose 作为 MD 初始构象
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 提供嵌合 Gpa1 + Gpr 复合物 AF3 结构作为 MD 初始构象
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发嵌合 Gpa1 验证需求
