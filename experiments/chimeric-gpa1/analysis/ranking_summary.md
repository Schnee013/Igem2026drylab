# AF3 嵌合 Gpa1 排名分析

> 生成时间: 2026-04-14

## 1. 单体折叠质量 (Batch A + B)

| 嵌合体 | 全局 pLDDT | C-term pLDDT | ΔpLDDT vs WT | pTM | ranking_score | disorder |
|--------|-----------|-------------|-------------|-----|-------------|----------|
| Gpa1-AoGpa2-C5 | 75.84 | 77.17 | +0.30 | 0.75 | 0.83 | 0.16 |
| Gpa1-AoGpa2-C10 | 75.76 | 74.7 | +0.22 | 0.74 | 0.83 | 0.18 |
| Gpa1-WT | 75.54 | — | +0.00 | 0.74 | 0.83 | 0.17 |
| Gpa1-AfGasA-C15 | 75.53 | 73.33 | -0.01 | 0.74 | 0.81 | 0.15 |
| Gpa1-AoGpa2-C37 | 75.05 | 78.0 | -0.49 | 0.73 | 0.83 | 0.19 |
| Gpa1-AoGpa2-C25 | 74.98 | 72.53 | -0.56 | 0.74 | 0.83 | 0.19 |
| Gpa1-AoGpa2-C15 | 74.84 | 72.16 | -0.70 | 0.73 | 0.82 | 0.18 |
| Gpa1-AfGasA-C37 | 74.52 | 75.4 | -1.02 | 0.72 | 0.81 | 0.18 |
| Gpa1-AfGasA-C5 | 73.79 | 75.54 | -1.75 | 0.73 | 0.81 | 0.17 |
| Gpa1-AfGasA-C25 | 73.57 | 73.4 | -1.97 | 0.71 | 0.8 | 0.18 |
| Gpa1-AfGasA-C10 | 72.39 | 75.52 | -3.15 | 0.69 | 0.8 | 0.22 |

> **判读**: pLDDT > 80 = 可信折叠; |ΔpLDDT| < 5 = 嫁接未显著破坏骨架; disorder < 0.2 = 整体有序

## 2. 复合物偶联质量 (Batch C + D)

### Ste2

| 嵌合体 | 类型 | ipTM | iPAE | pae_min | ranking | disorder |
|--------|------|------|------|---------|---------|----------|
| Gpa1-WT | ◎ control | 0.6 | 23.44 | 2.26 | 0.72 | 0.25 |

### Gpr2

| 嵌合体 | 类型 | ipTM | iPAE | pae_min | ranking | disorder |
|--------|------|------|------|---------|---------|----------|
| Gpa1-AfGasA-C25 | ○ cross | 0.56 | 24.03 | 3.05 | 0.68 | 0.23 |
| Gpa1-AfGasA-C15 | ○ cross | 0.55 | 24.5 | 3.39 | 0.67 | 0.24 |
| Gpa1-AfGasA-C37 | ○ cross | 0.55 | 24.6 | 3.41 | 0.68 | 0.26 |
| Gpa1-AfGasA-C10 | ○ cross | 0.51 | 24.81 | 3.94 | 0.64 | 0.25 |
| Gpa1-AfGasA-C5 | ○ cross | 0.48 | 24.84 | 4.99 | 0.61 | 0.25 |
| Gpa1-AoGpa2-C10 | ★ cognate | 0.46 | 25.26 | 5.12 | 0.59 | 0.24 |
| Gpa1-AoGpa2-C15 | ★ cognate | 0.45 | 25.33 | 5.16 | 0.59 | 0.26 |
| Gpa1-AoGpa2-C25 | ★ cognate | 0.45 | 25.36 | 5.3 | 0.59 | 0.26 |
| Gpa1-AoGpa2-C37 | ★ cognate | 0.44 | 25.0 | 5.45 | 0.58 | 0.25 |
| Gpa1-AoGpa2-C5 | ★ cognate | 0.44 | 25.23 | 6.2 | 0.58 | 0.25 |

### Gpr3

| 嵌合体 | 类型 | ipTM | iPAE | pae_min | ranking | disorder |
|--------|------|------|------|---------|---------|----------|
| Gpa1-AfGasA-C37 | ○ cross | 0.51 | 24.36 | 4.07 | 0.63 | 0.24 |
| Gpa1-AoGpa2-C15 | ★ cognate | 0.5 | 24.82 | 3.58 | 0.63 | 0.24 |
| Gpa1-AoGpa2-C37 | ★ cognate | 0.5 | 23.31 | 3.83 | 0.62 | 0.22 |
| Gpa1-AfGasA-C25 | ○ cross | 0.49 | 24.49 | 3.72 | 0.62 | 0.25 |
| Gpa1-AfGasA-C15 | ○ cross | 0.48 | 24.45 | 3.87 | 0.6 | 0.23 |
| Gpa1-AoGpa2-C10 | ★ cognate | 0.47 | 24.13 | 4.37 | 0.6 | 0.24 |
| Gpa1-AoGpa2-C25 | ★ cognate | 0.46 | 25.54 | 4.54 | 0.58 | 0.22 |
| Gpa1-AfGasA-C10 | ○ cross | 0.45 | 25.11 | 4.47 | 0.57 | 0.21 |
| Gpa1-AfGasA-C5 | ○ cross | 0.43 | 25.27 | 4.76 | 0.56 | 0.24 |
| Gpa1-AoGpa2-C5 | ★ cognate | 0.39 | 25.72 | 5.76 | 0.53 | 0.25 |

