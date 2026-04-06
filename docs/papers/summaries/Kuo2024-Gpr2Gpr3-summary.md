# Kuo et al. (2024) — Gpr2/Gpr3 文献总结

> **原文**: Kuo, C.-Y., Tay, R.J., Lin, H.-C., Juan, S.-C., Vidal-Diez de Ulzurrun, G., Chang, Y.-C., Hoki, J., Schroeder, F.C. & Hsueh, Y.-P. (2024). The nematode-trapping fungus *Arthrobotrys oligospora* detects prey pheromones via G protein-coupled receptors. *Nature Microbiology*, 9, 1738–1751.
> **DOI**: https://doi.org/10.1038/s41564-024-01679-w
> **物种**: *Arthrobotrys oligospora* (TWF154 wild isolate)

---

## 核心发现

*A. oligospora* 使用两类 GPCR 感知不同的线虫来源信号：
1. **碳受体家族（Carbon receptor family）**：Gpr2 和 Gpr3，负责感知 ascaroside（ascr#3 和 ascr#7），通过 Gpa2 激活 cAMP–PKA 通路
2. **Pth11-like GPCR 家族**：Gin 受体（GIN1–GIN8 等），负责感知非 ascaroside 的线虫来源信号，部分通过 MAPK 通路

两类受体均激活保守的 cAMP–PKA 信号通路来触发捕陷器发育。

---

## Ascaroside 在捕陷器诱导中的作用

### 实验证据

- 比较 WT *C. elegans* 与 *daf-22* 突变体（不能合成生物活性 ascaroside）诱导捕陷器的能力
- *daf-22* 突变体仍能触发捕陷器形成，但数量显著降低（约 75%）
- → *A. oligospora* 能感知 ascaroside 以外的其他线虫来源信号
- 单独 ascr#3 或 ascr#7 即可触发捕陷器形成，但数量远低于活体 *C. elegans*

---

## 基因组分析：*A. oligospora* 中的 GPCR 扩增

### GPCR 鉴定

- 对 *A. oligospora* TWF154 基因组进行分析
- 使用 TMHMM 2.0 和 Phobius 鉴定 83 个含 7 跨膜结构域的蛋白
- 根据序列同源性和结构相似性分为 **10 个类别**（Supplementary Table 1）
- 其中 **69 个属于 Pth11-like GPCR 家族** → 该家族在 *A. oligospora* 中大规模扩增
- Pth11-like GPCR 在 Pezizomycotina 亚门丝状真菌中特有
- 另有 3 个与酵母碳受体 Gpr1 同源的 GPCR：**Gpr1**（与 *S. cerevisiae* Gpr1 最相似）、**Gpr2** 和 **Gpr3**（两个旁系同源物）
- 还编码其他 GPCR 类别：推定信息素受体（Ste2, Ste3 同源物）等

### 转录组分析

- 分析 *C. elegans* 暴露后不同时间点的 RNA-seq 数据
- **Pth11-like GPCR（GIN 家族）**：32 个基因在线虫暴露后显著上调（q-value < 0.05, beta > 0.2），命名为 GIN（GPCR Induced by Nematodes）
- **碳受体家族**：**GPR2** 和 **GPR3** 在线虫暴露后也上调
- 多数 GIN 基因在暴露前表达极低，暴露后迅速上调
- 表达量最高的 5 个 GIN：**GIN1, GIN3, GIN7, GIN8** + 一个
- GPR2 和 GPR3 在暴露 2h 后即上调（与 GIN 类似的时间模式）
- Ste12 转录因子调控：GPR3, GIN1, GIN7, GIN8 的上调依赖 Ste12；GPR2 和 GIN3 的上调可能不依赖 Ste12

---

## 碳受体家族 GPCR（Gpr2 和 Gpr3）功能表征

### 基因敲除实验

