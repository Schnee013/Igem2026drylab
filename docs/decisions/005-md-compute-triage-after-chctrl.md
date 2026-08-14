# 决策 005：MD 算力收缩与突变 GPR MD 启动顺序

- **日期**: 2026-06-26
- **状态**: 已确认，执行前置审计中
- **关联方向**:
  - [P0-md-simulation](../modeling/P0-md-simulation.md)
  - [P3-chimeric-gprotein](../modeling/P3-chimeric-gprotein.md)
  - [P0 docking MD candidate-system shortlist](../modeling/P0-docking-md-candidate-shortlist.md)
  - [NKULiulab E2 共享云服务器使用规范](../ops/nkuliulab-e2-cloud-server.md)

## 背景

用户校准：chimeric Gpa1 的 control/chctrl 组 3 reps MD 完成发生在旧 Slurm 路线；E2 路线只有 chctrl rep1 及其 smoke / benchmark / early-gate 证据，不能写成 E2 完成 3 reps。当前可用算力主要是 E2 共享服务器；此前 chimeric MD 几乎占满 A100，影响其他用户使用，因此后续 MD 必须先降低算力占用。

旧 Slurm chctrl 3 reps 只能作为“历史控制组 MD 已完成”的进度事实进入路由；E2 chctrl rep1 只能作为单 replicate 的 E2 运行/early-gate 证据。任何稳定性结论、阈值判断或科学解释仍需回到 GROMACS log、trajectory、checksum、analysis output 和对应日志审查后再写入结果。

## 决定

1. 暂停继续推进 chimeric Gpa1 候选体系的大体系 full-production MD，不再按旧 E2 unified rerun 计划直接启动 Ch-1/Ch-2/Ch-4 长程生产。
2. chimeric Gpa1 线下一步先做体系优化方案调研，重点考察：
   - 减少体系大小，只保留回答 receptor-Gpa1 interface 稳定性所需的必要原子、膜/水/离子范围；
   - 或加入更强物理限制、分层 restraint、局部区域约束等算法，降低算力占用并保持可解释边界。
3. 在 chimeric 体系优化方案调研期间，先启动突变 GPR MD 的前置工作。当时的起点来自 2026-05 refreshed docking shortlist 中 Channel A/B 的优先候选位点：
   - Channel A: `Gpr2_R59C`
   - Channel B: `Gpr3_R167Y`
4. 突变 GPR MD 不直接进入 full production。第一步只做体系大小核查、资源估算和短程算力测试；通过共享资源门禁后，再单独决定 production 长度、rep 数和排程。
5. E2 上所有后续 MD 操作必须按共享服务器资源纪律执行：不长期独占 A100，不启动未经确认的长程并发任务，测试命令需显式记录线程、GPU 占用、运行目录和日志路径。

## 仍未决定

- chimeric Gpa1 缩小体系的具体原子选择、边界条件、膜/水保留范围和 restraint schedule。
- 缩小体系或强约束算法是否可作为原 full-system MD 的替代证据；在方案审查前只能作为候选路线。
- 突变 GPR MD 的 final production 时长、rep 数、是否保留 apo 对照、是否引入更长尺度或自由能计算。
- 旧 Slurm chctrl 3 reps 与 E2 chctrl rep1 的最终分析结论；需分别完成结果文件和日志级 source audit 后再写入科学结论，不合并为同一 E2 证据集。

## 后果

1. **执行优先级**：MD 主线从“继续 chimeric unified rerun”切换为“chimeric 省算力方案调研 + mutant GPR MD 前置算力测试”。
2. **计划边界**：旧 E2 chimeric restart plan 和 unified rerun sites plan 保留为历史执行路线、脚本和 provenance 参考；当前 full-production 启动需要新的 work order 和审批。
3. **候选来源（历史）**：突变 GPR MD 的初始候选来自当时的 refreshed docking shortlist 和 release report；该选择解释 2026-06 至 2026-07 已执行 R59C/R167Y MD 的输入来源，但不再定义当前或未来生产队列。
4. **证据边界**：减少体系或强约束会改变物理解释范围；未来写作必须明确它们是省算力 protocol，而不是无条件等同于原 full-system production MD。

## 历史输入边界

R59C/R167Y 的初始选择来自 2026-05 历史 shortlist。已完成 MD 的终态和输入身份
保持不变；其允许用途是描述各自实际起始 pose 下的单重复探索性行为。新的候选或
production 设计需要独立 work order、输入证据和资源门禁。
