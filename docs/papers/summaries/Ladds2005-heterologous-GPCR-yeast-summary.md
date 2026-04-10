# Ladds et al. 2005 — 文献总结

> **完整标题**: Functional analysis of heterologous GPCR signalling pathways in yeast
> **期刊**: Trends in Biotechnology, Vol. 23, No. 7, July 2005, pp. 367–373
> **DOI**: 10.1016/j.tibtech.2005.05.007
> **作者**: Graham Ladds, Alan Goddard, John Davey
> **机构**: Department of Biological Sciences, University of Warwick, Coventry, CV4 7AL, UK

---

## 核心发现（5-10 bullets，含数据）

- **>30 种哺乳动物 GPCRs** 已成功在酵母 *S. cerevisiae* 异源偶联至 pheromone response pathway，证明酵母平台具有广泛适用性。
- **嵌合 Gpa1/Gα（chimeric Gα）** 是解决偶联效率低下的核心策略：将 Gpa1 的 C 末端替换为哺乳动物 Gα 亚基对应残基（"Gα-transplants"），所得嵌合体的偶联特性广泛反映哺乳动物 Gα 的属性。
- **配体 screen 的尺度优势显著**：小分子配体（M_r < 1000）在酵母中的效力与哺乳动物细胞相近；大分子配体（M_r > 5000）效力降低约 100 倍，主要因细胞壁屏障所致。
- **报告基因选择**：FUS1 启动子控制的 HIS3（组氨酸生物合成）可提供生长表型读出，用于 high-throughput 分析；LacZ（β-galactosidase）提供定量读出，可用于测量激动剂/拮抗剂效力。
- **随机诱变（random mutagenesis）** 已被用于鉴定调控偶联效率的 GPCR 关键残基，在 V2 vasopressin receptor 系统中筛选了 30,000 个突变体，识别出跨膜螺旋中的功能关键残基。
- **RGS proteins**（Regulators of G protein Signalling）是酵母平台的重要调控节点：酵母自身的 Sst2 是 RGS 蛋白，其缺失（*sst2Δ*）可提高信号通路敏感性；AGS4 含三个 GPR 结构域，可以 Gβγ 非依赖方式激活 Gpa1。
- **裂殖酵母 *S. pombe*** 作为替代宿主：其 Gα 亚基（Gpa1）是 Gi/Go 的正效调节因子，腺苷酸环化酶受其调控，已被工程化用于分析 GPCR 突变体（含 constitutively active 状态的细胞在无尿嘧啶缺陷培养基中生长停滞，可借此分离功能变化的突变体）。
- **MAP kinase cascade 模块化**：酵母中的 Ste11（MEKK）→Ste7（MEK）→Fus3（MAPK）级联在功能上等价于哺乳动物 Raf→MEK→ERK；scaffold 蛋白 Ste5 和 Ste11 的 constitutively active 形式可用于在不依赖上游 GPCR/Gβγ 信号的情况下测试下游通路组件。
- **CRF-related peptides**（corticotropin-releasing factor 相关肽）可差异激活 CRF-R1A 和 CRF-R2B 受体；通过嵌合 Gα（Gs、Gi 或 Gq 系列）的组合，同一酵母系统可在不同 G 蛋白偶联背景下测量相同配体的受体选择性（图 3）。

---

## 实验方法（表格）

| 方法 | 用途 | 关键细节 |
|------|------|---------|
| 酵母 pheromone response pathway 重构 | 异源 GPCR 功能读出平台 | FUS1 启动子驱动 HIS3 或 LacZ 报告基因；删除 Ste2 防止内源信号干扰 |
| 嵌合 Gpa1/Gα 构建（Gα-transplants） | 改善 Gpa1 与哺乳动物 GPCR 偶联 | 替换 Gpa1 C 末端为哺乳动物 Gα（Gs、Gi、Gq 等）对应序列 |
| Far1 基因缺失（*far1Δ*） | 防止细胞周期停滞 | 避免信号激活后细胞死亡，保持活细胞用于高通量筛选 |
| Sst2 基因缺失（*sst2Δ*） | 提高受体信号敏感性 | 去除负调节；有时引入 RGS 蛋白以研究 G 蛋白信号去敏感化 |
| 随机诱变 + 酵母生长选择 | 鉴定 GPCR 功能残基 | 筛选 ~30,000 个 V2 vasopressin receptor 突变体，选取 constitutively active 或 increased/decreased sensitivity 表型 |
| β-galactosidase 定量报告基因 | 定量配体浓度-响应曲线 | LacZ 在 FUS1 启动子控制下表达，可用于 EC50 测定 |
| HIS3 营养选择报告基因 | 高通量 growth assay | 组氨酸缺陷培养基上的生长依赖信号激活 |
| *S. pombe* 工程化系统 | 替代宿主；Gi/Go 偶联研究 | 利用 *S. pombe* Gpa1 为 Gi/Go 同源物；uracil 缺陷培养基用于筛选 constitutively active 突变体 |
| MAP kinase cascade 独立激活 | 验证下游通路组件 | 使用 Ste5 scaffold 蛋白或 constitutively active Ste11 绕过上游信号 |
| 配体亲和力测定（配体屏幕） | 高通量配体筛选 | 可检测竞争性拮抗剂；部分系统使用 autocrine 筛选（配体与受体共表达） |

