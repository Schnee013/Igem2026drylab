# Juan et al. 2026 — 文献总结

> **完整标题**: Ammonium Transporters Govern Nutrient Sensing and Trap Induction in the Nematode-Trapping Fungi *Arthrobotrys oligospora*
> **期刊**: bioRxiv preprint（2026年2月9日）
> **DOI**: https://doi.org/10.64898/2026.02.06.704490
> **作者**: Sheng-Chian Juan¹²³, Hillel T. Schwartz³, Yen-Ping Hsueh¹²³ \*
> **机构**:
> - ¹ Institute of Molecular Biology, Academia Sinica, Taipei 115, Taiwan
> - ² Genome and Systems Biology Degree Program, Academia Sinica and National Taiwan University, Taipei 106, Taiwan
> - ³ Department of Complex Biological Interactions, Max Planck Institute for Biology Tübingen, 72076 Tübingen, Germany
> **通讯作者**: Yen-Ping Hsueh (ping.hsueh@tuebingen.mpg.de)
> **关键词**: nematode-trapping fungi; *Arthrobotrys oligospora*; ammonium transporter; nutrient sensing

---

## 核心发现

- *A. oligospora* 基因组中存在三个铵转运体（ammonium transporter）基因，命名为 **MEP1**、**MEP2**、**MEP3**，基于与 *S. cerevisiae* ScMep2 的序列同源性鉴定。
- 系统发育分析显示 **AoMep1 与低亲和力/高容量型转运体**（ScMep1、ScMep3）聚类，而 **AoMep2 和 AoMep3 与高亲和力/低容量型转运体**（ScMep2）聚类。
- 时间序列转录组分析表明三个 *MEP* 基因在线虫暴露后被诱导上调：*MEP1* 在暴露 **2 小时**达到峰值后下降，*MEP2* 在 **4 小时**达到峰值，*MEP3* 则在整个捕食过程中持续低水平表达；高浓度铵（10 mM 或 50 mM NH₄Cl）抑制三个基因的表达。
- 基因敲除实验证明 **Mep1 和 Mep3 是捕陷器诱导所必需的**：低氮条件下，*mep1* 和 *mep3* 单缺失突变体的捕陷器密度约为野生型的一半（>400 个/cm²降至约半数），而 *mep2* 突变体捕陷器数量与野生型相当；所有双缺失突变体的表型与含 *mep1* 或 *mep3* 的单缺失突变体相似。
- 线虫存活率实验显示：12 小时后，野生型和仅缺失 *MEP2* 的突变体中约 **25% 的线虫存活**，而缺失 *MEP1* 或 *MEP3* 的突变体中存活率**超过 50%**；表明 Mep1 和 Mep3 影响捕食效率。
- *mep* 突变体形成的捕陷器**形态与功能正常**：每个环的细胞数（野生型均值 5.28 ± 0.15；n=25）在任何单缺失或双缺失突变体中均无显著差异；捕获率实验（200 个线虫，10 分钟）显示所有菌株均在 10 分钟内捕获近全部线虫。
- **mep1 缺失突变体对铵离子具有部分耐受性**：在含 10 mM 铵的 LNM 培养基上，野生型菌落较小且菌丝紧密，而 *mep1* 缺失株菌落更大且菌丝排列更疏松；*mep1* 突变体在高铵条件下仍能产生与低氮条件下同等数量的捕陷器。
- 铵补充诱导各 *MEP* 基因的条件依赖性交叉调控（condition-dependent cross-regulation）：在氮限制条件下，单缺失或双缺失突变体中其余 *MEP* 基因表达量变化不大；而在 10 mM NH₄Cl 存在时，缺失 *MEP1* 的菌株中其余 *MEP* 基因显著上调至野生型水平或更高，尤其以 *MEP3* 上调最为明显。
- 酵母异源表达（heterologous expression）实验证明 **AoMep2 和 AoMep3 具有功能保守性**：在 *S. cerevisiae mep2* 突变体（MLY108a/α）中表达 *AoMEP2* 或 *AoMEP3* 可完全恢复低铵条件下的拟假菌丝（pseudohyphal）生长，而 *AoMEP1* 仅提供有限互补；在 *mep1 mep2 mep3* 三缺失酵母突变体（MLY131a/α）中，*AoMEP2* 或 *AoMEP3* 表达可恢复在 25 μM 硫酸铵的 SLADG 培养基上的生长，而 *AoMEP1* 表达甚至加剧了生长缺陷。

