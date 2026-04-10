# Youssar et al. 2019 — 文献总结

> **完整标题**: Intercellular communication is required for trap formation in the nematode-trapping fungus *Duddingtonia flagrans*
> **期刊**: PLoS Genetics, 15(3): e1008029
> **DOI**: https://doi.org/10.1371/journal.pgen.1008029
> **发表日期**: March 27, 2019
> **作者**: Loubna Youssar\*, Valentin Wernet\*, Nicole Hensel, Xi Yu, Heinz-Georg Hildebrand, Birgit Schreckenberger, Marius Kriegler, Birgit Hetzer, Phillip Frankino, Andrew Dillin, Reinhard Fischer（\* 共同第一作者）
> **机构**: Karlsruhe Institute of Technology (KIT), Max Rubner Institute (Karlsruhe), Howard Hughes Medical Institute / University of California Berkeley

---

## 核心发现（5-10 bullets，含数据）

- ***D. flagrans* 基因组测序完成**：基因组大小 36.64 Mb，共 9,927 个蛋白编码基因；GC 含量 45.1%；组装为 14 条 contigs，N50 contig 长度 6,168,687 bp（PacBio SMRT 测序，平均读长 8,516 nt）。
- **分泌组规模大**：638 个预测分泌蛋白（约占全基因组 6.4%），其中 249 个为小分泌蛋白（SSPs，< 300 aa），117 个为推定 effector/毒力因子蛋白（EffectorP 2.0 预测）；60 个效应蛋白预测定位于胞外，4 个定位于细胞核。
- **推定毒力效应蛋白 PefB 进入线虫细胞核**：PefB（DFL_009915，274 aa）含 N 端信号肽和核定位信号（NLS，aa 54–76）；在 *C. elegans* 与 *D. flagrans* 共培养 24 h 后，*pefB* 转录量上调 16.1 ± 2.1 至 81.1 ± 10.4 倍（三次生物重复）；GFP 融合蛋白在 *C. elegans* 咽部附近的神经/肠细胞核中可见定位，证明 NLS 在线虫中有功能。
- **细胞间通讯是捕陷器环闭合的必要条件**：*sofT*（*D. flagrans* 中 *N. crassa* 软化素 *so* 同源基因）敲除后，菌丝吻合（anastomosis）完全缺失，环闭合失败，仅能形成螺旋状非闭合结构；*ΔsofT* 菌株毒力显著下降（36 h 时消化线虫比例：WT 65 ± 14% vs. *ΔsofT* 1 ± 1%，P = 0.0476）；菌丝萌发时间和生长速率无显著差异，排除生长缺陷干扰。
- **建立 *D. flagrans* 遗传转化与荧光蛋白体系**：三种选择标记（hph, nat, neo）均可用；GFP 和 mCherry 在 *B. cinerea* 启动子驱动下成功表达，为首次在黏性捕陷型 NTF 中建立荧光蛋白工具；H2B-mCherry 核标记可追踪线虫体内菌丝核。
- **CRISPR/Cas9 系统在 *D. flagrans* 中成功应用**：以 RNP（核糖核蛋白）转化法靶向 *sofT* 第一外显子，获得 4 株转化子，其中 3 株插入了 *hph* 抗性盒；互补实验恢复野生型表型，确认 sofT 敲除表型的特异性。
- ***D. flagrans* 能捕食大型植物病原线虫**：成功捕获 3 mm 长的葡萄扇叶病毒传播者 *Xiphinema index*（远大于 *C. elegans*），48 h 共培养后首批线虫被固定，证明其作为生防真菌的广谱潜力。
- **二级代谢产物合成能力有限**：基因组仅含 3 个 PKS 和 3 个 NRPS 型基因簇，远少于其他丝状真菌（如 *A. flavus* 含 29 PKS + 27 NRPS）；其中一个 PKS 与 *A. oligospora* 中负调控捕陷器形成的基因同源。
- **厚垣孢子特异蛋白鉴定**：比较 *D. flagrans* 与 *A. oligospora* 蛋白质组，591 个 *D. flagrans* 特有蛋白中，81 个聚类与 5 种厚垣孢子形成真菌共享，包括糖基化转移酶（Dol-P-Man:Man(5)GlcNAc(2)-PP-Dol alpha-1,3-mannosyltransferase）等。

