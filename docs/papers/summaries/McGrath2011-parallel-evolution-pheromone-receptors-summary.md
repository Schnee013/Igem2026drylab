# McGrath et al. 2011 — 文献总结

> **完整标题**: Parallel evolution of *Caenorhabditis elegans* species targets pheromone receptor genes
> **期刊**: *Nature*, Vol. 477, pp. 321–325, 15 September 2011
> **DOI**: 10.1038/nature10378
> **作者**: Patrick T. McGrath, Yifan Xu, Michael Ailion, Jennifer L. Garrison, Rebecca A. Butcher, Cornelia I. Bargmann
> **机构**: Howard Hughes Medical Institute, Laboratory of Neural Circuits and Behavior, The Rockefeller University, New York; Department of Biological Chemistry and Molecular Pharmacology, Harvard Medical School (R.A.B.); Department of Biology, University of Florida, Gainesville (Y.X.)

---

## 核心发现（5–10 bullets，含数据）

- **平行进化（parallel evolution）驱动了信息素抗性的独立起源**：两个实验室长期培养株（LSJ2 和 CC1）与野生型 N2 相比，均对 ascaroside C3（ascr#3）表现出显著的 dauer larva 形成抗性，但二者是独立起源的——LSJ2 分化约自 1957–1960 年，CC1 自 2003 年。
- **抗性由同一基因组区域内的两个 srg 家族基因（*srg-36* 和 *srg-37*）的缺失引起**：LSJ2 株系删除了 *srg-37*（X 染色体 14,229–14,238 kb 区域），CC1 株系删除了 *srg-36*（同区域内）；两个基因位于 X 染色体上相距数 kb 的位置。
- **srg-36 和 srg-37 编码 ascaroside C3 的化学感觉受体（chemoreceptors）**：GFP 融合报告实验显示两者均在 ASI 感觉神经元中优先表达；异位表达于 ASH 神经元后，动物反而对 C3 表现出回避行为，证明 SRG-36/37 直接感知 C3。
- **钙成像（Ca²⁺ imaging）确认 SRG-36/37 为 C3 的共受体（co-receptors）**：在 ASH 中异位表达 SRG-36 或 SRG-37 的动物，对 1 μM C3 ascaroside 产生显著的胞内 Ca²⁺ 升高；对照动物及 C6 ascaroside 均无此响应。
- **C3 ascaroside 的感知由 ASI 神经元而非 ASE 或 AFD 神经元介导**：srg-47（ASI 选择性启动子）驱动的 srg-36 cDNA 可完全拯救 LSJ2-N2 NIL 株的 C3 dauer 表型，而 AFD/ASE 启动子驱动的转基因则不能。
- **遗传作图（QTL mapping）将 C3 抗性定位到 X 染色体**：在 LSJ2 × N2 重组近交系（RILs）中，最高 lod 分值（P = 0.05 阈值以上）位于 X 染色体，且基因组导入实验（NIL 构建）将区间精确缩小至同时含 *srg-36* 和 *srg-37* 的小区段。
- **C. briggsae 也独立进化出 ascaroside 抗性，且涉及同源 srg 基因缺失**：实验室株 DR1690 对 dauer 信息素产生抗性，其基因组中存在一个 33 kb 的缺失（删除 *CBG24690*，即 srg 旁系基因，及其周围 6 个基因），将该缺失导入参考株 AF16 后即可重现抗性表型，证明跨物种的平行进化。
- **srg 基因家族进化：srg-36 与 srg-37 是近期重复（recent duplicates），与 G 蛋白偶联受体（GPCR）超家族中 7 个化学受体超家族成员相关**；*C. elegans* 和 *C. briggsae* 的 srg 旁系基因之间无一对一直系同源（orthologs）关系，提示受体亚型的快速演替。
- **结果提示，在实验室高密度条件下（高信息素浓度），删除 ascaroside 受体基因是快速适应的可重复遗传策略**，其速度远超点突变期望值，且与基因调控进化或感觉神经元适应等其他机制不同。

