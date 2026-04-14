# MD 模拟体系 Pre-Registration

> **锁定日期**: 2026-04-12
> **目的**: 在生产计算启动前写死体系清单，防止中途增减导致统计比较不公
> **权威方向文档**: [P0-md-simulation.md](../../docs/modeling/P0-md-simulation.md) v1.3
> **对接数据来源**: [ratio_channel_report.md](../docking-repro/analysis/ratio_channel_report.md)

## 体系清单（8 个 holo）

原 MVP 方案写"7 holo (WT + Top 6)"，**修正为 8**：Top 6 横跨 Gpr2（3 个）和 Gpr3（3 个），各需独立 WT 对照。

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

### Q3: Top 6 pose 稳定性（M1–M6 vs C1/C2）

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
