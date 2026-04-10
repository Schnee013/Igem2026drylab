# Jiang et al. 2024 — 文献总结

> **完整标题**: Sensing host and environmental cues by fungal GPCRs
> **期刊**: Current Opinion in Plant Biology, 2024, **82**: 102667
> **DOI**: https://doi.org/10.1016/j.pbi.2024.102667
> **作者**: Cong Jiang, Aliang Xia, Daiying Xu, Jin-Rong Xu
> **机构**:
> - State Key Laboratory for Crop Stress Resistance and High-Efficiency Production, College of Plant Protection, Northwest A&F University, Yangling, Shaanxi 712100, China
> - Department of Botany and Plant Pathology, Purdue University, West Lafayette, IN 47907, USA
> **栏目**: VSI: Biotic Interactions 2025（Current Opinion in Plant Biology 专题综述）

---

## 核心发现（5-10 bullets，含数据）

- **真菌 GPCR 家族系统分类**：真菌 GPCR 可分为 10 个经典家族（Class I–X），包括信息素受体（Class I/II）、碳源感知受体（Class III）、氮源感知受体（Class IV）、cAMP 受体样受体（Class V）、微生物视蛋白（Class VI）、含 RGS 域受体（Class VII）、生长激素释放因子同源受体（Class VIII）、孕酮受体同源物（Class IX）；所有含 CFEM 域的真菌 GPCR 均归为 Class X。

- **异三聚体 G 蛋白信号系统**：大多数子囊菌只有 3 个 Gα、1 个 Gβ 和 1 个 Gγ 亚基（相比人类基因组编码 23 Gα、5 Gβ、12 Gγ）；GPCR 与配体结合后促进 Gα 上 GDP→GTP 交换，Gα 从 Gβγ 二聚体解离，激活下游 cAMP-PKA 和 MAP 激酶通路。

- **信息素受体（Pheromone receptors）的保守与扩展**：在酵母中，Ste2 和 Ste3 是最早鉴定的真菌 GPCR；在植物病原真菌（如 *F. graminearum*、*F. oxysporum*）中，Ste2/Ste3 同源物（Giv 家族）不仅调控有性生殖，还调控侵染垫形成、趋化生长、分生孢子萌发等致病过程，但在无性或极少有性生殖的物种中信息素受体可能不是致病必需。

- **碳源感知受体（Pth11-like，Class X CFEM）的功能**：在 *M. oryzae* 中，Pth11 通过随机突变筛选鉴定，缺失突变体附着孢形成缺陷，可被外源 cAMP 抑制；Pth11 含独特的细胞外 CFEM 域，定位于细胞核周围及胞内膜系统；*F. graminearum* 基因组含 22 个 CFEM-GPCR，其中 Gpr2/Gpr3 与 Pth11 亲缘关系相近，可能感知植物信号以触发不同侵染阶段。

- **Gpr2/Gpr3 对 *F. graminearum* 侵染的调控**：*gpr2 gpr3* 双突变体（而非单突变体）减毒表型显著，双突变体侵入性菌丝在穗轴内生长受阻；Gpr2 可能感知特定植物组织化合物，Gpr3 在穿透侵入方面非必需但对穗轴内侵入生长有贡献；含 FGRRES_16221 的 CFEM-GPCR 与 Gpa1/Gpa2/Gpa3 关联，参与致病性状转录调控和小麦防卫抑制。

- **NTF（线虫捕食真菌）中的 ascaroside 感知**：在 *A. oligospora* 中，Gpr1-like（Pth11-like）受体 Gpr2、Gpr3 及 Gin3 是感知线虫分泌的 ascaroside 信息素所必需的，激活下游 cAMP-PKA 通路以触发捕虫器形成；独立于线虫的 Pth11-like GPCRs（Gin1、Gin3、Gin4）感知非线虫衍生的化合物。在 *A. flagrans* 中，GprC 直接作为 ascaroside 感知受体，GprC 与 GasA（Gα 亚基）均定位于细胞质膜**和线粒体**——这是首个有文献记录的真菌 GPCR 双重定位案例，推测线粒体定位与捕食所需的呼吸增强有关。

- **Class VII 含 RGS 域 GPCR**：*M. oryzae* 和 *M. robertsii* 中的 *MrGPR* 基因编码含 RGS 域的 GPCR，调控小型菌落表型、孢子萌发、产孢和全毒力；删除导致 MrFox1 核转位异常，在昆虫检测中无毒力。

