# ascr18 CGenFF Parameters

Ascaroside #18 (PubChem CID 71514784) — C17H32O6 (neutral) / C17H31O6⁻ (deprotonated)

## Directory Structure

```
ascr18/
  protonated/           # COOH form (neutral, charge = 0)
    charmm-gui-7628908749/    # CHARMM-GUI Ligand Reader output
    penalty_summary.md        # CGenFF penalty analysis
  deprotonated/         # COO⁻ form (charge = -1) ← MD production 使用此版本
    ascr18_deprotonated.sdf   # 去质子化 SDF（CHARMM-GUI 提交用）
    charmm-gui-XXXXXXX/       # TODO: CHARMM-GUI 重新提交后存档
    penalty_summary.md        # TODO: 新 penalty 分析
```

## Protonation State Decision

- 羧酸 pKa ≈ 4.5，生理 pH 7.4 下应去质子化为 **COO⁻**（净电荷 -1）
- PubChem 3D Conformer SDF 为中性 COOH 形式
- CHARMM-GUI Ligand Reader 原样保留输入质子化态
- **MD 生产必须使用 COO⁻ 形式**：V138R 盐桥假说（ARG⁺ ↔ COO⁻）依赖正确电荷

## Deprotonation Method

- 脚本 `../deprotonate_carboxyl.py` 从质子化 SDF 移除 H55（atom 55，羧基 OH 质子）
- O5（atom 5）设置 formal charge = -1（V2000 M CHG 行）
- Open Babel 验证：FORMULA = C17H31O6⁻，TOTAL CHARGE = -1

## Affected Atoms (protonated → deprotonated)

| ITP atom | SDF atom | Type change | Charge change |
|----------|----------|-------------|---------------|
| O5 (5) | 5 | OG311 → OG2D2 (expected) | -0.600 → ~-0.76 |
| O6 (6) | 6 | OG2D1 → OG2D2 (expected) | -0.576 → ~-0.76 |
| H32 (55) | 55 | **removed** | +0.429 → N/A |
| C17 (23) | 23 | CG2O2 (stays) | +0.735 → ~+0.52 |

Note: 以上 charge 预估值仅供参考，实际值由 CGenFF/ParamChem 重新计算。
