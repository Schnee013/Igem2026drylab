# Mendy et al. 2017 — 文献总结

> **完整标题**: Arabidopsis leucine-rich repeat receptor–like kinase NILR1 is required for induction of innate immunity to parasitic nematodes
> **期刊**: PLoS Pathogens, 13(4): e1006284
> **DOI**: https://doi.org/10.1371/journal.ppat.1006284
> **发表日期**: 2017年4月13日
> **作者**: Badou Mendy, Mary Wanjiku Wang'ombe, Zoran S. Radakovic, Julia Holbein, Muhammad Ilyas, Divykriti Chopra, Nick Holton, Cyril Zipfel, Florian M. W. Grundler, Shahid Siddique
> **机构**: Rheinische Friedrich-Wilhelms-University of Bonn（INRES – Molecular Phytomedicine）；The Sainsbury Laboratory, Norwich Research Park, UK

---

## 核心发现（含数据）

- **线虫侵染触发植物 PTI 响应**：对拟南芥根段进行 GeneChip 微阵列分析，发现线虫侵染迁移期使 ~2,110 个基因上调（FDR < 0.05；Fold change > 1.5），富集类别包括免疫系统响应、JA/ET 信号合成基因，提示植物免疫应答机制被激活。

- **NemaWater 含蛋白质性 elicitor，可触发 ROS 爆发**：将 *Heterodera schachtii*（*Hs*）J2 浸泡水（NemaWater）处理拟南芥根段，可诱导强烈的 ROS 爆发，与 flg22 相当，但峰值略延迟（flg22 峰值 10–40 min，HsNemaWater 峰值 20–120 min）。Proteinase K 或加热处理可强烈抑制 NemaWater 诱导的 ROS 爆发，表明 elicitor 为蛋白质性质。*Meloidogyne incognita* 来源的 NemaWater 同样诱导强烈 ROS 爆发，提示 elicitor 在不同线虫种间保守。

- **NemaWater 预处理增强植物对线虫和细菌的抗性**：用 *Hs*NemaWater 预处理植物后，*H. schachtii* 雌虫数量和 *M. incognita* 瘤数均显著减少；同时，virulent *Pseudomonas syringae* pv. tomato DC3000 的细菌数量（Log cfu/cm²）也显著下降，表明 NemaWater 诱导的 PTI 具有跨病原体抗性效果。

- **NemaWater 诱导的 PTI 依赖 BAK1 共受体**：*bak1-5* 单突变体和 *bak1-5 bkk1-1* 双突变体对 *H. schachtii* 的易感性显著高于 Col-0（允许更多雌虫发育）。NemaWater 诱导的 ROS 爆发在 *bak1-5* 突变体中显著降低，生长抑制实验也得到相同结论，提示 BAK1 参与线虫来源 elicitor 的感知。

- **NILR1（AT1G74360）是首个植物线虫感知免疫受体**：从两次微阵列共同上调的 593 个基因中，筛选 52 个 RLK/RLP 候选基因，最终鉴定出 NILR1（Nematode-Induced LRR-RLK 1）。*nilr1-1* 功能缺失突变体对 *H. schachtii* 易感性显著增加（雌虫数量约为 Col-0 的 1.5 倍），对 *M. incognita* 瘤数也显著增多；而 *nilr2-1* 对两者无显著变化。

- **NILR1 为 PTI 响应所必需**：*nilr1-1* 突变体中 NemaWater 诱导的 ROS 爆发和生长抑制响应均显著降低，进一步支持 NILR1 作为线虫感知 PRR 的功能定位。

- **NILR1 定位于质膜**：通过在 *N. benthamiana* 表皮细胞瞬时表达 35S:NILR1-GFP，共聚焦显微镜确认 NILR1 与质膜标记物 35S:PIP2A-mCherry 共定位，与 PRR 的预期亚细胞位置一致。

- **NILR1 在双子叶植物中广泛保守**：BLAST 搜索发现 NILR1 同源蛋白广泛分布于多种双子叶和单子叶植物中（芸薹科家族等）。番茄、甜菜叶片对 NemaWater 有 ROS 响应，而烟草（*N. benthamiana*）和水稻响应较弱或不一致，提示保守性因物种而异。

- **线虫侵染激活 JA 信号，SA 信号相对较弱**：转录组分析显示，JA/ET 相关生物合成和信号基因的表达显著上调，而 SA 相关基因的变化相对不明显；与 NemaWater 处理（JA 模式相同）结论一致。

---

## 实验方法

| 方法 | 说明 |
|------|------|
| GeneChip 微阵列 | Affymetrix ATH1 Genome Array（>22,500 探针组），比较侵染/NemaWater 处理与对照根段基因表达差异（FDR < 0.05；FC > 1.5） |
| NemaWater 制备 | 约 40,000 个无菌 *H. schachtii* J2 在 2 mL ddH₂O 中孵育 24 h，离心取上清 |
| ROS 爆发检测 | L-012 化学发光法，96 孔板，0–120 min 动态测定，光度计读数（RLU） |
| 生长抑制实验 | 5 日龄幼苗在 NemaWater/flg22 中孵育 7 天，测定鲜重 |
| 线虫侵染实验 | 拟南芥 agar 板接种 60–70 J2，*H. schachtii* 雌虫计数（14 dai）；*M. incognita* 瘤计数（21 dai） |
| qRT-PCR | 13 个基因验证微阵列数据，18S 内参，ΔΔCt 法 |
| 亚细胞定位 | 35S:NILR1-GFP 瞬时转化 *N. benthamiana*，与 35S:PIP2A-mCherry 共聚焦共定位（Zeiss CLSM 710） |
| in silico 分析 | BLAST 搜索 NILR1 ECD 同源序列（318 hits，44 物种），PHYML 最大似然树，SWISS-MODEL 结构预测（以 BRI1 为模板） |
| 突变体筛选 | T-DNA 插入 knockout 系：*nilr1-1*（AT1G74360）、*nilr2-1*（AT1G53430）；RT-PCR 验证表达缺失 |