---

## 实验方法

| 方法 | 主要内容 |
|------|----------|
| **遗传作图 / QTL** | LSJ2 × N2 杂交生成 ~128 条重组近交系（RILs），对 C3 ascaroside 进行 dauer 形成率表型分析，全基因组 SNP 基因型扫描 |
| **近等基因系（NIL）构建** | 将 LSJ2 或 CC1 的小片段导入 N2 背景（及反向），精确定位抗性区间至 X 染色体 *srg-36/37* 附近 |
| **全基因组测序** | 对 LSJ2 和 CC1 进行 Illumina 测序，比较 N2 参考基因组，鉴定缺失断点 |
| **转基因拯救实验** | 将含各自上游启动子区的 *srg-36* / *srg-37* cDNA（双顺反子 GFP 融合）导入抗性株，检测 C3 dauer 形成率 |
| **启动子-GFP 报告** | *srg-36* 和 *srg-37* 基因组区域（含内源启动子）融合 GFP，在 L1 幼虫期检测神经元表达 |
| **ASH 异位表达 + 回避行为** | 用 ASH 特异启动子（*sra-6*）驱动 *srg-36* / *srg-37* cDNA，在微流控装置中检测动物对 C3 / C6 的回避行为 |
| **钙成像（Ca²⁺ imaging）** | 使用遗传编码钙指示剂 GCaMP3.0，在 ASH 中异位表达 SRG-36/37，以微流控装置施加 1 μM C3 或 C6，记录荧光变化（ΔF/F） |
| **C. briggsae NIL 构建** | 比较 DR1690 与 AF16 基因组，鉴定 33 kb 缺失；将含 *CBG24690* 缺失的区域导入 AF16，检测 dauer 抗性 |
| **信息素提取与合成** | 从液体培养 *C. elegans* 中提取粗信息素；合成 ascaroside C3、C5、C6、C9（化学合成，浓度范围 0.01–1 μM）|
| **dauer 形成率测定** | 将 L1 幼虫铺于含不同浓度 ascaroside 的食物平板，25°C 培养至 L3/成虫期，计算 dauer 比例 |

---

## 关键数据

### Dauer 形成率（图 1c）

在 100 nM C3 ascaroside 刺激下：
- N2：约 0.6 fraction dauer（高度敏感）
- LSJ2：约 0（完全抗性）
- CC1：约 0（完全抗性）
- 1 μM C6 和 C9：三株系均无 dauer 诱导

### NIL 定位（图 1d–f）

- 在 LSJ2 × N2 RILs 中，X 染色体 lod 分值达到峰值（超过 P = 0.05 阈值）
- CX13249（LSJ2-N2 NIL，含 *srg-36/37* 区域的 LSJ2 DNA）：对 C3 表现出完全抗性（接近 LSJ2 表型）
- CX13591（CC1-N2 NIL，含 *srg-36* 缺失区域的 CC1 DNA）：对 C3 也表现出完全抗性

### 遗传缺失断点

- LSJ2：*srg-37* 基因组区域被删除（对应 X 染色体 ~14,229–14,238 kb，~9 kb 缺失，精确断点由测序确认）
- CC1：*srg-36* 基因组区域被删除（与 LSJ2 缺失区域不同但邻近）

### 转基因拯救（图 2b）

- *Psrg-36:srg-36-genomic* 转基因：在 LSJ2-N2 NIL 背景下可拯救 C3 dauer 形成（>0.5 fraction dauer）
- *Psrg-37:srg-37-genomic* 转基因：同样能拯救（>0.5 fraction dauer）
- 单独 *srg-36* 或 *srg-37* cDNA 均可独立拯救，但 *srg-37* 转基因活性较 *srg-36* 弱
- ASI 特异启动子（*srg-47*）驱动的 *srg-36* cDNA 可完全拯救；AFD/ASE 驱动的版本不能

### ASI/ASH 钙成像（图 3c）

