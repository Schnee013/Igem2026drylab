# Cevheroglu et al. 2017 — 文献总结

> **完整标题**: GPCR-Galpha protein precoupling: Interaction between Ste2p, a yeast GPCR, and Gpa1p, its Galpha protein, is formed before ligand binding via the Ste2p C-terminal domain and the Gpa1p N-terminal domain
> **期刊**: *Biochimica et Biophysica Acta (BBA) - Biomembranes* 1859:2435-2446
> **DOI**: 10.1016/j.bbamem.2017.09.022
> **本地 PDF**: `../pdf/Cevheroglu2017-Ste2-Gpa1-precoupling.pdf`
> **全文转写**: `../../../experiments/chimeric-gpa1/literature/fulltext_md/Cevheroglu2017-Ste2-Gpa1-precoupling.md`

## 核心发现

1. 该文用 BRET 检测 Ste2p 与 Gpa1p 的近距离互作，实验设计聚焦 Gpa1p N-terminal residues 与 Ste2p C-terminal residues。
2. BRET 构建中，Ste2p 在 304 位附近接入 RLuc；Gpa1p 在 N 端 10、36、67 位附近接入 EGFP。Gpa1p 10 位构建给出最高 BRET signal，36/67 位较低但仍可检测。
3. alpha-factor 刺激后，BRET signal 没有显著增加或降低；作者据此支持 Ste2p-Gpa1p 在 ligand binding 前已存在 pre-coupled heterodimer，而不是单纯 collision model。
4. BiFC/confocal 结果显示 Ste2p-Gpa1p heterodimer 可在 ER biosynthesis 阶段和 plasma membrane 上观察到。
5. 论文自身也把 Galpha C-terminus/alpha5 等区域作为已知 GPCR-Galpha 接触背景，因此该文不否定 Galpha C-terminal coupling-specificity 逻辑。

## 与项目的关系

- **可用作弱背景**：支持 Ste2-Gpa1 control/interface biology、yeast Gpa1 N 端 membrane anchoring / precoupling 相关背景。
- **对实际 candidate 的可迁移性有限**：本项目 chimeric candidate 面向 Gpr2/Gpr3/GprC，不是 Ste2；因此该文不能直接支撑 GPR-Gpa1 chimera 的候选排序、AF3 解释、MD setup、CG route 或 candidate replacement。
- **设计记录意义**：当前 chimera 方案保留 yeast Gpa1 N 端，只替换 C-terminal/eCT-alpha5-beta6 区域；该文最多提醒不要把 yeast Gpa1 N 端预偶联/定位功能错误删除。

## 边界

- 不支持 Martini/coarse-grained build route。
- 不支持 MD atom selection、restraints、padding、算力缩减或 benchmark 结论。
- 不支持将 Ste2-Gpa1 预偶联证据直接迁移到 Gpr2/Gpr3/GprC candidates。

## References / 所引

- `../pdf/Cevheroglu2017-Ste2-Gpa1-precoupling.pdf`
- `../../../experiments/chimeric-gpa1/literature/fulltext_md/Cevheroglu2017-Ste2-Gpa1-precoupling.md`
- `../../../experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`

## Referenced by / 被引

- `../literature-matrix.md`
- `../../../experiments/chimeric-gpa1/literature/chimeric_system_reduction_literature_matrix.md`
- `../../../experiments/chimeric-gpa1/literature/r4_gpcr_galpha_citation_chasing_20260704.md`
