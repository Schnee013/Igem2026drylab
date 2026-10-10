# ProLIF 配体区分残基只读分析

源工作簿：`../../../../../results/final-docking/prolif/af3/merged/prolif_interaction_frequency_profiles.xlsx`

SHA-256：`64c5652d8b6d46cc9163e095955c7863a1d03fd382afebb1c0c4cc88cf0a05c3`

核心问题：在同一个受体构建体内，哪些 residue–interaction 在 model 0–4 的配对比较中稳定偏向 ASCR3 或 ASCR18；再检查这些区分作用是否跨受体同源保守或功能趋同。不同 Interaction 始终分开，不累加 Frequency、Poses 或 Geometries。

区分筛选：偏好配体一侧至少达到中等重复；在至少 3/5 配对 model 中 Frequency 更高；5 个逐 model Frequency 差值的中位数至少为 0.20。稳健区分还要求偏好配体一侧达到稳健重复且至少 4/5 model 偏高。该标准是描述性候选筛选，不是物理能量或因果阈值。

## 简明结论

1. ASCR3：只发现 1 个跨 model 中等区分候选，即 gprc_wt WT 的 ASN56.A–HBAcceptor；没有稳健候选，也没有跨受体重复，不能称为 ASCR3 的同源保守区分残基。
2. ASCR18：发现 21 个区分候选，其中 10 个是 Hydrophobic，11 个只是 VdWContact/contact-only。最可解释的跨受体规律是芳香残基–Hydrophobic 在 4/5 构建体中重复（缺 daf37_wt），属于功能趋同，不是序列保守。
3. 现有证据支持一种不对称区分模式：ASCR3 只有受体特异的氢键偏向；ASCR18 更常由额外的芳香疏水包围来区分。它描述对接构象中的接触概率差异，不证明 ASCR18 亲和力更高。
4. 未发现满足重复门槛的同一残基 Interaction 类型转换。两配体有 77 个共同重复 residue–interaction；共同使用不等于完全相同，部分共同项仍因 Frequency 稳定偏高而进入区分候选。
5. 未发现可正式称为严格共有（5/5）或近保守（4/5）的同源区分残基。共同模板 c7xmsA 的配对对齐只有 9–19% identity，homologous_position 保持空白。

## A. 数据完整性和排除审计

| 项目 | 结果 | 判定 |
| --- | --- | --- |
| 工作簿模块 | 70 | 目标 70；通过 |
| 有效模块 | 50 | 目标 50；通过 |
| 排除 gpr2/gpr3 WT 模块 | 20 | 目标 20；通过，未进入计算 |
| 有效组合缺失/重复 | 0/0 | 均为 0；通过 |
| 有效 source_csv | 50 | 目标 50；通过 |
| CSV/metadata 错误模块 | 0 | 目标 0；通过 |
| profile/source_csv 不一致 | 0 | 目标 0；通过 |
| Frequency 范围 | 0.111–1.000 | 均为 poses/n_poses；通过 |
| pose 数分布 | 49×9 poses；1×8 poses | 未假设固定 9 poses |

## B. ASCR3：各受体的跨 model 配体区分候选

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | tier | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR3 | gprc_wt | WT | ASN56.A | — | HBAcceptor | directional_or_charge_related | 5/5 | 1.000 | 0.333 | 0.333 | 0.333-0.444 | m0,m1,m2,m3,m4 | moderate_discriminator | receptor_internal_discriminator_only | Within gprc_wt WT, ASCR3 is favored in 3/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |

daf37_wt、gpr2_twf154_wt deltaN、gpr3_twf154_wt deltaN、srbc64_wt 均未发现达到区分标准的 ASCR3 偏好 residue–interaction。gpr2 的 ARG181/ARG345/LYS364–Anionic 以及 srbc64 的 SER232–HBAcceptor 虽对 ASCR3 达到中等重复，但配对差值中位数只有 0.111，未作为区分候选。