- **Class X CFEM-GPCR 家族扩张**：植物病原性和线虫捕食真菌具有扩展的 CFEM-GPCR 基因家族（*F. graminearum* 22 个），而模式酵母 *S. cerevisiae* 仅 3 个；推测这些受体可能是感知宿主来源配体的主要受体类型。

- **工程化 GPCR 酵母筛选平台**：通过在 *ste2 ste2 far1* 酵母突变体中用真菌 GPCR 跨膜螺旋替换 Ste2/Ste3 的跨膜区，并在 *FUS1* 启动子控制下表达报告基因（FAR1 和 SST2 删除以消除细胞周期阻滞和脱敏），可建立配体筛选平台，已用于筛选 *F. oxysporum* 的配体化合物（碳水化合物、糖及氨基酸）。

---

## 实验方法（表格）

| 方法 | 应用对象/场景 | 关键描述 |
|------|-------------|---------|
| 遗传互补与缺失突变 | *F. graminearum* Gpr2/3, *M. oryzae* Pth11, *A. flagrans* GprC 等 | 构建单/双/多基因敲除株，评估附着孢、侵入生长、产孢、毒力等表型 |
| cAMP 外源添加回复实验 | *M. oryzae* pth11 突变体 | 外源 cAMP 可回复 pth11 附着孢形成缺陷，说明 Pth11 位于 cAMP-PKA 通路上游 |
| 方向生长检测（directional growth assay） | *F. oxysporum* Ste2/Ste3 同源物 | 检测信息素识别与趋化生长方向 |
| 分生孢子萌发与附着孢形成 | *F. oxysporum* | 检测分生孢子萌发方向及侵染结构形成 |
| 嵌合 GPCR 酵母配体筛选 | 真菌 GPCR 配体未知情况 | 将真菌 GPCR TM 区替换 Ste2/Ste3 TM 区，用 FUS1-报告基因筛选配体 |
| 亚细胞定位（荧光标记） | *A. flagrans* GprC、GasA | GFP/荧光融合蛋白确认细胞质膜+线粒体双重定位 |
| 捕虫器形成定量 | *A. oligospora* Gpr2/Gpr3/Gin 系列 | ascaroside 诱导后统计捕虫器数量 |
| 序列同源性与系统发育分析 | 多种真菌 GPCR | 将真菌 GPCR 分为 10 个 Class，鉴定 CFEM 等特征域 |
| 小麦穗轴侵染试验 | *F. graminearum* Giv1/Giv2/Giv3, Gpr2/Gpr3 | 测定侵染垫形成、穿透率、穗轴内侵入生长范围 |

---

## 关键数据（分小节）

### 1. *Fusarium graminearum* GPCR 与致病

- Giv1（Ste2-like）与 Gpa2 互作，激活 cAMP-PKA 和 GpMk1 MAP 激酶通路，调控侵染垫形成；Giv2 可能感知特定穗轴化合物，对穿透侵入非必需但对穗轴内侵入生长有贡献；Giv3 亦重要于穗轴侵入。
- CFEM-GPCR FGRRES_16221 与 Gpa1/Gpa2/Gpa3 关联，参与致病性状的转录调控和宿主防卫抑制。
- *gpr2 gpr3* 双突变体（Pth11-like Class X）表型：侵入性菌丝在穗轴内生长严重受阻；单基因突变表型不明显。

### 2. *M. oryzae* Pth11 与 Class X CFEM-GPCR

- *pth11* 缺失：附着孢形成缺陷，可被外源 cAMP 抑制（说明位于 cAMP 通路上游）；IBMX 处理影响表型，提示 cAMP 信号核心角色。
- Pth11 含胞外 CFEM 域，定位于细胞核周围与胞内膜结构。
- *F. graminearum* 基因组含 22 个 Class X CFEM-GPCR；Gpr2/Gpr3 与 Pth11 亲缘关系最近。

### 3. *A. oligospora* Gpr2/Gpr3 感知 ascarosides

- Gpr2、Gpr3、Gin3 均为 Pth11-like（Class X）；这三个受体激活下游 cAMP-PKA 通路以触发捕虫器形成。
- Gin1、Gin3、Gin4（Pth11-like）感知非线虫来源化合物，独立于线虫信号。
- Gpr2、Gpr3 与 Gin3 的配体特异性不同，说明 NTF 通过多个 GPCR 整合宿主与非宿主来源信号。

### 4. *A. flagrans* GprC 双重定位

