# ProLIF 同一配体跨受体只读分析

源工作簿：`../../../../../results/final-docking/prolif/af3/merged/prolif_interaction_frequency_profiles.xlsx`

SHA-256：`64c5652d8b6d46cc9163e095955c7863a1d03fd382afebb1c0c4cc88cf0a05c3`

分析口径：只纳入 daf37_wt WT、gpr2_twf154_wt deltaN、gpr3_twf154_wt deltaN、gprc_wt WT、srbc64_wt WT；每个构建体 model 0–4；ASCR3/ASCR18 分开。

## 简明结论

1. 70→50→20 审计完全闭合。50 个有效模块无缺失、重复、字段错误或 profile/CSV 不一致；20 个 gpr2/gpr3 WT 模块仅用于确认排除，未进入任何计算。
2. 未发现可以正式称为“严格同源保守”或“近保守”的残基。现有五份共同模板对齐只有 9–19% 序列一致性，缺少直接五受体 MSA、逐残基结构映射和逐位点置信度。
3. 两种配体最一致的跨受体信号是疏水环境的功能趋同：脂肪族 Hydrophobic 在 5/5 受体出现；芳香族 Hydrophobic 在 4/5 出现，缺失受体均为 daf37_wt。VdWContact 也广泛重复，但全部按 contact-only 处理，不能解释为结合能。
4. 方向性/电荷相关作用更受体特异：ASCR3 的重复候选集中在 gpr2 的 ARG181/ARG345/LYS364 Anionic、gprc ASN56 HBAcceptor、srbc64 SER232/LYS254 HBAcceptor；ASCR18 集中在 gpr3 SER67、gprc ARG395、srbc64 TYR181/LYS254 的 HBAcceptor。没有任何方向性/电荷相关类别达到 4/5 功能趋同。
5. ASCR3 与 ASCR18 有 77 个同一受体、同一残基、同一作用类型的共同重复项，其中 60 个是 contact-only、16 个 Hydrophobic、1 个方向性候选（srbc64 LYS254.A–HBAcceptor）。发现 7 个配体偏好候选；未发现满足重复性门槛的 interaction-type switch。

## A. 数据完整性和排除审计

| 审计项 | 结果 | 判定 |
| --- | --- | --- |
| 工作簿 profile 模块 | 70 | 通过 |
| Sources 模块 | 70 | 通过 |
| 有效模块 | 50 | 目标=50；通过 |
| 排除模块 | 20 | 目标=20；通过 |
| 意外模块 | 0 | 目标=0；通过 |
| 有效组合缺失/重复 | 0/0 | 通过 |
| 有效源CSV唯一数 | 50 | 目标=50；通过 |
| CSV/metadata审计错误模块 | 0 | 目标=0；通过 |
| profile 与 source CSV 不一致 | 0 | 目标=0；通过 |
| 有效源记录数 | 2255 | 全部用于未截断支持矩阵 |
| Frequency 范围 | 0.111–1.000 | 均在0–1；逐行等于 Poses/n_poses |
| 实际 n_poses 分布 | 8 poses: 1；9 poses: 49 | 逐模块读取，不固定假设9 |

唯一的 8-pose 模块是 `ASCR18 | daf37_wt | WT | model 2`；其 source CSV 与 metadata 均通过逐行核对。

未截断支持矩阵包含 791 个至少在一个有效 model 中出现过的 residue–interaction 键；每个键均补齐 m0–m4，缺失 model 的 Frequency=0。

## B. ASCR3 各受体跨 model 稳定残基表


### daf37_wt (WT) — robust 2；moderate 10

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR3 | daf37_wt | WT | GLN122.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | ARG329.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | MET1.A | — | VdWContact | contact-only | moderate | 3 | 0.600 | 0.667 | 0.778 | 0.000-1.000 | m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | ASP2.A | — | VdWContact | contact-only | moderate | 3 | 0.600 | 0.444 | 0.556 | 0.000-0.556 | m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | TYR89.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.333 | 0.389 | 0.000-0.444 | m0,m1,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | MET220.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.333 | 0.389 | 0.000-0.889 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | VAL221.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.444 | 0.667 | 0.000-0.889 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | ASN299.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.444 | 0.667 | 0.000-0.889 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | GLY302.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.444 | 0.667 | 0.000-1.000 | m0,m1,m2,m3 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | THR306.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | ILE332.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | daf37_wt | WT | MET1.A | — | Hydrophobic | hydrophobic | moderate | 3 | 0.600 | 0.556 | 0.556 | 0.000-0.889 | m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |

