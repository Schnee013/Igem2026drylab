# Duan et al. 2025 — 文献总结

> **完整标题**: Nutrient State-Dependent Ascarosides and Nematode Immune Response Limit the Predation of *Arthrobotrys oligospora*
> **期刊**: *Microorganisms* 2025, 13, 2816
> **DOI**: https://doi.org/10.3390/microorganisms13122816
> **作者**: Jia-Hong Duan, Zhong-Kan He, Xin-Qian Gong, Qiu Zhao, Xin-Yue Tang, Cheng-Gang Zou\*, Yi-Cheng Ma\*
> **机构**: State Key Laboratory for Conservation and Utilization of Bio-Resources in Yunnan / Key Laboratory of Industrial Microbial Fermentation Engineering of Yunnan Province, Yunnan University, Kunming 650091, China; Southwest United Graduate School, Kunming 650092, China

---

## 核心发现（5-10 bullets，含数据）

- **饥饿线虫逃脱捕食的概率显著更高**：与饱食对照（CTL）相比，饥饿处理（STR，24 h无菌 NGM）的线虫周围 *A. oligospora* adhesive trap 密度和捕获比例均显著降低（trap 密度 p < 0.001，捕获率 p < 0.01）。
- **饥饿选择性下调短链 ascaroside**：LC-MS/HRMS 定量显示，STR 组中 ascr#1、ascr#3、ascr#5、ascr#9 含量显著降低（p < 0.001），而 **ascr#7 含量不变**（ns）。这四种短链 ascaroside 正是诱导 *A. oligospora* 成trap的主要化学信号。
- **ACOX 基因表达受营养状态调控**：qRT-PCR 显示饥饿显著下调 *acox-1.1*、*acox-1.2*、*acox-1.3*、*acox-1.4* mRNA，而 *acox-3* 不变。转录报告株 *acox-1.2p::GFP* 荧光强度在 STR 条件下降低（p < 0.01）。
- **acox-1.2、-1.3、-1.4 是 trap 诱导的功能性效应基因**：RNAi 敲低 *acox-1.2*、*acox-1.3*、*acox-1.4*（而非 *acox-1.1*）在饱食线虫中减少了 trap 形成和捕获数量；在饥饿线虫中进一步敲低 *acox-1.2* 不产生叠加效应（Figure S1），表明两者作用于同一通路。
- **逃避失败后，线虫依赖三条先天免疫通路存活**：筛选显示 PMK-1（p38 MAPK）、ATFS-1（线粒体 UPR 转录因子）和 FSHR-1（G 蛋白偶联受体）突变体或 RNAi 敲低后生存率显著下降（p < 0.001）；而 DAF-16/FOXO、DBL-1/TGF-β、SKN-1、XBP-1、HLH-30、EGL-30 等通路在此情境下不必要。
- **UPR^mt 被 *A. oligospora* 捕食激活，而 p38 MAPK 以基底活性为主**：*hsp-6p::GFP*（UPR^mt 标志物）荧光在暴露 *A. oligospora* 后显著升高（p < 0.001），而 *T24B8.5p::GFP*（p38 MAPK 标志物）无显著变化，提示线粒体对真菌捕食的响应更为突出。
- **营养异质性可解释 NTF 生防效果的田间变异**：短链 ascaroside 在营养匮乏土壤中选择性减少，使 *A. oligospora* trap 诱导减弱；而营养丰富区的线虫则产生更强信号，更易被捕，从而形成局部"高风险/低风险"分布格局。

---

## 实验方法（表格）

| 方法 | 关键参数 |
|------|----------|
| 饥饿处理 | 同步化年轻成虫在无菌 NGM 板 24 h（STR），对照保留 OP50（CTL）|
| 捕食实验（Predation Assay） | 100 条线虫/板，20°C，每 12 h 计数；每组 ≥3 板，3 次独立实验 |
| Ascaroside 定量（LC-MS/HRMS） | 冻干虫体，50% 甲醇提取，UHPLC-Orbitrap FTMS；EIC 窗口对应 ascr#5/9/7/1/3（m/z 70–1000） |
| qRT-PCR | TRIzol 提取 RNA，SYBR Premix Ex Taq II，2^−ΔΔCt 法，内参 *act-1* |
| RNAi 敲低 | Ahringer library 菌株（*acox-1.1/-1.2/-1.3/-1.4/-3* 等），L1 幼虫同步化喂食至成虫 |
| 生存实验（Survival Assay） | ~50 条/组，WA 板，每 12 h 判死（无咽泵/运动），log-rank (Mantel-Cox) 检验，3 次生物重复 |
| 荧光显微镜 | Zeiss Axioskop 2 Plus，ImageJ 1.47f 定量；每组 n=30 |
| 统计 | 双因素 ANOVA + Šidák 校正（多组比较）；Student's *t*-test（两组比较）；p < 0.05 显著 |

---

## 关键数据（分小节）

