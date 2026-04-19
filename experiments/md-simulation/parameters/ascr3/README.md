# ascr3 CGenFF Parameters

Ascaroside #3 (PubChem CID 16066476) — C15H26O6 (neutral) / C15H25O6⁻ (deprotonated)

## Directory Structure

```
ascr3/
  protonated/           # COOH form (neutral, charge = 0)
    charmm-gui-7628970666/    # CHARMM-GUI Ligand Reader output
    penalty_summary.md        # CGenFF penalty analysis
  deprotonated/         # COO⁻ form (charge = -1) ← MD production 使用此版本
    ascr3_deprotonated.sdf    # 去质子化 SDF（CHARMM-GUI 提交用）
    charmm-gui-XXXXXXX/       # TODO: CHARMM-GUI 重新提交后存档
    penalty_summary.md        # TODO: 新 penalty 分析
```

## Protonation State Decision

同 ascr18 — 详见 `../ascr18/README.md`

## Deprotonation Method

- 脚本 `../deprotonate_carboxyl.py` 从质子化 SDF 移除 H26（atom 47，羧基 OH 质子）
- O5（atom 5）设置 formal charge = -1（V2000 M CHG 行）
- Open Babel 验证：FORMULA = C15H25O6⁻，TOTAL CHARGE = -1
