---
direction: P0-molecular-docking
type: md-candidate-shortlist
target_audience: drylab-md-team; post-MD candidate discussion
status: withdrawn
last_updated: 2026-07-30
---

# 已撤回：MD 前候选体系清单

## 当前状态

本清单于 2026-07-30 撤回。AF3 mutant docking 未先把 receptor 刚体叠合到 WT docking frame，却复用了 WT frame 的绝对搜索框；因此旧 mutant score、ratio、IFP、配对排名和以这些 pose 构建的候选均不能作为当前科学事实。

当前不存在 active docking shortlist，也不存在可发送的 wetlab handoff。新的候选身份必须来自 Gpr2/Gpr3 共 162 个 mutant、两个配体和 4 个同版本 WT baseline 的共同 frame 全量重跑，并通过预冻结的 provenance、膜/口袋 geometry、ratio 和 IFP 审计。

## 历史证据边界

下列 2026-05-20 产物仅保留为待纠错历史快照，不得作为当前候选来源：

- Ratio 报告：`../../experiments/docking-repro/analysis/ratio_channel_report.md`
- 配对排名：`../../experiments/docking-repro/analysis/ratio_pairings.csv`
- IFP 刷新结果：`../../experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/`

旧 R59C/R167Y MD 包及轨迹不作废，但只能支持各自实际旧起始 pose 的单重复探索性描述；它们不能验证 frame 修复后的候选排名，也不能给旧 shortlist 恢复 current 身份。

## 重建门禁

- 修复方案固定为 mutant→WT 七 TM Cα Kabsch 对齐后再生成 PDBQT。
- smoke 必须覆盖 Gpr2 WT/R59C 与 Gpr3 WT/R167Y 的 ascr#18/ascr#3，共 8 个唯一 job。
- smoke 通过后才可完成 328-job/6560-pose 全量矩阵。
- 新 shortlist 只含 Gpr2/Gpr3；最终 7 对需至少两个不同 Gpr2 mutant identity 且至少一个 Gpr3 候选。
- 不强留任何旧候选；不足 7 对或任一 provenance/geometry/ratio/IFP 门禁失败时停止。
