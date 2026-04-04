# 决策 002：建立独立的 Hu2024 精确复现 Pipeline

- **日期**: 2026-04-04
- **状态**: 已决定
- **关联方向**: [P0-molecular-docking](../modeling/P0-molecular-docking.md)

## 背景

v2 pipeline（主线）使用 OpenBabel + RDKit MMFF + Meeko，production 运行（exhaustiveness=200）后：
- GprC ascr18 = -6.05 kcal/mol（Hu2024: -8.29，差 2.24）
- GprC ascr3 = -6.45 kcal/mol（Hu2024: -8.31，差 1.86）
- PLIP 关键残基 N2.57(Res83) 和 R6.45(Res281) 均未出现在接触列表中

iGEM 报告需要引用 Hu2024 作为方法参照，绝对值差距过大会影响可信度。

## 方法差异分析（5 项）

| # | 环节 | Hu2024 | v2 | 估计影响 |
|---|------|--------|----|---------|
| 1 | 受体准备 | ADFR Suite `prepare_receptor` | OpenBabel | 原子类型/加氢 |
| 2 | 配体几何 | Orca DFT B3LYP/def2-TZVP | RDKit MMFF | ~1 kcal/mol（最大） |
| 3 | 配体 PDBQT | ADFR `prepare_ligand` (7-11 DOF) | Meeko (15 DOF) | 采样+torsion 惩罚 |
| 4 | Grid spacing | 0.1 Å | 0.25 Å | 格点精度 |
| 5 | 配体来源 | Avogadro 手建 | PubChem SDF | DFT 优化后可忽略 |

## 选项

1. **方案 A：接受 v2 结果，仅修正文字说明**
   - 优点：无额外工作
   - 缺点：PLIP 残基不匹配，绝对值差 2 kcal/mol 难以在报告中自圆其说

2. **方案 B：仅改 ADFR（不做 Orca）**
   - 优点：较快（无 Orca 依赖）
   - 缺点：配体几何差异是最大单因素，改了受体但漏了配体效果有限

3. **方案 C：独立 docking-repro pipeline，全部对齐**
   - 优点：尽可能逼近 Hu2024，结果可直接与文献比对
   - 缺点：需要安装 ADFR + Orca，额外工作量约 2-3 天

## 决定

选择**方案 C**，原因：
1. iGEM 评审重视方法可重复性，与 Hu2024 完全一致是最强的论据
2. Windows 台式机（7500F）可运行 Orca DFT，无硬件瓶颈
3. 独立路径不影响 v2 已有结果，可并行保留两套数据

## 实现要点

- spacing=0.1 + box=40Å 超出 Vina 格点限制（64M > 27M），用**两阶段对接**解决：
  Stage1 (40Å/0.25Å) 定位口袋 → Stage2 (20Å/0.1Å，8.1M 格点) 精修
- 计算节点：Windows 7500F（通过 Tailscale SSH），不用 WSL2，直接 Windows 原生
- 代码路径：`src/modeling/docking-repro/`，产出路径：`experiments/docking-repro/`

## 后果

- 更新 DOCMAP.md 增加"方法变体"命名规则
- 更新 P0-molecular-docking.md 增加方法变体章节
- 在 Windows 机器上安装 ADFR Suite + Orca（安装脚本在 `scripts/win-setup/`）