| 突变体 | 对 ascr#3 的响应 | 对 ascr#7 的响应 | 对活体 C. elegans 的响应 |
|--------|---------------|---------------|---------------------|
| WT | ~30 traps/cm² | ~40 traps/cm² | ~500 traps/cm² |
| Δgpr1 | 正常 | 正常 | 正常 |
| **Δgpr2** | **显著减少** | **显著减少** | 正常 |
| **Δgpr3** | **显著减少** | **显著减少** | 正常 |
| Δgpr2gpr3 | 与单敲除相似，无更严重表型 | 与单敲除相似 | 显著减少（P=0.01） |

- **关键结论**：Gpr2 和 Gpr3 **非冗余地**参与 ascr#3 和 ascr#7 的感应
- 所有 gpr 突变体对活体 *C. elegans* 仍有部分响应 → 存在额外受体（即 Gin 家族）

### 过表达实验

- 使用 *A. nidulans* gpdA 启动子组成型表达 GPR2 和 GPR3
- 过表达株系对 ascr#3 和 ascr#7 的捕陷器形成能力**显著增强**
- → 两个受体的表达量直接影响 ascaroside 感应灵敏度

### 受体内吞（Endocytosis）

- 使用 Gpr2-GFP 和 Gpr3-GFP 融合蛋白观察配体诱导的内吞
- 无 ascr#7 时：表达低，主要在细胞膜（FM4-64 染色确认）
- ascr#7 暴露 2h 后：表达迅速增强，受体被内化到液泡（CellTracker Blue CMAC 染色确认）
- 捕陷器形成后（10h）：两个受体在捕陷器细胞中信号更强，持续内吞
- → ascr#3 和 ascr#7 触发 Gpr2 和 Gpr3 的配体诱导内吞

---

## Gpr2/Gpr3 与 Gpa2 互作，调控 cAMP–PKA 通路

### Co-IP 实验（在 *S. cerevisiae* 中异源表达）

- Gpr2–3×HA 和 Gpr3–3×HA 分别与 Gpa1–Myc、Gpa2–Myc、Gpa3–Myc 共表达
- **Gpr2 和 Gpr3 均与 Gpa2 强烈互作**，但不与 Gpa1 或 Gpa3 互作
- → Gpr2 和 Gpr3 通过 Gpa2 激活下游 cAMP–PKA 通路

### Gpr2 形成异源二聚体

- Gpr2–3×HA 与 Gpr3–Myc 在 *S. cerevisiae* 中 co-IP 证实 **Gpr2 和 Gpr3 形成异源二聚体**
- → Gpr2 可能通过与 Gpr3 二聚化来介导对 ascr#3 和 ascr#7 的响应

### cAMP 水平测量

- WT 在线虫诱导后 cAMP 水平显著升高
- Δgpr2 和 Δgpr3 突变体中 cAMP **不升高**
- → 两个受体均参与激活 cAMP–PKA 通路

### 遗传学验证

- 表达显性活化 Gpa2（GPA2^Q208L）：
  - 在 Δgpr2 背景下：显著增加 ascr#3 和 ascr#7 诱导的捕陷器数量
  - 在 Δgpr3 背景下：无明显效果（与 Gpr3 与 Gpa2 的互作较弱一致）
- → Gpr2 和 Gpa2 之间存在强遗传互作

---

## Gin 受体（Pth11-like GPCR）感知非 ascaroside 信号

### Gin 受体功能

| 突变体 | 对 ascaroside 的响应 | 对活体 C. elegans 的响应 |
|--------|-------------------|---------------------|
| Δgin1 | 正常 | 减少（~200 traps/cm²） |
| Δgin3 | 正常 | **严重减少**（~4 traps/cm²） |
| Δgin4 | 正常 | 减少（~200 traps/cm²） |
| gin1GIN1 回补 | - | 部分恢复 |
| gin3GIN3 回补 | - | 部分恢复 |
| gin4GIN4 回补 | - | 部分恢复 |

- **关键结论**：Gin 受体不参与 ascaroside 感应，而是感知其他线虫来源信号
- **GIN3** 是活体线虫诱导中最关键的 Gin 受体

