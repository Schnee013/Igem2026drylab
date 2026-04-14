---
direction: P0-md-simulation
status: learning
priority: P0
chassis_dependent: false
last_updated: 2026-04-12
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
>
> **执行顺序（2026-04-12 决策）**：本方向排在 **嵌合 Gpa1 设计之后**执行。理由：(1) 嵌合 Gpa1 直接阻塞湿实验（不知道用哪个嵌合方案就无法构建），MD 不阻塞任何人；(2) MD 有硬性外部依赖（CHARMM-GUI 审批 + PI 服务器 + ascaroside 参数化 2-5 周），嵌合 Gpa1 的 AF3 预测 1-2 周可交付；(3) MD 是"锦上添花"（方法学首创 + 机制深化），嵌合 Gpa1 是"必须交付"。技术栈调研已全部完成，待嵌合 Gpa1 交付后 + CHARMM-GUI 审批通过后立即启动 ascaroside penalty 扫描。

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
| **MD 软件** | GROMACS / OpenMM / AMBER / NAMD / Desmond | GPCR 膜蛋白使用频率？教程可用性？iGEM 团队历史使用情况？学术免费授权？ |
| **力场** | CHARMM36m / Amber ff19SB / OPLS-AA(GROMOS) | GPCR + 小分子配体体系适用性？哪种与所选 MD 软件搭配最佳？是否支持 ascaroside 这类糖脂？ |
| **膜体系构建** | CHARMM-GUI Membrane Builder / PACKMOL-Memgen / Membed (GROMACS) | 接收 PDB → 出可直接 MD 的体系的工作流？膜组成（POPC vs POPC:POPE 混合）选取依据？ |
| **配体参数化** | GAFF2 / CGenFF / OpenFF | ascarylose 糖骨架 + 长侧链脂肪酸的拓扑生成？哪个工具对环糖支持最好？ |
| **时间尺度惯例** | 50 / 100 / 200 / 500 ns | GPCR + 配体稳定性验证近 3 年文献中的典型时长？复制次数（3× / 5×）？ |
| **盐桥/HBond 分析** | MDAnalysis / mdtraj / PLUMED / VMD | 时间序列盐桥占比的脚本可用性？接触持续时间（contact lifetime）算法？ |
| **自由能 / MM-PBSA** | gmx_MMPBSA / pymbar / alchemlyb | 入门门槛？iGEM 时间窗口是否够？是否能直接给出"WT vs V138R 自由能差"？ |

### 调研产出

完成调研后，**回填到本文档**的"工具栈与参数选型"小节，附**每个选择的文献依据**（年份 + DOI / arXiv / 预印本链接）。**禁止凭印象写入决定**。

### 调研后的技术栈选型

> **两轮调研全部完成（2026-04-12）**，完整报告含对比表 / 引用 / 风险分析：[P0-md-tech-stack-research.md](P0-md-tech-stack-research.md) v2.0
>
> 第一轮（§1–§5）= 软件 / 力场 / 膜构建；第二轮（§6–§10）= 时间尺度 / 分析工具 / 自由能 / ascaroside 类比。

**生产栈**（基于 3 维度一致性结论 + 与 V138R 盐桥假说的匹配度）：

| 层 | 选择 | 关键理由 |
|---|---|---|
| MD 引擎 | **GROMACS**（最新稳定版） | GPCR MD 文献 ~57%；iGEM 团队主流；LGPL 开源 |
| 蛋白力场 | **CHARMM36m** | Arg-Asp/Glu 盐桥 LJ 修正**正好对症 V138R 胍基-羧基假说** |
| 配体参数化 | **CGenFF**（via CHARMM-GUI Ligand Reader & Modeler） | penalty score 定量诊断；与 C36m 同源 |
| 脂质力场 | **CHARMM36 lipid** | 与 C36m 原生配套；POPC / ergosterol 均支持 |
| 水 + 离子 | **TIP3P + 0.15 M KCl** | C36m 默认；CHARMM-GUI 无缝 |
| 膜构建 | **CHARMM-GUI Membrane Builder + PPM 2.0** | 零基础 + 5 月窗口唯一现实选项；全 MD 引擎输出 |
| 膜组分（第一轮） | 纯 **POPC** | Benchmark，易收敛，对照主流 GPCR MD |
| 膜组分（第二轮） | **POPC:ergosterol (80:20)** | 真菌质膜近似，CHARMM36 原生 ergosterol |
| 分析工具 | **MDAnalysis + mdtraj + ProLIF** | 链接上游 IFP 管道，Python-first |

