# Bai et al. 2022 — 文献总结

> **完整标题**: Ric8 acts as a regulator of G-protein signaling required for nematode-trapping lifecycle of *Arthrobotrys oligospora*
> **期刊**: *Environmental Microbiology*
> **DOI**: 10.1111/1462-2920.15735
> **作者**: Na Bai, Guosheng Zhang, Wenjie Wang, Huihua Feng, Xuewei Yang, Yaqing Zheng, Le Yang, Meihua Xie, Ke-Qin Zhang\*, Jinkui Yang\*（#共同第一作者）
> **机构**: State Key Laboratory for Conservation and Utilization of Bio-Resources & Key Laboratory for Microbial Resources of the Ministry of Education, School of Life Sciences, Yunnan University, Kunming 650091, China

---

## 核心发现（5-10 bullets，含数据）

- **AoRic8 是 *A. oligospora* 捕陷能力的绝对必要因子**：ΔAoric8 三个独立缺失突变株（ΔAoric8-23、ΔAoric8-38、ΔAoric8-39）在线虫诱导 48 hpi 时完全无法形成任何捕陷器（adhesive network），导致线虫捕获率为 0%；而野生型（WT）在 12/24/36/48 hpi 时分别捕获 14.3%、49.1%、78.6%、88.6% 的线虫。
- **AoRic8 仅与 Gα1 互作，不与 Gα2 或 Gα3 互作**：酵母双杂交（Y2H）证实 AoRic8—AoGα1 直接互作，并进一步激活 cAMP/PKA 通路（AoPka、AoSom1、AoStuA）；这与其他丝状真菌（*N. crassa* 与 Gna-1/Gna-3 互作、*M. oryzae* 与 MagB 互作）存在物种特异性差异。
- **cAMP 水平显著降低**：ΔAoric8 突变株胞内 cAMP 浓度仅为 52–97.5 fmol/mL，而 WT 在第 3 天为 806 fmol/mL 并在后续升至约 1,640–1,745 fmol/mL（约 2 倍增加）；腺苷酸环化酶基因 *Aoacy* 在突变株中同步下调（尤其第 3、7 天）。
- **菌丝生长与产孢严重受损**：ΔAoric8 在 TG 培养基上菌落直径较 WT 缩减 2–5 倍；孢子畸形率从 2.3%（WT）升至 30%；产孢量下降 88.3%；孢子萌发显著减慢，在 40 h 延长培养后萌发率仍无法恢复至正常水平，提示孢子活力受损。
- **细胞形态与分隔异常**：ΔAoric8 菌丝细胞长度缩短（24.9 μm vs WT 的 59.5 μm），隔膜数增多，出现肿胀细胞；TEM 显示成熟菌丝中脂滴（LDs）减少、液泡数量增多，且内菌丝（intrahyphal hyphae）数量更多。
- **应激耐受性下降**：ΔAoric8 对 0.2 M NaCl（抑制增加 46.2–50.2%）、0.02% SDS（32.4–33.3%）、0.05 mM menadione（60.5–63.3%）和 5 mM H₂O₂（53.1–53.5%）均较 WT 更敏感；抗氧化酶（*gluT*、*thi*、*cat1*、*gluR*、*per1*）及细胞壁合成酶（*chi1*、*chi2*、*gls*、*glu*）相关基因在突变株中下调。
- **胞吞作用受阻**：FM4-64 染色显示 WT 在 10 min 内完成内吞并标记内体/液泡，而 ΔAoric8 菌丝仅细胞壁附近膜结构被染色，提示胞吞功能缺陷。
- **转录组分析揭示大规模基因重排**：RNA-seq（样本收集于线虫诱导后 0、12、24、36 hpi）平均每样本获得 5,220 万 clean reads（Q30 92.3–94.9%）；在 12 hpi 差异表达基因数最多（上调 2,023 个、下调 1,765 个）；上调基因富集于细胞周期、DNA 复制与重组（KEGG），下调基因富集于核糖体、氧化磷酸化、过氧化物酶体和脂肪酸降解。
- **代谢组学显示次生代谢产物大规模下调**：LC-MS 分析显示 ΔAoric8 突变株中 8,314 个化合物下调、444 个上调（P < 0.05）；下调化合物富集于次生代谢产物合成（399 个）、UTQB（100 个）和氨基酸合成（53 个）；arthrobotrisins A 和 B（寡聚孢素/oligosporon 类抗生素）丰度降低，对应基因簇 AOL_s00215g 在突变株中多个基因被下调。

---

## 实验方法（表格）

