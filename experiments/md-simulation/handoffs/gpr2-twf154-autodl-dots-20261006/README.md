# 狼尊 / GPT Dots 离线接管包

**当前执行方式已改为普通本地 agent，取消邮件通知。** 用户反馈狼尊无法访问 SSH，因此直接使用本目录现成材料，不再上传或重组分卷。先读当前 [WORK_ORDER.json](WORK_ORDER.json)、[INPUTS.md](INPUTS.md)、[RUNBOOK.md](RUNBOOK.md)、[MONITORING.md](MONITORING.md)，按 [当前执行提示词](../../../../codex/docs/plans/gpr2-twf154-dots-handoff-20261006.md) 推进。认证只读私密 MD 的 SSH 字段，新端口尚未实连核验；该 MD 其余旧 Dots/邮件指令不适用。`bundle/` 与下述归档是冻结快照，仍用于输入完整性检查；其中旧操作者、认证、邮件与上传方式由本目录当前工作单覆盖，不修改快照去伪造原哈希。

以下发送记录与离线包说明保留历史用途，不代表当前 agent 必须邮件通知或处理附件。

用户已选择六组各 rep1、每条正式生产 100 ns，共 600 ns；必要准备、验证、实际运行、持续监测和回收交由狼尊。此处已整理无需访问 Roy 本地文件的材料；**本次没有连接 AutoDL、启动生产或替狼尊建立监测任务。**

## 发送哪些文件

上传页面限制单附件 20 MB，当前使用 [upload-20mb/](upload-20mb/READ_ME_FIRST.md) 下的五个普通 ZIP 分卷，必须全部发送：

1. [drylab-md-v3-01-of-05.zip](upload-20mb/drylab-md-v3-01-of-05.zip)
2. [drylab-md-v3-02-of-05.zip](upload-20mb/drylab-md-v3-02-of-05.zip)
3. [drylab-md-v3-03-of-05.zip](upload-20mb/drylab-md-v3-03-of-05.zip)
4. [drylab-md-v3-04-of-05.zip](upload-20mb/drylab-md-v3-04-of-05.zip)
5. [drylab-md-v3-05-of-05.zip](upload-20mb/drylab-md-v3-05-of-05.zip)

每个小于 20,000,000 字节，第 1 卷内含重组工具、清单与说明；重组为完整的 `gpr2-twf154-dots-20261006-v3-new-access.zip` 后再次校验。具体体积、哈希及恢复测试见 [传输清单](upload-20mb/upload_manifest.json) 和 [验证记录](upload-20mb/validation.json)。v1/v2 大包和旧邮件补丁保留历史身份，不再沿用其认证指引。

**旧凭据已作废，旧 PRIVATE_ACCESS.txt 已按用户要求删除。** 用户随后提供新的 SSH 连接信息，并反馈提示词输入框长度受限；本轮改为单独交付 `START_MD_PRODUCTION.md`，里面已填好最新连接信息及完整任务。该含凭据文件仅在私密临时目录交付，不进入仓库或分卷；仓库 [提示词模板](../../../../codex/docs/plans/gpr2-twf154-dots-handoff-20261006.md) 只保留认证占位符。独立 MD 的最新 SSH 信息优先于已冻结分卷中的旧端口/占位记录，分卷无需重传或改动。

把五个 ZIP 附件和 `START_MD_PRODUCTION.md` 一并交给狼尊，输入框只需要求它先读该 MD 并按全文执行。只有恢复后 `compute/` 与同级工作单是必须放到算力卡上的材料；`context/` 供狼尊在自己的工作区恢复上下文。若它没有 Shell、SSH/SFTP 或定时执行能力，附件本身不会补出这些工具，必须先实际确认。

三类邮件正文已在 [EMAIL_TEMPLATES.md](EMAIL_TEMPLATES.md) 逐项规定：无法处理的错误、必须暂停的错误、阶段性成果。触发及发送失败处理见 [MONITORING.md](MONITORING.md)。本次只更新交接要求，没有配置发件账号、部署通知服务或实际发信。

归档体积、SHA256、文件清单和恢复方式见 [archive.json](archive.json) 与 [export_manifest.json](export_manifest.json)。`bundle/`、压缩包是本地 payload，已单独忽略，不纳入 Git；本次没有提交或推送。

## 六组的实际起点