**原型/备份栈**：**OpenMM**（Python 原型 + ProLIF 直连；CHARMM-GUI 同时出双格式）；**AMBER ff19SB + GAFF2 + Lipid21 + OPC** 仅做 alchemical FEP 时切换。

**淘汰选项**：Desmond（闭源 + 公开披露条款）、NAMD（工具链脱节）、g_membed（官方已推荐用 CHARMM-GUI 替代）、OPLS-AA/M（膜生态弱）、OpenFF Sage 做 ascaroside 生产 runs（糖脂 benchmark 缺失）。

### 采样协议（第二轮 §6）

| 方案 | 体系数 | 时长/rep | Reps | 总 ns | A100 天数 | 用途 |
|---|---|---|---|---|---|---|
| **最小 MVP** | **8 holo** (2 WT + Top 6) | **200 ns** | **3** | 4800 | ~28 | t-test 可做，首 50 ns eq |
| **标准** | 8 holo + 2 WT-apo | 300 ns | 3 | 9000 | ~51 | p 值稳定 + bootstrap CI |
| **理想** | 14 (holo + apo) | 500 ns | 3 | 21000 | ~120 | 匹配 GPCRmd-2 |

**推荐执行路径**：先跑 MVP 出初稿 → 剩余时间把 V138R、F170E 升级到 500 ns × 5 seeds 做 publication-grade。AF3 起始需分阶段 restraint release（2→60→80→20 ns schedule），生产前额外损耗 50–100 ns。**不用 HMR 4 fs**（对 CGenFF 数值不稳定，留后期优化）。**不跑 GaMD / metadynamics / LiGaMD**（5 月窗口内学习曲线吃不下）。

### 分析栈（第二轮 §7）

| 任务 | 工具 | 输出 |
|---|---|---|
| **盐桥/HBond IFP 动态** | **ProLIF** `Fingerprint(interactions=["Cationic","Anionic","HBDonor","HBAcceptor"])` 直接接 MDAnalysis trajectory | MultiIndex DataFrame，直接迁移 `run_ifp_mutants.py` |
| **盐桥几何 cross-check** | MDAnalysis `distances.distance_array`（ARG NH1/NH2/NE ↔ ascr18 羧基 O，取 min() ≤ 4.0 Å） | 布尔矩阵 |
| **Contact lifetime histogram** | 自写 run-length encoding (itertools.groupby) 或 MDAnalysis `HydrogenBondAnalysis.lifetime(intermittency=)` | dwell time 直方图 |
| **F170E 侧链动态** | MDAnalysis `analysis.dihedrals.Janin(resid 170).run()` | χ1/χ2 时序 |
| **RMSD/RMSF** | MDAnalysis `analysis.rms.RMSD` / `RMSF`，PMDA/joblib 并行 18 条 |
| **GPCR 社区 cross-check** | **GetContacts**（GPCRmd 标准，4.0 Å N↔O 盐桥判据） | flareplot |

**判据纪律**：各工具数值不一致（MDAnalysis 3.0/150° vs mdtraj 2.5/120° vs gmx hbond 3.5/30°），**必须从头到尾用同一套**；ARG 胍基必须取 `min()` 而非 `mean()`；PBC 先 `gmx trjconv -pbc mol -center`；**同时汇报 occupancy 和 lifetime histogram**（闪烁 ≠ 稳定）。

### 自由能路径（第二轮 §8）

**主路径 = gmx_MMPBSA + per-residue decomposition + ProLIF 盐桥占比三角**（避免把单一 ΔG 数字当真理）：
- 体系：WT 与 V138R holo × 3 rep，ε_in = 4–8 扫描 + `charmm_radii`
- 论文必须明确声明 MM-PBSA 作为"**定性 ranking**"使用（Genheden-Ryde 误差 ±2–10 kcal/mol；Roux-Chipot JPCB 2024 警告构象熵涨落）
- per-residue decomposition 把能量贡献定位到 ARG138
- IFP 占比 + 结构证据作 cross-reference

**Stretch (alchemical RBFE)**：若 7 月前膜系统稳定，做"WT → V138R"蛋白侧单点突变 relative ΔΔG（配体不动，比 ligand RBFE 简单），10–15 λ × 4 ns × 3 rep × 2 腿 ≈ 360 ns。GROMACS 2024 AWH 自适应 λ。

