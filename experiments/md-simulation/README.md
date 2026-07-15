# MD 模拟体系 Pre-Registration

> **锁定日期**: 2026-04-12
> **目的**: 在生产计算启动前写死体系清单，防止中途增减导致统计比较不公
> **权威方向文档**: [P0-md-simulation.md](../../docs/modeling/P0-md-simulation.md) v1.3
> **对接数据来源**: [ratio_channel_report.md](../docking-repro/analysis/ratio_channel_report.md)
>
> **2026-06-02 边界**：下方 mutant-holo 8 体系是 2026-04 历史 pre-registration，保留作方法和 provenance 记录，不代表当前生产队列或湿实验推荐。当前 MD 状态看 [docs/INDEX.md](../../docs/INDEX.md) 和 [P0-md-simulation.md](../../docs/modeling/P0-md-simulation.md)。

## 体系清单（8 个 holo）

原 MVP 方案写"7 holo (WT + historical candidate set)"，**修正为 8**：历史候选横跨 Gpr2（3 个）和 Gpr3（3 个），各需独立 WT 对照。

| ID | 受体 | 突变 | 配体 | ΔG(18) | abs sel | 科学问题 | 目录 |
|----|------|------|------|--------|---------|---------|------|
| C1 | Gpr2 | WT | ascr#18 | — | −0.40 | 对照（Gpr2 系列） | `gpr2-wt-ascr18/` |
| C2 | Gpr3 | WT | ascr#18 | — | +0.20 | 对照（Gpr3 系列） | `gpr3-wt-ascr18/` |
| M1 | Gpr2 | M327A | ascr#18 | −6.74 | −1.39 | Q3 pose 稳定性 | `gpr2-M327A-ascr18/` |
| M2 | Gpr2 | M327D | ascr#18 | −6.67 | −1.09 | Q3 pose 稳定性 | `gpr2-M327D-ascr18/` |
| M3 | Gpr2 | R59F | ascr#18 | −6.66 | −0.96 | Q3 pose 稳定性 | `gpr2-R59F-ascr18/` |
| M4 | Gpr3 | V138R | ascr#18 | −6.14 | −0.88 | **Q1 盐桥实证**（最高优先级） | `gpr3-V138R-ascr18/` |
| M5 | Gpr3 | F170E | ascr#18 | −6.25 | −0.50 | **Q2 pose drift + ECL2** | `gpr3-F170E-ascr18/` |
| M6 | Gpr3 | I141A | ascr#18 | −5.19 | −0.59 | Q3 pose 稳定性 | `gpr3-I141A-ascr18/` |

### 可选扩展（不在 MVP 内，需额外算力预算）

| ID | 受体 | 突变 | 配体 | 用途 |
|----|------|------|------|------|
| X1 | Gpr3 | F170E | **ascr#3** | Q2 双配体对照（GLU170 与 ascr3 接触反常） |
| X2 | Gpr2 | WT | — (apo) | "标准"方案需要的 apo 对照 |
| X3 | Gpr3 | WT | — (apo) | "标准"方案需要的 apo 对照 |

### 修改纪律

- 上表 C1–M6 一经锁定，**禁止**在生产计算期间增删
- 扩展体系 X1–X3 需在 MVP 全部完成后单独决策
- 任何修改须在本文件 §变更记录 中注明日期、原因、审批人

## Chimeric Gpa1 体系 Pre-Registration（5 个复合物：4 core + 1 stretch）

> **锁定日期**: 2026-04-16（初始 4 体系）; 2026-04-17 修订（+Ch-4, Ch-3 降为 stretch, Ch-ctrl 改用 AF3）
> **目的**: 嵌合 Gpa1 + Gpr 复合物界面稳定性验证（问题 4，独立于突变体 MD）
> **权威方向文档**: [P0-md-simulation.md](../../docs/modeling/P0-md-simulation.md) §问题 4（协议/指标/判定的唯一权威源）
> **文献依据**: [P0-md-tech-stack-research.md §12](../../docs/modeling/P0-md-tech-stack-research.md)（Tawfeeq 2025 / Mohanty 2025 / Renault 2019 / Velazhahan 2021 等 source-audited 引用）
> **候选选择来源**: [ranking_summary.md](../chimeric-gpa1/analysis/ranking_summary.md)
> **执行计划**: [E2 Chimeric MD Restart Plan](../../codex/docs/plans/e2-chimeric-md-restart.md)