---

## 实验方法（表格）

| 方法 | 关键参数 |
|------|---------|
| 基因组测序 | PacBio SMRT；平均读长 8,516 nt；36.64 Mb；14 contigs |
| RNA-seq | Illumina BGISEQ-500；23,941,723 reads；88.84% 映射至基因组；混合营养型/捕食期样品 |
| 基因预测 | BRAKER2（GeneMark-EX + AUGUSTUS）+ RNAseq 辅助 |
| 分泌蛋白预测 | SignalP 4.0 + WoLF PSORT + TMHMM；效应蛋白预测用 EffectorP 2.0 |
| 转化体系 | 原生质体 PEG/CaCl₂ 法（改良自 *A. oligospora*/*A. oryzae* 方案）；100 µg/ml 潮霉素 B |
| CRISPR/Cas9 | RNP 法（200 nM Cas9 + 10 nM sgRNA）；靶向 *sofT* 外显子 1；PAM 位点 BLASTN 验证脱靶 |
| *sofT* 敲除验证 | Southern blot（HindIII/XbaI 酶切 + 3'-probe/hph-probe）+ PCR |
| 荧光标记 | GFP/mCherry（*A. nidulans oliC/gpdA* 启动子）；H2B-mCherry（H2B 原启动子）；共聚焦 Leica TC SP5 |
| 毒力实验 | LNA 平板；200 只 L2 幼虫；24 h/36 h 计数捕获/消化比例；3 次生物重复 |
| 定量 RT-PCR | SensiFast SYBR；CFX Connect 系统；gamma actin（DFL_002353）内参；ΔΔCt 法 |
| ABTS 分泌实验 | 含 1 mM ABTS 的 LNA 平板；漆酶活性以蓝绿色显色判定 |
| 捕陷器诱导 | LNA（pH 6.5）+ ~100 只 *C. elegans*；室温 6 h 后出现首个捕陷网 |
| 菌丝吻合定量 | 荧光共培养（野生型 GFP 背景 + *ΔsofT* magenta）；CFW 细胞壁染色；激光共聚焦 |

---

## 关键数据

### 基因组特征

| 指标 | 数值 |
|------|------|
| 基因组大小 | 36.64 Mb |
| G+C 含量 | 45.1% |
| 蛋白编码基因 | 9,927 |
| 分泌蛋白（secretome） | 638（~6.4%） |
| 小分泌蛋白（SSPs, <300 aa） | 249 |
| 推定效应蛋白 | 117 |
| tRNA 基因 | 159 |
| 平均外显子数/基因 | 3.80 |
| 平均内含子长度 | 92 bp |

### 与其他 NTF 比较（OrthoVenn）

| 物种 | 蛋白数 | 聚类数 | 单例数 |
|------|--------|--------|--------|
| *D. flagrans* | 9,927 | 8,890 | 855 |
| *A. oligospora* | 11,479 | 9,449 | 1,723 |
| *Da. haptotyla* | 10,959 | 8,576 | 2,017 |
| *Dr. stenobrocha* | 5,597 | 5,597 | 424 |

四种 NTF 共有 4,646 个直系同源基因家族；*D. flagrans* 与 *A. oligospora* 共有 950 个特有家族。

### sofT 敲除毒力数据

| 时间点 | WT 捕获率 | *ΔsofT* 捕获率 | WT 消化率 | *ΔsofT* 消化率 |
|--------|-----------|----------------|-----------|----------------|
| 24 h | 10 ± 4% | 7 ± 4%（ns） | 19 ± 5% | 5 ± 2%（\*） |
| 36 h | 65 ± 14% | 35 ± 12%（\*） | 5 ± 2% | 1 ± 1%（\*） |

（\* P < 0.05，unpaired t-test；ns = 不显著）

### PefB 表达上调倍数（三次独立实验）

- 实验 1：16.1 ± 2.1 倍
- 实验 2：31.7 ± 4.1 倍
- 实验 3：81.1 ± 10.4 倍

---

## 与项目的关系

本文研究对象为 *Duddingtonia flagrans*，与本项目核心受体 **GprC**（来自 *A. flagrans*，即 *D. flagrans*）直接相关，提供了以下背景信息：

1. **GprC 所在物种的基因组背景**：本文提供了 *D. flagrans* 完整基因组（36.64 Mb，9,927 基因），是理解 GprC 在物种水平上的受体家族大小、分泌蛋白总量及信号通路的基础文献。
2. **NTF 捕陷器形成机制**：捕陷器形成依赖菌丝吻合（hyphal anastomosis）介导的细胞间通讯，*sofT* 是关键信号基因；这一发现表明 ascaroside 感知后的下游响应（捕陷器形成）在细胞层面需要细胞间协调，为研究 GprC 信号的生物学意义（从受体激活到捕陷器形成的因果链）提供了框架。
3. **推定效应蛋白进入线虫细胞核**：PefB 含 NLS，可在 *C. elegans* 中定位于细胞核，提示 *D. flagrans* 分泌蛋白与线虫存在跨界（interkingdom）分子互作，这是理解 GprC 在 NTF–线虫互作界面中角色的重要背景。
4. **遗传工具可用性**：本文建立的转化体系（GFP/mCherry/CRISPR）对后续 GprC 功能验证（如 CRISPR 敲除、荧光标记受体）有直接参考价值。

> 注意：本文未直接研究 GprC 受体或 ascaroside 感知，上述联系均基于物种背景，不代表本文结论。

---

## 关键引用（8条）

1. **Nordbring-Hertz B, Friman E, Veenhuis M** (1989). Hyphal fusion during initial stages of trap formation in *Arthrobotrys oligospora*. Ant Leeuw. 1989; 55(3):237–44. PMID: 2757366. — 菌丝吻合在捕陷器形成早期的经典描述。
2. **Yang E, Xu L, Yang Y, et al.** (2012). Origin and evolution of carnivorism in the Ascomycota (fungi). Proc Natl Acad Sci USA. 109(27):10960–5. — NTF 起源于二叠纪/三叠纪，由腐生型进化而来。
3. **Hsueh YP, Gronquist MR, Schwarz EM, et al.** (2017). Nematophagous fungus *Arthrobotrys oligospora* mimics olfactory cues of sex and food to lure its nematode prey. eLife. 6:e20023. — NTF 利用 ascaroside 等信号诱捕线虫的直接证据。
4. **Lebrigand K, He LD, Thakur N, et al.** (2016). Comparative genomic analysis of *Drechmeria coniospora* reveals core and specific genetic requirements for fungal endoparasitism of nematodes. PLoS Genet. 12(5):e1006017. — NTF 比较基因组学参照。
5. **Sperschneider J, Dodds PN, et al.** (2018). EffectorP 2.0: Mol Plant Pathol. 19(9):2094–110. — 本文预测效应蛋白所用的 EffectorP 2.0 方法文献。
6. **Herzog S, Schumann MR, Fleissner A** (2015). Cell fusion in *Neurospora crassa*. Curr Opin Microbiol. 28:53–9. — 菌丝吻合分子机制综述，sofT 所在通路基础。
7. **Xu ZF, Wang BL, Sun HK, et al.** (2015). High trap formation and low metabolite production by disruption of the polyketide synthase gene in *Arthrobotrys oligospora*. J Agric Food Chem. 63(41):9076–82. PMID: 26422178. — PKS 负调控捕陷器形成的直接证据，*D. flagrans* 同源基因讨论的依据。
8. **Taffoni C, Pujol N** (2015). Mechanisms of innate immunity in *C. elegans* epidermis. Tissue Barriers. 3(4):e1078432. — 线虫表皮先天免疫机制，与 PefB 进入线虫核的生物学意义讨论相关。
