# Ostrov et al. 2017 — 文献总结

> **完整标题**: A modular yeast biosensor for low-cost point-of-care pathogen detection
> **期刊**: *Science Advances* 2017; **3**: e1603221
> **DOI**: 10.1126/sciadv.1603221
> **作者**: Nili Ostrov†, Miguel Jimenez†, Sonja Billerbeck†, James Brisbois†, Joseph Matragrano, Alastair Ager, Virginia W. Cornish（†同等贡献）
> **机构**: Columbia University（Chemistry, Global Health Initiative, Microbiology & Immunology）; Ohio State University（H. capsulatum 菌株）；Brown University（P. brasiliensis 菌株）
> **注**: 论文作者列表中 Billerbeck 为共同第一作者，期刊发表年份为 2017；部分引用文献将其列为"Billerbeck2018"系引用惯例差异，原文发表时间为 2017年6月28日。

---

## 核心发现（5–10 bullets，含数据）

- **平台概念**: 将真菌病原体分泌的配体特异性交配肽（mating peptide）与 *S. cerevisiae* GPCR 信号通路耦联，驱动番茄红素（lycopene）生物合成基因的转录激活，产生肉眼可见的红色素输出，无需仪器即可读取。
- **灵敏度**: 优化后的酵母生物传感器（Lyco-2 菌株）对 *C. albicans* 配体的检出限（EC₅₀）约 12 nM，可见阈值（visible threshold）为约 3.5 LPC（lycopene per cell），在 10 μM 合成肽诱导后 9 小时可达最大产量约 11 LPC。
- **多病原体覆盖（EC₅₀ 范围）**: 通过引入异源真菌 GPCR，平台扩展至 11 种真菌病原体受体；EC₅₀ 从 0.46 nM（*H. capsulatum*）到 14,000 nM（*C. glabrata*）不等，覆盖了多种人类、植物、食品、环境真菌病原体。
- **特异性验证**: Ca.Ste2（*C. albicans*）和 Sc.Ste2（*S. cerevisiae*）受体分别仅对其同源肽响应，在 5 μM 浓度下测试的 11 种异源肽中均显示背景水平荧光（交叉反应性极低）。
- **代谢工程优化**: Lyco-2 菌株整合了 CrtE、CrtB、CrtI 番茄红素合成基因以及额外的 CrtI 拷贝（2xCrtI）和 FAD1 辅因子基因，使最大番茄红素产量比 Lyco-1 提高约 3 倍（~7 LPC → ~11 LPC）；CrtE-CrtB-CrtI 合成路径将 FPP → GGPP → 番茄红素。
- **复杂样本检测**: 在 1 μM 合成肽条件下，传感器可在土壤、尿液、血清、血液等复杂基质中检出 *P. brasiliensis* 和 *C. albicans* 配体，土壤和尿液信号与 YPD 培养基对照无显著差别；血液/血清样本信号略低但仍高于可见阈值。
- **临床分离株验证**: 对 3 种 *C. albicans*、3 种 *P. brasiliensis*、3 种 *H. capsulatum* 临床分离株的培养上清液（cell-free supernatant）进行检测，所有菌株的传感器响应显著高于空白对照（**P ≤ 0.01 或 ***P ≤ 0.001），证明病原体在液体培养中实际分泌可检测水平的配体。
- **纸基 dipstick 测定**: 将番茄红素生物传感菌株冻干于滤纸上，制成稳定的干粉试纸（dipstick）；以红色变化为读数，在室温储存 36 周后功能完整；对 1 μM *P. brasiliensis* 配体的检测结果与液体测定一致，12 小时内达到最大信号。
- **三维打印持纸夹**: 设计了低成本丙烯腈丁二烯苯乙烯（ABS）3D 打印卡盒用于规范 dipstick 形式，使测试标准化并适用于资源匮乏环境（point-of-care）。
- **传感器长期稳定性**: 纸基传感器在室温储存 36 周后仍保持检测功能，支持常温分发和储存，无需冷链。

---

## 实验方法（表格）