---

## 关键数据

### 转录组响应
- 线虫侵染迁移期：2,110 个上调基因（FDR < 0.05，FC > 1.5）
- NemaWater 处理：2,520 个差异表达基因（1,422 上调，1,098 下调）
- 两次微阵列共同上调基因：593 个（Venn 图：侵染特异 544，NemaWater 特异 826）

### ROS 爆发（L-012 检测）
- *Hs*NemaWater 可诱导与 flg22 相当的 ROS 爆发，但峰值略延迟
- Proteinase K 或加热（90°C，30 min）强烈抑制 NemaWater 诱导的 ROS 爆发
- *nilr1-1* 中 NemaWater 诱导 ROS 显著低于 Col-0；*bak1-5* 也显著降低

### 线虫侵染表型
- *nilr1-1*：*H. schachtii* 雌虫数量显著多于 Col-0（约增加 ~50%）；*M. incognita* 瘤数也显著增加
- *nilr2-1*：两种线虫侵染均无显著变化
- *bak1-5* 和 *bak1-5 bkk1-1*：允许更多雌虫发育，对线虫易感性升高

### NemaWater 诱导的广谱抗性
- *H. schachtii* 预处理后：雌虫数量显著减少（P < 0.05）
- *M. incognita* 预处理后：瘤数显著减少（P < 0.05）
- *P. syringae* pv. tomato：4 dpi 细菌数量（Log cfu/cm²）显著低于对照（P < 0.05）

### NILR1 蛋白结构
- 分子量：121.8 kDa（1,106 氨基酸）
- 含 22 个 LRR 拷贝（LRR17–LRR18 之间有 76 aa 岛状结构域）
- 胞外域含半胱氨酸簇（Cx₅₂Cx₁₆C 模式），跨膜域 + Ser/Thr 激酶域

---

## 与项目的关系

本文鉴定了 NILR1 作为植物感知线虫 NAMP 的 LRR-RLK 受体，提供了植物端 PRR 识别线虫来源信号分子的首个直接证据。

iGEM 2026 干实验关注的是 ascr#18 在植物端的受体机制。本文虽未研究 ascr#18，但其核心结论与项目高度相关：

- **信号感知机制类比**：NILR1 属于 LRR-RLK，通过 BAK1 共受体形成感知复合体，与植物感知 PAMP 的经典 PRR 框架一致。若植物存在感知 ascr#18 的受体，其结构和信号机制很可能遵循类似的 LRR-RLK + co-receptor 模式。
- **NemaWater 系统**：本文建立的 NemaWater elicitor 系统（体外孵育线虫分泌物）为研究线虫分泌组分（包括 ascarosides）诱导 PTI 的实验提供了方法论参考。
- **PTI 下游标志物**：ROS 爆发（L-012）和生长抑制实验作为 PTI 的功能性读出指标，可应用于验证 ascr#18 受体功能的实验设计。
- **植物保守性**：NILR1 同源物在多种双子叶植物中保守，支持 ascr#18 感知机制在不同宿主植物中可能存在类似保守性的假设。

---

## 关键引用

1. **Mendy et al. 2017**（本文）— NILR1 is required for PTI induction to parasitic nematodes. *PLoS Pathog* 13(4): e1006284.

2. **Teixeira MA, Wei L, Kaloshian I (2016)** — Root-knot nematodes induce pattern-triggered immunity in Arabidopsis thaliana roots. *New Phytol* 211: 276–87. [NemaWater PTI 的 BAK1 依赖性基础]

3. **Peng HC, Kaloshian I (2014)** — The tomato leucine-rich repeat receptor-like kinases SlSERK3A and SlSERK3B have overlapping functions in bacterial and nematode innate immunity. *PLoS One* 9: e93302. [BAK1 同源物 SlSERK 在番茄中的线虫免疫功能]

4. **Manosalva P et al. (2015)** — Conserved nematode signalling molecules elicit plant defenses and pathogen resistance. *Nature Communication* 6: 7795. [ascarosides 作为 NAMP 激活植物防御的直接证据]

5. **Holbein J, Grundler FM, Siddique S (2016)** — Plant basal resistance to nematodes: an update. *J Exp Bot* 67: 2049–2061. [线虫基础抗性综述]

6. **Zipfel C (2014)** — Plant pattern-recognition receptors. *Trends in Immunology* 35: 345–351. [PRR 综述，PTI 框架背景]

7. **Albert I et al. (2015)** — An RLP23–SOBIR1–BAK1 complex mediates NLP-triggered immunity. *Nature Plants* 1: 15140. [BAK1 共受体复合体机制]

8. **Kammerhofer N et al. (2015)** — Role of stress-related hormones in plant defense during early infection of the cyst nematode *Heterodera schachtii* in Arabidopsis. *New Phytologist* 207: 778–789. [线虫侵染早期 JA/SA 激素响应]
