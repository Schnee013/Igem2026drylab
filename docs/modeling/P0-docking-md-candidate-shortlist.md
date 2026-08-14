---
direction: P0-molecular-docking
type: md-candidate-shortlist
status: historical-only
target_audience: drylab-md-team
created: 2026-05-20
last_updated: 2026-08-14
---

# 2026-05 MD 输入选择快照（历史）

## 允许用途

本文件用于追溯 2026-05 docking 分析如何形成后续 MD 输入选择；允许用途限于当时的选择过程和已完成体系的输入 provenance。

## 历史证据

- Ratio 报告：`../../experiments/docking-repro/analysis/ratio_channel_report.md`
- 配对排名：`../../experiments/docking-repro/analysis/ratio_pairings.csv`
- 全谱结果：`../../experiments/docking-repro/analysis/ratio_spectrum.csv`
- 版本化 release：`../../experiments/docking-repro/analysis/releases/gpr3_f_full_20260520_0854/`
- IFP 结果：`../../experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/`

## 已完成 MD 体系的输入关系

| MD 体系 | 实际 system-local pose | 历史来源 |
|---|---|---|
| `Gpr2_R59C + ASCR18` | `../../experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/Gpr2_R59C_ascr18_pose1.sdf` | 2026-05 docking/IFP release |
| `Gpr3_R167Y + ASCR3` | `../../experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf` | 2026-05 docking/IFP release |

这两个 MD 包及其完成轨迹继续以实际起始 pose、运行证据和 system-local 状态文件为解释边界。历史 ranking 只解释输入 provenance。
