# von Reuss et al. 2012 — 文献总结

> **完整标题**: Comparative Metabolomics Reveals Biogenesis of Ascarosides, a Modular Library of Small-Molecule Signals in *C. elegans*
> **期刊**: *Journal of the American Chemical Society (JACS)*, 2012, **134**, 1817–1824
> **DOI**: 10.1021/ja210202y
> **作者**: Stephan H. von Reuss, Neelanjan Bose, Jagan Srinivasan, Joshua J. Yim, Joshua C. Judkins, Paul W. Sternberg, Frank C. Schroeder
> **机构**: Boyce Thompson Institute and Department of Chemistry and Chemical Biology, Cornell University, Ithaca, New York 14853; Howard Hughes Medical Institute and Division of Biology, California Institute of Technology, Pasadena, California 91125

---

## 核心发现（5–10 bullets，含数据）

- 利用基于 MS/MS 的比较代谢组学（comparative metabolomics），系统分析了 *C. elegans* 野生型及一系列 β-氧化通路突变体的分泌代谢组，鉴定出 **124 种**此前未报道的新型 ascaroside，大幅扩展了已知分子库。
- 揭示了 ascaroside 的生物合成经由**脂肪酸 β-氧化**（peroxisomal β-oxidation）逐步缩短 ascarylose 侧链，循环每次缩短 2 个碳，由此生成从长链到短链的一系列同系物。四个关键酶依次为：acyl-CoA 氧化酶 **ACOX-1**、enoyl-CoA 水化酶 **MAOC-1**、3-羟基-acyl-CoA 脱氢酶 **DHS-28**、3-酮酰-CoA 硫解酶 **DAF-22**。
- 确认了 **DAF-22**（人类 MFE-2 同源物）参与 β-氧化最后一步，*daf-22* 突变体完全不产生短链 ascaroside（侧链 ≤C₉），而积累相应长链前体。
- **MAOC-1** 和 **DHS-28** 被鉴定为人类 MFE-2 功能同源物：MAOC-1 行使 enoyl-CoA 水化酶功能，DHS-28 行使 (3R)-羟基脂酰-CoA 脱氢酶功能；两者突变体分别积累特征性 α,β-不饱和或 ω-/ω-1-羟基化 ascaroside。
- 在 *acox-1* 突变体中，长链（≥C₁₃）ascaroside（如 ascr#9, ascr#10）显著积累，说明 **ACOX-1 主要处理长链底物**；短链合成在 *acox-1* 突变体中受阻，提示另有其他 acyl-CoA 氧化酶参与短链处理。
- 新鉴定的 ascaroside 含 **indole-3-carbonyl** 修饰的"indole ascaroside"（icas#）系列：在 *acox-1* 突变体中，icas#9 比对应非 indole 型 ascr#9 高出超过 **100 倍**，提示 indole-3-carbonyl 附加在 β-氧化之前的底物上，修饰位点位于 ascarylose 的 4'-OH。
- 营养状态（饥饿）对 ascaroside 谱影响显著：饥饿条件下，长链（ω-1-连接）ascaroside 和 ascr#5（dauer 信息素组分）产量更高；正常培养条件下以短链 ascaroside 为主。ascr#5 和 ascr#3 在饥饿时增加，相对 ω-linked 化合物更明显（P < 0.01）。
- 蠕虫体（worm body pellet）与培养液（liquid culture supernatant）的 ascaroside 谱不同：虫体中 indole ascaroside 更丰富，提示部分 ascaroside 主要保留于体内，而非分泌到培养液。
- 通过**氘标记色氨酸**（deuterium-labeled tryptophan）喂养实验，证实 indole ascaroside 的 indole-3-carbonyl 基团来源于色氨酸（tryptophan），再由 ascaroside 生物合成体系完成后续修饰。

---

## 实验方法（表格）

| 方法 | 描述 |
|------|------|
| LC-MS/MS（ESI 负离子） | 主要检测平台，用于分泌代谢组分析；ESI 灵敏度高于 APCI，可检测低至 µg/mL 级别 ascaroside |
| MS/MS 碎片分析 | 利用特征碎片离子（如 ascarylose 碎片 *m/z* 73）筛选所有含 ascarylose 的化合物 |
| 比较代谢组学 | 同时对比野生型（N2）与多个 β-氧化突变体（*acox-1*, *maoc-1*, *dhs-28*, *daf-22*）的完整代谢组 |
| 2D NMR（COSY、TOCSY、HSQC 等） | 对代表性化合物进行结构确认，与文献已知 ascaroside 比对 |
| 化学合成 | 合成参考标准品以确认结构，如 icas#3、indole ascaroside 系列 |
| 氘标记喂养实验 | 用氘代色氨酸（deuterium-labeled tryptophan）喂养 *acox-1* 突变体，追踪 indole 碳骨架来源 |
| 液体培养 + 虫体提取 | 分别分析培养液（分泌组）和虫体研磨液（体内代谢组） |
| 突变体表型验证 | 使用 *acox-1(ok2257)*, *maoc-1(hj13)*, *dhs-28(hj8)*, *daf-22* 等经遗传验证的等位基因 |

---

## 关键数据（分小节）

### 2.1 新 ascaroside 鉴定

- 利用 *m/z* 73 离子（ascarylose 特征碎片）筛选全代谢组，共鉴定 **124 种**新 ascaroside 类似物。
- 新化合物涵盖：ω-/ω-1-连接的饱和、α,β-不饱和、β-羟基化 ascaroside；含 indole 修饰的 icas# 系列；含甘油（glycosyl）残基的衍生物。

### 2.2 ACOX-1 功能