---

## 关键数据（分小节）

### 异源 GPCR 偶联成功率
- 截至综述发表时，>30 种哺乳动物 GPCRs 已在 *S. cerevisiae* pheromone pathway 中成功偶联，涵盖多类 Gα 亚基偶联特异性。

### 配体效力与细胞壁屏障
- 小分子配体（M_r < 1000，如 sphingosine-1-phosphate）：酵母中效力与哺乳动物细胞相近。
- 大分子配体（M_r > 5000，如 peptide 激素）：酵母中效力约低 100 倍，可能因细胞壁阻隔。
- 解决方案：酶解去除细胞壁（spheroplasting）使部分大分子配体活性恢复，但细胞变脆弱。

### 嵌合 Gα 偶联特异性（图 3 数据）
- CRF-R1A 与 CRF-R2B 受体在不同嵌合 Gα（Gs/Gi 系列）背景下对 UCN I、UCN II、UCN III 配体的差异应答在酵母系统中可被定量区分。
- Gα-transplants 的偶联特性广泛与对应哺乳动物 Gα 亚基一致。

### 随机诱变筛选规模
- V2 vasopressin receptor 系统：筛选约 **30,000 个突变体**，鉴定出跨膜螺旋中调控偶联的关键残基。
- M3 muscarinic acetylcholine receptor：通过诱变鉴定出 silence constitutively active mutant 的点突变，揭示 receptor/G protein 偶联的关键界面。

### *S. pombe* 系统参数
- 腺苷酸环化酶（encoded by *cyr1*）是 *S. pombe* cAMP 通路的关键酶，由 Gpa1 调控其活性。
- *S. pombe* constitutively active GPCR 系统：相关突变体细胞在缺乏尿嘧啶的培养基中无法生长（URAs 基因在 PRE 启动子控制下），可借此负向选择筛选 constitutively active 突变。

---

## 与项目的关系

本综述直接为 iGEM 2026 干实验的**嵌合 Gpa1 设计**提供实验文献基础：

1. **嵌合 Gα 设计原理验证**：综述明确说明 Gα-transplants（替换 Gpa1 C 末端为哺乳动物 Gα 对应残基）是解决 Gpa1 与非酵母 GPCR 低效偶联的主流策略，且其偶联特性可预测性地反映哺乳动物 Gα 属性。这为项目中嵌合 Gpa1 的设计思路提供了直接文献依据。

2. **平台可行性**：>30 种 GPCRs 成功偶联的记录证明，酵母异源 GPCR 表达系统对本项目拟使用的靶标 GPCR 具有可行性。

3. **信号通路读出选择**：综述描述的 HIS3 生长选择和 LacZ 定量报告基因体系，是项目验证 GPCR-嵌合 Gpa1 偶联功能的参考标准读出方案。

4. **RGS 蛋白调控节点**：Sst2 等 RGS 蛋白对信号敏感性的影响，提示在设计实验时需考虑 *sst2Δ* 背景对嵌合体偶联效率检测的影响。

> 注：以上为文献内容与项目的关系分析，不含项目实验数据。

---

## 关键引用（原文 References 编号）

1. **[4] Ramsay et al.** — 第一个在酵母 pheromone pathway 中偶联的异源 GPCR 为人 β₂-adrenergic receptor。
2. **[7] (review of chimeric Gα)** — 嵌合 Gα 的发展和特性综述（综述中引用为对 chimeric Gα 的专门综述）。
3. **[15] Klein et al. (1998)** — 鉴定 human FPRL-1 受体的代理激动剂，通过酵母 autocrine 筛选方法，在 *Nat. Biotechnol.* 发表。
4. **[25] Schmidt et al. (2003)** — 通过随机诱变鉴定 M3 muscarinic receptor 中"silence"组成性活化突变体的点突变，揭示 receptor/G protein 关键偶联残基。
5. **[26] Beukers et al. (2004)** — 随机诱变鉴定 human adenosine A2B receptor 的 constitutively active 和 gain-of-function 突变。
6. **[38] Dohlman et al. (1996)** — SST2 是 pheromone 脱敏化的负调节模型基因。
7. **[57] Arkinstall et al. (1995)** — neurokinin NK2 receptor 与 G protein 组件在裂殖酵母中共表达，验证 *S. pombe* 平台用于 GPCR 分析。
8. **[58] Ladds et al. (2003)** — 通过修饰的酵母细胞研究 GPCRs 对特定 G 蛋白的偶联（本综述第一作者的早期工作）。
