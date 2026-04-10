# Ma et al. 2021 — 文献总结

> **完整标题**: Functional analysis of seven regulators of G protein signaling (RGSs) in the nematode-trapping fungus *Arthrobotrys oligospora*
> **期刊**: *Virulence*, 2021, Vol. 12, No. 1, pp. 1825–1840
> **DOI**: 10.1080/21505594.2021.1948667
> **作者**: Ni Ma, Yining Zhao, Yunchuan Wang, Le Yang, Dongni Li, Jiangliu Yang, Kexin Jiang, Ke-Qin Zhang, Jinkui Yang（前两位作者同等贡献）
> **机构**: State Key Laboratory for Conservation and Utilization of Bio-Resources, Yunnan University, Kunming, China; Institute of Medical Biology, Chinese Academy of Medical Sciences & Peking Union Medical College, Kunming, China

---

## 核心发现（5–10 bullets，含数据）

- 在 *A. oligospora* 基因组中鉴定出 7 个 RGS 蛋白（AoRgsA、AoRgsB、AoRgsB2-1/2/3、AoFlbA、AoRgsC），分别归属三个进化枝（clade I–III），功能分析表明它们在菌落生长、孢子发生、捕食陷阱形成与致病性方面发挥多效调控作用。
- 删除 *AoFlbA*（clade I，分子量最大，852 aa，含 DEP 域）导致无法产生分生孢子和捕食陷阱，并使胞内 cAMP 水平显著升高（WT 的 3.6–7.2 倍，测定于 3、5、7 d），是所有突变体中表型最严重的。
- 删除 *AoRgsB* 和 *AoRgsB2-1* 分别使菌丝生长在 PDA/TYGA 培养基上受到明显抑制；删除 *AoRgsC*（1272 aa，含 TM、PX、PXA、Nexin_C 域）使捕食陷阱数量减少至 WT 的 0.08 倍，捕食线虫效率（48 h）仅为 WT 的 43.1%。
- 所有 7 个 *ΔAoRgs* 突变体捕线虫活性均有不同程度下降：WT 在 12/24/36/48 h 分别捕获 24.3%/76.0%/85.5%/92.9% 线虫，各突变体均显著低于 WT。
- 胞内 cAMP 水平检测显示，各 *ΔAoRgs* 突变体 cAMP 均高于 WT，确认 RGS 蛋白整体负调控 cAMP 信号；*ΔAoFlbA* 的 cAMP 升高幅度远超其他突变体。
- RNA-seq（*ΔAoFlbA* vs WT）在 4 个诱导时间点（0/6/12/24 h）共鉴定出 2713–1852 个 DEGs；GO/KEGG 富集显示，0 h 和 6 h 氨基酸代谢与生物合成通路显著上调；12 h 氧化还原酶活性与跨膜转运通路显著上调；24 h 核糖体生物合成相关通路上调。
- G 蛋白信号组分基因表达分析（RT-PCR，0–48 h）显示，*AoFlbA* 缺失后 *StuA* 和 *Gγ* 表达在 12–36 h 显著下调（*Gγ* 表达在 12/24/36 h 分别降低 11.6/5.6/6.7 倍），*Ga1、Ga2、Ga3* 在陷阱诱导期总体也呈下调趋势。
- 在 *A. oligospora* 基因组中鉴定出至少 42 个 *Gas1* 家族基因（同源于 *A. nidulans* Eel16/Elg16H），数量远多于粘性柱产生的 NT 真菌（≤35 个）；*Gas1-127* 和 *Gas1-178* 缺失分别使孢子产量降低 33.2% 和 76.1%，陷阱数量降低 57.6% 和 43.5%（P < 0.05）。
- *AoFlbA* 是 *A. oligospora* 的一个关键 RGS，在陷阱形成中下调氨基酸代谢与生物合成（可能通过调节氨基酸代谢参与陷阱结构物质合成），并参与调控细胞膜完整性相关基因的表达。

---

## 实验方法（表格）