| 方法 | 具体操作 |
|------|---------|
| **基因鉴定** | 以 *N. crassa* Ric8（XP_963944）和 *M. oryzae* Ric8（XP_003716129）为查询序列搜索 *A. oligospora* 基因组；InterProScan 功能域分析；ClustalX 1.83 比对，MEGA7 邻接法构建系统发育树 |
| **基因敲除** | 双同源重组策略（modified yeast cloning procedure）；筛选标记 hph（hygromycin，200 μg/mL）；PCR（引物 338yz-5f/3r）和 Southern blot（KpnI 酶切，North2South 化学发光试剂盒）验证；获得 3 个阳性敲除株（ΔAoric8-23、38、39） |
| **捕陷实验** | WA 培养基 28°C 培养 3–4 d；加入约 300 条 *C. elegans*（N2 株）诱导；12 hpi 和 48 hpi 显微观察，统计捕陷器密度（个/cm²）和线虫捕获率 |
| **酵母双杂交（Y2H）** | BD Matchmaker 试剂盒（Clontech）；bait 质粒 pGBKT7（Aoric8、Aopka、Aosom1），prey 质粒 pGADT7（AoGa1、Aosom1、AostuA）；共转化 AH109 株；SD/-4 + X-α-gal/Aba 培养基验证蓝色显色 |
| **生长与产孢分析** | TG、TYGA、PDA、WA、CMA 培养基观察菌落形态；CMY 培养基 14 d 后用 CFW（calcofluor white）染色观察孢子；统计产孢量和萌发率 |
| **应激耐受** | TG 培养基补充 NaCl（0.2 M）、SDS（0.02%）、menadione（0.05 mM）、H₂O₂（5 mM）等；测量菌落直径计算相对生长抑制率 |
| **cAMP 测定** | TG 液体培养 3–7 d 收集菌丝，液氮冻存；direct cAMP ELISA kit（Enzo Life Sciences）定量 |
| **胞吞检测** | FM4-64 脂质染料（Biotium）孵育 1 min 和 10 min，荧光显微镜（Nikon）观察 |
| **TEM 分析** | PDA 28°C 培养 1 d 和 3 d 的菌丝；2.5% 戊二醛固定；透射电子显微镜观察细胞器 |
| **蛋白酶活性** | LMZ 液体培养基 28°C 培养 6 d；上清液点种酪蛋白平板，观察透明圈；RT-PCR 分析 7 个丝氨酸蛋白酶基因 |
| **转录组（RNA-seq）** | 线虫诱导后 0、12、24、36 hpi 收样；Illumina HiSeq 4000 测序；TopHat 比对；RSEM/TPM 定量；DEG 阈值 |log2 ratio| ≥ 1，adjusted P < 0.05；GO 和 KEGG 富集分析（Bonferroni 校正 P < 0.05） |
| **代谢组（LC-MS）** | PDA 培养 7 d 后收集培养液；乙酸乙酯提取，甲醇复溶；Thermo Dionex Ultimate 3000 UHPLC + Q Exactive 高分辨质谱；Compound Discoverer 3.0 非靶向分析 |
| **RT-PCR** | TRIzol 提取 RNA，PrimeScript RT 试剂盒反转录；Primer3 设计引物；β-Tubulin（AOL_s00076g640）为内参；2⁻ᐩᐩCt 法计算相对转录水平 |

---

## 关键数据

### 捕陷器形成与线虫捕获

- WT 在 24 hpi 和 48 hpi 分别形成约 11 个/cm² 和 20 个/cm² 成熟捕陷器（含 ≥5 个菌丝环）
- WT 在 12、24、36、48 hpi 线虫捕获率分别为 14.3%、49.1%、78.6%、88.6%
- ΔAoric8 三株突变体在 48 hpi 时捕陷器形成数量为 0，线虫捕获率为 0%

### AoRic8 蛋白特性

- 编码基因：AOL_s00215g338；515 氨基酸；预测等电点 5.11；分子量 56.2 kDa
- 与 NcRic8 序列同一性 35.3%，与 MoRic8 为 33.8%；与其他 NT 真菌同源物同一性 59.6–89.3%
- InterProScan 鉴定含 conserved guanine nucleotide exchange factor（IPR019318）和两个 synembryn 结构域（IPR008376）
- 系统发育：真菌 Ric8 同源物聚为 Clade A，动物同源物聚为 Clade B

### cAMP/PKA 通路

- WT 第 3 天 cAMP 806 fmol/mL，后升至 1,640–1,745 fmol/mL
- ΔAoric8 整个培养期 cAMP 仅 52–97.5 fmol/mL（降低 3.0–11.3%，多时间点均显著）
- 腺苷酸环化酶基因 *Aoacy* 在突变株第 3 和第 7 天显著下调

