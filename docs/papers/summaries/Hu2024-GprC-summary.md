---
paper_id: Hu2024
document_role: corrected concise summary
source: Hu et al. 2024 version of record and the linked detailed evidence audit
as_of: 2026-08-12
allowed_use: quick orientation; use the detailed evidence audit for exact values, source locations, internal inconsistencies, and reproducibility analysis
update_trigger: correction to the version of record or update of the detailed evidence audit
---

# Hu et al. (2024) — GprC–GasA 校正版摘要

> **按需查看详细证据**：[Hu2024-GprC-detailed-evidence.md](../Hu2024-GprC-detailed-evidence.md)
>
> 详细稿逐图梳理正文、Methods、Extended Data、官方 Source Data、Supplementary Tables、Reporting Summary 和原始 blot，另列 Fig. 1f 的解释、docking 全流程、内部不一致及复现缺口。本页只保留主线结论和最常用数据。

**论文**：Hu, X. et al. *GprC of the nematode-trapping fungus Arthrobotrys flagrans activates mitochondria and reprograms fungal cells for nematode hunting*. *Nature Microbiology* 9, 1752–1763 (2024).

**DOI**：<https://doi.org/10.1038/s41564-024-01731-9>

**研究菌株**：*Arthrobotrys flagrans* CBS 349.94

---

## 一句话结论

Hu et al. 通过遗传表型、`artA` reporter、亚细胞定位、蛋白互作和呼吸测量，支持 GprC–GasA 把线虫/ascaroside 响应连接到捕食相关的基因重编程与呼吸增强；点突变、线虫受体嵌合体和 AlphaFold/Vina docking 又提出了胞外正构口袋及 S/R motif 模型。直接配体结合、线粒体定位池的独立因果作用和受体到核内输出之间的具体效应器仍未闭合。

---

## 1. GprC 是捕陷器形成的重要上游组成部分

作者先用真菌 GPCR 做 protein BLAST，在 *A. flagrans* 基因组中找到 14 个推定受体，再聚焦 GprA–F。活体线虫诱导 6 h 后，`gprC` 转录平均升至 3.27 倍；六个删除株中，`ΔgprC` 的捕陷器下降最明显。

Fig. 1b Source Data（traps cm⁻²，`n = 3`）：

| 菌株 | 均值 ± s.d. | 与 WT 的 P 值 |
|---|---:|---:|
| WT | 434.67 ± 28.85 | — |
| `ΔgprB` | 339.20 ± 24.89 | 0.0123 |
| `ΔgprC` | 226.08 ± 28.06 | 0.0009 |
| `ΔgprD` | 332.43 ± 31.35 | 0.0142 |
| `ΔgprC + gprC–GFP` | 428.21 ± 52.29 | 0.8606 |
| `gprC` 过表达 | 625.97 ± 48.70 | 0.0042 |

`ΔgprC` 仍保留约 WT 一半的捕陷器，表型是明显减少，不是完全丧失。删除—回补—过表达的方向一致，使 GprC 的遗传证据较完整。`gprB` 和 `gprD` 也有较小表型，提示线虫响应不只依赖一个 GPCR。

`gprA`、`gprE`、`gprF` 只是在这组活体线虫诱导实验中与 WT 无显著差异；论文没有逐一用纯 ascaroside 检验它们。

---

## 2. GasA 是 GprC 主线中的关键 Gα，GasB 与 cAMP 相连

*A. flagrans* 编码 GasA、GasB、GasC 三个 Gα。`ΔgasA` 的捕陷器几乎完全消失，野生型 `gasA` 或 GFP–GasA 都能恢复表型。

| 菌株/处理 | traps cm⁻²，均值 ± s.d. | 与 WT 的 P 值 |
|---|---:|---:|
| WT | 472.96 ± 63.23 | — |
| `ΔgasA` | 9.39 ± 3.28 | 0.0002 |
| `ΔgasA + gasA` | 444.00 ± 53.39 | 0.5771 |
| `ΔgasA + GFP–gasA` | 411.89 ± 33.87 | 0.2143 |
| `ΔgasA + 8′-Br-cAMP` | 7.84 ± 4.11 | 0.0002 |

8′-Br-cAMP **不能挽救 `ΔgasA`**。被它挽救的是 `ΔgasB`：`ΔgasB` 为 237.76 traps cm⁻²，加入 8′-Br-cAMP 后升至 420.64，与 WT 的 404.96 无显著差异。论文没有测试 8′-Br-cAMP 能否挽救 `ΔgprC`。

