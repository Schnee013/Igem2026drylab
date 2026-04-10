# Kuo et al. 2026 — 文献总结

> **完整标题**: A nematode-trapping fungus orchestrates polarity cues, septins, and NOX signaling for trap formation
> **期刊/预印本**: bioRxiv（预印本，未经同行评审）
> **DOI**: https://doi.org/10.64898/2026.03.09.710510
> **发布日期**: 2026年3月13日
> **作者**: Chih-Yen Kuo, Hung-Che Lin, Yun-Zhen Chou, Sheng-An Chen, Hillel Schwartz, Yen-Ping Hsueh
> **通讯作者**: Yen-Ping Hsueh（yphsueh@tuebingen.mpg.de）
> **机构**:
> - Department of Complex Biological Interactions, Max Planck Institute for Biology, Tübingen 72076, Germany
> - Department of Biology, Duke University, Durham, NC 27708, USA
> - Institute of Molecular Biology, Academia Sinica, Taipei 11529, Taiwan

---

## 核心发现（5–10 bullets，含数据）

- **细胞极性蛋白重定向驱动捕陷器形态发生**：在营养菌丝伸长期，几丁质合酶（Chs1、Chs7）和细胞末端标记物（Tea1-GFP）富集于菌丝顶端；线虫诱导后约200 mpe（minutes post-exposure），这些蛋白重新富集至捕陷器顶端 SPK（Spitzenkörper）、新形成的隔膜和即将发生融合的位点，提示同一套极性模块被重新部署用于捕陷器三维弯曲生长。

- **septins 优先富集于捕陷器环内凹缘，介导环路弯曲**：*A. oligospora* 基因组编码6个 septin（Sep3–Sep8）。四个核心 septin（Sep3、Sep4、Sep5、Sep6）在230–240 mpe 时显著富集于捕陷器内侧弯曲缘及分支/融合位点，与其在高膜曲率区域的保守定位一致。删除任何核心 septin 均显著减少捕陷器形成；*sep3* 和 *sep6* 缺失体几乎完全不产生捕陷器，*sep5* 和 *sep6* 缺失体以简单单环或不完整环为主，而 *sep4* 缺失体捕陷器形态接近野生型——提示 Sep3、Sep5、Sep6 专门负责多环复合捕陷器结构的成熟。

- **NADPH 氧化酶 Nox1 介导局域化 ROS 信号，是细胞–细胞融合的空间检查点**：*NOX1* 和 *NOXR1* 均为线虫响应基因，在捕陷器形成起始阶段显著上调；pNOX1–GFP 报告基因仅在与线虫接触后的捕陷器初始细胞中特异表达。*nox1* 和 *noxr1* 缺失体可正常发起捕陷器生长和弯曲，但无法完成菌丝融合，形成特征性"猪尾"（pigtail）状未闭合结构。

- **ROS 局域化决定融合位点的精确性**：用 NBT（nitroblue tetrazolium）染色检测超氧阴离子：在捕陷器形成早期（2–3.5 hpe），野生型和 *nox* 突变体菌丝尖端均出现 ROS 积累（Nox1 非依赖性）；而在 4 hpe，野生型在接受菌丝上的特定融合位点出现局域化 NBT 信号，该信号在 *nox1* 和 *noxr1* 突变体中完全缺失——表明 Nox1 专门产生靶细胞侧的定点 ROS 信号以触发菌丝融合。

- **Nox1 介导的 ROS 是极性蛋白和细胞骨架向融合位点招募的必要条件**：野生型中，Chs1-mNG、Tea1-GFP 和 Lifeact-GFP 在 225 mpe 时强烈富集于接受菌丝的融合位点；在 *nox* 突变体中，这些蛋白在捕陷器尖端定位正常，但无法在接受菌丝的预期融合位点积累，导致在 300 mpe 时捕陷器仍未闭合。

- **actin 与 septin 在感染结构（infection bulb）中的空间分工**：线虫被捕后，捕陷器细胞分化出穿透线虫角质层的侵袭菌丝。actin（Lifeact-GFP）在 ~70 mpc（minutes post-capture）富集于新生侵袭菌丝顶端，而 septins 在 75 mpc 时重新集中于感染球（infection bulb）与侵袭菌丝的分支节点——揭示活性菌丝尖端（actin）与基部分支位点（septins）的精细空间组织。

