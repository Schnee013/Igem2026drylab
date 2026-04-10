# Srinivasan et al. 2012 — 文献总结

> **完整标题**: A Modular Library of Small Molecule Signals Regulates Social Behaviors in *Caenorhabditis elegans*
> **期刊**: *PLoS Biology*, Volume 10, Issue 1, e1001237
> **DOI**: 10.1371/journal.pbio.1001237
> **作者**: Jagan Srinivasan, Hendrik M. von Reuss, Neelanjan Bose, Alon Zaslaveri, Parag Mahanti, Margaret C. Ho, Oran G. O'Doherty, Arthur S. Edison, Paul W. Sternberg, Frank C. Schroeder
> **机构**: Thomas Hughes Medical Institute / California Institute of Technology（Pasadena）; Boyce Thompson Institute / Cornell University（Ithaca）; University of Florida（Gainesville）

---

## 核心发现（5–10 bullets，含数据）

- **首次鉴定 indole ascarosides（icas）**：利用 DANS（Differential Analysis via 2D-NMR Spectroscopy）比较野生型与 *daf-22* 突变体代谢组，发现 5 种依赖 *daf-22* 的新型 indole 衍生信号分子（icas#1、icas#3、icas#7、icas#9、icas#10），均在 *daf-22* 突变体中消失。

- **icas 吸引雌雄同体与雄性**：icas#1、icas#3、icas#9 在 spot attraction assay 中对雌雄同体和 *him-5* 雄性均表现出显著吸引力（*p* < 0.001），与非 indole ascarosides（ascr）仅吸引雄性的特征截然不同。

- **icas#3 感知需要 ASK 感觉神经元与下游 AIA 中间神经元**：ablation 实验证明，ASK 神经元缺失后对 icas#3 的吸引力几乎完全消失；钙成像（GCaMP）显示 icas#3 在 AIA interneuron 中诱导显著钙瞬变（平均荧光变化约 +45%，*p* < 0.01）。

- **icas#3 促进聚集行为（aggregation）**：低虫密度（20 只/皿）下，exogenous icas#3 在 femtomolar 至 picomolar 浓度（10 fM–1 pM）显著增加野生型 N2 聚集百分比，并延长平均停留时间（mean stopped duration 由 ~0.6 s 升至 ~1.6 s）。

- **ascr#3 与 icas#3 竞争信号**：ascr#3 在纳摩尔至微摩尔浓度下产生排斥，而 icas#3 在飞摩尔至皮摩尔浓度下引起吸引；两者混合时（120 fmol ascr#3 + 10 fmol icas#3），低浓度下 icas#3 主导吸引，高浓度下 ascr#3 的排斥占主导，形成浓度依赖的双向调控。

- **NPR-1 区分 icas 与 ascr 信号**：非 indole ascarosides（ascr#2, 3, 5）的吸引需要 NPR-1 突变体（高社群行为株 CB4856、RC301），而 icas#3 对野生型（N2）即可吸引；*npr-1(ad609)* 突变体对 icas#3 反应与 N2 相似，表明 icas 信号不经由 NPR-1 通路。

- **RMG interneuron 非 icas#3 传导必需**：RMG 缺失（*ncs-1::tgfb* 转基因抑制）不影响对 icas#3 的 spot attraction，与 ASK→AIA 通路区别明显；而非 indole ascarosides 的社群行为依赖 ASK + RMG 共同参与。

- **模块化化学语言假说**：作者提出 *C. elegans* ascaroside 信号系统由来自色氨酸（indole 头基）、脂肪酸（侧链）、氨基苯甲酸（PABA，末端修饰）和碳水化合物（ascarylose 核心）的构建模块组合而成，形成一个多维度的化学通讯语言（图 6B–C）。

- **icas 在极低浓度即有效**：单只成体线虫体积中 icas#3 分子数估算仅约 20 个，表明该信号系统在极低丰度下即可发挥生理作用。

---

## 实验方法（表格）

| 方法 | 用途 | 关键参数 |
|------|------|----------|
| DANS（2D-NMR 差异分析） | 鉴定 *daf-22* 依赖代谢物 | Varian INOVA 600 MHz；野生型 vs *daf-22(m130)* |
| HPLC-MS（质谱） | 定量 icas/ascr 相对丰度；确认分子量 | Agilent 1100 系列；电喷雾负离子模式 |
| 化学全合成 | 提供 icas#1, 3, 7, 9 标准品 | 详见 Text S1；NMR 验证结构 |
| Spot Attraction Assay | 测量化合物对线虫的吸引/排斥 | 35 mm NGM 琼脂板，4 分区，计分 zone A；15 min + 30 min 计分 |
| Quadrant Chemotaxis Assay | 测量趋化指数（Chemotaxis Index） | 10 cm 四分区 Petri 皿；30 min 后计分 |
| 神经元 ablation（laser/基因） | 确定 ASK、ASI、AIM、RMG、AIA 的功能 | 哺乳动物 caspase 转基因表达；细胞特异性启动子 |
| GCaMP 钙成像（microfluidic） | 测量 ASK、AIA 神经元钙响应 | "Olfactory chip" 微流控；GCaMP 荧光变化 ΔF/F₀ |
| 聚集行为定量 | 分析 icas#3 对群体行为的影响 | 低密度 20 只/皿；高密度 ~120 只/皿；接触 ≥3 只计为聚集 |
| 运动参数自动追踪 | 分析 icas#3 对停留时长/频率的影响 | 自动化虫追踪系统；逐帧分析 |