---

## 实验方法

| 方法类别 | 具体方法 | 关键参数 |
|----------|----------|----------|
| 菌株构建 | 同源重组基因敲除（ku70 背景） | NAT1/GentR 抗性筛选；PCR + Southern blotting 验证 |
| 捕陷器计数 | 低营养培养基（LNM）诱导；加入 60 个 *C. elegans* N2 L4 幼虫 | 6 h 暴露后移除线虫，24 h 后 40× 立体显微镜拍照，归一化为 traps/cm² |
| 铵处理实验 | LNM 补充 10 mM 或 50 mM NH₄Cl | 2 天预培养后加线虫 |
| 线虫存活率实验 | 3 cm LNM 平板，80 条 N2 young-adult | 每 2 h 计数爬行线虫，共 12 h；存活率 = 活动线虫数/80 |
| 捕获率实验 | 5 cm LNM 平板，200 条 N2 young-adult | 10 分钟内计数未捕获线虫（30 条成虫），捕获率 = 存活活动线虫数/30 |
| 捕陷器形态 | 0.1% SCRI Renaissance Stain 2200（SR2200）细胞壁染色 | ZEISS AxioObserver Z1，40× 物镜；Fiji ImageJ 图像处理 |
| 基因表达分析 | qPCR（RT-qPCR） | 参照基因 GPD1；2^−ΔCT 法；三重复 |
| 生物信息学分析 | Blast2GO；MAFFT v7 序列比对；MEGA11 系统发育树（NJ 法，3000 bootstrap）；TMHMM v2.0 跨膜结构域预测 | JTT 矩阵 |
| 蛋白结构预测 | AlphaFold；Foldseek 结构比对；PyMOL 可视化 | — |
| 酵母功能分析 | AoMEP cDNA 克隆至 pRS42N_OE（PGK1 启动子）；电穿孔转化 | SLADG 培养基（25 μM 硫酸铵）；ZEISS Stemi 305，80× 拍照 |

---

## 关键数据

### 捕陷器诱导表型

- 野生型（低氮条件）：>400 traps/cm²
- *mep1* 单缺失、*mep3* 单缺失：约为野生型的 **50%**
- *mep2* 单缺失：与野生型无显著差异
- 所有双缺失突变体（*mep1 mep2*、*mep2 mep3*、*mep1 mep3*）：表型与含 *mep1* 或 *mep3* 的单缺失相当，未见进一步加重
- 10 mM NH₄Cl 补充后：*mep1* 突变体在高铵条件下产生的捕陷器数量与低氮条件下相当，而野生型显著减少

### 线虫存活率

- 12 小时后野生型存在下存活率：~25%
- *mep2* 缺失突变体存在下：约同野生型（~25%）
- *mep1* 缺失突变体存在下：>50%
- *mep3* 缺失突变体存在下：>50%

### 捕陷器形态

- 野生型每环细胞数：5.28 ± 0.15（SEM），n = 25
- 所有 *mep* 单/双缺失突变体：无显著差异

### MEP 基因表达时间模式（线虫暴露后，时间序列转录组）

- *MEP1*：2 h 峰值后下降
- *MEP2*：4 h 峰值
- *MEP3*：整个过程持续低水平

### 铵浓度对基因表达的影响（qPCR）

- 无氮培养基：MEP1 > MEP2 > MEP3（表达量从高到低）
- 10 mM 或 50 mM NH₄Cl：三个基因均被抑制

### 酵母互补实验

