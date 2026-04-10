# Jumper et al. 2021 — 文献总结

> **完整标题**: Highly accurate protein structure prediction with AlphaFold
> **期刊**: *Nature*, Vol. 596, pp. 583–589, 26 August 2021
> **DOI**: https://doi.org/10.1038/s41586-021-03819-2
> **作者**: John Jumper†, Richard Evans†, Alexander Pritzel†, Tim Green, Michael Figurnov, Olaf Ronneberger, Kathryn Tunyasuvunakool, Russ Bates, Augustin Žídek, Anna Potapenko, Alex Bridgland, Clemens Meyer, Simon A. A. Kohl, Andrew J. Ballard, Andrew Cowie, Bernardino Romera-Paredes, Stanislav Nikolov, Rishub Jain, Jonas Adler, Trevor Back, Stig Petersen, David Reiman, Ellen Clancy, Michal Zielinski, Martin Steinegger, Michalina Pacholska, Tamas Berghammer, Sebastian Bodenstein, David Silver, Oriol Vinyals, Andrew W. Senior, Koray Kavukcuoglu, Pushmeet Kohli, Demis Hassabis
> （† 同等贡献）
> **机构**: DeepMind, London, UK；首尔国立大学生命科学学院（部分作者）

---

## 核心发现（5–10 bullets，含数据）

- **原子精度结构预测**: AlphaFold2 是首个能在绝大多数情况下以接近实验精度预测蛋白质三维结构的计算方法，在无同源结构时同样适用。
- **CASP14 竞赛压倒性胜出**: 在第 14 届 CASP（Critical Assessment of protein Structure Prediction, 2020）评估中，AlphaFold2 的中位骨架精度（C-α RMSD）为 **0.96 Å**（95% 置信区间 0.85–1.16 Å），而最优竞争方法为 **2.8 Å**；全原子精度（GDT_TS）中位数 **92.4**（满分100），竞争者约 **75**。
- **Free-modelling 类别** (无同源结构): CASP14 目标集中，AlphaFold2 中位 C-α RMSD 仅 **1.5 Å**，同等情况下竞争方法为 **5.1 Å**，领先三倍以上。
- **近期 PDB 结构验证**: 在对 2021 年 PDB 中公开的蛋白质（与训练集无重叠）测试时，中位 C-α RMSD 为 **1.46 Å**（全原子精度 87.0 GDT_TS），结果接近实验误差范围。
- **Evoformer 架构**: 网络核心为全新的 Evoformer 模块——将 multiple sequence alignment (MSA) 和氨基酸残基对（pair representation）联合迭代更新，通过三角形乘积更新（triangle multiplicative update）和三角形自注意力（triangle self-attention）在 48 个共享权重 block 中反复精炼，使序列进化信息与空间约束信息充分融合。
- **Structure Module（结构模块）**: 以不变点注意力（Invariant Point Attention, IPA）为核心，在具体三维骨架坐标上直接操作，并以 FAPE（Frame Aligned Point Error）损失函数监督，每个残基预测其局部刚体坐标框架（backbone frame）后再预测侧链二面角。
- **自蒸馏与无标注数据**: 训练策略结合有监督（PDB 实验结构）和自蒸馏——用初始模型对 **350,000 个** UniRef90 序列预测结构，筛选高置信度（pLDDT > 0.7）预测后加入训练集（noisy student self-distillation），显著提高精度。
- **pLDDT 可靠性估计**: 网络输出每残基置信度分数（predicted local distance difference test, pLDDT），与真实 lDDT-Cα 高度相关，可用于识别无序区域及预测质量；此外还输出 predicted aligned error (PAE) 用于评估结构域间相对方向的置信度。
- **侧链与 cross-chain 接触精度**: 在 CASP14 测试集中，侧链准确性远超历史最优方法；对于拥有少量 intra-chain 同源接触的蛋白质（每链 <30 个），仍能准确预测，解决了长期存在的结构域-结构关联难题。
- **单 GPU 推理效率**: 推理中位耗时约 4 分钟（256 残基，单 GPU A100）；训练则需要大量 TPU 资源，模型参数约 93M。

---

## 实验方法（表格）

| 方法/步骤 | 说明 |
|-----------|------|
| **输入** | 氨基酸序列 → 生成 MSA（使用 UniRef90/BFD/MGnify 数据库）+ 模板结构（PDB70/HHsearch） |
| **MSA 构建** | HHblits（UniRef30/BFD）+ HHSearch（PDB70）；MSA 搜索时还使用了 UniClust30 和 MGnify |
| **Evoformer 模块** | 48 个 block，共享权重；输入 MSA representation（N_seq × N_res × c_m）和 pair representation（N_res × N_res × c_z）；执行行/列 gated self-attention、triangle multiplicative update、triangle self-attention 等操作 |
| **Structure Module** | 8 个 block；IPA（Invariant Point Attention）在三维骨架坐标上操作；输出骨架 rigid body（旋转+平移）+ 侧链扭角；最终以 Amber99sb 力场做约束弛豫 |
| **损失函数** | FAPE（backbone & side-chain）+ 扭角损失 + distogram 头（CB距离分布）+ MSA masked prediction + pLDDT 头 |
| **训练数据** | PDB（截至 2021-04-30）; 40% 序列相似度聚类去冗余；自蒸馏：350,000 条 UniRef90 序列（pLDDT>0.7 筛选）；模板截止日期：2018-05-14 |
| **训练框架** | TensorFlow v1 + Sonnet v1；XLA 编译（JAX v0.1.69 + Haiku v0.0.4）；TPU 集群 |
| **评估基准** | CASP14（97个域）；近期 PDB 测试集（2021-04-30 后，去冗余，≤1400 残基，无 NMR/未知残基）|
| **结构验证** | RMSD、GDT_TS、lDDT-Cα、IDDT-Ca、TM-score（TM-align）；侧链用 FAPE 量化 |
| **Amber 弛豫** | OpenMM v7.3.1 + Amber99sb 力场，消除键长/键角违规，不显著改变 GDT 精度 |

