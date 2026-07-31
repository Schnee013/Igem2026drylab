# Docking geometry-gate recalibration decision

> Status: `FROZEN_GATE_SEED44_HOLDOUT_FAILED_FULL_BLOCKED`
>
> Scope: decide how to replace or revalidate the non-transferable historical
> WT geometry-distribution gate before any further docking. The gate was
> subsequently frozen from seed 42 + 43 WT evidence, and the separately
> authorized seed-44 holdout was executed. It failed before full-run. This
> document does not authorize gate relaxation, a replacement holdout, the
> remaining 320 jobs, ranking, candidate selection, wet-lab handoff, commit,
> or push.

## 说人话结论

新门已经冻结并接受了独立 seed-44 检验，但检验没有通过。8/8 docking、
IFP 和 geometry 都技术完成；失败的是 `Gpr3/R167Y` 的两条 geometry arm，
其中 ascr3 的 MODEL 1 也失败。按预先约定，run 已停在
`fail_stop_before_full`，没有启动剩余 320 jobs。不能用这次 holdout 的结果
回头放宽门。

R1 的 Vina 没有因为只返回 18 个 pose 而失败。`num_modes=20` 已按“最多
20 个”正确实现，8/8 docking 和 8/8 IFP 都技术完成。

真正卡住的是旧 geometry gate：它把一次旧 WT docking 的 pose 高度极值和
合格 pose 数量直接冻结为硬线，没有留跨 Vina 版本或平台的容差。现在 E2 上
使用锁定的 Vina 1.2.6 重跑后，Gpr2 的两个 WT 对照自身都过不了这条旧线，
所以不能再用该门判断 mutant 好坏，也不能据此进入 320-job full run。

R1 的 `TERMINAL_ABNORMAL / fail_stop_before_full` 仍是正确的失败停止记录；
本决策不会回写或“翻绿”该归档。

## 已验证事实

### 1. Maximum-20 技术合同已经通过

- 当前权威 run：
  `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/`
- run identity：
  `950639bdc788bf23a3cacc61d57dfa130ea05872f3d64663f87b88e567f6bce8`
- 8 个唯一 docking job 均一次完成；6 个返回 20 poses，Gpr3
  R167Y–ascr18/ascr3 各返回 18 poses。
- 两个 18-pose job 均满足 `1 <= actual_modes <= 20`、MODEL 连续、
  MODEL 1 存在及 affinity 同源要求。
- 8/8 IFP 完成。当前失败源是 geometry distribution，不是 Vina 或 IFP
  crash。

### 2. 当前 WT 对旧门的复核结果

| WT arm | MODEL 1 | 当前合格 / 旧下限 | 主要差异 |
|---|---|---:|---|
| Gpr2 / ascr18 | pass | 17 / 19 | 两个 pose 只越过旧高度边界 0.033 Å、0.053 Å；另一个 pose 位于约 31.2 Å 外的错误高度簇 |
| Gpr2 / ascr3 | pass | 17 / 18 | 当前出现 3 个错误高度簇 pose；历史单次 calibration 只有 2 个 |
| Gpr3 / ascr18 | pass | 18 / 15 | pass |
| Gpr3 / ascr3 | pass | 18 / 15 | pass |

因此至少对 Gpr2 而言，旧门不是当前锁定工具链的可复现 WT positive
control。Gpr2/ascr18 同时暴露了“零容差极值”的数值脆弱性；
Gpr2/ascr3 则说明 pose 分布计数本身也会随 Vina 版本/平台发生离散变化，
仅增加一个很小的高度容差不能解决全部问题。

### 3. 差异不是 receptor 或 ligand 文件被换掉

- Gpr2 WT receptor PDBQT 去除 CRLF/LF 差异后的共同 SHA256：
  `ccd7aa39e9bbe8cb00381397a5f624de5f3c55710398ecf415450e39d7680773`
- Gpr3 WT receptor PDBQT 去除 CRLF/LF 差异后的共同 SHA256：
  `d48ee0bdfd8866a47e12835ae1153a13da0960380ddb2d96d1d1f6f0509a8bc2`
