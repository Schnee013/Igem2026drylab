# 双/多突变 docking 方向

> Status: `phase2_local_schema_test_ready_blocked_by_frame_repair`
>
> Source: 当前 docking-repro 状态、mutant GPR MD 证据边界、本目录核心文献账本。
>
> As of: `2026-07-30`
>
> Allowed use: 规划 frame 修复后的受限双突变计算与验证；不得从已撤回的旧 ratio/IFP/shortlist 发布候选。
>
> Update trigger: docking frame repair 和全量单突变重跑通过、重建 active shortlist、双突变结果落地，或结构/grid/评分合同变化。

## 1. 当前结论

多突变方向的 Phase 2 本地 schema/test vertical slice 已完成，但**现在不能直接从
旧单突变结果组合候选**。

当前 [P0 docking](../P0-molecular-docking.md) 状态为
`geometry_gate_v3_seed44_holdout_fail_stop_full_blocked`：R1 已修正
maximum-20 与显式 CPU8 合同；seed 42 + 43 WT evidence 已冻结新 geometry gate，
但 seed-44 独立 8-job holdout 的 Gpr3/R167Y 两臂未通过冻结门，终态为
`fail_stop_before_full`。328-job 全量未启动。因此旧 Gpr2/Gpr3 mutant score、
ratio、IFP、排名和 shortlist 仍只是历史缺陷快照，失败 holdout 也只作 gate
审计，二者都不是当前候选依据。

本方向的正确顺序是：

1. 先完成 mutant→WT 共同 frame、PDBQT provenance、smoke 和单突变全量重跑；
2. 用修复后的单突变结果重新建立 active shortlist；
3. 再从 shortlist 中冻结少量双突变 `WT / A / B / AB` 周期；
4. 只有双突变证据明确且存在实验标签时，才讨论三突变或 low-N 模型。

本地 Phase 2 当前入口是
[`experiments/docking-repro/multi-mutant/README.md`](../../../experiments/docking-repro/multi-mutant/README.md)。
该入口只提供 canonical genotype、multi-mutation FASTA、旧单突变只读兼容、
`WT / A / B / AB` cycle validator 和 matched result join；其中 template 与测试
全部使用 synthetic placeholder，不是 candidate release。

## 2. 要回答的问题

单突变验证不理想时，双突变不是简单“多加一个有利突变”，而是检验：

- 两个位点是否在目标配体/非目标配体之间形成非加和选择性变化；
- 一个选择性位点能否与另一个结构稳定/口袋重排位点形成互补；
- 组合效应是否跨 receptor conformer、Vina seed 和 pose/IFP cluster 保持；
- 计算上的改善是否仍保留可表达、可定位、低 basal leak 的受体。

因此首轮只做双突变，不做全组合穷举。

## 3. frame 修复后的候选生成规则

首轮最多冻结 4 个主双突变周期（建议每个受体 2 个），另保留最多 2 个条件探索
周期。每个组合必须来自修复后的同版本单突变 release，并满足：

1. **单突变身份有效**：A、B 均通过共同 frame、双配体、multi-seed、geometry 和
   IFP gate；
2. **位点不冲突**：A、B 位于不同 residue，WT identity 与 full-length sequence
   authority 一致；
3. **机制互补**：优先组合不同接触/结构机制，不只挑两个最低 Vina score；
4. **负向设计**：同时考察 ascr#18 与 ascr#3，不能只优化目标 ligand；
5. **结构风险可控**：排除明显 clash、膜内不合理极性暴露或 pocket collapse；
6. **对照完整**：必须同时生成 WT、A、B、AB，任一臂缺失则不计算非加和 contrast。

优先考虑三类组合：

| 类别 | A/B 角色 | 目的 |
|---|---|---|
| 同方向、不同机制 | 两个修复后同 Channel 候选，接触网络不同 | 检验选择性移动能否超过加和模型 |
| 选择性 + 结构补偿 | 一个强选择性候选 + 一个稳定性/表达补偿候选 | 避免只追求 docking 分数而牺牲受体可用性 |
| 局部 + 远端 | 一个直接 pocket 位点 + 一个第二壳层/构象位点 | 区分直接接触与间接构象上位性 |

以下情况不进入首轮：