### Core（4 个，必做）

| ID | 受体 | Chimera | ipTM | iPAE | 起始结构 | 科学问题 | 目录 |
|----|------|---------|------|------|---------|---------|------|
| Ch-1 | Gpr3 | AoGpa2-C37 | 0.50 | 23.31 | AF3 `experiments/chimeric-gpa1/af3_predictions/downloads/gpr3_gpa1_aogpa2_c37_complex/` | 全数据集最低 iPAE；主工程路线 Channel B | `chimeric-gpr3-aogpa2-c37/` |
| Ch-2 | Gpr3 | AoGpa2-C15 | 0.50 | 24.82 | AF3 `experiments/chimeric-gpa1/af3_predictions/downloads/gpr3_gpa1_aogpa2_c15_complex/` | C37 vs C15 嫁接长度对比 | `chimeric-gpr3-aogpa2-c15/` |
| Ch-4 | Gpr2 | AoGpa2-C10 | 0.46 | 25.26 | AF3 `experiments/chimeric-gpa1/af3_predictions/downloads/gpr2_gpa1_aogpa2_c10_complex/` | Channel A 覆盖；ipTM 低为 AF3 假阴性（详见执行计划 §Gpr2 偶联评估） | `chimeric-gpr2-aogpa2-c10/` |
| Ch-ctrl | Ste2 | Gpa1-WT | 0.60 | 23.44 | AF3 `experiments/chimeric-gpa1/af3_predictions/downloads/ste2_gpa1_wt_complex/`（PDB 7AD3 Gpa1 缺失 238 残基，改用 AF3 完整结构；7AD3 保留作分析阶段交叉验证） | 阳性对照（Velazhahan 2021 / PDB 7AD3 结构锚点；Mohanty 2025 仅作 Ste2p-Gpa1p interface context） | `chimeric-ste2-gpa1-wt/` |

### Stretch（1 个，GPU 余量时做）

| ID | 受体 | Chimera | ipTM | iPAE | 起始结构 | 科学问题 | 目录 |
|----|------|---------|------|------|---------|---------|------|
| Ch-3 | GprC | AfGasA-C25 | 0.38 | 26.47 | AF3 `experiments/chimeric-gpa1/af3_predictions/downloads/gprc_gpa1_afgasa_c25_complex/` | 唯一 cognate 特异性（Δ=+0.16）；XY≥130 Å box | `chimeric-gprc-afgasa-c25/` |

### 体系组成

- GPCR + Chimeric Gpa1（或 WT Gpa1），**不含** Gβγ / 核苷酸 / 配体
- POPC 膜 + CHARMM-modified TIP3P + 0.15 M KCl
- 估算规模：~200-250k atoms / system（比突变体 MD 的 ~130k atoms 大）

### 采样协议

> 以下为 2026-04-16 锁定快照；权威活文档 → [P0-md-simulation.md §4.3](../../docs/modeling/P0-md-simulation.md)

| 参数 | 值 | 依据 |
|------|-----|------|
| 时长/rep | **500 ns** | Tawfeeq 2025（4×0.5 μs/model；AMBER 栈，非 GROMACS/CHARMM 模板）+ Renault 2019（A2A–Mini-Gs，last 500 ns retained）→ 完整引用见 [§12.6](../../docs/modeling/P0-md-tech-stack-research.md) |
| Reps | **3** (independent seeds) | 最小统计需求 |
| 分析窗口起点 | **100 ns** | AF3 结构需更长松弛期 |
| 总 ns | 4 × 500 × 3 = **6000 ns** | |
| 估算 wall time | 待 E2 A100 smoke / benchmark 后更新；不沿用旧 Slurm node3 估算 | |
| 估算 GPU-days | 待 E2 A100 smoke / benchmark 后更新 | |
| 温度 | 303.15 K | 酵母生长温度 |