| 方法/模块 | 关键细节 |
|-----------|---------|
| 酵母菌株构建 | 亲本株 LW2591（*MATa inc* 基因型）；基因经 *HO* 位点整合，用 reiterative recombination 进行无痕基因缺失和替换 |
| 番茄红素报告系统 | 来自 *E. herbicola* 的 CrtE、CrtB、CrtI 基因（GGPP→Phytoene→Lycopene），受 P_TDH3、P_TEF1、P_PGK1 启动子驱动；pFUS1 诱导型启动子驱动 CrtI（信号放大） |
| 异源 GPCR 克隆 | 从病原体基因组 DNA 或密码子优化合成；用 MUSCLE（v3.8.31）多序列比对；与 Sc.Ste2 同源性（MAVITY）约 17.2% |
| 荧光读数 | mCherry（转录活性）：激发 588 nm、发射 620 nm；OD₆₀₀ 校正，96 孔板 800 rpm，30°C |
| 番茄红素读数 | 光密度法：OD₄₀₀/OD₆₀₀；分光光度计定量（LPC 单位）；LPC 阈值 3.5 |
| 合成配体 | ≥95% 纯度（GenScript 或 Zymo Research）；测试浓度范围 10⁻³–10⁴ nM（液体）及 1 μM（dipstick） |
| 临床分离株培养 | *C. albicans* 30°C 液体培养 24 h；*P. brasiliensis*（GC75、Pb01、Pb18）25°C 液体培养；*H. capsulatum*（Hc01、Hc06、Hcdr1）25°C 酵母相培养 10 天 |
| 复杂样本制备 | 尿液（50% pooled）、血清（50%）、血液（2% whole blood）加入到 YPD 培养基；土壤（50% v/v，Fafard专业盆栽土）；配体终浓度 1 μM |
| Dipstick 制备 | 传感器菌株铺于 Whatman 2# 滤纸（4 mm 圆孔）；冻干；3D 打印 ABS 卡盒固定；1 μM 配体复溶测试 |
| 统计 | 所有实验三个以上独立重复（n=3）；Student *t*-test；*P ≤ 0.01、***P ≤ 0.001 |

---

## 关键数据（分小节）

### 传感器灵敏度与 EC₅₀

| 受体来源物种 | 缩写 | EC₅₀ (nM) |
|------------|------|-----------|
| *Candida glabrata* | Cg | 14,000 |
| *Magnaporthe oryzae* | Mo | 13,000 |
| *Fusarium graminearum* | Fg | 360 |
| *Saccharomyces cerevisiae* | Sc | 190 |
| *Lodderomyces elongisporus* | Le | 54 |
| *Paracoccidioides brasiliensis* | Pb | 36 |
| *Zygosaccharomyces rouxii* | Zr | 35 |
| *Zygosaccharomyces bailii* | Zb | 22 |
| *Botrytis cinerea* | Bc | 4.8 |
| *Candida albicans* | Ca | 12 |
| *Histoplasma capsulatum* | Hc | 0.46 |

### 番茄红素菌株优化

| 菌株 | 构型 | 最大 LPC（10 μM 配体，9 h） |
|------|------|--------------------------|
| Null | 无番茄红素基因 | ~0.5 |
| Lyco-1 | CrtE + CrtB + CrtI（单拷贝） | ~3.5（接近阈值）|
| +2xCrtI | Lyco-1 + 额外 CrtI 质粒 | ~5 |
| +Fad1 | Lyco-1 + Fad1 质粒 | ~5 |
| Lyco-2 | 所有基因染色体整合（+2xCrtI + Fad1） | ~11 |

### Dipstick 检测时间

- *P. brasiliensis* 配体（1 μM）：dipstick 在 12 小时达到最大红色信号
- 可见阈值在约 3.5 red color units（RGB Δ红色值）
- 室温储存 36 周：功能未丧失

### 临床样本信号

