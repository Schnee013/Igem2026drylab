# Manosalva et al. 2015 — 文献总结

> **完整标题**: Conserved nematode signalling molecules elicit plant defenses and pathogen resistance
> **期刊**: Nature Communications 6:7795
> **DOI**: 10.1038/ncomms8795
> **作者**: Patricia Manosalva, Murli Manohar, Stephan H. von Reuss, Shiyan Chen, Aline Koch, Fatma Kaplan, Andrea Choe, Robert J. Micikas, Xiaohong Wang, Karl-Heinz Kogel, Paul W. Sternberg, Valerie M. Williamson, Frank C. Schroeder & Daniel F. Klessig
> **发表日期**: 2015-07-23

## 核心发现

- **Ascarosides 是植物可感知的线虫保守分子信号 (nematode-associated molecular patterns, NAMPs)**：植物能像识别细菌 MAMPs (flagellin, peptidoglycan) 一样，识别线虫产生的 ascarosides，并激活先天免疫反应
- **ascr#18 是植物寄生线虫产出的主要 ascaroside**：三个属的植物寄生线虫 (*Meloidogyne*, *Heterodera*, *Pratylenchus*) 均以 ascr#18 为最丰富的 ascaroside 成分
- **Picomolar 到 micromolar 浓度即可激活防御**：ascr#18 在极低浓度下即触发 MAMP-triggered immunity (MTI) 相关基因表达、MAPK 磷酸化以及 SA/JA 信号通路
- **Broad-spectrum resistance**：ascr#18 处理可增强 *Arabidopsis*、tomato、potato、barley 对 viral、bacterial、oomycete、fungal 及 nematode 感染的抗性
- **农业应用潜力**：利用 ascarosides 等小分子激活植物免疫，有望改善农业的经济性和环境可持续性

## 实验方法

- **Ascaroside 代谢组分析**：HPLC-MS/MS 高灵敏度筛选方法，分析植物寄生线虫 (*M. incognita*, *M. javanica*, *M. hapla*, *H. glycines*, *P. brachyurus*) 培养上清 (exo-metabolome) 中的 ascaroside 谱
- **Root treatment / leaf infiltration / foliar spray**：多种 ascr#18 施用方式 (根部浸泡、叶片注射、叶面喷雾)
- **qRT-PCR**：监测 defense marker genes 表达量 — *FRK1*, *PHI1* (MTI markers), *PR-1*, *PR-4* (SA-responsive), *PDF1.2* (JA-responsive), *GSTF6*, *LOX2*, *AOS* (SA/JA biosynthetic)
- **MAPK activation assay**：Immunoblot 检测 MPK3/MPK6 磷酸化 (anti-pTE-pY antibody)
- **Pathogen resistance assays**：
  - Bacterial: *Pseudomonas syringae* pv. *tomato* DC3000 (Arabidopsis, tomato)
  - Viral: Turnip Crinkle Virus / TCV (Arabidopsis) — 通过 coat protein (CP) immunoblot 定量
  - Oomycete: *Phytophthora infestans* US22 (tomato, potato)
  - Fungal: *Blumeria graminis* f. sp. *hordei* (barley)
  - Nematode: *Heterodera schachtii* (cyst) 和 *Meloidogyne incognita* (root-knot) on Arabidopsis

## 关键数据

### ascr#18 在线虫 exo-metabolome 中的浓度
- *Meloidogyne* spp. 培养上清中 ascr#18 浓度范围：**5 nM - 100 nM**
- *H. glycines* 和 *P. brachyurus* 中也检测到 ascr#18，但含量较低

### 最优有效浓度 (dose-response，按物种和病原体分)
| 植物 | 病原体 | ascr#18 最佳浓度 | 施用方式 |
|------|--------|------------------|---------|
| *Arabidopsis* | *Pst* DC3000 (bacterial) | **1 uM** | root treatment, 24 h |
| *Arabidopsis* | TCV (viral) | **1 uM** | root treatment, 24 h |
| Tomato | *P. infestans* (oomycete) | **1-10 nM** | root treatment, 48 h |
| Tomato | *Pst* DC3000 (bacterial) | **10 nM** | root treatment, 48 h |
| Potato | *P. infestans* (oomycete) | **10 nM** | root bathing / foliar spray, 48 h |
| Barley | *B. graminis* f. sp. *hordei* (fungal) | **0.01-1 uM** | leaf spray, 48 h |
| *Arabidopsis* | *H. schachtii* (cyst nematode) | **10 nM** | root treatment, 48 h |
| *Arabidopsis* | *M. incognita* (root-knot nematode) | **10 nM** | root treatment, 48 h |

