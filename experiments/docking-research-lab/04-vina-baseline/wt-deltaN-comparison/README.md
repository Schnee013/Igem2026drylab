# Vina docking results inventory

整理日期：2026-08-23

## 目录结构

- `source-archives/`：三个原始 ZIP 的只读留档副本；原件仍保留在 `Downloads`。
- `inputs/`：配体、受体结构及拓扑预测输入，共 291 个有效文件。
- `outputs/`：14 组 AutoDock Vina 对接结果，共 14 个日志、14 个多构象 PDBQT 和 4 张已有二维接触图。
- `interaction-diagrams-2d/`：从“作用图.zip”单独整理出的 4 张二维接触图。

解压时已排除 `__MACOSX`、`.DS_Store` 和 AppleDouble (`._*`) 元数据。三个原始 ZIP 均已通过 `unzip -t` 完整性校验。

## inputs.zip 的内容

### 配体

- 原始 SDF：ascr3（PubChem CID 16066476）、ascr18（PubChem CID 71514784）。
- 去质子化（-1 电荷）版本：每个配体各有 SDF、PDBQT 和 atom-map JSON。

### 受体

- 5 条 FASTA：DAF-37、Gpr2、Gpr3、GprC、SRBC-64。
- AlphaFold2：GPR2 WT、GPR3 WT 的多排名结构、分数和运行记录。
- AlphaFold3：7 个用于对接的 model 0 结构，均有 PDB/PDBQT；包括 DAF-37 WT、GPR2 WT、GPR2 ΔN1–16、GPR3 WT、GPR3 ΔN1–5、GprC WT、SRBC-64 WT。
- 拓扑预测：5 个受体的 Phyre2/MEMSAT-SVM 与 DeepTMHMM 结果。

## outputs.zip 的内容

这是 2 个配体 × 7 个受体构象的完整组合，共 14 组对接。每组含 Vina `.log` 和多 pose `.pdbqt`；其中 4 组另带二维接触 PNG。

各组 pose 数：

| 受体 | ascr3 | ascr18 |
|---|---:|---:|
| DAF-37 WT | 9 | 9 |
| GPR2 WT | 9 | 9 |
| GPR2 ΔN1–16 | 8 | 6 |
| GPR3 WT | 9 | 9 |
| GPR3 ΔN1–5 | 4 | 3 |
| GprC WT | 9 | 9 |
| SRBC-64 WT | 9 | 9 |

## 最佳 pose 的 Vina affinity

单位为 kcal/mol；数值越负通常表示该打分函数下越有利，但不能直接视为实验结合自由能。

| 受体 | ascr3 | ascr18 |
|---|---:|---:|
| DAF-37 WT | -5.916 | -6.324 |
| GPR2 WT | -5.184 | -5.606 |
| GPR2 ΔN1–16 | -4.178 | -3.855 |
| GPR3 WT | -6.092 | -5.898 |
| GPR3 ΔN1–5 | +4.937 | +7.667 |
| GprC WT | -7.215 | -7.435 |
| SRBC-64 WT | -6.916 | -7.030 |

当前打分最优的是 GprC WT–ascr18（-7.435），其次是 GprC WT–ascr3（-7.215）和 SRBC-64 WT–ascr18（-7.030）。GPR3 ΔN1–5 的两个最佳分数均为正，需优先检查结构、口袋位置、网格和空间冲突，暂不宜作有利结合解释。

## “作用图.zip”的内容

共 4 张 pose 1 二维接触图：

- GprC WT–ascr3
- GprC WT–ascr18
- GPR3 ΔN1–5–ascr3
- GPR3 ΔN1–5–ascr18

SHA-256 比对显示，这 4 张图与 `outputs/` 中对应复合物附带的 4 张 PNG 完全相同；此处单独汇总，便于后续二维分析。

其中源文件 `gprc_wt_model_0-poses_ascr3_deprotonated-pose1.png` 的命名多了一个 `poses_`，现保留原名以维持溯源。

## PyMOL 分析入口

三维分析应成对载入 `inputs/receptors/af3/pdb/` 中对应受体的 `fold_*_model_0.pdb`，以及 `outputs/` 中对应的 `poses_*.pdbqt`。优先比较 pose 1，并进一步检查口袋残基、极性接触、疏水接触、配体埋藏程度，以及 WT/ΔN 截短体的构象差异。二维接触图应与相同复合物的 pose 1 逐项核对。