### 转录组 DEG 数量

| 时间点 | 上调基因数 | 下调基因数 |
|--------|-----------|-----------|
| 0 hpi  | >1,000    | >1,000    |
| 12 hpi | 2,023     | 1,765（最多）|
| 24 hpi | >1,000    | >1,000    |
| 36 hpi | >1,000    | >1,000    |

- PCA 分析：PCA1 贡献率 46.65%，PCA2 贡献率 17.82%

### 代谢组

- ΔAoric8 vs WT：下调化合物 8,314 个，上调 444 个（P < 0.05）
- 下调化合物富集：次生代谢产物合成（399 个）、UTQB（100 个）、氨基酸合成（53 个）
- Oligosporons-arthrobotrisins A 和 B 丰度降低；基因簇 AOL_s00215g 多基因下调

---

## 与项目的关系

本文直接研究 *A. oligospora*（iGEM 项目核心物种之一，Gpr2/Gpr3 宿主）的 G 蛋白信号通路上游调控节点，与项目高度相关：

1. **信号通路 ODE 建模的上游节点**：AoRic8 作为非受体 GEF，位于 GPCR（如 Gpr2/Gpr3）→ Gα → cAMP/PKA 通路的激活环节。本文证明 AoRic8—AoGα1—腺苷酸环化酶—cAMP 这条轴线对捕陷行为不可缺少，可为 ODE 模型中 Gα 激活速率常数和 cAMP 产生模块提供定性约束：cAMP 从 ~50 fmol/mL（缺 Ric8）到 ~1,700 fmol/mL（WT）的量级差异，提示该节点是通路的关键放大步骤。

2. **Gα 亚型选择性**：AoRic8 仅与 AoGα1 互作（不与 Gα2/Gα3 互作）——这一 *A. oligospora* 特有的选择性为 Gpr2/Gpr3 下游 Gα 偶联模型的构建提供了参考（若 Gpr2/Gpr3 也优先偶联 Gα1，则与 Ric8 信号汇聚于同一轴线）。

3. **lifestyle switch（捕陷开关）定量化**：WT 捕获曲线（12 h: 14.3% → 48 h: 88.6%）可作为 ODE 模型中"捕陷触发阈值"和"线虫检测动力学"的拟合参考数据点。

4. **转录组数据资源**：NCBI 登录号 PRJNA693116 包含 0/12/24/36 hpi 的 WT vs ΔAoric8 RNA-seq 数据，可供后续提取捕陷相关基因的动态表达模式。

> 注意：本文未涉及 ascaroside 配体感知实验，GprC 属 *A. flagrans* 而非本文研究的 *A. oligospora*；上述关联为通路层面的结构性参考，不代表本文直接研究相同受体。

---

## 关键引用（6条）

1. **Miller et al. (2000)** RIC-8 (Synembryn): a novel conserved protein that is required for G(q)alpha signaling in the *C. elegans* nervous system. *Neuron* **27**: 289–299. — Ric8 的原始发现论文，确立其为 G 蛋白信号调控子。

2. **Hinrichs et al. (2012)** Ric-8: different cellular roles for a heterotrimeric G-protein GEF. *J Cell Biochem* **113**: 2797–2805. — 综述 Ric8 作为 GEF 的作用机制：结合 Gα-GDP，催化 GDP→GTP 交换，形成无核苷酸过渡态复合物。

3. **Wright et al. (2011)** [*N. crassa* Ric8 研究，引文号 Wright et al., 2011; Eaton et al., 2012] — 丝状真菌中 Ric8 缺失导致菌丝生长和分生孢子萌发缺陷，并与 Gna-1/Gna-3 互作。

4. **Li et al. (2010)** MoRic8 is a novel component of G-protein signaling during plant infection by the rice blast fungus *Magnaporthe oryzae*. *Mol Plant Microbe Interact* **23**: 317–331. — MoRic8 敲除使 *M. oryzae* 丧失致病力（附着胞形成缺陷），类比 AoRic8 敲除丧失捕陷能力。

5. **Yang et al. (2020)** [*A. oligospora* Gβ 亚基研究] — 证实 Gβ 亚基缺失几乎完全消除 *A. oligospora* 捕陷能力，与本文 AoRic8 结果平行，共同支持 G 蛋白信号通路对捕陷的核心调控作用。

6. **Ma et al. (2021)** Functional analysis of seven regulators of G protein signaling (RGSs) in the nematode-trapping fungus *Arthrobotrys oligospora*. *Virulence* **12**: 1825–1840. — RGS 蛋白（G 蛋白信号负调控子）在同一物种的研究，与 AoRic8（正调控）形成通路调控对称。
