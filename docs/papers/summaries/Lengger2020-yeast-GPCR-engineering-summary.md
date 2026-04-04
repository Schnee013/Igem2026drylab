# Lengger & Jensen 2020 — 文献总结

> **完整标题**: Engineering G protein-coupled receptor signalling in yeast for biotechnological and medical purposes
> **期刊**: FEMS Yeast Research, 20, foz087
> **DOI**: https://doi.org/10.1093/femsyr/foz087
> **类型**: Minireview
> **作者**: Bettina Lengger and Michael K. Jensen (Novo Nordisk Foundation Center for Biosustainability, Technical University of Denmark)

## 核心发现

- 酵母（*S. cerevisiae*）天然拥有三个 GPCR（Ste2, Ste3 用于 pheromone sensing，Gpr1 用于 glucose sensing），其 mating pathway 已被广泛改造用于 heterologous GPCR 的功能表达和信号转导研究
- 已有 **>50 种 heterologous GPCR** 在酵母中成功功能表达，覆盖 human GPCR Class A 的大部分 subclass（aminergic, peptide, protein, lipid, melatonin, nucleotide, alicarboxylic acid, sensory, orphan）以及少量 Class B1
- 成功偶联 heterologous GPCR 到 yeast mating pathway 的关键工程参数已被系统总结，形成 8 大 engineering hotspot（见 Fig. 1B）
- 酵母作为 GPCR 研究平台的核心优势：synthetic 'null' GPCR background（可删除 Ste2/Ste3/Gpr1）、培养周期短、无需 cell passage、遗传工具丰富

## 主要内容

### 1. Engineered G protein-coupling（chimeric Ga 设计）

- G protein 是连接 heterologous GPCR 与 yeast mating pathway 的关键节点
- 人类基因组编码 16 种 Ga subunit，分为四大类：**Gai/o, Gas, Gaq, G12/13**
- 虽然可以直接使用 yeast endogenous Gpa1 或哺乳动物对应的 Ga subunit，但 **chimeric Ga subunit 通常偶联效率更高**
- Chimeric Ga 的典型设计：将 native Gpa1 的 **C-terminal 5 个氨基酸替换**为对应 heterologous Ga 的序列（C-terminal 在 receptor recognition 中起关键作用；Conklin et al. 1993; J. Liu et al. 1995）
- 一项大规模研究测试了 8 种 human receptor 与 7 种 chimeric Ga 的组合，结果显示：**7/8 的 GPCR 在使用 chimera 后 coupling efficiency 和 ligand sensitivity 提高**（Brown et al. 2000）
- 不同 GPCR class 在 coupling promiscuity 上有差异：natively coupling to **Gai/o 或 Gaq** 的 receptor 更 promiscuous，而 **Gai coupling receptor** 倾向于对 G protein choice 更 selective（Okashah et al. 2019）
- G protein 表达水平的平衡也很重要：需要优化 Ga, Gb, Gy 的表达比例，以确保高 pathway output 同时维持低 basal activity（Bush et al. 2016; Bridge et al. 2018; Shaw et al. 2019）
- Ga 的选择还会影响 olfactory receptor（OR）的 agonist-sensing ability（Minic et al. 2005; Fukutani et al. 2012）

### 2. Streamlining GPCR signalling（信号通路精简）

- Mating pathway 的激活会导致 cell cycle arrest 和 mating，这些对 GPCR assay 是不需要的
- **基本删除策略**：删除 sst2（Gpa1 的 negative regulator）、far1（cell cycle arrest inducer）、bar1（protease cleaving a-factor）以增强和稳定信号
- **进阶精简**（Billerbeck et al. 2018）：进一步删除 a-factor protease-cleaving 片段、排除 negative feedback 机制（MFA1/2, MFALPHA1/MFALPHA2 等 pheromone genes）
- **最极致的精简**（Shaw et al. 2019）：敲除 **15 个 GPCR 信号通路基因**，包括所有三个 native GPCR（STE2, STE3, GPR1）、negative regulator、cell cycle arrest inducer 等，构建出一个 minimised and tunable 的 yeast strain
- 利用定义好的 24 bp 序列进行 targeted insertion，使得关键信号基因可以 cost-effectively 地重新引入

### 3. GPCR expression optimisation（表达优化）

- Receptor number 与 sensitivity 正相关（Bush et al. 2016; Shaw et al. 2019）
- 使用强启动子如 **TDH3** 或 **PGK1** 可提高 GPCR transcription（Billerbeck et al. 2018; Hashi et al. 2018）
- 添加 **Kozak-like sequence** (-AAAAAAAUGUCU-) 于 GPCR ORF 上游，使 neurotensin receptor 的 fluorescence 提高约 **70%**（Hamilton, Watanabe and de Boer 1987; Hashi et al. 2018）
- 但高表达并非万能：很多 GPCR 的功能表达仍然困难，原因包括 post-translational processing 失败、ER trapping、cell surface non-availability、accessory protein 缺失、proteolytic degradation 等