### gpr2_twf154_wt (deltaN) — robust 9；moderate 10

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR3 | gpr2_twf154_wt | deltaN | ASN28.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | LEU31.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.667-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | PHE77.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | SER80.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.778-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | LYS364.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 1.000-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | ILE367.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | PHE77.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 1.000 | 1.000 | 1.000-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | LYS364.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.778 | 0.778 | 0.778-1.000 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | ILE367.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.889 | 0.889 | 0.667-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | ALA81.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | ASN84.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.444 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | LEU90.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | THR106.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | VAL110.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | ARG181.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | VAL368.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | ARG181.A | — | Anionic | directional_or_charge_related | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.333-0.333 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | ARG345.A | — | Anionic | directional_or_charge_related | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.333-0.333 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr2_twf154_wt | deltaN | LYS364.A | — | Anionic | directional_or_charge_related | moderate | 4 | 0.800 | 0.333 | 0.333 | 0.000-0.333 | m0,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |

### gpr3_twf154_wt (deltaN) — robust 6；moderate 14

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR3 | gpr3_twf154_wt | deltaN | VAL17.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.333-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | PHE63.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.444-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | ARG167.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | LYS333.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.444-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | LEU336.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.333-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | PHE96.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.778 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | PRO66.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.444 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | SER67.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | PHE90.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.333 | 0.333 | 0.000-0.333 | m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | MET92.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.444 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | GLN93.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | PHE96.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | ALA146.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.333 | 0.389 | 0.000-0.556 | m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | PHE147.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.333 | 0.389 | 0.000-0.444 | m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | ASN171.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | TYR172.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | VAL17.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | PHE63.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.889 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | ARG167.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.667 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gpr3_twf154_wt | deltaN | LYS333.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |

### gprc_wt (WT) — robust 9；moderate 12

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR3 | gprc_wt | WT | VAL91.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.556-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | SER152.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | TRP155.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.778 | 0.778 | 0.556-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | TRP157.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.778 | 0.778 | 0.556-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | ARG174.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | ARG395.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.778 | 0.778 | 0.444-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | GLN411.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | GLN415.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | TRP155.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.556 | 0.556 | 0.333-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | ASN56.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.444-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | ASN60.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.444-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | VAL151.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | HIS171.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.444 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | TRP388.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.444-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | GLN408.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.444 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | THR414.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | VAL417.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.333 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | ASN56.A | — | HBAcceptor | directional_or_charge_related | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.333-0.444 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | VAL91.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.333-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | TRP157.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.778 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | gprc_wt | WT | TRP388.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |

### srbc64_wt (WT) — robust 10；moderate 9

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR3 | srbc64_wt | WT | PHE161.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.667-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | TRP173.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | TYR181.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | SER232.A | — | VdWContact | contact-only | robust | 4 | 0.800 | 0.556 | 0.611 | 0.000-0.778 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | THR250.A | — | VdWContact | contact-only | robust | 4 | 0.800 | 0.778 | 0.778 | 0.000-0.889 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | ILE251.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.667-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | LYS254.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.667-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | PHE161.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.556 | 0.556 | 0.556-0.778 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | TRP173.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.889 | 0.889 | 0.778-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | ILE251.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.778 | 0.778 | 0.222-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | TYR56.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | VAL60.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | LYS64.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.444 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | THR89.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | TYR170.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.444 | 0.500 | 0.000-0.556 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | PHE243.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | PRO248.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.333 | 0.333 | 0.000-0.333 | m0,m1,m2,m3 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | SER232.A | — | HBAcceptor | directional_or_charge_related | moderate | 4 | 0.800 | 0.444 | 0.444 | 0.000-0.444 | m0,m1,m2,m3 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR3 | srbc64_wt | WT | LYS254.A | — | HBAcceptor | directional_or_charge_related | moderate | 4 | 0.800 | 0.333 | 0.333 | 0.000-0.444 | m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |

## C. ASCR18 各受体跨 model 稳定残基表


### daf37_wt (WT) — robust 3；moderate 10

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR18 | daf37_wt | WT | ASN217.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.500 | 0.500 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | GLU309.A | — | VdWContact | contact-only | robust | 4 | 0.800 | 0.556 | 0.590 | 0.000-0.889 | m0,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | ARG329.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | MET1.A | — | VdWContact | contact-only | moderate | 3 | 0.600 | 0.778 | 1.000 | 0.000-1.000 | m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | ASP2.A | — | VdWContact | contact-only | moderate | 3 | 0.600 | 0.444 | 0.750 | 0.000-0.889 | m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | TYR89.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.125-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | VAL221.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | ASN299.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.750 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | GLY302.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.875 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | THR306.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | ILE332.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | ASN333.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | daf37_wt | WT | MET1.A | — | Hydrophobic | hydrophobic | moderate | 3 | 0.600 | 0.778 | 0.778 | 0.000-1.000 | m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |

### gpr2_twf154_wt (deltaN) — robust 12；moderate 4

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR18 | gpr2_twf154_wt | deltaN | ASN28.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | LEU31.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.667-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | PHE77.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 0.778-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | SER80.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.667-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | ALA81.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | THR106.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | LYS364.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | ILE367.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 1.000-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | VAL368.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.444-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | PHE77.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 1.000 | 1.000 | 1.000-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | LYS364.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 1.000 | 1.000 | 0.889-1.000 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | ILE367.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.889 | 0.889 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | ASN84.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | VAL110.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | ARG181.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr2_twf154_wt | deltaN | TRP338.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.444 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |

### gpr3_twf154_wt (deltaN) — robust 14；moderate 9

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR18 | gpr3_twf154_wt | deltaN | VAL17.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.556-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | PHE63.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.556-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | SER67.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | MET92.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | GLN93.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | PHE96.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.556-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | ARG167.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.444-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | TYR172.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | LYS333.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.556-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | LEU336.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.444-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | PHE63.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.667 | 0.667 | 0.556-0.778 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | PHE96.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.778 | 0.778 | 0.333-0.889 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | ARG167.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.556 | 0.556 | 0.444-0.778 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | TYR172.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.667 | 0.667 | 0.333-0.778 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | PRO66.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.667 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | ASN171.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | SER67.A | — | HBAcceptor | directional_or_charge_related | moderate | 4 | 0.800 | 0.444 | 0.444 | 0.000-0.667 | m0,m1,m2,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | VAL17.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.333 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | MET92.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.444-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | ASN171.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.778 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | TRP306.A | — | Hydrophobic | hydrophobic | moderate | 4 | 0.800 | 0.333 | 0.333 | 0.000-0.444 | m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | LYS333.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gpr3_twf154_wt | deltaN | LEU336.A | — | Hydrophobic | hydrophobic | moderate | 4 | 0.800 | 0.444 | 0.500 | 0.000-0.778 | m0,m1,m2,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |

### gprc_wt (WT) — robust 15；moderate 6

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR18 | gprc_wt | WT | ASN56.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.111-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | ASN60.A | — | VdWContact | contact-only | robust | 4 | 0.800 | 0.556 | 0.722 | 0.000-0.889 | m0,m1,m2,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | VAL91.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.333-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | VAL151.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.444-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | SER152.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.778 | 0.778 | 0.667-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | TRP155.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 0.556-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | TRP157.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.333-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | ARG174.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.667 | 0.667 | 0.222-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | TRP388.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.333-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | ARG395.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 1.000 | 1.000 | 0.778-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | GLN411.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.778 | 0.778 | 0.667-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | GLN415.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.333-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | TRP155.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.889 | 0.889 | 0.556-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | TRP157.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.667 | 0.667 | 0.333-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | TRP388.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.667 | 0.667 | 0.333-0.778 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | GLY153.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.444 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | HIS171.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.667 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | GLN408.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | THR414.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.556 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | ARG395.A | — | HBAcceptor | directional_or_charge_related | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.333 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | gprc_wt | WT | VAL91.A | — | Hydrophobic | hydrophobic | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.222-0.778 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |

### srbc64_wt (WT) — robust 11；moderate 7

| ligand | receptor | construct | residue | homologous_position | interaction | interaction_evidence_class | tier | model_support_n | model_support_fraction | median_frequency_all_models | median_frequency_when_present | frequency_range | involved_models | conservation_status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR18 | srbc64_wt | WT | TYR56.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | PHE161.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.444-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | TRP173.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | TYR181.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.556 | 0.556 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | SER232.A | — | VdWContact | contact-only | robust | 4 | 0.800 | 0.556 | 0.556 | 0.000-0.667 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | THR250.A | — | VdWContact | contact-only | robust | 4 | 0.800 | 0.778 | 0.833 | 0.000-0.889 | m0,m1,m2,m3 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | ILE251.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.889 | 0.889 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | LYS254.A | — | VdWContact | contact-only | robust | 5 | 1.000 | 0.778 | 0.778 | 0.333-0.889 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | PHE161.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.889 | 0.889 | 0.667-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | TRP173.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 1.000 | 1.000 | 0.889-1.000 | m0,m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | ILE251.A | — | Hydrophobic | hydrophobic | robust | 5 | 1.000 | 0.889 | 0.889 | 0.778-1.000 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | THR89.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.333-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | TYR170.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.444 | 0.444 | 0.111-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | PHE243.A | — | VdWContact | contact-only | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.222-0.667 | m0,m1,m2,m3,m4 | functional_convergence_5of5 | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | PRO248.A | — | VdWContact | contact-only | moderate | 4 | 0.800 | 0.333 | 0.333 | 0.000-0.444 | m0,m1,m2,m3 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | TYR181.A | — | HBAcceptor | directional_or_charge_related | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.444 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | LYS254.A | — | HBAcceptor | directional_or_charge_related | moderate | 5 | 1.000 | 0.333 | 0.333 | 0.111-0.444 | m0,m1,m2,m3,m4 | receptor_internal_only | 5-model recurrence; exact source trace in candidate CSV. |
| ASCR18 | srbc64_wt | WT | TYR170.A | — | Hydrophobic | hydrophobic | moderate | 4 | 0.800 | 0.333 | 0.389 | 0.000-0.667 | m1,m2,m3,m4 | functional_convergence_4of5 | 5-model recurrence; exact source trace in candidate CSV. |

## D. ASCR3 跨受体保守或功能趋同候选

严格共有：未发现可声明候选。近保守：未发现可声明候选。原因见 G。

功能趋同候选：

