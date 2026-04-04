# Hsueh et al. (2013) — 文献总结

> **原文**: Hsueh, Y.-P., Mahanti, P., Schroeder, F.C. & Sternberg, P.W. (2013). Nematode-Trapping Fungi Eavesdrop on Nematode Pheromones. *Current Biology*, 23, 83–86.
> **DOI**: https://doi.org/10.1016/j.cub.2012.11.035
> **物种**: *Arthrobotrys oligospora* 及多种近缘捕食性真菌

---

## 核心发现

1. **Nematophagous fungi 能感知线虫分泌的 ascaroside pheromone** 并以此触发 trap morphogenesis（捕陷器形态发生）
2. **合成 ascaroside 即可诱导捕陷器形成**，无需活体线虫存在
3. 不同 ascaroside 的诱导效率不同：**碳链长度 7–9 的 ascaroside（ascr#1, ascr#3, ascr#7）效果最强**
4. Ascaroside 诱导的 trap formation **依赖营养限制条件**（nutrient starvation），在富营养培养基上被完全抑制
5. Ascaroside 感应在 Orbiliaceae 科**多个物种中保守**，但不同物种对不同 ascaroside 的响应谱各异
6. 这是**首次证明微生物捕食者能"窃听"（eavesdrop）后生动物的化学通讯信号**来调控自身形态发生

---

## 实验方法

### Trap induction assay

- *A. oligospora* 在 20 mL LNM agar plate 上 25°C 培养 4–14 天至菌落直径约 5 cm
- 在菌丝上滴加 1 μL 1 mM ascaroside 溶液（终浓度 50 nM），或等体积溶剂对照（25% EtOH）
- 48 h 后在解剖显微镜下计数 ascaroside 滴加位点周围 1.5 cm 半径内的 trap 数量
- 每个物种-ascaroside 组合独立重复 3–6 次

### Ascaroside 筛选

- 共测试 **10 种合成 ascaroside**：ascr#1–#10（覆盖多种碳链长度和修饰类型）
- 包括广泛分泌的种类（如 ascr#1, ascr#9）和少数物种特有的种类（如 ascr#2, ascr#8）
- 测试浓度范围：50 pM–50 nM

### 营养条件测试

- 比较 LNM（低营养培养基）、LNM + 2% glucose、LNM + 0.5% (NH₄)₂SO₄、PDA（富营养培养基）上的 trap induction
- 使用 50 nM ascr#7 作为诱导物

### 物种比较

- 测试 8 种 Orbiliaceae 科真菌对 ascaroside 的响应
- 使用 ITS 区域序列构建 Bayesian inference phylogeny

---

## 关键数据

### 1. Ascaroside 特异性（*A. oligospora*）

| Ascaroside | 碳链长度 | Trap induction（50 nM, 48 h） |
|------------|---------|-------------------------------|
| ascr#1 | C7 | **强** |
| ascr#3 | C9 | **强** |
| ascr#7 | C7-modified | **最强**（~90 traps/cm²） |
| ascr#5 | C9 | 中等 |
| ascr#9 | C5-modified | 弱 |
| ascr#2, #4, #6, #8, #10 | 各异 | 弱或无 |
| 对照（溶剂） | — | ~0 traps/cm² |

### 2. 浓度依赖性（ascr#7, *A. oligospora*）

| 浓度 | Trap 数量 |
|------|----------|
| 50 nM | ~100 traps/cm² |
| 5 nM | ~50 traps/cm² |
| 0.5 nM | ~20 traps/cm² |
| 50 pM | ~5 traps/cm² |
| 对照 | ~0 traps/cm² |

- **平均有效浓度低至 0.5 nM**，在线虫种群附近的生理浓度范围内 [15]

### 3. 营养条件依赖性（ascr#7, *A. oligospora*）

| 培养基 | Trap 数量（50 nM ascr#7） |
|--------|-------------------------|
| LNM | ~140 traps/cm² |
| LNM + 2% glucose | ~60 traps/cm²（显著减少） |
| LNM + 0.5% (NH₄)₂SO₄ | ~20 traps/cm²（严重抑制） |
| PDA | ~0 traps/cm²（完全抑制） |

- **氮源补充对 trap induction 的抑制效果最强** → nitrogen starvation 是 ascaroside 响应的前提

### 4. 跨物种保守性

| 物种 | Trap 类型 | Ascaroside 响应 | 最强诱导物 |
|------|----------|----------------|----------|
| *A. oligospora* | AN | 有 | ascr#1, #3, #7 |
| *A. musiformis* | AN | 有 | ascr#1, #5, #9 |
| *A. javanica* | AN | 有 | ascr#3, #7, #9 |
| *Dactylella gampsospora* | AN | 有 | ascr#3, #7 |
| *A. brochopaga* | CR | 无 | — |
| *D. polybrocha* | CR | 无 | — |
| *Monacrosporium doedycoides* | CR | 无 | — |
| *Gamsylella gephyropaga* | AC | 无 | — |

