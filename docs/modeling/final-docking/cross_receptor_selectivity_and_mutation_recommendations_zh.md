# ASCR3/ASCR18 跨受体识别与突变建议

## 合并后的判断

把 ProLIF 的五-model 配对结果、五受体 MSA、结构残基映射和 gpr2/gpr3 突变建议放在一起，最清楚的主线仍然属于 ASCR18：Gpr2 W338、Gpr3 W306 和 GprC W388 构成一个三受体共享的 TM6 芳香核心候选。三个 Trp 在 MAFFT 和 MUSCLE 中落入同一列，两两结构映射在 25/25 个模型组合中一致，也都映到 c7xmsA:226；同时，它们在各自受体内都稳定偏向 ASCR18。

ASCR3 目前仍以受体特异信号为主。GprC N56–HBAcceptor 是唯一达到既有区分标准的 ASCR3 候选，适合用 N56A 直接测试同一受体内的 ASCR3/ASCR18 响应比。五受体 MSA 对 N56 的对应和化学保守性较弱，因此它更像 GprC 的配体区分位点，而不是跨五受体共享核心。

新的突变工作簿补充了五套 gpr2/gpr3 工程方案。它们主要围绕两个思路展开：一是削弱现有的 ASCR18 偏向接触，从而把相对响应推向 ASCR3；二是在 Gpr3 中增加或保留芳香疏水环境，把相对响应推向 ASCR18。工作簿提供的是设计方向，逐位点的支持强弱由 ProLIF 和残基映射结果决定。

## 三受体共享的 ASCR18 TM6 芳香核心

| 受体 | 位点 | 受体内区分信号 | 跨受体证据 |
| --- | --- | --- | --- |
| Gpr2 deltaN | W338–Hydrophobic | 5/5 model 出现，5/5 偏向 ASCR18，中位差 0.222 | 与 Gpr3 W306、GprC W388 同 MSA 列；结构映射 25/25 一致 |
| Gpr3 deltaN | W306–Hydrophobic | 4/5 model 出现，3/5 偏向 ASCR18，中位差 0.222 | 与另外两个 Trp 同 MSA 列；结构映射 25/25 一致 |
| GprC WT | W388–Hydrophobic | 5/5 model 出现，3/5 偏向 ASCR18，中位差 0.333 | 与另外两个 Trp 同 MSA 列；结构映射 25/25 一致 |

这组三个位点是目前最适合称为“跨受体共享机制候选”的残基组。DAF-37 和 SRBC-64 在该位置的直接 MSA 与结构映射仍有分歧，因此当前命名停留在“三受体共享的 ASCR18 TM6 芳香核心”。

最直接的验证方式是平行构建 Gpr2 W338F、Gpr3 W306F 和 GprC W388F。W→F 保留芳香性并缩小侧链体积，适合检验 Trp 侧链大小是否特别有利于 ASCR18。若出现清楚的双配体选择性变化，再增加 W→A 测试去除芳香环后的效应。

## 五套 gpr2/gpr3 突变方案放在什么位置

| 工作簿方案 | 现有数据怎样支持 | 综合定位 |
| --- | --- | --- |
| Gpr2 `S80N/F186L`，目标 ASCR3-selective | S80–HBAcceptor 在 3/5 model 中偏向 ASCR3，中位差 0.111；F186–Hydrophobic 在 4/5 model 中偏向 ASCR18，中位差 0.222。两者都低于既有区分候选门槛。F186 与 Gpr3 Y172 有稳定的 MSA 和结构对应关系。 | 合理的“增强极性、削弱芳香接触”探索组合。F186L 的依据强于 S80N；应先测两个单突变，再测双突变。 |
| Gpr3 `Y172W/F147L`，目标 ASCR18-selective | Y172–Hydrophobic 是稳健 ASCR18 候选：5/5 model 偏向 ASCR18，中位差 0.333。F147–VdWContact 只有较弱的 ASCR3 趋势，中位差 0.111。 | 工作簿中数据支持最强的 ASCR18 工程组合，主要证据来自 Y172。Y172W 增加芳香侧链体积的效果仍需实测；F147L 是辅助调节位点。 |
| Gpr2 `F186L/V368A`，目标 ASCR3-selective | F186 提供较弱的 ASCR18 疏水趋势；V368–VdWContact 是稳健 ASCR18 候选，5/5 model 出现、4/5 偏向 ASCR18，中位差 0.222。 | 这是较直接的“削弱 ASCR18 接触”方案。V368 的证据属于 contact-only，实验中要用单突变和表达/定位对照区分选择性变化与总体功能下降。 |
| Gpr3 `Y172W/N88Q`，目标 ASCR18-selective | Y172 提供强 ASCR18 疏水信号；N88–HBDonor 仅有较弱的 ASCR3 趋势，3/5 model 偏向 ASCR3，中位差 0.111。 | Y172 是主要驱动位点；N88Q 属于低优先级的极性几何微调。整体优先级低于 Y172W/F147L。 |
| Gpr2 `V110F` + Gpr3 `F96V`，互换测试 | 两个位点被两套 MSA 放在同一列，结构映射为 25/25，并同样映到 c7xmsA:84。Gpr3 F96–VdWContact 在 5/5 model 中偏向 ASCR18，中位差 0.222；Gpr2 V110 没有稳定配体偏向。 | 最有价值的两受体机制对照。若 V110F 在 Gpr2 中获得 ASCR18 偏向，而 F96V 在 Gpr3 中削弱该偏向，将直接支持“同源位置的芳香性差异参与选择性”的假说。 |

