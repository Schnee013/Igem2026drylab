---
direction: P0-molecular-docking
status: historical-only
priority: P0
chassis_dependent: false
last_updated: 2026-08-14
---

# P0: 受体-配体分子对接与 In Silico 突变扫描

> 本仓库中本方向的维护状态为 `historical-only`。
>
> **允许用途**：追溯 2026 年 4–5 月完成的 docking 方法、结果、候选生成过程，以及已完成 MD 体系的实际起始输入。
>
> 项目级状态以 [docs/INDEX.md](../INDEX.md) 为准；详细经过回到 [2026 年 4–5 月日志](../logs/) 和原始结果文件。

## 历史科学问题

该阶段研究 Gpr2、Gpr3、GprC 与 ascr#18、ascr#3、ascr#7 的结合模式，并用静态突变扫描提出差异化选择性与结合口袋机制假说。历史结果服务于当时的候选排序、IFP 解释和 MD 输入选择。

## 历史方法快照

1. 从 AlphaFold DB 获取 Gpr2、Gpr3、GprC WT 结构。
2. 从 PubChem 获取 ascr#18、ascr#3、ascr#7 配体结构。
3. 使用 ADFR 准备受体与配体，按 Hu2024 参数开展 AutoDock Vina 单阶段对接。
4. 使用 ProLIF 分析静态相互作用指纹。
5. 使用 AlphaFold 3 预测的突变体结构开展 alanine/saturation scan，并生成当时的双通道排序和候选清单。

历史配置和实现位于：

- `src/modeling/docking-repro/`
- `environments/mac-docking.yml`
- `environments/mac-docking.lock.yml`
- `environments/win-docking-repro.lock`
- [历史 full-refresh 计划](../../codex/docs/plans/docking-repro-full-refresh-slurm.md)

这些文件用于解释当时结果和方法身份。可运行性需要按实际环境重新验证。

## 保留的历史证据

| 角色 | 路径 | 允许用途 |
|---|---|---|
| Ratio 报告 | `experiments/docking-repro/analysis/ratio_channel_report.md` | 解释 2026-05 双通道分析 |
| 配对排序 | `experiments/docking-repro/analysis/ratio_pairings.csv` | 追溯当时的候选配对 |
| 全谱结果 | `experiments/docking-repro/analysis/ratio_spectrum.csv` | 追溯当时的合并结果 |
| 版本化 release | `experiments/docking-repro/analysis/releases/gpr3_f_full_20260520_0854/` | 固定 2026-05-20 结果身份 |
| Mutant IFP | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/` | 追溯静态接触与 MD pose 来源 |
| 历史交付包 | `temp/docking-results/` | 保存当时整理出的 docking 结果副本 |
| 目录合同 | [docking-repro README](../../experiments/docking-repro/README.md) | 说明保留目录与下游输入关系 |
| 候选快照 | [MD 前候选体系清单](P0-docking-md-candidate-shortlist.md) | 追溯当时的 MD 输入选择 |

## 已完成 MD 的实际输入来源

已完成的 MD 体系保留各自 system-local pose 作为输入权威；docking 结果目录仅提供 provenance。

| MD 体系 | System-local 输入 | 历史 docking 来源 |
|---|---|---|
| `Gpr2_R59C + ASCR18` | `experiments/md-simulation/systems/gpr2-R59C-ascr18/ligand/Gpr2_R59C_ascr18_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr2_R59C_ascr18_poses.sdf` |
| `Gpr3_R167Y + ASCR3` | `experiments/md-simulation/systems/gpr3-R167Y-ascr3/ligand/Gpr3_R167Y_ascr3_pose1.sdf` | `experiments/docking-repro/results/ifp_analysis_mutants_gpr3_f_full_20260520_0854/tmp/Gpr3_R167Y_ascr3_poses.sdf` |

对应 MD 结论只绑定各自实际起始 pose、实际轨迹和分析合同。

## 证据边界

- Vina score 和历史 ratio 仅支持当时工作流内的相对排序；`Kd`、`EC50` 与受体激活强度需要独立 binding 或功能实验。
- 静态 IFP 支持提出接触与机制假说；持续性、驻留和构象变化由 MD 或实验确认。
- 历史候选清单支持输入 provenance，不承担当前候选或项目优先级。
- 结果文件是数值权威；本文只维护方法、用途边界和指针。

## 历史方法演化

| 时间 | 方法节点 | 历史意义 |
|---|---|---|
| 2026-04-03 至 04-04 | OpenBabel、RDKit MMFF、早期 Vina 探索 | 建立初始 WT 对接基线 |
| 2026-04-05 至 04-06 | ADFR、Orca DFT、两阶段 docking-repro | 对齐 Hu2024 工具链并暴露协议差异 |
| 2026-04-07 至 04-14 | 单阶段 Vina、ICL3 截断、TM 质心、BW 映射与 ProLIF 修正 | 形成后续历史分析采用的方法框架 |
| 2026-04-23 至 05-20 | Gpr2 3D offset、Gpr3 方案 F、supplemental docking、ratio/IFP refresh | 形成保留的 2026-05 历史 release 与 MD 输入来源 |

详细记录：

- [2026-04-03](../logs/2026-04-03.md) 至 [2026-04-14](../logs/2026-04-14.md)：方法建立与修正。
- [2026-04-23](../logs/2026-04-23.md)：Gpr2/Gpr3 方法修订。
- [2026-05-19](../logs/2026-05-19.md)：full refresh 执行证据。
- [2026-05-20](../logs/2026-05-20.md)：历史 shortlist 与 IFP 结果边界。

## 关键文献

- Kuo et al. (2024), DOI `10.1038/s41564-024-01679-w` — Gpr2/Gpr3 与 ascaroside 的来源证据；见 [Kuo2024 summary](../papers/summaries/Kuo2024-Gpr2Gpr3-summary.md)。
- Hu et al. (2024), DOI `10.1038/s41564-024-01731-9` — GprC docking 方法背景；见 [Hu2024 summary](../papers/summaries/Hu2024-GprC-summary.md)。

## 与其他方向的关系

- **输出到**：
  - [P0-md-simulation](P0-md-simulation.md)：提供两个已完成 MD 体系的历史起始 pose provenance。
  - [P0-signal-pathway-ode](P0-signal-pathway-ode.md)：提供 WT 场景名称和历史机制背景；ODE 数值参数使用独立文献、扫参或湿实验校准。
- **依赖于**：
  - `experiments/docking-repro/` 中保留的历史输入、结果和分析文件。
  - 2026 年 4–5 月规范日志。
