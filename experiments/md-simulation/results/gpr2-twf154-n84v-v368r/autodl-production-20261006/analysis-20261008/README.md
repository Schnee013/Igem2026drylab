# Gpr2 TWF154 六组 100 ns 后分析交付

**2026-10-09 已完成且全部验收通过。** 本目录名称沿任务接入日期 2026-10-08；后处理、七类共享指标与比较实际执行于 10 月 9 日凌晨。六组 rep1 各 100 ns，42 次共享 driver 真实退出为 0；内容验收 180 项、独立 RMSD 复算 60 项、动态接触交叉检查 48 项全部通过。六组 processed 各有 10001 帧并保留配体。[总验收 JSON](evidence/final_acceptance.json) 指向各项真实证据。

首先阅读 [中文结果报告](REPORT_CN.md) 和 [六组汇总表](comparison/six_case_summary.csv)。报告说明起点身份、逐组观测、六组比较和解释局限；汇总表保存主要窗口 50–100 ns 的原始精度均值、趋势、身份及原子/帧计数。每组仅一条轨迹，不能据此认定突变因果、亲和力排名或机制成立。

| 入口 | 用途 |
|---|---|
| [METHODS.md](METHODS.md) | 输入核验、合并、PBC/拟合、选择、时间窗口、采样、指标定义与复现环境 |
| [全程六组图 PNG](comparison/six_case_timeseries.png) / [PDF](comparison/six_case_timeseries.pdf) | 查看受体/配体运动、BSA、接触与主要窗口 |
| [RMSF 图](comparison/six_case_receptor_rmsf.png) / [表](comparison/receptor_RMSF_50_100ns.csv) | 按真实残基号定位波动；灰带为 lid 164–178 |
| [10 ns 块图](comparison/six_case_ten_ns_blocks.png) / [表](comparison/ten_ns_blocks.csv) | 同一轨迹内的时间变化；不是独立重复误差条 |
| [逐窗口统计](comparison/time_series_statistics.csv) | 全程、早期和后半程的均值、范围、时间标准差与趋势 |
| [动态接触热图](comparison/ligand_paths/matched_residue_contact_occupancy.png) / [表](comparison/ligand_paths/residue_contact_occupancy.csv) | 区分初始接触保留与新增接触，按各自残基身份读取 |
| [质心运动图](comparison/ligand_paths/matched_ligand_movement_timeseries.png) / [共同坐标系路径](comparison/ligand_paths/matched_centroid_path_common_frame.png) | 在同一受体参考下描述配体运动；不消除起点差异 |
| [代表帧索引](comparison/ligand_paths/representative_frames.csv) | 定位 E2 轨迹中的 0/50/75 ns、最大位移及末帧 |
| [输入/PBC 验收汇总](evidence/input_processed_validation.tsv) | 六组时间、合法重复、原子映射和全帧 PBC 检查，指向原验证 JSON |
| [逐组小产物](e2_delivery/) | 各自 system config、参考 PDB/solution TPR、七类指标 CSV/PNG/judgement、命令及验证日志 |

E2 数据根为 `/ifs1/User/dengwei/igem/md/gpr2-autodl/analysis/`。24 份派生 XTC 留在 E2，约 37.09 GB；[轨迹清单](evidence/retained_e2_trajectories.tsv) 记录全部路径与 SHA256。每组使用自身 `processed/rep1/solution.tpr` 或 `protein_ref.pdb` 配 `prod_protein.xtc`；该轨迹包含受体与配体。`prod_cluster.xtc` 是历史接口名，本轮内容为 nojump。原 `runs/`、`operator_records/` 保持只读。

[最终 E2 清单](evidence/e2_artifacts.tsv) 有 657 个文件，633 个小文件逐份回收到本地并[SHA 验证通过](evidence/local_delivery_validation.tsv)。清单排除 reader 缓存、锁及生成清单时仍写入的哈希日志；哈希日志单独保留。实际执行源码在 [v2](configs/deployed_source_v2/) / [v3](configs/deployed_source_v3/)，初次部署哈希文件不代替最终源码身份。v2 严格检查停在已证实的 PDB 配体名截断；v3 重新核对完整原子映射后运行，原失败记录保留。[本地交付哈希](evidence/local_deliverables.sha256) 覆盖本目录最终内容（排除其自身与运行缓存）。

所引：[生产回收入口](../README.md)、[E2 原始文件树](../E2_FILE_TREE.md)、[原输入来源](../../input-selection-20261005/provenance.json)、本目录方法/配置/真实输出/验证。被引：Gpr2 总入口、生产回收 README、E2_FILE_TREE、[INDEX](../../../../../../docs/INDEX.md) 与 [2026-10-09 日志](../../../../../../docs/logs/2026-10-09.md)；其他下游引用未穷尽检索。本任务未提交或推送 Git，未启动 AutoDL、追加 MD 或恢复定时任务。