- ascr18 ligand PDBQT SHA256：
  `db821bc51fcc887d8e26cfcd6c5bc6b13ac469e42ffb64b9cf38e91c9c544f69`
- ascr3 ligand PDBQT SHA256：
  `bea9eb4fa79318915e2e826922846d0ea00f52dc43b926fee4ac2a1440308450`

原始 receptor SHA 不同来自历史文件 CRLF 与当前文件 LF 的换行差异；规范化
后内容相同。

### 4. 历史 calibration 不能直接代表当前 production toolchain

- Gpr2 calibration 来自 2026-04-16 的 Slurm Vina 1.2.5 运行。
  当前实现从该单次 pose ensemble 的胞外簇直接取
  `membrane_height_min/max`，没有拟合 margin；`min_passing_modes`
  也等于该次运行实际合格数。
- Gpr3 calibration 来自历史 Windows 结果；本地只保留 19-MODEL pose
  artifact 和方法日志，没有锁定完整 Vina executable/package build、OS、
  CPU 或 ADFR/OpenBabel 身份。
- R1 使用 E2 Linux、Vina conda 1.2.6、OpenBabel conda 3.1.1 和
  ADFRsuite 1.1dev build 100，并已锁定 executable/package/input identity。

旧门仍可作为历史几何诊断背景，但现有证据不支持把它当作跨工具链
production hard gate。

## 仍未知

- 不同 seed 下，E2/Vina 1.2.6 的四条 WT arm 各自会有多大 pose-population
  波动。
- Gpr3 历史 Windows calibration 的精确 Vina、OpenBabel、ADFR、CPU 和 OS
  身份；现有 artifact 无法补齐这些运行时事实。
- 若将分布门改为稳健统计或物理锚定窗口，应该使用几次独立 WT replicate
  才能形成可接受的 holdout 证据。

## 选项

### A. 在 E2 锁定工具链下重新校准并做独立 holdout（推荐）

保留 receptor、ligand、box、Vina 1.2.6、CPU8、exhaustiveness、spacing、
`num_modes=20` maximum 语义和 IFP 合同。geometry 门只使用 WT 数据重新
校准，不读取 mutant score、ratio、IFP 或排名来定阈值。

建议分两道独立门：

1. 新增一个预先锁定 seed 的四臂 WT replicate
   （Gpr2/Gpr3 × ascr18/ascr3，共 4 jobs），与现有 seed 42 WT 证据一起
   估计跨 replicate 分布并冻结新 gate；
2. gate 冻结后，另起新 run 做 8-job 双配体 holdout smoke，且不得用该
   holdout 结果再次调阈值。

影响：新增 12 个 E2 docking jobs；能保留统一工具链和清楚的 calibration /
validation 分离。风险是计算成本增加，且两个 calibration seeds 仍只能给出
有限的运行间波动估计。

### B. 只保留 MODEL 1、frame、box、contact 和膜/蛋白物理检查为硬门

将完整 pose 分布降为审计指标，不再作为 fail-stop。

影响：不需要额外 WT calibration jobs，能最快进入 full run。风险是会显著
降低对错误 pose ensemble 的拦截能力，尤其可能让“MODEL 1 正常、后续大量
pose 落入错误高度簇”的 job 通过。不推荐。

### C. 恢复历史工具链

Gpr2 尝试回到 Vina 1.2.5；Gpr3 尝试重建历史 Windows 环境。

影响：会拆分 production toolchain。Gpr3 的精确历史环境身份缺失，无法证明
真正复现；PDBQT 和平台差异也会重新引入。不可作为当前推荐路线。

### D. 保持当前 fail-stop

不改门、不新增作业，继续阻塞 full run。

影响：科学风险最低，但 frame-repair 主线不再前进。

## 推荐路线与已执行动作

选项 A 的第一步已获单独批准并执行，授权范围为：

> 在现有 E2 锁定环境中创建新的、不可覆盖的 geometry-calibration run；
> 固定一个尚未使用的 seed，运行 Gpr2/Gpr3 WT × ascr18/ascr3 共 4 jobs；
> 仅用 WT 结果与现有 seed 42 WT 证据提出并冻结新 geometry gate；不运行
> mutant、不启动 320-job full run、不做 ratio/排名/候选、不安装依赖、
> 不 commit、不 push。四臂 WT calibration 审计完成后再次停下，提交新门
> 和下一道 8-job holdout smoke 的独立授权包。

