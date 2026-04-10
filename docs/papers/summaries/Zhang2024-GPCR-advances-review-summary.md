# Zhang et al. 2024 — 文献总结

> **完整标题**: G protein-coupled receptors (GPCRs): advances in structures, mechanisms and drug discovery
> **期刊**: *Signal Transduction and Targeted Therapy* (2024) 9:88
> **DOI**: https://doi.org/10.1038/s41392-024-01803-6
> **作者**: Mingyang Zhang\*, Ting Chen\*, Xun Lu\*, Xiaobing Lan†, Ziqiang Chen†, Shaoyong Lu†
> **通讯作者**: Ziqiang Chen (chensuper@1viv.cn), Shaoyong Lu (lushaoyong@sjtu.edu.cn)
> **机构**: School of Pharmacy, Ningxia Medical University; Medicinal Chemistry and Bioinformatics Center, Shanghai Jiao Tong University School of Medicine; Department of Cardiology, Changzheng Hospital; Department of Orthopedics, Changhai Hospital, Shanghai
> **类型**: 综述（Review Article）
> **接收/接受/发表**: 2023-08-15 / 2024-03-13 / 2024-04-10

---

## 核心发现（主要论点）

1. **结构解析技术的历史性突破**：过去二十年 cryo-EM 和 X-ray 晶体学的联合应用推动了 GPCR 结构研究，截至 2023 年 11 月蛋白质数据库已积累 554 个 GPCR 结构，其中 523 个经 cryo-EM 解析；第一个 GPCR-G 蛋白复合物结构（β2AR-Gs，PDB: 3SN6）于 2011 年解析，第一个 cryo-EM GPCR-arrestin 结构于 2019 年报道。

2. **变构调控位点的系统梳理**：综述系统梳理了 GPCR 中全部 11 个变构结合位点，分布于胞外前庭（3 个位置）、跨膜域外侧（5 个位置）、跨膜域内侧（1 个位置）及胞内表面（2 个位置）；其中 7TMD 内部（between helices）是迄今发现变构药物最集中的口袋（19 种已知配体结合 Class A GPCR 代表结构 CB1R）。

3. **FDA 批准的正构药物结合机制**：综述详细分析了近年 FDA 批准的 10 余种 GPCR 靶向正构药物（包括 μOR-oliceridine、S1PR-siponimod、5-HT1F-lasmiditan、GnRH1-elagolix、A2AR-istradefylline 等）的原子级药-靶相互作用，揭示了各受体亚型选择性的结构基础。

4. **偏向信号（biased signaling）的结构基础**：以 μOR 的芬太尼（G 蛋白偏向）与奥利西定（β-arrestin 招募较少）为典型案例，展示如何通过受体-arrestin 接触面积差异（fentanyl: 1550.3 Å², oliceridine: 1201.4 Å²）量化偏向；D2R 的 β-arrestin 偏向激动剂 Compound 12（β-arrestin bias factor = 2.5）和 Compound 13（bias factor = 20）的 SAR 分析提供结构参考。

5. **变构调控药物 39 个结构被解析**：自 2019 年 cinacalcet（CaSR PAM）首次获批以来，已有 4 个变构调控剂获 FDA 批准（cinacalcet、evocalcet、vismodegib、avacopan），1 个进入临床试验（LSN3160440 靶向 GLP-1R），另有大量前临床候选物。

6. **共价结合变构策略（Compound 2 for GLP-1R）**：发现 GLP-1R 的 TM VI 顶端含游离半胱氨酸（Cys347），设计共价 PAM（Compound 2）与其形成二硫键，显示胞内 TM VI 的突出可用于不可逆 GPCR 变构调控。

7. **计算方法的演进**：AF2/AlphaFold 可以预测准确的 GPCR 结构（相当于晶体级别），但中间激活态和变构结合位点的预测仍是挑战；MD 模拟可揭示构象变化和信号传导的时间序列；fragment-based 方法和 FBDD 筛选正扩大变构小分子的化学空间。