- 表达 SRG-36 或 SRG-37 的 ASH 神经元：1 μM C3 刺激后 ΔF/F 显著升高（约 60–100% 相对于基线）
- 表达 *C. briggsae CBG24690* 的 ASH 神经元：对 C3 响应较弱（ΔF/F 低于 SRG-36/37）
- 对照（空 vector）及 C6 ascaroside：所有条件下无显著 Ca²⁺ 升高

### C. briggsae 平行进化（图 4）

- DR1690 中 CBG24690 及其周围 ~33 kb 区域被缺失
- AF16 背景中导入该缺失后，动物对 dauer 信息素的响应明显降低（类似 DR1690）
- AF16-CBG24690 del NIL（DR1690-AF16 NIL）：对 dauer 粗提物表现中等抗性，介于两亲本株之间

---

## 与项目的关系

本论文与 iGEM 2026 干实验「NTF 跨界受体进化分析」方向高度相关，主要体现在以下几点：

1. **平行进化框架**：McGrath et al. 证明，在 *C. elegans* 和 *C. briggsae* 中，针对 ascaroside 感知的受体基因（srg 家族）在实验室条件下独立发生功能丧失突变，且目标基因高度一致。这为跨物种比较 ascaroside 受体进化提供了经典案例，与本项目研究 NTF（线虫捕食真菌）和 *C. elegans* 之间 ascaroside 受体共进化的框架直接类比。

2. **srg-36/srg-37 作为 ascaroside 受体**：这两个 GPCR 被实验确认为 C3 ascaroside 的感知受体（定位 ASI，钙成像功能验证），可与本项目所研究的 GprC（*A. flagrans*）、Gpr2/Gpr3（*C. briggsae*）等进行进化位置对比。

3. **受体特异性与配体-受体关系**：SRG-36/37 对 C3 具有选择性（不响应 C6、C9），这与项目中 GprC 对 ascr#18 的选择性响应形成对照，有助于理解不同 ascaroside 的受体识别机制。

4. **化学感觉神经元（ASI）介导 ascaroside dauer 决策**：确认 ASI 是 C3 感应的核心神经元，为跨界信号感知比较（线虫 vs. 真菌）提供神经元层面的参考。

5. **实验室适应性进化速率**：LSJ2 lineage 在约 50 年内（~1957–2009）、CC1 在约 4 年内（~2003–2009）独立演化出抗性，提示信息素受体基因删除是快速适应的遗传路径之一，为讨论 NTF-线虫 co-evolution 压力下受体演替速率提供参照。

---

## 关键引用

1. **Butcher et al. (2008)** — *Proc. Natl Acad. Sci. USA* 105, 14288–14292. 识别 *C. elegans* dauer 信息素的强效成分（包括 ascaroside C3）。

2. **Jeong et al. (2005)** — *Nature* 433, 541–545. 报道 *C. elegans* dauer 信息素的化学结构和生物活性。

3. **Srinivasan et al. (2008)** — *Nature* 454, 1115–1118. 发现小分子混合物同时调控交配和发育（dauer），进一步定义 ascaroside 系统。

4. **Kim et al. (2009)** — *Science* 326, 994–998. 发现两个化学受体介导 dauer 信息素对 *C. elegans* 发育的影响（SRBC64/66 相关研究背景）。

5. **Bargmann & Horvitz (1991)** — *Science* 251, 1243–1246. 鉴定 ASI 作为 *C. elegans* dauer 决策的关键神经元。

6. **Nei, Niimura & Nozawa (2008)** — *Nat. Rev. Genet.* 9, 951–963. 动物化学感觉受体基因库进化：机遇与必然性，为 srg 基因家族快速演替提供进化理论背景。

7. **Cutter (2008)** — *Mol. Biol. Evol.* 25, 778–786. 利用直接估算中性突变率推断 *C. elegans* 和 *C. briggsae* 的分化时间（约 2000 万年前）。

---

## 版本记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-10 | v1.0 | 初始总结，忠实于原文 PDF 内容 |
