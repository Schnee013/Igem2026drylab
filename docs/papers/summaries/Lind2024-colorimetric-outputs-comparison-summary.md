# Lind et al. 2024 — 文献总结

> **完整标题**: Evaluation and comparison of colorimetric outputs for yeast-based biosensors in laboratory and point-of-use settings
> **期刊**: *FEMS Microbiology Letters* 2024; **371**: fnae034
> **DOI**: 10.1093/femsle/fnae034
> **作者**: Andrea Clausen Lind, Florian David, Verena Siewers
> **机构**: Department of Life Sciences, Chalmers University of Technology, Gothenburg, Sweden; Novo Nordisk Foundation Center for Biosustainability, DTU, Denmark; Division of Systems and Synthetic Biology, Chalmers University of Technology, Gothenburg, Sweden

---

## 核心发现（5–10 bullets，含数据）

- **系统比较了三种比色输出**：在 Shaw et al. 2019 Design 4 菌株（S288C 背景）上，分别构建番茄红素（lycopene, 红色）、前脱氧紫色杆菌素（prodeoxyviolacein, 绿色）和前紫色杆菌素（proviolacein, 棕绿色）三种比色报告系统，在琼脂平板、液体培养和纸片试纸条三种场景下评估其检测时间（TOD）和色素强度。
- **琼脂平板：三种输出在 72 h 后表现相当**：1 µM α-factor 诱导 72 h 后，三种色素均可通过肉眼检测；培养基复杂度（SDC、SDC+5%YPD、YPD）对输出影响有限，但复杂培养基可小幅增加 lycopene 和 prodeoxyviolacein 的基线表达。
- **液体培养：lycopene 4 h 可检测，violacein 衍生物 24 h 仍不可测**：在 SDC+5%YPD 混合培养基中（模拟高复杂度临床样本），lycopene 在 4 h 即可通过吸光度检测到显著诱导信号（Figure 3A）；prodeoxyviolacein 和 proviolacein 在 24 h 采样窗口内均未产生可被吸光度法检测的信号差异。
- **纸片试纸条：lycopene 6 h 统计显著**：将菌株干燥于滤纸上，浸入含 1 µM α-factor 的 YPD 培养基后，lycopene 在 6 h 即产生统计显著的红色变化（**p = 0.028**，单侧 unpaired t-test）；24 h 后 lycopene 信号更强（**p = 2.6e−05**），prodeoxyviolacein（p = 0.0061）和 proviolacein（p = 0.0012）也在 24 h 产生统计显著信号但色素强度低于 lycopene。
- **番茄红素的 TOD 优势**：lycopene 的 TOD 在液体培养中为 **4 h**，纸片上为 **6 h**；而 prodeoxyviolacein 和 proviolacein 在液体中不可测量，在纸片上 TOD 为 **24 h**。lycopene 的 TOD 与先前报道（Ostrov et al. 2017: 6–9 h liquid, 8–9 h paper）基本一致。
- **通路基因数和诱导架构差异**：lycopene 通路含 5 个基因（crtE, crtB, 2× crtI, FAD1），其中 2 个（crtI）受 mating pathway 诱导；violacein 通路 prodeoxyviolacein 含 3 个基因（vioA, vioB, vioE），proviolacein 含 4 个基因（vioA, vioB, vioC, vioE），各仅 1 个基因（vioE）受诱导。
- **violacein 通路优化空间**：作者指出 violacein 通路未经系统优化（与 lycopene 通路在 Ostrov 2017/Shaw 2019 等中经历多轮迭代不同），未来通过酶表达量瓶颈优化、额外 crtI 类等价优化，可能改善 violacein 衍生物的输出。
- **菌株构建细节**：在 IMX581（CEN PK 背景）上使用 CRISPR/Cas9 进行基因组整合；Ste12-LexA 合成转录因子 + LexO(6x)-pLEU2m 合成启动子驱动报告基因；*FAR1* 缺失 + 修改后的 mating pathway 组件表达量。

---

## 实验方法（表格）

| 方法 | 用途 | 关键细节 |
|------|------|---------|
| 比色输出菌株构建 | 三种色素通路整合 | lycopene: crtE/crtB/2×crtI/FAD1（来自 *E. herbicola*）；violacein: vioA/vioB/vioE（±vioC）（来自 *C. violaceum*），基因密码子优化 |
| 琼脂平板检测 | 肉眼可见输出评估 | 点样（spot assay）于 SDC/SDC+5%YPD/YPD 平板，±1 µM α-factor，72 h，30°C |
| 液体培养吸光度检测 | 定量色素随时间积累 | SDC+5%YPD，30°C，200 rpm；每 2 h 测 lycopene（395/600 nm）、prodeoxyviolacein（395/750 nm）、proviolacein（395/750 nm）敏感波长（420/450/450 nm）|
| 纸片试纸条 | 模拟 POC 场景 | 菌株干燥于滤纸（Whatman）→ 浸入含/不含 1 µM α-factor 的 YPD → ImageJ 分析红/绿色强度 |
| 统计分析 | 显著性检验 | 单侧 unpaired t-test；R (v4.0.3) 数据分析与可视化 |
| 吸光度计算 | 色素定量 | 三波长法：2 个 robust 波长（不受色素影响）+ 1 个 sensitive 波长（色素主要贡献）；相对吸光度 = (受体+ / 输出null) 标准化 |