**淘汰**：g_mmpbsa（过时、无 CHARMM 支持）、纯 MM-PBSA absolute ranking（误差窗吞掉 2–4 kcal/mol 真实盐桥贡献）。

### ascaroside 参数化行动计划（第二轮 §9）

**关键红利**：CHARMM36 carbohydrate (par_all36_carb) **已原生覆盖 fucose/rhamnose**（ascarylose 的最近类比）；脂肪酸链 + α-O-glycoside 桥都在 CGenFF drug-like 覆盖范围（CB1 + anandamide 系列证实 "all very low penalties"）。

| 阶段 | 动作 | 预估 |
|---|---|---|
| 1. ParamChem | ascr#18 mol2 → CGenFF stream；糖头 / 脂肪链分离跑便于审计 | 1–2 天 |
| 2. Penalty 分级 | <10 直用 / 10–50 基本验证 / 50–100 torsion 重拟 / >100 ffTK 重拟 / >200 原子型选错 | 2–3 天 |
| 3. QM 重拟（条件） | Gaussian B3LYP/6-31G*（环糖 MP2/cc-pVTZ 单点校正）：环内 C-C-O-C、糖苷键 φ/ψ、>100 项 relaxed scan + ffTK | 1–2 周 |
| 4. Sanity check | Cremer-Pople (Q,θ,φ) 椅式分布（应 ⁴C₁ dominant）+ 糖苷键 φ/ψ 热力图 + 液相密度 / ΔG_hyd（目标 ≤15%, ±0.5 kcal/mol） | 1 周 |
| 5. 并入生产栈 | CHARMM-GUI Ligand Reader & Modeler 读 stream → Gpr3 + POPC 组装 | 2–3 天 |
| **总计** | | **3–5 周**（若阶段 2 全 < 50 可跳 3，缩至 ~2 周） |

