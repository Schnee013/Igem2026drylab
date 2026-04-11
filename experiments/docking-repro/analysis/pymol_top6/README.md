# PyMOL Top 6 可视化素材

Top 6 突变体的 WT vs Mutant 可视化对比（PI 交付）。

## 目录结构

```
pymol_top6/
├── README.md            # 本文件
├── style_detail.pml     # 细节版样式脚本（聚焦氢键 + 残基 label）
├── style_overview.pml   # 全览版样式脚本（透明 surface + 整体姿态）
├── receptors/           # 8 个受体 PDB（AF3 预测，TM 截断）
│   ├── Gpr2_WT.pdb,       Gpr3_WT.pdb
│   ├── Gpr2_M327A.pdb,    Gpr2_M327D.pdb,   Gpr2_R59F.pdb
│   └── Gpr3_V138R.pdb,    Gpr3_F170E.pdb,   Gpr3_I141A.pdb
└── ligands/             # 16 个配体 PDB（Vina Top 1 pose）
    ├── Gpr2_WT_ascr18.pdb,   Gpr2_WT_ascr3.pdb
    ├── Gpr3_WT_ascr18.pdb,   Gpr3_WT_ascr3.pdb
    ├── Gpr2_M327A_ascr18.pdb, Gpr2_M327A_ascr3.pdb
    ├── Gpr2_M327D_ascr18.pdb, Gpr2_M327D_ascr3.pdb
    ├── Gpr2_R59F_ascr18.pdb,  Gpr2_R59F_ascr3.pdb
    ├── Gpr3_V138R_ascr18.pdb, Gpr3_V138R_ascr3.pdb
    ├── Gpr3_F170E_ascr18.pdb, Gpr3_F170E_ascr3.pdb
    └── Gpr3_I141A_ascr18.pdb, Gpr3_I141A_ascr3.pdb
```

**设计取舍**：受体和配体**分开存**（而非合并成 complex PDB）——这样在 PyMOL 里
加载后能独立操作每个对象（单独着色、隐藏、对齐等）。两个 `.pml` 样式脚本用
`polymer.protein` / `organic` 通用选择子，对已加载的任意组合都生效，与对象名
无关。

每个配体 PDB 都是 Vina 输出的 Top 1 pose（MODEL 1），由 `obabel -f 1 -l 1` 抽取
后改写为 `HETATM` 记录，`resname=LIG`, `chain=X`, `resi=901`——这样 PyMOL 的
`organic` 选择子能正确识别。

## 选这 6 个突变体的理由

全部来自 P0 分子对接 **Tier 1**（ΔΔG_sel ≤ −0.48，>3σ 噪声），覆盖**两条受体**、
**两种机制路径**，直接对应 [wet-lab-handoff-P0-docking.md](../../../../docs/modeling/wet-lab-handoff-P0-docking.md)
的湿实验推荐清单：

| 受体 | 突变 | abs sel | ΔΔG_sel | 机制 | 为什么选 |
|------|------|---------|---------|------|---------|
| Gpr2 | **M327A** | −1.39 | −0.987 | 丢失 ascr3 相互作用 | Tier 1 最强，纯 Ala 机制最干净 |
| Gpr2 | **M327D** | −1.09 | −0.685 | 主动引入负电 | 同位点两条路径对照（vs M327A）|
| Gpr2 | **R59F**  | −0.96 | −0.552 | 芳香替换正电 | Gpr2 非 M327 的独立位点 |
| Gpr3 | **V138R** ⭐ | −0.88 | **−1.070** | Arg 胍基几何 | ΔΔG_sel 全表最负；Gpr3 首次穿透噪声；盐桥假说（待 MD 证）|
| Gpr3 | **F170E** | −0.50 | −0.696 | ECL2 酸性改造 | F170E + F170D 双双入 Tier 1 |
| Gpr3 | **I141A** | −0.59 | −0.786 | 疏水口袋松弛 | Gpr3 非 V138 的独立位点 |

**不选**的候选：
- R59A / F170D（Tier 1 P4/P8）——与 R59F/F170E 同位点同方向，机制冗余
- Hu2024 实验对照：N60A (N2.57)、R395A (R6.45)、S44A (S2.41) 为真阳性对照，全部落 Tier 4；N56A (N2.53) 是 Hu2024 阴性对照（strain 13/14 "无影响"），但在本 pipeline 中也落 Tier 4（假阳性）。均不作为湿实验候选，校验用途详见 [P0-molecular-docking.md §Pipeline 验证](../../../../docs/modeling/P0-molecular-docking.md#pipeline-验证)

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
