# Eberhardt et al. 2021 — 文献总结

> **完整标题**: AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings
> **期刊**: Journal of Chemical Information and Modeling, 2021, 61, 3891–3898
> **DOI**: https://doi.org/10.1021/acs.jcim.1c00203
> **作者**: Jerome Eberhardt\*, Diogo Santos-Martins†, Andreas F. Tillack, Stefano Forli\*
> **机构**: Department of Integrative Structural and Computational Biology, Scripps Research, La Jolla 92037, California, United States
> **接收/发表**: Received February 22, 2021 / Published July 19, 2021

---

## 核心发现（5-10 bullets，含数据）

- **AutoDock4.2 scoring function 移植**：将 AD4 评分函数（van der Waals、静电、氢键、去溶剂化、熵惩罚）集成进 Vina，使 Vina 可使用与 AutoDock4 完全相同的 MC/BFGS 搜索引擎评估 AD4 能量景观，速度比 AD4 原生程序快最多 100 倍。
- **AD4 评分平均用时约为 Vina 评分的 3×**：由于 AD4 需要对每个移动原子插值多张 grid map，计算开销更大。
- **新原子类型扩展**：增加了 AD4 原子类型（含 CGe、CG0–3 用于大环），同时支持显式水分子对接（hydrated docking）所需的 W 类型，以及锌配位原子类型。
- **Macrocycle（大环分子）对接**：将 AD4 专用的大环构象采样方法（断键→虚拟线性势）移植到 Vina，在 D3R Grand Challenge 4 BACE-1 数据集（19 个大环）复现测试中，RMSD 中位数 2.53 Å（Vina 评分）vs 1.74 Å（AD4 评分）。
- **Hydrated Docking（显式水分子对接）**：将 HSP90 显式水分子对接协议移植到 Vina，使用 AD4 评分函数，成功率与原 AD4 协议可比，平均 RMSD 5.12–4.56 Å。
- **Simultaneous Multiple Ligand Docking**：新增 `--batch` 选项，可同时加载多个配体文件，无需重复加载受体和 grid map，显著提升高通量虚拟筛选效率。
- **设置评估次数上限 `--max_evals`**：新增参数，等价于 AD4 的 `ga_num_evals`，给予用户对搜索计算量更精细的控制。
- **虚拟筛选基准（DUD-E，102 靶标，22,840 actives + 1,388,885 decoys）**：Vina 与 AD4 评分函数表现总体相当；平均 AUC 分别为 0.72±0.12（Vina）和 0.70±0.12（AD4），BEDROC 分别为 0.26±0.15 和 0.25±0.17，EF(1%) 分别为 9.70±9.43 和 9.70±10.60；晶体姿势复现率（top 1，RMSD<2 Å）Vina 为 68%，AD4 为 68%（BACE-1 数据集）。
- **Python bindings**：实现与 CPython 语言规范兼容的 `from vina import Vina` 接口，由 Simplified Wrapper and Interface Generator (SWIG) 自动生成，支持在任意 Python 管线中配置和调用完整对接功能。

---

## 实验方法（表格）

| 方法/模块 | 说明 |
|-----------|------|
| 搜索算法 | Monte-Carlo (MC) iterated local search + BFGS 梯度优化（Vina 原有） |
| 评分函数 A | Vina scoring function（van der Waals-like 势 + 两个 Gaussian + 氢键 + 扭转熵） |
| 评分函数 B | AutoDock4.2 scoring function（物理场：vdW + 静电 + 方向性氢键 + 去溶剂化 + 熵惩罚）；从 AMBER 力场衍生 |
| Grid map | AD4 地图由 AutoGrid 预计算后加载；Vina 地图在运行时动态计算（两者均可通过 Vina 1.2 使用） |
| 大环对接 | 断开可旋转键 → 线性势恢复（linear potential）→ MC/BFGS 搜索 → 闭环构象 |
| 显式水分子对接 | 水分子作为特殊小分子附加到配体坐标；使用 HSP90-水分子-配体组合体验证 |
| 虚拟筛选数据集 | DUD-E（102 靶标）、D3R Grand Challenge 4 BACE-1 数据集（19 大环） |
| 姿势评估指标 | RMSD（< 2 Å / < 1 Å / < 0.5 Å 判断成功）；AUC、BEDROC（α=20）、EF(1%) |
| Python 接口 | SWIG 自动生成；`from vina import Vina`，支持 set_receptor / compute_vina_maps / dock / write_poses 等 |