- *S. cerevisiae mep2* 突变体（MLY108a/α）：AoMEP2 或 AoMEP3 完全恢复拟假菌丝生长；AoMEP1 仅部分互补
- *S. cerevisiae mep1 mep2 mep3* 三缺失（MLY131a/α，25 μM 铵 SLADG 培养基）：AoMEP2 或 AoMEP3 恢复生长；AoMEP1 未能恢复（反而加剧缺陷）

---

## 与项目的关系

本文直接揭示了 *A. oligospora* 中**氮感知（ammonium sensing via Mep transporters）与捕陷器诱导之间的因果关系**，并明确了氮信号与猎物来源信号（ascaroside）在捕陷器调控中的分工：

1. **氮信号与 ascaroside 感知相互独立**：本文的核心模型是，铵转运体（Mep1/Mep3）作为**氮感知模块**上游于捕陷器发育决策，而 GPCR（Gpr2/Gpr3，感知 ascaroside）代表另一条信号输入。两者均可触发捕陷器，但机制独立。这为 iGEM 2026 项目的**信号通路 ODE 建模**提供了两条相互独立输入的实验依据：ODE 模型中氮状态（intracellular ammonium）节点与 ascaroside–GPCR 节点不应在上游合并，而应作为并行输入。

2. **高铵条件抑制捕陷器的机制阐明**：已知氮补充抑制 *A. oligospora* 捕陷器形成；本文将该机制归因于 Mep1 介导的铵内流激活氮充足信号（nitrogen sufficiency signaling），从而压制饥饿相关信号通路。这对 ODE 模型中"氮充足"节点的参数化有参考价值。

3. **Mep 转运体功能保守**：AoMep2 和 AoMep3 与 ScMep2 功能同源（均为高亲和力型，参与感知而非仅转运），提示 AoMep2/3 可能也具有 transceptor（transporter + receptor）功能，类似于 *S. cerevisiae* ScMep2 激活 MAPK 通路的方式。这一机制细节若进一步确认，可能构成氮信号通路 ODE 模型的节点之一。

4. **本文不直接涉及 Gpr2/Gpr3 功能**（ascaroside GPCR）：*mep* 突变体中 Gpr2/Gpr3 通路未受干扰，捕陷器在 *mep1* 或 *mep3* 缺失背景下虽减少但仍可被诱导，说明 Gpr2/Gpr3 信号通路保持完整。

5. **生物防治背景**：文章指出农业高氮环境（化肥）是 NTF 生物防治效率下降的原因之一；理解氮感知机制有助于设计对高氮不敏感的工程菌株。

---

## 关键引用

1. **Hsueh et al. 2013** — *A. oligospora* 窃听线虫信息素触发捕陷器。*Current Biology* 23, 83–86. (ref 16)
2. **Kuo et al. 2024** — *A. oligospora* 通过 GPCR（Gpr2/Gpr3）感知 ascaroside。*Nature Microbiology* 9, 1738–1751. (ref 17)
3. **Lin et al. 2023** — 真菌捕食不同阶段所需的关键基因过程。*PLoS Biology* 21, e3002400. (ref 18)
4. **Lorenz & Heitman 1998** — ScMEP2 铵转运体调控 *S. cerevisiae* 的拟假菌丝分化。*EMBO J* 17, 1236–1247. (ref 22)
5. **Hsueh et al. 2017** — *A. oligospora* 模拟食物和信息素气味吸引猎物线虫。*eLife* 6, e20023. (ref 15)
6. **Vidal-Diez de Ulzurrun & Hsueh 2018** — 捕食性真菌与线虫相互作用综述。*Applied Microbiology and Biotechnology* 102, 3939–3949. (ref 14)
7. **Kuo, Chen & Hsueh 2020** — HOG 通路参与 *A. oligospora* 渗透压感知、捕陷器形态与分生孢子形成。*Journal of Fungi* 6, 191. (ref 28)

---

## 版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-10 | v1.0 | 初始总结，忠实于原文内容 |
