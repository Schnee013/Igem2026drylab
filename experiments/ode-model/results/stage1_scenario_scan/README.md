# P0 ODE Phase 1：归一化情景扫描结果包

## 范围与边界

本目录是 2026-07-16 生成的 Phase 1 情景扫描结果包。它扩展 Phase 0 单一
time-course，执行三组可配置、可重复的工程情景：剂量 × 半响应、偶联 ×
输出泄漏、以及 1/2/4 copy × gain × 观察时间。

所有配置数值和输出均为 `scenario_prior`。它们用于比较“在何种假设下存在
响应窗口、哪些未知量会改变解释”，不是项目实测的 `EC50`、偶联速率、
检测限、最佳 copy number 或最终构建推荐。docking `ΔG` 没有进入任何数值
字段。

## 复现

从仓库根目录执行：

```powershell
python src/modeling/ode/run_scenario_scans.py
python src/modeling/ode/plot_scenario_scan.py
python -m unittest tests.modeling.test_ode_minimal_solver tests.modeling.test_ode_scenario_scans -v
```

默认运行产生 143 个情景（包括匹配的无 ligand 对照）和 23,023 条 time-course
记录。完整扫描范围的权威输入见
[`../../configs/stage1_scenario_scan.json`](../../configs/stage1_scenario_scan.json)。

## 文件说明

| 文件 | 角色 | 内容 |
|---|---|---|
| `scan_suite_config_snapshot.json` | 运行时输入快照 | 本次扫描实际使用的 suite config 副本。 |
| `scenario_manifest.csv` | 情景合同 | 每个 scenario 的 ID、scan family、角色、轴值和完整数值参数快照。 |
| `timecourses.csv` | 数值结果权威源 | 每个 scenario 的完整 `G_on`、MAPK、sTF、GAL 与 color time-course。 |
| `final_metrics.csv` | 紧凑分析表 | 最终 color、曲线面积、相对自身最终值的半程时间，以及相对匹配无 ligand 对照的差值/比值。 |
| `stage1_scenario_summary.png` | 图形摘要 | 三组扫描的条件性比较图；图中保留 `scenario_prior` 边界。 |
| `run_metadata.json` | 运行摘要 | 情景数、time-course 行数、模型范围和结论边界。 |

无 ligand 对照与各 ligand 情景保持除输入外的全部参数相同。对于泄漏扫描，应优先用
`final_color_ratio_vs_no_ligand` 看相对可分辨性；纯差值会因当前方程中 leak 的加性形式
而抵消，不能单独代表背景风险。

## 后续消费规则

- 只有在宽的 `scenario_prior` 范围内仍成立的趋势，才可写为稳健的条件性设计观察。
- 需要通过同一酵母底盘下的 dose-response、无 ligand 背景、time-course、表达/定位和
  chimeric Gpa1 coupling 实验，把对应字段替换为可追溯数据后，才能升级为校准解释。
- 具体参数状态、可替换实验和不可使用的数值来源见
  [`docs/modeling/P0-ode-lumped-parameter-register.md`](../../../../docs/modeling/P0-ode-lumped-parameter-register.md)。
