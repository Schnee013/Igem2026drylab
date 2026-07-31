# 双/多突变 docking 核心文献来源

> Source: Crossref/OpenAlex API 去重结果，Europe PMC metadata/abstract/full text 复核，以及 DOI 官方落地页。
>
> As of: `2026-07-30`
>
> Allowed use: 支持组合空间控制、双配体负向设计、上位性分析、GPCR 验证和结构预测边界；不直接提供本项目数值阈值。
>
> Update trigger: 新来源会改变候选生成、结构比较、评分统计或实验 gate。

## 1. 检索与核验口径

检索围绕 computational saturation mutagenesis、iterative/combinatorial
mutagenesis、ligand specificity/negative design、protein epistasis、GPCR
directed evolution、missense structure prediction 和 low-N protein engineering
展开。

本账本只收敛会直接改变执行计划的核心来源，不把临时检索池全部搬入长期文档。
DOI、标题、作者和年份先按 Crossref/OpenAlex 对齐，再用 Europe PMC
metadata/abstract 或可用全文核对项目所引结论。机器可读字段见
[literature-sources.csv](literature-sources.csv)。

核验层级：

- `full_text`：已直接核对正文中的方法或数字；
- `abstract_and_metadata`：已核对 DOI 元数据与摘要；
- `metadata_title_scope`：只用题名/文类界定风险，不引用正文数值。

## 2. 核心来源

### L01 — 计算饱和突变、docking 与分阶段缩库

Federica Chiappori, Pasqualina D'Ursi, Ivan Merelli, Luciano Milanesi,
Ermanna Rovida (2009). *In silico saturation mutagenesis and docking screening
for the analysis of protein-ligand interaction: the Endothelial Protein C
Receptor case study*. BMC Bioinformatics.
[DOI](https://doi.org/10.1186/1471-2105-10-S12-S3) ·
[Europe PMC full text](https://europepmc.org/articles/PMC2762068)

- 核验：`full_text`。
- 原研究从 27 个位点生成 513 个单突变模型；docking 阶段保留 43 个 substitution，
  组合生成 797 个双突变，docking filter 保留 212 个，完整筛选最终收敛到 12 个
  单突变和 17 个双突变。
- 项目用途：支持“先单突变缩库，再有限双突变组合，再过稳定性 gate”。
- 不支持：把其 Ki/FoldX cutoff 或成本直接移植到本项目。

### L02 — 同时优化目标 ligand 并抑制 decoy ligand

Hossein Fazelinia, Patrick C. Cirino, Costas D. Maranas (2007).
*Extending Iterative Protein Redesign and Optimization (IPRO) in Protein
Library Design for Ligand Specificity*. Biophysical Journal.
[DOI](https://doi.org/10.1529/biophysj.106.096016)

- 核验：`abstract_and_metadata`。
- 摘要把 desired ligand 的 binding energy 优化与 decoy ligand 的显式约束放入
  同一框架。
- 项目用途：支持 ASCR18/ASCR3 同时进入每个 genotype 的负向设计与 Pareto gate。
- 不支持：把 IPRO 能量函数视为 Vina 分数校准。

### L03 — 小 site、迭代组合，而非一次穷举

Manfred T. Reetz, José Daniel Carballeira (2007).
*Iterative saturation mutagenesis (ISM) for rapid directed evolution of
functional enzymes*. Nature Protocols.
[DOI](https://doi.org/10.1038/nprot.2007.72)

- 核验：`abstract_and_metadata`。
- 摘要定义的 rational site 由 1、2 或 3 个 amino-acid positions 组成，并按轮次
  迭代饱和突变。
- 项目用途：支持首轮只跑少数预注册双位点，结果回流后再决定是否扩展。
- 不支持：在没有实验标签时直接进入三位点或全空间组合。

### L04 — 组合效应不能由单突变简单相加

Tyler N. Starr, Joseph W. Thornton (2016).
*Epistasis in protein evolution*. Protein Science.
[DOI](https://doi.org/10.1002/pro.2897)

- 核验：`abstract_and_metadata`。
- 综述说明直接/间接物理相互作用可非加和地改变构象、稳定性和 ligand affinity。
- 项目用途：支持 `WT / A / B / AB` 四元周期和显式非加和 contrast。
- 不支持：把 docking-derived `εsel_score` 称为实验热力学 coupling energy。

### L05 — GPCR 多个小贡献与正交表型

Casim A. Sarkar et al. (2008).
*Directed evolution of a G protein-coupled receptor for expression, stability,
and binding selectivity*. Proceedings of the National Academy of Sciences.
[DOI](https://doi.org/10.1073/pnas.0803103105)

- 核验：`abstract_and_metadata`。
- 摘要报告 GPCR 功能表达、稳定性和 binding selectivity 的联合定向进化，并指出
  改进来自多个小贡献。
- 项目用途：支持多突变假说，同时把 expression/stability 与 ligand response
  分开设置 gate。
- 不支持：仅凭结构或 docking 分数断言细胞功能改善。

### L06 — GPCR ligand specificity 的筛选与跨体系验证

Blaine N. Armbruster, Xiang Li, Mark H. Pausch, Stefan Herlitze,
Bryan L. Roth (2007). *Evolving the lock to fit the key to create a family of
G protein-coupled receptors potently activated by an inert ligand*.
Proceedings of the National Academy of Sciences.
[DOI](https://doi.org/10.1073/pnas.0700293104)

- 核验：`abstract_and_metadata`。
- 原研究先在 yeast 中筛选受体，再在人细胞体系继续筛选和验证。
- 项目用途：支持把计算、酵母表达/功能筛选和下游验证视为不同证据层。
- 不支持：把单一体系结果外推为所有表达体系中的 receptor function。

### L07 — AlphaFold missense 结构敏感性风险

Gwen R. Buel, Kylie J. Walters (2022).
*Can AlphaFold2 predict the impact of missense mutations on structure?*
Nature Structural & Molecular Biology.
[DOI](https://doi.org/10.1038/s41594-021-00714-2)

- 核验：`metadata_title_scope`。
- 项目用途：把独立 AF3 结构限定为 starting-structure sensitivity；matched-backbone
  保留为主比较。
- 不支持：据此给出 AF3 在本项目中的数值误差。

### L08 — low-N ML 必须建立在真实功能标签上

Surojit Biswas, Grigory Khimulya, Ethan C. Alley, Kevin M. Esvelt,
George M. Church (2021). *Low-N protein engineering with data-efficient deep
learning*. Nature Methods.
[DOI](https://doi.org/10.1038/s41592-021-01100-y)

- 核验：`abstract_and_metadata`。
- 摘要以少量已功能测定 mutant sequences 监督模型，再做大规模 in silico 筛选。
- 项目用途：作为未来获得真实 expression/response 标签后的扩展路线。
- 不支持：用当前 Vina 分数代替功能标签直接训练多突变模型。

## 3. 对当前计划的约束

1. 先修复单突变 frame 和重建 shortlist，再生成 AB；
2. 单突变只负责缩小组合空间，AB 必须单独计算；
3. 每个双突变保留 `WT / A / B / AB`；
4. target 与 off-target ligand 同时计算；
5. 稳定性、pose/IFP 和功能实验是独立 gate；
6. 先双突变小批次，不做三突变和全组合穷举；
7. AF3 是敏感性路线，独立模型不作为 matched replicate；
8. low-N ML 需要真实功能标签和独立留出验证。
