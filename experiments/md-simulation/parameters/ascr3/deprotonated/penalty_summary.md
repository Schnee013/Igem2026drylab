# ascr3 去质子化 (COO⁻) CGenFF Penalty Summary

- **CHARMM-GUI Job ID**: 7629305001
- **输入**: `ascr3_deprotonated.sdf` (TOTAL CHARGE = -1, C15H25O6⁻)
- **分子类型名**: ASCR3 (区别于质子化版 ASC3)
- **原子数**: 46 (比质子化版少 1H)
- **总电荷**: -1.000

## Penalty

| 类型 | 数量 | Max Penalty | 唯一值 |
|------|------|-------------|--------|
| Param (torsion) | 14 | 5.500 | 0.6, 0.9, 1.5, 5.5 |
| Charge | 2 | 5.500 | — |

**全部 < 10，无需 QM torsion scan。**

与质子化版 (ASC3, Job 7628970666) 结果一致。

## GROMACS 拓扑

- `charmm-gui-7629305001/gromacs/ASCR3.itp` — **这个用于 MD 生产**
- `charmm-gui-7629305001/gromacs/charmm36.itp` — 力场补充参数