### 4. Leader sequences for membrane insertion and ER processing

- N-terminal fusion of a **leader sequence** 可辅助 receptor 的膜插入（Fig. 1B）
- Yeast mating receptor **Ste2 的 N-terminal** 的 30 个 N-terminal residue 对 cell surface expression 和 negative regulation 至关重要（Uddin et al. 2016）
- 早期成功案例：用 Ste2 的 N-terminal sequence 替换 beta2-adrenergic receptor 的 N-terminal 实现功能化（King et al. 1990）
- 在 *P. pastoris* 中，fusion a-factor pre-propeptide 到 mouse 5-HT5A serotonin receptor 使表达提高 **3 倍**（Weiss et al. 1998）
- 但 leader sequence 效果因 receptor 而异，并非通用方案；部分研究显示提高了 cell surface display 但降低了 coupling efficacy（Iguchi et al. 2010）
- OR266/rat I7 chimera 研究：替换 N-terminal 32 或 58 个残基为 rat I7 序列可改善 localization 和 signal transduction；同时替换 C-terminal 和 N-terminal（含一个 intracellular loop）可使 bioluminescence 达到 native receptor 的近 **2 倍**（Fukutani et al. 2012）
- 删除 M1, M3, M5 muscarinic receptor 的第三个 intracellular loop 的中央部分可增加 receptor amount 和 Bmax（Erlenbach et al. 2001b），提示 internal loops 可能是 protease degradation 的靶标

### 5. Accessory proteins

- **Receptor-transporting protein** 的共表达可辅助 odorant receptor 到 cell membrane 的转运（如 OREG 和 OR7D4）
- **Odorant-binding protein**（来自 silkworm *Bombyx mori*）的共表达增加了 OREG 对 eugenol 的 sensitivity（Fukutani et al. 2015）
- **RAMP**（Receptor Activity Modifying Protein）可与 Class B GPCR 结合，改变其 ligand specificity、transport、internalization 和 downstream signalling（Klein, Matson and Caron 2016）
- 其他 accessory protein 包括 GEF, GDI, GAP, GTPase-activating protein, Gby-interacting protein 等（详见 Sato et al. 2006, 2013）

### 6. Synthetic transcription factors and promoters

- MAPK cascade 激活后，Ste12 从 cytoplasm 转位至 nucleus，调控 >100 个 endogenous mating pathway target promoter（Roberts et al. 2000）
- 常用 reporter promoter：**FUS1** 和 **FIG1**（Trueheart et al. 1987, 1989; Muller et al. 2003; Alvaro and Thorner 2016）
- 需要限制 Ste12 表达强度以避免 impair cell growth（Shaw et al. 2019）
- **Synthetic transcription factor 策略**：将 Ste12 与 LexA bacterial repressor protein 融合，reporter gene 置于含不同数量 LexA DNA binding domain 的 synthetic promoter 下，实现 **3-fold modulation** 的 output response，同时保持低 basal expression（Mukherjee, Bhattacharyya and Peralta-Yahya 2015; Shaw et al. 2019）
- 用 PLexA(4x) promoter 驱动 GFP 检测 OR1G1 对 decanoic acid 的响应，比 FIG1 promoter 下的 Ste12 控制提高了 **7 倍**

### 7. GPCR signalling read-outs（Reporter 系统）

- **Growth-based**：HIS3 growth-coupled assay，用于筛选 weak partial agonist 和 inverse agonist（将 equilibrium shift 至 inactive state）；CAN1/FUI1 permease 系统用于 negative selection（non-functional GPCR 才能存活）
- **Fluorescence**：趋势是使用 yeast-optimised fluorescent marker，提供 high sensitivity 和 high signal-to-noise ratio（Nakamura et al. 2013; Kaishima et al. 2016; Hashi et al. 2018）
- **Colourimetric**：beta-galactosidase, carotenoid 等 phenotypic screen（Price et al. 1995; Ostrov et al. 2017; Shaw et al. 2019）

### 8. Evolution of GPCRs（定向进化）

- Directed evolution 可优化 GPCR 的 expression level、ligand sensitivity 和 ligand specificity
- 经典案例：Ste2 的 directed evolution 使其识别 *Saccharomyces kluyveri* pheromone（Marsh 1992），site-directed mutagenesis 使其特异性识别 *Kluyveromyces lactis* pheromone（Di Roberto et al. 2017）
- **RASSLs**（Receptors Activated Solely by Synthetic Ligand）、**DREADDs**（Designer Receptors Exclusively Activated by Designer Drugs）、**TRECs** 和 **neoceptors** 等 synthetic GPCR 平台用于推断 drug targetability（Conklin et al. 2008）
- Directed evolution 也被用于提高 GPCR 表达水平，最佳 variant 可达 **26 倍**表达提升（Schutz et al. 2016）

