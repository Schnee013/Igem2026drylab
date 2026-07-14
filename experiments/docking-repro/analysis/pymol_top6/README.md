# PyMOL 湿实验候选可视化素材

湿实验优先候选突变体（Channel A + B 全局 top）的 WT vs Mutant 可视化对比（PI 交付）。

## 目录结构

```
pymol_top6/
├── README.md            # 本文件
├── style_detail.pml     # 细节版样式脚本（聚焦氢键 + 残基 label）
├── style_overview.pml   # 全览版样式脚本（透明 surface + 整体姿态）
├── receptors/           # 8 个受体 PDB（AF3 预测，TM 截断）
│   ├── Gpr2_WT.pdb,       Gpr3_WT.pdb
│   ├── Gpr2_M327A.pdb,    Gpr2_M327D.pdb,   Gpr2_R59F.pdb   # Ch A
│   └── Gpr3_V138R.pdb,    Gpr3_V138T.pdb,   Gpr3_F170N.pdb  # Ch A / Ch B
└── ligands/             # 16 个配体 PDB（Vina Top 1 pose）
    ├── Gpr2_WT_ascr18.pdb,   Gpr2_WT_ascr3.pdb
    ├── Gpr3_WT_ascr18.pdb,   Gpr3_WT_ascr3.pdb
    ├── Gpr2_M327A_ascr18.pdb, Gpr2_M327A_ascr3.pdb
    ├── Gpr2_M327D_ascr18.pdb, Gpr2_M327D_ascr3.pdb
    ├── Gpr2_R59F_ascr18.pdb,  Gpr2_R59F_ascr3.pdb
    ├── Gpr3_V138R_ascr18.pdb, Gpr3_V138R_ascr3.pdb
    ├── Gpr3_V138T_ascr18.pdb, Gpr3_V138T_ascr3.pdb
    └── Gpr3_F170N_ascr18.pdb, Gpr3_F170N_ascr3.pdb
```

**设计取舍**：受体和配体**分开存**（而非合并成 complex PDB）——这样在 PyMOL 里
加载后能独立操作每个对象（单独着色、隐藏、对齐等）。两个 `.pml` 样式脚本用
`polymer.protein` / `organic` 通用选择子，对已加载的任意组合都生效，与对象名
无关。

每个配体 PDB 都是 Vina 输出的 Top 1 pose（MODEL 1），由 `obabel -f 1 -l 1` 抽取
后改写为 `HETATM` 记录，`resname=LIG`, `chain=X`, `resi=901`——这样 PyMOL 的
`organic` 选择子能正确识别。

## 选这 6 个突变体的理由

覆盖 2026-04/05 双通道传感器设计阶段的历史 **Top6** 可视化集合。当前 docking-derived MD 候选与湿实验讨论入口以
[MD 前候选体系清单](../../../../docs/modeling/P0-docking-md-candidate-shortlist.md) 为准；本目录保留为旧 Top6 PyMOL 素材证据。

**Channel A Top 4**（sel_mut < −0.477，ascr#18 偏好传感器）：

| 受体 | 突变 | sel_mut | 机制 | 为什么选 |
|------|------|---------|------|---------|
| Gpr2 | **M327A** | −1.391 | 丢失 ascr3 疏水接触 | Channel A 全表最强 |
| Gpr3 | **V138R** ⭐ | −0.875 | Arg 胍基几何富集 ascr18 | Gpr3 Ch A 最强；盐桥假说待 MD 实证 |
| Gpr2 | **M327D** | −1.089 | 主动引入羧基 | M327 同位点第二路径（vs M327A 对照）|
| Gpr2 | **R59F** | −0.956 | 芳香替换正电 | Gpr2 独立位点 |

**Channel B Top 2**（sel_mut > +0.477，ascr#3 偏好传感器）：

| 受体 | 突变 | sel_mut | 机制 | 为什么选 |
|------|------|---------|------|---------|
| Gpr3 | **V138T** | +1.042 | 小极性侧链保留 ascr3 | Channel B 全表最强；与 V138R 同位点双通道开关 |
| Gpr3 | **F170N** | +0.616 | ECL2 极性替换 | Channel B Gpr3 非 V138 独立位点 |

