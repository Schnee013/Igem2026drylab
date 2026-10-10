# 六组模拟的运行与恢复工具

- `wt_controller_v1_5.py`：WT 生产控制器；N84V、双任务及剩余组控制器与其共享工具一并保留。
- `archive_closed_v1_3.py`：文件回收；`archive_closed_v1_2.py` 仍是交接程序核对旧进程身份时使用的版本。
- `lid_recovery_successor_v1.py`、`lid_pair_recovery_v1.py`：新 lid 两组的准备、接续与恢复。
- 其他准备、资格检查、监控脚本及 `upstream/` 保留调用关系；部分带旧版本号的文件仍被其他程序使用。

早期 WT 控制器和回收程序位于 `nkuliulab-e2:/ifs1/User/dengwei/igem/backups/wiki-freeze-abc-20261010/`，沿用仓库相对路径；文件身份见归档内 `MANIFEST.tsv`。[归档入口](../../../../docs/research/local-remote-sync-20261008/README.md)。

脚本需要相应工作包、输入清单和运行环境；执行范围以[工作单](../../handoffs/gpr2-twf154-autodl-dots-20261006/WORK_ORDER.json)及当前运行状态为准。