- *acox-1(ok2257)* 突变体中，长链 ascr#9（C₁₁ 侧链）和 ascr#10（C₉ 侧链）的 ω-1-连接同系物大量积累。
- ω-oxygenated 化合物在 *acox-1* 中增加，说明 ω-功能化先于 peroxisomal β-氧化发生。
- 短链 ascaroside（<C₉）在 *acox-1* 突变体中几乎消失（减少约 90%），说明链缩短在 ACOX-1 步骤受阻。

### 2.3 MAOC-1 和 DHS-28 功能

- *maoc-1(hj13)* 分泌组以 α,β-不饱和 ascaroside（如 ascr#21 C₁₁，ascr#25 C₉）为主，说明 MAOC-1 负责 enoyl-CoA 水化。
- *dhs-28(hj8)* 分泌组中，ascr#22（C₁₁）为最丰富组分，属 β-羟基化系列，印证 DHS-28 的 (3R)-羟基脂酰-CoA 脱氢酶功能。
- 两者均与人类 **MFE-2**（multifunctional β-oxidation enzyme 2）的结构域同源，后者突变导致人类过氧化物酶体病。

### 2.4 DAF-22 功能

- *daf-22* 突变体**完全不产生**短链（≤C₉）ascaroside，且不积累 ω-oxygenated 中间体，提示链缩短在硫解酶步骤终止。
- 长链（≥C₁₃）β-羟基化 ascaroside 在 *daf-22* 中大量积累（见图 4c、4d）。

### 2.5 Indole Ascaroside 系列

- 新系列 icas#（如 icas#3、icas#9、icas#10）含 indole-3-carbonyl 连接于 ascarylose 的 4'-OH。
- 在 *acox-1* 突变体中，icas#9 丰度是 ascr#9 的 **100 倍以上**（worm body）。
- 氘标记喂养确认 indole 骨架来源于色氨酸。

### 2.6 营养状态对 ascaroside 谱的影响

- 饥饿条件下，长链 ω-1-连接 ascaroside 以及 ascr#5（dauer 信息素）产量升高。
- ascr#5 在饥饿时增加，ascr#3 同样响应，两者对虫群密度信号起重要作用（ascr#5 > ascr#3 > ascr#2 协同诱导 dauer）。

---

## 与项目的关系

本论文直接提供了 iGEM 2026 项目核心配体的化学背景：

1. **ascr#18 的结构类别定位**: ascr#18 属于 ascaroside 家族，其生物合成经由本文揭示的 β-氧化通路。了解侧链长度与酶的对应关系，有助于推断 ascr#18 在 *C. elegans* 体内的生物合成节点。

2. **ascr#3 的生物合成**: ascr#3 是本文明确分析的 dauer 信息素组分之一，饥饿状态下产量上升；与项目配体列表（ascr#18, ascr#3, ascr#7）直接重叠，提供了配体产生的生理背景。

3. **配体化学结构理解**: 本文阐明了 ascaroside = ascarylose（糖）+ 脂肪酸侧链的模块化结构，不同侧链长度和修饰（indole、ω-oxygenation）产生功能不同的信号分子，这对理解 Gpr3/GprC 受体-配体选择性（特别是 ascr#18 是否具有 indole 修饰）提供了结构框架。

4. **受体-配体选择性参考**: 本文指出低浓度（低于信息素混合物常规浓度）的 ascaroside 也可产生显著活性，且不同 ascaroside 激活不同信号通路，提示受体结合特异性高度依赖侧链化学结构，与 Gpr3/GprC 对 ascr#18 的选择性对接研究相关。

---

## 关键引用（原文参考文献）

1. Butcher, R. A.; Fujita, M.; Schroeder, F. C.; Clardy, J. *Nat. Chem. Biol.* **2007**, *3*, 420–422. — 首次报道 *daf-22* 缺失对 ascaroside 产生的影响。

2. Srinivasan, J.; Kaplan, F.; Ajredini, R.; Zachariah, C.; Alborn, H. T.; Teal, P. E.; Malik, R. U.; Edison, A. S.; Sternberg, P. W.; Schroeder, F. C. *Nature* **2008**, *454*, 1115–1118. — 鉴定 ascr#3 和 ascr#8 为 dauer 吸引信息素。

3. Butcher, R. A.; Ragains, J. R.; Kim, E.; Clardy, J. *Proc. Natl. Acad. Sci. U.S.A.* **2008**, *105*, 14288–14292. — 建立四组分 dauer 信息素混合物（ascr#2, ascr#3, ascr#4, ascr#5）。

4. Pungaliya, C.; Srinivasan, J.; Fox, B. W.; Malik, R. U.; Ludewig, A. H.; Sternberg, P. W.; Schroeder, F. C. *Proc. Natl. Acad. Sci. U.S.A.* **2009**, *106*, 7708–7713. — 发现 ascr#8（ascr#18 相关结构）吸引雄虫。

5. Butcher, R. A.; Ragains, J. R.; Li, W.; Ruvkun, G.; Clardy, J.; Mak, H. Y. *Proc. Natl. Acad. Sci. U.S.A.* **2009**, *106*, 1875–1879. — 描述 daf-22 突变体的代谢特征与 ascaroside 积累。

6. Macosko, E. Z.; Pokala, N.; Feinberg, E. H.; Chalasani, S. H.; Butcher, R. A.; Clardy, J.; Bargmann, C. I. *Nature* **2009**, *458*, 1171–1175. — 报道 ascaroside 介导的神经回路与集群行为（clumping behavior）。

7. Kim, K.; Sato, K.; Shibuya, M.; Zeiger, D. M.; Butcher, R. A.; Ragains, J. R.; Clardy, J.; Touhara, K.; Sengupta, P. *Science* **2009**, *326*, 994–998. — 首次报道 *C. elegans* 嗅觉受体响应 ascaroside 的神经机制，与 Gpr 受体研究方向平行。
