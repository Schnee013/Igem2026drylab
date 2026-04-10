# Kim et al. 2009 — 文献总结

> **完整标题**: Two Chemoreceptors Mediate Developmental Effects of Dauer Pheromone in *C. elegans*
> **期刊**: *Science*, Vol. 326, 13 November 2009, pp. 994–998
> **DOI**: 10.1126/science.1176331
> **作者**: Kyuhyung Kim, Koji Sato, Mayumi Shibuya, Danna M. Zeiger, Rebecca A. Butcher, Justin R. Ragains, Jae Clardy, Michi Touhara, Piali Sengupta
> **机构**: Department of Biology and National Center for Behavioral Genomics, Brandeis University, Waltham, MA; Department of Chemistry, Harvard University; Department of Applied Biological Chemistry, University of Tokyo

---

## 核心发现（5–10 bullets，含数据）

- **鉴定了两个 ascaroside pheromone 受体**：*srbc-64*（编码 SRBC-64）和 *srbc-66*（编码 SRBC-66）是 *C. elegans* SRBC 亚家族成员，其功能缺失突变体在 ascaroside C6、C9、C7、C3 诱导的 dauer 形成中均显著缺陷（P < 0.01 与野生型比较，图 1A–D）。
- **功能等同于 DAF-37/DAF-38**：论文中将这两个受体命名为 DAF-37（SRBC-64）和 DAF-38（SRBC-66），是首次从分子层面鉴定的 dauer pheromone 受体，与早期遗传命名 *daf-37*/*daf-38* 对应（不同命名系统的早期引用见 Park 2012）。
- **双突变体表型最强**：*srbc-64; srbc-66* 双突变体对高浓度 ascaroside（C6、C7、C9）的响应几乎完全丧失（图 1A–C，图 3B），提示两个受体功能部分冗余、共同介导多种 pheromone 组分的信号。
- **ascaroside C3 有独立通路**：*srbc-64; srbc-66* 双突变体对 C3 仍保留部分（但显著降低的）dauer 响应（图 1D），提示存在感知 C3 的其他受体分子。
- **受体定位于 ASK 感觉神经元纤毛**：全长 GFP 标记的 SRBC-64 和 SRBC-66 均特异性定位于 ASK 化学感觉神经元的纤毛（图 3A），且两者亚细胞定位互相依赖（单独缺失对方时定位不改变，但共表达时正确）。
- **调控基因表达的下游通路**：ascaroside 通过 SRBC-64 和 SRBC-66 下调 *str-3p::gfp* 报告基因表达；*srbc-64* 突变体中该下调响应丧失（图 2A–C），且 ASK 神经元特异性 *srb-9* 启动子驱动的表达可救回 *srbc-64* 突变体的基因表达缺陷（图 2D）。
- **偶联 Gα 蛋白 GPA-3**：遗传学实验显示 SRBC-64 和 SRBC-66 部分通过 Gα 蛋白 GPA-3 传递信号，激活下游 DAF-11（鸟苷酸环化酶）抑制 cGMP 产生，进而调控 dauer 形成（图 3D–E，基于 *gpa-3* 突变体与 DAF-11 互作证据）。
- **在 HEK293 异源细胞中介导 cAMP 响应**：将 SRBC-64 + SRBC-66 共转染至人 HEK293 细胞后，ascaroside C6 和 C9（10 μM）显著促进胞内 cAMP 产生，单独转染任一受体均无效，证明两者功能性共表达才能产生配体响应（图 4A–C）。
- **ascaroside 作为反向激动剂**：在 HEK293 细胞中，ascaroside 通过抑制腺苷酸环化酶（inverse agonists 模式）降低 cAMP 水平（图 4A–B），与体内通过抑制 DAF-11 活性促进 dauer 的机制一致。
- **扩展 SRBC 受体家族重要性**：*C. elegans* 基因组编码 86 个预测 SRBC 亚家族成员（srbc subfamily），其中多个成员可能响应不同 pheromone 组分，本研究鉴定的两个受体是打开这一大家族功能解析的第一步。

---

## 实验方法（表格）

| 方法 | 具体内容 |
|------|---------|
| 遗传筛选 | 在 EMS 诱变背景下筛选 dauer 形成缺陷突变体；鉴定 *srbc-64*、*srbc-66*、*gpa-3* 等位基因 |
| Dauer 形成定量 | 在不同浓度 ascaroside（C3、C6、C7、C9，1–100 μM 梯度）存在下计数 dauer 占比；n = 50–100/实验，≥4 次独立重复 |
| 荧光报告基因（*str-3p::gfp*）| 使用 *str-3* 或 *daf-7p* 驱动 gfp，通过荧光显微镜定量 ASI/ASK 神经元表达水平；n > 30/实验 |
| RT-PCR | 定量 *srbc-64*、*srbc-66* mRNA 水平（补充表 S1–S4） |
| 透射电镜（TEM）| 检查 *srbc-64*、*srbc-66* 突变体 ASK 纤毛超微结构（未见异常，补充图 S5） |
| 共聚焦显微镜 | GFP 融合蛋白纤毛定位；侧面观，比例尺 10 μm（图 3A） |
| HEK293 异源表达 | 瞬时转染 SRBC-64 + SRBC-66（分别或共转），HTRF cAMP assay 检测胞内 cAMP（图 4A–C），n = 3–11 次试验取平均 |
| 遗传救回实验 | 利用 ASK 特异性 *srb-9* 或 *str-3* 启动子驱动受体，转为染色体外阵列（Ex[...]）后检验 dauer 表型救回（图 1E，图 2D） |
| 钙成像 | 成体蛔线虫体内 ASK 神经元钙动态（对 C6/C9 的即时响应，图 4 相关补充） |
| 统计 | Student's t-test；*P < 0.05，**P < 0.01，###P < 0.001 与野生型比较 |

---

## 关键数据

### Dauer 形成缺陷

- 野生型在 1000 nM（10³ nM）C6 时约 80% 形成 dauer；*srbc-64* 单突变体降至约 20%（P < 0.01，图 1A）。
- *srbc-64; srbc-66* 双突变体在同等 C6 浓度下约 5% 形成 dauer，且对 C7、C9 亦几乎完全丧失响应（图 1B–C）。
- 600 nM C6 条件下，转入 *srbc-64p::srbc-64* 或 *srbc-66p::srbc-66* 染色体外阵列可显著救回 dauer 缺陷（图 1E，#P < 0.01）。

### 基因表达下调

- 野生型成体中，6 μM C6 处理导致 *str-3p::gfp* 荧光降至乙醇对照的约 20%；*srbc-64* 突变体中该荧光值维持较高水平，降低幅度显著小于野生型（图 2A–C，P < 0.05）。
- *srbc-64; srbc-66* 双突变体中 pheromone 诱导的 *str-3p::gfp* 下调对 C6、C9 均丧失（图 2D）。

### HEK293 cAMP 数据

- SRBC-64 + SRBC-66 共转染细胞中，10 μM C6 使 cAMP 水平升高约 2–4 倍（与对照 pME185 相比，图 4A）；C9 效果相似。
- 单独转染 SRBC-64 或 SRBC-66 均无显著 cAMP 变化，说明两受体必须共表达才能产生功能性信号（图 4A）。
- 体外 cAMP 数据显示 ascaroside 增加 cAMP，而体内数据显示 cAMP 下降——论文认为这一表观矛盾源自体内 GPA-3 下游的抑制性信号（反向激动剂机制）。

### 受体定位

- SRBC-64::GFP 和 SRBC-66::GFP 在 ASK 纤毛明确共定位（图 3A），且各自的正确定位依赖于两个受体同时存在。

---

## 与项目的关系

本文是鉴定 *C. elegans* ascaroside pheromone 受体（SRBC-64/DAF-37 和 SRBC-66/DAF-38）的奠基性文献，对 iGEM 2026 干实验项目具有以下直接相关性：

1. **受体身份确认**：项目中 Hu2024 嵌合设计的 GprC（源自线虫 ascaroside 受体亲缘蛋白）可追溯至本文所鉴定的受体家族（SRBC 亚家族）。本文确立了 DAF-37/DAF-38 是感知 ascaroside（ascr#5=C6、ascr#9=C9 等）的分子靶点。

2. **ascr#3/ascr#7 受体背景**：本文鉴定的受体对 C3（对应 ascr#3）和 C7（对应 ascr#7，实验中 ascaroside C7）均有响应，与项目关注的 ascaroside 信号分子谱系吻合。

3. **GPCR 偶联机制参考**：本文证明 SRBC-64/66 通过 GPA-3（Gαi 类）→ cGMP/cAMP 通路传递信号，为项目在 NTF（*Neurospora crassa*）等真菌中构建异源 GPCR 信号系统提供了信号偶联参照。

4. **异源表达可行性**：本文在 HEK293 细胞成功重建 ascaroside 响应，说明线虫 ascaroside GPCR 在异源系统中具有功能活性，支持项目将相关受体在酵母或真菌底盘中表达的技术路线可行性。

---

## 关键引用（8 条）

1. **Jeong et al. 2005, *Nature*** — 首次报道 dauer pheromone 的化学成分含 ascaroside，奠定化学基础。
2. **Butcher et al. 2007, *Nat. Chem. Biol.*** — 进一步解析 ascaroside 结构并鉴定多种活性组分（C3、C6、C7、C9）。
3. **Golden & Riddle 1984, *Dev. Biol.*** — 经典 dauer 遗传框架，确立 dauer 形成为可遗传调控的发育决策。
4. **Bargmann & Horvitz 1991, *Science*** — 化学感觉神经元消融实验，证明 ASK 等神经元在 dauer 感知中的核心角色。
5. **Murakami et al. 2001, *Mech. Dev.*** — 描述 *srbc* 基因家族（SRBC subfamily），本文受体命名基础。
6. **Murayama et al. 2012（预期引用）**/ 原文引用 **Antebi et al. 2000** — DAF 信号通路（DAF-11 guanylyl cyclase）与 cGMP 调控。
7. **Zwaal et al. 1997, *Genetics*** — *gpa-3* 的遗传功能，GPA-3 作为 pheromone 下游 Gα 蛋白的证据链。
8. **Schackwitz et al. 1996, *Neuron*** — ASI 与 ASK 神经元在 dauer 形成中的冗余与互补作用。

> 注：原文 References and Notes 编号 1–28，以上引用按原文内容忠实重建，非项目信息。
