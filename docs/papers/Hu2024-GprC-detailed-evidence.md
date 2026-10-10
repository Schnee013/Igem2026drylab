---
paper_id: Hu2024
document_role: source-backed detailed evidence audit
source: Hu et al. 2024 version of record, Extended Data, publisher Source Data, Supplementary Tables, Reporting Summary, and original blot files
as_of: 2026-08-12
allowed_use: interpret the Hu2024 GprC/GasA evidence, audit figure claims, and delimit docking, mitochondrial, and direct-binding claims
update_trigger: correction to the version of record, newly released receptor-ligand binding data, or a new audit of the publisher files
---

# Hu et al. (2024) 详细证据审读：GprC–GasA、线粒体响应与 ascaroside 受体模型

> **对应摘要**：[Hu2024-GprC-summary.md](summaries/Hu2024-GprC-summary.md)
>
> **论文**：Hu, X. et al. *GprC of the nematode-trapping fungus Arthrobotrys flagrans activates mitochondria and reprograms fungal cells for nematode hunting*. *Nature Microbiology* 9, 1752–1763 (2024).
>
> **DOI**：<https://doi.org/10.1038/s41564-024-01731-9>
>
> **研究菌株**：*Arthrobotrys flagrans* CBS 349.94

## 1. 先给结论

这篇论文建立的主线是：线虫到来后，*A. flagrans* 需要 GprC 和 GasA 完成两类变化——一类是以 `artA` 抑制和捕陷器形成代表的细胞重编程，另一类是菌丝尖端的呼吸增强。GprC 和 GasA 同时出现在质膜和线粒体相关位置，由此形成了一个“同一受体–G 蛋白轴连接猎物识别与能量动员”的模型。

其中较有力的证据包括：

1. `gprC` 缺失使捕陷器显著减少，回补恢复，过表达增加捕陷器；`gasA` 缺失则使捕陷器几乎完全消失；
2. `artA` 启动子对线虫和 ascr#18 的抑制反应依赖 GprC 与 GasA；
3. GprC–GFP 的成像和膜分级支持质膜/线粒体双定位，split-GFP 与酵母双杂交支持 GprC–GasA 相互作用；
4. 线虫诱导后的正常 OCR 增强依赖 GprC 和 GasA；
5. GprC 点突变、线虫受体–GprC 嵌合体和 AutoDock Vina 模型共同支持胞外正构口袋与 S/R motif 的功能模型。

论文尚未把下列环节闭合：

1. 没有直接测量 ascaroside 与 GprC 的结合，也没有实验解析的 GprC–配体结构；
2. 没有把质膜 GprC 和线粒体 GprC 分开操纵，因此不能把 OCR/ROS 表型只归因于线粒体定位池；
3. Fig. 3b 反而显示所测 HogA、MakA、MakB 的磷酸化不依赖 GprC–GasA，不能把该轴写成“通过这三条 MAPK”；
4. 点突变体和嵌合体只用 RT–PCR 确认转录，蛋白丰度、折叠和定位没有逐一验证；
5. docking 的实际输入坐标、完整输出和随机运行身份没有公开，只能近似重建，不能严格复现。

最合适的总括是：**遗传、细胞定位、reporter、呼吸和结构功能证据共同支持 GprC–GasA 是线虫/ascaroside 响应的重要上游轴，并支持 GprC 参与受体样识别；直接配体结合、线粒体定位池的独立因果作用以及从受体到具体效应器的完整通路仍待实验闭合。**

---

## 2. 核查材料与证据用语

### 2.1 本次直接核查的材料

