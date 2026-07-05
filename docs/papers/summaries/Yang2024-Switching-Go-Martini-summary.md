# Yang and Song 2024 — 文献总结

> **完整标题**: Switching Go-Martini for Investigating Protein Conformational Transitions and Associated Protein-Lipid Interactions
> **期刊**: *Journal of Chemical Theory and Computation* 20:2618-2629
> **DOI**: 10.1021/acs.jctc.3c01222
> **本地 PDF**: `../pdf/Yang2024-Switching-Go-Martini.pdf`
> **全文转写**: `../../../experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md`

## 核心发现

1. 该文提出 Switching Go-Martini：把 switching Go 思路接入 Martini 3，用两个已知构象状态的拓扑/Go-like contact network 驱动蛋白从 State A 转向 State B，同时保留 explicit water、lipid 和 Martini membrane 环境。
2. 方法用 GlnBP、AdK、beta2AR 做 benchmark；beta2AR 是 GPCR 例子，作者报告转变路径与既有 CG/atomistic MD 定性一致。
3. 该方法被应用到 ATP8A1-CDC50a flippase，在 explicit membrane 中观察构象转换伴随 lipid transport 的细节。
4. 方法本身不是无偏 CG 生产模拟：状态驻留时间由 switching protocol 控制，作者明确指出它不能定量给出两态之间 free-energy landscape 或 kinetics，且高能切换可能产生 improper pathways。
5. 主文说明 Supporting Information 含 simulation parameters、transition pathway summary 和 tutorial；本次只归档了用户提供的主文 PDF，补充文件尚未本地归档。

## 方法摘录

- Force field / engine: Martini 3 version 3.0.0；GROMACS 2020.x 或 2021.x。
- Protein CG generation: `martinize2.py` / `vermouth-martinize`。
- Go-like contacts: OV 和 rCSU contacts；`create_goVirt.py` 或作者修改的 `create_goVirt_for_multimer.py`；contact distance cutoff 3-11 A；dissociation energy epsilon = 12.0 kJ/mol。
- General MD setup: energy minimization 后 NPT equilibration；CG protein BB position restraints 10 kJ/mol/A^2；production 使用 1 atm、310.15 K、V-rescale tau 1.0 ps、Parrinello-Rahman pressure coupling tau 12.0 ps；electrostatics 和 van der Waals cutoffs 11 A；reaction-field epsilon_r = 15。
- Switching step: State A topology 下先振荡；切到 State B 前用 State B topology 做 1000 steps x 0.002 ps short/slow relaxation；随后用 State B topology 生产模拟。
- beta2AR setup: active/inactive structures from PDB 3SN6 and 2RH1；Modeller 修补缺失 loop/mutations；POPC bilayer，80 x 80 x 100 A box，150 mM NaCl；40 CG simulations with 500 x 2 ns。
- ATP8A1-CDC50a setup: PDB 6K7M/6K7G；asymmetric membrane，120 x 120 x 190 A box；cytoplasmic leaflet 10% POPS，其余 POPC；150 mM NaCl；50 simulations of 200 ns plus 800 ns，部分 lipid-trapping state 追加 1000 ns。

## 与项目的关系

- **支持 R4 继续 source-gate**：这是当前已读来源中最明确的 Martini 3 + Go-like structure-bias + explicit lipid/water membrane conformational-transition 方法源。
- **支持需要写入 R4 object contract 的字段**：两端构象来源、protein trimming/missing-loop policy、Go-like contact generator、bias energy、contact cutoff、membrane/ion setup、switching schedule、replicate count、comparison metrics。
- **不能直接支持 chctrl build**：该文没有 GPCR-Galpha、Ste2-Gpa1 或 chimeric Galpha complex；beta2AR 是 receptor-only conformational transition benchmark，不是 receptor-effector interface preservation source。
- **不能作为 candidate replacement 依据**：Switching Go-Martini 会人为驱动两态转换；它适合探索路径和后续 atomistic/free-energy 工作的初筛，不等价于 full atomistic receptor-Galpha-in-membrane evidence。

## 边界

- R4 如果采用 Go-Martini，必须先定义 receptor-Galpha quaternary contact 是否被 bias、如何 bias、以及如何与 existing chctrl atomistic evidence 对比。
- 在没有本地归档 SI/tutorial 和项目级 object contract 前，该文只能把 P0047 状态推进到 `method_extracted_structure_bias_source`，不能推进到 buildable prototype。
- 该文不支持 Ch-1/Ch-2/Ch-4 action、E2 run、算力缩减成功、或候选迁移。

## References / 所引

- `../pdf/Yang2024-Switching-Go-Martini.pdf`
- `../../../experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`

## Referenced by / 被引

- `../literature-matrix.md`
- `../../../experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
