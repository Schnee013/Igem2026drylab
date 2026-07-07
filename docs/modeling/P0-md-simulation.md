---
direction: P0-md-simulation
status: compute_triage
priority: P0
chassis_dependent: false
last_updated: 2026-07-06
---

# P0: MD 模拟（机制验证 + 嵌合 Gpa1 稳定性）

> 来源: 2026-04-11 新建 | iGEM 评审定位: 直接支撑湿实验设计的机制实证
>
> **范围边界**：本文维护 MD 方法、protocol、gate、分析指标和证据边界。当前执行状态、阻塞项和优先级只看 [docs/INDEX.md](../INDEX.md)；具体经过看 [docs/logs/](../logs/)。
>
> **历史突变体 MD 背景**：2026-04 的 docking/IFP 阶段提出了 ARG138 盐桥、F170E/ECL2 pose drift 和候选 pose 稳定性等静态方法无法回答的问题。这些问题保留为 mutant-holo 方法背景；若未来重启，必须基于当前 refreshed docking handoff 重新定义候选集合，不沿用旧清单。
>
> 同时 [P3-chimeric-gprotein](P3-chimeric-gprotein.md)（已升 P0）的嵌合 Gpa1 设计也需要 MD 稳定性验证。
>
> **本方向的边界**：是 docking 与嵌合 Gpa1 的**实证补充**，**不再做新对接**（用户决策：算力全部投入 MD）。
>
> **当前权威指针**：最新执行优先级见 [决策 005](../decisions/005-md-compute-triage-after-chctrl.md)、[docs/INDEX.md](../INDEX.md) 和最新日志。站点矩阵、E2 环境证据、E2 restart plan 与 unified rerun sites plan 保留为历史执行路线、脚本和 provenance 参考；2026-06-26 后不再作为 chimeric candidate full-production 的直接启动指令。
>
> **2026-06-26 校准**：旧 Slurm 上 chimeric control/chctrl 组 3 reps MD 已完成；E2 路线只有 chctrl rep1 及其 smoke / benchmark / early-gate 证据，不能写成 E2 完成 3 reps。候选体系 full MD 因算力不足暂停。当前 MD 主线改为两步并行：调研 chimeric Gpa1 省算力 protocol（减少体系大小或更强物理限制），并从 `Gpr2_R59C` / `Gpr3_R167Y` 启动 mutant GPR MD 的体系大小核查和短程算力测试。
>
> **2026-07-05 校准**：R1 `chctrl` tight full-system rebuild 已完成 E2 step6 和 100 ps short production，但 `120 A` XY / `20 A` water 的实例是 Z-only 缩减，atom-count delta 只有 `-2.57%`。公开 atom-count 对照未显示该体系蛋白/总原子占比异常，因此 R1 Z-only 保留为 build/run evidence point，不作为省算力成功或候选迁移规则。full-object throughput baseline 只作配套排程/性能规划，不是体系缩减路线。
>
> **2026-07-06 校准**：`Gpr2_WT + ASCR18` 已完成 E2 100 ps short benchmark，作为 Decision 005 后 mutant GPR 前测的 WT holo 资源基线；该结果只回答 GPU 占用和短程生产速率，不支持突变体稳定性、配体稳定性或 full-production 收敛结论。`Gpr2_WT + ASCR18` 200 ns rep1 目前只有 launch-gate/started 证据，尚无 completion archive。
>
> 当前 mutant GPR 主线仍是 local input gate：按 `../../codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`、`../../experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/material_matrix.tsv` 和 `../../experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/decision_package.md` 把 `Gpr2_R59C + ASCR18` / `Gpr3_R167Y + ASCR3` 推进到可审计 MD input package。两个 system 已有 PPM output、CHARMM-GUI manual submission package、return-intake 模板、submission preflight、return validator、Gpr3 ASCR3 46-atom coordinate layer 和后续 metric preregistration；仍需按 `../../experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md` 回收 CHARMM-GUI output，填 intake/manifest，再做 final ligand insertion/alignment、topology、index 和 warning review。
>
> **2026-07-06 operator packet**：当前 CHARMM-GUI 操作员上传/校验/回传清单已集中到 `../../experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_operator_packet_20260706.md` 和 `.tsv`；该包给出两个体系的 upload PDB、SHA256、counts、settings/manifest checksum、return target 和 validator command，是下一步人工提交/回收 CHARMM-GUI output 的执行入口。
>
> **2026-07-06 采样队列决策**：为节省 E2 共享 A100 算力，GPR MD 不按 `Gpr2/Gpr3 WT x ASCR3/ASCR18` 全矩阵或 Channel A/B top3 mutant 全量 3 reps 铺开。当前队列为：先完成并归档 `Gpr2_WT + ASCR18` 200 ns rep1；随后推进 `Gpr2_R59C + ASCR18` package gate、smoke/benchmark 和 200 ns rep1；先做 Gpr2 WT/mut matched analysis；再启动 Gpr3 matched ASCR3 pair（`Gpr3_WT + ASCR3` 与 `Gpr3_R167Y + ASCR3`）。rep1 稳定时可暂停 rep2/3，待最终 candidate 保留后再补；rep1 只作为 triage evidence，不作为最终 3-rep 统计结论。

## 解决什么问题

对接 + IFP 给出**静态 pose 与平均接触频率**，无法回答：