所以这组结果支持 GasB 使用 cAMP 相关通路，也说明补充 cAMP 不能替代 GasA。GprC–GasA 后续接到哪一个具体信号模块，论文仍未找到。

---

## 3. Fig. 1f 的双向上调更像稳态补偿

| 比较 | WT 均值 | 删除株均值 | 变化 | P 值 |
|---|---:|---:|---:|---:|
| `gasA`：WT vs `ΔgprC` | 0.04900 | 0.06540 | 1.33× | 0.0154 |
| `gprC`：WT vs `ΔgasA` | 0.0005476 | 0.001745 | 3.19× | 0.00443 |

GprC 和 GasA 处于同一功能轴。删除一端后，路径输出下降，细胞上调另一端来补偿信号通量，是最符合这组数据的解释。两边补偿并不对称，`ΔgasA` 中 `gprC` 的增幅更大。

Fig. 1f 只有一个时间点，图注也没有单独说明诱导条件。论文没有做启动子 reporter、反馈时间序列或回补后的表达复位，因此它显示的是双向补偿现象，具体反馈因子和触发输出尚不清楚。

---

## 4. GprC 与 GasA 在质膜和线粒体相关位置相遇

GprC–GFP 的定位要区分两种表达方式：

- 强 `oliC` 启动子过表达时，主要看到与 MitoTracker 重合的胞内丝状结构，质膜信号不可见或不明显；
- 原生 `gprC` 启动子下，菌丝尖端偏线粒体定位，远离尖端的区段偏质膜定位；
- 捕陷器中两类定位都可见，但没有明显的尖端—后部梯度。

膜分级在富集线粒体的 P1/P2 和富集质膜的 P3 中都检测到约 90 kDa 的 GprC–GFP。Proteinase K 可消化三个 pellet 中的 GprC–GFP，而已导入线粒体基质的 CitA(N)–GFP 短片段受到保护；这一结果与 GprC 位于线粒体外膜并暴露于外侧相符。

线虫存在时，GprC–GFPC 与 GFPN–GasA 的 split-GFP 信号出现在质膜和线粒体样位置；单构建对照没有荧光。酵母双杂交又显示 GasA 可与全长 GprC 或其 111 aa C 端尾部互作。两组实验共同支持 GprC 与 GasA 在这些位置近距离接触，C 端尾部参与结合。

---

## 5. `artA` reporter 把 ascr#18 接到了 GprC–GasA 输出

`artA` 编码合成 arthrosporol 和 6-MSA 所需的聚酮合酶。作者用 `artA` promoter–H2B–mCherry 把其表达显示为核荧光：

- WT 营养菌丝中核荧光强；加入活体线虫或 ascr#18 后信号消失；
- `ΔgasA` 和 `ΔgprC` 中，reporter 对线虫或 ascr#18 都不再作出同样响应。

这说明 GprC 和 GasA 是 ascr#18 触发 `artA` 抑制所需的组成部分。Extended Data Fig. 2e 的群体 RT–qPCR 方向一致：WT 在线虫诱导后 `artA–D` 降至约 0.56–0.69 倍，而 `ΔgasA` 基本不响应。

这条纯 ascr#18 下游读数与遗传表型、嵌合体和 docking 一起支撑受体模型；它本身测量的是转录响应，不是配体结合。

---

## 6. MAPK 结果与旧摘要相反

线虫诱导 3 h 后，HogA 和 MakB 在 WT、`ΔgasA`、`ΔgprC` 中都发生磷酸化；MakA 在所有样本中都只有弱信号。作者因此判断 GprC–GasA 信号独立于所测的 HogA、MakA、MakB。

Fig. 3b 不能解读为“`ΔgasA`/`ΔgprC` 中 HogA 和 MakB 磷酸化消失”，也不能把 GprC–GasA 指定为这三条 MAPK 的上游。结合 8′-Br-cAMP 实验，现有结果只把 cAMP 替代和三种 MAPK 磷酸化排除在简单解释之外，真正的中间信号模块仍待寻找。

---

## 7. ROS 与 OCR 支持正常呼吸增强依赖 GprC–GasA

Fig. 3c 的 CellROX Source Data：

| 菌株 | 未诱导均值 | 线虫诱导均值 | P 值 |
|---|---:|---:|---:|
| WT | 1,385.42 | 6,228.41 | 2.55 × 10⁻¹¹ |
| `ΔgasA` | 2,356.28 | 2,408.05 | 0.917 |
| `ΔgprC` | 1,910.24 | 2,978.20 | 1.88 × 10⁻³ |