| 组合 | 包内材料 | 正式生产前还需做什么 |
|---|---|---|
| N84V–ascr18 | `raw_n84v_ascr18/zero_start_100ns`，包含生产前 NPT 末态和从零生产 TPR | 当前机器、结构用途、数值兼容与续跑复核 |
| N84V–ascr3 | 自己的原输入、最小化及 125 ps 预热末态 | NPT、约束释放与最终准备验收 |
| V368R–ascr18 | 自己的原输入、最小化及 125 ps 预热末态 | NPT、约束释放与最终准备验收 |
| 独立 WT–ascr18 | 独立 WT、自己的 pose、已选 W174 侧链修复分支的预热末态 | NPT、约束释放与最终准备验收 |
| V368R–ascr3 新 lid | `v368r_ascr3_lid_rebuilt_own_pose_v1` 的候选、自己的 pose 和装配参考 | 候选结构/能量验收，重建完整膜/水/离子体系和全部准备 |
| 独立 WT–ascr3 新 lid | `native_wt_ascr3_lid_rebuilt_own_pose_v1` 的候选、自己的 pose 和装配参考 | 候选结构/能量验收，重建完整膜/水/离子体系和全部准备 |

**“生产起点”不是“E2 跑到一半的轨迹”。** N84V–ascr18 复用的是当时正式生产开始前的平衡状态，接管后从生产时间 0 重新跑 100 ns。本包没有旧 E2 生产轨迹或生产中途 CPT，不抵扣旧完成量；也不是可直接追加的迁移续跑包。

每组受体/配体的具体文件、母体来源、原 pose 和重构边界见 [INPUTS.md](INPUTS.md)。两组新 lid 只有静态初筛通过，不能因为有文件就视为 MD 准备完成。未经验证不得更换 pose、母体或混用旧检查点。

## 狼尊的工作重点

- 以 [WORK_ORDER.json](WORK_ORDER.json) 固定六组、rep1、100 ns 范围；先完成 [RUNBOOK.md](RUNBOOK.md) 中环境、来源、结构、准备、数值和续跑检查。
- 根据实际推进的 ns/day 做有限调优；不能用 GPU 利用率或历史两组速度代替六组实测。新 lid 准备成本另计，单价 2.88 元/小时。
- 按 [MONITORING.md](MONITORING.md) 进行持续现场复核、异常停机取证、去重续跑和磁盘管理；状态必须有新鲜进程/文件证据。
- 六组均核对 100 ns 终点、分段连续、输出完整并回收到实例以外，才算完成。实例按用户约定不关机，并提醒继续计费。

## 本次验证的边界

[本地脚本检查](validation/validation.json) 已覆盖语法、正常分段、模拟 LINCS 异常停机、拒绝覆盖已有输出、生产缺验收记录时拒绝启动，以及认证未进入 payload。[输入静态核对](validation/input_static_checks.json) 覆盖引用路径、有限坐标、拓扑/坐标原子数；两组新 lid 的此项核对针对旧的自身膜坐标参考，不是新完整体系。

[分卷重组与异地目录解压校验](upload-20mb/validation.json) 记录五卷恢复后原 ZIP 身份、全部清单文件哈希、无软链接和拓扑 include 完整性，并验证缺卷或损坏会阻止恢复；旧版本校验保留在 validation 目录。上述检查均不等于实际 GROMACS 编译、5090 再测速或科学验收；这些工作交由狼尊执行并产生日志。

所引：[当前输入选择](../../results/gpr2-twf154-n84v-v368r/input-selection-20261005/README.md)、[保留包](../../results/gpr2-twf154-n84v-v368r/retained-20261005/README.md)、[新 lid 候选](../../results/gpr2-twf154-n84v-v368r/lid-rebuild-own-pose-20261005/README.md)、[历史实测与环境](../../results/gpr2-twf154-n84v-v368r/benchmark-20261005-autodl/README.md)，具体导出来源与哈希见清单。

被引：[INDEX](../../../../docs/INDEX.md)、[DOCMAP](../../../../docs/DOCMAP.md)、[当天日志](../../../../docs/logs/2026-10-06.md)、[当前结果入口](../../results/gpr2-twf154-n84v-v368r/README.md)。输入、授权范围或工具发生变化时须重新导出和校验，不覆盖已经发出的归档身份。