1. **相互作用类型**：ARG138-羧基 9 次 VdWContact 在 PDBQT 工作流下是否掩盖了真正的盐桥？（PDBQT→SDF 不含形式电荷，ProLIF 盐桥检测结构性失效；MD 力场自动分配电荷态，能正确检测离子型相互作用）
2. **pose 稳定性**：候选 mutant 的 pose 在 ns 时间尺度是否保持？还是只是 Vina 全局搜索找到的局部最小值？
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
| 历史 mutant-holo MVP | 8 holo (2 WT + 2026-04 历史候选集合) | 200 ns | 3 | 4800 | ~28 | 历史方案；若重启必须按 refreshed handoff 重新定义 |
| **标准** | 8 holo + 2 WT-apo | 300 ns | 3 | 9000 | ~51 | p 值稳定 + bootstrap CI |
| **理想** | 14 (holo + apo) | 500 ns | 3 | 21000 | ~120 | 匹配 GPCRmd-2 |

**历史 mutant-holo 执行路径**：先跑 MVP 出初稿，再视结果升级关键机制问题到更长时长和更多 seeds。该路径不是当前生产队列；2026-06-26 后若重启 mutant GPR MD，候选起点为 current refreshed docking handoff 的 `Gpr2_R59C` / `Gpr3_R167Y`，并且先做体系大小核查和算力测试。AF3 起始需分阶段 restraint release（2→60→80→20 ns schedule），生产前额外损耗 50–100 ns。**不用 HMR 4 fs**（对 CGenFF 数值不稳定，留后期优化）。**不跑 GaMD / metadynamics / LiGaMD**（5 月窗口内学习曲线吃不下）。

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

排序按严重程度（含第二轮 §10 新增 + 2026-04-16 provenance 审计新增 #9-#13）：

