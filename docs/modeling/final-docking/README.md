# 受体对接、相互作用指纹与残基比较

本组材料覆盖 DAF-37、Gpr2 TWF154、Gpr3 TWF154、GprC 和 SRBC-64 的结构准备，
以及 ascr#3/ascr#18 的对接、ProLIF 指纹和残基映射分析。Gpr2/Gpr3 的全长与截短
构建体分别保留，不能只按受体名称合并结果。

| 内容 | 入口 |
|---|---|
| 方法、模型输入与命令 | [工具说明](../../../src/modeling/docking-repro/final-docking/README.md)、[环境](../../../environments/final-docking/INSTALL_AF2_RELAX.md) |
| 序列、预测结构、置信度、拓扑与比对 | [受体输入](../../../experiments/docking-repro/receptors/final-docking/) |
| 配体与原子映射 | [配体输入](../../../experiments/docking-repro/ligands/final-docking/) |
| 对接使用的 PDB/PDBQT | [准备后输入](../../../experiments/docking-repro/prepared/final-docking/) |
| 70 组 Vina 姿态和得分 | [Vina 结果](../../../experiments/docking-repro/results/final-docking/vina/) |
| ProLIF 指纹、CSV、SDF 与汇总工作簿 | [ProLIF 结果](../../../experiments/docking-repro/results/final-docking/prolif/af3/) |
| 残基对应和比较矩阵 | [MSA/ProLIF 证据](../../../experiments/docking-repro/analysis/final-docking/msa-prolif/) |
| 突变组合建议 | [工作簿](../../../experiments/docking-repro/mutagenesis/final-docking/recommendations/gpr2_gpr3_selectivity_mutation_recommendations.xlsx) |
| 可重建缓存及 runtime 的位置与校验值 | [外部文件清单](../../../experiments/docking-repro/analysis/final-docking/payload_manifest.tsv) |

研究正文依次见 [跨受体比较](prolif_cross_receptor_biological_summary.md)、
[MSA 与结构映射](msa_prolif_biological_report_zh.md)、
[选择性与突变建议](cross_receptor_selectivity_and_mutation_recommendations_zh.md)。
姿态和相互作用指纹是计算结果，突变建议仍是待验证假设；不等同于亲和力测量或功能验证。

Gpr2 TWF154 的全长结构、截短对接受体与两种配体的既有姿态同时用于
[六组 MD 输入来源](../../../experiments/md-simulation/results/gpr2-twf154-n84v-v368r/retained-20261005/README.md)。
删去 lid 的动机见[决策 006](../../decisions/006-gpr2-twf154-docking-lid-deletion.md)。

所引：本页链接的输入、程序、结果、报告和外部文件清单。
被引：[P0 Docking](../P0-molecular-docking.md)、[docking-repro 目录入口](../../../experiments/docking-repro/README.md)和[项目 INDEX](../../INDEX.md)。
