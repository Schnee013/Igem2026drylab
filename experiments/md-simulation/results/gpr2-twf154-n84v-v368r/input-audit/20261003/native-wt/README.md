# 独立 WT 补跑

> **2026-10-05 用途更新**：现有六套重建 lid 版本停用；四套回变 WT 也按用户最新决定不纳入长期保留。六个原始来源组合及两条生产已有产物已筛选保存到仓库。下文仅保留历史经过；当前保留范围、软链接目录和方法见 [结果说明](../../../README.md)。

2026-10-03 用户指定使用 docking 项目的独立 WT：固定 AF3 model 0，配体取同模型 deltaN（删除 1–21、164–178）docking 的 MODEL 1，恢复对应全长受体；不重新 docking。全长与 deltaN 保留原子坐标逐原子一致。配体重原子坐标保持原样，依据 PDBQT 中的化学映射补全键级、手性和氢。

来源与输入身份见 [input_manifest.json](input_manifest.json)。独立 WT 本机环境与中间产物：`/private/tmp/gpr2-wt-replacement-20261003-_214_9xd`；E2：`/ifs1/User/dengwei/igem/md/gpr2_twf154_native_wt_20261003`。

2026-10-03 当时决定（已被 10-05 最新保留范围取代）：**旧的回变 WT 全部保留**，与独立 WT 同列但必须明确来源。此前删除请求已撤销，未删除任何旧 WT 文件。旧 WT 来源见 [上级说明](../README.md)。

生产授权：独立 WT 两组预热完成后，推进 N84V–ascr18、V368R–ascr3 原始全长模型路线的 rep1 各 100 ns；先按项目现有 CHARMM 方案做 125+500+500+500 ps 膜压力平衡和约束递减，再做 1000 ps 无位置/二面角约束准备；若最后 500 ps 的面积、密度或盒高两半窗口仍有超过 2% 的变化，可再延长 1–4 ns 准备，仍异常则停下检查。上述条件只筛查明显漂移，不宣称结合或全体系热力学收敛。两者使用各自原始模型及 pose，主生产比较不再是共同起始骨架或同配体共享 pose 设计；重建 lid 支路当时保留为制备对照，现已按上述 2026-10-05 决定停用。

所引：用户指定 docking 目录、输入清单、运行日志。被引：项目 INDEX、2026-10-03 日志、上级结果说明。准备中的状态不等同于预热完成或生产已启动。

参数所引：[现有 Gpr2 NPT 模板](../../../../../systems/Gpr2_WT/gromacs/step6.3_equilibration.mdp)；[GROMACS 2025.4 压力耦合说明](https://manual.gromacs.org/2025.4/user-guide/mdp-options.html#pressure-coupling)。沿用 C-rescale、半各向同性压力耦合、303.15 K、1 bar；制备约束参考坐标随盒缩放。生产为无位置/二面角约束的 100 ns，2 fs 步长。

当前状态（2026-10-03 12:23 北京时间核验）：**独立 WT–ascr18 / WT–ascr3 均完成 125 ps 预热**，见 [结果记录](preheat_status.json) 和 [所用最小化分支](selected_run_manifest.json)。原 12 套与独立 WT 两套已合并为 14 套查看结果；回变 WT 四套全部保留。

WT–ascr18 原始最小化及冻结配体分支曾出现 Trp174/糖环互锁与成键畸变，没有沿失败末态进入预热。最终采用 [Trp174 侧链朝向修复](trp174_orientation_repair.json)：离散修复只改该侧链，骨架、配体及其他原子当时不动；随后原力场最小化及预热允许松弛。选用 `attempt6_trp174_orientation/em.gro`，预热末态没有发现异常键长、手性翻转或已检查环的互锁。不能把离散修复解释为真实解套运动。

**原始全长 N84V–ascr18、V368R–ascr3 两组 rep1 的 100 ns 生产均已实际开始。** 北京时间 2026-10-03，N84V–ascr18 于 17:03:34 启动，V368R–ascr3 于 17:32:25 启动。17:35–17:36 两次核对确认同一生产进程持续运行、步数增加，分别到 0.28 ns 和 0.03 ns。见 [启动记录](production_launch.json)；它是带时间的启动证据，不能当作 100 ns 完成记录。

两组都完成了既定 NPT 和约束释放流程，不需要额外准备延长；预热与准备合计 2.75 ns，生产时钟重新从零计数。生产参数均为 100 ns、2 fs 步长，无位置或二面角制备约束。本次自动跟进的结束条件已经满足，E2 的两个计算进程继续运行至各自 100 ns 目标；未增加对照生产、rep 或时长。

原会话名为 `twf154_raw_n84v_ascr18_rep1_100ns` 与 `twf154_raw_v368r_ascr3_rep1_100ns`。后续实时状态仍需核对实际进程、`production.log` 和 checkpoint，不能按会话名判断。此前 [NPT 快照](priority_npt_progress.json)仅保留准备阶段历史。


运行恢复：北京时间 11:51 左右，默认 tmux 服务及本任务接续进程消失，原因尚未确定。50 ps 升温正常结束且检查点、输入身份与结构均完整，因此只恢复剩余 75 ps 恒温，没有重复升温。11:56 恢复完成监测和原两条等待任务。当前会话使用独立 socket `/ifs1/User/dengwei/igem/md/gpr2_twf154_native_wt_20261003/tmux.sock`；核对时使用 `tmux -S <该路径> list-sessions`，不能因默认 tmux 为空而重复启动。

本地已回收两组原始全体系坐标、预热末态、checkpoint、恒温短轨迹及关键记录，见 [回收清单](completed_return_manifest.json) 和 [本地核验](completed_return_verified.json)。文件在 `/private/tmp/gpr2-wt-replacement-20261003-_214_9xd/results/completed_wt/`；结构查看包只导出受体与配体，不能作为完整膜体系的重启输入。

两组固定生产输入与 NPT 末态已备份到 `/private/tmp/gpr2-wt-replacement-20261003-_214_9xd/results/production_launch/`，见 [文件清单](production_input_return_manifest.json) 和 [本机核验](production_input_return_verified.json)。持续增长的生产轨迹仍在 E2，本次未把它们称为完成归档。
