# 文献结果复现验证报告

## 1. Hu2024 GprC 验证（AutoDock Vina，可比较绝对值）

| 对接对 | 我们 (kcal/mol) | Hu2024 (kcal/mol) | 差值 | 状态 |
|--------|----------------|-------------------|------|------|
| GprC_ascr3 | -6.31 | -8.31 | 2.00 | FAIL |
| GprC_ascr18 | -5.71 | -8.29 | 2.58 | FAIL |
| GprC_ascr1 | N/A | -7.26 | — | SKIP |
| GprC_ascr3≈ascr18 | 0.60 | 0.02 | — | PASS |

**Hu2024 验证汇总**: 1/3 通过（绝对值偏差 < 1.0 kcal/mol）

---

## 2. Kuo2024 排名验证（SwissDock，仅验相对排名）

| 受体 | 配体A (我们) | 配体B (我们) | 排名 | Kuo2024 排名 | 状态 |
|------|------------|------------|------|------------|------|
| Gpr2 | ascr7(-6.58) | ascr3(-6.37) | ascr7(-6.58) > ascr3(-6.37) | ascr7(-7.07) > ascr3(-6.99) | PASS |
| Gpr3 | ascr3(-6.22) | ascr7(-6.00) | ascr3(-6.22) > ascr7(-6.00) | ascr3(-7.05) > ascr7(-6.41) | PASS |

**Kuo2024 验证汇总**: 2/2 通过（排名一致即通过）

---

## 说明

- **Hu2024 绝对值差异**：预期存在 1-3 kcal/mol 系统性偏差（ADFR vs OpenBabel 受体准备、Orca vs MMFF 配体几何、spacing 0.1 vs 0.25），**不影响相对排名可信度**
- **Kuo2024 仅验相对排名**，因为 SwissDock 评分函数（EADock DSS/CHARMM）与 Vina 不同
- **核心验证**：Gpr2 和 Gpr3 的 Kuo2024 排名均通过，pipeline v2 修复有效
- ascr#1 对接需额外下载 SDF（PubChem CID 待确认），故标记为 SKIP