- AN = adhesive networks（粘性网络）；CR = constricting rings（收缩环）；AC = adhesive columns（粘性柱）
- **仅产生 AN 型 trap 的 4 个物种响应 ascaroside**
- **产生 CR 或 AC 型 trap 的 4 个物种均不响应**
- 4 个响应物种在系统发育上形成独立 clade
- 不同物种对不同 ascaroside 的响应谱不同 → 可能与其偏好的猎物物种的 ascaroside 分泌谱相关

---

## 讨论要点

1. **Ascaroside 作为"线虫相关分子模式"（nematode-associated molecular pattern, NAMP）**：类比于动植物识别 MAMPs/PAMPs，ascaroside 被捕食性真菌用作识别猎物的分子标志
2. **进化逻辑**：ascaroside 在线虫生物学中不可或缺（调控 dauer formation、交配、社会行为），因此作为猎物检测信号具有高度可靠性
3. **捕食-被捕食共进化**（predator-prey coevolution）：真菌"窃听"线虫种间信号的能力可能在进化上持续被选择
4. **AN vs CR/AC 物种差异**：是否响应 ascaroside 可能与 trap 类型和进化谱系相关；不响应的物种可能使用其他线虫来源信号（如非 ascaroside 代谢物）
5. 作者预测这一发现可推广至其他涉及线虫的跨界互作系统

---

## 与项目的关系

### 1. 奠基性论文地位

本文是 **首次证明 nematophagous fungi 能感知 ascaroside 的开创性工作**。后续所有关于 Gpr2/Gpr3（Kuo et al. 2024）和 GprC（Hu et al. 2024）受体鉴定的工作均建立在本文发现之上。本文作者 Hsueh 和 Schroeder 也是后续受体鉴定工作的核心作者。

### 2. Ascaroside 检测灵敏度参考

- 本文证明 **0.5 nM ascaroside 即可触发 trap formation**，这为 biosensor 的灵敏度设计提供了天然基准
- 50 nM 下的强响应（~100 traps/cm²）是可靠的阳性对照浓度
- 这些数据可用于评估工程化 GPCR biosensor 的检测限是否达到生理相关水平

### 3. Ascaroside 选择依据

- 本文系统比较了 10 种 ascaroside 的诱导效率
- **ascr#3 和 ascr#7 是 *A. oligospora* 中最有效的诱导物** → 这正是后续 Kuo et al. 2024 中 Gpr2/Gpr3 对接研究选用的配体
- 对 biosensor 项目来说，优先选择 ascr#3、ascr#7（以及 Hu et al. 中使用的 ascr#18）作为目标检测物是合理的

### 4. 营养条件对信号通路的调控

- Ascaroside 响应依赖 nitrogen starvation → 暗示信号通路与营养感知通路存在 crosstalk
- 这对酵母底盘方案有启示：需要考虑宿主细胞的代谢状态是否影响 GPCR 信号输出

### 5. 物种选择参考

- 本文测试的 8 个物种中，仅 AN 类群（包括 *A. oligospora*、*A. musiformis*、*A. javanica*、*D. gampsospora*）对 ascaroside 有响应
- Kuo et al. 2024 使用 *A. oligospora*，Hu et al. 2024 使用 *A. flagrans*（本文未测试但属于同一科）
- 如果项目需要比较不同物种的 GPCR，本文提供了物种-ascaroside 响应谱的基础数据

### 6. 本文的局限性（后续工作弥补）

- **未鉴定受体**：本文只证明了"真菌能感知 ascaroside"这一现象，但未鉴定参与感知的具体受体分子 → 直到 2024 年 Kuo et al. 和 Hu et al. 才分别鉴定了 Gpr2/Gpr3 和 GprC
- **未解析信号通路**：仅证明需要 nutrient starvation，未阐明下游信号通路 → 后续工作揭示了 cAMP-PKA 和 MAPK 两条通路
- **未进行分子对接**：无结构生物学或计算化学数据

---

## 关键引用

| 引用编号 | 参考文献 | 与项目的潜在关联 |
|---------|---------|--------------|
| [2] | Srinivasan et al. (2008) *Nature* 454, 1115 | Ascaroside 在 *C. elegans* 中调控交配和发育的开创性工作 |
| [3] | Srinivasan et al. (2012) *PLoS Biol.* 10, e1001237 | Ascaroside 的"模块化文库"概念 |
| [4] | Butcher et al. (2007) *Nat. Chem. Biol.* 3, 420 | Ascaroside 调控 dauer formation |
| [9] | von Reuss et al. (2012) *JACS* 134, 1817 | Ascaroside 比较代谢组学，鉴定了 >100 种 ascaroside |
| [12] | Choe et al. (2012) *Curr. Biol.* 22, 772 | Ascaroside signaling 在线虫中广泛保守 |
| [15] | Izrayelit et al. (2012) *ACS Chem. Biol.* 7, 1321 | 线虫群体中 ascaroside 的生理浓度测定 |
| [17] | Scholler & Rubner (1994) *Microbiol. Res.* 149, 145 | *A. oligospora* 捕食活性依赖营养条件 |

---

## 版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-03 | v1.0 | 初始总结，忠实于原文内容 |