**端到端模板参考**：[ACS Bio Med Chem Au 2025 CB1 ZCZ011](https://pubs.acs.org/doi/10.1021/acsbiomedchemau.5c00169)（CHARMM36m + CGenFF + gmx_MMPBSA 完整工作流）。

**起始构象放置**：测试"直接 orthosteric dock"与"膜内预平衡再入"两种方案（参考 [S1P1R Sci Rep 2016](https://www.nature.com/articles/srep22639) 膜-受体界面 entry）。

### 前置风险与强制动作

排序按严重程度（含第二轮 §10 新增）：

1. ⭐⭐⭐ **ascaroside CGenFF 糖环 penalty 审计**：不审计 = V138R 盐桥占比数字不可信。阶段 1-2 = ParamChem + penalty 分级（1-2 天出数据），即可判断是否触发阶段 3 (QM 重拟 1-2 周)。重点：α-L-ascarylose 环 ⁴C₁/¹C₄ 椅式稳定性 + C7 末端羧基 charge。**重大红利**：CHARMM36 碳水已原生覆盖 fucose/rhamnose（ascarylose 最近类比），若阶段 2 全 <50 可直接锁定。
2. ⭐⭐⭐ **AlphaFold3 结构必须过 PPM 2.0 对齐**：跳过会在 production 发现 TM 倾角 30°+ 灾难；顺带明确声明"基于 inactive-like 预测"。AF3 起始首 50 ns 必须从分析窗口扣除（不是晶体结构）。
3. ~~⭐⭐⭐ **CHARMM-GUI 学术账号**~~：**已通过（2026-04-14）**。
4. ⭐⭐ ~~**体系清单 pre-register**~~：**已完成**（2026-04-12）→ 8 holo 锁定到 [experiments/md-simulation/README.md](../../experiments/md-simulation/README.md)。
5. ⭐⭐ **脂质力场引入 ionic lock 假信号**：β2AR+POPC 对比研究显示不同脂质力场让 R-E ionic lock 动力学完全不同。锁定 CHARMM36 lipid 不中途切换。
6. ⭐⭐ **Single replica 审稿常识 = 不够**：≥3 independent seeds，每 ≥200 ns 用于 Welch t-test / Mann-Whitney U；effect size 接近阈值（0.4 vs 0.6）必须 5 seeds 做 bootstrap CI。
7. ⭐ **水盒子 benchmark**：PI 服务器配置确认后跑一次，验证 `-update gpu -bonded gpu -pme gpu` + CPU ≥ 8 核是否开到位。80k-atom 体系 A100 ~265 ns/day 为基准（[NHR@FAU 2024](https://hpc.fau.de/2024/08/13/gromacs-2024-1-on-brand-new-gpgpus/)）。
8. ⭐ **分阶段 equilibration schedule**：借鉴 mwSuMD 2→60→80→20 ns restraint release。

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

### 执行节点：PI 课题组服务器（即将可用）

- **所有 MD 生产计算在 PI 课题组服务器上执行**（2026-04-12 确认）
- 配置待 PI 确认（CPU / GPU / RAM）
- 通常学术服务器以 NVIDIA CUDA 为主流 → 技术栈选型按 **CUDA 主流生态**约束
- 待服务器配置确认后，回填本节并评估显存 → 体系规模与时间尺度上限

### 本地 Windows 节点：不用于 MD

- 本地 AMD Radeon RX 6750 GRE 10 GB 节点**不用于 MD 生产计算**，也**不作为选型约束**
- 本地节点仍用于 docking / AF3 下游分析 / 小体系快速 sanity check（如需）
- 技术栈调研**无需考虑 AMD ROCm/HIP 兼容性**

## 学习资源

**调研清单本身就是学习资源**。完成调研后，在 [learning/roadmap.md](../learning/roadmap.md) 阶段三补充选定工具的入门材料（教程链接 + 关键 paper + 视频课程）。

**禁止**：在技术栈调研完成前预先填入"GROMACS 教程"等条目 —— 这会污染选型独立性。

## 产出定义

### 阶段 0：调研（首要）

- [x] 前 3 维度技术栈调研（软件 / 力场 / 膜构建）：[P0-md-tech-stack-research.md](P0-md-tech-stack-research.md) v1.0（2026-04-12）
- [x] 回填本文档 §调研后的技术栈选型
- [x] 剩余 4 维度调研（时间尺度 / 分析工具 / MM-PBSA / ascaroside 类比）：[P0-md-tech-stack-research.md §6-10](P0-md-tech-stack-research.md) v2.0（2026-04-12）
- [x] 回填采样协议 / 分析栈 / 自由能路径 / ascaroside 行动计划
- [ ] PI 课题组服务器配置确认后，在本文档 §执行节点 回填并校核软件 CUDA 版本
- [x] CHARMM-GUI 学术账号注册（已提交 2026-04-12，**审批通过 2026-04-14**）
- [x] 体系清单 pre-register：8 holo（2 WT + Top 6），已锁定到 [experiments/md-simulation/README.md](../../experiments/md-simulation/README.md)（2026-04-12）

### 阶段 1：执行（待调研完成后启动）

- [ ] V138R 盐桥占比时间序列图 + 统计（vs WT 对照）
- [ ] F170E pose drift 分析 + GLU170 χ 角时间序列
- [ ] Top 6 mutant 的 RMSD/RMSF 汇总表 + WT 对照
- [ ] 嵌合 Gpa1 + Gpr 复合物界面稳定性报告（与 P3 联动）
- [ ] 产出路径：`experiments/md-simulation/`（目录骨架已创建 2026-04-12，CHARMM-GUI 输出后填充）

## 方法学局限性

1. **时间尺度**：200–500 ns × 3 rep 足够 bound-state 局部稳定性（盐桥占比 / pose drift / RMSD/RMSF），**不能**覆盖 μs–ms 罕见事件（ligand (un)binding、activation transition）；iGEM 5 月窗口无法触及 Anton 级 3×20 μs。
2. **AF3 起始结构非晶体**：真菌 GPCR 不在 training set，置信度比人源 GPCR 低；TM helix 断点可能需要基于序列比对手动修复；首 50 ns 必须从分析窗口扣除（侧链 rotamer / loop 平衡 artifact）。
3. **ascaroside 参数化直接文献 = 0**：α-L-ascarylose / ascr#18 / ascr#3 均无公开全原子 MD 研究；参数依赖 CHARMM 碳水类比 (fucose/rhamnose) + CGenFF 脂肪链（CB1 + anandamide 类比）+ ParamChem penalty 审计；若糖环 penalty >50，结论的物理精度需加不确定性声明。
4. **MM-PBSA 精度**：Genheden-Ryde 基准 ±2–10 kcal/mol，class A GPCR 20 靶点 / 934 配体评估里 MM-PBSA 仅 8/20 好于 docking；**论文必须明确声明作为"定性 ranking"使用**，不可报 ΔΔG 绝对值；per-residue decomposition + IFP 占比做三角互证避免数字陷阱。
5. **单 replica 审稿/iGEM 都会被质疑**：即便 1 μs 单 run 不如 3 × 200 ns 有说服力；effect size 接近阈值（0.4 vs 0.6）必须 5 seeds 做 bootstrap CI。
6. **跨工具判据不可比**：HBond 数值（MDAnalysis 3.0 Å/150° vs mdtraj 2.5 Å/120° vs gmx hbond 3.5 Å/30°）各不相同，V138R 分析必须从头到尾锁定一套判据。
7. **iGEM 历史无 7-TM GPCR 全原子 MD 先例**（2022–2025 wiki 检索）：reviewer 参照物稀缺，需自证方法合理；同时是本项目方法学亮点。

## 进展记录

| 日期 | 事件 | 备注 |
|---|---|---|
| 2026-04-11 | 方向新建（骨架 + 调研清单） | 底盘锁定酵母后启动；技术栈待调研 |
| 2026-04-12 | 算力节点切换到 PI 课题组服务器 | 本地 AMD 卡退出 MD 选型约束；技术栈按 CUDA 主流生态调研 |
| 2026-04-12 | 前 3 维度技术栈调研完成 | 生产栈确定：GROMACS + CHARMM36m + CGenFF + CHARMM36 lipid + CHARMM-GUI + 纯 POPC；详见 [P0-md-tech-stack-research.md](P0-md-tech-stack-research.md) |
| 2026-04-12 | 后 4 维度调研完成 | 采样 MVP = 7 holo × 200 ns × 3 rep；分析栈 MDAnalysis + ProLIF (Cationic/Anionic) + GetContacts；自由能主路径 gmx_MMPBSA + per-residue + IFP 三角；ascaroside 路径 ParamChem → penalty 分级 → 条件 QM → Cremer-Pople；详见 [P0-md-tech-stack-research.md §6-10](P0-md-tech-stack-research.md) |
| 2026-04-14 | CHARMM-GUI 学术账号审批通过 | 阶段 0 前置风险 §3 解除；可启动 ascaroside ParamChem 扫描 + 膜体系搭建规划 |

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|---|---|---|---|
| 2026-04-11 | v1.0 | 新建：方向背景、调研清单、4 个科学问题、AMD 硬件约束 | docking 完成后机制实证 + 嵌合 Gpa1 升 P0 后稳定性验证需求 |
| 2026-04-12 | v1.1 | 算力节点改为 PI 课题组服务器；移除 AMD ROCm 约束；调研维度 1 简化 | 用户确认本地 AMD 卡不用于 MD |
| 2026-04-12 | v1.2 | 前 3 维度调研完成，生产栈回填；阶段 0 部分勾选；新增前置风险与强制动作 | deep-research skill + 3 并行子代理产出 [研究报告](P0-md-tech-stack-research.md) |
| 2026-04-12 | v1.3 | 后 4 维度调研完成：采样协议 / 分析栈 / 自由能路径 / ascaroside 行动计划全量回填；方法学局限性重写；前置风险扩到 8 条（加 pre-register 体系、CHARMM-GUI 账号提前、seeds ≥ 3）；阶段 0 全勾选 | 第二轮 deep-research 3 并行子代理产出 [研究报告 v2.0](P0-md-tech-stack-research.md) |
| 2026-04-14 | v1.4 | CHARMM-GUI 学术账号审批通过；前置风险 §3 标记已完成 | 外部审批到位 |

## 与其他方向的依赖关系

- **输出到**:
  - [P0-molecular-docking](P0-molecular-docking.md): V138R 盐桥实证 / F170E 机制 / Top 6 pose 稳定性 → 回填机制结论与置信度
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 嵌合 Gpa1 + Gpr 复合物 MD 验证 → 选定首选嵌合方案
  - [wet-lab-handoff-P0-docking](wet-lab-handoff-P0-docking.md): V138R 盐桥实证为湿实验提供机制背书
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): Top 6 mutant pose 作为 MD 初始构象
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 提供嵌合 Gpa1 + Gpr 复合物 AF3 结构作为 MD 初始构象
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发嵌合 Gpa1 验证需求