---

## 关键数据（分小节）

### CASP14 整体性能
- AlphaFold2 在 CASP14 自由建模类（TBM-hard + FM）目标上 median C-α RMSD = **0.96 Å**（竞争对手 ~2.8 Å）
- GDT_TS 中位数 **92.4**（竞争对手 ~75；人工精化后的结构中位 ~87）
- 在全部 97 个 CASP14 域中，AlphaFold2 有 **87%** 的结构与实验结构相差 < 2 Å RMSD

### 近期 PDB 测试集（2021年，独立）
- **30,791 条** PDB 链（过滤后），中位 C-α RMSD = **1.46 Å**，GDT_TS = **87.0**
- pLDDT 与真实 lDDT-Cα 的相关性在独立测试集中得到验证

### MSA 深度的影响
- MSA 深度从 1（单序列）增加到数百时，精度显著提升；但 MSA 非常深时（>512行），边际收益递减
- 移除 MSA（单序列）精度大幅下降，证明进化信息的关键作用

### 模板的贡献
- 加入同源结构模板整体提高约 **1.1 GDT**（95% CI）；无同源模板时 AlphaFold2 仍能高精度预测（free-modeling）

### Evoformer 循环迭代（recycling）
- 全网络输出反复循环 **3 次**（recycling），每次精炼结构，最终精度比单次推理显著提高

### 置信度估计
- 网络输出的 pLDDT 分数在测试集上与真实 lDDT-Cα 的相关性高；pLDDT < 50 的区域通常为内在无序区（intrinsically disordered regions）

---

## 与项目的关系

本项目（iGEM 2026 干实验）使用 **AlphaFold3**（AlphaFold2 的继承版本）预测真菌 G 蛋白偶联受体（GPCR）GprC 和 Gpr3 的三维结构，作为分子对接（AutoDock Vina 两阶段流程）的受体输入。

Jumper et al. 2021 的核心意义：

1. **结构来源的理论依据**: 项目中用于对接的受体 PDBQT 文件来自 AlphaFold 预测结构；本文奠定了 AlphaFold 方法的准确性基础（CASP14 中位 RMSD 0.96 Å），为使用预测结构代替实验结构提供了文献支持。
2. **pLDDT 用于结构质量评估**: 项目中 GprC/Gpr3 结构的质量评估可引用 pLDDT 作为残基级可靠性指标，特别是对接 binding pocket 区域的 pLDDT 值用于判断预测可信度。
3. **无实验结构时的适用性**: GprC 和 Gpr3 均无实验解析的晶体结构，AlphaFold 的 free-modeling 能力（无同源结构时仍 RMSD 1.5 Å）为本项目提供了方法合理性支撑。
4. **Amber 弛豫步骤**: 本文描述的 Amber99sb 最终弛豫步骤（消除键长/键角违规而不显著改变 GDT）与项目 ADFR/ADFRsuite 受体准备中的结构预处理在逻辑上一致。

> 注意：项目中的对接结果（ΔG、IFP、Δ值等）为项目自身数据，不属于本文内容，不在此总结中呈现。

---

## 关键引用（来自原文参考文献列表）

1. **Berman et al. 2000** — Protein Data Bank (PDB)：训练和评估数据的来源，约100,000条已知蛋白质三维结构。
2. **Moult et al. 2020** — CASP14 竞赛综述，*Proteins*：提供 AlphaFold2 性能评估的标准基准框架。
3. **Senior et al. 2020** (*Nature*) — AlphaFold1（前版本），使用 distance map 预测，奠定深度学习在蛋白质折叠中的基础。
4. **Vaswani et al. 2017** — "Attention is All You Need"：Transformer/自注意力架构，是 Evoformer 设计的理论基础。
5. **Steinegger & Söding 2017** — MMseqs2，*Nat. Methods*：AlphaFold2 中用于大规模 MSA 搜索和序列聚类的核心工具。
6. **Remmert et al. 2012** — HHblits，*Nat. Methods*：AlphaFold2 MSA 构建的核心同源搜索工具。
7. **Maier et al. 2015** — ff14SB Amber 力场；本文使用 Amber99sb 做最终结构弛豫，相关方法学基础。
8. **Altschul et al. 1997** — PSI-BLAST：序列比对与 MSA 构建的经典方法，AlphaFold2 所替代的传统路径之一。