WT 的 ROS 相关荧光增幅最大；`ΔgasA` 没有增幅；`ΔgprC` 增幅较弱但仍显著。这里官方 Source Data 与正文“两个缺失株都不显著”的说法存在冲突，应以表中原始数值描述。

Seahorse XFe24 的 OCR 曲线更直接：线虫诱导使 WT 的耗氧率明显上升，`ΔgasA` 和 `ΔgprC` 都没有出现 WT 式增强。这支持 GprC 和 GasA 对正常的线虫诱导呼吸增强是必需的。

论文使用的是全基因删除，没有分别构建质膜专一或线粒体专一的 GprC。因而最合适的机制图景是：双定位和 OCR 共同支持 GprC–GasA 参与线粒体调节；线粒体定位池如何连接呼吸链仍待定位分离实验。

---

## 8. 嵌合受体把外部识别与真菌信号接口拆开

作者构建了：

`C. elegans 受体 TM1–4 + A. flagrans GprC TM5–7`

| 构建 | traps cm⁻²，均值 | 相对 `ΔgprC` 的 P 值 | 结果 |
|---|---:|---:|---|
| `ΔgprC` | 229.87 | reference | — |
| GprC 回补 | 507.84 | 0.00262 | 恢复 |
| Octr-1–GprC | 183.15 | 0.159 | 不恢复 |
| DAF37–GprC | 220.27 | 0.806 | 不恢复 |
| DAF38–GprC | 529.28 | 0.0407 | 恢复 |
| SRBC64–GprC | 622.61 | 0.00769 | 恢复 |
| SRBC66–GprC | 489.28 | 0.00117 | 恢复 |
| 全长 SRBC66 | 227.52 | 0.953 | 不恢复 |

SRBC64/66 或 DAF38 的前四条 TM 与 GprC 后三条 TM 能组成有功能的嵌合体，而全长线虫受体和阴性对照 Octr-1 不能。这支持外部识别模块与真菌胞内信号接口可以拆分和重组。

这些构建只用 RT–PCR 确认转录；论文没有逐个确认蛋白丰度、膜定位和折叠，也没有分别测试每种 ascaroside 的响应谱。

---

## 9. 点突变支持胞外口袋和 S/R motif 的功能

| GprC/SRBC64 构建 | traps cm⁻²，均值 | 相对 `ΔgprC` 的 P 值 | 功能 |
|---|---:|---:|---|
| GprC N2.53A | 491.84 | 0.00260 | 保留回补功能 |
| GprC N2.57A | 242.03 | 0.649 | 丧失回补功能 |
| GprC R6.45A | 241.49 | 0.650 | 丧失回补功能 |
| GprC S2.41A | 231.04 | 0.965 | 丧失回补功能 |
| SRBC64 N2.60A–GprC | 237.23 | 0.825 | 丧失回补功能 |

更靠胞内侧的 N2.53A 保留功能，而更靠胞外侧的 N2.57A 丧失功能，与胞外正构口袋模型一致。R6.45A 和 S2.41A 表明 R/S motif 对整体受体功能重要。

S2.41 在模型中离结合口袋较远，更像构象转换或信号传递位点。上述功能丧失也尚未用蛋白丰度和定位控制排除折叠或膜插入问题，因此这些实验确定的是“功能必需性”，不是逐个残基的直接配体接触。

---

## 10. Docking 技术栈与主要结果

### 技术流程

```text
AFDB / AlphaFold 2.3
  -> 提取预测 GPCR 的跨膜部分
  -> ADFR prepare_receptor

Avogadro 1.2.0 构建配体
  -> ORCA 5.0.1，B3LYP/def2-TZVP 几何优化
  -> ADFR prepare_ligand
  -> 环外单键可旋转，7–11 DOF，Gasteiger 电荷

AutoDock Vina 1.2.3
  -> 40 Å box，中心为受体质心
  -> exhaustiveness = 200，spacing = 0.1 Å
  -> 分析前五个 pose
```

突变体和嵌合体用 AF2 web server 建模：每个输出 5 个模型，`max_recycles = 24`，`num_ensemble = 2`。Methods 明确处理的是跨膜部分，不是带长环区的完整受体。