## 两个新的两受体位置假说

### F186/Y172：相同位置，不同证据强度

Gpr2 F186 和 Gpr3 Y172 在 MAFFT、MUSCLE 与 Gpr2–Gpr3 结构映射中一致对应。两者都是芳香残基，也都呈现 ASCR18 方向的疏水趋势，但 Gpr3 Y172 达到稳健区分标准，Gpr2 F186 的 ASCR18 中位 Frequency 只有 0.222，重复强度较弱。

这使 F186/Y172 成为一个“两受体共享的次级芳香位置”候选。适合的实验不是只做两个双突变组合，而是先比较 Gpr2 F186L 与 Gpr3 Y172F、Y172A、Y172W 的单突变效应，再决定是否加入 S80N、F147L 或 V368A。

### V110/F96：同源位置上的化学差异

Gpr2 V110 与 Gpr3 F96 的位置对应证据很强，但两者的化学性质不同。Gpr3 F96 的芳香侧链伴随明显的 ASCR18 contact-only 偏向，Gpr2 V110 则没有同等级信号。因此，这一对更适合研究“同源位置的 Val/Phe 差异是否改变选择性”，而不是作为保守残基处理。

互换实验应被拆成两个平行的单突变：Gpr2 V110F 和 Gpr3 F96V。两种受体都在同一批次测 ASCR3 与 ASCR18，观察选择性是否沿相反方向移动。这比只比较两个野生型受体更接近因果检验。

## 哪些方案最先做

如果首要问题是“跨受体是否共享同一套 ASCR18 识别机制”，优先顺序为：

1. Gpr2 W338F、Gpr3 W306F、GprC W388F，三受体平行双配体测试。
2. Gpr2 V110F 与 Gpr3 F96V，作为同源位置芳香性互换实验。
3. Gpr2 F186L 与 Gpr3 Y172F/Y172A/Y172W，检验第二个两受体芳香位置。

如果首要问题是“能否工程化改变单个受体对两个配体的相对响应”，优先顺序为：

1. Gpr3 Y172W、F147L 及双突变；Y172 是主要位点。
2. Gpr2 F186L、V368A 及双突变；这是削弱 ASCR18 接触的路线。
3. Gpr2 S80N 和 Gpr3 N88Q，作为较低优先级的极性微调位点。

如果首要问题是“ASCR3 是否有自己的区分位点”，GprC N56A 加 N60A 总功能阳性对照仍然是最直接的实验。N56A 需要同时测 ASCR3 与 ASCR18，结果以两种配体响应比的变化来解释。

所有组合建议都应包含 WT、两个单突变和双突变，并在同一表达背景下完成双配体测量。受体表达量或定位检测与一般功能对照可以帮助判断观察到的是选择性改变还是受体整体受损。

## 结果来源

- gpr2/gpr3 突变建议工作簿：`../../../experiments/docking-repro/mutagenesis/final-docking/recommendations/gpr2_gpr3_selectivity_mutation_recommendations.xlsx`，`推荐组合!A1:E6`
- MSA 与结构映射后的完整 ProLIF 矩阵：`../../../experiments/docking-repro/analysis/final-docking/msa-prolif/prolif_ligand_discrimination_matrix_all_msa_annotated.csv`
- 逐残基映射证据：`../../../experiments/docking-repro/analysis/final-docking/msa-prolif/residue_mapping_evidence.csv`
- MSA/ProLIF 生物学报告：`msa_prolif_biological_report_zh.md`
- ProLIF 源工作簿：`../../../experiments/docking-repro/results/final-docking/prolif/af3/merged/prolif_interaction_frequency_profiles.xlsx`