---

## 关键数据

### BACE-1 大环对接（Table 1，19 个大环，D3R Grand Challenge 4）

| 评分函数 | n_exhaustiveness | RMSD median (Å) | 成功率（top 1，RMSD<2.5 Å）|
|----------|-----------------|-----------------|---------------------------|
| AD4      | 8               | 1.74            | ~64%（参考 Table 1）|
| Vina     | 8               | 2.53            | ~50%（参考 Table 1）|

- 线性势参数（linear potential）：50 kcal/mol/Å；比 AD4 默认的 25 kcal/mol/Å 更强，提供更好的键闭合质量。

### 虚拟筛选（DUD-E，Figure 3）

| 指标 | Vina | AD4 |
|------|------|-----|
| AUC | 0.72 ± 0.12 | 0.70 ± 0.12 |
| BEDROC (α=20) | 0.26 ± 0.15 | 0.25 ± 0.17 |
| EF (1%) | 9.70 ± 9.43 | 9.70 ± 10.60 |

- AD4 在 BEDROC 指标上对以下靶标表现优于 Vina：*pur2, fpps, tryb1, xiap, s3*。
- 两种评分函数对 25/102 靶标（top 1）的 RMSD 均 < 2 Å，前 3 pose 成功率 Vina 68%、AD4 68%。

### 姿势精度（crystal pose reproduction，BACE-1）

- top 1 成功（RMSD < 2 Å）：Vina 54%，AD4 68%
- top 1 成功（RMSD < 1 Å）：Vina 27%，AD4 46%
- top 3 成功（RMSD < 2 Å）：Vina ~68%，AD4 ~76%（Figure 2）

### Python 最简示例（论文 Figure 4）

```python
from vina import Vina
v = Vina()
v.set_receptor("protein.pdbqt")
v.set_ligand_from_file("ligand.pdbqt")
v.compute_vina_maps([0., 0., 0.], [30, 30, 30])
v.dock(exhaustiveness=32)
v.write_poses("docking_results.pdbqt")
```

---

## 与项目的关系

本项目（iGEM 2026 干实验）直接使用 AutoDock Vina 1.2.x 进行 GprC/Gpr3 与配体（如 ascr#18）的分子对接，并通过 Python bindings 驱动批量运行和多轮对接脚本。以下是本文与项目的具体对应关系：

1. **Python bindings**：项目中的 `run_multiseed.py` 等脚本均依赖 `from vina import Vina` 接口，正是本文所描述的 SWIG 实现。
2. **评分函数选择**：项目目前使用 Vina 默认评分函数。本文的基准数据（AUC/BEDROC/EF/姿势RMSD）为理解两种评分函数的适用场景提供了参考——如需更高晶体姿势复现率可考虑切换至 AD4 评分。
3. **`--exhaustiveness` 与 `--max_evals`**：项目使用多 seed 策略（run_multiseed），与本文描述的搜索控制参数直接相关；`exhaustiveness=32` 是论文验证 hydrated docking 采用的参数值。
4. **Grid map 加载机制**：本文明确说明 Vina 1.2 同时支持运行时动态计算地图（Vina 模式）和加载 AutoGrid 预计算地图（AD4 模式），后者与项目中 `prepare_receptor.py` 的 ADFR 工作流一致。
5. **Batch docking**：本文新增的 `--batch` 功能可提升未来多配体高通量筛选效率，与项目后续虚拟筛选规划相关。

---

## 关键引用（原文参考文献编号）

1. **[1] Trott & Olson 2010** — AutoDock Vina 原始论文（搜索算法、评分函数）
2. **[3] Santos-Martins et al. 2020** — AutoDock-GPU，AD4 评分函数的 GPU 加速实现
3. **[12] Forli et al. 2012** — AutoDock4 大环柔性对接原始方法
4. **[14] Forli & Olson 2012** — 显式水分子对接（hydrated docking）原始方法
5. **[30] Santos-Martins et al. 2019** — D3R Grand Challenge 4 用 AutoDock-GPU 对接 BACE-1
6. **[36] DUD-E 数据集** — Mysinger et al. 2012，虚拟筛选基准数据集
7. **[38] Nguyen et al. 2019** — Vina 更准确姿势但 AD4 评分更优的对照研究
