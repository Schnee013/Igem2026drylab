# Trott & Olson 2010 — 文献总结

> **完整标题**: AutoDock Vina: Improving the Speed and Accuracy of Docking with a New Scoring Function, Efficient Optimization, and Multithreading
> **期刊**: Journal of Computational Chemistry, Vol. 31, No. 2, pp. 455–461
> **DOI**: 10.1002/jcc.21334
> **作者**: Oleg Trott, Arthur J. Olson
> **机构**: Department of Molecular Biology, The Scripps Research Institute, La Jolla, California
> **接收/接受**: 2009年3月3日收稿，2009年4月21日接受；2009年6月4日在线发表

---

## 核心发现（5–10 bullets，含数据）

- AutoDock Vina 相比 AutoDock 4（实验室前代软件）速度提升约两个数量级（~100×），在 190 个蛋白–配体复合物测试集上单线程平均耗时 8.41 min vs. AutoDock 521.85 min，八线程并行进一步降至 1.16 min。
- 姿势预测精度显著提升：Vina 在 190 个测试复合物中 78% 达到 RMSD < 2 Å，而 AutoDock 4.0.1 仅为 49%（Figure 4）。
- 评分函数从 AutoDock 的 physics-based 力场改为混合经验/知识势（inspired by X-score），包含 steric（gauss₁、gauss₂、repulsion）、hydrophobic 和 hydrogen bonding 五个加权项（Table 1）；参数权重通过 PDBbind 训练集回归得到，并非全从头推导。
- 优化算法采用 Iterated Local Search Global Optimizer，局部优化使用 Broyden-Fletcher-Goldfarb-Shanno（BFGS）准牛顿法（基于梯度），兼顾探索效率与精度。
- 评分函数定义在原子对之间的 surface distance（$d_{ij} = r_{ij} - R_i - R_j$），交互函数在 $r_{ij} = 8$ Å 截止；氢原子不参与显式原子类型分配，受体和配体氢原子均被视为氢键供体。
- 预测自由能采用 conformation-independent 惩罚项修正可旋转键柔性：$g(c_{\text{inter}}) = c_{\text{inter}} / (1 + wN_{\text{rot}})$，其中 $N_{\text{rot}}$ 为活性可旋转键数。
- 程序自动计算 grid maps、聚类对接结果，无需用户手动干预中间步骤，兼容 AutoDock 4 的 PDBQT 格式。
- 多线程支持通过 C++ Boost::Thread 实现，在多核 CPU（测试机器为两块 2.66 GHz Xeon 四核）上自动并行多次独立随机搜索，合并后聚类输出。
- 自由能预测相关性：Figure 7 显示 Vina 与实验 ΔG 的散点分布与 AutoDock 整体相似，但在中等可旋转键数量的配体上表现更稳定（RMSD 随旋转键数量增加上升幅度较 AutoDock 小，Figure 3）。

---

## 实验方法（表格）

| 项目 | 内容 |
|------|------|
| 测试数据集 | PDBbind 190 个蛋白–配体复合物（与 AutoDock 4 训练集相同） |
| 对照软件 | AutoDock 4.0.1（Lamarckian 遗传算法，25 million evaluations × 50 runs） |
| 受体处理 | 受体视为刚体（rigid receptor） |
| 配体处理 | 配体视为柔性分子（flexible ligand），活性可旋转键数 0–32 |
| 搜索空间 | 以实验结合构象质心为基准，各维度扩展 10 Å + 随机一维再扩展 5 Å，最小 22.5 Å |
| 精度评价指标 | RMSD（预测最优构象 vs. 实验结合构象），阈值 2 Å |
| 速度评价 | 单次对接平均耗时（min/complex），机器：双 Xeon E5430 四核 2.66 GHz |
| AutoDock 聚类 | AutoDock Tools 脚本，取最大簇作为预测结合构象 |
| 评分函数训练 | PDBbind 数据集（非本文 190 个测试集），X-score 框架线性回归 |

---

## 关键数据（分小节）

### 速度对比（Figure 5）

