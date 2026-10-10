# Gpr2 TWF154：本地 agent 生产接管提示词

请在 `/Users/roy/Documents/drylab` 使用 drylab-project 技能，接管 AutoDL 上的 Gpr2 TWF154 MD。已授权六组各 rep1、每条正式生产 100 ns，共 600 ns；必要环境、输入准备、验收、调优、生产、监测、异常处理与回收均由你执行，通过验收后直接生产，不逐项重复询问。当前只完成了材料交接，新端口和远端进度尚未核验；先查现有作业，避免重复启动。

本次由可访问本地文件的普通 agent 执行，不再使用狼尊，不需要附件、上传分卷或解压重组。用户已明确取消邮件通知：不配置邮件、不发送测试或成果邮件，只在当前任务对话报告关键进展、异常、需决策事项和完成。下面当前工作单优先于旧 Dots 文档中的操作者、SSH、邮件及传输指令。

按顺序读取这六处：

1. 当前执行范围与通知约定：`/Users/roy/Documents/drylab/experiments/md-simulation/handoffs/gpr2-twf154-autodl-dots-20261006/WORK_ORDER.json:1`。
2. 最新 SSH 认证：`/private/tmp/gpr2-dots-handoff-20261006/START_MD_PRODUCTION.md:7`，只读取第 7–9 行的连接与认证字段；不要执行该文件其余旧 Dots、邮件或分卷指令。当前端口 27626，旧端口 31540 和旧凭据禁用。不要将密码打印到终端、写入日志、脚本、仓库或镜像；文件缺失时明确报告，不能猜测或回退旧凭据。
3. 六组实际输入、来源及准备差异：`/Users/roy/Documents/drylab/experiments/md-simulation/handoffs/gpr2-twf154-autodl-dots-20261006/INPUTS.md:1`。
4. 环境、准备、科学/数值验收、性能调优、生产与回收：`/Users/roy/Documents/drylab/experiments/md-simulation/handoffs/gpr2-twf154-autodl-dots-20261006/RUNBOOK.md:1`。
5. 持续监测、停机取证、恢复与当前对话通知：`/Users/roy/Documents/drylab/experiments/md-simulation/handoffs/gpr2-twf154-autodl-dots-20261006/MONITORING.md:1`。
6. 实体输入与脚本的冻结材料入口：`/Users/roy/Documents/drylab/experiments/md-simulation/handoffs/gpr2-twf154-autodl-dots-20261006/bundle/00_START_HERE.md:1`。该目录只是带日期的快照，忽略其旧上传/邮件要求；实际计算材料和环境配置在同目录 `compute/`，溯源证据在 `context/`。

先在冻结 bundle 根目录运行 `python3 compute/scripts/verify_bundle.py --root .`。通过后再创建独立工作副本部署；部署使用上一级当前 WORK_ORDER.json，记录其与快照的差异和新哈希，不改原 bundle、MANIFEST 或原输入。软件环境和中间文件放 `/private/tmp/` 的任务目录；正式结果回收进项目 MD 结果目录，更新 INDEX 与当天日志，不提交或推送 Git。

严格按 INPUTS 与 RUNBOOK 的实际阶段推进：N84V–ascr18 从生产前平衡起点重新生产 100 ns，不接 E2 中途轨迹；另三组补 NPT，两组新 lid 必须验收并重新完整准备。不能替换母体/pose、混用旧检查点、忽略异常、降低物理或输出设置来跑通。原包通过完整性检查不等于六组已通过生产验收。

不要停止或修改 E2 作业。不得自行新增重复、延长、租新实例或付费扩容。单价沿工作单 2.88 元/小时；不套用旧 benchmark 的一小时上限，但必要成本显著偏离估计时报告并请求取舍。完成后保留实例，不自行关机，提醒继续计费。

下一步：校验本地材料并用最新凭据实际连接，报告资源、已有进程、六组准备状态、时间/费用估计与结果回收位置；随后按已授权范围完成准备和生产。实际建立服务器持久运行及周期现场复核；不能把一次启动当成持续值守。遇到影响正确性或浪费算力的异常，先停止受影响的本任务作业并保全证据，再在当前对话报告。最终以六组各 100 ns、分段连续、输出完整并在实例外回收校验通过为完成条件；科学限制按工作单披露。
