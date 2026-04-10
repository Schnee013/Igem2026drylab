# Lengger et al. 2022 — 文献总结

> **完整标题**: Serotonin G Protein-Coupled Receptor-Based Biosensing Modalities in Yeast
> **期刊**: *ACS Sensors* 2022; **7**: 1323–1335
> **DOI**: 10.1021/acssensors.1c02061
> **作者**: Bettina Lengger, Emma E. Hoch-Schneider, Christina N. Jensen, Tadas Jakočiūnas, Anja A. Petersen, Thomas M. Frimurer, Emil D. Jensen, Michael K. Jensen
> **机构**: Novo Nordisk Foundation Center for Biosustainability, Technical University of Denmark (DTU), Kgs. Lyngby, Denmark

---

## 核心发现（5–10 bullets，含数据）

- **构建了 144 成员的 GPCR/Gα 组合库**：将 12 种人源 serotonin GPCRs（5-HT1A, 1B, 1D, 1E, 1F, 2A, 2B, 2C, 4, 5A, 6, 7）分别与 12 种 Gα 背景（Gpa1, Gαs/olf, Gα12, Gα13, Gαi1/2, Gαi3, Gαz, Gα15/16, Gαq/11, Gα14, Gαo, tGPA1 截断对照）组合，系统评估 serotonin 传感活性。
- **5-HT4 在几乎所有 Gα 背景下均可被 serotonin 激活**：在 pH 4.8 和 pH 7.2 条件下，5-HT4 是唯一在所有非截断 Gα 背景中均产生信号的受体；pH 4.8 时 Gαz 偶联的 fold induction 最高达 **64 倍**，Gαi3 为 48 倍，原生 Gpa1 为 46 倍。
- **pH 显著影响传感灵敏度（>4 个数量级）**：pH 7.2 时，许多在 pH 4.8 弱激活的受体显示约 10 倍的绝对荧光增加；但 pH 7.2 下 fold change 降低（背景也升高）。5-HT4 在 Gαz 背景下 pH 4.8 EC₅₀ 约 12.4 µM，pH 7.2 时灵敏度可进一步改变。
- **嵌合转录因子（chimeric TF）设计**：使用 Ste12 PRD 与 LexA DBD 融合（基于 Shaw et al. 2019 设计），驱动含 6× LexO 的 pLEU2m 合成启动子控制 sfGFP 表达，确保信号输出与 GPCR 偶联直接相关。
- **HPLC 验证传感器定量能力**：利用 5-HT4/Gαz 传感器检测工程酵母产生的 serotonin（通过 TPH 和 DDC 从 L-tryptophan 合成），传感器荧光与 HPLC 定量 serotonin 浓度呈线性相关（**R² = 0.91**）。
- **废培养基中的实际检测**：在添加 10%、25%、50% 体积比废培养基（72 h spent media）或 MilliQ 水的条件下，传感器 EC₅₀ 从 2.59 µM（25% MQ）上升至 11.21 µM（25% SM）和 1.70 µM（50% MQ）至 20.41 µM（50% SM），表明复杂基质适度影响灵敏度但不阻碍检测。
- **19 种人源 5-HT4 天然多态性的功能表征**：对 1000 Genomes Project 中 5-HT4 isoform b 的 19 个单氨基酸变体进行了剂量-响应曲线测定。多数变体保留功能但 EC₅₀ 和 Hill 系数有差异；测试区域覆盖胞外域、跨膜域和胞内环。
- **受体亚型展现 Gα 选择性**：5-HT1B、5-HT1E 和 5-HT4 在原生 Gpa1 背景下即可偶联，与其他亚型分离；5-HT1D 仅偶联 Gαi2，与文献中哺乳动物细胞数据一致。

---

## 实验方法（表格）

| 方法 | 用途 | 关键细节 |
|------|------|---------|
| 组合 GPCR/Gα 库构建 | 系统性偶联评估 | 12 GPCRs × 12 Gα = 144 菌株；GPCR 从着丝粒质粒表达，Gα 通过 CRISPR/Cas9 基因组整合 |
| 嵌合 Gα 构建 | 偶联异源 GPCR 至酵母通路 | 基于 Shaw et al. 2019 的底盘菌株；chimeric Gα 整合到 *GPA1* 位点 |
| sfGFP 荧光报告 | 定量 GPCR 信号激活 | LexA-Ste12 PRD chimeric TF → 6× LexO-pLEU2m → sfGFP；流式细胞术 10,000 events |
| 流式细胞术 | 单细胞荧光定量 | 三个技术重复，报告 fold change = 诱导（100 µM serotonin）/ 非诱导（0 µM）的中位荧光比 |
| 四参数 Hill 模型拟合 | EC₅₀ 和 Hill 系数测定 | Variable slope 四参数曲线拟合；浓度范围 0.01–1000 µM serotonin |
| HPLC 定量 | 验证传感器实际应用能力 | TPH 多拷贝工程酵母产 serotonin → 72 h 废培养基 → 传感器检测 → HPLC 对照 |
| pH 梯度实验 | 评估培养条件对灵敏度影响 | pH 2–7 梯度测试 5-HT4b/Gαz 传感器；SC 培养基和人血清 |
| 天然变体表征 | 多态性功能影响评估 | 1000 Genomes Project 19 个 5-HT4b SNPs → 单氨基酸突变 → 剂量-响应 |

