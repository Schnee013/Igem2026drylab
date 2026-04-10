# Hsueh et al. 2017 — 文献总结

> **完整标题**: Nematophagous fungus *Arthrobotrys oligospora* mimics olfactory cues of sex and food to lure its nematode prey
> **期刊**: *eLife* 2017;6:e20023
> **DOI**: 10.7554/eLife.20023
> **作者**: Yen-Ping Hsueh, Matthew R Gronquist, Erich M Schwarz, Ravi David Nath, Ching-Han Lee, Shalha Gharib, Frank C Schroeder, Paul W Sternberg
> **机构**: California Institute of Technology (Howard Hughes Medical Institute); Academia Sinica, Taiwan; State University of New York at Fredonia; Cornell University; Boyce Thompson Institute

## 核心发现

- *Arthrobotrys oligospora* 能吸引 *C. elegans* 及至少12种其他线虫（包括 *P. redivivus*、*P. pacificus*、*B. xylophilus*），chemotaxis index (CI) 成虫约 0.8，dauers 和 L1 幼虫吸引力显著较低（p<0.001）
- 引诱行为由挥发性化合物介导：三分隔皿实验（线虫只能感知气体而非溶液）仍观察到显著趋化，证明 *A. oligospora* 产生挥发性引诱物
- GC × GC-TOFMS 分析鉴定出5种真菌特异性挥发物：S-methyl thioacetate (SMT)、(±)-2-methyl-1-butanol (MB)、dimethyl disulfide (DMDS)、**methyl 3-methyl-2-butenoate (MMB)**、2,4-dithiapentane (DTP)；其中 MMB 对 *C. elegans* 的吸引力最强，跨 10⁶ 浓度范围均有效
- MMB 模拟性信息素功能：对成年雌雄同体和雌性线虫高度吸引，但对雄性无吸引力（甚至排斥），且会严重干扰 *C. afra* 的交配行为（1 µl MMB 使多数试验在30分钟内不能完成交配）
- *A. oligospora* 引诱由 AWC 嗅觉神经元介导：AWC 神经元激光消融使吸引率从~70%降至~20%（p<0.0001）；*odr-1*、*odr-3*、*tax-2*、*tax-4* 等 AWC 功能基因突变体趋化性显著下降
- AWC^on 神经元直接被 MMB 激活：GCaMP6 钙成像显示 MMB（10⁻³ M）引发强烈 AWC^on 激活；AWC⁻ 突变体（*ceh-36*）对 MMB 趋化性完全丧失，且在 *A. oligospora* 培养板上16小时存活率（~30%）显著高于野生型（~3%，p<0.0001）
- 前向遗传筛选鉴定出 *odr-7* 是 MMB 受体的关键调节基因：两个强缺陷突变体（sy837、sy838）均携带 *odr-7* 基因提前终止突变（codon 83 和 188），互补实验证实为同一基因；*odr-7* 是调节 AWA 和 AWC 神经元基因表达的核受体
- 单细胞 RNA-seq 分析 AWC^on 神经元：检测到 5894 个基因表达，其中 48 个 GPCRs，34 个含化学感受 PFAM 结构域；Gene Ontology 显示 AWC 特异性富集 G-protein coupled receptor activity [GO:0004930] 和 olfactory learning [GO:0008355]
- 适应性实验证实 MMB 是真实化学感受信号：*A. oligospora* 培养物预适应2小时后，*C. elegans* 对 MMB 的趋化性显著降低（odor-specific，而对 IAA 和 BA 吸引力不变），符合 *C. elegans* 已知的嗅觉适应机制
- 提出"嗅觉拟态"（olfactory mimicry）进化假说：*A. oligospora* 通过产生模拟线虫食物气味（DMDS、MB 等，存在于松露香气中）和性信息素（MMB）的挥发物，将线虫引诱至捕食范围，是非运动性捕食者克服猎物逃逸的进化适应

## 实验方法

| 方法 | 用途 |
|------|------|
| 4点趋化实验（chemotaxis assay）| 定量评估线虫对 *A. oligospora* 或纯化学物质的吸引力（CI = (I+III−II−IV)/(I+II+III+IV)） |
| 三分隔皿挥发性趋化实验 | 区分挥发性 vs 溶液信号的贡献 |
| SPME + GC × GC-TOFMS | 固相微萃取真菌顶空挥发物，二维气质联用鉴定化合物结构 |
| AWC 神经元激光消融 | 验证 AWC 对 *A. oligospora* 引诱的必要性（mock n=37 vs AWC⁻ n=34） |
| 微流控 GCaMP6 钙成像 | 实时测量 AWC^on 对挥发物的钙响应（str-2::GCaMP6） |
| EMS 前向遗传筛选 + SNP 定位 + 全基因组测序 | 鉴定 MMB 感知所需基因；筛选约40,000个基因组 |
| 单细胞 RT-PCR RNA-seq（9个 AWC^on 细胞）| 构建 AWC 特异性转录组，鉴定候选化学感受 GPCR |
| 交配行为追踪（*C. afra*）| 评估 MMB 对雌雄交配效率的干扰（30分钟窗口） |
| 生存实验（AWC vs 野生型）| 比较嗅觉缺陷线虫在 *A. oligospora* 上的存活率 |