## C. ASCR18：各受体的跨 model 配体区分候选

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | tier | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR18 | gpr2_twf154_wt | deltaN | VAL368.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.667 | 0.667 | 0.444-0.667 | m0,m1,m2,m3,m4 | robust_discriminator | limited_cross_receptor_recurrence_3of5_contact-only | Within gpr2_twf154_wt deltaN, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr2_twf154_wt | deltaN | TRP338.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.444 | 0.444 | 0.222-0.444 | m0,m1,m2,m3,m4 | moderate_discriminator | functional_convergence_discriminator_candidate_4of5_not_sequence_conservation;provisional_common_template_position_3of5_not_homology_claim | Within gpr2_twf154_wt deltaN, ASCR18 is favored in 5/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | MET92.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.556 | 0.556 | 0.333-0.667 | m0,m1,m2,m3,m4 | robust_discriminator | limited_cross_receptor_recurrence_3of5_contact-only | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.333. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | PHE96.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.889 | 0.889 | 0.556-1.000 | m0,m1,m2,m3,m4 | robust_discriminator | limited_cross_receptor_recurrence_2of5_contact-only;provisional_common_template_position_2of5_not_homology_claim | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 5/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | TYR172.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.667 | 0.667 | 0.333-0.778 | m0,m1,m2,m3,m4 | robust_discriminator | functional_convergence_discriminator_candidate_4of5_not_sequence_conservation | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 5/5 paired models; median paired Frequency delta=0.333. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | TYR172.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.556 | 0.556 | 0.444-0.889 | m0,m1,m2,m3,m4 | moderate_discriminator | limited_cross_receptor_recurrence_2of5_contact-only;provisional_common_template_position_2of5_not_homology_claim | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 3/5 paired models; median paired Frequency delta=0.333. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | ASN171.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.444 | 0.444 | 0.111-0.778 | m0,m1,m2,m3,m4 | moderate_discriminator | receptor_internal_discriminator_only | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 3/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | LEU336.A | — | Hydrophobic | hydrophobic | 4/5 | 0.800 | 0.444 | 0.500 | 0.000-0.778 | m0,m1,m2,m4 | moderate_discriminator | receptor_internal_discriminator_only | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | MET92.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.444 | 0.444 | 0.444-0.667 | m0,m1,m2,m3,m4 | moderate_discriminator | receptor_internal_discriminator_only | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 5/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gpr3_twf154_wt | deltaN | TRP306.A | — | Hydrophobic | hydrophobic | 4/5 | 0.800 | 0.333 | 0.333 | 0.000-0.444 | m1,m2,m3,m4 | moderate_discriminator | functional_convergence_discriminator_candidate_4of5_not_sequence_conservation;provisional_common_template_position_3of5_not_homology_claim | Within gpr3_twf154_wt deltaN, ASCR18 is favored in 3/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | ARG174.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.667 | 0.667 | 0.222-0.889 | m0,m1,m2,m3,m4 | robust_discriminator | receptor_internal_discriminator_only | Within gprc_wt WT, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.333. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | TRP388.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.889 | 0.889 | 0.333-0.889 | m0,m1,m2,m3,m4 | robust_discriminator | limited_cross_receptor_recurrence_2of5_contact-only | Within gprc_wt WT, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.333. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | GLN411.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.778 | 0.778 | 0.667-1.000 | m0,m1,m2,m3,m4 | robust_discriminator | receptor_internal_discriminator_only | Within gprc_wt WT, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | SER152.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.778 | 0.778 | 0.667-1.000 | m0,m1,m2,m3,m4 | robust_discriminator | receptor_internal_discriminator_only | Within gprc_wt WT, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | TRP155.A | — | VdWContact | contact-only | 5/5 | 1.000 | 1.000 | 1.000 | 0.556-1.000 | m0,m1,m2,m3,m4 | robust_discriminator | limited_cross_receptor_recurrence_2of5_contact-only | Within gprc_wt WT, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | VAL91.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.889 | 0.889 | 0.333-1.000 | m0,m1,m2,m3,m4 | robust_discriminator | limited_cross_receptor_recurrence_3of5_contact-only;provisional_common_template_position_2of5_not_homology_claim | Within gprc_wt WT, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | HIS171.A | — | VdWContact | contact-only | 5/5 | 1.000 | 0.444 | 0.444 | 0.111-0.667 | m0,m1,m2,m3,m4 | moderate_discriminator | provisional_common_template_position_2of5_not_homology_claim | Within gprc_wt WT, ASCR18 is favored in 3/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | TRP388.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.667 | 0.667 | 0.333-0.778 | m0,m1,m2,m3,m4 | moderate_discriminator | functional_convergence_discriminator_candidate_4of5_not_sequence_conservation;provisional_common_template_position_3of5_not_homology_claim | Within gprc_wt WT, ASCR18 is favored in 3/5 paired models; median paired Frequency delta=0.333. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | TRP155.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.889 | 0.889 | 0.556-1.000 | m0,m1,m2,m3,m4 | moderate_discriminator | functional_convergence_discriminator_candidate_4of5_not_sequence_conservation | Within gprc_wt WT, ASCR18 is favored in 3/5 paired models; median paired Frequency delta=0.333. Screen is descriptive, not energetic or causal. |
| ASCR18 | gprc_wt | WT | TRP157.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.667 | 0.667 | 0.333-1.000 | m0,m1,m2,m3,m4 | moderate_discriminator | functional_convergence_discriminator_candidate_4of5_not_sequence_conservation | Within gprc_wt WT, ASCR18 is favored in 3/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |
| ASCR18 | srbc64_wt | WT | PHE161.A | — | Hydrophobic | hydrophobic | 5/5 | 1.000 | 0.889 | 0.889 | 0.667-1.000 | m0,m1,m2,m3,m4 | robust_discriminator | functional_convergence_discriminator_candidate_4of5_not_sequence_conservation | Within srbc64_wt WT, ASCR18 is favored in 4/5 paired models; median paired Frequency delta=0.222. Screen is descriptive, not energetic or causal. |