### Ascaroside 含量变化（STR vs CTL）

| Ascaroside | 变化 | 显著性 |
|-----------|------|--------|
| ascr#1 | 显著降低 | p < 0.001 |
| ascr#3 | 显著降低 | p < 0.001 |
| ascr#5 | 显著降低 | p < 0.001 |
| ascr#9 | 显著降低 | p < 0.001 |
| ascr#7 | 无变化 | ns |

### ACOX 基因表达（STR vs CTL，qRT-PCR）

| 基因 | 变化 | 显著性 |
|------|------|--------|
| *acox-1.1* | 显著降低 | p < 0.001 |
| *acox-1.2* | 显著降低 | p < 0.001 |
| *acox-1.3* | 显著降低 | p < 0.001 |
| *acox-1.4* | 显著降低 | p < 0.001 |
| *acox-3* | 不变 | ns |

### 免疫通路生存贡献

| 通路/基因 | 功能必要性 | 备注 |
|-----------|-----------|------|
| PMK-1（p38 MAPK） | 必要 | *pmk-1(km25)* 生存率显著下降 |
| ATFS-1（UPR^mt） | 必要 | *atfs-1(gk3094)* 生存率显著下降 |
| FSHR-1（GPCR） | 必要 | *fshr-1(ok778)* 生存率显著下降 |
| DAF-16/FOXO | 不必要 | *daf-16(mu86)* 与 WT 无差异 |
| DBL-1/TGF-β（*dbl-1* RNAi） | 不必要 | — |
| SKN-1（*skn-1* RNAi） | 不必要 | — |
| XBP-1（*xbp-1* RNAi） | 不必要 | — |
| HLH-30/TFEB | 不必要 | *hlh-30(tm1978)* 无差异 |
| EGL-30/Gq | 不必要 | *egl-30* RNAi 无差异 |

---

## 与项目的关系

本文与 iGEM 2026 干实验的核心相关性体现在以下几点：

1. **配体丰度受营养状态调控**：本文明确证明 ascr#1、ascr#3、ascr#5 在饥饿条件下显著减少，而 ascr#7 不变。这为理解线虫在不同生境下的 ascaroside 分泌谱提供了重要背景——项目中研究 NTF 对 ascr#18、ascr#3、ascr#7 感知时，需考虑宿主营养状态对配体浓度的影响。

2. **ascr#7 的特殊性**：本文数据显示 ascr#7 含量不受饥饿影响（ns），与其他短链 ascaroside 行为不同，这与 ascr#7 头部基团修饰的独特性一致，或对本项目中 ascr#7 在 Gpr2/Gpr3 受体结合模式的理解有参考价值。

3. **FSHR-1（GPCR）作为免疫感知枢纽**：本文确认 FSHR-1（一种肠道 GPCR）在抗真菌捕食中必要，提示 ascaroside 信号与 GPCR 免疫下游有功能交叉，可为项目中嵌合 G 蛋白设计及 GPCR 信号通路分析提供上下文参照。

4. **生防效果的土壤异质性解释**：本文提出的"营养热点=高风险区域"模型，说明 ascaroside 信号的空间分布不均，这对于理解 NTF 系统在田间尺度的效率差异具有生态学意义。

> 注意：本文不涉及受体结构、分子对接或 ascr#18 数据，与项目计算建模部分无直接数值对应关系。

---

## 关键引用（3-8条）

1. **Kuo et al. 2024** (*Nat. Microbiol.*): *A. oligospora* 通过 G 蛋白偶联受体感知 ascaroside pheromone 来检测猎物，是本文和本项目的直接上游文献。[Ref 11]

2. **Zhang et al. 2013** (*ACS Chem. Biol.*): Acyl-CoA oxidase 精细调控特定链长的 ascaroside pheromone 产生，奠定 ACOX-ascaroside 关系的生化基础。[Ref 13]

3. **von Reuss & Schroeder 2015** (*Nat. Prod. Rep.*): Ascaroside 组合化学综述——模块化初级代谢产物的组合装配，为理解 ascaroside 结构多样性提供框架。[Ref 12]

4. **Yang et al. 2020** (*PNAS*): 确立 *A. oligospora* 作为线虫-NTF 相互作用的鲁棒模型菌株，方法学基础。[Ref 7]

5. **Powell et al. 2009** (*PNAS*): FSHR-1 是 *C. elegans* 先天免疫所必需的 GPCR，本文在抗真菌捕食情境中复现并扩展了此发现。[Ref 27]

6. **Pellegrino et al. 2014** (*Nature*): 线粒体 UPR 提供病原体感染抵抗力，本文将 UPR^mt/ATFS-1 轴延伸到真菌捕食情境。[Ref 33]

7. **Park et al. 2012** (*PNAS*): Ascaroside 作为神经功能配体的综述，涵盖 ascr#1/3/5/7 等主要成员的化学特性与受体功能，与本项目配体选择直接相关。[Ref 36]