### 9. 应用领域

#### Novel ligands and deorphanisation
- Somatostatin analogue 的 agonist/antagonist 鉴定（L-Cys2-L-Cys7 vs D-Cys2,L-Cys7）
- FPRL1 的 surrogate agonist 发现（6 个 novel peptide agonist from random plasmid library）
- CXCR4 的 allosteric agonist 鉴定（160,000 化合物库筛选）
- GPR119 的 novel agonist PSN375963
- Ste2 的 substrate walking 进化使其识别 biomarker protein **Cystatin C**（Adeniran et al. 2018）
- 目前仅 ~10% 的 >400 human orphan receptor 被 deorphanised

#### Biotechnological applications
- **Whole-cell biosensor**：GPCR-based biosensor 用于 point-of-care 环境监测
  - 2,4-dinitrotoluene 检测（rat olfactory receptor Olfr226，cAMP 系统；Radhika et al. 2007）
  - Medium-chain fatty acid 检测（GPR40, OR1G1；13-17 fold signal increase；Mukherjee et al. 2015）
  - Serotonin 检测（5-HT4 sensor strain，2-fold GFP increase；Ehrenworth et al. 2017）
  - **Melatonin 检测**（MTNR1A receptor；consortium of 2 sensing strains 覆盖 4 个数量级浓度范围；Shaw et al. 2019）
  - 病原真菌 pheromone 检测（*Candida albicans*, *C. glabrata*, *Paracoccidioides brasiliensis* 等 12 种真菌；Ostrov et al. 2017）——对 *P. brasiliensis* strain 通过 CCW12 强启动子实现 **picomolar sensitivity**
- **Metabolic engineering**：GPCR 用于筛选和优化代谢产物生产菌株
  - Sender-receiver concept：产物生产菌（sender）分泌 ligand，biosensor 菌（receiver）通过 GPCR 检测产量
  - 应用于 cannabinoid、opioid、strictosidine 等天然产物的生物合成（Galanie et al. 2015; Luo et al. 2019）

#### Medical applications
- Human rhodopsin（P23H mutant，retinitis pigmentosa 致病突变）偶联至 yeast mating pathway，用于筛选 rhodopsin-stabilising compound（Scott et al. 2019a,b）——semi-high-throughput 药物筛选平台

## 关键数据

| 指标 | 数据 |
|------|------|
| Human GPCR 总数 | 831（encoded in human genome） |
| FDA-approved 药物靶点中 GPCR 占比 | ~1/3 |
| 在酵母中功能表达的 GPCR 数量 | >50 |
| Human orphan receptor deorphanisation 比例 | ~10% of >400 |
| Shaw et al. 2019 精简 strain 敲除基因数 | 15 个 GPCR signalling genes |
| Chimeric Ga 提高 coupling 的成功率 | 7/8 tested GPCR（Brown et al. 2000） |
| Kozak-like sequence 对 NTR expression 的提升 | ~70% |
| PLexA(4x) vs FIG1 promoter 信号提升 | 7-fold |
| Medium-chain fatty acid biosensor signal increase | 13-17 fold |
| Melatonin biosensor 动态范围 | 4 orders of magnitude |
| Directed evolution 最大表达提升 | 26-fold（Schutz et al. 2016） |

**Fig. 1B 总结的 8 大 engineering hotspot：**
1. Engineered G protein-coupling
2. Streamlining GPCR signalling
3. GPCR expression optimisation
4. Leader sequences for membrane insertion and ER processing
5. Accessory proteins
6. Synthetic transcription factors and promoters
7. GPCR signalling read-outs
8. Evolution of GPCRs

## 与项目的关系

### Yeast chassis design for expressing Gpr2/Gpr3/GprC

- 本综述系统梳理了在 *S. cerevisiae* 中表达 heterologous GPCR 的全部工程策略，直接适用于项目中将线虫寄生真菌（nematode-trapping fungi）的 Gpr2/Gpr3/GprC 表达在酵母中的方案
- **关键启示**：需要构建一个删除了 STE2, STE3, GPR1 的 "null" GPCR background strain，避免 native GPCR 的 signalling crosstalk（Shaw et al. 2019 的 minimised strain 是最佳参考）
- 同时需要删除 sst2, far1, bar1 等基因以增强信号和消除 cell cycle arrest

### Chimeric Gpa1 design strategies