执行结果见 [2026-07-31 日志](../../../docs/logs/2026-07-31.md) 和本地归档
`temp/docking_frame_repair_20260731_e2_wt_calibration_seed43_r3/`：

- seed 43 四个 WT jobs 全部正常完成，各返回 20 poses；技术合同仍为
  `1 <= actual_modes <= 20`；
- 4/4 IFP 和 4/4 历史 geometry gate 诊断完成；
- 旧门对 Gpr2/ascr18、Gpr2/ascr3 仍失败，对两项 Gpr3 通过；该结果只作
  跨 seed 诊断，未自动修改阈值；
- 没有运行 mutant、没有创建 full plan、没有启动剩余 320 jobs；
- `config.yaml` 和 geometry validator 阈值均未修改。

后续授权已完成以下动作：

- 四臂 MODEL 1 / pose 1 人工目视通过；
- 只使用 seed 42 + 43 WT evidence 冻结
  `docking-geometry-gate-v3`，gate identity
  `5b59c1d36b3b5e89e0c67ed9846c2b76b48bf1ca5ce8af9873a8562565740924`；
- 在新 run 中固定 seed 44 完成独立 8-job holdout；
- 8/8 docking、IFP、geometry 技术完成，但 Gpr3/R167Y-ascr18 为 14/16，
  Gpr3/R167Y-ascr3 为 11/18 且 MODEL 1 失败；
- terminal identity
  `43967837a7473c1a422df31e87924e727b1d9a54a1fe933f1252712bb7b5bbfa`
  记录 `fail_stop_before_full`；没有创建 full plan 或启动剩余 320 jobs。

逐 pose 复核进一步确认，两条失败 arm 的独立基础失败项都只有
`membrane_absolute_height`；box、径向距离、ProLIF 接触和
protein-over-membrane 检查全部通过。具体 pose 数、高度范围和距阈值差值见
[2026-07-31 日志](../../../docs/logs/2026-07-31.md)。

当前下一步必须是新的决策门：保持 fail-stop，或在不读取 mutant 排名的前提
下提出新的、可独立验证的 geometry 策略。任何改门、重做 holdout 或绕过门
进入 full-run 都需要单独授权。

## References / 所引

- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/terminal/smoke_terminal.json`
- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/docking/jobs/*/WT/*/geometry/geometry_report.json`
- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/environment_manifest.json`
- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/RUN_FILES.sha256`
- `temp/docking_frame_repair_20260730_e2_smoke_r1_v5/geometry_calibration_report.json`
- `temp/docking_frame_repair_20260731_e2_wt_calibration_seed43_r3/docking/wt_calibration_postprocess_completion.json`
- `temp/docking_frame_repair_20260731_e2_wt_calibration_seed43_r3/RUN_FILES.sha256`
- `temp/docking_frame_repair_20260731_e2_full_seed44_r1/terminal/smoke_terminal.json`
- `temp/docking_frame_repair_20260731_e2_full_seed44_r1/run_state_events.tsv`
- `temp/docking_frame_repair_20260731_e2_full_seed44_r1/RUN_FILES.sha256`
- `experiments/docking-repro/geometry-gates/20260731_seed42_seed43_wt_v1/geometry_gate.json`
- `src/modeling/docking-repro/config.yaml`
- `src/modeling/docking-repro/geometry_calibration.py`
- `src/modeling/docking-repro/geometry_gate.py`
- `docs/logs/2026-04-16.md`
- `docs/logs/2026-04-23.md`
- `docs/logs/2026-07-31.md`
- `codex/docs/plans/docking-frame-repair-18mode-recovery-contract-20260730.md`

## Referenced by / 被引

- `docs/INDEX.md`
- `docs/modeling/P0-molecular-docking.md`
- `docs/logs/2026-07-30.md`
- `docs/logs/2026-07-31.md`
- `codex/docs/plans/README.md`