- GprC（*A. flagrans* 线虫捕食真菌）作为 ascaroside 感知受体，与 Gα 亚基 GasA 共定位于细胞质膜和线粒体。
- *gprC* 缺失：捕虫器（trap）形成受阻；*gasA* 缺失：cAMP-PKA 和 MAP 激酶通路激活受阻，*gasA* Gα 缺失突变体捕虫器形成完全受阻。
- 线粒体定位推测与捕食过程中呼吸增强的代谢需求相关；这是首个有文献记录的真菌 GPCR 双重定位。

### 5. GPCR 家族规模与功能扩展

- 酵母 *S. cerevisiae*：3 个 GPCR；*Neurospora crassa*：39 个；*M. oryzae* 和 *F. graminearum*：分别 76 和 109 个。
- 植物病原性真菌的 GPCR 数量显著多于非病原物种，提示家族扩张与寄生/捕食生活方式适应相关。

---

## 与项目的关系

本文是迄今对真菌 GPCR（尤其是线虫捕食真菌和植物病原真菌）功能系统综述中最直接相关的文献之一，直接涵盖项目研究的核心受体。

**直接相关内容：**

1. **GprC（*A. flagrans*）**：本文第 5 页专节介绍 GprC 作为 ascaroside 感知受体的功能，确认其 Class X（Pth11-like CFEM-GPCR）归属，并报告了 GprC 细胞质膜+线粒体双重定位现象（Ref 36，*Nat Microbiol* 2024）。这直接为项目中 GprC 的受体身份和信号传导提供文献支撑。

2. **Gpr2/Gpr3（*A. oligospora*）**：本文明确将 Gpr2/Gpr3 归类为 Pth11-like（Class X）GPCR，并说明 Gpr2、Gpr3 与 Gin3 均负责感知 ascaroside 以激活 cAMP-PKA 通路触发捕虫器形成（Ref 36）。

3. **Pth11 同源物（Class X CFEM-GPCR）家族**：本文提供了 Pth11-like 家族的系统背景——该家族在植物病原真菌中大量扩张（*F. graminearum* 22 个），是感知宿主来源配体的主要受体类型，为项目从进化角度理解 GprC/Gpr2/Gpr3 功能提供框架。

4. **信号通路**：本文确认 Gpr2/Gpr3/GprC 均通过 cAMP-PKA 和/或 MAP 激酶通路激活下游响应，与项目 ODE 信号通路建模的通路选择一致。

5. **配体特异性**：本文强调不同 Pth11-like GPCR 识别不同配体，NTF 整合多种信号；提示项目在建模 ascaroside 特异性时需区分不同受体亚型。

**需注意的局限：** 本文为综述，不含原始结构数据或结合亲和力数值；配体-受体互作的原子细节需参考原始研究（如 Kuo2024 等）。

---

## 关键引用（本文引用的核心文献）

1. **Ref 1** — Brown NA et al. *Fungal GPCR signalling*（综合真菌 GPCR 综述，提供 10 类 GPCR 分类框架）

2. **Ref 5** — Zhang MZ, Chen Y, Xu JR et al.（Ste2 Gα亚基偶联结构研究，提供 Ste2-Gpa1 激活机制）

3. **Ref 6/7** — Xia A, Xu JR et al.（Ste2 配体结合结构变化；拮抗剂机制洞察）

4. **Ref 22** — Yan KB et al.（*M. oryzae* Pth11 随机突变筛选鉴定；cAMP 回复实验）

5. **Ref 33/34** — Khayeri TMCA et al.; Subramani R et al.（线虫捕食真菌通过 cAMP-PKA 和 MAP 激酶感知线虫存在）

6. **Ref 35** — Guo L et al.（*A. oligospora* Gpr2/Gpr3 感知 ascarosides，激活 cAMP-PKA 触发捕虫器形成；Gin1/3/4 感知非线虫信号）

7. **Ref 36** — ★★ Yu D et al. *Nat Microbiol* 2024, **9**: 1752–1763. — ***A. flagrans* GprC 与 GasA 感知 ascaroside，双重定位于质膜与线粒体，GasA 激活 cAMP-PKA 和 MAP 激酶通路触发捕虫器形成；首个真菌 GPCR 双重定位案例**

8. **Ref 40** — Lengger B, Jensen MK: *Engineering G protein-coupled receptor signalling in yeast for biotechnological and medical purposes*. *FEMS Yeast Res* 2020 — 嵌合 GPCR 酵母配体筛选平台方法学基础
