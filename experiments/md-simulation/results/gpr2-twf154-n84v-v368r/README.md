# Gpr2 TWF154：当前保留范围与结果入口

**2026-10-10 当前研究入口：[四项局部机制分析](autodl-production-20261006/mechanism-20261010/README.md) → [中文报告](autodl-production-20261006/mechanism-20261010/REPORT_CN.md)／[机制图](autodl-production-20261006/mechanism-20261010/figures/mechanism_evidence_map.png)／[证据表](autodl-production-20261006/mechanism-20261010/EVIDENCE_TABLE.md)。** 复用六组既有轨迹完成突变位点邻域、基团锚定、局部拟合/lid 与时间顺序检查。N84V–ascr18 羧酸端锚定有证据，但 84 位到锚点的联系未建立；V368R 的局部重排可见，但主要锚点在 WT 中同样存在。独立数值复算、既有结果交叉核对及回收哈希通过，仍为不同母体/lid/pose 下的单重复探索；未追加 MD 或 FEP。详细方法、E2 路径和哈希回交付入口；记录见 [10 月 10 日日志](../../../../docs/logs/2026-10-10.md)。

> 2026-10-09 清理说明：已按用户选择移除历史性能和生产回收流水。当前研究沿下方后分析交付入口读取；原分析报告作为完成时快照保留，其中两条旧回收凭证引用的本地文件已清理。处置与短期回退记录见[清理记录](../../../../docs/research/local-remote-sync-20261008/cleanup-execution-20261009.json)。分析报告、数值和交付校验文件未改动。

**2026-10-09 基础后分析入口：[六组后分析交付](autodl-production-20261006/analysis-20261008/README.md) → [中文报告](autodl-production-20261006/analysis-20261008/REPORT_CN.md)。** 六组rep1各100ns完成PBC/拟合、共享七指标和六组比较，输入/processed、42次真实driver退出、指标内容与独立复算、本地回收SHA均验证通过。主要窗口50–100ns，证据限于各自母体/lid/pose下的单重复探索，不能确立突变因果、亲和力排名或机制。图表/配置/表格/验证已回收，大轨迹留E2并有路径与哈希。

生产及回收沿[AutoDL执行记录](autodl-production-20261006/README.md)、[六组E2原始文件树](autodl-production-20261006/E2_FILE_TREE.md)和77段600ns总凭证（原本地文件已按用户选择清理）回查。用户10月8日确认AutoDL已关机，原定时任务已删除；本轮不启动AutoDL、追加MD或恢复定时任务，未读取账单，未提交或推送Git。

下面10月5–6日条目保留输入选择、旧E2快照及交接经过；其中“尚未准备/未启动”是当时状态。两组新lid已在本轮分别完成自己的完整准备、资格及100ns生产，当前状态以上方入口为准。

**2026-10-06 接管入口：[狼尊 / GPT Dots 离线材料包](../../handoffs/gpr2-twf154-autodl-dots-20261006/README.md)。** 用户已选六组各 rep1、100 ns；材料包包含各自输入、必要环境/准备/运行工具和上下文。N84V–ascr18 复用生产前平衡起点后从零计算；不把旧 E2 生产快照用作迁移续跑。两组新 lid 仍需正式验收和完整准备；本次仅整理交接，未启动远端生产。

**2026-10-05 最新输入选择：[两组 ascr3 改用各自的 lid 重构起点](input-selection-20261005/README.md)。** V368R–ascr3、独立 WT–ascr3 采用 `lid_rebuilt_own_pose_v1`，已完成 [各自母体/pose 的并行候选生成](lid-rebuild-own-pose-20261005/README.md)，现各有静态筛选通过的待审坐标，正式验收与新体系准备未完成；其余四组沿原输入/准备来源，WT–ascr18 保留已有 Trp174 侧链修复。旧混杂 `rebuilt_*` 不恢复使用。当前选择表是 [selection.json](input-selection-20261005/selection.json)，原始保留包保持历史身份不变。

同日此前确定的长期保留范围如下；仓库或 Docking 已有文件只留软链接，不整包复制。

1. 四个原始突变体组合和两个独立 WT 的指定输入及预热结果。
2. 原始 N84V–ascr18、V368R–ascr3 rep1 两条生产的已有产物。
3. 精简的 lid 局部重建方法、相关代码指针与输入设计错误记录。

**历史保留包入口：[retained-20261005/README.md](retained-20261005/README.md)。** 该目录保存必要实体和软链接，不依赖 `/private/tmp` 的文件。六组预热完整保留；生产是 2026-10-05 10:12–10:17 回收的文件快照，轨迹分别至 16.44 ns 和 16.82 ns，尚非 100 ns 完成结果，也不抵扣本轮AutoDL六组600ns。

## 不纳入本次长期保留的内容

- 六套 `rebuilt_*`：旧重建分支改变了受体母体或跨组合共享 pose，不再用于本轮比较、输入选择或后续生产。精简原因见 [错误记录](../../../../docs/modeling/gpr2-twf154-input-design-error.md)。
- 四套回变 WT，包括原始与重建 lid：用户最新决定均不保留到本包；这取代先前“保留旧回变 WT”的决定。
- 旧 WT–ascr18 的 200 ns 项目：本来已有独立结果入口，本次不移动、不复制、不清理。
- 旧候选、安装环境、下载缓存、渲染视频和混装十四组的查看包。

本次完成的是筛选后保留，不包括对旧临时目录或 E2 目录的大范围删除。此前 `/private/tmp/gpr2-lid-archive-20261005/` 为全量临时副本，不再是当前长期保留入口。

## 方法与历史来源

两组新 lid 起点遵循 [固定本组合受体和 pose 的局部重建方法](../../../../docs/modeling/gpr2-twf154-lid-local-rebuild.md)。保留整理阶段未生成新候选，晚间仅完成原输入的有限性能短测；后续授权的局部生成已完成，见 [候选与检查记录](lid-rebuild-own-pose-20261005/README.md)；新膜体系准备及生产尚未启动。下一轮 [上卡测速方案](../../../../codex/docs/plans/gpr2-autodl-throughput-qualification-20261005.md) 先用 N84V 原生产输入的隔离副本测试调度，之后必须用新 lid 体系复核。原始版预热完成不能视为穿越问题解决。

原制备经过保留在 [2026-10-03 输入记录](input-audit/20261003/README.md)与 [独立 WT 记录](input-audit/20261003/native-wt/README.md)；其中早期共同骨架、共享 pose 与保留回变 WT 的表述属于当时经过，当前用途以本文和用户最新决定为准。

所引：用户最新取舍、六组实际来源、600ns生产及回收凭证（原本地文件已按用户选择清理）、[后分析交付与验收](autodl-production-20261006/analysis-20261008/README.md)、E2运行文件、历史[文件清单](retained-20261005/manifest.json)和[本地核对](retained-20261005/validation.json)。被引：[项目 INDEX](../../../../docs/INDEX.md)、2026-10-05/08日志、[2026-10-09 日志](../../../../docs/logs/2026-10-09.md)、原制备入口；其他下游未穷尽检索。保留各材料的历史身份。