- 本文明确了 chimeric Ga 的核心设计原则：**替换 Gpa1 C-terminal 5 个氨基酸为 target GPCR 对应的 mammalian/fungal Ga C-terminal sequence**
- 对于 fungal GPCR（Gpr2/Gpr3/GprC），需要确定它们 natively couple 到哪个 Ga 类型，然后设计相应的 chimeric Gpa1
  - 如果 fungal Ga 与 yeast Gpa1 的 C-terminal 序列差异较大，chimera 策略尤其重要
  - 可参考 Brown et al. 2000 的系统 chimera 筛选方法，测试多个 chimeric variant
- G protein expression level 的平衡也需要优化（Ga:Gb:Gy 比例）

### Reporter system selection

- 对于初步功能验证：推荐 **FUS1 或 FIG1 promoter** 驱动 **GFP/fluorescent reporter**，简单直观
- 对于更高灵敏度和动态范围：使用 **synthetic transcription factor**（Ste12-LexA fusion）配合 **PLexA(4x) synthetic promoter**，可实现 7-fold 信号提升和低 basal expression
- 对于 high-throughput 筛选：可考虑 **HIS3 growth-coupled** assay 或 colourimetric reporter（beta-galactosidase）
- 对于 negative selection（筛选 loss-of-function mutant）：**CAN1/FUI1** inverted reporter system

### Known challenges and solutions for fungal GPCR expression in yeast

| 挑战 | 文中提到的解决策略 |
|------|----------------|
| Receptor 无法到达 cell surface（ER trapping） | N-terminal leader sequence fusion（Ste2 N-terminal 或 a-factor pre-propeptide） |
| 表达水平低 | 强启动子（TDH3, PGK1）+ Kozak-like sequence + codon optimization |
| G protein coupling 失败 | Chimeric Gpa1（C-terminal swap）；测试多个 chimera variant |
| Native pathway crosstalk | 删除 Ste2/Ste3/Gpr1 构建 null background |
| Cell cycle arrest 干扰 assay | 删除 FAR1 |
| Basal signalling 过高 | 删除 SST2 可增强信号但需注意 basal 升高；优化 G protein expression ratio |
| Post-translational processing 问题 | Accessory protein 共表达；protease-deficient strain |
| Lipid environment 不匹配 | Ergosterol 替换为 cholesterol 可使 membrane 更接近 mammalian cell（Hirz et al. 2013） |
| Olfactory receptor 特有的 insolubility 问题 | RAMP 共表达；odorant-binding protein 共表达 |

**特别注意**：本文提到 nematode chemoreceptor **ODR-10** 已在酵母中功能表达（Tehseen et al. 2014, PLoS One），这是线虫 chemoreceptor 在酵母中成功表达的直接先例，与项目高度相关。

## 关键引用

- **Shaw et al. 2019** — *Cell* 177:782-96. Engineering a model cell for rational tuning of GPCR signalling. **最极致的 mating pathway minimisation（15 gene KO），构建 tunable GPCR signalling chassis**
- **Brown et al. 2000** — *Yeast* 16:11-22. Functional coupling of mammalian receptors using chimeric Gpa1. **系统测试 8 receptor x 7 chimera 的 coupling 矩阵**
- **Billerbeck et al. 2018** — *Nat Commun* 9:5057. A scalable peptide-GPCR language for engineering multicellular communication. **Streamlined signalling pathway design**
- **Mukherjee, Bhattacharyya and Peralta-Yahya 2015** — *ACS Synth Biol* 4:1261-9. GPCR-based chemical biosensors for medium-chain fatty acids. **Synthetic TF (Ste12-LexA) + PLexA promoter 策略**
- **Ostrov et al. 2017** — *Sci Adv* 3:e1603221. A modular yeast biosensor for low-cost point-of-care pathogen detection. **12 种真菌 pheromone 的 biosensor 构建**
- **Tehseen et al. 2014** — *PLoS One* 9:e111429. Functional coupling of a nematode chemoreceptor to the yeast pheromone response pathway. **线虫 ODR-10 在酵母中的功能表达先例**
- **Conklin et al. 1993** — *Nature* 363:274-6. Substitution of three amino acids switches receptor specificity of Gqa to that of Gia. **C-terminal 氨基酸替换改变 Ga coupling specificity 的经典论文**
- **King et al. 1990** — *Science* 250:121-3. Control of yeast mating signal transduction by a mammalian beta2-adrenergic receptor and Gs alpha subunit. **第一个在酵母中功能表达的 heterologous GPCR**
- **Uddin et al. 2016** — *Biochim Biophys Acta* 1858:715-24. N-terminus of Ste2p plays critical roles in surface expression, signalling, and negative regulation. **Ste2 N-terminal 功能研究**
- **Adeniran et al. 2018** — *ACS Synth Biol* 7:696-705. Detection of a peptide biomarker by engineered yeast receptors. **Ste2 directed evolution 识别 Cystatin C biomarker**
