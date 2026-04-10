# Huang et al. 2023 — 文献总结

> **完整标题**: NILR1 perceives a nematode ascaroside triggering immune signaling and resistance
> **期刊**: Current Biology 33, 3992–3997
> **发表日期**: September 25, 2023
> **DOI**: https://doi.org/10.1016/j.cub.2023.08.017
> **作者**: Li Huang, Yulin Yuan, Chloe Lewis, Joanna Kud, Joseph C. Kuhl, Allan Caplan, Louise-Marie Dandurand, Inga Zasada, Fangming Xiao
> **通讯作者**: Fangming Xiao (fxiao@uidaho.edu)
> **机构**: University of Idaho (Plant Sciences, Entomology); University of Arkansas (Entomology); USDA-ARS (Corvallis, OR)

---

## 核心发现（5–10 bullets，含数据）

- **NILR1 直接结合 Ascr18**：等温滴定量热法（ITC）测定 Ecto-NILR1 与 Ascr18 的解离常数 K_D = 0.610 ± 0.136 μM，结合化学计量比 N = 0.719 ± 0.2（约 1:1），表明单分子结合模式。
- **结合特异性依赖 ID 结构域与 C 端 LRR**：截短突变体 Ecto-NILR1^Δ494–695 完全丧失与 Ascr18 的结合（ITC 无热变化），表明胞外域 C 端 ID 结构域及最后 5 个 LRR 对结合不可缺少。
- **Ascr2/Ascr3 不直接结合 NILR1**：ITC 结果显示 Ascr2 和 Ascr3 均不与 Ecto-NILR1 发生直接相互作用，但二者也能触发免疫信号，说明存在其他 PRR 参与识别。
- **NILR1 是 Ascr18 触发免疫信号的遗传必需因子**：WT 植株用 1 μM Ascr18 处理后，PR1、PR4、FRK1、GSTF6 等免疫标记基因在 6 h 显著上调；nilr1-1 和 nilr1-2 两个功能缺失突变体中，该响应完全消失。
- **NILR1 介导对细菌（Pst DC3000）的抗性**：Ascr18 预处理后 WT 植株 Pst DC3000 菌落数（CFU/cm²）显著降低（**p < 0.01）；nilr1-1/nilr1-2 中该诱导抗性完全丧失（n.d.）。
- **NILR1 介导根部对根结线虫（M. incognita）的抗性**：10 nM Ascr18 预处理 48 h 后，WT 根系被 M. incognita 侵染形成的虫瘿数量显著减少（~400 freshly hatched J2 inoculum，6 周后计数，**p < 0.01，n = 12）；nilr1 突变体中虫瘿数无显著差异（n.d.）。
- **根部 Ascr18 信号也依赖 NILR1**：10 nM Ascr18 处理 nilr1 突变体根系后，PR1、PDF1.2、SAUR34 等防御基因表达不被诱导（WT 中均显著上调）。
- **NILR1 激活 MAPK 信号通路**：Ascr18 处理 WT 原生质体后 p44/42 MAPK 磷酸化激活；nilr1-2 突变体中该激活减弱，提示 NILR1 通过 MAPK 级联传递信号。
- **首个植物/动物先天免疫中明确的线虫 NAMP–受体对**：Ascr18–NILR1 是迄今报道的第一个在任何生物体（植物或动物）中鉴定的、针对线虫感染的配体–受体免疫识别对。

---

## 实验方法（表格）

| 方法 | 技术细节 |
|------|---------|
| 等温滴定量热法（ITC） | Nano ITC（TA Instruments），25°C；100 μM Ascr18 注入含 10 μM Ecto-NILR1 的标准池；20 次注射（3 μL/次，150 s 间隔）；NanoAnalyze 3.5 分析 |
| 重组蛋白表达与纯化 | NILR1 胞外域克隆入 pDEST17（N端 6×His 标签）；E. coli BL21 于 37°C 表达 10 h，0.5 mM IPTG 22–23°C 诱导过夜；HisTrap FF 镍柱亲和纯化；Western blot（Anti-6-His）验证 |
| 截短突变体 | Ecto-NILR1^Δ494–695（缺失 aa 494–570）和 Ecto-NILR1^Δ494–695（缺失 aa 494–695） |
| qRT-PCR | Split RNA 提取试剂盒（Lexogen）；SuperScript IV 反转录；Power SYBR Green；ABI Prism 7100；Tubulin 内参；ΔΔCt 法 |
| 细菌感染实验 | 5 周龄 WT / nilr1 植株；Ascr18 或 Mock 预处理；Pst DC3000（1×10^7 CFU/mL）注射接种；4 天后测定叶片 CFU/cm² |
| 线虫感染实验 | Ascr18（10 nM）或 mock 预处理 48 h；接种 ~400 freshly hatched M. incognita J2；6 周后计数虫瘿（n=12）；t 检验，**p < 0.01 |
| MAPK 磷酸化检测 | 原生质体提取（Macerozyme R10 + Cellulase R10）；1 μM Ascr18 或 Mock 处理 10 min；Western blot 检测 phospho-p44/42 MAPK（Cell Signaling Technology #9101）|
| 系统发育分析 | TAIR 获取 AtNILR1 直系同源蛋白序列（烟草、番茄、小麦等 11 个物种）；BLASTp；MEGA-X Neighbor-Joining 法；1000 bootstrap；ITOL 可视化 |
| 植物材料 | Arabidopsis thaliana Col-0（WT）；nilr1-1（SAIL_865_E07）；nilr1-2（SAIL_859_H01）；22–24°C，16 h 光照 / 8 h 黑暗 |

