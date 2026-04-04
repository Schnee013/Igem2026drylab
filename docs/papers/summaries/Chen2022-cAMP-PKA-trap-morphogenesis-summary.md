# Chen et al. 2022 — 文献总结

> **完整标题**: The cAMP-PKA pathway regulates prey sensing and trap morphogenesis in the nematode-trapping fungus *Arthrobotrys oligospora*
> **期刊**: G3: Genes|Genomes|Genetics, 2022, 12(10), jkac217
> **DOI**: https://doi.org/10.1093/g3journal/jkac217
> **作者**: Sheng-An Chen, Hung-Che Lin, Yen-Ping Hsueh (中研院分子生物所)

## 核心发现

- **Tpk2 是 PKA 的关键 catalytic subunit**：*A. oligospora* 基因组编码两个 PKA catalytic subunit（TPK1, TPK2），其中 TPK2 在 nematode 诱导下转录上调，而 TPK1 表达不变。*tpk2* 突变体完全丧失 trap morphogenesis 能力，菌丝在线虫存在下保持未分化状态，无法捕杀线虫（24h survival rate 100% vs. WT 的 0%）
- **Gpa2 是 cAMP-PKA pathway 上游的 G protein alpha subunit**：*gpa2* 突变体 trap 形成严重受损（数量和形态均缺陷），仅形成少量不完整的 single loop 或 half loop，而非成熟的 3-cell adhesive network。24h 后约 50% 线虫仍存活（vs. WT 全部被捕杀）
- **外源 cAMP 可 rescue *gpa2* 突变表型**：添加 5 mM exogenous cAMP 或 5 mM IBMX（phosphodiesterase inhibitor）到培养基中，显著恢复了 *gpa2* 突变体的 trap formation（从 ~5 个增至 ~60 个 traps），证明 Gpa2 通过 cAMP 信号起作用
- **cAMP/IBMX 无法 rescue *tpk2* 或 *gpb1* 突变体**：说明 Tpk2 位于 cAMP 下游（PKA catalytic subunit 本身），而 Gpb1（G protein beta subunit）不通过 cAMP-PKA pathway 起作用，而是通过 pheromone-response MAPK cascade
- **完整信号通路模型**：Nematode-derived signals → unidentified GPCR(s) → Gpa2 (Galpha, Class III) 解离 → Adenylyl cyclase Cyr1 激活 → ATP→cAMP → cAMP 结合 regulatory subunit Bcy1 → 释放 catalytic subunit Tpk2 → 磷酸化下游 unknown targets → **trap morphogenesis**

## 实验方法

- **Gene deletion**：在 *ku70* mutant 背景（TWF154）中进行 targeted gene deletion，利用 NHEJ deficiency 提高 homologous recombination 效率。使用 clonNAT resistance cassette，通过 PEG-mediated protoplast transformation
- **Gene complementation**：将 wild-type gene copies（含 1.5-2 kb upstream + 0.5 kb downstream）fused to G418 resistance cassette 回补到突变体中
- **Trap induction assay**：在 LNM（low-nutrient medium）上培养 2 天后，加入 30 条 L4 stage *C. elegans*，6h 后移除线虫，24h 后在 dissecting microscope 下 40x 放大计数 trap 数量，使用 Fungal Feature Tracker 软件定量
- **Nematode survival assay**：80 条 adult *C. elegans* 加入到 fungal culture 上，每 2h 计数存活线虫数
- **Phylogenetic analysis**：ClustalW alignment + Mega 7 neighbor-joining tree（3000 bootstrap replicates）
- **Transcriptomic analysis**：time-course RNA-seq（TPM normalization）比较 TPK1 vs. TPK2 在 nematode induction 后的表达变化
- **cAMP rescue 实验**：在 LNM 中添加 5 mM cAMP 或 5 mM IBMX，观察能否恢复突变体的 trap formation
- **SR2200 染色**：特异性标记 fungal cell wall，用于可视化 vegetative hyphae 和 trap 结构差异

## 关键数据

