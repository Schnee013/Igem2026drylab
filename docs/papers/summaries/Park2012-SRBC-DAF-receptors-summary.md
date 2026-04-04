# Park et al. 2012 — 文献总结

> **完整标题**: Interaction of structure-specific and promiscuous G-protein-coupled receptors mediates small-molecule signaling in *Caenorhabditis elegans*
> **期刊**: PNAS, vol. 109, no. 25, pp. 9917–9922
> **DOI**: 10.1073/pnas.1202216109
> **发表日期**: June 19, 2012

## 核心发现

- **首次鉴定 ascaroside 受体 DAF-37 和 DAF-38**: 通过 DAF-8 免疫共沉淀发现两个未知 GPCR，命名为 DAF-37 和 DAF-38，它们协同介导 ascaroside 感知
- **DAF-37 是 ascr#2 的结构特异性受体**: Photoaffinity labeling 和 AlphaScreen 实验直接证明 ascr#2 与 DAF-37 物理结合；DAF-37 属于 serpentine receptor class w 家族，编码 465 aa 的 GPCR
- **DAF-38 是混杂型 (promiscuous) 共受体**: DAF-38 与 human gonadotropin-releasing hormone receptor 同源，参与 ascr#2 及其他多种 ascarosides 的感知，但非结构特异性
- **DAF-37/DAF-38 形成异源二聚体 (heterodimer)**: Pb-FRET 分析显示两者在 HEK293 细胞中形成预组装的异源二聚体，ascr#2 处理后二聚化增强
- **异源二聚化对信号转导至关重要**: 仅 DAF-37/DAF-38 共转染细胞在 ascr#2 处理后显著抑制 forskolin 诱导的 cAMP 产生；单独转染无显著效应
- **同一受体在不同神经元中介导不同表型**: DAF-37 在 ASI 神经元中调控 dauer formation（幼虫），在 ASK 神经元中调控 hermaphrodite repulsion（成虫）
- **daf-37 突变体表型**: 对 ascr#2 的 dauer 诱导和雄虫吸引完全缺失，但对 ascr#3 和 ascr#5 响应正常
- **daf-38 突变体表型**: 对多种 ascarosides（ascr#2, ascr#3, ascr#5）的响应部分降低，提示其与多种受体配合

## 实验方法

| 方法 | 用途 |
|------|------|
| **Co-immunoprecipitation (Co-IP)** | 通过 DAF-8 (SMAD/TGF-beta pathway component) 拉下互作蛋白，发现 DAF-37/38 |
| **Dauer formation assay** | 用不同浓度 ascr#2/3/5/8 处理 L1 幼虫，量化 dauer 形成率 |
| **Male attraction assay** | 评估 *him-5* 雄虫对 ascarosides 的趋化行为 |
| **Hermaphrodite repulsion assay** | 评估成虫对 ascaroside 混合物的排斥行为 |
| **Photoaffinity labeling** | 合成含 trifluorodiazirine photo-crosslinker 和 alkyne click handle 的 ascr#2 probe，光交联后与 biotin-azide 偶联，证明与 DAF-37 直接结合 |
| **AlphaScreen (amplified luminescence proximity assay)** | 在 HEK293T 细胞中用 biotinylated ascr#2 probe 与 1D4-tagged DAF-37 共定位，luminescence 信号证实直接结合 |
| **Pb-FRET (photobleaching FRET)** | HEK293 细胞中 cMyc-DAF-37 (FITC) 和 HA-DAF-38 (Cy3) 共转染，测定 FRET efficiency 证实异源二聚化 |
| **Co-immunoprecipitation (Co-IP) of heterodimers** | cMyc-DAF-37 + HA-DAF-38 共转染后 IP，Western blot 检测 ~110 kDa 异源二聚体条带 |
| **cAMP inhibition assay** | 稳定转染 HEK293 细胞中测量 forskolin 诱导的 cAMP 水平变化 |
| **Cell-specific rescue/overexpression** | 用 ASI-specific (*gpa-4*) 和 ASK-specific (*srbc-64*) promoter 驱动 *daf-37* 表达，分离不同神经元的功能 |
| **Promoter-GFP/dsRED reporter** | 确定 *daf-37* 和 *daf-38* 的表达模式：ASI, ASK, IL-2 神经元 |
| **Genetic epistasis** | *daf-37* 与 *daf-11*/guanylyl cyclase, *daf-7*/TGF-beta, *daf-2*/insulin 通路的双突变分析 |

## 关键数据

### Receptor-ligand 特异性
- **DAF-37**: 对 ascr#2 高度特异——*daf-37* 突变体对 ascr#2 的 dauer 诱导完全丧失，但对 ascr#3 和 ascr#5 响应与 WT 相同
- **DAF-38**: 混杂型——*daf-38* 突变体对 ascr#2 的 dauer 诱导反而增强（可能因信号通路补偿），对 ascr#3 和 ascr#5 响应降低

