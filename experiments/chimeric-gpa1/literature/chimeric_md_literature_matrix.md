# Chimeric Gα + GPCR-Gα 复合物 MD 文献矩阵

> **初始调研日期**: 2026-04-17
> **source-audit 修订**: 2026-05-06
> **重要降级**: 旧版“全量 / 仅 2 篇 / 仅 1 篇 / 首创”属于 only-N 强断言。2026-05-06 审查发现作者名和旧引用存在错误，完整重新枚举前，本矩阵只作为 **exact-pointer anchors + pending audit list**，不得直接用于 wiki/paper 的 final novelty claim。

---

## 1. 真菌 / Ste2-Gpa1 相关 exact-pointer anchors

| # | 文献 | 物种 | 体系组成 | 方法/技术栈 | 时长 | Chimeric Gα? | 当前用途 | 审查状态 |
|---|------|------|---------|-------------|------|-------------|----------|----------|
| 1 | **Velazhahan et al. 2021** (*Nature* 589:148–153; DOI `10.1038/s41586-020-2994-1`; PDB `7AD3`) | 酿酒酵母 | Ste2 dimer + 2× heterotrimeric G proteins | cryo-EM + Ste2/G protein 相关 MD 背景 | 需按原文 methods 再细拆 | 否 (WT) | Ch-ctrl 结构/界面几何锚点 | 已核 DOI/PDB；MD 参数不直接迁移 |
| 2 | **Mohanty et al. 2025** (*eLife* 14:RP106397; DOI `10.7554/eLife.106397.3`) | 酿酒酵母 | Ste2p-Gpa1p interface / Ste2p-metabolite / miniGpa1 docking context | Gcoupler + Ste2p-ligand MD + docking/ΔG/Kd analysis | 非本项目同类 full-complex production MD | 否 (WT/interface context) | Ste2p-Gpa1p interface allosteric/metabolite context | **旧文档误作 Ramasamy et al.；已降级为非 full-complex MD protocol** |

**当前结论**: 仅能说“Velazhahan 2021 是 Ste2-Gpa1/G protein 结构锚点；Mohanty 2025 是 Ste2p-Gpa1p interface/allosteric context”。暂不再写“真菌 GPCR-Gα 复合物 MD 仅 2 篇”。

## 2. Chimeric Gα + GPCR 复合物 MD exact-pointer anchor

| # | 文献 | 物种 | 体系组成 | 力场/引擎 | 时长 | 嵌合设计 | 当前用途 | 审查状态 |
|---|------|------|---------|----------|------|---------|----------|----------|
| 1 | **Tawfeeq et al. 2025** (*Biochemistry*; DOI `10.1021/acs.biochem.4c00779`) | 人 | D1R/D2R + Gαs/Gαi WT + G_i18s/G_s18i | CHARMM-GUI setup + AMBER PMEMD；AMBER ff19SB/Lipid17/OPC/GAFF2 | 每模型 4 rep × 500 ns | C-term/α5 18 aa swap (Gs↔Gi) | 最直接的 chimeric Gα MD 设计先例；支持 500 ns/rep 量级 | 已核；不是 GROMACS/CHARMM36m 来源；不支持 empty-only |

**当前结论**: Tawfeeq 2025 是已核 direct precedent，但完整“唯一 chimeric Gα MD”声明需重新枚举后才能用于 final 文稿。

> ⚠️ **引用勘误**: 项目文档中此前引用为 “Tsai et al. 2025”，实际第一作者为 **Tawfeeq C**；2026-05-06 进一步纠正其技术栈和 nucleotide-state 迁移。

## 3. 相关工程化 Gα + GPCR MD（非严格 chimeric）

| # | 文献 | 物种 | 体系组成 | 力场/引擎 | 时长 | 工程化类型 | 当前用途 | 审查状态 |
|---|------|------|---------|----------|------|----------|----------|----------|
| 1 | **Renault et al. 2019** (*Scientific Reports* 9:5495; DOI `10.1038/s41598-019-41980-x`) | 人 | A2A receptor + Mini-Gs / α5 helix | CHARMM-GUI；POPC；CHARMM36 + CGenFF；GROMACS 5.1.4 | 2 independent replicas × 600 ns；discard first 100 ns；selected systems extended to 2 μs | Mini-Gs = engineered Gα mimic | 支持 GROMACS/CHARMM/POPC + engineered Gα/α5 protocol analogy | **替换旧错误引用 Ranganathan et al. 2019 / Sci Rep 9:11265** |

## 4. 近缘但不含 Gα 的真菌 GPCR MD / 待查项目

| # | 文献 | 物种 | 体系 | 备注 | 审查状态 |
|---|------|------|------|------|----------|
| 1 | **Bansal & Shukla 2026** (bioRxiv 2026.01.14.699465) | 酿酒酵母 | Ste2 单体 apo | 毫秒级 MD，Class D 激活机制，**无 G 蛋白** | 本轮未审；pending source audit |
| 2 | Gcoupler / sterols 相关旧条目 | 酿酒酵母 | Ste2 单体 + 脂双层 / interface context | 已合并到 Mohanty et al. 2025 条目 | 已重新定位 |

## 5. 本项目方法学声明（修订纪律）

**不得直接使用的旧声明**:

- “真菌 GPCR-Gα 复合物全原子 MD 仅有 2 篇”
- “Chimeric Gα + GPCR 复合物 MD 全文献仅 1 篇”
- “本项目首个……”

**可安全使用的当前表述**:

> 在 2026-05-06 已核 exact-pointer 文献中，尚未找到非酿酒酵母真菌 chimeric Gα–GPCR complex MD 的直接先例；本项目需要把 novelty claim 标为 pending source audit，待完整文献重枚举后再写入 wiki/paper。

---

## 引用来源

1. Velazhahan V et al. (2021). “Structure of the class D GPCR Ste2 dimer coupled to two G proteins.” *Nature* 589:148–153. DOI: `10.1038/s41586-020-2994-1`; PDB: `7AD3`.
2. Mohanty SK et al. (2025). “Deep learning reveals endogenous sterols as allosteric modulators of the GPCR–Gα interface.” *eLife* 14:RP106397. DOI: `10.7554/eLife.106397.3`.
3. Tawfeeq C et al. (2025). “G Protein Selectivity in Dopamine Receptors is Determined before GDP Release.” *Biochemistry* 64(11):2439–2454. DOI: `10.1021/acs.biochem.4c00779`.
4. Renault P et al. (2019). “Molecular Dynamics Simulations of the Allosteric Modulation of the Adenosine A2a Receptor by a Mini-G Protein.” *Scientific Reports* 9:5495. DOI: `10.1038/s41598-019-41980-x`.
5. Casiraghi M et al. (2025). “Structure and dynamics determine G protein coupling specificity at a class A GPCR.” *Science Advances* 11(12):eadq3971. DOI: `10.1126/sciadv.adq3971`.
6. van den Broek RL et al. (2024). “Memprot.GPCR-ModSim: modelling and simulation of membrane proteins in a nutshell.” *Bioinformatics* 40(11):btae662. DOI: `10.1093/bioinformatics/btae662`.
7. Miszta P et al. (2021). “GPCRsignal: webserver for analysis of the interface between G-protein–coupled receptors and their effector proteins by dynamics and mutations.” *Nucleic Acids Research* 49(W1):W247–W256. DOI: `10.1093/nar/gkab434`.
