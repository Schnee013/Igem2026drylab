# Yang and Song 2024 — 文献总结

> **完整标题**: Switching Go-Martini for Investigating Protein Conformational Transitions and Associated Protein-Lipid Interactions
> **期刊**: *Journal of Chemical Theory and Computation* 20:2618-2629
> **DOI**: 10.1021/acs.jctc.3c01222
> **本地 PDF**: `../pdf/Yang2024-Switching-Go-Martini.pdf`
> **全文转写**: `../../../experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md`
> **补充资料**: `../../../experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-supporting-information.pdf`
> **Tutorial archive**: `../../../experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-tutorial.zip`

## 核心发现

1. 该文提出 Switching Go-Martini：把 switching Go 思路接入 Martini 3，用两个已知构象状态的拓扑/Go-like contact network 驱动蛋白从 State A 转向 State B，同时保留 explicit water、lipid 和 Martini membrane 环境。
2. 方法用 GlnBP、AdK、beta2AR 做 benchmark；beta2AR 是 GPCR 例子，作者报告转变路径与既有 CG/atomistic MD 定性一致。
3. 该方法被应用到 ATP8A1-CDC50a flippase，在 explicit membrane 中观察构象转换伴随 lipid transport 的细节。
4. 方法本身不是无偏 CG 生产模拟：状态驻留时间由 switching protocol 控制，作者明确指出它不能定量给出两态之间 free-energy landscape 或 kinetics，且高能切换可能产生 improper pathways。
5. 主文说明 Supporting Information 含 simulation parameters、transition pathway summary 和 tutorial；补充 PDF 与 tutorial zip 已在 repo 内归档，并已在 R4 方法抽取文档中完成方法相关细节提取。

## 方法摘录

- Force field / engine: Martini 3 version 3.0.0；GROMACS 2020.x 或 2021.x。
- Protein CG generation: `martinize2.py` / `vermouth-martinize`。
- Go-like contacts: OV 和 rCSU contacts；`create_goVirt.py` 或作者修改的 `create_goVirt_for_multimer.py`；contact distance cutoff 3-11 A；dissociation energy epsilon = 12.0 kJ/mol。
- General MD setup: energy minimization 后 NPT equilibration；CG protein BB position restraints 10 kJ/mol/A^2；production 使用 1 atm、310.15 K、V-rescale tau 1.0 ps、Parrinello-Rahman pressure coupling tau 12.0 ps；electrostatics 和 van der Waals cutoffs 11 A；reaction-field epsilon_r = 15。
- Switching step: State A topology 下先振荡；切到 State B 前用 State B topology 做 1000 steps x 0.002 ps short/slow relaxation；随后用 State B topology 生产模拟。
- beta2AR setup: active/inactive structures from PDB 3SN6 and 2RH1；Modeller 修补缺失 loop/mutations；POPC bilayer，80 x 80 x 100 A box，150 mM NaCl；40 CG simulations with 500 x 2 ns。
- ATP8A1-CDC50a setup: PDB 6K7M/6K7G；asymmetric membrane，120 x 120 x 190 A box；cytoplasmic leaflet 10% POPS，其余 POPC；150 mM NaCl；50 simulations of 200 ns plus 800 ns，部分 lipid-trapping state 追加 1000 ns。

### Supplementary PDF / tutorial archive

Source-faithful extraction:

- SI Table S1 records the per-system CG schedules: GlnBP/AdK/beta2AR/ATP8A1-CDC50a minimization steps 5000/5000/15000/15000; equilibration 1/1/2/10 ns; production 300 x 3 ns, 100 x 2 ns, 500 x 2 ns, and 200/800 ns; repeats 50/70/40/50; transition relaxation 1000 steps x 0.002 ps.
- SI Table S2 records pathway counts: GlnBP 50 open-closed; AdK 48 NMP-closing, 7 LID-closing, 15 middle; beta2AR 39 normal and 1 abnormal; ATP8A1-CDC50a 36 main, 5 middle, 9 incomplete.
- Tutorial zip uses beta2AR active-to-inactive transition as the worked GPCR example: preprocess 3SN6/2RH1, repair 3SN6 missing loop/mutations with Modeller, add 2RH1 missing side chains, trim both to residues 30-230 and 265-341, and build state-specific Martini/Go topologies.
- Tutorial commands use `martinize2 -ff martini3001 -govs-include` with state-specific `-govs-moltype`; the OV/rCSU contact-map step is followed by `create_goVirt_for_multimer.py --go_eps 12 --Natoms 681`.
- The modified Go script defaults to 0.3-1.1 nm contact cutoffs, sequence-distance exclusion 4, symmetric OV+rCSU contact retention, and outputs virtual-site bead definitions, LJ Go tables, exclusions, and VMD-only harmonic Go-bond files.
- Tutorial membrane setup uses `insane.py` for an 8 x 8 x 10 nm POPC/water/ion box with 0.15 M salt and warns that ion names/counts require manual correction because virtual atoms without charges are counted by `insane.py`.
- Prepared tutorial topology records one receptor molecule, 77 + 79 POPC, 2970 water beads, 31 `NA`, and 33 `CL`; state topologies define `GO_VIRT` and include state-specific Active/Inactive ITP files.
- Tutorial MDP files record steepest-descent minimization with 15000 steps, NPT with `define = -DPOSRES` and 20 ns at 0.020 ps timestep, 1000-step 0.002 ps transition relaxation under the destination topology, and 500 ns production with 0.020 ps timestep. This tutorial NPT length differs from SI Table S1 beta2AR equilibration (2 ns), so this summary preserves both source statements.

Project interpretation:

- The SI/tutorial closes the previous "Yang supplementary method extraction pending" gap.
- It refines R4 object-contract vocabulary around state-pair preprocessing, Go-contact generation, topology switching, membrane/ion setup, MDP schedule, and trajectory post-processing.
- It remains beta2AR receptor-only tutorial evidence, not receptor-Galpha, not Ste2-Gpa1, and not chimeric Galpha.
- The follow-up R4 new-source plan uses Yang2024 as vocabulary for what to extract next: interface/contact policy, structure-bias choice, and CG-to-AA revalidation.

## 与项目的关系

- **支持 R4 继续 source-gate**：这是当前已读来源中最明确的 Martini 3 + Go-like structure-bias + explicit lipid/water membrane conformational-transition 方法源。
- **支持需要写入 R4 object contract 的字段**：两端构象来源、protein trimming/missing-loop policy、Go-like contact generator、bias energy、contact cutoff、membrane/ion setup、switching schedule、replicate count、comparison metrics。
- **不能直接支持 chctrl build**：该文没有 GPCR-Galpha、Ste2-Gpa1 或 chimeric Galpha complex；beta2AR 是 receptor-only conformational transition benchmark，不是 receptor-effector interface preservation source。
- **不能作为 candidate replacement 依据**：Switching Go-Martini 会人为驱动两态转换；它适合探索路径和后续 atomistic/free-energy 工作的初筛，不等价于 full atomistic receptor-Galpha-in-membrane evidence。

## 边界

- R4 如果采用 Go-Martini，必须先定义 receptor-Galpha quaternary contact 是否被 bias、如何 bias、以及如何与 existing chctrl atomistic evidence 对比。
- 在没有项目级 receptor-Galpha object contract、backmapping/atomistic comparison gate 和 interface-drift failure criteria 前，该文只能把 P0047 状态推进到 `method_extracted_structure_bias_source`，不能推进到 buildable prototype。
- 该文不支持 Ch-1/Ch-2/Ch-4 action、E2 run、算力缩减成功、或候选迁移。

## References / 所引

- `../pdf/Yang2024-Switching-Go-Martini.pdf`
- `../../../experiments/chimeric-gpa1/literature/fulltext_md/Yang2024-Switching-Go-Martini.md`
- `../../../experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-supporting-information.pdf`
- `../../../experiments/chimeric-gpa1/literature/source_attachments/Yang2024-Switching-Go-Martini-tutorial.zip`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `../../../experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`

## Referenced by / 被引

- `../literature-matrix.md`
- `../../../experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
- `../../../experiments/chimeric-gpa1/literature/r4_direct_gpcr_galpha_cg_source_chase_20260705.md`