| chemical_class | interaction | evidence_class | receptor_support | missing | residues_by_receptor | status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| polar_uncharged | VdWContact | contact-only | 5/5 | — | daf37_wt: GLN122.A, ASN299.A, THR306.A; gpr2_twf154_wt: ASN28.A, SER80.A, ASN84.A, THR106.A; gpr3_twf154_wt: SER67.A, GLN93.A, ASN171.A; gprc_wt: SER152.A, GLN411.A, GLN415.A, ASN56.A, ASN60.A, GLN408.A, THR414.A; srbc64_wt: SER232.A, THR250.A, THR89.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| basic_or_cationic | VdWContact | contact-only | 5/5 | — | daf37_wt: ARG329.A; gpr2_twf154_wt: LYS364.A, ARG181.A; gpr3_twf154_wt: ARG167.A, LYS333.A; gprc_wt: ARG174.A, ARG395.A; srbc64_wt: LYS254.A, LYS64.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aliphatic_hydrophobic | VdWContact | contact-only | 5/5 | — | daf37_wt: MET1.A, MET220.A, VAL221.A, ILE332.A; gpr2_twf154_wt: LEU31.A, ILE367.A, ALA81.A, LEU90.A, VAL110.A, VAL368.A; gpr3_twf154_wt: VAL17.A, LEU336.A, MET92.A, ALA146.A; gprc_wt: VAL91.A, VAL151.A, VAL417.A; srbc64_wt: ILE251.A, VAL60.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aromatic | VdWContact | contact-only | 5/5 | — | daf37_wt: TYR89.A; gpr2_twf154_wt: PHE77.A; gpr3_twf154_wt: PHE63.A, PHE90.A, PHE96.A, PHE147.A, TYR172.A; gprc_wt: TRP155.A, TRP157.A, TRP388.A; srbc64_wt: PHE161.A, TRP173.A, TYR181.A, TYR56.A, TYR170.A, PHE243.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aliphatic_hydrophobic | Hydrophobic | hydrophobic | 5/5 | — | daf37_wt: MET1.A; gpr2_twf154_wt: ILE367.A; gpr3_twf154_wt: VAL17.A; gprc_wt: VAL91.A; srbc64_wt: ILE251.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aromatic | Hydrophobic | hydrophobic | 4/5 | daf37_wt | gpr2_twf154_wt: PHE77.A; gpr3_twf154_wt: PHE96.A, PHE63.A; gprc_wt: TRP155.A, TRP157.A, TRP388.A; srbc64_wt: PHE161.A, TRP173.A | functional_convergence_4of5 | Functional convergence; not sequence conservation. |

## E. ASCR18 跨受体保守或功能趋同候选

严格共有：未发现可声明候选。近保守：未发现可声明候选。原因见 G。

功能趋同候选：

| chemical_class | interaction | evidence_class | receptor_support | missing | residues_by_receptor | status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| polar_uncharged | VdWContact | contact-only | 5/5 | — | daf37_wt: ASN217.A, ASN299.A, THR306.A, ASN333.A; gpr2_twf154_wt: ASN28.A, SER80.A, THR106.A, ASN84.A; gpr3_twf154_wt: SER67.A, GLN93.A, ASN171.A; gprc_wt: ASN56.A, ASN60.A, SER152.A, GLN411.A, GLN415.A, GLN408.A, THR414.A; srbc64_wt: SER232.A, THR250.A, THR89.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| basic_or_cationic | VdWContact | contact-only | 5/5 | — | daf37_wt: ARG329.A; gpr2_twf154_wt: LYS364.A, ARG181.A; gpr3_twf154_wt: ARG167.A, LYS333.A; gprc_wt: ARG174.A, ARG395.A; srbc64_wt: LYS254.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aliphatic_hydrophobic | VdWContact | contact-only | 5/5 | — | daf37_wt: MET1.A, VAL221.A, ILE332.A; gpr2_twf154_wt: LEU31.A, ALA81.A, ILE367.A, VAL368.A, VAL110.A; gpr3_twf154_wt: VAL17.A, MET92.A, LEU336.A; gprc_wt: VAL91.A, VAL151.A; srbc64_wt: ILE251.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aromatic | VdWContact | contact-only | 5/5 | — | daf37_wt: TYR89.A; gpr2_twf154_wt: PHE77.A; gpr3_twf154_wt: PHE63.A, PHE96.A, TYR172.A; gprc_wt: TRP155.A, TRP157.A, TRP388.A; srbc64_wt: TYR56.A, PHE161.A, TRP173.A, TYR181.A, TYR170.A, PHE243.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aliphatic_hydrophobic | Hydrophobic | hydrophobic | 5/5 | — | daf37_wt: MET1.A; gpr2_twf154_wt: ILE367.A; gpr3_twf154_wt: VAL17.A, MET92.A, LEU336.A; gprc_wt: VAL91.A; srbc64_wt: ILE251.A | functional_convergence_5of5 | Functional convergence; not sequence conservation. |
| aromatic | Hydrophobic | hydrophobic | 4/5 | daf37_wt | gpr2_twf154_wt: PHE77.A, TRP338.A; gpr3_twf154_wt: PHE63.A, PHE96.A, TYR172.A, TRP306.A; gprc_wt: TRP155.A, TRP157.A, TRP388.A; srbc64_wt: PHE161.A, TRP173.A, TYR170.A | functional_convergence_4of5 | Functional convergence; not sequence conservation. |