8. **双表位配体（bitopic ligand）设计原理**：将与正构位点结合的"anchor"片段通过 linker 连接至变构位点结合的"driver"片段，可同时获得高亲和力（正构位点）和高选择性（变构位点）；文章提出了设计此类配体的具体框架。

9. **GPCR 突变与人类疾病关联**：超过 2350 个 GPCR 突变与人类遗传病相关，其中功能获得型（GoF）和功能丧失型（LoF）突变各有特异性疾病谱；涉及受体包括 β2AR（青光眼）、MC4R（肥胖）、CaSR（低钙血症）、TSHR（甲状腺疾病）等。

10. **孤儿 GPCR 功能揭示**：GPR101（下丘脑-垂体功能）、GPR40（胰岛素分泌）、GPR61/GPR88（神经精神疾病）等孤儿 GPCR 的变构激动剂结构被解析，为发现其内源配体提供了工具。

---

## 主要讨论主题（综述性质）

| 章节 | 核心内容 | 代表药物/结构 |
|------|----------|------------|
| GPCR 结构进展 | X-ray / cryo-EM / XFELs / NMR / DEER-FRET 综述；GPCR 结构解析历史节点 | β2AR (2007), GPCR-G protein (2011), cryo-EM GPCR-arrestin (2019) |
| GPCR 激活与信号转导 | G 蛋白四大家族（Gs/Gi/Gq/G12）信号级联；β-arrestin 模式（tail vs core）；GRK 磷酸化；receptor crosstalk | β2AR-Gs 信号，MAPK/ERK/ASK1 |
| GPCR 功能多样性 | 五大功能类型（Class A-F）；脂肪酸、嗅觉、趣味性 GPCR；突变分类（GoF/LoF/trafficking/selectivity） | MC4R（肥胖）, β2AR（哮喘）, TSHR（甲状腺）|
| 正构位点药物发现 | FDA 批准药物药-靶相互作用原子级分析；SAR 规律；偏向信号设计 | oliceridine（μOR）, siponimod（S1PR）, lasmiditan（5-HT1F）, elagolix（GnRH1）|
| 变构位点药物发现（胞外前庭） | 3 个胞外变构位点（outside TM I-II, TM II-III, within 7TMD）；GLP-1R / GPR101 / M2R-M4R / CaSR 结构 | LSN3160440（GLP-1R PAM）, cinacalcet（CaSR NAM）, LY2119620（M2R/M4R PAM）|
| 变构位点药物发现（TM 外侧） | 5 个 TM 外侧变构位点（TM I-III / II-IV / III-V / V-VI / I,VI,VII）；CB1R / C5aR1 / CXCR3 / βAR / mGlu4 结构 | ORG27569（CB1R NAM）, avacopan（C5aR1 NAM, FDA approved 2021）, MIPS521（A1R PAM）|
| 变构位点药物发现（7TMD 内） | FFAR3 / CRF1R / PTH1R / mGluR5 结构；mGluR5 NAM 进入 Phase 1-3 | mavoglurant（mGlu5 NAM, Phase 3）, fenobam, HTL14242, PCO371（PTH1R PAM, Phase 2）|
| 变构位点药物发现（胞内面） | GCGR / GPR88 / CCGR / GLP-1R / CCR9 / GABA-B 胞内结合位点结构 | MK-0893（GCGR NAM, Phase 2）, vercirnon（CCR9 NAM, Phase 3）, BHFF（GABAB PAM）, Compound 2（GLP-1R 共价 PAM）|
| 展望 | 双表位配体设计；计算工具（AF2/MD/FBDD/ML）；变构药物分类新框架 | — |

---

## 关键数据

### GPCR 结构数量（截至 2023 年 11 月）