| 材料 | 本次用途 |
|---|---|
| [版本记录正文](https://doi.org/10.1038/s41564-024-01731-9) | 正文、Methods、主图和 Extended Data；本地 PDF SHA256 为 `ca37844b37097bf036d9f5814f574e12b334296da885a12f57a9f1818d3a7125` |
| [Supplementary Information](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01731-9/MediaObjects/41564_2024_1731_MOESM1_ESM.pdf) | 菌株、质粒和引物表 |
| [Reporting Summary](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01731-9/MediaObjects/41564_2024_1731_MOESM2_ESM.pdf) | 软件版本与研究设计信息 |
| [Source Data](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01731-9/MediaObjects/41564_2024_1731_MOESM3_ESM.xlsx) | Fig. 1b/c/e/f/g、2a、3c/d、4b 和 Extended Data Fig. 2e 的原始数值 |
| [原始 western blots](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01731-9/MediaObjects/41564_2024_1731_MOESM4_ESM.pdf) | Fig. 2c/d、Fig. 3b 与 Extended Data Fig. 3 的未裁剪条带 |
| [原始 PCR/Southern blots](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41564-024-01731-9/MediaObjects/41564_2024_1731_MOESM5_ESM.pdf) | 删除株、回补株、突变体和嵌合体的构建验证 |

本文中的均值、标准差和 P 值沿用官方 Source Data。作者通常使用双尾非配对 Student's *t* 检验，样本量多为 3 个生物学重复；这些多组比较没有报告多重检验校正。Fig. 3c 的 `n = 15` 来自 3 条菌丝、每条 5 个荧光区域，不能当作 15 个独立生物学重复。

### 2.2 本文如何区分证据

| 用语 | 含义 |
|---|---|
| 直接测量 | 实验直接读出所讨论的关系，例如 OCR、reporter 或捕陷器数量 |
| 支持 | 数据与该解释一致，但仍存在其他机制解释 |
| 预测 | 来自定位算法、AlphaFold 或 docking |
| 未显示 | 论文及官方附件中没有对应数据 |

---

## 3. 论文的逻辑链

论文不是从“已知 GprC 是受体”出发，而是逐层把候选收敛成一个机制模型：

1. **候选筛选**：以已知真菌 GPCR 为 bait，在基因组中找到 14 个候选，再聚焦 GprA–F；
2. **遗传收敛**：六个删除株中 `ΔgprC` 的捕陷器下降最明显，`gprC` 又被线虫诱导，并呈剂量方向一致的“删除下降—回补恢复—过表达上升”；
3. **下游配对**：三个 Gα 中 `gasA` 对捕陷器形成最关键，GprC 与 GasA 在细胞内共定位并相互作用；
4. **输出拆分**：`artA` reporter 指向基因重编程，ROS/OCR 指向呼吸调节；
5. **受体模型加强**：线虫 ascaroside 受体嵌合体、点突变和 docking 把功能定位到胞外口袋及 S/R motif；
6. **统一模型**：GprC–GasA 在质膜响应外界信号，同时在线粒体相关位置参与呼吸调节。

这个逻辑强在多种证据相互呼应，弱点则集中在“受体是否直接结合 ascaroside”和“双定位如何分别产生因果效应”两个接口。

---

## 4. Fig. 1：从六个 GPCR 候选收敛到 GprC–GasA

### 4.1 候选是怎样来的

作者以 *Aspergillus nidulans* 和 *Saccharomyces cerevisiae* GPCR 为 bait，对 *A. flagrans* 基因组做标准 protein BLAST，得到 14 个推定受体编码基因。根据与已知受体的相似性排除若干不太像 ascaroside 感受器的候选后，实验聚焦于 GprA–F。

序列预测还给 GprC 提供了一个线粒体线索：

- N 端前 30 aa 被预测为信号肽；
- MitoProt 预测第 82 aa 后存在切割位点，线粒体靶向概率为 98.41%；
- 这只是算法预测，真正的双定位证据来自后面的成像和分级实验。

### 4.2 删除、回补和过表达形成一致方向

Fig. 1b Source Data（traps cm⁻²，均为 `n = 3`）：

| 菌株 | 均值 ± s.d. | 与 WT 的 P 值 | 相对 WT |
|---|---:|---:|---:|
| WT | 434.67 ± 28.85 | — | 100% |
| `ΔgprA` | 412.53 ± 36.94 | 0.4594 | 94.9% |
| `ΔgprB` | 339.20 ± 24.89 | 0.0123 | 78.0% |
| `ΔgprC` | 226.08 ± 28.06 | 0.0009 | 52.0% |
| `ΔgprD` | 332.43 ± 31.35 | 0.0142 | 76.5% |
| `ΔgprE` | 445.39 ± 24.92 | 0.6517 | 102.5% |
| `ΔgprF` | 415.68 ± 17.18 | 0.3829 | 95.6% |
| `ΔgprC + gprC–GFP` | 428.21 ± 52.29 | 0.8606 | 98.5% |
| `gprC` 过表达 | 625.97 ± 48.70 | 0.0042 | 144.0% |

这里最重要的校正是：`ΔgprC` 仍产生约 WT 一半的捕陷器，表型是**明显减少**，不是完全丧失。`gprB`、`gprD` 删除也有较小但显著的下降，因此 GprC 是关键组成部分，而不是由这组实验确定的唯一 GPCR。

`gprA/E/F` 在本实验的**活体线虫诱导条件**下与 WT 无显著差异。该结果没有逐一使用纯 ascaroside 测试，不能扩写成“它们不参与 ascaroside 感应”。

Fig. 1c 的 6 h 活体线虫诱导 RT–qPCR 中，`gprC` 平均升至 3.27 倍；其余候选没有同等上调。它说明线虫暴露会诱导 `gprC` 转录，不等于证明具体是 ascaroside 直接诱导。

### 4.3 GasA 和 GasB 走向不同

Fig. 1e Source Data：

| 菌株/处理 | traps cm⁻²，均值 ± s.d. | 与 WT 的 P 值 |
|---|---:|---:|
| WT | 472.96 ± 63.23 | — |
| `ΔgasA` | 9.39 ± 3.28 | 0.0002 |
| `ΔgasA + gasA` | 444.00 ± 53.39 | 0.5771 |
| `ΔgasA + GFP–gasA` | 411.89 ± 33.87 | 0.2143 |
| `ΔgasA + 5 mM 8′-Br-cAMP` | 7.84 ± 4.11 | 0.0002 |

`ΔgasA` 的表型接近完全丧失，野生型和 GFP 融合回补均恢复。8′-Br-cAMP **不能挽救 `ΔgasA`**，Fig. 1e 没有测试 `ΔgprC`。

Fig. 1g 中，`ΔgasB` 从 WT 的 404.96 降至 237.76 traps cm⁻²（P = 0.0094）；`gasB` 回补为 486.40，而 8′-Br-cAMP 处理的 `ΔgasB` 为 420.64，与 WT 无显著差异（P = 0.6979）。因此 cAMP 类似物挽救的是 **`ΔgasB`**。

这组药理结果支持 GasB 与 cAMP 通路相连，也排除了“补充 cAMP 足以替代 GasA”的简单模型。它本身不能证明 GprC–GasA 必定进入某条 MAPK；Fig. 3b 后来进一步显示该轴独立于作者所测的 HogA、MakA、MakB 磷酸化反应。

---

## 5. Fig. 1f：为什么删除一方会使另一方上调

### 5.1 原始效应有多大

Fig. 1f 没有画 fold change，而是画 actin 归一化后的相对表达量：

| 比较 | WT 均值 | 删除株均值 | 倍数 | P 值 |
|---|---:|---:|---:|---:|
| `gasA`：WT vs `ΔgprC` | 0.04900 | 0.06540 | 1.33× | 0.0154 |
| `gprC`：WT vs `ΔgasA` | 0.0005476 | 0.001745 | 3.19× | 0.00443 |

也就是说，双向上调确实存在，但并不对称：失去 GasA 后 `gprC` 的补偿幅度明显更大。

### 5.2 最符合数据的解释

GprC 和 GasA 位于同一功能轴上。删除其中一端后，捕陷器形成、`artA` 调控或呼吸输出下降，细胞可能通过稳态反馈提高另一端的转录，试图补偿信号通量。这类“路径输出不足 → 上调剩余组件”的补偿，是 Fig. 1f 最顺的解释。

但 Fig. 1f 只给一个时间点的稳态转录量，图注也没有单独说明这里是否经过线虫诱导。论文没有做时间序列、启动子 reporter、回补后的表达复位，也没有找到负责反馈的转录因子。因此，这张图支持**互相补偿的转录反馈现象**，还不能确定反馈由哪一个输出、哪一个传感器或哪条支路触发。

---

## 6. Fig. 2：双定位和 GprC–GasA 相互作用

### 6.1 GprC–GFP 的定位依赖表达背景和菌丝位置

用强 `oliC` 启动子表达 GprC–GFP 时，信号主要位于菌丝内部的丝状结构，并与 MitoTracker 重合；质膜信号不可见或不明显。不能把这组过表达图写成“同时清晰显示质膜和线粒体”。

用 `gprC` 原生启动子表达同一融合蛋白时，分布呈空间梯度：

- 菌丝尖端主要呈线粒体样信号；
- 远离尖端的较老区段更偏质膜；
- 捕陷器内两类定位都可见，但没有同样的尖端—后部梯度。

GprC–GFP 能回补 `ΔgprC`，说明这个带标签版本保留了支持捕陷器形成的功能。

### 6.2 split-GFP 和 Y2H 各自说明什么

GprC 接 GFP C 端片段，GasA 接 GFP N 端片段，并由各自原生启动子表达。两者同时存在且加入线虫时，质膜和线粒体样位置出现重组荧光；单构建对照没有荧光。这支持两种蛋白在这些位置近距离接触。

酵母双杂交又显示全长 GprC 或其 111 aa C 端尾部可与 GasA 互作，C 端尾部的生长信号略强。它支持 GprC C 端参与 GasA 结合，但 spot assay 不是定量亲和力测量。

### 6.3 分级实验怎样支持线粒体外膜定位

GprC–GFP 约 90 kDa，在富集线粒体的 P1/P2 和富集质膜的 P3 中均被检测。三个 pellet 中的 GprC–GFP 都可被 proteinase K 完全消化，而线粒体基质对照 CitA(N)–GFP 的已导入短片段受到保护。结果与 GprC 暴露在线粒体外膜外侧相符。

这套分级不是高纯度细胞器蛋白质组，P1/P2/P3 的交叉污染程度也没有用多组独立膜标志全面定量；因此最稳妥的说法是“成像与分级共同支持质膜和线粒体外膜相关定位”。

---

## 7. Fig. 3a 与 Extended Data Fig. 2e：GprC–GasA 控制 `artA` 响应

`artA` 编码合成 arthrosporol 和 6-MSA 所需的聚酮合酶。作者把 `artA` 启动子接到 H2B–mCherry，使转录输出显示为核荧光。

- WT 营养菌丝中核荧光强；加入活体线虫或 ascr#18 后信号消失；
- `ΔgasA` 与 `ΔgprC` 中，该 reporter 对两种刺激均不再作出同样响应。

这条证据尤其重要，因为它把“纯 ascr#18 输入”接到了 GprC/GasA 依赖的细胞转录输出。它比仅用活体线虫的表型更接近 ascaroside 感受，但仍是下游 reporter，不是受体–配体结合测量。

Extended Data Fig. 2e 的群体 RT–qPCR 与 reporter 方向一致：在线虫诱导的 WT 中，`artA–D` 平均降到未诱导 WT 的 0.56–0.69 倍；`ΔgasA` 中诱导前后大体不变。作者把群体差异较弱解释为较老菌丝区段会重新激活该簇，细胞分辨率 reporter 因而更直观。

---

## 8. Fig. 3b：MAPK 结果应怎样读

线虫诱导 3 h 后：

- HogA 和 MakB 在 WT、`ΔgasA`、`ΔgprC` 中都出现磷酸化；
- MakA 在所有诱导和未诱导样本中均为弱信号；
- 作者据此写明 GprC–GasA signalling **independent of the three MAP kinases**。

因此 Fig. 3b 不是“`ΔgasA`/`ΔgprC` 中 HogA、MakB 磷酸化消失”，也不支持把 GprC–GasA 指定为 HogA/MakB 上游。把 Fig. 1e 和 Fig. 3b 合起来，论文实际得到的是：GasA 不能被外源 cAMP 替代，且其作用不依赖所测三种 MAPK 的诱导磷酸化；真正连接 GprC–GasA 与核内转录的中间效应器仍未找到。

---

## 9. Fig. 3c–d：ROS 与呼吸证据

### 9.1 ROS 的 Source Data 与正文有一处冲突

CellROX Orange 的 CTCF（`n = 15` 个区域，来自 3 条菌丝）：

| 菌株 | 未诱导均值 | 线虫诱导均值 | 倍数 | P 值 |
|---|---:|---:|---:|---:|
| WT | 1,385.42 | 6,228.41 | 4.50× | 2.55 × 10⁻¹¹ |
| `ΔgasA` | 2,356.28 | 2,408.05 | 1.02× | 0.917 |
| `ΔgprC` | 1,910.24 | 2,978.20 | 1.56× | 1.88 × 10⁻³ |

正文说缺失 GprC 或 GasA 后荧光增幅都“不显著”，但官方 Source Data 显示 `ΔgprC` 仍有统计学显著的较弱增幅。准确表述应是：WT 增幅最大，`ΔgasA` 没有增幅，`ΔgprC` 增幅被削弱但仍显著。

CellROX 是氧化状态相关荧光读数，作者将其作为呼吸产生 ROS 的指标；单凭该染料不能定位具体 ROS 来源或呼吸链位点。

### 9.2 OCR 给出更直接的呼吸读数

作者用 Seahorse XFe24 测量 OCR：约 10³ 个孢子培养 24 h，加入约 50 条成虫诱导 6 h，洗去游离线虫后测量。每组有 3 个生物学重复。

- WT 诱导曲线在整个约 60 min 测量期明显高于未诱导曲线；
- `ΔgasA` 诱导与未诱导曲线接近；
- `ΔgprC` 没有出现 WT 式增强，诱导曲线还略低于未诱导曲线。

因此 OCR 支持 GprC 和 GasA 对正常的线虫诱导呼吸增强是必需的。实验没有构建“只保留质膜定位”或“只保留线粒体定位”的 GprC，也没有直接激活单独的线粒体定位池；合理结论是它支持作者提出的线粒体调节模型，而不是已经单独证明“线粒体 GprC 直接激活呼吸链”。

---

## 10. Fig. 4：线虫受体嵌合和点突变怎样加强受体模型

### 10.1 嵌合体设计

作者在 *C. elegans* cDNA 中克隆出 SRBC64、SRBC66、DAF37、DAF38。全长线虫受体在 `ΔgprC` 中均不能恢复到 WT 水平。随后构建：

`线虫受体 TM1–4 + GprC TM5–7`

保留 GprC 后三条 TM 的目的是保留真菌胞内信号接口。功能结果为：

| 构建 | traps cm⁻²，均值 | 相对 `ΔgprC` 的 P 值 | 功能判断 |
|---|---:|---:|---|
| `ΔgprC` | 229.87 | reference | — |
| GprC 回补 | 507.84 | 0.00262 | 恢复 |
| Octr-1–GprC | 183.15 | 0.159 | 不恢复 |
| DAF37–GprC | 220.27 | 0.806 | 不恢复 |
| DAF38–GprC | 529.28 | 0.0407 | 恢复 |
| SRBC64–GprC | 622.61 | 0.00769 | 恢复 |
| SRBC66–GprC | 489.28 | 0.00117 | 恢复 |
| 全长 SRBC66 | 227.52 | 0.953 | 不恢复 |

结果说明 SRBC64/66 或 DAF38 的外侧四条 TM 可以和 GprC 的内侧三条 TM 组合成功，支持“外部识别模块与真菌信号模块可拆分”的模型。它没有直接显示嵌合体响应的是哪一种 ascaroside，也没有提供每个构建的蛋白定位和丰度。

### 10.2 点突变的功能结果

| 构建 | traps cm⁻²，均值 | 相对 `ΔgprC` 的 P 值 | 解释 |
|---|---:|---:|---|
| GprC N2.53A | 491.84 | 0.00260 | 保留回补功能；作者的阴性位置对照 |
| GprC N2.57A | 242.03 | 0.649 | 丧失回补功能 |
| GprC R6.45A | 241.49 | 0.650 | 丧失回补功能 |
| GprC S2.41A | 231.04 | 0.965 | 丧失回补功能 |
| SRBC64 N2.60A–GprC | 237.23 | 0.825 | 丧失回补功能 |

N2.53A 保留功能而更靠胞外侧的 N2.57A 丧失功能，与胞外正构口袋模型相符。R6.45A 和 S2.41A 显示 R/S motif 对整体功能重要；其中 S2.41 离 docking 口袋较远，更像构象转换或信号传递所需位置，而不是直接配体接触残基。

Extended Data Fig. 2f 只用 374 bp RT–PCR 片段确认这些构建有转录。突变造成的功能丧失也可能受蛋白稳定性、折叠、膜插入或定位影响，论文没有用蛋白水平和定位控制逐项排除。

---

## 11. Fig. 5：docking 技术栈和计算流程

### 11.1 从受体到 pose 的完整流程

论文使用的技术栈可以还原为：

```text
AFDB / AlphaFold 2.3
  -> 选取或预测 WT、突变体和嵌合体结构
  -> 提取预测 GPCR 的跨膜部分
  -> ADFR suite prepare_receptor 生成受体 PDBQT

Avogadro 1.2.0
  -> 手工构建 ascaroside 三维结构
  -> ORCA 5.0.1，B3LYP/def2-TZVP 几何优化
  -> ADFR suite prepare_ligand
  -> ascarylose 环外单键设为可旋转，7–11 个 DOF
  -> Gasteiger 电荷，生成配体 PDBQT

AutoDock Vina 1.2.3
  -> 40 Å 立方 box
  -> box 中心为处理后受体的质心
  -> exhaustiveness = 200
  -> spacing = 0.1 Å
  -> 使用前五个 pose 做分值和接触分析
```

WT 的 GprC、SRBC64、DAF37 模型来自 AlphaFold Protein Structure Database；Reporting Summary 列 AlphaFold 2.3。突变体和嵌合体由 AF2 web server 建模，参数为每个输出 5 个模型、`max_recycles = 24`、`num_ensemble = 2`。TM 区 pLDDT > 0.85 是模型质量描述，不是文中明确声明的截取阈值。

Methods 明确说处理的是预测结构的 **transmembrane portions**，因此不能再用“长 ICL3 偏移全长受体质心”解释 box 问题。真正缺的是：TM 部分的精确残基范围和最终受体文件没有公开。

### 11.2 计算矩阵实际有多大

Extended Data Table 2 共有 13 个受体/构建体：

- 7 个 WT：GprB、GprC、GprD、SRBC64、SRBC66、DAF37、DAF38；
- 2 个嵌合体：SRBC64–GprC、DAF37–GprC；
- 4 个突变体：SRBC64 N2.60A、GprC N2.53A、GprC N2.57A、GprC R6.45A。

不是 10 个。主分析包含 ascr#1、#2、#3、#5、#18 五种配体，GprB/GprC/GprD/SRBC64/SRBC66/DAF37 还对接了 glucose 和 sucrose；部分构建只计算 #1/#2/#3/#5。

Methods 写“7–11 DOFs for the four ascarosides”，但正文和表中明确有五种 ascaroside，这是内部数量不一致。

### 11.3 最值得保留的 Vina 分值

Extended Data Table 2 报告 best pose 的预测分值（kcal mol⁻¹）：

| 受体 | ascr#1 | ascr#2 | ascr#3 | ascr#5 | ascr#18 | glucose | sucrose |
|---|---:|---:|---:|---:|---:|---:|---:|
| GprB | −6.25 | −6.11 | −7.04 | −6.09 | −7.02 | −5.73 | −5.97 |
| **GprC** | **−7.26** | **−6.90** | **−8.31** | **−6.62** | **−8.29** | −5.63 | −6.85 |
| GprD | −5.08 | −5.69 | −6.30 | −5.00 | −5.85 | −4.86 | −5.64 |
| SRBC64 | −6.99 | −6.61 | −7.61 | −6.50 | −7.51 | −6.00 | −6.57 |
| SRBC66 | −6.36 | −6.34 | −6.18 | −6.05 | −6.94 | −5.36 | −5.77 |
| DAF37 | −6.06 | −5.40 | −6.25 | −5.24 | −6.76 | −4.70 | −6.32 |
| DAF38 | −7.03 | −6.40 | −7.64 | −5.54 | n.d. | n.d. | n.d. |

GprC 在该评分体系中对 ascr#3（−8.31）和 ascr#18（−8.29）的分值最负。R6.45A 对 ascr#3 的分值由 −8.31 变为 −6.69，变化最大；N2.53A 为 −7.91，N2.57A 为 −7.57。

这里有一个重要的功能—打分分离：N2.57A 在捕陷器回补实验中丧失功能，但 ascr#3 Vina 分值仍为 −7.57。由此可见，Vina score 不能直接等同于受体功能，更不能当作实验亲和力。

### 11.4 口袋、残基和 motif

作者把前五个 pose 的 3.5 Å 邻近残基汇总到 Extended Data Table 3。主要模型是：

- 配体从胞外侧进入锥形正构口袋；
- TM1 和 TM4 没有进入作者汇总的配位集合，TM2/3/5/6/7 参与；
- GprC 与 SRBC64 的 ECL2 参与配位，DAF37 的 ECL2 更长且未进入作者统计的 20 个 pose 接触集合；
- GprC 的 N2.57、R motif 和胞外口袋相邻；S2.41 离口袋较远。

文中还存在编号冲突：正文、突变体名和 Extended Data Table 2 使用 `R6.45`，Fig. 5g 与 Extended Data Table 3 的 GprC TM6 却列 `R6.55`。在没有绝对序列位置映射和实际坐标文件的情况下，应保留原文的冲突记录，不能自行把两者合并为一个确定编号。

### 11.5 两个嵌合体的口袋不要写反

正文 p.1759 的顺序是：

- **DAF37–GprC**：不恢复功能，缺少 S motif，模型口袋位于 TM1/2/7；
- **SRBC64–GprC**：恢复功能，保留 S2.41，模型口袋位于 TM3/5/6/7。

这与作者前面对 WT 受体“TM1 不参与”的概括并不完全一致，说明嵌合体模型的口袋几何不能机械套用 WT 汇总。

---

## 12. Docking 的复现性审核

### 12.1 已报告的信息

Hu2024 比许多只写软件名的 docking 论文更完整，报告了：

- AlphaFold 来源或 AF2 web 参数；
- 仅处理 TM 部分；
- 受体和配体准备工具；
- 配体量化化学优化层级；
- 可旋转键规则、自由度范围和 Gasteiger 电荷；
- Vina 版本、box 大小、box 中心原则、exhaustiveness、spacing；
- 分析前五个 pose；
- 以 BW 编号汇总 3.5 Å 邻近残基。

这足以重建一条相似的计算流程。

### 12.2 严格复现仍缺什么

| 类别 | 未报告或未公开内容 | 直接影响 |
|---|---|---|
| 受体输入 | 实际 PDB/PDBQT、AFDB accession 对照、TM 精确截取范围、文件校验值 | 无法确认使用同一坐标与同一处理后质心 |
| AF2 选择 | 五个候选模型中选哪一个、排序依据、seed、MSA/模板和数据库日期 | 突变体/嵌合体结构不能精确重建 |
| 配体输入 | 实际结构文件、立体化学检查、质子化态、ORCA 输入输出与收敛记录 | 不能确认化学身份和优化构象完全一致 |
| PDBQT 细节 | ADFR suite 版本、受体质子化/残基电荷、具体命令与日志 | 会改变 Vina 输入 |
| Vina 运行 | 精确 box 坐标、`num_modes`、`energy_range`、seed、CPU 和完整命令 | 不能重建同一 pose 集合 |
| 输出 | 全部 pose 坐标、每个 pose 分值、运行日志和接触分析文件 | 不能复核图中选择和残基统计 |
| 自定义分析 | 3.5 Å 接触筛选脚本、排除 gly/pro/backbone 的实现、姿势汇总代码 | Extended Data Table 3 不能逐项复算 |
| 稳健性 | 多 AF2 模型、多 seed、不同质子化态、膜环境或 induced-fit/MD 验证 | 不知道口袋与排序对输入的敏感性 |

论文没有提供 GitHub 或自定义代码。Reporting Summary 的 code availability 只列第三方软件。

### 12.3 论文自身的四组不一致

1. Methods 写“四种 ascaroside”，实际表中有 #1/#2/#3/#5/#18 五种；
2. Fig. 5 图注说 25 poses，正文统计 ECL2 时又说 20 poses；合理推测后者按四种配体统计，但文中没有解释；
3. `R6.45` 与 `R6.55` 并存；
4. 正文把 DAF37–GprC 和 SRBC64–GprC 的口袋分别写为 TM1/2/7 与 TM3/5/6/7，旧摘要曾将二者倒置。

### 12.4 最合适的判定

现有信息允许按相同软件族、公开参数和相似输入做**近似重跑**，但不足以获得论文的同一坐标、同一随机输出和同一接触表。docking 在本文中应作为口袋与突变位点的假设生成层，与遗传功能结果联合解释；它不能单独证明 GprC 直接结合某种 ascaroside，也不能把 Vina 分值称作实验“结合亲和力”。

---

## 13. Fig. 6：双功能模型成立到哪一步

Fig. 6 把全文压缩成两个并行输出：

```text
ascaroside / 线虫信号
        |
     GprC–GasA
       /     \
质膜相关轴     线粒体相关轴
   |              |
artA 抑制       OCR / ROS 改变
捕陷器形成      呼吸动员
```

左支路有纯 ascr#18 reporter、遗传表型和互作证据，右支路有双定位、ROS 与 OCR。这个模型很好地解释了为何捕食转变既要改写基因表达，也要在生长尖端动员能量。

目前两条支路仍共享同一组全基因删除，尚未用定位分离突变体把它们拆开。论文讨论部分也明确承认，两种定位是否都为真菌–线虫互作所必需仍待确定。

---

## 14. 最容易误写的八点

1. `ΔgprC` 是捕陷器明显减少，不是完全消失；接近完全丧失的是 `ΔgasA`。
2. 8′-Br-cAMP 挽救 `ΔgasB`，不能挽救 `ΔgasA`；论文没有测试 `ΔgprC`。
3. HogA/MakB 在线虫诱导后也在 `ΔgasA`、`ΔgprC` 中磷酸化，作者据此认为 GprC–GasA 独立于所测三种 MAPK。
4. `gprA/E/F` 的结论限于所测活体线虫条件下无显著表型；其对纯 ascaroside 的响应仍未测试。
5. `oliC` 过表达的 GprC–GFP 主要显示线粒体样丝状结构，质膜信号不可见或不明显。
6. ROS Source Data 显示 `ΔgprC` 仍有较弱但显著的增幅，与正文“不显著”表述冲突。
7. S2.41 对功能重要，但离 docking 口袋远，更像信号/构象位点；功能丧失不等于直接配体接触。
8. 嵌合体口袋为 DAF37–GprC：TM1/2/7；SRBC64–GprC：TM3/5/6/7，不能倒置。

---

## 15. 建议采用的准确表述

> Hu et al. 通过删除、回补、过表达、`artA` reporter、双定位成像、GprC–GasA 相互作用和 OCR 测量，支持 *A. flagrans* 的 GprC–GasA 轴把线虫/ascaroside 响应连接到捕食相关转录重编程和呼吸增强。GprC 点突变、线虫受体–GprC 嵌合体与 AlphaFold/Vina 模型进一步支持胞外正构口袋及 S/R motif 的功能，但本文没有直接结合测量，也没有分离操纵质膜与线粒体定位池；因此 GprC 直接结合具体 ascaroside 及其在线粒体上直接调节呼吸链仍属于由多层证据支持的机制模型。

---

## 16. 最终证据分级

| 命题 | 判定 | 主要依据 |
|---|---|---|
| GprC 参与线虫诱导的捕陷器形成 | 较强支持 | 删除下降、回补恢复、过表达上升 |
| GprC 是唯一相关 GPCR | 不支持 | `ΔgprC` 仍有约半数捕陷器；`gprB/gprD` 也有表型 |
| GprC–GasA 处于同一功能轴 | 较强支持 | 遗传表型、split-GFP、Y2H、共同影响 reporter/OCR |
| GprC–GasA 通过 HogA/MakA/MakB | 不支持 | Fig. 3b 显示三者磷酸化不依赖 GprC/GasA |
| GasB 使用 cAMP 相关通路 | 支持 | `ΔgasB` 被 8′-Br-cAMP 挽救 |
| GprC/GasA 支持正常线虫诱导呼吸增强 | 较强支持 | ROS 趋势与 OCR 曲线 |
| 线粒体定位的 GprC 单独直接激活呼吸链 | 未闭合 | 未做定位分离操纵或呼吸链直接靶点实验 |
| GprC 直接结合 ascaroside | 中等模型支持，未直接证明 | ascr#18 reporter、遗传/嵌合/突变 + docking；无结合测量 |
| N2.57、R motif、S motif 对受体功能重要 | 支持 | 回补表型；但蛋白丰度/定位控制不足 |
| S2.41 是直接配体接触残基 | 不支持 | 模型中远离口袋 |
| 论文 docking 可严格复现 | 不支持 | 缺实际输入输出、精确坐标、seed 与选择规则 |

## 17. 参考文献

1. Hu, X. et al. *Nature Microbiology* 9, 1752–1763 (2024). <https://doi.org/10.1038/s41564-024-01731-9>
2. Eberhardt, J., Santos-Martins, D., Tillack, A. F. & Forli, S. *Journal of Chemical Information and Modeling* 61, 3891–3898 (2021). <https://doi.org/10.1021/acs.jcim.1c00203>
3. Park, J. Y., Joo, H. J., Park, S. & Paik, Y. K. *International Journal of Molecular Sciences* 20, 3898 (2019). <https://doi.org/10.3390/ijms20163898>