| 方法 | 简述 |
|------|------|
| 基因序列与聚类分析 | 以 *A. nidulans*、*M. oryzae*、*S. cerevisiae* 的 RGS/RGS-like 蛋白为 query，从 *A. oligospora* 基因组检索；InterProScan 预测保守域；Mega v7.0 构建 NJ 树 |
| 载体构建与基因敲除 | 同源重组策略，PCR 扩增靶基因上下游 + *hph* 抗性盒；原生质体转化；SC-Ura 和 PDAS 筛选；PCR 及 Southern blot 确认 |
| 菌落形态与生长速率 | PDA/TYGA/TG 平板，28°C，每 24 h 测菌落直径 |
| 孢子产量测定 | CMY 培养基，28°C，14 d，血细胞计数板计数 |
| 应激耐受测试 | TG 平板添加 SDS（0.01–0.03%）、NaCl（0.1–0.3 M）、H₂O₂（5–15 mM），计算相对生长抑制率（RGI） |
| 陷阱形成与捕线虫活性 | 水琼脂平板接种 ~3×10⁴ 分生孢子，4 d 后加入 ~300 条线虫，每 12 h 统计捕获数量 |
| 蛋白水解活性测定 | PD 肉汤 28°C 振荡培养 7 d，脱脂牛奶平板检测蛋白水解环 |
| 胞内 cAMP 定量 | PD 培养基 28°C，3/5/7 d 收获菌丝，HCl 裂解 + 液氮冻存 + ELISA 试剂盒（Enzo Life Sciences）检测 |
| RT-PCR & RNA-seq | 总 RNA 提取，β-tubulin 内参；RNA-seq 文库构建（诱导 0/6/12/24 h），平均 45.29 M clean reads/样品；DEGs 以 TPM 值比较；GO/KEGG 富集 |
| 荧光显微镜观察 | Calcofluor White 染细胞壁与隔膜，DAPI 染核 |
| *Gas1* 家族分析 | 以 *A. oligospora* Gas1 基因为 query，GenBank 检索 NT 及其他真菌中的同源基因，构建系统发育树；RT-PCR 验证转录水平 |

---

## 关键数据（分小节）

### 1. 菌落/菌丝生长

- *ΔAoFlbA* 和 *ΔAoRgsB2-1* 在所有三种培养基上菌落直径均缩小。
- *ΔAoRgsB* 在 TYGA 菌落直径减小；*ΔAoRgsC* 菌落直径略有增大。
- *ΔAoRgsB2-1* 产生致密菌丝，*ΔAoRgsB* 产生稀疏气生菌丝。

### 2. 分生孢子产量

- *ΔAoRgsB* 孢子产量降低 83.3%（最大降幅）；*ΔAoFlbA* 完全丧失产孢能力。
- *ΔAoRgsA*、*ΔAoRgsB2-2*、*ΔAoRgsB2-3* 孢子产量分别增加 17.3%、18.2%、28.8%。

### 3. 应激耐受

- *ΔAoFlbA*（RGI 71.34% on 15 mM H₂O₂）和 *ΔAoRgsB2-1*（62.88%）显著低于 WT（83.3%）——抗氧化能力下降。
- 0.1 M NaCl 降低 *ΔAoRgsB* 和 *ΔAoFlbA* 的 RGI，但增加其他突变体的 RGI。

### 4. 陷阱形成与线虫捕获

- *ΔAoRgsC*：48 h 捕获率仅 43.1% vs WT 92.9%；陷阱数 0.08 倍于 WT。
- *ΔAoFlbA*：48 h 无陷阱形成，线虫捕获/降解能力丧失。
- *ΔAoRgsB* 和 *ΔAoRgsB2-1* 蛋白水解活性最低；*ΔAoRgsB2-2* 蛋白水解活性略有上升。

### 5. 胞内 cAMP

- *ΔAoFlbA* cAMP 水平在 3/5/7 d 分别为 WT 的 3.6/3.3/7.2 倍（最高）。
- 所有其他 *ΔAoRgs* 突变体 cAMP 均高于 WT，表明 RGS 蛋白负调控 cAMP 积累。

### 6. 转录组（*ΔAoFlbA* vs WT）

- 0 h/6 h 上调：氨基酸代谢（alpha-/aspartate-/sulfur 家族）和生物合成、氧化还原酶活性。
- 12 h 上调：氧化还原过程、氧化还原酶活性、跨膜转运；膜内在成分通路下调。
- 24 h 上调：核糖体生物合成；氧化还原酶活性上调持续。
- KEGG 上调路径（0/12 h）：核糖体生物合成（真核）、半胱氨酸与蛋氨酸代谢、赖氨酸生物合成。

