# ascr18 去质子化 (COO⁻) CGenFF Penalty Summary

- **CHARMM-GUI Job ID**: 7629292909
- **输入**: `ascr18_deprotonated.sdf` (TOTAL CHARGE = -1, C17H31O6⁻)
- **分子类型名**: ASCR18 (区别于质子化版 ASC18)
- **原子数**: 54 (比质子化版少 1H)
- **总电荷**: -1.000

## Penalty

| 类型 | 数量 | Max Penalty | 唯一值 |
|------|------|-------------|--------|
| Param (torsion) | 12 | 5.500 | 0.6, 1.5, 5.5 |
| Charge | 2 | 5.500 | — |

**全部 < 10，无需 QM torsion scan。**

与质子化版 (ASC18, Job 7628908749) 结果一致。

## GROMACS 拓扑

- `charmm-gui-7629292909/gromacs/ASCR18.itp` — **这个用于 MD 生产**
- `charmm-gui-7629292909/gromacs/charmm36.itp` — 力场补充参数