### 共同模板位置线索（仅线索，不是保守性结论）

| ligand | provisional_template_position | interaction | evidence_class | support | receptor_residues | status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR3 | c7xmsA:84 | VdWContact | contact-only | 4/5 | daf37_wt: GLN122.A (robust, n=5, med=0.556); gpr2_twf154_wt: VAL110.A (moderate, n=5, med=0.444); gpr3_twf154_wt: PHE96.A (moderate, n=5, med=0.444); gprc_wt: VAL91.A (robust, n=5, med=0.667) | template_anchored_provisional_4of5 | homologous_position remains blank; mapping is provisional. |
| ASCR3 | c7xmsA:54 | VdWContact | contact-only | 4/5 | gpr2_twf154_wt: PHE77.A (robust, n=5, med=1.000); gpr3_twf154_wt: PHE63.A (robust, n=5, med=0.667); gprc_wt: ASN60.A (moderate, n=5, med=0.444); srbc64_wt: VAL60.A (moderate, n=5, med=0.333) | template_anchored_provisional_4of5 | homologous_position remains blank; mapping is provisional. |
| ASCR3 | c7xmsA:251 | VdWContact | contact-only | 4/5 | gpr2_twf154_wt: LYS364.A (robust, n=5, med=1.000); gpr3_twf154_wt: LYS333.A (robust, n=5, med=0.667); gprc_wt: GLN411.A (robust, n=5, med=0.556); srbc64_wt: ILE251.A (robust, n=5, med=0.889) | template_anchored_provisional_4of5 | homologous_position remains blank; mapping is provisional. |
| ASCR3 | c7xmsA:254 | VdWContact | contact-only | 4/5 | gpr2_twf154_wt: ILE367.A (robust, n=5, med=1.000); gpr3_twf154_wt: LEU336.A (robust, n=5, med=0.556); gprc_wt: THR414.A (moderate, n=5, med=0.444); srbc64_wt: LYS254.A (robust, n=5, med=0.667) | template_anchored_provisional_4of5 | homologous_position remains blank; mapping is provisional. |
| ASCR18 | c7xmsA:251 | VdWContact | contact-only | 5/5 | daf37_wt: ASN333.A (moderate, n=5, med=0.333); gpr2_twf154_wt: LYS364.A (robust, n=5, med=1.000); gpr3_twf154_wt: LYS333.A (robust, n=5, med=0.556); gprc_wt: GLN411.A (robust, n=5, med=0.778); srbc64_wt: ILE251.A (robust, n=5, med=0.889) | template_anchored_provisional_5of5 | homologous_position remains blank; mapping is provisional. |
| ASCR18 | c7xmsA:254 | VdWContact | contact-only | 4/5 | gpr2_twf154_wt: ILE367.A (robust, n=5, med=1.000); gpr3_twf154_wt: LEU336.A (robust, n=5, med=0.667); gprc_wt: THR414.A (moderate, n=5, med=0.444); srbc64_wt: LYS254.A (robust, n=5, med=0.778) | template_anchored_provisional_4of5 | homologous_position remains blank; mapping is provisional. |

## F. ASCR3 与 ASCR18 共享及差异候选

共同重复项共 77 个：contact-only 60，Hydrophobic 16，方向性/电荷相关 1。下表列出全部非 contact-only 共享项；60 个 contact-only 共享项保留在 ligand comparison CSV。

