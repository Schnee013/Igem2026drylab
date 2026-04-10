# Huang et al. 2023 — 文献总结

> **完整标题**: Ammonia and Nematode Ascaroside Are Synergistic in Trap Formation in *Arthrobotrys oligospora*
> **期刊**: *Pathogens* 2023, 12, 1114
> **DOI**: https://doi.org/10.3390/pathogens12091114
> **作者**: Jinrong Huang†, Xi Zheng†, Mengqing Tian, Keqin Zhang*
> **机构**: State Key Laboratory for Conservation and Utilization of Bio-Resources in Yunnan, Yunnan University, Kunming 650091, China；Key Laboratory for Potato Biology of Yunnan Province / CAAS-YNNU-YINMORE Joint Academy of Potato Science, Yunnan Normal University

---

## 核心发现（5-10 bullets，含数据）

- **氨与 Ascr#18 协同促进捕陷器形成**：单独施用 Ascr#18（10 nM）或氨（Am，25% 氨稀释 10³ 倍）均可诱导 *A. oligospora* 产生捕陷器；二者混合后捕陷器数量显著高于任一单一处理（Fig. 1A,B；p < 0.001），协同效应最强。
- **其他含氮物同样协同**：NH₄Cl（37.4 mM）、尿素（33.3 mM）、谷氨酰胺（Glu，3.4 mM）分别与 Ascr#18 合用均显著增加捕陷器数（Fig. 1C；p < 0.001），表明协同效应是含氮信号的普遍特征，而非氨特有。
- **Amt43 是 *A. oligospora* 的主要氨转运蛋白**：*A. oligospora* 基因组含三个氨通透酶基因（Amt06、Amt43、Amt80）；Amt43（AOL_s00043g163p）与酵母 Mep2 同源性最高，为最保守的氨转运/感受蛋白（Fig. 2A,B）；结构建模显示其含 11 个跨膜螺旋（Fig. 2C）。
- **Amt43 缺失部分阻断氨诱导的捕陷器形成**：ΔAoAmt43 突变体（三株独立系）在 Am、NH₄Cl、尿素、Glu 单独诱导下捕陷器数均低于 WT（72 h；Fig. 4C）；但 Ascr#18 单独诱导下 ΔAoAmt43 与 WT 表现相当，说明氨通道不参与 Ascr#18 本身的摄取。
- **Ascr#18 的添加可部分补偿 Amt43 缺失**：ΔAoAmt43 突变体在 Ascr#18 + Am 混合处理下，捕陷器数量高于单独加氨的突变体（Fig. 4D），表明 Ascr#18 信号路径独立于 Amt43。
- **氨诱导 Amt43 内吞，Ascr#18 可缓解该内吞**：Amt43::GFP 标记株在 Am（13.3 mM）处理后 5 min 内，GFP 信号从质膜快速转位至细胞质（内吞/液泡化）；单独 Ascr#18 不改变 Amt43 定位；Am + Ascr#18 混合处理削弱了 Amt43 的内吞，保持了相对完整的胞内状态（Fig. 3C）。
- **FM4-64 内吞标记实验**：Am 在 1 min 内即产生明显内吞；Ascr#18 处理也引起轻度内吞；Am + Ascr#18 混合处理促进内吞但同时维持相对完整的胞内结构（Fig. 3D）。
- **ΔAoAmt43 生长/产孢减弱**：突变体在 PDA/CMY 培养基生长直径和孢子数均低于 WT（Fig. 4A,B），说明 Amt43 对正常生长也有贡献；过表达株（ΔAoAmt43::Amt43）可回补上述表型（Fig. 4C）。

---

## 实验方法（表格）

| 方法 | 关键参数 |
|------|----------|
| 菌株培养 | *A. oligospora* ATCC24927；28 °C PDA；WA 培养基用于捕陷器诱导实验 |
| 基因敲除 | 同源重组（HPH 盒）；Southern blot 验证；潮霉素 B 200 µg/µL 筛选 |
| GFP 标记 / 过表达 | 融合 GFP 至 Amt43 启动子-ORF-终止子；原生质体转化 |
| 捕陷器形成检测 | 3×10³ 孢子/板（WA，6 cm）；密封 36 h 预培养后加诱导物（1 mL）；计数时间梯度 24/48/72 h；3 次重复 |
| 诱导物浓度 | Am：25% 氨稀释 10³ 倍；Ascr#18：10 nM；NH₄Cl：37.4 mM；尿素：33.3 mM；Glu：3.4 mM |
| 内吞分析 | FM4-64（5 µg/mL，1 min 或 5 min 染色）；荧光显微镜观察 |
| 系统发育分析 | MEGA 7；包括 *A. oligospora*、*D. stenobrocha*、*A. niger*、*A. nidulans*、*S. cerevisiae* |
| 统计 | GraphPad Prism 9.5.1；t-test；SD；p < 0.05 显著 |

