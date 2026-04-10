# iGEM 2026 干实验文献查阅文档
> 55 篇本地 PDF | 56 篇已总结 | Tier 1-6 分层 | 更新: 2026-04-10
> 快速查阅表见 literature-quick-ref.csv，可直接插入飞书表格
---
## 目录
- **Tier 1** 核心受体-配体研究（19篇）— GprC/Gpr2/Gpr3 受体、ascaroside 对接、NTF 信号通路
- **Tier 2** *C. elegans* ascaroside 受体（3篇）— 嵌合设计上游文献
- **Tier 3** Ascaroside 生物学（13篇）— 化学、植物防御、受体、代谢
- **Tier 4** 酵母 GPCR 异源表达（13篇）— GPR/Gpa1 偶联改造 | 下游通路改造 | 显色物质/输出
- **Tier 5** iGEM 历史项目（9个）— 方法参考
- **Tier 6** 方法学（8篇）— Vina、AlphaFold、IFP 分析
---
# Tier 1: 核心受体-配体研究
> 涵盖 GprC/Gpr2/Gpr3 受体鉴定、ascaroside 配体对接、NTF 信号通路组分与 ODE 建模参数。本项目分子对接直接复现 Hu2024 和 Kuo2024 的结果。
## Hu2024 | Hu et al. (2024) ★★★
**GprC of the nematode-trapping fungus *Arthrobotrys flagrans* activates mitochondria and reprograms fungal cells for nematode hunting**
- **期刊**: *Nature Microbiology* 9:1752–1763
- **说明**: 首次在 *A. flagrans* 中鉴定 GprC 作为 ascr#18 的 GPCR 受体。使用 AutoDock Vina 1.2.3 进行分子对接获得 25 poses，标注 BW 编号关键残基，通过 6 个 alanine 突变验证结合口袋。ΔgprC 突变体完全丧失 ascr#18 诱导的 trap formation。
- **项目关联**: **本项目分子对接的直接复现对象**。GprC×ascr#18 ΔG=-8.29 kcal/mol 是主要验证靶标（我们复现 Δ=0.05）；突变残基定义了 alanine scan 靶点；BW 编号体系是 IFP 交叉验证基础。
- **引用**: Hu Y et al. (2024) *Nat Microbiol* 9:1752–1763. [DOI: 10.1038/s41564-024-01731-9](https://doi.org/10.1038/s41564-024-01731-9)
## Kuo2024 | Kuo et al. (2024) ★★★
**The nematode-trapping fungus *Arthrobotrys oligospora* detects prey pheromones via G protein-coupled receptors**
- **期刊**: *Nature Microbiology* 9:1738–1751
- **说明**: 在 *A. oligospora* TWF154 中鉴定 Gpr2 和 Gpr3 作为 ascr#3 和 ascr#7 的受体。SwissDock 对接得到 ΔG 值（Gpr2×ascr#3=-6.99, Gpr3×ascr#3=-7.05），Y168 为关键结合残基。双突变体 ΔΔgpr2gpr3 对 ascaroside 完全无响应。
- **项目关联**: **Gpr2/Gpr3 对接的直接复现对象**。ΔG 值是 Vina vs SwissDock 方法对比基准；Y168 等残基用于 IFP 验证；受体序列是 AF3 结构预测输入。
- **引用**: Kuo CY et al. (2024) *Nat Microbiol* 9:1738–1751. [DOI: 10.1038/s41564-024-01679-w](https://doi.org/10.1038/s41564-024-01679-w)
## Hsueh2013 | Hsueh et al. (2013) ★★★
**Nematode-trapping fungi eavesdrop on nematode pheromones**
- **期刊**: *Current Biology* 23:83–86
- **说明**: **奠基性文献**。首次证明 *A. oligospora* 通过感知线虫 ascaroside（ascr#18 等）触发 trap morphogenesis，鉴定 Gpr2/Gpr3 为候选 GPCR。ΔΔgpr2gpr3 双突变体 trap 形成显著减少。
- **项目关联**: 定义了"NTF 窃听线虫信息素"的核心叙事框架；Gpr2/Gpr3 的首次鉴定为后续 Kuo2024 的深入研究奠定基础。
- **引用**: Hsueh YP et al. (2013) *Curr Biol* 23:83–86. [DOI: 10.1016/j.cub.2012.11.035](https://doi.org/10.1016/j.cub.2012.11.035)
## Chen2021 | Chen et al. (2021) ★★★
**Prey sensing and response in a nematode-trapping fungus is governed by the MAPK pheromone response pathway**
- **期刊**: *Genetics* 217(2):iyaa008
- **说明**: 揭示 Fus3 MAPK cascade（Ste11→Ste7→Fus3→Ste12）是 *A. oligospora* 感知线虫并启动 trap morphogenesis 的核心通路。Fus3 在 nematode induction 后 2h 和 4h 被磷酸化。ste7/fus3 突变体完全丧失 trap formation。
- **项目关联**: **ODE 建模直接参数来源**：Fus3 磷酸化时间序列（0/2/4/24/48h）可拟合 rate constants；通路拓扑 Gpr2/3→Gpb1→Ste11→Ste7→Fus3→Ste12 是 ODE 骨架。
- **引用**: Chen SA et al. (2021) *Genetics* 217(2):iyaa008. [DOI: 10.1093/genetics/iyaa008](https://doi.org/10.1093/genetics/iyaa008)
## Chen2022 | Chen et al. (2022) ★★★
**The cAMP-PKA pathway regulates prey sensing and trap morphogenesis in the nematode-trapping fungus *Arthrobotrys oligospora***
- **期刊**: *G3* 12(9):jkac217
- **说明**: 解析 cAMP-PKA 通路：Gpa2（Gα）→ adenylyl cyclase → cAMP → PKA 调控 trap 形态。cAMP 浓度变化在 nematode induction 后 2h 显著上升。双通路（MAPK + cAMP-PKA）平行调控。
- **项目关联**: **ODE 第二条通路**：Gpr2/Gpr3→Gpa2→cAMP→PKA 与 MAPK cascade 并行；cAMP 浓度动力学可作为 ODE 拟合靶标。
- **引用**: Chen SA et al. (2022) *G3* 12(9):jkac217. [DOI: 10.1093/g3journal/jkac217](https://doi.org/10.1093/g3journal/jkac217)
## Bai2022 | Bai et al. (2022) ★★★
**Ric8 acts as a regulator of G-protein signaling required for nematode-trapping lifecycle of *Arthrobotrys oligospora***
- **期刊**: *Environmental Microbiology* 24:1714–1730
- **说明**: 鉴定 AoRic8（非受体 GEF）选择性与 AoGα1 互作，激活 adenylyl cyclase→cAMP/PKA→Som1/StuA 轴。ΔAoric8 突变体 trap formation 完全丧失，cAMP 仅 52–97.5 fmol/mL vs WT 最高 1,740 fmol/mL。
- **项目关联**: **ODE 关键节点**：AoRic8→AoGα1 的 GEF 活性约束 Gα 激活动力学参数；WT 线虫捕获时程数据（14.3%→88.6%，12–48 hpi）可作 ODE 拟合参考。
- **引用**: Bai N et al. (2022) *Environ Microbiol* 24:1714–1730. [DOI: 10.1111/1462-2920.15735](https://doi.org/10.1111/1462-2920.15735)
## Ma2021 | Ma et al. (2021) ★★☆
**Functional analysis of seven regulators of G protein signaling (RGSs) in the nematode-trapping fungus *Arthrobotrys oligospora***
- **期刊**: *Virulence* 12(1):1825–1840
- **说明**: 系统分析 *A. oligospora* 的 7 个 RGS 基因，负调控 G 蛋白信号→cAMP 通路。不同 RGS 对 trap formation、生长和 conidiation 有差异化调控。
- **项目关联**: ODE 负反馈组件：RGS 提供 G 蛋白信号关闭的速率常数约束。
- **引用**: Ma N et al. (2021) *Virulence* 12(1):1825–1840. [DOI: 10.1080/21505594.2021.1948667](https://doi.org/10.1080/21505594.2021.1948667)
## Kuo2026 | Kuo et al. (2026) ★★☆
**A nematode-trapping fungus orchestrates polarity cues, septins, and NOX signaling for trap formation**
- **期刊**: bioRxiv preprint
- **说明**: 系统阐明 *A. oligospora* trap morphogenesis 中极性信号、septins 和 NOX/ROS 三模块的协调。Nox1 介导的 ROS 是 trap 环闭合的空间检查点：nox 突变体弯曲正常但 100% 无法融合。
- **项目关联**: **ODE 新节点**：Gpr2/Gpr3→MAPK→Nox1→ROS→融合 扩展模块；时间节点数据（200/230/240 mpe，4 hpe）可校准时间常数。
- **引用**: Kuo CY et al. (2026) bioRxiv. [DOI: 10.64898/2026.03.09.710510](https://doi.org/10.64898/2026.03.09.710510)
## Juan2026 | Juan et al. (2026) ★★☆
**Ammonium Transporters Govern Nutrient Sensing and Trap Induction in the Nematode-Trapping Fungi *Arthrobotrys oligospora***
- **期刊**: bioRxiv preprint
- **说明**: 鉴定 Mep1/Mep3 铵转运体介导氮感知，mep 突变体 trap 数量减少约 50%。关键结论：**氮感知与 ascaroside-GPCR 感知是两条并行独立输入**。
- **项目关联**: **ODE 建模约束**：两个输入节点（Mep 铵 vs Gpr2/3 ascaroside）不应在上游合并。
- **引用**: Juan SC et al. (2026) bioRxiv. [DOI: 10.64898/2026.02.06.704490](https://doi.org/10.64898/2026.02.06.704490)
## Huang2023a | Huang et al. (2023) ★★☆
**Ammonia and Nematode Ascaroside Are Synergistic in Trap Formation in *Arthrobotrys oligospora***
- **期刊**: *Pathogens* 12(9):1114
- **说明**: ascr#18（10 nM）+ 氨混合处理协同最强（~140 traps/cm² vs 单独各约 50）。Amt43 是主要氨转运蛋白，但 ascr#18 感知通路独立于 Amt43。
- **项目关联**: 进一步支持 GPCR（Gpr2/Gpr3）作为 ascr#18 专属受体通路。
- **引用**: Huang TY et al. (2023) *Pathogens* 12(9):1114. [DOI: 10.3390/pathogens12091114](https://doi.org/10.3390/pathogens12091114)
## Heinen2025 | Heinen et al. (2025) ★★☆
**The rise of fungal G-protein coupled receptors in pathogenesis and symbiosis**
- **期刊**: *PLoS Pathogens*
- **说明**: 真菌 GPCR 综述。指出真菌 GPCR 目前无实验结构，计算对接是研究配体结合的唯一途径，直接验证了本项目方法的必要性。
- **项目关联**: wiki 中引用以论证"为何选择 computational docking"。
- **引用**: Heinen PR et al. (2025) *PLoS Pathog*. PMID: 40504784
## Jiang2024 | Jiang et al. (2024) ★★☆
**Sensing host and environmental cues by fungal GPCRs**
- **期刊**: *Current Opinion in Plant Biology* 82:102667
- **说明**: 系统分类真菌 GPCR 家族（Class I–IX），确认 Gpr2/Gpr3 和 GprC 的家族归属与系统发育位置。
- **项目关联**: 确认受体分类归属，wiki 背景介绍引用。
- **引用**: Jiang Y et al. (2024) *Curr Opin Plant Biol* 82:102667. [DOI: 10.1016/j.pbi.2024.102667](https://doi.org/10.1016/j.pbi.2024.102667)
## Lin2023 | Lin et al. (2023) ★★☆
**Key processes required for the different stages of fungal carnivory by a nematode-trapping fungus**
- **期刊**: *PLoS Biology* 21(12):e3002400
- **说明**: *A. oligospora* 暴露于 *C. elegans* 后 2–48 hpe 全转录组时间课程。三阶段：感知/trap 形成（TOR + DNA 复制）→ trap 功能（分泌组 50.6% DEG）→ 消化（119 个蛋白酶 DEG）。
- **项目关联**: 受体感知（GprC/Gpr2/Gpr3 所在层）触发后的完整下游应答背景，是项目叙事核心参考框架。
- **引用**: Lin HC et al. (2023) *PLoS Biol* 21(12):e3002400. [DOI: 10.1371/journal.pbio.3002400](https://doi.org/10.1371/journal.pbio.3002400)
## Yang2020 | Yang et al. (2020) ★★☆
**Natural diversity in the predatory behavior facilitates the establishment of a robust model strain for nematode-trapping fungi**
- **期刊**: *PNAS* 117(12):6762–6770
- **说明**: 从 38 株野生 *A. oligospora* 中筛选出高性能模式菌株 TWF154（trap ~145个 vs ATCC24927 ~7个）。Gpb1 敲除验证 GPCR 假说。基因组 BUSCO 97.7%。
- **项目关联**: TWF154 是 Kuo2024 的宿主背景菌株；Gpb1→GPCR 假说为后续受体鉴定提供遗传框架。
- **引用**: Yang CT et al. (2020) *PNAS* 117(12):6762–6770. [DOI: 10.1073/pnas.1919726117](https://doi.org/10.1073/pnas.1919726117)
## Hsueh2017 | Hsueh et al. (2017) ★☆☆
**Nematophagous fungus *Arthrobotrys oligospora* mimics olfactory cues of sex and food to lure its nematode prey**
- **期刊**: *eLife* 6:e20023
- **说明**: *A. oligospora* 产生 MMB（methyl 3-methyl-2-butenoate）模拟线虫食物/性信息素气味，通过 AWC 嗅觉神经元吸引 *C. elegans*。跨 10⁶ 浓度范围有效。
- **项目关联**: 构建"NTF 化学拟态"叙事框架——真菌主动引诱 + GPCR 被动感知构成双向化学对话。
- **引用**: Hsueh YP et al. (2017) *eLife* 6:e20023. [DOI: 10.7554/eLife.20023](https://doi.org/10.7554/eLife.20023)
## Youssar2019 | Youssar et al. (2019) ★☆☆
**Intercellular communication is required for trap formation in the nematode-trapping fungus *Duddingtonia flagrans***
- **期刊**: *PLoS Genetics* 15(3):e1008029
- **说明**: 在 *D. flagrans*（= *A. flagrans*）中证明细胞间通讯是 trap formation 必需条件。涉及 GprC 所在物种的信号机制背景。
- **项目关联**: GprC 所在物种的细胞通讯背景。
- **引用**: Youssar L et al. (2019) *PLoS Genet* 15(3):e1008029. [DOI: 10.1371/journal.pgen.1008029](https://doi.org/10.1371/journal.pgen.1008029)
## Wernet2021 | Wernet et al. (2021) ★☆☆
**The small-secreted cysteine-rich protein CyrA is a virulence factor participating in the attack of *Caenorhabditis elegans* by *Duddingtonia flagrans***
- **期刊**: *PLoS Pathogens* 17(12):e1010028
- **说明**: CyrA 是 *A. flagrans* 分泌的小蛋白毒力因子，参与攻击 *C. elegans*。Fischer 实验室体系。
- **项目关联**: 同属 Fischer 实验室 *A. flagrans* 侵染研究体系，叙事背景补充。
- **引用**: Wernet N et al. (2021) *PLoS Pathog* 17(12):e1010028. [DOI: 10.1371/journal.ppat.1010028](https://doi.org/10.1371/journal.ppat.1010028)
## Wernet2024 | Wernet et al. (2024) ★☆☆
**The cysteine-rich virulence factor NipA of *Arthrobotrys flagrans* interferes with cuticle integrity of *Caenorhabditis elegans***
- **期刊**: *Nature Communications* 15:5850
- **说明**: NipA（133 aa，EGF-like）在穿透位点分泌，干扰 *C. elegans* 角质层完整性。ΔnipA 穿透时间延长 64→78 min。
- **项目关联**: Fischer 实验室最新工作，代表"侵染执行"层面，与 GprC（化学感应层）功能互补。
- **引用**: Wernet N et al. (2024) *Nat Commun* 15:5850. [DOI: 10.1038/s41467-024-50096-4](https://doi.org/10.1038/s41467-024-50096-4)
## Duan2025 | Duan et al. (2025) ★☆☆
**Nutrient State-Dependent Ascarosides and Nematode Immune Response Limit the Predation of *Arthrobotrys oligospora***
- **期刊**: *Microorganisms* 13(12):2816
- **说明**: 饥饿线虫减少 ascaroside 分泌，降低被 NTF 捕获的概率。
- **项目关联**: 田间 ascaroside 浓度受线虫营养状态影响，为传感器灵敏度设计提供生态背景。
- **引用**: Duan YL et al. (2025) *Microorganisms* 13(12):2816. [DOI: 10.3390/microorganisms13122816](https://doi.org/10.3390/microorganisms13122816)
---
# Tier 2: *C. elegans* ascaroside 受体
> 线虫端的 ascaroside 受体鉴定，是 Hu2024 嵌合受体设计的上游文献基础。
## Park2012 | Park et al. (2012) ★★★
**Interaction of structure-specific and promiscuous G-protein-coupled receptors mediates small-molecule signaling in *Caenorhabditis elegans***
- **期刊**: *PNAS* 109(23):9236–9241
- **说明**: 首次鉴定 *C. elegans* 中 4 个 ascaroside 受体：SRBC-64/66（ASK 神经元）和 DAF-37/38（ASI 神经元）。SRBC-64/66 为 structure-specific 型，DAF-37/38 为 promiscuous 型。
- **项目关联**: **Hu2024 嵌合设计的直接基础**——Hu 将 SRBC-64/DAF-37 的配体结合域与真菌受体融合。
- **引用**: Park D et al. (2012) *PNAS* 109(23):9236–9241. [DOI: 10.1073/pnas.1202216109](https://doi.org/10.1073/pnas.1202216109)
## Kim2009 | Kim et al. (2009) ★★☆
**Two Chemoreceptors Mediate Developmental Effects of Dauer Pheromone in *C. elegans***
- **期刊**: *Science* 326(5955):994–998
- **说明**: 首次从分子水平鉴定 DAF-37/DAF-38 为 dauer pheromone 受体。两者须共表达才能在 HEK293 产生 cAMP 响应。信号通路：受体→GPA-3（Gαi）→抑制 DAF-11→cGMP 下降→dauer。
- **项目关联**: HEK293 异源表达成功支持在真菌底盘重建 ascaroside 感知通路的可行性。
- **引用**: Kim K et al. (2009) *Science* 326(5955):994–998. [DOI: 10.1126/science.1176331](https://doi.org/10.1126/science.1176331)
## McGrath2011 | McGrath et al. (2011) ★☆☆
**Parallel evolution of *Caenorhabditis elegans* species targets pheromone receptor genes**
- **期刊**: *Nature* 477:321–325
- **说明**: 发现 SRG-36/SRG-37 是 ascr#3 的直接受体，*C. elegans* 和 *C. briggsae* 独立进化出 srg 基因缺失导致 pheromone 抗性。
- **项目关联**: 平行进化的受体多样性为"NTF-线虫受体共进化"提供类比框架。
- **引用**: McGrath PT et al. (2011) *Nature* 477:321–325. [DOI: 10.1038/nature10378](https://doi.org/10.1038/nature10378)
---
# Tier 3: Ascaroside 生物学
> ascr#18 的化学背景、植物防御活性、跨界受体和代谢命运。为传感器设计和 HP（Human Practices）叙事提供支撑。
## Manosalva2015 | Manosalva et al. (2015) ★★★
**Conserved nematode signalling molecules elicit plant defenses and pathogen resistance**
- **期刊**: *Nature Communications* 6:7795
- **说明**: **HP 叙事核心**。首次证明 ascr#18 激活植物 MAPK 免疫通路（SA/JA 双通路），fmol 级即有效，在拟南芥/番茄/马铃薯/大麦中均诱导广谱抗性。
- **项目关联**: 定义了 ascr#18 的"跨界信号分子"身份——线虫信息素→植物免疫激活剂→NTF 捕陷器诱导物，是项目 HP 的核心叙事。
- **引用**: Manosalva P et al. (2015) *Nat Commun* 6:7795. [DOI: 10.1038/ncomms8795](https://doi.org/10.1038/ncomms8795)
## Ludewig2013 | Ludewig & Schroeder (2013) ★★★
**Ascaroside signaling in *C. elegans***
- **期刊**: *WormBook* (综述)
- **说明**: **必须引用**。Ascaroside 信号全景综述：化学结构（ascarylose + 脂肪酸侧链）、生物合成（β-oxidation）、受体通路、浓度依赖性行为调控。
- **项目关联**: 配体化学背景的权威综述，定义 ascr 命名体系和结构分类框架。
- **引用**: Ludewig AH, Schroeder FC (2013) *WormBook*. [DOI: 10.1895/wormbook.1.155.1](https://doi.org/10.1895/wormbook.1.155.1)
## Huang2023b | Huang et al. (2023) ★★☆
**NILR1 perceives a nematode ascaroside triggering immune signaling and resistance**
- **期刊**: *Current Biology* 33(18):3951–3962
- **说明**: 鉴定拟南芥 NILR1 为 ascr#18 的直接结合受体。ITC 实测 Kd=0.610±0.136 μM（约 1:1 结合）。ascr#2/ascr#3 不结合 NILR1。nilr1 功能缺失突变体丧失 ascr#18 免疫诱导。
- **项目关联**: Kd≈0.61 μM 是分子对接结合亲和力的实验参照基准；ascr#18 作为线虫信息素和植物 NAMP 的双重身份支撑跨界感知叙事。
- **引用**: Huang S et al. (2023) *Curr Biol* 33(18):3951–3962. [DOI: 10.1016/j.cub.2023.08.017](https://doi.org/10.1016/j.cub.2023.08.017)
## Huang2024 | Huang et al. (2024) ★★☆
**A receptor for dual ligands governs plant immunity and hormone response and is targeted by a nematode effector**
- **期刊**: *PNAS*
- **说明**: StNILR1 是双受体（同时结合 ascr#18 和 brassinolide）。ascr#18 Kd~1.79 μM。线虫效应蛋白可直接靶向 StNILR1 抑制免疫。
- **项目关联**: ascr#18 亲和力量级参考（μM 级），与对接 ΔG 换算一致性校验。
- **引用**: Huang S et al. (2024) *PNAS*. PMID: 查阅原文
## Klessig2019 | Klessig et al. (2019) ★★☆
**Nematode ascaroside enhances resistance in a broad spectrum of plant-pathogen systems**
- **期刊**: *Journal of Phytopathology* 167:265–272
- **说明**: ascr#18 在拟南芥-细菌、烟草-病毒、番茄-真菌等系统中均诱导广谱抗性。0.001–1 μM 范围有效。
- **项目关联**: ascr#18 田间应用可行性的生物活性支撑。
- **引用**: Klessig DF et al. (2019) *J Phytopathol* 167:265–272. [DOI: 10.1111/jph.12795](https://doi.org/10.1111/jph.12795)
## Choe2012 | Choe et al. (2012) ★★☆
**Ascaroside Signaling Is Widely Conserved among Nematodes**
- **期刊**: *Current Biology* 22(9):772–780
- **说明**: 证明 ascaroside 信号在线虫门广泛保守（超过 fpp 和 ppn 物种均产生 ascaroside），包括 PPN 也分泌 ascr#18。
- **项目关联**: 支持"ascr#18 是田间普遍存在的线虫信号"的前提假设。
- **引用**: Choe A et al. (2012) *Curr Biol* 22(9):772–780. [DOI: 10.1016/j.cub.2012.03.024](https://doi.org/10.1016/j.cub.2012.03.024)
## Dong2020 | Dong (Manohar) et al. (2020) ★★☆
**Plant metabolism of nematode pheromones mediates plant-nematode interactions**
- **期刊**: *Nature Communications* 11:208
- **说明**: 植物根系通过 peroxisomal β-oxidation 代谢 ascr#18（每轮去 2C：ascr#18→ascr#10→ascr#1→ascr#9）。ascr#18 根际半衰期约 0.5–3 小时。代谢产物 ascr#9 具独立驱线虫活性。
- **项目关联**: 传感器需考虑 ascr#18 在植物根际快速降解→有效浓度窗口短。
- **引用**: Manohar M et al. (2020) *Nat Commun* 11:208. [DOI: 10.1038/s41467-019-14104-2](https://doi.org/10.1038/s41467-019-14104-2)
## Letia2025 | Letia et al. (2025) ★☆☆
**Ascaroside#18 Promotes Plant Defence by Repressing Auxin Signalling**
- **期刊**: *Physiologia Plantarum* 177(1):e70386
- **说明**: ascr#18 通过下调 auxin 转运/信号基因（AUX1, GH3.6 等）抑制线虫取食位点发育。不依赖经典 PTI 或 NILR1。三浓度（0.001–1 μM）均有效。
- **项目关联**: ascr#18 植物侧最新机制，与真菌侧 GPCR 感知构成互补视角。
- **引用**: Letia I et al. (2025) *Physiol Plant* 177(1):e70386. [DOI: 10.1111/ppl.70386](https://doi.org/10.1111/ppl.70386)
## Kamboj2024 | Kamboj et al. (2024) ★☆☆
**The nematode signaling molecule ascr#18 induces prepenetration defenses in wheat against a leaf rust fungus**
- **期刊**: *Journal of Plant Diseases and Protection* 131:1803–1814
- **说明**: ascr#18 叶面喷施诱导小麦抗叶锈。四品种 uredinia 减少 70–81%（1 μM）。最低有效浓度 0.01 nM，剂量-响应跨 6 个数量级。
- **项目关联**: 田间极低浓度即有效→传感器检测限需匹配 nM–pM 量级。
- **引用**: Kamboj A et al. (2024) *J Plant Dis Prot* 131:1803–1814. [DOI: 10.1007/s41348-024-00950-w](https://doi.org/10.1007/s41348-024-00950-w)
## Mendy2017 | Mendy et al. (2017) ★☆☆
**Arabidopsis leucine-rich repeat receptor-like kinase NILR1 is required for induction of innate immunity to parasitic nematodes**
- **期刊**: *PLoS Pathogens* 13(4):e1006284
- **说明**: 鉴定 NILR1（LRR-RLK）为线虫 NAMP 感知的 PRR。nilr1 突变体对胞囊线虫和根结线虫均显著易感。依赖 BAK1 共受体。
- **项目关联**: 植物免疫 PRR 体系背景。
- **引用**: Mendy B et al. (2017) *PLoS Pathog* 13(4):e1006284. [DOI: 10.1371/journal.ppat.1006284](https://doi.org/10.1371/journal.ppat.1006284)
## Srinivasan2012 | Srinivasan et al. (2012) ★☆☆
**A Modular Library of Small Molecule Signals Regulates Social Behaviors in *Caenorhabditis elegans***
- **期刊**: *PLoS Biology* 10(1):e1001237
- **说明**: 利用 DANS（差异 2D-NMR）鉴定 5 种 indole ascaroside（icas#1/3/7/9/10）。ascr#3 在低浓度（fmol）引起吸引，高浓度（nmol-µmol）排斥。模块化化学语言框架。
- **项目关联**: ascr#3/ascr#7 化学骨架描述；浓度依赖性非线性响应对传感器动态范围设计有参考价值。
- **引用**: Srinivasan J et al. (2012) *PLoS Biol* 10(1):e1001237. [DOI: 10.1371/journal.pbio.1001237](https://doi.org/10.1371/journal.pbio.1001237)
## vonReuss2012 | von Reuss et al. (2012) ★☆☆
**Comparative Metabolomics Reveals Biogenesis of Ascarosides, a Modular Library of Small-Molecule Signals in *C. elegans***
- **期刊**: *JACS* 134(3):1817–1824
- **说明**: 利用比较代谢组学+β-oxidation 突变体揭示 ascaroside 生物合成通路：ACOX-1→MAOC-1→DHS-28→DAF-22。新鉴定 124 种 ascaroside。
- **项目关联**: ascr#18 的生物合成化学背景，模块化结构框架解释受体配体选择性。
- **引用**: von Reuss SH et al. (2012) *JACS* 134(3):1817–1824. [DOI: 10.1021/ja210202y](https://doi.org/10.1021/ja210202y)
## Zhao2016 | Zhao et al. (2016) ★☆☆
**Ascarosides coordinate the dispersal of a plant-parasitic nematode with the metamorphosis of its vector beetle**
- **期刊**: *Nature Communications* 7:12341
- **说明**: Ascaroside 协调松材线虫（PPN）与天牛的种间同步。PPN 产 ascaroside 的直接实证。
- **项目关联**: 支持"PPN 在田间释放 ascaroside"的生态假设。
- **引用**: Zhao L et al. (2016) *Nat Commun* 7:12341. [DOI: 10.1038/ncomms12341](https://doi.org/10.1038/ncomms12341)
---
# Tier 4: 酵母 GPCR 异源表达
> 酵母底盘设计三模块：受体偶联 → 信号放大 → 可读输出。本项目计划在酵母中异源表达 GprC/Gpr2/Gpr3 作为 ascaroside 生物传感器。
## Tier 4a: GPR/Gpa1 偶联改造
## Mukherjee2025 | Mukherjee et al. (2025) ★★★
**A yeast mating platform for multiplex screening of fungal GPCR-ligand interactions**
- **期刊**: *PNAS* 122(4):e2521198122
- **说明**: 利用酵母 mating pathway 高通量筛选真菌 GPCR-配体互作。成功偶联多个真菌 GPCR 并检测纳摩尔级配体响应。
- **项目关联**: **最高相关**——直接证明真菌 GPCR 可在酵母中功能性表达并偶联 mating pathway，与项目底盘设计方案高度吻合。
- **引用**: Mukherjee S et al. (2025) *PNAS* 122(4):e2521198122. [DOI: 10.1073/pnas.2521198122](https://doi.org/10.1073/pnas.2521198122)
## Lengger2020 | Lengger & Jensen (2020) ★★★
**Engineering G protein-coupled receptor signalling in yeast for biotechnological and medical purposes**
- **期刊**: *FEMS Yeast Research* 20(1):foz087
- **说明**: **底盘设计必读综述**。系统介绍酵母 GPCR 工程：受体表达优化、Gpa1 嵌合设计、报告基因体系、负反馈敲除策略。
- **项目关联**: 底盘设计的方法论蓝图。
- **引用**: Lengger B, Jensen MK (2020) *FEMS Yeast Res* 20(1):foz087. [DOI: 10.1093/femsyr/foz087](https://doi.org/10.1093/femsyr/foz087)
## Ladds2005 | Ladds et al. (2005) ★★☆
**Functional analysis of heterologous GPCR signalling pathways in yeast**
- **期刊**: *Trends in Biotechnology* 23(7):367–373
- **说明**: 酵母异源 GPCR 综述。>30 种 GPCRs 成功偶联。嵌合 Gα 设计原理。大分子配体效力约低 100 倍（细胞壁屏障）。
- **项目关联**: 嵌合 Gpa1 设计原理参考；细胞壁屏障提示 ascaroside（小分子）应无通透性问题。
- **引用**: Ladds G et al. (2005) *Trends Biotechnol* 23(7):367–373. [DOI: 10.1016/j.tibtech.2005.05.007](https://doi.org/10.1016/j.tibtech.2005.05.007)
## Medici1997 | Medici et al. (1997) ★★☆
**Efficient signal transduction by a chimeric yeast-mammalian G protein alpha subunit Gpa1-Gsα covalently fused to the yeast receptor Ste2**
- **期刊**: *EMBO Journal* 16(24):7241–7249
- **说明**: 嵌合 Gpa1-Gsα 的经典文献。证明 Gpa1 C-末端替换为哺乳动物 Gα 可实现功能性偶联。
- **项目关联**: 嵌合 Gpa1 设计策略的原始文献依据。
- **引用**: Medici R et al. (1997) *EMBO J* 16(24):7241–7249
## Brown2000 | Brown et al. (2000) ★★☆
**Functional coupling of mammalian receptors to the yeast mating pathway using novel yeast/mammalian G protein α-subunit chimeras**
- **期刊**: *Yeast* 16(1):11–22
- **说明**: 10 种嵌合 Gpa1 "transplants"，C-末端 5 aa 替换为哺乳动物 Gα 序列。测试 7 chimeras × 8 hGPCRs，Gαi/o 类嵌合体偶联范围最广，Gαs/Gαq 嵌合体在 GPA1 启动子下无活性。
- **项目关联**: 嵌合 Gpa1 C-末端 5 aa 替换的系统性比较，确定真菌 Gα 类型后可选择最佳 transplant 序列。
- **引用**: Brown AJ et al. (2000) *Yeast* 16(1):11–22. DOI: 10.1002/(SICI)1097-0061(20000115)16:1<11::AID-YEA497>3.0.CO;2-K
## Hara2012 | Hara et al. (2012) ★★☆
**Chimeric Yeast G-Protein alpha Subunit Harboring a 37-Residue C-Terminal Gustducin-Specific Sequence Is Functional in *Saccharomyces cerevisiae***
- **期刊**: *Bioscience, Biotechnology, and Biochemistry* 76(6):1088–1093
- **说明**: 嵌合 Gpa1 C-末端 37 aa vs 44 aa 替换比较。37 aa 替换足以实现功能性偶联。
- **项目关联**: **嵌合 Gpa1 设计的直接参考**——确定 C 末端替换长度。
- **引用**: Hara K et al. (2012) *Biosci Biotechnol Biochem* 76(6):1088–1093. [DOI: 10.1271/bbb.110820](https://doi.org/10.1271/bbb.110820)
## Lengger2022 | Lengger et al. (2022) ★★☆
**Serotonin G Protein-Coupled Receptor-Based Biosensing Modalities in Yeast**
- **期刊**: *ACS Sensors* 7(5):1323–1335
- **说明**: 12 种人 serotonin GPCRs × 12 种 Gα backgrounds（native Gpa1 + 10 chimeras + truncated）= 144 组合库。灵敏度跨 >4 数量级。鉴定 5-HT4+Gpa1/Gαz 为最优偶联组合。
- **项目关联**: 系统性 Gα 选型方法论——144 组合筛选范式可指导 GprC/Gpr2/Gpr3 偶联 Gα 选择策略。
- **引用**: Lengger B et al. (2022) *ACS Sensors* 7(5):1323–1335. [DOI: 10.1021/acssensors.1c02061](https://doi.org/10.1021/acssensors.1c02061)
## Tier 4b: 下游通路改造
## Shaw2019 | Shaw et al. (2019) ★★★
**Engineering a Model Cell for Rational Tuning of GPCR Signaling**
- **期刊**: *Cell* 177(3):782–796
- **说明**: 通过 9 轮 CRISPR 敲除 15 个基因构建极简 GPCR 模型菌株 yWS1922。ODE 模型指导表达量优化，合成 TF 将输出提升 ≥250 倍。异源 GPCR domestication：3 周优化→<1 周移植。
- **项目关联**: **直接提供底盘极简化策略和"建模优先"表达量调控流程**；四参数框架（EC50/dynamic range/operational range/Hill slope）是传感器性能评估标准。
- **引用**: Shaw WM et al. (2019) *Cell* 177(3):782–796. [DOI: 10.1016/j.cell.2019.02.023](https://doi.org/10.1016/j.cell.2019.02.023)
## Fan2024 | Fan et al. (2024) ★★☆
**Cascaded amplifying circuit enables sensitive detection of fungal pathogens**
- **期刊**: *Biosensors and Bioelectronics* 246:116020
- **说明**: 三层级联放大（GPCR MAPK→sTF→GAL 正反馈），LOD 从 1 nM 降至 0.25 pM（4000 倍改善）。BvCYP76AD5+MjDOD 甜菜色素比色输出，肉眼可见。
- **项目关联**: sTF + Δsst2 + GAL 正反馈三件套是信号放大成熟框架；Hill 函数建模方法可用于 ODE 性能评估。
- **引用**: Fan X et al. (2024) *Biosens Bioelectron* 246:116020. [DOI: 10.1016/j.bios.2024.116058](https://doi.org/10.1016/j.bios.2024.116058)
## Miettinen2022 | Miettinen et al. (2022) ★★☆
**A GPCR-based yeast biosensor for biomedical, biotechnological, and point-of-use cannabinoid determination**
- **期刊**: *Nature Communications* 13:3664
- **说明**: 酵母 GPCR 大麻素生物传感器。异源表达人 CB2R + 嵌合 Gpa1，GFP/lycopene 双输出。EC50 ~10 nM。
- **项目关联**: 完整的"异源 GPCR + 嵌合 Gpa1 + 双输出"底盘实现案例。
- **引用**: Miettinen K et al. (2022) *Nat Commun* 13:3664. [DOI: 10.1038/s41467-022-31357-6](https://doi.org/10.1038/s41467-022-31357-6)
## FanC2023 | Fan C & Yuan (2023) ★★☆
**Reshaping the yeast galactose regulon via GPCR signaling cascade**
- **期刊**: *Cell Reports Methods* 3(12):100647
- **说明**: 将 GPCR 信号通路与 GAL 调控子重新连接，通过调控 GPCR cascade 关键组分重塑 GAL 系统的动态范围、灵敏度和响应时间。构建 α-factor 自分泌菌株实现群体感应行为。
- **项目关联**: 下游信号放大策略参考——GAL 系统重塑方法可用于优化 ascaroside 响应的动态范围。
- **引用**: Fan C, Yuan J (2023) *Cell Rep Methods* 3(12):100647. [DOI: 10.1016/j.crmeth.2023.100647](https://doi.org/10.1016/j.crmeth.2023.100647)
## Tier 4c: 显色输出
## Billerbeck2017 | Billerbeck (Ostrov) et al. (2018) ★★☆
**A modular yeast biosensor for low-cost point-of-care pathogen detection**
- **期刊**: *Science Advances* 4(1):eaat3603
- **说明**: 模块化酵母生物传感器，11 种真菌受体偶联成功，番茄红素比色输出，纸基 dipstick 室温 36 周稳定。
- **项目关联**: 产品化参考——比色输出 + 纸基 dipstick + 室温储存。
- **引用**: Ostrov N, Billerbeck S et al. (2018) *Sci Adv* 4(1):eaat3603. [DOI: 10.1126/sciadv.1603221](https://doi.org/10.1126/sciadv.1603221)
## Lind2024 | Lind et al. (2024) ★★☆
**Evaluation and comparison of colorimetric outputs for yeast-based biosensors in laboratory and point-of-use settings**
- **期刊**: *FEMS Microbiology Letters* 371:fnae034
- **说明**: 系统比较番茄红素（lycopene）、脱氧紫色杆菌素（prodeoxyviolacein）和前紫色杆菌素（proviolacein）三种比色输出。琼脂平板上三者强度相当；液体培养和纸片条中番茄红素信号最强、检出时间最短（6h 肉眼可见）。
- **项目关联**: 显色输出选型的直接数据支持——确认番茄红素为 point-of-care 应用最优比色方案。
- **引用**: Lind AC, David F, Siewers V (2024) *FEMS Microbiol Lett* 371:fnae034. [DOI: 10.1093/femsle/fnae034](https://doi.org/10.1093/femsle/fnae034)
---
# Tier 5: iGEM 历史项目
> 历届 iGEM 团队在 GPCR 信号建模、分子对接、酵母传感器方面的相关项目。
- **BIT-China 2017** — GPCR 信号通路建模 — [wiki](https://2017.igem.org/Team:BIT-China)
- **Patras 2021** — 分子对接建模 — [wiki](https://2021.igem.org/Team:Patras)
- **Duke 2017** — 分子对接建模 — [wiki](https://2017.igem.org/Team:Duke)
- **TU Darmstadt 2012** — 分子对接建模 — [wiki](https://2012.igem.org/Team:TU_Darmstadt)
- **UCopenhagen 2019** — GPCR 设计 — [wiki](https://2019.igem.org/Team:UCopenhagen)
- **SJTU-BioX-Shanghai 2016** — 酵母 GPCR 传感器 — [wiki](https://2016.igem.org/Team:SJTU-BioX-Shanghai)
- **Chalmers-Gothenburg 2012** — 酵母 GPCR 检测 hCG — [wiki](https://2012.igem.org/Team:Chalmers-Gothenburg)
- **TU-Delft 2012** — 酵母 GPCR 平台 — [wiki](https://2012.igem.org/Team:TU-Delft)
- **Peking 2013** — 生物传感器设计 — [wiki](https://2013.igem.org/Team:Peking)
---
# Tier 6: 方法学
> 分子对接（Vina）、结构预测（AlphaFold）、交互指纹分析（IFP/ProLIF）、GPCR 结构综述。
## Trott2010 | Trott & Olson (2010) ★★★
**AutoDock Vina: Improving the Speed and Accuracy of Docking with a New Scoring Function, Efficient Optimization, and Multithreading**
- **期刊**: *Journal of Computational Chemistry* 31(2):455–461
- **说明**: **必须引用**。AutoDock Vina 原始论文。RMSD<2Å 成功率 78%（vs AutoDock 4 的 49%），速度提升约 62×（单线程）。评分函数 5 项加权和（gauss/repulsion/hydrophobic/H-bond/Nrot）。
- **项目关联**: 本项目使用 Vina 进行所有对接；评分函数公式和权重参数是 ΔG 值解读的理论基础。
- **引用**: Trott O, Olson AJ (2010) *J Comput Chem* 31(2):455–461. [DOI: 10.1002/jcc.21334](https://doi.org/10.1002/jcc.21334)
## Eberhardt2021 | Eberhardt et al. (2021) ★★★
**AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings**
- **期刊**: *Journal of Chemical Information and Modeling* 61(8):3891–3898
- **说明**: **必须引用**。Vina 1.2.0 功能升级：AD4 评分函数移植（速度快 100×）、大环/hydrated docking、Python bindings（`from vina import Vina`）。
- **项目关联**: 项目脚本直接调用 `from vina import Vina`；后续可切换 AD4 评分函数。
- **引用**: Eberhardt J et al. (2021) *J Chem Inf Model* 61(8):3891–3898. [DOI: 10.1021/acs.jcim.1c00203](https://doi.org/10.1021/acs.jcim.1c00203)
## Jumper2021 | Jumper et al. (2021) ★★★
**Highly accurate protein structure prediction with AlphaFold**
- **期刊**: *Nature* 596:583–589
- **说明**: **必须引用**。AlphaFold2 蛋白结构预测。CASP14 中位骨架 RMSD 0.96Å（竞争者 2.8Å），free-modeling RMSD 1.5Å。pLDDT/PAE 可靠性估计。
- **项目关联**: 本项目以 AlphaFold（AF3）预测 GprC/Gpr3 受体结构用于 Vina 对接；pLDDT>0.95 可信区域是结构质量过滤标准。
- **引用**: Jumper J et al. (2021) *Nature* 596:583–589. [DOI: 10.1038/s41586-021-03819-2](https://doi.org/10.1038/s41586-021-03819-2)
## Lee2022 | Lee et al. (2022) ★★★
**Evaluating GPCR modeling and docking strategies in the era of deep learning-based protein structure prediction**
- **期刊**: *Computational and Structural Biotechnology Journal* 21:158–167
- **说明**: **关键方法论**。AF2+Vina 对接 benchmark：刚性 Vina 仅 24–32% RMSD<2Å（远低于晶体结构）。pLDDT>0.95 区域结构可信。wiki 须声明此局限性。
- **项目关联**: 直接约束项目结论的置信度声明——AF 预测结构 + 刚性 Vina 对接的固有局限性必须在 wiki 中明确说明。
- **引用**: Lee GR et al. (2022) *Comput Struct Biotechnol J* 21:158–167
## Bouysset2021 | Bouysset et al. (2021) ★★★
**ProLIF: a library to encode molecular interactions as fingerprints**
- **期刊**: *Journal of Cheminformatics* 13:72
- **说明**: **必须引用**。ProLIF 工具论文：计算蛋白-配体交互指纹（IFP），支持氢键/疏水/π-stacking/盐桥等类型。
- **项目关联**: 本项目使用 ProLIF 进行所有 IFP 交叉验证（3 受体 × 3 配体）。
- **引用**: Bouysset C, Fiorucci S (2021) *J Cheminform* 13:72. [DOI: 10.1186/s13321-021-00548-6](https://doi.org/10.1186/s13321-021-00548-6)
## Boukharta2014 | Boukharta et al. (2014) ★★☆
**Computational Prediction of Alanine Scanning and Ligand Binding Energetics in G-Protein Coupled Receptors**
- **期刊**: *PLoS Computational Biology* 10(4):e1003585
- **说明**: FEP（Free Energy Perturbation）计算预测 GPCR alanine scan 对配体结合能的影响。预测与实验 ΔΔG 相关性 R²~0.6–0.8。
- **项目关联**: Alanine scan 方法学参考——验证 Vina 能量差 ΔΔG 趋势的合理性。
- **引用**: Boukharta L et al. (2014) *PLoS Comput Biol* 10(4):e1003585. [DOI: 10.1371/journal.pcbi.1003585](https://doi.org/10.1371/journal.pcbi.1003585)
## Vass2016 | Vass et al. (2016) ★★☆
**Molecular interaction fingerprint approaches for GPCR drug discovery**
- **期刊**: *Current Opinion in Pharmacology* 30:59–68
- **说明**: GPCR 交互指纹（IFP）综述。系统介绍 IFP 在 GPCR 配体筛选/构效关系/选择性分析中的应用。
- **项目关联**: IFP 分析方法学背景——解释为何选择 IFP 作为对接结果交叉验证手段。
- **引用**: Vass M et al. (2016) *Curr Opin Pharmacol* 30:59–68. [DOI: 10.1016/j.coph.2016.07.007](https://doi.org/10.1016/j.coph.2016.07.007)
## Zhang2024 | Zhang et al. (2024) ★☆☆
**G protein-coupled receptors (GPCRs): advances in structures, mechanisms and drug discovery**
- **期刊**: *Signal Transduction and Targeted Therapy* 9:88
- **说明**: 43 页综述，涵盖 554 个 PDB GPCR 结构、11 个变构位点、偏向信号结构量化、AF2 在 GPCR 预测中的适用范围与局限。
- **项目关联**: BW 编号残基参考框架；AF2 结构质量认知；真菌 GPCR 不可直接套用哺乳动物保守性数据的注意事项。
- **引用**: Zhang M et al. (2024) *Signal Transduct Target Ther* 9:88. [DOI: 10.1038/s41392-024-01803-6](https://doi.org/10.1038/s41392-024-01803-6)