| receptor | construct | residue | interaction | evidence_class | ASCR3 | ASCR18 | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| daf37_wt | WT | MET1.A | Hydrophobic | hydrophobic | moderate; n=3; med=0.556 | moderate; n=3; med=0.778 | shared exact residue-interaction |
| gpr2_twf154_wt | deltaN | PHE77.A | Hydrophobic | hydrophobic | robust; n=5; med=1.000 | robust; n=5; med=1.000 | shared exact residue-interaction |
| gpr2_twf154_wt | deltaN | LYS364.A | Hydrophobic | hydrophobic | robust; n=5; med=0.778 | robust; n=5; med=1.000 | shared exact residue-interaction |
| gpr2_twf154_wt | deltaN | ILE367.A | Hydrophobic | hydrophobic | robust; n=5; med=0.889 | robust; n=5; med=0.889 | shared exact residue-interaction |
| gpr3_twf154_wt | deltaN | VAL17.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.333 | moderate; n=5; med=0.333 | shared exact residue-interaction |
| gpr3_twf154_wt | deltaN | PHE63.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.444 | robust; n=5; med=0.667 | shared exact residue-interaction |
| gpr3_twf154_wt | deltaN | PHE96.A | Hydrophobic | hydrophobic | robust; n=5; med=0.556 | robust; n=5; med=0.778 | shared exact residue-interaction |
| gpr3_twf154_wt | deltaN | ARG167.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.444 | robust; n=5; med=0.556 | shared exact residue-interaction |
| gpr3_twf154_wt | deltaN | LYS333.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.444 | moderate; n=5; med=0.444 | shared exact residue-interaction |
| gprc_wt | WT | VAL91.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.333 | moderate; n=5; med=0.444 | shared exact residue-interaction |
| gprc_wt | WT | TRP155.A | Hydrophobic | hydrophobic | robust; n=5; med=0.556 | robust; n=5; med=0.889 | shared exact residue-interaction |
| gprc_wt | WT | TRP157.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.444 | robust; n=5; med=0.667 | shared exact residue-interaction |
| gprc_wt | WT | TRP388.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.444 | robust; n=5; med=0.667 | shared exact residue-interaction |
| srbc64_wt | WT | PHE161.A | Hydrophobic | hydrophobic | robust; n=5; med=0.556 | robust; n=5; med=0.889 | shared exact residue-interaction |
| srbc64_wt | WT | TRP173.A | Hydrophobic | hydrophobic | robust; n=5; med=0.889 | robust; n=5; med=1.000 | shared exact residue-interaction |
| srbc64_wt | WT | ILE251.A | Hydrophobic | hydrophobic | robust; n=5; med=0.778 | robust; n=5; med=0.889 | shared exact residue-interaction |
| srbc64_wt | WT | LYS254.A | HBAcceptor | directional_or_charge_related | moderate; n=4; med=0.333 | moderate; n=5; med=0.333 | shared exact residue-interaction |

### 配体偏好候选

操作性判据：偏好配体至少 medium-repeat；另一配体 scattered；support gap ≥1；median_frequency_all_models gap ≥0.20。

| favored_ligand | receptor | construct | residue | interaction | evidence_class | favored | other | support_gap | median_gap | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASCR18 | gpr2_twf154_wt | deltaN | TRP338.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.444 | scattered; n=3; med=0.111 | 2 | 0.333 | ASCR18_preference_candidate |
| ASCR18 | gpr3_twf154_wt | deltaN | ASN171.A | Hydrophobic | hydrophobic | moderate; n=5; med=0.444 | scattered; n=4; med=0.222 | 1 | 0.222 | ASCR18_preference_candidate |
| ASCR18 | gpr3_twf154_wt | deltaN | TRP306.A | Hydrophobic | hydrophobic | moderate; n=4; med=0.333 | scattered; n=2; med=0.000 | 2 | 0.333 | ASCR18_preference_candidate |
| ASCR18 | gprc_wt | WT | GLY153.A | VdWContact | contact-only | moderate; n=5; med=0.333 | scattered; n=3; med=0.111 | 2 | 0.222 | ASCR18_preference_candidate |
| ASCR3 | gprc_wt | WT | VAL417.A | VdWContact | contact-only | moderate; n=5; med=0.333 | scattered; n=3; med=0.111 | 2 | 0.222 | ASCR3_preference_candidate |
| ASCR3 | srbc64_wt | WT | VAL60.A | VdWContact | contact-only | moderate; n=5; med=0.333 | scattered; n=4; med=0.111 | 1 | 0.222 | ASCR3_preference_candidate |
| ASCR3 | srbc64_wt | WT | LYS64.A | VdWContact | contact-only | moderate; n=5; med=0.333 | scattered; n=4; med=0.111 | 1 | 0.222 | ASCR3_preference_candidate |