| 软件 | 平均时间（min/complex） |
|------|------------------------|
| AutoDock 4.0.1 | 521.85（不含 AutoGrid 时间） |
| Vina 单线程（cpu=1） | 8.41 |
| Vina 八线程（cpu=8） | 1.16 |

速度提升：单线程约 **62×**，八线程约 **450×**。

### 姿势预测精度（Figure 4）

| 软件 | RMSD < 2 Å 比例 |
|------|----------------|
| AutoDock 4.0.1 | 49%（~93/190） |
| Vina | 78%（~148/190） |

### 评分函数权重（Table 1）

| 权重 | 项 |
|------|----|
| −0.0356 | gauss₁ |
| −0.00516 | gauss₂ |
| 0.840 | Repulsion |
| −0.0351 | Hydrophobic |
| −0.587 | Hydrogen bonding |
| 0.0585 | $N_{\text{rot}}$（可旋转键惩罚） |

### 评分函数公式要点

- 总评分：$c = c_{\text{inter}} + c_{\text{intra}}$（分子间 + 分子内贡献之和）
- 预测自由能：$s_1 = g(c_1 - c_{\text{intra1}}) = g(c_{\text{inter1}})$
- 截止距离：$r_{ij} = 8$ Å；surface distance $d_{ij} = r_{ij} - R_i - R_j$
- gauss₁：$e^{-(d/0.5\text{Å})^2}$；gauss₂：$e^{-(d-3\text{Å})/2\text{Å})^2}$
- Repulsion：$d^2$（当 $d < 0$），否则 0
- Hydrophobic：1（$d < 0.5$ Å），0（$d > 1.5$ Å），线性插值中间段
- H-bond：1（$d < −1$ Å），0（$d > 0$），线性插值中间段

---

## 与项目的关系

iGEM 2026 干实验使用 AutoDock Vina 对 GprC、Gpr2/Gpr3 等 GPCR 受体与 ascaroside 配体（ascr#18 等）进行两阶段分子对接。

本文是 AutoDock Vina 的原始方法论来源，提供以下关键依据：

1. **评分函数解释**：项目中报告的 Vina 对接 ΔG 值（单位 kcal/mol）由本文 Table 1 五项加权和决定，其中氢键（−0.587）和疏水项（−0.0351）是主导亲和力来源，可解释 IFP 分析中氢键/疏水接触与 ΔG 的对应关系。
2. **精度参考基准**：以 RMSD < 2 Å 作为姿势预测成功的判据（本文建立此标准），适用于项目复现实验结果的验证。
3. **可旋转键与精度**：Figure 3 显示可旋转键越多 RMSD 离散度越大；ascaroside 配体如有较多可旋转键时，应关注此不确定性。
4. **多线程参数**：项目 `run_multiseed.py` 中使用的 `--cpu` 参数对应本文 cpu=8 的并行策略，可合理加速大批量对接。
5. **受体刚性假设**：Vina 默认受体刚性，项目的 GPCR 对接结果受此限制，任何构象柔性效应需通过 MD 后处理或柔性侧链设置弥补。

---

## 关键引用（3–8条）

1. **Trott O, Olson AJ** (2010). AutoDock Vina: Improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. *J Comput Chem* **31**(2): 455–461. DOI: 10.1002/jcc.21334
   — 本文自身（方法论基础引用）

2. **Morris GM et al.** (AutoDock 4, 参考文献 2 in original) — Vina 的前代软件，本文主要对照基准。

3. **Wang R et al.** (X-score, 参考文献 8/9 in original) — Vina 评分函数设计的主要灵感来源，PDBbind 数据库作者。

4. **Liu M, Wang S** (MFCD, 参考文献 16/17 in original) — Iterated Local Search Global Optimizer 的原型，Abagyan et al. 方法相关。

5. **Huey R et al.** (AutoDock Tools / AutoGrid, 参考文献 4 in original) — Vina 兼容的辅助工具链（PDBQT 格式、AutoGrid 前处理），项目 `prepare_receptor.py` 使用 ADFR/AutoDockTools 与此相关。

6. **Nocedal J, Wright SJ** (BFGS 准牛顿法，参考文献 19 in original) — 局部优化算法数学基础。