### GprC

| 嵌合体 | 类型 | ipTM | iPAE | pae_min | ranking | disorder |
|--------|------|------|------|---------|---------|----------|
| Gpa1-AfGasA-C25 | ★ cognate | 0.38 | 26.47 | 5.45 | 0.56 | 0.33 |
| Gpa1-AfGasA-C15 | ★ cognate | 0.37 | 26.6 | 6.0 | 0.56 | 0.34 |
| Gpa1-AfGasA-C37 | ★ cognate | 0.36 | 26.48 | 6.81 | 0.55 | 0.33 |
| Gpa1-AfGasA-C5 | ★ cognate | 0.33 | 27.05 | 7.73 | 0.52 | 0.34 |
| Gpa1-AoGpa2-C5 | ○ cross | 0.32 | 26.89 | 8.76 | 0.51 | 0.32 |
| Gpa1-AfGasA-C10 | ★ cognate | 0.31 | 27.36 | 7.26 | 0.51 | 0.35 |
| Gpa1-AoGpa2-C10 | ○ cross | 0.28 | 27.71 | 7.28 | 0.47 | 0.34 |
| Gpa1-AoGpa2-C15 | ○ cross | 0.26 | 29.05 | 12.04 | 0.46 | 0.35 |
| Gpa1-AoGpa2-C37 | ○ cross | 0.23 | 28.49 | 13.06 | 0.44 | 0.35 |
| Gpa1-AoGpa2-C25 | ○ cross | 0.22 | 28.88 | 14.34 | 0.42 | 0.33 |

> **判读标准**:
> - ipTM > 0.6 = 可能存在真实界面; ipTM > 0.8 = 高置信度偶联
> - iPAE < 10 Å = 界面位置预测可靠
> - pae_min: AF3 内置的链对最小 PAE，越低越好
> - cognate (★) ipTM 应显著高于 cross (○) — 否则嫁接未起效

## 3. 综合推荐

### Top cognate 偶联 (按 ipTM 排序)

1. `Gpa1-AoGpa2-C15` × `Gpr3`: ipTM=0.5, iPAE=24.82, ranking=0.63
2. `Gpa1-AoGpa2-C37` × `Gpr3`: ipTM=0.5, iPAE=23.31, ranking=0.62
3. `Gpa1-AoGpa2-C10` × `Gpr3`: ipTM=0.47, iPAE=24.13, ranking=0.6
4. `Gpa1-AoGpa2-C10` × `Gpr2`: ipTM=0.46, iPAE=25.26, ranking=0.59
5. `Gpa1-AoGpa2-C25` × `Gpr3`: ipTM=0.46, iPAE=25.54, ranking=0.58
6. `Gpa1-AoGpa2-C15` × `Gpr2`: ipTM=0.45, iPAE=25.33, ranking=0.59
7. `Gpa1-AoGpa2-C25` × `Gpr2`: ipTM=0.45, iPAE=25.36, ranking=0.59
8. `Gpa1-AoGpa2-C37` × `Gpr2`: ipTM=0.44, iPAE=25.0, ranking=0.58
9. `Gpa1-AoGpa2-C5` × `Gpr2`: ipTM=0.44, iPAE=25.23, ranking=0.58
10. `Gpa1-AoGpa2-C5` × `Gpr3`: ipTM=0.39, iPAE=25.72, ranking=0.53
11. `Gpa1-AfGasA-C25` × `GprC`: ipTM=0.38, iPAE=26.47, ranking=0.56
12. `Gpa1-AfGasA-C15` × `GprC`: ipTM=0.37, iPAE=26.6, ranking=0.56
13. `Gpa1-AfGasA-C37` × `GprC`: ipTM=0.36, iPAE=26.48, ranking=0.55
14. `Gpa1-AfGasA-C5` × `GprC`: ipTM=0.33, iPAE=27.05, ranking=0.52
15. `Gpa1-AfGasA-C10` × `GprC`: ipTM=0.31, iPAE=27.36, ranking=0.51

### cognate vs cross 对比
- cognate 平均 ipTM: 0.4207 (n=15)
- cross 平均 ipTM: 0.4213 (n=15)
- Δ(cognate - cross): -0.0007

> ✗ cognate 偶联信号未优于 cross — 全局平均掩盖了受体间差异，见 §4 逐受体分析