### Gin 受体的捕陷器形态

- 多数 gin 突变体形成正常的三环菌丝捕陷器（3 hyphal loops）
- **Δgin3** 只形成单环，形态缺陷最严重

### Gin 受体内吞

- Gin1-GFP 和 Gin3-GFP：无线虫时表达低，定位于细胞膜
- *C. elegans* 暴露 2h 后迅速上调并内化
- 10h 后在捕陷器中信号强，且被内吞
- → 类似于 Gpr2/Gpr3 的配体诱导内吞模式

---

## Gin3 与 Gpa2 互作，调控 cAMP–PKA 通路

### Co-IP 实验

- Gin3–3×HA 与 Gpa–Myc 共表达
- Gin3 与 **Gpa2 强烈互作**，与 Gpa1 和 Gpa3 微弱互作
- → Gin3 主要通过 Gpa2 激活 cAMP–PKA 通路

### cAMP 水平

- Δgin3 突变体中线虫诱导后 cAMP 不显著升高
- gin3GIN3 回补株部分恢复
- → Gin3 也参与 cAMP–PKA 通路的激活

---

## Gpr2、Gpr3 和 Gin3 调控 MAPK 磷酸化

### 三个 MAP kinase

| MAP kinase | 对应名称 | 功能 |
|-----------|--------|------|
| Fus3 | p38 | 高渗透压信号通路；在早期被磷酸化（2-4h） |
| Slt2 | p44/42 | 细胞壁完整性通路；持续磷酸化 |
| Hog1 | - | 参与捕陷器形态发生 |

### 磷酸化分析结果

- **Fus3 和 Slt2**：在 WT、Δgpr2、Δgpr3、Δgin3 和 Δgin3GIN3 中均在线虫暴露后被磷酸化
- **Hog1**：
  - WT 中磷酸化水平在线虫暴露后降低
  - Δgpr2、Δgpr3、Δgin3 中 Hog1 磷酸化水平**不变**（不降低）
  - → Gpr2、Gpr3 和 Gin3 可能调控 Hog1 的磷酸化动力学
- 存在复杂的通路间串扰（crosstalk）

---

## 分子对接结果（与本项目直接相关）

### 方法

- 使用 **SwissDock** web 服务（非 AutoDock Vina）
- 受体结构：AlphaFold 预测
- 配体化学结构：从 **ChemSpider** 获取（ascr#3 和 ascr#7）
- 使用 **TM-align** 进行蛋白结构比对

### Gpr2 与 SRBC-66（*C. elegans* ascaroside 受体）结构比较

- TM-align TM score ≈ 0.7 → 结构高度相似（尽管序列相似性低）
- Gpr3 与 SRBC-66 的 TM score 也约为 0.7

### 对接结合能（ΔG 值）

| 受体 | ascr#3 | ascr#7 |
|------|--------|--------|
| **Gpr2** | **−6.99 kcal/mol** | **−7.07 kcal/mol** |
| SRBC-66 | −7.47 kcal/mol（ascr#3） | - |
| **Gpr3** | **−7.05 kcal/mol** | **−6.41 kcal/mol** |

- Gpr2 对 ascr#3 和 ascr#7 的预测亲和力与 SRBC-66 对 ascr#3 的亲和力相似

### 关键结合残基

| 受体 | ascr#3 结合残基 | ascr#7 结合残基 |
|------|-------------|-------------|
| Gpr2 | **Y168** | **Y168** |
| SRBC-66 | **N161** | - |

> **注**：原文（p.1741）写的是 "Y168 and N161 in Gpr2 and SRBC-66, **respectively**"，即 Y168 仅属于 Gpr2，N161 仅属于 SRBC-66，两者不共享。

- Gpr2 和 SRBC-66 的 ascaroside 结合口袋位于**胞外结构域**（extracellular domain）
- 尽管来自进化距离遥远的物种（真菌 vs 线虫），结合口袋在结构上保守

### 重要说明

