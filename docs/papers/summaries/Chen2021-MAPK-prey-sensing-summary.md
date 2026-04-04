# Chen et al. 2021 — 文献总结

> **完整标题**: Prey sensing and response in a nematode-trapping fungus is governed by the MAPK pheromone response pathway
> **期刊**: GENETICS, 2021, 217(2), iyaa008
> **DOI**: 10.1093/genetics/iyaa008
> **作者**: Sheng-An Chen, Hung-Che Lin, Frank C. Schroeder, Yen-Ping Hsueh
> **机构**: Academia Sinica (Taiwan), Boyce Thompson Institute & Cornell University

## 核心发现

- **Fus3 MAPK cascade 是 *A. oligospora* 感知线虫并启动 trap morphogenesis 的核心通路**。该通路由保守的 pheromone-response MAPK pathway 组成：Ste11 (MAPKKK) → Ste7 (MAPKK) → Fus3 (MAPK) → Ste12 (transcription factor)。
- **STE7 和 FUS3 基因敲除突变体完全丧失 trap formation 能力**，即使暴露于超过 1000 条 *C. elegans* 一周也无法形成任何 trap。同时对 ascaroside ascr#18（线虫保守 pheromone）也无响应。
- **Fus3 在线虫接触后被磷酸化激活**。Western blot 时间序列显示：Fus3 在 nematode induction 后 2h 和 4h（trap initiation 阶段）被磷酸化，到 24h（trap 形成完成后）信号消失。
- **Slt2 MAPK 组成性磷酸化，非 trap morphogenesis 必需**。slt2 突变体在长时间暴露于线虫后仍可形成少量 trap。
- **Gpb1（G-protein beta subunit，Ste4 homolog）作用于 Fus3 上游**。gpb1 突变体中 Fus3 磷酸化缺失，暗示 GPCR/G-protein 信号传导至 Fus3 cascade。
- **Ste12 是 Fus3 下游的关键 transcription factor**。ste12 突变体无法形成正常 trap，但 conidiation 不受影响（与 ste7/fus3 不同），说明 Fus3 还有 Ste12 以外的靶标调控 conidiation。
- **Ste12-dependent regulon 包含 525 个转录本**（约占 *A. oligospora* 基因组的 4%），其中 44%（231/525）仅在 NTF 中有 BLAST hit，暗示这些基因是 NTF 特有的 predatory lifestyle 相关基因。
- **MAPK 通路同时调控 vegetative growth 和 conidiation**。ste7 和 fus3 突变体生长缓慢，且 conidiation 完全被废除。

## 实验方法

| 方法 | 用途 |
|------|------|
| **Targeted gene deletion**（homologous recombination in ku70 background） | 构建 ste7, fus3, ste12, slt2 deletion mutants |
| **CRISPR-Cas9 gene deletion** | 构建 SLT2 deletion（作为替代策略验证） |
| **Western blot**（phospho-p44/42 MAPK antibody） | 检测 Fus3 和 Slt2 的磷酸化状态与动态变化 |
| **Trap formation assay**（*C. elegans* N2 induction） | 定量 trap 数量，24h 后 40x 显微镜计数 |
| **Ascaroside ascr#18 induction** | 测试化学信号单独诱导 trap 的能力 |
| **RNA-seq**（Illumina NovaSeq 6000, 150bp PE） | ku70 vs ku70 ste12 在有/无线虫条件下的 transcriptome profiling |
| **Differential expression analysis**（Salmon + Sleuth） | 识别 Ste12-dependent nematode-responsive genes（\|betas\| >= 2, adj P < 0.05） |
| **GO enrichment**（Blast2GO 5 PRO, Fisher's exact test） | 分析 Ste12-dependent regulon 的功能富集 |
| **Complementation** | 回补野生型 allele 验证表型恢复 |
| **Southern blot** | 确认 targeted deletion 和无 ectopic integration |

## 关键数据

### MAPK Pathway 组分（*A. oligospora* gene IDs）

| 组分 | 功能 | Gene ID | S. cerevisiae ortholog |
|------|------|---------|----------------------|
| Ste11 | MAPKKK | EYR41_007451 | Ste11 |
| **Ste7** | **MAPKK** | **EYR41_011623** | Ste7 |
| **Fus3** | **MAPK** | **EYR41_011934** | Fus3/Kss1 |
| **Ste12** | **Transcription factor** | **EYR41_007450** | Ste12 |
| Slt2 | MAPK (cell wall integrity) | EYR41_004559 | Slt2 |
| Gpb1 | G-protein beta subunit | — | Ste4 |

### 磷酸化动力学