**不选**的候选：

- F170E / I141A（Ch A 低优先级）——sel 弱于已选 4 条，机制未提供额外信息
- R59A / F170D——与 R59F/F170N 同位点同方向，机制冗余
- Hu2024 实验对照（N60A/R395A/S44A/N56A）：校验用途，不作湿实验候选，详见
  [P0-molecular-docking.md §Pipeline 验证](../../../../docs/modeling/P0-molecular-docking.md#pipeline-验证)

## 使用方法

### 1. 手动加载

在 PyMOL 命令行里，按需 load 对比组合。例：看 Gpr3 V138R vs WT 在 ascr18 下的对比：

```pml
cd /Users/roy/Documents/drylab/experiments/docking-repro/analysis/pymol_top6

load receptors/Gpr3_WT.pdb,       rec_wt
load ligands/Gpr3_WT_ascr18.pdb,  lig_wt_18
load receptors/Gpr3_V138R.pdb,    rec_mut
load ligands/Gpr3_V138R_ascr18.pdb, lig_mut_18

# 叠加突变体到 WT 骨架
align rec_mut, rec_wt
# 把突变体的配体也跟着变换 —— align 只会动 rec_mut 本身，
# 所以需要用 matrix_copy：
matrix_copy rec_mut, lig_mut_18
```

> **提示**：配体是独立对象，`align` 不会自动把它跟着旋转平移。必须手动
> `matrix_copy rec_mut, lig_mut_18` 把 rec_mut 的变换矩阵复制给配体。
> 或者先用 `create complex_mut, rec_mut or lig_mut_18`（临时合体）再 align，
> 然后 split。

### 2. 应用样式

```pml
@style_detail.pml      # 细节版（聚焦氢键 + 残基 label + 云朵表面）
# 或
@style_overview.pml    # 全览版（整体轮廓 + 透明 surface）
```

两个脚本都**不包含 load**，只做样式设置。可以随时切换（先手工 `hide everything; hide labels; hide dashes` 清理再 `@` 新脚本）。

### 3. 出图

```pml
ray 1600 1200
png out/F4_Gpr3_V138R_detail.png, dpi=300
```

### 4. 可视化元素速查

**style_detail.pml**：
- 珍珠灰 cartoon = 所有受体对象（`polymer.protein`）
- 霓虹洋红 + 白/蓝配色 = 所有配体（`organic`）
- 粉色高透明 surface = 每个受体对象的 `{obj}_cloud` 副本
- 金棕 sticks = 4 Å 内含极性原子的残基（`hbond_residues`，含 label）
- 青色粗虚线 = `distance` 对象 `hbonds`，≤3.5 Å，mode=2（仅极性）
- zoom 到 hbond_residues

**style_overview.pml**：
- 珍珠灰 cartoon + 极光蓝 surface（82% 透明）
- 配体球棍（更大 sphere_scale=0.32）
- `orient all` + `zoom all, buffer=2.5`

## PyMOL 文件类型速查

| 扩展名 | 是否原生支持 | 推荐场景 |
|--------|-------------|---------|
| `.pdb`  | ✅ 首选 | 蛋白、配体单独文件，手工编辑 |
| `.pdbqt` | ✅ 支持（当 multi-state 读） | Vina 原始 pose 文件，不用转 |
| `.sdf`  | ✅ 支持 | RDKit/obabel 中间产物 |
| `.mol2` | ✅ 支持 | 带键级/电荷的配体 |
| `.cif`  | ✅ 支持 | AF3 原始输出 |
| `.pml`  | 脚本语言 | 样式/可视化 |
| `.pse`  | 会话存档 | 最后存盘交 PI |

**重要澄清**：PyMOL 不要求"合并 complex PDB"。分别 load 蛋白和配体就是一个复合体——它们共享坐标空间。单独文件反而让你能独立操作每一个对象。

## 重新生成

输入文件变更后（例如重跑 ifp_analysis_mutants 或改 Top 6 清单）：

```bash
conda activate docking
python /Users/roy/Documents/drylab/src/modeling/docking-repro/prep_pymol_top6.py
```

会覆盖 `receptors/` 和 `ligands/` 下的全部 PDB。