Interaction 类型变化候选：未发现。没有降低门槛，也没有把不同 Interaction 合并来制造 switch。

## G. 同源映射限制和下一步所需材料

| receptor | common_template | HHsearch_probability | identity_percent | aligned_cols | existing_alignment | use |
| --- | --- | --- | --- | --- | --- | --- |
| daf37_wt | c7xmsA | 99.970 | 19.000 | 274 | ../../../../../receptors/final-docking/source-archives/phyre2-complete-jobs/DAF-37/aligs/c7xmsA_.89.alig.txt | provisional only |
| gpr2_twf154_wt | c7xmsA | 99.950 | 15.000 | 264 | ../../../../../receptors/final-docking/source-archives/phyre2-complete-jobs/Gpr2/aligs/c7xmsA_.146.alig.txt | provisional only |
| gpr3_twf154_wt | c7xmsA | 99.960 | 12.000 | 267 | ../../../../../receptors/final-docking/source-archives/phyre2-complete-jobs/Gpr3/aligs/c7xmsA_.344.alig.txt | provisional only |
| gprc_wt | c7xmsA | 99.820 | 14.000 | 268 | ../../../../../receptors/final-docking/source-archives/phyre2-complete-jobs/GprC/aligs/c7xmsA_.147.alig.txt | provisional only |
| srbc64_wt | c7xmsA | 99.950 | 9.000 | 265 | ../../../../../receptors/final-docking/source-archives/phyre2-complete-jobs/SRBC-64/aligs/c7xmsA_.313.alig.txt | provisional only |

这些对齐足以提供共同模板列线索，但低序列一致性、无逐位点 posterior、也无直接五受体结构叠合；因此不足以把相同模板列自动称为可靠同源位置。正式候选表的 `homologous_position` 保持空白。

gpr2 deltaN 文件名和 PDB 编号显示删除 1–21、164–178 后仍保留原序列编号（22 起始，163 后接 179）；gpr3 删除 1–7、150–163 后同样保留原编号（8 起始，149 后接 164）。因此本分析没有对 deltaN 残基号施加固定偏移。

完成严格保守性判断至少需要以下之一：

- 经过人工检查的五受体直接 MSA，并给出候选位点的列映射与局部置信度；
- 五个有效构建体的残基级结构叠合映射（最好限定跨模型稳定的 TM 核心，并给出每个位点的映射质量）；
- 若采用 GPCR 通用编号，需要明确编号体系、TM 边界来源及 deltaN 到全长序列的映射表。

## 可追溯输出

- 未截断支持矩阵（791 rows）：`/Users/roy/.codex/visualizations/2026/08/25/01a0380b-162d-7fa3-bc30-3dbd965d3a5c/prolif-cross-receptor-readonly/prolif_support_matrix_all.csv`
- 稳健/中等候选全表（182 rows）：`/Users/roy/.codex/visualizations/2026/08/25/01a0380b-162d-7fa3-bc30-3dbd965d3a5c/prolif-cross-receptor-readonly/prolif_candidate_table.csv`
- 50 模块审计与 source CSV：`/Users/roy/.codex/visualizations/2026/08/25/01a0380b-162d-7fa3-bc30-3dbd965d3a5c/prolif-cross-receptor-readonly/prolif_module_audit.csv`
- 配体共享/偏好比较：`/Users/roy/.codex/visualizations/2026/08/25/01a0380b-162d-7fa3-bc30-3dbd965d3a5c/prolif-cross-receptor-readonly/prolif_ligand_comparison.csv`
- 跨受体功能趋同与暂定模板位置：`/Users/roy/.codex/visualizations/2026/08/25/01a0380b-162d-7fa3-bc30-3dbd965d3a5c/prolif-cross-receptor-readonly/prolif_cross_receptor_candidates.csv`

所有 CSV 均为派生只读分析结果，写在 Codex 会话输出目录；项目工作簿、源 CSV 与项目文件未修改。