- Protein Data Bank 累积 GPCR 结构总数：**554 个**
- 其中经 cryo-EM 解析：**523 个**
- 综述中分析的正构小分子结构：**388 个**
- 综述中分析的变构小分子结构：**53 个**（其中 33 个结合胞外前庭，9 个结合 TM 外侧，9 个结合 7TMD 内，4 个结合 7TMD 内侧）

### 药物发现统计

- 已有约 **34%** 的 FDA 批准药物靶向 GPCR
- 至综述截稿时，已有 **4 个变构 GPCR 调控剂**获 FDA 批准
- 变构调控剂中进入临床试验：cinacalcet（批准）, evocalcet（批准）, vismodegib（批准）, avacopan（批准 2021）, PCO371（Phase 2）, HTL14242（Phase 1）, mavoglurant（Phase 3）, fenobam（Phase 1）, vercirnon（Phase 3）, MK-0893（Phase 2）

### 代表性配体-受体相互作用数据

| 受体 | 配体 | 结合类型 | 关键残基 | 数据来源 |
|------|------|----------|----------|---------|
| μOR | oliceridine | 正构激动剂（β-arr. low recruitment） | Y326^7.43, W293^6.48 | PDB: 8EF5/8EF8 |
| μOR | fentanyl | 正构激动剂 | 口袋更大，β-arr 接触面 1550.3 Å² | PDB: 8EF5 |
| S1PR1 | siponimod | 正构激动剂 | K34, Y29, R120, T97^2.56, F125^3.36, W269^6.48 | PDB: 7T6B |
| 5-HT1F | lasmiditan | 正构激动剂（扩展结合口袋 EBP） | H176^ECL2, P158^4.60, I174^ECL2, T182^5.40, D103^3.32 | PDB: 7EXD |
| GnRH1 | elagolix | 正构拮抗剂（独特信号传导机制） | K121^3.33, Y283^6.51, Y290^6.58, Y296^7.33 | PDB: 7BR3 |
| D2R | Compound 12 | β-arrestin 偏向激动剂（bias factor = 2.5） | I184^ECL2, S193^4.42 | PDB: 3BUL |
| GLP-1R | LSN3160440 | PAM（外 TM I-II） | L20^GLP-1, V16^GLP-1, K202^7.72, Y145^1.40, L142^1.37 | PDB: 6VCB |
| M2R | LY2119620 | PAM（外 7TMD） | Y177^ECL2, Tyr^7.35, Trp^7.35, Thr422^7.35 | PDB: 4MQT |
| CaSR | cinacalcet | NAM（内 7TMD） | Trp^6.50 reorientation | PDB: 7M3F |
| CaSR | NPS-2143 | NAM（内 7TMD） | Phe684^3.36, Leu776^5.43, Trp818^6.50 | PDB: 7M3E |
| C5aR1 | avacopan | NAM（外 TM III-V） | Ile124^3.40, Leu125^3.41, Trp213^5.49 | PDB: 6C1R |
| mGluR5 | HTL14242 | NAM（内 7TMD） | Tyr659^1.44, Ser809^7.39, Val806^7.36 | PDB: 5CGD |
| GCGR | MK-0893 | NAM（胞内面外 TM V-VII） | Arg346^6.37, Lys349^6.40, Leu352^6.43 | PDB: 5EE7 |
| GABAB | BHFF | ago-PAM（胞内面外 TM V-VII） | Tyr789^6.59, Ala788^5.58, Tyr791^6.38, Met807^6.61 | PDB: 7C7Q |

### 变构位点分布统计（Fig. 12）

全 GPCR 中报道的 11 个变构位点（以 Class A CB1R 为参考坐标系）：

| 位置 | 已知配体数（代表 GPCR 数） |
|------|------------------------|
| 胞外 EC 前庭（TM I-II 外） | 1(1) |
| 胞外 EC 前庭（TM I-III 外） | 1(1) |
| 胞外 TM I-II-III 交界 | 1(1) |
| 内 7TMD（跨膜螺旋内） | **19(12)** — 最多 |
| TM I-III 外侧 | 1(1) |
| TM II-IV 外侧 | 3(2) |
| TM III-V 外侧 | **7(4)** |
| TM V-VI 外侧 | 1(1) |
| TM I,VI,VII 外侧 | 4(3) |
| 胞内面外 TM V-VII | 7(4) |
| 胞内面内 7TMD | 7(7) |