Extended Data Table 2 实际包含 **13 个受体/构建体**：7 个 WT、2 个嵌合体、4 个突变体。主分析使用 ascr#1、#2、#3、#5、#18 五种配体，部分 WT 还加入 glucose 和 sucrose 对照。

GprC 的 best-pose Vina 分值（kcal mol⁻¹）：

| ascr#1 | ascr#2 | ascr#3 | ascr#5 | ascr#18 | glucose | sucrose |
|---:|---:|---:|---:|---:|---:|---:|
| −7.26 | −6.90 | **−8.31** | −6.62 | **−8.29** | −5.63 | −6.85 |

在这一评分体系中，GprC 对 ascr#3 和 ascr#18 的分值最负。R6.45A 的 ascr#3 分值由 −8.31 变为 −6.69；N2.57A 虽然丧失回补功能，分值仍为 −7.57，清楚说明 Vina score 与受体功能不能直接画等号。

### 两个嵌合体的口袋

- **DAF37–GprC**：不恢复功能、缺少 S motif，模型口袋位于 TM1/2/7；
- **SRBC64–GprC**：恢复功能、保留 S2.41，模型口袋位于 TM3/5/6/7。

旧摘要把两者写反，现已修正。

### 原文内部不一致

- Methods 写“四种 ascaroside”，表中实际有五种；
- Fig. 5 图注写 25 poses，残基汇总段又写 20 poses；
- 正文、突变名和 Table 2 使用 `R6.45`，Fig. 5g 和 Table 3 使用 `R6.55`。

### 复现程度

论文给出的软件、主要参数和配体准备步骤足以近似重跑，但没有公开实际 PDB/PDBQT、AF2 五模型选择规则、TM 精确截取范围、box 坐标、seed、`num_modes`、`energy_range`、完整 poses、运行日志或自定义接触分析代码。现有 docking 的证据用途是提出候选口袋和突变位点；直接结合与实验亲和力仍需独立测量。

---

## 11. 这篇论文对本项目最有价值的内容

1. **受体候选证据链**：删除、回补、过表达、纯 ascr#18 reporter 和下游输出可以组合成比单一 docking 更扎实的受体论证。
2. **Gα 接口**：GprC–GasA 的 C 端互作与嵌合体策略说明，外部识别模块和胞内 G 蛋白接口应分别验证。
3. **嵌合设计**：`线虫受体 TM1–4 + 真菌 GprC TM5–7` 提供了可实验验证的模块化先例，但成功与否取决于整体折叠、定位和信号兼容性。
4. **结构位点筛选**：N2.57、R motif 和 S motif 可作为功能筛选思路；其中 S motif 更接近信号位点，不宜直接当作口袋接触残基。
5. **docking 参考参数**：Vina 1.2.3、40 Å box、exhaustiveness 200、spacing 0.1 Å 是论文级近似重跑的明确起点；正式比较仍需固定输入身份、frame、seed 和 pose 选择规则。
6. **通路建模**：GprC–GasA 对 `artA` 与 OCR 的影响明确，但 cAMP 和所测三种 MAPK 都不能解释这条主轴，ODE 中应把中间效应器保留为待识别节点。

---

## 12. 证据结论表

| 命题 | 判定 |
|---|---|
| GprC 参与线虫诱导的捕陷器形成 | 较强支持 |
| GprC 是唯一相关 GPCR | 不支持 |
| GprC–GasA 处于同一功能轴 | 较强支持 |
| GprC–GasA 通过 HogA/MakA/MakB | 不支持 |
| GasB 使用 cAMP 相关通路 | 支持 |
| GprC/GasA 对正常的线虫诱导呼吸增强必需 | 较强支持 |
| 线粒体定位的 GprC 单独直接激活呼吸链 | 尚未分离验证 |
| GprC 直接结合 ascaroside | 多层模型支持，缺直接结合测量 |
| N2.57、R motif、S motif 对受体功能重要 | 支持 |
| S2.41 是直接配体接触残基 | 不支持 |
| 论文 docking 可严格复现 | 不支持 |

---

## 版本记录

| 日期 | 版本 | 说明 |
|---|---|---|
| 2026-04-03 | v1.0 | 初始总结 |
| 2026-04-10 | v2.1 | 补充方法和 Extended Data 表格 |
| 2026-08-12 | v3.0 | 基于版本记录、Source Data、补充材料和原始 blot 全面校正；新增详细证据回指，修正 cAMP、MAPK、ROS、嵌合口袋及 docking 构建数量等错误 |
