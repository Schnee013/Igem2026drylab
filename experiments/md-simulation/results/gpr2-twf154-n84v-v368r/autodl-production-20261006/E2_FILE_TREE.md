# E2 数据与后分析输入入口

2026-10-09：本文件保留清点之后新增的后分析输入路由；原本地分段/回收流水已按用户选择清理。数据根仍为 `/ifs1/User/dengwei/igem/md/gpr2-autodl/`；原 `runs/` 和 `operator_records/`、派生 `analysis/` 均未被本次清理操作。

按以下现存材料定位实际文件，不依据目录名推断分析已经完成：

| 需要查找的内容 | 当前来源 |
|---|---|
| 原输入和处理方法 | [METHODS.md](analysis-20261008/METHODS.md)及[原六组来源](../input-selection-20261005/provenance.json) |
| 六组输入、PBC 与原子映射检查 | [输入/处理检查表](analysis-20261008/evidence/input_processed_validation.tsv) |
| E2 派生轨迹的完整路径与哈希 | [轨迹清单](analysis-20261008/evidence/retained_e2_trajectories.tsv) |
| 全部交付产物身份 | [E2 产物清单](analysis-20261008/evidence/e2_artifacts.tsv)及[本地校验](analysis-20261008/evidence/local_delivery_validation.tsv) |
| 研究结果和解释范围 | [交付入口](analysis-20261008/README.md)、[中文报告](analysis-20261008/REPORT_CN.md)、[总验收](analysis-20261008/evidence/final_acceptance.json) |

每组实际使用的配置、结构及验证材料位于 [e2_delivery](analysis-20261008/e2_delivery/)。原始/处理后轨迹的读取须遵守方法文件中的原子匹配和时间网格要求；此次目录清理没有重新核验服务器或重算轨迹。

所引：上表现存交付材料。被引：[本层入口](README.md)、后分析交付入口和项目 INDEX。删除范围见[处置记录](../../../../../docs/research/local-remote-sync-20261008/cleanup-execution-20261009.json)。