---

## 与项目的关系

本综述为 iGEM 2026 干实验的 GPCR 对接工作提供以下直接参考价值：

1. **AF2 结构质量的背景认知**：综述明确指出 AF2 预测的 GPCR 结构与晶体结构精度接近（可用于对接），但在激活中间态和变构口袋构象上可能存在偏差。本项目以 AF2 结构（pLDDT > 85 TM 螺旋区）作为受体输入，与文献认可的做法一致。

2. **正构结合位点残基参考**：综述提供了大量 GPCR 正构位点的关键残基（以 Ballesteros-Weinstein 编号标注），为本项目 IFP 分析中判断哪些残基属于"期望接触"提供了跨受体的结构参考框架。

3. **对接结果解读的背景知识**：文中关于 7TMD 内部口袋（TM2/3/5/6/7 之间的锥形腔）作为大多数正构小分子结合位点的描述，与本项目对 GprC 和 Gpr3 配体结合口袋的对接结果定性一致。

4. **偏向信号与突变分析**：μOR 案例（fentanyl vs oliceridine 的 β-arrestin 接触面积差异）展示了如何从结构角度量化偏向效应，对未来讨论 GprC 突变体功能影响（如 R6.45A）提供了类比框架。

5. **变构位点的多样性提示**：综述指出 GPCR 中至少存在 11 个不同变构结合口袋，其中多个未被系统开发。对于 GprC 这类孤儿样真菌 GPCR，正构结合口袋是目前唯一已知的计算对接靶点，变构位点有待探索。

6. **化学空间与配体设计**：文中 bitopic ligand 设计思路（正构 anchor + 变构 driver）对未来优化 ascaroside 类配体与 GprC 的结合亲和力和选择性具有概念参考价值。

> 注意：本综述描述的均为人类/哺乳动物 GPCR（Class A-F），本项目靶向的 GprC 是真菌 GPCR，序列同源性较低。结构原理和对接方法论可类比，但具体残基保守性数据不可直接套用。

---

## 关键引用

1. **Rasmussen et al. (2011)** — 首个 GPCR-G 蛋白复合物晶体结构（β2AR-Gs），*Nature* 477, 549–555。(*文中引用 #36*)

2. **Koehl et al. (2018)** — 首个 cryo-EM GPCR-G 蛋白复合物结构（μOR-Gi），*Nature* 558, 547–552。(*文中引用 #39*)

3. **Huang et al. (2020)** — AlphaFold 预测 GPCR 结构的评估，*Acta Pharmacol. Sin.* 42, 1451–1461。(*文中引用 #446*)

4. **Jumper et al. (2021)** — AlphaFold2 蛋白结构预测，*Nature* 596, 583–589。(*文中引用 #443*)

5. **Liu et al. (2020)** — LSN3160440 与 GLP-1R-Gs 的 cryo-EM 结构（PAM），*Nature* 587, 499–504。(*文中引用 #180*)

6. **Isberg et al. (2016)** — GPCRdb：GPCR 数据库及 Ballesteros-Weinstein 编号系统，*Nucleic Acids Res.* 44, D356–364。(*文中引用 #6*)

7. **Fronik et al. (2017)** — 双表位配体（Bitopic ligands）在 GPCR 药物发现中的机遇与挑战，*Pharmacol. Ther.* 119, 105–116。(*文中引用 #26*)

8. **Hauser et al. (2021)** — GPCR 结构学方法：cryo-EM 的突破，*Trends Biochem. Sci.* 46, 479–491。(*文中引用 #31*)

---

## 版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-10 | v1.0 | 初始生成，基于全文 43 页完整阅读 |