- 本文使用的是 **SwissDock**（而非 Hu et al. 中的 AutoDock Vina）
- 未检测到受体残基与 ascaroside 之间的强氢键 → 结合可能主要通过疏水作用和范德华力
- 本文**未对 ascr#18 进行对接**（仅对接了 ascr#3 和 ascr#7）

---

## Discussion 核心观点

1. **两类 GPCR 分工明确**：碳受体（Gpr2/Gpr3）感知 ascaroside，Pth11-like（Gin）感知非 ascaroside 信号
2. ascaroside 感知只是线虫检测的一部分；ascr#3 和 ascr#7 可能代表了一个复杂感知网络的冰山一角
3. 碳受体 GPCR 在真菌中演化出了多样化的配体感知能力（从糖到 ascaroside）
4. Pth11-like GPCR 的扩增（69 个）是 *A. oligospora* 特有的，可能与其捕食性生活方式的进化相关
5. Gin3 与多个 Gα 互作可能允许它激活不同的下游通路
6. Gpr2、Gpr3 和 Gin3 共同调控 Hog1 磷酸化，暗示通路间复杂串扰

---

## Methods 中的关键实验参数

### 菌株与培养

- *A. oligospora* TWF154（野生分离株）
- 基因敲除在 ku70 突变体背景下进行（提高同源重组效率）
- 培养：PDA（常规），LNM（低营养培养基，用于捕陷器诱导）

### 捕陷器诱导实验

- 3.5 cm LNM plate, 25°C, 48h
- 加入 30 只 *C. elegans* N2 L4 幼虫
- 6h 后移除线虫，24h 后在 0.5 cm 范围内计数
- Ascaroside 处理：1 mM ascr#3 或 ascr#7 加在菌丝边缘 2 mm 处，2 天后计数

### 对接方法

| 参数 | 值 |
|------|------|
| 对接工具 | **SwissDock**（web 服务） |
| 受体结构 | AlphaFold 预测 |
| 配体来源 | **ChemSpider** |
| 结构比对 | **TM-align**（TM score > 0.5 视为相似） |
| 配体 | ascr#3, ascr#7 |
| 对接受体 | Gpr2, Gpr3, SRBC-66 |

### 数据可用性

- *A. oligospora* TWF154 基因组：GenBank **SOZJ00000000**
- RNA-seq 数据：GEO **GSE233568**

---

## 与本项目的关键关联

1. **Gpr2 (G1X9E2) 和 Gpr3 (G1XJN1)** 是 *A. oligospora* 中 ascaroside 感应的核心受体，功能已验证
2. 两者通过 **Gpa2** 激活 **cAMP–PKA 通路**（与 Hu et al. 中 GprC 通过 GasA 激活 MAPK 通路不同）
3. **Gpr2/Gpr3 可形成异源二聚体**，这对酵母异源表达策略有参考意义
4. 本文对接使用 **SwissDock**（非 AutoDock Vina），且仅对接了 ascr#3 和 ascr#7，**未包含 ascr#18**
5. 对接结合能：Gpr2 对 ascr#3 约 −7.0, ascr#7 约 −7.1；Gpr3 对 ascr#3 约 −7.1, ascr#7 约 −6.4
6. 关键结合残基：Gpr2 中 **Y168**（SRBC-66 中对应 N161）
7. RNA-seq 数据（GEO GSE233568）可用于丝状真菌方案的启动子挖掘
8. 过表达可增强 ascaroside 灵敏度 → 对酵母底盘方案的表达策略有参考
9. **Gin 受体（特别是 Gin3）** 检测非 ascaroside 信号，如果项目需要检测活体线虫（而非纯 ascaroside），需考虑此通路

---

## 版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-03 | v1.0 | 初始总结，忠实于原文内容 |
| 2026-04-06 | v1.1 | 修正 N161 归属：N161 属于 SRBC-66（非 Gpr2），Gpr2 唯一确认结合残基为 Y168；修正"关键关联"第 6 条 |