## 4. 逐受体分析 + β6 假设验证

### 4.1 Per-receptor cognate vs cross

| 受体 | cognate 均值 | cross 均值 | Δ | 判读 |
|------|-------------|-----------|---|------|
| Gpr2 (cognate=AoGpa2) | 0.448 | 0.530 | **-0.082** | ✗ cross 反超 cognate |
| Gpr3 (cognate=AoGpa2) | 0.464 | 0.472 | -0.008 | △ 无差异 |
| GprC (cognate=AfGasA) | 0.350 | 0.262 | **+0.088** | ✓ cognate 优于 cross |

> **关键发现**: 全局 Δ≈0 是因为 Gpr2 的反向信号 (-0.08) 恰好抵消了 GprC 的正向信号 (+0.09)。**GprC×AfGasA 是唯一展现真正 cognate 特异性的配对。**

### 4.2 GprC 特异性随嫁接长度的变化

| 长度 | cognate (AfGasA) | cross (AoGpa2) | Δ | pae_min cognate |
|------|-----------------|---------------|---|-----------------|
| C5 | 0.33 | 0.32 | +0.01 | 7.73 |
| C10 | 0.31 | 0.28 | +0.03 | 7.26 |
| C15 | 0.37 | 0.26 | **+0.11** | 6.00 |
| C25 | 0.38 | 0.22 | **+0.16** | 5.45 |
| C37 | 0.36 | 0.23 | **+0.13** | 6.81 |

> - C5/C10: 特异性 Δ ≤ 0.03，噪声范围
> - **C15 起跳** (Δ=+0.11): α5 helix 替换开始体现受体识别差异
> - **C25 峰值** (Δ=+0.16): 完整 α5 helix 替换最大化特异性，且 pae_min=5.45 为 GprC 全系列最低
> - C37 回落 (Δ=+0.13): β6 sheet 加入未进一步提升，反而 pae_min 升至 6.81

### 4.3 Gpr3 cognate 长度趋势

| 长度 | ipTM | iPAE | pae_min |
|------|------|------|---------|
| C5 | 0.39 | 25.72 | 5.76 |
| C10 | 0.47 | 24.13 | 4.37 |
| C15 | **0.50** | 24.82 | 3.58 |
| C25 | 0.46 | 25.54 | 4.54 |
| C37 | **0.50** | **23.31** | 3.83 |

> C15 和 C37 ipTM 并列 0.50，但 C37 iPAE (23.31) 显著优于 C15 (24.82)。β6 sheet 可能为 Gpr3 偶联界面提供了更紧密的接触，但 ipTM 未能反映——需 MD 验证接触面残基持续性。

### 4.4 Gpr2 反向信号解读

Gpr2 中 AfGasA (cross) 全面优于 AoGpa2 (cognate)。可能原因：
1. **AfGasA C 端序列本身折叠质量更利于 AF3 预测界面**，与生物学特异性无关
2. Gpr2 与 Gpa2 的体内偶联可能依赖 ICL2/ICL3 而非 C 端——与 Class D GPCR 非经典激活机制一致
3. AF3 训练集缺乏真菌 Gα 偶联数据，对 AoGpa2 系嫁接的评分系统性偏低

### 4.5 β6 假设结论

| 受体 | C15→C37 ipTM 变化 | C15→C37 iPAE 变化 | β6 有帮助？ |
|------|-------------------|-------------------|-----------|
| Gpr2 cognate | 0.45→0.44 | 25.33→25.0 | ✗ 无变化 |
| Gpr3 cognate | 0.50→0.50 | 24.82→**23.31** | △ iPAE 改善但 ipTM 持平 |
| GprC cognate | 0.37→0.36 | 26.60→26.48 | ✗ C25 反而更优 |

> **β6 sheet (C37) 未按文献预期（Ueda2003/Hara2012）成为关键功能阈值。** 对 GprC 最优切点是 C25（完整 α5 helix），对 Gpr3 是 C15 或 C37（iPAE 更优）。真菌 GPCR 的 Gα 偶联界面可能与哺乳动物 T2R 体系不同。

### 4.6 推荐 Top 候选（送 MD 验证）

| 优先级 | 候选 | 受体 | ipTM | iPAE | 理由 |
|--------|------|------|------|------|------|
| 1 | Gpa1-AoGpa2-C37 | Gpr3 | 0.50 | 23.31 | 全数据集最低 iPAE；cognate ipTM 并列最高 |
| 2 | Gpa1-AfGasA-C25 | GprC | 0.38 | 26.47 | cognate 特异性 Δ=+0.16 最强；pae_min=5.45 |
| 3 | Gpa1-AoGpa2-C15 | Gpr3 | 0.50 | 24.82 | 最短有效嫁接，折叠风险最低 |

> 以 Ste2-WT ipTM=0.60 为基准：Top 1 达到 83% (0.50/0.60)，Top 2 达到 63% (0.38/0.60)。
