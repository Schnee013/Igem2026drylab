# Boukharta et al. (2014) — FEP Alanine Scan GPCR

> **原文**: Boukharta, L., Gutiérrez-de-Terán, H. & Åqvist, J. (2014). Computational Prediction of Alanine Scanning and Ligand Binding Energetics in G-Protein Coupled Receptors. *PLoS Computational Biology*, 10(4), e1003585.
> **DOI**: https://doi.org/10.1371/journal.pcbi.1003585

---

## 核心内容

使用自由能微扰 (FEP) 方法对 NPY Y1 受体进行计算 alanine scanning，预测 13 个突变位点的 ΔΔG，与实验值对比验证。这是 GPCR 领域将 FEP 用于系统性 alanine scan 的早期范例。

---

## 方法学

### 计算流程

1. **结构准备**：NPY Y1 受体同源模型（基于 β1-AR 晶体结构），配体为 BIBP3226
2. **MD 模拟**：GROMACS，OPLS-AA 力场，~5.6 ns per perturbation window
3. **FEP 方案**：
   - 将目标残基渐变为 Ala（侧链消失）
   - 使用 stepwise subperturbation scheme 解决大侧链残基（Phe, Trp, Arg）的收敛问题
   - 每个突变 = 6 独立重复 × 正反两方向 → 取平均
4. **ΔΔG 计算**：ΔΔG = ΔG_bind(WT) - ΔG_bind(mutant)，通过热力学循环

### 关键结果（Table 1）

| 突变 | ΔΔG_exp (kcal/mol) | ΔΔG_calc (kcal/mol) | 误差 |
|------|-------------------|---------------------|------|
| D6.59A | 3.2 | 3.3 ± 0.4 | 0.1 |
| Q3.32A | 2.5 | 2.2 ± 0.5 | 0.3 |
| H6.55A | 1.1 | 0.7 ± 0.5 | 0.4 |
| Y2.64A | 0.4 | 0.6 ± 0.3 | 0.2 |
| ... | | | |

- **平均无符号误差 (MUE)**：0.9 kcal/mol
- **方向预测正确率**：11/13（85%）
- **大效应量（|ΔΔG| > 1.5）全部正确识别**

### Stepwise subperturbation

- 大侧链残基（F, W, R, K）直接 → Ala 收敛差
- 解决方案：分步消除侧链原子（如 Phe → Ala 分 3 步）
- 显著改善 Phe6.55、Trp6.60 等的 FEP 收敛性

---

## 与 Vina ΔΔG 的对比

| 维度 | FEP (本文) | Vina (我们的 pipeline) |
|------|-----------|----------------------|
| 精度 | MUE ~0.9 kcal/mol | ~2-3 kcal/mol |
| 物理模型 | 显式溶剂 + 采样 | 刚性对接 + empirical scoring |
| 计算成本 | 数天/突变（GPU） | 数分钟/突变（CPU） |
| 方向预测 | 85% 正确 | 不确定（信噪比低） |
| 统计误差 | 提供 CI | 需多 seed 估算 |

---

## 关键结论

1. FEP alanine scan 可在 GPCR 同源模型上达到 ~0.9 kcal/mol 精度
2. 即使是「金标准」FEP，误差仍在 0.5-1.0 kcal/mol 量级
3. 大效应量突变（|ΔΔG| > 1.5）比小效应量更可靠预测
4. 接触分析 + ΔΔG 联合验证优于单独使用任一方法

---

## 对本项目的启示

1. **FEP 不可行**：需要 MD 基础设施（GROMACS + GPU），我们没有 — 但了解精度基准有助于设置合理预期
2. **Vina ΔΔG 精度不足**：即使 FEP 精度也只有 ~0.9 kcal/mol；Vina 的 2-3 kcal/mol 误差意味着 |ΔΔG| < 1 的突变效应完全在噪声内
3. **聚焦大效应量**：FEP 和 Vina 都在大效应量时更可靠 → 我们应优先关注 |ΔΔG| > 1.5 的候选
4. **双路径验证**：本文隐含支持接触分析 + 能量联合方法（作者也讨论了结合口袋残基接触模式）
5. **文献先例**：证明在 GPCR 同源模型上做计算 alanine scan 是被认可的方法学