- **Tea1 是捕陷器定向弯曲的必要极性标记物**：*tea1* 缺失体产生仅具柄状初始结构、缺乏环路弯曲的形态缺陷捕陷器，捕获效率显著降低（捕陷器数目与野生型相近，但不能形成完整环）。而 *tea5* 缺失体捕陷器数量正常但尺寸减小，在培养基菌落内部形成锯齿形菌丝，提示 Tea5 主要调控网络组织而非顶端生长。

- **几丁质合酶 Chs1 对捕陷器数量有重要贡献**：*chs1* 缺失体捕陷器数量约 100 个/cm²，显著少于野生型约 500 个/cm²；所产捕陷器形态简单，仅由单一菌丝环组成，说明 Chs1 参与捕陷器细胞壁重塑。

---

## 实验方法（表格）

| 方法 | 关键细节 |
|------|----------|
| 菌株与培养 | *A. oligospora* TWF154；低营养培养基（LNM）诱导捕陷器；*C. elegans* N2（Bristol）作为线虫猎物 |
| 基因组分析 | Blast2GO 5 PRO 局域 BLAST；T-Coffee 多序列比对；FastTree 系统发育树；InterPro 域预测；iTOL 可视化 |
| 转录组分析 | 利用已发表的 RNA-seq 时间序列数据集（Lin et al., 2023；GEO：GSE233568），追踪线虫暴露后 0–48 hpe 转录变化 |
| 荧光融合蛋白标记 | C 端融合 GFP 或 mNeonGreen，内源启动子驱动；SR2200（细胞壁）、FM4-64（膜）共染 |
| 活细胞成像 | LSM980 Airyscan 2 共聚焦显微镜（Carl Zeiss），Plan-Apochromat 100×/1.46 油镜；Andor Revolution WD + Nikon Ti-E EMCCD（捕陷器发育分析） |
| 基因敲除 | *ku70* 突变背景（提高同源重组频率），PCR + Southern blotting 验证；互补实验确认表型特异性 |
| 表型定量 | 30只 *C. elegans* L4 期幼虫暴露48 h；40× 显微镜下拍照计数捕陷器；线虫逃逸率（30只成体，10 min） |
| 超氧化物检测 | NBT（0.1% w/v nitroblue tetrazolium）染色；2–4 hpe 时间点；LSM980 共聚焦成像 |
| 统计分析 | 至少3个生物学重复；双尾 Student's *t* 检验或单因素 ANOVA + Fisher's LSD 多重检验；*P* < 0.05 显著 |

---

## 关键数据

### 几丁质合酶（CHS）

- *A. oligospora* TWF154 基因组含7个 CHS 基因（Chs1–Chs7），代表丝状真菌中保守的7个 CHS 家族。
- Chs1–Chs3 序列同一性约60%，Chs4–Chs6 约35%，Chs7 与其他 CHS 仅15–20% 同一性。
- RNA-seq：*CHS1*、*CHS4*、*CHS7* 均为线虫响应基因，4 hpe 下调，10 hpe 捕陷器形成时回升。
- *chs1* 缺失：捕陷器数量 ~100/cm²（野生型 ~500/cm²），捕陷器形态简单（单环）。

### 细胞末端标记物（cell-end markers）

- 鉴定到 Tea1、Tea2、Tea4 和 Tea5（Mod5 同源物）的同源物；未发现 Tea3 同源物。
- *TEA1*、*TEA2*、*TEA4*、*TEA5* 均为线虫响应基因，峰值表达在 10 hpe。
- Tea1-GFP 在营养菌丝顶端形成新月形皮层帽；捕陷器形成时迁移至预期融合位点（225 mpe）。
- *tea1* 缺失：产生柄状初始结构（无弯曲），无法形成正常捕陷器环；*tea5* 缺失：捕陷器数量正常但尺寸缩小，菌落内部菌丝锯齿形。

### Septin 系统

- *A. oligospora* 含6个 septin 基因；Sep3、Sep4、Sep5、Sep6 属四个核心 septin 组（1a、2a、3、4），Sep7/Sep8 属第5组（丝状真菌/原生生物特有）。
- 核心 septins 与 *A. nidulans* 和 *M. oryzae* 同源物序列同一性达85–90%；Sep7/Sep8 保守性显著低。
- 核心 septins 均在线虫暴露后上调（RNA-seq）。
- 定位：在菌丝顶端胞质弥散分布（SPK 区域排斥），富集于分支基部高曲率膜区。
- 捕陷器中，Sep3/Sep4/Sep5 在230–240 mpe 富集于分支/融合区；Sep6-GFP 主要定位于发育中隔膜。
- 表型：*sep3*/*sep6* 缺失体几乎不产生捕陷器；*sep5*/*sep6* 产生简单单环或不完整环；*sep4* 缺失体形态接近野生型。