### 防御通路激活
- **MAPK pathway**: MPK3 和 MPK6 在 ascr#18 leaf infiltration 后 **10 min** 内即被磷酸化激活
- **SA pathway**: *PR-1*, *PR-4*, *GSTF6* 在 root treatment 后 6-24 h.p.t. 显著上调
- **JA pathway**: *PDF1.2*, *LOX2*, *AOS* 显著上调
- **MTI markers**: *FRK1* (6 h.p.t.), *PHI1* (24 h.p.t.) 显著上调
- ET 和 auxin signalling 基本不受影响 (仅 *SAUR34* 有轻微上调)

### 其他 ascarosides 的活性
- **ascr#3** 和 **ascr#9**：leaf infiltration 可诱导 *PR-1* 和 *PDF1.2* 表达；ascr#9 还可增强 tomato 对 *P. infestans* 的抗性
- **oscr#9**：在所有测试中均无活性 (结构仅与 ascr#9 差异在 ascarylose 连接位置)
- 活性呈 **structure- and species-dependent** 特征

### 关键观察：高浓度抑制效应
- 在 *Arabidopsis* 和 tomato 中，**高浓度 ascr#18 (5 uM for Arabidopsis; 100 nM for tomato) 防御效果反而下降**
- 最佳防御浓度通常在 nM 级别 (tomato/potato) 或低 uM 级别 (Arabidopsis/barley)
- 与线虫中 ascaroside 的 bell-shaped dose-response 现象一致

## 与项目的关系

### ascr#18 as plant defense inducer
- 本文是 ascarosides 激活植物免疫的 **landmark paper**，首次证明植物将 ascarosides 识别为 nematode-associated molecular patterns (NAMPs)
- ascr#18 被确认为植物寄生线虫中最丰富的 ascaroside，是最主要的 plant defense elicitor
- 植物通过根部自然接触线虫分泌物中的 ascarosides，这与 biosensor 的检测场景高度一致

### Concentration ranges for biosensor design
- 线虫 exo-metabolome 中 ascr#18 的自然浓度为 **5 nM - 100 nM**
- 植物防御的最佳诱导浓度为 **1-10 nM** (tomato/potato) 到 **~1 uM** (Arabidopsis)
- Biosensor 的检测灵敏度目标应覆盖 **nM 级别**，以匹配生物学相关浓度范围

### HP narrative for economic benefit model
- 线虫每年造成全球农业损失超过 **$100 billion** (引用文献 8)
- 论文明确提出：利用 ascarosides 等小分子激活植物免疫 "has potential utility to improve economic and environmental sustainability of agriculture"
- Root bathing 和 foliar spray 均有效，提示 ascr#18 可作为 **环保型生物农药** 的先导分子
- 三个马铃薯品种 (Desiree, Eva, Yukon Gold) 均对 ascr#18 处理表现出对 *P. infestans* 的增强抗性

### Broad-spectrum resistance evidence
- 本文提供了 ascr#18 对 **5 大类病原体** (virus, bacteria, oomycete, fungus, nematode) 和 **4 种作物** (Arabidopsis, tomato, potato, barley，含 dicot 和 monocot) 的抗性增强证据
- 这种 broad-spectrum 特性类似于 bacterial MAMPs (如 flagellin) 触发的 pattern-triggered immunity

## 关键引用

- **Boller & Felix 2009** (Ref 1): MAMP perception 和 pattern-recognition receptors 的综述
- **von Reuss et al. 2012** (Ref 27): *C. elegans* ascaroside 代谢组的 comparative metabolomics 方法论 (本文使用的 MS 筛选方法源于此)
- **Hsueh et al. 2013** (Ref 25): 线虫捕食真菌 (nematophagous fungi) 对 ascarosides 的应答 — 形成捕食装置 (trapping devices)
- **Choe et al. 2012** (Ref 19): Ascaroside signalling is widely conserved across nematodes
- **Schroeder 2015** (Ref 18): *C. elegans* 中 ascaroside 作为 modular chemical language 的综述
- **Jagdale et al. 2009** (Ref 12): Entomopathogenic nematodes 诱导植物系统抗性的前期证据
- **Jones et al. 2013** (Ref 26): Plant-parasitic nematodes 对农业的重要性 (Top 10 plant-parasitic nematodes)