---

## 关键数据（分小节）

### GPCR/Gα 偶联热图（Figure 1C 摘要）

- **最高 fold change（pH 4.8）**：5-HT4 / Gαz ≈ 64 倍
- **第二梯队**：5-HT4 / Gαi3 ≈ 48 倍；5-HT4 / Gpa1 ≈ 46 倍
- **仅少数受体在 Gpa1 背景下可检测**：5-HT1B、5-HT1E、5-HT4
- **完全无信号的受体**：5-HT2A、5-HT2B、5-HT5A、5-HT7 在所有 Gα 背景下均无法检测

### pH 效应

| 条件 | EC₅₀ 变化趋势 | 说明 |
|------|-----------|------|
| pH 4.8 | 较低绝对荧光，但高 fold change | 背景荧光低；诱导后信号/噪声比高 |
| pH 7.2 | 绝对荧光升高约 10 倍 | 背景也升高，fold change 下降；信号绝对值更高 |
| pH 对 Gα 选择性影响 | Gαz 在 pH 4.8 和 7.2 均为最佳 | Gαz C 末端第三位为甘氨酸（Gly），与最敏感设计相关 |

### HPLC 验证

- 传感器菌株：5-HT4 / Gαz + sfGFP
- 产 serotonin 菌株：BY4741 + TPH 多拷贝
- **R² = 0.91**（简单线性回归；sfGFP 荧光 vs HPLC serotonin 浓度）

### 代表性 EC₅₀ 数据（5-HT4 / 不同 Gα，pH 4.8）

文中报道 5-HT4 在所有 Gα 背景下的 EC₅₀ 范围横跨数个数量级。具体 EC₅₀ 值因 Gα 背景和 pH 条件而异，Gαz 背景下的 5-HT4b 参考 EC₅₀ ≈ 12.40 µM（pH 4.8，Figure 2）。

### 天然多态性（Figure 4）

- 19 种 5-HT4b 单氨基酸变体中，多数保留 serotonin 响应
- 部分变体显著改变 EC₅₀ 或 Hill 系数
- 变体位于胞外 N 端、跨膜区域、胞内环等不同位置

---

## 与项目的关系

本文建立的 144 成员 GPCR/Gα 组合库方法论，对项目中真菌 GPCR 异源表达系统的 Gα 选型有直接指导价值：

1. **系统性 Gα 选型方法论**：12 种 Gα 背景的组合筛选策略可直接应用于 GprC、Gpr2、Gpr3 等真菌 GPCR 的最优 Gα 偶联选择——无需预先假设偶联特异性，而是通过实验系统地覆盖所有可能的组合。

2. **嵌合 Gα C 末端甘氨酸规则**：文中观察到 Gα C 末端第三位为 Gly 的嵌合体（如 Gαz: GCGLY）通常灵敏度更高，为嵌合 Gpa1 C 末端序列设计提供了选择依据。

3. **pH 对传感器性能的关键影响**：pH 4.8 vs 7.2 导致灵敏度变化超过 4 个数量级，提示在设计传感器实验时必须严格控制培养基 pH。

4. **HPLC 验证工作流**：传感器检测 → HPLC 定量对照的验证策略可作为项目验证 ascaroside 传感器定量能力的参考范式。

5. **chimeric TF 设计参考**：LexA-Ste12 PRD 的嵌合转录因子设计与 Fan C & Yuan 2023 的 Gal4 DBD-Ste12 PRD 互为补充，提供了两种不同的信号读出重定向方案。

> 注：以上为文献内容与项目的关系分析，不含项目实验数据。

---

## 关键引用（原文 References 节选）

1. **Shaw et al. 2019 *Cell*** — 底盘菌株 Design 4 的来源；本文的嵌合 TF 设计和 Gα 整合策略直接基于此工作。
2. **Ehrenworth et al. (ref 14)** — 此前报道 5-HT1A 与 Gpa1 偶联，本文实验未能复现此结果（可能因着丝粒质粒 vs 高拷贝质粒表达差异）。
3. **Mukherjee et al. 2015 *ACS Synth. Biol.*** — GPCR-based chemical biosensors for medium-chain fatty acids，GPCR 传感器应用参考。
4. **Miettinen et al. 2022 *Nat Commun*** — 酵母 GPCR 大麻素生物传感器，使用类似的嵌合 Gα 策略。
5. **Ostrov et al. 2017 *Sci Adv*** — 番茄红素比色酵母传感器（Billerbeck 菌株），本文用于传感器设计比较。
6. **Kapolka et al. 2020 *Proc Natl Acad Sci USA*** — 高通量 CRISPR GPCR 多路平台，本文 GPCR 序列来源之一。