| 指标 | Wild-type | *tpk2* | *gpa2* | 回补株 |
|------|-----------|--------|--------|--------|
| Trap formation (24h) | 大量成熟 adhesive networks | **完全无 trap** | 极少量不完整 trap（single/half loop） | 恢复至 WT 水平 |
| *C. elegans* survival (24h) | ~0% | **100%** | **~50%** | 恢复至 WT 水平 |
| Colony morphology (PDA) | 正常 rosette cluster | 生长缓慢，仅 1-2 conidia on conidiophore | 轻微生长缺陷，conidiation 不受影响 | 恢复 |
| Trap count (*gpa2* + cAMP 5mM) | — | — | 从 ~5 增至 **~60** (p<0.0001) | — |
| Trap count (*tpk2* + cAMP 5mM) | — | **无变化 (ns)** | — | — |
| TPK2 mRNA (TPM, 0h→24h) | ~50 → ~350 | — | — | — |
| TPK1 mRNA (TPM, 0h→24h) | ~200 → ~200 (不变) | — | — | — |

- Gpa2 phylogenetically 属于 **Class III Galpha subunit**，与 *S. cerevisiae* Gpa2（nutrient-sensing pathway 调控 cAMP）同组
- Tpk2 phylogenetically 与 *M. oryzae* CPKA 和 *U. maydis* ADR1 同组——这两个是各自物种中负责 pathogenicity 的主要 PKA catalytic subunit

## 与项目的关系

### 与 Gpr2/Gpa2 coupling（Kuo 2024）的衔接
- Kuo 2024 确定了 **Gpr2** 是感知 nematode ascaroside 信号的 GPCR，并通过遗传学证据提出 Gpr2 与 Gpa2 偶联
- 本文（Chen 2022）提供了 Gpa2 下游 **完整的 cAMP-PKA cascade** 的功能验证：Gpa2 → Cyr1 (adenylyl cyclase) → cAMP → Bcy1/Tpk2 (PKA) → trap morphogenesis
- 两篇文章共同构建了从受体到效应器的完整信号通路：**Ascarosides → Gpr2 → Gpa2 → Cyr1 → cAMP → PKA (Bcy1+Tpk2) → Trap formation**

### 对 ODE modeling (P0) 的价值
- **可建模的节点**：GPCR activation → G protein dissociation → adenylyl cyclase activation → cAMP production → PKA activation → downstream phosphorylation → morphological output
- **关键参数来源**：
  - cAMP rescue concentration: **5 mM** exogenous cAMP 足以恢复 *gpa2* 表型
  - IBMX (PDE inhibitor) 同样以 5 mM 有效，暗示内源 cAMP 被 phosphodiesterase 快速降解（Ma et al. 2022 中有 PdeH/PdeL 数据可参考）
  - TPK2 transcription upregulation: ~7x（50→350 TPM）在 nematode induction 后
  - Trap formation 时间尺度：6h nematode exposure 即可触发，24h 后 quantifiable
  - *gpa2* 突变体 trap 数量约为 WT 的 ~10%，且形态不成熟
- **建模需注意**：
  - 该通路与 MAPK pheromone-response pathway（Fus3 MAPK）平行但独立——*gpb1* 不通过 cAMP-PKA
  - Tpk2 同时影响 vegetative growth 和 conidiation，说明存在 crosstalk
  - 下游 phosphorylation targets 尚未鉴定（论文 Fig. 4 标为 "Unknown target"）

### 缺失信息（建模时需注意）
- Adenylyl cyclase Cyr1 (EYR41_002009) 的 deletion mutant **未成功获得**（多次转化失败），可能是 essential gene
- 下游 PKA phosphorylation substrates 完全未知
- 内源 cAMP 的绝对浓度未测量（仅有 exogenous rescue 数据）
- Regulatory subunit Bcy1 和 catalytic subunit Tpk1 的功能尚未表征

## 关键引用

- **Ma et al. 2022** — *A. oligospora* 中两个 cAMP phosphodiesterases (PdeH, PdeL) 的功能分析；*pdeH* 突变导致 cAMP 水平升高，生长缺陷且无法形成 trap（cAMP 过高也有害）
- **Chen et al. 2021** — Fus3 MAPK pheromone-response pathway 在 *A. oligospora* 中的功能（与 cAMP-PKA 平行的另一条通路）
- **Kuo et al. 2020** — *ku70* mutant strain (TWF1697) 的建立；HOG pathway 在 osmosensing 和 trap morphogenesis 中的作用
- **Zhen et al. 2018** — Slt2 MAPK (cell wall integrity pathway) 在 NTF trap formation 中的保守作用
- **Li et al. 2007** — Filamentous fungi 中 heterotrimeric G protein signaling 的综述
- **Mehrabi et al. 2009** — Plant pathogenic fungi 中 cAMP signaling 和 MAP kinase pathways 的综述
- **Borges-Walmsley and Walmsley 2000** — Pathogenic fungi 中 cAMP signalling 控制 dimorphic switching 和 pathogenicity