## 关键数据

### 趋化指数（CI）

| 条件 | CI（均值） |
|------|-----------|
| *C. elegans* 成虫 vs *A. oligospora* | ~0.8 |
| Dauers vs *A. oligospora* | 显著低于成虫（p<0.001） |
| L1 幼虫 vs *A. oligospora* | 显著低于成虫（p<0.001） |
| AWC 消融动物 vs *A. oligospora* | ~20%（对照~70%，p<0.0001） |
| *ceh-36*（AWC⁻）vs MMB (10⁻⁴ M) | 接近0（野生型 ~0.9，p<0.0001） |

### MMB 效价范围

- 吸引浓度：10⁻¹ 至 10⁻⁶ M，跨越 **10⁶** 数量级

### 存活率（16小时 *A. oligospora* 暴露）

| 基因型 | 存活率 |
|--------|--------|
| N2（野生型） | ~3% |
| *ceh-36*（AWC⁻） | ~30%（p<0.0001） |

### 遗传筛选

- 筛选规模：约 40,000 个基因组
- 分离突变体：13株（2株强缺陷 sy837、sy838，均为 *odr-7* 突变）
- *odr-7* 突变位点：sy837 codon 83 提前终止；sy838 codon 188 提前终止

### AWC 单细胞转录组

- 检测到上背景表达基因：5894个（5294 蛋白编码 + 32 非编码）
- GPCR 数量：48个，其中34个含化学感受 PFAM 结构域

## 与项目的关系

本文直接建立了 NTF 与线虫 ascaroside 感知体系的化学生态背景：*A. oligospora* 产生挥发性拟态物引诱线虫，而这一引诱机制的分子受体端（AWC 表达的 GPCR）与项目研究的 Gpr2/Gpr3 受体系统存在潜在关联。

- **叙事背景**：本文是理解 NTF 如何感知/利用线虫化学信号的关键背景文献——*A. oligospora* 不仅能被动诱捕，还主动产生化学拟态物，说明真菌-线虫的化学信号对话是双向的
- **AWC GPCR 候选**：文章鉴定到 AWC 神经元表达至少 34 个含化学感受结构域的 GPCR，提示线虫端存在多个未被鉴定的 ascaroside/食物气味受体，与项目研究的真菌端受体（GprC、Gpr2、Gpr3）互为镜像
- **ascaroside 上下文**：本文前置文献 Hsueh et al. 2013 显示 NTF 能窃听 *C. elegans* 的 ascaroside 通讯来诱导捕猎圈形成，本文则展示了真菌对食物和性信息素的主动拟态，两篇合并为项目的 NTF 化学感知叙事提供完整框架
- **MMB 的性信息素拟态**：MMB 的雌性/雌雄同体特异性吸引及交配干扰，暗示 NTF 可能特异性针对可繁殖成体进行捕食——这与研究 ascaroside（性别特异性化学信号）作为 GprC/Gpr2/Gpr3 配体的项目背景高度相关
- **研究缺口**：本文未鉴定 *A. oligospora* 端感知线虫信号（包括 ascaroside）的受体，正是项目 Gpr2/Gpr3 研究填补的空白

## 关键引用

- Hsueh YP, Mahanti P, Schroeder FC, Sternberg PW. 2013. Nematode-trapping fungi eavesdrop on nematode pheromones. *Current Biology* 23:83–86. — NTF 窃听 ascaroside 诱导捕猎圈，本文的直接前置工作
- Bargmann CI, Horvitz HR. 1991. Chemosensory neurons and overlapping functions direct chemotaxis to multiple chemicals in *C. elegans*. *Neuron* 7:729–742. — AWC 神经元功能经典文献
- Thomas JH, Robertson HM. 2008. The *Caenorhabditis* chemoreceptor gene families. *BMC Biology* 6:42. — *C. elegans* ~1300 个化学受体基因综述，MMB 受体筛选背景
- Sengupta P, Chou JH, Bargmann CI. 1996. *odr-10* encodes a seven transmembrane domain olfactory receptor required for responses to the odorant diacetyl. *Cell* 84:899–909. — 第一个由遗传筛选鉴定的 *C. elegans* 化学感受 GPCR
- Park D et al. 2012. Interaction of structure-specific and promiscuous G-protein-coupled receptors mediates small-molecule signaling in *Caenorhabditis elegans*. *PNAS* 109:9917–9922. — SRBC/DAF 受体感知 ascaroside，与项目配体-受体匹配直接相关
- Schwarz EM, Kato M, Sternberg PW. 2012. Functional transcriptomics of a migrating cell in *Caenorhabditis elegans*. *PNAS* 109:16246–16251. — 本文 AWC 单细胞 RNA-seq 的方法基础
- Troemel ER, Sagasti A, Bargmann CI. 1999. Lateral signaling mediated by axon contact and calcium entry regulates asymmetric odorant receptor expression in *C. elegans*. *Cell* 99:387–398. — str-2 不对称表达机制，AWC^on 定义的关键文献
- Flach A et al. 2006. Pollination by sexual mimicry in *Mormolycea ringens*. — 植物嗅觉拟态的类比，支持真菌"化学拟态"进化框架的跨界案例