证据构成：Hydrophobic 10 项；contact-only 11 项。contact-only 仅说明非特异接触频率差异，不能解释为结合能。daf37_wt 未发现 ASCR18 区分候选。

## D. ASCR3 跨受体保守或功能趋同候选

未发现。唯一 ASCR3 区分候选只出现在 gprc_wt；没有 4/5 或 5/5 跨受体重复，也没有足够的同源映射支持。

## E. ASCR18 跨受体保守或功能趋同候选

严格同源共有：未发现。近同源保守：未发现。

功能趋同候选：芳香残基–Hydrophobic 在 gpr2_twf154_wt deltaN、gpr3_twf154_wt deltaN、gprc_wt WT、srbc64_wt WT 中达到区分门槛，缺失 daf37_wt。涉及 TRP338；TYR172/TRP306；TRP388/TRP155/TRP157；PHE161。这是相同化学类别与相同作用类型的 4/5 重复，不能称为序列保守。

共同模板线索：TRP338（gpr2）、TRP306（gpr3）和 TRP388（gprc）的 ASCR18–Hydrophobic 都落在暂定 c7xmsA:226，但只有 3/5，且映射可靠性不足；仅适合作为后续验证假说。

## F. ASCR3 与 ASCR18 的共享及差异候选

两配体共有 77 个至少中等重复的同一受体、同一残基、同一 Interaction 项：directional/charge 1，Hydrophobic 16，contact-only 60。这些主要是共同锚定/口袋接触证据；只有在逐 model 配对 Frequency 持续偏高时才进入本次区分表。

ASCR3 偏向：gprc ASN56.A–HBAcceptor（中等）。

ASCR18 偏向：核心功能信号是 4/5 受体的芳香–Hydrophobic 功能趋同；其余多为受体特异或 contact-only。

Interaction 类型变化：未发现满足两侧至少中等重复且作用类型彼此不共享的稳定 switch。

## G. 同源映射限制和下一步所需材料

现有材料只有五个受体分别对共同模板 c7xmsA 的 Phyre2/HHsearch 配对对齐，identity 为 9–19%，没有直接五受体 MSA、逐残基结构对应关系或逐位点置信度。因此 homologous_position 留空，不能正式宣称严格/近同源保守残基。

要完成严格判断，需要：五受体（明确 WT 与 deltaN 编号换算）的可靠 MSA；或五个受体 model 的逐残基结构映射；最好同时给出跨 model/跨受体映射一致性与位点置信度。优先验证暂定 c7xmsA:226 以及 4/5 芳香疏水区分网络。

## 追溯文件

- `prolif_ligand_discrimination_matrix_all.csv`：451 行未经区分阈值截断的同受体、同 residue–interaction 配对矩阵。
- `prolif_ligand_discrimination_candidates.csv`：22 个候选，含逐 model ASCR3/ASCR18 Frequency、差值、source_csv 和源行号。
- `prolif_ligand_discrimination_cross_receptor.csv`：功能趋同与共同模板位置线索。
- `prolif_ligand_discrimination_module_audit.csv`：50 个有效模块的 source_csv、pose 数及错误审计。