---

## 关键数据（分小节）

### ITC 结合参数

| 配体–受体对 | K_D (μM) | N（化学计量比） |
|------------|----------|---------------|
| Ascr18 + Ecto-NILR1 | 0.610 ± 0.136 | 0.719 ± 0.2 |
| Ascr18 + Ecto-NILR1^Δ494–695 | 无结合（无热变化）| — |
| Ascr2 + Ecto-NILR1 | 无结合 | — |
| Ascr3 + Ecto-NILR1 | 无结合 | — |

### 免疫基因诱导（叶片，1 μM Ascr18，6 h）

- PR1、PR4、FRK1、GSTF6 在 WT 中均显著上调（相对表达量约 5–18 倍）
- nilr1-1 和 nilr1-2 中上述基因响应完全缺失

### 细菌抗性（Pst DC3000）

- WT + Ascr18 预处理：CFU/cm² 从约 4×10^7 降至约 1×10^7（**p < 0.01）
- nilr1-1/nilr1-2 + Ascr18：CFU 无显著变化（n.d.）

### 线虫抗性（M. incognita，根系，10 nM Ascr18）

- WT + Ascr18：虫瘿数从约 28 降至约 18（**p < 0.01，n = 12）
- nilr1-1/nilr1-2 + Ascr18：虫瘿数无显著变化（n.d.）

### 根部防御基因（10 nM Ascr18，48 h）

- WT 中 PR1、PDF1.2、SAUR34 均显著上调
- nilr1 突变体中上述基因均无响应

---

## 与项目的关系

本文是 iGEM 2026 干实验 ascr#18 跨界感知机制研究的核心文献之一，意义如下：

1. **受体确认**：本文首次鉴定了植物侧识别 ascr#18 的受体 NILR1，其 K_D ≈ 0.61 μM 是分子对接与结合亲和力研究的重要参照数据点。

2. **结合口袋线索**：结合特异性依赖 C 端 LRR（ID 结构域 + 最后 5 个 LRR），为后续 homology modeling 和对接研究提供了功能性约束——对接结果应优先关注 Ecto-NILR1 C 端 LRR 区域的结合口袋。

3. **跨界感知验证**：ascr#18 同时被线虫（作为性信息素/群体信号）和宿主植物（作为 NAMP）识别，体现了化学信号的"双向利用"，是项目跨界感知叙事的直接证据。

4. **配体特异性对比**：NILR1 不结合 Ascr2/Ascr3，而 Ascr2/Ascr3 可能通过其他 PRR 触发免疫，提示 ascr 家族不同成员有不同受体，项目若考虑多个 ascaroside 的模拟需区分受体系统。

5. **信号通路锚点**：NILR1→MAPK→PR1/FRK1 的信号轴为下游 ODE 信号通路建模提供了生物学基础。

---

## 关键引用（来自本文参考文献）

1. **Mendy et al. 2017** — NILR1 被首次报道为先天免疫所需的白氨酸重复受体激酶，PLoS Pathog. 13, e1006284. (Ref 4)
2. **DeFalco & Zipfel 2021** — 植物早期模式触发免疫的分子机制综述，Mol. Cell 81, 3449–3467. (Ref 1)
3. **Manosalva et al. 2015** — 保守线虫 ascaroside 激活植物防御和病原抗性，Nat. Commun. 6, 7795. (Ref 3)
4. **Wram & Zasada 2019** — 亚致死剂量线虫处理对根结线虫的短期效应，Phytopathology 109, 1605–1613. (Ref 14)
5. **Klessig et al. 2018** — 线虫 ascaroside 在多种植物病原系统中增强抗性，J. Phytopathol. 167, 265–272. (Ref 8)
6. **Li et al. 2018** — 葡萄 VqSTS21 基因表达赋予拟南芥渗透/生物胁迫抗性但不依赖于 NILR1，Front. Plant Sci. 7, 1379. (Ref 19)
7. **Zhang & Gleason 2021** — 植物寄生线虫转录组分析鉴定假定效应蛋白，J. Nematol. 53, 1–13. (Ref 16)