- **Fus3 磷酸化**: 0h (无) → 2h (强) → 4h (强) → 24h (消失) → 48h (消失)
- **Slt2 磷酸化**: 所有时间点均为 constitutive phosphorylation
- gpb1 和 fus3 突变体中 Fus3 磷酸化完全缺失；Slt2 磷酸化不受影响

### Transcriptome 数据

- ku70 nematode-induced vs control: **261 up + 682 down** (共 943 DEGs)
- ku70 ste12 induced vs control: **132 up + 205 down** (仅 337 DEGs，响应大幅减弱)
- **Ste12-dependent regulon**: 525 transcripts（186 仅在 ku70 中差异表达 + 525 与 ste12/ku70 基线差异的交集定义）
  - 141 upregulated, 384 downregulated in ste12 mutant
  - GO 富集: "integral component of membrane", "oxidation-reduction process"
  - 关键靶基因: NOX enzymes (NoxR EYR41_003117, Nox2 EYR41_011461), polyketide synthase (EYR41_000001), lipoxygenase, alcohol dehydrogenases
- **44% 的 Ste12-dependent regulon (231/525) 仅在 NTF 中有 significant BLAST hit**，186/231 无功能注释

### Trap 定量

- WT: ~60 traps/plate (mean); ku70: similar
- ste7, fus3 mutants: **0 traps**（包括 >1000 线虫暴露一周）
- ste12 mutants: **0 traps** (24h); 长时间暴露后可形成少量异常 trap
- Complemented strains: trap formation 恢复

## 与项目的关系

### 1. MAPK pathway downstream of Gpr2/Gpr3 — 信号级联建模

本文直接揭示了 ascaroside 信号感知的下游通路。虽然文中未直接研究 Gpr2/Gpr3，但明确指出：
- **GPCRs 和 G-protein 信号传导可能作用于 Fus3 MAPK cascade 上游**（Discussion 中明确提出此 hypothesis）
- **Gpb1 (G-protein beta subunit) 是 Fus3 激活所必需的**，gpb1 突变体无法磷酸化 Fus3
- 这为构建 **Gpr2/Gpr3 → G-protein (Gpb1) → Ste11 → Ste7 → Fus3 → Ste12** 的完整信号通路提供了实验依据

### 2. Signal pathway ODE modeling (P0) — 关键参数

本文提供了 ODE 建模所需的关键信息：
- **Fus3 磷酸化动力学**：有明确的时间序列数据（0, 2, 4, 24, 48h），可用于拟合 phosphorylation/dephosphorylation rate constants
- **Pathway 拓扑结构**：Ste11 → Ste7 → Fus3 → Ste12，三级级联，符合经典 MAPK cascade 模型
- **Slt2 pathway 独立且非必需**：可简化模型，聚焦 Fus3 cascade
- **输入信号**: ascaroside (ascr#18) 单独即可触发 trap formation
- **输出**: trap initiation ~2.5h，trap formation complete ~12h (来自 Yang et al. 2020 的数据)

### 3. Pathway component identification — 完整的组分列表

文中提供了所有 MAPK cascade 组分的 Gene ID，以及系统发育分析确认的 ortholog 关系，可直接用于：
- 从 *A. oligospora* TWF154 genome 中提取序列
- 构建 protein-protein interaction network
- 与 Hsueh et al. 2013 中 Gpr2/Gpr3 的数据整合

### 4. NOX/ROS 作为下游效应器

Ste12-dependent regulon 中包含 NOX enzymes，ROS production 可能是 trap development 的 secondary messenger，这为模型增加了从 transcription factor 到细胞形态学改变的效应通路。

## 关键引用

- **Hsueh et al. 2013** — *Curr Biol* 23:83-86. 首次报道 NTF 通过 ascarosides 感知线虫，Gpr2/Gpr3 的发现论文
- **Yang et al. 2020** — *PNAS* 117:6762-6770. *A. oligospora* TWF154 reference strain 建立，本文使用的遗传背景
- **Choe et al. 2012** — *Curr Biol* 22:772-780. Ascaroside signaling 在线虫中的保守性
- **Kuo, Chen et al. 2020** — *J Fungi* 6. HOG pathway (Hog1 MAPK) 在 *A. oligospora* 中的功能，与本文互补
- **Zhen et al. 2018** — *Fungal Genet Biol* 116:42-50. Slt2 MAPK orthologs 在两种 NTF 中的功能
- **Li, Kang et al. 2017** — *J Microbiol* 55:885-891. NoxA 在 *A. oligospora* 捕食中的作用
- **Manosalva et al. 2015** — *Nat Commun* 6:7795. Ascarosides 跨界激活植物 MAPK 通路的先例