1. ~~⭐⭐⭐ **ascaroside CGenFF 糖环 penalty 审计**~~：**已完成（2026-04-16）**。ascr18 + ascr3 全部 penalty < 10，跳过 QM。详见 `parameters/{ascr18,ascr3}/protonated/penalty_summary.md`。
2. ~~⭐⭐⭐ **AlphaFold3 结构必须过 PPM 2.0 对齐**~~：**已完成（2026-04-16）**。Gpr2（33.0Å/3°）+ Gpr3（30.6Å）正常；GprC（23.4Å）偏薄待观察。输出 `structures/ppm2/`。
3. ~~⭐⭐⭐ **CHARMM-GUI 学术账号**~~：**已通过（2026-04-14）**。
4. ~~⭐⭐ **体系清单 pre-register**~~：**已完成**（2026-04-12）→ 8 holo 锁定到 [experiments/md-simulation/README.md](../../experiments/md-simulation/README.md)。
5. ⭐⭐ **脂质力场引入 ionic lock 假信号**：β2AR+POPC 对比研究显示不同脂质力场让 R-E ionic lock 动力学完全不同。锁定 CHARMM36 lipid 不中途切换。
6. ⭐⭐ **Single replica 审稿常识 = 不够**：≥3 independent seeds，每 ≥200 ns 用于 Welch t-test / Mann-Whitney U；effect size 接近阈值（0.4 vs 0.6）必须 5 seeds 做 bootstrap CI。
7. ⭐ **水盒子 / smoke benchmark**：如后续更换服务器、GPU 或 GROMACS 二进制，再跑一次，验证 `-update gpu -bonded gpu -pme gpu` + CPU ≥ 8 核是否开到位。80k-atom 体系 A100 ~265 ns/day 仅作外部参考基准（[NHR@FAU 2024](https://hpc.fau.de/2024/08/13/gromacs-2024-1-on-brand-new-gpgpus/)）。
8. ⭐ **分阶段 equilibration schedule**：借鉴 mwSuMD 2→60→80→20 ns restraint release。
9. ~~⭐⭐ **Docking pose 空间兼容性**~~：**已完成（2026-04-16）**。
   Gpr3：需删 POPC resid 514（Phase 3 已处理），其余就绪。
   Gpr2：3D offset `[6.17, 0.65, -7.85]` 修复后 76/80 poses 胞外（历史 Slurm job 6535），best pose Z≈106。
   Gpr2 新 pose 需重新检查 POPC 碰撞（Phase 3 第一步）。
   → `docs/logs/2026-04-16.md` §Gpr2 Docking Pose 朝向验证
10. ~~⭐⭐ **Ascr18/ascr3 羧基质子化态确认**~~：**已完成（2026-04-16）**。ascr18 + ascr3 均已去质子化重新参数化。ASCR18.itp（54 atoms, qtot=-1.000）Job 7629292909 + ASCR3.itp（46 atoms, qtot=-1.000）Job 7629305001。penalty 全部 < 10。输出 `parameters/{ascr18,ascr3}/deprotonated/charmm-gui-{jobid}/gromacs/`。
11. ⭐ **突变体引入方法未指定**（2026-04-16 provenance 审计新增）：Phase 4 "从 WT 膜体系引入点突变"未指定工具。推荐：PyMOL `mutagenesis wizard`（单点突变 + 最优 rotamer 选择）或 CHARMM-GUI PDB Manipulator；突变后需对突变残基做局部 EM 消除新侧链 clash，再跑完整 6 步 eq。
12. ⭐ **mwSuMD restraint release 时间表来源待验证**（2026-04-16 provenance 审计新增）：#8 中 "2→60→80→20 ns" 的具体数字是否来自 [Deganutti eLife 2024](https://elifesciences.org/articles/96513) 原文需验证。CHARMM-GUI 标准 6 步渐进释放（step6.1-6.6）是 0.375 ns 级别，AF3 结构可能需延长至 ns 级但具体数值需文献背书。
13. ⭐ **CHARMM-modified TIP3P 命名**（2026-04-16 provenance 审计新增）：CHARMM-GUI 输出的水模型实际是 CHARMM-modified TIP3P (TIPS3P，含 LJ on H)，与 standard TIP3P 有微小差异。当前 pipeline 使用 CHARMM-GUI 默认值是正确的，但论文/wiki 写作时需明确标注 "CHARMM-modified TIP3P" 而非 "TIP3P"。

## 待回答的科学问题

本节的突变体问题来自 2026-04 历史 mutant-holo 分支，不代表当前生产队列。若未来恢复突变体 MD，应从 current docking handoff 重新定义体系、候选和证据目标。

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

### 问题 3：历史候选 binding pose 稳定性

**体系**：2026-04 历史候选集合只作方法背景。2026-05 refresh 后若要重启突变体 MD，必须从 [wet-lab-handoff-P0-docking.md](wet-lab-handoff-P0-docking.md) 和当前 ratio/IFP release 重新定义清单。

**核心测量**：
- 配体 RMSD（相对初始 docking pose）
- 受体 backbone RMSF（特别是结合口袋残基）
- 关键 HBond 时间序列

**判定**：哪些候选 pose 在 MD 中稳定（→ 湿实验高置信度）；哪些发生大幅 drift（→ 降低优先级或重新解读）。

### 问题 4：嵌合 Gpa1 + Gpr 复合物界面稳定性（与 [P3-chimeric-gprotein](P3-chimeric-gprotein.md) 联动）

> **文献调研完整报告**：[P0-md-tech-stack-research.md §12](P0-md-tech-stack-research.md)
>
> **关键先例**：Tawfeeq et al. 2025 (Biochemistry) — D1R/D2R + chimeric Gs18i/Gi18s，4 reps × 500 ns，与本项目设计（C 端交换 chimeric Gα + MD 验证）直接对应。Ramasamy et al. 2025 (eLife) — 唯一 Ste2-Gpa1 MD 研究，验证酵母 GPCR-Gα 体系可做 MD。
>
> **技术栈验证**：现有 GROMACS + CHARMM36m + CHARMM-GUI + POPC 栈完全适用于 GPCR-Gα 复合物 MD，无需更换（Ranganathan 2019: A2A + Mini-Gs 用 CHARMM36 + POPC + GROMACS；Memprot.GPCR-ModSim 2024: CHARMM36m + GROMACS 自动化管线）。
>
> **方法学首创声明**（2026-04-17 经 4 维度系统搜索修订，矩阵 → `experiments/chimeric-gpa1/literature/chimeric_md_literature_matrix.md`）：(1) 真菌 GPCR-Gα MD 仅 2 篇（Velazhahan 2021 + Ramasamy 2025），均为酿酒酵母 Ste2-Gpa1 → 本项目首次扩展到非酿酒酵母真菌；(2) chimeric Gα MD 仅 1 篇人源（Tawfeeq 2025）→ 本项目首个真菌 chimeric Gα MD；(3) 零篇 ascaroside 结合态 GPCR-Gα MD → 初版不含配体可规避。MD 只能评估结构稳定性（界面是否解离），不能完全表征偶联动力学（ms 时标，Casiraghi/Kobilka 2025 警告）。

#### 4.1 体系选择（与 P3 决策树对齐）

决策树走"是"分支（GprC saturation scan 有 no-caveat 候选）→ 主路线 = Gpr2/3 + AoGpa2 chimeric Gpa1。

| 优先级 | 体系 ID | 受体 | Chimera | ipTM | iPAE | 理由 |
|--------|---------|------|---------|------|------|------|
| **P1** | Ch-1 | Gpr3 | AoGpa2-C37 | 0.50 | 23.31 | 全数据集最低 iPAE；主工程路线 |
| **P2** | Ch-2 | Gpr3 | AoGpa2-C15 | 0.50 | 24.82 | 最短有效嫁接；与 P1 对比 C37 vs C15 |
| **P3** | Ch-3 | GprC | AfGasA-C25 | 0.38 | 26.47 | 唯一 cognate 特异性（Δ=+0.16）；备选路线 |
| **ctrl** | Ch-ctrl | Ste2 | Gpa1-WT | 0.60 | 23.44 | **阳性对照**（PDB 7AD3 实验结构，不依赖 AF3；Ramasamy 2025 提供 MD 交叉验证锚点） |

> 候选选择权威源 → [ranking_summary.md](../../experiments/chimeric-gpa1/analysis/ranking_summary.md)；
> AF3 起始结构 → `experiments/chimeric-gpa1/af3_predictions/downloads/{gpr3_gpa1_aogpa2_c37,gpr3_gpa1_aogpa2_c15,gprc_gpa1_afgasa_c25}_complex/`；
> 阳性对照 → PDB 7AD3（Ste2-Gpa1 cryo-EM 结构，Velazhahan 2021）→ RCSB 下载后存放 `experiments/md-simulation/structures/pdb/7AD3.pdb`。

#### 4.2 体系组成

| 组件 | 包含？ | 理由 |
|------|--------|------|
| GPCR（AF3 预测 / PDB 7AD3） | ✅ | 起始结构 |
| Chimeric Gpa1（AF3 预测）/ WT Gpa1 | ✅ | 验证目标 |
| Gβγ (Ste4/Ste18) | ❌ | 增加 ~400 residues + 复杂度；Tawfeeq 2025 不含 Gβγ |
| 核苷酸 (GDP/GTP) | ❌ | AF3 预测为 nucleotide-free 态（类似 cryo-EM）；Tawfeeq 2025 亦为 empty |
| 配体 (ascr18) | ❌ 初版 | 问题是界面稳定性，不是配体结合；且配体不在 Gα 界面 |
| POPC 膜 | ✅ | 与突变体 MD 一致 |
| CHARMM-modified TIP3P + 0.15 M KCl | ✅ | 标准 |

**体系规模估算**：GPCR (~300 res, ~5k atoms) + Gα (~470 res, ~7.5k atoms) + POPC (~200 lipids, ~30k atoms) + 水+离子 (~150-200k atoms) = **~200-250k atoms**（vs 突变体 MD 的 ~130k atoms）。Box size ~100×100×220 Å（Z 维度需增加容纳胞内侧 Gα）。

#### 4.3 协议参数

| 参数 | 值 | 依据 |
|------|-----|------|
| 模拟时长 | **500 ns/replicate final；100-150 ns full-system early stability gate** | 500 ns 仍是最终 production 目标；100-150 ns 只作中途筛查和调度门禁，详见 [E2 Chimeric MD Restart Plan](../../codex/docs/plans/e2-chimeric-md-restart.md) |
| 独立 replicates | **3** | 最小统计需求；如效应量近阈值升到 5 |
| 分析窗口起点 | 100 ns | AF3 结构需要更长松弛期（比 docking pose 更大的初始偏差） |
| 约束释放 | 与突变体 MD 相同 6 步 CHARMM-GUI 平衡化 | 已验证可用 |
| 时间步长 | 2 fs (no HMR) | 与突变体 MD 一致 |
| 温度 | 303.15 K | 酵母生长温度 |
| 压力耦合 | semi-isotropic, 1 bar | 膜体系标准 |
| **GPU** | **E2 A100-SXM4-80GB primary；Slurm RTX 5090 validated secondary candidate** | 以各站点 preflight / smoke / benchmark 日志为准；旧 Slurm 2025.2-spack 估算只作历史参考，不迁移为当前 rerun 证据 |

**算力估算**：500 ns × 3 reps × 4 systems = 6000 ns。当前已验证 E2 A100 primary 路线；推荐 GROMACS 2025.4 MPI-CUDA 环境已通过 preflight，四体系输入同步和 rep1 smoke 已完成。2026-05-30 E2 same-GPU benchmark 显示最佳 2-job 总吞吐低于单 job，因此 E2 production cap 为一个 full GPU MD job。Slurm RTX 5090 只能在同 pin 环境、smoke、benchmark 通过后进入 production。默认 16-32 CPU threads；同一 GPU 同时只跑一个 full MD job。100-150 ns early gate 只决定是否继续同一 full-system replicate 到 500 ns，不改变最终证据等级。

#### 4.4 分析指标

| 指标 | 工具 | 判定阈值 | 文献来源 |
|------|------|---------|---------|
| 1. α5-helix iRMSD | MDAnalysis | < 3 Å → 稳定；> 5 Å → 解离 | Bauer 2022 |
| 2. BSA 时间序列 | FreeSASA | 下降 < 20% → 稳定 | Bauer 2022 |
| 3. 接触图持续性 | GetContacts (4 Å cutoff) | > 50% 初始接触保持 | GPCRsignal (Jakowiecki 2021) |
| 4. 界面 H-bond 占比 | MDAnalysis | > 10% 占比 → 有效 | 文献通用 |
| 5. COM 距离 (ICL2/3 ↔ Gα C-term) | MDAnalysis | 不单调递增 | Casiraghi/Kobilka 2025 |
| 6. 嫁接连接区 RMSF | MDAnalysis | 与 WT backbone RMSF 相当 | 项目设计（chimeric 特有） |
| 7. MM-PBSA (可选) | gmx_MMPBSA | 定性排名，不绝对 | 与突变体 MD 相同 |

**判定**：
- P1/P2/P3 vs ctrl：chimeric 体系的 α5-helix iRMSD 与阳性对照（Gpa1-WT × Ste2）在同一量级 → 界面稳定
- P1 vs P2：C37 vs C15 嫁接长度对界面稳定性的影响（iPAE 差异 23.31 vs 24.82 是否在 MD 中放大）
- Ch-3 (AfGasA-C25)：cognate 特异性（Δ=+0.16）是否在 MD 中体现为更稳定的界面

#### 4.5 Chimeric MD Pipeline 步骤

```
Phase C1: 结构准备
  AF3 CIF → 清理 PDB → PPM 2.0 膜对齐
  ctrl: PDB 7AD3 → 清理 PDB → PPM 2.0 膜对齐

Phase C2: 膜体系构建
  CHARMM-GUI Membrane Builder（多链蛋白 + POPC）
  → GROMACS topol/gro/mdp 输出
  注意：box Z 维度 ~220 Å（需容纳胞内侧 Gα，比突变体 MD 大 ~45 Å）

Phase C3: EM + 平衡化
  复用突变体 MD 的 run_phase3.sh 框架
  无需 ligand 合并步骤 → assemble_complex.py 的简化版本（prepare_chimeric_system.py）

Phase C4: Production MD
  旧计划：500 ns × 3 reps × 4 systems = 6000 ns
  2026-06-26 决策：旧 Slurm control/chctrl 组 3 reps 已完成；E2 只有 chctrl rep1 证据；候选体系 full-production 暂停
  2026-07-04 R1-Z 校准：R1 reduced chctrl 可 build/short-run，但 Z-only atom-count 降幅不足；不迁移候选
  E2 是共享服务器；新的 MD 前测必须先做资源估算和短程 benchmark，不长期独占 A100

Phase C5: 分析
  7 项指标（§4.4）+ 可选 MM-PBSA
  与突变体 MD 分析工具链复用（MDAnalysis + GetContacts）
```

#### 4.6 与突变体 MD 的关系

| 维度 | 共享 | 独立 |
|------|------|------|
| 技术栈 | ✅ GROMACS + CHARMM36m + CHARMM-GUI | — |
| 力场文件 | ✅ toppar/ 基本相同 | 无 CGenFF 配体参数（不含配体） |
| 服务器 | ✅ 同一生产 pin 与 clean-start 规则 | E2 primary；Slurm RTX 5090 只有通过 validated secondary gate 后可加入 |
| 运行脚本 | 部分复用 | E2 使用 `e2_*` scripts；Slurm rerun 只能使用新的 `slurm_*` gate scripts，不复用旧 Slurm production 模板 |
| 分析脚本 | 部分复用 | 新增界面特异性分析（iRMSD, BSA, COM） |
| 执行顺序 | — | 2026-06-26 后改为 chimeric 省算力方案调研与 mutant GPR 前测并行；不再直接推进 chimeric candidate full-production |

#### 4.7 Chimeric MD Phase 定义

| Phase | 名称 | 输入 | 输出 | 状态 |
|-------|------|------|------|------|
| C1 | 结构准备 | AF3 CIF / PDB 7AD3 | 清理 PDB + PPM 对齐 | ✅ 完成（详见 04-18/04-26 日志） |
| C2 | 膜体系构建 | PPM 对齐 PDB | CHARMM-GUI GROMACS 输出 | ✅ 完成（chctrl/Ch-1/Ch-2/Ch-4 已建系） |
| C3 | EM + 平衡化 | Phase C2 体系 | 可跑 production 的体系 | ✅ chctrl/Ch-1/Ch-2/Ch-4 完成 step6.6 |
| C4 | Production MD | Phase C3 体系 | trajectories (.xtc/.trr) | ⏸ 旧 Slurm control/chctrl 组 3 reps 已完成；E2 只有 chctrl rep1 证据；R1-Z 已降级为省算力不足；Ch-1/Ch-2/Ch-4 candidate full-production 因算力不足暂停 |
| C5 | 分析 | trajectories | 7 项指标 + 可选 MM-PBSA | ⏳ chctrl 结果待 source audit 与分析；candidate 体系等待新 protocol |

## 算力资源

### 服务器执行入口

- 新服务器/远程计算默认使用 [NKULiulab E2 共享云服务器使用规范](../ops/nkuliulab-e2-cloud-server.md)；登录、传输、远程 IDE、软件环境或长任务前必须先读该手册。
- 2026-06-26 后 chimeric candidate full-production 暂停；旧 Slurm RTX 5090 validated secondary route 仅保留为历史/未来备选指针，不能直接启动新的 production。
- 旧 Slurm 操作指南 [slurm-md-server.md](../ops/archives/slurm-md-server.md) 仅保留历史执行记录、硬件和坑位追溯；2026-04-26 Slurm 历史核查和旧 production 日志只用于追溯，不作为当前 rerun 结果。
- E2 MD/GROMACS 环境证据矩阵见 [e2-md-gromacs.md](../../environments/e2-md-gromacs.md)；站点环境细节不在本文重复维护。
- chimeric rerun 旧范围为 chctrl + Ch-1/Ch-2/Ch-4；截至 2026-07-06，旧 Slurm control/chctrl 组 3 reps 已完成，E2 路线有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据，但 R1-Z atom-count 降幅不足，candidate full-production 继续暂停。mutant GPR 当前状态回 [docs/INDEX.md](../INDEX.md) 和 `../../codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`；未完成门禁是 WT rep1 completion archive、两个 mutant system 的 CHARMM-GUI returned output，以及 final coordinate/topology/index/warning review。

### 本地 Windows 节点：不用于 MD

- 本地 AMD Radeon RX 6750 GRE 10 GB 节点**不用于 MD 生产计算**，也**不作为选型约束**
- 本地节点仍用于 docking / AF3 下游分析 / 小体系快速 sanity check（如需）
- 技术栈调研**无需考虑 AMD ROCm/HIP 兼容性**

## 执行 Phase 定义（唯一权威源）

> 日志和 memory 中引用 "Phase N" 时，定义以本节为准。

| Phase | 名称 | 输入 | 输出 | 状态 |
|-------|------|------|------|------|
| 0 | 调研 + 前置风险 | 文献 + 技术栈候选 | 生产栈选型 + 风险清单 | ✅ 完成 |
| 1 | 膜体系构建 | PPM 2.0 对齐 PDB | CHARMM-GUI GROMACS 输出 (topol/gro/mdp) | Gpr2 ✅ Gpr3 ✅ GprC 暂缓 |
| 2 | Docking pose 提取 + 坐标对齐 | Vina PDBQT + Phase 1 体系 | 膜坐标系下的配体 aligned PDB | Gpr3 ✅ / Gpr2 ✅ (3D offset) |
| 2.5 | 配体 CGenFF 参数化（去质子化） | 去质子化 SDF | .itp (qtot=-1) | ✅ ASCR18 + ASCR3 |
| 3 | 拓扑合并 + EM + 平衡化 | Phase 1 体系 + Phase 2 配体 + Phase 2.5 itp | 可跑 production 的 WT holo 体系 | ✅ 完成 (Gpr2 job 6595 + Gpr3 job 6596) |
| 4 | 突变体引入 | Phase 3 WT holo 体系 + 突变定义 | 突变体体系 (local EM + 6 步 eq) | ⏳ `Gpr2_R59C` / `Gpr3_R167Y` 已到 CHARMM-GUI manual submission + return-intake gate；仍缺 returned output、final coordinates、topology、index 和 warning review |
| 5 | Production MD | Phase 3/4 体系 | trajectories (.xtc/.trr) | baseline：`Gpr2_WT + ASCR18` 100 ps E2 short benchmark 已完成；WT 200 ns rep1 只有 launch/started 证据；mutant/full production 未开始，需另过输入门禁与排程决策 |
| 6 | 分析 | trajectories | 盐桥占比 / RMSD / IFP / MM-PBSA | ❌ 未开始 |
| **C1** | **Chimeric 结构准备** | AF3 CIF / PDB 7AD3 | 清理 PDB + PPM 对齐 | ✅ 完成 |
| **C2** | **Chimeric 膜体系构建** | PPM 对齐 PDB | CHARMM-GUI GROMACS 输出 | ✅ 完成 |
| **C3** | **Chimeric EM + 平衡化** | Phase C2 体系 | 可跑 production 的体系 | ✅ step6.6 完成 |
| **C4** | **Chimeric Production MD** | Phase C3 体系 | trajectories (.xtc/.trr) | ⏸ 旧 Slurm control/chctrl 组 3 reps 已完成；E2 有 chctrl rep1 early-gate 与 R1 reduced-chctrl exploratory short-run 证据；R1-Z 降级，candidate full-production 暂停 |
| **C5** | **Chimeric 分析** | trajectories | 7 项指标 + 可选 MM-PBSA | ⏳ chctrl 结果待 source audit 与分析；candidate 体系等待新 protocol |

> Chimeric MD Phase（C1-C5）独立于突变体 MD Phase（0-6），可并行执行。详见 §问题 4。

### Phase 3 详细步骤

1. 将 Phase 2 对齐后的配体 PDB 插入 Phase 1 膜体系 GRO
2. 删除与配体碰撞的 POPC（Gpr3: resid 514, 0.40 Å；Gpr2 无碰撞）
3. 合并 `topol.top`：添加配体 `.itp`（Phase 2.5 去质子化版）+ `[ molecules ]` 条目
4. Energy Minimization（`gmx grompp` + `gmx mdrun`，steep descent）
5. 6 步平衡化（CHARMM-GUI 标准方案：BB 10→0.1 / SC 5→0 / 脂质约束递减）
6. → 输出可直接跑 Production 的完整体系

### Phase 4 详细步骤

1. 从 Phase 3 WT holo 体系出发
2. PyMOL `mutagenesis wizard`（单点突变 + 最优 rotamer 选择）或 CHARMM-GUI PDB Manipulator
3. 突变残基局部 EM 消除新侧链 clash
4. 完整 6 步 eq（同 Phase 3 step 5）

### 历史突变体 MD 阻塞关系（2026-04 snapshot，不作当前状态）

```text
Phase 3 (Gpr2) → ✅ 完成 (EM Fmax=983.5, 6步eq完成 19:26 CST)
Phase 3 (Gpr3) → ✅ 完成 (EM Fmax=986.0, 6步eq完成 19:30 CST)
Phase 4 → 已解除阻塞，可开始
Phase 5 → 阻塞于 Phase 4
Phase 6 → 阻塞于 Phase 5
```

## 产出定义

### Phase 0 检查清单

- [x] 前 3 维度技术栈调研：[P0-md-tech-stack-research.md](P0-md-tech-stack-research.md) v1.0（2026-04-12）
- [x] 回填本文档 §调研后的技术栈选型
- [x] 剩余 4 维度调研：[P0-md-tech-stack-research.md §6-10](P0-md-tech-stack-research.md) v2.0（2026-04-12）
- [x] 回填采样协议 / 分析栈 / 自由能路径 / ascaroside 行动计划
- [ ] PI 课题组服务器配置确认后，在本文档 §执行节点 回填并校核软件 CUDA 版本
- [x] CHARMM-GUI 学术账号注册（已提交 2026-04-12，**审批通过 2026-04-14**）
- [x] 体系清单 pre-register：历史 mutant-holo 8 体系，已锁定到 [experiments/md-simulation/README.md](../../experiments/md-simulation/README.md)（2026-04-12）

### Phase 1–2.5 检查清单

- [x] Phase 1: Gpr2 膜体系构建（CHARMM-GUI Job 7628027774）
- [x] Phase 1: Gpr3 膜体系构建（CHARMM-GUI Job 7628627163）
- [ ] Phase 1: GprC 膜体系构建（暂缓：蛋白 X extent 97.93 Å > box 90 Å，需 XY≥130）
- [x] Phase 2: Gpr3 docking pose 提取 + Kabsch 对齐（RMSD=0.064 Å）
- [x] Phase 2: Gpr2 docking pose 对齐（3D offset 修复, job 6535, 76/80 EC, Z≈106）
- [x] Phase 2.5: ASCR18 去质子化 CGenFF（Job 7629292909, qtot=-1）
- [x] Phase 2.5: ASCR3 去质子化 CGenFF（Job 7629305001, qtot=-1）

### Phase 6 最终产出

- [ ] V138R 盐桥占比时间序列图 + 统计（vs WT 对照）
- [ ] F170E pose drift 分析 + GLU170 χ 角时间序列
- [ ] 历史候选或未来 refreshed 候选的 RMSD/RMSF 汇总表 + WT 对照
- [ ] 嵌合 Gpa1 + Gpr 复合物界面稳定性报告（与 P3 联动）
- [ ] 产出路径：`experiments/md-simulation/`

## 方法学局限性

1. **时间尺度**：200–500 ns × 3 rep 足够 bound-state 局部稳定性（盐桥占比 / pose drift / RMSD/RMSF），**不能**覆盖 μs–ms 罕见事件（ligand (un)binding、activation transition）；iGEM 5 月窗口无法触及 Anton 级 3×20 μs。
2. **AF3 起始结构非晶体**：真菌 GPCR 不在 training set，置信度比人源 GPCR 低；TM helix 断点可能需要基于序列比对手动修复；首 50 ns 扣除目前按项目 operational burn-in heuristic 处理（侧链 rotamer / loop 平衡 artifact），不能写作文献硬阈值。
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
| 2026-04-14 | CHARMM-GUI 学术账号审批通过 | Phase 0 前置风险 §3 解除 |
| 2026-04-16 | Phase 1 完成（Gpr2 + Gpr3 膜体系）| CHARMM-GUI Membrane Builder，GprC 暂缓（box 不够大）|
| 2026-04-16 | Phase 2 完成（Gpr2 + Gpr3） | Gpr3 对齐 ✅；Gpr2 3D offset ✅（job 6535, 76/80 EC）|
| 2026-04-16 | Phase 2.5 完成 | ascr18 + ascr3 去质子化 CGenFF itp（qtot=-1）|
| 2026-04-16 | 前置风险 #1 penalty 审计完成 | ascr18 + ascr3 全部 < 10，跳过 QM |
| 2026-04-16 | 前置风险 #9 Gpr2 pose 已解决 | 3D offset job 6535, 76/80 EC, Z≈106 → 日志 |
| 2026-04-16 | Phase 定义表新增 | 本文档 §执行 Phase 定义 为唯一权威源 |
| 2026-04-16 | 问题 4 扩展为完整 chimeric MD 子节 | 文献调研（6 篇）+ 体系选择（3+1 ctrl）+ 协议（500ns×3rep）+ 7 项分析指标 + Phase C1-C5 定义 |
| 2026-04-27 | chimeric MD 历史状态校准 | 旧 Slurm chctrl production 完成；该状态已被 2026-05-29 E2 rerun 决策取代 |
| 2026-05-06 | GPCR-Gα tech-stack citation source audit | Ramasamy→Mohanty；Ranganathan→Renault；Jakowiecki→Miszta；Tawfeeq/Memprot 方法迁移降级；only-N novelty claim 暂停使用 |
| 2026-05-29 | E2 rerun 决策校准 | chctrl 纳入 E2 统一环境 clean-start rerun；环境矩阵归档到 `environments/e2-md-gromacs.md` |
| 2026-05-30 | E2 rerun benchmark gate | chctrl rep1 checkpoint-gated interrupt completed; same-GPU 2-job benchmark lower than single-job baseline; rep1 resumed single-job from `prod.cpt` |
| 2026-05-30 | unified sites route | Slurm RTX 5090 added as validated secondary candidate only; site matrix and `slurm_*` gate scripts added; old Slurm 2025.2-spack outputs remain historical pointers |
| 2026-06-01 | tiered validation protocol | 100-150 ns defined as full-system early stability gate; 500 ns/replicate remains final target; local pocket/interface-only MD is not an equivalent rerun substitute |
| 2026-06-26 | MD 算力收缩决策 | 旧 Slurm chimeric control/chctrl 组 3 reps 已完成；E2 只有 chctrl rep1 证据；candidate full-production 暂停；转为 chimeric 省算力 protocol 调研 + `Gpr2_R59C` / `Gpr3_R167Y` mutant GPR 前测 |
| 2026-07-04 | R1-Z 公开 atom-count 对照 | R1 reduced `chctrl` 可 build/short-run，但 Z-only atom-count delta 仅 `-2.57%`；该实例保留为 evidence point，不作为省算力成功或候选迁移规则；下一步为 route family 选择 |
| 2026-07-05 | WT holo E2 short benchmark | `Gpr2_WT + ASCR18` 100 ps 短时 MD benchmark 完成，作为 mutant GPR 前测资源基线；不作为突变体稳定性或 full-production 收敛结论 |
| 2026-07-05/06 | Mutant GPR local input gate | 两个 mutant system 已从 AF3/package design 推进到 ligand topology scaffold、clean receptor、PPM output、CHARMM-GUI manual submission package；仍不是 runnable package |
| 2026-07-06 | Mutant GPR return workflow | CHARMM-GUI operator packet、return intake、submission preflight、return validator、material-return board 和 outbound request pack 已形成；下一步是 output acquisition + final package review |
| 2026-07-06 | GPR sampling queue and WT rep1 launch | 队列收缩为先完成 `Gpr2_WT + ASCR18` rep1，再做 Gpr2 WT/mut matched analysis；当前只有 rep1 launch-gate/started 证据，尚无 completion archive |

## 版本记录

| 日期 | 版本 | 变更内容 | 触发原因 |
|---|---|---|---|
| 2026-04-11 | v1.0 | 新建：方向背景、调研清单、4 个科学问题、AMD 硬件约束 | docking 完成后机制实证 + 嵌合 Gpa1 升 P0 后稳定性验证需求 |
| 2026-04-12 | v1.1 | 算力节点改为 PI 课题组服务器；移除 AMD ROCm 约束；调研维度 1 简化 | 用户确认本地 AMD 卡不用于 MD |
| 2026-04-12 | v1.2 | 前 3 维度调研完成，生产栈回填；阶段 0 部分勾选；新增前置风险与强制动作 | deep-research skill + 3 并行子代理产出 [研究报告](P0-md-tech-stack-research.md) |
| 2026-04-12 | v1.3 | 后 4 维度调研完成：采样协议 / 分析栈 / 自由能路径 / ascaroside 行动计划全量回填；方法学局限性重写；前置风险扩到 8 条（加 pre-register 体系、CHARMM-GUI 账号提前、seeds ≥ 3）；阶段 0 全勾选 | 第二轮 deep-research 3 并行子代理产出 [研究报告 v2.0](P0-md-tech-stack-research.md) |
| 2026-04-14 | v1.4 | CHARMM-GUI 学术账号审批通过；前置风险 §3 标记已完成 | 外部审批到位 |
| 2026-04-16 | v1.5 | 问题 4 从 3 行概述扩展为完整 chimeric MD 子节（§4.1-4.7）；新增 Phase C1-C5 定义；tech stack §12 GPCR-Gα 文献调研 | P3 Phase 4 完成（Top 3 选定）→ Phase 5 MD 验证需完整技术方案 |
| 2026-04-27 | v1.6 | frontmatter 改为 in_progress；chimeric C1-C5 状态与 Slurm 资源状态校准 | 2026-04-26 chctrl 完成核查 |
| 2026-05-06 | v1.7 | GPCR-Gα tech-stack source audit 回填；作者名/旧引用纠错；Tawfeeq、Memprot、Casiraghi、GPCRsignal 的可迁移范围重写 | operational cutoff 与技术栈来源必须有 DOI/title/method pointer |
| 2026-05-29 | v1.8 | chimeric MD 改为 E2 统一环境 rerun 范围；旧 Slurm 细节改为历史指针；rep1 smoke gate 完成后启动 chctrl rep1 full production | `environments/e2-md-gromacs.md`, `codex/docs/plans/e2-chimeric-md-restart.md` |
| 2026-05-30 | v1.9 | chctrl rep1 checkpoint-gated interrupt, benchmark outcome, and single-job resume routed; current production cap remains one full GPU MD job | `docs/logs/2026-05-30.md`, `codex/docs/plans/e2-chimeric-md-restart.md` |
| 2026-05-30 | v2.0 | 把旧 Slurm RTX 5090 纳入新统一 rerun 体系，但只作为同 pin 验证后的 secondary site；新增站点矩阵和 Slurm gate scripts | `environments/md-production-sites.md`, `codex/docs/plans/chimeric-md-unified-rerun-sites.md` |
| 2026-06-01 | v2.1 | 新增 tiered validation 摘要：100-150 ns 是 full-system early stability gate，不替代 500 ns final production，也不引入局部口袋 production rerun | `codex/docs/plans/e2-chimeric-md-restart.md` |
| 2026-06-26 | v2.2 | frontmatter 改为 compute_triage；chimeric candidate full-production 标记暂停；新增 mutant GPR 前测起点和 E2 共享资源边界 | [决策 005](../decisions/005-md-compute-triage-after-chctrl.md), [2026-06-26 日志](../logs/2026-06-26.md) |
| 2026-07-05 | v2.7-v3.4 | 补充 WT short benchmark 与 mutant GPR local input-gate 指针；详细材料清单回日志、plan 和 analysis package | [2026-07-05 日志](../logs/2026-07-05.md), `../../codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md` |
| 2026-07-06 | v3.5-v3.8 | 补充两个 mutant system 的 PPM/CHARMM-GUI handoff、Gpr3 ASCR3 coordinate layer 和 CHARMM-GUI output work order 指针 | [2026-07-06 日志](../logs/2026-07-06.md), `../../experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_output_work_order_20260706.md` |
| 2026-07-06 | v3.9-v3.12 | 补充 return intake/validator/submission-preflight 指针；当前下一步为人工提交、returned-output intake、final package review | `../../experiments/md-simulation/analysis/mutant_gpr_input_gate_20260705/charmm_gui_submission_preflight_20260706.tsv`, `../logs/2026-07-06.md` |

## 与其他方向的依赖关系

- **输出到**:
  - [P0-molecular-docking](P0-molecular-docking.md): 机制验证与候选 pose 稳定性 → 回填机制结论与置信度
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 嵌合 Gpa1 + Gpr 复合物 MD 验证 → 选定首选嵌合方案
  - [wet-lab-handoff-P0-docking](wet-lab-handoff-P0-docking.md): MD 机制证据可作为湿实验交接的补充材料
- **依赖于**:
  - [P0-molecular-docking](P0-molecular-docking.md): 若重启突变体 MD，候选 pose 必须来自 current refreshed handoff/ratio/IFP release
  - [P3-chimeric-gprotein](P3-chimeric-gprotein.md): 提供嵌合 Gpa1 + Gpr 复合物 AF3 结构作为 MD 初始构象
  - [决策 003](../decisions/003-chassis-yeast-ste2-integration.md): 底盘锁定酵母触发嵌合 Gpa1 验证需求