### 判定标准

> 以下为 2026-04-16 锁定快照；权威活文档（含完整文献来源）→ [P0-md-simulation.md §4.4](../../docs/modeling/P0-md-simulation.md)

| 指标 | 判定 | 文献来源 |
|------|------|---------|
| α5-helix iRMSD < 3 Å | operational stable band（待查验） | 原 “Bauer 2022” 无 exact pointer；alpha5/eCT 结构背景见 Hara 2012 DOI [`10.1271/bbb.110820`](https://doi.org/10.1271/bbb.110820) 与 Velazhahan 2021 DOI [`10.1038/s41586-020-2994-1`](https://doi.org/10.1038/s41586-020-2994-1) |
| α5-helix iRMSD > 5 Å | operational severe-displacement band（待查验） | 原 “Bauer 2022” 无 exact pointer，暂不承认为权威阈值 |
| BSA 下降 < 20% | operational interface-retention heuristic（待查验） | 当前 driver 使用 [MDTraj `shrake_rupley`](https://mdtraj.readthedocs.io/en/latest/api/generated/mdtraj.shrake_rupley.html)，实现见 [`analyze_bsa.py`](analysis/chctrl/analyze_bsa.py)；20% cutoff 未获权威来源 |
| 接触图 > 50% 保持 | majority-retention heuristic | GPCRsignal/Miszta et al. 2021 DOI [`10.1093/nar/gkab434`](https://doi.org/10.1093/nar/gkab434) 支持 interaction frequency 分析；>50% 非 universal pass cutoff |
| 嫁接连接区 RMSF ≈ WT | 嫁接区无异常 | 项目设计 |

> 2026-04-29 / 2026-05-06 cutoff-source audit：上述 operational cutoff 在补齐 DOI / title / 原文方法段落 / 官方工具文档 exact pointer 前，不得写作权威文献阈值。chctrl 审查见 `results/chimeric-ste2-gpa1-wt/analysis/cutoff_source_audit.md`。

### 修改纪律

- 上表 core 体系（Ch-1/2/4/ctrl）一经锁定，**禁止**在生产计算期间增删
- Stretch 体系（Ch-3）在 core 全部完成后单独决策
- 任何修改须在本文件 §变更记录 中注明日期、原因

## 采样协议

| 参数 | 值 | 依据 |
|------|-----|------|
| 时长/rep | **200 ns** | GPCRmd-2 审稿地板 |
| Reps | **3** (independent seeds) | Welch t-test 最低要求 |
| Equilibration | 分阶段 restraint release（2→60→80→20 ns） | mwSuMD protocol |
| 分析窗口起点 | **50 ns** | AF3 起始非晶体，前 50 ns 扣除 |
| 总 ns | 8 × 200 × 3 = **4800 ns** | 原 7 体系 4200 ns + 1 WT = +600 ns |
| 估算 GPU 天 | ~28（A100 80GB, ~175 ns/day @120k atoms） | |
| 时间步 | 2 fs（不用 HMR 4 fs） | CGenFF 数值稳定性 |
| 增强采样 | 不用（GaMD/metadynamics 不在 MVP scope） | 5 月窗口约束 |

## 初始构象来源

| 组件 | 来源 | 处理 |
|------|------|------|
| 受体 | AlphaFold3 预测 | **必须过 PPM 2.0** 膜定位 + 声明 "inactive-like" |
| 配体 | 对接 best pose（`experiments/docking-repro/results/`） | CGenFF 参数化 via CHARMM-GUI |
| 突变体 | AF3 直接预测突变序列（非 in-silico mutagenesis） | 同上 |
| 膜 | CHARMM-GUI Membrane Builder | 一轮纯 POPC；二轮 POPC:ergosterol 80:20 |
| 水 + 离子 | TIP3P + 0.15 M KCl | CHARMM-GUI 默认 |

## 判定标准

### Q1: V138R 盐桥（M4 vs C2）

| 占比范围 | 判定 | 后续 |
|---------|------|------|
| > 30% | **实证盐桥** | 写入 wiki + handoff |
| 5–30% | 弱/间歇盐桥 | 升级到 500 ns × 5 seeds |
| < 5% | **推翻盐桥假说** | 改为"Arg 胍基特异 VdW" |

测量：ARG138 Nε/NH₁/NH₂ ↔ ascr18 羧基 O，取 min() ≤ 4.0 Å + 角度。

### Q2: F170E pose drift（M5 vs C2）

- ascr#18 pose RMSD 时间序列（相对 t=0）
- GLU170 侧链 χ1/χ2 角度时间序列
- 如有 X1 扩展：ascr#18 vs ascr#3 双配体对比

### Q3: 历史候选 pose 稳定性（M1–M6 vs C1/C2）

- 配体 heavy-atom RMSD（相对 docking pose）
- 结合口袋残基 RMSF
- 关键 HBond 时间序列 + occupancy
- **判定**：RMSD < 3 Å 稳定 → 湿实验高置信度；> 5 Å 大幅 drift → 降低优先级

## 目录结构

```
experiments/md-simulation/
├── README.md                 ← 本文件（体系清单 + 协议）
├── systems/                  # 每个体系一个目录
│   ├── gpr2-wt-ascr18/       # C1
│   ├── gpr2-M327A-ascr18/    # M1
│   ├── gpr2-M327D-ascr18/    # M2
│   ├── gpr2-R59F-ascr18/     # M3
│   ├── gpr3-wt-ascr18/       # C2
│   ├── gpr3-V138R-ascr18/    # M4 ⭐
│   ├── gpr3-F170E-ascr18/    # M5
│   └── gpr3-I141A-ascr18/    # M6
│   ├── chimeric-gpr3-aogpa2-c37/   # Ch-1 (core)
│   ├── chimeric-gpr3-aogpa2-c15/   # Ch-2 (core)
│   ├── chimeric-gpr2-aogpa2-c10/   # Ch-4 (core, Channel A)
│   ├── chimeric-ste2-gpa1-wt/      # Ch-ctrl (core, 阳性对照)
│   └── chimeric-gprc-afgasa-c25/    # Ch-3 (stretch)
├── parameters/               # 配体参数化
│   └── ascr18/               # CGenFF stream + penalty audit
├── analysis/                 # 跨体系分析脚本
└── scripts/                  # Pipeline 通用脚本
```

每个体系目录在 CHARMM-GUI 输出后将包含：

```
system/
├── charmm-gui/    # CHARMM-GUI 输出包（gromacs/）
├── em/            # energy minimization
├── eq/            # NVT + NPT + restraint release
├── prod/          # 生产
│   ├── rep1/
│   ├── rep2/
│   └── rep3/
└── analysis/      # 单体系分析输出
```

## 变更记录

| 日期 | 变更 | 原因 |
|------|------|------|
| 2026-04-12 | 初始锁定 8 体系（修正自 7） | 2 个 WT 对照（Gpr2 + Gpr3） |
| 2026-04-16 | 新增 chimeric Gpa1 体系 pre-registration（4 体系：Ch-1/2/3 + ctrl） | P3 Phase 4 完成（Top 3 选定）→ chimeric MD 路线具体化 |
| 2026-04-17 | +Ch-4 (Gpr2+AoGpa2-C10) 为 core；Ch-3 降为 stretch；Ch-ctrl 起始结构改 AF3（PDB 7AD3 Gpa1 helical domain 缺 238 残基） | Gpr2-AoGpa2 偶联调研 + Channel A 覆盖需求；PDB gap 不适合 MD |
| 2026-05-06 | chimeric MD 文献依据 source audit：Ramasamy→Mohanty、Ranganathan→Renault、Jakowiecki→Miszta；Tawfeeq/Memprot 方法迁移降级 | 作者名纠错与 exact-pointer 规则执行 |
