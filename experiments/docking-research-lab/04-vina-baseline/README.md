# WT和删段结构的Vina探索

本目录按来源和运行协议保留基础对照。不同菌株、模型、删段方案和搜索参数分别说明，再由后续突变研究引用需要的基线与输入。

## 已核对的任务集合

| 集合 | 已有内容 | 来源与比较口径 |
|---|---|---|
| [ATCC全长r3](atcc-full-length-r3/README.md) | Gpr2/Gpr3×两配体，共4个作业的审阅导出包 | 外部Drylab运行来源见export_manifest；配体为−1电荷，以稳定pose ID复查 |
| [WT与短N端删段](wt-deltaN-comparison/README.md) | 7种受体构象×两配体，共14组pose及日志 | 包含Gpr2 ΔN1–16、Gpr3 ΔN1–5及参考受体；以各日志中的实际网格为准 |
| [多模型与删段资料](deltaNlid-source/) | outputs下70组pose及日志 | 含5类受体与多个模型/处理状态；原始目录名只是线索，参数见逐次清单 |
| [对应ProLIF分析](prolif-analysis/) | batch_manifest中70项均记录completed | 清单记录外部来源路径；接触与原对接结果的来源关系需按逐项记录查证 |
| [TWF154对齐WT及删段](twf154-aligned-controls/) | 8组带run.json的对接记录 | seed=44、40 Å框、exhaustiveness=200，与突变批次另列 |

[逐次运行清单](run-inventory.csv)从14+70+8组实际日志/记录提取受体、配体、网格、seed、评分和pose数。ATCC是独立的审阅导出包，其4项以原export_manifest及pose_index为准。

## 展示副本与残基范围

TWF154的32个结果文件与`deltaNlid-source/display/output/`中对应文件逐字节相同，见[展示副本核对](display-copy-check.csv)。两处都保留来源布局，但统计时只算同一组8次运行。

[受体编号检查](receptor-numbering.csv)记录多模型输入PDB的实际残基编号区间。实际删段需将具体模型与运行输入对应后判断，不能把名称含deltaN的资料都当成同一删段方案。

## 与突变研究的关系

突变流程引用多模型资料中的原序列、−1配体和共同对齐参考；原始来源保存在`deltaNlid-source/inputs/`。后续01–08使用seed=1919及26 Å框，具体身份和配置见[突变README](../05-mutant-research/README.md)。

本轮完成文件分组、日志参数提取、展示副本一致性和编号检查。外部历史路径的完整运行环境、每组人工pose审阅及科学结论验收仍需各任务的原始记录支持；不同协议的最低分不合并为统一排名。