### 7. Gas1 家族基因

- *A. oligospora* 含 42 个 *Gas1* 同源基因，远多于其他 NT 真菌（产黏性柱）及非 NT 真菌。
- *ΔGas1-127*：孢子产量 ↓33.2%，陷阱数 ↓57.6%。
- *ΔGas1-178*：孢子产量 ↓76.1%，陷阱数 ↓43.5%。

---

## 与项目的关系

本文直接研究了 *A. oligospora* 中 G 蛋白信号通路的负调控层——RGS 蛋白家族，与项目核心受体 Gpr2/Gpr3（同属 *A. oligospora*）的下游信号机制高度相关。

**具体关联点**：

1. **Gα 信号通路 ODE 建模的参数基础**：本文定量测量了各 *ΔAoRgs* 突变体的胞内 cAMP 水平（pmol/mg，3–7 d），提供了 Gα–cAMP–PKA 轴在 NTF 中的生理范围数据，可用于 ODE 模型中 RGS 对 Gα 的 GTP 水解速率参数约束。

2. **AoFlbA 是 Gpr2/Gpr3 下游 cAMP 信号的关键负调控节点**：*ΔAoFlbA* cAMP 大幅升高（WT 的 3–7 倍）揭示了 AoFlbA 对 Gα 活性的强效抑制，表明 Gpr2/Gpr3 激活后的信号衰减主要依赖 AoFlbA。若 ODE 模型需要描述信号终止/衰减动力学，AoFlbA 的 GPA 活性是关键参数。

3. **信号通路组分表达量数据**：RT-PCR 数据（Fig. 4e）展示了 *Pka、Hag1、Camk、StuA、SomI、Ga1、Ga2、Ga3、Gβ、Gγ* 在陷阱诱导 0–48 h 的动态变化，可作为 ODE 模型初始条件和时序约束的参考。

4. **Gas1 家族与 ascaroside 感知的潜在联系**：*Gas1* 家族基因在 *A. oligospora* 中扩张（42 个），并在陷阱形成中起关键作用，提示线虫感知（ascaroside 诱导）可能激活 Gpr2/Gpr3 后经 G 蛋白 → RGS/cAMP → Gas1 家族这一级联通路调控捕食行为。

5. **注意区分**：本文研究对象为 *A. oligospora*，而项目的 GprC 来自 *A. flagrans*，两者在基因组背景上存在差异；引用本文数据时应注明物种来源。

---

## 关键引用（8 条）

1. **[1] Li LD et al.** Annu Rev Microbiol. 2007;61:423–452. — 丝状真菌中异源三聚体 G 蛋白信号综述（RGS 功能背景）。
2. **[2] Wang Y et al.** Appl Microbiol Biotechnol. 2013;97(18):7977–7987. — 真菌 RGS 表征与 G 蛋白信号调控综述。
3. **[6] Liebmann B et al.** Infect Immun. 2004;72(9):5193–5203. — *A. fumigatus* 中 cAMP 依赖蛋白激酶网络调控发育与毒力（AoFlbA 参照背景）。
4. **[16] Heterotrimeric YI. G protein signaling and RGSs in *A. nidulans*.** J Microbiol. 2006;44(2):145–154. — *A. nidulans* G 蛋白与 RGS 综述，提供进化树参照。
5. **[21] Ji X, Yu Z, Yang J et al.** iScience. 2020;23(5):101057. — 病原基因扩张驱动 NT 真菌适应性，Gas1 家族背景。
6. **[22] Yang JK et al.** PLoS Pathog. 2011;7(9):e1002179. — *A. oligospora* 基因组与蛋白质组学分析（本文 RGS 鉴定的基因组依据）。
7. **[37] （cAMP ELISA 方法参考文献）** — 胞内 cAMP 定量方法原始文献（本文引用但未在摘录段落中列出完整条目，见原文参考文献 [37]）。
8. **[48]（*A. fumigatus* ΔRgsA 表型参考）** — 对应 *A. fumigatus* 中 RgsA 敲除导致径向生长增加、产孢增加，与 *A. oligospora* ΔAoRgsA 行为形成跨物种比较依据（见原文 Discussion）。
