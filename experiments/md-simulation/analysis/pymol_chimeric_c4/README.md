# PyMOL 嵌合 Gpa1 C4 体系可视化素材

Phase C4（生产 MD）4 个核心体系的起始结构（AF3 预测 + PPM2 膜取向）PyMOL 可视化素材。

## 目录结构

```
pymol_chimeric_c4/
├── README.md                        # 本文件
├── Ch1_Gpr3_AoGpa2_C37.pdb          # Ch-1: Gpr3 + AoGpa2-C37（主工程路线 Channel B）
├── Ch2_Gpr3_AoGpa2_C15.pdb          # Ch-2: Gpr3 + AoGpa2-C15（嫁接长度对比）
├── Ch4_Gpr2_AoGpa2_C10.pdb          # Ch-4: Gpr2 + AoGpa2-C10（Channel A）
└── Chctrl_Ste2_Gpa1_WT.pdb          # Ch-ctrl: Ste2 + Gpa1-WT（阳性对照）
```

每个 PDB 含两条链：`chain A` = GPCR，`chain B` = Gα（嵌合或 WT）。

**结构来源**：AF3 `model_0`（ranking_score 最高）→ MMCIFParser → 链拆分 → HIS→HSD →
PPM2 2.0 膜取向（`_submit.pdb`）。即 MD 真正起始的坐标，不是 AF3 原始取向。

参考上游脚本：[../../scripts/prepare_chimeric_structures.py](../../scripts/prepare_chimeric_structures.py) · 上游 PDB 全集：[../../structures/chimeric/](../../structures/chimeric/)

## 选这 4 个体系的理由

对应 [../../README.md §Chimeric Gpa1 体系 Pre-Registration](../../README.md)
的 Core 4 体系（Ch-3 GprC×AfGasA-C25 为 stretch，余量时再做）：

| ID | 受体 | Chimera | ipTM | iPAE | 科学问题 |
|------|------|---------|------|------|---------|
| Ch-1 | Gpr3 | AoGpa2-C37 | 0.50 | 23.31 | 全数据集最低 iPAE；主工程路线 Channel B |
| Ch-2 | Gpr3 | AoGpa2-C15 | 0.50 | 24.82 | C37 vs C15 嫁接长度对比 |
| Ch-4 | Gpr2 | AoGpa2-C10 | 0.46 | 25.26 | Channel A 覆盖；ipTM 低为 AF3 假阴性 |
| Ch-ctrl | Ste2 | Gpa1-WT | 0.60 | 23.44 | 阳性对照（Velazhahan 2021 + Ramasamy 2025） |

> 候选选择依据权威源：[../../../chimeric-gpa1/analysis/ranking_summary.md](../../../chimeric-gpa1/analysis/ranking_summary.md)

## 使用方法

### 1. 单体系加载（看某一个复合物）

```pml
cd /Users/roy/Documents/drylab/experiments/md-simulation/analysis/pymol_chimeric_c4
load Ch1_Gpr3_AoGpa2_C37.pdb, ch1

# 按链着色：GPCR 一色，Gα 另一色
color cyan, ch1 and chain A
color orange, ch1 and chain B
show cartoon
```

### 2. 跨体系对比（例：Ch-1 vs Ch-2，同受体不同嫁接长度）

```pml
load Ch1_Gpr3_AoGpa2_C37.pdb, c37
load Ch2_Gpr3_AoGpa2_C15.pdb, c15

# 对齐 GPCR 骨架（chain A），看 Gα（chain B）姿态差异
align c15 and chain A, c37 and chain A
color cyan, c37 and chain A; color salmon, c37 and chain B
color lightblue, c15 and chain A; color yellow, c15 and chain B
show cartoon
```

### 3. 看界面（α5-helix ↔ GPCR intracellular）

```pml
# 以 Ch-1 为例：Gα 的 α5-helix = chain B C-terminal ~20 残基
select alpha5, ch1 and chain B and resi 453-472
select icl_pocket, byres (ch1 and chain A) within 5 of alpha5
show sticks, alpha5 or icl_pocket
zoom alpha5
```

> α5-helix 边界参考：Bauer 2022（iRMSD 判据）和 [../../README.md §判定标准](../../README.md)。
> 实际 Gα C 末端残基号以各体系 `chain B` 最后 ~20 残基为准（不同嵌合体长度不同）。

## 与 docking pymol_top6 的差异

| 维度 | `docking-repro/analysis/pymol_top6/` | 本目录 |
|------|-------------------------------------|--------|
| 用途 | 湿实验候选突变体对接 pose 可视化 | C4 生产 MD 起始复合物可视化 |
| 内容 | 受体 PDB + 配体 PDB 分开存 | 受体 + Gα 复合物（单 PDB 双链） |
| 预设样式脚本 | `style_detail.pml` / `style_overview.pml` | **无**（按需手写） |
| 坐标系 | AF3 原始取向 + TM 截断 | AF3 预测 + PPM2 2.0 膜取向（全长） |

## 重新生成

起始结构源文件变更后（例如重跑 `prepare_chimeric_structures.py`）：

```bash
cd /Users/roy/Documents/drylab/experiments/md-simulation/analysis/pymol_chimeric_c4
cp ../../structures/chimeric/Ch1_Gpr3_AoGpa2_C37_submit.pdb    Ch1_Gpr3_AoGpa2_C37.pdb
cp ../../structures/chimeric/Ch2_Gpr3_AoGpa2_C15_submit.pdb    Ch2_Gpr3_AoGpa2_C15.pdb
cp ../../structures/chimeric/Ch4_Gpr2_AoGpa2_C10_submit.pdb    Ch4_Gpr2_AoGpa2_C10.pdb
cp ../../structures/chimeric/Chctrl_Ste2_Gpa1_WT_submit.pdb    Chctrl_Ste2_Gpa1_WT.pdb
```
