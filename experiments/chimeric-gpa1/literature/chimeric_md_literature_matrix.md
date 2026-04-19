# Chimeric Gα + GPCR-Gα 复合物 MD 文献矩阵

> **调研日期**: 2026-04-17
> **调研方法**: 7 个并行 agent × 4 搜索维度（PubMed/Scholar + bioRxiv/chemRxiv + Citation graph + 广义 chimeric Gα）
> **覆盖**: ≥4 独立搜索维度，每维度 3-6 组关键词，≥12 次 WebSearch

---

## 1. 真菌 GPCR-Gα 复合物 MD 文献（全量）

| # | 文献 | 物种 | 体系组成 | 力场/引擎 | 时长 | Chimeric Gα? | 备注 |
|---|------|------|---------|----------|------|-------------|------|
| 1 | **Velazhahan et al. 2021** (Nature 589:148-153) | 酿酒酵母 | Ste2 dimer + 2×(Gpa1-Ste4-Ste18) | CHARMM36m / GROMACS | 未详述 | 否 (WT) | cryo-EM + 显式 MD；PDB 7AD3 来源论文 |
| 2 | **Ramasamy et al. 2025** (eLife 14:RP106397) | 酿酒酵母 | Ste2 + Gpa1 (from 7AD3) | 酵母磷脂膜 | 未详述 | 否 (WT) | sterol allosteric modulator; deep learning cavity analysis |

**结论**: 真菌 GPCR-Gα 复合物 MD 仅 2 篇，均为酿酒酵母 Ste2-Gpa1 WT 系统。**零篇**涉及线虫捕食真菌（Arthrobotrys/A. flagrans）GPCR。

## 2. Chimeric Gα + GPCR 复合物 MD 文献（全量，不限物种）

| # | 文献 | 物种 | 体系组成 | 力场/引擎 | 时长 | 嵌合设计 |
|---|------|------|---------|----------|------|---------|
| 1 | **Tawfeeq et al. 2025** (Biochemistry, DOI: 10.1021/acs.biochem.4c00779) | 人 | D1R/D2R + Gs18i/Gi18s | CHARMM / lipid bilayer | 4 rep × 500 ns = 2 μs/complex | C-term 18 aa swap (Gs↔Gi) |

**结论**: 全文献范围仅 1 篇 chimeric Gα MD。零篇真菌 chimeric Gα MD。

> ⚠️ **引用勘误**: 项目文档中此前引用为 "Tsai et al. 2025"，实际第一作者为 **Tawfeeq C**。已全局修正。

## 3. 相关工程化 Gα + GPCR MD（非严格 chimeric）

| # | 文献 | 物种 | 体系组成 | 力场/引擎 | 时长 | 工程化类型 |
|---|------|------|---------|----------|------|----------|
| 1 | **Ranganathan et al. 2019** (Sci Rep 9:11265) | 人 | A2A + Mini-Gs | CHARMM36 + CGenFF / GROMACS 5.1.4 | 2.0 μs | Mini-Gs = 截短 GTPase domain + 稳定性突变 |

## 4. 近缘但不含 Gα 的真菌 GPCR MD

| # | 文献 | 物种 | 体系 | 备注 |
|---|------|------|------|------|
| 1 | **Bansal & Shukla 2026** (bioRxiv 2026.01.14.699465) | 酿酒酵母 | Ste2 单体 apo | 毫秒级 MD，Class D 激活机制，**无 G 蛋白** |
| 2 | **Gcoupler / Sterols** (bioRxiv 2023 → eLife) | 酿酒酵母 | Ste2 单体 + 脂双层 | 100 ns × 3 rep，受体-only；Gpa1 界面分析基于几何非 MD |

## 5. 本项目方法学首创声明（经系统搜索验证）

**原声明**: "零篇真菌 GPCR-Gα 复合物 MD 文献；零篇 ascaroside 结合态 GPCR-Gα MD"

**修正声明**:

> 截至 2026-04-17，真菌 GPCR-Gα 复合物全原子 MD 仅有 2 篇发表工作（Velazhahan et al. 2021, Nature; Ramasamy et al. 2025, eLife），均限于酿酒酵母 Ste2-Gpa1 野生型系统。Chimeric Gα + GPCR 复合物 MD 全文献仅 1 篇（Tawfeeq et al. 2025, Biochemistry），使用人源 D1R/D2R + Gs/Gi C 端 18 残基交换嵌合体。
>
> 本项目在以下两个维度上**方法学首创**：
> 1. 首个非酿酒酵母真菌 GPCR（*A. oligospora* Gpr2/Gpr3, *A. flagrans* GprC）与 Gα 蛋白的全原子 MD
> 2. 首个真菌嵌合 Gα（酿酒酵母 Gpa1 骨架 + 真菌 Gα C 端）复合物 MD
>
> 验证维度：PubMed/Google Scholar 精确检索（5 组关键词）+ bioRxiv/chemRxiv 预印本（6 组关键词）+ Semantic Scholar 引用图谱追踪（Velazhahan 2021, Ramasamy 2025, Tawfeeq 2025 的正向/反向 2 层）+ 广义 chimeric Gα 全文献搜索（6 组关键词）。

---

## 引用来源

1. Velazhahan V, Ma N, Vaidehi N, Tate CG (2021). Structure of the class D GPCR Ste2 dimer coupled to two G proteins. *Nature* 589:148-153. DOI: 10.1038/s41586-020-2994-1
2. Ramasamy S et al. (2025). Deep learning reveals endogenous sterols as allosteric modulators of the GPCR-Gα interface. *eLife* 14:RP106397.
3. Tawfeeq C, Hilibrand AS, Smith JS, Portillo J, Kruse AC, Abrol R (2025). G Protein Selectivity in Dopamine Receptors is Determined before GDP Release. *Biochemistry*. DOI: 10.1021/acs.biochem.4c00779
4. Ranganathan A et al. (2019). Allosteric coupling across the orthosteric binding site in the A2A-Mini-Gs complex. *Sci Rep* 9:11265.
5. Bansal S, Shukla D (2026). Sequence constraints predispose Class D GPCRs to follow an atypical activation mechanism. *bioRxiv* 2026.01.14.699465.