---

## 关键数据（分小节）

### 捕陷器数量（72 h，traps/cm²，约值）

| 处理 | 数量（约） |
|------|-----------|
| Control | ~20 |
| Ascr#18 单独 | ~50 |
| Am 单独 | ~50 |
| Ascr#18 + Am | ~140 |
| Ascr#18 + NH₄Cl | ~65 |
| Ascr#18 + Urea | ~110 |
| Ascr#18 + Glu | ~85 |

（Fig. 1B,C，读数为目估近似值）

### Amt43 与 Mep2 同源性

- Amt43 在系统发育树上与 *S. cerevisiae* Mep2（最重要氨转运受体）聚为一支（bootstrap 100%）；Amt06 和 Amt80 分属不同分支（Fig. 2B）。

### ΔAoAmt43 捕陷器缺陷

- Am 单独处理：WT ~20 traps/cm²，ΔAoAmt43 ~5 traps/cm²（72 h，Fig. 4C）
- Ascr#18 单独处理：WT ≈ ΔAoAmt43（无显著差异）
- Ascr#18 + Am：ΔAoAmt43 捕陷器数介于 Am 单独和 WT 混合之间（Fig. 4D）

---

## 与项目的关系

本文研究物种 *Arthrobotrys oligospora* 与项目核心受体 Gpr2/Gpr3 所在物种相同，提供了重要的信号背景：

1. **Ascr#18 信号独立于 Amt43 氨通道**：文章证明 ΔAoAmt43 突变体对 Ascr#18 单独诱导的捕陷器形成无影响，说明 ascaroside 感知通路在 *A. oligospora* 中不依赖氨转运蛋白；这支持 Gpr2/Gpr3 等 GPCR 作为 Ascr#18 专属受体的假设。

2. **氨与 Ascr#18 协同**：自然土壤环境中氨和 ascaroside 同时存在，两者协同产生更多捕陷器。这意味着 NTF 系统（包括 GprC/Gpr2/Gpr3 感知 ascr#18）在真实场景中可能与氮代谢信号共同调控；项目在分析 docking 结果时可关注受体下游信号是否与氮感应通路有交叉。

3. **Amt43 内吞机制**：氨诱导 Amt43 快速内吞，而 Ascr#18 可缓解这一内吞，提示胞内稳态（plasma membrane integrity）与 ascaroside 信号传导相关，为受体定位稳定性研究提供参考背景。

4. **物种一致性**：本文所有实验均在 *A. oligospora* ATCC24927 进行，与项目 Gpr2/Gpr3 来源物种一致，方法和表型数据可直接参考。

---

## 关键引用（3-8条）

1. **Jiang et al. 2017** *Microbiol. Spectr.* — 线虫捕陷真菌综述；参考文献 [1]
2. **Xu et al. 2006** *Mol. Biol.* — nematode-trapping fungi 中 ascaroside 作为 trap inducer 的原始报道（ascr#5, #7, #18）；参考文献 [50 in paper]
3. **Lorenz et al. 2000** *Genetics* — Mep2 作为氨感受转导蛋白调控酵母假菌丝生长；参考文献 [46]（Amt43 功能类比基础）
4. **Biswas & Morschhäuser 2005** *Mol. Microbiol.* — Mep2 控制 *Candida albicans* 氮饥饿下假菌丝转换；参考文献 [47]
5. **Pires et al. 2017** *Biol. Control* — Ascr#18 诱导 NTF 捕陷器形成的实验证据；参考文献 [33 in paper]
6. **Zhang et al. 2023** *J. Fungi* — *A. oligospora* 捕陷器形成与分散；参考文献 [58]
7. **Zhao et al. 2013** *PLoS Pathog.* — 尿素及其代谢氨通过 Amt 转运蛋白调控 *A. oligospora* 生活方式转换；参考文献 [27 in paper]（氨驱动 NTF 生活方式转换的直接前序工作）
