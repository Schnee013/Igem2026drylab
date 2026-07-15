# Sahoo et al. 2023 — 文献总结

> **完整标题**: Transmembrane region dimer structures of Type 1 receptors readily sample alternate configurations: MD simulations using the Martini 3 coarse grained model compared to AlphaFold2 Multimer
> **期刊**: *Structure* 31:735-745.e2
> **DOI**: 10.1016/j.str.2023.03.014
> **本地 PDF**: `../pdf/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.pdf`
> **全文转写**: `../../../experiments/chimeric-gpa1/literature/fulltext_md/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.md`

## 核心发现

1. 该文用 Martini 3 coarse-grained MD 研究 11 个 type 1 receptor transmembrane-region dimer 的组装和构象采样，并与 NMR structures、PREDDIMER 和 AlphaFold2 Multimer 比较。
2. Martini 3 CG 结果与 NMR 的一致性有限：主文摘要报告 5/11 个 CG TM structures 与 NMR structures 接近，PREDDIMER 和 AlphaFold2 Multimer 的对应数量更高。
3. CG simulations 的主要价值在于显示 TM dimers 会采样 alternate configurations，并在多个状态之间 interconvert；作者用 4 条轨迹中的相似 2D distance-angle regions 和约 10 次或更多 state transitions 缓解 convergence 担忧。
4. 论文强调 flanking residues 对 TM dimer stability 很重要；只保留非极性 TM domain 在多套系统中不能稳定得到 dimer。
5. 该文讨论 Martini 2 膜内 protein-protein interaction 过 sticky 的已知问题，并设置 polyAla / polySer negative-control 尝试；这对 R4 的 quaternary-bias 和 false association 风险有提示意义。

## 方法摘录

- System scope: 11 个 single-pass/type 1 receptor TM region dimers，主要来自 receptor tyrosine kinases；不是 GPCR，也不是 Galpha complex。
- Initial model: UniProt 定义的 TM hydrophobic domain 建成 ideal alpha helix；N 端加 8-9 residues、C 端加 10 residues；两个相同 peptide 初始相距 50 A，置于 DMPC bilayer 中。
- CG generation: `martinize2.py` workflow module of Martini 3 / `vermouth-martinize`；DSSP secondary-structure assignment。
- Structure bias: elastic network 用于稳定 TM monomer helical secondary structure；force constant 500 kJ/mol/nm2；lower/upper elastic cutoff 0.5/0.9 nm。
- Engine/setup: GROMACS 2016.5；`insane.py` 生成 DMPC bilayer，典型 306 lipids 和 4870 CG water molecules；100 x 100 x 100 A cubic box；regular Martini water；neutralized and 0.15 M NaCl。
- Equilibration/production: equilibration 500 ps；reaction-field electrostatics cutoff 11 A；LJ potential-shift-verlet cutoff 11 A；V-rescale at 320 K；Berendsen barostat tau 1.0 ps，compressibility 3.0 x 10^-4 bar^-1，1 bar；time step 20 fs；4 replicates x 4 us。
- Backmapping/comparison: extracted CG structures converted to atomistic representation using Martini Backward tool / CG2AT-related tooling for NMR/PREDDIMER/AlphaFold comparison.

## 与项目的关系

- **支持 R4 风险识别**：CG Martini 3 可以采样膜内 protein-protein alternate states；因此 chctrl 的 receptor-Galpha interface 若走 CG，必须显式定义是否允许 interface 重排、如何判定 false quaternary rearrangement、如何做 replicate/convergence check。
- **支持 validation vocabulary**：多 replicate、distance/crossing-angle state map、backmapping to atomistic representation、与实验/预测结构比较，可作为未来 R4 object contract 的检查类别。
- **不能直接支持 buildable R4**：该文系统是 single-pass TM peptide dimer，不含 full GPCR、Galpha、heterotrimeric context、alpha5/eCT junction、explicit receptor-Galpha interface metrics。
- **不能迁移 padding/setup 数值**：DMPC 100 A cubic box、306 lipids、4870 CG waters 等只适用于短 TM peptide dimer benchmark，不是 chctrl full-complex membrane setup。

## 边界

- 该文对 R4 的定位是 `quaternary-bias_risk_and_validation_analog`，不是 direct GPCR-Galpha CG route。
- 不支持 candidate replacement、Ch-1/Ch-2/Ch-4 action、E2 run、或省算力成功结论。
- 若未来采用 Martini 3/elastic-network route，需要避免把 elastic network 的 secondary-structure stabilization 误读为 receptor-Galpha interface preservation。

## References / 所引

- `../pdf/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.pdf`
- `../../../experiments/chimeric-gpa1/literature/fulltext_md/Sahoo2023-Type1-Receptor-Dimers-Martini3-AF2Multimer.md`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`

## Referenced by / 被引

- `../literature-matrix.md`
- `../../../experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_source_screen_20260704.tsv`
- `../../../experiments/chimeric-gpa1/literature/r4_cg_method_extraction_20260704.md`