---

## 关键数据（分小节）

### icas 鉴定与结构

- DANS 方法在野生型 2D-NMR 谱中识别出至少 5 个 *daf-22* 依赖的新信号（图 1B–D）。
- icas#3、icas#9 是分泌量最高的两种 indole ascaroside（图 1G；相对量约为 ascr#3 的 10%）。
- icas 结构特征：indole-3-carbonyl 头基通过酰胺键连接至 ascarylose，再连接不同长度的 lipid 侧链（图 1E）。

### 吸引力行为定量

- icas#1、icas#3、icas#9 在 1 pmol spot assay 中对 N2 雌雄同体和 *him-5* 雄性均显著高于溶剂对照（*p* < 0.001，图 2C）。
- icas#3 趋化指数剂量依赖：1 pM 时 Chemotaxis Index ≈ 0.4（N2），10 pM 时 ≈ 0.45（图 2E）。
- *npr-1* 突变体同样被 icas#3 吸引（spot assay），但不被非 indole ascr#2,3,5 混合物吸引（图 3A–B）。

### 聚集行为

- 低密度（20 只/皿）下，10 fM icas#3 即显著提升 N2 聚集率（*p* < 0.05）；1 pM 时效果最强（图 4A）。
- *daf-22* 突变体（不产 icas）在外源 1 pM 或 10 pM icas#3 下聚集率显著上升，接近 N2 水平（图 4C）。
- icas#3（1 pM）显著延长平均停留时间（~1.6 s vs 对照 ~0.6 s，*p* < 0.05–0.01，图 4D）。

### 神经回路

- ASK 神经元 ablation 导致 icas#3 聚集反应完全消失（图 5C）；ASI ablation 无显著影响。
- ASK ablation + ASI ablation 联合不比单独 ASK ablation 更强，排除 ASI 独立贡献。
- AIA interneuron 钙成像：icas#3（1 µM）引起 AIA 平均 ΔF/F₀ 约 +45%（图 5D–E，*p* < 0.01）。
- AIA 缺失（MEC-4 DEG/ENaC 转基因）导致对 icas#3 完全无聚集反应（图 5B）。

### 竞争信号

- 120 fmol ascr#3 + 10 fmol icas#3 混合时，worms 被吸引至含 icas#3 的区域（图 6A，Condition 1）。
- 12 pmol ascr#3 + 1 pmol icas#3 混合时，worms 被驱离至外围（图 6A，Condition 2），ascr#3 高浓度排斥占主导。

---

## 与项目的关系

本文直接为 iGEM 2026 NTF 研究提供以下背景：

1. **核心配体结构基础**：ascr#3、ascr#7 均在本文中作为已知非 indole ascaroside 参照物使用（图 1A、6B），确认了其化学结构（ascarylose 糖核 + 脂肪酸侧链）。ascr#18 虽未在本文中出现，但本文建立的模块化骨架（ascarylose + lipid 侧链）适用于全部 ascr 家族成员。

2. **配体-受体匹配的信号特异性**：本文显示 icas#3 通过 ASK→AIA 通路感知，非 indole ascarosides 通过涉及 NPR-1 的不同通路感知，提示不同 ascaroside 配体的受体/通路是分离的——这对 NTF（嵌合 G 蛋白）设计中理解配体特异性受体激活有直接意义。

3. **picomolar/femtomolar 活性浓度**：icas#3 在 10 fM 至 1 pM 下即可促进聚集，说明 ascaroside 受体具有极高亲和力，这为分子对接中合理的结合能阈值提供了生物学参照。

4. **ascr#3 的双重功能**：本文阐明 ascr#3 在低浓度（fmol）促进雄性吸引、高浓度（nmol-µmol）产生排斥（图 6B），提示配体浓度与受体响应的非线性关系，在解读对接打分时需考虑浓度效应。

5. **模块化库概念**：文章构建的 ascaroside 化学多样性框架（head group × lipid chain × terminus 组合）说明该类配体具有高度结构可变性，这解释了为何不同 ascr 亚型在行为上功能各异——对 NTF 感知机制研究有参考价值。

---

## 关键引用（7条）

1. **Pungaliya et al. 2009** (*PNAS*) — 建立 DANS 方法，首次用于 *C. elegans* 代谢组比较分析（本文方法基础）。

2. **Jeong et al. 2005** (*Nature*) — 鉴定 ascr#5（*daf*-inducing pheromone 组分之一），建立 ascaroside 作为 dauer 信号分子的框架。

3. **Srinivasan et al. 2008** (*Nature*) — 鉴定 ascr#2、ascr#3 混合物为雄性吸引信号，首次报道 ascr 在社会行为中的作用。

4. **de Bono & Bargmann 1998** (*Cell*) — 鉴定 NPR-1 作为神经肽 Y 受体同源物，调控 *C. elegans* 社群/单独行为切换（本文 icas vs ascr 通路对比基础）。

5. **Macosko et al. 2009** (*Nature*) — 鉴定 RMG interneuron 作为调控聚集与食物响应的中枢（本文用于比较 icas 与 ascr 神经回路差异）。

6. **Kim et al. 2009** (*Science*) — 报道两种趋化受体介导 dauer pheromone 的平行发育效应，说明 ascaroside 感知的多受体机制。

7. **Butcher et al. 2009** (*Nat Chem Biol*) — 鉴定含 indole 的 dauer 信号分子组分（异常活性特征），为 icas 的发现提供化学背景。
