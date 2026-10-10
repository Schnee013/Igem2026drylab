# 01-sidechain-combination

固定骨架改侧链组合：历史数据，不纳入当前AF3位点筛选。cli/helpers.py的通用ProLIF函数仍被AF3流程调用。

- `cli/`：用户运行的分阶段命令与辅助代码；不是计算结果。
- `run-01/`：已完成的首轮结果；受体/配体目录及文件名保持原样。
- `run-01/score_comparison.csv`：该批次评分及WT差分。
- 每个受体的raw_model0/trimmed/input/prepared/receptor文件为结构准备链；ascr3、ascr18下的poses、日志、summary、top1_contacts为对接及接触结果。

运行约定见[操作协议](../../user-run-vina.md)。历史日志中的旧绝对路径保留作溯源。