- 三株 *C. albicans* 临床分离株（GC75、yBS45、W303-1B 作参照）：所有上清样本显著高于 Sc 传感器背景
- 三株 *P. brasiliensis*（Pb01、Pb18 等）：荧光/lycopene 信号均显著高于阴性对照（***P ≤ 0.001）
- *H. capsulatum*：三株（Hcdr1、Hc01、Hc06）均阳性，EC₅₀ 最低（0.46 nM），灵敏度最高

---

## 与项目的关系

本文为 iGEM 2026 干实验酵母 GPCR 生物传感器产品化设计提供了核心参考框架，具体相关性如下：

1. **GPCR 信号通路工程化**：本文证明了将非酵母病原真菌 GPCR（如 *C. albicans* Ca.Ste2）异源表达于 *S. cerevisiae*，并与其内源 Gα/Gβγ 信号通路耦联产生功能性输出的可行性——这与项目中将嵌合 G 蛋白（chimeric G protein）用于 GPCR 信号重定向的设计直接相关。

2. **比色/无仪器读数设计**：番茄红素色素输出的肉眼可见阈值（3.5 LPC）及 pFUS1 诱导型启动子设计，为项目产品化阶段选择报告基因和输出方式提供了具体的工程参数。

3. **配体特异性验证策略**：11 种受体的特异性交叉反应测试矩阵（Fig. 3C heatmap）提供了一套可复用的 GPCR 特异性验证实验范式，可直接应用于项目中对目标 GPCR 信号特异性的测试设计。

4. **产品化路径**：Dipstick 形式（冻干菌株 + 滤纸 + 3D 打印卡盒）和 36 周室温稳定性数据，为项目湿实验团队设计最终产品原型（POC 诊断工具）提供了直接的工程实现参考。

5. **局限性参考**：部分病原体（*C. glabrata*, *M. oryzae*）EC₅₀ 高达 10⁴ nM，灵敏度不足；文章也指出配体的临床特征化仍不充分——这些局限与项目选择靶标 GPCR 时的灵敏度要求直接相关。

---

## 关键引用（原文 References 节选）

1. **S. Jarque, M. Bittner, L. Blaha, K. Hilscherova**. Yeast biosensors for detection of environmental pollutants: current state and limitations. *Trends Biotechnol.* **34**, 408–419 (2016). — 综述酵母传感器现状与局限。

2. **A. Adeniran, M. Sherer, K. E. J. Tyo**. Yeast-based biosensors: design and applications. *FEMS Yeast Res.* **15**, 1–15 (2014). — 酵母生物传感器设计综述。

3. **V. Radhika et al.**. Chemical sensing of DNT by engineered olfactory yeast strain. *Nat. Chem. Biol.* **3**, 325–330 (2007). — GPCR 化学感应工程化先驱工作。

4. **Y. Pei, S. C. Rogan, F. Yan, B. L. Roth**. Engineered GPCRs as tools to modulate signal transduction. *Physiology* **23**, 313–321 (2008). — GPCR 信号调控工程综述。

5. **M. Wu, B. Repetto, D. M. Glerum, A. Tzagoloff**. Cloning and characterization of FAD1, the structural gene for flavin adenine dinucleotide synthetase of *Saccharomyces cerevisiae*. *Mol. Cell. Biol.* **15**, 264–271 (1995). — FAD1 辅因子工程基础。

6. **J. Heitman et al.** (Strum, J. M. Wingfield, E. T. Steenkamp). Causes and consequences of variability in peptide mating pheromones of ascomycete fungi. *Mol. Biol. Evol.* **28**, 1987–2003 (2011). — 真菌交配信息素多样性分析。

7. **M. D. Richardson**. Changing patterns and trends in systemic fungal infections. *J. Antimicrob. Chemother.* **56** (Suppl. 1), i5–i11 (2005). — 系统性真菌感染流行病学背景。

8. **G. E. Crooks, G. Hon, J.-M. Chandonia, S. E. Brenner**. WebLogo: a sequence logo generator. *Genome Res.* **14**, 1188–1190 (2004). — 序列 logo 分析工具（用于配体序列保守性分析）。
