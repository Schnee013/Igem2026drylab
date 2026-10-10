# 六组既有轨迹：局部机制分析交付

2026-10-10。六组 rep1 × 100 ns 的四项补充分析均已完成并通过数值与文件验证；未追加 MD 或 FEP。

**先读 [中文报告](REPORT_CN.md)，再看 [机制证据图](figures/mechanism_evidence_map.png) 和 [逐命题证据表](EVIDENCE_TABLE.md)。** 图中明确区分实测结构联系、候选解释及尚未成立的因果链。报告的结论是：N84V–ascr18 的羧酸端锚定有具体证据，但 84 位到锚点的联系未建立；V368R 的局部重排可见，但主要锚点在 WT 中同样存在。现有六条不同起点轨迹不足以建立突变增强选择性的机制。

## 四项分析及输出

| 分析 | 输出与用途 |
|---|---|
| 84／368 位局部邻域与侧链状态 | [局部原子对](tables/local_pair_summary.csv)、[侧链二面角](tables/sidechain_rotamers.csv)、[两步空间近接](tables/proximity_bridges.csv)：寻找可定位的位点—口袋联系，不能把邻接解释为能量传递 |
| 配体的原子／基团锚定 | [基团接触](tables/anchor_group_occupancy.csv)、[氢键并集](tables/anchor_hbond_union.csv)、[阈值敏感性](tables/anchor_sensitivity.csv)：区分糖环、碳链及羧酸端，避免以残基名称推断相互作用类型 |
| 口袋与 lid 相对运动 | [六组汇总](tables/six_case_local_summary.csv)、[三种拟合图](figures/alignment_sensitivity.png)、[lid 几何图](figures/lid_geometry.png)：比较全受体、膜内核心及口袋拟合，识别整体运动的影响 |
| 时间顺序 | [事件表](tables/event_timeline.csv)、[时间图](figures/local_timeline.png)、[Arg368–Asp70 化学几何](tables/Arg368_Asp70_summary.csv)：记录接触先后及起点已存在的联系，不据此确立因果 |

另有 [实际 75 ns 构象图](figures/representative_structures_75ns.png) 和六组各 6 帧的 [可查看 PDB](structures/README.md)。全部图有同名 PNG、PDF、SVG。每组只是一条轨迹，主窗口 50–100 ns，100 ps 采样；不同母体、lid 与 pose 的限制贯穿结论。

## 方法与验收

[METHODS](METHODS.md) 说明选择依据、真实原子映射、距离/氢键口径、第二轮探索性复核及解释边界。[配置](configs/mechanism_config.json) 和 [原子对复核配置](configs/pair_detail_config.json) 对六组使用同一共享实现，显式 `CHIMERIC_MD_REPS=1`。主分析与原子对复核分别使用冻结的 `configs/source_v1`、`configs/source_v2`；两者的完成凭证记录各自源码和配置哈希。

总记录为 [final_acceptance.json](evidence/final_acceptance.json)：

- 六组重新读取完整 10001 个时间点；18 份 processed 输入哈希与上一轮凭证相符。
- 两轮各六组均真实退出 0；独立数值复算 975 项、原子对复核 528 项通过；原采样口径的 36 项接触交叉核对通过。
- 本地回收的 120 份逐组输出逐文件 SHA256 相符；最终 15 份图形与 E2 原件一致，5 张图均经可读性检查。
- 验证仅证明输入、实现、数值与交付的一致性，不代表科学机制或突变因果已经验证。

独立核验详见 [主数值记录](evidence/validation.json)、[原子对记录](evidence/pair_validation.json)、[既有接触交叉核对](evidence/previous_contact_crosscheck.csv)。[本地文件清单](evidence/local_artifacts.tsv) 记录大小和 SHA256；清单不包含自身。

## E2 路径与回溯

E2 根目录：`/ifs1/User/dengwei/igem/md/gpr2-autodl/analysis/`。

- 本次逐组派生表与精确代表坐标：`<case_id>/mechanism-20261010/`；原子对复核在其 `pair_details/`。
- 原 processed 轨迹：`<case_id>/processed/rep1/`。大体积 XTC 继续留 E2，具体输入路径与哈希见配置和各组 `input_identity.json`。
- 本次共享配置、源码、独立日志：`_mechanism_20261010/`；**最终图使用 `figures_final/`**，早期 `figures/` 为字体调整前版本。
- 中文报告、表格、图形、代表结构与验收记录的回收快照：`_mechanism_20261010/delivery/`。该快照用于恢复；仓库相对文档链接以本地结果目录为准。

六个 `case_id`：`native_wt_ascr18`、`raw_n84v_ascr18`、`raw_n84v_ascr3`、`raw_v368r_ascr18`、`v368r_ascr3_lid_rebuilt_own_pose_v1`、`native_wt_ascr3_lid_rebuilt_own_pose_v1`。最后两组各自重建 lid；WT–ascr18 保留原 Trp174 侧链修复。

E2 逐文件路径、大小及哈希见 [remote_artifacts.json](evidence/remote_artifacts.json)；逐组回收映射见 [主输出清单](evidence/delivery_manifest.json) 和 [原子对清单](evidence/pair_delivery_manifest.json)。原始 `runs/`、`operator_records/` 及上一轮输入保持只读；本次使用 2 线程、低 CPU 优先级、持久会话串行执行。

所引：[上一轮后分析交付](../analysis-20261008/README.md)、[六组输入来源](../../input-selection-20261005/provenance.json)、本轮配置/实测输出/验收。被引：[Gpr2 结果总入口](../../README.md)、[本轮结果入口](../README.md)、[项目 INDEX](../../../../../../docs/INDEX.md)、[2026-10-10 日志](../../../../../../docs/logs/2026-10-10.md)；其他下游未穷尽检索。