- 旧 `ratio_spectrum.csv` 排名未经修复重跑就直接组合；
- 同一 residue 的两个替换；
- 只有单 ligand 结果；
- 三突变、随机全组合或把全部氨基酸笛卡尔积一次展开；
- 缺少真实功能标签时直接训练 low-N 模型筛选多突变。

## 4. 结构比较合同

### 4.1 主比较：matched-backbone

对每个 cycle，从同一 WT parent conformer 派生 WT、A、B、AB，并使用相同
side-chain placement 和 local relaxation 合同。这样可把“独立结构预测差异”和
“突变差异”尽量拆开。

### 4.2 敏感性路线：独立 AF3 ensemble

将四个 genotype 的完整序列分别提交 AF3，保留全部输入、模型、ranking/confidence
文件和 checksum。每个 AF3 mutant 必须先按预冻结的七 TM Cα 集合刚体叠合到对应
WT docking frame，再生成 PDBQT 和应用 receptor-specific 绝对 grid。

AF3 ensemble 用于 starting-structure sensitivity，不与 matched-backbone 样本混合
当作 paired technical replicates。AF3 提交属于外部动作，执行前需单独确认账户、
配额和数据处理边界。

## 5. docking 与 pose/IFP 合同

- 每个 genotype 同时对接 ascr#18 和 ascr#3；
- 同一受体使用 genotype-invariant grid；
- 固定 ligand identity、质子化/电荷、PDBQT 工具、Vina 版本和 matched seeds；
- 至少 3 个合格 receptor conformers × 5 Vina seeds × 2 ligands；
- 每次保存 Top 5 poses；
- 按跨 seed 的 pose cluster、口袋位置和 IFP 共识选择代表姿态；
- 不从所有运行中 cherry-pick 单个最低分。

## 6. 双突变周期口径

对 genotype `g ∈ {WT, A, B, AB}`：

```text
S(g) = ΔG18(g) - ΔG3(g)
εsel_score = S(AB) - S(A) - S(B) + S(WT)
```

- Channel A 目标中，负向 `εsel_score` 表示 AB 的 docking-derived 选择性移动比
  加和模型更偏向 ascr#18；
- Channel B 目标中，正向 `εsel_score` 表示 AB 的 docking-derived 选择性移动比
  加和模型更偏向 ascr#3。

`εsel_score` 不是实验双突变周期的热力学 coupling free energy。只有 matched
conformer、matched seed、pose/IFP 合格的样本才进入 paired bootstrap。旧
`±0.477 kcal/mol` 来自已撤回的历史单突变分析，不能作为本路线阈值；新的
empirical null/noise floor 必须由修复后的 WT/control 重复预注册。

## 7. 推进门

一个 AB 只有同时满足以下条件，才进入有限 MD/湿实验候选讨论：

- frame、sequence、WT residue、mutation list、PDBQT provenance 和 checksum 完整；
- 无明显 backbone break、side-chain clash 或不合理膜内极性暴露；
- 两个 ligand 均有跨 seed、跨 conformer 的 pocket-consistent pose/IFP 共识；
- `εsel_score` 方向稳定，paired uncertainty 与 empirical null 不支持纯噪声解释；
- AF3 sensitivity 不出现相反且无法解释的结论；
- target、off-target、稳定性、pose/IFP 和结构敏感性共同通过 Pareto gate；
- 结论保持为“候选优先级/机制假说”，不写成 Kd、EC50、激活或传感器性能。

## 8. 路由

- 核心文献与核验层级：[literature-sources.md](literature-sources.md)
- 机器可读文献账本：[literature-sources.csv](literature-sources.csv)
- 执行计划：
  [multi-mutant-docking-execution-plan-20260730.md](../../../codex/docs/plans/multi-mutant-docking-execution-plan-20260730.md)
- 当前 docking 状态：[P0-molecular-docking.md](../P0-molecular-docking.md)
- 已撤回 shortlist 边界：[P0-docking-md-candidate-shortlist.md](../P0-docking-md-candidate-shortlist.md)
- docking-repro 目录合同：
  [experiments/docking-repro/README.md](../../../experiments/docking-repro/README.md)
- Phase 2 本地 schema/test 合同：
  [experiments/docking-repro/multi-mutant/README.md](../../../experiments/docking-repro/multi-mutant/README.md)