---

## 关键数据（分小节）

### 三种比色输出属性总结（Table 2）

| 属性 | Lycopene | Prodeoxyviolacein | Proviolacein |
|------|----------|-------------------|--------------|
| 输出颜色 | 红色 | 绿色 | 棕/绿色 |
| 通路基因数 | 5 | 3 | 4 |
| 受 mating pathway 诱导的基因 | 2× crtI | vioE | vioE |
| 通路基因 | crtE, crtB, 2× crtI, FAD1 | vioA, vioB, vioE | vioA, vioB, vioC, vioE |
| Robust 波长 (nm) | 395, 600 | 395, 750 | 395, 750 |
| Sensitive 波长 (nm) | 420 | 450 | 450 |
| 液体培养 TOD (h) | **4** | 不可测 | 不可测 |
| 纸片 TOD (h) | **6** | 24 | 24 |

### 纸片试纸条统计显著性（Figure 4）

| 时间点 | Lycopene p 值 | Prodeoxyviolacein p 值 | Proviolacein p 值 |
|--------|-------------|----------------------|-----------------|
| 6 h | **0.028** | 不显著 | 不显著 |
| 24 h | **2.6e−05** | **0.0061** | **0.0012** |

### 液体培养时间序列（Figure 3）

- **Lycopene**：4 h 起诱导组（1 µM α-factor）与非诱导组出现可测量差异，并持续升高至 24 h
- **Prodeoxyviolacein**：24 h 内诱导组与非诱导组无可检测差异（吸光度法灵敏度不足）
- **Proviolacein**：同上，24 h 内不可检测

### 琼脂平板定量（Figure 2）

- 72 h 后三种色素在 SDC、SDC+5%YPD、YPD 培养基上均可肉眼检测
- lycopene 和 prodeoxyviolacein 在复杂培养基（YPD）中基线略升高
- proviolacein 的基线表达不受培养基影响

---

## 与项目的关系

本文是目前唯一系统比较酵母 GPCR 传感器比色输出选项的研究，对项目的显色报告系统选型有直接参考价值：

1. **lycopene 为首选比色输出**：综合 TOD、信号强度和场景适用性，lycopene 在液体培养（4 h）和纸片（6 h）中均显著优于 violacein 衍生物，支持项目选择 lycopene 作为初始比色输出方案。

2. **violacein 衍生物的潜在优势**：虽然 TOD 较长，但 prodeoxyviolacein 仅需 3 个基因（vs lycopene 5 个），通路更简洁；若经过系统优化（酶表达量调整、辅因子工程），可能成为备选方案。

3. **纸片试纸条验证**：本文的纸片检测方案（菌株干燥 → 浸泡 → ImageJ 分析）可作为项目 POC 产品原型验证的直接实验模板。

4. **定量方法参考**：三波长吸光度法（2 robust + 1 sensitive）为不同色素的定量提供了标准化方案，避免了细胞密度和培养基颜色的干扰。

5. **底盘菌株兼容性**：本文使用的 Design 4 菌株与 Shaw 2019 一致，确认了该底盘对多种比色输出通路的兼容性。

> 注：以上为文献内容与项目的关系分析，不含项目实验数据。

---

## 关键引用（原文 References 节选）

1. **Shaw et al. 2019 *Cell*** — Design 4 底盘菌株来源；本文的信号通路组件（修改后的 GPA1、STE12-LexA、pLexO）直接沿用此设计。
2. **Ostrov et al. 2017 *Sci Adv*** — lycopene 比色系统的原始报道（CrtE/CrtB/CrtI + FAD1）；本文的 lycopene 菌株基因组整合架构来源于此。
3. **Lee et al. 2013; DeLoache et al. 2016; Rantasalo et al. 2018** — violacein 通路在酵母中的先前工作；本文指出这些系统产量较低但优化空间存在。
4. **Miettinen et al. 2022 *Nat Commun*** — 生物发光（NanoLuc）系统，TOD 约 30 min，但需要外源试剂；本文用作 TOD 比较基准。
5. **Adeniran et al. 2015 *FEMS Yeast Res*** — 酵母生物传感器设计综述。
6. **Billerbeck et al. 2018 *Nat Commun*** — lycopene 纸片 dipstick 原始应用（36 周室温稳定性数据来源）。
