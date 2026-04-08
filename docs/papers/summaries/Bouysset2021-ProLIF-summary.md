# Bouysset & Fiorucci (2021) — ProLIF 工具

> **原文**: Bouysset, C. & Fiorucci, S. (2021). ProLIF: a library to encode molecular interactions as fingerprints. *Journal of Cheminformatics*, 13, 72.
> **DOI**: https://doi.org/10.1186/s13321-021-00548-6

---

## 核心内容

ProLIF (Protein-Ligand Interaction Fingerprints) 是一个 Python 库，从分子对接 pose 或 MD 轨迹中自动计算蛋白-配体交互指纹。支持 14 种交互类型，基于 MDAnalysis + RDKit 后端，可直接读取 Vina PDBQT 输出。

---

## 支持的交互类型（Table 2）

| 交互类型 | 距离阈值 | 角度阈值 |
|---------|---------|---------|
| Hydrophobic | ≤ 4.5 Å | — |
| HBDonor / HBAcceptor | ≤ 3.5 Å | D-H···A ≥ 130° |
| Cation-π / π-Cation | ≤ 4.5 Å | 角度 ≤ 30° |
| π-Stacking (Face/Edge) | ≤ 5.5 Å | 面/边角度阈值 |
| Anionic / Cationic | ≤ 4.5 Å | — |
| Metal coordination | ≤ 2.8 Å | — |
| VdWContact | ≤ VdW + 0.5 Å | — |

距离和角度阈值可自定义。使用 SMARTS 模式（Table 3）检测功能基团。

---

## 使用方式

### 基本用法（对接 pose）

```python
import prolif as plf
import MDAnalysis as mda

# 读取受体和对接 pose
u = mda.Universe(receptor_pdb, ligand_pose_pdbqt)
lig = u.select_atoms("resname LIG")
prot = u.select_atoms("protein")

fp = plf.Fingerprint()
fp.run(u.trajectory[0:1], lig, prot)

# 转为 DataFrame
df = fp.to_dataframe()
```

### 可视化

- **LigNetwork** (Fig 1)：交互式 2D 网络图，显示配体-残基连接及交互类型
- **Heatmap**：残基 × 交互类型矩阵，可跨配体/跨帧比较
- 支持导出为 Pandas DataFrame，便于下游分析

---

## 案例研究

### Case 1: 5-HT1B GPCR-配体分析
- 15 个共晶结构的 IFP 比较
- 聚类分析揭示不同化学骨架的共同接触模式
- **直接相关**：演示了跨配体 IFP 比较方法

### Case 2: Rhodopsin 蛋白-蛋白相互作用
- 证明 ProLIF 也可分析 PPI（非小分子），扩展性好

### Case 3: β2-G 蛋白耦合
- MD 轨迹分析，展示时间维度的接触变化

---

## 对本项目的启示

1. **直接适用**：ProLIF 可读取我们的 Vina PDBQT 输出（receptor PDB + ligand pose PDBQT）
2. **差异分析**：对 GprC×ascr18 vs GprC×ascr3 生成 IFP，差集即选择性候选残基
3. **可视化**：LigNetwork 图可直接用于 iGEM wiki / 论文展示
4. **BW 编号支持**：通过自定义残基映射，可将 PDB 残基号转为 BW 编号
5. **阈值可调**：如默认阈值产生太多/太少接触，可微调距离参数

### 实施注意事项

- 需要将 PDBQT pose 转为 MDAnalysis 可读格式（ProLIF 内置支持）
- 受体需使用 PDB 格式（含完整原子类型），配体 pose 可用 PDBQT
- 安装：`conda install -c conda-forge prolif` 或 `pip install prolif`
- 依赖：MDAnalysis, RDKit（均可通过 conda-forge 安装）