### Nox1/ROS 信号

- *A. oligospora* 编码 Nox1 及其调控因子 NoxR1 的保守同源物；Ao-Nox1 含铁蛋白还原酶跨膜结构域、FAD 结合域和 NAD 结合域；Ao-NoxR1 含 TPR、Phox 和 Bem1 结构域。
- *NOX1* 和 *NOXR1* 线虫暴露后转录显著上调。
- pNOX1-GFP 报告基因：营养生长期不可检测；线虫接触后特异性在捕陷器初始细胞中表达（4 hpe 遍及延长/弯曲的捕陷器细胞）。
- *nox1*/*noxr1* 缺失体：捕陷器数量与野生型相当，但100% 无法完成菌丝融合，形成"猪尾"状结构（pigtail morphology）。
- NBT 染色：4 hpe 时，野生型接受菌丝的融合位点出现局域化超氧信号；*nox* 突变体该信号完全缺失（早期 ROS 产生保留，证明早期 ROS 为 Nox1 非依赖性）。
- 在 *nox* 突变体中，Chs1-mNG、Tea1-GFP、Lifeact-GFP 均无法在接受菌丝融合位点积累（捕陷器尖端定位正常），300 mpe 时捕陷器仍未闭合。

---

## 与项目的关系

本文研究对象为 *Arthrobotrys oligospora*，与本项目核心受体（Gpr2/Gpr3）所在物种相同，提供了从线虫信号感知到捕陷器形态发生的细胞学/分子机制背景，对 iGEM 2026 信号通路 ODE 建模具有以下参考价值：

1. **新信号节点（NOX/ROS）**：本文揭示 Nox1-mediated ROS 是捕陷器闭合的必要空间信号，且 *NOX1*/*NOXR1* 受线虫信号转录激活。已知 pheromone-responsive MAPK 通路调控 *NOX* 转录（Chen et al., 2021）。这意味着 Gpr2/Gpr3 → MAPK → NOX1 → ROS → 融合 可作为 ODE 模型的一个下游模块扩展，对应捕陷器闭合这一关键输出节点。

2. **Septin 作为形态输出变量**：核心 septin 的转录在线虫暴露后上调，且其局域化（内凹缘富集）直接对应捕陷器几何形状的量化特征；可作为 ODE 模型中"形态成熟度"的代理变量。

3. **时间线参数**：文中提供了明确的时间节点数据（200 mpe 极性蛋白重定位；230–240 mpe septin 富集；4 hpe Nox1 局域化 ROS），可用于校准捕陷器形成时间常数。

4. **局限性**：本文不涉及 ascaroside 受体结合或 Gpr2/Gpr3 的具体生化参数，ODE 建模所需的动力学常数（kon/koff、Hill 系数等）需从其他文献（Hu2024、Kuo2024 等）补充。

---

## 关键引用（来自本文参考文献）

1. **Chen et al., 2021** — pheromone-responsive MAPK 通路调控 *A. oligospora* NOX 转录及捕陷器诱导（本文 Discussion 多次引用）

2. **Hu et al., 2024** — 捕陷器诱导信号通路表征（与 Gpr2/Gpr3 相关的关键上下文文献）

3. **Kuo et al., 2024** — 捕陷器诱导信号通路表征（同上）

4. **Lin et al., 2023** — *A. oligospora* 线虫暴露后转录组时间序列 RNA-seq 数据集（GEO: GSE233568），本文多项分析的基础数据来源

5. **Kriegler et al., 2025b** — *A. flagrans* 中 cell-end marker 和 septins（Cdc11）在捕陷器形成中的作用，支持 NTF 极性保留为保守特征

6. **Herzog et al., 2015** — CAT（conidial anastomosis tube）融合中 MAP kinase 激活 NADPH 氧化酶的机制（NOX/ROS 在真菌细胞融合中的核心经典文献）

7. **Roca et al., 2012** — NOX 衍生 ROS 作为局域信号触发细胞壁重塑和膜融合的证据（真菌融合 ROS 信号经典文献）

8. **Yang et al., 2020** — *A. oligospora* TWF154 基因组序列（NCBI SOZJ00000000），本文基因组分析基础