### Dauer formation 定量
- WT: ascr#2 (700 nM) 诱导 ~60% dauer；*daf-37* 突变体: ~0%
- DAF-37 过表达 (*mIs41[daf-37p::cMyc::daf-37]*) 在 *daf-37* 背景下: ascr#2 浓度低至 1 nM 即可诱导 >50% dauer（WT 在此浓度仅 <3%）
- Dose-response curve 显示 *daf-37* 过表达使 ascr#2 敏感性提高约 100 倍

### Pb-FRET 效率
- DAF-37 homodimer: 15.4 +/- 0.5% relative Pb-FRET efficiency
- DAF-37/DAF-38 heterodimer: 18.3 +/- 0.8%
- ascr#2 处理后 heterodimer 的 FRET efficiency 小幅增加
- 阴性对照 (DAF-37/rhodopsin, DAF-37/SST5CR1): 仅 2-3%

### cAMP 抑制
- DAF-37 单独转染 + ascr#2: 几乎无 cAMP 抑制
- DAF-37 + DAF-38 共转染 + 100 nM ascr#2: 显著抑制 cAMP（~10-15%）
- 500 nM ascr#2 反而抑制效果降低（可能因高浓度干扰受体构象）

### 信号通路定位
- *daf-37* 功能位于 *daf-11*/guanylyl cyclase 上游
- *daf-37* 功能位于 *daf-7*/TGF-beta 和 *daf-2*/insulin 信号上游
- *daf-10* (intraflagellar transport) 突变抑制了 DAF-37 过表达的 dauer 诱导，确认 DAF-37 在 sensory cilia 中发挥功能

## 与项目的关系

### SRBC-64/66, DAF-37/38 受体鉴定
- 本文是 **首篇鉴定 ascaroside GPCR 受体的论文**，建立了 DAF-37 (structure-specific) + DAF-38 (promiscuous) 的受体模型
- 论文同时讨论了 *srbc-64/66* 和 *srg-36/37* 等其他 GPCR 的角色：*srbc-64/66* 突变体仅部分影响 dauer 诱导，功能弱于 *daf-37*；*srg-36/37* 对 ascr#5 特异
- 提出 ascaroside 信号可能由 structure-specific receptors (如 DAF-37, SRG-36/37) 与 promiscuous receptors (如 DAF-38, SRBC-64/66) 的组合实现

### Hu 2024 chimeric receptor 设计的基础
- Hu et al. 2024 的 GprC chimeric receptor 实验直接建立在本文发现之上：DAF-37 的 ascr#2 结合特异性和 GPCR 二聚化机制为跨物种 chimeric receptor 设计提供了结构基础
- 本文证明 DAF-37 可在哺乳动物细胞 (HEK293) 中异源表达并保持功能，这为 chimeric receptor 在异源系统中的可行性提供了关键先例

### 跨物种受体比较与 molecular docking
- DAF-37: serpentine receptor class w 家族，465 aa，*C. elegans* 特有的化学感受器家族大规模扩张的一员
- DAF-38: 与 human gonadotropin-releasing hormone receptor 同源
- 两种受体属于不同 GPCR 家族却形成功能性异源二聚体——这对跨物种 molecular docking 建模有重要启示：需要考虑二聚体界面而非仅单体结构
- Pb-FRET 数据提供了 heterodimer 形成的定量参考

### Ascarosides 的结构-活性关系
- ascr#2 (ascarosyl unit + short fatty acid side chain) 是最强的 dauer 诱导剂之一
- 不同 ascarosides 的微小结构变化导致完全不同的受体特异性：ascr#2 -> DAF-37; ascr#5 -> SRG-36/37
- Photoaffinity probe 设计表明 ascr#2 的 ascarosyl sugar moiety 是受体识别的关键，side chain 可容忍 bulky modifications（trifluorodiazirine + alkyne）而不完全丧失活性

## 关键引用

- **Butcher et al. 2007** (ref 2): 首次鉴定 dauer pheromone 的化学组成为 ascarosides
- **Srinivasan et al. 2008** (ref 5): ascaroside 混合物调控 mating 和 development 的协同效应
- **Kim et al. 2009** (ref 17): *srbc-64/66* 和 *srg-36/37* 在 ascaroside-mediated dauer 中的作用（本文的直接前驱工作）
- **Birnby et al. 2000** (ref 14): *daf-11*/guanylyl cyclase 在 dauer 信号通路中的定位
- **Jensen & Bhatt 2020 / Thomas & Robertson 2008** (ref 20): *C. elegans* chemoreceptor 家族的大规模进化扩张
- **Bulenger et al. 2005** (ref 32): GPCR homo- and heterodimerization 的综述
- **Hashimoto & Hatanaka 2008** (ref 25): diazirine-based photoaffinity labeling 技术
